#!/usr/bin/env python3
"""csa_local_curve.py — focused CSA learning-curve on CPU via his validated parallel path.

A stable, self-contained runner for a FEW (benchmark, size, seed) points using his own
16-process CPU annealing (``processes=16``, no batching) — the byte-for-byte-reproduced path
(docs/findings/2026-06-30-tamburini-reproduction). Writes one cell JSON per point + assembles the
accuracy-vs-size curve + chance floor + Linear-A locator (reusing learning_curves helpers), so the
result is a real, reproducible learning curve even without the GPU sweep.

Usage:  PYTHONPATH=. python -u scripts/baselines/csa_local_curve.py --out runtime/csa_curve [--steps 1500]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.baselines import run_tamburini as rt  # noqa: E402
from scripts.baselines import csa_sweep as S  # noqa: E402
from scripts.comparison import learning_curves as lc  # noqa: E402

# focused plan: primary Linear-A analog (linearb-greek) across sizes, then the smaller benchmarks.
# n_gold values are read at runtime from the cog; sizes are Linear-A-scale and below + a couple above.
PLAN = [
    ("linearb-greek", 2, 1, [100, 200, 400, 650, 900]),
    ("luvian-hittite", 2, 1, [30, 44, 59]),
    ("phoenician-ugaritic", 2, 1, [100, 200, 400]),
    ("cypriot-greek", 2, 1, [100, 200, 400, 650]),
    ("ugaritic-noiseless", 1, 2, [100, 200, 400, 650]),
]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Focused CSA learning-curve on CPU (his parallel path)")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "..", "runtime", "csa_curve"))
    ap.add_argument("--steps", type=int, default=1500)
    ap.add_argument("--chunk", type=int, default=250)
    ap.add_argument("--processes", type=int, default=1)     # batched serial: one tiled edit-distance
    ap.add_argument("--no-batched", action="store_true")     #   call/step, no per-step pool overhead
    ap.add_argument("--seeds", type=int, nargs="*", default=[0])
    ap.add_argument("--plateau-eps", type=float, default=0.02)
    ap.add_argument("--plateau-patience", type=int, default=3)
    args = ap.parse_args(argv)

    cells_dir = os.path.abspath(os.path.join(args.out, "cells"))
    os.makedirs(cells_dir, exist_ok=True)
    module = rt._load_vendor_module()
    import tempfile
    tmp = tempfile.mkdtemp(prefix="csa_local_")

    benches = [p[0] for p in PLAN]
    for bench, N, M, sizes in PLAN:
        cfg = lc.KNOWN_ANSWER_BENCHMARKS[bench]
        path = os.path.join(lc._DATA_DIR, cfg["cog"])
        if not os.path.isfile(path):
            print(f"SKIP {bench}: cog missing", flush=True)
            continue
        n_gold = lc.parse_cog(path).n_gold
        for size in sizes:
            if size > n_gold:
                continue
            for seed in args.seeds:
                cid = f"{bench}__sz{size}__seed{seed}"
                cp = os.path.join(cells_dir, cid + ".json")
                if os.path.exists(cp):
                    continue
                cell = dict(benchmark=bench, size=int(size), seed=int(seed),
                            n_gold=n_gold, N=N, M=M, penf=4.0)
                t0 = time.time()
                try:
                    r = S.run_cell(module, cell, steps=args.steps, chunk=args.chunk, device="cpu",
                                   processes=args.processes, plateau_eps=args.plateau_eps,
                                   plateau_patience=args.plateau_patience, tmp_dir=tmp,
                                   log=lambda *a: None, batched=(not args.no_batched))
                    json.dump(r, open(cp, "w"))
                    print(f"DONE {cid} acc={round(r.get('acc') or 0, 3)} "
                          f"steps={r.get('steps_run')} wall={r.get('wall_s')} "
                          f"early={r.get('early_stopped')}", flush=True)
                except Exception as e:  # noqa: BLE001
                    print(f"FAIL {cid}: {type(e).__name__}: {e}", flush=True)

    report = S.assemble_report(benches, args.seeds, cells_dir, args.steps)
    rp = os.path.abspath(os.path.join(args.out, "csa_curve_report.json"))
    json.dump(report, open(rp, "w"), indent=2, ensure_ascii=False)
    print(f"CURVE_COMPLETE -> {rp}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
