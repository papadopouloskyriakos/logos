# EPOCH-019 — Component-channel value-recovery identifiability surface (§12 third power surface, gate A)

**Frozen:** 2026-07-08, BEFORE any (b,q) cell is realized or any ARI is computed.
**Seed:** 20260708 (SEED). All realization RNG streams derive deterministically from SEED via
`sha256(SEED|key)`-seeded generators (no shared mutable global RNG state).
**Claim layer:** L1 (identifiability geometry) only. NO phonetic value, NO L2+ claim, NO
transfer licence touched (Art. XV: none earned, none claimed). This epoch assigns zero LA
readings; it prices a synthetic capacity surface and locates one already-measured real
statistic (E013/E018's LA component-channel MRR) plus one already-priced real count (the
anchor-lattice campaign's independent distinct-lineage anchor count) on it.

**Articles triggered:** V (claim layer L1 fixed above), VII (search receipt below — exactly
one recovery-method design is specified, frozen before any grid cell runs; no post-hoc method
swap), VIII (effective-n / power — the whole point of the surface is a power/identifiability
characterization, reported as ARI with 95% CI, not a bare point estimate), IX (info budget —
every headline number carries its null/adversarial-floor comparison and CI alongside it), XI/XII
(non-circularity — the ONLY real-world inputs are (a) E013/E018's already-published,
byte-reproduced component-channel MRR 0.24701551940826028 and (b) the anchor-lattice
campaign's already-closed independent-anchor count = 0 [WP-C dependency-collapse + WP-G
counterfactual pricing, `research/linear-a-anchor-lattice` HEAD 28bbd59]; NEITHER encodes any
sign's phonetic value — MRR is a retrieval-quality scalar, the anchor count is a cardinality;
the synthetic grid's row/col ground truth is arbitrary integer bookkeeping, not a language
claim), XV (licence ledger unchanged), XVII (append-only — E013/E018 untouched; the
anchor-lattice campaign's G/C findings are cited, not altered), XVIII (assumption register
entries below), XXII (this header + compliance line in the report).

## Question

E003 priced the **whole-sign anchor-profile** surface (how many distinct-lineage anchors buys
what exact-sign recovery, on a Jaccard/motif whole-sign channel). E018 confirmed the
**component-decomposition cross-script channel carries real structure** (agg MRR 0.2470,
survives a frequency+degree-exact adaptive null, p_deflated 0.003) — but MRR is a FORM-matching
statistic (which gallery item looks most like this query), not a value-CLASS-recovery
statistic (do same-row / same-column signs actually cluster together once you have this
channel). This epoch prices a **third, distinct surface**: treating the component channel as
the feature space, how much (anchor budget × channel quality) buys recovery of the *latent
grid structure* (which signs share a consonant row, which share a vowel column) — and where
does LA's real, already-measured operating point sit on it.

## Design (frozen)

**Ground-truth grid (synthetic, truth known by construction):** `n_c=18` consonant-row
classes × `n_v=5` vowel-column classes = `K=90` sign-values, one per grid cell (dense,
no gaps — an explicit simplification, logged as ASSUMPTION-E19-1 below). Each sign's true
code = concat(one-hot(row, 18), one-hot(col, 5)), a 23-dim binary vector. This is a
stand-in for "the component channel, if it behaved like a syllabary grid" — not a claim about
LA/LB's actual row/column count (see ASSUMPTION-E19-1).

**Channel-quality axis Q** (7 levels, calibrated by bisection to a target retrieval-MRR on the
identical query-vs-gallery matching statistic E009/E013/E018 use — one fresh Gaussian-noise
draw per side, `MRR = mean_i 1/rank_i(true match by ascending Euclidean distance)`):
`Q = [0.15 (sub-LA reference), 0.24701551940826028 (LA's real measured E013/E018 component
channel), 0.30, 0.39934712069259104 (LB real measured within-script self-MRR, E009), 0.55,
0.75, 1.0 (oracle, sigma=0, exact)]`. Calibration: bisection on `sigma`, 30 draws/trial,
tolerance |achieved − target| ≤ 0.004, ≤ 40 iterations; calibration RNG seeded independently of
the sweep RNG and logged.

