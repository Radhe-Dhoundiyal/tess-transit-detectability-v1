"""Serve the explorer's allowlisted assets and run its depth example on loopback."""
import argparse
import csv
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from tess_detectability.demonstration import normalization_case

ROOT = Path(__file__).resolve().parent
ASSETS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/grid_comparison.js": ("grid_comparison.js", "text/javascript; charset=utf-8"),
    "/recorded_data.js": ("recorded_data.js", "text/javascript; charset=utf-8"),
    "/curve_data.js": ("curve_data.js", "text/javascript; charset=utf-8"),
    "/calibration.png": ("calibration.png", "image/png"),
    "/results/figures/period_grid_recovery_v1_1_0.png": (
        "../results/figures/period_grid_recovery_v1_1_0.png", "image/png"),
    "/results/figures/period_grid_hosts_v1_1_0.png": (
        "../results/figures/period_grid_hosts_v1_1_0.png", "image/png"),
}


def grid_comparison():
    records_path = ROOT.parent / "data/records/period_grid_pairs_v1_1_0.csv"
    with records_path.open(encoding="utf-8", newline="") as stream:
        records = list(csv.DictReader(stream))
    identity = ("trial_id", "host_name", "cohort", "baseline_recovery_class", "alternative_recovery_class")
    endpoints = ("baseline_direct_top10", "alternative_direct_top10",
                 "baseline_direct_top1_literal", "alternative_direct_top1_literal")
    rows = [{**{key: row[key] for key in identity},
             **{key: row[key] == "True" for key in endpoints}} for row in records]
    summary_path = ROOT.parent / "results/tables/period_grid_summary_v1_1_0.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))["combined_finite_benchmark"]
    return {"rows": rows, "summary": summary}


class Handler(BaseHTTPRequestHandler):
    def respond(self, status, body, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlsplit(self.path)
        if url.path == "/api/normalization":
            query = parse_qs(url.query, keep_blank_values=True)
            if set(query) != {"case"} or query["case"] not in (["0"], ["100"], ["500"]):
                self.respond(400, b'{"error":"Choose case 0, 100 or 500"}')
                return
            try:
                output = normalization_case(float(query["case"][0]))
                self.respond(200, json.dumps(output, allow_nan=False).encode())
            except Exception:
                self.respond(500, b'{"error":"Function execution failed; no result substituted"}')
        elif url.path == "/api/grid-comparison":
            try:
                self.respond(200, json.dumps(grid_comparison(), allow_nan=False).encode())
            except Exception:
                self.respond(500, b'{"error":"Saved comparison unavailable; no result substituted"}')
        elif url.path == "/api/health":
            self.respond(200, b'{"app":"TESS_SAVED_RECORDS","bind":"127.0.0.1"}')
        elif url.path in ASSETS:
            filename, content_type = ASSETS[url.path]
            self.respond(200, (ROOT / filename).read_bytes(), content_type)
        else:
            self.respond(404, b'{"error":"Not found"}')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8783)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        print(json.dumps({"cases": [normalization_case(v) for v in (0, 100, 500)]}, indent=2))
    else:
        print(f"Saved-record explorer: http://127.0.0.1:{args.port}/index.html", flush=True)
        ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()
