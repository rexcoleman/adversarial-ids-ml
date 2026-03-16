# ARTIFACT MANIFEST SPECIFICATION

<!-- version: 1.0 -->
<!-- created: 2026-03-16 -->

## 1) Run ID Format

```
{model}_{attack}_{seed}
```

**Components:**
- `model`: classifier name — `rf`, `xgboost`, `mlp`
- `attack`: attack type — `noise`, `zoo`, `hopskipjump`, `baseline`, `defense_{name}`
- `seed`: integer seed value from [42, 123, 456, 789, 1024]

**Examples:**
- `rf_noise_42` — Random Forest under noise attack, seed 42
- `xgboost_baseline_123` — XGBoost clean baseline, seed 123
- `mlp_defense_advtrain_42` — MLP adversarial training defense, seed 42

## 2) Per-Run Files

Every run directory MUST contain:

| File | Format | Description |
|------|--------|-------------|
| `metrics.json` | JSON | Attack success rate, F1, accuracy per epsilon |
| `config_resolved.yaml` | YAML | Fully resolved config (model, attack, epsilon, seed, constraint mode) |
| `summary.json` | JSON | Aggregated results, budget usage, wall-clock time |

## 3) Global Provenance

Location: `outputs/provenance/`

| File | Contents |
|------|----------|
| `versions.txt` | Python + sklearn + ART + numpy versions |
| `git_commit_sha.txt` | `git rev-parse HEAD` output |
| `run_log.json` | Ordered list of run_ids with exit codes and wall-clock |
| `config_resolved.yaml` | Global config snapshot |

## 4) Output Directory Structure

```
outputs/
├── baselines/          # Clean model metrics per seed
├── adversarial/        # Attack results (unconstrained + constrained JSON)
├── defense/            # Defense comparison results
├── diagnostics/        # Learning/complexity curves
├── eda/                # EDA artifacts
├── figures/            # Report-ready figures
├── tables/             # Report-ready tables
├── provenance/         # Global provenance files
models/
├── {Model}_seed{seed}.pkl
```

## 5) Integrity Verification

All hashes use SHA-256. Run `python scripts/verify_manifests.py` to validate.

## 6) Change Control

Changes to run_id format, per-run file requirements, or hashing rules require a `CONTRACT_CHANGE` commit.
