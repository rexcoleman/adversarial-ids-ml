#!/usr/bin/env python
"""Train expanded model set: SVM-RBF + LightGBM on CICIDS2017.

Extends the RF + XGBoost + MLP baselines from src/train_baselines.py with:
  - SVM-RBF: SVC(kernel='rbf', C=1.0, gamma='scale', probability=True)
    Subsampled to 50K training rows (SVM O(n^2) memory).
  - LightGBM: LGBMClassifier(n_estimators=200, max_depth=10)
    Graceful skip if lightgbm not installed.

Evaluation: Macro-F1 (matching existing baseline metric).
Seeds: [42, 123, 456, 789, 1024] (per EXPERIMENT_CONTRACT)

Outputs:
  outputs/models/expanded_seed{seed}.json
  outputs/models/expanded_summary.json

Usage:
    python scripts/train_expanded_models.py
    python scripts/train_expanded_models.py --seeds 42 --sample-frac 0.1
    python scripts/train_expanded_models.py --project-dir ~/adversarial-ids-ml
"""

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
)
from sklearn.svm import SVC


DEFAULT_SEEDS = [42, 123, 456, 789, 1024]
SVM_SUBSAMPLE = 50_000


def get_expanded_models(seed):
    """Return expanded model configs.

    SVM-RBF always included. LightGBM included if importable.
    """
    models = {
        "SVM-RBF": SVC(
            kernel="rbf",
            C=1.0,
            gamma="scale",
            probability=True,
            random_state=seed,
        ),
    }

    try:
        from lightgbm import LGBMClassifier
        models["LightGBM"] = LGBMClassifier(
            n_estimators=200,
            max_depth=10,
            random_state=seed,
            n_jobs=1,
            verbose=-1,
        )
    except ImportError:
        print("  [WARN] lightgbm not installed — skipping LightGBM.")

    return models


def subsample_for_svm(X_train, y_train, max_n, seed):
    """Subsample training data for SVM if too large."""
    if len(X_train) <= max_n:
        return X_train, y_train
    rng = np.random.RandomState(seed)
    idx = rng.choice(len(X_train), size=max_n, replace=False)
    idx.sort()
    return X_train[idx], y_train[idx]


def train_and_evaluate(model, model_name, X_train, y_train, X_val, y_val,
                       X_test, y_test, label_names, seed):
    """Train model and return evaluation metrics."""
    print(f"\n  Training {model_name} (seed={seed})...")

    if hasattr(model, "random_state"):
        model.random_state = seed

    # Subsample for SVM
    X_tr, y_tr = X_train, y_train
    if "SVM" in model_name:
        X_tr, y_tr = subsample_for_svm(X_train, y_train, SVM_SUBSAMPLE, seed)
        if len(X_tr) < len(X_train):
            print(f"    Subsampled {len(X_train):,} → {len(X_tr):,} for SVM")

    start = time.time()
    model.fit(X_tr, y_tr)
    train_time = time.time() - start

    # Predictions
    y_val_pred = model.predict(X_val)
    y_test_pred = model.predict(X_test)

    # Metrics
    val_f1 = f1_score(y_val, y_val_pred, average="macro", zero_division=0)
    test_f1 = f1_score(y_test, y_test_pred, average="macro", zero_division=0)
    test_acc = accuracy_score(y_test, y_test_pred)

    # Per-class report
    present_classes = sorted(set(y_test) | set(y_test_pred))
    present_names = [label_names[i] for i in present_classes if i < len(label_names)]
    report = classification_report(
        y_test, y_test_pred, labels=present_classes,
        target_names=present_names,
        output_dict=True, zero_division=0,
    )

    result = {
        "model": model_name,
        "seed": seed,
        "train_time_seconds": round(train_time, 2),
        "val_macro_f1": round(float(val_f1), 4),
        "test_macro_f1": round(float(test_f1), 4),
        "test_accuracy": round(float(test_acc), 4),
        "per_class_f1": {
            name: round(float(report[name]["f1-score"]), 4)
            for name in present_names if name in report
        },
        "n_train": len(X_tr),
        "n_val": len(X_val),
        "n_test": len(X_test),
    }

    print(f"    Val F1={val_f1:.4f}, Test F1={test_f1:.4f}, "
          f"Acc={test_acc:.4f}, Time={train_time:.1f}s")

    return result


def run_expanded_models(project_dir, seeds, sample_frac):
    """Run expanded model experiments."""
    proj = Path(project_dir).resolve()
    sys.path.insert(0, str(proj))
    from src.preprocessing import run_preprocessing_pipeline, set_seed

    output_dir = proj / "outputs" / "models"
    output_dir.mkdir(parents=True, exist_ok=True)

    all_results = []

    for seed in seeds:
        print(f"\n{'='*60}")
        print(f"Seed {seed}")
        print(f"{'='*60}")

        set_seed(seed)

        print("Running preprocessing pipeline...")
        data = run_preprocessing_pipeline(seed=seed, sample_frac=sample_frac)

        X_train = data["X_train"]
        X_val = data["X_val"]
        X_test = data["X_test"]
        y_train = data["y_train"]
        y_val = data["y_val"]
        y_test = data["y_test"]
        label_names = data["label_names"]

        models = get_expanded_models(seed)
        seed_results = {"seed": seed, "results": []}

        for model_name, model in models.items():
            result = train_and_evaluate(
                model, model_name,
                X_train, y_train, X_val, y_val, X_test, y_test,
                label_names, seed,
            )
            seed_results["results"].append(result)
            all_results.append(result)

        # Save per-seed
        seed_path = output_dir / f"expanded_seed{seed}.json"
        with open(seed_path, "w") as f:
            json.dump(seed_results, f, indent=2, default=str)
        print(f"\n  Saved: {seed_path}")

    # Summary
    summary = {
        "experiment": "expanded_models",
        "seeds": seeds,
        "sample_fraction": sample_frac,
        "models": list(set(r["model"] for r in all_results)),
        "results": all_results,
    }

    for model_name in summary["models"]:
        model_results = [r for r in all_results if r["model"] == model_name]
        f1s = [r["test_macro_f1"] for r in model_results]
        summary[f"{model_name}_macro_f1_mean"] = round(float(np.mean(f1s)), 4)
        summary[f"{model_name}_macro_f1_std"] = round(float(np.std(f1s)), 4)

    summary_path = output_dir / "expanded_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\nSummary saved: {summary_path}")

    # Print summary
    print(f"\n{'='*60}")
    print("EXPANDED MODELS SUMMARY")
    print(f"{'='*60}")
    for model_name in sorted(summary["models"]):
        mean = summary[f"{model_name}_macro_f1_mean"]
        std = summary[f"{model_name}_macro_f1_std"]
        print(f"  {model_name:15s}: macro-F1 = {mean:.4f} +/- {std:.4f}")

    return summary


def main():
    parser = argparse.ArgumentParser(description="Train expanded models (SVM-RBF + LightGBM)")
    parser.add_argument("--project-dir", default=".", help="Project root directory")
    parser.add_argument("--seeds", type=int, nargs="+", default=DEFAULT_SEEDS,
                        help="Random seeds (default: 42 123 456 789 1024)")
    parser.add_argument("--sample-frac", type=float, default=None,
                        help="Data sampling fraction for smoke testing")
    args = parser.parse_args()
    run_expanded_models(args.project_dir, args.seeds, args.sample_frac)


if __name__ == "__main__":
    main()
