# EPOCH-054 REPORT — Benford's Law on Linear A Numeral Magnitudes

**Campaign:** Linear A frontier-72h
**Epoch:** EPOCH-054
**Layer:** L2/L3 (structural magnitude statistics — NOT a decipherment)
**Verdict (mechanical, frozen rule):** `NUMERALS_BENFORD_DEVIANT`
**PC status:** PASSED

---

## 1. Question

Do the LINEAR A NUMERAL MAGNITUDES (the corpus `v` field of `num` tokens) follow BENFORD'S LAW
(first-digit P(d) = log10(1 + 1/d): 1≈30.1%, 2≈17.6%, …, 9≈4.6%)? Real accounting / natural-quantity data
closely follows Benford; uniform, constant, or fabricated data does not. This is a plausibility check on
whether the numerals represent genuine administrative quantities.

### Honest caveat (necessary-not-sufficient)
Benford-conformance is a **plausibility check on "real quantities," NOT a decipherment.** Benford-consistency
is expected of most natural count/accounting data and is **necessary but not sufficient** evidence that the
magnitudes are genuine administrative quantities. This test assigns NO phonetic or semantic value to any sign;
it is a structural property of the quantities only.

## 2. Discipline (non-circular)

- **Magnitudes only** — integer `v` field of `num` tokens.
- **No sign values, no readings.**
- **L2/L3 only.**
- Prereg + plan_hash frozen BEFORE running. Positive control FIRST. Mechanical verdict from a frozen rule.

plan_hash: `ec3370f947b690dec636160ac09946787f10ac7358a7c452046b544f20a44e1f  prereg.md`

## 3. Data inspection

| Quantity | Value |
|---|---|
| Total `num` tokens | 1276 |
| Numerals with v ≥ 1 | **1276** |
| Excluded (v < 1) | **0** |
| Magnitude range | 1 … 3000 |

No fractions or zeros in the corpus; all 1276 numeral magnitudes are positive integers and enter the analysis.

## 4. Positive control (gates the verdict) — PASSED

| Check | Result |
|---|---|
| Synthetic Benford magnitudes (n=1276) → classification | **CONSISTENT** (MAD=0.00572, *close*) ✓ |
| Synthetic uniform-random magnitudes (n=1276) → classification | **DEVIANT** (MAD=0.06412, *nonconformant*) ✓ |
| False-deviant rate on 20 true-Benford samples | **0.00 / 20** (≤ 0.10) ✓ |
| **PC verdict** | **PASSED** |

The fitter correctly distinguishes Benford from uniform in both directions and is well-calibrated
(false-deviant rate 0%). The machinery is informative.

## 5. Global LA result

**Observed vs Benford first-digit distribution (n=1276):**

| d | Observed count | Observed % | Benford % |
|---|---|---|---|
| 1 | 511 | **40.0%** | 30.1% |
| 2 | 241 | 18.9% | 17.6% |
| 3 | 142 | 11.1% | 12.5% |
| 4 | 114 | 8.9% | 9.7% |
| 5 | 102 | 8.0% | 7.9% |
| 6 | 77 | 6.0% | 6.7% |
| 7 | 40 | 3.1% | 5.8% |
| 8 | 29 | 2.3% | 5.1% |
| 9 | 20 | 1.6% | 4.6% |

| Statistic | Value |
|---|---|
| Benford MAD | **0.025106** → Nigrini band **nonconformant** |
| Chi-square GoF (df=8) | χ² = 107.61, **p ≈ 1.18 × 10⁻¹⁹** |
| **Classification (frozen rule)** | **DEVIANT** (MAD > 0.015 AND p < 0.01) |

The chi-square p-value was cross-validated against `scipy.stats.chi2.sf` to 15 significant digits.

## 6. Robustness — per-largest-site

