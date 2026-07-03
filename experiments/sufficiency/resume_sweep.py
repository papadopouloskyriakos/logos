#!/usr/bin/env python3
"""resume_sweep.py — LAUNCHER/SCHEDULER for finishing the Exit-B CSA sweep. NOT cell code.

The sweep cell code (`csa_sweep.run_cell` + the vendored CSA_OptMatcher) is imported UNCHANGED and
called with parameters PINNED to the 92 completed cells: device=cpu, processes=4, steps=2000,
chunk=1000, plateau_eps=0.05, plateau_patience=3. This file only changes ORDER (biggest-first) and
adds host-level concurrency + a resume/claim queue + optional sharding for a second host — all
launcher/scheduler level, none of it touches a cell's computation.

Byte-identity: each cell runs in its OWN subprocess (`--cell`), loading the vendored module fresh
with torch's DEFAULT thread settings (exactly as the sequential original), so concurrency changes
throughput, never a cell's result. A cell is skipped if its checkpoint exists; a per-cell O_EXCL
claim file prevents any cell from running twice within a host. Across hosts without a shared FS,
`--shard i/n` gives each host a disjoint cell set.

Modes:
  --plan                 print the pending cells biggest-first + the makespan projection; run nothing
  --run [--concurrency K] scheduler: keep K cell-subprocesses busy, biggest-first, resume/claim-safe
  --cell BENCH:SZ:SEED   worker: run exactly ONE cell (pinned params) and checkpoint it
Shared: --out-dir (default runtime/csa_sweep), --shard i/n, --host NAME.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import socket
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, _ROOT)

from scripts.baselines import csa_sweep, run_tamburini as rt      # noqa: E402  (UNCHANGED cell code)
from scripts.comparison import learning_curves as lc              # noqa: E402

PINNED = dict(steps=2000, chunk=1000, device="cpu", processes=4,
              plateau_eps=0.05, plateau_patience=3)

# per-benchmark cost fit wall_s ~= a * size^b, from the 92 completed cells (Step-0 audit); used
# ONLY to order biggest-first and to project makespan — never touches a cell's computation.
COST_FIT = {"linearb-greek": (0.195, 1.79), "cypriot-greek": (0.378, 1.83),
            "ugaritic-noiseless": (0.475, 1.51), "phoenician-ugaritic": (0.30, 1.7),
            "luvian-hittite": (0.30, 1.7)}


def est_cost(cell) -> float:
    a, b = COST_FIT.get(cell["benchmark"], (0.3, 1.7))
    return a * cell["size"] ** b


def all_cells():
    return csa_sweep.cell_plan(list(lc.KNOWN_ANSWER_BENCHMARKS), [0, 1, 2, 3])


def pending_cells(out_dir, shard=(0, 1)):
    cells_dir = os.path.join(out_dir, "cells")
    i, n = shard
    out = []
    for idx, c in enumerate(sorted(all_cells(), key=lambda c: (-est_cost(c), c["benchmark"], c["seed"]))):
        if idx % n != i:                                    # disjoint shard for a second host
            continue
        if os.path.isfile(os.path.join(cells_dir, csa_sweep._cell_id(c) + ".json")):
            continue                                        # already completed -> never re-run
        out.append(c)
    return out                                              # already biggest-first


def run_one_cell(cell, out_dir, host):
    cells_dir = os.path.join(out_dir, "cells")
    os.makedirs(cells_dir, exist_ok=True)
    cid = csa_sweep._cell_id(cell)
    cp = os.path.join(cells_dir, cid + ".json")
    if os.path.isfile(cp):
        return "skip-exists"
    claim = cp + ".claim"
    try:
        fd = os.open(claim, os.O_CREAT | os.O_EXCL | os.O_WRONLY)   # atomic claim; no double-run
        os.write(fd, f"{host} {datetime.now(timezone.utc).isoformat()}\n".encode())
        os.close(fd)
    except FileExistsError:
        return "claimed-elsewhere"
    module = rt._load_vendor_module()
    start = datetime.now(timezone.utc).isoformat()
    t0 = time.time()
    try:
        with tempfile.TemporaryDirectory() as tmp:
            res = csa_sweep.run_cell(module, cell, tmp_dir=tmp, log=logging.getLogger("cell"),
                                     batched=False, **PINNED)
        res["host"] = host                                  # provenance (extra keys; assemble_report ignores)
        res["started_utc"] = start
        res["ended_utc"] = datetime.now(timezone.utc).isoformat()
        with open(cp, "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=2)
        return f"done acc={res.get('acc')} wall_s={time.time()-t0:.0f}"
    finally:
        try:
            os.remove(claim)
        except OSError:
            pass


def scheduler(out_dir, concurrency, shard, host):
    pend = pending_cells(out_dir, shard)
    print(f"[sched] host={host} shard={shard[0]}/{shard[1]} pending={len(pend)} "
          f"concurrency={concurrency} (biggest-first)", flush=True)
    procs = {}                                              # popen -> cid
    q = list(pend)
    while q or procs:
        while q and len(procs) < concurrency:
            c = q.pop(0)
            cid = csa_sweep._cell_id(c)
            cpath = os.path.join(out_dir, "cells", cid + ".json")
            if os.path.isfile(cpath):
                continue
            p = subprocess.Popen([sys.executable, os.path.abspath(__file__),
                                  "--cell", f"{c['benchmark']}:{c['size']}:{c['seed']}",
                                  "--out-dir", out_dir, "--host", host])
            procs[p] = (cid, time.time())
            print(f"[sched] launch {cid} (~{est_cost(c)/3600:.1f}h) [{len(procs)} running, "
                  f"{len(q)} queued]", flush=True)
        time.sleep(5)
        for p in list(procs):
            if p.poll() is not None:
                cid, t0 = procs.pop(p)
                print(f"[sched] finished {cid} rc={p.returncode} wall={ (time.time()-t0)/3600:.2f}h "
                      f"[{len(procs)} running, {len(q)} queued]", flush=True)
    print(f"[sched] host={host} shard complete.", flush=True)


def makespan_plan(out_dir, shard, concurrency):
    pend = pending_cells(out_dir, shard)
    costs = sorted((est_cost(c) for c in pend), reverse=True)
    total = sum(costs)
    biggest = costs[0] if costs else 0
    makespan = max(biggest, total / max(1, concurrency))    # floor = largest cell; else work/lanes
    print(f"[plan] pending={len(pend)}  total={total/3600:.0f} core-cell-h  "
          f"largest-cell={biggest/3600:.1f}h  concurrency={concurrency}")
    print(f"[plan] biggest-first makespan projection = {makespan/3600:.0f}h = {makespan/86400:.1f} days")
    print("[plan] first 8 (biggest-first):")
    for c in pend[:8]:
        print(f"   {csa_sweep._cell_id(c):40s} ~{est_cost(c)/3600:.1f}h")
    return makespan


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--cell", help="BENCH:SZ:SEED worker mode")
    ap.add_argument("--out-dir", default=os.path.join(_ROOT, "runtime", "csa_sweep"))
    ap.add_argument("--concurrency", type=int, default=5)
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--host", default=socket.gethostname())
    a = ap.parse_args()
    shard = tuple(int(x) for x in a.shard.split("/"))

    if a.cell:
        b, s, sd = a.cell.split(":")
        cfg = lc.KNOWN_ANSWER_BENCHMARKS[b]
        ng = lc.parse_cog(os.path.join(lc._DATA_DIR, cfg["cog"])).n_gold
        cell = dict(benchmark=b, size=int(s), seed=int(sd), n_gold=ng,
                    N=cfg["N"], M=cfg["M"], penf=cfg["penf"])
        print(run_one_cell(cell, a.out_dir, a.host), flush=True)
        return 0
    if a.plan:
        makespan_plan(a.out_dir, shard, a.concurrency)
        return 0
    if a.run:
        scheduler(a.out_dir, a.concurrency, shard, a.host)
        return 0
    ap.error("choose --plan / --run / --cell")


if __name__ == "__main__":
    raise SystemExit(main())