**Anchor-budget axis B** (5 levels): `B = [0, 2, 4, 8, 12]`. `b=0` is LA's real operating point
(the anchor-lattice campaign's WP-C dependency-collapsed independent distinct-lineage anchor
count for Linear A = 0 today — ASSUMPTION-E19-2 records this citation). `b=12` is the ceiling
tested (order-of-magnitude above the anchor-lattice's own "absolute recovery" requirement of
12×8-slot anchors, used here only as a generous ceiling for the surface, not a re-derivation of
that number).

**Recovery method (frozen, one design, no sweep):**
- `b=0` (no labels available): unsupervised — `KMeans(n_clusters=18)` on the K query-side
  embeddings → row partition; separately `KMeans(n_clusters=5)` → column partition.
  `n_init=10`, seeded.
- `b>0`: `b` sign-ids sampled uniformly without replacement; nearest-centroid classifier —
  centroid per observed row-label among anchors (mean embedding), centroid per observed
  col-label among anchors; every non-anchor sign assigned to its nearest row-centroid and
  nearest col-centroid by Euclidean distance. (Classes with zero anchors are simply
  unreachable — not special-cased.)
- Scoring is **held-out only**: anchors are excluded from the ARI computation.
- Metric: `ARI_row = adjusted_rand_score(true_row, pred_row)` and `ARI_col` likewise on the
  held-out set; `ARI_combined = mean(ARI_row, ARI_col)` is the primary scalar for
  contour-finding. Adjusted Rand Index is label-permutation-invariant (no cluster-to-class
  alignment step needed) and is 0 in expectation under independence — the natural chance floor.
- **R = 30 replicates per (b,q) cell**, independent noise draw + independent anchor sample each
  replicate (deterministic per-replicate seeding).

## Positive control (runs FIRST, gates interpretation of the main sweep)

Four frozen sub-checks, ALL must PASS:
1. **PC-monotonic-b**: at `q = 0.39934712069259104` (LB point) fixed, Spearman ρ(B,
   mean ARI_combined across the 5 budget levels) ≥ 0.8.
2. **PC-monotonic-q**: at `b = 12` fixed, Spearman ρ(Q, mean ARI_combined across the 7 quality
   levels) ≥ 0.8.
3. **PC-oracle-ceiling**: at `(q=1.0, b=12)`, mean ARI_combined ≥ 0.9 (sanity: the recovery
   method itself must be capable of near-total recovery when there is no noise and a generous
   anchor budget — otherwise the surface's zero point is a broken-harness artifact, not an
   information-geometry fact).
4. **PC-LB-point**: at `(q=0.39934712069259104, b=12)`, mean ARI_combined ≥ 0.5 (foothold) —
   "reproduces the LB operating point's recovery within tolerance," operationalized as: LB's
   real measured within-script channel quality, given a generous (non-LA) anchor budget, must
   clear the same foothold bar the LA point is graded against.

`PC_PASS := (1) AND (2) AND (3) AND (4)`. If PC_PASS is false, the epoch's main-sweep numbers
are reported but the verdict is downgraded to `HARNESS_NOT_VALIDATED` (fail-closed) regardless
of what the LA cell shows.

## Adversarial control (wrong-channel / shuffled-identity null)

Runs the **identical** (Q×B×R) grid and recovery pipeline, with one change: per replicate, draw
a uniform random permutation σ of the 90 sign-ids; grading truth and anchor labels both use
`adv_row[i] = true_row[σ(i)]`, `adv_col[i] = true_col[σ(i)]` — i.e., anchors are told (and
scoring uses) a self-consistent but structurally decoupled relabeling, while the embeddings
themselves remain tied to each id's ORIGINAL true code. This tests whether the recovery
pipeline can be fooled into reporting apparent recovery from generic cluster structure alone,
independent of any real correspondence between channel identity and the graded partition.

**Rule:** `max` over every one of the 35 (b,q) cells of mean ARI_combined (adversarial
condition) `< 0.05`. Any cell ≥ 0.05 → adversarial control FAILS → the main-sweep verdict is
downgraded to `SURFACE_CONFOUNDED` (fail-closed), regardless of the LA cell's main-condition
reading.

## Verdict rule (mechanical, applied only if PC_PASS and adversarial PASSES)

