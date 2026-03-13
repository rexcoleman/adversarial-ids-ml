# Tradeoff Log

> **Purpose:** Document every significant architectural decision with alternatives considered. This is D4 evidence (first-principles reasoning under uncertainty).
> **Rule:** No entry without at least 2 alternatives and a rationale.

---

| # | Decision | Alternatives Considered | Chosen | Rationale | Date |
|---|----------|------------------------|--------|-----------|------|
| TD-01 | Dataset selection | CICIDS2017, NSL-KDD, UNSW-NB15, CIC-IDS2018 | CICIDS2017 | Most widely benchmarked (reproducibility), modern traffic patterns (2017), 15 attack classes (granular analysis), freely available. NSL-KDD is older (1999 traffic). UNSW-NB15 has fewer published baselines. | 2026-03-13 |
| TD-02 | Attack method library | Custom implementation, IBM ART, CleverHans, Foolbox | IBM ART | MIT license, feature-space attack support (not just image-space), active maintenance, built-in defenses for comparison. CleverHans is TF-only. Foolbox lacks feature-space attacks. | 2026-03-13 |
| TD-03 | govML profile | supervised, unsupervised, full | supervised + manual ADVERSARIAL_EVALUATION | Baseline classifiers are supervised. Anomaly detectors added manually. Full profile includes templates we don't need (RL, build system). | 2026-03-13 |
| TD-04 | Data source | Official CIC portal (manual download), Kaggle mirror | Official CIC portal | Security community credibility — citing official UNB source vs Kaggle mirror matters for publication trust. Official is full dataset (2.83M flows). Kaggle versions may be subsets. Trade-off: manual download + scp vs one-line API call. | 2026-03-13 |
| TD-05 | PyTorch variant | Default (CUDA, ~2GB), CPU-only (~185MB) | CPU-only | VM has no GPU (Azure B2ms). 29GB disk too small for CUDA build. CPU-only is 10x smaller with zero functionality loss — all experiments are scikit-learn/XGBoost. Torch needed only for ART's PyTorch estimators. | 2026-03-13 |
| TD-06 | setuptools version | Latest (82.0.1), pinned <72 | Pinned <72 | setuptools 72+ removed pkg_resources. ART 1.17.1 depends on it. No way around this until ART releases a fix. | 2026-03-13 |
