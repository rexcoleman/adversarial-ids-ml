# REPRODUCIBILITY SPECIFICATION

<!-- version: 1.0 -->
<!-- created: 2026-02-20 -->
<!-- last_validated_against: CS_7641_Machine_Learning_SL_Report -->

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
- See [ENVIRONMENT_CONTRACT](../core/ENVIRONMENT_CONTRACT.tmpl.md) §5 for environment setup commands and §7 for reproduction commands
- See [DATA_CONTRACT](../core/DATA_CONTRACT.tmpl.md) §2 for canonical data paths and §7 for provenance artifacts
- See [SCRIPT_ENTRYPOINTS_SPEC](../core/SCRIPT_ENTRYPOINTS_SPEC.tmpl.md) §6 for minimal reproduction sequence
- See [ARTIFACT_MANIFEST_SPEC](../core/ARTIFACT_MANIFEST_SPEC.tmpl.md) §5 for hashing and integrity verification

**Downstream (depends on this contract):**
- See [PRE_SUBMISSION_CHECKLIST](PRE_SUBMISSION_CHECKLIST.tmpl.md) §4 for reproducibility verification checks

## Customization Guide

Fill in all `{{PLACEHOLDER}}` values before use. Delete this section when customization is complete.

| Placeholder | Value |
|-------------|-------|
| Project name | Adversarial ML on Network Intrusion Detection |
| Report link | *(generated from outputs/ after full reproduction)* |
| Repository URL | https://github.com/rexcoleman/adversarial-ids-ml |
| Final commit SHA | `2dc19126293f67827ff9d02fcc3d2894de908984` |
| Platform OS | Ubuntu 20.04 (Linux 5.15.0-1089-azure) |
| Platform CPU | Azure B2ms — 2 vCPUs |
| Platform RAM | 8 GiB |
| Platform GPU | Not required (CPU-only) |
| Environment manager | conda |
| Environment file | environment.yml |
| Environment name | adversarial-ids |
| Python version | 3.10.13 |
| Default seed | 42 |
| All seeds | [42, 123, 456, 789, 1024] |
| Data source | https://www.unb.ca/cic/datasets/ids-2017.html (registration required) |
| Dataset | CICIDS2017 (2,827,876 flows, 8 CSV files, 78 features, 15 classes) |
| Tier 1 authority | EXECUTION_PLAN.md |
| Tier 2 authority | docs/ADVERSARIAL_EVALUATION.md |
| Tier 3 authority | docs/EXPERIMENT_CONTRACT.md |

---

## 1) Purpose

This document enables anyone to reproduce **all** artifacts for the **Adversarial ML on Network Intrusion Detection** project from a fresh clone. It is the single document a reviewer needs to go from zero to verified outputs.

**Completeness requirement:** Every command needed to reproduce the project MUST appear in this document. If a command is missing, the project is not reproducible.

---

## 2) Report Link & Repository

| Item | Value |
|------|-------|
| **Report (read-only)** | *(generated from `outputs/` after full reproduction)* |
| **Repository** | https://github.com/rexcoleman/adversarial-ids-ml |
| **Branch** | `main` |
| **Final commit SHA** | `2dc19126293f67827ff9d02fcc3d2894de908984` |

**Verification:**

```bash
git clone https://github.com/rexcoleman/adversarial-ids-ml
cd adversarial-ids-ml
git log --oneline -1
# Expected: 2dc1912
```

---

## 3) Hardware Requirements

| Resource | Specification | Notes |
|----------|--------------|-------|
| **OS** | Ubuntu 20.04 (Linux 5.15.0-1089-azure) | *(tested platform)* |
| **CPU** | Azure B2ms — 2 vCPUs (Intel Xeon) | *(minimum for reasonable runtime)* |
| **RAM** | 8 GiB | *(minimum to avoid OOM)* |
| **GPU** | Not required (CPU-only) | *(torch 2.1.2+cpu)* |
| **Disk** | ~2 GB | *(8 CSV files + outputs)* |

**CPU reproducibility rule:** All final report artifacts MUST be reproducible on CPU. GPU may be used for exploration but MUST NOT be required for delivery artifacts.

