# A3 — Independent Replications of "Internal Structure Recovers C/V on Opaque Linear B"

**Constitution v2.2 | claim layer L3 (structure) | seed 20260708 | 2026-07-07**
Script: `scripts/a3_replications.py` · Data: `data/A3_replications.json`
Corpus: DĀMOS Linear B = 13,562 word-segmented wordforms; 77 signs with freq ≥ 20; 5 true vowels {A,E,I,O,U}.
**Non-circular:** known LB vowel values grade the benchmark ONLY, never enter as a model input.

## The claim under audit (Foundry WP1/WP3)

Foundry reported that position/distributional structure breaks the C/V relabeling symmetry on opaque LB:
single-feature word-initial-rate AUC **0.744** (perm p≈0.035); a 7-feature logistic classifier with 7-fold CV
AUC **0.835** (perm p 0.01, n_null 200); verdict `CV_PARTITION_RECOVERED`. The honest questions: does it survive
a proper null, independent re-implementation, grouped CV, and multiplicity — and is it real *structure* or a
*frequency prior*?

## Three genuinely distinct implementations

| Model | Family | Uses labels to TRAIN? | LB C/V recovery (AUC) | Honest perm-p | ARI |
|---|---|---|---|---|---|
| **A_MODEL_1** supervised logistic (grouped-by-sign 7-fold CV) | discriminative | yes | **0.828** | **0.006** one-sided / **0.146** oriented | — |
| **A_MODEL_2** 2-component Gaussian mixture (EM) | generative, **unsupervised** | no | **0.704** | **0.131** (oriented) | **0.002** |
| **A_MODEL_3** 2-state HMM over sequences (Baum–Welch) | sequence, **unsupervised** | no | **0.719** | **0.109** (oriented) | **0.058** |

Models 2 and 3 use the true labels *only* to orient/score the recovered latent partition; the partition itself
is inferred with no phonetic supervision. Their permutation nulls are oriented (max(a,1−a)) because orientation
is a scoring-time free parameter — the honest null for an unsupervised model.

## Result 1 — The supervised point estimate replicates; its *significance* does not survive an honest null

A_MODEL_1 reproduces Foundry's headline (CV AUC 0.828 ≈ 0.835). But Foundry's p=0.01 is a **one-sided** null.
With only **5 positives**, an oriented (two-sided) label-permutation null has a 95th-percentile AUC of **0.908** —
a *random* labeling beats AUC 0.83 about **15%** of the time. Reconciliation (n=2000 perms):

