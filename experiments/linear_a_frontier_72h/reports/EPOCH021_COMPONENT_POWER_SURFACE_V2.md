# EPOCH-021 — Component-channel value-recovery identifiability surface, ATTEMPT 2 (redesigned) (§12 third power surface, gate A)

**Verdict (mechanical, fail-closed): `HARNESS_NOT_VALIDATED`.** The redesign FIXED E019's diagnosed
bug (an exact geometric tie from symmetric row/col block amplitude) — the oracle-ceiling check
climbed from 0.4514 (E019) to **0.8907** (this attempt), a fold improvement of ~2×, and
`PC-monotonic-q` now passes cleanly (ρ=1.0). But two of the four positive-control sub-checks still
fail: `PC-oracle-ceiling` misses its 0.9 bar by 0.009 (0.8907 vs 0.9 — close, not a clean pass), and
`PC-LB-point` fails clearly (0.2567 vs the 0.5 foothold, at the REAL, non-circularly-calibrated LB
channel quality). `PC-monotonic-b` also fails (ρ=0.6, p=0.28, not significant) as a direct
consequence of the LB-point noise floor. Per the prereg's fail-closed rule, this blocks any
graduation-eligible claim about LA's operating point. LA's real numbers are still reported below
(pre-committed, non-negotiable), but are NOT certified.

Frontier §12 (third power surface) · gate A · **attempt 2 of the redesign directed by the epoch
brief** · plan_hash `397633786d941f96f96d769ea6781c6a7a3a09d85ec4e81fe28b17f9fffa66a6` (prereg frozen
2026-07-08, before any cell of this final grid realized) · seed 20260708 · claim layer **L1**
(identifiability geometry only; no phonetic value, no transfer licence touched). Articles: V, VII,
VIII, IX, XI, XII, XV, XVII, XVIII, XXII.

## Relationship to E019 and what changed

E019 returned `HARNESS_NOT_VALIDATED` because its recovery method's positive control failed
outright (`pc_monotonic_b` ρ=0.0, `pc_oracle_ceiling` 0.4514, `pc_lb_point` 0.1145). Diagnosis
(§Diagnosis below) traced this to a genuine benchmark defect: the row-block (18 classes) and
column-block (5 classes) one-hot sub-vectors had EQUAL amplitude, so "differs only in row" and
"differs only in col" pairwise distances were both exactly `sqrt(2)`, and `KMeans(n_clusters=18)`
on the exact noiseless code reached the SAME globally-optimal inertia (72.0) via a non-row-
respecting partition as via the true row-partition — an exact tie in the objective landscape, not
an algorithm bug. This epoch fixes it two ways, per the brief's (1) and (2):

1. **Asymmetric block amplitude** (`A_ROW=1.3`, `A_COL=1.0`): breaks the tie. Diagnosed BEFORE
   freezing (on synthetic-only data, never touching LA's cell): even `A_ROW=1.1` already makes
   noiseless `KMeans` recover BOTH axes exactly (ARI=1.0/1.0). `1.3` was chosen for margin.
2. **Anchor-only learned metric with unseen-class generalization** (b>0 only): a per-dimension
   Fisher-like weight learned from the `b` anchors, smoothed via k=5 nearest-neighbour averaging in
   each dimension's own UNSUPERVISED marginal-variance space so that classes never seen among the
   anchors don't collapse to zero weight (E019's inherited nearest-centroid design left unreachable
   classes permanently misclassified; a naive un-smoothed Fisher weight was tried during redesign
   and diagnosed to have the SAME collapse problem — see §Diagnosis). Seeded weighted K-means:
   anchors hard-assigned to their known class, missing classes seeded via weighted-space
   k-means++, Lloyd iterations refine everything else.

Both fixes are disclosed pre-freeze diagnostic/calibration work (search receipt in
`epochs/EPOCH-021/prereg.md` §Search receipt) — never touching LA's real q=0.247 cell — and the ONE
resulting design is what is frozen and run exactly once at R=30 for the numbers below.

## Design as executed

