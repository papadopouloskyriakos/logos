# EPOCH-072 PREREGISTRATION (FROZEN)

**Task:** EPOCH-072 — Does the libation (stone-vessel) formula recur as an
ORDERED SEQUENCE across sites — a shared canonical order of its word-forms —
beyond a within-inscription word-order shuffle null? (formula-as-sequence; L3)

**Status:** FROZEN before any global computation. PC is synthetic (stated).

## Question (mechanical, value-blind)

When two libation word-forms co-occur in an inscription, do they appear in a
CONSISTENT relative order — and is that canonical order SHARED across sites —
BEYOND a within-inscription word-order shuffle null? Pure structural ORDER
(L3): word-forms are anonymous sign-tuples; order = position in the stream;
NO reading, NO phonetic value, NO meaning. We do NOT claim WHAT the formula
says, only whether a fixed ORDER recurs cross-site.

This is the direct successor of EPOCH-071. E071 tested whether individual
libation word-FORMS spread across sites beyond frequency+site-size and found
they DO NOT. E071 did NOT test the formula's DEFINING feature: its fixed
SEQUENTIAL ORDER. A "formula" is precisely a shared ORDER, not just shared
vocabulary. E072 isolates ORDER.

## Non-circular / discipline (hard)

- Anonymous word-forms = sign tuples, len>=2.
- A co-occurrence = two DISTINCT word-forms in the same inscription.
- Order = which comes first in the stream (position of FIRST occurrence if a
  form repeats).
- Site = given `site` field.
- The within-inscription word-order SHUFFLE null preserves EACH inscription's
  word multiset AND therefore preserves WHICH form-pairs co-occur, at WHICH
  sites, and HOW MANY times — it destroys ONLY the ORDER. So the set of
  testable pairs and cross-site pairs is INVARIANT under the null; only the
  order signal changes. This isolates ORDER cleanly.
- CRITICAL: consistency of a pair seen only ONCE is trivially 1.0 under BOTH
  obs and null, so it is uninformative — restrict to pairs with >=2
  co-occurrences.
- The null mean of consistency is NOT 0.5 (for a pair with k occurrences,
  max(heads,tails)/k > 0.5 in expectation) — we MUST use the EMPIRICAL
  within-inscription shuffle null, never a 0.5 baseline. (Validated in
  machinery self-check against closed-form E[max(H,T)/k].)
- L3 ONLY. No reading, no meaning.

## Data

- Corpus: `corpus/silver/inscriptions_structured.json`
- LIBATION corpus = inscriptions with `support == "Stone vessel"`.
- Word-FORM = tuple(signs) with len>=2 (anonymous). Stream tokens with
  `t == "word"` carrying a `signs` list of length >= 2 are word-forms; other
  stream tokens (div/nl) are ignored.
- For each inscription extract its ORDERED list of multi-sign word-forms
  (stream order; duplicates allowed but for a pair use distinct form
  identities; position = FIRST occurrence).

## Metric (FROZEN)

- For each inscription, for every unordered pair {fa, fb} of DISTINCT
  word-forms both present, record one observation: the site, and the
  SIGN = +1 if (in a fixed lexicographic key order fa<fb) fa precedes fb in
  the stream, else -1. (If a form repeats, use the position of its FIRST
  occurrence.)
- TESTABLE pairs = unordered form-pairs with total occurrences (across all
  inscriptions) >= 2.
- consistency(pair) = max(n_plus, n_minus) / (n_plus + n_minus)  in [0.5, 1].
- GLOBAL statistic C_glob = mean consistency over ALL testable pairs.
- CROSS-SITE pairs = testable pairs observed at >= 2 DISTINCT sites.
- CROSS-SITE statistic C_cross = mean consistency over cross-site pairs.
- CROSS-SITE AGREEMENT A_cross = number of cross-site pairs whose DOMINANT
  order (sign of n_plus-n_minus) is the SAME when computed independently
  within EACH site that has >=1 occurrence (every site agrees on the order).
  agree_frac = A_cross / n_cross_pairs.

## Null (FROZEN)

The ACTUAL within-inscription word-order shuffle: for each draw, independently
SHUFFLE the order of each inscription's word-form list, recompute every
pair's sign, recompute C_glob, C_cross, A_cross over the SAME (invariant)
testable/cross-site pair sets. >=1000 draws. One-sided perm p =
frac(null stat >= observed) for each of C_glob, C_cross, A_cross
(enrichment = more consistent/ordered than chance). Add-one smoothing.

## Positive Control (SYNTHETIC — stated)

PC is fully synthetic (no real data in PC).

(a) DETECT — plant a corpus where a set of forms ALWAYS appears in a fixed
    canonical order at every site; confirm C_cross AND A_cross enriched
    (perm p<=0.05).
(b) FALSE-POSITIVE — plant co-occurrences with RANDOM order within each
    inscription (same co-occurrence / site structure, no canonical order);
    confirm C_cross NOT flagged (rejection <=0.10 across >=20 draws).
(c) POWER — estimate power to detect a planted canonical order at the
    OBSERVED corpus's pair/site counts (fraction of >=20 planted replicates
    flagged at p<=0.05); report power_est.

If it can't detect a planted ordered formula OR fires on random-order
co-occurrence -> MACHINERY_UNINFORMATIVE.

## Frozen mechanical verdict

- LIBATION_FORMULA_ORDERED_SEQUENCE_CROSS_SITE iff PC passed (incl.
  power_est>=0.5) AND C_cross significantly > its null (perm p<=0.05) AND
  A_cross significantly > its null (perm p<=0.05).
- LIBATION_ORDER_SITE_LOCAL iff C_glob significantly > null BUT A_cross NOT
  beyond null (perm p>0.05).
- LIBATION_NO_ORDERED_STRUCTURE iff C_glob NOT significantly > null.
- LIBATION_SEQUENCE_UNDERPOWERED iff n_cross_pairs < 5 OR fewer than 2 sites
  contribute cross-site pairs OR PC power_est < 0.5.
- MACHINERY_UNINFORMATIVE iff PC detect/false-positive calibration failed.

Order of precedence: MACHINERY_UNINFORMATIVE first (PC gates everything);
then UNDERPOWERED; then the three substantive verdicts.
