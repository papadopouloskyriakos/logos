# Sufficiency sweep — resume progress log

## 2026-07-03 ~22:32Z — §1 RESUMED on claude01 (biggest-first, whole box)
- 92/168 cells done (restored from csa_cells_2026-07-02.tgz into runtime/csa_sweep/cells/).
- Scheduler `experiments/sufficiency/resume_sweep.py --run --concurrency 5` launched detached
  (PID 810418, log runtime/csa_sweep/logs/CURRENT_LOG). Byte-identical cell code
  (csa_sweep.run_cell), params PINNED to the 92 done cells (device=cpu, processes=4, steps=2000,
  chunk=1000, plateau 0.05/3). Biggest-first: first wave = cypriot sz693 ×4 + ugaritic sz2214 —
  all confirmed in "PARALLEL ANNEALING".
- **Makespan projection (measured power-law fit): ~106h ≈ 4.4 days at concurrency 5** (largest
  single cell cypriot sz693 ≈ 16.6h sets the floor). Pessimistic under shared-box contention:
  up to ~9 days. Remaining: 76 cells / ~532 core-cell-h.
- gpu01 lane: probe + equivalence gate pending (§2); GPU benchmark pending (§3). claude01 does
  NOT wait for them.
