# Scientific and software limitations

## A finite, selected benchmark

The known-signal endpoint is 15/51 eligible direct period-and-epoch recoveries,
with 19 additional catalogue entries outside the search range. The accepted
synthetic experiment is separate: 98/320 direct and 123/320 direct-or-harmonic
recoveries. Trials share 40 host substrates; they are not 320 independent
stars. These rates do not estimate population-wide completeness or occurrence.
No new planet discovery or external astronomical validation is claimed.

The empirical injection profile is central and circular, with fixed limb
darkening and finite exposure averaging. Preprocessing can attenuate signals;
its primary rolling-median detrending has no transit protection. The planning
SNR is a white-noise proxy, not a correlated-noise model or BLS significance.
The sampled-depth contract concerns retained timestamps, not an unobserved
continuous minimum. See [methods](METHODS.md) for matching and model details.

## Catalogue-reference provenance

The saved NASA Exoplanet Archive metadata lacks exact originating-literature
mappings for five classes: planet identity/target metadata, orbital periods,
transit epochs, planet radii/depths and stellar parameters. Archive attribution
and saved values are traceable; complete row-and-parameter paper mappings are
not. The [historical bibliography](../archive/2026-07-25/results/tables/source_specific_bibliography_v1_0_0_rc2.csv)
explicitly records that gap. Discovery references cannot substitute for each
parameter's source, and a new catalogue lookup cannot establish historical
consumption. No paper or DOI has been invented to fill missing fields.

This scope supports a bounded software demonstration and inspection of saved
results with the caveat retained. It does not support a claim of complete
literature-provenance closure or publication-quality revalidation of every
catalogue value. Repair would require authenticated original reference
metadata, or a separately dated new source mapping.

## Modeling and unfinished work

Validation is internal and grouped by target. The SciPy penalized logistic
fallback is not a fitted hierarchical model. The original numeric-cadence
sensitivity centers each frame locally, and its AUC helper does not average
tied ranks; both are documented in [methods](METHODS.md). Preserving code is
not silently correcting historical metrics. V2 science and C2 qualification
remain unfinished and are not established by the portable example.

## Reproduction scope

The package supplies working algorithms, a small example, focused tests and
selected saved records. The complete astronomical input archive and private
production orchestration are not bundled. Installation is not full pipeline
reproduction. The viewer is a present-day interface over historical records;
missing injected-flux arrays are not reconstructed. Tests were measured on
Windows/CPython 3.12.3 and Chromium, not certified across operating systems
or browser engines. Current source hashes identify bytes, not personal typing
or exact historical execution. See [verification](VERIFICATION.md).
