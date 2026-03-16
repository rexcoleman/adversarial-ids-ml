"""Tests for adversarial attack and defense pipeline correctness.

These tests verify attack/defense properties using saved results
and lightweight computations rather than re-running attacks.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from src.preprocessing import (
    ATTACKER_CONTROLLABLE_FEATURES,
    DEFENDER_OBSERVABLE_ONLY,
    get_controllable_feature_mask,
)

ADV_DIR = PROJECT_DIR / "outputs" / "adversarial"
DEF_DIR = PROJECT_DIR / "outputs" / "defense"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def unconstrained_results():
    """Load unconstrained attack results."""
    path = ADV_DIR / "unconstrained_results.json"
    if not path.exists():
        pytest.skip("Unconstrained results not found — run adversarial_attacks.py first")
    with open(path) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def constrained_results():
    """Load constrained attack results."""
    path = ADV_DIR / "constrained_results.json"
    if not path.exists():
        pytest.skip("Constrained results not found — run adversarial_attacks.py first")
    with open(path) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def defense_results():
    """Load defense comparison results."""
    path = DEF_DIR / "defense_comparison.json"
    if not path.exists():
        pytest.skip("Defense results not found — run defenses.py first")
    with open(path) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Attack result tests
# ---------------------------------------------------------------------------

class TestAttackResults:
    """Verify adversarial attack result properties."""

    def test_asr_bounded_zero_one(self, unconstrained_results):
        """Attack success rate must be in [0, 1]."""
        for r in unconstrained_results:
            asr = r["attack_success_rate"]
            assert 0.0 <= asr <= 1.0, (
                f"ASR {asr} out of bounds for {r['model']} eps={r['epsilon']}"
            )

    def test_constrained_asr_bounded(self, constrained_results):
        """Constrained attack success rate must be in [0, 1]."""
        for r in constrained_results:
            asr = r["attack_success_rate"]
            assert 0.0 <= asr <= 1.0, (
                f"Constrained ASR {asr} out of bounds for {r['model']} eps={r['epsilon']}"
            )

    def test_f1_drops_with_attack(self, unconstrained_results):
        """Adversarial F1 should be <= clean F1 (attacks degrade performance)."""
        for r in unconstrained_results:
            assert r["adv_macro_f1"] <= r["clean_macro_f1"] + 0.01, (
                f"Adv F1 ({r['adv_macro_f1']}) > clean F1 ({r['clean_macro_f1']}) "
                f"for {r['model']} eps={r['epsilon']}"
            )

    def test_constrained_flag_correct(self, unconstrained_results, constrained_results):
        """Unconstrained results should have constrained=False, constrained=True."""
        for r in unconstrained_results:
            assert r["constrained"] is False
        for r in constrained_results:
            assert r["constrained"] is True

    def test_l2_perturbation_positive(self, unconstrained_results):
        """L2 perturbation norm must be non-negative."""
        for r in unconstrained_results:
            assert r["mean_l2_perturbation"] >= 0.0

    def test_results_have_required_keys(self, unconstrained_results):
        """Each result dict must contain required metric keys."""
        required = {
            "epsilon", "attack_type", "clean_macro_f1", "adv_macro_f1",
            "attack_success_rate", "mean_l2_perturbation", "model", "seed",
            "constrained",
        }
        for r in unconstrained_results:
            missing = required - set(r.keys())
            assert not missing, f"Missing keys: {missing}"


class TestConstrainedAttackLogic:
    """Verify constraint logic for feature perturbation."""

    def test_noise_perturbation_shape(self):
        """Random noise should match input shape."""
        rng = np.random.RandomState(42)
        X = rng.randn(100, 78).astype(np.float32)
        epsilon = 0.3
        noise = rng.uniform(-epsilon, epsilon, size=X.shape).astype(np.float32)
        assert noise.shape == X.shape

    def test_noise_bounded_by_epsilon(self):
        """Noise perturbation should be bounded by [-epsilon, +epsilon]."""
        rng = np.random.RandomState(42)
        epsilon = 0.3
        noise = rng.uniform(-epsilon, epsilon, size=(1000, 78)).astype(np.float32)
        assert noise.min() >= -epsilon - 1e-6
        assert noise.max() <= epsilon + 1e-6

    def test_constrained_mask_zeroes_observable(self):
        """Constrained perturbation should zero out defender-observable features."""
        # Simulate the masking operation from adversarial_attacks.py
        feature_cols = ATTACKER_CONTROLLABLE_FEATURES[:5] + DEFENDER_OBSERVABLE_ONLY[:3]
        mask = get_controllable_feature_mask(feature_cols).astype(np.float32)

        rng = np.random.RandomState(42)
        noise = rng.uniform(-0.3, 0.3, size=(10, 8)).astype(np.float32)
        constrained_noise = noise * mask

        # Observable features (last 3) should be zero
        np.testing.assert_array_equal(
            constrained_noise[:, 5:], 0.0,
            err_msg="Defender-observable features should not be perturbed"
        )
        # Controllable features (first 5) should be non-zero (with high probability)
        assert constrained_noise[:, :5].any(), "Controllable features should be perturbed"

    def test_noise_distribution_uniform(self):
        """Noise should be approximately uniformly distributed."""
        rng = np.random.RandomState(42)
        epsilon = 0.3
        noise = rng.uniform(-epsilon, epsilon, size=(10000,))
        # Mean should be close to 0
        assert abs(noise.mean()) < 0.01, f"Noise mean {noise.mean():.4f} not close to 0"
        # Std should be close to epsilon/sqrt(3) for uniform distribution
        expected_std = epsilon / np.sqrt(3)
        assert abs(noise.std() - expected_std) < 0.01


# ---------------------------------------------------------------------------
# Defense result tests
# ---------------------------------------------------------------------------

class TestDefenseResults:
    """Verify defense evaluation properties."""

    def test_defense_pipeline_results_exist(self, defense_results):
        """Defense comparison JSON should contain results."""
        assert len(defense_results) > 0, "Defense results should not be empty"

    def test_defense_types_present(self, defense_results):
        """All 4 defense types should be in results."""
        defense_types = {r["defense"] for r in defense_results}
        expected = {"none", "adversarial_training", "feature_squeezing",
                    "constraint_aware_detection"}
        assert expected.issubset(defense_types), (
            f"Missing defenses: {expected - defense_types}"
        )

    def test_recovery_ratios_bounded(self, defense_results):
        """Recovery ratios should be in reasonable range."""
        for r in defense_results:
            if "recovery_ratio" in r:
                rr = r["recovery_ratio"]
                assert -0.5 <= rr <= 1.5, (
                    f"Recovery ratio {rr} out of range for {r['defense']}/{r['model']}"
                )

    def test_constraint_aware_detection_rate(self, defense_results):
        """Constraint-aware detection should report a detection rate."""
        cad = [r for r in defense_results if r["defense"] == "constraint_aware_detection"]
        for r in cad:
            assert "detection_rate" in r, "Constraint-aware should include detection_rate"
            assert 0.0 <= r["detection_rate"] <= 1.0

    def test_no_defense_baseline_present(self, defense_results):
        """A 'none' (no defense) baseline should be present for comparison."""
        no_defense = [r for r in defense_results if r["defense"] == "none"]
        assert len(no_defense) >= 1, "Must have at least one no-defense baseline"
