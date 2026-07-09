# EPOCH-069 — Preregistration (FROZEN)

## Task
Are entry-INITIAL words systematically LONGER (more signs) than entry-INTERNAL words
(name-then-modifiers), CROSS-SITE, and NOT merely the A-prefix effect? (ledger grammar; L2.)

## Layer
L2 — pure structural word-length. word-length = len(signs); position = order within a line
(between consecutive `nl`). `A` is the anonymous E022 slot. NO sign values, NO readings,
NO meaning.

## Data
- corpus/silver/inscriptions_structured.json — ORDERED `stream`.
- A LINE = the WORD tokens between consecutive `nl` (ignore num/div/other; words keep
  in-line order). Trailing words before EOF (no final nl) form a final line.
- TARGET lines = lines with >=2 word tokens. Expected n~363.
- Per-site >=20 first-words testable: Haghia Triada (177), Khania (40), Zakros (33).

## Metric (frozen)
- diff = mean(len of FIRST words) - mean(len of LATER words), pooled over target lines.
- diff > 0  <=>  entry opens with a longer word.
- FIRST word = line's word[0]; LATER words = word[1:].

## Null (frozen)
- Within EACH line, uniformly SHUFFLE the ORDER of its word tokens; recompute diff
  (new first = shuffled word[0]).
- >=1000 shuffles; one-sided perm p = frac(null diff >= observed diff) (first longer).
- Under this null first/later positions are exchangeable so E[diff] = 0; it controls each
  line's word-length multiset + word count.

## Protocol
0. Inspect: n target lines; mean first/later word len; diff; per-site.
1. Freeze prereg + plan_hash; machinery.py with __main__ self-check (validate shuffle null
   gives E[diff]~=0).
2. GLOBAL: observed diff; null mean; perm p.
3. POSITIVE CONTROL FIRST (gates verdict), SYNTHETIC:
   (a) DETECT — plant lines where first word is always longer; confirm flagged (perm p<=0.05).
   (b) FALSE-POSITIVE — plant lines with word lengths independent of position; confirm NOT
       flagged (rejection <=0.10 across >=20 draws). If miscalibrated -> MACHINERY_UNINFORMATIVE.
4. CROSS-SITE: per site with >=20 first-words, diff + null + perm p + direction; count sites
   significant same direction (first longer). Leave-one-site-out on Haghia Triada.
5. A-PREFIX CONFOUND ROBUSTNESS (load-bearing): recompute GLOBAL diff + null EXCLUDING all
   A-initial words (drop any word whose first sign is 'A' from both pools; re-derive each
   line's first word among remaining words). Report diff_noA + perm p_noA. Effect is A-driven
   iff it becomes non-significant without A-words.
6. FROZEN MECHANICAL VERDICT (one token):
   - ENTRY_INITIAL_WORD_LONGER_CROSS_SITE iff PC passed AND global diff>0 sig (perm p<=0.05)
     AND sig same-direction in >=2 sites AND survives LOO AND survives A-exclusion
     (diff_noA>0, perm p_noA<=0.05).
   - ENTRY_INITIAL_LONGER_A_DRIVEN iff global diff>0 sig BUT becomes non-sig when A-initial
     words excluded.
   - ENTRY_INITIAL_LONGER_SITE_LOCAL iff global sig + survives A-exclusion BUT <2 sites / fails LOO.
   - NO_ENTRY_POSITION_LENGTH iff global diff not sig.
   - ENTRY_POSITION_UNDERPOWERED iff <2 sites have >=20 first-words.
   - MACHINERY_UNINFORMATIVE iff PC failed.

## Non-circularity
word-length = len(signs); position = order within line; within-line word-order shuffle null
makes first/later exchangeable; A-word exclusion controls the prefix confound. L2 only.

## Deviations
None at freeze.
