# Adversarial ML on Network IDS — Claude Code Context

## Project Purpose

Build baseline ML intrusion detectors on CICIDS2017, systematically attack them with adversarial evasion constrained to attacker-controllable features, measure evasion rates, and evaluate defenses including adaptive attackers.

- **Context:** FP-01 (Frontier Pipeline) / PUB-012 (Publishable Artifacts)
- **Profile:** supervised (from ml-governance-templates / govML)
- **Python:** 3.10 | **Env:** adversarial-ids

## Authority Hierarchy

When requirements conflict, higher tiers win. Always.

| Tier | Source | Path |
|------|--------|------|
| 1 (highest) | Execution Plan | `EXECUTION_PLAN.md` |
| 2 | Adversarial Evaluation | `docs/ADVERSARIAL_EVALUATION.md` |
| 3 | Experiment Contract | `docs/EXPERIMENT_CONTRACT.md` |
| Contracts | Governance docs | `docs/*.md` |

## Current Phase

**Phase:** 0 — Environment & Data

### Phase Commands

```bash
# Phase 0 gate
bash scripts/verify_env.sh
python scripts/check_data_ready.py

# Phase 1 gate
python -m pytest tests/test_leakage.py tests/test_determinism.py -v

# Phase 2 gate
python scripts/run_baselines.py --seeds 42,123,456,789,1024
python scripts/check_baseline_threshold.py

# Phase 3 gate
python scripts/run_adversarial.py --attack fgsm,pgd,cw --constrained
python scripts/check_evasion_findings.py

# Phase 4 gate
python scripts/run_defenses.py --defense adv_training,ensemble,feature_squeezing
python scripts/run_adversarial.py --attack fgsm,pgd,cw --mode adaptive --target defended

# Phase 5 gate
python scripts/verify_manifests.py
```

## Project-Specific Rules

1. **Seed protocol:** Always use seeds [42, 123, 456, 789, 1024]. Report median and IQR, not mean.
2. **Attacker constraints:** Adversarial perturbations MUST distinguish between attacker-controllable and defender-observable features. See TRADEOFF_LOG.md TD-XX for feature split.
3. **No security by obscurity:** Every defense MUST be re-evaluated with an adaptive attacker that knows the defense mechanism.
4. **Leakage barrier:** Adversarial examples generated from train/val ONLY. Test set reserved for final evaluation.
5. **Metric consistency:** Use "detection rate" (not recall/TPR), "evasion rate" (not 1-detection), "adversarial evasion" (not adversarial attack).

## Key Files

| File | Purpose |
|------|---------|
| `EXECUTION_PLAN.md` | Phased delivery plan with gates |
| `TRADEOFF_LOG.md` | Architectural decisions (D4 evidence) |
| `FINDINGS.md` | Blog-ready summary (fill after Phase 3) |
| `project.yaml` | Drives govML generators (sweep, manifest, gates) |
| `config/base.yaml` | Shared experiment config |
| `scripts/run_baselines.py` | Phase 2 experiment runner |
| `scripts/run_adversarial.py` | Phase 3 attack runner |
| `scripts/run_defenses.py` | Phase 4 defense runner |

## Data

- **CICIDS2017** — 2.8M network flows, 15 attack classes + benign
- Located: `data/raw/` (not committed)
- Splits: 60/20/20 stratified by attack class, seed 42
- Preprocessing: `src/preprocessing.py`

## What NOT To Do

- Do not interpret findings or write blog prose — human writes those
- Do not skip the adaptive attacker step — it's the credibility differentiator
- Do not use test set for anything except final evaluation
- Do not add unnecessary abstractions — this ships in 4 weeks
