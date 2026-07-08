# EPOCH-019 deviations (Art. XVII, append-only)

1. **Added one declared POSTHOC_CHARACTERIZATION pass (seeded-KMeans recovery) not specified
   in the frozen prereg.** The prereg's frozen recovery method (nearest-centroid on the full
   23-dim embedding at b>0) failed its own preregistered positive control: `pc_monotonic_b`
   FAILED (rho=0.0 at the LB-quality row — mean ARI_combined actually DROPS from b=0 to b=2
   and never recovers to the b=0 unsupervised level within the tested budget range),
   `pc_oracle_ceiling` FAILED (0.4514 < 0.9 required at q=oracle, b=12), `pc_lb_point` FAILED
   (0.1145 < 0.5 at q=LB-quality, b=12). Per the prereg's own fail-closed rule, this correctly
   and mechanically produced verdict `HARNESS_NOT_VALIDATED` — that verdict IS NOT CHANGED by
   this deviation. To make the resulting negative finding useful for successor design (does
   the failure reflect a genuine information ceiling, or a naive-centroid artifact — the
   full-embedding centroid conflates the row-block and col-block, and a class with zero
   anchors is entirely unreachable), a second, still non-circular recovery method (seeded
   KMeans: anchor-label centroids seed as many of k's initial cluster centers as there are
   distinct anchor labels, remainder via k-means++, standard Lloyd iterations to convergence —
   uses ONLY anchor labels as an init hint, never a privileged row/col feature-block split) was
   run over the identical (Q×B×R) grid, scored with the identical ARI rule, and put through the
   identical PC/adversarial gates. This is reported alongside the primary result, clearly
   labeled `POSTHOC_CHARACTERIZATION`, and is diagnostic only — it does not supersede, and is
   not substituted for, EPOCH-019's frozen verdict or LA-point reading.

   **Posthoc outcome:** seeded-KMeans ALSO fails the same PC gate (`pc_monotonic_b` rho=-0.30,
   `pc_oracle_ceiling` 0.466<0.9, `pc_lb_point` 0.238<0.5; `pc_monotonic_q` PASSES, rho=1.0).
   Two structurally different recovery methods (raw nearest-centroid; anchor-seeded KMeans)
   both show the SAME qualitative failure — mean ARI_combined is *highest at b=0* (no anchors)
   and does not monotonically improve with anchor budget, at any tested channel quality,
   including oracle. Per-axis breakdown localizes this to the ROW axis specifically: ARI_row is
   at or below the adversarial floor (~0.00-0.04, occasionally negative) at EVERY (b,q) cell in
   BOTH methods, including q=oracle; ARI_col alone reaches 1.0 at (oracle, b=0) unsupervised
   but is also non-monotonic in b. This converges on a diagnosis that the failure is a
   geometric property of the benchmark's representation (concatenated one-hot blocks with
   equal isotropic noise make "differs in row only" and "differs in col only" pairwise
   distances numerically indistinguishable, see report §Diagnosis), not an artifact of one
   particular recovery algorithm. This diagnosis is itself POSTHOC_CHARACTERIZATION, not a
   verdict.
