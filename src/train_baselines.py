"""
Phase 2a: Train baseline classifiers on clean CICIDS2017 data.

Models: Random Forest, XGBoost, MLP (scikit-learn)
Evaluation: Macro-F1, per-class F1, accuracy, confusion matrix

Generates:
  outputs/baselines/baseline_results.json
  outputs/baselines/confusion_matrix_{model}.png
  outputs/baselines/per_class_f1.png
  models/{model}_seed{seed}.pkl

Governed by: EXPERIMENT_CONTRACT, HYPOTHESIS_CONTRACT H-1 baseline
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.neural_network import MLPClassifier
import joblib
import xgboost as xgb

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.preprocessing import run_preprocessing_pipeline, set_seed

OUTPUT_DIR = Path("outputs/baselines")
MODEL_DIR = Path("models")


def get_models():
    """Return model configs. Deterministic, single-threaded per ENVIRONMENT_CONTRACT §8."""
    return {
        "RandomForest": RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            min_samples_leaf=5,
            n_jobs=1,  # ENVIRONMENT_CONTRACT: n_jobs=1
            random_state=42,  # overridden per seed
        ),
        "XGBoost": xgb.XGBClassifier(
            n_estimators=100,
            max_depth=8,
            learning_rate=0.1,
            eval_metric="mlogloss",
            nthread=1,
            random_state=42,
            use_label_encoder=False,
        ),
        "MLP": MLPClassifier(
            hidden_layer_sizes=(128, 64),
            max_iter=50,
            early_stopping=True,
            validation_fraction=0.1,
            random_state=42,
        ),
    }


def train_and_evaluate(model, model_name, X_train, y_train, X_val, y_val,
                       X_test, y_test, label_names, seed):
    """Train model and return evaluation metrics."""
    print(f"\n  Training {model_name} (seed={seed})...")

    # Set seed on model
    if hasattr(model, "random_state"):
        model.random_state = seed

    start = time.time()
    model.fit(X_train, y_train)
    train_time = time.time() - start

    # Predictions
    y_val_pred = model.predict(X_val)
    y_test_pred = model.predict(X_test)

    # Metrics
    val_f1 = f1_score(y_val, y_val_pred, average="macro", zero_division=0)
    test_f1 = f1_score(y_test, y_test_pred, average="macro", zero_division=0)
    test_acc = accuracy_score(y_test, y_test_pred)

    # Filter label_names to only classes present in data
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
        "n_train": len(X_train),
        "n_val": len(X_val),
        "n_test": len(X_test),
    }

    print(f"    Val F1={val_f1:.4f}, Test F1={test_f1:.4f}, "
          f"Acc={test_acc:.4f}, Time={train_time:.1f}s")

    return result, model, y_test_pred


def plot_confusion_matrix(y_true, y_pred, label_names, model_name, seed):
    """Plot and save confusion matrix."""
    cm = confusion_matrix(y_true, y_pred)
    # Normalize for readability
    cm_norm = cm.astype("float") / cm.sum(axis=1, keepdims=True)

    fig, ax = plt.subplots(figsize=(14, 12))
    sns.heatmap(cm_norm, annot=True, fmt=".2f", cmap="Blues",
                xticklabels=label_names, yticklabels=label_names, ax=ax)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title(f"Confusion Matrix: {model_name} (seed={seed})")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / f"confusion_matrix_{model_name}_seed{seed}.png",
                dpi=150, bbox_inches="tight")
    plt.close()


def plot_per_class_f1(results, label_names):
    """Plot per-class F1 comparison across models."""
    fig, ax = plt.subplots(figsize=(14, 8))

    models = list(set(r["model"] for r in results))
    x = np.arange(len(label_names))
    width = 0.8 / len(models)

    for i, model_name in enumerate(sorted(models)):
        # Average across seeds
        model_results = [r for r in results if r["model"] == model_name]
        avg_f1 = {}
        for name in label_names:
            vals = [r["per_class_f1"].get(name, 0) for r in model_results]
            avg_f1[name] = np.mean(vals)

        f1_vals = [avg_f1.get(name, 0) for name in label_names]
        ax.bar(x + i * width, f1_vals, width, label=model_name)

    ax.set_xlabel("Attack Class")
    ax.set_ylabel("F1 Score")
    ax.set_title("Per-Class F1 by Model (averaged across seeds)")
    ax.set_xticks(x + width * (len(models) - 1) / 2)
    ax.set_xticklabels(label_names, rotation=45, ha="right")
    ax.legend()
    ax.set_ylim(0, 1.05)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "per_class_f1.png", dpi=150, bbox_inches="tight")
    plt.close()


def run_baselines(seeds=None, sample_frac=1.0):
    """Run all baseline experiments."""
    if seeds is None:
        seeds = [42]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

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

        models = get_models()

        for model_name, model in models.items():
            result, trained_model, y_pred = train_and_evaluate(
                model, model_name,
                X_train, y_train, X_val, y_val, X_test, y_test,
                label_names, seed,
            )
            all_results.append(result)

            # Save model
            model_path = MODEL_DIR / f"{model_name}_seed{seed}.pkl"
            joblib.dump(trained_model, model_path)

            # Confusion matrix (first seed only to save disk)
            if seed == seeds[0]:
                plot_confusion_matrix(y_test, y_pred, label_names,
                                      model_name, seed)

    # Per-class F1 comparison
    label_names_for_plot = all_results[0]["per_class_f1"].keys()
    plot_per_class_f1(all_results, list(label_names_for_plot))

    # Summary
    summary = {
        "experiment": "baseline_classifiers",
        "seeds": seeds,
        "sample_fraction": sample_frac,
        "models": list(set(r["model"] for r in all_results)),
        "results": all_results,
    }

    # Aggregate stats per model
    for model_name in summary["models"]:
        model_results = [r for r in all_results if r["model"] == model_name]
        f1s = [r["test_macro_f1"] for r in model_results]
        summary[f"{model_name}_macro_f1_mean"] = round(float(np.mean(f1s)), 4)
        summary[f"{model_name}_macro_f1_std"] = round(float(np.std(f1s)), 4)

    results_path = OUTPUT_DIR / "baseline_results.json"
    with open(results_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\nResults saved to {results_path}")

    # Print summary
    print(f"\n{'='*60}")
    print("BASELINE SUMMARY")
    print(f"{'='*60}")
    for model_name in sorted(summary["models"]):
        mean = summary[f"{model_name}_macro_f1_mean"]
        std = summary[f"{model_name}_macro_f1_std"]
        print(f"  {model_name:15s}: macro-F1 = {mean:.4f} ± {std:.4f}")

    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train baseline classifiers")
    parser.add_argument("--seeds", type=int, nargs="+", default=[42],
                        help="Random seeds (default: [42])")
    parser.add_argument("--sample-frac", type=float, default=1.0,
                        help="Fraction of data to use (default: 1.0)")
    args = parser.parse_args()
    run_baselines(seeds=args.seeds, sample_frac=args.sample_frac)
