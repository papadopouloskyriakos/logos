# EPOCH-075 PREREGISTRATION (FROZEN)

**Task:** EPOCH-075 — HARDEN the E072 libation-order cross-site positive.
Does the canonical cross-site ORDER survive LEAVE-ONE-SITE-OUT (LOSO) and
LEAVE-THE-HUB-INSCRIPTION-OUT (LHIO), or is its cross-site BREADTH
concentrated in one site / one inscription? (robustness of a positive;
invariant #3 + Art. VIII effective-n; L3.)

**Status:** FROZEN before any global computation in this epoch. PC is
SYNTHETIC (stated). This epoch can only CONFIRM or QUALIFY E072 — it is an
append-only ERRATUM/robustness note, never a silent rewrite.

## Question (mechanical, value-blind)

E072 found the libation (stone-vessel) word-forms follow a perfectly
consistent canonical ORDER shared across sites (C_cross=1.0 vs
within-inscription shuffle null ~0.74, A_cross=10/10, perm p=0.0005). A
coordinator pre-check raised a CONCENTRATION concern that MUST be tested
before E072 is trusted as a broad cross-site positive: the 10 cross-site
pairs come from only 8 distinct inscriptions; ONE HUB inscription
(IOZa2, Iouktas) is an endpoint of ALL 10 cross-site pairs; and
leave-one-site-out drops n_cross from 10 to 3 when Iouktas is removed
(but stays 9-10 when Zakros/Palaikastro/Syme are removed).

QUESTION (mechanical, value-blind): does the canonical-order signal
SURVIVE these leave-outs (a ROBUST cross-site positive), or does its
cross-site BREADTH collapse (a QUALIFIED / narrow positive)? Pure
structural ORDER (L3): anonymous sign-tuples; NO reading, NO meaning.

## Non-circular / discipline (hard)

- SAME metric + SAME null as E072 (frozen). Robustness = recompute the
  SAME statistic on leave-one-out subsets. No new statistic is invented.
- Anonymous word-forms = sign tuples, len>=2.
- A co-occurrence = two DISTINCT word-forms in the same inscription.
- Order = which comes first in the stream (position of FIRST occurrence).
- Site = given `site` field.
- The within-inscription word-order SHUFFLE null preserves EACH
  inscription's word multiset AND therefore preserves WHICH form-pairs
  co-occur, at WHICH sites, and HOW MANY times — it destroys ONLY the
  ORDER. On a SUBSET, the testable/cross-site pair sets are recomputed
  over THAT subset (the subset's own invariant sets).
- DISTINGUISH signal-loss from power-loss (the central discipline of this
  epoch): a leave-out that reduces n_cross below the floor (n_cross<3) is
  UNDERPOWERED — report it as such, NOT as evidence of fragility. Only a
  leave-out that KEEPS enough pairs (n_cross>=3) but LOSES significance
  (perm p>0.05) or drops C_cross toward the null is genuine FRAGILITY.
- EFFECTIVE-N (Art. VIII): report #distinct carrier inscriptions and
  #distinct carrier sites vs the raw pair count. Pairs sharing the hub
  inscription are NOT independent evidence.
- L3 ONLY. No reading, no meaning.

## Data

- Corpus: `corpus/silver/inscriptions_structured.json`
- LIBATION corpus = inscriptions with `support == "Stone vessel"`.
- Word-FORM = tuple(signs), len>=2 (anonymous). Stream tokens with
  `t == "word"` carrying a `signs` list of length >= 2 are word-forms.
- For each inscription extract its ORDERED list of multi-sign word-forms
  (stream order; position = FIRST occurrence).
- Track each inscription's identity (enumerate index) for leave-out.

VERIFIED pre-counts (reproduced in machinery self-check): 99 libation
inscriptions; 56 with >=2 distinct forms; n_testable=13, n_cross=10; the
cross-site pairs are carried by 8 distinct inscriptions across 6 sites;
the top-carrier inscription (IOZa2, Iouktas) is an endpoint of all 10
cross pairs. Leave-one-site-out n_cross: drop Zakros->10, drop Iouktas->3,
drop Palaikastro->9, drop Syme->10. Leave-hub-inscription-out: drop
top1->4, top2->3, top3->2.

## Metric (FROZEN — identical to E072)

- For each inscription, for every unordered pair {fa, fb} of DISTINCT
  word-forms both present, record one observation: the site, and the
  SIGN = +1 if (in a fixed lexicographic key order fa<fb) fa precedes fb
  in the stream, else -1. (If a form repeats, use FIRST occurrence.)
- TESTABLE pairs = unordered form-pairs with total occurrences >= 2.
- consistency(pair) = max(n_plus, n_minus) / (n_plus + n_minus) in [0.5,1].
- CROSS-SITE pairs = testable pairs observed at >= 2 DISTINCT sites.
- C_cross = mean consistency over cross-site pairs.
- A_cross = # cross-site pairs whose DOMINANT order is the SAME in EVERY
  site that has >=1 occurrence (full cross-site agreement).

## Null (FROZEN — identical to E072)

The ACTUAL within-inscription word-order shuffle: for each draw,
independently SHUFFLE the order of each inscription's word-form list,
recompute every pair's sign, recompute C_cross, A_cross over the SAME
(invariant) testable/cross-site pair sets OF THAT SUBSET. >=1000 draws.
One-sided perm p = frac(null stat >= observed), add-one smoothed.

## Robustness floor (FROZEN)

A subset is TESTABLE for robustness iff n_cross >= 3 (else UNDERPOWERED
for that leave-out). Below the floor, the leave-out is reported as
UNDERPOWERED, NOT as fragility.

## Protocol

0. Inspect: baseline n_testable, n_cross, C_cross, A_cross, perm p
   (reproduce E072); carrier inscriptions per cross-pair; identify HUB;
   effective-n = (#distinct inscriptions, #distinct sites).
1. FREEZE prereg + plan_hash + machinery.py (with __main__ self-check).
2. BASELINE: reproduce E072 (C_cross, A_cross, n_cross, perm p).
3. LOSO: for each libation site with >=5 inscriptions (Zakros, Iouktas,
   Palaikastro, Syme), drop it; recompute n_cross, C_cross, A_cross,
   perm p on the remainder. Mark ROBUST (n_cross>=3 AND perm p<=0.05 AND
   C_cross >> null), UNDERPOWERED (n_cross<3), or FRAGILE (n_cross>=3 but
   perm p>0.05 / C_cross collapses toward null).
4. LHIO: drop the single top-carrier inscription; recompute. Then drop
   top-2, top-3. Mark ROBUST / UNDERPOWERED / FRAGILE by the same rule.
5. EFFECTIVE-N (Art. VIII): report #distinct carrier inscriptions and
   #distinct sites vs raw 10 pairs; pairs sharing the hub are NOT
   independent evidence.
6. POSITIVE CONTROL FIRST (gates verdict), SYNTHETIC:
   (a) DETECT-FRAGILE — synthetic libation-scale corpus whose cross-site
       order is carried by ONE hub inscription + one partner site;
       confirm LHIO/LOSO FLAGS it fragile/qualified.
   (b) DETECT-ROBUST — corpus with canonical order spread across MANY
       independent inscriptions/sites; confirm robustness test passes it
       ROBUST (survives every leave-out with n_cross>=3, perm p<=0.05).
   (c) POWER — report leave-out power to distinguish robust from fragile
       at the observed scale.
   If PC cannot tell hub-concentrated from broadly-spread ->
   MACHINERY_UNINFORMATIVE.

## Frozen mechanical verdict

- LIBATION_ORDER_ROBUST_CROSS_SITE iff PC passed AND baseline significant
  AND EVERY leave-out that stays powered (n_cross>=3) remains significant
  (perm p<=0.05, C_cross >> null), INCLUDING dropping the hub inscription.
- LIBATION_ORDER_CROSS_SITE_QUALIFIED iff the core order consistency
  SURVIVES most leave-outs (the order signal is real) BUT the cross-site
  BREADTH is concentration-dependent: at least one powered site-drop
  (e.g. Iouktas) OR the hub-inscription-drop reduces the signal to
  UNDERPOWERED or non-significant — E072 stands as a REAL but NARROW
  cross-site positive (breadth carried by one site / hub inscription;
  effective-n << 10).
- LIBATION_ORDER_FRAGILE iff a single leave-out that STAYS powered
  (n_cross>=3) makes C_cross collapse toward the null (perm p>0.05 with
  adequate n) — the order signal itself, not just breadth, depends on one
  site/inscription; this would DOWNGRADE E072 (SUPERSEDING correction).
- LIBATION_ORDER_ROBUSTNESS_UNDERPOWERED iff every leave-out drops
  n_cross<3 so robustness cannot be assessed.
- MACHINERY_UNINFORMATIVE iff the PC cannot distinguish robust from
  fragile.

Order of precedence: MACHINERY_UNINFORMATIVE first (PC gates everything);
then UNDERPOWERED; then FRAGILE; then QUALIFIED; then ROBUST.

This epoch may only CONFIRM or QUALIFY E072 (append-only); it never
silently strengthens it.
