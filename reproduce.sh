#!/usr/bin/env bash
# reproduce.sh — Full reproduction pipeline for FP-01 Adversarial IDS
#
# Reproduces all results from FINDINGS.md:
#   1. Environment setup (conda)
#   2. Data download + verification
#   3. Baseline training (5 seeds x 3 models)
#   4. Expanded model training (5 seeds x 2 models)
#   5. Sanity baselines (dummy + shuffled)
#   6. Adversarial attack experiments
#   7. Defense experiments
#   8. Figure generation
#
# Usage:
#   bash reproduce.sh              # Full pipeline
#   bash reproduce.sh --skip-env   # Skip conda env creation
#   bash reproduce.sh --sample 0.1 # Use 10% data sample (fast)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
DATA_DIR="${PROJECT_DIR}/data/raw"

# --- Parse arguments ---
SKIP_ENV=false
SAMPLE_FRAC=""
SEEDS="42 123 456 789 1024"

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-env)
            SKIP_ENV=true
            shift
            ;;
        --sample)
            SAMPLE_FRAC="$2"
            shift 2
            ;;
        --seeds)
            SEEDS="$2"
            shift 2
            ;;
        *)
            echo "Unknown argument: $1"
            echo "Usage: bash reproduce.sh [--skip-env] [--sample FRAC] [--seeds '42 123']"
            exit 1
            ;;
    esac
done

SAMPLE_ARG=""
if [[ -n "$SAMPLE_FRAC" ]]; then
    SAMPLE_ARG="--sample-frac $SAMPLE_FRAC"
    echo "NOTE: Using ${SAMPLE_FRAC} data sample (results will differ from FINDINGS.md)"
fi

echo "============================================================"
echo "FP-01 Adversarial IDS — Full Reproduction Pipeline"
echo "============================================================"
echo "Project dir: $PROJECT_DIR"
echo "Seeds: $SEEDS"
echo "Sample fraction: ${SAMPLE_FRAC:-1.0 (full dataset)}"
echo ""

# --- Step 1: Environment setup ---
if [[ "$SKIP_ENV" == false ]]; then
    echo "=== Step 1: Creating conda environment ==="
    if conda env list | grep -q "adversarial-ids"; then
        echo "  Environment 'adversarial-ids' already exists. Updating..."
        conda env update -f "${PROJECT_DIR}/environment.yml" --prune
    else
        echo "  Creating environment from environment.yml..."
        conda env create -f "${PROJECT_DIR}/environment.yml"
    fi
    echo "  Done."
    echo ""
else
    echo "=== Step 1: Skipping environment setup (--skip-env) ==="
    echo ""
fi

# Activate environment
echo "Activating conda environment 'adversarial-ids'..."
eval "$(conda shell.bash hook)"
conda activate adversarial-ids

# --- Step 2: Data download + verification ---
echo ""
echo "=== Step 2: Data download and verification ==="
if [[ -d "$DATA_DIR" ]] && [[ $(ls "$DATA_DIR"/*.csv 2>/dev/null | wc -l) -eq 8 ]]; then
    echo "  All 8 CICIDS2017 CSV files found. Skipping download."
else
    echo "  Downloading CICIDS2017 dataset..."
    bash "${PROJECT_DIR}/scripts/download_data.sh"
fi

echo "  Verifying data integrity..."
python "${PROJECT_DIR}/scripts/check_data_ready.py"
echo "  Done."

# --- Step 3: Baseline training (RF, XGBoost, MLP) ---
echo ""
echo "=== Step 3: Training baseline models (RF, XGBoost, MLP) ==="
echo "  Seeds: $SEEDS"
python "${PROJECT_DIR}/src/train_baselines.py" \
    --seeds $SEEDS \
    $SAMPLE_ARG
echo "  Done. Results: outputs/baselines/baseline_results.json"

# --- Step 4: Expanded models (SVM-RBF, LightGBM) ---
echo ""
echo "=== Step 4: Training expanded models (SVM-RBF, LightGBM) ==="
python "${PROJECT_DIR}/scripts/train_expanded_models.py" \
    --project-dir "$PROJECT_DIR" \
    --seeds $SEEDS \
    $SAMPLE_ARG
echo "  Done. Results: outputs/models/expanded_summary.json"

# --- Step 5: Sanity baselines ---
echo ""
echo "=== Step 5: Running sanity baselines (dummy + shuffled) ==="
python "${PROJECT_DIR}/scripts/run_sanity_baselines.py" \
    --project-dir "$PROJECT_DIR" \
    --seeds $SEEDS \
    $SAMPLE_ARG
echo "  Done. Results: outputs/baselines/sanity_summary.json"

# --- Step 6: Adversarial attacks ---
echo ""
echo "=== Step 6: Running adversarial attack experiments ==="
echo "  Unconstrained + constrained noise attacks at epsilon=[0.01..0.5]"
python "${PROJECT_DIR}/src/adversarial_attacks.py" \
    --models RandomForest XGBoost \
    --seeds 42 \
    --attacks noise \
    ${SAMPLE_ARG:---sample-frac 0.1}
echo "  Done. Results: outputs/adversarial/"

# --- Step 7: Defense experiments ---
echo ""
echo "=== Step 7: Running defense experiments ==="
echo "  Adversarial training, feature squeezing, constraint-aware detection"
python "${PROJECT_DIR}/src/defenses.py" \
    --models RandomForest XGBoost \
    --seed 42 \
    ${SAMPLE_ARG:---sample-frac 0.1}
echo "  Done. Results: outputs/defense/"

# --- Step 8: Learning curves ---
echo ""
echo "=== Step 8: Running learning curves ==="
python "${PROJECT_DIR}/scripts/run_learning_curves.py" \
    --project-dir "$PROJECT_DIR" \
    ${SAMPLE_ARG:---sample-frac 0.1}
echo "  Done."

# --- Step 9: Generate report figures ---
echo ""
echo "=== Step 9: Generating report figures ==="
mkdir -p "${PROJECT_DIR}/figures"
python "${PROJECT_DIR}/scripts/make_report_figures.py"
echo "  Done. Figures: figures/"

# --- Step 10: Run tests ---
echo ""
echo "=== Step 10: Running test suite ==="
python -m pytest "${PROJECT_DIR}/tests/" -v --tb=short
echo "  Done."

# --- Summary ---
echo ""
echo "============================================================"
echo "REPRODUCTION COMPLETE"
echo "============================================================"
echo ""
echo "Key outputs:"
echo "  outputs/baselines/baseline_results.json    — Baseline model results"
echo "  outputs/baselines/sanity_summary.json      — Sanity check results"
echo "  outputs/models/expanded_summary.json       — Expanded model results"
echo "  outputs/adversarial/unconstrained_results.json — Attack results"
echo "  outputs/adversarial/constrained_results.json   — Constrained attack results"
echo "  outputs/defense/defense_comparison.json    — Defense comparison"
echo ""
echo "Figures:"
echo "  outputs/baselines/per_class_f1.png"
echo "  outputs/baselines/confusion_matrix_*.png"
echo "  outputs/adversarial/budget_curve_*.png"
echo "  outputs/defense/defense_recovery.png"
echo ""
echo "Report figures:"
echo "  figures/algorithm_comparison.png"
echo "  figures/learning_curves.png"
echo "  figures/defense_comparison.png"
echo "  figures/adversarial_budget_curves.png"
echo ""
echo "To run tests:  pytest tests/ -v"
echo "To view findings: cat FINDINGS.md"
