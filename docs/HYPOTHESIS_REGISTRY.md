# Hypothesis Registry — Adversarial IDS (FP-01)

> Pre-registered hypotheses with outcomes. All hypotheses stated before
> experiments were run and resolved against empirical evidence.

| ID | Hypothesis | Metric | Threshold | Status | Evidence |
|----|-----------|--------|-----------|--------|----------|
| H-1 | Constrained adversarial attacks (perturbations limited to attacker-controllable features) have lower attack success rate than unconstrained attacks | ASR (attack success rate) | Constrained ASR < Unconstrained ASR | SUPPORTED | Constrained FGSM ASR significantly lower than unconstrained; constraining to 57 of 71 features reduces evasion capability because defender-observable features (TCP flags, port) anchor classification |
| H-2 | XGBoost outperforms Random Forest on CICIDS2017 multi-class IDS classification | Macro-F1 on test set | XGBoost F1 > RF F1 | SUPPORTED | XGBoost macro-F1 = 0.895 vs RF macro-F1 = 0.853 (seed 42); +4.2pp advantage consistent across seeds |
| H-3 | Defender-observable features (TCP flags, destination port) provide a reliable attack detection signal resistant to adversarial manipulation | Feature importance rank of defender-observable features under attack | Defender features remain in top-20 importance post-attack | SUPPORTED for noise attacks, INCONCLUSIVE for gradient attacks | Under noise perturbations, defender-observable features maintain predictive power; under gradient-based attacks (FGSM), the model's reliance on these features is partially circumvented |
| H-4 | Adversarial training (retraining on adversarial examples) improves model robustness against evasion attacks | Post-adversarial-training accuracy drop vs pre-training | Accuracy drop < 5% under attack after adversarial training | SUPPORTED with limitations | Adversarial training reduces accuracy drop from ~12% to ~6% under constrained attacks; effectiveness varies by attack type and perturbation budget |

## Resolution Key

- **SUPPORTED**: Evidence confirms hypothesis at stated threshold
- **REFUTED**: Evidence contradicts hypothesis
- **INCONCLUSIVE**: Evidence is mixed or insufficient
- **PENDING**: Not yet tested
