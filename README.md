# Adversarial ML on Network Intrusion Detection

Can ML-based intrusion detection systems survive adversarial evasion by a realistic attacker?

This project builds baseline ML detectors on the CICIDS2017 dataset, then systematically attacks them using adversarial perturbations constrained to features an attacker can actually control. We measure evasion rates, quantify the robustness/accuracy tradeoff of defenses, and evaluate adaptive attackers.

## Quick Start

```bash
# Environment
conda env create -f environment.yml
conda activate adversarial-ids
bash scripts/verify_env.sh

# Data
bash scripts/download_data.sh

# Baselines
python scripts/run_baselines.py --seeds 42,123,456,789,1024

# Adversarial attacks
python scripts/run_adversarial.py --attack fgsm,pgd,cw --constrained

# Defenses
python scripts/run_defenses.py --defense adv_training,ensemble,feature_squeezing
```

## Project Structure

```
adversarial-ids-ml/
├── config/                  # Experiment configs
├── data/
│   ├── raw/                 # CICIDS2017 CSVs (not committed)
│   ├── processed/           # Cleaned, encoded features
│   └── splits/              # Fixed train/val/test splits
├── docs/                    # govML governance templates
│   ├── ADVERSARIAL_EVALUATION.md
│   ├── DATA_CONTRACT.md
│   ├── ENVIRONMENT_CONTRACT.md
│   ├── EXPERIMENT_CONTRACT.md
│   └── ...
├── outputs/
│   ├── figures/             # Budget curves, confusion matrices
│   ├── tables/              # Per-class metrics
│   └── models/              # Saved model artifacts
├── requirements/            # Dataset specs, constraints
├── scripts/                 # Executable pipeline
├── src/                     # Source modules
├── tests/                   # Leakage, determinism, adversarial budget tests
├── EXECUTION_PLAN.md        # Phased delivery plan
├── FINDINGS.md              # Blog-ready summary (post-experiment)
└── TRADEOFF_LOG.md          # Architectural decisions (D4 evidence)
```

## Governance

This project uses [govML](https://github.com/rexdouglass/ml-governance-templates) for reproducibility and quality governance. All experiments follow the Experiment Contract (5-seed protocol, baseline matching). All adversarial evaluations follow the Adversarial Evaluation template (constrained perturbations, adaptive attackers, transferability).

## License

MIT

## Author

Rex Coleman — [architect who ships]
