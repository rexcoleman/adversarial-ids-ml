"""
Phase 2b-2c: Adversarial attacks on IDS classifiers.

Part 2b: Unconstrained attacks (all features perturbed)
Part 2c: Constrained attacks (only attacker-controllable features)

Attack methods: FGSM, PGD (via IBM ART)
Target models: Trained baselines from Phase 2a

Generates:
  outputs/adversarial/unconstrained_results.json
  outputs/adversarial/constrained_results.json
  outputs/adversarial/budget_curve.png

Governed by: ADVERSARIAL_EVALUATION.md, HYPOTHESIS_CONTRACT H-1, H-2
"""

import argparse
import json
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import joblib
from sklearn.metrics import f1_score, accuracy_score

from art.estimators.classification import SklearnClassifier
from art.attacks.evasion import FastGradientMethod, ProjectedGradientDescent

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.preprocessing import (
    run_preprocessing_pipeline,
    set_seed,
    get_controllable_feature_mask,
)

OUTPUT_DIR = Path("outputs/adversarial")
MODEL_DIR = Path("models")

# Attack budget schedule (epsilon values)
EPSILON_SCHEDULE = [0.01, 0.05, 0.1, 0.2, 0.3, 0.5]


def load_trained_model(model_name: str, seed: int):
    """Load a trained baseline model."""
    path = MODEL_DIR / f"{model_name}_seed{seed}.pkl"
    if not path.exists():
        raise FileNotFoundError(f"Model not found: {path}. Run train_baselines.py first.")
    return joblib.load(path)


def wrap_sklearn_model(model, n_features: int, n_classes: int):
    """Wrap sklearn model for ART compatibility."""
    clip_values = (0.0, 1.0)  # Data is scaled but may exceed [0,1]
    return SklearnClassifier(model=model, clip_values=None)


def run_attack(art_model, X_test, y_test, epsilon, attack_type="fgsm",
               feature_mask=None):
    """Run adversarial attack and return metrics."""
    if attack_type == "fgsm":
        attack = FastGradientMethod(
            estimator=art_model,
            eps=epsilon,
            batch_size=1024,
        )
    elif attack_type == "pgd":
        attack = ProjectedGradientDescent(
            estimator=art_model,
            eps=epsilon,
            eps_step=epsilon / 4,
            max_iter=10,
            batch_size=1024,
        )
    else:
        raise ValueError(f"Unknown attack type: {attack_type}")

    # Apply feature mask for constrained attacks
    if feature_mask is not None:
        attack.set_params(mask=feature_mask)

    # Generate adversarial examples
    start = time.time()
    X_adv = attack.generate(x=X_test)
    attack_time = time.time() - start

    # Evaluate on adversarial examples
    y_pred_clean = art_model.predict(X_test).argmax(axis=1)
    y_pred_adv = art_model.predict(X_adv).argmax(axis=1)

    # Metrics
    clean_f1 = f1_score(y_test, y_pred_clean, average="macro", zero_division=0)
    adv_f1 = f1_score(y_test, y_pred_adv, average="macro", zero_division=0)
    clean_acc = accuracy_score(y_test, y_pred_clean)
    adv_acc = accuracy_score(y_test, y_pred_adv)

    # Attack success rate: fraction of correctly classified samples that are misclassified after attack
    correct_mask = y_pred_clean == y_test
    if correct_mask.sum() > 0:
        asr = (y_pred_adv[correct_mask] != y_test[correct_mask]).mean()
    else:
        asr = 0.0

    # L2 perturbation norm
    l2_norm = np.sqrt(((X_adv - X_test) ** 2).sum(axis=1)).mean()

    return {
        "epsilon": epsilon,
        "attack_type": attack_type,
        "clean_macro_f1": round(float(clean_f1), 4),
        "adv_macro_f1": round(float(adv_f1), 4),
        "f1_drop": round(float(clean_f1 - adv_f1), 4),
        "clean_accuracy": round(float(clean_acc), 4),
        "adv_accuracy": round(float(adv_acc), 4),
        "attack_success_rate": round(float(asr), 4),
        "mean_l2_perturbation": round(float(l2_norm), 4),
        "attack_time_seconds": round(attack_time, 2),
        "n_test_samples": len(X_test),
        "constrained": feature_mask is not None,
    }