| Site | n | MAD | band | χ² p | class |
|---|---|---|---|---|---|
| Haghia Triada | 834 | 0.02427 | nonconformant | <0.0001 | **DEVIANT** |
| Zakros | 126 | 0.03573 | nonconformant | 0.0065 | **DEVIANT** |
| Khania | 121 | 0.04324 | nonconformant | 0.0045 | **DEVIANT** |
| Phaistos | 37 | 0.09240 | nonconformant | 0.0001 | **DEVIANT** |
| Arkhalkhori | 33 | 0.04071 | nonconformant | 0.7773 | CONSISTENT (underpowered) |
| Tylissos | 31 | 0.03791 | nonconformant | 0.5827 | CONSISTENT (underpowered) |

The deviation is **corpus-wide, not HT-only**: the three largest sites (HT, Zakros, Khania, combined n=1081,
85% of the corpus) are each individually DEVIANT. The two small "CONSISTENT" sites have n<35 and are
underpowered (their MAD is in fact worse than the large sites; they fail to reject only because of low n).

## 7. Frozen mechanical verdict

PC PASSED. LA classification = DEVIANT (MAD=0.0251 > 0.015 AND χ² p ≈ 1.2e-19 < 0.01).

→ **`NUMERALS_BENFORD_DEVIANT`**

## 8. Interpretation — what kind of deviation?

Crucially, the LA magnitudes are **NOT uniform-random-like** (uniform would be the signature of fabricated
or constant data). Instead they show a **super-Benford / heavy-small-magnitude** pattern:

- Leading **1s are OVER-represented**: 40.0% observed vs 30.1% Benford expected.
- **High digits (7–9) are UNDER-represented**: 7.0% observed vs 18.0% Benford expected.

This shape is consistent with administrative tallies dominated by **small lot sizes and round numbers**
(many 1s, 10s, 100s), which is a known Benford-violator in real accounting data that mixes many small
transactions with few large ones. It is the *opposite* signature from random/fabricated data.

## 9. Bottom line (with necessary-not-sufficient caveat)

The Linear A numeral magnitudes **do NOT conform to Benford's Law** (MAD=0.025, χ² p≈10⁻¹⁹, DEVIANT), and
the deviation is corpus-wide. **However**, the deviation is a *super-Benford* excess of small leading digits
— the signature of small-lot / round-number administrative tallies, NOT of uniform or fabricated data. So
this result does **not** support "the numerals are fabricated/random"; if anything it is consistent with
real but small-magnitude-dominated accounting. Benford is a **necessary-not-sufficient** plausibility check,
not a decipherment: failure of strict Benford conformity here is most plausibly read as a mixture-of-scales /
rounding effect in genuine small-quantity tallies, and the question of whether the magnitudes are genuine
administrative quantities remains open pending scale-partitioned and per-commodity follow-ups (H1, H5).

## 10. Successor hypotheses

- **H1 (L2):** Partition numerals by preceding word/sign-cluster and re-fit Benford per partition to test
  whether the deviation is a mixture-of-scales effect.
- **H2 (L2):** Fit alternative first-digit models (truncated power law, log-normal) and compare AIC; the
  super-Benford shape suggests a steeper power-law tail.
- **H3 (L2):** Examine magnitude rounding/clustering (10, 20, 100) — round-number usage breaks Benford.
- **H4 (L3):** Compare LA first-digit profile to published Benford analyses of Mycenaean Linear B tablets.
- **H5 (L2):** Restrict to magnitudes ≥ 10 and re-test (small-integer rounding may drive the excess of 1s).
- **H6 (L3):** Test second-digit and first-two-digit Benford for a finer, rounding-robust conformity check.

## 11. Outputs

- `experiments/linear_a_frontier_72h/epochs/EPOCH-054/prereg.md`
- `experiments/linear_a_frontier_72h/epochs/EPOCH-054/plan_hash.txt`
- `experiments/linear_a_frontier_72h/epochs/EPOCH-054/machinery.py`
- `experiments/linear_a_frontier_72h/epochs/EPOCH-054/result.json`
- `experiments/linear_a_frontier_72h/data/epoch_054/benford_analysis.json`
- `experiments/linear_a_frontier_72h/reports/EPOCH054_REPORT.md` (this file)
