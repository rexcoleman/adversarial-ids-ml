# HYPOTHESIS CONTRACT

<!-- version: 1.0 -->
<!-- created: 2026-02-20 -->
<!-- last_validated_against: CS_7641_Machine_Learning_SL_Report -->

> **Authority Hierarchy**
>
> | Priority | Document | Role |
> |----------|----------|------|
> | Tier 1 | `EXECUTION_PLAN.md` | Primary spec — highest authority |
> | Tier 2 | `docs/ADVERSARIAL_EVALUATION.md` | Clarifications — cannot override Tier 1 |
> | Tier 3 | `docs/EXPERIMENT_CONTRACT.md` | Advisory only — non-binding if inconsistent with Tier 1/2 |
> | Contract | This document | Implementation detail — subordinate to all tiers above |
>
> **Conflict rule:** When a higher-tier document and this contract disagree, the higher tier wins.
> Update this contract via `CONTRACT_CHANGE` or align implementation to the higher tier.

### Companion Contracts

**Upstream (this contract depends on):**
- See [DATA_CONTRACT](DATA_CONTRACT.tmpl.md) §6 for EDA compatibility and prior-work continuity
- See [METRICS_CONTRACT](METRICS_CONTRACT.tmpl.md) §2 for metric definitions referenced in predictions

**Downstream (depends on this contract):**
- See [EXPERIMENT_CONTRACT](EXPERIMENT_CONTRACT.tmpl.md) §1 for experiment design grounded in hypotheses
- See [REPORT_ASSEMBLY_PLAN](../report/REPORT_ASSEMBLY_PLAN.tmpl.md) §3 for hypothesis statements and §6 for resolution templates
- See [IMPLEMENTATION_PLAYBOOK](../management/IMPLEMENTATION_PLAYBOOK.tmpl.md) §2 for Phase 2 hypothesis gate

## Customization Guide

Fill in all `{{PLACEHOLDER}}` values before use. Delete this section when customization is complete.

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `Adversarial ML on Network Intrusion Detection` | Project name | Sentiment Analysis Benchmark |
| `{{DATASET_N_NAME}}` | Human-readable dataset name | Adult Income |
| `{{DATASET_N_EDA_OBSERVATION}}` | Key EDA finding driving the hypothesis | 3:1 class imbalance, high feature sparsity |
| `{{DATASET_N_PREDICTION}}` | Specific predicted outcome | Linear SVM will outperform DT on Adult |
| `{{DATASET_N_THEORY}}` | ML theory connecting EDA to prediction | Margin maximization is robust to sparse features |
| `{{DATASET_N_FAILURE_MODE}}` | Condition that would invalidate the prediction | High label noise causes SVM overfitting |
| `{{DATASET_N_METRIC}}` | Metric most relevant to this hypothesis | F1 (binary) |
| `{{DATASET_N_BASELINE_METRIC}}` | Baseline value for comparison | Accuracy = 0.758 (majority class) |
| `{{LOCK_COMMIT_SHA}}` | Git SHA of the commit that locks hypotheses | abc1234 |
| `EXECUTION_PLAN.md` | Tier 1 authority document | Project requirements spec |
| `docs/ADVERSARIAL_EVALUATION.md` | Tier 2 authority document | FAQ or clarifications document |
| `docs/EXPERIMENT_CONTRACT.md` | Tier 3 authority document | Course TAs' Piazza clarifications |

---

## 1) Purpose & Scope

This contract defines the hypothesis pre-registration protocol for the **Adversarial ML on Network Intrusion Detection** project. It ensures that testable predictions are formulated **before** experiments begin, grounded in EDA evidence and ML theory, preventing post-hoc rationalization.

**Core principle:** Hypotheses are predictions, not observations. They are written before results exist and resolved with quantitative evidence after experiments complete.

---

## 2) Temporal Gate

**Experiments MUST NOT begin before hypotheses are locked.**

The hypothesis lock is a hard phase gate:

1. Complete EDA for all datasets (see DATA_CONTRACT §6, IMPLEMENTATION_PLAYBOOK Phase 1)
2. Formulate hypotheses using the template in §4
3. Commit hypotheses with message: `HYPOTHESIS_LOCK: all hypotheses registered`
4. Record the lock commit SHA: `{{LOCK_COMMIT_SHA}}`
5. Only after this commit may experiment scripts be executed

