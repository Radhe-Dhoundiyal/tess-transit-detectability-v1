# Third-party software

Dependencies are installed separately from the declared PyPI source; their
source code and binary wheels are not vendored or relicensed here. Retain
their installed distribution notices. Tested versions, license declarations
and license-file locators are in `provenance/dependencies.json`.

Core dependencies are NumPy 1.26.4, pandas 2.2.2, Astropy 7.2.2 and SciPy
1.14.1. The test extra adds pytest 8.3.4 and PyArrow 17.0.0. Transitive
versions from the disposable environment are pinned in `requirements-lock.txt`.
This records one Windows/Python 3.12 resolution, not a promise of identical
wheels on every platform. Build dependencies are separately pinned in
`pyproject.toml`.

Astropy BLS supplies the search statistic. The original project implements
the grid, candidate handling, matching, injection normalization and
statistical workflow around that library. The July dependency analysis is
retained as historical evidence in the archive.
