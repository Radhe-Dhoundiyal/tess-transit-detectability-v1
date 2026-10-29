"""Blind BLS runner. This module has no catalogue-truth dependency."""
from __future__ import annotations

import numpy as np
import pandas as pd
from astropy.timeseries import BoxLeastSquares

from .bls_grid import duration_grid, period_grid
from .peak_extraction import select_peak_indices
from .recovery_config import RecoveryConfig


def run_blind_search(time: np.ndarray, flux: np.ndarray,
                     config: RecoveryConfig) -> tuple[pd.DataFrame, dict[str, object]]:
    time = np.asarray(time, dtype=float)
    flux = np.asarray(flux, dtype=float)
    if len(time) < 50:
        return pd.DataFrame(), {"search_status": "INSUFFICIENT_ROWS"}
    baseline = float(time.max() - time.min())
    if baseline <= 2 * config.minimum_period_days:
        return pd.DataFrame(), {"search_status": "INSUFFICIENT_BASELINE"}
    periods = period_grid(baseline, config)
    durations = duration_grid(config)
    if not len(periods):
        return pd.DataFrame(), {"search_status": "PERIOD_GRID_EMPTY"}
    bls = BoxLeastSquares(time, flux)
    best = {
        name: np.full(len(periods), np.nan, dtype=float)
        for name in [
            "power", "duration", "transit_time", "depth", "depth_err"]}
    for duration in durations:
        valid = duration < config.maximum_duration_period_fraction * periods
        if not valid.any():
            continue
        result = bls.power(
            periods[valid], float(duration),
            objective="likelihood", method="fast")
        indexes = np.flatnonzero(valid)
        improve = ~np.isfinite(best["power"][indexes]) | (
            np.asarray(result.power) > best["power"][indexes])
        chosen = indexes[improve]
        source = np.flatnonzero(improve)
        for name in best:
            if name == "duration":
                best[name][chosen] = duration
            else:
                best[name][chosen] = np.asarray(getattr(result, name))[source]
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
    return pd.DataFrame(rows), {
        "search_status": "SEARCH_COMPLETE", "baseline_days": baseline,
        "searched_min_period": float(periods.min()),
        "searched_max_period": float(periods.max()),
        "period_grid_count": len(periods),
        "duration_grid_count": len(durations),
    }
