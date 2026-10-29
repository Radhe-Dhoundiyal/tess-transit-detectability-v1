"""Present-day five-sample arithmetic example, separate from historical trials."""
import hashlib
from pathlib import Path
import numpy as np
from . import injection_model


def normalization_case(requested_depth_ppm):
    """Execute the original V1 function on an explicitly synthetic sampled model."""
    raw = np.array([1.0, 0.9998, 0.9996, 0.9998, 1.0], dtype=np.float64)
    normalized, diagnostics = injection_model.normalize_sampled_depth(
        raw, requested_depth_ppm)
    realized = float((1.0 - normalized.min()) * 1e6)
    error = abs(realized - requested_depth_ppm)
    if error >= 1e-6:
        raise ArithmeticError("Sampled-depth contract failed")
    return {
        "classification": "NEW_EXPLICITLY_SYNTHETIC_CODE_DEMONSTRATION",
        "function": "normalize_sampled_depth",
        "module_sha256": hashlib.sha256(Path(injection_model.__file__).read_bytes()).hexdigest().upper(),
        "input_raw_model": raw.tolist(),
        "requested_depth_ppm": float(requested_depth_ppm),
        "normalized_model": normalized.tolist(),
        "diagnostics": diagnostics,
        "realized_depth_ppm": realized,
        "max_error_ppm": error,
        "numpy": np.__version__,
        "scientific_scope": "Five synthetic samples; not a historical trial, observation or recovery result.",
    }
