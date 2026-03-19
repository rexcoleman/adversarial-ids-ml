# Substack Newsletter Intro — FP-01 Adversarial IDS

> **Status:** Draft | **Target:** Send when blog goes live

---

**Subject line:** The adversarial ML metric everyone gets wrong (and what to measure instead)

---

I just published a deep dive into adversarial ML on intrusion detection systems, and the central finding surprised me.

Standard adversarial testing perturbs all input features — but network attackers can only control about 73% of the features in a typical IDS dataset. When you restrict testing to what attackers can actually manipulate, the threat picture changes dramatically. XGBoost attack success drops by 35%. And the best defense isn't adversarial training (61% recovery) — it's monitoring the features attackers cannot control (100% detection of naive attacks).

In this post I cover:

- **The feature controllability framework** — splitting IDS features by who controls them
- **Why feature squeezing is dead on tabular data** — 0% recovery, complete failure
- **The 75% data plateau** — more training data actually hurts performance past a threshold
- **What H-5 REFUTED means** — SVM and LightGBM fail under real IDS constraints, and that matters
- **The controllability principle** — how this framework transfers to vulnerability prediction, agent security, and post-quantum migration

All code is open source. All experiments use structured hypothesis registries and multi-seed validation.

Read the full post: [LINK]

---

This is part of my builder-in-public series on AI security architecture. If you are building ML systems for security applications, or you are interested in how adversarial ML works in practice (not just on MNIST), this one is for you.

Rex

---

> **Newsletter notes:**
> - Include `blog/images/controllable_vs_observable.png` as hero image
> - Link to GitHub repo
> - CTA: "Reply with your experience testing adversarial robustness on tabular data"
