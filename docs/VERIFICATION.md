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
