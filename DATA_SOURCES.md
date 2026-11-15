# Data sources and included records

V1 used NASA TESS/SPOC observations from MAST and catalogue metadata from the
NASA Exoplanet Archive. The original source bibliographies remain in the
July archive. This package includes selected derived records and figures,
not the large raw FITS or processed Parquet archive.

| Included item | Provenance and interpretation |
|---|---|
| `results/tables/transit_recovery_planet_results.csv` | 70 original catalogue-match rows; 51 eligible, 19 outside range |
| `data/records/injection_recovery_results_v1_0_2.csv` | 320 accepted synthetic trials in observed substrates |
| `data/records/detectability_oof_predictions_v1_0_1.csv` | Saved internal target-grouped predictions, not a new fit |
| `results/tables/detectability_calibration_v1_0_1.csv` | Ten original calibration bins |
| `demo/curve_data.js` | 8,000 deterministic displayed samples from 371,497 retained WASP-127 observations; times and fluxes unchanged |
| `demo/inputs/CURVE_SOURCE.json` | Four processed-product and upstream mission-product hashes, sectors and sample rule |

Hashes and transfer types are in `provenance/source_manifest.json`. Original
relative paths inside saved rows describe historical provenance; omitted
files are not promised by this small distribution. The viewer's public
source labels point to included counterparts.

External observations and factual catalogue content retain their own rights
and acknowledgments. No proprietary document, mission logo or new observation
download is included. See [acknowledgments](ACKNOWLEDGMENTS.md) and
[rights boundaries](THIRD_PARTY_AND_DATA_RIGHTS.md).

## V1.1 records

| Included item | Provenance and interpretation |
|---|---|
| `data/records/period_grid_pairs_v1_1_0.csv` | 320 paired checkpoint exports; trial/host/cohort identities, primary/literal rank-1 and other classifications, input identity, grid hashes/counts, CPU/wall/RSS diagnostics |
| `data/records/period_grid_candidates_v1_1_0.csv` | Ten retained blind peaks per trial per grid (6,400 rows), preserving saved numeric text |
| `data/records/period_grid_known_subset_v1_1_0.csv` | Five paired catalogue entries on four hosts; three eligible, two outside range |
| `data/records/period_grid_known_truth_v1_1_0.csv` | The saved catalogue period, epoch and duration values needed for those five entries |
| `data/records/period_grid_known_candidates_v1_1_0.csv` | 80 retained peaks from the four host searches with each grid |
| `results/tables/period_grid_summary_v1_1_0.json` | Recomputable primary/cohort counts, host-bootstrap seed/replicates/intervals and search-time totals |

`matching_baseline_days` preserves the historical matcher span; the exact
observed `search_span_days` is kept separately for grid reconstruction.
`injection_period_days`, `injection_epoch_btjd` and `injection_duration_days`
preserve the execution-plan matching truth at full saved precision;
other injection properties and upstream product identities are
joined by `trial_id` to the unchanged accepted V1 table. Hosts share eight
injections each. Boolean primary outcomes and literal rank-1 diagnostics
retain different definitions; see [methods](docs/METHODS.md#v11-period-grid-comparison).
Source-candidate hashes authenticate the original CSV files before their
rows were combined; the manifest authenticates the combined export bytes.
Input identities hash the shapes and little-endian float64 bytes of time
and injected flux in that order. They are identities, not downloadable data.

For a new astronomical rerun, use the recorded TESS product filenames/TICs
and sectors to retrieve the corresponding SPOC light curves from
[MAST](https://mast.stsci.edu/portal/Mashup/Clients/Mast/Portal.html), then use
the included reading/preprocessing/injection algorithms and saved trial
parameters. The complete historical orchestration, all catalogue snapshots
and processed arrays are not included, so retrieval alone is not a promise
of byte-identical reproduction. V1.1 reused the saved inputs rather than
querying a later catalogue. External attribution and rights boundaries
continue to apply to the derived records.
