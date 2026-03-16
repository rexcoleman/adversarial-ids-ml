#!/usr/bin/env python
"""Generate report figures from JSON result files.

Reads from outputs/ and saves PNG figures to figures/.
No training or data loading — purely visualization from pre-computed results.

Usage:
    python scripts/make_report_figures.py
    python scripts/make_report_figures.py --output-dir figures/
"""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


PROJECT_ROOT = Path(__file__).parent.parent
OUTPUTS = PROJECT_ROOT / "outputs"


def load_json(path):
    """Load JSON file, exit with message if missing."""
    if not path.exists():
        print(f"WARNING: {path} not found, skipping dependent figure.")
        return None
    with open(path) as f:
        return json.load(f)


def fig_algorithm_comparison(output_dir):
    """Bar chart: macro-F1 comparison across all 5 algorithms (5 seeds each)."""
    baseline = load_json(OUTPUTS / "baselines" / "baseline_results.json")
    expanded = load_json(OUTPUTS / "models" / "expanded_summary.json")
    if baseline is None:
        return

    models = []
    means = []
    stds = []

    # Baseline models
    for model in ["XGBoost", "RandomForest", "MLP"]:
        models.append(model)
        means.append(baseline[f"{model}_macro_f1_mean"])
        stds.append(baseline[f"{model}_macro_f1_std"])

    # Expanded models
    if expanded is not None:
        for model in ["SVM-RBF", "LightGBM"]:
            key_mean = f"{model}_macro_f1_mean"
            key_std = f"{model}_macro_f1_std"
            if key_mean in expanded:
                models.append(model)
                means.append(expanded[key_mean])
                stds.append(expanded[key_std])

    # Sort by mean descending
    order = sorted(range(len(means)), key=lambda i: means[i], reverse=True)
    models = [models[i] for i in order]
    means = [means[i] for i in order]
    stds = [stds[i] for i in order]

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["#2ecc71", "#3498db", "#e74c3c", "#9b59b6", "#f39c12"]
    bars = ax.bar(models, means, yerr=stds, capsize=5, color=colors[:len(models)],
                  edgecolor="black", linewidth=0.5, alpha=0.85)

    # Add value labels
    for bar, m, s in zip(bars, means, stds):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + s + 0.01,
                f"{m:.3f}", ha="center", va="bottom", fontsize=11, fontweight="bold")

    ax.set_ylabel("Test Macro-F1", fontsize=13)
    ax.set_title("Algorithm Comparison on CICIDS2017 (10% sample, multi-seed)", fontsize=14)
    ax.set_ylim(0, 1.05)
    ax.axhline(y=0.5, color="gray", linestyle="--", alpha=0.5, label="Random baseline")
    ax.legend(fontsize=10)
    ax.grid(axis="y", alpha=0.3)

    # Add seed count annotation
    n_baseline_seeds = len(baseline.get("seeds", []))
    n_expanded_seeds = len(expanded.get("seeds", [])) if expanded else 0
    ax.annotate(
        f"Baselines: {n_baseline_seeds} seeds | Expanded: {n_expanded_seeds} seeds",
        xy=(0.5, 0.02), xycoords="axes fraction", ha="center", fontsize=9,
        color="gray"
    )

    plt.tight_layout()
    path = output_dir / "algorithm_comparison.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def fig_learning_curves(output_dir):
    """Learning curves: val F1 vs training fraction for RF, XGBoost, MLP."""
    data = load_json(OUTPUTS / "diagnostics" / "learning_curves_seed42.json")
    if data is None:
        return

    fractions = data["fractions"]
    curves = data["curves"]

    fig, ax = plt.subplots(figsize=(10, 6))
    markers = {"XGBoost": "o", "RandomForest": "s", "MLP": "^"}
    colors = {"XGBoost": "#2ecc71", "RandomForest": "#3498db", "MLP": "#e74c3c"}

    for model in ["XGBoost", "RandomForest", "MLP"]:
        if model not in curves:
            continue
        c = curves[model]
        ax.plot(fractions, c["val_f1"], marker=markers.get(model, "o"),
                label=f"{model} (val)", color=colors.get(model, "gray"),
                linewidth=2, markersize=8)
        ax.plot(fractions, c["train_f1"], marker=markers.get(model, "o"),
                label=f"{model} (train)", color=colors.get(model, "gray"),
                linewidth=1, linestyle="--", alpha=0.5, markersize=5)

    ax.set_xlabel("Training Fraction", fontsize=13)
    ax.set_ylabel("Macro-F1", fontsize=13)
    ax.set_title("Learning Curves — CICIDS2017 (seed 42, 10% sample)", fontsize=14)
    ax.set_xticks(fractions)
    ax.set_xticklabels([f"{f:.0%}" for f in fractions])
    ax.set_ylim(0.5, 1.05)
    ax.legend(fontsize=9, ncol=2)
    ax.grid(alpha=0.3)

    # Add n_samples as secondary labels
    n_samples = curves["XGBoost"]["n_samples"]
    ax2 = ax.twiny()
    ax2.set_xlim(ax.get_xlim())
    ax2.set_xticks(fractions)
    ax2.set_xticklabels([f"n={n:,}" for n in n_samples], fontsize=8, color="gray")
    ax2.set_xlabel("Training Samples", fontsize=10, color="gray")

    plt.tight_layout()
    path = output_dir / "learning_curves.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def fig_defense_comparison(output_dir):
    """Grouped bar chart: defense recovery ratios for RF and XGBoost."""
    data = load_json(OUTPUTS / "defense" / "defense_comparison.json")
    if data is None:
        return

    defenses_order = ["none", "feature_squeezing", "adversarial_training", "constraint_aware_detection"]
    defense_labels = {
        "none": "No Defense",
        "feature_squeezing": "Feature\nSqueezing",
        "adversarial_training": "Adversarial\nTraining",
        "constraint_aware_detection": "Constraint-Aware\nDetection",
    }

    by_model = defaultdict(dict)
    for r in data:
        by_model[r["model"]][r["defense"]] = r["recovery_ratio"]

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(defenses_order))
    width = 0.35

    models_to_plot = ["XGBoost", "RandomForest"]
    colors = ["#2ecc71", "#3498db"]

    for i, model in enumerate(models_to_plot):
        if model not in by_model:
            continue
        vals = [by_model[model].get(d, 0) for d in defenses_order]
        bars = ax.bar(x + i * width, vals, width, label=model, color=colors[i],
                      edgecolor="black", linewidth=0.5, alpha=0.85)
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                    f"{v:.0%}", ha="center", va="bottom", fontsize=10)

    ax.set_ylabel("Recovery Ratio", fontsize=13)
    ax.set_title("Defense Effectiveness Against Noise Perturbation (seed 42)", fontsize=14)
    ax.set_xticks(x + width / 2)
    ax.set_xticklabels([defense_labels[d] for d in defenses_order], fontsize=10)
    ax.set_ylim(-0.1, 1.25)
    ax.axhline(y=0, color="gray", linewidth=0.5)
    ax.legend(fontsize=11)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    path = output_dir / "defense_comparison.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {path}")


