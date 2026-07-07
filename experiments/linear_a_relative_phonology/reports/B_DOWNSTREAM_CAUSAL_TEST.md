# B6 — Downstream causal segmentation test

**Constitution v2.2** — Art. VII (search receipt), VIII (multiplicity), XII (no grading a target by
the rule that created it), XV (transfer licences). Seed 20260708. Script:
`scripts/b6_downstream_causal.py` → `data/B6.json`. All numbers below are MEASURED, not described.

Highest claim layer L2/L3. **No phonetic value assigned; licences NOT_EARNED.** Every channel input is
an anonymous sign-distribution statistic; LB (C,V) values / true endings and LA pure-vowel identities
are read *afterward* to grade recovery only, never as an input (Art. XII).

## Question

Five candidate Linear A segmentations exist (GORILA word, ENTRY, FORMULA, B5 probabilistic-boundary
ensemble, INSCRIPTION_CONTEXT). Which one should downstream relative-structure work **freeze**? We
refuse to decide by Linear A internal fit — that is circular (the segmentation search would be graded
by the very corpus it was tuned on, and LA carries no ground truth to catch over-fitting). We instead
**charge the segmentation search against a held-out known script (Linear B, DĀMOS)**, where true values
and true word boundaries can grade recovery.

## Design

Each LA candidate embodies a segmentation *strategy*. We build the matched LB analogue of every strategy
from the gold DĀMOS wordform streams (3,856 tablets, 13,562 wordform tokens) and run the **same two
downstream channels** on each, graded against LB truth:

| LB analogue | construction | LA counterpart | mean len (signs) |
|---|---|---|---|
| LB_WORD | gold word boundaries | GORILA_WORD | 3.23 |
| LB_FORMULA | merge only *recurrent* (≥2-tablet) word bigrams | FORMULA | 3.73 |
| LB_ENTRY | merge consecutive word pairs (under-segment) | ENTRY | 5.48 |
| LB_ENSEMBLE | Harris branching-entropy induced, tuned to over-cut (target 2.5) | B5 ensemble | 2.50 |
| LB_CONTEXT | whole-tablet, no word cuts | INSCRIPTION_CONTEXT | 11.38 |

**Channel (a) substitution / relative-class** — substitution-graph frame-weight AUC for `same_consonant`
(the vocalic-alternation slot Greek inflection lives in) via the audited C3 machinery, plus the count of
word-final morphophonological minimal pairs the segmentation still exposes.
**Channel (b) morphology** — paradigm-induction (E1) suffix precision against the true LB inflectional
ending signs (defined once, from gold word-final `same_consonant` alternations).

**Primary recovery metric = discrimination × structure-volume**:
`(same_consonant_auc − 0.5) × (n_morphophonological_final_pairs / n_at_gold_WORD)`.
`same_consonant` AUC is a fixed-inventory analysis-A statistic (n_pos = **122 constant** across all five
segmentations), so it is a fair cross-segmentation comparison; the structure-volume factor charges a
segmentation for dissolving the known inflectional channel. Deliberately **dropped from the score** (kept
as diagnostics): the word-final morphophonological AUC (its n swings 116–788, so cross-segmentation AUC
is small-n-noise-inflated — LB_ENSEMBLE's 0.8175 > gold WORD's 0.7435 is exactly this artifact), and
suffix precision@10 (58 true-ending signs ≈ most of the syllabary → non-discriminating).

## Held-out Linear B recovery (the causal charge)

| LB analogue | same_C AUC (n=122) | morphophon-final pairs | morphfin AUC (diag.) | **recovery score** | rank |
|---|---|---|---|---|---|
| **LB_WORD** | **0.6327** | **788** | 0.7435 | **0.13270** | **1** |
| LB_FORMULA | 0.6323 | 773 | 0.7413 | 0.12978 | 2 |
| LB_ENTRY | 0.6237 | 220 | 0.7311 | 0.03454 | 3 |
| LB_ENSEMBLE | 0.5870 | 272 | 0.8175† | 0.03003 | 4 |
| LB_CONTEXT | 0.6083 | 157 | 0.6587 | 0.02158 | 5 |

† small-n-inflated; excluded from the score (see above).

The ladder is monotone and **well separated**: word-level (WORD) and recurrent-chunk (FORMULA) preserve
~98–100 % of the morphophonological channel and top `same_consonant` discrimination; the three
under/over-segmenting strategies (ENTRY, ENSEMBLE, CONTEXT) collapse recovery by **~4×**. WORD vs FORMULA
(0.1327 vs 0.1298, ~2 %) is a **statistical tie** — the endorsement is *word-level granularity*, with
FORMULA an equivalent alternative, not a knife-edge WORD-over-FORMULA claim.

## Linear A internal descriptors (anonymous, non-selecting)

| LA segmentation | n words | subst edges | A-prefix prod (null p) | JA-suffix prod | frac pure-vowel top prefixes |
|---|---|---|---|---|---|
| GORILA_WORD | 3147 | 1507 | 47 (p=0.005) | 26 | 0.333 |
| FORMULA | 1642 | 575 | 23 (p=0.005) | 9 | 0.333 |
| ENTRY | 1068 | 408 | 10 (p=0.060) | 7 | 0.167 |
| INSCRIPTION_CONTEXT | 1341 | 173 | 10 (p=0.040) | 4 | 0.167 |
| B5_ENSEMBLE | 3526 | 686 | 6 (p=1.00) | 0 | 0.167 |

These are LA-internal fit; they do **not** select. Their rank agreement with the LB-recovery ranking says
whether an LA-internal search would have reached the same choice:
- Spearman(LB recovery, LA edge count) = **0.70**
- Spearman(LB recovery, LA A-prefix productivity) = **0.90**

## Causal verdict

**Freeze GORILA_WORD** (LB analogue LB_WORD tops held-out recovery; FORMULA an equivalent runner-up).

The value of the test is not "word wins" — on LB the truth *is* word-level, so WORD trivially preserves
maximum structure. The value is (1) the **quantified 4× degradation ladder** proving coarser
(ENTRY/CONTEXT) and unsupervised-over-cut (ENSEMBLE) segmentations destroy the very substitution +
morphology channels this campaign runs on, and (2) the **exposure of the ensemble/edge-count trap**:
LA-internal edge count ranks **B5_ENSEMBLE #2** (over-segmentation manufactures spurious substitution
edges — 686 edges — without recovering real structure), whereas the held-out causal charge ranks the
ensemble analogue **4th (near-worst)**. The LA side corroborates independently: the B5 ensemble
**annihilates** the LA morphology signal (A-prefix productivity 6, null p=1.00; JA-suffix 0), matching
its near-worst LB recovery. Using the finer A-prefix-productivity proxy (ρ=0.90) an LA-internal search
would mostly agree; using raw edge counts (ρ=0.70) it would have been fooled into promoting the ensemble.

Because C/V is refuted and LA is value-blind, the LA-internal peaks are **not evidence** — the
segmentation to freeze is the one the held-out known-script recovery charges: **GORILA_WORD**.

**Multiplicity (Art. VIII):** 5 candidate segmentations searched; the endorsement rests on a well-separated
4× recovery gap, not a marginal best-of-5 pick. No licence is earned or upgraded by this test (Art. XV):
it selects a *representation*, assigns no value, and does not turn any prior null into a positive.
