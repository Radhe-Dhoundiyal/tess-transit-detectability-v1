"""Blind BLS runner. This module has no catalogue-truth dependency."""
from __future__ import annotations

import numpy as np
import pandas as pd
from astropy.timeseries import BoxLeastSquares

from .bls_grid import array_sha256, duration_grid, period_grid
from .period_grid import alternative_period_grid, GRID_VERSION
from .peak_extraction import select_peak_indices
from .recovery_config import RecoveryConfig


def run_blind_search(time: np.ndarray, flux: np.ndarray,
                     config: RecoveryConfig) -> tuple[pd.DataFrame, dict[str, object]]:
    """Historical V1 interface and unchunked search settings."""
    candidates, summary, _ = _run_search(time, flux, config, "v1", None)
    return candidates, summary


def run_grid_search(time: np.ndarray, flux: np.ndarray, *, grid_kind: str,
                    config: RecoveryConfig, chunk_size: int | None = 2048
                    ) -> tuple[pd.DataFrame, dict[str, object], dict[str, np.ndarray]]:
    """Explicit V1/V1.1 search; arrays permit inspection without catalogue truth."""
    if grid_kind not in ("v1", "v1.1"):
        raise ValueError("grid_kind must be 'v1' or 'v1.1'")
    if chunk_size is not None and (type(chunk_size) is not int or chunk_size < 1):
        raise ValueError("chunk_size must be a positive integer or None")
    candidates, summary, arrays = _run_search(time, flux, config, grid_kind, chunk_size)
    if arrays:
        summary.update({
            "grid_version": GRID_VERSION if grid_kind == "v1.1" else "historical-v1",
            "grid_array_sha256": array_sha256(arrays["period"]),
            "chunk_size": len(arrays["period"]) if chunk_size is None else chunk_size,
        })
    return candidates, summary, arrays


def _run_search(time, flux, config, grid_kind, chunk_size):
    time = np.asarray(time, dtype=float)
    flux = np.asarray(flux, dtype=float)
    if len(time) < 50:
        return pd.DataFrame(), {"search_status": "INSUFFICIENT_ROWS"}, {}
    baseline = float(time.max() - time.min())
    if baseline <= 2 * config.minimum_period_days:
        return pd.DataFrame(), {"search_status": "INSUFFICIENT_BASELINE"}, {}
    periods = (period_grid(baseline, config) if grid_kind == "v1"
               else alternative_period_grid(baseline, config))
    durations = duration_grid(config)
    if not len(periods):
        return pd.DataFrame(), {"search_status": "PERIOD_GRID_EMPTY"}, {}
    bls = BoxLeastSquares(time, flux)
    best = {
        name: np.full(len(periods), np.nan, dtype=float)
        for name in [
            "power", "duration", "transit_time", "depth", "depth_err"]}
    for duration in durations:
        valid = duration < config.maximum_duration_period_fraction * periods
        if not valid.any():
            continue
        valid_indices = np.flatnonzero(valid)
        step = len(periods) if chunk_size is None else chunk_size
        for start in range(0, len(valid_indices), step):
            indexes = valid_indices[start:start + step]
            result = bls.power(
                periods[indexes], float(duration),
                objective="likelihood", method="fast", oversample=10)
            improve = ~np.isfinite(best["power"][indexes]) | (
                np.asarray(result.power) > best["power"][indexes])
            chosen = indexes[improve]
            source = np.flatnonzero(improve)
            for name in best:
                best[name][chosen] = (duration if name == "duration"
                                     else np.asarray(getattr(result, name))[source])
    indices = select_peak_indices(
        periods, best["power"],
        baseline_days=baseline, top_k=config.top_k)
    rows = []
    for rank, index in enumerate(indices, start=1):
        period = float(periods[index])
        duration = float(best["duration"][index])
        transit_time = float(best["transit_time"][index])
        mask = bls.transit_mask(time, period, duration, transit_time)
        frequency = 1.0 / period
        daily = [str(integer) for integer in (1, 2, 3)
                 if abs(frequency - integer) <= 1.0 / baseline]
        depth = float(best["depth"][index])
        depth_err = float(best["depth_err"][index])
        rows.append({
            "candidate_rank": rank, "candidate_period": period,
            "candidate_frequency": frequency, "candidate_duration": duration,
            "candidate_transit_time": transit_time,
            "candidate_power": float(best["power"][index]),
            "candidate_depth": depth, "candidate_depth_err": depth_err,
            "candidate_depth_snr":
                depth / depth_err if np.isfinite(depth_err) and depth_err > 0 else np.nan,
            "predicted_transit_count": int(np.floor(baseline / period)) + 1,
            "in_transit_point_count": int(mask.sum()),
            "local_peak_status": "LOCAL_MAXIMUM",
            "alias_flags": "|".join(f"INTEGER_DAY_FREQUENCY_{item}" for item in daily),
            "search_grid_index": int(index),
        })
    summary = {
        "search_status": "SEARCH_COMPLETE", "baseline_days": baseline,
        "searched_min_period": float(periods.min()),
        "searched_max_period": float(periods.max()),
        "period_grid_count": len(periods),
        "duration_grid_count": len(durations),
    }
    arrays = {"period": periods, **best}
    return pd.DataFrame(rows), summary, arrays
