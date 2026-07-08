# EPOCH-031 PREREGISTRATION — LEDGER WORD→NUMERAL ORDER, CALIBRATED PAIR-FLIP NULL

**Task ID:** EPOCH-031
**Campaign:** Linear A frontier-72h
**Layer:** L2/L3 (token-ORDER structure only)
**Successor of:** EPOCH-030 (which found raw word→numeral order p_wordfirst=0.982 but its frozen full-stream-shuffle null was MISCALIBRATED, fp=0.48 → MACHINERY_UNINFORMATIVE)
**Claim ceiling:** L2/L3. No arithmetic on numeral values, no phonetics, no meaning.

## QUESTION (frozen)
Is word-before-numeral the dominant adjacency order, robustly across independent SITES, under a
properly-calibrated null?

Pure token-ORDER structure. A word/num adjacency = an adjacent (token_i, token_{i+1}) pair in a stream
where the types are {word, num} in either order. Token type key in the corpus is `'num'` (NOT `'numeral'`).

```
p_wordfirst = (#word→num) / (#word→num + #num→word)
```

## DATA (verified)
`corpus/silver/inscriptions_structured.json` — list of 1341 inscriptions; each has `site` and an ORDERED
`stream` of tokens `{"t": "word"|"num"|"nl"|"div"|"other", ...}`. Numeral type key = `'num'`.

Inspection (frozen counts, E030-confirmed):
- GLOBAL: n_adj=1059, n_word_first=1040, n_num_first=19, p_wordfirst=0.982059
- 8 sites with ≥15 word/num adjacencies: Haghia Triada (692), Zakros (117), Khania (80), Phaistos (30),
  Tylissos (28), Arkhalkhori (27), Malia (25), Palaikastro (18).

## NULL MODEL (frozen, calibrated pair-flip)
H0: no order preference. For each observed adjacent word/num pair, independently keep or FLIP its order
with probability 0.5 (fair coin per pair), then recompute p_wordfirst. This is exchangeable BY
CONSTRUCTION (H0: word-first prob = 0.5 per pair), so it is guaranteed calibrated.

- ≥2000 draws.
- Two-sided p for "p_wordfirst deviates from 0.5".
- Equivalently under H0: #word_first ~ Binomial(n_adj, 0.5); report the EXACT binomial two-sided p AND
  the permutation (pair-flip) p. They should AGREE — that agreement is part of the PC.

## PROTOCOL (in order)
0. Inspect: count word/num adjacencies globally + per site (type key `'num'`). Report exact counts.
1. FREEZE this prereg; `plan_hash.txt = "<sha256>  prereg.md"`; `machinery.py` with `__main__` self-check.
2. GLOBAL: p_wordfirst; pair-flip null two-sided p; exact Binomial(n,0.5) two-sided p; confirm agreement.
3. POSITIVE CONTROL FIRST (gates verdict) — confirms calibration (pair-flip is calibrated by construction):
   (a) DETECT: on data with a planted 90% word-first bias, null rejects (p≤0.05, correct direction).
   (b) FALSE-POSITIVE: on data with each pair's order set by a fair coin (true H0), rejection rate ≤0.10
       across ≥30 synthetic sets. If fp>0.10 → MACHINERY_UNINFORMATIVE.
4. LA MAIN — CROSS-SITE held-out: per site with ≥15 word/num adjacencies, compute p_wordfirst + pair-flip p;
   count sites significant (p≤0.05) AND direction; require CONSISTENT direction. Leave-one-site-out on the
   largest site (Haghia Triada): is word-first still significant on the pooled rest?
5. FROZEN MECHANICAL VERDICT (count):
   - `LEDGER_WORD_NUMERAL_CROSS_SITE_ROBUST` iff PC passed AND global pair-flip p≤0.05 (word-first direction)
     AND ≥3 sites individually significant same direction AND survives leave-one-site-out.
   - `LEDGER_WORD_NUMERAL_SITE_LOCAL` iff global significant BUT <3 sites significant OR direction flips.
   - `LEDGER_WORD_NUMERAL_NO_SIGNAL` iff global pair-flip p>0.05.
   - `LEDGER_UNDERPOWERED` iff <3 sites with ≥15 word/num adjacencies.
   - `MACHINERY_UNINFORMATIVE` iff PC false-positive rate >0.10 (null miscalibrated).
6. WRITE OUTPUTS to the PATH CONTRACT paths.

## SCOPE / NON-CIRCULARITY
Token TYPES (word/num) and stream order are directly observed. No phonetic value, no arithmetic on numeral
values, Linear B not used here. Anonymous (no sign identities enter the statistic). This is a token-ORDER
ledger-grammar claim (L2/L3), nothing more.
