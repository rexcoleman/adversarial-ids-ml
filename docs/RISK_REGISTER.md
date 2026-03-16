# RISK REGISTER

<!-- version: 1.0 -->
<!-- created: 2026-03-16 -->

## 1) Purpose

Tracks known risks, their status, and mitigations for the adversarial IDS project.

## 2) Active Risks

| ID | Risk | Severity | Likelihood | Status | Mitigation |
|----|------|----------|-----------|--------|------------|
| R-1 | sklearn version mismatch breaks ART wrapper | HIGH | LOW | MITIGATED | Pinned sklearn==1.4.x in requirements.txt; ART SklearnClassifier tested with `pytest.importorskip`; version mismatch triggers skip, not failure |
| R-2 | CICIDS2017 dataset age (2017 vintage) | MEDIUM | CERTAIN | ACCEPTED | Disclosed in FINDINGS.md as threat-to-validity. Modern attacks differ, but CICIDS2017 remains the standard IDS benchmark. Results framed as methodology validation, not production claims |
| R-3 | Noise-only attacks lack gradient signal | MEDIUM | CERTAIN | ACCEPTED | ZOO and HopSkipJump available as gradient-free alternatives but prohibitively slow on sklearn models. Noise baseline is the primary attack; acknowledged in FINDINGS.md as conservative lower bound on adversarial vulnerability |
| R-4 | Feature mask may not reflect real attacker capabilities | MEDIUM | MEDIUM | MITIGATED | 57/14 split based on domain analysis (packet-level vs infrastructure features). Sensitivity analysis at multiple epsilon values covers range of attacker capability |
| R-5 | 10% sample may miss rare attack classes | LOW | MEDIUM | MITIGATED | Stratified sampling preserves class ratios. Rare classes with <3 samples dropped and disclosed. Full-data run available as validation |

## 3) Resolved Risks

| ID | Risk | Resolution |
|----|------|------------|
| R-6 | Memory overflow on full CICIDS2017 (2.8M rows) | Resolved by 10% sampling + Azure B2ms 8GiB RAM sufficient |
| R-7 | Non-deterministic sklearn models | Resolved by explicit `random_state=seed` on all estimators |

## 4) Change Control

New risks or status changes require a commit with `RISK_UPDATE` tag.
