# EPOCH-006 — PREREGISTRATION (frozen BEFORE any analysis run)

**Campaign:** linear-a-frontier-72h · frontier **F3** (substitution-neighborhood bridges v3)
**Epoch question:** SEED-EFFICIENT ESTIMATORS — can a global-transform method that uses 5 anchors
ONLY to fix a transform/coupling on unsupervised full-graph motif geometry reach the signal that
E003 showed is available (required 5-seed hit rate 0.119 < channel LOO rate 0.149, while M1's
5-anchor profile geometry delivers only 0.039)?
**Branch:** research/linear-a-frontier-72h · **Seed:** 20260708 · **Date frozen:** 2026-07-08
**Substantive gate:** A.
**Articles triggered:** V (claim layers), VII (search receipt), VIII (effective_n + multiplicity),
IX (info budget), XI/XII (non-circularity), XV (transfer licences: nothing here earns a value),
XXII (stage header).
**Claim layer of ANY result here: L2 (relative/structural), calibrated on KNOWN scripts
(LB, Cypriot). No Linear A value claim can emerge from this epoch. No LA data is aligned.**

## Question

E003's open door: at the LA operating point (b=5 seeds, f=0.75), the information needed for a
Holm-surviving recovery exists in the channel (LOO hit rate 0.149 ≥ required 0.119), but M1's
NN-transfer geometry collapses at 5 anchor-profile dimensions (0.039). Test four estimators whose
anchors fix a GLOBAL transform over the full unsupervised similarity graph rather than serving as
the (only) feature coordinates:

- **EST_GW** — landmark-fused entropic Gromov–Wasserstein (anchor penalty fused into the GW cost).
- **EST_SPEC** — landmark orthogonal Procrustes on Laplacian-eigenmap embeddings (k=6).
- **EST_OT** — anchor-regularized entropic OT (Sinkhorn) on the unsupervised structural-signature
  cost (M2 signature), anchor penalty fused.
- **EST_CCA** — ridge linear map (λ=0.1) on the same eigenmap embeddings, fit on anchor rows.

## Non-circular contract (Art. XI/XII)

Identical to E002/E003: all similarity matrices are MF_A trigram-frame cofill-Jaccard built from
sign IDENTITY + word co-occurrence only; known values are read AFTERWARD to define GT pairs and
GRADE. Alignment operates on opaque per-script sign lists with target order shuffled (seeded).
Anchors enter each estimator ONLY as (source_idx, target_idx) pairs; no value strings reach any
estimator. Nothing here is applied to Linear A (a seed-efficient hit would require its own prereg
+ anchor-integrity gate before any LA application).

## Data / units (frozen; identical to E003, same RNG streams)

- KNOWN pair = LB-cog ↔ Cypriot-cog (`f_bridge_common.load_lb_cog/load_cyp_cog`), full-corpus
  alignable n=47 (MIN_SUP=3 both sides, shared parse_cv value).
- CTRL pair = LB-DĀMOS split-half (seeded), identity GT, full-corpus alignable n=71.
- Corpus subsampling, problem construction, target-order shuffling, seed-subset draws, wrong-seed
  injection and null-permutation streams reuse E003's exact deterministic streams
  (`e003_seed_poverty.rng_for` with identical keys: (pair,"corpus",f,d), (pair,"shuffle",f,d),
  (pair,"seeds",f,d,b,rep), (pair,"null",f,d,b,rep), ("KNOWN","adv_seeds"/"adv_null",1.0,0,b,kw,rep)),
  so every cell is REPLICATE-PAIRED with E003's M1 cells.
- MIN_SUP=3, MIN_HELDOUT=10, N_PERM=1000, R=20 replicates/cell (f<1.0: 5 corpus draws × 4 seed
  draws; f=1.0: 20 seed draws), seed 20260708. Machinery reused read-only:
  `e002_motif_common.py`, `e003_seed_poverty.py`, `f2_cross_script_bridge.py`.

## Estimators (frozen; NO hyperparameter tuning — one fixed setting each)

