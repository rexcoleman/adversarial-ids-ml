#!/usr/bin/env python
"""Generate learning curves for baseline classifiers.

Trains RF, XGBoost, and MLP on increasing fractions of training data
across multiple seeds. Measures macro-F1 at each fraction to diagnose
overfitting vs underfitting.

Seeds: [42, 123, 456, 789, 1024] (per EXPERIMENT_CONTRACT)
Fractions: [0.1, 0.25, 0.5, 0.75, 1.0]
Models: RandomForest, XGBoost, MLP

Outputs:
  outputs/diagnostics/learning_curves_seed{seed}.json
  outputs/diagnostics/learning_curves_summary.json

Usage:
    python scripts/run_learning_curves.py
    python scripts/run_learning_curves.py --seeds 42 123 --sample-frac 0.1
    python scripts/run_learning_curves.py --project-dir ~/adversarial-ids-ml
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score
from sklearn.neural_network import MLPClassifier
import xgboost as xgb


def get_models(seed):
    """Return model configs with given seed."""
    return {
        "RandomForest": RandomForestClassifier(
            n_estimators=100, max_depth=20, min_samples_leaf=5,
            n_jobs=1, random_state=seed,
        ),
        "XGBoost": xgb.XGBClassifier(
            n_estimators=100, max_depth=8, learning_rate=0.1,
            eval_metric="mlogloss", nthread=1, random_state=seed,
            use_label_encoder=False,
        ),
        "MLP": MLPClassifier(
            hidden_layer_sizes=(128, 64), max_iter=50,
            early_stopping=True, validation_fraction=0.1,
            random_state=seed,
        ),
    }


FRACTIONS = [0.1, 0.25, 0.5, 0.75, 1.0]
DEFAULT_SEEDS = [42, 123, 456, 789, 1024]


def run_learning_curves(project_dir, seeds, sample_frac):
    """Run learning curve experiments."""
    proj = Path(project_dir).resolve()
    sys.path.insert(0, str(proj))
    from src.preprocessing import run_preprocessing_pipeline, set_seed

    output_dir = proj / "outputs" / "diagnostics"
    output_dir.mkdir(parents=True, exist_ok=True)

    all_results = []

    for seed in seeds:
        print(f"\n{'='*60}")
        print(f"Seed {seed}")
        print(f"{'='*60}")

        set_seed(seed)

        print("Loading data...")
        data = run_preprocessing_pipeline(seed=seed, sample_frac=sample_frac)
        X_train_full = data["X_train"]
        y_train_full = data["y_train"]
        X_val = data["X_val"]
        y_val = data["y_val"]
        X_test = data["X_test"]
        y_test = data["y_test"]

        seed_results = {"seed": seed, "fractions": FRACTIONS, "curves": {}}

        for model_name, model in get_models(seed).items():
            print(f"\n  {model_name}:")
            train_scores = []
            val_scores = []
            test_scores = []
            n_samples_list = []

            for frac in FRACTIONS:
                n = int(len(X_train_full) * frac)
                X_sub = X_train_full[:n]
                y_sub = y_train_full[:n]

                # Clone model with same params
                from sklearn.base import clone
                m = clone(model)
                m.random_state = seed

                start = time.time()
                m.fit(X_sub, y_sub)
                elapsed = time.time() - start

                train_f1 = f1_score(y_sub, m.predict(X_sub), average="macro", zero_division=0)
                val_f1 = f1_score(y_val, m.predict(X_val), average="macro", zero_division=0)
                test_f1 = f1_score(y_test, m.predict(X_test), average="macro", zero_division=0)

                train_scores.append(round(float(train_f1), 4))
                val_scores.append(round(float(val_f1), 4))
                test_scores.append(round(float(test_f1), 4))
                n_samples_list.append(n)

                print(f"    frac={frac:.2f} n={n:>7,}  "
                      f"train={train_f1:.4f}  val={val_f1:.4f}  "
                      f"test={test_f1:.4f}  ({elapsed:.1f}s)")

            seed_results["curves"][model_name] = {
                "train_f1": train_scores,
                "val_f1": val_scores,
                "test_f1": test_scores,
                "n_samples": n_samples_list,
            }

        # Save per-seed results
        seed_path = output_dir / f"learning_curves_seed{seed}.json"
        with open(seed_path, "w") as f:
            json.dump(seed_results, f, indent=2)
        print(f"\n  Saved: {seed_path}")
        all_results.append(seed_results)

    # Save summary across seeds
    summary = {
        "experiment": "learning_curves",
        "seeds": seeds,
        "fractions": FRACTIONS,
        "models": list(get_models(42).keys()),
        "per_seed": all_results,
    }

    # Aggregate mean/std across seeds per model per fraction
    for model_name in summary["models"]:
        for metric in ["train_f1", "val_f1", "test_f1"]:
            means = []
            stds = []
            for i, frac in enumerate(FRACTIONS):
                vals = [r["curves"][model_name][metric][i] for r in all_results]
                means.append(round(float(np.mean(vals)), 4))
                stds.append(round(float(np.std(vals)), 4))
            summary[f"{model_name}_{metric}_mean"] = means
            summary[f"{model_name}_{metric}_std"] = stds

    summary_path = output_dir / "learning_curves_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSummary saved: {summary_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate learning curves")
    parser.add_argument("--project-dir", default=".", help="Project root directory")
    parser.add_argument("--seeds", type=int, nargs="+", default=DEFAULT_SEEDS,
                        help="Random seeds (default: 42 123 456 789 1024)")
    parser.add_argument("--sample-frac", type=float, default=None,
                        help="Data sampling fraction for smoke testing")
    args = parser.parse_args()
    run_learning_curves(args.project_dir, args.seeds, args.sample_frac)


if __name__ == "__main__":
    main()
