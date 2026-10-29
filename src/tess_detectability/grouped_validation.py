"""New public boundary checks around the unchanged V1 modeling functions."""
import numpy as np
import pandas as pd
from .modeling import cv


def grouped_cv(data, folds, response="direct_recovery", model="A", interactions=False):
    """Validate supplied target fold assignments, then call the original V1 CV.

    This helper does not generate a split or reproduce the historical fit.
    Numeric-cadence sensitivity is deliberately not exposed here.
    """
    if not isinstance(folds, pd.Series) or not folds.index.equals(data.index):
        raise ValueError("fold index must match the data index exactly")
    if folds.isna().any() or data.target_id.isna().any() or folds.nunique() < 2:
        raise ValueError("at least two complete folds and target identities required")
    if pd.DataFrame({"target": data.target_id, "fold": folds}).groupby("target").fold.nunique().max() != 1:
        raise ValueError("a target appears in more than one validation fold")
    if data.trial_id.duplicated().any():
        raise ValueError("trial identities must be unique")
    if model not in ("A", "B"):
        raise ValueError("model must be A or B")
    if not data[response].isin([0, 1]).all():
        raise ValueError("binary response required")
    return cv(data, folds, response, model, interactions)
