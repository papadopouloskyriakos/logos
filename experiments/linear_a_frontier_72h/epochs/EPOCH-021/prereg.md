# EPOCH-021 — Component-channel value-recovery identifiability surface, ATTEMPT 2 (redesigned)

**Frozen:** 2026-07-08, BEFORE any (b,q) cell of the FINAL grid is realized with this design.
**Seed:** 20260708 (SEED). All realization RNG streams derive deterministically from SEED via
`sha256(SEED|key)`-seeded generators (no shared mutable global RNG state) — identical convention
to E019.
**Claim layer:** L1 (identifiability geometry) only. NO phonetic value, NO L2+ claim, NO transfer
licence touched (Art. XV: none earned, none claimed). Zero LA readings assigned; this epoch prices
a synthetic capacity surface and locates one already-measured real statistic (E013/E018's LA
component-channel MRR) plus one already-priced real count (anchor-lattice's independent
distinct-lineage anchor count) on it — same non-circular inputs as E019.

**Relationship to E019:** E019 (attempt 1) returned `HARNESS_NOT_VALIDATED`: its recovery method
(raw-Euclidean KMeans at b=0 / nearest-centroid at b>0) failed its own positive control
(`pc_monotonic_b` rho=0.0, `pc_oracle_ceiling` 0.4514<0.9, `pc_lb_point` 0.1145<0.5) because the
benchmark's row-block and column-block one-hot sub-vectors had IDENTICAL amplitude and additive
noise, making "differs only in row" and "differs only in col" pairwise distances numerically
indistinguishable (both `amplitude·sqrt(2)`) — a genuine geometric tie, confirmed by direct
diagnosis (`sklearn.cluster.KMeans(n_clusters=18)` on the exact noiseless code reaches the true
row-partition's global-minimum inertia of 72.0 but converges to a DIFFERENT, non-row-respecting
partition that reaches the identical inertia, because the grid's symmetric geometry admits multiple
tied global optima). This epoch is a full redesign addressing BOTH stated fix directions from the
epoch brief: (1) distinct per-dimension scale between the row-block and column-block (breaks the
exact tie), AND (2) a recovery method that learns a metric from the anchors alone, generalized to
classes without a direct anchor via an unsupervised (label-free) smoothing step — not a hand-coded
block split.

## Question (unchanged from E019)

Given the component-decomposition cross-script channel (E013/E018, agg MRR 0.2470, survives a
frequency+degree-exact adaptive null, p_deflated 0.003), how much (anchor budget × channel quality)
buys recovery of the *latent grid structure* (which signs share a consonant row, which share a
vowel column) — and where does LA's real, already-measured operating point (zero independent
anchors, per anchor-lattice WP-C) sit on that surface?

## Design (frozen) — what changed vs E019 and why

**Ground-truth grid:** unchanged — `n_c=18` consonant-row classes × `n_v=5` vowel-column classes =
`K=90` sign-values, one per grid cell (ASSUMPTION-E19-1, carried over unchanged: optimistic/
upper-bound simplification, logged again below as ASSUMPTION-E21-1).

