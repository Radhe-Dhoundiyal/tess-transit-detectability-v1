"""Stable Phase 6A seed hierarchy and globally balanced design."""
from __future__ import annotations

import hashlib
import numpy as np

DEPTHS = (100, 200, 400, 800, 1600, 3200, 6400, 12800)
PERIOD_BINS = ((0.3, 1.0), (1.0, 3.0), (3.0, 10.0), (10.0, 30.0))
DURATIONS = (0.06, 0.09, 0.13, 0.18)


def trial_seed(protocol: str, benchmark_order: int, selection_unit_id: str,
               cell_id: str, injection_index: int) -> int:
    value = "|".join(map(str, [protocol, benchmark_order, selection_unit_id,
                               cell_id, injection_index])).encode()
    return int.from_bytes(hashlib.sha256(value).digest()[:8], "big") & 0x7FFF_FFFF_FFFF_FFFF


def draw_trial(benchmark_order: int, selection_unit_id: str,
               injection_index: int, maximum_period: float,
               time_start: float) -> dict[str, object]:
    depth = DEPTHS[injection_index]
    bin_index = (benchmark_order - 1 + injection_index) % len(PERIOD_BINS)
    lower, upper = PERIOD_BINS[bin_index]
    upper = min(upper, maximum_period)
    if upper <= lower:
        viable = [index for index, (lo, _) in enumerate(PERIOD_BINS)
                  if lo < maximum_period]
        bin_index = viable[-1]
        lower, upper0 = PERIOD_BINS[bin_index]
        upper = min(upper0, maximum_period)
    cell_id = f"P{bin_index + 1}_D{injection_index + 1}"
    seed = trial_seed("1.0.0", benchmark_order, selection_unit_id,
                      cell_id, injection_index)
    rng = np.random.default_rng(seed)
    period = float(np.exp(rng.uniform(np.log(lower), np.log(upper))))
    epoch = float(time_start + rng.uniform(0.0, period))
    duration = float(min(DURATIONS[injection_index % 4], 0.15 * period))
    return {"cell_id": cell_id, "seed": seed, "period": period,
            "epoch": epoch, "depth_ppm": depth, "duration": duration,
            "period_bin": bin_index + 1, "depth_bin": injection_index + 1}
