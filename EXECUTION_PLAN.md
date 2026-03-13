# FP-01 / PUB-012: Adversarial ML on Network Intrusion Detection

> **Identity:** Architect who ships (DEC-026)
> **Thesis:** ML-based intrusion detection systems are brittle under adversarial evasion — and a practitioner with real attack knowledge can prove it, quantify it, and build defenses.
> **Dual-track:** This project satisfies both FP-01 (Frontier Pipeline) and PUB-012 (Publishable Artifacts Tracker).

---

## Research Questions

| # | Question | Method | Success Criterion |
|---|----------|--------|-------------------|
| RQ-1 | How accurately can supervised + unsupervised ML detect network intrusions on CICIDS2017? | Train baseline classifiers (RF, XGBoost, MLP) + anomaly detectors (Isolation Forest, DBSCAN, Autoencoder) | ≥95% F1 on known attack classes (matches published benchmarks) |
| RQ-2 | Which attack classes are most vulnerable to adversarial evasion? | Generate adversarial traffic using feature-space perturbations guided by attacker domain knowledge | Identify ≥2 attack classes where evasion drops detection below 50% |
| RQ-3 | How do realistic attacker constraints (budget, observability) affect evasion success? | Constrained adversarial generation: limit perturbable features to those an attacker can actually control | Quantify detection rate vs constraint level (budget curves) |
| RQ-4 | Can adversarial training improve robustness without destroying clean accuracy? | Retrain with adversarial examples, measure clean vs adversarial accuracy tradeoff | ≥80% adversarial accuracy with ≤5% clean accuracy drop |

---

## Phase Plan

### Phase 0: Environment & Data (Days 1-3)

**Goal:** Reproducible environment, data downloaded and validated.

| Task | Detail | govML Template | Done |
|------|--------|---------------|------|
| 0.1 | Create `environment.yml` (Python 3.10, scikit-learn, XGBoost, PyTorch, ART) | ENVIRONMENT_CONTRACT | [ ] |
| 0.2 | Download CICIDS2017 dataset from UNB | DATA_CONTRACT | [ ] |
| 0.3 | Compute SHA-256 checksums for raw data files | DATA_CONTRACT §3 | [ ] |
| 0.4 | Write `scripts/verify_env.sh` | ENVIRONMENT_CONTRACT | [ ] |
| 0.5 | Write `scripts/download_data.sh` with checksum verification | DATA_CONTRACT §3 | [ ] |
| 0.6 | Fill ENVIRONMENT_CONTRACT placeholders | — | [ ] |
| 0.7 | Fill DATA_CONTRACT placeholders | — | [ ] |
| 0.8 | Initial commit with governance + environment + data pipeline | — | [ ] |

**Gate:** `verify_env.sh` passes, data checksums match, both contracts filled.

### Phase 1: Data Exploration & Preprocessing (Days 3-5)

**Goal:** Clean dataset with understood class distribution, fixed train/val/test splits.

| Task | Detail | govML Template | Done |
|------|--------|---------------|------|
| 1.1 | EDA: class distribution, feature correlations, missing values | DATA_CONTRACT §4 | [ ] |
| 1.2 | Preprocessing: encoding, scaling, handling class imbalance | DATA_CONTRACT §5 | [ ] |
| 1.3 | Fixed 60/20/20 split, seed 42, stratified by attack class | DATA_CONTRACT §6 | [ ] |
| 1.4 | Write `tests/test_leakage.py` — no train/test contamination | TEST_ARCHITECTURE | [ ] |
| 1.5 | Write `tests/test_determinism.py` — same seed = same split | TEST_ARCHITECTURE | [ ] |
| 1.6 | Identify which features an attacker can realistically control | Domain knowledge (Mandiant experience) | [ ] |
| 1.7 | Document attacker-controllable vs defender-observable feature split | TRADEOFF_LOG.md | [ ] |

**Gate:** Leakage and determinism tests pass. Feature split documented.

### Phase 2: Baseline Detection Models (Days 5-10)

**Goal:** Strong baseline classifiers and anomaly detectors. Reproduce published benchmark performance.

