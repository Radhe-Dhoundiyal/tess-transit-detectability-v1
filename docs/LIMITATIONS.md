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

## Missing catalogue references

The saved NASA Exoplanet Archive metadata lacks links to the originating
papers for five classes: planet identity/target metadata, orbital periods,
transit epochs, planet radii/depths and stellar parameters. The saved values
and Archive attribution remain available, but they do not replace paper-level
references. The [saved source-reference table](../results/tables/source_specific_bibliography_v1_0_0_rc2.csv)
records these gaps.

Completing these mappings requires the original reference metadata.
A new catalogue lookup would describe a later snapshot. The historical
inputs remain only partially traceable to their originating papers.

## Modeling and unfinished work

Validation is internal and grouped by target. The SciPy penalized logistic
fallback is not a fitted hierarchical model. The original numeric-cadence
sensitivity centers each frame locally, and its AUC helper does not average
tied ranks; both are documented in [methods](METHODS.md). These limitations
remain in the code and historical metrics. V2 science and C2 qualification
remain unfinished; the small example does not establish either.

## Reproduction scope

The package includes algorithms, examples, tests and selected saved records.
Reproducing the complete pipeline requires the original astronomical inputs
and production orchestration. The viewer displays historical records and
leaves missing injected-flux arrays unavailable.
[Verification](VERIFICATION.md) describes the software checks and tested environment.

## V1.1 comparison scope

The 320 saved pairs show 20 primary gains and one loss after adding grid
nodes. The 32-trial/four-host exploratory cohort preceded the 288-trial
extension on the remaining 36 hosts. Neither cohort is a fresh randomized
population sample. The descriptive host-bootstrap interval measures
resampling variation within these selected substrates; four exploratory
hosts give especially limited uncertainty information.

No calibrated false-alarm threshold, inverted-light-curve control or new
transit-protecting detrending experiment was completed. A period-and-epoch
match is not a significance-calibrated planet detection. Finer sampling
alone cannot resolve all preprocessing, aliasing and peak-ranking failures;
the saved outcomes do not establish a cause for every remaining miss.

The alternative known-signal comparison has three eligible signals in four
selected host searches (five entries including two outside the range).
The other historical eligible signals were not searched with the new grid.
The package permits saved-peak reclassification, statistical recounts and
grid reconstruction, not a full light-curve rerun without external inputs.