Anchor penalty matrix L (shared by EST_GW/EST_OT): L=0 everywhere; then for every anchor (i,j):
row i ← 1, column j ← 1; then all anchor cells (i,j) ← 0. Order-independent.

1. **EST_GW**: D=1−S (diag 0) per script; entropic GW (E002's `entropic_gw` recursion: eps=0.01,
   outer=200, inner=40, uniform marginals) with per-outer-iteration fused cost
   `(1−α)·minmax01(gw_cost) + α·L`, α=0.5. Cost out = −coupling.
2. **EST_SPEC**: `F2.eigenmap(S, k)` with k=min(6, n−2) per script; orthogonal Procrustes
   (`F2.procrustes`) fit on anchor rows; cost = Euclidean distance in the aligned space.
   At LOO on the full KNOWN problem this is BY CONSTRUCTION identical to E002's M4 (exact_count 4/47) —
   declared reproduction check, see PC1.
3. **EST_OT**: base cost = `F2.method_M2_signature(Ss,St)` (fully unsupervised full-graph
   signature distance), minmax01-normalized; fused = (1−α)·base + α·L, α=0.5; Sinkhorn
   (eps=0.05, 500 iters, uniform marginals). Cost out = −coupling.
4. **EST_CCA**: same eigenmaps as EST_SPEC; W = (AᵀA + λI)⁻¹AᵀB on anchor rows (λ=0.1);
   cost = ‖Et − Es·W‖ rowwise.

Per replicate (identical to E003): seeds drawn from alignable pairs; prediction for each HELD-OUT
sign = argmin of the estimator's cost row over ALL target columns; endpoint = exact-recovery count
on held-out signs; null = 1,000 seeded permutations of true partners among held-out signs,
one-sided p. Replicate invalid if <10 gradeable held-out signs; cell NO_POWER if >R/2 invalid.

## Cells (frozen; per estimator — 8 cells × 20 reps; 32 cells total)

- **VERDICT CELL**: KNOWN (b=5, f=0.75, k_wrong=0) — E003's LA operating point.
- Seed column at f=1.0: KNOWN b ∈ {3, 5, 7, 10}, k_wrong=0.
- **PC2** (declared secondary power control, non-gating): CTRL (b=5, f=1.0) — M1 achieved
  SURVIVES_HOLM here (acc 0.112, p 0.001); an estimator failing PC2 lacks seed-efficiency even on
  a strong identity signal (reported, does not cap the verdict).
- **ADV**: KNOWN (b=5, k_wrong=1, f=1.0) — 1-wrong-in-5 poisoning.
- **NEG**: KNOWN (b=5, k_wrong=5, f=1.0) — full scramble; per-estimator negative control.

Cell statistics + verdicts identical to E003: **SURVIVES_HOLM** if median perm-p ≤ 0.05/12 =
0.0041667 (inherited E002 Holm-12 per-test bar); **NOMINAL** ≤ 0.05; else **FLOOR**; NO_POWER rule
as above.

## Positive controls (run FIRST, gates)

- **PC0 (harness identity, epoch-gating)**: E003's `positive_control()` must PASS again
  (KNOWN M1-LOO exact 7/47, CTRL 55/71, e002/e003 code paths prediction-identical). Any mismatch →
  DETECTOR_BROKEN, epoch aborts, no verdict.
- **PC1 (estimator expressiveness at b=46, per-estimator gate)**: full KNOWN problem, LOO —
  for each sign i, anchors = the 46 other true pairs, fix the transform, predict i; aggregate
  exact count + 1000-perm p. **PASS iff exact_count ≥ 7 AND p ≤ 0.0041667** (the LOO-level
  recovery M1 demonstrated). Declared expectations: EST_SPEC's PC1 statistic is mechanically
  E002's M4 LOO = 4/47 → predicted FAIL (reproducing 4/47 doubles as a code-path check; any other
  number → implementation bug, investigate before proceeding). For EST_GW/EST_OT the marginal
  constraint at LOO makes elimination push the held-out row toward the single unanchored column,
  so PC1 is a NECESSARY-but-weak gate for coupling estimators (declared; the evidence-bearing
  cells are b ≤ 10 where 37–44 held-out rows compete). PC1 FAIL → that estimator's verdict is
  capped at SEED_EFFICIENT_NOT_ACHIEVED (PC1_FAIL) regardless of its cells (cells still run and
  reported; a Holm-surviving verdict cell under PC1_FAIL is flagged ANOMALY → successor prereg
  required, no claim here).
