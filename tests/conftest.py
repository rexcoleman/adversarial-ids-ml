"""Shared fixtures for adversarial-ids-ml test suite."""
import json
import sys
from pathlib import Path

import pytest

# Ensure project root is on path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

OUTPUTS = PROJECT_ROOT / "outputs"
BASELINES_FILE = OUTPUTS / "baselines" / "baseline_results.json"
EXPANDED_SUMMARY = OUTPUTS / "models" / "expanded_summary.json"
CONSTRAINED_FILE = OUTPUTS / "adversarial" / "constrained_results.json"
UNCONSTRAINED_FILE = OUTPUTS / "adversarial" / "unconstrained_results.json"
DEFENSE_FILE = OUTPUTS / "defense" / "defense_comparison.json"
EDA_FILE = OUTPUTS / "eda" / "eda_summary.json"
LEARNING_CURVES_FILE = OUTPUTS / "diagnostics" / "learning_curves_seed42.json"
LEARNING_CURVES_SUMMARY = OUTPUTS / "diagnostics" / "learning_curves_summary.json"

SEEDS = [42, 123, 456, 789, 1024]
BASELINE_MODELS = ["RandomForest", "XGBoost", "MLP"]
EXPANDED_MODELS = ["SVM-RBF", "LightGBM"]
ALL_MODELS = BASELINE_MODELS + EXPANDED_MODELS

EXPECTED_CLASSES = [
    "BENIGN", "Bot", "DDoS", "DoS GoldenEye", "DoS Hulk",
    "DoS Slowhttptest", "DoS slowloris", "FTP-Patator", "PortScan",
    "SSH-Patator", "Web Attack \ufffd Brute Force", "Web Attack \ufffd XSS",
]


@pytest.fixture
def baseline_results():
    """Load baseline results JSON."""
    with open(BASELINES_FILE) as f:
        return json.load(f)


@pytest.fixture
def expanded_summary():
    """Load expanded model summary JSON."""
    with open(EXPANDED_SUMMARY) as f:
        return json.load(f)


@pytest.fixture
def constrained_results():
    """Load constrained attack results."""
    with open(CONSTRAINED_FILE) as f:
        return json.load(f)


@pytest.fixture
def unconstrained_results():
    """Load unconstrained attack results."""
    with open(UNCONSTRAINED_FILE) as f:
        return json.load(f)


@pytest.fixture
def defense_results():
    """Load defense comparison results."""
    with open(DEFENSE_FILE) as f:
        return json.load(f)


@pytest.fixture
def eda_summary():
    """Load EDA summary."""
    with open(EDA_FILE) as f:
        return json.load(f)


@pytest.fixture
def learning_curves():
    """Load learning curve data."""
    with open(LEARNING_CURVES_FILE) as f:
        return json.load(f)