| Task | Detail | govML Template | Done |
|------|--------|---------------|------|
| 2.1 | Train baseline classifiers: Random Forest, XGBoost, MLP | EXPERIMENT_CONTRACT | [ ] |
| 2.2 | Train anomaly detectors: Isolation Forest, DBSCAN, Autoencoder | EXPERIMENT_CONTRACT | [ ] |
| 2.3 | 5-seed evaluation (42, 123, 456, 789, 1024) | EXPERIMENT_CONTRACT §3 | [ ] |
| 2.4 | Per-class metrics: precision, recall, F1, confusion matrices | METRICS_CONTRACT | [ ] |
| 2.5 | Sanity checks: majority-class baseline, random baseline | METRICS_CONTRACT Appendix | [ ] |
| 2.6 | Write `scripts/run_baselines.py` | — | [ ] |
| 2.7 | Fill HYPOTHESIS_CONTRACT (H-1 through H-4 matching RQs) | HYPOTHESIS_CONTRACT | [ ] |
| 2.8 | Fill EXPERIMENT_CONTRACT placeholders | — | [ ] |

**Gate:** Baseline F1 ≥95% on known attacks (matches literature). All seeds produce consistent results (±2% F1).

### Phase 3: Adversarial Evasion (Days 10-18) — Core Contribution

**Goal:** Systematically evade ML-based detection using realistic attacker constraints.

| Task | Detail | govML Template | Done |
|------|--------|---------------|------|
| 3.1 | Implement feature-space adversarial perturbations using IBM ART | ADVERSARIAL_EVALUATION | [ ] |
| 3.2 | Attack methods: FGSM, PGD, C&W (feature-space adapted) | ADVERSARIAL_EVALUATION §2 | [ ] |
| 3.3 | Constrained attacks: only perturb attacker-controllable features | ADVERSARIAL_EVALUATION §3 | [ ] |
| 3.4 | Unconstrained attacks: perturb all features (upper bound on evasion) | ADVERSARIAL_EVALUATION §3 | [ ] |
| 3.5 | Budget curves: evasion rate vs perturbation budget (ε) | FIGURES_TABLES_CONTRACT | [ ] |
| 3.6 | Per-class vulnerability analysis: which attack types are easiest to evade? | METRICS_CONTRACT | [ ] |
| 3.7 | Transferability: do adversarial examples for RF also fool XGBoost? | ADVERSARIAL_EVALUATION §4 | [ ] |
| 3.8 | Write `scripts/run_adversarial.py` | — | [ ] |
| 3.9 | Write `tests/test_adversarial.py` — verify perturbations stay within budget | TEST_ARCHITECTURE | [ ] |

**Gate:** ≥2 attack classes with detection below 50% under constrained evasion. Budget curves generated for all models.

### Phase 4: Adversarial Defense (Days 18-22)

**Goal:** Evaluate defenses and quantify the robustness/accuracy tradeoff.

| Task | Detail | govML Template | Done |
|------|--------|---------------|------|
| 4.1 | Adversarial training: augment training set with adversarial examples | EXPERIMENT_CONTRACT | [ ] |
| 4.2 | Input preprocessing defenses: feature squeezing, statistical detection | EXPERIMENT_CONTRACT | [ ] |
| 4.3 | Ensemble defense: majority vote across model types | EXPERIMENT_CONTRACT | [ ] |
| 4.4 | Measure clean accuracy vs adversarial accuracy tradeoff per defense | METRICS_CONTRACT | [ ] |
| 4.5 | Adaptive attacker: re-attack defended models (no security by obscurity) | ADVERSARIAL_EVALUATION §5 | [ ] |
| 4.6 | Write `scripts/run_defenses.py` | — | [ ] |
| 4.7 | TRADEOFF_LOG entries: defense selection rationale | TRADEOFF_LOG.md | [ ] |

**Gate:** ≥1 defense achieves ≥80% adversarial accuracy with ≤5% clean accuracy drop. Adaptive attack results documented.

### Phase 5: Artifacts & Publication (Days 22-28)

**Goal:** Ship public artifacts. Blog post. Conference CFP draft.

| Task | Detail | govML Template | Done |
|------|--------|---------------|------|
| 5.1 | Generate all figures: budget curves, confusion matrices, tradeoff plots | FIGURES_TABLES_CONTRACT | [ ] |
| 5.2 | Write FINDINGS.md (500 words, blog-ready summary) | — | [ ] |
| 5.3 | Write blog post: "What 15 Years of Incident Response Taught Me About Adversarial ML" | Brand strategy Pillar 1 | [ ] |
| 5.4 | Draft BSides/DEF CON AI Village CFP abstract | V-cluster V2→V3 | [ ] |
| 5.5 | Clean repo for public release: README, LICENSE, .gitignore | — | [ ] |
| 5.6 | Run govML audit pipeline (G13-G16) on all documentation | REPORT_CONSISTENCY_SPEC | [ ] |
| 5.7 | Final TRADEOFF_LOG review | DECISION_LOG | [ ] |
| 5.8 | Tag release v1.0 | — | [ ] |

