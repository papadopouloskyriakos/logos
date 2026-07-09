# EPOCH-053 — LEDGER ENTRY-WORD VOCABULARY RESTRICTION (commodity lexicon?; L2/L3)

## TASK
Is the vocabulary of ENTRY-WORDS (word tokens immediately followed by a numeral
in the ordered stream) drawn from a MORE RESTRICTED, REPETITIVE form set than
NON-ENTRY words? "Commodity lexicon" = a low-diversity form set (distributional
claim only; forms ANONYMOUS; no phonetics, no meaning, no values).

## DATA
- corpus/silver/inscriptions_structured.json — ordered `stream` of tokens with
  types `word`/`num`/`div`/`nl`.
- ENTRY-word = a `word` token whose NEXT stream token is `num`.
- NON-ENTRY = a `word` token whose next token is NOT `num`.
- Word-form = the sign tuple (anonymous).

## METRIC (frozen)
Vocabulary restriction measured on:
  (a) TYPE-TOKEN RATIO (TTR) = distinct forms / tokens.
  (b) Normalized entropy = H(form distribution) / log2(n_types).
Restriction = entry-words have LOWER TTR AND LOWER normalized entropy than
non-entry words, beyond a sample-size-matched null.

## NULL / SIZE-MATCHING (frozen)
TTR is size-dependent. Control rigorously: subsample the LARGER group to the
size of the smaller (matched n) on every comparison; >=500 bootstrap resamples
for the matched TTR/entropy gap; report the entry-vs-non gap and a label-
permutation p (shuffle entry/non labels among all words, recompute the matched
gap). Direction recorded: "entry_more_restricted" if entry has lower matched
TTR AND lower matched entropy.

## PROTOCOL
0. Inspect: n entry, n non-entry; distinct forms; raw TTR; top entry forms (anon).
1. Freeze prereg + plan_hash; machinery.py with __main__ self-check.
2. GLOBAL: size-matched TTR + normalized entropy for entry vs non-entry; gap;
   label-permutation p + direction.
3. POSITIVE CONTROL FIRST (gates verdict):
   (a) DETECT — plant a restricted entry vocabulary (small form set) vs a diverse
       non-entry set; confirm size-matched test flags restriction (p<=0.05).
   (b) FALSE-POSITIVE — split words from the SAME vocabulary into two groups at
       DIFFERENT sizes; size-matched test must NOT flag restriction
       (false-positive rate <=0.10 across >=20 splits).
   If PC cannot detect planted restriction OR fires on same-vocab different-size
   groups -> MACHINERY_UNINFORMATIVE.
4. LA MAIN — CROSS-SITE: per site with >=20 entry AND >=20 non-entry words,
   compute size-matched restriction gap + p + direction; count significant sites
   in the same direction. Leave-one-site-out on HT (the dominant site).
5. FROZEN MECHANICAL VERDICT:
   - ENTRY_WORD_COMMODITY_LEXICON_CROSS_SITE iff PC passed AND global entry-words
     significantly more restricted (p<=0.05) AND >=2 sites significant same
     direction AND survives leave-one-site-out.
   - ENTRY_WORD_LEXICON_SITE_LOCAL iff global significant BUT <2 sites / collapses
     under LOO.
   - NO_ENTRY_WORD_LEXICON_RESTRICTION iff entry-words NOT significantly more
     restricted (size-matched).
   - ENTRY_LEXICON_UNDERPOWERED iff <2 sites have >=20 in each group.
   - MACHINERY_UNINFORMATIVE iff PC failed.
6. WRITE OUTPUTS to PATH CONTRACT paths.
7. FINAL REPLY: verdict, entry vs non-entry restriction (size-matched) + p +
   direction, n sites, PC pass y/n, one honest bottom line.

## NON-CIRCULAR / DISCIPLINE
Forms anonymous; entry = numeral-adjacency (observed); L2/L3 ONLY; LB control-
only (LB lacks stream numeral adjacency -> synthetic PC only; SAY SO).

## LAYER
L2/L3 (pure distributional vocabulary structure).
