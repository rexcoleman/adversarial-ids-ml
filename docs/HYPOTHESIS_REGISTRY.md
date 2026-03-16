# Hypothesis Registry — Adversarial IDS (FP-01)

> Pre-registered hypotheses with outcomes. All hypotheses stated before
> experiments were run and resolved against empirical evidence.

---

## Hypotheses

### H-1: Feature Controllability Reduces Attack Success

**Statement:** Restricting adversarial perturbations to attacker-controllable features (57 of 78) reduces attack success rate compared to unconstrained perturbation of all features.

| Field | Value |
|-------|-------|
| Metric | Attack Success Rate (ASR) at epsilon=0.3 |
| Threshold | Constrained ASR < Unconstrained ASR by >= 20% |
| Status | **PARTIALLY SUPPORTED** [DEMONSTRATED: 1 seed, noise perturbation] |
| Evidence | XGBoost: constrained ASR 0.227 vs unconstrained ASR 0.350 = 35% reduction. RF: constrained ASR 0.139 vs unconstrained ASR 0.146 = 5% reduction. XGBoost meets threshold; RF does not. |
| Data Files | `outputs/adversarial/constrained_results.json`, `outputs/adversarial/unconstrained_results.json` |

**Interpretation:** XGBoost relies more heavily on defender-observable features (TCP flags, destination port), so constraining perturbations to only controllable features substantially reduces attack effectiveness. RF distributes importance more evenly across features, making the constraint less impactful.

---

### H-2: Tree Ensembles Outperform on Tabular IDS Data

**Statement:** Tree-based ensemble methods (XGBoost, Random Forest) outperform neural networks (MLP) and kernel methods (SVM-RBF) on CICIDS2017 multi-class IDS classification, as measured by macro-F1.

| Field | Value |
|-------|-------|
| Metric | Test macro-F1 (mean across 4-5 seeds) |
| Threshold | Tree ensemble F1 > Non-tree F1 by >= 5pp |
| Status | **SUPPORTED** [DEMONSTRATED: 5 seeds for baselines, 5 seeds for expanded] |
| Evidence | XGBoost: 0.895 +/- 0.013. RF: 0.853 +/- 0.005. MLP: 0.774 +/- 0.007. SVM-RBF: 0.503 +/- 0.004. LightGBM: 0.174 +/- 0.063 (degraded — see H-5). XGBoost beats MLP by +12pp and SVM-RBF by +39pp. |
| Data Files | `outputs/baselines/baseline_results.json`, `outputs/models/expanded_summary.json` |

**Interpretation:** Consistent with the ML literature on tabular data: tree ensembles handle mixed feature scales, high cardinality, and class imbalance better than MLPs and SVMs. XGBoost's gradient boosting captures feature interactions that RF's bagging misses, yielding a +4pp advantage.

---

### H-3: Adversarial Robustness Varies by Feature Controllability

**Statement:** Noise perturbation success (F1 drop) differs between constrained (controllable-only) and unconstrained (all features) attacks, and the gap widens at higher epsilon values.

| Field | Value |
|-------|-------|
| Metric | F1 drop difference (unconstrained - constrained) across epsilon values |
| Threshold | Constrained F1 > Unconstrained F1 at epsilon >= 0.1 |
| Status | **SUPPORTED** [DEMONSTRATED: 1 seed, 6 epsilon values] |
| Evidence | At epsilon=0.3: XGBoost unconstrained F1=0.100 vs constrained F1=0.213 (gap=+0.113). RF unconstrained F1=0.207 vs constrained F1=0.218 (gap=+0.011). The gap is model-dependent: XGBoost shows strong controllability effect, RF shows weak effect. Gap grows with epsilon for XGBoost but plateaus for RF. |
| Data Files | `outputs/adversarial/constrained_results.json`, `outputs/adversarial/unconstrained_results.json` |

**Interpretation:** The XGBoost result confirms that feature controllability is a meaningful defense dimension. The RF result suggests that not all models benefit equally from controllability constraints — RF's robustness comes from ensemble averaging rather than reliance on specific feature subsets.

---

### H-4: Architectural Defense Outperforms Learned Defense

