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

## 2026-07-03 ~22:45Z — §0 EVACUATED claude01 (standing policy: ZERO cells on claude01)
- Scheduler + all 5 cell-subprocesses + their mp children SIGTERM→SIGKILL. Survivors: 0.
- claude01 load: BEFORE kill load1=31.5 (5 heavy cells); AFTER kill runnable=9/5257 (back to the
  neo4j+monitoring baseline; load1 average decaying from its tail). Real CPU freed.
- Completed-during-window: **0** (still 92 checkpoints; first completions were ~16h out).
- 5 killed cells (cypriot sz693 ×4 + ugaritic sz2214) re-queue biggest-first on gpu01; stale
  claim files cleared. claude01 is now orchestration/monitoring/rsync/commits ONLY.

## 2026-07-04 ~ (session) — §0–§2 FENCED RELAUNCH on claude01 (16-core cage)
- §0: no sweep process was alive (evac 2 days prior); **92 checkpoints intact, 0 completed in the
  gap** (last cell 2026-07-02 00:37); container now presents 32 CPUs. So §2 = fresh relaunch, no
  live cells to re-pin. gpu01-migration artifacts inert.
- §1 topology reality: the container's assignable cpuset is **32 NON-CONTIGUOUS host cores**
  (`0-13,15-18,20-21,37-39,42,44,47,49,51,53-55,57`), NOT 0-31. The human's "16-31 sweep / 0-15
  agentic" = halving the sorted effective set:
  - **agentic (protected, low 16): 0-13,15,16**
  - **sweep fence (high 16): 17,18,20,21,37,38,39,42,44,47,49,51,53,54,55,57**
- §1 fence PATH: cpuset **not delegated** to uid 1000 (claude-runner) and systemd system-slice
  creation is Access-denied → **sanctioned FALLBACK**: `taskset -c <high-16>` + `nice -n 19` +
  `ionice -c3` on the scheduler (affinity inherited by all children). Launcher:
  `experiments/sufficiency/run_fenced.sh`. Result-neutral (affinity/nice/ionice don't change the
  integer-DP + seeded-RNG computation) → fenced cells stay byte-identical to the 92.
- §1 cage PROVEN: throwaway busy procs + all 52 live python sweep tasks show
  `Cpus_allowed_list = 17-18,20-21,37-39,42,44,47,49,51,53-55,57`; 8× psr sampling → **0 sweep
  procs on protected cores**. (One transient `bash` from the monitoring harness itself is not
  sweep compute and is correctly unfenced.)
- §1 MemoryMax arithmetic: measured per-cell RSS ≈ **1070 MB**; per plan 1070 × 4 cells × 1.5 =
  **~6.4 GB** would-be cap. Container 32 GB total / 26 GB avail; agentic ~6 GB → ~19 GB headroom.
  **Enforcement unavailable at uid 1000** (memory controller not delegated) → tracked as a
  MONITORING threshold (daily high-water), current use ~4.3 GB for 4 cells.
- §2 relaunched biggest-first, **concurrency 4 = the 16 fenced cores** (4 cells × processes=4).
  First wave: cypriot sz693 ×4. Scheduler + all children inside the fence.
- **Makespan (measured fit, 4 lanes): sum ≈ 532 cell-h / 4 ≈ 133 h ≈ 5.5 days** (largest single
  cell 16.6 h is well under, so lanes stay full). Pessimistic (fence contention from the
  unfenced agentic system floating onto the high-16 under nice, + p90 tail): ~7–8 days. The fit
  is from UNFENCED cells, so fenced wall-clock is somewhat longer — 5.5 d is a floor.

## §4 gpu01 benchmark — SKIPPED per the escape clause (reported, not silently dropped)
gpu01 has **no matching torch/CUDA env** (torch absent; only system python 3.12, no pip/uv/3.11),
its **GPU is occupied by resident ollama + Plex** (not idle), and it **reboots daily**. Building a
same-version CUDA torch env + copying corpora exceeds the 20-min window AND cannot yield clean
idle-GPU timings. Per §4 ("if none exists, report and skip — no cross-version benchmarking") the
benchmark is skipped; production stays on the fenced CPUs (as §4 mandates regardless). The CSA GPU
path is already source-documented as orchestration-bound ("H100 ~1% utilised"), so the expected
`<3× → closure` branch is the likely outcome anyway. Say the word to pursue it and I'll set up the
env in a dedicated (non-20-min) pass.

## 2026-07-03 ~23:30Z — GPU lane CLOSED permanently + SMT fence characterization
- **GPU benchmark CLOSED permanently (human directive):** benchmark superseded by structural
  constraints; CSA GPU path documented orchestration-bound at source. Moot for production three
  ways over: gpu01's daily-reboot ceiling makes the big cells (>24 h at pinned processes=4)
  impossible; any GPU lane still prices a full 168-cell re-run + re-certification; and the GPU
  has a day job (ollama + Plex). Do NOT build the gpu01 env. `gpu01_gpu_benchmark.py` stays as a
  committed record, unused.
- **SMT topology → SOFT fence.** 6 of the 16 fence CPUs are hyperthread siblings of PROTECTED
  CPUs: fence 37↔prot 5, 38↔6, 39↔7, 42↔10, 44↔12, 47↔15. On those physical cores the sweep
  shares execution units / L1-L2 / memory ports with the agentic system despite perfect logical
  affinity → cache/port contention can leak across the fence. (2 SMT pairs are wholly inside the
  fence — 17↔49, 21↔53 — harmless.) So we have a **soft (logical-CPU) fence, not a hard
  physical-core fence.** No action taken (fence-width changes are human-gated, and none was
  requested): the agentic-baseline tripwire covers this empirically — if baseline responsiveness
  on 0-13,15,16 degrades, new cell starts pause and I report. A hard fence would require dropping
  the 6 straddling cores (fence → 10 cores / 3 lanes), a throughput cut available on request only.
