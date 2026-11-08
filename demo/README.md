# Saved-results explorer

After installation, run `python demo/serve_demo.py` from the repository root
and open `http://127.0.0.1:8783/index.html`. The server binds only to loopback.
Stop it with Ctrl+C. It serves a fixed asset list and writes no output files.
`python demo/serve_demo.py --check` executes the three small normalization
cases without starting a server.

The viewer displays 70 historical catalogue-match rows, 320 accepted
synthetic trials and ten original calibration bins. The WASP-127 curve
contains a deterministic 8,000-row subset of processed TESS observations.
Missing case-linked curves and injected-flux arrays remain unavailable.
Depth test calls the original V1 normalization function on five synthetic samples.

The viewer is self-contained. Opening `index.html` directly works for saved
records but clearly reports that function execution needs the server.
No external fonts, scripts, credentials or network assets are required.
The server imports the installed package. Saved rows and curves retain their
source identities, while the display uses logical labels for private paths.

Dataset path labels refer to the historical project.
Public counterparts are `results/tables/transit_recovery_planet_results.csv`,
`data/records/injection_recovery_results_v1_0_2.csv` and
`results/tables/detectability_calibration_v1_0_1.csv`.
Retain NASA/TESS/MAST and Exoplanet Archive attribution. Mission data and
factual metadata are not student-created data or relicensed software.
