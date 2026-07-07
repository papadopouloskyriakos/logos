# WP-A synthesis — CV_ANALOGUE_REFUTED + ERRATUM to Foundry C1

**Verdict (mechanical, A6):** `CV_ANALOGUE_REFUTED`. The Foundry position/distributional C/V-symmetry-break does
not survive a proper end-to-end null battery, independent replication, or multiplicity correction.

## What reproduced, and what did not
- **A1 REPRODUCED (exactly):** single-feature initial_rate AUC 0.744 (1-sided p 0.035), 7-feature 7-fold CV AUC
  0.835 (1-sided perm_p 0.01), ablation log_freq_only 0.838 / position_only 0.67. The numbers are real and
  correctly transcribed. Also surfaced a filter bug: `exp(log(20))=19.999…<20` silently drops 3 signs (*47,*63,TA2);
  clean integer freq≥20 → 77 signs, on which position_only collapses 0.67→**0.586** (≈chance).
- **A2 MULTIPLICITY:** the single-feature position claim survives NO correction (Bonferroni×7 0.245, ×13-atlas
  0.455, Holm 0.36, BH-FDR q 0.168, position-subfamily best-of-K 0.163). Position is not even the best channel —
  **log_freq (0.878) and rnbr_ent (0.800) beat it**; the only family-wise survivor is log-frequency, a prior.
- **A3 EXPLORATORY_FREQUENCY_ARTIFACT:** M1 replicates the point estimate but two independent unsupervised models
  fail (GMM p 0.131 ARI 0.002; HMM p 0.109 ARI 0.058); oriented (2-sided) null p **0.146**; only 3/5 vowels;
  dropping A → AUC 0.448.
- **A4 REFUTE-AS-STATED:** survives site/series/formula/document/word-family/chronology grouping, BUT the
  **frequency-band-disjoint** split collapses it (position-only 0.481 = chance; all-feats 0.658 n.s.). 4/5 vowels
  in the top log-freq quartile → "vowels are frequent," not a position break. Domain-robustness cannot count
  because every passing grouping preserves frequency rank.
- **A5 REFUTE + NO_POWER:** the 105-cell degradation surface is a flat non-significant plateau (no cell beats its
  own null-95; undegraded LB itself p≈0.16). Nothing to degrade; LA operating point at/below chance.
- **A6 CV_ANALOGUE_REFUTED:** random labels reach AUC≥0.828 ~15% of the time (p 0.146); frequency-matched
  within-quartile permutation p 0.130; destroying within-word order leaves AUC unchanged (0.839 vs 0.828) → no
  positional/order signal; best_of_model adaptive null fails (p 0.129).

## ERRATUM (Art. XVII, append-only — supersedes, does not delete)
The **Foundry campaign correction C1** ("internal methods are not value-blind because position recovers C/V on
opaque LB, AUC 0.744, p=0.035") is **SUPERSEDED**. That specific single-feature position result is a best-of-7
selection that does not survive multiplicity, is not the best channel, and the multi-feature 0.835 is a
**frequency typological prior**, not corpus-internal positional/relative-phonological structure. Under an honest
two-sided null it is not significant even before multiplicity (p≈0.146).

**What this does and does not change.** It does NOT resurrect a *proof* of value-blindness (no such theorem is
established either — see the constraint-expansion erratum). It DOES remove position/distribution as a
demonstrated corpus-internal symmetry-breaker. The "not value-blind" question now rests ENTIRELY on the
**substitution channel** (foundations C3: consonant-held/vocalic-alternation axis, AUC 0.744, degree-preserving
null lift up to 2.5×, p≈0.003) — which used a stronger (degree/frequency-preserving) null but has NOT yet had the
independent-replication + grouped + multiplicity audit that just refuted the position channel. That audit is now
the campaign's load-bearing task (WP-C4/C5 + WP-D). Frequency remains a legitimate but EXTERNAL prior.

**Highest earned claim layer unchanged: L2 (structural: a high-frequency sign class exists). No phonetic/relative
licence earned. All LA transfer licences NOT_EARNED.**
