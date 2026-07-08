# EPOCH-042 REPORT — SIGN POSITIONAL-ROLE SPECIALIZATION via ANALYTIC within-word null (L2/L3)

**Task:** EPOCH-042 · **Verdict: `SPECIALIZATION_UNDERPOWERED`** · **Layer: L2/L3** · `la_touched=true`

> Supersedes EPOCH-041. E041 was UNDERPOWERED at the NULL level: 2000 permutation
> draws imposed a p-floor of 1/2001 ≈ 5e-4 that collided with the Holm threshold
> across ~102 simultaneous (sign × position) tests, so 0 signs passed on BOTH LA
> and LB and the positive control FAILED. E042 replaces the permutation draws with
> the EXACT ANALYTIC within-word null (Poisson-binomial) — no draw floor.

---

## 1. The method fix (analytic Poisson-binomial null)

Under the within-word uniform permutation H0, for a word *w* of length *L*
containing sign *S* exactly *k_w* times, the probability that a SPECIFIC position
*p* (initial index 0, or final index L−1) holds *S* is **k_w / L**, independently
across words. The null count of *S* at *p* is therefore a **Poisson-binomial** over
the per-word Bernoulli probabilities *p_w = k_w / L_w*. The one-sided upper-tail
p-value is *P(X ≥ observed)*, computed by **exact DP/convolution** (every LA test
had n_bernoulli ≤ 4000, so no normal approximation was needed; method recorded per
test). Holm correction across all (sign × position) tests at family α = 0.05.

**Self-check (machinery `__main__`):** the analytic upper tail was validated
against a 400 000-draw brute-force within-word permutation on a small synthetic
case — analytic p = 0.00579 vs brute-force p = 0.00555 (|diff| = 0.00024 < 0.01
tolerance). PMF normalization and a known-value check also pass.

## 2. POSITIVE CONTROL (gates the verdict) — **PASSED**

| Quantity | Value |
|---|---|
| LB specialized fraction (DETECT) | **0.526** (41 / 78 signs) |
| LB initial-specialized | 24 |
| LB final-specialized | 17 |
| LB within-word-shuffled fraction (FALSE-POSITIVE) | **0.0006** (mean over 20 sets) |
| False-positive rate | 0.0006 (≤ 0.10 gate) |
| Max shuffled fraction across 20 sets | 0.0128 |
| PC verdict | **PASSED** (detect = true, fp_ok = true) |

The analytic machinery now **DETECTS** Linear B's known positional structure
(52.6% of LB signs are position-specialized, with both word-initial and word-final
concentration) and **does NOT fire** on within-word-shuffled LB words (where real
positional structure is destroyed): 0.0006 mean, max 0.013 — well under the 0.10
false-positive gate. **E041's `MACHINERY_UNINFORMATIVE` was a permutation p-floor
artifact, not a real null result. The machinery is now informative.**

## 3. LA GLOBAL result

- Words len ≥ 2: **1 369** · Signs tested (≥15 occ): **51**
- **Specialized: 17 / 51 = 0.333** (Holm-corrected, family α = 0.05)
- **Initial-specialized: 6** (word-starter tendency)
- **Final-specialized: 11** (word-ending tendency)

### Specialized signs (ANONYMOUS; sorted by preferred position then Holm p)

| Sign | Preferred | Initial rate | Final rate | Holm p |
|---|---|---|---|---|
| S11 | final | 0.065 | **0.848** | 1.3e-13 |
| S07 | final | 0.100 | 0.700 | 1.8e-06 |
| S13 | final | 0.226 | 0.602 | 1.4e-05 |
| S09 | final | 0.061 | 0.796 | 1.8e-05 |
| S16 | final | 0.000 | **0.882** | 5.1e-05 |
| S06 | final | 0.125 | 0.650 | 1.1e-03 |
| S10 | final | 0.148 | 0.537 | 1.6e-03 |
| S14 | final | 0.143 | 0.538 | 2.5e-03 |
| S01 | final | 0.095 | 0.762 | 1.0e-02 |
| S17 | final | 0.056 | 0.611 | 1.1e-02 |
| S12 | final | 0.167 | 0.517 | 2.8e-02 |
| S03 | initial | **0.906** | 0.047 | 3.9e-59 |
| S05 | initial | 0.664 | 0.104 | 7.3e-10 |
| S04 | initial | 0.533 | 0.147 | 4.8e-06 |
| S15 | initial | 0.609 | 0.188 | 1.3e-05 |
| S08 | initial | 0.744 | 0.128 | 1.9e-04 |
| S02 | initial | **1.000** | 0.000 | 2.7e-03 |