**FIX 1 — asymmetric block amplitude (breaks the exact geometric tie).** Each sign's true code is
`concat(A_ROW · one-hot(row, 18), A_COL · one-hot(col, 5))`, a 23-dim vector, with
`A_ROW = 1.3`, `A_COL = 1.0` (frozen constants, chosen by pre-freeze diagnostic calibration —
search receipt below). This is a MODEST asymmetry (30%): direct diagnosis (reported in
`reports/EPOCH021_COMPONENT_POWER_SURFACE_V2.md` §Diagnosis) shows even `A_ROW=1.1` is already
sufficient to make the noiseless (oracle) `KMeans(n_clusters=18)` and `KMeans(n_clusters=5)` recover
the true row- and column-partition EXACTLY (ARI=1.0 both), where the symmetric `A_ROW=A_COL=1.0`
case fails on the row axis specifically (ARI≈0, confirmed reproduction of E019's finding).
`A_ROW=1.3` is used for a safety margin beyond the minimal tie-breaking threshold, not tuned
against the LA operating point (which is untouched by this constant — see non-circularity
statement). **Framing note (honest, not a phonetic claim):** the row axis (18 classes) needs a
larger raw separation than the column axis (5 classes) purely because a finer partition is more
vulnerable to combinatorial ties in a shared Euclidean space at equal amplitude — this is a
class-cardinality compensation, not an encoding of "vowels are phonetically louder than
consonants." The real-world prior that column/vowel identity is operationally established with
LESS evidence is instead reflected in this design by the column axis needing far fewer anchors to
reach full class coverage (12 anchors reach ~100% of 5 col classes vs ~50% of 18 row classes) — see
ASSUMPTION-E21-2.

**FIX 2 — anchor-only learned metric with unseen-class generalization (recovery method, b>0).**
For `b>0`: (a) compute a per-dimension Fisher-like discriminability score from the `b` anchors ONLY
(`between-label variance / within-label variance`, summed over row-labels seen among anchors, for
the row task; same construction for the col task) — a dimension belonging to a class NEVER seen
among the anchors gets a raw score of ≈0 under this construction alone (the E019-successor problem
identified during redesign diagnosis: naive per-dimension anchor weighting collapses unseen classes
to a single point, capping recovery at the anchor-coverage fraction). (b) To avoid that collapse,
each dimension's final weight is SMOOTHED using a k=5 nearest-neighbour average in the space of
that dimension's own UNSUPERVISED (label-free) marginal variance across all 90 query points — i.e.
dimensions statistically similar to well-evidenced ones (in a way that requires no label and no
block-index privilege) inherit similar informativeness, letting classes without a direct anchor
still be discoverable via the learned metric rather than being permanently zero-weighted. (c)
Recovery: seeded weighted K-means — anchors are hard-assigned to their known class and centroids for
missing classes are initialized via k-means++ (in the weighted space) among the unlabeled points;
Lloyd iterations (`n_iter=25`, `n_init=8`, best-of-`n_init` by weighted inertia) update all
non-anchor assignments and every centroid; anchors stay fixed to their true class throughout. This
lets classes without an anchor still be discovered via unsupervised structure IN THE LEARNED METRIC
(not raw Euclidean, and not a hand-specified block split) rather than being permanently unreachable
as in E019's raw nearest-centroid.
For `b=0` (no anchors, nothing to learn a metric from): unchanged from E019 —
`KMeans(n_clusters=18)` / `KMeans(n_clusters=5)` on the raw (FIX-1-asymmetric) embeddings,
`n_init=15`, best-of-`n_init` by inertia. This is where FIX 1 alone must carry the recovery burden;
FIX 2 requires labels and cannot apply.
- Scoring is **held-out only**: anchors are excluded from the ARI computation (unchanged from
  E019).
- Metric: `ARI_row`, `ARI_col`, `ARI_combined = mean(ARI_row, ARI_col)` (unchanged from E019 —
  permutation-invariant, 0 in expectation under independence).
- **R = 30 replicates per (b,q) cell**, independent noise draw + independent anchor sample each
  replicate (deterministic per-replicate seeding via `sha256(SEED|"cell"|q_label|b|main/adv|rep)`).

**Channel-quality axis Q and anchor-budget axis B: UNCHANGED from E019** —
`Q = [0.15, 0.24701551940826028 (LA real E013/E018), 0.30, 0.39934712069259104 (LB real E009),
0.55, 0.75, 1.0 (oracle)]`, calibrated by the IDENTICAL bisection-on-sigma procedure as E019
(target = aggregate query-vs-gallery retrieval MRR on the full 23-dim vector, 30 draws/trial,
tolerance 0.004, ≤40 iterations) — re-run against the NEW asymmetric-amplitude code (so the
calibrated sigmas differ numerically from E019's, since achieving the same aggregate MRR against a
higher-amplitude code requires proportionally more noise). `B = [0, 2, 4, 8, 12]`, unchanged,
`b=0` is LA's real operating point (ASSUMPTION-E21-2/E19-2 citation unchanged).

## Positive control (runs FIRST, gates interpretation of the main sweep) — UNCHANGED bars from E019

Four frozen sub-checks, ALL must PASS (identical thresholds to E019):
1. **PC-monotonic-b**: at `q = LB_within_script` fixed, Spearman ρ(B, mean ARI_combined) ≥ 0.8.
2. **PC-monotonic-q**: at `b = 12` fixed, Spearman ρ(Q, mean ARI_combined) ≥ 0.8.
3. **PC-oracle-ceiling**: at `(q=1.0, b=12)`, mean ARI_combined ≥ 0.9.
4. **PC-LB-point**: at `(q=LB_within_script, b=12)`, mean ARI_combined ≥ 0.5 (foothold).

`PC_PASS := (1) AND (2) AND (3) AND (4)`. If PC_PASS is false, the epoch's main-sweep numbers are
reported but the verdict is downgraded to `HARNESS_NOT_VALIDATED` (fail-closed), exactly as E019's
rule, regardless of what the LA cell shows.

## Adversarial control (wrong-channel / shuffled-identity null) — UNCHANGED design from E019

Identical (Q×B×R) grid and recovery pipeline; per replicate a uniform random permutation σ of the
90 sign-ids relabels the grading truth (`adv_row[i]=true_row[σ(i)]`, `adv_col[i]=true_col[σ(i)]`)
while embeddings stay tied to each id's ORIGINAL true code. **Rule (unchanged):** `max` over every
one of the 35 (b,q) cells of mean ARI_combined (adversarial) `< 0.05`. Failure → `SURFACE_CONFOUNDED`
(fail-closed), regardless of the LA cell's main-condition reading.

## Verdict rule (mechanical, applied only if PC_PASS and adversarial PASSES) — UNCHANGED from E019

LA's real operating point = `(b=0, q=0.24701551940826028)` — not a free parameter (same citation as
E019: E013/E018 MRR; anchor-lattice WP-C anchor count = 0). Let `m = mean ARI_combined` at that cell
over R=30 replicates, 95% CI `m ± 1.96·sd/√R`.
- `m < 0.5` → **`LA_COMPONENT_POINT_BELOW_FOOTHOLD`**
- `0.5 ≤ m < 0.9` → **`LA_COMPONENT_POINT_AT_FOOTHOLD`**
- `m ≥ 0.9` → **`LA_COMPONENT_POINT_RECOVERS`**

