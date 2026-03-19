# Content Plan — FP-01 Adversarial IDS

> **Project:** FP-01 | **Created:** 2026-03-19

---

## Content Pipeline

| ID | Title | Channel | Status | Target Date | Dependencies |
|----|-------|---------|--------|-------------|-------------|
| C-01 | Feature Controllability: The Missing Variable in Adversarial IDS Research | Blog (rexcoleman.dev) | DRAFTED | 2026-03-24 | `blog/draft.md` complete |
| C-02 | LinkedIn announcement post | LinkedIn | DRAFTED | 2026-03-24 | `blog/linkedin_post.md`, C-01 published |
| C-03 | Substack intro / newsletter teaser | Substack | DRAFTED | 2026-03-24 | `blog/substack_intro.md`, C-01 published |
| C-04 | BSides conference abstract | BSides CFP | DRAFTED | TBD (CFP deadline) | `blog/conference_abstract.md` |
| C-05 | Twitter/X thread (5 tweets) | Twitter/X | NOT STARTED | After C-01 | Key metrics from FINDINGS.md |
| C-06 | Reddit r/MachineLearning post | Reddit | NOT STARTED | After C-01 | Focus on negative results (H-5, feature squeezing) |

---

## Content Hooks (from FINDINGS.md)

| Hook | Best Channel | Audience |
|------|-------------|----------|
| "Your IDS adversarial defense is testing the wrong threat model" | BSides talk, blog headline | Security practitioners |
| Feature controllability as general principle | Long-form blog, conference | ML security researchers |
| Adversarial training is a 61% solution | LinkedIn, Twitter thread | Engineering leaders |
| Feature squeezing is dead on tabular data | Blog section, Reddit | Data scientists, ML engineers |
| The 75% data plateau | Cross-post dev.to/Hashnode | Data science community |
| SVM/LightGBM fail under IDS constraints | Technical appendix | Algorithm selection guidance |

---

## Brand Alignment

All content must reinforce the "architect who ships" identity (DEC-026):
- Emphasize the **system-level design decision** (feature controllability framework), not just the ML results
- Position as security architecture thinking applied to ML, not ML applied to security
- Cross-reference govML as the governance infrastructure that enabled structured experimentation
- Link to the controllability principle's validation across 4 domains (FP-01, FP-02, FP-03, FP-05)

---

## Publication Sequence

1. **Blog post** (C-01) — canonical long-form, published on rexcoleman.dev
2. **LinkedIn + Substack** (C-02, C-03) — same day as blog, drive traffic
3. **Twitter thread** (C-05) — 24 hours after blog for second-wave engagement
4. **Reddit** (C-06) — 48 hours after blog, framed as "negative results" discussion
5. **BSides CFP** (C-04) — submit when next CFP opens

---

## Figures for Publication

| Figure | Source | Used In |
|--------|--------|---------|
| `figures/algorithm_comparison.png` | `scripts/make_report_figures.py` | C-01 (blog) |
| `figures/defense_comparison.png` | `scripts/make_report_figures.py` | C-01, C-04 |
| `figures/adversarial_budget_curves.png` | `scripts/make_report_figures.py` | C-01 |
| `figures/learning_curves.png` | `scripts/run_learning_curves.py` | C-01 |
| `figures/per_class_heatmap.png` | `scripts/make_report_figures.py` | C-01 |
| `blog/images/controllable_vs_observable.png` | copied from figures/ | C-01, C-02 |
| `blog/images/defense_recovery.png` | copied from figures/ | C-01, C-03 |

---

## Metrics to Track

| Metric | Target | Measurement |
|--------|--------|-------------|
| Blog views (week 1) | 500+ | Analytics |
| LinkedIn impressions | 2,000+ | LinkedIn analytics |
| GitHub stars (delta) | +10 | GitHub |
| BSides acceptance | Y/N | CFP result |
| Substack subscribers (delta) | +25 | Substack dashboard |
