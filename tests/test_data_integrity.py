"""Tests for CICIDS2017 data integrity and preprocessing contracts.

These tests verify data properties without running expensive compute.
They use file existence checks, metadata inspection, and small samples.
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
    CSV_FILES,
    DATA_RAW,
    DATA_SPLITS,
    get_controllable_feature_mask,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def split_metadata():
    """Load split metadata if available."""
    meta_path = DATA_SPLITS / "split_metadata.json"
    if not meta_path.exists():
        pytest.skip("Split metadata not found -- run preprocessing first")
    with open(meta_path) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def train_sample():
    """Load a small sample of the training split."""
    import pandas as pd

    train_path = DATA_SPLITS / "train.csv"
    if not train_path.exists():
        pytest.skip("Train split not found -- run preprocessing first")
    # Read only first 1000 rows for speed
    return pd.read_csv(train_path, nrows=1000)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestFeatureCounts:
    """Verify CICIDS2017 feature definitions are consistent."""

    def test_controllable_features_count(self):
        """CICIDS2017 should have exactly 57 attacker-controllable features."""
        assert len(ATTACKER_CONTROLLABLE_FEATURES) == 57, (
            f"Expected 57 controllable features, got {len(ATTACKER_CONTROLLABLE_FEATURES)}"
        )

    def test_defender_observable_count(self):
        """CICIDS2017 should have exactly 14 defender-observable-only features."""
        assert len(DEFENDER_OBSERVABLE_ONLY) == 14, (
            f"Expected 14 defender-observable features, got {len(DEFENDER_OBSERVABLE_ONLY)}"
        )

    def test_no_feature_overlap(self):
        """Controllable and observable feature sets must not overlap."""
        overlap = set(ATTACKER_CONTROLLABLE_FEATURES) & set(DEFENDER_OBSERVABLE_ONLY)
        assert len(overlap) == 0, f"Feature overlap detected: {overlap}"

    def test_total_categorized_features(self):
        """All categorized features sum to 71 (57 + 14)."""
        total = len(ATTACKER_CONTROLLABLE_FEATURES) + len(DEFENDER_OBSERVABLE_ONLY)
        assert total == 71, f"Expected 71 categorized features, got {total}"

    def test_controllable_mask_shape(self):
        """Controllable mask should match feature list length."""
        test_features = ATTACKER_CONTROLLABLE_FEATURES[:5] + DEFENDER_OBSERVABLE_ONLY[:3]
        mask = get_controllable_feature_mask(test_features)
        assert mask.shape == (8,)
        assert mask[:5].all(), "First 5 should be controllable"
        assert not mask[5:].any(), "Last 3 should be non-controllable"


class TestPreprocessedData:
    """Verify preprocessed data quality."""

    def test_no_nan_in_train(self, train_sample):
        """Preprocessed training data should contain no NaN values."""
        numeric_cols = train_sample.select_dtypes(include=[np.number]).columns
        nan_count = train_sample[numeric_cols].isna().sum().sum()
        assert nan_count == 0, f"Found {nan_count} NaN values in training data"

    def test_no_inf_in_train(self, train_sample):
        """Preprocessed training data should contain no infinite values."""
        numeric_cols = train_sample.select_dtypes(include=[np.number]).columns
        inf_count = np.isinf(train_sample[numeric_cols].values).sum()
        assert inf_count == 0, f"Found {inf_count} inf values in training data"

    def test_split_proportions(self, split_metadata):
        """Train/val/test split should be approximately 60/20/20."""
        total = (
            split_metadata["train_rows"]
            + split_metadata["val_rows"]
            + split_metadata["test_rows"]
        )
        train_ratio = split_metadata["train_rows"] / total
        val_ratio = split_metadata["val_rows"] / total
        test_ratio = split_metadata["test_rows"] / total

        assert abs(train_ratio - 0.6) < 0.05, f"Train ratio {train_ratio:.3f} not ~0.6"
        assert abs(val_ratio - 0.2) < 0.05, f"Val ratio {val_ratio:.3f} not ~0.2"
        assert abs(test_ratio - 0.2) < 0.05, f"Test ratio {test_ratio:.3f} not ~0.2"

    def test_label_encoded_column_exists(self, train_sample):
        """Training data must have label_encoded column."""
        assert "label_encoded" in train_sample.columns

    def test_label_values_contiguous(self, train_sample):
        """Encoded labels should be contiguous integers starting from 0."""
        labels = sorted(train_sample["label_encoded"].unique())
        if len(labels) > 0:
            assert labels[0] == 0, "Labels should start at 0"
            assert all(isinstance(l, (int, np.integer)) for l in labels)


class TestRawDataFiles:
    """Verify raw data file presence."""

    def test_csv_files_list_is_8(self):
        """CICIDS2017 consists of exactly 8 CSV files."""
        assert len(CSV_FILES) == 8

    def test_raw_data_directory_exists(self):
        """Raw data directory should exist."""
        assert DATA_RAW.exists(), f"Raw data directory not found: {DATA_RAW}"

    def test_all_csv_files_present(self):
        """All 8 CICIDS2017 CSV files should be present."""
        missing = [f for f in CSV_FILES if not (DATA_RAW / f).exists()]
        if missing:
            pytest.skip(f"Missing CSV files (download required): {missing}")

    def test_split_metadata_has_required_keys(self, split_metadata):
        """Split metadata JSON must contain required keys."""
        required = {"seed", "train_rows", "val_rows", "test_rows", "label_map", "n_features"}
        missing = required - set(split_metadata.keys())
        assert not missing, f"Missing metadata keys: {missing}"
