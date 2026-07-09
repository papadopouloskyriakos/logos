# EPOCH-068 PREREGISTRATION (FROZEN)

## Task
IS THE A-PREFIXED VOCABULARY MORE CROSS-SITE-SHARED THAN FREQUENCY-MATCHED NON-A VOCABULARY?
(grammar x lexicon; L2/L3).

## Definitions (anonymous, structural — NO reading, NO phonetic value, NO meaning)
- A **word-TYPE** = the tuple of signs of a word token (from `corpus/silver/inscriptions_structured.json`,
  field `words`, each entry a list of sign strings). Only multi-sign types (len>=2) are considered.
- **token count** of a type = total occurrences across the corpus.
- **sites** of a type = set of distinct `site` values where it occurs.
- **A-TYPE** = multi-sign type whose FIRST sign is the anonymous initial-slot label `'A'` (the anonymous
  word-initial slot from E022-E025; NO phonetic value).
- **NON-A type** = multi-sign type whose first sign != 'A'.
- **SHARED** type = appears at >=2 distinct sites.
- **Informative types** = types with token count >= 2 (count-1 hapax types can NEVER be shared and contribute
  0 to both share rates; they are excluded from the comparison).

## Metric (FROZEN)
D = share_rate(A) - share_rate(nonA), where
share_rate(X) = (# informative X-types that are SHARED) / (# informative X-types),
computed over count>=2 types only.

## Null hypothesis (FROZEN, FREQUENCY-MATCHED stratified permutation)
Within EACH token-count stratum (count = 2, 3, 4, ...), randomly PERMUTE the A/non-A labels among that
stratum's types, preserving the per-stratum A-count and nonA-count. Recompute D. Repeat >= 2000 draws.
One-sided perm p = frac(null D >= observed D)  (testing: A MORE shared).

This controls token frequency EXACTLY: labels only shuffle among types of equal token count, so any
frequency confound is removed.

## Verdict rule (FROZEN, MECHANICAL — proposer never adjudicates)
- POSITIVE CONTROL (PC) FIRST, SYNTHETIC:
  (a) DETECT: plant A-label on the most-shared count>=2 types within strata; confirm perm p<=0.05.
  (b) FALSE-POSITIVE: random A/non-A labeling within strata; confirm rejection rate <=0.10 over >=20 draws.
  (c) POWER: with REAL per-stratum A-counts, estimate power to detect a planted +0.3 sharing gap.
- Verdict:
  - A_MARKED_VOCAB_MORE_SHARED   iff PC passed AND power>=0.5 AND D_obs>0 significant (perm p<=0.05).
  - A_MARKED_VOCAB_MORE_LOCAL    iff PC passed AND power>=0.5 AND D_obs<0 significant.
  - A_MARKED_VOCAB_NO_DIFFERENCE iff PC passed AND power>=0.5 AND D not significant.
  - A_VOCAB_UNDERPOWERED         iff power<0.5 (report D_obs, claim nothing either way).
  - MACHINERY_UNINFORMATIVE      iff PC failed.

## Non-circularity
Anonymous word-forms only; 'A' is the anonymous initial-slot label; sharing = pure structural recurrence
across sites. No reading, no meaning, no phonetic value invoked. Frequency confound controlled by
within-stratum label permutation.

## Layer
L3 (grammar x lexicon cross-site structural recurrence).

## Data
corpus/silver/inscriptions_structured.json (verified: 115 A-types, 99 count-1 hapax, 16 informative;
868 nonA-types, 726 count-1, 142 informative).
