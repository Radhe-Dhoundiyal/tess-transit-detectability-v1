# Finding and fixing the injection problem

My starting question was whether a blind search could recover a transit's
period and epoch, not just whether the signal was present. Controlled
injections offered a way to compare a known input with the search result in
real TESS noise. Getting that input right turned out to be a problem of its own.

## The first injection did not add the intended signal

The original approach multiplied detrended residuals by a near-unity transit
model. Detrending had moved the baseline to zero, so this scaled the residuals
rather than adding a transit with the requested depth. The
[failure record](../results/development/injection_recovery_failure_v1_0_0.json)
contains 320 completed but scientifically invalid trial outputs and 400 BLS
executions including controls. Those outputs are not valid recovery results.

Restoring the baseline with `(1 + residual) * M - 1` fixed that equation:
outside transit, where `M = 1`, the residual is unchanged. But the
[next depth check](../results/development/injection_recovery_amendment_failure_v1_0_1.json)
found a second problem. The limb-darkened model used disk-average intensity
normalization, producing a sampled depth about 15.38% larger than requested.
All 320 depth checks failed before any BLS search ran.

## Measure and scale the sampled depth

The correction measures `delta_raw = max(1 - M_raw)` on the retained
timestamps, then scales the decrement:

`M_norm = 1 - (delta_requested / delta_raw) * (1 - M_raw)`

For positive depth, this sets the requested sampled depth while preserving
the relative shape and contact timing. A zero requested depth gives a flat
model. The baseline-restored injection then uses `M_norm`.
The [derivation](original/INJECTION_MODEL_NORMALIZATION_DERIVATION.md)
explains the calculation and its out-of-transit behavior.

The recorded [19-case function validation](../results/development/injection_model_normalization_validation_v1_0_2.json)
and [320-trial-plan depth check](../results/development/injection_all_trial_normalization_preflight_v1_0_2.json)
passed. The latter checked signal construction without running BLS or drawing
replacement trials. The small [normalization example](../examples/normalize_depth.py)
now makes the calculation easy to inspect on five synthetic samples.

## Correct injections still did not guarantee recovery

The accepted experiment recovered 98/320 trials directly and 123/320 directly
or at a harmonic. It also retained 12 aliases and 185 nonrecoveries.
Separately, the known-catalogue benchmark recovered 15/51 eligible signals
directly. Correct signal construction was necessary, but it did not make
the search complete.

These are results from a selected benchmark, not a population-wide recovery
rate. V2 science and C2 qualification remain unfinished; see
[limitations](LIMITATIONS.md). The failed outputs and checks remain alongside
the accepted records so the correction can be followed without discarding
what went wrong.
