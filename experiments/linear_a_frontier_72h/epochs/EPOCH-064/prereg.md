# EPOCH-064 PREREGISTRATION (FROZEN)

## Task
EPOCH-064 — Is word-initial entropy concentration (prefixing morphology) cross-site robust?
(morphological typology; L2/L3). Held-out cross-site test of E027's global finding that the
word-INITIAL sign position has LOWER entropy than the word-FINAL position (initial slot more
concentrated / drawn from a more restricted inventory = prefix-consistent signature).

## Layer / scope
- layer = L3 (typology of the writing system).
- Pure POSITIONAL structure: anonymous sign IDENTITIES at word-initial vs word-final POSITION.
- NO phonetic value, NO reading, NO meaning. Only the ENTROPY of the sign distribution by position.

## Data
- corpus/silver/inscriptions_structured.json (list of inscriptions; each has `words` = list of
  sign-lists, and `site`).
- TARGET = MULTI-SIGN words (len(signs) >= 2).
- Sites with >=20 multi-sign words (10): Haghia Triada (694), Zakros (132), Khania (120),
  Knossos (61), Phaistos (58), Palaikastro (57), Iouktas (34), Arkhalkhori (34), Syme (21),
  Tylissos (21). Global pooled n = 1369.

## Metric (frozen)
For a set of multi-sign words W:
  H(pos) = Shannon entropy (bits) of the sign distribution at that position over W.
  A = H(final sign) - H(initial sign).
  A > 0  <=>  initial MORE concentrated (lower entropy) = prefix-consistent.
  initial sign = signs[0]; final sign = signs[-1].

## Null (frozen) — within-word position shuffle
For each word, randomly PERMUTE its sign ORDER (uniform permutation of the sign list), then
recompute A over the shuffled words (signs[0]=initial, signs[-1]=final). This preserves each
word's sign MULTISET and the word-length distribution, makes initial/final positions EXCHANGEABLE
(E[A]=0 under null), and controls sign-frequency, word-length, AND per-site sample size.

## Test
- >=1000 shuffles per test.
- one-sided perm p (initial-concentration) = frac(null A >= observed A).
- reversed p (final-concentration) = frac(null A <= observed A) — to detect a REVERSED outcome.

## Positive control (SYNTHETIC, gates verdict)
(a) DETECT-PREFIX: synthetic words with RESTRICTED initial inventory + diverse final signs;
    expect A>0 flagged (perm p <= 0.05).
(b) DETECT-SUFFIX (direction check): restricted FINAL inventory; expect test flags REVERSED
    direction (A<0), NOT initial-concentration.
(c) FALSE-POSITIVE: SYMMETRIC words (initial & final drawn from SAME distribution); expect
    rejection rate <= 0.10 across >=20 independent draws.
PC is SYNTHETIC. If PC fails -> MACHINERY_UNINFORMATIVE.

## Protocol
0. Inspect n multi-sign words global + per site; global A; per-site A.
1. Freeze prereg + plan_hash; machinery.py with __main__ self-check (validate within-word
   permutation null on synthetic; confirm null-mean(A) ~= 0).
2. GLOBAL: observed A (pooled); null mean; perm p (one-sided) + reversed p.
3. PC FIRST (gates verdict), synthetic, three arms above.
4. LA CROSS-SITE: per site (>=20 multi-sign words) recompute A + within-word-shuffle null +
   perm p + direction; count sites significant same direction (A>0). Leave-one-site-out on
   Haghia Triada (pooled-minus-HT perm p).
5. FROZEN MECHANICAL VERDICT (one token):
   - INITIAL_CONCENTRATION_CROSS_SITE_ROBUST iff PC passed AND global A>0 sig (perm p<=0.05)
     AND significant same-direction (A>0) in >=2 sites AND survives leave-one-site-out
     (pooled-minus-HT p<=0.05).
   - INITIAL_CONCENTRATION_SITE_LOCAL iff global A>0 sig BUT <2 sites individually sig OR
     fails leave-one-site-out.
   - REVERSED_FINAL_CONCENTRATION iff global A<0 sig (suffixing, opposite of E027).
   - NO_ENTROPY_ASYMMETRY iff global A not sig in either direction.
   - ASYMMETRY_UNDERPOWERED iff <2 sites have >=20 multi-sign words.
   - MACHINERY_UNINFORMATIVE iff PC failed.

## Non-circularity
Anonymous sign IDs; positional entropy only; within-word position-shuffle null controls
sign-frequency + word-length + per-site sample size. No phonetic/semantic content used.
