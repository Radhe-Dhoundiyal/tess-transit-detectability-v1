# Getting started

Use Python 3.12 and open a terminal at the repository root. The commands below
install the local project, not a separately published TESS package.

## Install and run the example

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install --index-url https://pypi.org/simple ".[test]"
.venv\Scripts\python.exe examples/normalize_depth.py
```

The example creates five explicitly synthetic sampled model values and calls
the original `normalize_sampled_depth` function at 0, 100 and 500 ppm. The
JSON output includes requested depth, realized depth and absolute difference.
The 100 ppm result is approximately `99.99999999998899 ppm`; an error around
`1e-11 ppm` is ordinary floating-point rounding, below the `1e-6 ppm` check.
This is arithmetic on a small model, not one of the historical 320 trials.

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

Tests use synthetic fixtures and bundled records. Verification checks source
and payload hashes, original archived files, image provenance, local links
and saved result accounting. It does not download observations or refit the
scientific model. [Verification scope](VERIFICATION.md) states what was tested.

On macOS/Linux, use `.venv/bin/python` in place of
`.venv\Scripts\python.exe`. Those command forms are provided for convenience;
the measured environment was Windows with CPython 3.12.3.

Read [methods](METHODS.md), [source](SOURCE_GUIDE.md), [development](DEVELOPMENT.md)
and [limitations](LIMITATIONS.md) to move from the example to the study.
