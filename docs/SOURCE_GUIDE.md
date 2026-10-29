# Source guide

| Component | Entry points | Transfer and scope |
|---|---|---|
| FITS reading and processing | `lightcurve_reader`, `preprocessing_pipeline`, `normalization`, `detrending`, `quality_mask`, `time_cleaning` | Complete current V1 modules; no observations downloaded |
| Blind BLS and candidates | `bls_search.run_blind_search`, `bls_grid`, `peak_extraction` | Complete current V1 modules; truth-free search boundary |
| Catalogue matching | `recovery_matching.compare_pair`, `match_target` | Complete V1 matching and assignment code |
| Transit construction | `injection_model.transit_model`, `injection_design.draw_trial` | Complete V1 model/design modules |
| Depth and baseline | `normalize_sampled_depth`, `inject_baseline_restored` | Original functions in unchanged `injection_model.py` |
| Observability and SNR | `injection_model.observability`, `snr.expected_snr` | Original observability; separately labeled SNR argument adapter |
| Grouped modeling | `modeling.scaling`, `design`, `fit_penalized`, `cv`, `bootstrap_intervals` | Exact definitions extracted from V1 orchestration, with a new import header |
| Group boundary | `grouped_validation.grouped_cv` | New validation wrapper; no claim it was historically executed |
| Tiny demonstration | `demonstration.normalization_case` | New five-sample example calling unchanged V1 normalization |

The [source manifest](../provenance/source_manifest.json) gives original relative
paths, file hashes, extracted line spans, definition AST hashes and transfer
types. It identifies current bytes; it does not establish personal authorship
or exact historical code consumption. Full top-level V1 modules, tests,
scripts, configurations, documents and notebooks were inventoried locally;
private phase-control infrastructure was deliberately excluded from this
distribution.

The original production scripts assume an extensive private data layout,
phase gates, saved checkpoints and orchestration side effects. They cannot
be run independently merely by installing this package. Only meaningful
scientific functions are extracted from the modeling script. Test extraction
retains selected original unit-test bodies without assertion changes; full
original test files remain in `archive/v1_tests/`. Artifact-dependent tests
are not misrepresented as portable tests.

This package supports the small executable example, focused synthetic tests,
and reading saved records. It is not a promise to recreate the whole private
pipeline. All tests use synthetic fixtures or bundled saved records. Original
astronomical inputs are neither modified nor reacquired.
