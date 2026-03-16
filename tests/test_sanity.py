"""Tests for sanity baseline checks.

These tests verify that real models meaningfully outperform trivial baselines,
ruling out data leakage and label artifacts.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

BASELINE_DIR = PROJECT_DIR / "outputs" / "baselines"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def sanity_summary():
    """Load sanity baseline summary."""
    path = BASELINE_DIR / "sanity_summary.json"
    if not path.exists():
        pytest.skip("Sanity summary not found -- run run_sanity_baselines.py first")
    with open(path) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def baseline_results():
    """Load baseline model results."""
    path = BASELINE_DIR / "baseline_results.json"
    if not path.exists():
        pytest.skip("Baseline results not found -- run train_baselines.py first")
    with open(path) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestSanityBaselines:
    """Verify sanity check results."""

    def test_all_seeds_pass_sanity(self, sanity_summary):
        """All seeds should pass the sanity gap check (real >> dummy + shuffled)."""
        assert sanity_summary["all_pass"] is True, (
            "Not all seeds passed sanity check"
        )

    def test_real_model_beats_dummy_by_5pp(self, sanity_summary):
        """Real RF model should beat best dummy by >= 5pp on every seed."""
        for seed_result in sanity_summary["per_seed"]:
            gap = seed_result["sanity_gap_vs_dummy"]
            assert gap >= 0.05, (
                f"Seed {seed_result['seed']}: gap vs dummy = {gap:.4f} (need >= 0.05)"
            )

    def test_shuffled_model_worse_than_real(self, sanity_summary):
        """Shuffled-label model should be substantially worse than real model."""
        for seed_result in sanity_summary["per_seed"]:
            gap = seed_result["sanity_gap_vs_shuffled"]
            assert gap > 0.1, (
                f"Seed {seed_result['seed']}: gap vs shuffled = {gap:.4f} (need > 0.1)"
            )

    def test_consistent_results_across_seeds(self, sanity_summary):
        """Sanity gap should be consistent across seeds (std < 0.05)."""
        gaps = [r["sanity_gap_vs_shuffled"] for r in sanity_summary["per_seed"]]
        if len(gaps) < 2:
            pytest.skip("Need >= 2 seeds for consistency check")
        std = np.std(gaps)
        assert std < 0.05, (
            f"Sanity gap std = {std:.4f} (need < 0.05). Gaps: {gaps}"
        )


class TestBaselineQuality:
    """Verify baseline model performance thresholds."""

    def test_at_least_two_models_above_0_8(self, baseline_results):
        """At least 2 of 3 baseline models should achieve macro-F1 > 0.8."""
        results = baseline_results["results"]
        # Group by model, take mean F1 across seeds
        model_f1s = {}
        for r in results:
            model_f1s.setdefault(r["model"], []).append(r["test_macro_f1"])

        above_threshold = 0
        for model, f1s in model_f1s.items():
            if np.mean(f1s) > 0.8:
                above_threshold += 1

        assert above_threshold >= 2, (
            f"Only {above_threshold} models above 0.8 F1. "
            f"Model means: {[(m, np.mean(f)) for m, f in model_f1s.items()]}"
        )

    def test_xgboost_is_strongest_baseline(self, baseline_results):
        """XGBoost should have the highest mean macro-F1 among baselines."""
        results = baseline_results["results"]
        model_f1s = {}
        for r in results:
            model_f1s.setdefault(r["model"], []).append(r["test_macro_f1"])

        model_means = {m: np.mean(f) for m, f in model_f1s.items()}
        best_model = max(model_means, key=model_means.get)
        assert best_model == "XGBoost", (
            f"Expected XGBoost as best, got {best_model}. Means: {model_means}"
        )

    def test_model_f1_std_below_threshold(self, baseline_results):
        """Model F1 standard deviation across seeds should be < 0.05."""
        results = baseline_results["results"]
        model_f1s = {}
        for r in results:
            model_f1s.setdefault(r["model"], []).append(r["test_macro_f1"])

        for model, f1s in model_f1s.items():
            if len(f1s) >= 2:
                std = np.std(f1s)
                assert std < 0.05, (
                    f"{model} F1 std = {std:.4f} (need < 0.05). Values: {f1s}"
                )

    def test_baseline_results_have_per_class_f1(self, baseline_results):
        """Each result should include per-class F1 scores."""
        for r in baseline_results["results"]:
            assert "per_class_f1" in r, f"Missing per_class_f1 in {r['model']} seed {r['seed']}"
            assert len(r["per_class_f1"]) > 0, "per_class_f1 should not be empty"

    def test_sanity_files_exist_per_seed(self, sanity_summary):
        """Per-seed sanity result files should exist."""
        for seed_result in sanity_summary["per_seed"]:
            seed = seed_result["seed"]
            path = BASELINE_DIR / f"sanity_seed{seed}.json"
            assert path.exists(), f"Missing sanity file for seed {seed}: {path}"
