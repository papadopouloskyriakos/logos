# Dispatch-halt preflight — three durability/functional preconditions (READ-ONLY, nothing executed)

**Date:** 2026-07-05. Verifies that `kill -TERM 836963` is **durable**, **functionally child-safe**,
and **leaves no stale lock**. Nothing executed. Complements ACCELERATION_HALT_VERIFICATION.md.

## Bottom line: **ALL THREE preconditions satisfied → Stage 1 (PID-targeted SIGTERM) is safe.**
One operational note (not a blocker): the instant-watcher will alarm "SCHEDULER DOWN" during the
halt window — pause it as part of Stage 1 or accept the recurring notices.

## CHECK 1 — no auto-restart. **Halt is durable.**
- **systemd:** `/proc/836963/cgroup` = `0::/user.slice/user-0.slice/session-1147712.scope` — a
  **logind session `.scope`, not a `.service`**; scopes carry **no `Restart=`** policy. Scheduler
  **PPID = 1** (detached from the session's shell). No unit restarts it.
- **cron:** no user/system/`cron.d` entry references `resume_sweep`/`csa`/`sweep`.
- **supervisord / monit / runit / s6 / daemontools:** none running (the only long-lived helper is an
  unrelated `kubectl port-forward` to Prometheus).
- **agentic/shell watcher:** the instant-watcher (`buo9t6rag`) **only echoes** `⚠ EVENT: SCHEDULER
  DOWN` — verified it contains **no** `exec`/`Popen`/`run_fenced`/`nohup`/`setsid`/relaunch; its
  single `--run` token is the `pgrep -f "resume_sweep.py --run"` **liveness pattern**, not a launch.
  The home-lab agentic system does not manage the CSA sweep.
- **Verdict: no auto-restart mechanism — the halt is durable.**
- **Operational note:** after the SIGTERM, `buo9t6rag` will fire "SCHEDULER DOWN" every 120 s until
  `--run` is relaunched. Stage 1 should `TaskStop buo9t6rag` (or tolerate the alarms); re-arm it
  after resume. Not a precondition failure.

## CHECK 2 — child stdout/stderr topology. **SAFE (regular file, not a pipe).**
The scheduler's child launch (`resume_sweep.py:121`) is
`subprocess.Popen([sys.executable, __file__, "--cell", …, "--out-dir", …, "--host", …])` — **no
`stdout=`/`stderr=`**, so children **inherit** the scheduler's fds. Those fds are the fenced **log
file**, confirmed per child:
```
cell 2117096  fd/1 → …/logs/fenced_20260703T225841Z.log   fd/2 → …/fenced_20260703T225841Z.log
cell 2117990  fd/1 → …/fenced_20260703T225841Z.log        fd/2 → …/fenced_20260703T225841Z.log
cell 2155832  fd/1 → …/fenced_20260703T225841Z.log        fd/2 → …/fenced_20260703T225841Z.log
cell 2161915  fd/1 → …/fenced_20260703T225841Z.log        fd/2 → …/fenced_20260703T225841Z.log
scheduler 836963  fd/1,2 → same log file   (fd/0 → socket, stdin; children don't read it)
```
Each child holds its own inherited dup of the **regular-file** open description. Killing the
scheduler cannot break these writes: **no pipe reader to close → no SIGPIPE / BrokenPipeError / block**;
a file fd stays valid regardless of the parent's death. (And the cell RESULT is written to
`<cid>.json` independently of stdout.) **Verdict: SAFE — functionally child-safe.**

## CHECK 3 — no parent-level lock. **`--run` restarts clean.**
- `/proc/836963/fd`: only the log file + a stdin socket — **no lock/pid/flock fd**.
- Code: `resume_sweep.py` / `run_fenced.sh` have **no `flock`/`lockf`/pidfile/lockfile/singleton**
  logic. The **only** exclusion mechanism is the **per-cell** `O_EXCL` `.claim` in `run_one_cell`
  (`l.83`), which is child-level and self-cleaned on completion — not a parent lock.
- An abrupt SIGTERM to the scheduler leaves **no parent-level stale state**; `--run` on restart just
  recomputes `pending_cells` from disk. **Verdict: no stale-lock risk — Stage-3 resume is clean.**

## Verdict
| precondition | result |
|---|---|
| 1. durable halt (no auto-restart) | **PASS** (operational: pause `buo9t6rag`) |
| 2. functionally child-safe (fd topology) | **PASS** (children write to a regular log file) |
| 3. no stale parent-level lock | **PASS** (only per-cell `.claim`, no parent lock) |

**All three satisfied → `kill -TERM 836963` is durable AND functionally child-safe AND leaves no
stale lock. Stage 1 authorized — but still not executed; awaiting explicit go-ahead.** Recommended
Stage-1 addendum: `TaskStop buo9t6rag` first (silence the expected SCHEDULER-DOWN alarms), then the
PID-targeted SIGTERM.
