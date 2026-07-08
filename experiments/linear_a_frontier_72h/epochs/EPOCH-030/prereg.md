# EPOCH-030 PREREGISTRATION — Numeral / Logogram attachment order in the ledger grammar (FROZEN)

**Task ID:** EPOCH-030
**Campaign:** Linear A frontier-72h
**Layer:** L2/L3 (pure sequence / positional grammar)
**Status:** FROZEN before any main computation. PC runs FIRST and gates the verdict.

## 1. QUESTION (frozen)
In Linear A administrative token streams, do NUMERAL tokens (`t=='num'`) attach to
WORD tokens (`t=='word'`) in a FIXED ORDER — specifically WORD→NUMERAL (entry word
followed by its quantity) rather than NUMERAL→WORD — and is that ordering ROBUST
across independent SITES?

This is pure token-stream positional grammar. NO phonetics, NO meaning, NO values,
NO arithmetic on the numerals. Numerals are treated only as tokens of type `num`.

## 2. DATA
- `corpus/silver/inscriptions_structured.json` — list of inscriptions; each has
  `site` and an ORDERED `stream` (list of token dicts with a `t` type field).
- STEP-0 INSPECTION (performed before freeze): the distinct token types present in
  `stream` and their global counts are:
    - `word`: 3147
    - `nl`:    2114   (newline / entry-line boundary)
    - `num`:   1276   (numeral token — the "NUMERAL" of the metric)
    - `other`: 1056
    - `div`:    463
  Type vocabulary = {word, nl, num, other, div}. There is NO separate `logogram`
  or `fraction` type in this corpus; commodity logograms are encoded under
  `other`/`word`. The metric is therefore defined on `word` vs `num` (the only
  unambiguous "word" vs "numeral" contrast present). This is disclosed, not assumed.

## 3. METRIC (frozen)
For each inscription, scan ADJACENT token pairs (token_i, token_{i+1}) in the
literal stream order (i.e. the next token in the `stream` list — separators are
real tokens and are simply not word/num, so they never form a word-num pair; they
are NOT skipped/collapsed). For every adjacent pair where one token is `word` and
the other is `num`:
    - count `n_word_first`  if the pair is (word, num)
    - count `n_num_first`   if the pair is (num, word)
Define
    p_wordfirst = n_word_first / (n_word_first + n_num_first)
computed GLOBALLY (pooling adjacencies over all inscriptions) and PER SITE.

## 4. NULL MODEL (frozen)
Stream-order shuffle: within each inscription, uniformly permute the ORDER of all
tokens in that inscription's `stream` (keeping the multiset of token types fixed),
then recompute the global p_wordfirst on the permuted corpus. Repeat >= 1000 draws.
Two-sided p-value for "observed global p_wordfirst deviates from the shuffled null"
is computed as
    p = 2 * min( Pr(null >= obs), Pr(null <= obs) )
clipped to <= 1.0, where obs is the observed global p_wordfirst. Per-site p uses
the same shuffle applied within that site's inscriptions only.

## 5. POSITIVE CONTROL (gates verdict; runs FIRST)
The LB damos corpus carries wordform sequences only — NO ordered word/numeral
stream (numerals are embedded in free-text content). Per the mission's explicit
instruction, the PC is therefore BUILT from the LA stream itself as a synthetic
known-order control (disclosed choice). Two sub-controls:

(a) DETECT planted order: build a synthetic corpus by taking the LA streams and,
  within each inscription, for every word-num adjacency, forcing the order to be
  word→num with probability 0.90 (planted p_wordfirst ≈ 0.90). Run the full
  shuffle test. PASS iff p <= 0.05 AND observed direction is word-first.

(b) FALSE-POSITIVE control: build >= 20 synthetic corpora where, within each
  inscription, every word-num adjacency is assigned word→num vs num→word by a
  fair coin (planted p_wordfirst = 0.5). For each, run the shuffle test and
  record whether it rejects at p <= 0.05. PASS iff the false-positive rate
  across these corpora is <= 0.10.

PC verdict = PASSED iff BOTH (a) and (b) pass. If PC fails -> MACHINERY_UNINFORMATIVE.

## 6. CROSS-SITE HELD-OUT (frozen)
For every site with >= 15 word-num adjacencies (testable sites), compute the
per-site p_wordfirst and the per-site shuffle null p (>=1000 draws within that
site). Record direction (word_first if p_wordfirst > 0.5 else numeral_first).
Count sites significant at p <= 0.05. Direction is CONSISTENT iff all
individually-significant sites point the same way. Leave-one-site-out: drop the
largest site (by n inscriptions), recompute the global test, record loo_p.

## 7. FROZEN MECHANICAL VERDICT (count, in order)
- NUMERAL_ORDER_CROSS_SITE_ROBUST iff PC PASSED AND global p <= 0.05 AND
  >= 2 sites individually significant (p <= 0.05) AND direction CONSISTENT
  across those sites AND survives leave-one-site-out (loo_p <= 0.05, same dir).
- NUMERAL_ORDER_SITE_LOCAL iff global p <= 0.05 BUT (< 2 sites significant OR
  direction flips across the significant sites).
- NUMERAL_ORDER_NO_SIGNAL iff global p > 0.05.
- NUMERAL_ORDER_UNDERPOWERED iff < 2 sites have >= 15 word-num adjacencies.
- MACHINERY_UNINFORMATIVE iff PC FAILED.

## 8. NON-CIRCULARITY (hard)
Tokens carry NO phonetic / sound / meaning / language / reading. Only L2/L3
sequence statistics. LB is a positive-control benchmark only; here it lacks the
needed stream so the PC is synthetic-from-LA (disclosed). No numeral VALUES are
read or compared; only token TYPE and POSITION.

## 9. OUTPUTS
prereg.md, plan_hash.txt, machinery.py (with __main__ self-check), result.json,
report (EPOCH030_REPORT.md), data dir (epoch_030/). All at the PATH CONTRACT paths.
