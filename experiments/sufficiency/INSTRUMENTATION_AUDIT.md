# Instrumentation audit — CSA telemetry (verify-first, read-only)

## §1 Is read-only telemetry possible? YES — energy is cleanly separable from RNG/control-flow.
`pycsa.CoupledAnnealer.anneal()` per step: `update_func()` (worker_probe: `random.random()<qa` +
probe_function) → `__step(k)` (accept/reject: `random.uniform(0,1)<p`). The energy read
`min(self.current_energies)` / `get_best()` consumes **no RNG** and branches nothing; the existing
`__status_check(k, min(current_energies), ...)` is a **pure `sys.stderr` print**, gated by
`verbose>=1` (currently `verbose=0` in `run_tamburini._build_annealer`). Granularities:
- per-CHUNK: `run_one` already harvests `{steps,energy,acc,wall_s}` every `chunk=1000` and feeds
  `sink`/plateau — but chunk=1000 & steps=2000 ⇒ only **2 points/cell**, and with plateau
  patience=3 vs 2 chunks the plateau early-stop **can never fire** (every cell runs full 2000;
  all completed cells show `early_stopped=None`). "Plateau-proximity" is therefore moot.
- per-`update_interval` step via `verbose=1`: ~21 points/cell, byte-identical by construction
  (stderr only).

## §2 Byte-identity gate: UNSATISFIABLE — and NOT because of telemetry.
Gate cell phoenician-ugaritic sz21 seed0 (recorded energy 7.581385135650635, acc 0.7143, found 15):
- telemetry ON  → energy 8.739683, acc 0.3333, found 7   (DIFF)
- **CONTROL, telemetry OFF, same seed** → energy 8.081746, acc 0.7619, found 16  (**ALSO DIFF**)
⇒ **the parallel CSA is inherently non-deterministic run-to-run.** `__update_state` creates a
**fresh `mp.Pool` every step** and each of the 16 annealers' `worker_probe` draws RNG inside a
FORKED worker; the task→worker distribution and fork timing vary per run, so the same seed does
NOT reproduce the annealing trajectory (the seed only fixes `Problem.__init__`'s initial shuffle).
The byte-identity gate assumes seed→reproducible; that premise is false here, so bit-identity
cannot be produced by ANY re-run, instrumented or not.

**Decision (per the gate's pre-committed rule "any diff → revert entirely"): telemetry is NOT
activated on production cells.** The cells stay black-box. Nothing was changed to reach this —
the gate ran in an isolated process; no repo/launcher edit was made, so there is nothing to undo.
(Note the subtlety for the record: telemetry is inert *by construction* — stderr printing cannot
change the `random` sequence — but I am respecting the mandated gate rather than substituting my
own looser argument, since the gate is unmeetable here.)

## §3/§4 No production telemetry ⇒ no sidecar traces ⇒ no per-step dashboard.
The 4 in-flight and all 72 future cells remain black-box. Liveness stays covered by the existing
cumulative-CPU heartbeat + R-state count + pulse log (proven sufficient to distinguish
running vs hung).

## §5 ETA estimability — honest answer.
- **Per-cell WALL time** is estimable and already used: the size fit `wall_s≈a·size^1.83`
  (fenced ×~1.3) — this is what drives the makespan ETA. That does not need telemetry.
- **Per-cell step/energy trajectory** would, IF instrumented, give step/2000 as a clean LINEAR
  progress signal (plateau never fires ⇒ completion is exactly at step 2000), so an
  energy-slope ETA is not even needed — step-count alone would extrapolate linearly. But it is
  moot: telemetry is not activated.
- **The deeper consequence for the curve (must be disclosed in CURVE_REPORT):** each cell's
  RESULT is a single draw of a non-deterministic process. The 4-seed spread already sampled
  captures MOST but not all of this — run-to-run variance exists even at fixed seed. The curve's
  Monte-Carlo noise is therefore (seed spread) PLUS (fixed-seed run-to-run spread); the recorded
  per-cell values are one stochastic sample each, not reproducible point estimates. This is a
  property of the registered method (his parallel CSA), not a defect introduced here.