**Enforcement:**
- Any experiment output with a git timestamp before the hypothesis lock commit is invalid
- Modifying a hypothesis after the lock requires a `CONTRACT_CHANGE` commit with justification
- Post-lock modifications MUST NOT change the predicted direction — only clarifications of scope or metric are permitted

---

## 3) Hypothesis Requirements

Every hypothesis MUST include all five components defined in §4. A hypothesis that omits any component is incomplete and MUST NOT be considered locked.

### Acceptance Checklist (per hypothesis)

- [ ] **Predicts a specific outcome** — not a vague expectation but a directional or quantitative claim
- [ ] **Grounded in EDA evidence** — cites a specific observation from EDA artifacts
- [ ] **Linked to ML theory** — names the mechanism connecting evidence to prediction
- [ ] **States a failure mode** — identifies what would cause the prediction to fail
- [ ] **Specifies a metric** — names the metric on which the prediction will be evaluated
- [ ] **Written before experiments** — committed before any experiment outputs exist

---

## 4) Per-Hypothesis Template

Copy this block for each hypothesis. Number sequentially: H-1, H-2, etc.

```markdown
### H-{{N}}: {{SHORT_TITLE}}

**Dataset:** {{DATASET_NAME}}

**Prediction:**
{{DATASET_N_PREDICTION}}

**EDA Evidence:**
{{DATASET_N_EDA_OBSERVATION}}
*(Cite specific artifact: e.g., "outputs/eda/adult_eda_summary.json shows 3:1 class imbalance")*

**Theory Link:**
{{DATASET_N_THEORY}}
*(Name the ML concept and explain the causal chain: EDA property → mechanism → predicted outcome)*

**Metric Focus:**
{{DATASET_N_METRIC}}
*(Why this metric is most relevant to testing this specific prediction)*

**Baseline Prediction:**
Relative to the baseline ({{DATASET_N_BASELINE_METRIC}}), I predict that [intervention]
will [improve / not improve] because [reasoning].

**Failure Mode:**
{{DATASET_N_FAILURE_MODE}}
*(What specific dataset property, hyperparameter setting, or assumption violation would cause
this prediction to fail?)*
```

---

## 5) Registered Hypotheses

### H-1: Unconstrained adversarial attacks will degrade IDS classifiers significantly

**Dataset:** CICIDS2017

**Prediction:**
Unconstrained FGSM and PGD attacks (perturbing all 78 features) will reduce macro-F1 of baseline classifiers (RF, XGBoost, MLP) by ≥30 percentage points at ε=0.3.

**EDA Evidence:**
`outputs/eda/eda_summary.json` shows 50 highly correlated feature pairs (|r|>0.95) and 8 zero-variance features. The high redundancy means perturbations propagate through correlated features, amplifying adversarial impact. The 80.3% BENIGN majority means even small adversarial perturbations to attack-class samples can flip predictions.

**Theory Link:**
Adversarial examples exploit the linear nature of high-dimensional spaces (Goodfellow et al., 2014). With 78 features and extensive correlations, the effective dimensionality is lower, meaning gradient-based attacks can find efficient perturbation directions. Tree-based models (RF, XGBoost) are also vulnerable because tabular adversarial attacks shift samples across decision boundaries in feature space.

**Metric Focus:**
Macro-F1 — accounts for the extreme class imbalance (206,484:1 ratio between BENIGN and Heartbleed). Accuracy would be misleading given 80.3% BENIGN prevalence.

**Baseline Prediction:**
Relative to clean-data macro-F1 (expected ≥0.85 for RF/XGBoost based on published CICIDS2017 benchmarks), I predict that unconstrained adversarial perturbation will reduce macro-F1 to ≤0.55 because gradient-based attacks exploit the high-dimensional feature space without constraints.

**Failure Mode:**
If baseline classifiers are already poorly calibrated on rare classes (Infiltration: 36 samples, Heartbleed: 11), the "degradation" floor may already be hit by the imbalance, masking the adversarial effect.

---

### H-2: Realistic constraints will substantially reduce attack effectiveness

**Dataset:** CICIDS2017

**Prediction:**
Constraining adversarial perturbations to the 57 attacker-controllable features (excluding 14 defender-observable features like TCP flags and Destination Port) will reduce attack success rate by ≥40% relative to unconstrained attacks at the same ε budget.

**EDA Evidence:**
`outputs/eda/eda_summary.json` shows the top discriminative feature is PSH Flag Count (|r|=0.31 with label), which is defender-observable only (set by OS TCP stack). The top 3 label-correlated features include 2 that are at least partially defender-controlled. Constraining attacks removes the most informative features from the attacker's perturbation space.

