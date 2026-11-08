# Getting started

Use Python 3.12 and open a terminal at the repository root.

## Install and run the example

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install --index-url https://pypi.org/simple ".[test]"
.venv\Scripts\python.exe examples/normalize_depth.py
```

The example calls the original `normalize_sampled_depth` function on five
synthetic samples at 0, 100 and 500 ppm. Its JSON output reports requested
depth, realized depth and absolute error. Floating-point rounding remains
below the `1e-6 ppm` check. These example inputs are separate from the saved
320-trial experiment.

## Open the explorer

```powershell
.venv\Scripts\python.exe demo/serve_demo.py
```

Open `http://127.0.0.1:8783/index.html`. The server binds only to loopback;
Ctrl+C stops it. Observed shows catalogue-match records; Injections shows the
320 accepted synthetic trials; Model shows saved internal-validation results.
Depth test calls the same small function example. Try WASP-127 b, then
Kepler-31 b to inspect a direct result and an alias. Selecting them does not
rerun the search. Missing curves remain explicitly unavailable.

The viewer contains its own assets. Opening `demo/index.html` directly also
works for saved records, but executing the function needs the server.
`python demo/serve_demo.py --check` checks the three arithmetic cases without
starting a server. [Explorer notes](../demo/README.md) explain its data.

## Check the project

```powershell
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe scripts/verify_project.py
```

Tests use synthetic fixtures and bundled records. The verifier checks saved
results, evidence hashes and local links. [Verification](VERIFICATION.md)
also explains how to check historical source and archive identities.

On macOS/Linux, use `.venv/bin/python` in place of
`.venv\Scripts\python.exe`. See [verification](VERIFICATION.md) for the tested environment.

Read [methods](METHODS.md), [source](SOURCE_GUIDE.md), [development](DEVELOPMENT.md)
and [limitations](LIMITATIONS.md) to move from the example to the study.