Report alongside: (i) achieved `m` ± CI at LA's point (row/col/combined separately), (ii) gap to
foothold, (iii) gap to absolute, (iv) the (b,q) contour (first `b` crossing foothold for every `q`;
first `q` crossing foothold for every `b`; same for the absolute bar) — over the tested grid only.

**If PC_PASS is false:** verdict is `HARNESS_NOT_VALIDATED` (or `SURFACE_CONFOUNDED` if the
adversarial control specifically fails); the LA cell's raw numbers are still reported for the
record but are NOT read as a graduation-eligible finding, and a diagnosis of WHICH sub-check(s)
failed and why (localized to row/col axis, to b=0 vs b>0, etc.) is written into the report and
`DEVIATIONS.md`, distinguishing this attempt's failure mode from E019's if the mode differs.

## Search receipt (Art. VII)

Exactly **one** final recovery-method design is specified above and frozen before the FINAL R=30
grid is realized: `KMeans` (unweighted, asymmetric-amplitude code) at b=0; smoothed-Fisher-weighted
seeded K-means at b>0. **Pre-freeze calibration/diagnostic work (disclosed, not hidden):** reaching
this final design required diagnosing E019's exact failure mode (confirmed: symmetric global-optima
tie, `KMeans` inertia 72.0 achieved by both the true row-partition and a non-row-respecting
partition) and empirically checking, on SYNTHETIC diagnostic data only (never touching LA's q=0.247
cell or any LA-relevant number), that: (a) `A_ROW≥1.1` suffices to break the oracle-level tie for
both axes simultaneously (tested `A_ROW∈{1.0,1.1,1.2,1.3,1.5,1.6,1.8,2.0,3.0,4.0,5.0}` against
oracle-only, symmetric-noise-free data), (b) plain per-dimension anchor-only Fisher weighting
collapses unseen-class dimensions to ≈0 weight (diagnosed directly by inspecting the weight vector),
motivating the k-NN marginal-variance smoothing step, (c) an unsupervised (label-free) DIMENSION-
correlation clustering approach to discover the row/col block split was ALSO tried as an alternative
to (b) and REJECTED before freezing — it failed to reliably separate the true 18-dim/5-dim block
split (the row-block's internal pairwise correlation, −1/17 in theory, is too close to zero to
separate from the 0-correlation between-block baseline; only the col-block's stronger −1/4
correlation was reliably detected) — this negative diagnostic result is why FIX 2 uses the
Fisher-plus-variance-smoothing construction instead, not a discovered-block projection. This
diagnostic/calibration phase is disclosed as harness-DESIGN work (methodologically identical in
kind to E019's own sigma-calibration step, which is also a nuisance-parameter fit run before the
frozen sweep) — it never touched the real LA cell, and the ONE resulting design (this document) is
what is frozen and run exactly once at R=30 for the graduation-eligible numbers reported below.
`K_search = 1` for the verdict rule itself — no multiplicity deflation applies to a deterministic
threshold on a single frozen statistic.

