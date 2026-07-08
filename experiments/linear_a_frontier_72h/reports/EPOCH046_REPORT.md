# EPOCH-046 REPORT — Word-Length Distribution Shape / Generative Process

**Campaign:** Linear A frontier-72h · **Epoch:** 046 · **Layer:** L2/L3 (morphological typology)
**Operator:** logos z.ai research worker (GLM-5.2) · **Discipline:** STRICT LOGOS (proposer/operator; mechanical verdict)

## Question
Is the Linear A word-length distribution **GEOMETRIC/exponential** (memoryless concatenation —
each additional sign added with roughly constant continuation probability; agglutinative/
concatenative morphology) or **PEAKED/templatic** (a preferred word size with mode ≥ 2; fixed
templates / root-and-pattern)? And is the shape **consistent across sites**? Pure length
structure (L2/L3); signs ANONYMOUS; no phonetics/sound/meaning/reading.

## Verdict (mechanical, frozen rule)
### **`WORD_LENGTH_INCONCLUSIVE`**

## Positive Control (gates the verdict) — **PASSED**
The classifier must DETECT both directions on synthetic data of known shape:
- Synthetic GEOMETRIC (p=0.55, n=5000) → labeled **`geometric`** ✓
- Synthetic PEAKED (shifted-Poisson λ=3, mode≥2, n=5000) → labeled **`peaked`** ✓

Both correct → **PC PASSED**. Machinery is informative.

**LB (Linear B) control benchmark** (sanity / classifier discrimination on real data):
- LB word lengths: n=13,562, **mode=3**, mean=3.23, classified **`peaked`** (peaked BIC beats
  geometric by ≈12,400). LB has a strong preferred word length of 3 — a genuinely
  peaked/templatic shape. This confirms the classifier discriminates the two regimes on real
  data and that LA's profile (below) is qualitatively different.

## Global LA result
| statistic | value |
|---|---|
| n words | 3,147 |
| **mode** | **1** |
| mean | 1.84 |
| geometric p̂ | 0.543 |
| geometric GoF p | **1.8 × 10⁻¹²** (REJECTED) |
| peaked_BIC − geom_BIC | **+661.4** (geometric far better) |
| **classification** | **INCONCLUSIVE** |

Histogram (length: count): `1:1778, 2:617, 3:446, 4:189, 5:67, 6:33, 7:8, 8:4, 9+:4`.

The distribution is **monotone-decreasing from k=1** (mode=1) and geometric **massively** beats
peaked by BIC (+661). However, the strict chi-square geometric goodness-of-fit is **rejected**
at n=3147. The deviation is structural, not noise: a **dip at length 2** (obs 617 vs expected
781, −21%) and a **bump at length 3** (obs 446 vs expected 357, +25%). Under the frozen rule
(geometric requires mode==1 AND GoF p>0.05), the global unit is **INCONCLUSIVE**.

## Cross-site (sites with ≥ 50 words)
| Site | n | mode | mean | geom GoF p | classification |
|---|---|---|---|---|---|
| Haghia Triada | 1891 | 1 | 1.62 | 0.0 | INCONCLUSIVE |
| Khania | 368 | 1 | 1.51 | 0.708 | **geometric** |
| Zakros | 218 | 1 | 2.22 | 4.5e-4 | INCONCLUSIVE |
| Phaistos | 110 | 1 | 2.02 | 0.106 | **geometric** |
| Knossos | 98 | 1 | 2.61 | 0.108 | **geometric** |
| Palaikastro | 77 | 1 | 2.96 | 0.486 | **geometric** |
| Arkhalkhori | 63 | 1 | 2.06 | 0.501 | **geometric** |

**Shape counts:** geometric 5 / INCONCLUSIVE 2 / peaked **0**. Every site has mode=1; no site
is peaked/templatic. The two INCONCLUSIVE sites (HT, Zakros) fail only the geometric GoF, never
in the peaked direction. **LOO** (Haghia Triada excluded, n=1256): mode=1, GoF p=0.0076 →
**INCONCLUSIVE**.

## Why INCONCLUSIVE (not GEOMETRIC_CROSS_SITE)
The frozen `WORD_LENGTH_GEOMETRIC_CROSS_SITE` gate requires, among other things, that the
**global** shape be geometric with adequate GoF. Although 5/7 sites individually fit geometric
and the global shape is monotone-decreasing with geometric beating peaked by >600 BIC, the
**global geometric GoF is rejected** (p≈0) and **LOO is INCONCLUSIVE** — so the strict frozen
gate is not met. The honest mechanical outcome is INCONCLUSIVE: the LA length distribution is
**geometric-like but not a clean memoryless geometric process**, and it is **definitively not
peaked/templatic**.

## Bottom line (honest)
LA word lengths are **monotonically decreasing from length 1 at every site and globally, and
never peaked/templatic** — strongly suggestive of memoryless/concatenative morphology rather
than fixed templates. But the pure-geometric fit is **rejected at large n** by a systematic
length-2 dip / length-3 bump, so under the frozen rule the shape is **INCONCLUSIVE** (geometric-
like, not clean geometric). LB, by contrast, is cleanly **peaked** (mode 3). Length distribution
only; no phonetics/meaning inferred.

## Non-circularity
Pure word-LENGTH distributional statistics on ANONYMOUS sign ids. No phonetics, sound, meaning,
reading, or sign-value inference. Length = `len(signs)` only. LB used as positive-control
benchmark only (control-only); the LB peaked result is a classifier-discrimination/sanity check,
not evidence about LA language. Verdict is mechanical from the frozen rule. L2/L3 only.

## Deviation
Initial chi-square binning did not absorb the geometric tail mass beyond the max observed length
into the final bin (yielding NaN GoF / sum-mismatch). Corrected to implement the FROZEN method
as stated (tail-collapsed bins, expected ≥ 5, total expected == n). Frozen method, decision rule,
seeds, and verdict logic unchanged; only binning arithmetic fixed to match the prereg. Reported
result is post-fix.

## Artifacts
- prereg: `experiments/linear_a_frontier_72h/epochs/EPOCH-046/prereg.md`
- plan_hash: `experiments/linear_a_frontier_72h/epochs/EPOCH-046/plan_hash.txt`
- machinery: `experiments/linear_a_frontier_72h/epochs/EPOCH-046/machinery.py`
- result: `experiments/linear_a_frontier_72h/epochs/EPOCH-046/result.json`
- data: `experiments/linear_a_frontier_72h/data/epoch_046/` (length_histograms.json, per_site_fits.json)
