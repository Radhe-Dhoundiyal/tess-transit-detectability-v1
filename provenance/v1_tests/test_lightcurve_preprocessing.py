from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest

from astropy.io import fits
import numpy as np
import pandas as pd

from tess_detectability.detrending import detrend_segment, window_samples
from tess_detectability.lightcurve_reader import read_lightcurve
from tess_detectability.normalization import normalize_segment
from tess_detectability.preprocessing_config import FROZEN_CONFIG
from tess_detectability.preprocessing_pipeline import (
    process_lightcurve, write_parquet_atomic,
)
from tess_detectability.quality_mask import quality_keep_mask
from tess_detectability.time_cleaning import (
    assign_segments, deterministic_sort, duplicate_keep_mask,
)


def make_fits(path: Path, *, pdcsap=True, primary_finite=True,
              rows=100, duplicate=False) -> None:
    time = np.arange(rows, dtype=float) * 120.0 / 86400.0 + 2000
    if duplicate:
        time[2] = time[1]
    quality = np.zeros(rows, dtype=np.int32)
    quality[1] = 4
    sap = np.linspace(1000.0, 1001.0, rows)
    pdc = np.linspace(500.0, 501.0, rows)
    if not primary_finite:
        pdc[:] = np.nan
    columns = [
        fits.Column(name="TIME", format="D", array=time),
        fits.Column(name="QUALITY", format="J", array=quality),
        fits.Column(name="SAP_FLUX", format="D", array=sap),
        fits.Column(name="SAP_FLUX_ERR", format="D", array=np.ones(rows)),
    ]
    if pdcsap:
        columns += [
            fits.Column(name="PDCSAP_FLUX", format="D", array=pdc),
            fits.Column(name="PDCSAP_FLUX_ERR", format="D", array=np.ones(rows)),
        ]
    primary = fits.PrimaryHDU()
    primary.header["TICID"] = "123"
    primary.header["SECTOR"] = 1
    table = fits.BinTableHDU.from_columns(columns, name="LIGHTCURVE")
    fits.HDUList([primary, table]).writeto(path)


