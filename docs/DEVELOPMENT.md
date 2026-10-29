# What changed during V1

The project did not begin with a successful injection pipeline. Its recorded
failures distinguish a runnable algorithm from a valid experiment.

1. **Zero-centered substrate.** The original injection multiplied detrended
   residuals by a near-unity model. The residual median was zero, so this
   did not impose the intended transit depth. The [original failure record](../results/development/injection_recovery_failure_v1_0_0.json)
   preserves 320 completed but scientifically invalid trial outputs, 400 BLS
   executions including controls, and zero valid recovery claims. Later
   validation does not repair those products.
2. **Baseline restoration was necessary but insufficient.** The equation
   `(1+d)M-1` preserves the substrate when `M=1`. The [next failed preflight](../results/development/injection_recovery_amendment_failure_v1_0_1.json)
   nevertheless found all 320 sampled-depth contracts failed, with roughly
   15.38% relative depth error. No BLS execution or corrected trial was
   completed in this preflight. These are not 320 failed detections.
3. **Normalize the sampled decrement.** The raw central intensity had been
   divided by a disk-average intensity; its depth parameter was not the
   realized sampled minimum. Scaling `1-M_raw` by requested/raw sampled
   depth repaired that contract while preserving the relative sampled shape.
   The [19-case function validation](../results/development/injection_model_normalization_validation_v1_0_2.json)
   and [320-plan preflight](../results/development/injection_all_trial_normalization_preflight_v1_0_2.json)
   are historical accepted records, not tests newly run for this example.
4. **Finite recovery remained imperfect.** The accepted injection study
   yielded 98/320 direct and 123/320 direct-or-harmonic recovery. The
   independent known-signal benchmark yielded 15/51 direct. The saved
   outcomes are retained without selecting only successful examples.

The new `examples/normalize_depth.py` is a tiny synthetic demonstration of
the correction using the current byte-pinned V1 function. It does not prove
that every historical invocation consumed these exact current bytes. The
source manifest records present source identity, separately from saved
scientific result identity and personal authorship.

V2's scientific extension remains unfinished. C2 qualification is a separate
engineering obligation. Neither follows from the V1 results or the small
example. The original July 25 Git commit and its real dates remain in the
history; the scientific corrections are documented as corrections, not a
fictional sequence of development commits.
