# EPOCH-038 — POSITIONAL SIGN-ENTROPY ASYMMETRY (Linear A frontier-72h)

**QUESTION.** If Linear A words carry grammatical SUFFIXES, word-FINAL position should be
dominated by a SMALL set of signs (LOW entropy = a suffix paradigm) relative to word-INITIAL /
medial positions. Is the word-FINAL sign-position entropy significantly LOWER than the
word-INITIAL entropy (a suffixing tendency), and is that ROBUST across independent SITES?

**Layer / discipline.** Pure positional-entropy structure (L2/L3): signs are ANONYMOUS — no
phonetics, no sound, no meaning, no value assignment. This is a MORPHOLOGICAL-STRUCTURE probe
via entropy, distinct from prior positional-count work. LB is a POSITIVE-CONTROL benchmark
ONLY (LB inflects word-finally, so its final-position entropy is expected to be lower than
initial — this validates the entropy machinery, it is NOT a Linear-A claim).

## DATA (verified)
- `corpus/silver/inscriptions_structured.json` — word tokens `t=='word'` with `'signs'`; use
  words with `len(signs) >= 2`. FIRST-position sign = `signs[0]`; LAST-position sign =
  `signs[-1]`.
- LB positive control via `cross_script.data.load_b_damos()[0]` (list of sign-lists), with
  `scripts/` on `sys.path`.

## METRIC (FROZEN)
- Shannon entropy `H` (bits) of the sign distribution at a position.
  - `H_first` = entropy of the first-sign distribution over words (len>=2).
  - `H_last`  = entropy of the last-sign distribution.
- `ASYMMETRY = H_first - H_last`.
  - **ASYMMETRY > 0**  => final position MORE concentrated => suffix-like.
  - **ASYMMETRY < 0**  => initial position MORE concentrated => prefix-like.
- Normalized entropy `H / log2(n_distinct_at_position)` reported for transparency
  (support-agnostic inference uses the permutation null below).

## NULL (FROZEN — within-word permutation, calibrated by construction)
For each null draw: permute the sign order WITHIN each word (preserves each word's multiset
and length), recompute `H_first`, `H_last`, and the asymmetry. `>= 2000` draws.
- One-sided p for "observed asymmetry (`H_first - H_last`) > null" (final MORE concentrated
  than a random position would be). Under H0 (no positional specialization) asymmetry ~ 0.

## PROTOCOL (in order)
0. Inspect: n words len>=2; H_first, H_last, n_distinct first/last; top-5 final signs
   (ANONYMOUS) + share.
1. Freeze prereg + plan_hash; `machinery.py` with `__main__` self-check.
2. GLOBAL: observed asymmetry + within-word permutation null mean + one-sided p; report
   H_first, H_last, top-final-sign concentration.
3. POSITIVE CONTROL FIRST (gates verdict). On LB the SAME machinery must find final-position
   entropy significantly LOWER than initial (asymmetry > 0, p <= 0.05) [DETECT]; AND a
   FALSE-POSITIVE control: on words with signs shuffled within-word (no real positional
   structure), rejection rate <= 0.10 across >= 20 sets. Failure of either =>
   `MACHINERY_UNINFORMATIVE`.
4. LA MAIN — CROSS-SITE held-out: per site with >= 50 words (len>=2), compute asymmetry +
   permutation p; count sites significant (p <= 0.05, asymmetry > 0 same direction); require
   CONSISTENT direction. Leave-one-site-out on the largest site (Haghia Triada). ALSO report
   the reverse (is LA INITIAL more concentrated) to characterize direction honestly.
5. FROZEN MECHANICAL VERDICT (count):
   - `FINAL_SUFFIX_CONCENTRATION_CROSS_SITE` iff PC passed AND global asymmetry > 0
     significant (p <= 0.05) AND >= 3 sites individually significant same direction AND
     survives leave-one-site-out.
   - `SUFFIX_CONCENTRATION_SITE_LOCAL` iff global significant BUT < 3 sites OR direction flips
     OR collapses LOO.
   - `NO_POSITIONAL_ENTROPY_ASYMMETRY` iff global asymmetry not significant (p > 0.05) OR
     reversed (initial more concentrated) -> report the actual direction.
   - `ENTROPY_UNDERPOWERED` iff < 3 sites have >= 50 words.
   - `MACHINERY_UNINFORMATIVE` iff PC failed.

## NON-CIRCULARITY
Signs carry NO phonetic / sound / meaning / reading. L2/L3 statistics ONLY. LB is a
positive-control benchmark ONLY. Prereg + plan_hash frozen BEFORE running; PC FIRST;
mechanical verdict from the frozen rule.