- **NEG gate (per estimator)**: the NEG cell must be FLOOR; otherwise that estimator is
  ESTIMATOR_DETECTOR_BROKEN and excluded (reported).

## Mechanical verdicts (frozen)

Per estimator (after PC0 pass):
1. NEG ≠ FLOOR → **ESTIMATOR_DETECTOR_BROKEN** (excluded from epoch verdict).
2. PC1 FAIL → **SEED_EFFICIENT_NOT_ACHIEVED (PC1_FAIL)** (+ ANOMALY flag if verdict cell ≥ NOMINAL).
3. VERDICT CELL = SURVIVES_HOLM → **SEED_EFFICIENT_ACHIEVED**.
4. VERDICT CELL = NOMINAL → **SEED_EFFICIENT_PARTIAL_NOMINAL**.
5. else → **SEED_EFFICIENT_NOT_ACHIEVED**.

Epoch verdict: any estimator ACHIEVED → **NEW_SYMMETRY_BREAKING_CHANNEL_CANDIDATE** (KNOWN-script
calibration only; LA application requires a new prereg + anchor-integrity gate); elif any
PARTIAL_NOMINAL → **SEED_EFFICIENCY_PARTIAL_ONLY**; else **SEED_EFFICIENCY_NOT_ACHIEVED**.

Wrong-anchor robustness (per estimator, reported): tiers SURVIVES_HOLM=2/NOMINAL=1/FLOOR=0 on
KNOWN (b=5, f=1.0): **ROBUST** if clean ≥ 1 and ADV tier ≥ clean tier; **FRAGILE** if clean ≥ 1
and ADV tier < clean tier; **UNINFORMATIVE** if clean = 0.

## Multiplicity (Art. VIII)

4 primary tests (one verdict cell per estimator). The inherited per-test bar 0.0041667 is stricter
than Holm-4's entry bar (0.0125), so no additional correction is applied; the bar is frozen.
Everything else (seed columns, PC2, ADV/NEG) is control/descriptive, not claim-bearing.

## Search receipt (Art. VII)

4 estimators × 8 cells × 20 replicates + 4 LOO PC1 runs + PC0. One endpoint (held-out exact
count). Hyperparameters FIXED in this document before any run (α=0.5, eps_GW=0.01, eps_OT=0.05,
k=6, λ=0.1, outer=200, inner=40, sinkhorn_iters=500); no tuning, no alternative kernels,
fractions, budgets, restriction schemes, or endpoints will be tried; any deviation = new
preregistration. Pre-freeze work: a synthetic-data-only mechanics smoke test (random isomorphic
graphs, no corpus data); prior artifacts read: E002/E003 published results.

## Falsifiable prediction (committed)

E003 proved the required information exists at b=5 but M1 cannot express it. Global-transform
estimators inherit the full-graph geometry, whose unsupervised alignment quality on KNOWN is weak
(E002: M3 GW 3/47, M2 1/47, M4 4/47) — anchors must add a lot. Committed: P(≥1 estimator
SEED_EFFICIENT_ACHIEVED) = **0.20**; P(best outcome = PARTIAL_NOMINAL only) = 0.20;
P(all NOT_ACHIEVED) = **0.60**. Conditional: if any estimator achieves it, most likely EST_GW
(fused geometry uses all pairwise structure, not a 5-dim profile). PC1 predictions: EST_SPEC FAIL
(=4/47), EST_GW/EST_OT PASS (elimination-assisted), EST_CCA uncertain (0.5).
