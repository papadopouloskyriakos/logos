# Dispatch-halt verification — can the scheduler be stopped WITHOUT signaling in-flight cells?

**Date:** 2026-07-05. **READ-ONLY. Nothing executed** — no signal, stop, kill, launch, or stop-file.
This confirms the single mechanical fact the reprioritize plan rests on. §2 hard stop + `paper/`
freeze in force.

## Bottom line
**YES — a PID-targeted signal to the scheduler alone is provably child-safe.** The exact method is
`kill -TERM 836963` (the scheduler PID **only**, never the group). **NEVER** send a group signal
(`kill -- -836963`, `pkill -g`, `pkill -f resume_sweep`) — every child shares the scheduler's PGID
and would die, leaving stale `.claim`s.

## 1. Process tree (quoted `ps -o pid,ppid,pgid,sid,tty,stat`)

```
 PID     PPID    PGID    SID     TT  STAT  role
 836963  1       836963  836963  ?   SNsl  scheduler (--run)   ← PID==PGID==SID, PPID 1, no tty
 2117096 836963  836963  836963  ?   SNl   --cell sz2214 s0
 2117990 836963  836963  836963  ?   SNl   --cell sz2214 s1
 2155832 836963  836963  836963  ?   SNl   --cell sz2214 s2
 2161915 836963  836963  836963  ?   SNl   --cell sz2214 s3
 3734277 2117096 836963  836963  ?   RN    worker (1 of 16; child of a --cell parent)
 …       …       836963  836963  ?   RN    (all 16 workers)
```
**Every process — scheduler, 4 `--cell` children, 16 workers — is in PGID 836963 and SID 836963.**

## 2. Do children share the scheduler's process group? **YES. Signal-propagation risk: GROUP=YES, PID=NO.**

The `--cell` children were spawned with a plain `subprocess.Popen([… "--cell" …])` — **no
`start_new_session`, no `preexec_fn`** (grep of `resume_sweep.py` confirms none). So they inherited
the scheduler's PGID/SID rather than getting their own. Therefore:
- **A GROUP-directed signal hits the children** (they share PGID 836963): `kill -- -836963`,
  `kill -836963`, `pkill -g 836963`, and `pkill -f resume_sweep` (the pattern also matches the
  `--cell` argv!) would all terminate the in-flight cells → **stale `.claim` → skipped forever.
  These are the forbidden methods.**
- **A PID-directed signal does NOT reach the children.** `kill(836963, SIG)` is delivered by the
  kernel to that **one** process; it does not propagate to child PIDs or the group. Children survive.

## 3. Launch structure (setsid) and what it implies

`/proc/836963/stat`: `pgrp=836963 session=836963 tty_nr=0`; `ps` TT=`?`, STAT contains `s`
(session leader). So the scheduler was **`setsid`-detached: its own session/PGID, PPID 1 (original
launcher gone), and NO controlling terminal.** Implications:
- **No SIGHUP cascade.** SIGHUP-on-hangup is delivered to a session's foreground group only when a
  **controlling terminal** hangs up. `tty_nr=0` ⇒ no controlling terminal ⇒ killing the session
  leader sends **no** SIGHUP to the children.
- **No parent-death signal.** Plain Popen sets no `PR_SET_PDEATHSIG`, so the children get no signal
  when the scheduler dies — they reparent to init (PPID 1) and continue.

## 4. THE verified safe halt method

**`kill -TERM 836963`** (SIGTERM to the scheduler PID only). Why it is child-safe, each link verified:
- `resume_sweep.py` has **no signal handler and no stop-flag** (grep: no `signal.`, `SIGTERM`,
  `KeyboardInterrupt`, `atexit`, `killpg`, `.kill(`, `.terminate(`). So SIGTERM → Python default →
  the scheduler process terminates **without** running any child-cleanup.
- The scheduler's loop holds the `Popen` objects but **never kills them** on exit (no `finally`/
  `atexit` that does so). Popen does not auto-kill children when the interpreter exits.
