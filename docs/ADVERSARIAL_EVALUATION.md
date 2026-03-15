# ADVERSARIAL EVALUATION

<!-- version: 1.0 -->
<!-- created: 2026-03-11 -->
<!-- last_validated_against: none -->

> **Activation:** This template is OPTIONAL. Include it when your project involves adversarial
> robustness evaluation, security-sensitive ML, or when the project specification requires
> robustness analysis. Delete if not applicable.

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
- See [EXPERIMENT_CONTRACT](EXPERIMENT_CONTRACT.tmpl.md) §2 for compute budgets (adversarial budget draws from the same pool)
- See [METRICS_CONTRACT](METRICS_CONTRACT.tmpl.md) §2 for baseline metric definitions
- See [DATA_CONTRACT](DATA_CONTRACT.tmpl.md) §4 for leakage prevention (adversarial examples must not leak test data)

**Downstream (depends on this contract):**
- See [FIGURES_TABLES_CONTRACT](FIGURES_TABLES_CONTRACT.tmpl.md) §3 for robustness figures
- See [REPORT_ASSEMBLY_PLAN](../report/REPORT_ASSEMBLY_PLAN.tmpl.md) for adversarial analysis section placement
- See [RISK_REGISTER](../management/RISK_REGISTER.tmpl.md) for adversarial-specific risk entries

## Customization Guide

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `Adversarial ML on Network Intrusion Detection` | Project name | Image Classification Robustness Study |
| `{{THREAT_MODEL}}` | Adversary capability description | White-box, Lp-bounded, untargeted |
| `{{PERTURBATION_NORM}}` | Norm constraint | L∞, L2, L1 |
| `{{EPSILON_VALUES}}` | Perturbation budget values | [0.01, 0.03, 0.1, 0.3] |
| `{{ATTACK_METHODS}}` | Attack algorithms to evaluate | FGSM, PGD-20, AutoAttack |
| `{{DEFENSE_METHODS}}` | Defense methods (if applicable) | Adversarial training, input preprocessing |
| `{{ROBUSTNESS_METRICS}}` | Metrics for adversarial evaluation | Robust accuracy, certified radius |
| `EXECUTION_PLAN.md` | Tier 1 authority document | Project requirements spec |
| `docs/ADVERSARIAL_EVALUATION.md` | Tier 2 authority document | FAQ or clarifications document |
| `docs/EXPERIMENT_CONTRACT.md` | Tier 3 authority document | Advisory clarifications |

---

## 1) Purpose & Scope

This contract defines the adversarial evaluation protocol for the **Adversarial ML on Network Intrusion Detection** project. It specifies the threat model, attack and defense methods, robustness metrics, and disclosure requirements.

---

## 2) Threat Model Definition

The threat model MUST be defined before any adversarial evaluation begins. It constrains the adversary's knowledge, capability, and goals.

| Property | Value |
|----------|-------|
| **Adversary knowledge** | Black-box (no gradient access; sklearn models are non-differentiable) |
| **Adversary goal** | Untargeted misclassification (evade IDS detection — flip attack-class flows to BENIGN) |
| **Perturbation type** | Input perturbation (evasion attacks on test-time network flow features) |
| **Perturbation norm** | L∞ (uniform noise within ε-ball per feature) |
| **Perturbation budget (ε)** | [0.01, 0.05, 0.1, 0.2, 0.3, 0.5] |
| **Attack surface** | Test-time inputs (57 attacker-controllable features out of 78 total) |

### 2b) Formal Threat Model (YAML)

```yaml
threat_model:
  adversary_knowledge: black_box
  adversary_capability:
    perturbation_type: noise  # Only noise tested; gradient attacks NOT tested
    perturbation_budget:
      norm: L_inf
      epsilon: [0.01, 0.05, 0.1, 0.2, 0.5, 1.0]
    access:
      - feature_values  # Can observe and modify input features
    constraints:
      - "Cannot modify defender-observable features (14 of 71 total)"
      - "Cannot modify system-determined features"
  adversary_goal: untargeted  # Evade detection (cause misclassification)
  attack_surface:
    controllable_features: [payload_bytes, packet_size, port_number, protocol_flags, timing_intervals, ...]  # 57 features
    observable_features: [flow_duration, total_packets, bytes_transferred, ...]  # 14 features
    system_features: []
  attacks_tested:
    - type: random_noise_unconstrained
      sophistication: low
      tool: custom (numpy random perturbation)
    - type: random_noise_constrained
      sophistication: low
      tool: custom (numpy, controllable features only)
  attacks_NOT_tested:
    - type: FGSM
      reason: "sklearn RF/XGBoost lack differentiable outputs; would require PyTorch retraining"
    - type: PGD
      reason: "Same — requires gradient access"
    - type: C&W
      reason: "Same — gradient-based optimization"
    - type: transferability_attack
      reason: "Out of scope — would require training surrogate model"
    - type: adaptive_attack
      reason: "Out of scope — adversary aware of defense not tested"
  limitation_acknowledgment: |
    All attacks use random noise perturbation only. This represents a weak adversary.
    Gradient-based attacks (FGSM, PGD, C&W) were not tested because sklearn models
    lack differentiable outputs. Results should be interpreted as robustness against
    noise-based evasion, not against gradient-optimized or adaptive adversaries.
```

