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
The focused suite uses synthetic arrays/FITS, temporary Parquet files and
bundled saved records. It contains 28 selected V1 unit-test bodies with
unchanged assertions, plus tests of the packaged interfaces. Complete
original test files remain in [the archive](../archive/v1_tests/); tests that
need omitted inputs are outside this suite. The small optimizer and
cross-validation tests use synthetic targets, not a refit of the benchmark.

The [repository verifier](../scripts/verify_project.py) checks source and
archive files, preview images, included-file completeness and local links.
It also checks the observed/injected outcome counts, eight target-grouped
fold assignments, 1,280 saved predictions and four pairs of log-loss/Brier
calculations. The [source guide](SOURCE_GUIDE.md) explains which code is
included and where it came from.

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
