# WP4 (cross-script) + WP5 (anchors + reduced-seed bootstrap)

## WP4 — cross-script sign evolution → `NULL` (no non-circular value gain)
Three channels kept separate (shape/Salgarella homomorphy, admin-distributional, chronology).
- Known-truth calibration fires: the value-blind SHAPE channel recovers the Steele-Meissner LB↔Cypriot
  stable-11 (11/11, Fisher p=1.6e-5) — **but convergent-CONFOUNDED** (Salgarella homomorphy and S&M stability
  both proxy the same "core stable syllabogram" latent, not two independent signals).
- The genuinely **non-circular distributional channel is at the shuffled null** (56-sign leave-one-sign-out:
  R@1=0.000, R@5=0.071 vs null 0.066, perm-p 0.50–0.60; the 10 highest-certainty core signs sit at median
  true-partner rank 48/89). **Fourth independent null** of the distributional cross-script channel.
- Shape→LB-value is **circular** (Salgarella grade = LB identity; recall@1=1.0 by construction; ≤0.75 cap).
- **Verdict: no non-circular cross-script value constraint. Shared-AB held-out hypothesis REFUTED (non-circular).**

## WP5 — anchor inventory + reduced-seed C/V bootstrap → `SIGNAL_VALIDATED` (LB), `NULL` (LA)
**Inventory (a):** 115 provenance records / 62 signs across 3 independent channels (47 lexical/onomastic, 57
homomorphy, 11 Cypriot). Independence reconciliation is the key point: 26 signs are graded "multi-channel
independent," but the frozen gate recovered only **2 held-out** (I, RI), one-toponym-deep — nominal
independence overstates held-out survivability by ~13×. Only 3 pure one-deep pins remain; 31 signs are
structural-only (identity, no value-pin).

**Reduced-seed bootstrap (b) — the pivotal test.** Semi-supervised label spreading over the WP3.1-position +
WP3.2-substitution affinity graph (log_freq excluded from propagation; frequency enters only via seed choice):
- Unsupervised NULL reproduced at chance (held-out vowel AUC 0.568).
- **~3–4 CORRECT C/V seeds → held-out AUC 0.78 (kv=3) → 0.82/0.87 (kv=4 pos/pos+sub)** on known-truth LB —
  from the unsupervised floor to ≈ the supervised ceiling (0.835). **The mechanism is validated: a handful of
  correct seeds + internal propagation recovers C/V.**
- **Null 1 (honest):** *frequency-seeding fails* — the literal most-frequent signs are high-freq consonants
  (TO/JO/KO), so freq-seed AUC peaks 0.726, not above a 200-draw random-seed null (p=0.13–0.25). You need
  *correct* seeds, not just frequent ones.
- **Null 2 (the obstacle):** *LA transfer is NULL* — seeding LA top-freq (A/I/JA) + propagating leaves
  held-out signs flat (~0.01–0.016), true vowel U buried below consonants. No held-out LA vowel recovered.

## Convergent conclusion — the obstacle is precisely located
The bottleneck is **neither** internal value-blindness (WP1 refuted) **nor** anchor availability (WP5: A, I, U
are attested Cypriot-stable + homomorphic seeds). It is **Linear A's internal propagation power** — the
affinity graph from LA's position/substitution features is too weak to spread the few available seeds into a
full partition. This converges with WP3.2b's finding that LA is ~1.7× below the substitution clean regime.
**The value layer is reopened and the obstacle is quantified: LA-side corpus/segmentation power, not a
theorem and not missing anchors.** No reading; no licence. This materially sharpens the search space (a
mission objective).
