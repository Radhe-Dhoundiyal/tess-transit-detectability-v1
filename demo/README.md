# Saved-results explorer

After installation, run `python demo/serve_demo.py` from the repository root
and open `http://127.0.0.1:8783/index.html`. The server binds only to loopback.
Stop it with Ctrl+C. It serves a fixed asset list and writes no output files.
`python demo/serve_demo.py --check` executes the three small normalization
cases without starting a server.

This is a present-day viewer of 70 historical catalogue-match rows, 320
accepted synthetic trial rows and ten original calibration bins. The observed
WASP-127 curve is a deterministic 8,000-row display subset of saved processed
mission observations, not a reconstructed transit or a new observation.
Missing case-linked curves remain missing. No synthetic injected-flux arrays
are supplied or fabricated. The normalization tab calls installed original
V1 code on five new synthetic samples; no search, matching or model fit runs.

The viewer is self-contained. Opening `index.html` directly works for saved
records but clearly reports that function execution needs the server.
No external fonts, scripts, credentials or network assets are required.
The original 2026-10-28 viewer is curated here; its new server imports the
installed package, and private absolute source paths have been replaced
with logical labels. Source hashes, original saved row values and curve
values are checked separately from these presentation changes.

The original dataset path labels inside saved rows refer to provenance in
the historical private project, not files promised by this small candidate.
Public counterparts are `results/tables/transit_recovery_planet_results.csv`,
`data/records/injection_recovery_results_v1_0_2.csv` and
`results/tables/detectability_calibration_v1_0_1.csv`.
Retain NASA/TESS/MAST and Exoplanet Archive attribution. Mission data and
factual metadata are not student-created data or relicensed software.
