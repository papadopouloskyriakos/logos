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

## 2026-07-03 ~22:35Z — §2a gpu01 probe → gate BLOCKED, STOP for instruction
- nllei01gpu01 reachable (key SSH). Specs: **16 cores, 31 GB RAM, RTX 3090 Ti (driver
  570.211.01), 836 GB free /home**.
- **BLOCKERS (per §2a's "must match exactly or STOP"):** (1) **torch NOT installed** on gpu01
  (ModuleNotFoundError) — not a version mismatch, absent; (2) **python 3.12.3 vs claude01's
  3.11** (the 92 cells' interpreter); (3) **no logos repo checked out**; (4) **/home is local
  ext4 — NO shared FS with claude01** (only /volume1 NFS mounts, not the repo path).
- Equivalence gate (§2b) and pooling (§2c) are MOOT until gpu01 has a torch EXACTLY matching
  claude01's `2.12.1+cpu` on a matching interpreter, the repo, and the gitignored benchmark
  corpora. GPU benchmark (§3) additionally needs a CUDA-enabled torch. **gpu01 lane STOPPED for
  human instruction; claude01 continues uninterrupted.**
