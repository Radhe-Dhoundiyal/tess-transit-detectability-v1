"""Phase 5B endpoint and Wilson interval helpers."""
from __future__ import annotations

import math


def wilson_interval(successes: int, total: int, z: float = 1.959963984540054
                    ) -> tuple[float, float]:
    if total <= 0:
        return float("nan"), float("nan")
    p = successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    margin = z * math.sqrt(
        p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return center - margin, center + margin
