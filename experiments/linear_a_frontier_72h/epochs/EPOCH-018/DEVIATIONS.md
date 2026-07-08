# EPOCH-018 deviations (Art. XVII, append-only)

1. **N increased from prereg's stated targets (300 PERMUTE / 250 BOOTSTRAP) to 999 / 500.**
   Reason: the first run at the targeted N (300/250) already showed the observed statistic
   (0.2470) exceeding **every one of the 300 PERMUTE realizations** (null max 0.0948) — the raw
   adaptive p sat at the Monte Carlo floor `1/301 = 0.00332`. After the prereg's frozen ×3
   (K_SEARCH) Bonferroni deflation this floor value becomes `0.00997`, which clears the
   prereg's `alpha=0.01` gate only by a hair — a discretization artifact of N, not a genuine
   borderline effect (parametric check: the observed value is ≈19 empirical-null standard
   deviations above the null mean). Increasing N to 999/500 (both still satisfying the prereg's
   hard floor of "≥200") gives a tighter empirical bound and removes the floor-induced ambiguity
   without touching any frozen threshold, verdict rule, or hypothesis. This is a
   POSTHOC_CHARACTERIZATION precision improvement, not a threshold change; both the N=300/250
   run and the N=999/500 run are reported in `result.json` (`first_pass_floor_note`), and the
   verdict bucket is identical under both (`CHANNEL_SURVIVES_ADAPTIVE_NULL`).
