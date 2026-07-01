#!/usr/bin/env python3
"""csa_sweep.py — H100 driver for the CSA learning-curve sweep (task #21).

Orchestrates the EXPENSIVE half of ``learning_curves.py`` (its ``compute_placement`` note): for each
known-answer benchmark × downsample size × seed, run the VALIDATED Tamburini 2025 CSA_OptMatcher
(via ``run_tamburini``, ``device='cuda'``) on a downsampled ``.cog``, harvest held-out Luo-2019
cognate-ID accuracy, and assemble the accuracy-vs-size learning curve + chance floor + Linear-A
locator. The deterministic downsample / floor / locator / stats helpers are REUSED from
``learning_curves`` — this module only adds the GPU orchestration those helpers deliberately leave out.

Built for a long, possibly-preempted GPU run:
  * CHECKPOINT + RESUME per (benchmark, size, seed) cell → a crash/preemption loses at most one cell.
  * CONVERGENCE EARLY-STOP: chunked annealing (his continuous schedule) stops when the best energy
    plateaus, so we don't burn the ~90 % of Tamburini's 100 000 steps that sit past the plateau
    (his own runs reach Table 3 by ~4 000 steps; see docs/findings/2026-06-30-tamburini-reproduction).
  * PREFLIGHT: torch + CUDA availability, the vendor CSA module, and the (gitignored) benchmark .cog
    files — fail fast with a clear message rather than mid-sweep.
  * per-cell logging with a running ETA; ``--dry-run`` prints the full cell plan + a cost band and
    computes nothing.

This is NOT run by the test suite: it needs the CUDA vendor build (``CSA_OptMatcher`` +
``EditDistanceWild``) and the licensed benchmark corpora. The CPU reproduction + the harness tests
live in ``run_tamburini.py`` / ``learning_curves.py`` and stay green without a GPU.

Usage on the rented H100:
  python3 scripts/baselines/csa_sweep.py --device cuda --steps 12000 --chunk 1000 \
      --seeds 0 1 2 3 --out-dir runtime/csa_sweep
  python3 scripts/baselines/csa_sweep.py --dry-run            # preview the plan + cost, no compute
  python3 scripts/baselines/csa_sweep.py --device cuda --resume ...   # re-launch after preemption
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as _mp
import os
import sys
import tempfile
import time
from typing import Dict, List, Optional, Sequence, Tuple


def _install_cuda_mp_compat() -> None:
    """Make his CUDA multiprocessing path survive a many-cell driver process.

    His ``pycsa.CoupledAnnealer`` runs ``mp.set_start_method('spawn')`` (unforced) whenever
    ``device=='cuda'`` — CUDA REQUIRES spawn (a forked CUDA context is invalid), but that call may
    run at most once per process, and this driver builds a fresh annealer per (benchmark,size,seed)
    cell in ONE process, so the 2nd cell would raise ``RuntimeError: context has already been set``.
    We set spawn once up front (force) and make his subsequent identical calls no-ops, so his
    UNMODIFIED code runs many CUDA cells back-to-back. Called only for ``--device cuda``; the CPU
    path (and the tests) never touch this."""
    try:
        _mp.set_start_method("spawn", force=True)
    except RuntimeError:
        pass
    _orig = _mp.set_start_method

    def _tolerant(method="spawn", force=False):
        try:
            _orig(method, force=force)
        except RuntimeError:
            pass                                             # already spawn — his per-annealer call

    _mp.set_start_method = _tolerant

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from scripts.comparison import learning_curves as lc  # noqa: E402
from scripts.baselines import run_tamburini as rt      # noqa: E402


# --------------------------------------------------------------------------- #
# Preflight
# --------------------------------------------------------------------------- #
def preflight(device: str, benchmarks: Sequence[str]) -> Tuple[List[str], List[str]]:
    """Return (errors, warnings). Errors are fatal (missing corpus / vendor); warnings are advisory
    (e.g. device=cuda but torch reports no CUDA — the run would silently fall back to CPU)."""
    errors: List[str] = []
    warnings: List[str] = []
    # benchmark corpora (gitignored)
    for key in benchmarks:
        cfg = lc.KNOWN_ANSWER_BENCHMARKS[key]
        path = os.path.join(lc._DATA_DIR, cfg["cog"])
        if not os.path.isfile(path):
            errors.append(f"benchmark corpus missing: {key} -> {path} (licensed/gitignored)")
    # vendor CSA module
    try:
        rt._load_vendor_module()
    except Exception as e:                                   # noqa: BLE001
        errors.append(f"vendor CSA_OptMatcher not importable: {e} "
                      "(pip install his repo + EditDistanceWild on the H100)")
    # torch / CUDA
    if device == "cuda":
        try:
            import torch  # noqa: WPS433
            if not torch.cuda.is_available():
                warnings.append("device=cuda but torch.cuda.is_available() is False — his energy "
                                "would run on CPU (slow). Check the CUDA torch build + GPU visibility.")
            else:
                warnings.append(f"CUDA OK: {torch.cuda.get_device_name(0)}")
        except Exception as e:                               # noqa: BLE001
            warnings.append(f"torch not importable ({e}); device=cuda cannot engage the GPU.")
    return errors, warnings


# --------------------------------------------------------------------------- #
# Cell plan
# --------------------------------------------------------------------------- #
def cell_plan(benchmarks: Sequence[str], seeds: Sequence[int]) -> List[dict]:
    """Every (benchmark, size, seed) cell to run, with the per-benchmark size sweep."""
    cells: List[dict] = []
    for key in benchmarks:
        cfg = lc.KNOWN_ANSWER_BENCHMARKS[key]
        path = os.path.join(lc._DATA_DIR, cfg["cog"])
        if not os.path.isfile(path):
            continue
        bench = lc.parse_cog(path)
        for size in lc.size_sweep(bench.n_gold):
            for seed in seeds:
                cells.append(dict(benchmark=key, size=int(size), seed=int(seed),
                                  n_gold=bench.n_gold, N=cfg["N"], M=cfg["M"], penf=cfg["penf"]))
    return cells


def _cell_id(cell: dict) -> str:
    return f"{cell['benchmark']}__sz{cell['size']}__seed{cell['seed']}"


# --------------------------------------------------------------------------- #
# Convergence early-stop (plateau on the best energy)
# --------------------------------------------------------------------------- #
def _plateau_stopper(eps: float, patience: int):
    """Return an ``on_checkpoint(last)`` that stops once the best energy improves by < ``eps`` for
    ``patience`` consecutive chunks. CSA minimises energy, so we watch for the fall flattening out."""
    state = {"best": None, "stale": 0}

    def _cb(last: dict) -> bool:
        e = float(last.get("energy", 0.0))
        if state["best"] is None or e < state["best"] - eps:
            state["best"] = e
            state["stale"] = 0
            return False
        state["stale"] += 1
        return state["stale"] >= patience

    return _cb


# --------------------------------------------------------------------------- #
# Run one cell (CSA on a downsampled benchmark)
# --------------------------------------------------------------------------- #
def run_cell(module, cell: dict, *, steps: int, chunk: int, device: str,
             processes: int, plateau_eps: float, plateau_patience: int,
             tmp_dir: str, log) -> dict:
    """Downsample → write_cog → CSA (chunked, CUDA, plateau-early-stop) → Luo accuracy for one cell."""
    key = lc.KNOWN_ANSWER_BENCHMARKS[cell["benchmark"]]
    bench = lc.parse_cog(os.path.join(lc._DATA_DIR, key["cog"]))
    sub = lc.downsample(bench, cell["size"], seed=cell["seed"])
    cog_path = os.path.join(tmp_dir, f"{_cell_id(cell)}.cog")
    lc.write_cog(sub, cog_path)

    reg = f"_sweep_{_cell_id(cell)}"
    rt.BENCHMARKS[reg] = dict(cog=os.path.abspath(cog_path), N=cell["N"], M=cell["M"],
                              penf=cell["penf"], published_csa=float("nan"), published_neuro=None)
    trace: List[dict] = []
    try:
        res = rt.run_one(
            module, reg, cell["seed"], steps, processes,
            checkpoint=max(1, chunk), device=device,
            on_checkpoint=_plateau_stopper(plateau_eps, plateau_patience),
            sink=lambda line: trace.append(line))
    finally:
        rt.BENCHMARKS.pop(reg, None)
        try:
            os.remove(cog_path)
        except OSError:
            pass

    # deterministic companions (cheap, CPU): the chance floor + corpus stats at this size
    gp = sub.gold_rows
    floor = lc.chance_floor(gp, n_maps=0, seed=cell["seed"], empirical=False)   # analytic floor
    stats = lc.benchmark_stats(sub)
    out = dict(cell)
    out.update(
        acc=res.get("acc"), found=res.get("found"), total=res.get("total"),
        energy=res.get("energy"), steps_run=res.get("steps", steps),
        wall_s=res.get("wall_s"), early_stopped=bool(res.get("early_stopped", False)),
        under_converged=res.get("steps", steps) < 100000,
        chance_floor_analytic=floor.get("analytic"),
        V_lost=stats.get("V_lost"), V_known=stats.get("V_known"),
        mean_signs_per_word=stats.get("mean_signs_per_word"),
        n_chunks=len(trace))
    return out


# --------------------------------------------------------------------------- #
# Report assembly (same shape as learning_curves.build_report, from checkpointed cells)
# --------------------------------------------------------------------------- #
def assemble_report(benchmarks: Sequence[str], seeds: Sequence[int], cells_dir: str,
                    steps: int) -> dict:
    """Fold the per-cell checkpoints into the accuracy-vs-size curve + Linear-A locator per benchmark."""
    def _load_cell(cell: dict) -> Optional[dict]:
        p = os.path.join(cells_dir, _cell_id(cell) + ".json")
        return json.load(open(p, encoding="utf-8")) if os.path.isfile(p) else None

    import statistics
    report: dict = {
        "kind": "pseudo_decipherment_learning_curves",
        "driver": "scripts/baselines/csa_sweep.py",
        "citation": lc.CITATION,
        "honest_framing": lc.UPPER_BOUND_STATEMENT,
        "no_phonetic_claim": True,
        "linear_a_scale": lc.LINEAR_A,
        "recovery_method": "csa",
        "recovery_steps_budget": steps,
        "benchmarks": {},
    }
    for key in benchmarks:
        cfg = lc.KNOWN_ANSWER_BENCHMARKS[key]
        path = os.path.join(lc._DATA_DIR, cfg["cog"])
        if not os.path.isfile(path):
            report["benchmarks"][key] = {"error": f"cog not found: {path}"}
            continue
        bench = lc.parse_cog(path)
        sizes = lc.size_sweep(bench.n_gold)
        curve: List[dict] = []
        for size in sizes:
            accs, floors, ss, converged = [], [], [], []
            for seed in seeds:
                c = _load_cell(dict(benchmark=key, size=int(size), seed=int(seed)))
                if c is None:
                    continue
                if c.get("acc") is not None:
                    accs.append(float(c["acc"]))
                if c.get("chance_floor_analytic") is not None:
                    floors.append(float(c["chance_floor_analytic"]))
                if c.get("mean_signs_per_word") is not None:
                    ss.append(float(c["mean_signs_per_word"]))
                converged.append(not c.get("under_converged", True))
            curve.append({
                "size": int(size),
                "recovery_mean": (statistics.mean(accs) if accs else None),
                "recovery_std": (statistics.pstdev(accs) if len(accs) > 1 else (0.0 if accs else None)),
                "n_seeds_done": len(accs),
                "chance_floor_analytic": (statistics.mean(floors) if floors else None),
                "mean_signs_per_word": (statistics.mean(ss) if ss else None),
                "all_converged": (all(converged) if converged else False),
                "recovery_is_lower_bound": (not all(converged)) if converged else True,
            })
        locator = lc.linear_a_locator(curve)
        report["benchmarks"][key] = {
            "syllabic_analog": bool(cfg["syllabic"]),
            "is_primary_linear_a_analog": key == "linearb-greek",
            "full_n_gold": bench.n_gold,
            "sizes_swept": sizes,
            "curve": curve,
            "linear_a_locator": locator,
        }
    primary = "linearb-greek" if "linearb-greek" in benchmarks else (benchmarks[0] if benchmarks else None)
    if primary and "linear_a_locator" in report["benchmarks"].get(primary, {}):
        report["headline"] = {
            "primary_benchmark": primary,
            "linear_a_locator": report["benchmarks"][primary]["linear_a_locator"],
            "note": ("Known-answer UPPER BOUND: the syllabic analog (Linear B → Greek) is the closest "
                     "structural match to Linear A but WITH a real cognate signal Linear A lacks. "
                     "At-floor at Linear-A scale ⇒ information-insufficient; above-chance ⇒ the binding "
                     "constraint is identifiability, not corpus size. Never a decipherability claim."),
        }
    return report


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def _fmt_hms(s: float) -> str:
    s = int(s)
    return f"{s // 3600:d}h{(s % 3600) // 60:02d}m{s % 60:02d}s"


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="H100 driver for the CSA learning-curve sweep (task #21)")
    p.add_argument("--benchmarks", nargs="*", default=list(lc.KNOWN_ANSWER_BENCHMARKS),
                   choices=list(lc.KNOWN_ANSWER_BENCHMARKS))
    p.add_argument("--seeds", type=int, nargs="*", default=[0, 1, 2, 3])
    p.add_argument("--steps", type=int, default=12000,
                   help="max CSA steps per cell (his artifact hardcodes 100000; convergence is by "
                        "~4-10k, so 12000 + plateau early-stop is the converged budget). ")
    p.add_argument("--chunk", type=int, default=1000, help="checkpoint chunk (steps per harvest)")
    p.add_argument("--processes", type=int, default=16, help="annealer processes (<= 16)")
    p.add_argument("--device", default="cuda", choices=["cuda", "cpu"])
    p.add_argument("--plateau-eps", type=float, default=0.05,
                   help="stop a cell when best energy improves by < this for --plateau-patience chunks")
    p.add_argument("--plateau-patience", type=int, default=3)
    p.add_argument("--out-dir", default=os.path.join(_ROOT, "runtime", "csa_sweep"))
    p.add_argument("--fresh", action="store_true", help="ignore existing cell checkpoints (default: resume)")
    p.add_argument("--force", action="store_true", help="run even if preflight reports errors")
    p.add_argument("--dry-run", action="store_true", help="print the cell plan + cost band; compute nothing")
    args = p.parse_args(argv)
    if args.device == "cuda":
        _install_cuda_mp_compat()                            # his __init__ still set_start_method's; keep it a no-op
        # His parallel path (__update_state) creates a fresh mp.Pool EVERY step and passes CUDA
        # tensors across it — which forks a CUDA context and dies ("Cannot re-initialize CUDA in
        # forked subprocess"). With processes<=1 his annealer takes the SERIAL __update_state_no_par
        # path (no Pool at all); the GPU already parallelizes each EditDistanceWild energy eval over
        # the whole lexicon, so serial-over-16-annealers is both correct and fast on the H100.
        if args.processes > 1:
            print(f"[cuda] forcing --processes 1 (his parallel Pool forks CUDA tensors; the GPU "
                  f"parallelizes each energy eval, so serial annealing is the correct CUDA mode)")
            args.processes = 1

    cells = cell_plan(args.benchmarks, args.seeds)
    errors, warnings = preflight(args.device, args.benchmarks)
    for w in warnings:
        print(f"[preflight] {w}")
    for e in errors:
        print(f"[preflight][ERROR] {e}")

    # cost band from the CPU anchors (Ugaritic ~6h/seed converged on CPU); GPU factor is a documented
    # extrapolation (EditDistanceWild is CUDA-capable) so we print a band, not a point.
    if args.dry_run or errors:
        print(f"\n[plan] {len(args.benchmarks)} benchmarks × sizes × {len(args.seeds)} seeds "
              f"= {len(cells)} cells")
        by_b: Dict[str, int] = {}
        for c in cells:
            by_b[c["benchmark"]] = by_b.get(c["benchmark"], 0) + 1
        for b, n in by_b.items():
            print(f"   {b:22s} {n:3d} cells")
        print("\n[cost] CPU anchor: converged Ugaritic ≈ 6 h/seed (40 s/step × ~540 steps to cool). "
              "GPU (EditDistanceWild CUDA) extrapolated ~50–500× → converged sweep ≈ 2–6 h on one "
              "H100 (dominated by the largest full-size seeds; downsampled cells are minutes). "
              "Full 100k-step faithful protocol ≈ 1–3 days. Rental ≈ $2–3/h.")
        if errors and not args.dry_run:
            print("\n[abort] preflight errors above; pass --force to run anyway.")
            return 2
        if args.dry_run:
            return 0

    os.makedirs(args.out_dir, exist_ok=True)
    cells_dir = os.path.join(args.out_dir, "cells")
    os.makedirs(cells_dir, exist_ok=True)
    tmp_dir = tempfile.mkdtemp(prefix="csa_sweep_")

    module = rt._load_vendor_module()
    pending = []
    for c in cells:
        cp = os.path.join(cells_dir, _cell_id(c) + ".json")
        if not args.fresh and os.path.isfile(cp):
            continue
        pending.append(c)
    done0 = len(cells) - len(pending)
    print(f"\n[sweep] {len(cells)} cells total; {done0} already checkpointed; {len(pending)} to run.")

    t_start = time.time()
    for i, c in enumerate(pending, 1):
        t0 = time.time()
        res = run_cell(module, c, steps=args.steps, chunk=args.chunk, device=args.device,
                       processes=args.processes, plateau_eps=args.plateau_eps,
                       plateau_patience=args.plateau_patience, tmp_dir=tmp_dir, log=print)
        with open(os.path.join(cells_dir, _cell_id(c) + ".json"), "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=2)
        elapsed = time.time() - t_start
        eta = (elapsed / i) * (len(pending) - i)
        print(f"[cell {i}/{len(pending)}] {_cell_id(c):40s} acc={res.get('acc')} "
              f"E={res.get('energy')} steps={res.get('steps_run')} "
              f"{'(early-stop)' if res.get('early_stopped') else ''} "
              f"cell={_fmt_hms(time.time() - t0)} elapsed={_fmt_hms(elapsed)} eta={_fmt_hms(eta)}")

    report = assemble_report(args.benchmarks, args.seeds, cells_dir, args.steps)
    out_path = os.path.join(args.out_dir, "csa_sweep_report.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)
    print(f"\n[done] {len(pending)} cells run in {_fmt_hms(time.time() - t_start)}; report -> {out_path}")
    if "headline" in report:
        print("[headline]", json.dumps(report["headline"]["linear_a_locator"], ensure_ascii=False)[:300])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
