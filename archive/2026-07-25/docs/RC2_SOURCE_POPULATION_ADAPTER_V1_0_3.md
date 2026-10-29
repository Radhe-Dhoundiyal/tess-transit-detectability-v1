# RC2 source-population adapter protocol 1.0.3

Authorization: `TS-DETECTABILITY-RC2-DOCUMENTATION-AMEND-1.0.3-P6F1A3`  
Protocol: `1.0.3`

Protocol 1.0.2 successfully passed dependency and import resolution, then
correctly failed because an inherited v1.0.0 source-population routine expected
obsolete filenames. This adapter verifies and reuses the v1.0.2 gate, maps
legacy expectations to versioned authority, and populates RC2 without creating
fake compatibility files.

`environment.yml` is omitted: the repository contains no authoritative Conda
solver export or lock. Python 3.12, `pyproject.toml`, evidence-backed
requirements, and the observed-environment inventory are the supported
environment evidence.

All three failures, parent archives, scientific bytes, Git state, network
state, upload state, and DOI state remain preserved.
