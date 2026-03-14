# EXPERIMENT CONTRACT

<!-- version: 2.0 -->
<!-- created: 2026-02-20 -->
<!-- last_validated_against: CS_7641_Machine_Learning_OL_Report -->

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
- See [DATA_CONTRACT](DATA_CONTRACT.tmpl.md) §3 for split definitions and §4 for leakage prevention
- See [ENVIRONMENT_CONTRACT](ENVIRONMENT_CONTRACT.tmpl.md) §8 for determinism and seeding defaults
- See [METRICS_CONTRACT](METRICS_CONTRACT.tmpl.md) §2 for required metrics and §5 for convergence threshold

**Downstream (depends on this contract):**
- See [FIGURES_TABLES_CONTRACT](FIGURES_TABLES_CONTRACT.tmpl.md) §3 for experiment-sourced figures
- See [ARTIFACT_MANIFEST_SPEC](ARTIFACT_MANIFEST_SPEC.tmpl.md) §3 for per-run provenance files
- See [SCRIPT_ENTRYPOINTS_SPEC](SCRIPT_ENTRYPOINTS_SPEC.tmpl.md) §4 for experiment script specifications

## Customization Guide

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `Adversarial ML on Network Intrusion Detection` | Project name | Sentiment Analysis Benchmark |
| `{{EXPERIMENT_PARTS}}` | List of experimental parts/phases | Part 1: RO, Part 2: Adam Ablations, Part 3: Regularization |
| `{{BUDGET_CONFIG_FILE}}` | Path to budget config | config/budgets.yaml |
| `{{BACKBONE_DESCRIPTION}}` | Model architecture description | PyTorch compact MLP from prior project |
| `[42, 123, 456, 789, 1024]` | Stability seeds | [42, 123, 456, 789, 1024] |
| `42` | Primary seed | 42 |
| `EXECUTION_PLAN.md` | Tier 1 authority document | Project requirements spec |
| `docs/ADVERSARIAL_EVALUATION.md` | Tier 2 authority document | FAQ or clarifications document |
| `docs/EXPERIMENT_CONTRACT.md` | Tier 3 authority document | Course TAs' Piazza clarifications |

---

## 1) Scope & Experiment Matrix

This contract defines the experimental protocol for **Adversarial ML on Network Intrusion Detection**.

### 1.1 Experiment Parts

| Part | Description | Datasets | Methods | Budget Type |
|------|-------------|----------|---------|-------------|
| Part 1 (Phase 1) | EDA + Hypothesis Registration | CICIDS2017 | Correlation analysis, class distribution, feature controllability split | N/A |
| Part 2a | Baseline Training | CICIDS2017 (10% sample) | RF, XGBoost, MLP | wall_clock |
| Part 2b | Unconstrained Adversarial Attacks | CICIDS2017 (10% sample) | Noise, ZOO, HopSkipJump @ 6 ε values | func_evals |
| Part 2c | Constrained Adversarial Attacks | CICIDS2017 (10% sample) | Same as 2b, feature mask applied | func_evals |
| Part 2d | Defense Evaluation | CICIDS2017 (10% sample) | Adversarial training, feature squeezing, constraint-aware detection | wall_clock |

### 1.2 Cross-Part Constraints

Document hard rules that constrain relationships between parts:

| Constraint | Rule | Enforcement |
|-----------|------|-------------|
| Dataset lock | All parts use CICIDS2017 only | Single dataset in preprocessing pipeline |
| Model lock | Parts 2b-2d use models trained in Part 2a (no retraining except adversarial training defense) | Models loaded from `models/` via `joblib.load` |
| Seed lock | All parts share seed list [42, 123, 456, 789, 1024] | `set_seed(seed)` called before every experiment |
| Feature mask lock | Constrained attacks use identical 57-feature mask across all models/seeds | `get_controllable_feature_mask()` from preprocessing.py |
| ε schedule lock | All attack evaluations use [0.01, 0.05, 0.1, 0.2, 0.3, 0.5] | `EPSILON_SCHEDULE` constant in adversarial_attacks.py |

### 1.3 Cross-Part Dependency Graph

```
Part 1 (EDA) ──→ Part 2a (baseline training — informed by EDA feature analysis)
Part 2a ──→ Part 2b (unconstrained attacks — uses trained models)
Part 2a ──→ Part 2c (constrained attacks — uses trained models + feature mask from Part 1)
Part 2b ──→ Part 2d (defense eval — compares against unconstrained attack baseline)
Part 2c ──→ Part 2d (defense eval — constrained attack results inform H-4)
```

