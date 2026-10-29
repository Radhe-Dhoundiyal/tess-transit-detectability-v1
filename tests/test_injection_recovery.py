"""Selected portable V1 unit tests. Assertions unchanged; scope in source manifest."""
from __future__ import annotations


import unittest


from pathlib import Path


import numpy as np


from tess_detectability.injection_design import DEPTHS, draw_trial, trial_seed


from tess_detectability.injection_model import (
    inject_baseline_restored, inject_multiplicatively, normalize_sampled_depth,
    observability, transit_model)


class InjectionRecoveryTests(unittest.TestCase):
    def test_seed_is_stable_and_identity_sensitive(self):
        first = trial_seed("1.0.0", 1, "SYS-A", "P1_D1", 0)
        self.assertEqual(first, trial_seed("1.0.0", 1, "SYS-A", "P1_D1", 0))
        self.assertNotEqual(first, trial_seed("1.0.0", 2, "SYS-A", "P1_D1", 0))
    def test_design_bounds_and_all_depths(self):
        rows = [draw_trial(1, "SYS-A", index, 20.0, 100.0)
                for index in range(8)]
        self.assertEqual([row["depth_ppm"] for row in rows], list(DEPTHS))
        self.assertTrue(all(0.3 <= row["period"] <= 20 for row in rows))
        self.assertEqual(len({row["seed"] for row in rows}), 8)
    def test_transit_model_is_deterministic_and_finite(self):
        time = np.linspace(0, 10, 10001)
        first = transit_model(time, 2.0, 0.5, 0.1, 1000, 2 / 1440)
        second = transit_model(time, 2.0, 0.5, 0.1, 1000, 2 / 1440)
        np.testing.assert_array_equal(first, second)
        self.assertTrue(np.isfinite(first).all())
        self.assertLess(first.min(), 1.0)
    def test_exposure_integration_changes_edge_samples(self):
        time = np.array([0.445, 0.45, 0.455])
        narrow = transit_model(time, 2, 0.5, 0.1, 1000, 1e-6)
        integrated = transit_model(time, 2, 0.5, 0.1, 1000, 0.02)
        self.assertFalse(np.array_equal(narrow, integrated))
    def test_zero_depth_and_multiplicative_equivalence(self):
        time = np.linspace(0, 5, 1000)
        flux = 1 + 1e-3 * np.sin(time)
        model = transit_model(time, 1, 0.2, 0.08, 0, 2 / 1440)
        np.testing.assert_array_equal(model, np.ones_like(time))
        np.testing.assert_array_equal(inject_multiplicatively(flux, model), flux)
    def test_observability_counts_events_and_points(self):
        time = np.arange(0, 10, 0.01)
        result = observability(time, 2.0, 0.5, 0.1)
        self.assertGreaterEqual(result["observed_transit_count"], 2)
        self.assertGreaterEqual(result["in_transit_points"], 5)
        self.assertTrue(result["observable"])
    def test_invalid_geometry_fails_closed(self):
        with self.assertRaises(ValueError):
            transit_model(np.arange(10), 1, 0, 1, 1000, 0.01)
    def test_sampled_depth_normalization_contract(self):
        time = np.linspace(0, 4, 40001)
        raw = transit_model(time, 1, 0.5, 0.1, 1000, 2 / 1440)
        normalized, audit = normalize_sampled_depth(raw, 1000)
        self.assertAlmostEqual(1 - normalized.min(), 0.001, places=14)
        self.assertAlmostEqual(audit["realized_depth"], 0.001, places=14)
        raw_decrement = 1 - raw
        normalized_decrement = 1 - normalized
        mask = raw_decrement > 0
        np.testing.assert_allclose(
            normalized_decrement[mask],
            audit["scale_factor"] * raw_decrement[mask],
            rtol=0, atol=2e-16)
    def test_baseline_restored_injection_preserves_out_of_transit(self):
        flux = np.array([-0.01, 0.0, 0.02])
        model = np.array([1.0, 0.999, 1.0])
        injected = inject_baseline_restored(flux, model)
        self.assertAlmostEqual(injected[0], flux[0], places=15)
        self.assertAlmostEqual(injected[2], flux[2], places=15)
    def test_zero_depth_normalization_is_unity(self):
        raw = np.array([1.0, 0.998, 1.0])
        normalized, audit = normalize_sampled_depth(raw, 0)
        np.testing.assert_array_equal(normalized, np.ones_like(raw))
        self.assertEqual(audit["scale_factor"], 0)
    def test_normalization_edge_cases_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "RAW_DEPTH_ZERO_OR_NONFINITE"):
            normalize_sampled_depth(np.ones(10), 100)
        with self.assertRaisesRegex(ValueError, "REQUESTED_DEPTH_INVALID"):
            normalize_sampled_depth(np.array([1.0, 0.99]), -1)
        with self.assertRaisesRegex(FloatingPointError,
                                   "RAW_DEPTH_ZERO_OR_NONFINITE"):
            normalize_sampled_depth(np.array([1.0, np.nan]), 100)
