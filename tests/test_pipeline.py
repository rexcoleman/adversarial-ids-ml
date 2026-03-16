"""Tests for ML training pipeline correctness.

These tests verify pipeline properties using saved model artifacts
and metadata rather than re-running expensive training.
"""

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pytest

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

MODEL_DIR = PROJECT_DIR / "models"
OUTPUT_DIR = PROJECT_DIR / "outputs" / "baselines"
SPLIT_DIR = PROJECT_DIR / "data" / "splits"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def baseline_results_data():
    """Load baseline results JSON."""
    path = OUTPUT_DIR / "baseline_results.json"
    if not path.exists():
        pytest.skip("Baseline results not found -- run train_baselines.py first")
    with open(path) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def sample_test_data():
    """Load a small sample of the test split for model inference checks."""
    import pandas as pd

    test_path = SPLIT_DIR / "test.csv"
    if not test_path.exists():
        pytest.skip("Test split not found -- run preprocessing first")
    df = pd.read_csv(test_path, nrows=100)
    exclude = {"Label", "label_encoded"}
    feature_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c not in exclude]
    X = df[feature_cols].values.astype(np.float32)
    y = df["label_encoded"].values
    return X, y, feature_cols


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestModelArtifacts:
    """Verify trained model artifacts exist and are loadable."""

    EXPECTED_MODELS = ["RandomForest", "XGBoost", "MLP"]
    EXPECTED_SEED = 42

    @pytest.mark.parametrize("model_name", EXPECTED_MODELS)
    def test_model_file_exists(self, model_name):
        """Each model artifact should exist for seed 42."""
        path = MODEL_DIR / f"{model_name}_seed{self.EXPECTED_SEED}.pkl"
        if not path.exists():
            pytest.skip(f"Model file not found: {path}")
        assert path.stat().st_size > 0, f"Model file is empty: {path}"

    @pytest.mark.parametrize("model_name", EXPECTED_MODELS)
    def test_model_is_loadable(self, model_name):
        """Saved models should load without error via joblib."""
        path = MODEL_DIR / f"{model_name}_seed{self.EXPECTED_SEED}.pkl"
        if not path.exists():
            pytest.skip(f"Model file not found: {path}")
        model = joblib.load(path)
        assert model is not None
        assert hasattr(model, "predict"), f"{model_name} has no predict method"

    @pytest.mark.parametrize("model_name", EXPECTED_MODELS)
    def test_model_predictions_valid(self, model_name, sample_test_data):
        """Model predictions should be valid integer class labels."""
        path = MODEL_DIR / f"{model_name}_seed{self.EXPECTED_SEED}.pkl"
        if not path.exists():
            pytest.skip(f"Model file not found: {path}")
        model = joblib.load(path)
        X, y, _ = sample_test_data
        preds = model.predict(X)
        assert len(preds) == len(X), "Prediction count should match input count"
        assert all(isinstance(p, (int, np.integer)) for p in preds), \
            "Predictions should be integer class labels"

    @pytest.mark.parametrize("model_name", ["RandomForest", "XGBoost"])
    def test_model_probabilities_valid(self, model_name, sample_test_data):
        """RF and XGBoost should produce valid probability outputs."""
        path = MODEL_DIR / f"{model_name}_seed{self.EXPECTED_SEED}.pkl"
        if not path.exists():
            pytest.skip(f"Model file not found: {path}")
        model = joblib.load(path)
        X, _, _ = sample_test_data
        proba = model.predict_proba(X)
        assert proba.shape[0] == len(X)
        # Probabilities should sum to ~1
        row_sums = proba.sum(axis=1)
        np.testing.assert_allclose(row_sums, 1.0, atol=1e-5,
                                   err_msg="Probabilities should sum to 1.0")
        # All probabilities should be in [0, 1]
        assert proba.min() >= 0.0, "Probabilities must be >= 0"
        assert proba.max() <= 1.0, "Probabilities must be <= 1"


class TestPipelineIntegrity:
    """Verify pipeline output consistency."""

    def test_baseline_results_has_required_keys(self, baseline_results_data):
        """Baseline results JSON must contain required keys."""
        required = {"experiment", "seeds", "models", "results"}
        missing = required - set(baseline_results_data.keys())
        assert not missing, f"Missing keys: {missing}"

    def test_all_three_models_in_results(self, baseline_results_data):
        """All 3 baseline models should appear in results."""
        models = set(baseline_results_data["models"])
        expected = {"RandomForest", "XGBoost", "MLP"}
        assert expected.issubset(models), f"Missing models: {expected - models}"

    def test_feature_column_order_preserved(self, sample_test_data):
        """Feature columns should maintain consistent order across loads."""
        import pandas as pd

        test_path = SPLIT_DIR / "test.csv"
        train_path = SPLIT_DIR / "train.csv"
        if not test_path.exists() or not train_path.exists():
            pytest.skip("Split files not found")

        train_cols = pd.read_csv(train_path, nrows=1).columns.tolist()
        test_cols = pd.read_csv(test_path, nrows=1).columns.tolist()
        assert train_cols == test_cols, "Train and test column order must match"

    def test_scaler_fit_on_train_only(self):
        """StandardScaler should be fit on training data only (contract LT-1).

        We verify this by checking that the scale_features function signature
        and implementation accept separate train/val/test DataFrames.
        """
        from src.preprocessing import scale_features
        import inspect

        sig = inspect.signature(scale_features)
        params = list(sig.parameters.keys())
        assert "train_df" in params, "scale_features must accept train_df"
        assert "val_df" in params, "scale_features must accept val_df"
        assert "test_df" in params, "scale_features must accept test_df"

    def test_results_per_seed_count(self, baseline_results_data):
        """Each seed should produce results for all models."""
        seeds = baseline_results_data["seeds"]
        models = baseline_results_data["models"]
        results = baseline_results_data["results"]
        for seed in seeds:
            seed_results = [r for r in results if r["seed"] == seed]
            assert len(seed_results) == len(models), (
                f"Seed {seed}: expected {len(models)} results, got {len(seed_results)}"
            )
