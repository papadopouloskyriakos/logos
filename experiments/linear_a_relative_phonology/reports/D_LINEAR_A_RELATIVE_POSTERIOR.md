# D5 — Linear A Relative Posterior

**Task D5.** Produce the honest end-state deliverable of the relative-phonology campaign: **anonymous
posterior relative classes for Linear A signs**, with explicit per-sign uncertainty
(P(class_1), P(class_2), stability), combining the D1/D2 multi-view fused-latent features and
honouring the D3/D4 seed reality. **No phonetic value is assigned to any sign or class.**

- Script: `scripts/d5_relative_posterior.py` · Data: `data/D_la_posterior.json`
- Seed `20260708` · as_of `2026-07-07` · Highest layer **L2/L3** · Licences **NOT_EARNED**
- Non-circular: known Linear B syllabic values are used **only** to grade the anonymous partition;
  every model input is a distributional/structural statistic over sign identities.

## What was produced

For each of the **54** graded LA signs (clean CV/V syllabograms, freq ≥ 8; 5 pure-vowel signs) the
posterior gives:

- **Primary anonymous partition (K=2):** `p_class_1`, `p_class_2` (bootstrap membership over
  B=400 corpus resamples, Hungarian-aligned to the reference fit), `stability` (modal fraction),
  `coassign_stability` (label-free co-clustering), `loo_view_agreement`.
- **Fine anonymous partition (K=6, matching D1):** full 6-way posterior + modal class + stability.
- **Anonymous affixation paradigm (L2/L3):** per-sign edge/interior role from stem-affixation
  profiles (the LA-real word-INITIAL axis), NO phonetic value implied.

## Headline measured numbers

| Quantity | Value |
|---|---|
| Graded signs / pure-vowel signs | 54 / 5 |
| Fused latent dim (PCA 80% var) | K=4 |
| Fused macro **vowel** AUC (perm-p) | **0.538 (p=0.096)** → NULL |
| Fused C/V contrast AUC | 0.882 (wave-1 axis, REFUTED — reported not credited) |
| K=2 partition vs **vowel** benchmark | adjMI **0.032**, perm-p **0.140** → NULL |
| K=2 partition vs **C/V** benchmark | adjMI 0.040, perm-p 0.146 → NULL |
| K=6 partition vs vowel / vs C/V | adjMI 0.046 p=0.158 / 0.031 p=0.138 → NULL |
| K=2 stability (modal frac): mean / median / min | 0.755 / 0.802 / 0.505 |
| K=2 signs with stability ≥0.8 / ≥0.9 | 52% / **0%** |
| K=6 stability mean; signs ≥0.5 | 0.653; 81% |
| Bootstrap replicates used | 400 |

**Leave-one-view-out agreement (K=2 partition):**

| drop | agreement w/ reference |
|---|---|
| −FORMULA | 1.000 |
| −POSITION | 0.963 |
| −SUBSTITUTION | 0.926 |
| −MORPHOLOGY | 0.722 |
| **−SITE** | **0.500 (chance)** |

## Interpretation (honest)

1. **The posterior classes are real anonymous *relative* structure, not phonetics.** A stable binary
   partition exists (52% of signs land in one K=2 class ≥80% of bootstraps), but it **does not align
   with vowel identity or the C/V split beyond chance** (all AMI perm-p ∈ [0.14, 0.16], matching D1).
   The fused latent recovers vowels at AUC 0.538 (perm-p 0.096) — a NULL.

2. **The primary binary axis is provenance/dispersion + morphology, not sound.** Dropping the SITE
   view collapses the K=2 partition to chance (0.500); dropping MORPHOLOGY costs 0.28. Class C2_1
   (n=31) is higher-dispersion (mean 16.4 sites, more suffix/mid stems) vs C2_0 (n=23, 9.8 sites,
   more prefix-weighted). Vowel composition is scrambled across both classes (C2_0: A5 E7 O4 U5 I2;
   C2_1: A11 I8 U7 E4 O1) — the split is administrative/geographic, not phonological.

3. **No sign reaches high phonological confidence.** 0% of signs have K=2 stability ≥0.9, and the
   partition they are stable *within* is a value-blind structural one. There is no basis to promote
   any sign above **L3**.

4. **Seed reality honoured (D3/D4).** SEED_A = 0 secure value seeds; the seed-propagation "0.87" is a
   frequency artifact (pure frequency ranking AUC=0.872 ≥ seed-prop kv4 AUC=0.784; initial-rate alone
   0.759, no seeds). LA sits at the **k=0 pre-frontier origin**: only value-blind channels are
   available, which the Linear B control measures at the null floor. **No class can be attached to a
   phonetic value.**

## What is NOT determined

- **No phonetic value** — no `A_SIGN=/a/`, no vowel, no consonant — for any sign or class.
- **Vowel identity is not recoverable** (fused AUC 0.538, perm-p 0.096; K=2/K=6 partitions NULL vs
  vowel benchmark).
- **C/V split not recoverable value-independently** — the wave-1 position→C/V axis is REFUTED under
  multiplicity + oriented null; any C/V AUC here is reported, never credited.
- **No secure seed** (SEED_A=0); seed-propagation gains are a frequency artifact.
- **Cross-script value transfer is NULL** — classes are relative structure internal to Linear A.
- **Class labels are anonymous** — C2_0/C2_1/C6_j carry only KMeans ordering, no external meaning.

## Verdict

**ANONYMOUS_RELATIVE_STRUCTURE_ONLY (L2/L3).** A stable, bootstrap-quantified relative partition of
the LA sign inventory exists and is dominated by provenance-dispersion + word-initial affixation
structure; it carries **no** phonetic signal (vowel/CV alignment NULL at every K). The deliverable is
the anonymous posterior + uncertainties, with phonetic values explicitly **NOT_EARNED**.
