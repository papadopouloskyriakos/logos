# EPOCH-070 PREREGISTRATION (FROZEN)

## Task
What do fractions attach to? num->frac metrological remainder vs word->frac.
Cross-site template or site-local? (metrological grammar; L2).

## Context
E060 established FRACTION-class tokens are entry-TERMINAL (frac->nl, cross-site 3/3)
and LOGOGRAMS precede numerals (logo->num). It did NOT test what PRECEDES a fraction.
Naive metrological expectation: num->frac ('N and a fraction').

## Question
Is num->frac a CROSS-SITE metrological template, or does fractional attachment vary
by site (some sites attach fractions to numerals, others to words)?

## Scope — L2 ONLY
Pure token-class adjacency. The CLASS immediately before a fraction-class token.
NO fraction VALUE, NO sign values, NO readings, NO metrological arithmetic.

## Non-circular / discipline (hard)
- fraction-class = 'other' token whose raw contains a fraction slash '⁄' OR a vulgar
  fraction char in '½¼¾⅓⅕⅙⅛⅔⅗' (E060 definition).
- attachment = the token CLASS immediately before it (within the inscription stream).
- within-line shuffle null: permute the order of non-nl tokens within each line
  (segment between 'nl' boundaries), preserving the line's token multiset + nl
  structure; recompute R_num, R_word; >=1000 permutations; perm p one-sided
  (enrichment: frac(null rate >= observed)).

## Data
corpus/silver/inscriptions_structured.json — ORDERED 'stream'.
n ~ 310 fractions. BEFORE-class (verified): word 148 (0.48), num 120 (0.39),
nl 28, other 12. num->frac is HT-concentrated (HT 93 of 120).
Sites with >=20 fractions: Haghia Triada (194), Khania (73).

## Metric (frozen)
Two rates over fraction tokens:
- R_num  = fraction of fractions immediately preceded by a 'num' token.
- R_word = fraction of fractions immediately preceded by a 'word' token.

## NULL (frozen)
Within EACH line (segment between 'nl'), randomly PERMUTE the order of the non-nl
tokens (preserving the line's token multiset + nl structure); recompute R_num,
R_word; >=1000 permutations; perm p = frac(null rate >= observed) one-sided
(enrichment).

## SITE-CONTRAST
Compute R_num per site (HT, Khania). Test whether R_num DIFFERS between sites:
2-proportion / label-permutation across the two sites' pooled fractions
(site-label permutation: shuffle site labels of fraction tokens, recompute
|R_num(A)-R_num(B)|, perm p = frac(null >= observed)).

## PROTOCOL
0. Inspect: n fractions; before-class histogram; R_num, R_word global + per site.
1. FREEZE prereg + plan_hash; machinery.py with __main__ self-check (validate
   within-line permutation null on a synthetic).
2. GLOBAL: R_num, R_word; null means; perm p each.
3. POSITIVE CONTROL FIRST (gates verdict), SYNTHETIC:
   (a) DETECT — plant a corpus where fractions ALWAYS follow a numeral; confirm
       R_num enriched (perm p<=0.05).
   (b) FALSE-POSITIVE — plant fractions placed UNIFORMLY at random within lines;
       confirm R_num NOT flagged (rejection <=0.10 across >=20 draws).
   If miscalibrated -> MACHINERY_UNINFORMATIVE.
4. CROSS-SITE / SITE-CONTRAST: per site with >=20 fractions (HT, Khania),
   R_num + within-line null + perm p + direction. THEN test whether R_num(HT)
   differs significantly from R_num(Khania) (site-label permutation over pooled
   HT+Khania fractions; perm p). KEY site-local test.
5. FROZEN MECHANICAL VERDICT (one token):
   - FRAC_NUM_ATTACHMENT_CROSS_SITE iff PC passed AND R_num globally enriched
     (perm p<=0.05) AND R_num enriched same-direction in BOTH HT and Khania AND
     R_num(HT) NOT significantly different from R_num(Khania).
   - FRAC_ATTACHMENT_SITE_LOCAL iff R_num differs SIGNIFICANTLY between HT and
     Khania (site-contrast perm p<=0.05) OR R_num is enriched in only ONE of the
     two sites.
   - FRAC_WORD_ATTACHMENT_DOMINANT iff R_word globally enriched AND R_num NOT
     AND holds in both sites.
   - FRAC_ATTACHMENT_UNSTRUCTURED iff neither R_num nor R_word enriched.
   - FRAC_ATTACHMENT_UNDERPOWERED iff <2 sites have >=20 fractions.
   - MACHINERY_UNINFORMATIVE iff PC failed.
6. WRITE OUTPUTS to exact PATH CONTRACT paths.
7. FINAL REPLY: verdict, R_num vs R_word (obs vs null, p), per-site R_num,
   site-contrast p, PC pass y/n, one honest bottom line. L2 only.

## PC is SYNTHETIC
Positive controls use synthetic corpora. Stated plainly.

## Frozen
This prereg is FROZEN before any analysis run. plan_hash.txt records its sha256.
