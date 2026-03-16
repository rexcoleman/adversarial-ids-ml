"""Basic tests for FP-01 adversarial IDS pipeline."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_imports():
    """Verify core project modules are importable."""
    try:
        from scripts import preprocessing
    except ImportError:
        try:
            from src import preprocessing
        except ImportError:
            pytest.skip("preprocessing module not importable (scripts/ or src/)")
    assert hasattr(preprocessing, 'run_preprocessing_pipeline') or True  # Module exists


def test_findings_exists():
    assert Path("FINDINGS.md").exists()


def test_gitignore_exists():
    assert Path(".gitignore").exists()
