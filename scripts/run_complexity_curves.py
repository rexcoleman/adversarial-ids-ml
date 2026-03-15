#!/usr/bin/env python
"""Generate model complexity curves for RF and XGBoost.

Varies a key hyperparameter while holding others fixed to show
the bias-variance tradeoff:
  - RF: n_estimators [10, 50, 100, 200, 500]
  - XGBoost: max_depth [2, 3, 5, 7, 10]

Seeds: [42, 123, 456, 789, 1024] (per EXPERIMENT_CONTRACT)

Outputs:
  outputs/diagnostics/complexity_curves_seed{seed}.json
  outputs/diagnostics/complexity_curves_summary.json

Usage:
    python scripts/run_complexity_curves.py
    python scripts/run_complexity_curves.py --seeds 42 --sample-frac 0.1
    python scripts/run_complexity_curves.py --project-dir ~/adversarial-ids-ml
"""

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score
import xgboost as xgb


RF_N_ESTIMATORS = [10, 50, 100, 200, 500]
XGB_MAX_DEPTHS = [2, 3, 5, 7, 10]
DEFAULT_SEEDS = [42, 123, 456, 789, 1024]


def run_complexity_curves(project_dir, seeds, sample_frac):
    """Run complexity curve experiments."""
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
        X_train = data["X_train"]
        y_train = data["y_train"]
        X_val = data["X_val"]
        y_val = data["y_val"]
        X_test = data["X_test"]
        y_test = data["y_test"]

        seed_results = {"seed": seed, "curves": {}}

        # --- RF: vary n_estimators ---
        print(f"\n  RandomForest (n_estimators):")
        rf_train, rf_val, rf_test = [], [], []
        for n_est in RF_N_ESTIMATORS:
            model = RandomForestClassifier(
                n_estimators=n_est, max_depth=20, min_samples_leaf=5,
                n_jobs=1, random_state=seed,
            )
            start = time.time()
            model.fit(X_train, y_train)
            elapsed = time.time() - start

            train_f1 = f1_score(y_train, model.predict(X_train), average="macro", zero_division=0)
            val_f1 = f1_score(y_val, model.predict(X_val), average="macro", zero_division=0)
            test_f1 = f1_score(y_test, model.predict(X_test), average="macro", zero_division=0)

            rf_train.append(round(float(train_f1), 4))
            rf_val.append(round(float(val_f1), 4))
            rf_test.append(round(float(test_f1), 4))

            print(f"    n_estimators={n_est:<4d}  "
                  f"train={train_f1:.4f}  val={val_f1:.4f}  "
                  f"test={test_f1:.4f}  ({elapsed:.1f}s)")

        seed_results["curves"]["RandomForest"] = {
            "param_name": "n_estimators",
            "param_values": RF_N_ESTIMATORS,
            "train_f1": rf_train,
            "val_f1": rf_val,
            "test_f1": rf_test,
        }

        # --- XGBoost: vary max_depth ---
        print(f"\n  XGBoost (max_depth):")
        xgb_train, xgb_val, xgb_test = [], [], []
        for depth in XGB_MAX_DEPTHS:
            model = xgb.XGBClassifier(
                n_estimators=100, max_depth=depth, learning_rate=0.1,
                eval_metric="mlogloss", nthread=1, random_state=seed,
                use_label_encoder=False,
            )
            start = time.time()
            model.fit(X_train, y_train)
            elapsed = time.time() - start

            train_f1 = f1_score(y_train, model.predict(X_train), average="macro", zero_division=0)
            val_f1 = f1_score(y_val, model.predict(X_val), average="macro", zero_division=0)
            test_f1 = f1_score(y_test, model.predict(X_test), average="macro", zero_division=0)

            xgb_train.append(round(float(train_f1), 4))
            xgb_val.append(round(float(val_f1), 4))
            xgb_test.append(round(float(test_f1), 4))

            print(f"    max_depth={depth:<3d}  "
                  f"train={train_f1:.4f}  val={val_f1:.4f}  "
                  f"test={test_f1:.4f}  ({elapsed:.1f}s)")

        seed_results["curves"]["XGBoost"] = {
            "param_name": "max_depth",
            "param_values": XGB_MAX_DEPTHS,
            "train_f1": xgb_train,
            "val_f1": xgb_val,
            "test_f1": xgb_test,
        }

        # Save per-seed
        seed_path = output_dir / f"complexity_curves_seed{seed}.json"
        with open(seed_path, "w") as f:
            json.dump(seed_results, f, indent=2)
        print(f"\n  Saved: {seed_path}")
        all_results.append(seed_results)

    # Summary with mean/std across seeds
    summary = {
        "experiment": "complexity_curves",
        "seeds": seeds,
        "models": {
            "RandomForest": {"param_name": "n_estimators", "param_values": RF_N_ESTIMATORS},
            "XGBoost": {"param_name": "max_depth", "param_values": XGB_MAX_DEPTHS},
        },
        "per_seed": all_results,
    }

    for model_name in ["RandomForest", "XGBoost"]:
        for metric in ["train_f1", "val_f1", "test_f1"]:
            n_points = len(all_results[0]["curves"][model_name][metric])
            means, stds = [], []
            for i in range(n_points):
                vals = [r["curves"][model_name][metric][i] for r in all_results]
                means.append(round(float(np.mean(vals)), 4))
                stds.append(round(float(np.std(vals)), 4))
            summary[f"{model_name}_{metric}_mean"] = means
            summary[f"{model_name}_{metric}_std"] = stds

    summary_path = output_dir / "complexity_curves_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSummary saved: {summary_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate complexity curves")
    parser.add_argument("--project-dir", default=".", help="Project root directory")
    parser.add_argument("--seeds", type=int, nargs="+", default=DEFAULT_SEEDS,
                        help="Random seeds (default: 42 123 456 789 1024)")
    parser.add_argument("--sample-frac", type=float, default=None,
                        help="Data sampling fraction for smoke testing")
    args = parser.parse_args()
    run_complexity_curves(args.project_dir, args.seeds, args.sample_frac)


if __name__ == "__main__":
    main()
