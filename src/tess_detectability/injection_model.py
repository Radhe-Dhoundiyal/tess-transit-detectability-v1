"""Frozen deterministic empirical transit injection model for Phase 6A."""
from __future__ import annotations

import numpy as np


def circular_phase(time: np.ndarray, period: float, epoch: float) -> np.ndarray:
    return ((np.asarray(time, dtype=np.float64) - epoch + 0.5 * period) % period
            - 0.5 * period)


def limb_darkened_profile(position: np.ndarray, u1: float = 0.30,
                          u2: float = 0.20) -> np.ndarray:
    """Normalized small-planet quadratic limb-darkening intensity."""
    position = np.clip(np.asarray(position, dtype=np.float64), -1.0, 1.0)
    mu = np.sqrt(np.clip(1.0 - position * position, 0.0, 1.0))
    intensity = 1.0 - u1 * (1.0 - mu) - u2 * (1.0 - mu) ** 2
    disk_average = 1.0 - u1 / 3.0 - u2 / 6.0
    return intensity / disk_average


def transit_model(time: np.ndarray, period: float, epoch: float,
                  duration: float, depth_ppm: float,
                  exposure_days: float, supersample: int = 5) -> np.ndarray:
    """Central, circular, limb-darkened transit with finite exposure averaging."""
    if period <= 0 or duration <= 0 or depth_ppm < 0 or duration >= period:
        raise ValueError("invalid frozen transit parameters")
    offsets = np.linspace(-0.5, 0.5, supersample, dtype=np.float64) * exposure_days
    samples = []
    half = duration / 2.0
    ingress = max(exposure_days, 0.08 * duration)
    for offset in offsets:
        phase = circular_phase(time + offset, period, epoch)
        absolute = np.abs(phase)
        chord = np.clip(phase / half, -1.0, 1.0)
        profile = limb_darkened_profile(chord)
        edge = np.clip((half + ingress - absolute) / ingress, 0.0, 1.0)
        samples.append(1.0 - depth_ppm * 1e-6 * profile * edge)
    result = np.mean(samples, axis=0, dtype=np.float64)
    if not np.isfinite(result).all():
        raise FloatingPointError("nonfinite transit model")
    return result


def inject_multiplicatively(flux: np.ndarray, model: np.ndarray) -> np.ndarray:
    result = np.asarray(flux, dtype=np.float64) * np.asarray(model, dtype=np.float64)
    if not np.isfinite(result).all():
        raise FloatingPointError("nonfinite injected flux")
    return result


def normalize_sampled_depth(
        raw_model: np.ndarray, requested_depth_ppm: float,
        raw_depth_tolerance: float = 1e-15,
        negative_tolerance: float = 1e-15) -> tuple[np.ndarray, dict[str, float]]:
    """Rescale a sampled raw model to an exact requested sampled decrement.

    The minimum and raw depth are evaluated on the same retained timestamps as
    the returned model. Relative shape and contact timing are preserved because
    the raw decrement is multiplied by one scalar.
    """
    raw = np.asarray(raw_model, dtype=np.float64)
    requested = float(requested_depth_ppm) * 1e-6
    if not np.isfinite(requested) or requested < 0:
        raise ValueError("REQUESTED_DEPTH_INVALID")
    if not np.isfinite(raw).all():
        raise FloatingPointError("RAW_DEPTH_ZERO_OR_NONFINITE")
    if requested == 0:
        normalized = np.ones_like(raw)
        return normalized, {
            "raw_depth": float(1.0 - raw.min()),
            "requested_depth": 0.0,
            "scale_factor": 0.0,
            "realized_depth": 0.0,
        }
    raw_depth = float(1.0 - raw.min())
    if not np.isfinite(raw_depth) or raw_depth <= raw_depth_tolerance:
        raise ValueError("RAW_DEPTH_ZERO_OR_NONFINITE")
    scale = requested / raw_depth
    normalized = 1.0 - scale * (1.0 - raw)
    if not np.isfinite(normalized).all():
        raise FloatingPointError("NORMALIZED_MODEL_NONFINITE")
    if float(normalized.min()) < -negative_tolerance:
        raise ValueError("NORMALIZED_MODEL_NEGATIVE")
    realized = float(1.0 - normalized.min())
    return normalized, {
        "raw_depth": raw_depth,
        "requested_depth": requested,
        "scale_factor": scale,
        "realized_depth": realized,
    }


def inject_baseline_restored(flux: np.ndarray, model: np.ndarray) -> np.ndarray:
    """Inject a unity-baseline model into zero-centered detrended flux."""
    result = ((1.0 + np.asarray(flux, dtype=np.float64)) *
              np.asarray(model, dtype=np.float64) - 1.0)
    if not np.isfinite(result).all():
        raise FloatingPointError("nonfinite injected flux")
    return result


def observability(time: np.ndarray, period: float, epoch: float,
                  duration: float) -> dict[str, int | bool]:
    phase = circular_phase(time, period, epoch)
    mask = np.abs(phase) <= duration / 2.0
    event = np.floor((np.asarray(time) - epoch) / period + 0.5).astype(np.int64)
    observed = np.unique(event[mask])
    between = False
    if len(observed) >= 2:
        lo = epoch + observed.min() * period
        hi = epoch + observed.max() * period
        between = bool(((np.asarray(time) > lo + duration / 2) &
                        (np.asarray(time) < hi - duration / 2) & ~mask).any())
    return {"observed_transit_count": int(len(observed)),
            "in_transit_points": int(mask.sum()),
            "out_of_transit_between_events": between,
            "observable": bool(len(observed) >= 2 and mask.sum() >= 5 and between)}
