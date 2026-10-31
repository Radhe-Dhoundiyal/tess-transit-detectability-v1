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

Most modules are copied unchanged from V1. `modeling.py` collects selected
definitions from the original analysis script with a new import header.
The SNR adapter exposes the original planning expression through a small
public interface. `grouped_validation.py` and `demonstration.py` are wrappers
added for this package, not records of historical production runs. Original
paths, file checks and extraction details are in the
[source manifest](../provenance/source_manifest.json).

The original orchestration scripts expect the full input archive, checkpoint
layout and execution state. Installing this package does not recreate that
pipeline or download observations. It provides the algorithms, small example
and selected saved records for inspection.

The portable tests use synthetic fixtures or bundled records. Selected V1
unit-test bodies retain their original assertions; complete original test
files are in [the test archive](../archive/v1_tests/). Tests that need omitted
data and orchestration are outside this suite. See [verification](VERIFICATION.md)
for the commands and [methods](METHODS.md) for the scientific assumptions.
