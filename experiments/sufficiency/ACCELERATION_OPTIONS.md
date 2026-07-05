# Reaching the six load-bearing cells sooner — verified options (READ-ONLY, nothing executed)

**Date:** 2026-07-05. Read-only inspection + reasoning. **Nothing was executed** — no stop, pause,
reorder, kill, launch, re-pin, provision, or live claim test. The four in-flight `ugaritic sz2214`
cells and the scheduler are exactly as they were. §2 Exit-B hard stop and `paper/` freeze in force.

## PART A — Are the six cells sufficient to unlock the correction? **YES.**

The corrected locator@650 is produced per-benchmark, with **no full-sweep aggregate and no
neighboring-size dependence** beyond cells already complete:

- `_interp(curve, 650, "recovery_mean")` (`learning_curves.py:616`): with a completed point **at**
  650, the bracket `(600,650)` gives `t=(650-600)/(650-600)=1.0 → returns y1` = the **sz650 value
  exactly**; if 650 is the max completed size it hits the `x >= pts[-1]` branch and returns the
  sz650 value too. **The corrected value at 650 comes from sz650 alone** (its 4 seeds). `sz600`/`sz689`
  only shape the curve / the in-range flag; they are not needed for the number.
- `linear_a_locator` (`l.634`) and `csa_sweep.assemble_report` build **each benchmark's curve
  independently**; the `headline` is just the primary (linb) locator. **No ugaritic control, no
  cross-benchmark term, no completion-gated aggregate.** The chance floor + `recovery_is_lower_bound`
  at 650 are also read from sz650's own cell fields.

**Minimal set for the correction = linb `sz650`×4 + cypriot `sz650`×4 (8 cells).** The full six-point
set (linb 600/650/689 + cypriot 600/650/693; cypriot 693 already done) adds curve context and, with
the B2 guard, a correct in-range flag — nice-to-have, not required for the two corrected numbers.
**Acceleration is worthwhile.**

## PART B — Is reprioritization protocol-neutral? **YES.**

- **Cell independence:** `run_cell` (`csa_sweep.py:160`) takes fixed inputs (`downsample(bench, size,
  seed)`), writes one identity-keyed checkpoint `<bench>__sz<size>__seed<seed>.json`, and reads **no
  other cell's state**. Atomic `O_EXCL` `.claim`.
- **Seed = stable cell identity, NOT dispatch order.** `run_tamburini.run_one` does
  `random.seed(seed)` and `np.random.seed(seed)` (`run_tamburini.py:212,215`) with `seed=cell["seed"]`
  (0–3); `downsample`/`chance_floor` likewise keyed on `cell["seed"]`. No dependence on launch order
  or global RNG carried across cells. (Results are still stochastic run-to-run — pycsa forks a fresh
  pool per step — so the registered protocol already treats each cell as a stochastic replicate;
  order-independent either way.)
- **Prereg fixes the CELL SET + pinned params, NOT the order.** `resume_sweep.py` header: *"LAUNCHER/
  SCHEDULER … NOT cell code … This file only changes ORDER (biggest-first)."* Pinned
  (steps=2000, chunk=1000, device=cpu, processes=4, plateau 0.05/3) and cell code are registered;
  scheduling order is not. **Reordering is protocol-neutral.**

## PART C — The candidate paths

| path | feasible? | destructive? | integrity-neutral? | net time saved | verdict |
|---|---|---|---|---|---|
| **1. Clean-boundary pause-reprioritize-resume** | **Yes** | **No** (if in-flight not killed) | **Yes** | **~3–5 days** | **RECOMMENDED** |
| 2. Separate idle hardware | No (no env-matched host) | — | comparability risk | — | not available |
| 3. Same-host parallel | No | oversubscription | — | negative | **RULED OUT** |

**1. Clean-boundary pause-reprioritize-resume.** The scheduler launches cells via
`subprocess.Popen([… --cell …])` and only *polls* them; **the `--cell` child writes its own
checkpoint** (`run_one_cell`), so stopping the `--run` parent **orphans but does not kill** the four
sz2214 workers — they finish and checkpoint on their own. On resume, `pending_cells` and the launch
loop both `continue` on any existing `.json`, so **completed cells auto-skip (idempotent)**. The
reprioritization is: let the sz2214 batch finish (it holds all 16 cores anyway), then run the
load-bearing cells **next** (via `--cell` or a load-bearing-first queue) instead of the biggest-first
`ugaritic sz1660`/`sz1107` giants, then relaunch `--run` for the remainder.
- **Integrity-neutral** per Part B (order not registered; seeds stable; cells independent + idempotent).
- **CAVEAT (hard):** never **kill** an in-flight cell — `run_one_cell` leaves its `.claim` on kill,
  and a stale `.claim` makes the next attempt return `claimed-elsewhere` and **skip the cell forever**.
  The clean path relies on letting in-flight cells *complete* (they remove their own `.claim`). Any
  reprioritization must also not orphan a `.claim` (only launch cells with neither `.json` nor a live `.claim`).