def fig_adversarial_budget_curves(output_dir):
    """Line plot: F1 drop vs epsilon for constrained vs unconstrained attacks."""
    constrained = load_json(OUTPUTS / "adversarial" / "constrained_results.json")
    unconstrained = load_json(OUTPUTS / "adversarial" / "unconstrained_results.json")
    if constrained is None or unconstrained is None:
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)

    for idx, model in enumerate(["XGBoost", "RandomForest"]):
        ax = axes[idx]

        # Constrained
        c_eps = [r["epsilon"] for r in constrained if r["model"] == model]
        c_f1 = [r["adv_macro_f1"] for r in constrained if r["model"] == model]

        # Unconstrained
        u_eps = [r["epsilon"] for r in unconstrained if r["model"] == model]
        u_f1 = [r["adv_macro_f1"] for r in unconstrained if r["model"] == model]

        ax.plot(c_eps, c_f1, "o-", label="Constrained (controllable only)",
                color="#2ecc71", linewidth=2, markersize=7)
        ax.plot(u_eps, u_f1, "s--", label="Unconstrained (all features)",
                color="#e74c3c", linewidth=2, markersize=7)

        # Clean baseline
        clean_f1 = constrained[0]["clean_macro_f1"] if constrained else 0
        ax.axhline(y=clean_f1, color="gray", linestyle=":", alpha=0.6,
                    label=f"Clean F1 ({clean_f1:.3f})")

        ax.set_xlabel("Perturbation Budget (epsilon)", fontsize=12)
        if idx == 0:
            ax.set_ylabel("Adversarial Macro-F1", fontsize=12)
        ax.set_title(f"{model}", fontsize=13)
        ax.legend(fontsize=9)
        ax.grid(alpha=0.3)
        ax.set_ylim(0, 1.05)

    fig.suptitle("Attack Budget Curves: Constrained vs Unconstrained Noise (seed 42)",
                 fontsize=14, y=1.02)
    plt.tight_layout()
    path = output_dir / "adversarial_budget_curves.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