- Grid: dense 18×5 = 90 signs, code = `concat(1.3·one-hot(row,18), 1.0·one-hot(col,5))`, 23-dim.
- Channel: query-side embedding = code + N(0, σ(q)²·I); σ RECALIBRATED (against the new
  asymmetric-amplitude code — achieving the same aggregate retrieval-MRR against a higher-baseline
  code requires proportionally more noise) by the identical bisection procedure as E019:

| q label | target MRR | σ (E021) | achieved MRR | σ (E019, for reference) |
|---|---|---|---|---|
| sub_LA_ref | 0.150 | 0.656 | 0.146 | 0.548 |
| **LA_measured** | **0.2470** | 0.500 | 0.251 | 0.416 |
| mid1 | 0.300 | 0.459 | 0.302 | 0.375 |
| **LB_within_script** | **0.3993** | 0.398 | 0.403 | 0.334 |
| mid2 | 0.550 | 0.336 | 0.549 | 0.281 |
| high | 0.750 | 0.273 | 0.751 | 0.229 |
| oracle | 1.000 | 0.000 | 1.000 | 0.000 |

- Recovery (frozen): `b=0` → unweighted `KMeans(k=18)`/`KMeans(k=5)` on the asymmetric-amplitude
  code (n_init=15, best-of-inertia); `b>0` → smoothed-Fisher-weighted seeded K-means (n_init=8,
  n_iter=25), anchors fixed to their true class, missing classes seeded via weighted-space
  k-means++ among unlabeled points. Scored held-out only. `ARI_combined = mean(ARI_row, ARI_col)`.
- Positive control (4 sub-checks, ALL required, bars UNCHANGED from E019): PC-monotonic-b
  (ρ(b,ARI) at q=LB_within_script ≥0.8), PC-monotonic-q (ρ(q,ARI) at b=12 ≥0.8),
  PC-oracle-ceiling (ARI≥0.9 at q=oracle,b=12), PC-LB-point (ARI≥0.5 at q=LB_within_script,b=12).
- Adversarial: identical grid, grading truth independently permuted per replicate (embeddings
  unchanged). Rule: max ARI_combined across all 35 cells < 0.05.

## Positive control: FAILED (2 of 4 sub-checks)

| sub-check | bar | E019 (attempt 1) | E021 (attempt 2) | pass? |
|---|---|---|---|---|
| PC-monotonic-b (ρ, LB-quality across b) | ≥0.8 | 0.0 (posthoc: −0.30) | **0.600** (p=0.28, n.s.) | **FAIL** |
| PC-monotonic-q (ρ, quality across at b=12) | ≥0.8 | 1.0 (posthoc: 1.0) | **1.000** | **PASS** |
| PC-oracle-ceiling (ARI, q=oracle b=12) | ≥0.9 | 0.4514 | **0.8907** | **FAIL** (0.009 short) |
| PC-LB-point (ARI, q=LB b=12) | ≥0.5 | 0.1145 | **0.2567** | **FAIL** |

`PC_PASS = False`. Per the frozen rule, verdict = `HARNESS_NOT_VALIDATED`.

## Diagnosis — what the redesign fixed, what it did not, and why

**Fixed cleanly:** `PC-monotonic-q` now passes with a perfect Spearman correlation — recovery
quality reliably tracks injected channel noise at a fixed generous (b=12) anchor budget, which
E019 also showed but this confirms the fix didn't break it. More importantly, `PC-oracle-ceiling`
moved from a decisive failure (0.4514, less than half the bar) to a NEAR-miss (0.8907, 0.009 below
the bar) — direct evidence the asymmetric-amplitude fix (FIX 1) resolves the geometric-tie bug: at
zero noise, the row axis is now recoverable (`ari_row=0.7814` at b=12, vs E019's row axis being at
or below the adversarial floor at EVERY oracle cell). The residual 0.009 gap and the b=2/b=4 dip
below the b=0 unsupervised level (oracle: b=0 ARI=0.9897 → b=2 ARI=0.3029 → b=4 ARI=0.5645 → b=8
ARI=0.6629 → b=12 ARI=0.8907, a clear NON-monotonic dip at low anchor counts before recovering) are
themselves diagnostic: the seeded-weighted-K-means Lloyd loop, with very few anchors constraining
very few of the 18 clusters, is occasionally pinned into a worse local optimum than the fully
unsupervised b=0 run — a real, mechanical property of this specific recovery method's small-b
regime, not a further geometry defect (the b=0 unsupervised run, unconstrained by any anchor,
reaches 0.99 at the SAME oracle noise level, showing the underlying geometry supports near-total
recovery; it's the SEEDING itself that is occasionally a worse starting point than none at all,
until enough anchors accumulate to dominate the seed).

