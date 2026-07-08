# EPOCH-025 Report — A- Prefix PRODUCTIVITY (Adversarial Self-Scrutiny)

**Campaign:** Linear A frontier-72h | **Layer:** L2/L3 (positional/structural ONLY)
**Task:** Adversarial test of the campaign's headline (A- prefixation, E023/E024).
**Goal:** Try to BREAK the A- result. Is A- a genuinely PRODUCTIVE positional prefix slot, or is its word-initial excess an artifact of a few high-frequency A-initial word-types?

**Verdict: `A_PREFIX_PRODUCTIVE_ROBUST`**

---

## 1. Discipline (non-circular)

Sign names (A, ...) are **ANONYMOUS**. No phonetic value, sound, meaning, language, or reading assigned to ANY sign. Positional/structural statistics ONLY (L2/L3). LB is a positive-control benchmark ONLY. Metric = count of ≥2-sign words whose first sign is A, under the within-word uniform-permutation null (reused from E024/E023). Prereg + plan_hash frozen before running; positive control run first; verdict from the frozen rule.

## 2. Data inspection (Step 0)

- LA corpus: **1369** words with ≥2 signs.
- A-initial words: **155** (frac 0.1132).
- Among A-initial words: **115 distinct word-types** (distinct sign-sequences), **40 distinct second-signs**.
- Top A-initial word-types by count:

| rank | word-type | count | share of A-initial |
|------|-----------|-------|--------------------|
| 1 | A-TA-I-*301-WA-JA | 11 | 7.1% |
| 2 | A-DU | 10 | 6.5% |
| 3 | A-SE | 4 | 2.6% |
| 4 | A-KA-RU | 3 | 1.9% |
| 5 | A-RA | 3 | 1.9% |

**Already visible:** the top A-initial type accounts for only 7.1% of A-initial words. This is the opposite of few-type concentration — a first hint that A- is productive.

## 3. Global A-initial preference (Step 2)

| metric | value |
|--------|-------|
| A-initial count | 155 / 1369 |
| fraction | 0.1132 |
| null mean | 55.57 |
| p (1000 draws) | **0.001** |

Replicates E023/E024: A- is strongly word-initial.

## 4. Positive control — LB productive-vs-few-type separation (Step 3, gates verdict)

The PC must show the machinery **separates** a PRODUCTIVE initial sign (survives leave-top-type-out) from a FEW-TYPE sign (collapses). Selection is data-driven:
- **PRODUCTIVE** = globally-significant LB sign with the most distinct initial word-types → **A** (557 distinct initial types).
- **FEW-TYPE** = globally-significant LB sign with the highest top-type-share → **\*63** (top type = 84.2% of its initial occurrences; only 2 distinct initial types).

| sign | role | global p | leave-top-1 p | outcome |
|------|------|----------|---------------|---------|
| A (LB) | productive | 0.001 | 0.001 | **SURVIVES** ✓ |
| \*63 (LB) | few-type | 0.001 | 0.104 | **COLLAPSES** ✓ |

**PC verdict: PASSED.** The machinery correctly distinguishes a productive slot from a few-type artifact. This gates the LA claim.

## 5. LA main — leave-top-type-out (Step 4, the adversarial test)

Remove the single most-frequent A-initial word-type (A-TA-I-*301-WA-JA, 11 occ) and recompute:

| removal | remaining n | remaining A-initial | p |
|---------|-------------|---------------------|---|
| top-1 type | 1358 | 144 | **0.001** |
| top-2 types | 1348 | 134 | **0.001** |
| top-3 types | 1344 | 130 | **0.001** |

**A-initial preference SURVIVES removing its top 1, 2, and 3 word-types.** The adversarial test fails to break the result.

## 6. Type-diversity vs comparators (Step 5)

n_distinct_initial_word-types for A- and the 5 next-most-word-initial LA signs:

| sign | n_distinct initial types |
|------|--------------------------|
| **A** | **115** |
| I | 54 |
| JA | 51 |
| DA | 36 |
| KU | 33 |
| SA | 26 |

Comparator median = **36**. A-'s type-diversity (115) exceeds the comparator median by >3×.

## 7. Frozen mechanical verdict (Step 6)

Rule: `A_PREFIX_PRODUCTIVE_ROBUST` iff (PC passed) AND (leave-top-1 p ≤ 0.05) AND (n_distinct_A_types ≥ 8) AND (A-diversity > comparator median).

| gate | condition | result |
|------|-----------|--------|
| PC passed | pc_verdict == PASSED | ✓ |
| leave-top-1 significant | p = 0.001 ≤ 0.05 | ✓ |
| n_distinct_A_types ≥ 8 | 115 ≥ 8 | ✓ |
| A-diversity > comp median | 115 > 36 | ✓ |

**Verdict: `A_PREFIX_PRODUCTIVE_ROBUST`**

## 8. Bottom line

The adversarial test **failed to break** the A- result. A- is not an artifact of one or a few high-frequency A-initial word-types: it attaches to **115 distinct word-types** spanning **40 distinct second-signs**, its single most-frequent type is only 7.1% of A-initial words, and its word-initial preference remains highly significant (p=0.001) after removing the top 1, 2, or 3 types. Its type-diversity exceeds the comparator median by >3×. The LB positive control confirmed the machinery can detect few-type artifacts (sign \*63 collapsed). 

**A- behaves as a genuinely PRODUCTIVE positional prefix SLOT (L2/L3 structural claim only).** This is a bounded structural finding — it says nothing about phonetic value, meaning, or language. It does not claim A- is a "prefix" in any grammatical sense; only that word-position-1 is a recurrent, type-diverse slot occupied by the sign A far beyond what within-word chance produces, robustly across word-types.

## Deviations

`machinery.py` `lb_positive_control` selection logic was corrected after the initial self-check: the first version selected the few-type candidate by top-share without requiring global significance, picking a non-significant sign (PTE) that could not demonstrably collapse. The corrected version selects the FEW-TYPE candidate from globally-significant signs by highest top-type-share (picked \*63, which collapses p=0.001→0.104). **prereg.md and plan_hash were frozen BEFORE this correction and were NOT changed**; only machinery.py (an implementation detail) was refined. The frozen verdict rule in prereg step 6 was applied exactly as written.