- Children are separate PIDs in the same group; the PID-targeted signal doesn't reach them; no
  SIGHUP (no tty); no PDEATHSIG (plain Popen). ⇒ the 4 `--cell` workers **keep running, reparent to
  PPID 1, and self-checkpoint** on completion.
- Losing the scheduler's in-memory queue is harmless — resume recomputes pending from disk.

**Post-halt verification (for whoever executes it):** immediately after the signal, confirm the four
`--cell` PIDs (2117096/2117990/2155832/2161915) are still alive with **PPID now 1** and cumCPU still
rising — proving they were untouched.

*(SIGINT would also be safe — no handler ⇒ KeyboardInterrupt ⇒ no child cleanup — but SIGTERM is the
cleaner default. `TaskStop` is not applicable: the scheduler is a detached PPID-1 process, not a
harness-managed task.)*

**If any of the above had failed** (a signal handler that kills children, PDEATHSIG, a shared
controlling tty, or children in the scheduler's group with only a group-stop available) the honest
answer would be "no child-safe dispatch-halt; fall back to a boundary-triggered hold or wait." None
failed — the PID-targeted SIGTERM is provably safe here.

## 5. Resume path

- **Skip-completed — confirmed (two independent guards):** `pending_cells` (`l.68`)
  `if os.path.isfile(cells_dir/<cid>.json): continue  # already completed -> never re-run`, and the
  scheduler launch loop re-checks (`l.119` `if os.path.isfile(cpath): continue`). So the 4 sz2214 +
  the 8 load-bearing cells, once their `.json` exists, are never re-dispatched.
- **Dispatch order = a hardcoded SORT** (`l.65`):
  `sorted(all_cells(), key=lambda c: (-est_cost(c), c["benchmark"], c["seed"]))` — biggest-first.
  There is no order-input knob on `--run`.
- **Load-bearing-first is feasible WITHOUT touching that sort** via the built-in single-cell mode:
  `--cell BENCH:SZ:SEED` (`l.163-169`: `b,s,sd = a.cell.split(":"); run_one_cell(cell, …)`), which
  runs exactly one cell with the **same pinned params** the scheduler uses. So the resume sequence is:
  (a) let the 4 sz2214 finish; (b) run the 8 load-bearing cells as 8 `--cell` invocations (4 at a
  time, inside the same taskset fence); (c) relaunch `--run`, which skips all completed cells and
  finishes the rest biggest-first. No scheduler code change required.

## 6. `.claim` state + clean-completion signature

The four in-flight cells currently hold **live `.claim` files** (0 `.json` yet):
```
ugaritic-noiseless__sz2214__seed0.json.claim  nllei01claude01-fenced 2026-07-04T20:50:49Z
ugaritic-noiseless__sz2214__seed1.json.claim  nllei01claude01-fenced 2026-07-04T20:52:29Z
ugaritic-noiseless__sz2214__seed2.json.claim  nllei01claude01-fenced 2026-07-04T21:31:04Z
ugaritic-noiseless__sz2214__seed3.json.claim  nllei01claude01-fenced 2026-07-04T21:36:04Z
```
**Clean completion per cell** = `run_one_cell` writes `<cid>.json` then (`finally`) `os.remove(claim)`.
So the go-signal to proceed to the load-bearing cells is: **4 sz2214 `.json` present AND 0 sz2214
`.json.claim` remaining.** If a cell were killed instead, its `.claim` would linger and the next
attempt would return `claimed-elsewhere` and skip it — hence the whole point of not signaling children.

## Verified safe sequence (NOT executed — for approval)
1. `kill -TERM 836963` (scheduler PID only) — halts future dispatch; the 4 sz2214 workers keep running.
2. Wait until `ls …sz2214…*.json | wc -l == 4` **and** no `…sz2214…*.claim` remain (clean boundary).
3. Run the 8 load-bearing cells: `resume_sweep.py --cell linearb-greek:650:{0..3}` and
   `--cell cypriot-greek:650:{0..3}`, 4-concurrent, inside `run_fenced.sh`'s taskset fence.
4. `resume_sweep.py --run` via `run_fenced.sh` — resumes, skipping all completed cells.

**Nothing here has been run. Awaiting explicit go-ahead before any signal or launch.**