LA's real operating point on this surface = `(b=0, q=0.24701551940826028)` — **not** a free
parameter; both coordinates cite already-closed, non-circular external facts (E013/E018;
anchor-lattice WP-C/G). Let `m = mean ARI_combined` at that cell over R=30 replicates, with a
normal-approximation 95% CI (`m ± 1.96·sd/√R`).

- `m < 0.5` → **`LA_COMPONENT_POINT_BELOW_FOOTHOLD`**
- `0.5 ≤ m < 0.9` → **`LA_COMPONENT_POINT_AT_FOOTHOLD`**
- `m ≥ 0.9` → **`LA_COMPONENT_POINT_RECOVERS`**

Report alongside: (i) achieved `m` ± CI at LA's point (row/col/combined separately), (ii) gap
to foothold `max(0, 0.5 − m)`, (iii) gap to absolute `max(0, 0.9 − m)`, (iv) the (b,q) contour
— for every tested q, the smallest tested b (if any) whose mean ARI_combined ≥ 0.5, and
symmetrically for every tested b, the smallest tested q (if any) whose mean ARI_combined ≥ 0.5
— reported over the tested grid only (no interpolation/extrapolation claimed beyond the 35
measured cells).

## Search receipt (Art. VII)

Exactly **one** recovery-method design is specified above and frozen before any cell is run:
KMeans-unsupervised at b=0, nearest-centroid at b>0, ARI as the scoring statistic. No
alternative clustering algorithm (e.g. GMM, spectral, hierarchical), no alternative distance
metric, and no alternative anchor-selection rule are tried or compared; `K_search = 1` — no
multiplicity deflation is applicable to the verdict rule (a deterministic threshold on a single
frozen statistic, not a significance test over a searched family). The channel-quality
calibration (bisection to 7 fixed targets) is a nuisance-parameter fit, not a hypothesis search.

## Assumption register additions (Art. XVIII)

- **ASSUMPTION-E19-1** (grid shape): the synthetic ground truth uses a dense 18×5 grid (K=90,
  no gaps) as a stand-in for "a component channel with syllabary-grid latent structure." This
  is a simplification of the real LA/LB inventory (which has gaps and an irregular row/column
  count); it is not fit to LA's actual sign count and does not encode any real sign's identity.
  Net effect on interpretation: unknown sign, but plausibly makes recovery *easier* than a
  gappy/irregular real grid (a full, evenly-populated grid gives KMeans/centroid recovery the
  best possible geometry) — so this surface should be read as an **optimistic** (upper-bound)
  characterization of recoverability at a given (b,q), not a pessimistic one.
- **ASSUMPTION-E19-2** (LA's anchor count = 0): cites the anchor-lattice campaign's WP-C
  (dependency-collapsed independent distinct-lineage anchors = 0, all value-bearing lineages
  descend from one meta-lineage) and WP-G (absolute recovery threshold priced at 12×8-slot
  anchors, foothold at 2–3×8-slot) as already-closed, non-circular external facts
  (`research/linear-a-anchor-lattice` HEAD 28bbd59, MEMORY.md
  `linear-a-anchor-lattice-campaign.md`). This epoch does not re-derive that count; it is
  treated as a frozen input coordinate.
- **ASSUMPTION-E19-3** (recovery method is not the only possible one): the frozen
  KMeans/nearest-centroid design is a simple, defensible baseline, not a claim that it is the
  BEST possible recovery method at any (b,q) cell. A more sophisticated estimator (as E003's
  successor-1 flagged for its own surface) could occupy a different point on this same axis;
  this epoch prices ONE frozen method, consistent with the "no post-hoc method swap" search
  receipt above.

## Non-circularity statement (Art. XI/XII)

The synthetic grid's row/col identities are arbitrary integers with no linguistic content —
they are the SCORING truth for the synthetic benchmark only. The two real-world numbers that
enter this epoch (E013/E018's MRR, the anchor-lattice's anchor count) are both structural/
calibration scalars already published by prior, independently-verdicted epochs; neither is a
phonetic value, and neither is used as a model INPUT on any LA sign — they only locate a
coordinate on an otherwise fully synthetic surface. No known Linear A/B sign value is read,
assigned, or checked anywhere in this epoch.