**Theory Link:**
Feature-constrained adversarial attacks have a strictly smaller feasible perturbation set. If the most discriminative features for classification are in the defender-observable set, constraining the attacker forces perturbations through less informative features, requiring larger ε to achieve the same evasion. This is the "realistic threat model" argument from Pierazzi et al. (2020).

**Metric Focus:**
Attack success rate (ASR) — the fraction of adversarial examples that flip the classifier's prediction from correct attack label to BENIGN. Directly measures evasion capability.

**Baseline Prediction:**
Relative to unconstrained ASR (predicted ≥80% at ε=0.3), I predict constrained ASR will be ≤48% at the same budget because the defender-observable features (especially TCP flags) carry disproportionate discriminative power.

**Failure Mode:**
If the 57 controllable features contain sufficient discriminative information (i.e., the 14 defender-observable features are redundant with controllable features due to the 50 high-correlation pairs), then constraints may not meaningfully reduce attack effectiveness.

---

### H-3: Adversarial training will be more effective than input preprocessing defenses

**Dataset:** CICIDS2017

**Prediction:**
Adversarial training (retraining with adversarial examples) will recover ≥60% of the macro-F1 lost to constrained attacks, while input preprocessing defenses (feature squeezing, spatial smoothing) will recover ≤30%.

**EDA Evidence:**
`outputs/eda/eda_summary.json` shows 8 zero-variance features and many near-duplicate feature pairs (e.g., Fwd Packet Length Mean ≡ Avg Fwd Segment Size, r=1.0). This redundancy means preprocessing that clips or smooths individual features will be bypassed by attacking through correlated "backup" features. Adversarial training learns the attack distribution directly.

**Theory Link:**
Adversarial training creates a minimax game where the model learns the distribution of adversarial perturbations (Madry et al., 2018). Input preprocessing is input-agnostic and cannot adapt to the specific perturbation patterns. With 50+ highly correlated feature pairs, attackers can shift perturbation weight to correlated features that preprocessing leaves intact.

**Metric Focus:**
Macro-F1 recovery ratio — (defended_F1 - attacked_F1) / (clean_F1 - attacked_F1). Measures what fraction of adversarial degradation each defense recovers.

**Baseline Prediction:**
Relative to constrained-attack macro-F1, I predict adversarial training will achieve recovery ratio ≥0.60 while preprocessing defenses will achieve ≤0.30 because adversarial training is model-aware and preprocessing is not.

**Failure Mode:**
If adversarial training overfits to the specific attack method used during training (e.g., PGD) and fails to generalize to adaptive attacks, the recovery ratio will be lower than predicted.

---

### H-4: Adaptive attacks will bypass adversarial training but not constrained-feature defenses

**Dataset:** CICIDS2017

**Prediction:**
An adaptive attacker with knowledge of the adversarial training defense will recover ≥70% of the attack success rate lost to adversarial training. However, against a defense that also enforces feature constraints (only monitoring defender-observable features for detection), the adaptive attacker will recover ≤30% because the constraint is architectural, not learned.

**EDA Evidence:**
`outputs/eda/eda_summary.json` shows 14 defender-observable features including all TCP flag counts and Destination Port. These features are set by the OS network stack or network routing — an attacker cannot forge them without root access on the victim's machine. This architectural constraint cannot be "adapted around" regardless of attacker knowledge.

**Theory Link:**
The "arms race" in adversarial ML (Carlini & Wagner, 2017; Tramer et al., 2020) shows that defenses relying on learned patterns are vulnerable to adaptive attacks that account for the defense. However, constraints based on physical or architectural impossibilities (attacker cannot control TCP flags on the receiving end) create a hard bound on attack capability that no optimization can overcome.

**Metric Focus:**
Adaptive attack success rate (ASR) relative to non-adaptive ASR — measures how much defense benefit survives when the attacker knows the defense.

**Baseline Prediction:**
Relative to non-adaptive constrained ASR, I predict adaptive attacks against adversarially-trained models will increase ASR by ≥20pp but adaptive attacks against constraint-aware detection will increase ASR by ≤8pp.

