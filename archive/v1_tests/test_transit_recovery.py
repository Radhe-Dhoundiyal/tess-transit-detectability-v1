from __future__ import annotations

import inspect
from pathlib import Path
import tempfile
import unittest

import numpy as np
import pandas as pd

from tess_detectability.bls_grid import array_sha256, duration_grid, period_grid
from tess_detectability.bls_search import run_blind_search
from tess_detectability.peak_extraction import local_maxima, select_peak_indices
from tess_detectability.recovery_config import FROZEN_RECOVERY_CONFIG
from tess_detectability.recovery_matching import compare_pair
from tess_detectability.recovery_metrics import wilson_interval

ROOT = Path(__file__).resolve().parents[1]


class TransitRecoveryTests(unittest.TestCase):
    def test_period_and_duration_grids_are_deterministic(self):
        first = period_grid(27.0, FROZEN_RECOVERY_CONFIG)
        second = period_grid(27.0, FROZEN_RECOVERY_CONFIG)
        np.testing.assert_array_equal(first, second)
        self.assertEqual(array_sha256(first), array_sha256(second))
        self.assertEqual(first[0], 0.3)
        self.assertAlmostEqual(first[-1], 13.5)
        self.assertEqual(len(duration_grid(FROZEN_RECOVERY_CONFIG)), 7)

    def test_short_and_empty_grid_behavior(self):
        self.assertEqual(len(period_grid(0.5, FROZEN_RECOVERY_CONFIG)), 0)
        time = np.linspace(0, 0.5, 100)
        candidates, summary = run_blind_search(
            time, np.zeros_like(time), FROZEN_RECOVERY_CONFIG)
        self.assertTrue(candidates.empty)
        self.assertEqual(summary["search_status"], "INSUFFICIENT_BASELINE")

    def test_peak_extraction_separation_tie_and_topk(self):
        period = np.array([1.0, 1.1, 2.0, 3.0, 4.0])
        power = np.array([1.0, 1.0, 0.0, 2.0, 0.0])
        self.assertEqual(local_maxima(power).tolist(), [0, 1, 3])
        selected = select_peak_indices(
            period, power, baseline_days=100, top_k=2)
        self.assertEqual(selected, [3, 0])

    def test_clear_synthetic_transit_is_deterministic(self):
        time = np.arange(0, 20, 0.02)
        phase = ((time - 0.1 + 1.0) % 2.0) - 1.0
        flux = np.zeros_like(time)
        flux[np.abs(phase) < 0.06] = -0.02
        first, status1 = run_blind_search(
            time, flux, FROZEN_RECOVERY_CONFIG)
        second, status2 = run_blind_search(
            time, flux, FROZEN_RECOVERY_CONFIG)
        self.assertEqual(status1["search_status"], "SEARCH_COMPLETE")
        self.assertEqual(status1, status2)
        pd.testing.assert_frame_equal(first, second)
        self.assertLess(abs(first.iloc[0].candidate_period - 2.0), 0.05)

    def test_direct_half_double_and_other_harmonic_matching(self):
        truth = pd.Series({
            "catalogue_period": 2.0, "catalogue_epoch_btjd": 0.1,
            "catalogue_duration_days": 0.1})
        labels = [(2.0, "DIRECT_PERIOD_RECOVERY"),
                  (1.0, "HALF_PERIOD_HARMONIC"),
                  (4.0, "DOUBLE_PERIOD_HARMONIC"),
                  (6.0, "INTEGER_HARMONIC_OTHER")]
        for period, label in labels:
            candidate = pd.Series({
                "candidate_rank": 1, "candidate_period": period,
                "candidate_transit_time": 0.1,
                "candidate_duration": 0.1})
            result = compare_pair(
                candidate, truth, baseline=20,
                config=FROZEN_RECOVERY_CONFIG)
            self.assertEqual(result["match_class"], label)

    def test_epoch_missing_and_duration_diagnostics(self):
        candidate = pd.Series({
            "candidate_rank": 1, "candidate_period": 2.0,
            "candidate_transit_time": 0.1, "candidate_duration": 0.1})
        truth = pd.Series({
            "catalogue_period": 2.0, "catalogue_epoch_btjd": np.nan,
            "catalogue_duration_days": np.nan})
        result = compare_pair(
            candidate, truth, baseline=20, config=FROZEN_RECOVERY_CONFIG)
        self.assertFalse(result["epoch_matches"])
        self.assertFalse(result["duration_matches"])

    def test_blind_search_has_no_truth_dependency(self):
        source = inspect.getsource(run_blind_search).casefold()
        for token in [
            "truth", "catalogue_period", "catalogue_epoch", "planet_name",
            "recovery_matching"]:
            self.assertNotIn(token, source)

    def test_wilson_denominator_accounting(self):
        low, high = wilson_interval(5, 10)
        self.assertLess(low, 0.5)
        self.assertGreater(high, 0.5)
        self.assertTrue(np.isnan(wilson_interval(0, 0)[0]))

    def test_no_injection_or_model_dependency(self):
        paths = [
            ROOT / "src/tess_detectability/bls_search.py",
            ROOT / "src/tess_detectability/recovery_matching.py",
            ROOT / "src/tess_detectability/recovery_inputs.py",
        ]
        text = "\n".join(path.read_text(encoding="utf-8").casefold()
                         for path in paths)
        for token in ["injection_recovery", "model_training", "lightkurve"]:
            self.assertNotIn(token, text)


if __name__ == "__main__":
    unittest.main()
