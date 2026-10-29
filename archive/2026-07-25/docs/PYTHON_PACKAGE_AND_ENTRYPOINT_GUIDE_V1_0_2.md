# Python package and entry-point guide v1.0.2

Package roots are the repository root and `src/`. Run repository tests from
the repository root with `PYTHONPATH=src`. Verification scripts are supported
in script mode from the repository root and derive the root from `__file__`;
they do not import scientific modules. Scientific scripts historically use
script-directory sibling imports and must be invoked only under their frozen
phase instructions; RC2 verification does not invoke them.

Supported verification:

```powershell
$env:PYTHONPATH='src'
python scripts\verify_environment.py
python scripts\verify_hashes.py
python scripts\verify_release_candidate.py
```

Editable installation is supported by `pyproject.toml` for first-party
`src/tess_detectability`, but is not required for read-only RC2 verification.
No current-working-directory assumption is used to classify an import without
a concrete module path.
