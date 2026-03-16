"""Tests for reproducibility contracts.

These tests verify that:
- Seed protocol produces deterministic outputs
- Output files contain required structure
- Figure artifacts exist (if generated)
"""

import json
import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))


# ---------------------------------------------------------------------------
# Tests: Seed determinism
# ---------------------------------------------------------------------------

class TestSeedDeterminism:
    """Verify that setting the same seed produces identical outputs."""

    def test_numpy_seed_determinism(self):
        """Same numpy seed should produce identical random arrays."""
        rng1 = np.random.RandomState(42)
        arr1 = rng1.uniform(-0.3, 0.3, size=(100, 78))

        rng2 = np.random.RandomState(42)
        arr2 = rng2.uniform(-0.3, 0.3, size=(100, 78))

        np.testing.assert_array_equal(arr1, arr2,
                                      err_msg="Same seed should produce identical arrays")

    def test_different_seeds_differ(self):
        """Different seeds should produce different random arrays."""
        rng1 = np.random.RandomState(42)
        arr1 = rng1.uniform(-0.3, 0.3, size=(100, 78))

        rng2 = np.random.RandomState(123)
        arr2 = rng2.uniform(-0.3, 0.3, size=(100, 78))

        assert not np.array_equal(arr1, arr2), "Different seeds should differ"

    def test_set_seed_function_exists(self):
        """Project set_seed function should be importable."""
        from src.preprocessing import set_seed
        # Should not raise
        set_seed(42)

    def test_controllable_mask_deterministic(self):
        """Controllable mask should be deterministic for same feature list."""
        from src.preprocessing import (
            get_controllable_feature_mask,
            ATTACKER_CONTROLLABLE_FEATURES,
            DEFENDER_OBSERVABLE_ONLY,
        )
        features = list(ATTACKER_CONTROLLABLE_FEATURES[:10]) + list(DEFENDER_OBSERVABLE_ONLY[:5])
        mask1 = get_controllable_feature_mask(features)
        mask2 = get_controllable_feature_mask(features)
        np.testing.assert_array_equal(mask1, mask2)

    def test_label_encoder_deterministic(self):
        """LabelEncoder should produce same encoding for same input."""
        from sklearn.preprocessing import LabelEncoder

        labels = ["BENIGN", "DDoS", "Bot", "PortScan", "BENIGN", "DDoS"]
        le1 = LabelEncoder()
        enc1 = le1.fit_transform(labels)
        le2 = LabelEncoder()
        enc2 = le2.fit_transform(labels)
        np.testing.assert_array_equal(enc1, enc2)


# ---------------------------------------------------------------------------
# Tests: Output file structure
# ---------------------------------------------------------------------------

class TestOutputFileStructure:
    """Verify output JSON files have required schema."""

    def test_baseline_results_schema(self):
        """Baseline results JSON must have correct top-level keys."""
        path = PROJECT_DIR / "outputs" / "baselines" / "baseline_results.json"
        if not path.exists():
            pytest.skip("baseline_results.json not found")
        with open(path) as f:
            data = json.load(f)
        assert "experiment" in data
        assert "seeds" in data
        assert "models" in data
        assert "results" in data
        assert isinstance(data["results"], list)

    def test_adversarial_results_schema(self):
        """Adversarial results JSON must be a list of result dicts."""
        path = PROJECT_DIR / "outputs" / "adversarial" / "unconstrained_results.json"
        if not path.exists():
            pytest.skip("unconstrained_results.json not found")
        with open(path) as f:
            data = json.load(f)
        assert isinstance(data, list)
        if data:
            required = {"epsilon", "attack_type", "clean_macro_f1", "adv_macro_f1",
                        "attack_success_rate", "model", "seed"}
            missing = required - set(data[0].keys())
            assert not missing, f"Missing keys in adversarial result: {missing}"

    def test_defense_results_schema(self):
        """Defense results JSON must be a list with defense field."""
        path = PROJECT_DIR / "outputs" / "defense" / "defense_comparison.json"
        if not path.exists():
            pytest.skip("defense_comparison.json not found")
        with open(path) as f:
            data = json.load(f)
        assert isinstance(data, list)
        if data:
            assert "defense" in data[0]
            assert "model" in data[0]

    def test_split_metadata_schema(self):
        """Split metadata must have correct schema."""
        path = PROJECT_DIR / "data" / "splits" / "split_metadata.json"
        if not path.exists():
            pytest.skip("split_metadata.json not found")
        with open(path) as f:
            data = json.load(f)
        required = {"seed", "train_rows", "val_rows", "test_rows", "label_map",
                     "n_features", "split_ratio"}
        missing = required - set(data.keys())
        assert not missing, f"Missing metadata keys: {missing}"

    def test_sanity_summary_schema(self):
        """Sanity summary must have correct schema."""
        path = PROJECT_DIR / "outputs" / "baselines" / "sanity_summary.json"
        if not path.exists():
            pytest.skip("sanity_summary.json not found")
        with open(path) as f:
            data = json.load(f)
        assert "all_pass" in data
        assert "per_seed" in data
        assert isinstance(data["per_seed"], list)


# ---------------------------------------------------------------------------
# Tests: Figure artifacts
# ---------------------------------------------------------------------------

class TestFigureArtifacts:
    """Verify figure files exist if output directories are populated."""

    EXPECTED_FIGURES = [
        "outputs/baselines/per_class_f1.png",
        "outputs/adversarial/budget_curve_RandomForest_seed42.png",
        "outputs/adversarial/budget_curve_XGBoost_seed42.png",
        "outputs/defense/defense_recovery.png",
    ]

    @pytest.mark.parametrize("fig_path", EXPECTED_FIGURES)
    def test_figure_exists(self, fig_path):
        """Expected figure file should exist."""
        full_path = PROJECT_DIR / fig_path
        parent = full_path.parent
        if not parent.exists():
            pytest.skip(f"Output directory not found: {parent}")
        if not full_path.exists():
            pytest.skip(f"Figure not found (may not have been generated): {full_path}")
        assert full_path.stat().st_size > 0, f"Figure file is empty: {full_path}"

    def test_confusion_matrix_exists_for_seed42(self):
        """At least one confusion matrix should exist for seed 42."""
        cm_dir = PROJECT_DIR / "outputs" / "baselines"
        if not cm_dir.exists():
            pytest.skip("Baselines output dir not found")
        cm_files = list(cm_dir.glob("confusion_matrix_*_seed42.png"))
        if not cm_files:
            pytest.skip("No confusion matrix files for seed 42")
        for f in cm_files:
            assert f.stat().st_size > 0, f"Confusion matrix empty: {f}"
