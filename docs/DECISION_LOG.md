# DECISION LOG

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
- None — decisions may reference any contract but have no structural dependency.

**Downstream (depends on this contract):**
- See [CHANGELOG](CHANGELOG.tmpl.md) for CONTRACT_CHANGE entries triggered by decisions (cross-reference ADR IDs)
- See [RISK_REGISTER](RISK_REGISTER.tmpl.md) for risk entries mitigated by decisions
- See [IMPLEMENTATION_PLAYBOOK](IMPLEMENTATION_PLAYBOOK.tmpl.md) §5 for change control procedure referencing ADR entries

## Purpose

This log records architectural and methodological decisions for the **Adversarial ML on Network Intrusion Detection** project using a lightweight ADR (Architecture Decision Record) format. Each decision captures the context, alternatives, rationale, and consequences so that future changes are informed rather than accidental.

**Relationship to CHANGELOG:** When a decision triggers a `CONTRACT_CHANGE` commit, the change MUST also be logged in CHANGELOG with a cross-reference to the ADR ID.

---

## When to Create an ADR

Create a new ADR when:
- A decision affects multiple contracts or specs
- A decision resolves an ambiguity in authority documents
- A decision involves tradeoffs that future contributors need to understand
- A `CONTRACT_CHANGE` commit is triggered by a methodological choice
- A risk mitigation strategy is selected from multiple options

Do NOT create an ADR for routine implementation choices that follow directly from a single contract requirement with no alternatives.

---

## Status Lifecycle

```
Proposed → Accepted → [Superseded by ADR-YYYY]
```

- **Proposed:** Under discussion; not yet binding.
- **Accepted:** Binding; implementation may proceed.
- **Superseded:** Replaced by a newer ADR. MUST cite the superseding ADR ID. Do NOT delete superseded entries.

---

## Decision Record Template

Copy this block for each new decision:

```markdown
## ADR-XXXX: [Short title]

- **Date:** YYYY-MM-DD
- **Status:** Proposed | Accepted | Superseded by ADR-YYYY

### Context
[Problem statement and constraints. Cite authority documents by tier and section.]

### Decision
[The chosen approach. Be specific enough that someone can implement it without ambiguity.]

### Alternatives Considered

| Option | Description | Verdict | Reason |
|--------|-------------|---------|--------|
| A (chosen) | [approach] | **Accepted** | [why best] |
| B | [approach] | Rejected | [why not] |
| C | [approach] | Rejected | [why not] |

### Rationale
[Why this approach is best given the project constraints. Cite authority documents.]

### Consequences
[Tradeoffs and risks. Reference RISK_REGISTER entries if applicable.]

### Contracts Affected

| Contract | Section | Change Required |
|----------|---------|----------------|
| [contract name] | §N | [what changes] |

### Evidence Plan

| Validation | Command / Artifact | Expected Result |
|------------|-------------------|-----------------|
| [what to verify] | [command or file path] | [pass criteria] |
```

---

## Decisions

*(Record decisions below. Number sequentially: ADR-0001, ADR-0002, etc.)*

---

## ADR-0001: Use official CIC portal dataset over Kaggle mirror

- **Date:** 2026-03-13
- **Status:** Accepted

### Context
CICIDS2017 is available from multiple sources: official CIC/UNB portal (requires manual download), Kaggle mirrors (API download), and various GitHub re-uploads. EXECUTION_PLAN.md §Phase 0 requires data acquisition. Brand strategy prioritizes credibility with security research community.

### Decision
Download from official CIC portal at University of New Brunswick. Accept manual download + scp workflow.

### Alternatives Considered

| Option | Description | Verdict | Reason |
|--------|-------------|---------|--------|
| A (chosen) | Official CIC portal | **Accepted** | Full dataset (2.83M flows), citable source, security community credibility |
| B | Kaggle mirror | Rejected | May be subset (~240MB vs ~850MB uncompressed), less authoritative citation |
| C | GitHub re-upload | Rejected | No provenance guarantee, may have preprocessing applied |

### Rationale
For a publication-track security ML project, citing the official UNB/CIC source is essential. The security research community scrutinizes data provenance. Kaggle mirrors may be subsets or preprocessed versions.

### Consequences
Manual download workflow (browser + scp). Logged as ISS-007 in govML LESSONS_LEARNED — future template improvement to handle non-API data sources as primary path.

