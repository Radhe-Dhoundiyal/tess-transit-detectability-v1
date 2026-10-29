"""Deterministic sorting, duplicate resolution, and segmentation."""
from __future__ import annotations

import numpy as np
import pandas as pd


def duplicate_keep_mask(frame: pd.DataFrame) -> np.ndarray:
    """Keep one structurally valid row per exact TIME using frozen priority."""
    keep = np.zeros(len(frame), dtype=bool)
    eligible = frame.loc[frame.finite_time & frame.finite_flux].copy()
    if eligible.empty:
        return keep
    eligible["_quality_rank"] = pd.to_numeric(
        eligible.quality, errors="coerce").fillna(np.iinfo(np.int64).max)
    eligible["_quality_zero_rank"] = (~eligible.quality.eq(0)).astype(int)
    chosen = eligible.sort_values(
        ["time_btjd", "_quality_zero_rank", "_quality_rank", "original_row_index"],
        kind="mergesort").drop_duplicates("time_btjd", keep="first")
    keep[chosen.index.to_numpy(dtype=int)] = True
    return keep


def deterministic_sort(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result["_time_sort"] = pd.to_numeric(result.time_btjd, errors="coerce")
    result["_nonfinite_sort"] = ~np.isfinite(result["_time_sort"])
    result = result.sort_values(
        ["_nonfinite_sort", "_time_sort", "original_row_index"],
        kind="mergesort").drop(columns=["_time_sort", "_nonfinite_sort"])
    return result.reset_index(drop=True)


def assign_segments(frame: pd.DataFrame, *, cadence_seconds: int,
                    gap_multiplier: float) -> tuple[pd.Series, list[dict[str, object]]]:
    segment = pd.Series(pd.NA, index=frame.index, dtype="Int64")
    eligible = frame.index[frame.structural_keep & frame.quality_keep].tolist()
    audits: list[dict[str, object]] = []
    if not eligible:
        return segment, audits
    threshold_days = cadence_seconds * gap_multiplier / 86400.0
    current = 1
    previous_time = None
    previous_index = None
    for index in eligible:
        time = float(frame.at[index, "time_btjd"])
        delta = None if previous_time is None else time - previous_time
        if delta is not None and delta > threshold_days:
            audits.append({
                "previous_original_row_index": int(frame.at[previous_index,
                                                             "original_row_index"]),
                "next_original_row_index": int(frame.at[index, "original_row_index"]),
                "gap_days": delta,
                "gap_seconds": delta * 86400.0,
                "threshold_seconds": cadence_seconds * gap_multiplier,
                "new_segment_number": current + 1,
            })
            current += 1
        segment.at[index] = current
        previous_time = time
        previous_index = index
    return segment, audits
