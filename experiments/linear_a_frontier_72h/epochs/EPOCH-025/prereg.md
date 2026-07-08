# EPOCH-025 — A- PREFIX PRODUCTIVITY (adversarial self-scrutiny)

**Campaign:** Linear A frontier-72h
**Layer:** L2/L3 (positional / structural statistics ONLY)
**Task:** Adversarial test of the campaign's own headline (A- prefixation, E023/E024).
**Goal:** Try to BREAK the A- result. Is A- a genuinely PRODUCTIVE positional prefix slot
(it attaches to many DISTINCT word-types / continuations), or is its word-initial excess an
artifact of a FEW high-frequency A-initial word-types (e.g. one libation/ledger word)?

## NON-CIRCULAR / DISCIPLINE (hard)
- Sign names (A, ...) are ANONYMOUS. Assign NO phonetic value / sound / meaning / language /
  reading to ANY sign. Positional/structural statistics ONLY (L2/L3).
- LB is a positive-control benchmark ONLY.
- Freeze prereg + plan_hash BEFORE running. Positive control FIRST. Mechanical verdict from
  the frozen rule below.

## DATA
- LA: `corpus/silver/inscriptions_structured.json`; each `stream` token with `t=='word'` has a
  `signs` list. Analyse words with >=2 signs. A "word-type" = the full tuple of its sign sequence.
- LB PC: `from scripts.cross_script.data import load_b_damos` (3-tuple; words = element [0],
  a list of sign-lists).
- Null: REUSE E024 `permutation_null` (within-word uniform-permutation null). Metric = count of
  >=2-sign words whose FIRST sign is A; one-sided p over 1000 draws.

## PROTOCOL (in order)
0. Inspect data. Among >=2-sign words with first sign A: number of DISTINCT word-types,
   number of DISTINCT second-signs, top A-initial word-types by count.
1. Freeze prereg + plan_hash; write machinery.py with self-check.
2. GLOBAL: A-initial count/frac over all >=2-sign words (expect ~155/1369); plus
   n_distinct_A_types and n_distinct_second_signs.
3. POSITIVE CONTROL FIRST (gates the verdict). On LB, construct TWO reference signs and show
   the machinery separates them:
   (a) PRODUCTIVE initial sign — strongly word-initial AND whose initial occurrences span MANY
       distinct word-types — must (i) stay significant under the null AND (ii) SURVIVE removing
       its single most-frequent initial word-type.
   (b) FEW-TYPE / mono-word initial sign — word-initial mainly because one or few frequent
       word-types start with it — must COLLAPSE (lose significance) when its top word-type is
       removed.
   If the PC cannot exhibit this separation -> verdict MACHINERY_UNINFORMATIVE, no LA claim.
4. LA MAIN — LEAVE-TOP-TYPE-OUT (the adversarial test): identify the single most-frequent
   A-initial word-type; REMOVE all its occurrences; recompute A-initial count + null p on the
   remaining >=2-sign words. Does A-initial preference SURVIVE (p<=0.05)? Also report
   leave-top-2 and leave-top-3-types-out.
5. TYPE-DIVERSITY vs COMPARATORS: for the 5 next-most-word-initial comparator signs, compute
   their n_distinct_initial_word-types; A- is "productive" only if its type-diversity is high
   relative to them (not concentrated in 1-2 types).
6. FROZEN MECHANICAL VERDICT (decide by counting):
   - A_PREFIX_PRODUCTIVE_ROBUST iff (PC passed) AND A- stays significant (p<=0.05) after
     removing its top A-initial word-type AND n_distinct_A_types >= 8 AND A-'s type-diversity
     exceeds the comparator median.
   - A_PREFIX_FEW_TYPE_DRIVEN iff A- loses significance (p>0.05) once the top 1-2 word-types
     are removed, OR n_distinct_A_types < 8 / diversity at-or-below comparators.
   - A_PREFIX_UNDERPOWERED iff too few A-initial words remain after removal to test.
   - MACHINERY_UNINFORMATIVE iff the PC failed.

## OUTPUTS (exact PATH CONTRACT)
- prereg.md, plan_hash.txt, machinery.py, result.json, report, intermediate JSON to data dir.
