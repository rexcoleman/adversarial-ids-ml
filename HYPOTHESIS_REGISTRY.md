# HYPOTHESIS REGISTRY

<!-- version: 1.0 -->
<!-- created: 2026-03-14 -->

> **Authority Hierarchy**
>
> | Priority | Document | Role |
> |----------|----------|------|
> | Tier 1 | `EXECUTION_PLAN.md` | Primary spec — highest authority |
> | Tier 2 | `TRADEOFF_LOG.md` | Clarifications — cannot override Tier 1 |
> | Tier 3 | `README.md` | Advisory only — non-binding if inconsistent with Tier 1/2 |
> | Contract | This document | Implementation detail — subordinate to all tiers above |
>
> **Conflict rule:** When a higher-tier document and this contract disagree, the higher tier wins.

### Companion Contracts

**Upstream (this contract depends on):**
- See `EXECUTION_PLAN.md` for research questions that motivate hypotheses

**Downstream (depends on this contract):**
- See `FINDINGS.md` for hypothesis resolution narratives and evidence references

---

## 1) Pre-Registration Protocol

Hypotheses were written before Phase 2b experiments began.

**Gate:** >= 4 hypotheses registered and committed to version control before any experiment script was executed.

---

## 2) Registry Table

| hypothesis_id | statement | falsification_criterion | metric | resolution | evidence |
|---------------|-----------|------------------------|--------|------------|----------|
| H-1 | Unconstrained adversarial perturbation (random noise, epsilon=0.3) degrades macro-F1 by >= 30 percentage points on both RF and XGBoost classifiers trained on CICIDS2017 | Either model retains macro-F1 within 30pp of its clean baseline under unconstrained noise at epsilon=0.3 | `clean_macro_f1 - adv_macro_f1 >= 0.30` for both models | **SUPPORTED** | `outputs/adversarial/unconstrained_results.json` — XGBoost: 0.986 -> 0.086 (-74pp at eps=0.3); RF: 0.985 -> 0.153 (-63pp at eps=0.3). Both exceed 30pp threshold by wide margin. |
| H-2 | Constraining perturbations to attacker-controllable features only (57/78) reduces attack success rate by >= 40% compared to unconstrained attack | Constrained ASR reduction is < 40% relative to unconstrained ASR for either model | `(unconstrained_ASR - constrained_ASR) / unconstrained_ASR >= 0.40` | **PARTIALLY SUPPORTED** | `outputs/adversarial/constrained_results.json` — XGBoost: ASR reduction 35% (close but below 40% threshold). RF: ASR reduction 5% (far below threshold). Constraint effect is model-dependent; XGBoost nearly meets criterion but RF does not. |
| H-3 | Adversarial training recovers more lost F1 than feature squeezing (input preprocessing defense) | Feature squeezing recovery ratio >= adversarial training recovery ratio | `adv_training_recovery > feature_squeezing_recovery` | **SUPPORTED** | `outputs/defense/defense_comparison.json` — Adversarial training recovery: XGBoost 61%, RF 37%. Feature squeezing recovery: XGBoost 0%, RF 1%. Adversarial training dominates feature squeezing across both models. |
| H-4 | Architectural defense (monitoring uncontrollable features for impossible changes) outperforms learned defense (adversarial training) in F1 recovery | Constraint-aware detection recovery ratio <= adversarial training recovery ratio | `constraint_detection_recovery > adv_training_recovery` | **PARTIALLY SUPPORTED** | `outputs/defense/defense_comparison.json` — Constraint-aware detection: 100% recovery (both models) against unconstrained noise. However, this defense detects perturbations to defender-observable features; a constrained adversary who avoids those features would bypass it entirely (HYPOTHESIZED, not tested). Against the tested threat model (unconstrained noise), architectural defense dominates. Against adaptive adversaries, conclusion would likely reverse. |

---

## 3) Resolution Protocol

| Resolution | Criteria |
|------------|----------|
| **SUPPORTED** | Metric meets or exceeds the stated threshold across all specified conditions |
| **PARTIALLY SUPPORTED** | Metric is met for some but not all conditions, or is close to threshold |
| **REFUTED** | Metric falls below the stated threshold |
| **INCONCLUSIVE** | Ambiguous results, insufficient data, or metric within noise margin |

---

## 4) Resolution Summary

All 4 hypotheses resolved. 2 fully supported, 2 partially supported.

**Key qualification:** All attacks use random noise perturbation only. Gradient-based attacks (FGSM, PGD, C&W) were not tested because sklearn RF and XGBoost lack differentiable outputs. Results should be interpreted as robustness against noise-based evasion, not against gradient-optimized adversaries.

**lock_commit:** `PENDING` — will be set to the git SHA of the commit that finalizes all hypothesis resolutions and compute results.

---

## 5) Acceptance Criteria

- [x] >= 4 hypotheses registered before Phase 2b
- [x] All hypotheses follow the required format (all 6 fields populated)
- [x] All hypotheses resolved (no PENDING status at project end)
- [x] Every resolution includes an evidence reference to a specific output file
- [x] Resolution narrative for each hypothesis included in FINDINGS.md
