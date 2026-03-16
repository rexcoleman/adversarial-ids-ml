# SCRIPT ENTRYPOINTS SPECIFICATION

<!-- version: 1.0 -->
<!-- created: 2026-03-16 -->

## 1) Purpose

Locks the CLI interface for all scripts in `scripts/`. No script may change its flags or I/O contract without a `CONTRACT_CHANGE` commit.

## 2) Script Inventory

### Data & Environment

| Script | Description | Key Flags | Inputs | Outputs |
|--------|-------------|-----------|--------|---------|
| `scripts/download_data.sh` | Download CICIDS2017 CSVs | None | Network access | `data/raw/*.pcap_ISCX.csv` |
| `scripts/check_data_ready.py` | Validate data presence and splits | None | `data/raw/` | Exit code 0/1 |
| `scripts/verify_env.sh` | Check Python + library versions | None | Environment | Exit code 0/1, stdout |

### Training & Evaluation

| Script | Description | Key Flags | Inputs | Outputs |
|--------|-------------|-----------|--------|---------|
| `scripts/run_sanity_baselines.py` | Train RF/XGB/MLP baselines | `--seed`, `--sample-frac` | `data/raw/` | `outputs/baselines/`, `models/` |
| `scripts/train_expanded_models.py` | Multi-seed expanded training | `--seeds` | `data/raw/` | `outputs/baselines/`, `models/` |

### Diagnostics

| Script | Description | Key Flags | Inputs | Outputs |
|--------|-------------|-----------|--------|---------|
| `scripts/run_learning_curves.py` | Generate learning curves | `--seed` | `data/raw/` | `outputs/diagnostics/` |
| `scripts/run_complexity_curves.py` | Generate complexity curves | `--seed` | `data/raw/` | `outputs/diagnostics/` |

### Figures

| Script | Description | Key Flags | Inputs | Outputs |
|--------|-------------|-----------|--------|---------|
| `scripts/make_report_figures.py` | Generate all report figures | None | `outputs/` JSON files | `outputs/figures/`, `outputs/tables/` |

## 3) Common Conventions

- All scripts set `random_state` / `np.random.seed` from `--seed` (default: 42)
- All scripts write resolved config to their output directory
- Exit code 0 = success, 1 = failure
- Scripts MUST NOT read from `data/raw/` and write to `models/` in the same call without going through `src/preprocessing.py`

## 4) Change Control

Adding, removing, or renaming a CLI flag requires a `CONTRACT_CHANGE` commit.
