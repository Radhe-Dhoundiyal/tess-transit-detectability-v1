# TESS Transit Detectability Benchmark — RC2

## Overview

This evidence-first release candidate packages the frozen outputs of a fixed
TESS transit-detectability benchmark with traceable protocols, hashes, and
terminal authorities. It is intended for astronomy, statistics, and
reproducibility reviewers. RC2 is not a public or final release.

## Scope and contents

The benchmark contains evidence for 40 targets, 320 registered injection
trials, eight target-grouped folds, 68 converged fits, and 14 frozen figures.
RC2 includes reviewable scientific outputs and public notebooks but excludes
raw FITS, Parquet light curves, restricted/source downloads, and private
migration material.

## Headline findings

Primary Model A log loss is 0.3198223626785455, Brier score
0.1046725568285409, ROC AUC 0.9257676043390329, and PR AUC
0.8056516447845964. These are fixed benchmark results, not external
validation, causal evidence, or population-wide astrophysical claims.

## Installation and environment

Python 3.12 is supported. See `docs/CLEAN_MACHINE_SETUP_V1_0_0.md`,
`docs/ENVIRONMENT_REPRODUCTION_GUIDE_V1_0_0.md`, and
`requirements-lock.txt`. Identical dependency builds may not remain available
on every platform.

## Quick verification

Run `python scripts/verify_environment.py`, `python scripts/verify_hashes.py`,
and `python scripts/verify_release_candidate.py`. These commands are read-only
and require no restricted data.

## Reproducibility and lawful data reacquisition

Packaged-output verification requires no download. Scientific reruns require
lawful reacquisition from the NASA Exoplanet Archive and MAST under a separate
scientific authority; RC2 does not provide or trigger such acquisition.
Verification, computational, and exact-environment reproducibility are
distinguished in `docs/REPRODUCIBILITY_SCOPE_AND_LIMITATIONS_V1_0_0.md`.

## Repository structure

Protocols are in `config/`, authority and completion records in
`data/metadata/`, documentation in `docs/`, figures and tables in `results/`,
review notebooks in `notebooks/`, and read-only tools in `scripts/`.

## Citation, licensing, and acknowledgments

Use `CITATION.cff` as candidate metadata. Repository URL and DOI remain
`PENDING`. First-party code is MIT-licensed and identified first-party content
is CC BY 4.0; third-party data and software retain their own terms. See
`THIRD_PARTY_AND_DATA_RIGHTS.md`, `DEPENDENCY_NOTICES.md`, `DATA_SOURCES.md`,
and `ACKNOWLEDGMENTS.md`.

## Release status

Version `1.0.0-rc.2`, built 2026-07-24. This is a release candidate, not
publicly released. Recommended future repository name:
`tess-transit-detectability-benchmark`. No owner, URL, DOI, or final release
date is asserted.
