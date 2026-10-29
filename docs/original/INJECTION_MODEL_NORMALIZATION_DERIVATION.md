# Sampled transit-model normalization derivation

Let `R(t) = 1 - M_raw(t)` and `delta_raw = max R(t)` on the retained
timestamps. Define `M_norm(t) = 1 - delta_req R(t) / delta_raw`.
Then `max(1 - M_norm) = delta_req`. Multiplication by one positive scalar
preserves relative shape, contact timing, exposure integration, and sampling.
Where `M_raw = 1`, `M_norm = 1`. With zero requested depth, `M_norm = 1`.
Finally `(1 + d)M_norm - 1 = d` out of transit.
