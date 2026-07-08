# EPOCH-024 — A- PREFIXATION MULTI-AXIS HELD-OUT ROBUSTNESS

**Campaign:** Linear A frontier-72h (frontier F4)
**Layer:** L2/L3 (positional/structural statistics only)
**Claim ceiling:** A- is a corpus-wide productive positional prefix SLOT (no phonetic/semantic value assigned).

## Question
E022 showed A- prefixation survives a global adaptive null. E023 showed it holds across 9/10 SITES.
Does it ALSO hold across two ORTHOGONAL administrative partition axes — SUPPORT type and CONTEXT type —
i.e. is it a genuinely corpus-wide productive positional prefix SLOT, invariant to how the corpus is partitioned?

## Non-circular discipline (hard)
- Sign names (A, JA, ...) are ANONYMOUS. Assign NO phonetic value, sound, meaning, language, or reading to
  ANY sign. Positional/structural statistics ONLY (L2/L3).
- LB is a positive-control benchmark ONLY (it is NOT Linear A; it only certifies the machinery can detect a
  known positional-prefix analogue).
- Verdict is computed mechanically from a FROZEN rule; the operator never decides truth by narration.

## Data
- `corpus/silver/inscriptions_structured.json`: list of inscriptions; each has `site`, `support`, `context`
  and a `stream` whose `t=='word'` tokens carry a `signs` list. Analyze words with >=2 signs.
- LB positive control via `scripts.cross_script.data.load_b_damos` (returns list of word sign-lists).

## Metric
- For a sign S: count (and fraction) of >=2-sign words whose FIRST sign is S.
- Null: within-word uniform permutation (REUSED from E023 `machinery.permutation_null`); preserves each
  word's sign multiset and length exactly. 1000 draws, one-sided p = (1 + #(null >= obs)) / (1 + 1000).

## Protocol (frozen, in order)
0. Inspect corpus `support` and `context` value distributions (DONE; see below).
1. Freeze this prereg + plan_hash. Write `machinery.py` (imports E023 permutation_null) with self-check.
2. GLOBAL sanity: A word-initial count/frac over all >=2-sign words.
3. POSITIVE CONTROL FIRST (gates the verdict): on LB, pick the most word-initial-skewed sign with >=40 occ
   as a known positional-prefix analogue; partition LB by a seeded balanced 5-way split (no per-tablet
   metadata available in load_b_damos); require it significant (p<=0.05) in >=3 partitions AND a
   frequency-matched random LB sign NOT significant in >=3 partitions. If PC fails -> MACHINERY_UNINFORMATIVE.
4. SUPPORT AXIS (primary): partition LA by `support`; keep supports with >=20 qualifying words; for each
   compute A-initial obs, null-mean, p (1000 draws); Holm-correct across the support family;
   leave-one-support-out (drop the largest support = Tablet; is A- still significant on the rest?).
5. CONTEXT AXIS (secondary): same as step 4 but partition by `context`.
6. ADVERSARIAL: repeat the SUPPORT-axis test for the 5 next-most-initial comparator signs (excluding A);
   A- is special only if it clears materially more support partitions than the comparator median.
7. FROZEN MECHANICAL VERDICT (decide by counting):
   - `A_PREFIX_MULTIAXIS_ROBUST` iff (PC passed) AND A- significant (p<=0.05) in >=2 SUPPORT partitions AND
     survives support leave-one-out AND significant in >=2 CONTEXT partitions AND clears >=2 more support
     partitions than the comparator median.
   - `A_PREFIX_AXIS_DEPENDENT` iff robust on exactly one of the two axes.
   - `A_PREFIX_PARTITION_CONCENTRATED` iff significant globally but in <=1 partition on both axes / collapses
     under leave-one-out.
   - `A_PREFIX_UNDERPOWERED` iff too few partitions have >=20 words to test (report the power limit).
   - `MACHINERY_UNINFORMATIVE` iff the PC failed.

## Observed corpus structure (step 0, pre-freeze)
- SUPPORT qualifying (>=2-sign) words: Tablet 844, Stone vessel 259, Roundel 69, Clay vessel 58, Nodule 35,
  Metal object 30, (then <20: Inked 17, Lames 13, Stone object 13, ...). => 6 partitions testable on support.
- CONTEXT qualifying words: LMIB 833, '' 443, LMIA 31, LMI 29, (then <20: MMII 17, ...). => 4 partitions
  testable on context.
- Global A-initial sanity target: ~155/1369 (operator measured pre-freeze; the "~155/177" in the brief
  appears to use a different denominator — the operator will report the measured value and flag the
  discrepancy as a deviation).

## Outputs
- prereg.md, plan_hash.txt, machinery.py, result.json, EPOCH024_REPORT.md, intermediate JSON in data dir.