**Not fixed, and analytically cannot be fixed by amplitude tuning alone:** `PC-LB-point` stayed
firmly below its foothold (0.2567 vs 0.5), and — unlike the oracle-ceiling gap — pre-freeze
diagnostic sweeps (search receipt) show this is NOT a matter of picking a bigger `A_ROW`. The
calibration procedure (unchanged from E019 by design, non-circular) ties σ(q) to a FIXED external
retrieval-MRR target (LA's or LB's real, already-measured channel quality). Diagnostic runs at
`A_ROW ∈ {1.3, 2.0, 3.0, 4.0}` show the calibrated σ needed to hit the SAME LB_within_script target
MRR grows *proportionally* with `A_ROW` (σ=0.40 at 1.3, 0.54 at 2.0, 0.73 at 3.0, 0.91 at 4.0) —
because the aggregate-MRR calibration statistic is computed on the FULL vector, a louder row block
requires proportionally louder noise to keep the SAME aggregate retrieval quality, which
self-cancels any row-specific SNR gain from a bigger amplitude ratio. The resulting LB-point
ARI_combined stayed in the same narrow 0.10–0.30 band across every `A_ROW` tried in diagnosis — an
analytically clean, reproducible invariance, not an under-tuned constant. This localizes the
epoch's real, sharper finding: **at LB's actual measured channel quality (aggregate retrieval MRR
≈0.40, itself a real, non-circular external number — E009), recovering an 18-class row partition
from only 12 anchors (covering, in expectation, ~9 of 18 classes — a `birthday-problem` coverage
gap independent of the recovery algorithm) is not achievable to the 0.5 foothold by any recovery
method tried, including one that learns its metric from the anchors and generalizes to unseen
classes.** This is a DIFFERENT diagnosis from E019's (an exact-tie GEOMETRY bug, now demonstrably
fixed — see the oracle-ceiling improvement) — attempt 2's blocking finding is a genuine
reachability/SNR ceiling at this (`b_max=12`, `n_c=18`, real-noise) operating region, not a
benchmark or algorithm defect.

**Adversarial control: PASSED cleanly** (max ARI_combined over all 35 shuffled-identity cells =
0.0058, well under the 0.05 bar) — the recovery pipeline is not exploiting generic cluster
structure independent of the real row/col correspondence; whatever partial recovery it achieves at
each (b,q) cell is tied to the real, non-shuffled channel structure.

## LA's operating point (reported, NOT certified — PC failed)

