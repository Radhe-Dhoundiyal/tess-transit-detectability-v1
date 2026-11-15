"""V1.1 union grid, bounded by duration drift over the observed span."""
import numpy as np
from .bls_grid import period_grid
from .recovery_config import FROZEN_RECOVERY_CONFIG, RecoveryConfig

GRID_OVERSAMPLING = 2.0
GRID_VERSION = "v1-union-log-duration-bound-O2-v1"


def alternative_period_grid(baseline_days: float,
                            config: RecoveryConfig = FROZEN_RECOVERY_CONFIG,
                            oversampling: float = GRID_OVERSAMPLING) -> np.ndarray:
    if not np.isfinite(baseline_days) or baseline_days <= 2 * config.minimum_period_days:
        return np.array([], dtype=np.float64)
    minimum = float(config.minimum_period_days)
    maximum = min(float(config.maximum_period_days),
                  float(config.maximum_baseline_fraction) * baseline_days)
    duration = min(config.durations_days)
    if minimum <= 0 or duration <= 0 or not np.isfinite(oversampling) or oversampling <= 0:
        raise ValueError("Positive finite period, duration and oversampling are required")
    hmax = np.log1p(duration / (oversampling * baseline_days))
    intervals = int(np.ceil(np.log(maximum / minimum) / hmax))
    if intervals > 20_000_000:
        raise MemoryError("Requested grid exceeds explicit allocation limit; grid is not silently capped")
    log_grid = np.geomspace(minimum, maximum, intervals + 1, dtype=np.float64)
    # Retain every historical node: only sampling is added.
    return np.unique(np.r_[period_grid(baseline_days, config), log_grid])
