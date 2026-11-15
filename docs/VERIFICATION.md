# Verification

Use Python 3.12 from the repository root. These commands run the numerical example, the focused tests and the saved-record checks:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install --index-url https://pypi.org/simple ".[test]"
.venv\Scripts\python.exe examples/normalize_depth.py
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe scripts/verify_project.py
```

The tests cover preprocessing, blind BLS candidates, catalogue matching, injection depth, host-grouped validation and the small local demo. The numerical example checks 0, 100 and 500 ppm on five synthetic samples (errors below `1e-6` ppm).

The verifier checks the saved evidence and its file identities, including the two original injection failures. It recounts **15/51** known-signal and **98/320** synthetic direct recoveries, checks all eight target-grouped folds, and recomputes four log-loss/Brier pairs from 1,280 saved predictions. It does **not** rerun the astronomical survey.

The [GitHub Actions workflow](../.github/workflows/verify.yml) runs these checks on Windows with Python 3.12; [Actions](https://github.com/Radhe-Dhoundiyal/tess-transit-detectability-v1/actions) shows actual run results. Browser checks also covered saved cases, trial-cell navigation, missing curves and the depth demo in Chromium. Browser tests are separate from this CI workflow.

## Optional source and figure checks

For additional checks, use:

```powershell
.venv\Scripts\python.exe scripts/verify_project.py --provenance
```

This checks original V1 source identities, the preserved V1 test sources and the
14 saved modeling figures against their recorded checksums.

The public package includes algorithms and selected saved records, not all original TESS inputs or production orchestration. See [limitations](LIMITATIONS.md).

## V1.1 saved-result checks

The project verifier also runs the V1.1 saved-result checks. To run them
separately:

```powershell
.venv\Scripts\python.exe scripts/verify_grid_comparison.py
```

This reclassifies all 6,400 retained injection peaks into the 320 paired
outcomes, checks the baseline against historical V1 rows, reconstructs the
grids and their float64 hashes, and recomputes all three cohort summaries.
It verifies the known subset separately from the historical 51-signal
denominator. The 100,000-draw host bootstrap uses seed `20261111`; independent
host-multiplicity sums check 1,000 draws and exhaustive four-host draws check
the exploratory interval. `--write-summary` regenerates the derived JSON
after the numerical checks, without bypassing endpoint assertions.

Tests cover exact V1-runner compatibility on small synthetic fixtures, union
grid inclusion, spacing, bounds and allocation failure, chunking tolerance,
explicit grid selection and separation of primary and literal rank-1 rules.
The original V1 tests remain included. The test extra explicitly declares
PyYAML and packaging, which the existing citation/version test imports.

To recreate the figures:

```powershell
.venv\Scripts\python.exe -m pip install --index-url https://pypi.org/simple ".[plots]"
.venv\Scripts\python.exe scripts/plot_grid_comparison.py
```

The [V1.1 manifest](../provenance/period_grid_v1_1_0.json) authenticates selected
records, summary, implementation, tests, figure generator and image bytes.
It records the originating research implementation identity, not a claim
that the refactored source produced the historical files. The selected
exports were checked against 640 saved checkpoint/candidate pairs and all
320 alternative injection periodogram hashes before inclusion. Private
checkpoints and periodograms are not bundled.

The included `input_array_sha256` identifies identical baseline/alternative
time/flux arrays in the saved checkpoints. It cannot reconstruct absent
arrays. Input product identities remain in the historical V1 injection rows.
See [data sources](../DATA_SOURCES.md) for retrieval scope. These commands
verify saved results and small numerical examples; they do not rerun the
212.64 charged CPU-hour investigation.
