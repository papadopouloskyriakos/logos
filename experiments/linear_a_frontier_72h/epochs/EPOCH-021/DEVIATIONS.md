# EPOCH-021 deviations (Art. XVII, append-only)

No deviation from the frozen `prereg.md` occurred during execution of the FINAL grid
(`scripts/epoch021_component_power_surface_v2.py`, plan_hash
`397633786d941f96f96d769ea6781c6a7a3a09d85ec4e81fe28b17f9fffa66a6`) — the script implements exactly
the one design specified in the prereg (asymmetric block amplitude A_ROW=1.3/A_COL=1.0 at b=0
plain KMeans; smoothed-Fisher-weighted seeded K-means at b>0), run once at R=30 per cell, and the
mechanical verdict (`HARNESS_NOT_VALIDATED`) was computed directly from that one run with no
post-hoc adjustment.

For completeness (already disclosed in `prereg.md` §Search receipt, repeated here per Art. XVII's
append-only spirit): reaching this final frozen design required a documented pre-freeze diagnostic
phase, run entirely on synthetic data never touching LA's real q=0.247 cell:

1. Direct diagnosis of E019's exact failure mechanism: confirmed via
   `sklearn.cluster.KMeans(n_clusters=18)` on the noiseless symmetric-amplitude code reaching
   inertia 72.0 (matching the true row-partition's own inertia, verified by seeding K-means with
   the true labels as a fixed point) via a DIFFERENT, non-row-respecting partition — an exact tie
   in the objective, not a local-optimum/initialization failure (n_init up to 50 tried, same
   outcome).
2. Swept `A_ROW ∈ {1.0, 1.1, 1.2, ..., 5.0}` (col fixed at 1.0) on oracle (noiseless) data only;
   found `A_ROW ≥ 1.1` already sufficient to break the tie and reach ARI=1.0 on BOTH axes
   simultaneously via plain unsupervised KMeans. Chose `A_ROW=1.3` for margin — NOT tuned against
   any LA-relevant statistic.
3. Tried and REJECTED (before freezing) three alternative recovery-method designs for the b>0 case:
   (a) plain per-dimension Fisher weighting from anchors alone — diagnosed to collapse dimensions
   belonging to classes never seen among the anchors to ≈0 weight, permanently erasing those
   classes' recoverability; (b) unsupervised block discovery via K-means clustering of the 23
   dimensions by their pairwise correlation profile — diagnosed to fail because the row-block's
   theoretical internal correlation (−1/17 ≈ −0.059) is too close to the ≈0 between-block baseline
   to reliably separate from noise (only the col-block's stronger −1/4 signal was reliably
   detected); (c) balanced (capacity-constrained, Hungarian-assignment) K-means at b=0 without any
   amplitude asymmetry — diagnosed to still get stuck in local optima matching the ORIGINAL
   symmetric-tie degeneracy (found inertia 78.4 vs the true global minimum 72.0, ARI≈0.08), showing
   the size-balance constraint alone does not substitute for breaking the geometric tie. The final
   frozen design (smoothed Fisher weight, k=5 nearest-neighbour in marginal-variance space,
   combined with the asymmetric-amplitude code) was adopted only after these three were diagnosed
   and rejected.

None of this diagnostic phase touched LA's real operating point, any LA sign, or the LA_measured
q-level's realized cells — it was benchmark/harness design work exactly analogous in kind to
E019's own σ-calibration bisection (a nuisance-parameter fit preceding the frozen sweep), fully
disclosed per Art. VII's search-receipt requirement rather than hidden. The verdict
(`HARNESS_NOT_VALIDATED`) is unchanged by this disclosure — it is the correct, mechanical, fail-
closed output of the ONE frozen design's ONE R=30 run.
