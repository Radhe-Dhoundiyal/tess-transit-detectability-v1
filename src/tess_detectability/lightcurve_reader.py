"""Read registered SPOC light-curve columns without modifying raw FITS."""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
from astropy.io import fits

from .preprocessing_config import PreprocessingConfig


def _array(table, name: str, length: int, *, dtype=float) -> np.ndarray:
    if name not in (table.names or []):
        return np.full(length, np.nan, dtype=dtype)
    return np.asarray(table[name], dtype=dtype)


def inspect_flux_coverage(path: Path, config: PreprocessingConfig) -> dict[str, object]:
    """Read only registered structural columns and classify source usability."""
    with fits.open(path, mode="readonly", memmap=True, checksum=False) as hdus:
        table_hdu = next(hdu for hdu in hdus
                         if isinstance(hdu, (fits.BinTableHDU, fits.TableHDU))
                         and hdu.data is not None)
        table = table_hdu.data
        length = len(table)
        names = set(table.names or [])
        primary = _array(table, config.primary_flux, length)
        fallback = _array(table, config.fallback_flux, length)
        primary_count = int(np.isfinite(primary).sum())
        fallback_count = int(np.isfinite(fallback).sum())
        primary_fraction = float(primary_count / length) if length else 0.0
        fallback_fraction = float(fallback_count / length) if length else 0.0
        if config.primary_flux in names and \
                primary_fraction >= config.minimum_flux_finite_fraction:
            selected = config.primary_flux
            status = "PROCESS"
            reason = ""
        elif config.fallback_flux in names and \
                fallback_fraction >= config.minimum_flux_finite_fraction:
            selected = config.fallback_flux
            status = "PROCESS"
            reason = ""
        else:
            selected = ""
            status = "EXCLUDED_STRUCTURALLY_UNUSABLE_FLUX_COVERAGE"
            reason = "STRUCTURALLY_UNUSABLE_ALL_REGISTERED_FLUX_SOURCES"
        return {
            "total_count": length,
            "pdcsap_finite_count": primary_count,
            "pdcsap_total_count": length,
            "pdcsap_finite_fraction": primary_fraction,
            "sap_finite_count": fallback_count,
            "sap_total_count": length,
            "sap_finite_fraction": fallback_fraction,
            "selected_flux_source": selected,
            "file_status": status,
            "exclusion_reason": reason,
        }


def read_lightcurve(path: Path, config: PreprocessingConfig) -> tuple[
        pd.DataFrame, dict[str, object]]:
    with fits.open(path, mode="readonly", memmap=True, checksum=False) as hdus:
        table_hdu = next(hdu for hdu in hdus
                         if isinstance(hdu, (fits.BinTableHDU, fits.TableHDU))
                         and hdu.data is not None)
        table = table_hdu.data
        length = len(table)
        names = set(table.names or [])
        primary = _array(table, config.primary_flux, length)
        primary_fraction = float(np.isfinite(primary).sum() / length) if length else 0.0
        if config.primary_flux in names and primary_fraction >= config.minimum_flux_finite_fraction:
            flux_source = config.primary_flux
            uncertainty_source = (
                config.primary_uncertainty if config.primary_uncertainty in names else "NONE")
            fallback_reason = ""
        else:
            fallback = _array(table, config.fallback_flux, length)
            fallback_fraction = float(np.isfinite(fallback).sum() / length) if length else 0.0
            if config.fallback_flux not in names or fallback_fraction < config.minimum_flux_finite_fraction:
                raise ValueError("Both registered flux sources are structurally unusable")
            flux_source = config.fallback_flux
            uncertainty_source = (
                config.fallback_uncertainty if config.fallback_uncertainty in names else "NONE")
            if config.primary_flux not in names:
                fallback_reason = "PRIMARY_COLUMN_ABSENT"
            elif np.isfinite(primary).sum() == 0:
                fallback_reason = "PRIMARY_ZERO_FINITE_VALUES"
            else:
                fallback_reason = "PRIMARY_FINITE_COVERAGE_BELOW_MINIMUM"
        selected_flux = _array(table, flux_source, length)
        selected_error = (
            _array(table, uncertainty_source, length)
            if uncertainty_source != "NONE" else np.full(length, np.nan))
        quality = _array(table, "QUALITY", length, dtype=float)
        frame = pd.DataFrame({
            "original_row_index": np.arange(length, dtype=np.int64),
            "time_btjd": _array(table, "TIME", length),
            "raw_flux": selected_flux,
            "raw_flux_err": selected_error,
            "quality": pd.Series(quality).astype("Int64"),
        })
        decision = {
            "input_rows": length,
            "available_columns": "|".join(table.names or []),
            "flux_source": flux_source,
            "uncertainty_source": uncertainty_source,
            "primary_finite_fraction": primary_fraction,
            "fallback_reason": fallback_reason,
        }
        return frame, decision
