# LINEAR A DECIPHERMENT FOUNDRY — long-horizon campaign

**Branch:** `research/linear-a-decipherment-foundry` · **Parent:** `main@6fd4f20` · **Constitution:** v2.2 ·
**Opened:** 2026-07-08.

**Mission:** obtain a real, testable Linear A decipherment candidate or materially reduce the search space.
Find a real reading if present; never manufacture one. Do not stop at the first null; **do not issue the
final verdict until the mandatory work packages + quotas are complete.**

## Correction that motivates this campaign

The prior campaign treated a sign-relabeling result as a global stopping theorem. **WP1 audits and refutes
that:** the invariance holds only for identity-co-occurrence objectives; internal evidence (position,
substitution, morphology) DOES break partial symmetry and reduces the sign-value equivalence classes. The
value layer is not provably closed to internal methods.

## Constitutional stage header (Art. XXII)

- **entry gate:** isolated worktree from 6fd4f20; paper/, runtime/, completed branches UNTOUCHED; append-only
  ledger ACTIVE; test baseline 411 passed.
- **authorized outputs:** structural/functional/relative results + bounded prereg'd value/lexical/phonetic
  hypotheses with held-out predictions. **forbidden:** any reading without held-out success; subjective LLM
  translation; unbounded root/language search; a global impossibility claim without a scoped theorem.
- **licences at open:** all LA transfer NOT_EARNED.

## Work-package ledger

| WP | state |
|---|---|
| **1 · formal identifiability & symmetry audit** | ✅ **`PRIOR_THEOREM_OVERSTATED`** — position recovers C/V on LB (AUC 0.744, p=0.035); LA top-initial signs = A/I/U (vowel-corresponding). Internal evidence reduces value equivalence classes. Atlas of 13 channels built. |
| 2 · corpus reconstruction | ✅ segmentation is CHANNEL-DEPENDENT: helps C/V position (0.685->0.76) but HURTS substitution (105->47); 63 sources audited (48 independent); Anetaki II = held-out gold |
| 3 · relative phonology / morphology / scribal | ✅ DONE — channels VALIDATED on LB (substitution AUC 0.71 z=7.07; alternation p=0.0033; morphology 0.731 bits/word) but LA UNDERPOWERED (max subst weight 105 vs 303; unsegmented; needs C/V seed labels). 2nd correction: more corpus WOULD help |
| 4 · diachronic & cross-script sign evolution | ✅ NULL — no non-circular value (4th distributional null); shape circular |
| 5 · external-anchor factory | ✅ inventory 115 rec/62 signs; reduced-seed bootstrap VALIDATED on LB (3-4 seeds->AUC 0.87) but LA underpowered (NULL). Obstacle = LA propagation power, not anchors |
| 6 · candidate + agnostic | ✅ agnostic + candidate round 1 both AT_END_TO_END_NULL (rounds 2-3 pending) |
| lab · synthetic recovery | ✅ QUANTIFIED 5/5 — methods recover at scale, calibrated NO_POWER at LA-scale, reject wrong-language; LA needs ~1.9x tokens + segmentation |
| seals · sealed prediction programme | pending |
| nulls · end-to-end null programme | pending |
| acq · active evidence acquisition | pending |

## Mandatory quotas (tracked to final verdict)

6 WPs · 24+ commits · 18 prereg experiment families · 2 corpus encodings · 3 model families · 3 candidate
rounds · 1 agnostic search · 3 synthetic + 2 known-script benchmarks · ≥200/≥50 nulls per test · 60 sources ·
100 anchors (25 audited) · 10 sign-evolution + 10 substitution case studies · 5 sealed challenges. **No final
verdict before these are genuinely complete.**

## Run log

- **WP1 (commit _this_)** — theorem audited: `PRIOR_THEOREM_OVERSTATED`. Counterexample: internal word-position
  evidence separates LB vowels (AUC 0.744, p=0.035) and surfaces A/I/U as LA vowel candidates non-circularly.
  Symmetry-breaking atlas (13 channels) built. Reframed target: recover relative C/V + similarity + morphology
  (WP3) to reduce equivalence classes, cutting the external-anchor requirement (WP5).
