"""Public adapter for the V1 trial-planning SNR expression, not a new estimator."""
import numpy as np

def expected_snr(depth_ppm, in_transit_points, scatter):
    """Depth in ppm, retained in-transit point count, residual scatter in flux units.

    V1 white-noise proxy; does not model correlated noise. Nonpositive scatter
    returns NaN, as in the original planning expression.
    """
    accepted = {"depth_ppm": depth_ppm, "in_transit_points": in_transit_points}
    return (accepted["depth_ppm"] * 1e-6 *
                            np.sqrt(accepted["in_transit_points"]) / scatter
                            if scatter > 0 else np.nan)
