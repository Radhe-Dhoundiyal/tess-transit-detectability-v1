# Verification

The project is checked in a disposable virtual environment on Windows with
CPython 3.12.3. Installation builds the local project into a wheel and resolves
declared dependencies from PyPI. This is isolated-environment evidence, not a
clean-machine or cross-platform certification. The minimal
[CI workflow](../.github/workflows/verify.yml) runs the same Python checks on
a Windows runner. The workflow has also completed successfully on GitHub.
See the [Actions page](https://github.com/Radhe-Dhoundiyal/tess-transit-detectability-v1/actions)
for the current run history and status; a past successful run does not
guarantee that a later revision passes.

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install --index-url https://pypi.org/simple ".[test]"
.venv\Scripts\python.exe -m pip check
.venv\Scripts\python.exe examples/normalize_depth.py
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe scripts/verify_project.py
```

The focused suite contains 28 selected original V1 unit-test bodies with
unchanged assertions, plus public-boundary tests. Complete original test
files remain in `archive/v1_tests/`; artifact-dependent private checks are
outside this portable suite. Fixtures use synthetic arrays/FITS, temporary
Parquet files, or bundled saved records. Tiny optimizer/CV tests use synthetic
targets, not a refit of the historical benchmark.

The verifier checks copied source hashes and extracted definition ASTs,
saved observed/injected accounting, 1,280 stored predictions and four pairs
of log-loss/Brier calculations, eight target-grouped fold assignments,
archived Git objects, image hashes/metadata and current documentation links.
`provenance/payload_manifest.json` pins the distributable files and excludes
itself to avoid a circular hash. The historical attributes file is inert so
its checkout rules cannot alter preserved archive bytes.

| Requested depth | Realized sampled depth | Absolute difference |
|---|---|---|
| 0 ppm | 0 ppm | 0 ppm |
| 100 ppm | 99.99999999998899 ppm | 1.1013412404281553e-11 ppm |
| 500 ppm | 499.9999999999449 ppm | 5.5081272876122966e-11 ppm |

The saved-record explorer is tested in Chromium at 1920×1080, 1280×800 and
390×844. Checks exercise all outcome filters, 70 observed records, 320 trial
cells, alias accounting, missing curves, exact calibration bins, live depth
calls, invalid-case rejection, keyboard navigation, reload, full screen and
direct-file operation without a server. External asset requests are blocked
during these checks. The README previews use authenticated scientific figures
and a genuine browser capture; they do not substitute for execution.

No astronomical search, 320-trial production rerun, model bootstrap, V2 or C2
qualification is performed by these checks. [Limitations](LIMITATIONS.md)
separates software verification from scientific generalization.