**Rule:** The threat model MUST be documented in the report Methods section before adversarial experiments run.

**Verification:** Report Methods section contains a threat model paragraph specifying all properties above. `config_resolved.yaml` records `threat_model`, `perturbation_norm`, and `epsilon` for every adversarial run.

---

## 3) Perturbation Types

### 3.1 Input Perturbations (Evasion Attacks)

Additive perturbations to test-time inputs within an Lp-norm ball.

| Attack | Type | Parameters | When to Use |
|--------|------|-----------|-------------|
| **Random Noise** | Black-box, zero-query | ε | Sanity check baseline; lower bound on vulnerability |
| **ZOO** | Black-box, query-based | confidence, lr, max_iter, h | Zeroth-order optimization; estimates gradients via finite differences |
| **HopSkipJump** | Black-box, decision-based | max_iter, max_eval | Decision-boundary attack; no gradient or probability access needed |
| ~~FGSM~~ | ~~White-box~~ | ~~ε~~ | ~~Not applicable — sklearn RF/XGBoost lack gradient access (ISS-020)~~ |
| ~~PGD~~ | ~~White-box~~ | ~~ε, step_size~~ | ~~Not applicable — same reason~~ |

**Budget rule:** Attack iterations (PGD steps, query count) MUST be logged in `summary.json`. Total adversarial compute budget MUST be reported alongside standard evaluation budget.

### 3.2 Feature Controllability Matrix (ISS-010)

The core differentiator of this project: not all features are equally perturbable by a real attacker.

| Category | Count | Examples | Rationale |
|----------|-------|---------|-----------|
| **Attacker-controllable** | 57 | Fwd Packet Length Mean, Flow Duration, Idle Mean/Std, Fwd IAT Mean | Attacker controls packet timing, payload size, flow patterns |
| **Defender-observable only** | 14 | PSH Flag Count, Destination Port, SYN Flag Count, FIN Flag Count, URG Flag Count | Set by OS TCP stack or network routing — attacker cannot forge on receiver side |
| **Excluded (zero-variance/inf)** | 7 | Bwd PSH Flags, Fwd URG Flags, Fwd Avg Bytes/Bulk | Removed during EDA — zero variance or infinite values |

**Constraint enforcement:** `src/preprocessing.py` exports `ATTACKER_CONTROLLABLE_FEATURES`, `DEFENDER_OBSERVABLE_ONLY`, and `get_controllable_feature_mask()`. Constrained attacks multiply perturbation by the binary mask (1=controllable, 0=defender-only).

**Domain expertise source:** TCP/IP protocol specification (attacker cannot modify receiver-side TCP flags without root on victim), CICIDS2017 feature documentation, Pierazzi et al. (2020) realistic threat model framework.

### 3.2b Data Poisoning

> **Not applicable** for this project. Evasion attacks only (test-time perturbation).

### 3.3–3.4 RL Sections

> **Not applicable.** This is a supervised classification project.

---

## 4) Robustness Metrics

### 4.1 Required Metrics

| Metric | Definition | When Required |
|--------|-----------|---------------|
| **Clean accuracy** | Standard accuracy on unperturbed test set | Always (baseline) |
| **Robust accuracy** | Accuracy under strongest attack at each ε | Always |
| **Attack success rate** | Fraction of correctly-classified inputs that are misclassified after attack | Always |
| **Accuracy drop** | Clean accuracy − Robust accuracy | Always |
| **Macro-F1 drop** | Clean macro-F1 − adversarial macro-F1 | Always (captures multi-class performance) |
| **F1 recovery ratio** | (defended_F1 − attacked_F1) / (clean_F1 − attacked_F1) | When evaluating defenses |
| **Detection rate** | Fraction of adversarial samples detected by constraint-aware defense | When evaluating constraint-aware detection |
| ~~Certified radius~~ | ~~Not applicable — no certified defenses evaluated~~ | ~~N/A~~ |

**Verification:** `final_eval_results.json` contains `clean_accuracy`, `robust_accuracy_eps_{ε}`, and `attack_success_rate_eps_{ε}` for each ε value.

### 4.2 Reporting Requirements

- Robustness MUST be reported at multiple ε values, not just a single point
- Results MUST include both clean and robust accuracy to show the accuracy-robustness tradeoff
- Seed dispersion MUST be reported (median + IQR across seeds)
- Attack hyperparameters (steps, step size, restarts) MUST be disclosed

---

## 5) Adversarial Budget Accounting

### 5.1 Compute Budget

Adversarial evaluation has its own compute cost that MUST be tracked separately.

