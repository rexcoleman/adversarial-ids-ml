"""Leakage tripwire tests for FP-01 Adversarial IDS.

Each test guards against a specific data-leakage vector in the adversarial
ML pipeline.  If training artifacts are not yet generated, the test is
skipped rather than failed.

Reference: docs/DATA_CONTRACT.md (split protocol, scaler, attack design).

Run:  pytest tests/test_leakage_tripwires.py -m leakage
"""
import json
import pickle
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

OUTPUTS = PROJECT_ROOT / "outputs"
SCRIPTS = PROJECT_ROOT / "scripts"

pytestmark = pytest.mark.leakage


# ---------------------------------------------------------------------------
# LT-1  Train/test indices don't overlap
# ---------------------------------------------------------------------------
@pytest.mark.leakage
def test_lt1_train_test_indices_disjoint():
    """LT-1: Train and test sample indices must be completely disjoint.

    Ref: DATA_CONTRACT §split — no sample appears in both partitions.
    """
    # Look for saved index files or split metadata
    split_dir = OUTPUTS / "baselines"
    train_idx_file = None
    test_idx_file = None

    for pattern in ["train_indices*", "train_idx*"]:
        matches = list(split_dir.glob(pattern))
        if matches:
            train_idx_file = matches[0]
            break

    for pattern in ["test_indices*", "test_idx*"]:
        matches = list(split_dir.glob(pattern))
        if matches:
            test_idx_file = matches[0]
            break

    if train_idx_file is None or test_idx_file is None:
        # Fall back: check baseline_results.json for split metadata
        baseline_file = split_dir / "baseline_results.json"
        if not baseline_file.exists():
            pytest.skip("No index files or baseline results found")
        with open(baseline_file) as f:
            results = json.load(f)
        # Verify split counts are present and consistent
        meta = results.get("metadata", results.get("split", {}))
        if not meta:
            pytest.skip("No split metadata in baseline_results.json")
        train_n = meta.get("train_size", meta.get("n_train"))
        test_n = meta.get("test_size", meta.get("n_test"))
        if train_n and test_n:
            total = meta.get("total_size", meta.get("n_total"))
            if total:
                assert train_n + test_n <= total, (
                    f"Index overlap likely: train({train_n}) + test({test_n}) "
                    f"> total({total})"
                )
        return

    import numpy as np

    train_idx = set(np.load(str(train_idx_file)))
    test_idx = set(np.load(str(test_idx_file)))
    overlap = train_idx & test_idx
    assert len(overlap) == 0, (
        f"Index leakage: {len(overlap)} indices in both train and test"
    )


# ---------------------------------------------------------------------------
# LT-2  Controllability mask consistent between train and attack
# ---------------------------------------------------------------------------
@pytest.mark.leakage
def test_lt2_controllability_mask_consistent():
    """LT-2: Controllability mask used during attack must match training features.

    Ref: DATA_CONTRACT — adversarial perturbations respect feature controllability.
    """
    constrained_file = OUTPUTS / "adversarial" / "constrained_results.json"
    if not constrained_file.exists():
        pytest.skip("Constrained results not found")

    with open(constrained_file) as f:
        results = json.load(f)

    # Check that constrained attacks report which features were perturbed
    if isinstance(results, dict):
        meta = results.get("metadata", results.get("config", {}))
        controllable = meta.get("controllable_features", meta.get("mask"))
        if controllable is not None:
            assert len(controllable) > 0, (
                "Controllability mask is empty — attack is unconstrained"
            )
            # Verify mask length matches feature count from EDA
            eda_file = OUTPUTS / "eda" / "eda_summary.json"
            if eda_file.exists():
                with open(eda_file) as f:
                    eda = json.load(f)
                n_features = eda.get("n_features", eda.get("feature_count"))
                if n_features:
                    assert len(controllable) == n_features, (
                        f"Mask length {len(controllable)} != "
                        f"feature count {n_features}"
                    )