---

## 4) Environment Setup

```bash
# 1. Create environment
conda env create -f environment.yml
conda activate adversarial-ids

# 2. Verify environment
bash scripts/verify_env.sh
# Expected: exits 0, prints matching versions
```

### Key Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| python | 3.10.13 | Runtime |
| scikit-learn | 1.3.2 | Baseline classifiers (RF, SVM, MLP) |
| xgboost | 2.0.3 | Gradient-boosted tree baseline |
| adversarial-robustness-toolbox | 1.17.1 | Adversarial attack + defense framework |
| torch | 2.1.2+cpu | Neural network backend (CPU-only) |
| numpy | 1.24.3 | Numerical operations |
| pandas | 2.0.3 | Data loading and manipulation |
| matplotlib | 3.8.2 | Visualization |
| seaborn | 0.13.0 | Statistical plots |
| scipy | 1.11.4 | Scientific computing utilities |
| pytest | 7.4.4 | Test suite |

---

## 5) Data Acquisition

### Data Sources

| Dataset | Source | Filename | Destination |
|---------|--------|----------|-------------|
| CICIDS2017 (Monday) | UNB CIC | `Monday-WorkingHours.pcap_ISCX.csv` | `data/raw/` |
| CICIDS2017 (Tuesday) | UNB CIC | `Tuesday-WorkingHours.pcap_ISCX.csv` | `data/raw/` |
| CICIDS2017 (Wed) | UNB CIC | `Wednesday-workingHours.pcap_ISCX.csv` | `data/raw/` |
| CICIDS2017 (Thu AM) | UNB CIC | `Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv` | `data/raw/` |
| CICIDS2017 (Thu PM) | UNB CIC | `Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv` | `data/raw/` |
| CICIDS2017 (Fri AM) | UNB CIC | `Friday-WorkingHours-Morning.pcap_ISCX.csv` | `data/raw/` |
| CICIDS2017 (Fri PM PortScan) | UNB CIC | `Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv` | `data/raw/` |
| CICIDS2017 (Fri PM DDoS) | UNB CIC | `Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv` | `data/raw/` |

### Placement Instructions

```bash
# 1. Register at https://www.unb.ca/cic/datasets/ids-2017.html
# 2. Download the "MachineLearningCVE" ZIP archive (8 CSV files)
# 3. Extract all 8 CSV files into data/raw/
data/raw/Monday-WorkingHours.pcap_ISCX.csv
data/raw/Tuesday-WorkingHours.pcap_ISCX.csv
data/raw/Wednesday-workingHours.pcap_ISCX.csv
data/raw/Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv
data/raw/Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv
data/raw/Friday-WorkingHours-Morning.pcap_ISCX.csv
data/raw/Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv
data/raw/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv
```

### Verification

```bash
python scripts/check_data_ready.py
# Expected: exits 0, all files present, SHA-256 hashes match
```

---

## 6) Random Seeds

| Seed | Purpose |
|------|---------|
| `42` | Default seed for all stochastic operations |
| `[42, 123, 456, 789, 1024]` | Stability seeds for multi-seed experiments |

All scripts accept `--seed` flag. The default seed controls: data splits, cross-validation fold assignment, model initialization, and NumPy/PyTorch random state.

---

## 7) Reproduction Sequence

All commands run from repository root. Execute in order.

### Phase 0: Environment & Data Verification

```bash
# Verify environment
bash scripts/verify_env.sh

# Verify data
python scripts/check_data_ready.py

# Run leakage tripwires
python scripts/check_leakage.py
```

### Phase 1: EDA & Hypotheses

```bash
python src/eda.py --seed 42
# Produces: outputs/eda/eda_summary.json, outputs/eda/*.png
```

### Phase 2a: Baseline Classifiers

```bash
python src/train_baselines.py --seed 42
# Trains RF, XGBoost, MLP, SVM on clean data; produces accuracy/F1 baselines
```

### Phase 2b: Unconstrained Adversarial Attacks