- **Net saving:** it cannot beat the current sz2214 batch (must let it finish, ~1–1.5 d away — see
  Part D), but it **skips the sz1660 + sz1107 ugaritic giants** (each ~3–4× over est) that
  biggest-first would run *before* the load-bearing cells → **~3–5 days sooner** to the corrected data.

**2. Separate idle hardware — not cleanly available.** `nllei01gpu01` was probed earlier: python
3.12 vs 3.11, torch absent (irrelevant for CPU CSA but signals env drift), **no shared filesystem**.
Different interpreter/env risks non-comparable float/RNG semantics and forces artifact copying.
`claude01` is the fenced host (saturated) and its protected cores run the agentic system (off-limits
by standing policy). **No env-matched idle host exists** → would compromise comparability; not
recommended without an identical-env host.

**3. Same-host parallel — RULED OUT.** All **16 fenced cores are saturated** (4 cells × `processes=4`
= up to 16 R-state workers). A parallel launch on the fence = oversubscription → **slows the
in-flight sz2214 cells, net-negative**. The only other cores are the **protected agentic set
(0–13,15,16)**, which the standing host policy forbids for sweep work. No idle capacity.

## PART D — Better ETA (step-level anchor)

**The log has no per-step counter, but `PERFORMING PARALLEL ANNEALING` prints once per chunk**
(`pycsa.py:238`, inside `anneal()`; chunked mode calls it per 1000-step chunk). Evidence in the
current fenced log:
- 4 completed cypriot sz693 → **8** anneal-starts = **2 chunks each** (2000/1000, no early plateau).
- 4 in-flight sz2214 → **1** anneal-start each → **still in CHUNK 1 of 2** after ~26 h wall.

**⇒ sz2214 is only ~half done. True cost ≈ 50–60 h/cell (~3.5–4× the 14.8 h estimate), not 26 h.**
The batch (4 concurrent) should clear in roughly **~25–35 h more** (~1–1.5 days from now). This is a
worse anchor than wall-time alone implied, and it applies to the next giants too (`sz1660`, `sz1107`
will similarly be ~3–4× over).

**Consequence for the two routes:**
- **Biggest-first (wait):** load-bearing cells sit behind sz2214 (~30 h) **+ sz1660×4 + sz1107×4**
  (each ~30–45 h at 4-wide) → **~5–8 days** to the corrected data.
- **Reprioritize after sz2214:** load-bearing cells run next. Wall estimates (with observed overrun):
  linb sz600/650/689 ≈ 8–11 h each; cypriot sz600/650 ≈ 18–20 h each (cypriot 693 done).
  - **Correction-minimal (linb sz650×4 + cypriot sz650×4 = 8 cells):** makespan ≈ **~1.25 days**.
  - **Full six-point set (20 remaining cells):** makespan ≈ **~2.7 days**.
  - → corrected data in **~30 h + 1.25 d ≈ 2.5 d (minimal)** to **~30 h + 2.7 d ≈ 4 d (full set)**.

## Ranked recommendation (NOTHING executed)

1. **Clean-boundary pause-reprioritize-resume** — the only non-destructive, integrity-neutral,
   high-payoff path. After the sz2214 batch clears (~1–1.5 d, unavoidable), run the load-bearing
   cells next instead of the sz1660/1107 giants; resume the full sweep after. **Saves ~3–5 days** to
   the Exit-B correction; the remaining ugaritic curve completes later with no loss. Requires only a
   launcher-order change at a clean cell boundary — no cell code, params, seeds, or completed cells
   touched; never kill an in-flight cell.
2. **Default if declined / no approval:** wait on biggest-first → corrected data ~5–8 days out.
3. Separate host: only if an env-matched idle host is provisioned (none today). Same-host parallel:
   ruled out.

**This is analysis only — I have executed nothing and will not touch the scheduler, cells, or
watchers without your explicit go-ahead.**
