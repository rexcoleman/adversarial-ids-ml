# PUBLICATION BRIEF

<!-- version: 1.0 -->
<!-- created: 2026-03-11 -->
<!-- last_validated_against: none -->

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
- See [REPORT_ASSEMBLY_PLAN](../report/REPORT_ASSEMBLY_PLAN.tmpl.md) for report structure and content requirements
- See [HYPOTHESIS_CONTRACT](../core/HYPOTHESIS_CONTRACT.tmpl.md) for hypothesis resolution (source of key claims)
- See [FIGURES_TABLES_CONTRACT](../core/FIGURES_TABLES_CONTRACT.tmpl.md) for artifact inventory

**Downstream (depends on this contract):**
- See [ACADEMIC_INTEGRITY_FIREWALL](ACADEMIC_INTEGRITY_FIREWALL.tmpl.md) for content reuse boundaries
- See [LEAN_HYPOTHESIS](LEAN_HYPOTHESIS.tmpl.md) for portfolio-level hypothesis alignment

## Customization Guide

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `Adversarial ML on Network Intrusion Detection` | Project name | Optimizer Comparison Study |
| `{{TARGET_READER}}` | Primary audience | ML hiring manager, course grader, conference reviewer |
| `{{PRIMARY_DEMONSTRATION}}` | What this project primarily proves about the author | Rigorous experimental methodology |
| `{{PORTFOLIO_CONTEXT}}` | Where this fits in the author's body of work | Second of three ML course projects |
| `EXECUTION_PLAN.md` | Tier 1 authority document | Project requirements spec |
| `docs/ADVERSARIAL_EVALUATION.md` | Tier 2 authority document | FAQ or clarifications document |
| `docs/EXPERIMENT_CONTRACT.md` | Tier 3 authority document | Advisory clarifications |

---

## 1) Purpose

This brief defines the communication strategy for the **Adversarial ML on Network Intrusion Detection** deliverables. It ensures the project's write-up serves its intended audience and demonstrates the intended competencies, without overclaiming or underclaiming.

---

## 2) Target Reader & Takeaway

### 2.1 Reader Profile

| Property | Value |
|----------|-------|
| **Primary reader** | {{TARGET_READER}} |
| **Reader's goal** | *(What are they evaluating? e.g., "Assess ML methodology competence", "Grade against rubric")* |
| **Reader's time** | *(How long will they spend? e.g., "15-30 minutes", "5 minutes for executive summary")* |
| **Technical level** | *(What can you assume they know? e.g., "Familiar with gradient descent, may not know RO details")* |

### 2.2 One-Sentence Takeaway

After reading, the target reader should think:

> *"{{ONE_SENTENCE_TAKEAWAY}}"*

*(e.g., "This person can design, execute, and analyze controlled ML experiments with rigorous methodology.")*

**Rule:** Every section of the report MUST contribute to this takeaway. Content that does not support the takeaway is a candidate for removal or compression.

---

## 3) Primary Demonstration

### 3.1 What This Project Proves

| Competency | How Demonstrated | Evidence |
|-----------|-----------------|---------|
| {{PRIMARY_DEMONSTRATION}} | *(e.g., "Controlled ablation across 7 optimizers with matched budgets")* | *(e.g., "Summary table T1, Figures F1-F4")* |
| *(secondary competency)* | *(how)* | *(evidence)* |
| *(add rows)* | | |

### 3.2 What This Project Does NOT Prove

Be explicit about limitations to avoid overclaiming:

| Non-Claim | Why | Alternative Framing |
|-----------|-----|-------------------|
| *(e.g.)* "Adam is the best optimizer" | Limited to 2 datasets, compact MLP | "Adam converges fastest on these benchmarks under matched budgets" |
| *(e.g.)* "This approach generalizes" | No out-of-distribution testing | "Results are specific to the evaluated datasets and architecture" |
| *(add rows)* | | |

---

## 4) Narrative Constraints

### 4.1 Tone Guidelines

