# EPOCH-018 — Dedicated adaptive-null family for the E013 decomposition cross-script channel (Constitution §12, gate A)

**Verdict (mechanical): `CHANNEL_SURVIVES_ADAPTIVE_NULL`** — PC-1 PASS, deflated adaptive
p = 0.003 (< alpha 0.01), lift over the matched null mean = 4.14×.

**Stage header (Art. XXII).** Articles triggered: VII (search receipt: the channel's real
architecture history — E008/E009/E013, K=3 — enumerated and Bonferroni-applied, not just
E013's own frozen hyper-rules), VIII (the adaptive null *is* the effective-n correction: it
replaces an iid-uniform-rank null with one that burns the real frequency/degree/pairing DOF),
IX (adaptive p, null mean/p95, and observed MRR reported side-by-side on every number), XI/XII
(AB-value identity + LB font gallery are Unicode/font-standard ground truth, independent of the
extraction pipeline; components stay anonymous 13-dim vectors; synthetic PC uses arbitrary
integer sign IDs, never real values), XVII (append-only — EPOCH-013's `result.json` is
untouched; this is a declarative correction to its own weaker null, cross-referenced both ways),
XVIII (SigLA trace-standardization caveat inherited unchanged; an added open-limitation note on
shared-pipeline confounds the adaptive null cannot see), XXII (this header + compliance line
below). Gates: prereg frozen BEFORE any null realization
(sha256 `b0dd95792b5c9a2eaa4c6814f4d537c1d51d137eaba6e5ae492f0523640ddc45`); positive control ran
FIRST; fail-closed thresholds frozen in prereg. Seed 20260708. Claim layer: **L1 only** — this
epoch assigns zero phonetic values and touches no transfer licence.

## Question

EPOCH-013 reported that a bag-of-components matcher beats E009's whole-glyph matcher on the
identical LEG-1 frame (57 shared AB values, 74-item LB font gallery): agg MRR 0.2470 vs 0.1710
(+44.5%), p=5.0e-05 — but that p came from an **iid-uniform-rank** null, which only rules out
"ranks are uniform noise." It does not rule out "the lift is a generic artifact of shared
component-shape frequency" (most components in any script are short strokes, dots, or simple
junctions). §12 of the campaign requires ≥200-realization adaptive-null families that actually
preserve the nuisance structure (component frequency, per-sign component count, cross-script
pairing DOF) that could inflate MRR without a genuine LA↔LB shape correspondence. This epoch
supplies one, targeted squarely at the newest apparent positive.

## Search receipt (Art. VII)

Exactly **3** epochs in this campaign computed a comparable LA→LB-font-gallery MRR statistic
(grep of every `result.json` for the `"gallery_n": 74` signature): E008 (single-component
stroke pilot, held-out MRR 0.273, n=4 — too small to confirm alone, but a real prior attempt);
E009 (whole-glyph matcher, MRR 0.1710, n=57 — the frozen baseline); E013 (decomposition matcher,
MRR 0.2470, n=57 — under test here, explicitly framed as "beats E009"). **K=3.** No
hyperparameter sweep occurred *within* E013 (its K=12/3%/70%/13-dim/λ-median rule was frozen
once, pre-run). Deflated p = Bonferroni(K=3) applied to the adaptive p below.

## Step 1 — byte-for-byte reproduction

E013's published `components.json` (4,508 usable instances, raw component bags + labels +
status) reloaded; LB font gallery rebuilt via E013's **own imported** `decompose`/
`comp_features` functions (not reimplemented) over the same 74 renders; pooled (mean, sd), λ
(20,000-draw seeded median), and the 57-value eligible frame reconstructed identically.

| | reproduced | stored (E013 `result.json`) | diff |
|---|---|---|---|
| LEG-1 (`e009_ok_only`) agg MRR | 0.24701551940826028 | 0.24701551940826028 | **0.0** |

Exact match — no re-derivation ambiguity entered the null.

## Step 2 — adaptive null (PERMUTE, primary, ≥200 required)

**Null model:** pool every kept z-scored component vector across all `status=="ok"` usable
instances (the full LEG-1 query universe — 3,744 instances, not just the 57-value eligible
subset, for corpus-wide frequency fidelity); record each instance's component count (degree);
draw a uniform random permutation of the pooled vectors; re-chop the permuted pool into bags
using the ORIGINAL per-instance degree sequence. This is an exact bijection of the same
multiset onto the same slot sizes: it preserves the component-frequency profile exactly (every
real vector used once, globally, as before — a permutation, not a resample), the
component-count-per-instance distribution exactly (slot sizes literally unchanged), and still
has to match the real, fixed LB gallery (the cross-script pairing DOF the "generic artifact"
hypothesis needs). Gallery bags, λ, pooled stats, and instance→AB-value grouping are held at
their Step-1 observed values; only LA-side component IDENTITY is randomized.

| | value |
|---|---|
| N realizations | 999 (target 300 in prereg; raised — see Deviations) |
| null mean / std | 0.05966 / 0.00976 |
| null p5 / p50 / p95 / max | 0.04659 / 0.05783 / 0.07739 / **0.09592** |
| **observed (real) agg MRR** | **0.24701** |
| raw adaptive p | **0.001** (0/999 null draws ≥ observed) |
| Bonferroni-deflated p (K=3) | **0.003** |
| lift over null mean | **4.14×** |
| observed − null p95 | **+0.170** |
| z (observed vs null, parametric x-check only) | ≈19.2 SD |

