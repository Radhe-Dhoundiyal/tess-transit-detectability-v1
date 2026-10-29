"""Focused tests for new public boundaries and preserved scientific evidence."""
import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from tess_detectability.demonstration import normalization_case
from tess_detectability.grouped_validation import grouped_cv
from tess_detectability.modeling import scaling, fit_penalized, predict
from tess_detectability.snr import expected_snr

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("depth", [0, 100, 500])
def test_example_executes_original_depth_contract(depth):
    result = normalization_case(depth)
    assert result["requested_depth_ppm"] == depth
    assert abs(result["realized_depth_ppm"] - depth) < 1e-6
    assert result["normalized_model"][0] == result["normalized_model"][-1] == 1.0
    assert result["classification"] == "NEW_EXPLICITLY_SYNTHETIC_CODE_DEMONSTRATION"


def test_snr_units_and_nonpositive_scatter():
    assert expected_snr(100, 100, 0.001) == pytest.approx(1.0)
    assert np.isnan(expected_snr(100, 100, 0))
    assert np.isnan(expected_snr(100, 100, -0.001))


def test_group_leakage_is_rejected_before_fit():
    frame = pd.DataFrame({"target_id": ["A", "A", "B", "B"],
                          "trial_id": ["a", "b", "c", "d"], "direct_recovery": [0, 1, 0, 1]})
    with pytest.raises(ValueError, match="more than one"):
        grouped_cv(frame, pd.Series([0, 1, 0, 1]))
    with pytest.raises(ValueError, match="index"):
        grouped_cv(frame, pd.Series([0, 0, 1, 1], index=[4, 5, 6, 7]))


def test_scaling_is_fitted_on_training_values():
    train = pd.DataFrame({"x": [0.0, 2.0]})
    assert scaling(train, ["x"]) == {"x": (1.0, 1.0)}
    with pytest.raises(RuntimeError, match="Non-variable"):
        scaling(pd.DataFrame({"x": [1.0, 1.0]}), ["x"])


def test_original_optimizer_on_tiny_explicitly_synthetic_fixture():
    x = np.column_stack([np.ones(8), np.arange(-4, 4)])
    fitted = fit_penalized(x, np.array([0, 0, 0, 0, 1, 1, 1, 1]), ["Intercept", "x"])
    assert fitted["converged"]
    probability = predict(fitted, x)
    assert np.all(np.isfinite(probability)) and np.all(np.diff(probability) > 0)


def test_grouped_cv_runs_on_tiny_synthetic_targets():
    target = np.repeat(np.arange(8), 2)
    index = np.arange(16)
    frame = pd.DataFrame({
        "trial_id": [f"toy-{v}" for v in index], "target_id": target,
        "log10_expected_snr": index / 10, "log10_period_days": np.sin(index),
        "observed_transit_count": 3 + target, "tess_magnitude": 8 + np.cos(index),
        "sector_count": 1 + target % 4, "log10_baseline_days": np.log10(30 + target),
        "cadence_indicator": target % 2, "difficulty_stratum": "EASY",
        "direct_recovery": index % 2,
    })
    predictions, diagnostics = grouped_cv(frame, pd.Series(target // 2))
    assert len(predictions) == 16 and len(diagnostics) == 4
    assert predictions.trial_id.nunique() == 16
    assert predictions.training_target_count.eq(6).all()
    assert predictions.validation_target_count.eq(2).all()
    assert all(row["converged"] for row in diagnostics)


def test_demo_server_calls_code_and_serves_only_allowed_assets():
    import http.client
    import json
    import threading
    spec = importlib.util.spec_from_file_location("demo_server_test", ROOT / "demo/serve_demo.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    server = module.ThreadingHTTPServer(("127.0.0.1", 0), module.Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
    try:
        connection.request("GET", "/api/normalization?case=100")
        response = connection.getresponse()
        result = json.loads(response.read())
        assert response.status == 200 and result["max_error_ppm"] < 1e-6
        for path, status in [("/api/normalization?case=17", 400),
                             ("/api/normalization?case=100&case=500", 400),
                             ("/inputs/recorded_data.json", 404),
                             ("/../LICENSE", 404), ("/archive/", 404), ("/", 200)]:
            connection.request("GET", path)
            response = connection.getresponse()
            response.read()
            assert response.status == status
    finally:
        connection.close()
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_saved_science_and_source_definitions():
    spec = importlib.util.spec_from_file_location("candidate_verifier", ROOT / "scripts/verify_project.py")
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    assert verifier.verify_science()["synthetic_direct"] == "98/320"
    assert verifier.verify_sources() >= 40
    assert verifier.verify_links() >= 10


def test_current_citation_and_package_versions_agree():
    import importlib.metadata
    import tomllib
    import yaml
    import tess_detectability
    from packaging.version import Version
    citation = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    package = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert citation["cff-version"] == "1.2.0" and citation["type"] == "software"
    assert citation["authors"][0]["family-names"] == "Dhoundiyal"
    assert "date-released" not in citation and "doi" not in citation
    assert citation["repository-code"] == package["urls"]["Repository"]
    assert Version(citation["version"]) == Version(package["version"]) == Version(tess_detectability.__version__)
    assert Version(importlib.metadata.version("tess-detectability")) == Version(package["version"])
