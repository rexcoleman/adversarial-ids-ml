# Adversarial ML on Network Intrusion Detection: What Feature Controllability Reveals

Your IDS adversarial defense is probably testing the wrong threat model. I built an adversarial ML pipeline against a CICIDS2017 classifier and discovered that the most effective defense isn't adversarial training — it's understanding which features an attacker can actually control.

## What I Built

An end-to-end adversarial ML pipeline on the CICIDS2017 network intrusion detection dataset (2.83M flows, 15 attack classes). Three classifiers (XGBoost, Random Forest, MLP), three defense strategies, and the key insight: a **feature controllability matrix** that splits 78 network features into 57 attacker-controllable and 14 defender-observable.

Built with [govML](https://github.com/rexcoleman/govML) for project governance. This was the project that led to govML's security-ml profile.

## The Problem With Standard Adversarial Testing

Most adversarial ML research on IDS treats all features as equally perturbable. Apply FGSM, PGD, or random noise to all 78 features, measure accuracy drop, declare the model "vulnerable." But network attackers can't control everything:

- **Attacker-controlled (57 features):** Packet timing, payload size, flow duration — the attacker crafts these
- **Defender-observable only (14 features):** TCP flags, destination port — set by the OS/network stack, not the attacker

When you restrict perturbations to only the 57 attacker-controllable features, the picture changes dramatically.

## Architecture

```
CICIDS2017 (2.83M flows)
    │
    ├── Feature Engineering
    │     57 attacker-controllable features
    │     14 defender-observable features
    │     7 mixed/derived features
    │
    ├── Baselines (5 seeds)
    │     XGBoost: 0.895 ± 0.013 macro-F1
    │     Random Forest: 0.853 ± 0.005
    │     MLP: 0.774 ± 0.007
    │
    ├── Adversarial Attacks (noise, ε=0.3)
    │     Unconstrained: all 78 features
    │     Constrained: only 57 controllable features
    │
    └── Defenses
          Adversarial training (61% recovery)
          Feature squeezing (0% recovery)
          Constraint-aware detection (100% recovery)
```

## Key Findings

### 1. Feature Constraints Reduce Attack Success by 35%

| Attack Type | XGBoost F1 | Random Forest F1 |
|---|---|---|
| No attack (baseline) | 0.823 | 0.778 |
| Unconstrained (all features) | 0.086 (-74pp) | 0.153 (-63pp) |
| **Constrained (57 features only)** | **0.213 (-61pp)** | **0.217 (-56pp)** |
| **ASR reduction from constraints** | **35%** | **5%** |

Restricting to attacker-controllable features reduces XGBoost attack success rate by 35%. The model still degrades, but the threat is significantly smaller than unrestricted testing suggests.

### 2. Adversarial Training Works, Feature Squeezing Doesn't

| Defense | XGBoost Recovery | RF Recovery |
|---|---|---|
| Adversarial Training | **61%** | 37% |
| Feature Squeezing | 0% | 1% |
| Constraint-Aware Detection | **100%** | **100%** |

Feature squeezing (rounding features to reduce perturbation space) is completely ineffective on tabular data. Adversarial training recovers 37-61% of lost F1. But the winner is architectural.

### 3. The Best Defense Is Architectural, Not Learned

**Constraint-aware detection** monitors the 14 defender-observable features for impossible changes. If TCP flags change in a pattern that contradicts OS behavior, the traffic is adversarial or corrupted. This achieves **100% detection** of noise-based attacks — not because the model learned to detect them, but because the architecture makes them visible.

This is the core insight: **security architecture (which features to monitor) outperforms learned defenses (how to train the model).**

## The Controllability Principle

This finding led to what I now call **adversarial control analysis** — classifying inputs by who controls them. It's since been validated across three more domains:

| Domain | Project | Attacker-Controlled | Defender-Observable |
|---|---|---|---|
| Network IDS | FP-01 (this project) | 57 features | 14 features |
| CVE prediction | FP-05 | 13 features | 11 features |
| AI agent red-teaming | FP-02 | 5 input types | Varies |
| Crypto migration | FP-03 | 20% developer | 70% library |

The principle transfers because security is fundamentally about control: who controls the input determines what defense is possible.

## What I Learned

**Test the right threat model.** Standard adversarial ML benchmarks (all features perturbable) overstate vulnerability. Constrained testing (only attacker-controlled features) gives actionable results.

**Architecture beats learning.** Adversarial training is popular but recovers at most 61%. Monitoring uncontrollable features detects 100%. The architectural defense is also cheaper, faster, and doesn't require retraining.

**This was the project that changed my methodology.** Feature controllability started as a practical constraint (network attackers can't forge TCP flags) and became a general security architecture principle.

## What's Next

The framework is open source. The controllability methodology has been validated on 4 domains. Next: publish the methodology as a standalone blog post and submit to BSides.

---

*Rex Coleman is an MS Computer Science student (Machine Learning) at Georgia Tech, building at the intersection of AI security and ML systems engineering. Previously 15 years in cybersecurity (FireEye/Mandiant — analytics, enterprise sales, cross-functional leadership). CFA charterholder. Creator of [govML](https://github.com/rexcoleman/govML).*