**Failure Mode:**
If the defender-observable features have low individual discriminative power (despite PSH Flag Count being #1 at r=0.31, it may not be sufficient alone for robust detection), then the architectural constraint defense will be weak, and adaptive attacks will succeed against it too.

*(Add additional hypotheses as needed. Multi-part projects may have hypotheses per experimental part.)*

---

## 6) Resolution Protocol

After experiments complete, every hypothesis MUST be formally resolved. Resolution is not optional — unresolved hypotheses are a delivery blocker.

### Resolution Template

Copy this block for each hypothesis resolution:

```markdown
### Resolution: H-{{N}}

**Verdict:** Confirmed | Refuted | Partially Confirmed

**Evidence:**
- Predicted: [restate the original prediction]
- Observed: [median = Y.YYY, IQR = [a, b], under Z budget, N seeds]
- Delta from baseline: [+/- X.XXX absolute change]

**Explanation:**
[Why the prediction was supported or contradicted. Cite the specific mechanism —
did the theory hold? Did the failure mode occur? What was unexpected?]

**Implications:**
[What this result means for the broader project or future work.]
```

---

## 7) Resolution Summary Table

Maintain this table as hypotheses are resolved. It provides a single-glance view of all predictions and outcomes.

| ID | Dataset | Prediction (short) | Metric | Predicted Direction | Observed Result | Verdict | Evidence Artifact |
|----|---------|-------------------|--------|--------------------|-----------------|---------|--------------------|
| H-1 | CICIDS2017 | Unconstrained attacks degrade F1 ≥30pp | Macro-F1 | Clean F1 ≥0.85 → Attacked F1 ≤0.55 | *(pending)* | *(pending)* | *(pending)* |
| H-2 | CICIDS2017 | Realistic constraints reduce ASR ≥40% | ASR | Unconstrained ASR ≥80% → Constrained ASR ≤48% | *(pending)* | *(pending)* | *(pending)* |
| H-3 | CICIDS2017 | Adv training > preprocessing defense | F1 recovery ratio | Adv train ≥0.60 vs preprocess ≤0.30 | *(pending)* | *(pending)* | *(pending)* |
| H-4 | CICIDS2017 | Adaptive attacks bypass learned but not architectural defenses | Adaptive ASR delta | Adv train: +20pp, constraint-aware: ≤+8pp | *(pending)* | *(pending)* | *(pending)* |

### Verdict Criteria

| Verdict | Definition |
|---------|-----------|
| **Confirmed** | Observed result matches predicted direction AND magnitude is practically meaningful |
| **Refuted** | Observed result contradicts predicted direction OR effect is negligible |
| **Partially Confirmed** | Predicted direction holds for some conditions (e.g., one dataset but not another, or only under certain budgets) — requires explicit scope statement |

---

## 8) Traceability

### Hypotheses → Report Sections

Every hypothesis MUST appear in the report in two locations:

1. **Statement** (before results) — Section 3 or equivalent, using the hypothesis template language
2. **Resolution** (after results) — Discussion/Conclusion, with quantitative evidence and verdict

| Hypothesis | Stated In | Resolved In | Resolution Artifact |
|-----------|-----------|-------------|---------------------|
| H-1 | Report §3 (Methodology) | Report §5 (Discussion) | `outputs/adversarial/unconstrained_results.json` |
| H-2 | Report §3 (Methodology) | Report §5 (Discussion) | `outputs/adversarial/constrained_results.json` |
| H-3 | Report §3 (Methodology) | Report §5 (Discussion) | `outputs/defense/defense_comparison.json` |
| H-4 | Report §3 (Methodology) | Report §5 (Discussion) | `outputs/adaptive/adaptive_results.json` |

### Hypotheses → Experiment Design

Each hypothesis SHOULD map to at least one experimental part or comparison. If a hypothesis cannot be tested by the planned experiments, either revise the hypothesis or add an experiment.

---

## 9) Acceptance Gate (Phase Exit Criteria)

Before proceeding to experiments, the following MUST pass:

- [ ] All hypotheses satisfy the acceptance checklist (§3)
- [ ] Hypotheses are committed with `HYPOTHESIS_LOCK` message
- [ ] Lock commit SHA recorded as `{{LOCK_COMMIT_SHA}}`
- [ ] No experiment outputs exist prior to the lock commit
- [ ] Each hypothesis maps to at least one planned experiment
- [ ] Resolution summary table (§7) is prepared with empty verdict/result columns

---

## 10) Change Control Triggers

The following changes require a `CONTRACT_CHANGE` commit:

- Adding, removing, or modifying a hypothesis after lock
- Changing the predicted direction of any hypothesis
- Changing the metric focus of any hypothesis
- Modifying the resolution verdict after it has been recorded
- Changing the temporal gate rules
