"""Frozen Phase 5B transit-recovery configuration."""
from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class RecoveryConfig:
    protocol_version: str = "1.0.0"
    seed: int = 20260722
    minimum_period_days: float = 0.3
    maximum_period_days: float = 30.0
    maximum_baseline_fraction: float = 0.5
    oversampling_factor: int = 5
    minimum_grid_points: int = 2000
    maximum_grid_points: int = 12000
    durations_days: tuple[float, ...] = (
        0.04, 0.06, 0.09, 0.13, 0.18, 0.25, 0.35)
    maximum_duration_period_fraction: float = 0.20
    top_k: int = 10
    phase_drift_tolerance: float = 0.25
    harmonic_ratios: tuple[float, ...] = (
        1.0, 0.5, 2.0, 1.0 / 3.0, 3.0, 2.0 / 3.0, 1.5)
    epoch_duration_multiplier: float = 1.5
    epoch_fallback_period_fraction: float = 0.05
    duration_ratio_min: float = 0.5
    duration_ratio_max: float = 2.0
    top_candidate_count: int = 10

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


FROZEN_RECOVERY_CONFIG = RecoveryConfig()
