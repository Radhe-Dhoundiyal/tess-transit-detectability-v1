"""Frozen segment-median normalization."""
from __future__ import annotations

import numpy as np


def normalize_segment(flux: np.ndarray, *, minimum_points: int) -> tuple[
        np.ndarray, float | None, str]:
    values = np.asarray(flux, dtype=float)
    finite = np.isfinite(values)
    output = np.full(values.shape, np.nan, dtype=float)
    if int(finite.sum()) < minimum_points:
        return output, None, "INSUFFICIENT_SEGMENT_POINTS"
    baseline = float(np.median(values[finite]))
    if not np.isfinite(baseline) or baseline == 0:
        return output, baseline, "INVALID_SEGMENT_BASELINE"
    output[finite] = values[finite] / baseline - 1.0
    return output, baseline, "NORMALIZED"