- one-sided perm-p = **0.006** (reproduces Foundry's 0.01)
- oriented perm-p = **0.146** (not significant)

For a supervised model the one-sided null is defensible, so M1 alone does not refute Foundry. The refutation
comes from robustness and from the two independent models.

## Result 2 — The "signal" is a FREQUENCY prior, not word-position structure

Feature decomposition of M1 (one-sided p, the framing most favorable to the claim):

| Feature set | AUC | one-sided p |
|---|---|---|
| all 7 features | 0.828 | 0.006 |
| **log_freq only** (typological prior) | 0.792 | **0.004** ← strongest single driver |
| minus log_freq (6 feats) | 0.778 | 0.020 |
| **pure word-position** (initial/final/mean_pos) | 0.631 | **0.098 — NOT significant** |

The dominant M1 weight is `log_freq` (**1.285**). The neighbour-entropy features that carry the "minus-log_freq"
variant are themselves frequency proxies: Pearson r with log_freq = **+0.785** (lnbr_ent), **+0.762** (rnbr_ent).
The only frequency-*independent* features are initial/final/mean_pos (|r|≤0.15) — and those are exactly the ones
that fail (p=0.098). **Translation: "LB vowels are relatively frequent signs" (a typological universal) does the
work; "vowels are word-initial" (WP1's stated mechanism) does not clear the bar.**

## Result 3 — The two INDEPENDENT (unsupervised) models do NOT recover C/V

Neither the Gaussian mixture nor the HMM recovers the vowel/consonant partition above an honest null
(AUC p = 0.131 and 0.109). Their adjusted Rand indices are ≈ 0 (**0.002**, **0.058**): the natural 2-way split of
the 77-sign inventory is **36/41** (GMM) or **53/24** (HMM), nowhere near the true **5/72** vowel split. The C/V
partition is **not** a structure the data volunteers — it appears only when you supervise directly on the 5 known
vowels. Tellingly, the two unsupervised models agree strongly with each other (Spearman **0.827**) and only weakly
with the supervised model (M1↔M2 0.298, M1↔M3 0.436): the distributional structure they both find is real, but it
is **not** C/V.

## Result 4 — Even the supervised "signal" is 3 vowels, and extremely fragile

True-vowel ranks (of 77) by each model's vowel-score:

| vowel | M1 | M2 | M3 |
|---|---|---|---|
| A | 1 | 6 | 3 |
| E | 2 | 11 | 12 |
| O | 3 | 13 | 18 |
| **I** | **21** | **45** | **29** |
| **U** | **25** | **49** | **52** |

Only **A, E, O** rank vowel-like; **I and U look consonant-like** in all three implementations — consistent with a
"frequent + word-initial" effect on 3 signs, not a clean C/V axis. Vowel-jackknife on M1 (drop one true vowel,
refit CV): dropping **A alone collapses CV-AUC to 0.448** (below chance); range across the 5 vowels = **0.41**
(0.448 → 0.858). A verdict resting on 5 positives, ~3 of which carry it, and one of which flips it below chance, is
not robust.

## Multiplicity (WP1)

WP1's single-feature p=0.035 was the **best of 7** screened features (initial_rate). Bonferroni-corrected across
the 7 features → p ≈ **0.245**. Not significant after correcting for the feature search.

## Which models agree, which do not

- **M2 ≈ M3** (both unsupervised, Spearman 0.827): they find the *same* latent distributional structure — and it is
  NOT C/V (ARI≈0, wrong partition sizes).
- **M1 is the outlier** (weak correlation with M2/M3): its apparent C/V recovery is an artifact of supervising on
  the labels plus a frequency confound, not a property the corpus reveals on its own.
- A result that appears under **one** implementation's assumptions (supervised + one-sided null) and vanishes under
  two independent ones is, by Constitution Art. IV, **exploratory** — not a recovered structure.

## Verdict

**DOWNGRADE `CV_PARTITION_RECOVERED` → EXPLORATORY_FREQUENCY_ARTIFACT (IMPLEMENTATION-DEPENDENT).**

1. The supervised point estimate replicates, but its significance holds only under a one-sided null; the honest
   oriented null gives p=0.15.
2. The recovery is carried by **frequency** (log_freq-only p=0.004; pure word-position p=0.098, n.s.), i.e. a
   typological prior, not the "relative phonological structure" the WP1 symmetry-breaking theorem claimed.
3. **Two genuinely independent, unsupervised implementations fail** to recover C/V (p≈0.11–0.13, ARI≈0): C/V is not
   an emergent partition of the LB sign distribution.
4. The supervised effect is fragile (n_pos=5; jackknife range 0.41; dropping "A" → below chance) and captures only
   3 of 5 vowels.

**Implication for Linear A:** the M1→LA projection (AB-vowel benchmark AUC 0.696, a circular check) inherits the
same frequency confound and provides no honest phonological licence. Under Constitution Art. XV this earns **no**
transfer licence beyond L3-structural, and the "relative phonology" framing is not supported. Held-out /
independent replication — the standard the platform requires — is **NOT met**.

*Reusable per-model predictions (LB per-sign scores for all three models + LA M1 probabilities) are stored in
`data/A3_replications.json` under `A_MODEL_{1,2,3}_*` and `LA_application` for A4/A5.*
