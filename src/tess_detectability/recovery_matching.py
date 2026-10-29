"""Algorithmic truth matching performed only after blind publication."""
from __future__ import annotations

import math
import numpy as np
import pandas as pd

from .recovery_config import RecoveryConfig


LABELS = {
    1.0: "DIRECT_PERIOD_RECOVERY",
    0.5: "HALF_PERIOD_HARMONIC",
    2.0: "DOUBLE_PERIOD_HARMONIC",
    1.0 / 3.0: "INTEGER_HARMONIC_OTHER",
    3.0: "INTEGER_HARMONIC_OTHER",
    2.0 / 3.0: "INTEGER_HARMONIC_OTHER",
    1.5: "INTEGER_HARMONIC_OTHER",
}


def circular_offset(first: float, second: float, period: float) -> float:
    difference = abs(first - second) % period
    return min(difference, period - difference)


def compare_pair(candidate: pd.Series, truth: pd.Series, baseline: float,
                 config: RecoveryConfig) -> dict[str, object] | None:
    truth_period = float(truth.catalogue_period)
    candidate_period = float(candidate.candidate_period)
    matches = []
    for precedence, ratio in enumerate(config.harmonic_ratios):
        expected = truth_period * ratio
        drift = abs(candidate_period - expected) * baseline / expected ** 2
        if drift <= config.phase_drift_tolerance:
            matches.append((precedence, ratio, expected, drift))
    if not matches:
        truth_frequency = 1.0 / truth_period
        candidate_frequency = 1.0 / candidate_period
        alias = any(abs(abs(candidate_frequency - truth_frequency) - integer)
                    <= 1.0 / baseline for integer in (1, 2, 3))
        if not alias:
            return None
        precedence, ratio, expected, drift = 7, np.nan, truth_period, np.nan
        match_class = "DAILY_OR_WINDOW_ALIAS"
    else:
        precedence, ratio, expected, drift = min(matches)
        match_class = LABELS[ratio]
    truth_epoch = pd.to_numeric(pd.Series([truth.catalogue_epoch_btjd]),
                                errors="coerce").iloc[0]
    truth_duration_days = pd.to_numeric(
        pd.Series([truth.catalogue_duration_days]), errors="coerce").iloc[0]
    if np.isfinite(truth_epoch):
        epoch_offset = circular_offset(
            float(candidate.candidate_transit_time), float(truth_epoch), expected)
        tolerance = (
            config.epoch_duration_multiplier * float(truth_duration_days)
            if np.isfinite(truth_duration_days) and truth_duration_days > 0
            else config.epoch_fallback_period_fraction * truth_period)
        epoch_matches = epoch_offset <= tolerance
    else:
        epoch_offset = np.nan
        tolerance = np.nan
        epoch_matches = False
    duration_ratio = (
        float(candidate.candidate_duration) / float(truth_duration_days)
        if np.isfinite(truth_duration_days) and truth_duration_days > 0 else np.nan)
    duration_matches = (
        config.duration_ratio_min <= duration_ratio <= config.duration_ratio_max
        if np.isfinite(duration_ratio) else False)
    return {
        "candidate_rank": int(candidate.candidate_rank),
        "matched_candidate_period": candidate_period,
        "period_ratio": candidate_period / truth_period,
        "period_fractional_error": abs(candidate_period - truth_period) / truth_period,
        "phase_drift": drift, "epoch_offset": epoch_offset,
        "epoch_tolerance": tolerance,
        "epoch_matches": bool(epoch_matches),
        "epoch_offset_in_duration_units":
            epoch_offset / truth_duration_days
            if np.isfinite(epoch_offset) and np.isfinite(truth_duration_days)
            and truth_duration_days > 0 else np.nan,
        "duration_ratio": duration_ratio,
        "duration_matches": bool(duration_matches),
        "match_class": match_class, "match_precedence": precedence,
    }


def match_target(candidates: pd.DataFrame, truths: pd.DataFrame,
                 baseline: float, searched_min: float, searched_max: float,
                 config: RecoveryConfig) -> tuple[pd.DataFrame, pd.DataFrame]:
    pairs = []
    for truth_index, truth in truths.iterrows():
        period = pd.to_numeric(pd.Series([truth.catalogue_period]),
                               errors="coerce").iloc[0]
        if not np.isfinite(period) or period <= 0:
            continue
        if not (searched_min <= period <= searched_max):
            continue
        for _, candidate in candidates.iterrows():
            comparison = compare_pair(candidate, truth, baseline, config)
            if comparison is not None:
                pairs.append({
                    "truth_index": int(truth_index),
                    "planet_name": truth.planet_name, **comparison,
                })
    pairs_frame = pd.DataFrame(pairs)
    assigned = []
    used_truth = set()
    used_candidate = set()
    if not pairs_frame.empty:
        ordered = pairs_frame.sort_values([
            "match_precedence", "phase_drift", "epoch_offset",
            "candidate_rank", "planet_name", "matched_candidate_period"],
            kind="mergesort", na_position="last")
        for _, pair in ordered.iterrows():
            if pair.truth_index in used_truth or pair.candidate_rank in used_candidate:
                continue
            assigned.append(pair.to_dict())
            used_truth.add(pair.truth_index)
            used_candidate.add(pair.candidate_rank)
    return pd.DataFrame(assigned), pairs_frame
