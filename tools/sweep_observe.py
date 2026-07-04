#!/usr/bin/env python3
"""sweep_observe.py — STANDALONE, READ-ONLY observer for the CSA sufficiency sweep.

Design contract (Phase A):
  * Imports NOTHING from the sweep's worker modules (resume_sweep / csa_sweep /
    learning_curves / pycsa). Standard library only. Full import-time decoupling:
    running this can never trigger a worker-side import side effect or perturb a cell.
  * Everything is DERIVED from files the sweep already writes on disk, plus read-only
    /proc. It never writes into a running process, never signals, never re-pins.
        - plan (all 168 cells)  : results/csa/csa_full_report.json  (planned sizes/benchmark)
        - done  cells           : runtime/csa_sweep/cells/<id>.json          (checkpoint == state)
        - in-flight cells       : runtime/csa_sweep/cells/<id>.json.claim    (atomic claim)
        - liveness / cumCPU     : /proc/<pid>/{cmdline,stat,status}          (read-only)
        - tripwire metrics      : /proc/pressure/cpu, /proc/meminfo, Cpus_allowed_list

One invocation prints a human table AND writes a structured JSON snapshot under
runtime/csa_sweep/observe/, so a later invocation can diff cumCPU (rising vs flat = hang).

Usage:  python3 tools/sweep_observe.py [--json] [--debug]
Read-only. No arguments mutate anything.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
from datetime import datetime, timezone

HZ = os.sysconf("SC_CLK_TCK")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CELLS_DIR = os.path.join(ROOT, "runtime", "csa_sweep", "cells")
LOGS_DIR = os.path.join(ROOT, "runtime", "csa_sweep", "logs")
PLAN_REPORT = os.path.join(ROOT, "results", "csa", "csa_full_report.json")
SNAP_DIR = os.path.join(ROOT, "runtime", "csa_sweep", "observe")

SEEDS = (0, 1, 2, 3)
CONCURRENCY = 4
# The fence and the protected (agentic) cores — copied constants from run_fenced.sh, NOT imported.
FENCE = {17, 18, 20, 21, 37, 38, 39, 42, 44, 47, 49, 51, 53, 54, 55, 57}
PROTECTED = set(range(0, 14)) | {15, 16}
# Six integrity-resolving cell-points the Exit-B correction (Phase B) waits on.
LOAD_BEARING = [("linearb-greek", 600), ("linearb-greek", 650), ("linearb-greek", 689),
                ("cypriot-greek", 600), ("cypriot-greek", 650), ("cypriot-greek", 693)]
# est_cost fallback fit (copied from resume_sweep.COST_FIT) — used ONLY when a size has no
# observed wall-time yet, to order/estimate. Real ETA prefers OBSERVED per-size medians.
COST_FIT = {"linearb-greek": (0.195, 1.79), "cypriot-greek": (0.378, 1.83),
            "ugaritic-noiseless": (0.475, 1.51), "phoenician-ugaritic": (0.30, 1.7),
            "luvian-hittite": (0.30, 1.7)}
FENCED_UNDERPREDICT = 1.20  # est_cost under-predicts fenced wall ~20% (cypriot sz693 est 16.6h vs ~20h)


def cell_id(bench, size, seed):
    return f"{bench}__sz{size}__seed{seed}"


def utcnow():
    return datetime.now(timezone.utc)


# --------------------------------------------------------------------------- #
# Plan + on-disk state (filesystem is authoritative; process counts are NOT)
# --------------------------------------------------------------------------- #
def load_plan():
    """All 168 planned (benchmark, size) points + seeds, from the deposited report."""
    d = json.load(open(PLAN_REPORT, encoding="utf-8"))
    benches = {}
    for k, b in d["benchmarks"].items():
        benches[k] = sorted({p["size"] for p in b["curve"]})
    return benches


def scan_cells(benches):
    """done/in-flight/pending derived from cells/*.json (state) + *.json.claim (claim)."""
    done, inflight, pending = {}, {}, []
    for bench, sizes in benches.items():
        for size in sizes:
            for seed in SEEDS:
                cid = cell_id(bench, size, seed)
                jpath = os.path.join(CELLS_DIR, cid + ".json")
                cpath = jpath + ".claim"
                key = (bench, size, seed)
                if os.path.isfile(jpath):
                    try:
                        c = json.load(open(jpath, encoding="utf-8"))
                        done[key] = {"acc": c.get("acc"), "found": c.get("found"),
                                     "total": c.get("total"), "wall_s": c.get("wall_s"),
                                     "under_converged": c.get("under_converged"),
                                     "ended_utc": c.get("ended_utc"), "mtime": os.path.getmtime(jpath)}
                    except (OSError, ValueError):
                        done[key] = {"acc": None, "mtime": os.path.getmtime(jpath)}
                elif os.path.isfile(cpath):
                    claim = ""
                    try:
                        claim = open(cpath, encoding="utf-8").read().strip()
                    except OSError:
                        pass
                    inflight[key] = {"claim": claim, "claim_mtime": os.path.getmtime(cpath)}
                else:
                    pending.append(key)
    return done, inflight, pending


# --------------------------------------------------------------------------- #
# /proc: scheduler liveness (argv-exact, self-match-immune) + per-cell cumCPU subtree
# --------------------------------------------------------------------------- #
def read_proc_table():
    """pid -> {ppid, state, proc, cpu_s, argv} for every readable process. Read-only."""
    table = {}
    for pid_s in os.listdir("/proc"):
        if not pid_s.isdigit():
            continue
        pid = int(pid_s)
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as fh:
                argv = fh.read().split(b"\x00")
            argv = [a.decode("utf-8", "replace") for a in argv if a]
            with open(f"/proc/{pid}/stat", encoding="utf-8") as fh:
                stat = fh.read()
        except (OSError, ValueError):
            continue
        rp = stat.rfind(")")
        rest = stat[rp + 2:].split() if rp != -1 else []
        if len(rest) < 37:
            continue
        state = rest[0]
        ppid = int(rest[1])
        utime, stime, cutime, cstime = (int(rest[11]), int(rest[12]), int(rest[13]), int(rest[14]))
        proc = int(rest[36])
        table[pid] = {"ppid": ppid, "state": state, "proc": proc,
                      "cpu_s": (utime + stime + cutime + cstime) / HZ, "argv": argv}
    return table


def is_scheduler(argv):
    # python interpreter, running resume_sweep.py, in --run mode. Excludes the bash event-watcher
    # whose loop body merely CONTAINS the string 'resume_sweep.py --run' (argv[0] would be bash).
    if not argv:
        return False
    if "python" not in os.path.basename(argv[0]).lower():
        return False
    return any(a.endswith("resume_sweep.py") for a in argv) and "--run" in argv


def cell_token(bench, size, seed):
    return f"{bench}:{size}:{seed}"


def subtree_cpu(root_pid, table):
    """Sum (utime+stime+cutime+cstime) over the live subtree of root_pid.
    root's cutime/cstime already accounts for reaped pool workers; live descendants add their own.
    No double count: reaped children are gone from the table; each live pid contributes once."""
    children = {}
    for pid, info in table.items():
        children.setdefault(info["ppid"], []).append(pid)
    total, stack, seen, r_count = 0.0, [root_pid], set(), 0
    while stack:
        pid = stack.pop()
        if pid in seen or pid not in table:
            continue
        seen.add(pid)
        total += table[pid]["cpu_s"]
        if table[pid]["state"] == "R":
            r_count += 1
        stack.extend(children.get(pid, []))
    return total, r_count


def proc_health(table, inflight):
    sched = [pid for pid, i in table.items() if is_scheduler(i["argv"])]
    scheduler_alive = len(sched) >= 1
    scheduler_pid = sched[0] if sched else None
    # per in-flight cell: find its --cell parent (ppid == scheduler) and sum its subtree CPU
    percell = {}
    for (bench, size, seed) in inflight:
        tok = cell_token(bench, size, seed)
        roots = [pid for pid, i in table.items()
                 if any(a == tok for a in i["argv"]) and "--cell" in i["argv"]
                 and (scheduler_pid is None or i["ppid"] == scheduler_pid)]
        if not roots:  # fallback: any pid with the token whose parent lacks the token
            roots = [pid for pid, i in table.items() if any(a == tok for a in i["argv"])]
        cpu, rc, pinning = 0.0, 0, None
        for r in roots:
            c, rr = subtree_cpu(r, table)
            cpu += c
            rc += rr
        if roots:
            pinning = cpus_allowed_list(roots[0])
        percell[(bench, size, seed)] = {"cum_cpu_s": cpu, "r_in_subtree": rc,
                                        "roots": roots, "affinity": pinning}
    # protected-runq: R-state tasks currently scheduled on a protected core
    prunq = sum(1 for i in table.values() if i["state"] == "R" and i["proc"] in PROTECTED)
    return scheduler_alive, scheduler_pid, percell, prunq


def cpus_allowed_list(pid):
    try:
        for line in open(f"/proc/{pid}/status", encoding="utf-8"):
            if line.startswith("Cpus_allowed_list:"):
                return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return None


def parse_cpuset(spec):
    out = set()
    if not spec:
        return out
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-")
            out.update(range(int(a), int(b) + 1))
        elif part.strip():
            out.add(int(part))
    return out


# --------------------------------------------------------------------------- #
# Tripwire metric sources (the SAME ones the heartbeat reads)
# --------------------------------------------------------------------------- #
def read_pressure():
    try:
        for line in open("/proc/pressure/cpu", encoding="utf-8"):
            if line.startswith("some"):
                m = dict(re.findall(r"(avg\d+)=([\d.]+)", line))
                return {k: float(v) for k, v in m.items()}
    except OSError:
        pass
    return {}


def read_swap_mb():
    tot = free = 0
    try:
        for line in open("/proc/meminfo", encoding="utf-8"):
            if line.startswith("SwapTotal:"):
                tot = int(line.split()[1]) // 1024
            elif line.startswith("SwapFree:"):
                free = int(line.split()[1]) // 1024
    except OSError:
        pass
    return tot - free


def fenced_relaunch_time():
    """UTC of the fenced relaunch, parsed from logs/CURRENT_LOG -> fenced_<ts>Z.log filename."""
    try:
        p = open(os.path.join(LOGS_DIR, "CURRENT_LOG"), encoding="utf-8").read().strip()
        m = re.search(r"fenced_(\d{8}T\d{6})Z", p)
        if m:
            return datetime.strptime(m.group(1), "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)
    except OSError:
        pass
    return None


# --------------------------------------------------------------------------- #
# ETA — calibrated from OBSERVED per-(benchmark,size) wall-times; power-law fill for unrun sizes
# --------------------------------------------------------------------------- #
def observed_wall(done):
    import statistics
    obs = {}
    agg = {}
    for (bench, size, seed), c in done.items():
        if c.get("wall_s"):
            agg.setdefault((bench, size), []).append(c["wall_s"])
    for k, v in agg.items():
        obs[k] = statistics.median(v)
    return obs


def benchfit(obs, bench):
    """log-log least-squares wall_s ~ a*size^b from this benchmark's observed points."""
    import math
    pts = [(sz, w) for (b, sz), w in obs.items() if b == bench and w and sz > 0]
    if len(pts) >= 2:
        xs = [math.log(s) for s, _ in pts]
        ys = [math.log(w) for _, w in pts]
        n = len(xs)
        mx, my = sum(xs) / n, sum(ys) / n
        den = sum((x - mx) ** 2 for x in xs)
        if den > 0:
            b_exp = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den
            a = math.exp(my - b_exp * mx)
            return ("obs-fit", a, b_exp)
    a, b_exp = COST_FIT.get(bench, (0.3, 1.7))
    return ("cost-fit*1.2", a * FENCED_UNDERPREDICT, b_exp)


def predict_wall(obs, fits, bench, size):
    if (bench, size) in obs:
        return obs[(bench, size)], "observed"
    src, a, b = fits[bench]
    return a * (size ** b), src


def eta(benches, done, inflight, pending, obs):
    fits = {b: benchfit(obs, b) for b in benches}
    # remaining work items = pending + in-flight (in-flight counted at full predicted wall as a
    # conservative upper bound; we don't subtract elapsed to avoid over-optimism)
    remaining = list(pending) + list(inflight.keys())
    # biggest-first order (predicted wall desc) — same ordering discipline as the scheduler
    order = sorted(remaining, key=lambda k: -predict_wall(obs, fits, k[0], k[1])[0])
    cum = 0.0
    lb_done_at = {}
    lb_left = {lb: [s for s in SEEDS if (lb[0], lb[1], s) not in done] for lb in LOAD_BEARING}
    for k in order:
        cum += predict_wall(obs, fits, k[0], k[1])[0]
        lb = (k[0], k[1])
        if lb in lb_left and k[2] in lb_left[lb]:
            lb_done_at[k] = cum  # cumulative work-seconds when this seed finishes
    total_work = cum
    wall_full = total_work / CONCURRENCY
    # load-bearing: the LAST of the six points to finish (all seeds) sets the Phase-B gate ETA
    lb_finish = max(lb_done_at.values(), default=0.0) / CONCURRENCY if lb_done_at else 0.0
    return {"fits": {b: {"src": f[0], "a": round(f[1], 4), "b": round(f[2], 3)} for b, f in fits.items()},
            "hours_to_load_bearing_done": round(lb_finish / 3600, 1),
            "hours_to_full_168": round(wall_full / 3600, 1),
            "days_to_full_168": round(wall_full / 86400, 2)}


# --------------------------------------------------------------------------- #
# Snapshot assembly + rendering
# --------------------------------------------------------------------------- #
def prior_snapshot():
    snaps = sorted(glob.glob(os.path.join(SNAP_DIR, "snapshot-*.json")))
    if snaps:
        try:
            return json.load(open(snaps[-1], encoding="utf-8"))
        except (OSError, ValueError):
            return None
    return None


def build_snapshot():
    now = utcnow()
    benches = load_plan()
    total = sum(len(s) for s in benches.values()) * len(SEEDS)
    done, inflight, pending = scan_cells(benches)
    table = read_proc_table()
    sched_alive, sched_pid, percell, prunq = proc_health(table, inflight)
    obs = observed_wall(done)
    relaunch = fenced_relaunch_time()
    elapsed_h = round((now - relaunch).total_seconds() / 3600, 2) if relaunch else None

    prev = prior_snapshot()
    prev_cpu = {}
    if prev:
        for c in prev.get("in_flight", []):
            prev_cpu[tuple(c["cell"])] = c["cum_cpu_s"]
    prev_ts = prev.get("ts") if prev else None

    inflight_rows = []
    for k, meta in sorted(inflight.items()):
        cpu = percell.get(k, {}).get("cum_cpu_s", 0.0)
        delta = None
        if tuple(k) in prev_cpu:
            delta = round(cpu - prev_cpu[tuple(k)], 1)
        inflight_rows.append({"cell": list(k), "cum_cpu_s": round(cpu, 1),
                              "cum_cpu_h": round(cpu / 3600, 2),
                              "cpu_delta_s_since_prev": delta,
                              "r_in_subtree": percell.get(k, {}).get("r_in_subtree", 0),
                              "affinity": percell.get(k, {}).get("affinity")})

    # load-bearing tracker
    lb_rows = []
    for (bench, size) in LOAD_BEARING:
        seeds_done = {s: done[(bench, size, s)]["acc"] for s in SEEDS if (bench, size, s) in done}
        seeds_inflight = [s for s in SEEDS if (bench, size, s) in inflight]
        lb_rows.append({"benchmark": bench, "size": size,
                        "done": len(seeds_done), "inflight": len(seeds_inflight),
                        "acc_by_seed": {str(s): round(v, 5) for s, v in seeds_done.items() if v is not None}})
    lb_all_done = all(r["done"] == len(SEEDS) for r in lb_rows)

    # fence health
    worker_aff = next((r["affinity"] for r in inflight_rows if r["affinity"]), None)
    fence_intact = parse_cpuset(worker_aff) == FENCE if worker_aff else None
    press = read_pressure()
    swap_mb = read_swap_mb()
    stall60 = press.get("avg60")
    trip = "red" if (swap_mb and swap_mb > 0) or (stall60 and stall60 > 25) or prunq > 16 else \
           ("amber" if (stall60 and stall60 > 10) or prunq > 8 else "green")

    et = eta(benches, done, inflight, pending, obs)

    # recent completions (last 8 by mtime)
    recents = sorted(((c.get("mtime", 0), k) for k, c in done.items()), reverse=True)[:8]
    recent_rows = [{"cell": list(k), "ended_utc": done[k].get("ended_utc"),
                    "acc": round(done[k]["acc"], 5) if done[k].get("acc") is not None else None}
                   for _, k in recents]

    snap = {
        "ts": now.isoformat(), "prev_ts": prev_ts,
        "progress": {"done": len(done), "inflight": len(inflight), "pending": len(pending),
                     "total": total, "pct": round(100 * len(done) / total, 1)},
        "elapsed_h_since_fenced_relaunch": elapsed_h,
        "fenced_relaunch_utc": relaunch.isoformat() if relaunch else None,
        "scheduler": {"alive": sched_alive, "pid": sched_pid,
                      "liveness_method": "argv-exact /proc scan (python+resume_sweep.py+--run); "
                                         "self-match-immune (excludes bash watcher)"},
        "load_bearing": {"points": lb_rows, "all_six_done": lb_all_done,
                         "phase_b_gate": "OPEN" if (len(done) == total and lb_all_done) else "CLOSED"},
        "in_flight": inflight_rows,
        "fence": {"expected": sorted(FENCE), "worker_affinity": worker_aff, "intact": fence_intact,
                  "cpu_stall_some_avg60": stall60, "cpu_pressure": press,
                  "protected_runq": prunq, "protected_runq_cap": 16,
                  "swap_used_mb": swap_mb, "tripwire": trip,
                  "memorymax": "N/A (taskset fallback fence; cgroup undelegated — no systemd MemoryMax)"},
        "eta": et,
        "recent_completions": recent_rows,
        "state_sources": {"plan": "results/csa/csa_full_report.json (planned sizes)",
                          "done": "runtime/csa_sweep/cells/*.json", "inflight": "cells/*.json.claim",
                          "health": "/proc (read-only)"},
    }
    return snap


def render(snap):
    p = snap["progress"]
    L = []
    L.append("┌─ CSA sweep observer — %s ─────────────" % snap["ts"][:19])
    L.append("│ LOAD-BEARING (Exit-B Phase-B gate: %s)" % snap["load_bearing"]["phase_b_gate"])
    for r in snap["load_bearing"]["points"]:
        accs = " ".join(f"s{s}={a}" for s, a in r["acc_by_seed"].items()) or "—"
        L.append("│   %-15s sz%-4d  %d/4 done  %d in-flight   %s"
                 % (r["benchmark"], r["size"], r["done"], r["inflight"], accs))
    L.append("│ progress  : %d/%d cells (%.1f%%)  in-flight %d  pending %d"
             % (p["done"], p["total"], p["pct"], p["inflight"], p["pending"]))
    L.append("│ elapsed   : %sh since fenced relaunch (%s)"
             % (snap["elapsed_h_since_fenced_relaunch"], snap["fenced_relaunch_utc"]))
    sc = snap["scheduler"]
    L.append("│ scheduler : %s (pid %s)" % ("ALIVE" if sc["alive"] else "DOWN", sc["pid"]))
    f = snap["fence"]
    L.append("│ fence     : %s   stall(avg60)=%s%%  protected-runq %d/%d  swap %dMB  tripwire=%s"
             % ("INTACT" if f["intact"] else ("?" if f["intact"] is None else "BREACH"),
                f["cpu_stall_some_avg60"], f["protected_runq"], f["protected_runq_cap"],
                f["swap_used_mb"], f["tripwire"].upper()))
    L.append("│ in-flight cumCPU (rising=alive, flat=hang):")
    for r in snap["in_flight"]:
        d = r["cpu_delta_s_since_prev"]
        dtxt = "baseline" if d is None else ("+%.0fs %s" % (d, "RISING" if d > 0 else "FLAT⚠"))
        L.append("│   %-15s sz%-4d s%d  %.2fh (%s)  R=%d"
                 % (r["cell"][0], r["cell"][1], r["cell"][2], r["cum_cpu_h"], dtxt, r["r_in_subtree"]))
    e = snap["eta"]
    L.append("│ ETA (obs-calibrated): load-bearing done ~%.1fh | full 168/168 ~%.1fh (~%.2fd)"
             % (e["hours_to_load_bearing_done"], e["hours_to_full_168"], e["days_to_full_168"]))
    L.append("│ recent    : " + ", ".join("%s/sz%d/s%d=%s" % (c["cell"][0][:4], c["cell"][1], c["cell"][2], c["acc"])
                                           for c in snap["recent_completions"][:4]))
    L.append("└────────────────────────────────────────────")
    return "\n".join(L)


def render_digest(snap):
    """Compact load-bearing + ETA block for the Monitor cadence (one grouped notification)."""
    p, lb, e, f = snap["progress"], snap["load_bearing"], snap["eta"], snap["fence"]
    L = ["── observe %s | %d/%d (%.1f%%) | Phase-B gate %s | elapsed %sh"
         % (snap["ts"][:19], p["done"], p["total"], p["pct"], lb["phase_b_gate"],
            snap["elapsed_h_since_fenced_relaunch"]),
         "   ETA: load-bearing done ~%.1fh | full 168/168 ~%.2fd | fence %s | tripwire %s | sched %s"
         % (e["hours_to_load_bearing_done"], e["days_to_full_168"],
            "INTACT" if f["intact"] else ("?" if f["intact"] is None else "BREACH"),
            f["tripwire"].upper(), "ALIVE" if snap["scheduler"]["alive"] else "DOWN")]
    for r in lb["points"]:
        accs = " ".join(f"s{s}={a}" for s, a in r["acc_by_seed"].items()) or "pending"
        L.append("   %-15s sz%-4d %d/4 done %din-flight  %s"
                 % (r["benchmark"], r["size"], r["done"], r["inflight"], accs))
    if lb["all_six_done"]:
        L.append("   *** ALL SIX LOAD-BEARING CELLS DONE — Phase-B gate condition met ***")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description="Read-only CSA sweep observer.")
    ap.add_argument("--json", action="store_true", help="print the full JSON snapshot to stdout")
    ap.add_argument("--digest", action="store_true", help="compact load-bearing+ETA block (for Monitor)")
    ap.add_argument("--debug", action="store_true", help="dump raw mtimes, queue order, ETA inputs")
    a = ap.parse_args()

    snap = build_snapshot()
    os.makedirs(SNAP_DIR, exist_ok=True)
    stamp = snap["ts"].replace(":", "").replace("-", "")[:15]
    outp = os.path.join(SNAP_DIR, f"snapshot-{stamp}.json")
    with open(outp, "w", encoding="utf-8") as fh:
        json.dump(snap, fh, indent=2)
    with open(os.path.join(SNAP_DIR, "latest.json"), "w", encoding="utf-8") as fh:
        json.dump(snap, fh, indent=2)

    if a.json:
        print(json.dumps(snap, indent=2))
    elif a.digest:
        print(render_digest(snap))
    else:
        print(render(snap))
        print("\n[snapshot written] %s" % os.path.relpath(outp, ROOT))

    if a.debug:
        print("\n===== DEBUG =====")
        benches = load_plan()
        done, inflight, pending = scan_cells(benches)
        obs = observed_wall(done)
        print("observed per-size wall medians (h):")
        for k in sorted(obs):
            print("   %-20s sz%-4d %.3fh" % (k[0], k[1], obs[k] / 3600))
        print("ETA fits:", json.dumps(snap["eta"]["fits"], indent=2))
        print("in-flight roots + affinity:")
        for r in snap["in_flight"]:
            print("   ", r["cell"], "cumCPU=%.2fh" % r["cum_cpu_h"], "aff=", r["affinity"])
        print("pending count:", len(pending), " done:", len(done), " inflight:", len(inflight))


if __name__ == "__main__":
    main()
