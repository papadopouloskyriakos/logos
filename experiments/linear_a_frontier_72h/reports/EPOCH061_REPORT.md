# EPOCH-061 REPORT — Is the most frequent 'other' sign a systematic line-isolated document marker?

**Campaign:** Linear A frontier-72h · **Layer:** L2 (token-position structure) · **Verdict:** `STANDALONE_MARKER_CROSS_SITE`

## 1. Question (frozen in prereg)
Is the anonymous token TYPE whose `raw` contains `"\U0001076b"` (U+1076B; n=474, the single most frequent 'other' token, neither logogram nor fraction) a **systematic line-isolated document marker** — i.e. does it stand alone on its own content-line at a rate beyond a within-inscription position-shuffle null, and is that **cross-site**? Position-only; no sign value, reading, phonetics, or meaning.

## 2. Metric & null (frozen)
- **Line-isolation rate** = fraction of target tokens whose immediately-preceding token-type ∈ {nl, div, START} AND immediately-following token-type ∈ {nl, div, END}.
- **Null:** within each inscription, re-place the same number of target tokens uniformly at random among the inter-content-token gaps of the non-target skeleton (preserving nl structure + target count). ≥500 reshuffles (used 2000). Perm p = frac(null ≥ obs), one-sided enrichment.
- **Positive control:** synthetic. (a) DETECT — plant always-isolated corpus; expect p≤0.05. (b) FALSE-POSITIVE — plant uniform-random corpus; expect rejection ≤0.10 over ≥20 draws.

## 3. Inspect (Step 0)
- n target tokens = **474** across 14 sites; 5 sites have ≥15 targets (HT 187, Khania 154, Zakros 52, Knossos 28, Phaistos 22).
- 16 distinct `raw` strings contain U+1076B (mostly bare `\U0001076b`, plus a few fraction-adjacent clusters).
- Flanking histograms (before / after):

| side | nl | START/END | div | word | num | other |
|------|----|-----------|-----|------|-----|-------|
| before | 297 | 132 (START) | 11 | 20 | 5 | 9 |
| after  | 260 | 188 (END)  | 8  | 7  | 2 | 9 |

Boundaries (nl/div/START/END) dominate both sides; content tokens (word/num/other) touch the target on at least one side in only ~9% of cases.

## 4. Positive control (gates verdict) — SYNTHETIC, declared
- **DETECT:** always-isolated corpus → obs=1.000, null mean=0.298, **perm p=0.0020** (≤0.05). ✓
- **FALSE-POSITIVE:** uniform-random corpus → rejected in **0/25** draws, false-positive rate **0.000** (≤0.10). ✓
- **PC verdict: PASSED.** Self-check on a hand-built 1-target inscription reproduces the analytic null mean (0.3326 vs expected 0.3333).

## 5. Global result
| metric | value |
|--------|-------|
| n_target | 474 |
| isolated | 432 |
| **isolation_obs** | **0.9114** |
| isolation_null_mean | 0.2226 |
| **perm_p (2000 reshuffles)** | **0.0005** |

Observed isolation (91.1%) is **~4× the null** (22.3%); the null distribution never reaches the observed value (max null sample 0.276). Enrichment is overwhelming.

## 6. Cross-site (≥15 targets)
| site | n | obs | null | perm_p | direction |
|------|---|-----|------|--------|-----------|
| Haghia Triada | 187 | 0.947 | 0.203 | 0.0005 | enriched |
| Khania        | 154 | 0.929 | 0.264 | 0.0005 | enriched |
| Zakros        |  52 | 0.962 | 0.244 | 0.0005 | enriched |
| Knossos       |  28 | 0.571 | 0.187 | 0.0005 | enriched |
| Phaistos      |  22 | 0.909 | 0.175 | 0.0005 | enriched |

**5/5 testable sites** are significant and same-direction (enriched). Knossos is the weakest in absolute rate (57%) but still far above its null (19%). **Leave-one-site-out (drop HT):** obs=0.889, null=0.236, **p=0.0005** over 287 targets — survives.

## 7. Frozen mechanical verdict
PC PASSED ∧ global enriched (p=0.0005) ∧ ≥2 sites significant same-direction (5/5) ∧ survives LOO (p=0.0005).

→ **`STANDALONE_MARKER_CROSS_SITE`**

## 8. Bottom line (honest)
Yes. The anonymous token TYPE U+1076B is a **systematic, cross-site line-isolated document marker** in the Linear A administrative corpus: it stands alone on its own content-line in 91% of its 474 occurrences — about four times the rate expected from a within-inscription position shuffle (22%, p≈5×10⁻⁴) — and this holds independently at all five sites with adequate sample size and survives removal of the dominant site (Haghia Triada). Its behaviour is that of a structural/section/separator-type marker in the LA document apparatus. This is a pure L2 token-position finding: **no sign value, reading, phonetics, or meaning is assigned.**

## 9. Non-circularity
Target selected by raw-substring match only; metric is pure adjacent-token-type position structure; null preserves each inscription's non-target skeleton, nl structure, and target count. PC is synthetic and declared. Layer L2 only.

## 10. Outputs
- `experiments/linear_a_frontier_72h/epochs/EPOCH-061/prereg.md` (frozen)
- `experiments/linear_a_frontier_72h/epochs/EPOCH-061/plan_hash.txt` = `2f426f5eb22c79c70cf96a2278b5c3d2ca668095b963227334b514570493254d`
- `experiments/linear_a_frontier_72h/epochs/EPOCH-061/machinery.py` (self-checked)
- `experiments/linear_a_frontier_72h/epochs/EPOCH-061/result.json`
- `experiments/linear_a_frontier_72h/data/epoch_061/` (global null, flanking, cross-site, PC, LOO)
