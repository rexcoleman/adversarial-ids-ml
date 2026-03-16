# PROJECT BRIEF — Adversarial ML on Network Intrusion Detection

<!-- version: 1.0 -->
<!-- created: 2026-03-16 -->

## Thesis

Network intrusion detection systems built on classical ML classifiers are vulnerable to adversarial perturbation even under realistic feature constraints, but simple defenses can recover most lost performance.

## Research Questions

| RQ | Question |
|----|----------|
| RQ-1 | How much does adversarial noise degrade IDS classifier accuracy across epsilon values? |
| RQ-2 | Does constraining perturbations to attacker-controllable features (57/71) reduce attack success rate? |
| RQ-3 | Which defense strategy (adversarial training, feature squeezing, constraint-aware detection) recovers the most F1? |
| RQ-4 | Do gradient-boosted models (XGBoost) show different adversarial robustness than Random Forest? |

## Key Results

- XGBoost baseline macro-F1: 0.823, RF: 0.778, MLP: 0.717
- Constrained attacks reduce ASR by 15-40% vs unconstrained (feature mask works)
- Adversarial training recovers 85%+ of clean F1; constraint-aware detection most practical

## Target Venues

| Priority | Venue | Format | Status |
|----------|-------|--------|--------|
| 1 | Personal blog (Hugo) | Long-form post | Draft complete |
| 2 | BSides (regional) | 20-min talk + CFP | Pending |
| 3 | DEF CON AI Village | Talk/poster | Pending |

## Competitive Positioning

- **Novel angle:** Feature controllability analysis (57/14 split) is underexplored in IDS adversarial ML literature
- **Practical framing:** Defense recovery ratios, not just attack success rates
- **Reproducible:** Full govML governance, 5-seed stability, all outputs versioned

## Repository

- Data: CICIDS2017 (2017, Canadian Institute for Cybersecurity)
- Models: RF, XGBoost, MLP (sklearn)
- Attacks: Noise, ZOO, HopSkipJump via IBM ART
- Seeds: [42, 123, 456, 789, 1024]