Final-specialized signs concentrate strongly at word ends (rates up to 0.88,
Holm p down to ~1e-13); initial-specialized signs concentrate strongly at word
starts (rates up to 1.00, Holm p down to ~1e-59). Both tails are far above the
within-word null. The final-heavy split (11 vs 6) is consistent with templatic /
slot-like word structure (word-ending signs).

> Signs are ANONYMOUS (S01–S17). "Specialized" is a positional-distribution
> statistic, NOT a morpheme-with-meaning. No sign is named a suffix / prefix /
> case-ending.

## 4. CROSS-SITE held-out — **UNDERPOWERED at the ≥200-token gate**

| Site | Word tokens (len≥2) | Specialized fraction |
|---|---|---|
| Haghia Triada | 694 | **0.306** |
| Zakros | 132 | (< 200, not testable) |
| Khania | 120 | (< 200, not testable) |
| Knossos | 61 | (< 200) |
| Phaistos | 58 | (< 200) |
| Palaikastro | 57 | (< 200) |

- **Sites with ≥200 tokens: 1** (Haghia Triada only).
- Leave-one-site-out (excluding HT), on 675 words: specialized fraction **0.220** (≥ 0.20).
- The global signal (0.333), the LOO signal (0.220), and the HT-only fraction
  (0.306) all exceed 0.20 / 0.15, BUT the frozen cross-site gate requires **≥3
  sites with ≥200 tokens**, which the LA corpus does not satisfy.

## 5. FROZEN MECHANICAL VERDICT

Precedence: **PC gates everything → data adequacy → fraction thresholds.**

1. PC: **PASSED** (detect + false-positive both OK) → not `MACHINERY_UNINFORMATIVE`.
2. Data adequacy: sites with ≥200 tokens = **1 (< 3)** → **`SPECIALIZATION_UNDERPOWERED`**.

The positional-specialization signal is present and the machinery is now
informative, but the cross-site robustness test cannot be executed at the
preregistered ≥200-token threshold. The verdict rule blocks `HIGH_…_CROSS_SITE`
(which needs ≥3 sites ≥0.15) and `POSITIONAL_…_SITE_LOCAL` (which needs data
adequacy first) on data-adequacy grounds, not on the fraction values.

## 6. Honest bottom line

The analytic-null fix worked: the positive control now passes cleanly (LB 0.526
specialized vs 0.0006 on shuffled), and Linear A shows a **substantial**
positional-specialization signal — **one third of tested signs (17/51)** are
Holm-specialized, with a final-heavy split (11 final vs 6 initial) that is
consistent with templatic word structure. **However, the verdict is
`SPECIALIZATION_UNDERPOWERED`**: only Haghia Triada has ≥200 word-tokens, so the
frozen ≥3-site cross-site robustness gate cannot be met by the current corpus.
The signal is not an HT-only artifact (LOO excluding HT still gives 0.220), but
that is a single-site + pooled check, not the multi-site test the rule requires.
A successor epoch should pre-register a lower per-site token threshold (≥80 or
≥100 yields 3 sites: HT, Khania, Zakros) to actually run the cross-site test.

## Outputs

- `experiments/linear_a_frontier_72h/epochs/EPOCH-042/prereg.md` (frozen)
- `experiments/linear_a_frontier_72h/epochs/EPOCH-042/plan_hash.txt` (frozen)
- `experiments/linear_a_frontier_72h/epochs/EPOCH-042/machinery.py` (analytic Poisson-binomial + self-check)
- `experiments/linear_a_frontier_72h/epochs/EPOCH-042/result.json`
- `experiments/linear_a_frontier_72h/data/epoch_042/_run_full.json` (raw)
- this report
