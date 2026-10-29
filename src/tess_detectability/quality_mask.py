"""Global Phase 5A QUALITY policy."""
from __future__ import annotations

import numpy as np


def quality_keep_mask(quality: np.ndarray, keep_value: int = 0) -> np.ndarray:
    values = np.asarray(quality)
    return np.isfinite(values.astype(float, copy=False)) & (values == keep_value)
