# Quick verification guide

These read-only checks verify packaged evidence without downloading restricted
data or executing BLS, injection, or model fitting.

PowerShell:
```powershell
& .\.venv\Scripts\python.exe scripts\verify_environment.py
& .\.venv\Scripts\python.exe scripts\verify_hashes.py
& .\.venv\Scripts\python.exe scripts\verify_release_candidate.py
```

Command Prompt:
```bat
.venv\Scripts\python.exe scripts\verify_environment.py
.venv\Scripts\python.exe scripts\verify_hashes.py
.venv\Scripts\python.exe scripts\verify_release_candidate.py
```

POSIX:
```sh
./.venv/bin/python scripts/verify_environment.py
./.venv/bin/python scripts/verify_hashes.py
./.venv/bin/python scripts/verify_release_candidate.py
```
