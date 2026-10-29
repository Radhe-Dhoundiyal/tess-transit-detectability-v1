"""Deterministic Phase 5B period and duration grids."""
from __future__ import annotations

import hashlib
import numpy as np

from .recovery_config import RecoveryConfig


def period_grid(baseline_days: float, config: RecoveryConfig) -> np.ndarray:
    maximum = min(config.maximum_period_days,
                  baseline_days * config.maximum_baseline_fraction)
    if not np.isfinite(baseline_days) or maximum <= config.minimum_period_days:
        return np.array([], dtype=np.float64)
    min_frequency = 1.0 / maximum
    max_frequency = 1.0 / config.minimum_period_days
    raw_step = min(config.durations_days) / (
        config.oversampling_factor * baseline_days ** 2)
    raw_count = int(np.floor((max_frequency - min_frequency) / raw_step)) + 1
    count = min(config.maximum_grid_points,
                max(config.minimum_grid_points, raw_count))
    frequencies = np.linspace(min_frequency, max_frequency, count,
                              endpoint=True, dtype=np.float64)
    return (1.0 / frequencies)[::-1].copy()


def duration_grid(config: RecoveryConfig) -> np.ndarray:
    return np.asarray(config.durations_days, dtype=np.float64)


def array_sha256(values: np.ndarray) -> str:
    array = np.asarray(values, dtype="<f8")
    return hashlib.sha256(array.tobytes(order="C")).hexdigest().upper()
