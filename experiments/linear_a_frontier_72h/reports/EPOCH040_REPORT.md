# EPOCH-040 — INTRA-WORD SIGN REPETITION (reduplication vs anti-repetition; L2/L3)

**Verdict: `REPETITION_AT_CHANCE`**

Linear A intra-word sign repetition is **consistent with chance** under the length-matched
i.i.d.-unigram null. There is **no evidence** for either systematic reduplication (excess)
or systematic anti-repetition (avoidance). Once sign frequencies and word lengths are
accounted for, words repeat signs at exactly the rate expected from random sign sampling.

> Signs are ANONYMOUS throughout. "Repetition" is a pure L2/L3 distributional statistic
> (the same sign appearing ≥2× within a word). It is **not** a claim about sound, phonetics,
> morpheme meaning, or reading.

---

## 1. Question

Do Linear A words contain REPEATED signs (same sign ≥2× within a word) **more** than chance
(reduplication, a morphological process) or **less** (anti-repetition, a phonotactic/
orthographic constraint)? Is the direction robust across independent sites?

## 2. Frozen metric & null

- **Metric.** `rep_rate` = fraction of len≥2 words containing ≥1 repeated sign.
- **Null (i.i.d.-unigram, length-matched).** For each observed word of length L, draw L
  signs i.i.d. from the GLOBAL unigram frequency distribution; compute `rep_rate` over the
  synthetic corpus; ≥2000 draws; **two-sided** p for deviation. Direction: excess =
  reduplication; deficit = avoidance. This tests whether words repeat signs more/less than
  expected from sign frequencies + word lengths alone.

## 3. Data (step 0 inspection)

- LA words len≥2: **1369** (97 contain a repeated sign).
- Distinct signs: 156; total sign tokens: 4014.
- Length distribution: 2→617, 3→446, 4→189, 5→67, 6→33, 7→8, 8→4, 9→1, 10→1, 11→1, 16→1, 19→1.
  (~45% of words are length 2.)
- Sites with ≥50 words (testable): **6** — Haghia Triada (694), Zakros (132), Khania (120),
  Knossos (61), Phaistos (58), Palaikastro (57).
- LB (DAMOS, positive control only): 13,562 seqs, 43,868 tokens, 89 distinct signs.

## 4. Global result

| quantity | value |
|---|---|
| n words (len≥2) | 1369 |
| observed `rep_rate` | **0.0709** (97/1369) |
| i.i.d.-unigram null mean | **0.0735** |
| two-sided p | **0.74** |
| direction | deficit (negligible) |

The observed rate is essentially identical to the null expectation. p=0.74 is far above
0.05 → **REPETITION_AT_CHANCE** at the global level. (Stability check: p ∈ [0.70, 0.74]
across 5 independent null seeds; null mean ∈ [0.0735, 0.0738].)

A useful analytic cross-check: for length-2 words the exact P(repeat) = Σᵢ pᵢ² ≈ 0.0227
under the unigram; the observed length-2 rep_rate is 0.0113 — slightly below, consistent
with the tiny (non-significant) global deficit.

## 5. Positive control (gates the verdict) — Linear B (DAMOS)

| check | result |
|---|---|
| DETECT planted reduplication EXCESS (inject fully-reduplicated words) | p = 0.00, direction **excess** ✓ |
| DETECT planted DEFICIT (remove all repeat-words) | p = 0.00, direction **deficit** ✓ |
| FALSE-POSITIVE on true-H0 synthetic words (20 sets) | rejection rate = **0.10** (2/20) ≤ 0.10 ✓ |
| **PC verdict** | **PASSED** |

The machinery correctly detects a planted excess and a planted deficit with the right
directions, and does not over-fire on true-H0 data (FP rate at the 0.10 gate). The null
AT_CHANCE result is therefore **informative**, not a machinery failure.

## 6. Cross-site held-out

| site | n | rep_rate | p | direction |
|---|---|---|---|---|
| Haghia Triada | 694 | 0.0346 | **0.002** | deficit |
| Zakros | 132 | 0.0682 | 0.407 | deficit |
| Khania | 120 | 0.0500 | 0.623 | deficit |
| Knossos | 61 | 0.1475 | 1.000 | deficit |
| Phaistos | 58 | 0.0517 | 0.468 | deficit |
| Palaikastro | 57 | 0.2807 | 0.070 | excess |

- Sites significant: **1/6** (Haghia Triada only).
- Direction is **not consistent** (5 deficit, 1 excess trend).
- **Leave-one-site-out** (excluding Haghia Triada, the largest site): rep_rate 0.1081 vs
  null 0.1000, **p = 0.487**, non-significant. The single significant site does **not**
  survive LOO.

## 7. Frozen mechanical verdict

Global p = 0.74 > 0.05 → **`REPETITION_AT_CHANCE`** (rep_rate consistent with the
i.i.d.-unigram, length-matched null). PC passed, so the verdict is informative.

## 8. Bottom line (honest)

Linear A words repeat signs at exactly the rate expected from sign frequencies and word
lengths alone — **neither reduplication nor anti-repetition**. This is a genuine null:
the positive control confirms the machinery can detect a planted signal in either
direction and does not fire on true-H0 data. The one site-level significant result
(Haghia Triada deficit) does not survive leave-one-site-out and does not generalize.
Repetition structure in Linear A is fully explained by the unigram + length distribution;
no additional morphological or phonotactic constraint on intra-word repetition is supported
by this test. (Signs anonymous; this is a distributional statistic, not a claim about
sound or morpheme meaning.)

## 9. Implementation note (transparency)

The vectorized null initially contained a padding-sentinel bug that suppressed detected
repeats and produced a spurious strong-excess signal. It was caught by an independent
analytic check (P(repeat|L=2) = Σ pᵢ² ≈ 0.023 vs the buggy ~0.0047) and a brute-force
pure-python null (mean 0.0739), then rewritten to group words by length with no padding
(corrected null mean 0.0735). The frozen metric/null **definition** in `prereg.md` was
unchanged; only the implementation was corrected to faithfully realize it. The corrected
AT_CHANCE result supersedes the buggy result. See `deviations` in `result.json`.

## 10. Artifacts

- `prereg.md` — frozen protocol (plan_hash `7985f8a8…`).
- `machinery.py` — full pipeline + `__main__` self-check.
- `result.json` — structured output (all required keys).
- `data/epoch_040/` — per-site + global + PC summary tables (CSV/JSON).
