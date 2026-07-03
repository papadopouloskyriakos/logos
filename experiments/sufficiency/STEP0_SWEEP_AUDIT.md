# STEP 0 — sufficiency sweep state audit + lane ETAs (measured, no assumptions)

**Sweep state: INCOMPLETE — 92 / 168 cells.** Not running (no process; last write
2026-07-02 00:44Z, results/csa/). The run halted at 92 cells (the ~88/168 observation of
2026-07-01 21:45Z plus a few more), never resumed.

## §0 — CPU lane measures itself (all numbers from results/csa cell logs)

- **Grid = 42 size-points × 4 seeds = 168.** Done: **23 size-points fully seeded (92 cells)**;
  **19 size-points empty (76 cells remain)**. Report `csa_full_report.json` spans all 42 points
  but 19 carry `n_seeds_done=0`. (Tarball holds 93 files — one straggler beyond the 92 the
  report counts; noted, immaterial.)
- **The remaining 76 are the entire large-size tail** (small-first sort ran the cheap cells):
  linb 400–919, cypriot 400–693, ugaritic 400–2214; phoenician & luvian are fully done.
- **Per-cell wall_s (92 done, processes=4, 2000 steps):** median **738s (12.3min)**, mean 2324s,
  p90 6074s, max **19,778s (5.5h)** = cypriot sz346 seed2. Cost is ~quadratic in size
  (cypriot: sz100=28min → sz200=100min → sz346=298min; per-benchmark fits wall_s≈a·size^1.5–1.8).
- **Remaining-cell cost (power-law extrapolation from each benchmark's own done points):**
  **≈ 524 CPU-hours** (proc=4), dominated by cypriot sz600/650/693 (~13–17h/cell) and ugaritic
  sz2214 (~14h/cell). Full per-cell table in `step0_remaining_extrapolation` (below / results).
- **Convergence:** every cell `under_converged=True` at 2000 steps. This is the SEPARATELY
  REGISTERED lower-bound caveat (CLAUDE.md: "2,000-step = lower bound, at-floor branch
  non-definitive"), NOT part of finishing — the registered protocol reads 2000 steps as a lower
  bound; "finishing" = the remaining 76 cells at the identical 2000-step code.
- **Host:** 20 cores; load ~12 (neo4j + monitoring, mostly <1 core CPU); each CSA cell already
  forks `processes=4` internally. Launcher-level parallelism (multiple driver slices over
  disjoint sizes, resume-safe, cell code byte-identical) → concurrent cells = ⌊free_cores/4⌋.

**CPU ETA (arithmetic shown):** 524 CPU-h ÷ concurrent-cells:
- 3 cells (12 cores, safe on the shared box) = **175h ≈ 7.3 days**
- 4 cells (16 cores) = **131h ≈ 5.5 days**
- 5 cells (20 cores, whole box, starves neo4j) = **105h ≈ 4.4 days**
Pessimistic (p90-weighted tail, cypriot large cells running longer than the fit): +~25% → ~9 days
at 3 cells. No code change, no re-certification (byte-identical to the 92 done cells).

## §1 — GPU capability (source-quoted, corpus/bronze/code/CSA_OptMatcher/)

- **Natively torch/CUDA-capable, no port needed.** `CSA_OptMatcher.py`: `import torch`;
  `-d/--device cpu|cuda`; `self.y = torch.tensor(K…).to(self.device)`; the GPU work is the
  per-lost-word edit distance `editdistance1N(x, self.y, …)`. `run_tamburini.run_one(..., device=)`
  and `csa_sweep.run_cell(..., device=)` already thread `cuda` through.
- **BUT the hot loop is ORCHESTRATION-BOUND** — the coupled annealer (`pycsa.CoupledAnnealer`,
  `n_annealers=16`) runs its coupling via a CPU `multiprocessing` Pool, and per step the edit
  distance is `.to('cpu').numpy()` immediately. The vendored `csa_batched.py` docstring states it
  verbatim: *"The Pool forks CUDA tensors and dies … so the CUDA path is stuck in slow serial: per
  step it fires 16 × N_lost tiny editdistance1N kernels, each dominated by launch + host↔device
  transfer overhead, leaving an H100 ~1% utilised."* Memory `csa-sweep-compute-placement`:
  *"H100 is the wrong tool … batched CUDA built+validated, run on CPU."*
- **A batched CUDA variant EXISTS** (`csa_batched.batch_energy/install_batched`), one kernel/step,
  proven bit-identical to serial energy (max abs diff 0.0). It could saturate a GPU — but the CSA
  orchestration around it (State2Assignment, expandWord, lsa_2g, RNG, annealer coupling) stays on
  CPU each step, so the achievable speedup is Amdahl-capped and must be MEASURED, not assumed.
- **Comparability rule bites both GPU lanes:** device=cpu→cuda (even the mere flag) is not
  bit-identical to the 92 completed CPU cells, and the batched path is a different code path
  again. Either → a **full 168-cell re-run + equivalence re-certification**, never just the 76.

## Decision basis: TOTAL time-to-finished-curve (port + recert + reruns included)

`experiments/sufficiency/ankh_gpu_benchmark.py` is provided so the human can MEASURE the one
unknown (GPU/CPU per-cell ratio) on ankh in ~10-20 min before any GPU lane is priced as real.
