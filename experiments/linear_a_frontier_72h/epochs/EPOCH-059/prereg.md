# EPOCH-059 — CROSS-SITE SUB-LEXICAL SHARING (shared morphology; L2)

**Campaign:** Linear A frontier-72h
**Layer:** L2 (pure distributional n-gram statistics; anonymous sign IDs)
**Operator:** logos z.ai research worker (GLM-5.2)
**Discipline:** Proposer/operator, never adjudicator. MECHANICAL verdict from a FROZEN rule.

---

## QUESTION

At the INTERMEDIATE granularity — sign BIGRAMS/TRIGRAMS (sub-word sequences = candidate
shared affixes/formulae) — is there a SHARED SUB-LEXICAL inventory that recurs across
sites BEYOND what the shared single-sign frequencies alone predict?

- E036: single-sign FREQUENCIES are shared cross-site (shared script).
- E032: whole WORD-FORMS do NOT recur cross-site (site-local vocabulary).
- E039: a single A-prefix is shared.

A YES => the 'shared grammar' includes shared MORPHOLOGY (recurrent multi-sign elements)
beyond the single A-prefix. A NO => shared structure is bounded to signs + positional
grammar, with morphology being site-local.

## NON-CIRCULAR / DISCIPLINE (hard)

- Anonymous sign IDs only. NO sign values, NO readings, NO phonetics/meaning.
- L2 ONLY.
- The CRUX of the null: it MUST preserve each site's single-sign (unigram) frequencies,
  so any detected sharing is BEYOND shared signs. Because frequent shared signs still
  produce shared bigrams under the null, the null S will be substantial — the SIGNAL is
  the observed EXCESS over the null.

## DATA (verified)

- corpus/silver/inscriptions_structured.json — word tokens (t=='word','signs').
- Word-internal sign bigrams = adjacent sign pairs within a word (len>=2).
- 9 sites have >=50 word-internal bigrams (qualifying threshold).

## METRIC (frozen)

CROSS-SITE RECURRENCE of sign-bigrams beyond a unigram-preserving null.

- **Observed statistic S** = number of distinct bigram TYPES that recur across >=3 of the
  qualifying sites. Also report >=2 sites and the mean pairwise Jaccard of site bigram-sets.
- **NULL (frozen, the crux):** for EACH site, regenerate its bigram multiset by sampling
  the SAME NUMBER of sign-pairs, each pair = two INDEPENDENT draws from THAT SITE'S OWN
  unigram (single-sign) frequency distribution. This preserves per-site sign frequencies
  but destroys any sequence-specific structure.
- Recompute S under the null; >=500 null realizations; report null mean + a permutation
  p = frac(null S >= observed S).

## PROTOCOL

0. Inspect: qualifying sites (>=50 word-internal bigrams); n distinct bigrams; observed S
   (>=3-site recurrence); mean pairwise Jaccard; top cross-site bigrams (ANON).
1. FREEZE prereg + plan_hash; machinery.py with __main__ self-check (validate the
   unigram-null generator + the S statistic on a synthetic).
2. GLOBAL: observed S; null-mean S; permutation p; observed/null ratio.
3. POSITIVE CONTROL FIRST (gates verdict):
   (a) DETECT — synthetic sites that SHARE a planted set of bigrams on top of shared
       unigrams; confirm observed S EXCEEDS the unigram-null (perm p<=0.05).
   (b) FALSE-POSITIVE — synthetic sites with SHARED UNIGRAM frequencies but INDEPENDENTLY
       assembled bigrams (no shared sub-lexical inventory); confirm the test does NOT flag
       excess sharing (rejection <=0.10 across >=20 draws).
   If it cannot detect planted sharing OR fires on shared-unigrams-only =>
   MACHINERY_UNINFORMATIVE.
4. LA CLASSIFICATION: observed S vs unigram-null (perm p, ratio). Also report a TRIGRAM
   version as robustness.
5. FROZEN MECHANICAL VERDICT (one token):
   - SHARED_SUBLEXICAL_INVENTORY_CROSS_SITE iff PC passed AND observed S EXCEEDS the
     unigram-null (perm p<=0.05).
   - NO_SHARED_SUBLEXICAL_BEYOND_SIGNS iff observed S is CONSISTENT with the unigram-null
     (perm p>0.05).
   - SUBLEXICAL_SITE_LOCAL iff observed S is BELOW the null.
   - SUBLEXICAL_UNDERPOWERED iff <3 sites qualify.
   - MACHINERY_UNINFORMATIVE iff PC failed.
6. WRITE OUTPUTS to the EXACT PATH CONTRACT paths.
7. FINAL REPLY (plain text, then STOP).

## STATE OF THE NULL (frozen before running)

The unigram-preserving null preserves each site's single-sign frequencies. Therefore any
detected cross-site bigram sharing is BEYOND shared signs. The null S will be substantial
(shared signs still produce shared bigrams); the SIGNAL is the observed EXCESS over null.
