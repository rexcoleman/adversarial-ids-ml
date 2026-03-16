# PUBLICATION PIPELINE

<!-- version: 1.0 -->
<!-- created: 2026-03-16 -->

## 1) Purpose

Tracks publication targets, deadlines, and submission status for FP-01 outputs.

## 2) Pipeline

| Stage | Target | Format | Deadline | Status |
|-------|--------|--------|----------|--------|
| 1 | Blog post (Hugo + GitHub Pages) | Long-form (~2000 words) | Brand infra ready | DRAFT COMPLETE |
| 2 | BSides (regional, e.g., BSides NoVA/DC) | 20-min talk CFP | Next open CFP | PENDING |
| 3 | DEF CON AI Village | Talk or poster | DEF CON 2026 CFP | PENDING |

## 3) Blog Post

- **Title:** "How Fragile Is Your IDS? Adversarial ML Attacks on Network Intrusion Detection"
- **Content:** RQ summary, key figures (ASR curves, defense comparison), feature controllability insight
- **Source:** `FINDINGS.md` + `outputs/figures/`
- **Blocked on:** Brand infrastructure (Hugo site deployment)

## 4) Conference Submissions

### BSides CFP
- **Abstract focus:** Practical defense recommendations for SOC teams
- **Demo:** Live notebook showing noise attack on trained IDS model
- **Artifacts:** Slides (from figures), demo notebook, 1-page abstract

### DEF CON AI Village
- **Abstract focus:** Feature controllability as a new defensive primitive
- **Format:** 15-20 min talk or poster
- **Artifacts:** Slides, poster PDF, code repository link

## 5) Content Reuse Policy

- Blog post is the canonical source; conference talks derive from it
- All claims must trace to `FINDINGS.md` evidence
- No results beyond what is in `outputs/` (no unpublished data)

## 6) Dependencies

```
FINDINGS.md → Blog draft → Brand infra → Publish → Conference CFPs
```
