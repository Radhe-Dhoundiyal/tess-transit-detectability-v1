"""Deterministic probability-grid row processing for Phase 6B.1."""
from __future__ import annotations

from collections.abc import Callable, Sequence

import pandas as pd


def process_probability_grid(
    frame: pd.DataFrame,
    required_columns: Sequence[str],
    evaluator: Callable[[dict], dict],
) -> list[dict]:
    """Validate and evaluate grid records in original row order without mutation."""
    if not isinstance(frame, pd.DataFrame):
        raise TypeError("frame must be a pandas DataFrame")
    missing = [name for name in required_columns if name not in frame.columns]
    if missing:
        raise ValueError(f"missing required grid columns: {missing}")
    before_columns = tuple(frame.columns)
    before_index = frame.index.copy()
    records = frame.to_dict(orient="records")
    output = [evaluator(record.copy()) for record in records]
    if tuple(frame.columns) != before_columns or not frame.index.equals(before_index):
        raise RuntimeError("grid evaluator mutated DataFrame structure")
    if len(output) != len(frame):
        raise RuntimeError("grid evaluator did not preserve row count")
    return output
