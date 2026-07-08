# EPOCH-037 REPORT — LINE-FINAL NUMERAL / LEDGER LINE TEMPLATE (L2/L3)

**Campaign:** Linear A frontier-72h · **Epoch:** EPOCH-037 · **Layer:** L2/L3 (token-position structure)
**Operator:** logos z.ai research worker (GLM-5.2) — PROPOSER/OPERATOR, never adjudicator.
**Verdict (mechanical, from frozen rule):** `LINE_FINAL_NUMERAL_CROSS_SITE_ROBUST`

> Token-position ledger layout ONLY. No numeral arithmetic, no phonetics, no meaning, no
> reading of Minoan. A "line-final numeral" finding is a statement about editorial
> token-position structure in the silver corpus, consistent with a ledger layout; it is
> NOT a decipherment claim.

---

## 1. Question

Within a Linear A ledger LINE, is the NUMERAL token disproportionately LINE-FINAL — i.e.
is the layout the canonical "entry ... quantity [line break]" one-entry-per-line template?
This is the LINE dimension of the entry template. E031 certified WORD→NUMERAL
(entry-then-quantity); E037 tests whether, within a line, the numeral sits at the line
END, robustly across independent sites. Together they map the full positional template:
WORD first, NUMERAL last.

## 2. Discipline / non-circularity (hard)

- Tokens carry NO phonetic / sound / meaning / reading. Only token TYPE
  (`word`,`num`,`nl`,`div`,`other`) and within-line POSITION are used.
- L2/L3 positional statistics ONLY.
- The NULL is within-line position permutation, calibrated BY CONSTRUCTION (per-line
  token multiset fixed → per-line num-count fixed), so it cannot inherit any LA-side
  structure beyond the per-line multiset.
- Linear B (`load_b_damos` / DAMOS) is a POSITIVE-CONTROL BENCHMARK ONLY — used to
  validate the machinery. It is NEVER evidence for the LA claim.

## 3. Data & line-delimiter decision (frozen)

- Source: `corpus/silver/inscriptions_structured.json` (1341 inscriptions; token types
  word=3147, num=1276, nl=2114, div=463, other=1056).
- **Line delimiter = `nl` ONLY.** Inspection: of 463 `div` tokens, 341 are followed by
  content (intra-line / heading separator) and only 96 by `nl`; `div` is therefore a
  within-line/heading divider, NOT a line break. `nl` is the true line break (2073/2114
  followed by content or end-of-stream).
- Sensitivity: nl-only vs nl+div give near-identical results — 1158 vs 1147 qualifying
  lines, p_num_last 0.867 vs 0.866. The choice does not affect the verdict.
- A LINE = run of content tokens (word/num/other) between `nl` breaks. QUALIFYING line:
  ≥2 content tokens AND ≥1 `num`. Global qualifying lines = **1158** across **8 sites**
  with ≥15 qualifying lines (Haghia Triada 772, Zakros 115, Khania 93, Phaistos 34,
  Tylissos 30, Arkhalkhori 30, Malia 28, Palaikastro 18).

## 4. Metric & null (frozen)

- `p_num_last` = fraction of qualifying lines whose LAST content token is `num`.
- NULL: within-line position permutation — permute the ORDER of each line's content
  tokens (multiset fixed), recompute `p_num_last`, 5000 draws; one-sided
  p = P(permuted ≥ observed).
- Control: `p_num_first` (numeral line-INITIAL) — expected NOT elevated.

## 5. Positive control FIRST (gates verdict) — LB benchmark via `load_b_damos`

Pseudo-lines built from DAMOS Linear B wordforms (n=13,562) with a PLANTED line-final
numeral bias (bias=0.80).

| Check | Result | Gate |
|---|---|---|
| (a) Detect planted line-final bias | obs=0.800 vs null_mean=0.341, **p=0.0005** | ≤0.05, correct dir ✓ |
| (b) False-positive on position-randomized pseudo-lines | **rate=0.033** over 30 sets | ≤0.10 ✓ |

**PC verdict: PASSED.** Machinery is informative. (LB used as benchmark ONLY.)

## 6. Global result

| metric | observed | null mean | one-sided p |
|---|---|---|---|
| `p_num_last` (test) | **0.867** | 0.451 | **0.0002** |
| `p_num_first` (control) | 0.016 | 0.451 | 1.0 |

86.7% of qualifying ledger lines end in a numeral, vs 45.1% under within-line position
permutation. The control confirms numerals are NOT line-initial (1.6%): the effect is
position-specific to line-FINAL, not a generic "numeral anywhere" artifact.

## 7. Cross-site (held-out) — LA main

All 8 testable sites (≥15 qualifying lines) are individually significant in the SAME
direction (num line-final > chance):

| Site | n lines | p_num_last | null mean | p |
|---|---|---|---|---|
| Haghia Triada | 772 | 0.865 | 0.451 | 0.0002 |
| Zakros | 115 | 0.896 | 0.456 | 0.0002 |
| Khania | 93 | 0.828 | 0.446 | 0.0002 |
| Phaistos | 34 | 0.824 | 0.430 | 0.0002 |
| Tylissos | 30 | 0.800 | 0.429 | 0.0002 |
| Arkhalkhori | 30 | 0.900 | 0.439 | 0.0002 |
| Malia | 28 | 1.000 | 0.483 | 0.0002 |
| Palaikastro | 18 | 1.000 | 0.490 | 0.0002 |

**8/8 sites significant, direction consistent.**

**Leave-one-site-out** (exclude Haghia Triada, the dominant site): 348 lines across 7
sites, `p_num_last`=0.876, p=0.0002 — **survives**. The signal is not driven by a single
site.

## 8. Frozen mechanical verdict

Rule: `LINE_FINAL_NUMERAL_CROSS_SITE_ROBUST` iff PC passed AND global p≤0.05 (num
line-final > chance) AND ≥3 sites individually significant same direction AND survives
leave-one-site-out.

- PC passed ✓
- global p=0.0002 ≤0.05, direction correct ✓
- 8 sites significant same direction (≥3) ✓
- LOO survives ✓

**→ LINE_FINAL_NUMERAL_CROSS_SITE_ROBUST.**

## 9. Bottom line (honest)

Across 1158 qualifying ledger lines from 8 independent Linear A sites, the numeral is the
line-final content token 86.7% of the time (vs 45.1% under within-line position
permutation, p=0.0002), with numerals almost never line-initial (1.6%). The effect is
consistent in direction and significant at every testable site and survives dropping the
dominant site. Combined with E031 (WORD→NUMERAL), this maps a positional entry template:
**WORD first, NUMERAL last, within each line** — consistent with a "entry ... quantity [line
break]" one-entry-per-line ledger layout. This is a token-position (L2/L3) structural
claim about the silver corpus; it makes no claim about numeral values, phonetics, or
semantic content of the inscriptions.

## 10. Outputs (PATH CONTRACT)

- prereg: `experiments/linear_a_frontier_72h/epochs/EPOCH-037/prereg.md`
- plan_hash: `experiments/linear_a_frontier_72h/epochs/EPOCH-037/plan_hash.txt`
- machinery: `experiments/linear_a_frontier_72h/epochs/EPOCH-037/machinery.py`
- result: `experiments/linear_a_frontier_72h/epochs/EPOCH-037/result.json`
- data: `experiments/linear_a_frontier_72h/data/epoch_037/` (qualifying_lines.jsonl,
  per_site_summary.json, line_delim_sensitivity.json)