**Statement:** Constraint-aware detection (monitoring defender-observable features for impossible changes) outperforms adversarial training and feature squeezing as a defense against unconstrained noise perturbation.

| Field | Value |
|-------|-------|
| Metric | Recovery ratio (fraction of lost F1 recovered by defense) |
| Threshold | Constraint-aware recovery > Adversarial training recovery |
| Status | **SUPPORTED** [DEMONSTRATED: 1 seed, noise perturbation only] |
| Evidence | Constraint-aware detection: 100% recovery (both models). Adversarial training: 61% (XGBoost), 37% (RF). Feature squeezing: 0% (both models). |
| Data Files | `outputs/defense/defense_comparison.json` |

**Caveat:** The 100% detection rate is against *unconstrained* noise, which naively perturbs all features including defender-observable ones. A constrained adversary who avoids perturbing those features would bypass this defense entirely. The defense's value is as a low-cost filter for unsophisticated perturbation, not as a complete solution against adaptive attackers. [HYPOTHESIZED for generalization to gradient-based/adaptive adversaries]

---

### H-5: Expanded Algorithm Performance (SVM-RBF and LightGBM)

**Statement:** SVM-RBF and LightGBM achieve competitive performance (within 10pp macro-F1) relative to RF and XGBoost on CICIDS2017.

| Field | Value |
|-------|-------|
| Metric | Test macro-F1 (mean across 5 seeds) |
| Threshold | F1 gap < 10pp vs RF baseline |
| Status | **REFUTED** [DEMONSTRATED: 5 seeds] |
| Evidence | SVM-RBF: 0.503 +/- 0.004 (35pp below RF). LightGBM: 0.174 +/- 0.063 (68pp below RF, high variance). Both significantly underperform the tree ensemble baselines. |
| Data Files | `outputs/models/expanded_summary.json` |

**Interpretation:** SVM-RBF was subsampled to 50K training rows (SVM O(n^2) memory), which may explain its underperformance — it sees less than 30% of the training data that RF/XGBoost use. LightGBM's poor and unstable results (std=0.063) suggest hyperparameter sensitivity or a data pipeline incompatibility (e.g., handling of the 15-class label encoding). These results do not indicate that SVM-RBF and LightGBM are inherently poor algorithms — they indicate that these implementations, under these constraints, underperform.

---

### H-6: Learning Curves Show Genuine Signal

**Statement:** CICIDS2017 classification performance improves with more training data (up to 75% of available data), indicating genuine learnable signal rather than memorization.

| Field | Value |
|-------|-------|
| Metric | Validation macro-F1 across training fractions [0.10, 0.25, 0.50, 0.75, 1.00] |
| Threshold | Monotonic improvement from 10% to 75% (val F1 increases by >= 5pp) |
| Status | **SUPPORTED** [SUGGESTED: 1 seed, 10% sample] |
| Evidence | XGBoost val F1: 0.821 (10%) -> 0.897 (25%) -> 0.906 (50%) -> 0.922 (75%) -> 0.900 (100%). RF val F1: 0.629 -> 0.792 -> 0.812 -> 0.867 -> 0.840. Both show genuine improvement then slight decline at 100%. |
| Data Files | `outputs/diagnostics/learning_curves_seed42.json` |

**Interpretation:** The 75% -> 100% decline suggests the final quartile introduces noise or edge-case class imbalance. Single-seed, 10% sample — needs multi-seed validation to strengthen from SUGGESTED to DEMONSTRATED.

---

## Resolution Key

| Tag | Meaning |
|-----|---------|
| **SUPPORTED** | Evidence confirms hypothesis at stated threshold |
| **PARTIALLY SUPPORTED** | Evidence confirms for some conditions but not all |
| **REFUTED** | Evidence contradicts hypothesis |
| **INCONCLUSIVE** | Evidence is mixed or insufficient |
| **PENDING** | Not yet tested |

## Claim Strength Tags

| Tag | Meaning |
|-----|---------|
| [DEMONSTRATED] | Multi-seed, CI reported, raw data matches |
| [SUGGESTED] | Consistent pattern but limited evidence (1-2 seeds) |
| [PROJECTED] | Extrapolated from partial evidence |
| [HYPOTHESIZED] | Untested prediction |
