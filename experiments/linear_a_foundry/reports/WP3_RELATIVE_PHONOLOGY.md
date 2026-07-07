# WP3 — relative phonology (WP3.1 vowel/consonant recovery)

`scripts/wp3_cv_recovery.py` → `data/wp3_cv_recovery.json`. Multi-feature C/V classifier, trained + 7-fold
cross-validated on known-truth Linear B (vowels {A,E,I,O,U}), 200 permutation nulls; applied to Linear A.
Non-circular (distributional/position features over sign identities only). **`CV_PARTITION_RECOVERED` on LB.**

## Result + the honest ablation decomposition

| model (LB 7-fold CV AUC, vowel recovery) | AUC | reads as |
|---|---|---|
| all 7 features | **0.835** (perm p=0.01) | strong |
| `log_freq` **only** | **0.838** | a **typological prior** (vowels are among the most frequent signs) — relabeling-invariant per-sign, applied via external linguistic knowledge, **not corpus structure** |
| minus `log_freq` | 0.783 | corpus structure + neighbor entropy |
| **position-only** (initial/final/mean-pos) | **0.67** | the **genuine relabeling-variant corpus structure** — modest but above chance |

**Interpretation.** The C/V symmetry *is* broken by internal evidence — but the decomposition matters:
- **Frequency (0.838)** is the strong channel, and it is a *typological prior* (vowels frequent), not
  corpus-internal value evidence. It reduces the equivalence classes only through external knowledge about
  value-space structure. Legitimate (Ventris/Kober used frequency + position) but must be labelled as prior.
- **Position (0.67)** is the genuine corpus-structural symmetry-breaker: word-initial/position profile
  distinguishes vowels from consonants *independently of frequency*, above chance.

This refines WP1's claim precisely: internal corpus structure breaks the C/V symmetry **weakly but
significantly** (position AUC 0.67); combined with the standard typological frequency prior it reaches AUC
0.835. Neither pure corpus statistics with *no* prior (relabeling-invariant, WP1 theorem) nor a prior with no
corpus (no discrimination) suffices — the symmetry breaks only by *coupling* the two, exactly as the WP1
theorem states.

## Linear A application

The LB-trained classifier ranks LA signs **A, I** at the top (vowel-corresponding), consistent with WP1 — but
the LB-calibrated probabilities do **not** transfer (all < 0.05; LB→LA domain shift: shorter LA words, different
frequency structure), so LA yields a candidate *ranking*, not a calibrated partition. **WP3 follow-up:** an
LA-internal unsupervised 2-class clustering on the position features (avoiding cross-script calibration), plus
the scribal-substitution similarity graph (WP3.2) and morphology re-audit (WP3.4), to build a calibrated LA
C/V partition + similarity metric.

## Status

`CV_PARTITION_RECOVERED` (LB, validated). Genuine but modest internal symmetry-breaking; the equivalence-class
reduction is real (C/V partition recoverable with a typological prior; position-only weaker). Continues into
WP3.2 (substitutions) and WP3.4 (morphology). Not a reading; no licence earned.
