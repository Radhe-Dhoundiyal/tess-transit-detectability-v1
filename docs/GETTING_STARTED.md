# Getting started

Use Python 3.12 and open a terminal at the repository root.

## Install and run the example

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install --index-url https://pypi.org/simple ".[test]"
.venv\Scripts\python.exe examples/normalize_depth.py
```

The example runs `normalize_sampled_depth` on five synthetic samples at 0, 100 and 500 ppm. It prints requested depth, realized depth and numerical error.

## Open the explorer

```powershell
.venv\Scripts\python.exe demo/serve_demo.py
```

Open `http://127.0.0.1:8783/index.html`. The server binds only to loopback;
Ctrl+C stops it. Observed shows catalogue-match records; Injections shows the
320 accepted synthetic trials; Model shows saved internal-validation results.
Depth test runs the small normalization example. Try WASP-127 b, then
Kepler-31 b to compare saved direct and alias outcomes. Cases without retained curves show their recorded results.

The viewer contains its own assets. Opening `demo/index.html` directly also
works for saved records, but executing the function needs the server.
`python demo/serve_demo.py --check` checks the three arithmetic cases without
starting a server. [Explorer notes](../demo/README.md) explain its data.

## Check the project

```powershell
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe scripts/verify_project.py
```

Tests use synthetic fixtures and bundled records. See [verification](VERIFICATION.md) for scientific and optional historical checks.

On macOS/Linux, use `.venv/bin/python` in place of
`.venv\Scripts\python.exe`. See [verification](VERIFICATION.md) for the tested environment.

Read [methods](METHODS.md), [source](SOURCE_GUIDE.md), [development](DEVELOPMENT.md)
and [limitations](LIMITATIONS.md) to move from the example to the study.
