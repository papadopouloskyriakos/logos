# EPOCH-056 PREREGISTRATION — DUAL SIGN-CLASS INDUCTION (FROZEN)

**Campaign:** Linear A frontier-72h
**Epoch:** EPOCH-056
**Layer:** L2 (writing-system structure / sign-inventory taxonomy)
**Status:** FROZEN before any analysis run. PC FIRST. Mechanical verdict.

## CENTRAL QUESTION
Do Linear A signs PARTITION into >=2 distributionally-distinct FUNCTIONAL classes
recoverable from PURE DISTRIBUTION (position-in-word + numeral-adjacency +
solo-occurrence)? Is that partition BEYOND a frequency-shuffled null? Does ONE
class look "logogram-like" (higher numeral-adjacency + solo-word rate)? Is the
partition CROSS-SITE stable?

This is a STRUCTURAL taxonomy of the SIGN INVENTORY. Signs are ANONYMOUS IDs.
NO phonetic values, NO readings, NO meaning assigned. "logogram-like" /
"syllabogram-like" are DISTRIBUTIONAL cluster labels, NOT decipherment.

## NON-CIRCULAR / DISCIPLINE (hard)
- Signs = anonymous IDs (the corpus sign strings are treated as opaque tokens;
  their conventional names — e.g. commodity ideograms — are NOT used as evidence;
  only their distributional features are).
- Features are PURE distribution (position-in-word, numeral-adjacency,
  solo-occurrence, word length). No values, no readings, no semantics.
- L2 ONLY: this is about the writing system's sign-inventory structure, not
  about language/phonology/decipherment.
- "logogram-like" = a distributional label (high f1 + high f2 cluster), NOT a
  claim about meaning.

## DATA
- corpus/silver/inscriptions_structured.json
- Each inscription: ordered 'stream' of tokens; t=='word' carries 'signs' (list
  of sign IDs); t=='num' are numerals; each inscription has 'site'.
- LA has 61 signs with >=20 sign-tokens (clusterable). [Verified at inspection.]
- POSITIVE CONTROL IS SYNTHETIC: Linear B DAMOS wordforms are syllabic tuples
  with NO numeral stream and NO marked ideograms, so a real-LB ideogram-recovery
  control is NOT available. The PC below is therefore SYNTHETIC (stated plainly).

## PER-SIGN FEATURES (frozen; z-score each column across signs before clustering)
For each sign with >=20 sign-tokens, computed over its word-occurrences:
- f1 numeral_adjacency_rate = frac of the sign's word-occurrences whose
  containing word IMMEDIATELY precedes a 'num' token in the stream.
- f2 solo_word_rate = frac of occurrences where the sign is a 1-sign word.
- f3 word_initial_rate = frac where the sign is the FIRST sign of its word.
- f4 word_final_rate = frac where the sign is the LAST sign of its word.
- f5 mean_word_len = mean length (in signs) of words containing the sign.

## METHOD (frozen)
1. GLOBAL: z-score the 5 features across the >=20-token signs; 2-means into
   k=2 classes; SEPARATION = silhouette score. NULL: shuffle EACH feature column
   across signs independently (destroys sign-feature association, preserves
   marginals), recluster, recompute silhouette; >=500 perms; perm p = frac of
   null silhouettes >= observed.
2. CHARACTERIZE: mean f1 (numeral-adjacency) and f2 (solo-rate) per class;
   "logogram-like" class = higher mean(f1)+mean(f2); report between-class f1
   gap and a Mann-Whitney on f1 across the two induced classes.
3. CROSS-SITE STABILITY: for signs with >=10 tokens in EACH of >=2 sites,
   recompute per-SITE feature vectors and induce the k=2 partition per site;
   measure label agreement between site partitions (Adjusted Rand Index,
   resolving the arbitrary label swap by max over both labelings) vs a null
   (random 2-labelings of the same class sizes); report ARI + null mean.

## PROTOCOL
0. Inspect (done): 61 clusterable signs; features computed; rough classes visible.
1. FREEZE prereg + plan_hash; machinery.py with __main__ self-check.
2. GLOBAL: 2-class silhouette + perm p; per-class mean f1/f2; logogram-like
   class id + f1 gap + MW p.
3. POSITIVE CONTROL FIRST (gates verdict), SYNTHETIC:
   (a) DETECT — plant 2 sign-classes with distinct feature means (class A high
       f1+f2 'logogram-like', class B low); confirm pipeline recovers them
       (silhouette perm p<=0.05 AND recovered-vs-planted ARI>=0.7).
   (b) FALSE-POSITIVE — draw ALL synthetic signs from ONE feature distribution
       (single class); spurious 'significant 2-class' rate <=0.10 across >=20
       draws. If it cannot detect a planted split OR fires on single-class ->
       MACHINERY_UNINFORMATIVE.
4. LA CLASSIFICATION + CROSS-SITE: global perm p; logogram-like-class f1 gap +
   direction; cross-site ARI vs null; n sites usable.
5. FROZEN MECHANICAL VERDICT (one token):
   - DUAL_SIGN_CLASS_CROSS_SITE_ROBUST iff PC passed AND global silhouette
     perm p<=0.05 AND the two classes differ significantly in f1 (MW p<=0.05,
     one class clearly logogram-like) AND cross-site ARI beyond null (observed
     ARI > null mean) AND stable across >=2 sites.
   - DUAL_SIGN_CLASS_SITE_LOCAL iff global separation beyond null AND classes
     differ in f1 BUT cross-site ARI NOT beyond null OR <2 sites usable.
   - NO_SIGN_CLASS_STRUCTURE iff global 2-class silhouette NOT beyond null
     (perm p>0.05).
   - SIGN_CLASS_UNDERPOWERED iff <40 signs clusterable.
   - MACHINERY_UNINFORMATIVE iff PC failed.

## OUTPUTS (exact PATH CONTRACT)
- prereg.md  -> this file
- plan_hash.txt -> "<sha256>  prereg.md"
- machinery.py -> epochs/EPOCH-056/machinery.py (with __main__ self-check)
- result.json -> epochs/EPOCH-056/result.json
- report     -> reports/EPOCH056_REPORT.md
- data dir   -> data/epoch_056/

## SIGN ANONYMITY / L2 DISCIPLINE RESTATEMENT
All sign IDs in outputs are anonymous. "logogram-like" is a DISTRIBUTIONAL
label (the high-f1+f2 cluster), NOT a reading, NOT a meaning, NOT a
decipherment. layer = "L2".
