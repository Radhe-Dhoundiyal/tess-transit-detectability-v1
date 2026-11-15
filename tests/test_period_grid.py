"""Grid geometry, shared-kernel compatibility and post-search endpoint checks."""
from dataclasses import replace
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from tess_detectability.bls_grid import array_sha256, period_grid
from tess_detectability.bls_search import run_blind_search, run_grid_search
from tess_detectability.grid_comparison import classify_injection, host_bootstrap
from tess_detectability.period_grid import alternative_period_grid
from tess_detectability.recovery_config import FROZEN_RECOVERY_CONFIG as CONFIG

ROOT = Path(__file__).resolve().parents[1]


def original_runner():
    spec = importlib.util.spec_from_file_location(
        "tess_detectability.original_bls_runner", ROOT / "provenance/v1_source/bls_search.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.run_blind_search


@pytest.mark.parametrize("span", [8.0, 27.0, 100.0, 1400.0])
def test_union_grid_preserves_v1_nodes_and_bounds_duration_drift(span):
    old = period_grid(span, CONFIG)
    new = alternative_period_grid(span, CONFIG)
    np.testing.assert_array_equal(new[np.searchsorted(new, old)], old)
    assert new.dtype == np.float64 and np.all(np.diff(new) > 0)
    assert new[0] == CONFIG.minimum_period_days
    assert new[-1] == min(CONFIG.maximum_period_days, span / 2)
    # Adjacent log nodes bound fractional period error by d_min/(2*T).
    assert np.max(np.diff(new) / new[:-1]) <= min(CONFIG.durations_days) / (2 * span) * (1 + 1e-9)


@pytest.mark.parametrize("span", [float("nan"), float("inf"), -1, 0.5, 0.6])
def test_unusable_spans_are_empty(span):
    assert alternative_period_grid(span, CONFIG).size == 0


@pytest.mark.parametrize("oversampling", [0, -1, float("nan"), float("inf")])
def test_invalid_oversampling_is_rejected(oversampling):
    with pytest.raises(ValueError):
        alternative_period_grid(27, CONFIG, oversampling)


def test_excessive_grid_fails_before_allocation_instead_of_capping():
    with pytest.raises(MemoryError, match="not silently capped"):
        alternative_period_grid(1e8, CONFIG)


@pytest.mark.parametrize("span", [8.0, 27.0])
def test_historical_api_is_bit_identical_to_preserved_v1(span):
    rng = np.random.default_rng(631)
    time = np.linspace(0, span, 200)
    flux = rng.normal(0, 0.0001, len(time)) - 0.002 * (time % 2.3 < .09)
    expected, old_summary = original_runner()(time, flux, CONFIG)
    actual, summary = run_blind_search(time, flux, CONFIG)
    pd.testing.assert_frame_equal(actual, expected, check_exact=True)
    assert summary == old_summary


def test_chunking_preserves_grid_and_candidate_precision():
    config = replace(CONFIG, minimum_grid_points=128, maximum_grid_points=128,
                     maximum_period_days=3, durations_days=(.04, .09))
    time = np.linspace(0, 8, 400)
    flux = np.random.default_rng(91).normal(0, .0001, len(time)) - .003 * (time % 1.7 < .09)
    whole, _, whole_arrays = run_grid_search(time, flux, grid_kind="v1.1", config=config, chunk_size=None)
    parts, summary, arrays = run_grid_search(time, flux, grid_kind="v1.1", config=config, chunk_size=127)
    assert summary["chunk_size"] == 127
    assert summary["grid_array_sha256"] == array_sha256(whole_arrays["period"])
    for field in arrays:
        np.testing.assert_allclose(arrays[field], whole_arrays[field], rtol=1e-10, atol=1e-10)
    pd.testing.assert_frame_equal(parts, whole, check_exact=False, rtol=1e-10, atol=1e-10)


def test_grid_choice_is_explicit_and_search_has_no_truth_argument():
    time = np.arange(100) / 10
    with pytest.raises(TypeError):
        run_grid_search(time, np.zeros(100), config=CONFIG)
    with pytest.raises(TypeError):
        run_grid_search(time, np.zeros(100), grid_kind="v1.1", config=CONFIG, truth={})
    with pytest.raises(ValueError):
        run_grid_search(time, np.zeros(100), grid_kind="typo", config=CONFIG)
    for chunk in (0, -1, 1.2, True):
        with pytest.raises(ValueError):
            run_grid_search(time, np.zeros(100), grid_kind="v1.1", config=CONFIG, chunk_size=chunk)


def test_literal_rank_one_remains_distinct_from_winning_direct_assignment():
    # The smaller drift wins before epoch agreement. Literal rank one is a diagnostic.
    peaks = pd.DataFrame({"candidate_rank": [1, 2], "candidate_period": [2.001, 2.0],
                          "candidate_transit_time": [.01, .5], "candidate_duration": [.1, .1]})
    outcome = classify_injection(peaks, {"period": 2., "epoch": 0., "duration": .1}, 20.)
    assert outcome["direct_top1_literal"] and outcome["direct_any_qualifying_top10"]
    assert not outcome["direct_top10"] and outcome["recovery_class"] == "NOT_RECOVERED"


def test_single_host_does_not_produce_an_uncertainty_interval():
    row = {"trial_id": "toy", "selection_unit_id": "one", "baseline_direct_top10": False,
           "alternative_direct_top10": True}
    for method in ("baseline", "alternative"):
        row.update({f"{method}_{key}": 0 for key in ("direct_top1_literal", "harmonic", "alias", "unmatched", "cpu_seconds", "wall_seconds")})
    result = host_bootstrap(pd.DataFrame([row]), replicates=20)
    assert result["difference_percentile_95_ci"] is None
    assert result["interval_status"] == "NOT_ESTIMABLE_WITH_ONE_HOST"


def test_saved_peaks_and_host_bootstrap_reproduce_every_endpoint():
    spec = importlib.util.spec_from_file_location("grid_verifier", ROOT / "scripts/verify_grid_comparison.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    summary = module.verify_records()
    assert summary["extension"]["paired_losses"] == 1
    assert summary["original_exploratory"]["trials"] == 32
