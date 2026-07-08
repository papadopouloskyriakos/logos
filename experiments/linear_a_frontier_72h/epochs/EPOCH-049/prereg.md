# EPOCH-049 — PREREGISTRATION (FROZEN)

## Task
EPOCH-049 — INSCRIPTION-LEVEL SIGN CO-OCCURRENCE (document-topic association; L2/L3).

## Question
Do certain SIGNS co-occur WITHIN THE SAME INSCRIPTION (document) more than chance — evidence of
DOCUMENT-TOPIC structure (e.g. related commodities/entries clustering in the same account) — beyond
within-word adjacency (E029) and word-form identity (E032)? And is that co-occurrence structure ROBUST
across sites?

Pure document-level co-occurrence (L2/L3): signs ANONYMOUS; NO phonetics, NO meaning, NO values.

## Discipline (hard)
- Signs anonymous; NO phonetic/sound/meaning/reading.
- L2/L3 ONLY.
- LB control-only (positive-control benchmark).
- Freeze prereg + plan_hash BEFORE running.
- Positive control FIRST; mechanical verdict from a FROZEN rule.

## Data
- corpus/silver/inscriptions_structured.json — each inscription has 'site' and word tokens
  (t=='word', 'signs').
- SIGN SET of an inscription = set of distinct signs appearing anywhere in its words.
- Use inscriptions with >=2 distinct signs.
- LB PC via load_b_damos (LB has no document grouping beyond wordforms; build a synthetic
  document control — pool LB wordforms into synthetic documents of LA-matched sign-set sizes).

## Metric (FROZEN)
- co-occurrence structure = number of sign PAIRS (s,t) that co-occur in the same inscription
  significantly MORE than expected under an independent-placement null, at |z|>=3 among pairs with
  >=5 co-occurrences.
- Aggregate 'cooc_score' = count of such over-represented pairs.

## Null (FROZEN)
- Permute the sign-set-to-inscription assignment while preserving each inscription's sign-set SIZE
  and each sign's document frequency (degree-preserving bipartite shuffle of the sign x inscription
  incidence matrix, approximately preserving row+col marginals via iterative curveball swaps).
- Recompute cooc_score; >=500 draws; one-sided p for 'more co-occurrence structure than chance'.
- Report the null distribution of the score.

## z-score for a pair
- For pair (s,t): observed co-occurrence count C_obs.
- Expected under independent placement given marginals:
  E = (df_s * df_t) / N   (N = number of inscriptions; hypergeometric-style mean).
  Var = E * (1 - df_t/N) * (N - df_s)/(N - 1)   (hypergeometric variance for sampling df_t of N
  docs without replacement among which df_s contain s).
  z = (C_obs - E) / sqrt(Var).
- Pair is "over-represented" iff z >= 3 AND C_obs >= 5.

## Protocol
0. Inspect: n inscriptions (>=2 distinct signs), sign-set size distribution, top co-occurring pairs.
1. FREEZE prereg + plan_hash; machinery.py with __main__ self-check.
2. GLOBAL: cooc_score + degree-preserving-shuffle null mean + one-sided p.
3. POSITIVE CONTROL FIRST (gates verdict):
   (a) DETECT — plant known co-occurring sign-groups (topics) into a synthetic incidence matrix;
       confirm cooc_score >> null (p<=0.05).
   (b) FALSE-POSITIVE — on a degree-matched RANDOM incidence matrix (no real topics), rejection
       rate <=0.10 across >=20 sets.
   If cannot detect planted topics OR fires on random-degree-matched matrices -> MACHINERY_UNINFORMATIVE.
4. LA MAIN — CROSS-SITE held-out: per site with >=30 inscriptions, compute cooc_score + null p;
   count sites with significant document-cooccurrence structure. REPLICATION: do the top co-occurring
   pairs from the largest site also co-occur above chance in pooled other sites? Leave-one-site-out on HT.
5. FROZEN MECHANICAL VERDICT:
   - DOCUMENT_TOPIC_COOCCURRENCE_CROSS_SITE iff PC passed AND global cooc_score significant AND
     >=2 sites significant AND (top-pairs replicate held-out OR survives leave-one-site-out).
   - DOCUMENT_COOCCURRENCE_SITE_LOCAL iff global significant BUT <2 sites / no held-out replication /
     collapses LOO.
   - NO_DOCUMENT_COOCCURRENCE_STRUCTURE iff global cooc_score not significant vs degree-preserving null.
   - COOCCURRENCE_UNDERPOWERED iff <2 sites have >=30 inscriptions.
   - MACHINERY_UNINFORMATIVE iff PC failed.
6. WRITE OUTPUTS to PATH CONTRACT paths.

## Numbers required
- numbers.global = {n_inscriptions, cooc_score, null_mean, null_p, count_threshold}
- numbers.positive_control = {pc_verdict, detect_p, false_pos_rate}
- numbers.cross_site = {n_sites_testable, n_sites_sig, heldout_replication_frac, loo_excluded, loo_p}

## Seeds
- SEED_GLOBAL = 49001, SEED_PC_DETECT = 49002, SEED_FP = 49003, SEED_SITE = 49004.
- N_DRAWS = 600 (>=500). N_FP_CONTROLS = 25 (>=20). Z_THRESH = 3.0. COUNT_THRESH = 5.
