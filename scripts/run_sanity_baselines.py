#!/usr/bin/env python
"""Run sanity-check baselines: DummyClassifier + shuffled labels.

Confirms that real models outperform trivial baselines, ruling out
data leakage or label correlation artifacts.

Baselines:
  1. DummyClassifier (most_frequent) — always predicts majority class
  2. DummyClassifier (stratified) — random predictions matching class distribution
  3. Shuffled labels — train RandomForest on shuffled y, test on real y

Seeds: [42, 123, 456, 789, 1024] (per EXPERIMENT_CONTRACT)

Outputs:
  outputs/baselines/sanity_seed{seed}.json
  outputs/baselines/sanity_summary.json

Usage:
    python scripts/run_sanity_baselines.py
    python scripts/run_sanity_baselines.py --seeds 42 --sample-frac 0.1
    python scripts/run_sanity_baselines.py --project-dir ~/adversarial-ids-ml
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score


DEFAULT_SEEDS = [42, 123, 456, 789, 1024]


def run_sanity_baselines(project_dir, seeds, sample_frac):
    """Run sanity baselines on CICIDS2017."""
    proj = Path(project_dir).resolve()
    sys.path.insert(0, str(proj))
    from src.preprocessing import run_preprocessing_pipeline, set_seed

    output_dir = proj / "outputs" / "baselines"
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

        seed_results = {"seed": seed, "baselines": {}}

        # --- 1. DummyClassifier (most_frequent) ---
        print("\n  DummyClassifier (most_frequent):")
        dummy_mf = DummyClassifier(strategy="most_frequent", random_state=seed)
        dummy_mf.fit(X_train, y_train)
        y_pred_mf = dummy_mf.predict(X_test)
        f1_mf = f1_score(y_test, y_pred_mf, average="macro", zero_division=0)
        print(f"    Macro-F1: {f1_mf:.4f}")
        seed_results["baselines"]["dummy_most_frequent"] = {
            "macro_f1": round(float(f1_mf), 4),
        }

        # --- 2. DummyClassifier (stratified) ---
        print("\n  DummyClassifier (stratified):")
        dummy_strat = DummyClassifier(strategy="stratified", random_state=seed)
        dummy_strat.fit(X_train, y_train)
        y_pred_strat = dummy_strat.predict(X_test)
        f1_strat = f1_score(y_test, y_pred_strat, average="macro", zero_division=0)
        print(f"    Macro-F1: {f1_strat:.4f}")
        seed_results["baselines"]["dummy_stratified"] = {
            "macro_f1": round(float(f1_strat), 4),
        }

        # --- 3. Real RF (reference) ---
        print("\n  RandomForest (real labels — reference):")
        rf_real = RandomForestClassifier(
            n_estimators=100, max_depth=20, min_samples_leaf=5,
            n_jobs=1, random_state=seed,
        )
        rf_real.fit(X_train, y_train)
        y_pred_real = rf_real.predict(X_test)
        f1_real = f1_score(y_test, y_pred_real, average="macro", zero_division=0)
        print(f"    Macro-F1: {f1_real:.4f}")
        seed_results["baselines"]["rf_real"] = {
            "macro_f1": round(float(f1_real), 4),
        }

        # --- 4. Shuffled labels ---
        print("\n  RandomForest (shuffled labels):")
        rng = np.random.RandomState(seed)
        y_train_shuffled = y_train.copy()
        rng.shuffle(y_train_shuffled)

        rf_shuffled = RandomForestClassifier(
            n_estimators=100, max_depth=20, min_samples_leaf=5,
            n_jobs=1, random_state=seed,
        )
        rf_shuffled.fit(X_train, y_train_shuffled)
        y_pred_shuf = rf_shuffled.predict(X_test)
        f1_shuf = f1_score(y_test, y_pred_shuf, average="macro", zero_division=0)
        print(f"    Macro-F1: {f1_shuf:.4f}")
        seed_results["baselines"]["rf_shuffled"] = {
            "macro_f1": round(float(f1_shuf), 4),
        }

        # Sanity gap
        gap = f1_real - f1_shuf
        gap_vs_dummy = f1_real - max(f1_mf, f1_strat)
        print(f"\n  Sanity gap (real - shuffled): {gap:.4f}")
        print(f"  Sanity gap (real - best dummy): {gap_vs_dummy:.4f}")
        print(f"  {'PASS' if gap > 0.1 else 'FAIL'}: real >> shuffled")
        print(f"  {'PASS' if gap_vs_dummy > 0.1 else 'FAIL'}: real >> dummy")

        seed_results["sanity_gap_vs_shuffled"] = round(float(gap), 4)
        seed_results["sanity_gap_vs_dummy"] = round(float(gap_vs_dummy), 4)
        seed_results["sanity_pass"] = gap > 0.1 and gap_vs_dummy > 0.1

        # Save per-seed
        seed_path = output_dir / f"sanity_seed{seed}.json"
        with open(seed_path, "w") as f:
            json.dump(seed_results, f, indent=2)
        print(f"\n  Saved: {seed_path}")
        all_results.append(seed_results)

    # Summary
    print(f"\n{'='*60}")
    print("SANITY BASELINE SUMMARY")
    print(f"{'='*60}")
    all_pass = True
    for r in all_results:
        status = "PASS" if r["sanity_pass"] else "FAIL"
        if not r["sanity_pass"]:
            all_pass = False
        print(f"  Seed {r['seed']}: "
              f"gap_shuf={r['sanity_gap_vs_shuffled']:.4f} "
              f"gap_dummy={r['sanity_gap_vs_dummy']:.4f} "
              f"[{status}]")

    summary = {
        "experiment": "sanity_baselines",
        "seeds": seeds,
        "all_pass": all_pass,
        "per_seed": all_results,
    }
    summary_path = output_dir / "sanity_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSummary saved: {summary_path}")


def main():
    parser = argparse.ArgumentParser(description="Run sanity-check baselines (FP-01)")
    parser.add_argument("--project-dir", default=".", help="Project root directory")
    parser.add_argument("--seeds", type=int, nargs="+", default=DEFAULT_SEEDS,
                        help="Random seeds (default: 42 123 456 789 1024)")
    parser.add_argument("--sample-frac", type=float, default=None,
                        help="Data sampling fraction for smoke testing")
    args = parser.parse_args()
    run_sanity_baselines(args.project_dir, args.seeds, args.sample_frac)


if __name__ == "__main__":
    main()
