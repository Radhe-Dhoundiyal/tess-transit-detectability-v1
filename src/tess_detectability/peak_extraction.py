"""Deterministic local-maximum and candidate extraction."""
from __future__ import annotations

import numpy as np


def local_maxima(power: np.ndarray) -> np.ndarray:
    values = np.asarray(power, dtype=float)
    if not len(values):
        return np.array([], dtype=int)
    left = np.r_[-np.inf, values[:-1]]
    right = np.r_[values[1:], -np.inf]
    return np.flatnonzero(
        np.isfinite(values) & (values >= left) & (values >= right) &
        ((values > left) | (values > right)))


def select_peak_indices(period: np.ndarray, power: np.ndarray, *,
                        baseline_days: float, top_k: int) -> list[int]:
    maxima = local_maxima(power)
    if not len(maxima) and len(power):
        maxima = np.array([int(np.nanargmax(power))])
    ordered = sorted(
        maxima.tolist(),
        key=lambda index: (-float(power[index]), float(period[index]), index))
    selected: list[int] = []
    min_frequency_separation = 1.0 / baseline_days
    for index in ordered:
        frequency = 1.0 / float(period[index])
        if any(abs(frequency - 1.0 / float(period[other])) <
               min_frequency_separation for other in selected):
            continue
        selected.append(index)
        if len(selected) >= top_k:
            break
    return selected