The observed statistic exceeds **every single one of 999** frequency/degree-matched null
draws; the null's own max (0.0959) is barely above chance-uniform territory relative to the
real value. This is not a marginal call.

**Weaker comparison (BOOTSTRAP, i.i.d.-with-replacement, ignores exact frequency, N=500,
NOT confirmatory):** mean 0.05945, p95 0.07816, raw p=0.002 — nearly identical to PERMUTE.
The frequency-exactness distinction between the two null designs makes essentially no
difference here; the real signal is far enough outside either null that the choice between
"exact multiset permutation" and "with-replacement resample" doesn't matter at this scale.

## Step 4 — positive control (ran before the real-data null was interpreted)

- **PC-signal** (M=25 synthetic signs, planted per-sign query↔gallery component
  correspondence): observed agg MRR **0.98** vs PERMUTE-null mean 0.135, p95 0.202 (N=250) →
  **p=0.004 < 0.01, obs > p95 — PASS.** The null correctly rejects H0 when a real
  correspondence is planted.
- **PC-null** (same vocabulary, components drawn i.i.d. from the global prototype pool,
  independent of nominal sign — no true correspondence): leave-one-out calibration on its own
  250 PERMUTE realizations gives **FPR = 0.008 at alpha=0.01** (2/250), inside the
  Binomial(250, 0.01) 95% band [0, 0.024] — **well-calibrated, PASS.**
- **PC-1 PASS := both.** The adaptive-null machinery is validated for both power (detects a
  planted signal) and calibration (does not over-fire on pure noise) before being trusted on
  the real E013 statistic.

## Deviations (Art. XVII, `epochs/EPOCH-018/DEVIATIONS.md`)

The first pass at the prereg's *target* N (300 PERMUTE / 250 BOOTSTRAP — both already
satisfying the *required* ≥200 floor) put 0/300 null draws at or above the observed MRR, so the
raw adaptive p sat exactly at the Monte Carlo floor `1/301=0.00332`; after ×3 deflation this
became `0.00997`, clearing `alpha=0.01` by construction of the floor rather than because the
effect was weak. N was raised to 999/500 (still ≥200 throughout) to remove the
floor-induced ambiguity; the verdict bucket is identical at both N
(`CHANNEL_SURVIVES_ADAPTIVE_NULL`); both runs are recorded in `result.json`
(`first_pass_floor_note`). No threshold, hypothesis, or verdict rule was altered.

## Honest interpretation

The E013 decomposition channel's LEG-1 lift is **not** explained by generic component-shape
frequency, per-sign component count, or the cross-script pairing degrees of freedom alone — a
null that exactly preserves all three still tops out at MRR≈0.096 across 999 draws, four times
below the observed 0.247. Combined with EPOCH-013's own within-epoch adversary controls (aspect
0.0987, count 0.0915, both far below 0.2470) and this epoch's structure-matched permutation
null, the channel's calibration signal is robust across three independent ways of asking "is
this better than chance/structure?" **This still licenses nothing beyond L1** (Art. V): it says
the bag-of-components representation genuinely discriminates AB-value identity better than
chance or nuisance structure predicts on a **font-gallery, hand-traced-epigraphy** comparison —
it does not license a phonetic value, a reading, or any transfer licence (Art. XV: none earned,
none claimed here). E013's own `HOLD` gate (within-script self-retrieval on the expanded corpus)
still fails its bar — the two findings are compatible: the representation is a genuinely
better CROSS-script calibration channel and a genuinely worse WITHIN-script discriminator,
exactly as EPOCH-013 already characterized it.

**Open limitation not fixed by this design (Art. XVIII):** the adaptive null permutes
component IDENTITY across LA instances but cannot detect a confound shared by the LA extraction
pipeline and the LB font-rendering pipeline themselves (e.g. both use the same
`despeckle`/`skeletonize`/8-connectivity rules, so any systematic bias those rules impose on
*any* sign's component decomposition would inflate both sides identically and would NOT be
caught by this null, since the null never touches the shared processing code, only the
assignment of already-processed real vectors). This is a genuine caveat, not resolved here —
flagged for any future epoch that wants to push this channel further (e.g. an
independently-rendered LB gallery, or a leave-one-pipeline-step-out ablation).

**Caveats inherited from EPOCH-013 (Art. XVIII), unchanged:** SigLA traces are standardized
expert re-drawings — every retrieval number is an upper bound on photograph-level allography;
the LB gallery is a font, not epigraphic LB; nothing here licenses sign identity or value.

**Compliance line (Art. XXII):** prereg-frozen null design and thresholds applied unmodified
(one logged N-precision deviation, non-substantive, Art. XVII); positive control ran before
interpretation; verdict computed mechanically by
`scripts/epoch018_decomp_adaptive_null.py`; search-adjusted via K=3 architecture-search
receipt; EPOCH-013's `result.json` untouched — this report is the append-only cross-reference.
