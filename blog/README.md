# Blog Content — FP-01 Adversarial IDS

## Contents

| File | Description | Status |
|------|-------------|--------|
| `draft.md` | Long-form blog post for rexcoleman.dev | Draft |
| `linkedin_post.md` | LinkedIn announcement post | Draft |
| `substack_intro.md` | Substack newsletter teaser | Draft |
| `conference_abstract.md` | BSides / DEF CON AI Village abstract | Draft |
| `adversarial_ids_threat_model.md` | Threat model reference (STRIDE) | Complete |

## Images

| File | Description | Source |
|------|-------------|--------|
| `images/adversarial_budget_curves.png` | F1 vs epsilon budget curves | `figures/` |
| `images/algorithm_comparison.png` | 5-algorithm macro-F1 comparison | `figures/` |
| `images/budget_curve_XGBoost_seed42.png` | XGBoost-specific budget curve | `figures/` |
| `images/class_distribution.png` | CICIDS2017 class distribution | `figures/` |
| `images/controllable_vs_observable.png` | Feature controllability split | `figures/` |
| `images/defense_comparison.png` | Defense strategy comparison | `figures/` |
| `images/defense_recovery.png` | Defense recovery bar chart | `figures/` |
| `images/learning_curves.png` | Learning curves across train fractions | `figures/` |
| `images/per_class_f1.png` | Per-class F1 scores | `figures/` |
| `images/per_class_heatmap.png` | Feature importance by attack class | `figures/` |

## Publication Workflow

1. Finalize `draft.md` with inline image references
2. Convert to Hugo-compatible markdown for rexcoleman.dev
3. Publish blog post
4. Post `linkedin_post.md` and send `substack_intro.md` same day
5. Submit `conference_abstract.md` at next BSides CFP
