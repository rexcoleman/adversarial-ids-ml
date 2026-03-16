# IMPLEMENTATION PLAYBOOK

<!-- version: 1.0 -->
<!-- created: 2026-03-16 -->

## 1) Purpose

Defines the four implementation phases with explicit Definition of Done (DoD) gates.

## 2) Phase Overview

| Phase | Name | Description | Status |
|-------|------|-------------|--------|
| 0 | Data + Environment | Data download, preprocessing, env validation | COMPLETE |
| 1 | Baselines | Train RF, XGBoost, MLP on clean CICIDS2017 | COMPLETE |
| 2 | Attacks | Noise, ZOO, HopSkipJump at 6 epsilon values | COMPLETE |
| 3 | Defenses | Adversarial training, feature squeezing, constraint-aware detection | COMPLETE |
| 4 | Figures + Publication | Report figures, blog draft, venue submission | IN PROGRESS |

## 3) Phase Definitions of Done

### Phase 0: Data + Environment
- [x] CICIDS2017 raw CSVs downloaded (8 files)
- [x] `scripts/check_data_ready.py` exits 0
- [x] `scripts/verify_env.sh` exits 0
- [x] Preprocessing pipeline produces 78 features after cleaning
- [x] Stratified 70/15/15 split validated

### Phase 1: Baselines
- [x] RF, XGBoost, MLP trained for seed 42
- [x] All models achieve macro-F1 > 0.70 (XGB: 0.823, RF: 0.778, MLP: 0.717)
- [x] Models saved to `models/{Model}_seed{seed}.pkl`
- [x] Multi-seed training (5 seeds) complete for stability analysis

### Phase 2: Attacks
- [x] Unconstrained + constrained attacks at epsilon [0.01, 0.05, 0.1, 0.2, 0.3, 0.5]
- [x] Attack success rates computed for RF and XGBoost
- [x] Feature controllability split applied (57 controllable / 14 system)
- [x] Results in `outputs/adversarial/`

### Phase 3: Defenses
- [x] Adversarial training (50K noise-augmented samples)
- [x] Feature squeezing (4-bit quantization)
- [x] Constraint-aware detection (defender-observable feature flagging)
- [x] Recovery ratios computed and saved to `outputs/defense/defense_comparison.json`

### Phase 4: Figures + Publication
- [x] FINDINGS.md shipped
- [x] Blog draft written
- [ ] Figures regenerated at publication quality
- [ ] BSides CFP submitted
- [ ] DEF CON AI Village submission

## 4) Dependencies

```
Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4
                  ↘ Phase 2 also feeds Phase 4 directly (attack figures)
```

## 5) Change Control

Phase gate criteria changes require a `CONTRACT_CHANGE` commit.
