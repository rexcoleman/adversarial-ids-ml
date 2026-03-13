#!/usr/bin/env bash
# verify_env.sh — Phase 0 gate: verify conda environment matches environment.yml
set -euo pipefail

EXPECTED_ENV="adversarial-ids"
EXPECTED_PYTHON="3.10"

echo "=== Environment Verification ==="

# Check conda env is active
if [[ "${CONDA_DEFAULT_ENV:-}" != "$EXPECTED_ENV" ]]; then
    echo "FAIL: Expected conda env '$EXPECTED_ENV', got '${CONDA_DEFAULT_ENV:-none}'"
    echo "  Run: conda activate $EXPECTED_ENV"
    exit 1
fi
echo "PASS: Conda env = $EXPECTED_ENV"

# Check Python version
PY_VER=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if [[ "$PY_VER" != "$EXPECTED_PYTHON" ]]; then
    echo "FAIL: Expected Python $EXPECTED_PYTHON, got $PY_VER"
    exit 1
fi
echo "PASS: Python = $PY_VER"

# Check critical packages
PACKAGES=(
    "numpy"
    "pandas"
    "sklearn"
    "matplotlib"
    "xgboost"
    "art"
    "torch"
    "scipy"
    "pytest"
    "yaml"
)

for pkg in "${PACKAGES[@]}"; do
    if python -c "import $pkg" 2>/dev/null; then
        VERSION=$(python -c "import $pkg; print(getattr($pkg, '__version__', 'ok'))" 2>/dev/null || echo "ok")
        echo "PASS: $pkg ($VERSION)"
    else
        echo "FAIL: $pkg not importable"
        exit 1
    fi
done

echo ""
echo "=== All checks passed ==="
