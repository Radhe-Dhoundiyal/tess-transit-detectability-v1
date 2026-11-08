"""Check saved research records and links offline, with optional source provenance."""
import argparse
from collections import Counter
from pathlib import Path
import ast
import csv
import hashlib
import json
import math
import re
import struct
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path):
    with (ROOT / path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def verify_science():
    real = rows("results/tables/transit_recovery_planet_results.csv")
    synthetic = rows("data/records/injection_recovery_results_v1_0_2.csv")
    assert len(real) == 70 and len({r["planet_name"] for r in real}) == 70
    assert Counter(r["planet_recovery_status"] for r in real) == {
        "DIRECTLY_RECOVERED": 15, "HARMONICALLY_RECOVERED": 10,
        "ALIAS_RECOVERED": 1, "NOT_RECOVERED": 25, "OUTSIDE_SEARCH_RANGE": 19,
    }
    assert sum(r["primary_recovery_success"] == "True" for r in real) == 15
    assert len(synthetic) == 320 and len({r["trial_id"] for r in synthetic}) == 320
    assert Counter(r["recovery_class"] for r in synthetic) == {
        "DIRECT_RECOVERY": 98, "HALF_PERIOD_HARMONIC_RECOVERY": 6,
        "DOUBLE_PERIOD_HARMONIC_RECOVERY": 5, "OTHER_INTEGER_HARMONIC_RECOVERY": 14,
        "ALIAS_RECOVERY": 12, "NOT_RECOVERED": 185,
    }
    assert sum(r["primary_recovery_success"] == "True" for r in synthetic) == 98
    assert sum(r["top10_direct_or_harmonic_recovery"] == "True" for r in synthetic) == 123
    folds = rows("results/tables/detectability_cv_fold_assignment_v1_0_0.csv")
    assert len(folds) == 320 and {r["trial_id"] for r in folds} == {r["trial_id"] for r in synthetic}
    by_target = {}
    for row in folds:
        by_target.setdefault(row["target_id"], set()).add(row["fold"])
    assert len(by_target) == 40 and all(len(f) == 1 for f in by_target.values())
    assert len({r["fold"] for r in folds}) == 8
    fold_map = {r["trial_id"]: r for r in folds}
    trial_map = {r["trial_id"]: r for r in synthetic}
    predictions = rows("data/records/detectability_oof_predictions_v1_0_1.csv")
    assert len(predictions) == 1280
    groups = {}
    for prediction in predictions:
        trial = trial_map[prediction["trial_id"]]
        assignment = fold_map[prediction["trial_id"]]
        assert prediction["target_id"] == assignment["target_id"] == trial["selection_unit_id"]
        assert prediction["fold"] == assignment["fold"]
        assert prediction["training_target_count"] == "35" and prediction["validation_target_count"] == "5"
        endpoint = "primary_recovery_success" if prediction["response"] == "direct_recovery" else "top10_direct_or_harmonic_recovery"
        assert int(prediction["observed_outcome"]) == int(trial[endpoint] == "True")
        groups.setdefault((prediction["response"], prediction["model_specification"]), []).append(prediction)
    performance = rows("results/tables/detectability_model_performance_v1_0_1.csv")
    assert len(groups) == 4
    for group, values in groups.items():
        assert len(values) == 320 and len({r["trial_id"] for r in values}) == 320
        recorded = next(r for r in performance if (r["response"], r["specification"]) == group)
        losses, errors = [], []
        for value in values:
            y, p = int(value["observed_outcome"]), float(value["predicted_probability"])
            assert 0 < p < 1
            losses.append(-y * math.log(p) - (1-y) * math.log1p(-p))
            errors.append((y-p)**2)
        assert abs(sum(losses)/320 - float(recorded["log_loss"])) < 1e-12
        assert abs(sum(errors)/320 - float(recorded["brier_score"])) < 1e-12
    data = json.loads((ROOT / "demo/inputs/recorded_data.json").read_text(encoding="utf-8"))
    assert {r["id"]: r["raw"] for r in data["real"]} == {r["planet_name"]: r for r in real}
    assert {r["id"]: r["raw"] for r in data["synthetic"]} == {r["trial_id"]: r for r in synthetic}
    assert data["calibration"] == rows("results/tables/detectability_calibration_v1_0_1.csv")
    files = {"real": "results/tables/transit_recovery_planet_results.csv",
             "synthetic": "data/records/injection_recovery_results_v1_0_2.csv",
             "calibration": "results/tables/detectability_calibration_v1_0_1.csv"}
    for label, path in files.items():
        assert sha(ROOT / path).upper() == data["sources"][label]["sha256"]
    failed_run = json.loads((ROOT / "results/development/injection_recovery_failure_v1_0_0.json").read_text())
    assert failed_run["completed_trials"] == 320 and failed_run["bls_execution_count"] == 400
    assert failed_run["derived_completeness_scientifically_valid"] is False
    assert failed_run["completion_marker_written"] is False
    failure = json.loads((ROOT / "results/development/injection_recovery_amendment_failure_v1_0_1.json").read_text())
    assert failure["depth_failures"] == 320 and failure["bls_execution_count"] == 0
    return {"known_direct": "15/51", "known_outside": 19, "synthetic_direct": "98/320",
            "synthetic_direct_or_harmonic": "123/320", "targets": 40, "folds": 8,
            "saved_predictions_checked": 1280, "saved_metric_pairs_recomputed": 4}


def source_entries():
    return json.loads((ROOT / "provenance/source_manifest.json").read_text(encoding="utf-8"))["files"]


def verify_source_bytes(item):
    path = ROOT / item["destination"]
    assert sha(path) == item["destination_sha256"], item["destination"]
    if item["transfer"] == "byte-identical":
        assert item["source_sha256"] == item["destination_sha256"], item["destination"]


def verify_record_hashes():
    """Authenticate saved inputs, outcomes, original methods and scientific figures."""
    recorded_demo_assets = {
        "demo/calibration.png",
        "demo/curve_data.js",
        "demo/inputs/CURVE_SOURCE.json",
        "demo/inputs/recorded_data.json",
        "demo/recorded_data.js",
    }
    records = [
        item for item in source_entries()
        if item["destination"].startswith(("data/records/", "docs/original/", "results/"))
        or item["destination"] in recorded_demo_assets
    ]
    for item in records:
        verify_source_bytes(item)
    return len(records)


def verify_sources():
    """Compare V1 source and retained tests with their published identities."""
    sources = [
        item for item in source_entries()
        if item["destination"].startswith(("src/", "provenance/v1_tests/"))
    ]
    for item in sources:
        verify_source_bytes(item)
        path = ROOT / item["destination"]
        nodes = None
        for segment in item.get("segments", []) + item.get("selected_methods", []):
            if nodes is None:
                nodes = list(ast.walk(ast.parse(path.read_bytes())))
            matches = [n for n in nodes if getattr(n, "name", None) == segment["name"]]
            if not matches:  # top-level constant assignment
                matches = [n for n in nodes if isinstance(n, ast.Assign) and
                           any(isinstance(t, ast.Name) and t.id == segment["name"] for t in n.targets)]
            assert len(matches) == 1, segment["name"]
            assert hashlib.sha256(ast.dump(matches[0], include_attributes=False).encode()).hexdigest() == segment["ast_sha256"], segment["name"]
    return len(sources)


def verify_links():
    checked = 0
    files = list(ROOT.glob("*.md")) + [ROOT / "LICENSE"]
    files += list((ROOT / "docs").glob("*.md")) + [ROOT / "demo/README.md"]
    for file in files:
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", file.read_text(encoding="utf-8")):
            url = urlsplit(target)
            if url.scheme or not url.path:
                continue
            path = (file.parent / unquote(url.path)).resolve()
            assert path.is_relative_to(ROOT.resolve()) and path.exists(), (file.relative_to(ROOT), target)
            checked += 1
    return checked


def verify_model_figures():
    """Check the retained V1 model figures against their recorded hashes."""
    figures = rows("provenance/detectability_existing_figure_integrity_v1_0_4.csv")
    assert len(figures) == 14
    assert len({item["path"] for item in figures}) == 14
    for item in figures:
        path = ROOT / item["path"]
        assert path.is_file() and path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"), item["path"]
        assert sha(path).upper() == item["sha256"], item["path"]
        assert path.stat().st_size == int(item["size_bytes"]), item["path"]
    return len(figures)


def verify_images():
    """Check authenticated preview bytes, dimensions and source-record paths."""
    images = json.loads((ROOT / "provenance/images.json").read_text(encoding="utf-8"))["images"]
    for item in images:
        image_path = ROOT / item["path"]
        data = image_path.read_bytes()
        assert sha(image_path) == item["sha256"] and len(data) == item["bytes"], item["path"]
        assert data[:8] == b"\x89PNG\r\n\x1a\n"
        assert list(struct.unpack(">II", data[16:24])) == item["dimensions"]
        position = 8
        while position < len(data):
            length = int.from_bytes(data[position:position+4], "big")
            chunk = data[position+4:position+8]
            value = data[position+8:position+8+length]
            assert chunk != b"eXIf", "Unexpected EXIF in preview"
            if chunk in (b"tEXt", b"iTXt", b"zTXt"):
                assert not re.search(rb"[A-Z]:[\\/]|[\w.+%-]+@[\w.-]+\.[A-Za-z]{2,}", value), "Personal metadata in preview"
            position += length + 12
        assert (ROOT / item["source_data"]).is_file()
    return len(images)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provenance", action="store_true",
                        help="also check V1 source identities, tests and saved model figures")
    args = parser.parse_args()
    report = {
        "historical_record_hashes": verify_record_hashes(),
        "science": verify_science(),
        "current_links": verify_links(),
        "images": verify_images(),
    }
    if args.provenance:
        report["sources"] = verify_sources()
        report["model_figures"] = verify_model_figures()
    print(json.dumps(report, indent=2))