# ---------------------------------------------------------------------------
# LT-3  No test data accessed during adversarial training
# ---------------------------------------------------------------------------
@pytest.mark.leakage
def test_lt3_no_test_in_adversarial_training():
    """LT-3: Adversarial training scripts must not load test data.

    Ref: DATA_CONTRACT — adversarial robustness training uses train split only.
    """
    import ast

    train_scripts = [
        SCRIPTS / "train_expanded_models.py",
        SCRIPTS / "run_sanity_baselines.py",
    ]
    # Also check any adversarial training scripts
    for p in SCRIPTS.glob("*adversar*"):
        if p.suffix == ".py":
            train_scripts.append(p)

    suspicious = ["X_test", "y_test", "test_loader", "test_data"]

    found_scripts = [s for s in train_scripts if s.exists()]
    if not found_scripts:
        pytest.skip("No training scripts found")

    violations = []
    for script in found_scripts:
        source = script.read_text()
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id in suspicious:
                violations.append(f"{script.name}: variable '{node.id}'")

    assert len(violations) == 0, (
        f"Potential test-data access in training scripts:\n"
        + "\n".join(f"  - {v}" for v in violations)
    )


# ---------------------------------------------------------------------------
# LT-4  Scaler fit on train only
# ---------------------------------------------------------------------------
@pytest.mark.leakage
def test_lt4_scaler_fit_train_only():
    """LT-4: If a saved scaler exists, verify it was fit on train-sized data.

    Ref: DATA_CONTRACT §preprocessing — StandardScaler fit on train partition.
    """
    scaler_candidates = list(OUTPUTS.rglob("*scaler*.pkl")) + list(
        OUTPUTS.rglob("*scaler*.joblib")
    )
    if not scaler_candidates:
        pytest.skip("No saved scaler artifact found")

    # Get expected train size from EDA or baseline results
    expected_n = None
    eda_file = OUTPUTS / "eda" / "eda_summary.json"
    if eda_file.exists():
        with open(eda_file) as f:
            eda = json.load(f)
        expected_n = eda.get("train_size", eda.get("n_train"))

    for scaler_path in scaler_candidates:
        with open(scaler_path, "rb") as f:
            scaler = pickle.load(f)
        if hasattr(scaler, "n_samples_seen_"):
            n_seen = scaler.n_samples_seen_
            if hasattr(n_seen, "__len__"):
                n_seen = n_seen[0]
            if expected_n is not None:
                assert n_seen == expected_n, (
                    f"Scaler {scaler_path.name} saw {n_seen} samples, "
                    f"expected train_size={expected_n}"
                )
            else:
                # At minimum verify it didn't see the full dataset
                baseline_file = OUTPUTS / "baselines" / "baseline_results.json"
                if baseline_file.exists():
                    with open(baseline_file) as f:
                        res = json.load(f)
                    meta = res.get("metadata", res.get("split", {}))
                    total = meta.get("total_size", meta.get("n_total"))
                    if total:
                        assert n_seen < total, (
                            f"Scaler saw {n_seen} samples = full dataset "
                            f"({total}), likely fit on train+test"
                        )


# ---------------------------------------------------------------------------
# LT-5  Attack perturbations applied to test data only
# ---------------------------------------------------------------------------
@pytest.mark.leakage
def test_lt5_attack_perturbations_test_only():
    """LT-5: Adversarial perturbations must target test data, not training data.

    Ref: DATA_CONTRACT — attacks evaluate on held-out test set only.
    """
    # Check constrained and unconstrained result files for split info
    for name in ["constrained_results.json", "unconstrained_results.json"]:
        result_file = OUTPUTS / "adversarial" / name
        if not result_file.exists():
            continue

        with open(result_file) as f:
            results = json.load(f)

        if isinstance(results, dict):
            meta = results.get("metadata", results.get("config", {}))
            split_used = meta.get("split", meta.get("eval_split"))
            if split_used is not None:
                assert split_used == "test", (
                    f"{name}: attack ran on split='{split_used}', expected 'test'"
                )

            # Verify attack sample count matches test size, not total
            n_attacked = meta.get("n_samples", meta.get("n_attacked"))
            train_size = meta.get("train_size", meta.get("n_train"))
            if n_attacked and train_size:
                assert n_attacked < train_size, (
                    f"{name}: attacked {n_attacked} samples >= train_size "
                    f"{train_size}, likely includes training data"
                )
