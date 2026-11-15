"""Post-search injection assignment and descriptive paired host bootstrap."""
from itertools import product

import numpy as np
import pandas as pd

from .recovery_config import FROZEN_RECOVERY_CONFIG
from .recovery_matching import compare_pair


def classify_injection(candidates, trial, baseline):
    truth = pd.Series({
        "catalogue_period": trial["period"], "catalogue_epoch_btjd": trial["epoch"],
        "catalogue_duration_days": trial["duration"],
    })
    pairs = [comparison for _, candidate in candidates.iterrows()
             if (comparison := compare_pair(
                 candidate, truth, baseline, FROZEN_RECOVERY_CONFIG)) is not None]
    ordered = sorted(pairs, key=lambda p: (
        p["match_precedence"],
        p["phase_drift"] if np.isfinite(p["phase_drift"]) else np.inf,
        p["epoch_offset"] if np.isfinite(p["epoch_offset"]) else np.inf,
        p["candidate_rank"],
    ))
    winner = ordered[0] if ordered else {}
    label = winner.get("match_class")
    labels = {
        "HALF_PERIOD_HARMONIC": "HALF_PERIOD_HARMONIC_RECOVERY",
        "DOUBLE_PERIOD_HARMONIC": "DOUBLE_PERIOD_HARMONIC_RECOVERY",
        "INTEGER_HARMONIC_OTHER": "OTHER_INTEGER_HARMONIC_RECOVERY",
        "DAILY_OR_WINDOW_ALIAS": "ALIAS_RECOVERY",
    }
    recovery = ("DIRECT_RECOVERY" if winner.get("epoch_matches") else "NOT_RECOVERED"
                ) if label == "DIRECT_PERIOD_RECOVERY" else labels.get(label, "NOT_RECOVERED")
    qualifying = [p for p in pairs if p["match_class"] == "DIRECT_PERIOD_RECOVERY"
                  and p["epoch_matches"]]
    direct = recovery == "DIRECT_RECOVERY"
    return {
        "recovery_class": recovery, "direct_top10": direct,
        "direct_top1_historical": bool(direct and winner.get("candidate_rank") == 1),
        "direct_top1_literal": any(p["candidate_rank"] == 1 for p in qualifying),
        "direct_any_qualifying_top10": bool(qualifying),
        "harmonic": "HARMONIC" in recovery, "alias": recovery == "ALIAS_RECOVERY",
        "unmatched": recovery == "NOT_RECOVERED",
    }


def host_bootstrap(frame, *, seed=20261111, replicates=100000):
    """Resample whole hosts with replacement, keeping every injection together."""
    if frame.empty or replicates < 1:
        raise ValueError("Nonempty paired records and positive replicates required")
    grouped = frame.groupby("selection_unit_id", sort=True).agg(
        n=("trial_id", "size"), old=("baseline_direct_top10", "sum"),
        new=("alternative_direct_top10", "sum"))
    n, old, new = (grouped[key].to_numpy(dtype=int) for key in ("n", "old", "new"))
    hosts = len(grouped)
    draws = np.random.default_rng(seed).integers(0, hosts, size=(replicates, hosts))
    delta = (new - old)[draws].sum(axis=1) / n[draws].sum(axis=1)
    # A second calculation uses host multiplicities rather than indexed sums.
    for indices, value in zip(draws[:1000], delta[:1000]):
        counts = np.bincount(indices, minlength=hosts)
        assert counts @ (new - old) / (counts @ n) == value
    result = {
        "trials": int(n.sum()), "hosts": hosts,
        "baseline_direct": int(old.sum()), "alternative_direct": int(new.sum()),
        "absolute_difference": float((new.sum() - old.sum()) / n.sum()),
        "paired_gains": int((~frame.baseline_direct_top10 & frame.alternative_direct_top10).sum()),
        "paired_losses": int((frame.baseline_direct_top10 & ~frame.alternative_direct_top10).sum()),
        "unchanged_primary": int((frame.baseline_direct_top10 == frame.alternative_direct_top10).sum()),
        "difference_percentile_95_ci": np.quantile(delta, [.025, .975]).tolist() if hosts > 1 else None,
        "bootstrap_seed": seed, "bootstrap_replicates": replicates,
        "reference_draw_checks": min(1000, replicates),
        "interval_status": "DESCRIPTIVE_EMPIRICAL_HOST_BOOTSTRAP" if hosts > 1 else "NOT_ESTIMABLE_WITH_ONE_HOST",
    }
    if 1 < hosts <= 5:
        exact = np.asarray(list(product(range(hosts), repeat=hosts)))
        values = (new - old)[exact].sum(axis=1) / n[exact].sum(axis=1)
        result["exact_empirical_bootstrap_percentile_95_ci"] = np.quantile(values, [.025, .975]).tolist()
    for method in ("baseline", "alternative"):
        for field in ("direct_top1_literal", "harmonic", "alias", "unmatched"):
            result[f"{method}_{field}"] = int(frame[f"{method}_{field}"].sum())
        result[f"{method}_search_cpu_seconds"] = float(frame[f"{method}_cpu_seconds"].sum())
        result[f"{method}_search_wall_seconds_sum"] = float(frame[f"{method}_wall_seconds"].sum())
    return result
