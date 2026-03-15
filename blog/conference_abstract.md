# Conference Abstract — BSides / DEF CON AI Village

## Title
Your IDS Adversarial Defense Is Testing the Wrong Threat Model: Feature Controllability Changes Everything

## Abstract (250 words)

Standard adversarial ML evaluations on intrusion detection systems treat all features as equally perturbable — but network attackers cannot control TCP flags set by the OS stack or destination ports determined by the protocol. We present an adversarial ML pipeline on CICIDS2017 (2.83M flows, 15 attack classes) that introduces **feature controllability analysis**: splitting 78 network features into 57 attacker-controllable and 14 defender-observable.

When attacks are restricted to only attacker-controllable features, XGBoost attack success drops by 35% compared to unconstrained testing. This means standard adversarial benchmarks significantly overstate IDS vulnerability.

We evaluate three defenses: adversarial training (61% F1 recovery), feature squeezing (0% recovery — completely ineffective on tabular data), and constraint-aware detection (100% detection). The most effective defense is architectural, not learned: monitoring defender-observable features for impossible changes catches all noise-based adversarial traffic without retraining the model.

This feature controllability methodology has since been validated across three additional security domains — vulnerability prediction, AI agent red-teaming, and post-quantum cryptography migration — establishing it as a general security architecture principle. The core insight: **classifying inputs by who controls them determines what defense is possible.**

All code, attack scenarios, and defense implementations are open source.

## Keywords
adversarial ML, intrusion detection, feature controllability, CICIDS2017, defense-in-depth, security architecture

## Bio
Rex Coleman is an MS Computer Science student (Machine Learning) at Georgia Tech, building at the intersection of AI security and ML systems engineering. Previously 15 years in cybersecurity (FireEye/Mandiant — analytics, enterprise sales, cross-functional leadership). CFA charterholder. Creator of govML (open-source ML governance framework).
