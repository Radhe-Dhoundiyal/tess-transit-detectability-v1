# Injection baseline-restoration derivation

For zero-centered detrended flux `d` and transit model `M`, Phase 6A.1 defines:

```text
f = (1 + d)M - 1
```

Outside transit, if `M = 1`, then `f = d`; the substrate is preserved.

For a flat substrate, `d = 0`, so `f = M - 1`.

Consequently, if and only if the model minimum is `1 - delta`, the minimum
injected residual is `-delta` and the realized depth is `delta`.

This identity separates two gates: the baseline-restoration equation and the
unchanged transit model's requested-depth contract. Passing the first does not
imply passing the second.
