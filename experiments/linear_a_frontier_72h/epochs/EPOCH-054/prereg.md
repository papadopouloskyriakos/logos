# EPOCH-054 — Preregistration: Benford's Law on Linear A Numeral Magnitudes

**Campaign:** Linear A frontier-72h
**Epoch:** EPOCH-054
**Layer:** L2/L3 (structural magnitude statistics; NO decipherment)
**Operator:** logos z.ai worker (GLM-5.2)
**Status:** FROZEN before any analysis run.

## Question
Do the LINEAR A NUMERAL MAGNITUDES (the corpus `v` field of `num` tokens) follow BENFORD'S LAW
(first-digit P(d) = log10(1 + 1/d): 1≈30.1%, 2≈17.6%, ..., 9≈4.6%)?

Real accounting / natural-quantity data closely follows Benford; uniform, constant, or fabricated data does NOT.
This tests whether the numerals represent GENUINE ADMINISTRATIVE QUANTITIES (a plausibility check on the
corpus substrate as real economic data).

## Honest Caveat (NECESSARY-NOT-SUFFICIENT)
Benford-conformance is a **plausibility check on "real quantities"**, NOT a decipherment. Benford-consistency
is expected of most natural count/accounting data and is **necessary but not sufficient** evidence that the
magnitudes are genuine administrative quantities. It assigns NO phonetic or semantic value to any sign.
This is a structural property of the QUANTITIES, not a decipherment.

## Non-Circular / Discipline (hard constraints)
- **Magnitudes only.** Uses ONLY the integer `v` field of `num` tokens.
- **No sign values, no readings.** No sign is assigned any phonetic/semantic value.
- **L2/L3 ONLY.** Structural statistics on quantities.
- Prereg + plan_hash frozen BEFORE running. Positive control FIRST. Mechanical verdict from frozen rule.

## Data
- Source: `corpus/silver/inscriptions_structured.json`
- Extract all `num` tokens' `v` values with `v >= 1` (Benford applies to positive magnitudes).
- Record count of excluded `v < 1` (fractions/zeros), if any.

## Method (frozen)
1. First-digit distribution of magnitudes vs Benford expected.
2. Goodness-of-fit:
   - **Chi-square GoF** (df=8), report statistic and p.
   - **Benford MAD** (mean absolute deviation of observed vs Benford first-digit proportions) with
     **Nigrini conformity bands**:
       - MAD < 0.006 → close conformity
       - 0.006 ≤ MAD < 0.012 → acceptable conformity
       - 0.012 ≤ MAD < 0.015 → marginal conformity
       - MAD ≥ 0.015 → nonconformant
3. Report observed first-digit histogram vs Benford expected.

## Protocol
0. **Inspect:** n numerals with v≥1; magnitude range; first-digit histogram; excluded (v<1) count.
1. **Freeze** prereg + plan_hash; `machinery.py` with `__main__` self-check (validate Benford fitter on
   synthetic Benford data → conformant; on uniform-random → nonconformant).
2. **GLOBAL:** first-digit distribution; chi-square GoF p; Benford MAD + Nigrini band; classification.
3. **POSITIVE CONTROL FIRST** (gates verdict):
   - (a) DETECT: synthetic Benford-distributed magnitudes classify CONFORMANT; synthetic UNIFORM-random
     classify NONCONFORMANT (both directions correct).
   - (b) FP: false 'deviant' rate on true-Benford samples of LA sample size ≤ 0.10 across ≥ 20 draws.
   - If it cannot distinguish Benford from uniform OR is miscalibrated → MACHINERY_UNINFORMATIVE.
4. **LA CLASSIFICATION** (frozen thresholds):
   - CONSISTENT if MAD ≤ 0.012 (close/acceptable) OR chi-square p > 0.05.
   - DEVIANT if MAD > 0.015 AND chi-square p < 0.01.
   - INCONCLUSIVE otherwise.
   - Robustness: per-largest-site first-digit fit (corpus-wide vs HT-only).
5. **FROZEN MECHANICAL VERDICT:**
   - `NUMERALS_BENFORD_CONSISTENT` iff PC passed AND LA classification = CONSISTENT.
   - `NUMERALS_BENFORD_DEVIANT` iff PC passed AND LA classification = DEVIANT.
   - `NUMERALS_BENFORD_INCONCLUSIVE` iff borderline.
   - `BENFORD_UNDERPOWERED` iff < 100 numerals with v≥1.
   - `MACHINERY_UNINFORMATIVE` iff PC failed.

## Outputs (exact PATH CONTRACT paths)
- prereg.md, plan_hash.txt, machinery.py, result.json, report, data dir.
