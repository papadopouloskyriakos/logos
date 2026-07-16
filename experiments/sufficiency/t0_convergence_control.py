# PROVENANCE: this is the exact T0 convergence-control driver that ran as /root/t0_run.py on
# vast.ai instance 44534071 (destroyed 2026-07-16). Verdict CONVERGENCE_ARTIFACT (acc 0.373 @
# 6000 steps). The /root/logos paths below are the INSTANCE paths, preserved as-run; on a fresh
# checkout adjust sys.path + OUT to the repo root. Results: runtime/csa_sweep/T0_convergence/.
# Frozen prereg: docs/revision-queue/csa_sufficiency_sweep_novelty.md (T0 section, plan_hash 4f85b82).

#!/usr/bin/env python3
"""T0 convergence control — linearb-greek FULL, calling run_one DIRECTLY so we capture the
per-1000-step acc TRAJECTORY (run_one computes acc each chunk; run_cell discards it). Same
compute as the sweep cells. plan_hash 4f85b82. Writes traj + heartbeat; touches no sweep cell."""
import os, sys, json, time
sys.path.insert(0, "/root/logos")
import torch  # noqa: F401  (before EditDistanceWild for libc10.so)
from scripts.baselines import run_tamburini as rt

BENCH = "linearb-greek"
SEED = int(os.environ.get("T0_SEED", "0"))
STEPS = int(os.environ.get("T0_STEPS", "6000"))
OUT = "/root/logos/runtime/csa_sweep/T0_convergence"
os.makedirs(OUT, exist_ok=True)
TRAJ = os.path.join(OUT, f"traj_seed{SEED}.jsonl")
HB = os.path.join(OUT, "HEARTBEAT_T0.json")
open(TRAJ, "w").close()

module = rt._load_vendor_module()
state = {"best": None, "stale": 0, "pts": []}


def on_ckpt(last):
    row = {k: last.get(k) for k in ("steps", "acc", "found", "total", "energy", "wall_s")}
    state["pts"].append(row)
    with open(TRAJ, "a") as f:
        f.write(json.dumps(row) + "\n")
    json.dump({"status": "RUNNING", "pid": os.getpid(), "bench": BENCH, "seed": SEED,
               "steps_cap": STEPS, "last": row, "trajectory": state["pts"]},
              open(HB, "w"), indent=2)
    e = float(last.get("energy", 0.0))
    if state["best"] is None or e < state["best"] - 0.05:
        state["best"] = e; state["stale"] = 0; return False
    state["stale"] += 1
    return state["stale"] >= 3          # plateau early-stop (eps=0.05, patience=3), as pinned


json.dump({"status": "STARTING", "pid": os.getpid(), "steps_cap": STEPS}, open(HB, "w"), indent=2)
res = rt.run_one(module, BENCH, SEED, STEPS, 4, checkpoint=1000,
                 sink=lambda s: None, device="cpu", on_checkpoint=on_ckpt, batched=False)
acc = res.get("acc"); early = bool(res.get("early_stopped"))
verdict = ("CONVERGENCE_ARTIFACT" if (acc is not None and acc >= 0.20)
           else "REAL_FLOOR" if (acc is not None and acc <= 0.10 and early)
           else "AMBIGUOUS_ESCALATE")
res.update(t0_steps_cap=STEPS, T0_VERDICT=verdict, baseline_2000=dict(seed0=0.065, mean=0.024),
           trajectory=state["pts"])
json.dump(res, open(os.path.join(OUT, f"linearb_full_seed{SEED}_steps{STEPS}.json"), "w"), indent=2)
json.dump({"status": "DONE", "acc": acc, "steps_run": res.get("steps"), "early_stopped": early,
           "verdict": verdict, "trajectory": state["pts"], "pid": os.getpid()},
          open(HB, "w"), indent=2)
print(f"T0 DONE verdict={verdict} acc={acc} steps={res.get('steps')} early={early}")
