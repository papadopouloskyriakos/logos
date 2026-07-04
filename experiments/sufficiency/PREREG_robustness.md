# PRE-REGISTRATION — Exit-B sufficiency-curve robustness study (NEW, separately deposited)

**Status: FROZEN pre-registration for a NEW experiment.** This does NOT modify the registered
Exit-B sweep; its results ANNOTATE the main curve and never overwrite it. Same discipline as
every logos experiment: freeze → external timestamp (Zenodo, new standalone record) → then run.
**No robustness cell runs before the timestamp commit exists.** The running main sweep is
untouched. Gated by STEP A = branch (a) (STEP_A_RULING.md): the sweep is valid as-is; this study
quantifies two confounds the aggregate curve did not separate.

## Motivation (both attack load-bearing caveats, neither changes the deposited numbers)

1. **Fixed-seed execution variance.** The parallel CSA is non-deterministic run-to-run
   (`__update_state` forks a fresh `mp.Pool` every step; probe RNG runs in forked workers with
   nondeterministic task distribution — INSTRUMENTATION_AUDIT.md; sz21 seed0: 7.58 recorded vs
   8.08 re-run). The deposited `± 0.023` confounds across-seed variance with fixed-seed run-to-run
   variance. This study measures the fixed-seed component the main sweep never isolated.
2. **Step-budget sensitivity.** The deposited curve is 2,000-step and self-described as a *lower
   bound* / *non-definitive at floor* (plateau never fires: 2 chunks < patience 3). This study
   tests whether the "at floor" classification survives adequate convergence.

## Frozen design

### Representative cells (fixed now; the byte-identical pinned config: device=cpu, processes=4,
### chunk=1000, plateau 0.05/3 — the SAME cell code as the main sweep)
- **small:** phoenician-ugaritic sz21
- **mid:** cypriot-greek sz200
- **LA-scale:** linearb-greek sz650 (the primary analog, at the 600–700-word LA locator — the
  cell whose "at floor" verdict is load-bearing)

### Arm 1 — fixed-seed execution variance
Each representative cell, **nominal seed = 0**, repeated **R = 10** independent executions (fresh
process each; the parent seed is fixed, the nondeterminism is intrinsic). Report per cell:
mean, sd, min, max, coefficient of variation of `acc` and `energy`. Pre-committed reading: the
fixed-seed sd is reported as an ADDITIVE component to the deposited seed-spread; if it is a
material fraction of the deposited `± 0.023`, the CURVE_REPORT states the total dispersion is
(seed spread ⊕ fixed-seed run-to-run), never that per-cell values are point estimates.

### Arm 2 — step-budget convergence ladder
Each representative cell (seed 0, **R = 4** to average the nondeterminism per budget), at step
budgets **{2000, 5000, 10000, 20000}** (chunk=1000 throughout, so plateau CAN fire at ≥3 chunks).
Report per (cell, budget): mean acc, mean energy, whether plateau fired, wall_s. Pre-committed
reading — the load-bearing test: **does linb sz650 (LA-scale) rise materially above its
2,000-step floor (0.044) at higher budgets?**
- If it stays at floor through 20k steps (plateau fired) → the "information-insufficient even
  given a cognate" reading is STRENGTHENED (the 2k lower bound was not hiding recoverable signal).
- If it rises materially above floor → the deposited at-floor branch was an under-convergence
  artifact; this is a REPORTABLE correction that annotates (never overwrites) the main curve, and
  the deposited "non-definitive" hedge is vindicated as having been the honest call.

### Pre-committed reporting rule
Both arms reported regardless of outcome. Results go to a NEW file
(`experiments/sufficiency/ROBUSTNESS_REPORT.md`) and ANNOTATE the main CURVE_REPORT; the deposited
`results/csa/` numbers are never edited. "Curve shape and floor classification survive BOTH
analyses" is the headline verdict, stated Yes/No/Partial with the numbers.

### Run protocol
- Master/execution seeds recorded per run; artifacts under `experiments/sufficiency/robustness/`.
- **Contention rule:** runs on the SAME fenced cores as the main sweep, at LOWER priority, and
  ONLY after the main sweep completes (or in idle fence capacity) — it must never delay the
  registered sweep or breach the CPU fence (agentic cores 0-13,15,16 stay protected).
- Compute budget: Arm 1 = 3 cells × 10 = 30 runs; Arm 2 = 3 cells × 4 seeds × 4 budgets = 48 runs
  (the 20k linb sz650 runs are the expensive tail — each ~5× the 2k, hours; run last, harvestable).

## STEP C — the deterministic repair (RECORDED for any FUTURE sufficiency work; NOT applied here)

The registered sweep's non-determinism is NOT fixed retroactively (would break the deposited
curve's comparability and re-open the freeze). For any FUTURE sufficiency experiment, the required
design is: **per-worker RNG via `numpy.random.SeedSequence(master).spawn()` keyed on
`(master, cell_id, step, annealer_id)`** — each forked worker deriving its own independent,
reproducible stream from the spawned SeedSequence — **NOT** module-global `random` inside workers
(the current defect: forked workers share/advance parent state nondeterministically), and **NOT**
merely `processes=1` (the serial CSA path is documented broken — memory `csa-serial-path-broken`,
processes=1 gives garbage). This gives bit-reproducible-per-seed cells while preserving the
16-annealer parallel coupling. It is a design note for a future, separately-registered study.

## Status clause
FROZEN. Binding only after the external-timestamp commit (`PREREG_ROBUSTNESS_TIMESTAMP.md`). No
cell runs before it. This file's freeze commit hash + SHA-256 go to Zenodo as a new standalone
record (citing the sufficiency artifacts), same as every prior logos pre-registration.
