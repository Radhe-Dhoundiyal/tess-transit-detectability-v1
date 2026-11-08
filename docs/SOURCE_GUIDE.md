# Source guide

| Component | Entry points | What to look for |
|---|---|---|
| FITS reading and processing | `lightcurve_reader`, `preprocessing_pipeline`, `normalization`, `detrending`, `quality_mask`, `time_cleaning` | Loading observations, handling quality/time flags, and normalizing and detrending flux |
| Blind BLS and candidates | `bls_search.run_blind_search`, `bls_grid`, `peak_extraction` | Searching without catalogue truth and retaining candidate peaks |
| Catalogue matching | `recovery_matching.compare_pair`, `match_target` | Comparing periods and epochs, then assigning matches |
| Transit construction | `injection_model.transit_model`, `injection_design.draw_trial` | Building the empirical transit profile and drawing injection parameters |
| Depth and baseline | `normalize_sampled_depth`, `inject_baseline_restored` | Setting sampled depth and injecting into zero-centered residuals |
| Observability and SNR | `injection_model.observability`, `snr.expected_snr` | Counting observed events/samples and estimating white-noise SNR |
| Grouped modeling | `modeling.scaling`, `design`, `fit_penalized`, `cv`, `bootstrap_intervals` | Scaling, penalized logistic fits, target-grouped validation and bootstrap intervals |
| Group checks | `grouped_validation.grouped_cv` | Checking fold assignments before calling the modeling functions |
| Small demonstration | `demonstration.normalization_case` | Calling V1 normalization on five explicitly synthetic samples |

The modules cover the original V1 scientific workflow. `modeling.py` brings together selected functions from the original fitting script; `grouped_validation.py` checks host-grouped folds, and `demonstration.py` provides the five-sample example. The [source manifest](../provenance/source_manifest.json) records original identities, and the [verification guide](VERIFICATION.md#optional-source-and-figure-checks) explains how to check them.

The complete astronomical input archive and historical orchestration are not bundled here. Start with [methods](METHODS.md) for scientific assumptions or the [original V1 tests](../provenance/v1_tests/) to inspect the test cases.
