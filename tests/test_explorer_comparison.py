"""The comparison reads the canonical saved records without a second export."""
import csv
import importlib.util
import json
from pathlib import Path
import threading
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]


def server_module():
    spec = importlib.util.spec_from_file_location("comparison_server", ROOT / "demo/serve_demo.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_comparison_preserves_each_trial_and_both_endpoint_definitions():
    data = server_module().grid_comparison()
    with (ROOT / "data/records/period_grid_pairs_v1_1_0.csv").open(encoding="utf-8", newline="") as stream:
        saved = list(csv.DictReader(stream))
    assert len(data["rows"]) == len(saved) == 320
    for actual, expected in zip(data["rows"], saved):
        for key, value in actual.items():
            assert value == (expected[key] == "True" if isinstance(value, bool) else expected[key])
    rows = data["rows"]
    assert sum(row["cohort"] == "original_exploratory" for row in rows) == 32
    assert sum(not row["baseline_direct_top10"] and row["alternative_direct_top10"] for row in rows) == 20
    losses = [row["trial_id"] for row in rows if row["baseline_direct_top10"] and not row["alternative_direct_top10"]]
    assert losses == ["IR-36-07"]
    assert sum(row["baseline_direct_top1_literal"] for row in rows) == 72
    assert sum(row["alternative_direct_top1_literal"] for row in rows) == 94
    assert data["summary"]["difference_percentile_95_ci"] == [0.028125, 0.096875]


def test_comparison_endpoint_and_figures_are_allowlisted_assets():
    module = server_module()
    server = module.ThreadingHTTPServer(("127.0.0.1", 0), module.Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f"http://127.0.0.1:{server.server_port}"
        with urlopen(base + "/api/grid-comparison") as response:
            assert response.headers["Cache-Control"] == "no-store"
            assert json.load(response) == module.grid_comparison()
        for path in ("/grid_comparison.js", "/results/figures/period_grid_recovery_v1_1_0.png",
                     "/results/figures/period_grid_hosts_v1_1_0.png"):
            with urlopen(base + path) as response:
                filename, content_type = module.ASSETS[path]
                assert response.headers["Content-Type"] == content_type
                assert response.read() == (ROOT / "demo" / filename).read_bytes()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
