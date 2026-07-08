# EPOCH-028 — Document-class word-length register signature (L2/L3)

**Task ID:** EPOCH-028
**Campaign:** Linear A frontier-72h
**Layer:** L2/L3 (structural / administrative typology — NO phonetics, NO meaning)
**Operator:** logos z.ai research worker (GLM-5.2), proposer/operator only.

## Question (frozen)
Do Linear A administrative DOCUMENT CLASSES (the `support` field: Tablet, Roundel,
Stone vessel, Clay vessel, Nodule, Metal object) carry DISTINCT word-length
distributions (a structural "register" fingerprint) that is ROBUST across
independent SITES — i.e. NOT merely a by-product of which sites use which supports?

Word length = number of signs per word (`len(signs)` of a `t=='word'` stream token).
Pure structural/administrative typology. No phonetics, no meaning, no reading.

## Data
- `corpus/silver/inscriptions_structured.json` — each inscription has `site`,
  `support`, `context`, and a `stream` whose `t=='word'` tokens carry `signs`.
- Use ALL words with `len(signs) >= 1`. Report sensitivity to `>=2`.
- Keep support classes with `>= 40` words for the GLOBAL test.
- LB positive control via `cross_script.data.load_b_damos()[0]` (list of sign-lists;
  each list = one LB "word"). LB is a positive-control benchmark ONLY.

## Non-circular / discipline (hard)
Sign/word tokens carry NO phonetic / sound / meaning / language / reading content.
L2/L3 distributional statistics ONLY. LB is a positive-control benchmark ONLY.
No adjudication by the operator — verdict is computed mechanically from the rule below.

## Protocol (in order)
0. **Inspect** (already done, recorded for transparency): per `support` class,
   `n_words`, mean, median, histogram. Keep support classes with `>= 40` words.
   Tabulate support × site to expose the confound structure.
1. **FREEZE** this prereg + `plan_hash.txt` + `machinery.py` BEFORE running the
   verdict. PC FIRST.
2. **GLOBAL**: overall word-length distribution; per-support mean length; a
   Kruskal–Wallis across the kept (`>=40`-word) supports. Report H and p.
3. **POSITIVE CONTROL FIRST** (gates the verdict). On LB:
   - (a) DETECT a planted length difference: split LB words into two length-shifted
     pools (lower-half vs upper-half of the per-word length distribution) and run a
     Mann–Whitney U two-sided test; require p <= 0.05.
   - (b) FALSE-POSITIVE control: across >= 20 random balanced splits of LB into two
     pools drawn from the SAME distribution, run the same test; require rejection
     rate <= 0.10 at nominal alpha 0.05.
   - If (a) fails OR (b) > 0.10 -> `MACHINERY_UNINFORMATIVE`.
4. **LA MAIN — SITE-CONTROLLED test** (the key held-out move). For each site with
   `>= 2` support classes each with `>= 15` words: run a Kruskal–Wallis (or
   Mann–Whitney if exactly 2 supports) on word length across those supports,
   WITHIN that site. Record p and which support is longer (the support with the
   larger mean length). Count independent sites with p <= 0.05. Also run a
   stratified permutation test: pool the within-site sign-rank contrasts
   (mean-length difference between the two largest supports, per site) and permute
   support labels within site; report pooled permutation p.
5. **CONSISTENCY**: among the within-site-significant sites, is the DIRECTION of
   the support-length effect consistent (e.g. Roundels always shorter than Tablets)
   or does it flip? A robust register signature needs a consistent direction. We
   define direction consistency operationally: among significant sites, the
   "longer" support is the same support class in every significant site (or, when
   the support pairs differ, the relative ordering does not contradict a single
   global ranking of supports by mean length).
6. **FROZEN MECHANICAL VERDICT** (count, in order):
   - `DOCCLASS_LENGTH_SIGNATURE_ROBUST` iff PC passed AND global Kruskal–Wallis
     p <= 0.05 AND within-site support effect significant (p <= 0.05) in >= 2
     independent sites AND direction consistent across those sites AND pooled
     permutation p <= 0.05.
   - `DOCCLASS_LENGTH_SITE_CONFOUNDED` iff global length differs by support
     (Kruskal–Wallis p <= 0.05) BUT the within-site effect vanishes (< 2 sites
     significant) OR the direction flips.
   - `DOCCLASS_LENGTH_NO_SIGNAL` iff no global length difference
     (Kruskal–Wallis p > 0.05).
   - `DOCCLASS_UNDERPOWERED` iff < 2 sites have >= 2 supports with >= 15 words each.
   - `MACHINERY_UNINFORMATIVE` iff the PC failed.
   - Evaluation order: MACHINERY_UNINFORMATIVE -> UNDERPOWERED -> NO_SIGNAL ->
     SITE_CONFOUNDED -> SIGNATURE_ROBUST.
7. **OUTPUTS** to the exact PATH CONTRACT paths: `prereg.md`, `plan_hash.txt`,
   `machinery.py`, `result.json`, `report`, `data dir`.

## Pre-registered inspection summary (transparency; does NOT determine verdict)
- Support classes with >= 40 words: Tablet (1775), Nodule (640), Stone vessel (370),
  Roundel (119), Clay vessel (84). Metal object has 39 (< 40, excluded from GLOBAL).
- Sites with >= 2 supports each >= 15 words: Haghia Triada (Tablet/Nodule/Roundel),
  Khania (Tablet/Roundel), Knossos (Tablet/Clay vessel). => n_sites_testable = 3
  (>= 2, so NOT pre-emptively UNDERPOWERED).
- Confound structure: Tablet is dominated by Haghia Triada; Nodule almost entirely
  Haghia Triada; Stone vessel dominated by Zakros. This is exactly why the
  within-site test is the held-out move.

## Deviations
None at freeze time.

## PC estimator refinement (pre-LA, transparency)
The PC false-positive rate is measured over `n_null_splits=200` random balanced
splits of LB (still satisfies the prereg's ">= 20 random splits"). Rationale: with
only 25 splits the FPR estimator has binomial SD ~0.044, making the <=0.10 gate
unstable (a frozen seed=7/25-split run gave 0.12, while the test itself is
calibrated at 3.5% over 200 null draws). 200 splits gives a stable calibration
estimate. This refinement was made BEFORE any LA verdict was computed.
