#!/usr/bin/env python3
"""Bounded memory probe: ONE ugaritic sz2214 cell, fenced + capped + watched.
Protections (layered): per-process RLIMIT_DATA 8GB (kernel-enforced malloc ceiling);
2-second watchdog killing the WHOLE process group if MemAvailable < 16GB; RSS-plateau
early stop; 15-min hard cap. Writes PROBE_RESULT.json + a 2s-resolution rss curve."""
import json, os, resource, signal, subprocess, sys, time

ROOT = "/home/claude-runner/gitlab/n8n/logos"
sys.path.insert(0, os.path.join(ROOT, "experiments", "sufficiency"))
import resume_sweep as rs   # tree_rss_mb, shed_tree (tested today)

FENCE = "17,18,20,21,37,38,39,42,44,47,49,51,53,54,55,57"
CELL = "ugaritic-noiseless:2214:1"
CAP_GB = 8                    # per-process RLIMIT_DATA
MEM_FLOOR_MB = 16000          # kill the instant available memory dips below this
HARD_CAP_S = 900
PLATEAU_S = 60                # done when RSS moved <1% over this window (after 120s warmup)
OUT = os.path.join(ROOT, "runtime", "csa_sweep", "probe")

def preexec():
    cap = CAP_GB * (1 << 30)
    resource.setrlimit(resource.RLIMIT_DATA, (cap, cap))
    os.nice(19)

def main():
    base_avail = rs.mem_available_mb()
    curve = []
    p = subprocess.Popen(
        ["taskset", "-c", FENCE, sys.executable,
         os.path.join(ROOT, "experiments", "sufficiency", "resume_sweep.py"),
         "--cell", CELL, "--out-dir", os.path.join(ROOT, "runtime", "csa_sweep"),
         "--host", "nllei01claude01-probe"],
        start_new_session=True, preexec_fn=preexec,
        stdout=open(os.path.join(OUT, "probe_cell.log"), "w"), stderr=subprocess.STDOUT)
    t0 = time.time()
    reason = "hard_cap"
    try:
        while time.time() - t0 < HARD_CAP_S:
            time.sleep(2)
            if p.poll() is not None:
                reason = f"cell_exited_rc={p.returncode}"
                break
            avail = rs.mem_available_mb()
            rss = rs.tree_rss_mb(p.pid)
            curve.append({"t": round(time.time() - t0, 1), "tree_rss_mb": rss,
                          "mem_available_mb": avail})
            if avail < MEM_FLOOR_MB:
                reason = f"MEM_FLOOR breached ({avail}MB < {MEM_FLOOR_MB}MB)"
                break
            if len(curve) >= (120 + PLATEAU_S) // 2:
                w = [c["tree_rss_mb"] for c in curve[-(PLATEAU_S // 2):]]
                if max(w) > 200 and (max(w) - min(w)) / max(w) < 0.01:
                    reason = "rss_plateau"
                    break
    finally:
        rs.shed_tree(p)
        claim = os.path.join(ROOT, "runtime", "csa_sweep", "cells",
                             "ugaritic-noiseless__sz2214__seed1.json.claim")
        try: os.remove(claim)
        except OSError: pass
    peak = max((c["tree_rss_mb"] for c in curve), default=0)
    res = {"cell": CELL, "stop_reason": reason, "duration_s": round(time.time() - t0, 1),
           "baseline_mem_available_mb": base_avail,
           "peak_tree_rss_mb": peak, "final_tree_rss_mb": curve[-1]["tree_rss_mb"] if curve else 0,
           "min_mem_available_mb": min((c["mem_available_mb"] for c in curve), default=base_avail),
           "caps": {"rlimit_data_gb_per_proc": CAP_GB, "mem_floor_mb": MEM_FLOOR_MB,
                     "fence": FENCE, "nice": 19, "hard_cap_s": HARD_CAP_S},
           "n_samples": len(curve), "curve": curve}
    json.dump(res, open(os.path.join(OUT, "PROBE_RESULT.json"), "w"), indent=1)
    print(f"PROBE DONE: {reason} | peak tree RSS {peak}MB | "
          f"min MemAvailable {res['min_mem_available_mb']}MB | {len(curve)} samples")

if __name__ == "__main__":
    main()
