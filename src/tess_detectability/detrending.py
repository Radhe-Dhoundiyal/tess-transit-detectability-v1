"""Frozen centered rolling-median additive detrending."""
from __future__ import annotations

import math
import numpy as np
import pandas as pd


def window_samples(window_days: float, cadence_seconds: int) -> int:
    samples = max(1, int(round(window_days * 86400.0 / cadence_seconds)))
    if samples % 2 == 0:
        samples += 1
    return samples


def detrend_segment(normalized_flux: np.ndarray, *, cadence_seconds: int,
                    window_days: float, minimum_fraction: float,
                    minimum_floor_points: int) -> tuple[np.ndarray, np.ndarray, int, int]:
    values = np.asarray(normalized_flux, dtype=float)
    window = window_samples(window_days, cadence_seconds)
    minimum = max(minimum_floor_points, int(math.ceil(window * minimum_fraction)))
    minimum = min(minimum, len(values))
    trend = pd.Series(values).rolling(
        window=window, center=True, min_periods=minimum).median().to_numpy(dtype=float)
    detrended = values - trend
    return trend, detrended, window, minimum
