# PROVENANCE SPECIFICATION

<!-- version: 1.0 -->
<!-- created: 2026-03-16 -->

## 1) Purpose

Defines the provenance chain for all experiment outputs, ensuring every result can be traced to its exact code version, environment, and configuration.

## 2) Provenance Directory

Location: `outputs/provenance/`

| File | Contents | When Written |
|------|----------|-------------|
| `versions.txt` | Python + all key library versions + platform info | Start of any experiment run |
| `git_commit_sha.txt` | Output of `git rev-parse HEAD`; notes dirty state | Start of any experiment run |
| `run_log.json` | Ordered list of run_ids with exit codes and wall-clock | Updated after each run |
| `config_resolved.yaml` | Global config snapshot for the reproduction sequence | Start of reproduction sequence |

## 3) Per-Run Provenance

Each run directory also contains `config_resolved.yaml` with:
- `run_id`: deterministic ID per ARTIFACT_MANIFEST_SPEC §2
- `git_sha`: commit hash at run time
- `seed`: random seed used
- `timestamp_utc`: ISO 8601 run start time

## 4) Environment Capture

`versions.txt` schema:

```
python: 3.x.x
numpy: x.x.x
pandas: x.x.x
scikit-learn: x.x.x
art: x.x.x
matplotlib: x.x.x
platform: linux-x86_64
```

## 5) Integrity Chain

```
git_commit_sha.txt → code version
versions.txt       → environment version
config_resolved.yaml → parameter version
run_log.json       → execution record
```

All four files together form the minimum provenance needed to reproduce any result.

## 6) Verification

Run `scripts/verify_env.sh` to confirm environment matches `versions.txt`.

## 7) Change Control

Changes to provenance file format or requirements need a `CONTRACT_CHANGE` commit.
