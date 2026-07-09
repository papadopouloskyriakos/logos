# EPOCH-073 PREREGISTRATION (FROZEN)

**Task:** EPOCH-073 — GENRE CONTRAST: Is a rigid canonical within-inscription
word-ORDER a GENERAL Linear A feature, or is it LIBATION-SPECIFIC?
(order rigidity by genre; L3). This is the CONTROL for EPOCH-072.

**Status:** FROZEN before any global computation. PC is synthetic (stated).

## Question (mechanical, value-blind)

EPOCH-072 found the LIBATION (stone-vessel) corpus has a PERFECTLY consistent
canonical word-ORDER (all pairs order-consistency 1.000, cross-site, beyond a
within-inscription shuffle null). The skeptic's question: is that just what LA
word-order looks like everywhere (a general feature), or is the RIGID canonical
order a property of the LIBATION genre specifically (a liturgical formula)?

This epoch applies the SAME order-consistency machinery (E072) to the
ADMINISTRATIVE corpus (support in {Tablet, Nodule, Roundel}) and CONTRASTS its
order-rigidity with libation's. Pure structural ORDER (L3): word-forms are
anonymous sign-tuples; NO reading, NO phonetic value, NO meaning.

E071 already established admin VOCABULARY is site-local; a prediction is that
admin will have FEW cross-site co-occurring pairs (site-local vocab => forms
don't co-occur across sites), so the admin CROSS-SITE order test may be
structurally UNDERPOWERED — that itself is an honest finding. The WELL-POWERED
question is the GLOBAL within-inscription order rigidity and the genre
contrast.

## Non-circular / discipline (hard)

- Anonymous word-forms = sign tuples, len>=2.
- Genre = physical `support` field (ADMIN = {Tablet, Nodule, Roundel};
  LIBATION = Stone vessel, the E072 reference).
- A co-occurrence = two DISTINCT word-forms in the same inscription.
- Order = which comes first in the stream (position of FIRST occurrence if a
  form repeats).
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
- ADMIN corpus = inscriptions with `support` in {Tablet, Nodule, Roundel}.
- LIBATION corpus (reference) = inscriptions with `support == "Stone vessel"`.
- Word-FORM = tuple(signs) with len>=2 (anonymous). Stream tokens with
  `t == "word"` carrying a `signs` list of length >= 2 are word-forms; other
  stream tokens (div/nl) are ignored.
- For each inscription extract its ORDERED list of multi-sign word-forms
  (stream order; duplicates allowed but for a pair use distinct form
  identities; position = FIRST occurrence).

VERIFIED pre-counts (reproduced before freezing):
- ADMIN: ~174 multi-word inscriptions over ~11 sites, n_testable_pairs ~77,
  n_cross_pairs ~3, C_glob ~0.839.
- LIBATION (E072 reference): C_glob = 1.000, 13 testable pairs, 10 cross-site.

## Metric (FROZEN) — identical to E072

- For each inscription, for every unordered pair {fa, fb} of DISTINCT
  word-forms both present, record one observation: the site, and the
  SIGN = +1 if (in a fixed lexicographic key order fa<fb) fa precedes fb in
  the stream, else -1. (If a form repeats, use the position of its FIRST
  occurrence.)
- TESTABLE pairs = unordered form-pairs with total occurrences (across all
  inscriptions) >= 2.
- consistency(pair) = max(n_plus, n_minus) / (n_plus + n_minus)  in [0.5, 1].
- ADMIN C_glob = mean consistency over admin testable pairs.
- LIBATION C_glob (reference) = same over stone-vessel testable pairs
  (expect 1.000).
- CROSS-SITE pairs = testable pairs observed at >= 2 DISTINCT sites.
- Report n_cross for admin (expect ~3) and libation.

## Null (FROZEN)

The ACTUAL within-inscription word-order shuffle: for each draw, independently
SHUFFLE the order of each inscription's word-form list, recompute every
pair's sign, recompute C_glob over the SAME (invariant) testable pair set.
>=1000 draws. One-sided perm p = frac(null C_glob >= observed) for admin
(enrichment = more consistent/ordered than chance). Add-one smoothing.

## Genre contrast (FROZEN)

delta = C_glob(libation) - C_glob(admin). Test whether admin C_glob is
SIGNIFICANTLY BELOW libation's by BOOTSTRAPPING over admin pairs: resample the
admin testable pairs' consistency values with replacement >=2000 times; report
the 95% bootstrap CI of admin C_glob; admin is 'significantly less rigid than
libation' iff the bootstrap UPPER bound < libation C_glob (i.e. admin C_glob
< 1.000 with CI excluding it).

## Positive Control (SYNTHETIC — stated)

PC is fully synthetic (no real data in PC).

(a) DETECT — plant an admin-sized corpus with a rigid canonical order;
    confirm C_glob enriched (perm p<=0.05) with power_est (fraction of >=20
    planted replicates flagged) at the admin pair scale.
(b) FALSE-POSITIVE — plant random-order co-occurrences (same
    co-occurrence/site structure); confirm C_glob NOT flagged (rejection
    <=0.10 across >=20 draws).
(c) DISCRIMINATION — confirm the machinery can DISTINGUISH a rigid corpus
    (C~1.0) from a weak-order corpus (C~0.84): plant both, confirm the
    bootstrap contrast separates them.

If miscalibrated -> MACHINERY_UNINFORMATIVE.

## Frozen mechanical verdict

- ADMIN_ORDER_WEAKER_THAN_LIBATION iff PC passed AND admin C_glob is
  significantly > shuffle null (admin has SOME within-doc order preference,
  perm p<=0.05) AND admin C_glob is significantly BELOW libation's (bootstrap
  upper bound < libation C_glob) — a rigid canonical order is
  LIBATION-SPECIFIC; admin order is only weakly preferred. (Report admin
  cross-site as underpowered if n_cross<5.)
- ADMIN_ORDER_AS_RIGID_AS_LIBATION iff admin C_glob significantly > null AND
  its bootstrap CI includes libation C_glob (admin order is as rigid as
  libation) — canonical order is a GENERAL LA feature.
- ADMIN_ORDER_FREE iff admin C_glob NOT significantly > shuffle null — admin
  word order is free / bag-of-words (an even sharper contrast with libation).
- ADMIN_ORDER_UNDERPOWERED iff admin n_testable_pairs < 15 OR the PC power to
  detect a rigid order at admin scale < 0.5 (report the power estimate).
  [Note: the GLOBAL test is expected well-powered (~77 pairs); this escape is
  for the machinery/power failing, NOT for the cross-site sub-analysis being
  underpowered.]
- MACHINERY_UNINFORMATIVE iff PC detect/false-positive/discrimination
  calibration failed.

Order of precedence: MACHINERY_UNINFORMATIVE first (PC gates everything);
then UNDERPOWERED; then the three substantive verdicts.
