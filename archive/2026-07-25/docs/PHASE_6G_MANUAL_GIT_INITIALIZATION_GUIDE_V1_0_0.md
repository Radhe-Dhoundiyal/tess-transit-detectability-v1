# Phase 6G manual Git initialization guide

This is guidance only; Phase 6F.2 performs no Git action.

Use `release/TESS_Transit_Detectability_Benchmark_v1.0.0-rc.3` as the future
repository root. Never initialize Git at the private project root. Under a
separate Phase 6G authorization:

1. Reverify the RC3 archive and manifests.
2. Initialize Git only inside the approved RC3 staging directory.
3. Inspect `git status --short --ignored`.
4. Confirm no required evidence is ignored and no sensitive file is untracked.
5. Add a remote only after the owner/account and repository URL are confirmed.
6. Do not push until Phase 6G explicitly authorizes the push.
