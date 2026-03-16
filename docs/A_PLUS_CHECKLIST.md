# A+ COMPLIANCE CHECKLIST

<!-- version: 1.0 -->
<!-- created: 2026-03-16 -->
<!-- project: FP-01 Adversarial ML on Network Intrusion Detection -->
<!-- tests: 70 pass, 2 skip -->

> **Usage:** Check items as you complete them. Each item references the quality gate that requires it.

---

## 1) ML Rigor

| Done | Item | Gate Ref | Notes |
|------|------|----------|-------|
| [x] | Learning curves plotted (train vs val over epochs/iterations) | Gate 3 | `figures/learning_curves.png` via `scripts/run_learning_curves.py` |
| [x] | Model complexity analysis (bias-variance tradeoff documented) | Gate 3 | `scripts/run_complexity_curves.py` |
| [x] | Multi-seed validation (>=3 seeds, mean +/- std reported) | Gate 3 | 3+ seeds, documented in FINDINGS.md |
| [ ] | Ablation study (component contribution isolated) | Gate 4 | Not yet implemented |
| [x] | Hyperparameter sensitivity analysis documented | Gate 3 | Via complexity curve sweeps |
| [x] | Baseline comparison (trivial/random baseline included) | Gate 3 | `scripts/run_sanity_baselines.py` |
| [x] | Sanity checks pass (model beats random, loss decreases) | Gate 1 | Sanity tests pass |
| [x] | Leakage tripwires pass (LT-1 through LT-5) | Gate 1 | Leakage tests in test suite |
| [x] | Cross-validation or held-out validation used correctly | Gate 1 | Stratified split with multi-seed |
| [ ] | Statistical significance tested where applicable | Gate 4 | Not yet implemented |
| [x] | Feature importance / interpretability analysis | Gate 4 | Per-class heatmap: `figures/per_class_heatmap.png` |
| [x] | Failure mode analysis (where does the model break?) | Gate 4 | Adversarial budget curves show degradation thresholds |

---

## 2) Cybersecurity Rigor

| Done | Item | Gate Ref | Notes |
|------|------|----------|-------|
| [x] | Threat model defined (STRIDE, attack surface, trust boundaries) | Gate 2 | `blog/adversarial_ids_threat_model.md` |
| [x] | Adversarial Capability Assessment (ACA) documented | Gate 2 | `docs/ADVERSARIAL_EVALUATION.md` |
| [x] | Adaptive adversary tested (attacker adapts to defense) | Gate 4 | Budget sweep: constrained + unconstrained adversary |
| [x] | Evasion resistance measured (adversarial examples) | Gate 4 | `outputs/adversarial/` — budget curves per model |
| [ ] | Data poisoning resilience evaluated | Gate 4 | Not in scope |
| [ ] | Model extraction resistance assessed | Gate 4 | Not in scope |
| [ ] | Temporal drift analysis (model degrades over time?) | Gate 4 | Not yet implemented |
| [x] | Real-world attack scenario validation | Gate 4 | NSL-KDD dataset with real attack categories |
| [x] | Defense-in-depth layers documented | Gate 2 | `figures/defense_comparison.png`, `outputs/defense/` |
| [x] | False positive / false negative tradeoff analyzed | Gate 3 | `figures/algorithm_comparison.png` |

---

## 3) Execution

| Done | Item | Gate Ref | Notes |
|------|------|----------|-------|
| [x] | All tests pass (`pytest tests/ -v`) | Gate 1 | 70 pass, 2 skip |
| [x] | Leakage tests pass (`pytest tests/ -m leakage -v`) | Gate 1 | Pass |
| [x] | Determinism tests pass (`pytest tests/ -m determinism -v`) | Gate 1 | `test_reproducibility.py` |
| [x] | All figures generated from code (no manual screenshots) | Gate 5 | `scripts/make_report_figures.py` |
| [x] | Figure provenance tracked (script + seed + commit hash) | Gate 5 | `outputs/provenance/` (config, git_commit_sha, versions) |
| [x] | `reproduce.sh` runs end-to-end without manual steps | Gate 5 | `reproduce.sh` at repo root |
| [x] | Environment locked (`environment.yml` or `requirements.txt`) | Gate 0 | `environment.yml` |
| [ ] | Data checksums verified (SHA-256 in manifest) | Gate 0 | Not yet implemented |
| [ ] | Artifact manifest complete and hashes match | Gate 5 | No manifest spec yet |
| [ ] | All phase gates pass (`bash scripts/check_all_gates.sh`) | Gate 5 | No gate script yet |
| [ ] | CI pipeline green (if applicable) | Gate 5 | No CI configured |
| [x] | Code review completed (self or peer) | Gate 5 | Self-reviewed |

---

## 4) Publication

| Done | Item | Gate Ref | Notes |
|------|------|----------|-------|
| [x] | Blog post drafted (builder-in-public narrative) | Gate 6 | `blog/draft.md` |
| [x] | Key findings distilled into 3-5 bullet points | Gate 6 | In FINDINGS.md |
| [x] | Figures publication-ready (labels, legends, DPI >= 300) | Gate 6 | 5 figures in `figures/` |
| [x] | Venue identified (conference, journal, or workshop) | Gate 7 | `blog/conference_abstract.md` |
| [ ] | External review solicited (>=1 reviewer outside project) | Gate 7 | Pending |
| [x] | Code repository public and documented | Gate 6 | GitHub public repo |
| [x] | README includes reproduction instructions | Gate 6 | README.md present |
| [x] | License and attribution complete | Gate 6 | LICENSE file present |
| [x] | FINDINGS.md written with structured conclusions | Gate 5 | 13 [DEMONSTRATED] tags |

---

## Summary

| Section | Complete | Total | Percentage |
|---------|----------|-------|------------|
| ML Rigor | 10 | 12 | 83% |
| Cybersecurity Rigor | 7 | 10 | 70% |
| Execution | 8 | 12 | 67% |
| Publication | 8 | 9 | 89% |
| **Overall** | **33** | **43** | **77%** |

> **A+ threshold:** All Gate 0-5 items checked. Gate 6-7 items required for publication track only.
>
> **Remaining gaps:** Ablation study (Gate 4), statistical tests (Gate 4), data checksums (Gate 0), artifact manifest (Gate 5), gate script (Gate 5), CI (Gate 5), external review (Gate 7), and 3 out-of-scope cybersecurity items.
