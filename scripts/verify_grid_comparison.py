"""Recount saved V1.1 peaks, paired endpoints and descriptive host intervals."""
import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

from tess_detectability.bls_grid import array_sha256, period_grid
from tess_detectability.grid_comparison import classify_injection, host_bootstrap
from tess_detectability.period_grid import alternative_period_grid
from tess_detectability.recovery_config import FROZEN_RECOVERY_CONFIG as CONFIG
from tess_detectability.recovery_matching import match_target

ROOT = Path(__file__).resolve().parents[1]
RECORDS = ROOT / "data/records"
SUMMARY = ROOT / "results/tables/period_grid_summary_v1_1_0.json"


def read(name):
    return pd.read_csv(RECORDS / name, float_precision="round_trip")


def summarize(frame):
    return {name: host_bootstrap(group) for name, group in (
        ("original_exploratory", frame[frame.cohort.eq("original_exploratory")]),
        ("extension", frame[frame.cohort.eq("extension")]),
        ("combined_finite_benchmark", frame),
    )}


def verify_known():
    truths = read("period_grid_known_truth_v1_1_0.csv")
    peaks = read("period_grid_known_candidates_v1_1_0.csv")
    saved = read("period_grid_known_subset_v1_1_0.csv").set_index("planet_name")
    direct = {"baseline": 0, "alternative": 0}
    eligible_count = 0
    for unit, truth in truths.groupby("selection_unit_id"):
        for method in direct:
            candidates = peaks[peaks.selection_unit_id.eq(unit) & peaks.method.eq(method)]
            span = float(candidates.matching_baseline_days.iloc[0])
            maximum = min(CONFIG.maximum_period_days, span * CONFIG.maximum_baseline_fraction)
            assigned, pairs = match_target(candidates, truth, span, CONFIG.minimum_period_days, maximum, CONFIG)
            for index, row in truth.iterrows():
                eligible = CONFIG.minimum_period_days <= row.catalogue_period <= maximum
                if method == "baseline":
                    eligible_count += int(eligible)
                match = assigned[assigned.truth_index.eq(index)] if not assigned.empty else assigned
                status = "NOT_RECOVERED"
                if not eligible:
                    status = "OUTSIDE_SEARCH_RANGE"
                elif not match.empty:
                    winner = match.iloc[0]
                    if winner.match_class == "DIRECT_PERIOD_RECOVERY":
                        status = "DIRECTLY_RECOVERED" if winner.epoch_matches else "NOT_RECOVERED"
                    elif winner.match_class == "DAILY_OR_WINDOW_ALIAS":
                        status = "ALIAS_RECOVERED"
                    else:
                        status = "HARMONICALLY_RECOVERED"
                expected = saved.loc[row.planet_name]
                assert status == expected[f"status_{method}"], (row.planet_name, method)
                assert eligible == expected.eligible
                if not pairs.empty:
                    qualifying = pairs[pairs.truth_index.eq(index) & pairs.match_class.eq("DIRECT_PERIOD_RECOVERY") & pairs.epoch_matches]
                    assert bool(qualifying.candidate_rank.eq(1).any()) == expected[f"direct_top1_literal_{method}"]
                direct[method] += int(status == "DIRECTLY_RECOVERED")
    assert eligible_count == 3 and direct == {"baseline": 0, "alternative": 2}
    return {"selected_hosts": int(truths.selection_unit_id.nunique()), "catalogue_entries": len(truths),
            "eligible_signals": eligible_count, "baseline_direct": direct["baseline"], "alternative_direct": direct["alternative"]}


def verify_records(*, check_manifest=True):
    if check_manifest:
        manifest = json.loads((ROOT / "provenance/period_grid_v1_1_0.json").read_text(encoding="utf-8"))
        for path, expected in manifest["sha256"].items():
            assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected, path
    frame = read("period_grid_pairs_v1_1_0.csv")
    peaks = read("period_grid_candidates_v1_1_0.csv")
    truth = read("injection_recovery_results_v1_0_2.csv").set_index("trial_id")
    assert len(frame) == 320 and frame.trial_id.nunique() == 320
    assert set(frame.trial_id) == set(truth.index)
    assert set(peaks.trial_id) == set(frame.trial_id) and len(peaks) == 6400
    assert frame.groupby("selection_unit_id").size().eq(8).all()
    assert frame.groupby("selection_unit_id").cohort.nunique().eq(1).all()
    assert set(frame.cohort) == {"original_exploratory", "extension"}
    grouped_peaks = dict(tuple(peaks.groupby(["trial_id", "method"])))
    grids = {}
    for row in frame.to_dict("records"):
        trial = truth.loc[row["trial_id"]].to_dict()
        assert trial["selection_unit_id"] == row["selection_unit_id"]
        # Keep execution precision separate from the rounded historical summary export.
        trial["epoch"] = row["injection_epoch_btjd"]
        trial["period"] = row["injection_period_days"]
        trial["duration"] = row["injection_duration_days"]
        for method in ("baseline", "alternative"):
            candidates = grouped_peaks[row["trial_id"], method]
            assert candidates.candidate_rank.tolist() == list(range(1, 11))
            actual = classify_injection(candidates, trial, row["matching_baseline_days"])
            for field, value in actual.items():
                assert value == row[f"{method}_{field}"], (row["trial_id"], method, field)
            if method == "baseline":
                assert actual["recovery_class"] == trial["recovery_class"]
            key = method, row["search_span_days"]
            if key not in grids:
                grid = (period_grid if method == "baseline" else alternative_period_grid)(key[1], CONFIG)
                grids[key] = len(grid), array_sha256(grid)
            assert grids[key] == (row[f"{method}_period_grid_count"], row[f"{method}_grid_array_sha256"])
            assert row[f"{method}_cpu_seconds"] >= 0 and row[f"{method}_wall_seconds"] > 0
            assert row[f"{method}_peak_rss_sampled_bytes"] > 0
    summary = summarize(frame)
    combined = summary["combined_finite_benchmark"]
    assert (combined["baseline_direct"], combined["alternative_direct"], combined["paired_gains"], combined["paired_losses"]) == (98, 117, 20, 1)
    assert combined["difference_percentile_95_ci"] == [0.028125, 0.096875]
    assert (combined["baseline_direct_top1_literal"], combined["alternative_direct_top1_literal"]) == (72, 94)
    assert verify_known()["eligible_signals"] == 3
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-summary", action="store_true", help="recreate the derived summary after verification")
    args = parser.parse_args()
    summary = verify_records(check_manifest=not args.write_summary)
    if args.write_summary:
        SUMMARY.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")
    else:
        assert summary == json.loads(SUMMARY.read_text(encoding="utf-8"))
    print(json.dumps(summary, indent=2))
