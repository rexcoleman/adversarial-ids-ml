"""
EDA for CICIDS2017 — Phase 1 artifact.

Generates:
  outputs/eda/class_distribution.png
  outputs/eda/feature_correlations.png
  outputs/eda/controllable_vs_observable.png
  outputs/eda/eda_summary.json

Governed by: DATA_CONTRACT §6, HYPOTHESIS_CONTRACT §4 (EDA evidence)
"""

import json
import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Project imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.preprocessing import (
    ATTACKER_CONTROLLABLE_FEATURES,
    DEFENDER_OBSERVABLE_ONLY,
    load_raw_data,
    clean_data,
)

OUTPUT_DIR = Path("outputs/eda")
SEED = 42


def class_distribution(df: pd.DataFrame) -> dict:
    """Analyze and plot class distribution."""
    counts = df["Label"].value_counts()
    total = len(df)

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Absolute counts (log scale)
    counts.plot(kind="barh", ax=axes[0], color="steelblue")
    axes[0].set_xlabel("Count (log scale)")
    axes[0].set_xscale("log")
    axes[0].set_title("Class Distribution (absolute)")

    # Percentage
    pcts = (counts / total * 100).round(2)
    pcts.plot(kind="barh", ax=axes[1], color="coral")
    axes[1].set_xlabel("Percentage (%)")
    axes[1].set_title("Class Distribution (relative)")

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "class_distribution.png", dpi=150, bbox_inches="tight")
    plt.close()

    return {
        "total_samples": int(total),
        "n_classes": int(len(counts)),
        "class_counts": counts.to_dict(),
        "class_percentages": pcts.to_dict(),
        "majority_class": counts.index[0],
        "majority_pct": float(pcts.iloc[0]),
        "imbalance_ratio": float(counts.iloc[0] / counts.iloc[-1]),
    }


def feature_analysis(df: pd.DataFrame) -> dict:
    """Analyze feature statistics and correlations."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    # Basic stats
    stats = {
        "n_features": len(numeric_cols),
        "n_numeric": len(numeric_cols),
        "features_with_zero_variance": [],
        "features_with_high_correlation": [],
    }

    # Zero variance features
    variances = df[numeric_cols].var()
    zero_var = variances[variances == 0].index.tolist()
    stats["features_with_zero_variance"] = zero_var

    # Correlation analysis (sample for speed)
    sample = df[numeric_cols].sample(n=min(50000, len(df)), random_state=SEED)
    corr = sample.corr()

    # Find highly correlated pairs (|r| > 0.95)
    high_corr = []
    for i in range(len(corr.columns)):
        for j in range(i + 1, len(corr.columns)):
            r = corr.iloc[i, j]
            if abs(r) > 0.95:
                high_corr.append({
                    "feature_1": corr.columns[i],
                    "feature_2": corr.columns[j],
                    "correlation": round(float(r), 4),
                })
    stats["features_with_high_correlation"] = high_corr
    stats["n_highly_correlated_pairs"] = len(high_corr)

    # Plot top 20 feature correlations with Label (encoded)
    if "Label" in df.columns:
        label_encoded = df["Label"].astype("category").cat.codes
        feature_label_corr = sample[numeric_cols].corrwith(
            label_encoded.loc[sample.index]
        ).abs().sort_values(ascending=False).head(20)

        fig, ax = plt.subplots(figsize=(10, 8))
        feature_label_corr.plot(kind="barh", ax=ax, color="steelblue")
        ax.set_xlabel("|Correlation with Label|")
        ax.set_title("Top 20 Features Most Correlated with Attack Label")
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / "feature_correlations.png", dpi=150, bbox_inches="tight")
        plt.close()

        stats["top_features_by_label_correlation"] = {
            k: round(float(v), 4)
            for k, v in feature_label_corr.items()
        }

    return stats


def controllability_analysis(df: pd.DataFrame) -> dict:
    """Analyze attacker-controllable vs defender-observable features."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    controllable_present = [f for f in ATTACKER_CONTROLLABLE_FEATURES if f in numeric_cols]
    observable_present = [f for f in DEFENDER_OBSERVABLE_ONLY if f in numeric_cols]
    uncategorized = [f for f in numeric_cols
                     if f not in ATTACKER_CONTROLLABLE_FEATURES
                     and f not in DEFENDER_OBSERVABLE_ONLY]

    stats = {
        "controllable_features": len(controllable_present),
        "observable_features": len(observable_present),
        "uncategorized_features": len(uncategorized),
        "controllable_list": controllable_present,
        "observable_list": observable_present,
        "uncategorized_list": uncategorized,
    }

    # Compare feature importance between controllable and observable
    fig, ax = plt.subplots(figsize=(8, 5))
    categories = ["Attacker-\nControllable", "Defender-\nObservable Only", "Uncategorized"]
    counts = [len(controllable_present), len(observable_present), len(uncategorized)]
    colors = ["#e74c3c", "#2ecc71", "#95a5a6"]
    ax.bar(categories, counts, color=colors)
    ax.set_ylabel("Number of Features")
    ax.set_title("Feature Controllability Breakdown\n(Core differentiator: constrained adversarial attacks)")
    for i, v in enumerate(counts):
        ax.text(i, v + 0.5, str(v), ha="center", fontweight="bold")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "controllable_vs_observable.png", dpi=150, bbox_inches="tight")
    plt.close()

    return stats


