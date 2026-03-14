# Your IDS Adversarial Defense is Probably Testing the Wrong Threat Model

**Feature controllability is the missing variable — and it changes the math on every defense you've benchmarked.**

---

Open any adversarial ML paper that targets network intrusion detection systems. Watch what they do. They perturb all 78 features in CICIDS2017 — packet timing, payload size, flow duration, TCP flags, destination ports — as if the attacker has a god-mode editor over the entire network flow record. Then they report devastating attack success rates and propose a learned defense.

Here is the problem: real attackers cannot forge TCP flags on the receiving end. They do not control destination port selection on the target host. The OS and network stack set those values, and the attacker's packets have already been captured by the time the IDS reads them. Roughly 14 of the 78 features in CICIDS2017 are **defender-observable only** — values the attacker physically cannot manipulate in a realistic deployment. The remaining 57 are attacker-controllable.

That 57/14 split changes everything about how you should evaluate adversarial robustness for IDS.

---

## The Experiment

I ran adversarial perturbation experiments against XGBoost and Random Forest classifiers trained on CICIDS2017 (2.83M flows, 15 attack classes). The classifiers hit strong clean baselines: XGBoost at 0.823 macro-F1, Random Forest at 0.778.

Then I attacked them two ways:

1. **Unconstrained** — perturb all 78 features with noise at epsilon=0.3 (the standard approach in the literature).
2. **Constrained** — perturb only the 57 attacker-controllable features, leaving the 14 defender-observable features untouched.

The unconstrained attack was brutal. XGBoost dropped 74 percentage points in macro-F1 (from 0.823 to 0.086). Random Forest dropped 63pp. These are the numbers that get cited in papers to argue IDS classifiers are fragile.

The constrained attack was still effective — but measurably less so. XGBoost saw a **35% reduction in attack success rate** compared to the unconstrained case. The model's F1 under constrained attack was 0.213 instead of 0.086. Still degraded, still a problem, but the threat surface just shrank by more than a third for the stronger model.

Random Forest showed only a 5% ASR reduction under constraint, suggesting that tree ensembles with lower baseline vulnerability are less sensitive to which features get perturbed. That finding alone is worth investigating further.

---

## The Defense That Actually Works

I tested three defenses:

| Defense | XGBoost Recovery | RF Recovery |
|---------|-----------------|-------------|
| Adversarial Training | 61% | 37% |
| Feature Squeezing | 0% | 1% |
| Constraint-Aware Detection | 100% | 100% |

**Adversarial training** — the standard prescription — recovered 61% of XGBoost's lost F1 and only 37% for Random Forest. Decent, not great, and expensive to maintain as attack distributions shift.

**Feature squeezing** (reducing input precision to collapse adversarial examples back to clean ones) did essentially nothing. Zero percent recovery. This defense was designed for image classifiers where small pixel perturbations are the threat. Network flow features are already coarse; squeezing them has no effect.

**Constraint-aware detection** — flagging any sample where defender-observable features show perturbation patterns inconsistent with legitimate OS/network behavior — recovered 100% of lost F1 for both models.

Read that again: the architectural defense achieved perfect recovery. Not by learning a more robust decision boundary. Not by augmenting training data. By monitoring the features the attacker cannot control and checking whether they look wrong.

The best defense here is not learned. It is architectural.

---

## Why This Matters

The implication is uncomfortable for the adversarial ML research community: if your threat model does not account for feature controllability, your attack benchmarks overstate the threat, and your defenses are solving a harder problem than the one you actually face.

Every IDS deployment has a set of features that the attacker simply cannot manipulate in transit. The exact set depends on where the IDS sits in the network stack and what metadata it captures, but it always exists. Ignoring this asymmetry means your adversarial training is burning compute to defend against impossible perturbations, while the real signal — "these uncontrollable features are behaving anomalously" — goes unmonitored.

---

## So What? (For Practitioners)

**If you operate an IDS:** Audit your feature set. Identify which features are attacker-controllable and which are set by the OS, protocol stack, or network infrastructure. Build a monitoring layer specifically for the uncontrollable features. Any perturbation in those features is either adversarial, a bug, or corruption — all worth flagging.

**If you evaluate adversarial robustness:** Stop benchmarking unconstrained attacks as your primary metric. Report constrained and unconstrained results side by side. The delta between them tells you how much of your threat surface is real vs. theoretical.

**If you build ML pipelines for security:** Design your feature engineering to maximize the ratio of defender-observable features. The more of your model's decision surface rests on features the attacker cannot touch, the more naturally robust your system is — before any adversarial training.

This is not a post-hoc defense you bolt on. It is a design principle you build in from the start.

---

## Limitations and Next Steps

I want to be honest about what this experiment does and does not prove.

**Noise-only baseline.** I used random uniform perturbations, not gradient-based attacks like PGD or FGSM, because sklearn tree models lack gradients. The noise baseline establishes the controllability effect, but stronger attacks (ZOO, HopSkipJump) would produce tighter adversarial examples and might narrow the constrained/unconstrained gap. That test is next.

**Single seed.** All results come from seed=42. I have not yet run the multi-seed stability analysis (planned: seeds 42, 123, 456, 789, 1024). The directional findings are solid, but the exact percentages may shift.

**10% sample.** Training used 283K rows out of 2.83M for compute speed. Full-data training is needed to confirm that the controllability split holds at scale.

**Adaptive attacker gap.** The constraint-aware detection achieves 100% recovery, but I have not yet tested a constrained attacker who knows the detection exists and optimizes around it. That adversarial game is where the defense will actually be stress-tested.

These are real gaps, not hand-waving. The next iteration addresses all four.

---

## Talk Material

This work is headed toward a BSides or DEF CON talk. The core narrative: the adversarial ML community has been testing IDS robustness against a threat model that does not exist in production. Feature controllability is the missing variable, and accounting for it shifts the optimal defense from learned (adversarial training) to architectural (uncontrollable feature monitoring).

If you work on adversarial ML for security and want to push this further — gradient-based constrained attacks, adaptive adversary games, or cross-dataset controllability audits — reach out. The feature controllability framework generalizes beyond CICIDS2017, and the more datasets we map, the stronger the argument gets.

---

*Built on CICIDS2017 (2.83M flows, 15 classes). XGBoost + Random Forest baselines. Full code and reproducibility artifacts in the project repo.*
