# Verification

Run the checks with Python 3.12. The
[GitHub Actions workflow](../.github/workflows/verify.yml) runs them on Windows;
the [Actions page](https://github.com/Radhe-Dhoundiyal/tess-transit-detectability-v1/actions)
shows the current run history and status. Local checks have been measured
with Windows/CPython 3.12.3; other platforms have not been verified.

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install --index-url https://pypi.org/simple ".[test]"
.venv\Scripts\python.exe -m pip check
.venv\Scripts\python.exe examples/normalize_depth.py
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe scripts/verify_project.py
```

Installation builds this local project and gets its dependencies from PyPI.
The tests use synthetic arrays and FITS files, temporary Parquet files,
and saved records. One test runs blind candidate generation in a fresh process
with catalogue matching unavailable. The optimizer and cross-validation
tests use small synthetic fixtures. The [archive](../archive/v1_tests/)
preserves the complete V1 tests, including those that need omitted inputs.

The [verifier](../scripts/verify_project.py) checks saved record and figure
hashes, current local links, and the two historical injection failure records.
It recomputes observed and injected outcome counts and four pairs of log-loss
and Brier scores from 1,280 saved predictions and checks the eight target-grouped
folds. These checks use the bundled records without downloading observations
or rerunning the study.

### Historical provenance

Run the optional provenance check from a full Git clone to compare the V1
source and archived tests with the [source manifest](../provenance/source_manifest.json)
and the July archive with its original Git tree.

```powershell
.venv\Scripts\python.exe scripts/verify_project.py --provenance
```

The [payload manifest](../provenance/payload_manifest.json) describes the
repository at commit
`93592297b5a8117aa6e2ef7d45c493764232d940`. To check the complete
historical payload, use that revision's verifier in a separate worktree.

```powershell
git worktree add --detach ../tess-release-snapshot 93592297b5a8117aa6e2ef7d45c493764232d940
Push-Location ../tess-release-snapshot
python scripts/verify_project.py
Pop-Location
```

## Example and explorer

The normalization example produces:

| Requested depth | Realized sampled depth | Absolute difference |
|---|---|---|
| 0 ppm | 0 ppm | 0 ppm |
| 100 ppm | 99.99999999998899 ppm | 1.1013412404281553e-11 ppm |
| 500 ppm | 499.9999999999449 ppm | 5.5081272876122966e-11 ppm |

The saved-results explorer has been checked in Chromium at 1920×1080,
1280×800 and 390×844. Checks cover outcome filters, all 70 observed records,
320 trial cells, alias accounting, missing curves, calibration rows, live
depth calculations, invalid-case rejection, keyboard controls, reload,
full screen and direct-file operation without a server. External asset
requests were blocked during those checks.

These are software and saved-record checks, not a full astronomical rerun.
[Limitations](LIMITATIONS.md) explains what they cannot establish.