class PreprocessingTests(unittest.TestCase):
    def test_flux_and_uncertainty_hierarchy(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "p.fits"
            make_fits(path)
            _, decision = read_lightcurve(path, FROZEN_CONFIG)
            self.assertEqual(decision["flux_source"], "PDCSAP_FLUX")
            self.assertEqual(decision["uncertainty_source"], "PDCSAP_FLUX_ERR")
            self.assertEqual(decision["fallback_reason"], "")

    def test_structural_fallback_is_not_visual(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "p.fits"
            make_fits(path, primary_finite=False)
            _, decision = read_lightcurve(path, FROZEN_CONFIG)
            self.assertEqual(decision["flux_source"], "SAP_FLUX")
            self.assertEqual(decision["uncertainty_source"], "SAP_FLUX_ERR")
            self.assertEqual(decision["fallback_reason"], "PRIMARY_ZERO_FINITE_VALUES")

    def test_quality_policy(self):
        result = quality_keep_mask(np.array([0, 1, 4, 0]))
        self.assertEqual(result.tolist(), [True, False, False, True])

    def test_duplicate_rule_prefers_quality_zero_then_index(self):
        frame = pd.DataFrame({
            "time_btjd": [1.0, 1.0, 2.0, 2.0],
            "quality": [4, 0, 0, 0],
            "original_row_index": [0, 1, 2, 3],
            "finite_time": [True] * 4,
            "finite_flux": [True] * 4,
        })
        self.assertEqual(duplicate_keep_mask(frame).tolist(),
                         [False, True, True, False])

    def test_sort_and_gap_segmentation(self):
        frame = pd.DataFrame({
            "time_btjd": [2.0, 1.0, 1.0013888889, np.nan],
            "original_row_index": [0, 1, 2, 3],
            "structural_keep": [True, True, True, False],
            "quality_keep": [True, True, True, True],
        })
        sorted_frame = deterministic_sort(frame)
        self.assertEqual(sorted_frame.original_row_index.tolist(), [1, 2, 0, 3])
        segments, gaps = assign_segments(
            sorted_frame, cadence_seconds=120, gap_multiplier=5)
        self.assertEqual(segments.dropna().astype(int).tolist(), [1, 1, 2])
        self.assertEqual(len(gaps), 1)

    def test_normalization_and_fallback(self):
        normalized, baseline, status = normalize_segment(
            np.array([2.0, 4.0, 6.0]), minimum_points=3)
        self.assertEqual(status, "NORMALIZED")
        self.assertEqual(baseline, 4.0)
        np.testing.assert_allclose(normalized, [-0.5, 0, 0.5])
        self.assertEqual(normalize_segment(
            np.array([1.0]), minimum_points=2)[2], "INSUFFICIENT_SEGMENT_POINTS")

    def test_window_is_cadence_specific_odd_and_edges_are_defined(self):
        self.assertEqual(window_samples(0.5, 120), 361)
        self.assertEqual(window_samples(0.5, 20), 2161)
        values = np.linspace(-0.1, 0.1, 100)
        trend, residual, window, minimum = detrend_segment(
            values, cadence_seconds=120, window_days=0.5,
            minimum_fraction=0.5, minimum_floor_points=5)
        self.assertEqual(window, 361)
        self.assertEqual(minimum, 100)
        self.assertTrue(np.isfinite(trend).all())
        self.assertTrue(np.isfinite(residual).all())

    def test_pipeline_row_accounting_and_no_transit_or_outlier_removal(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "p.fits"
            make_fits(path, rows=100, duplicate=True)
            before = hashlib.sha256(path.read_bytes()).hexdigest()
            metadata = {
                "benchmark_order": 1, "selection_unit_id": "SYS-SYNTH",
                "host_name": "SYNTH", "resolved_tic": "123", "sector": 1,
                "camera": 1, "ccd": 1, "cadence_seconds": 120,
                "source_file": "p.fits", "source_file_sha256": before.upper(),
            }
            output, decision, duplicates, audits = process_lightcurve(
                path, metadata, FROZEN_CONFIG)
            self.assertEqual(len(output), 100)
            self.assertEqual(len(duplicates), 1)
            self.assertFalse(output.protected_transit_window.any())
            self.assertTrue((output.outlier_keep == np.isfinite(
                output.detrended_flux)).all())
            self.assertEqual(before, hashlib.sha256(path.read_bytes()).hexdigest())

    def test_atomic_parquet_is_deterministic(self):
        frame = pd.DataFrame({"a": [1, 2], "b": [0.5, np.nan]})
        with tempfile.TemporaryDirectory() as folder:
            first = Path(folder) / "first.parquet"
            second = Path(folder) / "second.parquet"
            write_parquet_atomic(frame, first, FROZEN_CONFIG)
            write_parquet_atomic(frame, second, FROZEN_CONFIG)
            self.assertEqual(hashlib.sha256(first.read_bytes()).hexdigest(),
                             hashlib.sha256(second.read_bytes()).hexdigest())
            self.assertFalse(Path(str(first) + ".tmp").exists())

    def test_no_period_search_or_recovery_dependencies(self):
        root = Path(__file__).resolve().parents[1]
        paths = [
            root / "src/tess_detectability/preprocessing_pipeline.py",
            root / "src/tess_detectability/detrending.py",
            root / "src/tess_detectability/normalization.py",
            root / "src/tess_detectability/time_cleaning.py",
        ]
        text = "\n".join(path.read_text(encoding="utf-8").casefold() for path in paths)
        for token in ["boxleastsquares", "periodogram", "phase_fold",
                      "injection_recovery", "recovery_score", "lightkurve"]:
            self.assertNotIn(token, text)


if __name__ == "__main__":
    unittest.main()