---

## 2) Compute Budgets

### 2.1 Budget Source

Budgets are defined per-script as constants (no external config file — project scope doesn't warrant it). Wall-clock is the primary budget constraint (Azure B2ms, 2 vCPUs, 8 GiB RAM).

### 2.2 Budget Types

Different experiment paradigms use different budget accounting:

| Budget Type | Unit | When to Use | Counting Rule |
|------------|------|-------------|---------------|
| `func_evals` | Function evaluations | Black-box optimization, randomized search, evolutionary methods | Each objective function computation (including full validation sweep) counts as ONE evaluation |
| `grad_evals` | Gradient evaluations | Gradient-based training (SGD, Adam, etc.) | Each backward pass counts as ONE gradient evaluation; multiple batches per step still count as one |
| `episodes` | Environment episodes | RL / sequential decision-making | Each complete episode (reset → terminal) counts as ONE episode |
| `wall_clock` | Seconds | Real-time constrained experiments | Cumulative wall-clock time; MUST be reported alongside primary budget |

**Accounting rules:**
- Every run MUST log both `budget_allocated` and `budget_used` in `summary.json`
- If validation is computed via mini-batches for memory efficiency, the entire sweep still counts as ONE function evaluation
- Wall-clock MUST be reported alongside the primary budget type for all experiments (even if wall-clock is not the budget constraint)

**Verification:** Schema-validate every `summary.json` for presence of `budget_allocated`, `budget_used`, and `wall_clock_s` fields.

### 2.3 Budget Schema

```yaml
# {{BUDGET_CONFIG_FILE}}
part1:
  func_evals: {{PART1_BUDGET}}
part2:
  grad_evals: {{PART2_BUDGET}}
  eval_interval_steps: {{EVAL_INTERVAL}}
  threshold_l: {{THRESHOLD_L}}
part3:
  grad_evals: {{PART3_BUDGET}}  # MUST equal part2.grad_evals
seeds:
  default: 42
  stability_list: [42, 123, 456, 789, 1024]
```

### 2.4 Budget-Matching Rule

Within each part, all compared methods MUST use identical compute budgets. This is non-negotiable for fair comparisons.

- Scripts MUST enforce budget caps and hard-stop at the limit (no silent overruns)
- Over-budget runs MUST set `over_budget: true` in `summary.json`
- Over-budget runs MUST be excluded from head-to-head comparison tables and claims
- Over-budget runs MAY be reported in supplementary analysis with clear disclosure

**Verification:** At each phase gate, assert that all runs within a part have `budget_used <= budget_allocated` and that `budget_allocated` is identical across methods.

### 2.5 Cross-Part Budget Consistency

Where experiments in different parts are compared (e.g., regularization vs baseline), budgets MUST match. Specifically:
- `part3.grad_evals == part2.grad_evals` (if Part 3 builds on Part 2)
- This is validated at Phase 0 and enforced in scripts

---

## 3) Dataset Splits & Leakage Prevention

### 3.1 Split Source

*(Reference DATA_CONTRACT for full details.)*

Split files: generated in-memory by `src/preprocessing.py` via stratified train/val/test split (70/15/15). Rare classes (<3 samples) dropped and labels remapped to contiguous integers.

### 3.2 Test-Split Access Policy

Test split is accessible ONLY through the final evaluation script. All other scripts MUST use train and validation splits only.

### 3.3 Leakage Prevention

- Fit preprocessing on train only (see DATA_CONTRACT §4)
- No test metrics in per-run outputs
- No hyperparameter selection based on test performance

---

## 4) Seeding & Initialization Protocol

### 4.1 Seed Policy

- **Default seed:** 42
- **Stability list:** [42, 123, 456, 789, 1024]
- Seeds are set before every experiment via the deterministic seeding function (see ENVIRONMENT_CONTRACT §8)

### 4.2 Baseline State Matching

For experiments that compare different methods on the same system, all methods MUST start from an identical baseline state. The exact form of the baseline depends on the project domain:

| Domain | Baseline State | Verification Method |
|--------|---------------|-------------------|
| **Neural networks** | Initial weight `state_dict` | Forward-pass equality within tolerance (1e-6) |
| **Systems / C/C++** | Compiled binary + input data + initial memory state | Binary hash equality + input hash equality |
| **RL agents** | Initial policy weights + environment seed | First-episode trajectory equality |

**Verification:** All methods within a part share an identical baseline. The verification method above confirms equality at run start.

#### Protocol (Neural Network Projects)

1. **Initialize once per seed:** Create the model with the current seed and save the initial `state_dict`:
   ```python
   torch.manual_seed(seed)
   model = build_model(config)
   torch.save(model.state_dict(), f"outputs/init_weights/{{DATASET}}_seed_{seed}.pt")
   ```

2. **Load before each run:** Before each method's training begins, load the saved `state_dict`:
   ```python
   model.load_state_dict(torch.load(f"outputs/init_weights/{{DATASET}}_seed_{seed}.pt"))
   ```

3. **Verify identical start:** Assert that all methods produce the same first-batch forward-pass output:
   ```python
   # After loading init weights, before training:
   with torch.no_grad():
       output = model(X_sample)
   # Compare against reference output from first method — must match within tolerance
   assert torch.allclose(output, reference_output, atol=1e-6), \
       f"Init mismatch: method {method} diverges from reference at seed {seed}"
   ```

#### Protocol (Systems / C/C++ Projects)

1. **Build once per configuration:** Compile the binary with locked build profile (see BUILD_SYSTEM_CONTRACT §3). Record binary hash.
2. **Share input data:** All compared methods receive identical input files. Record input hashes.
3. **Verify identical start:** Assert binary hash and input hash match across all method runs.

#### Storage Convention

```
outputs/init_weights/          # Neural network projects
├── {{DATASET_1_NAME}}_seed_42.pt
├── {{DATASET_1_NAME}}_seed_123.pt
└── ...

outputs/baseline_state/        # Systems projects
├── binary_hash.json
├── input_hashes.json
└── ...
```

#### Scope

Baseline state matching applies to:
- All methods within a single part (e.g., all optimizers in Part 2)
- All methods across dependent parts (e.g., Part 3 uses the same init as Part 2)
- Part composition experiments (e.g., Part 4 gradient phase uses the same init)

Baseline state matching does NOT apply to:
- Methods with fundamentally different architectures (if permitted by the experiment design)
- Black-box optimization phases where the "initialization" is the pre-trained weights from a prior phase

### 4.3 Multi-Seed Stability

All experiments MUST be run across the full seed list to support:
- Median + IQR reporting (not just single-seed point estimates)
- Stability analysis across methods
- Credible dispersion in comparative claims

**Verification:** For each method, assert that `len(completed_seeds) == len(stability_list)`. Multi-seed outputs exist under `outputs/{{PART}}/{{DATASET}}/{{METHOD}}/seed_*/`.

---

## 5) Metrics & Evaluation Rules

*(Reference METRICS_CONTRACT for full definitions.)*

### 5.1 Evaluation Determinism

During evaluation (validation loss computation, metric calculation):
- `model.eval()` MUST be called
- Dropout MUST be disabled
- Batch normalization MUST be frozen (running stats, not batch stats)
- Data augmentation MUST be disabled
- `torch.no_grad()` MUST wrap the evaluation block

**Verification:** Assert `model.training == False` during evaluation. Verify `config_resolved.yaml` records `eval_mode: True`, `dropout_off: True`, `bn_frozen: True`.

### 5.2 Required Metrics Per Run

Every run MUST log:
- `train_loss` and `val_loss` at every evaluation interval
- Primary validation metric(s) per dataset
- `wall_clock_s` cumulative timing
- Budget usage (`grad_evals` or `func_evals`)

---

## 6) Per-Part Protocols

### Part 2a: Baseline Training

**Goal:** Train IDS classifiers on clean CICIDS2017 data to establish clean-performance baselines.

**Methods:** Random Forest, XGBoost, MLP (sklearn)

**Budget:** Wall-clock ~5 min per model per seed at 10% sample (283K rows)

**Protocol:**
1. Load preprocessed data via `run_preprocessing_pipeline(seed=seed, sample_frac=0.1)`
2. Train each model with fixed hyperparameters (no tuning — these are baselines)
3. Evaluate on test set: macro-F1, accuracy, per-class classification report
4. Save models to `models/{ModelName}_seed{seed}.pkl`

**Operator Disclosures:**

| Method | Required Disclosures |
|--------|---------------------|
| Random Forest | n_estimators=100, max_depth=20, min_samples_leaf=5 |
| XGBoost | n_estimators=100, max_depth=8, learning_rate=0.1, eval_metric=mlogloss |
| MLP | hidden_layer_sizes=(256,128,64), max_iter=200, early_stopping=True |

### Part 2b-c: Adversarial Attacks

**Goal:** Measure IDS vulnerability to adversarial perturbation under unconstrained (2b) and constrained (2c) threat models.

**Methods:** Random noise baseline (primary), ZOO, HopSkipJump (available but slow)

**Budget:** 2,000-sample eval subset per attack × 6 ε values × 2 constraint modes × 2 models = 48 evaluations

**Protocol:**
1. Load trained baseline model from Part 2a
2. Wrap model via ART (`SklearnClassifier` for RF, `BlackBoxClassifierNeuralNetwork` for XGBoost)
3. For each ε: generate adversarial examples, apply feature mask (constrained only), evaluate
4. Save results to `outputs/adversarial/{unconstrained,constrained}_results.json`

### Part 2d: Defense Evaluation

**Goal:** Compare three defense strategies and measure F1 recovery ratio.

**Methods:** Adversarial training, feature squeezing (4-bit), constraint-aware detection

**Budget:** Adversarial training retrains model (~5 min each); other defenses are inference-only

**Protocol:**
1. Load baseline model + generate noise adversarial examples at ε=0.3
2. Adversarial training: augment training data with 50K noise-perturbed samples, retrain
3. Feature squeezing: quantize adversarial inputs to 4-bit depth
4. Constraint-aware detection: flag samples where defender-observable features changed
5. Evaluate all defenses: macro-F1 on defended examples, compute recovery ratio
6. Save to `outputs/defense/defense_comparison.json`

**Constraints:**
- All defenses evaluated against same noise attack (ε=0.3) for fair comparison
- Adversarial training uses different RNG seed (seed+1) for re-attack to avoid overfitting to training perturbations

---

## {{N+1}}) Output Directory Structure

```
outputs/
+-- eda/                                   # EDA artifacts (summary.json, plots)
+-- baselines/                             # Baseline training results per seed
+-- adversarial/                           # Attack results (unconstrained + constrained JSON)
+-- defense/                               # Defense comparison results + recovery plots
+-- provenance/                            # versions.txt, git_commit_sha.txt, run_log.json
models/
+-- {ModelName}_seed{seed}.pkl             # Trained baseline models
```

### Per-Run Output Files

Every run directory MUST contain:

| File | Format | Contents |
|------|--------|----------|
| `metrics.csv` | CSV | Per-step metrics (see METRICS_CONTRACT §9) |
| `summary.json` | JSON | Run summary with best metrics, budget usage, flags |
| `config_resolved.yaml` | YAML | Full resolved configuration (CLI + config file + defaults) |
| `run_manifest.json` | JSON | SHA-256 hashes of all output files |

**Verification:** `python scripts/verify_manifests.py` checks that all four files exist in every run directory and that `run_manifest.json` hashes are correct.

---

## 8) Pipeline Composition Protocol

Parts compose linearly: 2a → 2b/2c → 2d. No complex multi-part composition required.

**Composition rule:** Defense evaluation (Part 2d) loads models from Part 2a and generates its own adversarial examples. Attack results from Parts 2b-2c are used for comparison only, not as direct inputs to Part 2d.

---

## 9) Exit Gates

### Part 2a Exit Gate
- [x] All 3 models trained for seed 42
- [ ] All 3 models trained for seeds 123, 456, 789, 1024 (in progress)
- [x] Macro-F1 > 0.70 for all models (XGB: 0.823, RF: 0.778, MLP: 0.717)
- [x] Models saved to `models/` directory

### Part 2b-c Exit Gate
- [x] Unconstrained + constrained results at all 6 ε values for RF and XGBoost
- [x] ASR computed for all conditions
- [x] Budget curves plotted
- [x] Results saved to `outputs/adversarial/`

### Part 2d Exit Gate
- [x] All 3 defenses evaluated for RF and XGBoost
- [x] Recovery ratios computed
- [x] Results saved to `outputs/defense/defense_comparison.json`
- [x] Defense comparison plot generated

---

## 10) Change Control Triggers

The following changes require a `CONTRACT_CHANGE` commit:

- Compute budgets
- Method list for any part
- Initialization protocol
- Output schemas (metrics.csv, summary.json, config_resolved.yaml)
- Evaluation determinism rules
- Budget-matching constraints
- Part composition rules
- Cross-part constraints or dependency graph

---

## Appendix A: RL Protocol

> **Not applicable.** This is a supervised classification project. Appendix deleted.