def missing_and_infinity_analysis(df: pd.DataFrame) -> dict:
    """Check for missing values and infinities."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    missing = df[numeric_cols].isnull().sum()
    missing_cols = missing[missing > 0]

    inf_counts = {}
    for col in numeric_cols:
        n_inf = np.isinf(df[col]).sum() if df[col].dtype in [np.float64, np.float32] else 0
        if n_inf > 0:
            inf_counts[col] = int(n_inf)

    return {
        "total_missing_values": int(missing.sum()),
        "columns_with_missing": {k: int(v) for k, v in missing_cols.items()},
        "columns_with_infinity": inf_counts,
        "total_infinity_values": sum(inf_counts.values()),
    }


def run_eda(sample_frac: float = 1.0) -> dict:
    """Run full EDA pipeline."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading raw data...")
    df = load_raw_data(sample_frac=sample_frac, seed=SEED)
    print(f"  Loaded {len(df):,} rows, {len(df.columns)} columns")

    print("Analyzing missing values and infinities (before cleaning)...")
    data_quality = missing_and_infinity_analysis(df)
    print(f"  Missing: {data_quality['total_missing_values']}, Inf: {data_quality['total_infinity_values']}")

    print("Cleaning data...")
    df = clean_data(df)
    print(f"  After cleaning: {len(df):,} rows")

    print("Analyzing class distribution...")
    class_stats = class_distribution(df)
    print(f"  {class_stats['n_classes']} classes, majority={class_stats['majority_class']} ({class_stats['majority_pct']:.1f}%)")

    print("Analyzing features...")
    feature_stats = feature_analysis(df)
    print(f"  {feature_stats['n_features']} features, {feature_stats['n_highly_correlated_pairs']} highly correlated pairs")

    print("Analyzing feature controllability...")
    ctrl_stats = controllability_analysis(df)
    print(f"  {ctrl_stats['controllable_features']} controllable, {ctrl_stats['observable_features']} observable")

    summary = {
        "dataset": "CICIDS2017",
        "source": "Official CIC portal (University of New Brunswick)",
        "seed": SEED,
        "sample_fraction": sample_frac,
        "data_quality": data_quality,
        "class_distribution": class_stats,
        "feature_analysis": feature_stats,
        "controllability": ctrl_stats,
    }

    summary_path = OUTPUT_DIR / "eda_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\nEDA summary saved to {summary_path}")

    return summary


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="CICIDS2017 EDA")
    parser.add_argument("--sample-frac", type=float, default=1.0,
                        help="Fraction of data to load (default: 1.0 = all)")
    args = parser.parse_args()
    run_eda(sample_frac=args.sample_frac)