```bash
python src/adversarial_attacks.py --seed 42
# Applies FGSM, PGD, C&W, ZOO on baseline models (all features perturbed)
```

### Phase 2c: Constrained Adversarial Attacks

```bash
python src/adversarial_attacks.py --seed 42 --constrained
# Restricts perturbations to controllable features only (57 of 78)
```

### Phase 2d: Adversarial Defenses

```bash
python src/defenses.py --seed 42
# Evaluates adversarial training, feature squeezing, input preprocessing
```

*(For multi-seed stability runs, repeat each phase with seeds [42, 123, 456, 789, 1024].)*

### Final: Evaluation & Artifacts

```bash
# Verify artifact integrity
python scripts/check_data_ready.py
# Expected: exits 0, all hashes match
```

---

## 8) EDA Summaries

### CICIDS2017 (all 8 CSV files combined)

```
Shape: 2,827,876 rows x 79 columns (78 features + 1 label)
Target: Label (categorical, 15 classes)
Features: 78 numeric (57 controllable, 14 observable, 7 uncategorized)
Missing values: 1,358 (Flow Bytes/s only)
Infinity values: 4,376 (Flow Bytes/s: 1,509; Flow Packets/s: 2,867)
Zero-variance features: 8 (Bwd PSH/URG Flags, all 6 Bulk Rate features)
Highly correlated pairs (|r| > 0.95): 50
```

**Class Distribution:**

| Class | Count | Fraction |
|-------|------:|---------:|
| BENIGN | 2,271,320 | 80.32% |
| DoS Hulk | 230,124 | 8.14% |
| PortScan | 158,804 | 5.62% |
| DDoS | 128,025 | 4.53% |
| DoS GoldenEye | 10,293 | 0.36% |
| FTP-Patator | 7,935 | 0.28% |
| SSH-Patator | 5,897 | 0.21% |
| DoS slowloris | 5,796 | 0.20% |
| DoS Slowhttptest | 5,499 | 0.19% |
| Bot | 1,956 | 0.07% |
| Web Attack - Brute Force | 1,507 | 0.05% |
| Web Attack - XSS | 652 | 0.02% |
| Infiltration | 36 | <0.01% |
| Web Attack - SQL Injection | 21 | <0.01% |
| Heartbleed | 11 | <0.01% |

**Imbalance ratio:** 206,484:1 (BENIGN vs Heartbleed)

---

## 9) Expected Outputs

After running the full reproduction sequence, the following directory structure is produced:

```
outputs/
├── eda/                           # EDA artifacts
│   ├── eda_summary.json           # Full EDA statistics (JSON)
│   ├── class_distribution.png     # Class imbalance visualization
│   ├── feature_correlations.png   # Correlation heatmap
│   └── controllable_vs_observable.png  # Feature controllability chart
├── provenance/                    # Provenance artifacts
│   ├── versions.txt               # Package versions snapshot
│   ├── run_log.json               # Execution log
│   └── git_commit_sha.txt         # Commit SHA at run time
├── baselines/                     # Phase 2a baseline results
├── attacks/                       # Phase 2b-2c adversarial attack results
├── defenses/                      # Phase 2d defense evaluation results
├── figures/                       # Report figures
└── tables/                        # Report tables
```

### Verification

```bash
# Verify data integrity
python scripts/check_data_ready.py
# Expected: exits 0, all 8 CSV files present, SHA-256 hashes match data/checksums.sha256

# Run test suite
python -m pytest tests/ -v
# Expected: all tests pass
```

---

## 10) Determinism Guarantee

Running the full reproduction sequence with the same seed, data, and environment MUST produce byte-identical outputs (excluding timestamps in logs). If outputs differ, the determinism contract (ENVIRONMENT_CONTRACT §8) has been violated.

**Quick verification:** Compare `artifact_manifest.json` hashes between two independent runs with the same seed.

---

## 11) Change Control Triggers

The following changes require a `CONTRACT_CHANGE` commit and an update to this document:

- Environment file or Python version
- Data acquisition procedure or file paths
- Reproduction sequence (commands, ordering, flags)
- Random seeds
- Expected output structure
- Hardware requirements