**Gate:** All figures reproducible from scripts. Blog post draft complete. Repo public-ready.

---

## govML Template Usage Map

| Template | Phase Used | Purpose in This Project |
|----------|-----------|------------------------|
| ENVIRONMENT_CONTRACT | 0 | Pin Python 3.10, scikit-learn, ART, PyTorch versions |
| DATA_CONTRACT | 0-1 | CICIDS2017 download, checksums, splits, preprocessing |
| EXPERIMENT_CONTRACT | 2-4 | Seed protocol, baseline matching, experiment matrix |
| METRICS_CONTRACT | 2-4 | Per-class F1, sanity checks (majority baseline), budget curves |
| HYPOTHESIS_CONTRACT | 2 | Map RQ-1→H-1 through RQ-4→H-4 |
| TEST_ARCHITECTURE | 1-3 | Leakage, determinism, adversarial budget constraint tests |
| ADVERSARIAL_EVALUATION | 3-4 | Attack taxonomy, constrained perturbations, transferability, adaptive attacks |
| FIGURES_TABLES_CONTRACT | 3-5 | Budget curves, confusion matrices, tradeoff plots |
| DECISION_LOG | All | Architectural decisions (model selection, defense choices) |
| REPORT_ASSEMBLY_PLAN | 5 | Blog post + CFP structure |
| REPORT_CONSISTENCY_SPEC | 5 | Ten Simple Rules compliance for blog |
| RUBRIC_TRACEABILITY | 2-5 | Research Question Traceability (self-directed appendix) |
| REPRODUCIBILITY_SPEC | 5 | Full reproduction instructions |
| PRE_SUBMISSION_CHECKLIST | 5 | Final quality gate before public release |
| CLAUDE_MD | All | AI collaboration governance |

---

## Key Dependencies

| Dependency | Source | License | Why |
|-----------|--------|---------|-----|
| CICIDS2017 | University of New Brunswick | Public/research | Real labeled network intrusion data (2.8M flows, 15 classes) |
| IBM Adversarial Robustness Toolbox (ART) | IBM Research | MIT | Feature-space adversarial attacks + defenses |
| scikit-learn | Community | BSD-3 | Baseline classifiers (RF, IF, DBSCAN) |
| XGBoost | Community | Apache-2.0 | Gradient boosted baseline |
| PyTorch | Meta | BSD-3 | Autoencoder + MLP |

---

## Cluster Impact Targets

| Cluster | Current | Target | Evidence This Project Produces |
|---------|---------|--------|-------------------------------|
| S | S1-S2 | **S2→S3** | Novel adversarial evasion findings on real attack data with attacker-realistic constraints |
| V | V1-V2 | **V2→V3** | Public repo + blog post + BSides CFP |
| L | L3+ | L3+ reinforced | govML templates on new dataset/domain |
| D | D3 | **D3→D4** | TRADEOFF_LOG with defense selection rationale, feature controllability analysis |

---

## Scarcity Positioning

**Target intersection:** C2 (S4+P4, <100 people globally)

**What makes this project different from academic adversarial ML papers:**
1. **Attacker-realistic constraints.** Most papers perturb all features. We only perturb features an attacker can actually control (packet timing, payload size — not TCP flags set by the OS). This comes from 15 years of incident response, not from reading papers.
2. **Defense evaluation includes adaptive attackers.** No security by obscurity. If the defense is public, the attacker adapts.
3. **Governance-grade reproducibility.** Full govML pipeline — not a Jupyter notebook with hardcoded paths.
4. **Blog framing for practitioners.** Not an arXiv paper for academics. A "here's what this means for your SOC" post for security practitioners.

---

## Timeline

| Week | Phase | Key Deliverable |
|------|-------|-----------------|
| 1 | Phase 0 + 1 | Environment, data, preprocessing, splits |
| 2 | Phase 2 | Baseline models, benchmark reproduction |
| 3 | Phase 3 | Adversarial evasion (core contribution) |
| 4 | Phase 4 + 5 | Defenses, artifacts, blog draft, repo cleanup |

---

## Revision Log

| Date | Change |
|------|--------|
| 2026-03-13 | Initial execution plan |