def fig_per_class_heatmap(output_dir):
    """Heatmap of per-class F1 across models (best seed per model)."""
    baseline = load_json(OUTPUTS / "baselines" / "baseline_results.json")
    expanded = load_json(OUTPUTS / "models" / "expanded_summary.json")
    if baseline is None:
        return

    # Pick best seed per model
    best = {}
    all_results = baseline["results"]
    if expanded is not None:
        all_results = all_results + expanded["results"]

    for r in all_results:
        model = r["model"]
        if model not in best or r["test_macro_f1"] > best[model]["test_macro_f1"]:
            best[model] = r

    model_order = ["XGBoost", "RandomForest", "MLP", "SVM-RBF", "LightGBM"]
    model_order = [m for m in model_order if m in best]

    # Get all classes from first model
    classes = list(best[model_order[0]]["per_class_f1"].keys())

    matrix = []
    for model in model_order:
        row = [best[model]["per_class_f1"].get(c, 0.0) for c in classes]
        matrix.append(row)

    matrix = np.array(matrix)

    fig, ax = plt.subplots(figsize=(14, 5))
    im = ax.imshow(matrix, cmap="RdYlGn", aspect="auto", vmin=0, vmax=1)

    ax.set_xticks(range(len(classes)))
    ax.set_xticklabels(classes, rotation=45, ha="right", fontsize=9)
    ax.set_yticks(range(len(model_order)))
    ax.set_yticklabels(model_order, fontsize=11)

    # Add text annotations
    for i in range(len(model_order)):
        for j in range(len(classes)):
            val = matrix[i, j]
            color = "white" if val < 0.4 else "black"
            ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                    fontsize=7, color=color)

    plt.colorbar(im, ax=ax, label="F1 Score", shrink=0.8)
    ax.set_title("Per-Class F1 Scores (Best Seed per Model)", fontsize=14)
    plt.tight_layout()
    path = output_dir / "per_class_heatmap.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


def main():
    parser = argparse.ArgumentParser(description="Generate report figures from JSON results")
    parser.add_argument("--output-dir", type=str, default="figures",
                        help="Output directory for PNG figures")
    args = parser.parse_args()

    output_dir = PROJECT_ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Generating report figures...")
    print(f"  Source: {OUTPUTS}")
    print(f"  Destination: {output_dir}")
    print()

    fig_algorithm_comparison(output_dir)
    fig_learning_curves(output_dir)
    fig_defense_comparison(output_dir)
    fig_adversarial_budget_curves(output_dir)
    fig_per_class_heatmap(output_dir)

    print()
    print(f"Done. {len(list(output_dir.glob('*.png')))} figures in {output_dir}/")


if __name__ == "__main__":
    main()