`(b=0, q=0.24701551940826028)` — citation unchanged from E019 (b=0: anchor-lattice WP-C
dependency-collapsed independent distinct-lineage anchor count = 0, `research/linear-a-anchor-lattice`
HEAD 28bbd59; q: E013/E018's real measured LEG-1 aggregate component-channel MRR).

- `ARI_row = 0.0679`, `ARI_col = 0.0896`, `ARI_combined = 0.0787` (95% CI [0.0718, 0.0857], R=30).
- Gap to foothold (0.5): **0.4213**. Gap to absolute (0.9): **0.8213**.
- Descriptively (not a certified finding): this is barely above the adversarial-shuffled floor
  (~0.006) and far below both bars — consistent with, though not statistically certifying (PC
  failed), the qualitative picture that zero anchors and LA's real (moderate) component-channel
  quality do not support value-class recovery on this surface.

## Contour (tested grid only, no interpolation)

- First `b` crossing the 0.5 foothold, by `q`: only `high` (b=8) and `oracle` (b=0) cross it among
  the 7 tested quality levels — `sub_LA_ref`, `LA_measured`, `mid1`, `LB_within_script`, `mid2`
  never cross the foothold at ANY tested anchor budget up to 12.
- First `q` crossing the 0.5 foothold, by `b`: at `b=0`, only `oracle` and `mid2`... — see raw
  JSON (`data/component_power_surface_v2/E021_surface.json`, `contour` key) for the full table;
  headline: at `b=2` NO tested quality level reaches the foothold (the seeding dip described in
  §Diagnosis), and at `b=8`/`b=12` only `high` and `oracle` do.
- First `b`/`q` crossing the 0.9 absolute bar: only `oracle` at `b=0` (0.9897) — no other cell in
  the entire 35-cell tested grid reaches 0.9, including `oracle` at every `b>0` (the seeding-dip
  effect keeps even the noiseless case below the bar until b=12, which itself narrowly misses at
  0.8907).

## Compliance line (Art. XXII)

Articles triggered: V (claim layer L1, held throughout — zero phonetic values, zero transfer
licences touched), VII (search receipt: one final frozen design; pre-freeze diagnostic/calibration
work on synthetic-only data disclosed in `epochs/EPOCH-021/prereg.md`), VIII (power/identifiability
characterized via ARI + 95% CI at every reported cell, not a bare point estimate), IX (every
headline number carries its adversarial-floor comparison and CI), XI/XII (non-circularity: the only
real-world inputs are E013/E018's already-published MRR and the anchor-lattice's already-closed
anchor count; neither is a phonetic value or an LA-side model input; `A_ROW`/`A_COL`/`K_SMOOTH` are
benchmark-design constants fixed by synthetic-only diagnosis before freezing, never fit to LA's own
numbers), XV (licence ledger unchanged — no licence earned or touched), XVII (append-only — E019 is
cited, not altered; this epoch's own DEVIATIONS.md records that execution matched the frozen prereg
exactly, no in-run deviation), XVIII (ASSUMPTION-E21-1..4 recorded in the prereg), XXII (this
header/compliance line). Fail-closed applied per rule: `PC_PASS=False` → verdict
`HARNESS_NOT_VALIDATED`, LA's cell reported descriptively only, not graduated.

## Successor hypotheses (for a hypothetical attempt 3, NOT run here)

1. Raise `b_max` beyond 12 (e.g. to 18–24) so the row axis's anchor coverage stops being capped by
   the birthday-problem gap (~9/18 at b=12) — the epoch brief pinned `B_LEVELS=[0,2,4,8,12]`
   unchanged, so this was out of scope here, but the diagnosis above suggests it, not amplitude
   tuning, is the lever that would move PC-LB-point.
2. A recovery method with an EXPLICIT coverage-aware seeding schedule (allocate the anchor budget
   deliberately to maximize distinct-class coverage rather than uniform random sampling) — would
   cleanly separate "is 12 anchors enough information in principle" from "did uniform random
   sampling waste anchors on already-covered classes."
3. Investigate the b=2/b=4 seeding-dip mechanically (its own root cause, not yet isolated) — it may
   indicate the seeded K-means Lloyd loop needs a better initialization heuristic at low anchor
   counts specifically (e.g. always initialize missing-cluster seeds from the RESIDUAL of removing
   anchor-explained variance, rather than raw k-means++ on the unlabeled pool).
4. Repeat this exact design with LA's REAL leg-1/leg-2 sign inventory shape (gappy, irregular
   row/column counts) instead of the dense synthetic 18×5 grid, to check whether
   ASSUMPTION-E21-1's "optimistic upper bound" framing holds quantitatively, not just directionally.
5. A fourth surface attempt could fold in E018's actual component-channel EMBEDDING (not a
   synthetic stand-in calibrated only to its aggregate MRR) to check whether the real channel's
   higher-order structure (not captured by a scalar MRR target) makes the row/col recovery problem
   easier or harder than this Gaussian-block synthetic surrogate predicts.
6. Formally test whether PC-oracle-ceiling's 0.009 shortfall is a stable feature of this exact
   `n_init`/`n_iter` configuration or would clear 0.9 with a larger `n_init` (currently 8) — a small,
   cheap follow-up that does not require redesigning the geometry.
7. Report the ROW-axis-only and COL-axis-only surfaces separately as primary outputs going forward
   (rather than only the averaged `ARI_combined`) — the row/col asymmetry in this epoch's own
   results (e.g. oracle b=12: row=0.78 vs col=1.00) shows the two axes have genuinely different
   recoverability profiles that a combined scalar partially obscures.