def plot_budget_curves(unconstrained_results, constrained_results, model_name):
    """Plot F1 degradation vs epsilon budget for constrained and unconstrained."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    for attack_type in ["fgsm", "pgd"]:
        ax = axes[0] if attack_type == "fgsm" else axes[1]

        # Unconstrained
        u_results = [r for r in unconstrained_results if r["attack_type"] == attack_type]
        if u_results:
            eps = [r["epsilon"] for r in u_results]
            f1 = [r["adv_macro_f1"] for r in u_results]
            ax.plot(eps, f1, "r-o", label="Unconstrained", linewidth=2)

        # Constrained
        c_results = [r for r in constrained_results if r["attack_type"] == attack_type]
        if c_results:
            eps = [r["epsilon"] for r in c_results]
            f1 = [r["adv_macro_f1"] for r in c_results]
            ax.plot(eps, f1, "b-s", label="Constrained (realistic)", linewidth=2)

        # Clean baseline
        if u_results:
            ax.axhline(y=u_results[0]["clean_macro_f1"], color="green",
                       linestyle="--", label="Clean baseline", alpha=0.7)

        ax.set_xlabel("Epsilon (perturbation budget)")
        ax.set_ylabel("Macro-F1")
        ax.set_title(f"{attack_type.upper()} Attack — {model_name}")
        ax.legend()
        ax.set_ylim(0, 1.05)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / f"budget_curve_{model_name}.png",
                dpi=150, bbox_inches="tight")
    plt.close()


def run_adversarial_evaluation(model_names=None, seeds=None, sample_frac=0.1,
                                attack_types=None):
    """Run full adversarial evaluation."""
    if model_names is None:
        model_names = ["RandomForest", "XGBoost"]  # Skip MLP (weakest baseline)
    if seeds is None:
        seeds = [42]
    if attack_types is None:
        attack_types = ["fgsm", "pgd"]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_unconstrained = []
    all_constrained = []

    for seed in seeds:
        print(f"\n{'='*60}")
        print(f"Seed {seed}")
        print(f"{'='*60}")

        set_seed(seed)

        # Load preprocessed data
        print("Running preprocessing...")
        data = run_preprocessing_pipeline(seed=seed, sample_frac=sample_frac)
        X_test = data["X_test"].astype(np.float32)
        y_test = data["y_test"]
        feature_cols = data["feature_cols"]
        controllable_mask = data["controllable_mask"]

        for model_name in model_names:
            print(f"\n--- {model_name} ---")

            # Load trained model
            model = load_trained_model(model_name, seed)
            n_classes = len(data["label_names"])
            art_model = wrap_sklearn_model(model, X_test.shape[1], n_classes)

            for attack_type in attack_types:
                for epsilon in EPSILON_SCHEDULE:
                    print(f"  {attack_type.upper()} ε={epsilon:.2f} (unconstrained)...", end=" ")
                    result = run_attack(art_model, X_test, y_test, epsilon,
                                       attack_type=attack_type)
                    result["model"] = model_name
                    result["seed"] = seed
                    all_unconstrained.append(result)
                    print(f"F1: {result['clean_macro_f1']:.3f}→{result['adv_macro_f1']:.3f} "
                          f"(ASR={result['attack_success_rate']:.3f})")

                    print(f"  {attack_type.upper()} ε={epsilon:.2f} (constrained)...", end=" ")
                    result = run_attack(art_model, X_test, y_test, epsilon,
                                       attack_type=attack_type,
                                       feature_mask=controllable_mask.astype(np.float32))
                    result["model"] = model_name
                    result["seed"] = seed
                    all_constrained.append(result)
                    print(f"F1: {result['clean_macro_f1']:.3f}→{result['adv_macro_f1']:.3f} "
                          f"(ASR={result['attack_success_rate']:.3f})")

            # Plot budget curves
            model_u = [r for r in all_unconstrained
                       if r["model"] == model_name and r["seed"] == seed]
            model_c = [r for r in all_constrained
                       if r["model"] == model_name and r["seed"] == seed]
            plot_budget_curves(model_u, model_c, f"{model_name}_seed{seed}")

    # Save results
    for name, results in [("unconstrained", all_unconstrained),
                          ("constrained", all_constrained)]:
        path = OUTPUT_DIR / f"{name}_results.json"
        with open(path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nSaved: {path}")

    # Summary
    print(f"\n{'='*60}")
    print("ADVERSARIAL EVALUATION SUMMARY")
    print(f"{'='*60}")
    for model_name in model_names:
        print(f"\n  {model_name}:")
        for attack_type in attack_types:
            u = [r for r in all_unconstrained
                 if r["model"] == model_name and r["attack_type"] == attack_type
                 and r["epsilon"] == 0.3]
            c = [r for r in all_constrained
                 if r["model"] == model_name and r["attack_type"] == attack_type
                 and r["epsilon"] == 0.3]
            if u and c:
                print(f"    {attack_type.upper()} ε=0.3: "
                      f"Unconstrained ASR={u[0]['attack_success_rate']:.3f}, "
                      f"Constrained ASR={c[0]['attack_success_rate']:.3f}, "
                      f"Reduction={u[0]['attack_success_rate'] - c[0]['attack_success_rate']:.3f}")

    return {"unconstrained": all_unconstrained, "constrained": all_constrained}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Adversarial attacks on IDS")
    parser.add_argument("--models", nargs="+", default=["RandomForest", "XGBoost"],
                        help="Models to attack")
    parser.add_argument("--seeds", type=int, nargs="+", default=[42])
    parser.add_argument("--sample-frac", type=float, default=0.1)
    parser.add_argument("--attacks", nargs="+", default=["fgsm", "pgd"])
    args = parser.parse_args()
    run_adversarial_evaluation(
        model_names=args.models, seeds=args.seeds,
        sample_frac=args.sample_frac, attack_types=args.attacks,
    )
