# QUOTA_RESULT — Phase 2 Step 1 (read off by the pre-committed rule, SWEEP_SPEC @ `42618ac`)

**Quota: n_anchors = 8, redundancy cap R = 1.** Honest sentence: **eight vetted anchor words
(lengths matching the real S&M Table 6.3 distribution), covering distinct signs (R=1 cap;
realized coverage ≈ 26 sign-slots over the 49 eligible), make a true positive LOTO-survivable
at the frozen GO band** — LOTO-survival power 0.81 at s=2 and 0.93 at s=3 (band: ≥0.80 at some
s ≤ 3), where survival = clears the frozen bar AND every leave-one-anchor-out variant still
clears (Phase-1 clause (ii) semantics).

- Artifact: `results/phase2_quota_sweep.json` (all 19 cells × 8 strengths × 100 reps,
  n_perm=200, master seed 20260712; machinery valid: s=0 false-fire 0.01, s=13 power 1.00).
- Wall-clock: profile cell 32.6 s → printed projection 0.9 min on 18 workers; actual sweep
  **83.1 s** (tripwire 6 h: nowhere near). **GPU decision (amendment):** kernel breakdown shows
  the permutation-fit loop dominates (0.14 ms per 24×24-SVD Procrustes fit + 20×73 NN;
  embedding load 1.1 s one-time/worker; scoring ~2 ms per 200 draws per scoring). No CUDA
  device exists on this host (torch `+cpu`, no nvidia-smi), so the GPU end-to-end projection is
  NOT MEASURABLE here — and the kernel shape (µs-scale math per op) is launch/transfer-bound on
  any GPU. Decision rule collapsed to CPU-parallel; both "numbers" reported as
  (CPU: 83.1 s measured; GPU: unavailable on host).
- Grid summary (max LOTO-survival power at s ≤ 3): 5 anchors: 0.65–0.78 (**below band at every
  R** — retro-explains Phase 1: five toponyms could not have produced a LOTO-survivable
  positive); **8 anchors: 0.86–0.93 (band met — quota)**; 10: 0.93–0.95; 15+: 0.98–1.00
  (saturated). Redundancy cap R barely moves the curves at fixed n — at these sizes coverage
  breadth, not per-sign leg count, is the binding variable (mean pinning words at the quota
  cell ≈ 3.2 of 8; survival works by having enough INDEPENDENT pinning words that dropping any
  one leaves ≥2 pins).
- Descriptive h-sensitivity at the quota cell (sanctioned, run after read-off): h=15 → 0.94;
  h=25 → 0.75 (a larger mask spends more of the anchor supply on collisions; h=20 stands).
- Infeasible cells skipped a priori per spec: (20,1), (25,1), (30,1), (40,1), (40,2).
- Selftest passed pre-sweep: a two-masked-sign word pins neither (collision); a doubly-covered
  sign survives either leg drop.

**Meaning for Step 2:** the census must supply ≥ 8 quota-eligible anchors (classes 1–3,
non-fringe) whose LA forms cover ≥ ~20 distinct eligible signs between them; per-sign
redundancy beyond 1 leg is a bonus, not a requirement, at this design size.
