# Project Context

Updated: 2026-07-24 (Asia/Calcutta)

## Project vision

Build a reproducible, evidence-first characterization of transit detectability
in a fixed TESS benchmark. Every scientific result must be traceable to frozen
inputs, preregistered methods, grouped validation, immutable hashes, and an
explicit terminal state.

## Architecture overview

The phase-controlled pipeline is:

1. benchmark definition and source acquisition;
2. canonical preprocessing to 160 Parquet light curves;
3. Phase 5B blind BLS recovery and truth matching;
4. Phase 6A.2 normalized injection-recovery;
5. Phase 6B preregistered statistical detectability modeling;
6. Phase 6B.4 terminal figure-manifest and lineage authority.

Authority layers comprise Markdown preregistrations/amendments, YAML
protocols, JSON authorizations/manifests/terminal markers, CSV evidence tables,
model JSON files, executed notebooks, and SHA-256 output manifests.

## Technology stack

- Windows PowerShell
- Python 3.12 at
  `<local-user-path>`
- NumPy, pandas, SciPy/statsmodels modeling dependencies, Matplotlib
- Astropy and PyArrow for upstream astronomy/data products
- nbformat, nbclient, ipykernel for executed notebooks
- JSON, YAML, CSV, Parquet, PNG, Markdown, Jupyter Notebook
- standard-library `unittest`; `pytest` is not installed

Run direct scripts from repository root with `$env:PYTHONPATH='src'`.

## Directory structure

- `config/`: immutable versioned protocols.
- `data/metadata/`: authorizations, manifests, audits, prepublication records,
  completion/failure markers.
- `data/raw/`: source products; preserve.
- `data/processed/`: canonical light curves, injection benchmark, modeling
  dataset.
- `data/interim/`: blind outputs, OOF/LOTO predictions, checkpoints.
- `models/`: four v1.0.1 full-data model families and their metadata.
- `results/tables/`: endpoints, diagnostics, manifests, lineage, audits.
- `results/figures/detectability_modeling_v1_0_1/`: terminal 14-figure set.
- `notebooks/`: executed evidence notebooks.
- `scripts/`: phase preparation, execution, validation, reconstruction, and
  publication entry points.
- `src/tess_detectability/`: reusable pipeline functions.
- `tests/`: unit and phase-gate tests.

## Core systems/modules

- `scripts/run_detectability_modeling_phase6b.py`: original modeling logic and
  reusable metrics/bootstrap functions.
- `scripts/run_detectability_modeling_retry_phase6b1.py`: corrected grid
  helper and figure-generation implementation.
- `scripts/finalize_detectability_modeling_retry_phase6b1.py`: final
  fold/sensitivity figure generation and v1.0.1 evidence finalization.
- `scripts/reconstruct_detectability_figure_authority_phase6b4.py`: v1.0.4
  inventory, dependency graph, temporary regeneration, supplements, and
  terminal combined manifest/lineage views.
- `scripts/validate_detectability_figure_authority_phase6b4.py`: independent
  scientific/metric validation, reports, and 24-section notebook.
- `scripts/publish_detectability_figure_authority_phase6b4.py`: final
  prepublication gates and atomic completion-marker publication.
- `tests/test_phase6b4_figure_authority.py`: v1.0.4 terminal gates.

## Design principles

- Evidence first; separate facts, assumptions, and limitations.
- Freeze rules before scientific execution.
- Fail closed and preserve diagnostic failures.
- Never overwrite upstream or failed-phase authorities.
- Use exact hashes and deterministic regeneration where possible.
- Group validation by target to prevent leakage.
- Separate computational validation from external scientific validation.
- Do not infer authorization from a likely next step.
- Write terminal completion markers last.

## Constraints and assumptions

- The benchmark contains 320 injection trials from 40 targets.
- Cross-validation uses eight target-grouped folds.
- Results are benchmark-specific predictive associations, not causal effects.
- The injection design and target sample limit population generalization.
- No functional Git authority is currently discoverable.
- The Python interpreter is shared and not locked by a project environment.
- Timestamps are supporting evidence only; hashes are authoritative.

## Things that should not change without approval

- All Phase 5A.2, Phase 5B, Phase 6A, and Phase 6B authorities and terminal
  markers.
- The 160 canonical Parquet files and frozen modeling dataset.
- All v1.0.0–v1.0.3 failure evidence.
- v1.0.1 scientific tables, OOF/LOTO predictions, model JSON files, and 14
  figure PNGs.
- v1.0.4 supplements, combined manifest/lineage, prepublication record, and
  completion marker.
- Frozen outcomes, predictors, folds, interaction threshold, sensitivity
  definitions, bootstrap rules, or figure scope.
- No MAST query, download, preprocessing, BLS, injection, truth matching,
  completeness recalculation, model fit, or figure replacement without a
  separately versioned authority and explicit user authorization.
