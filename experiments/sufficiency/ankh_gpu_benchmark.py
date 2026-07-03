#!/usr/bin/env python3
"""ankh_gpu_benchmark.py — one-cell CSA timing benchmark for the human to run on ankh (RTX 3090 Ti).

PURPOSE: measure the ONE number the GPU lanes hinge on — the per-cell GPU/CPU wall-clock RATIO for
Tamburini's CSA_OptMatcher. The sweep's 76 remaining cells are the large sizes; if the GPU ratio is
~1 (orchestration-bound, as the vendored csa_batched.py docstring predicts: naive CUDA leaves "an
H100 ~1% utilised"), the GPU lanes lose on total time-to-curve. If it is large, they merit pricing.

This MODIFIES NOTHING in the sweep. It calls the sweep's own `run_cell` (byte-identical cell path)
with the device toggled and the opt-in `batched=` flag threaded through exactly as the sweep does.
Because it is a different code path from the 92 completed CPU cells, its OUTPUT is a timing only —
never a sweep cell (comparability rule).

PREREQUISITES on ankh: the logos repo; the gitignored licensed benchmark corpora under corpus/bronze/
(copy the *.cog from the logos host — not redistributed); torch+CUDA for the 3090 Ti; the vendored
EditDistanceWild / pycsa / lsa_2g reachable (the script adds them to sys.path).

RUN (repo root), ~10-20 min total:
  # 1. CPU sanity — should land near the printed host baseline (confirms corpora+env match):
  python3 experiments/sufficiency/ankh_gpu_benchmark.py --device cpu  --cell cypriot-greek:100:0
  # 2. GPU naive (device=cuda, unbatched) — expected SLOW (orchestration-bound):
  python3 experiments/sufficiency/ankh_gpu_benchmark.py --device cuda --cell cypriot-greek:100:0
  # 3. GPU batched (one kernel/step, the built+validated path):
  python3 experiments/sufficiency/ankh_gpu_benchmark.py --device cuda --batched --cell cypriot-greek:100:0
REPORT BACK: the wall_s for each + peak GPU-util from `nvidia-smi dmon` during run 3.
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
import tempfile
import time

# measured 2000-step, processes=4 CPU baselines from the logos host (results/csa cells):
CPU_BASELINE_S = {"cypriot-greek:100:0": 1759.0, "cypriot-greek:69:0": 948.0,
                  "linearb-greek:200:0": 1040.0, "phoenician-ugaritic:100:0": None}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    ap.add_argument("--batched", action="store_true")
    ap.add_argument("--cell", required=True, help="benchmark:size:seed, e.g. cypriot-greek:100:0")
    ap.add_argument("--steps", type=int, default=2000)      # match the completed cells
    ap.add_argument("--processes", type=int, default=4)     # match the completed cells
    a = ap.parse_args()

    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, root)
    sys.path.insert(0, os.path.join(root, "corpus", "bronze", "code", "CSA_OptMatcher"))

    from scripts.baselines import csa_sweep, run_tamburini as rt
    from scripts.comparison import learning_curves as lc

    bench, size, seed = a.cell.split(":")
    size, seed = int(size), int(seed)
    cfg = lc.KNOWN_ANSWER_BENCHMARKS[bench]
    ngold = lc.parse_cog(os.path.join(lc._DATA_DIR, cfg["cog"])).n_gold
    cell = dict(benchmark=bench, size=size, seed=seed, n_gold=ngold,
                N=cfg["N"], M=cfg["M"], penf=cfg["penf"])
    module = rt._load_vendor_module()

    base = CPU_BASELINE_S.get(a.cell)
    print(f"[bench] cell={a.cell} device={a.device} batched={a.batched} steps={a.steps} "
          f"proc={a.processes}" + (f" | host CPU baseline={base:.0f}s ({base/60:.1f}min)"
                                   if base else " | no host baseline for this cell"), flush=True)

    with tempfile.TemporaryDirectory() as tmp:
        t0 = time.time()
        out = csa_sweep.run_cell(module, cell, steps=a.steps, chunk=1000, device=a.device,
                                 processes=a.processes, plateau_eps=0.05, plateau_patience=3,
                                 tmp_dir=tmp, log=logging.getLogger("bench"), batched=a.batched)
        dt = time.time() - t0
    print(f"[bench] RESULT acc={out.get('acc'):.4f} steps_run={out.get('steps_run')} "
          f"wall_s={dt:.0f} ({dt/60:.1f}min)")
    if base:
        print(f"[bench] GPU/CPU wall RATIO = {dt/base:.2f}x "
              f"({'FASTER' if dt < base else 'SLOWER — orchestration-bound, GPU lane loses'})")
    print("[bench] timing only; NOT a sweep cell (different path => not comparable to the 92 done).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
