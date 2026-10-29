"""Frozen Phase 5A preprocessing parameters."""
from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class PreprocessingConfig:
    protocol_version: str = "1.0.0"
    variant: str = "PRIMARY"
    primary_flux: str = "PDCSAP_FLUX"
    fallback_flux: str = "SAP_FLUX"
    primary_uncertainty: str = "PDCSAP_FLUX_ERR"
    fallback_uncertainty: str = "SAP_FLUX_ERR"
    minimum_flux_finite_fraction: float = 0.50
    quality_keep_value: int = 0
    gap_threshold_multiplier: float = 5.0
    minimum_segment_points: int = 50
    normalization_method: str = "SEGMENT_MEDIAN_DIVIDE_MINUS_ONE"
    detrending_method: str = "CENTERED_ROLLING_MEDIAN_ADDITIVE"
    detrending_window_days: float = 0.5
    rolling_minimum_fraction: float = 0.5
    rolling_minimum_floor_points: int = 5
    transit_protection_enabled: bool = False
    outlier_clipping_enabled: bool = False
    parquet_engine: str = "pyarrow"
    parquet_compression: str = "zstd"

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


FROZEN_CONFIG = PreprocessingConfig()

# Phase 5A.1 changes only the protocol lineage and the globally registered
# handling of files for which neither registered flux source reaches the
# unchanged structural threshold. Numerical preprocessing parameters remain
# byte-for-byte equivalent to 1.0.0.
AMENDED_CONFIG = PreprocessingConfig(protocol_version="1.0.1")
