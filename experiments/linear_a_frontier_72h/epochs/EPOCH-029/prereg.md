# EPOCH-029 — WORD-INTERNAL SIGN-BIGRAM COLLOCATION STRUCTURE (prereg, FROZEN)

**Campaign:** Linear A frontier-72h
**Epoch:** 029
**Layer:** L2/L3 (positional/combinatorial distributional statistics ONLY)
**Claim ceiling:** L2/L3. No phonetics, no meaning, no reading.

## QUESTION
Beyond the position-1 A- prefix result, do Linear A words carry a COMBINATORIAL grammar —
specific adjacent sign-PAIRS (bigrams) that are over- or under-represented relative to chance —
and is that structure ROBUST across independent SITES (a shared combinatorial system, not one
archive's habit)? Adjacency constraints relationally constrain sign values WITHOUT assigning any.

## DATA
- `corpus/silver/inscriptions_structured.json` — inscriptions with `site` and a `stream` whose
  `t=='word'` tokens carry `signs`. Analyse words with `len(signs)>=2`.
- A **bigram** = an adjacent ordered sign pair (s_i, s_{i+1}) within a word.
- LB positive control via `scripts.cross_script.data.load_b_damos()[0]` (list of sign-lists).

## NON-CIRCULAR / DISCIPLINE (hard)
Sign tokens carry NO phonetic/sound/meaning/language/reading. L2/L3 distributional statistics
ONLY. LB is a positive-control benchmark ONLY. Bigrams are reported as ANONYMOUS sign ids.

## NULL (frozen): WITHIN-WORD SIGN SHUFFLE
For each null draw, uniformly permute the signs within each word, recount all bigrams. This
preserves each word's sign multiset and length exactly, testing ADJACENCY/order, not sign
frequency. For a bigram b, one-sided over-representation p =
`(1+#{null_count(b) >= obs(b)})/(1+draws)`; under-representation analogously.
Use >=1000 draws for the aggregate statistic.

## AGGREGATE STATISTIC (frozen): "structure score"
= number of bigrams whose observed count deviates from the null at |z|>=3 (equivalently a
two-sided permutation p<=0.01), among bigrams with observed count >= `count_threshold`
(count_threshold = 5, reported). Measures HOW MUCH non-random adjacency structure exists overall.
Compare observed structure score to the null distribution of the structure score itself (draw the
whole statistic under the shuffle >=500 times) -> a **search-adjusted p** for "the corpus has more
bigram structure than chance".

z-score definition (frozen): for bigram b with observed count obs(b), null draws give mean mu(b)
and std sigma(b); z = (obs(b)-mu(b))/sigma(b) with sigma(b) replaced by 1e-9 if 0. A bigram is
"deviating" iff |z|>=3. (Equivalent to two-sided permutation p<=0.01 by the normal approx; the
search-adjusted p is the authoritative test, computed by redrawing the whole statistic.)

## PROTOCOL (in order)
0. Inspect: n words len>=2, n distinct bigrams, top bigrams by count.
1. FREEZE prereg + plan_hash; machinery.py with __main__ self-check.
2. GLOBAL: structure score on full LA corpus + search-adjusted p. Report top over/under bigrams
   (ANONYMOUS).
3. POSITIVE CONTROL FIRST (gates verdict):
   (a) On LB (real phonotactics), SAME machinery must find significant bigram structure
       (search-adjusted p<=0.05).
   (b) False-positive control: on SYNTHETIC words built by sampling signs i.i.d. from the LB
       unigram distribution (so NO real adjacency structure), the structure score must be within
       the null (rejection rate <=0.10 across >=20 synthetic corpora).
   If method finds "structure" in i.i.d. synthetic data OR misses LB's real structure ->
   MACHINERY_UNINFORMATIVE.
4. LA MAIN — CROSS-SITE held-out: for each site with >=40 words len>=2, compute its structure
   score + search-adjusted p independently. Count sites with significant bigram structure
   (p<=0.05). Also test REPLICABILITY of SPECIFIC bigrams: take the top-K over-represented
   bigrams found on the LARGEST site (Haghia Triada) as a training set, and test whether they are
   ALSO over-represented (p<=0.05, same null) on the POOLED OTHER sites (held-out generalization
   of specific structure). K = 10.
5. FROZEN MECHANICAL VERDICT (count):
   - BIGRAM_STRUCTURE_CROSS_SITE_ROBUST iff PC passed AND global structure search-adjusted p<=0.05
     AND >=2 independent sites individually significant AND the HT-trained top bigrams
     held-out-replicate on the pooled other sites (>=50% replicate at p<=0.05).
   - BIGRAM_STRUCTURE_SITE_LOCAL iff global/HT significant BUT <2 other sites significant OR the
     HT-trained bigrams do NOT replicate held-out (<50%).
   - BIGRAM_STRUCTURE_NO_SIGNAL iff global structure search-adjusted p>0.05.
   - BIGRAM_UNDERPOWERED iff <2 sites have >=40 words len>=2.
   - MACHINERY_UNINFORMATIVE iff PC failed.
6. WRITE OUTPUTS to PATH CONTRACT paths.
7. FINAL REPLY: verdict, global search-adjusted p, n significant sites, held-out replication
   fraction, PC pass y/n, one honest bottom line. Bigrams are ANONYMOUS sign pairs.

## FROZEN PARAMETERS
- count_threshold = 5
- bigram null draws (per-bigram p) = 1000
- search-adjusted null draws (whole statistic) = 500
- LB search-adjusted null draws = 500
- synthetic false-positive control: 20 synthetic corpora, each tested at search-adj p<=0.05;
  rejection rate threshold = 0.10
- site significance threshold: search-adj p<=0.05
- held-out K_top = 10; replication threshold = 50%
- site minimum words (len>=2) = 40
- seeds: LA global seed=29; LB seed=229; synthetic seed=1029; per-site seed = 2900+site_index

## ALLOWED VERDICT TOKENS (exactly one)
BIGRAM_STRUCTURE_CROSS_SITE_ROBUST | BIGRAM_STRUCTURE_SITE_LOCAL | BIGRAM_STRUCTURE_NO_SIGNAL |
BIGRAM_UNDERPOWERED | MACHINERY_UNINFORMATIVE
