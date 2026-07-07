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

---

## WP3 core complete — relative channels VALIDATED on LB, LA UNDERPOWERED (a second correction)

| sub | LB (known-truth) | LA | verdict |
|---|---|---|---|
| **3.2 scribal substitution** | strong edges recover same-C/same-V at **1.39× the degree-preserving null, z=7.07, p=0.0033**; hub-normalized weight→feature AUC **0.714** — an INDEPENDENT relational channel (not the frequency prior). Signal is in edge WEIGHT, not existence. | max substitution weight **105** cannot reach the clean regime (LB 303); strong subgraph a candidate, unverified | **`SIGNAL_VALIDATED`** (LB); LA candidate-underpowered |
| **3.1b C/V clustering** | unsupervised 2-class clustering is at chance (ARI ~0, p 0.42–0.50) — the dominant variance axis (frequency) is orthogonal to the 5-vs-69 C/V split; supervised WP3.1 got 0.835, so labels are required | withheld (fail-closed) | **`NULL`** |
| **3.4 morphology** | detector validated (LB +0.731 bits/word, 704 stems) | LA gain is a whole-wordform-recurrence artifact, no productive paradigms | **`NULL`** |
| **3.3 orthographic alternation** | validated (recovers Greek inflectional alternations, same-V 1.15×, same-C 1.45×, p=0.0033) | LA unsegmented (inscription=unit): only 1 pair reaches support≥3 | **`NO_POWER`** (LA data-limited) |

**The corrected obstacle (sharper than the prior campaign's).** The relative symmetry-breaking channels are
**real and validated on Linear B** — internal evidence is *not* value-blind (WP1). But **Linear A is
underpowered** for them: 1,270 word-units vs LB's 13,562; unsegmented (kills alternations); max substitution
weight 105 vs the ~120 where the signal is clean. The obstacle is **corpus power for the relative channels**,
not a symmetry theorem.

**Second correction to the prior campaign:** it claimed "more corpus cannot help the value layer (value-blind)."
That is now **refuted** — more LA corpus (or ~10× the current mass) would push the substitution weights into
the validated clean regime, provide segmentation for alternations, and give morphology the depth it lacks,
each of which reduces the value equivalence classes. And the C/V partition needs only a **few seed labels**
(unsupervised fails; supervised works) — a *reduced* external-anchor requirement, exactly as WP1 predicted.
