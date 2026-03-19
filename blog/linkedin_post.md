# LinkedIn Post — FP-01 Adversarial IDS

> **Status:** Draft | **Target:** Post when blog goes live

---

**Your IDS adversarial defense is probably testing the wrong threat model.**

Most adversarial ML research on intrusion detection perturbs all features equally. But network attackers can't control TCP flags set by the OS stack or destination ports determined by the protocol.

I built an adversarial ML pipeline on CICIDS2017 (2.83M flows, 15 attack classes) that splits 78 features into what attackers can actually control (57) vs. what only defenders observe (14).

The results changed how I think about adversarial defense:

- Constraining attacks to controllable features reduces XGBoost attack success by 35%
- Adversarial training recovers 61% of lost performance — decent, not great
- Feature squeezing recovers 0% — completely useless on tabular data
- Monitoring uncontrollable features catches 100% of naive attacks

The best defense is architectural, not learned. Security architecture (which features to monitor) outperforms learned defenses (how to train the model).

This feature controllability framework has since been validated across 4 security domains — IDS, vulnerability prediction, agent red-teaming, and post-quantum migration.

Full writeup with code, figures, and methodology: [LINK]

Built with govML for project governance. 70+ tests, 5 seeds, structured hypothesis registry.

#MachineLearning #Cybersecurity #AdversarialML #SecurityArchitecture #BuilderInPublic

---

> **Post notes:**
> - Attach `blog/images/defense_recovery.png` as the post image
> - Tag: Georgia Tech, relevant ML security researchers
> - Post Tuesday or Wednesday morning (highest LinkedIn engagement)