| Budget Component | Unit | How Counted |
|-----------------|------|-------------|
| Attack generation | forward + backward passes | Per-sample: n_steps × (1 forward + 1 backward) for PGD |
| Robustness evaluation | forward passes | Per-sample: 1 forward per attack variant per ε |
| Adversarial training *(if applicable)* | grad_evals | Same as standard training budget, logged separately |

### 5.2 Logging

Every adversarial evaluation run MUST log in `summary.json`:

```json
{
  "adversarial": {
    "attack": "noise",
    "epsilon": 0.03,
    "attack_steps": 20,
    "attack_step_size": 0.003,
    "n_restarts": 1,
    "total_attack_forward_passes": 0,
    "total_attack_backward_passes": 0,
    "clean_accuracy": 0.0,
    "robust_accuracy": 0.0,
    "attack_success_rate": 0.0
  }
}
```

---

## 6) Evaluation Protocol

### 6.1 Standard Evaluation Sequence

```
1. Evaluate clean accuracy and macro-F1 on unperturbed test set (2,000-sample eval subset)
2. For each ε in [0.01, 0.05, 0.1, 0.2, 0.3, 0.5]:
   a. Generate adversarial examples via noise perturbation (unconstrained: all 78 features)
   b. Generate adversarial examples via noise perturbation (constrained: 57 controllable only)
   c. Evaluate macro-F1, accuracy, ASR on both
   d. Log mean L2 perturbation norm and attack time
3. Report budget curves: F1 vs ε for constrained and unconstrained (per model)
4. For ε=0.3 (standard budget): run defense evaluation (Phase 2d)
```

### 6.2 Defense Evaluation

Three defenses evaluated (HYPOTHESIS_CONTRACT H-3, H-4):

| Defense | Method | Parameters | Recovery Metric |
|---------|--------|-----------|----------------|
| **Adversarial Training** | Retrain on clean + noise-augmented data (50K adversarial samples) | ε=0.3, same model hyperparameters | F1 recovery ratio |
| **Feature Squeezing** | Quantize input features to 4-bit depth | bit_depth=4 (16 levels) | F1 recovery ratio |
| **Constraint-Aware Detection** | Flag samples where defender-observable features changed | threshold=0.1 on max absolute diff | Detection rate + F1 recovery |

| Property | Requirement |
|----------|------------|
| **Adaptive attacks** | H-4 requires adaptive attacker evaluation — constrained attacker who knows defense but can only perturb 57 controllable features |
| **No security through obscurity** | Defense mechanism fully disclosed; constraint-aware detection relies on architectural impossibility (attacker cannot forge receiver-side TCP flags), not secrecy |

**Limitation (FINDINGS.md §Limitations):** Constraint-aware detection achieved 100% detection on noise attacks because noise perturbs ALL features including defender-observable ones. A constrained attacker (who only perturbs controllable features) would evade this specific detection — but that's the point: the constraint itself IS the defense.

---

## 7) Adversarial Baselines

Every adversarial evaluation MUST include baselines for context:

| Baseline | Purpose |
|----------|---------|
| **Undefended model** | Clean accuracy upper bound; robustness lower bound |
| **Random perturbation** | Distinguishes adversarial vulnerability from noise sensitivity |
| **Strongest known attack** | Upper bound on vulnerability (AutoAttack recommended) |

---

## 8) Disclosure Rules

### 8.1 Report Disclosures

The report MUST disclose:

- Complete threat model definition (§2)
- All attack methods, hyperparameters, and implementation sources
- All defense methods and training procedures (if applicable)
- Clean vs robust accuracy at every evaluated ε
- Compute cost of adversarial evaluation
- Any limitations of the evaluation (e.g., attacks not tested, threat models not covered)

### 8.2 Figure and Table Requirements

- Accuracy-robustness curves MUST show clean accuracy as the y-intercept (ε=0)
- Tables MUST include both clean and robust columns
- Captions MUST state the attack method, ε value, and number of seeds

---

## 9) Acceptance Criteria

- [x] Threat model documented before adversarial experiments (§2 filled)
- [x] Clean accuracy baseline established (Part 2a: XGB 0.823, RF 0.778, MLP 0.717 macro-F1)
- [x] Robust accuracy evaluated at all specified ε values (6 values × 2 constraint modes × 2 models)
- [x] Attack hyperparameters logged in `outputs/adversarial/*.json`
- [x] Adversarial compute budget tracked (attack_time_seconds per run)
- [x] Baselines included (undefended model + random noise perturbation)
- [ ] Seed dispersion reported for all adversarial metrics (multi-seed in progress)
- [x] Report discloses all required information (FINDINGS.md §Limitations)

---

## 10) Change Control Triggers

The following changes require a `CONTRACT_CHANGE` commit:

- Threat model definition (adversary knowledge, goal, perturbation type/norm)
- ε values or attack method list
- Robustness metric definitions
- Defense methods or adversarial training protocol
- Evaluation protocol or baseline list
- Disclosure requirements

---

## Appendix B: Systems Security Evaluation

> **Not applicable.** This is a Python ML project — no compiled code, no buffer overflows. Appendix deleted.
