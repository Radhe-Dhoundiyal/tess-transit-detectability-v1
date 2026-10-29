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
