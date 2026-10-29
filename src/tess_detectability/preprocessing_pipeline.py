"""Deterministic, provenance-complete Phase 5A preprocessing pipeline."""
from __future__ import annotations

import os
from pathlib import Path
import numpy as np
import pandas as pd

from .detrending import detrend_segment
from .lightcurve_reader import read_lightcurve
from .normalization import normalize_segment
from .preprocessing_config import PreprocessingConfig
from .quality_mask import quality_keep_mask
from .time_cleaning import assign_segments, deterministic_sort, duplicate_keep_mask


def process_lightcurve(raw_path: Path, metadata: dict[str, object],
                       config: PreprocessingConfig) -> tuple[
                           pd.DataFrame, dict[str, object], list[dict[str, object]],
                           list[dict[str, object]]]:
    frame, source_decision = read_lightcurve(raw_path, config)
    frame["finite_time"] = np.isfinite(frame.time_btjd.to_numpy(dtype=float))
    frame["finite_flux"] = np.isfinite(frame.raw_flux.to_numpy(dtype=float))
    frame["quality_keep"] = quality_keep_mask(
        frame.quality.fillna(np.iinfo(np.int64).max).to_numpy(),
        config.quality_keep_value)
    frame["duplicate_keep"] = duplicate_keep_mask(frame)
    frame["structural_keep"] = (
        frame.finite_time & frame.finite_flux & frame.duplicate_keep)
    duplicate_removed = frame.loc[
        frame.finite_time & frame.finite_flux & ~frame.duplicate_keep,
        ["original_row_index", "time_btjd", "quality"]].copy()
    frame = deterministic_sort(frame)
    segment_numbers, gap_audit = assign_segments(
        frame, cadence_seconds=int(metadata["cadence_seconds"]),
        gap_multiplier=config.gap_threshold_multiplier)
    frame["segment_id"] = segment_numbers.map(
        lambda value: pd.NA if pd.isna(value) else
        f"{metadata['selection_unit_id']}_S{int(metadata['sector']):04d}_G{int(value):03d}")
    frame["protected_transit_window"] = False
    frame["normalization_factor"] = np.nan
    frame["normalized_flux"] = np.nan
    frame["trend_flux"] = np.nan
    frame["detrended_flux"] = np.nan
    frame["outlier_keep"] = False
    segment_audits: list[dict[str, object]] = []
    for segment_id in frame.segment_id.dropna().unique():
        mask = frame.segment_id.eq(segment_id)
        indexes = frame.index[mask]
        normalized, baseline, normalization_status = normalize_segment(
            frame.loc[indexes, "raw_flux"].to_numpy(dtype=float),
            minimum_points=config.minimum_segment_points)
        frame.loc[indexes, "normalization_factor"] = baseline
        frame.loc[indexes, "normalized_flux"] = normalized
        if normalization_status == "NORMALIZED":
            trend, detrended, window, minimum = detrend_segment(
                normalized, cadence_seconds=int(metadata["cadence_seconds"]),
                window_days=config.detrending_window_days,
                minimum_fraction=config.rolling_minimum_fraction,
                minimum_floor_points=config.rolling_minimum_floor_points)
            frame.loc[indexes, "trend_flux"] = trend
            frame.loc[indexes, "detrended_flux"] = detrended
            frame.loc[indexes, "outlier_keep"] = np.isfinite(detrended)
        else:
            window = minimum = 0
        segment_audits.append({
            "segment_id": segment_id,
            "segment_rows": len(indexes),
            "normalization_factor": baseline,
            "normalization_status": normalization_status,
            "detrending_method": config.detrending_method,
            "window_days": config.detrending_window_days,
            "window_samples": window,
            "rolling_minimum_points": minimum,
            "finite_detrended_rows": int(np.isfinite(
                frame.loc[indexes, "detrended_flux"].to_numpy(dtype=float)).sum()),
        })
    frame["final_keep"] = (
        frame.structural_keep & frame.quality_keep & frame.duplicate_keep &
        frame.outlier_keep & np.isfinite(frame.detrended_flux.to_numpy(dtype=float)))
    for key in ["benchmark_order", "selection_unit_id", "host_name", "resolved_tic",
                "sector", "camera", "ccd", "cadence_seconds", "source_file",
                "source_file_sha256"]:
        frame[key] = metadata[key]
    frame["flux_source"] = source_decision["flux_source"]
    frame["preprocessing_variant"] = config.variant
    frame["protocol_version"] = config.protocol_version
    ordered = [
        "benchmark_order", "selection_unit_id", "host_name", "resolved_tic",
        "sector", "camera", "ccd", "cadence_seconds", "source_file",
        "source_file_sha256", "original_row_index", "time_btjd", "raw_flux",
        "raw_flux_err", "flux_source", "quality", "quality_keep", "finite_time",
        "finite_flux", "duplicate_keep", "structural_keep",
        "protected_transit_window", "segment_id", "normalization_factor",
        "normalized_flux", "trend_flux", "detrended_flux", "outlier_keep",
        "final_keep", "preprocessing_variant", "protocol_version",
    ]
    return frame[ordered], source_decision, duplicate_removed.to_dict("records"), (
        [{**metadata, **row} for row in gap_audit] + segment_audits)


def write_parquet_atomic(frame: pd.DataFrame, destination: Path,
                         config: PreprocessingConfig) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(str(destination) + ".tmp")
    if temporary.exists():
        temporary.unlink()
    frame.to_parquet(temporary, engine=config.parquet_engine,
                     compression=config.parquet_compression, index=False)
    os.replace(temporary, destination)