### Contracts Affected

| Contract | Section | Change Required |
|----------|---------|----------------|
| DATA_CONTRACT | §2 | Data source = "Official CIC portal, UNB" |
| ENVIRONMENT_CONTRACT | §6 | Data placement instructions updated |

### Evidence Plan

| Validation | Command / Artifact | Expected Result |
|------------|-------------------|-----------------|
| Data integrity | `python scripts/check_data_ready.py` | 8/8 CSVs present, row counts match expected |
| SHA-256 checksums | `outputs/provenance/data_checksums.json` | Checksums recorded for reproducibility |

---

## ADR-0002: CPU-only PyTorch to fit 29GB disk constraint

- **Date:** 2026-03-13
- **Status:** Accepted

### Context
Azure Standard B2ms VM has 29GB OS disk. Default PyTorch pip install pulls CUDA build (~2GB). With conda base env, dataset (850MB), and other dependencies, disk fills. ENVIRONMENT_CONTRACT §2 specifies CPU-only target platform.

### Decision
Use `torch==2.1.2+cpu` from PyTorch CPU-only index. 185MB vs ~2GB.

### Alternatives Considered

| Option | Description | Verdict | Reason |
|--------|-------------|---------|--------|
| A (chosen) | CPU-only PyTorch via `--extra-index-url` | **Accepted** | 10x smaller, matches target platform, zero functionality loss |
| B | Default PyTorch (CUDA) | Rejected | Fills disk; no GPU on VM |
| C | Skip PyTorch entirely | Rejected | ART requires PyTorch for some estimator classes |
| D | Resize Azure disk | Rejected | Cost increase, over-engineering for the constraint |

### Rationale
ENVIRONMENT_CONTRACT §10 (CPU Reproducibility Rule): "ALL report artifacts MUST be reproducible on CPU." CPU-only variant is the correct choice regardless of disk constraints.

### Consequences
Cannot use GPU-accelerated ART attacks even if a GPU were added later. Would need to rebuild env. Acceptable trade-off given project scope.

### Contracts Affected

| Contract | Section | Change Required |
|----------|---------|----------------|
| ENVIRONMENT_CONTRACT | §4 | PyTorch version = 2.1.2+cpu |
| environment.yml | pip section | Added `--extra-index-url` for CPU wheel |

### Evidence Plan

| Validation | Command / Artifact | Expected Result |
|------------|-------------------|-----------------|
| Import check | `python -c "import torch; print(torch.__version__)"` | `2.1.2+cpu` |
| verify_env.sh | `bash scripts/verify_env.sh` | All checks pass |

---

## ADR-0003: Pin setuptools<72 for ART compatibility

- **Date:** 2026-03-13
- **Status:** Accepted

### Context
ART 1.17.1 imports `from pkg_resources import packaging` during initialization. setuptools 72+ removed the `pkg_resources` module entirely. Conda's default channel installed setuptools 82.0.1, causing ART import to fail with `ModuleNotFoundError`.

### Decision
Pin `setuptools<72` in environment.yml as a conda dependency (not pip).

### Alternatives Considered

| Option | Description | Verdict | Reason |
|--------|-------------|---------|--------|
| A (chosen) | Pin setuptools<72 | **Accepted** | Minimal change, fixes root cause |
| B | Upgrade ART to newer version | Rejected | ART 1.18+ may have breaking API changes; would need to revalidate all attack code |
| C | Monkey-patch pkg_resources | Rejected | Fragile, non-reproducible |

### Rationale
The fix is deterministic and reproducible. When ART releases a version that drops pkg_resources dependency, we can remove the pin via CONTRACT_CHANGE.

### Consequences
Stuck on older setuptools until ART fix. No practical impact — setuptools is a build tool, not a runtime dependency for our code.

### Contracts Affected

| Contract | Section | Change Required |
|----------|---------|----------------|
| ENVIRONMENT_CONTRACT | §4 | Added setuptools<72 to dependency table |
| environment.yml | dependencies | Added `setuptools<72` with comment |

### Evidence Plan

| Validation | Command / Artifact | Expected Result |
|------------|-------------------|-----------------|
| ART import | `python -c "import art; print(art.__version__)"` | `1.17.1` |
| verify_env.sh | `bash scripts/verify_env.sh` | All checks pass |