| Guideline | Description |
|-----------|-------------|
| **Evidence-first** | Every claim MUST be supported by a specific figure, table, or metric |
| **Mechanism-focused** | Explain *why* results occurred, not just *what* happened |
| **Precise language** | Use "outperforms on this metric under these conditions" not "is better" |
| **Honest about limitations** | Acknowledge failure modes, negative results, and scope boundaries |

### 4.2 Anti-Claims

Statements the report MUST NOT make:

| Anti-Claim | Why Prohibited | Acceptable Alternative |
|-----------|---------------|----------------------|
| "Method X is superior" | Unbounded generalization from limited experiments | "Method X achieves lower val_loss on Adult under 10K grad_evals" |
| "We prove that..." | Empirical results don't constitute proofs | "Our experiments show that..." or "Evidence suggests..." |
| "Novel contribution" | Unless genuinely novel; class projects typically are not | "Our analysis reveals..." or "We demonstrate..." |
| *(add project-specific)* | | |

**Rule:** Before submitting, search the report for anti-claim patterns. Each match MUST be rewritten.

**Verification:** Grep report for "superior", "prove", "novel", "always", "never", "best" (without qualification). Flag and review each match.

### 4.3 Hedging Requirements

Claims involving comparisons MUST include:
- The specific metric being compared
- The budget/conditions under which the comparison holds
- The datasets tested
- Dispersion information (median + IQR or mean ± std)

---

## 5) Portfolio Alignment

### 5.1 Portfolio Context

| Property | Value |
|----------|-------|
| **This project** | Adversarial ML on Network Intrusion Detection |
| **Portfolio position** | {{PORTFOLIO_CONTEXT}} |
| **Builds on** | *(prior project, if any)* |
| **Feeds into** | *(next project or career goal, if applicable)* |

### 5.2 Skill Narrative

How this project fits the broader skill story:

| Prior Work | This Project | Growth Demonstrated |
|-----------|-------------|-------------------|
| *(e.g.)* SL Report: trained and evaluated models | OL Report: compared optimization strategies | Moved from execution to experimental design |
| *(add rows)* | | |

### 5.3 Transferable Artifacts

Identify which project components have value beyond the immediate deliverable:

| Artifact | Transferable Value | Audience |
|----------|-------------------|----------|
| *(e.g.)* Governance framework | Reusable for any ML project | Future projects, team members |
| *(e.g.)* Ablation methodology | Demonstrates rigorous experimental design | Hiring managers |
| *(add rows)* | | |

---

## 6) Message Governance

### 6.1 Key Messages (Priority Order)

| # | Message | Supporting Evidence | Report Section |
|---|---------|-------------------|---------------|
| 1 | *(highest-priority message)* | *(figure/table/metric)* | *(section)* |
| 2 | *(second message)* | *(evidence)* | *(section)* |
| 3 | *(third message)* | *(evidence)* | *(section)* |

### 6.2 Message-to-Section Mapping

Every report section MUST map to at least one key message. Sections that don't support any message are candidates for removal.

| Report Section | Key Message(s) Supported | Page Budget |
|---------------|------------------------|-------------|
| Introduction | 1, 2 | *(e.g., 0.5 pages)* |
| Methods | 1 | *(e.g., 1 page)* |
| Results | 1, 2, 3 | *(e.g., 2 pages)* |
| Discussion | 1, 2 | *(e.g., 1 page)* |
| Conclusion | 1, 2, 3 | *(e.g., 0.5 pages)* |

---

## 7) Pre-Publication Checklist

- [ ] One-sentence takeaway is clear and supported by evidence
- [ ] Primary demonstration is documented with specific artifacts
- [ ] Anti-claims have been searched for and eliminated
- [ ] All comparative claims include metric + conditions + dispersion
- [ ] Portfolio context is documented (for career artifacts)
- [ ] Key messages map to report sections
- [ ] No section lacks a key message justification

---

## 8) Change Control Triggers

The following changes require a `CONTRACT_CHANGE` commit:

- Target reader or takeaway definition
- Primary demonstration claims
- Anti-claim list
- Key messages or message-to-section mapping
- Portfolio alignment context