## Assumption register additions (Art. XVIII)

- **ASSUMPTION-E21-1** (grid shape, carried from E19-1 unchanged): dense 18×5 grid, K=90, no gaps;
  optimistic/upper-bound simplification of LA/LB's real gappy inventory.
- **ASSUMPTION-E21-2** (LA's anchor count = 0, carried from E19-2 unchanged): cites
  anchor-lattice WP-C/WP-G (`research/linear-a-anchor-lattice` HEAD 28bbd59) as a frozen input
  coordinate, not re-derived here.
- **ASSUMPTION-E21-3** (block-amplitude asymmetry is a class-cardinality compensation, not a
  phonetic-realism encoding): `A_ROW=1.3 > A_COL=1.0` is chosen ONLY to give the harness a
  non-degenerate geometry (break E019's exact tie) at a modest, defensible margin above the
  empirically-diagnosed minimum (1.1); it is not fit to, or informed by, LA's own component-channel
  statistics (E013/E018's MRR enters ONLY as the pre-existing Q-axis coordinate, unchanged
  construction from E019). Net effect on interpretation: this is a benchmark-DESIGN choice, logged
  so a reader can distinguish "the row axis recovers better/worse because of this constant" from "a
  property of LA's real channel."
- **ASSUMPTION-E21-4** (recovery method is not the only possible one, carried from E19-3): the
  frozen smoothed-Fisher seeded-K-means design is a defensible, non-circular baseline that directly
  targets E019's diagnosed failure mode; it is not a claim of optimality. A more sophisticated
  estimator could occupy a different point on this axis.

## Non-circularity statement (Art. XI/XII) — unchanged guarantee from E019

The synthetic grid's row/col identities are arbitrary integers with no linguistic content. The two
real-world numbers entering this epoch (E013/E018's MRR, the anchor-lattice's anchor count) are
already-published, independently-verdicted structural/calibration scalars; neither is a phonetic
value, neither is a model INPUT on any LA sign. `A_ROW/A_COL` and the Fisher-smoothing k=5 constant
are benchmark-design/nuisance parameters fixed by diagnostic work on SYNTHETIC data only, before
freezing, and are not fit to LA's own numbers. No known Linear A/B sign value is read, assigned, or
checked anywhere in this epoch.
