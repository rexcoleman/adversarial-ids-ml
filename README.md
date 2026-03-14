# Adversarial ML on Network Intrusion Detection

**Can ML-based intrusion detection systems survive adversarial evasion by a realistic attacker?**

Most adversarial ML research on IDS perturbs all features equally. Real attackers can't forge TCP flags or control destination ports. This project quantifies how **feature controllability constraints** change everything about adversarial robustness.

## Key Results

| Metric | XGBoost | Random Forest |
|--------|---------|---------------|
| Clean Macro-F1 (5-seed mean) | 0.895 ± 0.013 | 0.853 ± 0.005 |
| Unconstrained Attack F1 (e=0.3) | 0.086 (-74pp) | 0.153 (-63pp) |
| Constrained Attack F1 (e=0.3) | 0.213 (-61pp) | 0.217 (-56pp) |
| ASR Reduction (constrained vs unconstrained) | **35%** | 5% |

### Defense Effectiveness

| Defense | XGBoost Recovery | RF Recovery |
|---------|-----------------|-------------|
| Adversarial Training | 61% | 37% |
| Feature Squeezing | 0% | 1% |
| Constraint-Aware Detection | **100%** | **100%** |

**Core insight:** The most effective defense is architectural (monitoring the 14 defender-observable features for impossible changes), not learned (adversarial training).

## Architecture

```
                    CICIDS2017 (2.83M flows, 78 features)
                                |
                    Preprocessing + Feature Split
                       /                    \
            57 Attacker-                14 Defender-
            Controllable                Observable Only
           (packet timing,             (TCP flags,
            payload size)               Dest Port)
                |                           |
        Constrained                 Constraint-Aware
        Attacks (e-ball)            Detection (monitor
                |                    for impossible
        Baseline Models              changes)
        (RF, XGBoost, MLP)              |
                |                   100% detection
        Adversarial Training         on perturbed
        (61% F1 recovery)           observable features
```

## Quick Start

```bash
# 1. Environment setup
conda env create -f environment.yml
conda activate adversarial-ids
bash scripts/verify_env.sh

# 2. Data (manual download required — registration at unb.ca/cic/datasets/ids-2017.html)
# Extract CSVs to data/raw/MachineLearningCVE/
python scripts/check_data_ready.py

# 3. Run full pipeline
python src/eda.py                                          # EDA + feature analysis
python src/train_baselines.py --seeds 42 123 456 789 1024  # Baseline classifiers
python src/adversarial_attacks.py --attacks noise zoo       # Adversarial attacks
python src/defenses.py                                      # Defense evaluation
```

## Project Structure

```
adversarial-ids-ml/
+-- src/
|   +-- preprocessing.py       # Data pipeline + feature controllability split
|   +-- eda.py                 # Exploratory data analysis
|   +-- train_baselines.py     # RF, XGBoost, MLP training
|   +-- adversarial_attacks.py # Unconstrained + constrained attacks
|   +-- defenses.py            # Adversarial training, squeezing, constraint-aware
+-- data/
|   +-- raw/MachineLearningCVE/  # CICIDS2017 CSVs (not committed)
|   +-- splits/                  # Split metadata
|   +-- checksums.sha256         # Data integrity verification
+-- models/                    # Trained model artifacts (.pkl)
+-- outputs/
|   +-- eda/                   # Feature correlations, class distribution, summary
|   +-- baselines/             # Per-seed training results + confusion matrices
|   +-- adversarial/           # Budget curves, unconstrained/constrained results
|   +-- defense/               # Defense comparison + recovery plots
|   +-- provenance/            # versions.txt, git SHA, run log
+-- docs/                      # govML governance templates (16 active)
+-- blog/                      # Publication drafts
+-- scripts/                   # Utility scripts (verify_env, check_data_ready)
+-- FINDINGS.md                # Publication-ready results summary
+-- TRADEOFF_LOG.md            # Architectural decisions
```

## Hypotheses

All hypotheses pre-registered before experiments (see `docs/HYPOTHESIS_CONTRACT.md`):

| ID | Prediction | Verdict |
|----|-----------|---------|
| H-1 | Unconstrained attacks degrade F1 >= 30pp | **Confirmed** (74pp XGB, 63pp RF) |
| H-2 | Constraints reduce ASR >= 40% | **Partially Confirmed** (35% XGB, 5% RF) |
| H-3 | Adversarial training > preprocessing defense | **Confirmed** (61% vs 0% recovery) |
| H-4 | Architectural > learned defense | **Partially Confirmed** (100% detection, but see limitations) |

## Limitations

1. **Noise baseline only** -- sklearn models lack gradients, so FGSM/PGD don't apply. ZOO/HopSkipJump available but slow.
2. **Single primary seed** -- Full 5-seed stability analysis in progress.
3. **10% sample** -- Trained on 283K rows (10% of 2.83M) for speed.
4. **Adaptive attacker gap** -- Constraint-aware detection achieves 100% on noise (which perturbs observable features), but a constrained attacker who only perturbs controllable features would evade it. The constraint IS the defense.

## Governance

Built with [govML](https://github.com/rexcoleman/ml-governance-templates) -- 16 active templates covering data contracts, experiment protocols, hypothesis pre-registration, adversarial evaluation, and reproducibility specs.

## Publication

- Blog post: [Your IDS Adversarial Defense is Probably Testing the Wrong Threat Model](blog/adversarial_ids_threat_model.md)
- Talk target: BSides / DEF CON AI Village
- Full findings: [FINDINGS.md](FINDINGS.md)

## License

MIT

## Author

Rex Coleman
