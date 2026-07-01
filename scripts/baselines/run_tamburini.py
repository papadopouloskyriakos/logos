#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
logos wrapper around Tamburini 2025 CSA_OptMatcher — the published non-neural
cognate-ID baseline (the B-K&K + Luo comparison layer; prior art, NOT a logos
contribution). Reproduces Table 3 of:

    Tamburini, F. (2025). "On automatic decipherment of lost ancient scripts
    relying on combinatorial optimisation and coupled simulated annealing."
    Frontiers in Artificial Intelligence 8:1581129.
    DOI: 10.3389/frai.2025.1581129
    Code: https://github.com/ftamburin/CSA_OptMatcher (+ EditDistanceWild)

WHAT THIS WRAPPER DOES
  Invokes Tamburini's *unmodified* classes/functions (Problem, CoupledAnnealer,
  lsa_2g, EvalModel, energy, move) to run CSA on a benchmark .cog file, then
  parses the Luo et al. 2019 cognate-ID accuracy his EvalModel prints.

WHAT IT DOES NOT DO
  - It does NOT modify the CSA algorithm, the energy function, the move operator,
    the LSA-2G matcher, or the accuracy metric. Every one of those is his code.
  - It only (a) wires his module so multiprocessing pickling works on our host
    (import as a real importable module, not a synthetic importlib name), (b)
    exposes CLI knobs for seed / steps / processes that his monolithic __main__
    hardcodes, and (c) parses the printed accuracy into a machine-readable line.

PROTOCOL (paper §3.2-3.3, reproduced faithfully):
  - 16 coupled annealers (his n_annealers constant).
  - N, M set by his stated rule:  N=1,M=2 if |L_s|>|K_s| else N=2,M=1.
  - lambda (penf) = 4 generally; = 8 for U/OH-noisy (his stated exception).
  - tacc_initial=200, tacc_schedule=0.95, tgen_initial=1, tgen_schedule=0.999,
    qa=0.1, update_interval=ceil(|state|/16) (all his defaults).
  - mean +/- std over >=4 seeds (Reimers & Gurevych 2017) — use --seeds.

HONEST DEVIATIONS (no GPU on this host; paper used CUDA):
  - His code hardcodes steps=100000 and prints every energy eval to stdout.
    On CPU, 100000 steps is infeasible for the large lexica (U/OH = 18.8 s per
    energy eval x 16 annealers x 100000 steps ~= weeks). We therefore expose
    --steps (default 1000) and report the budget used alongside every number.
    His paper's *stated* stopping rule is "100 temperature updates without
    improvement in best sigma" — his released code does not implement that
    early-stop, so a fixed step budget is the faithful reading of the artifact.
  - torch is CPU-only here; set OMP/OPENBLAS/MKL_NUM_THREADS=1 + torch threads=1
    so the 8-worker pool does not thrash 8x20 threads on 20 cores.

USAGE
  python3 scripts/baselines/run_tamburini.py --list
  python3 scripts/baselines/run_tamburini.py --benchmark luvian-hittite --steps 1000
  python3 scripts/baselines/run_tamburini.py --benchmark ugaritic-noiseless --seeds 0 1 2 3 --steps 1000

Exit code 0 on success. Prints a final parseable line per seed:
  TAMBURINI_RESULT benchmark=... seed=... steps=... processes=... acc=0.xxx found=N total=M energy=... wall_s=...
and, with --seeds >1, a final summary:
  TAMBURINI_SUMMARY benchmark=... n_seeds=... mean=... std=... published=...
"""

import os

# --- Thread caps MUST precede `import torch` (torch reads them at import). ---
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("OPENBLAS_MAIN_FREE", "1")  # his README requirement

import sys
import re
import json
import math
import time
import argparse
import io
import contextlib
import random
import statistics

# Locate the vendored code (gitignored under corpus/bronze). Resolve from the
# logos repo root so the wrapper works regardless of cwd.
HERE = os.path.dirname(os.path.abspath(__file__))
LOGOS_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CSA_DIR = os.path.join(LOGOS_ROOT, "corpus", "bronze", "code", "CSA_OptMatcher")
DATA_DIR = os.path.join(CSA_DIR, "data")
FIXNULL = os.path.join(DATA_DIR, "FixNULL")  # empty file = no pre-pinned signs

if not os.path.isdir(CSA_DIR):
    sys.stderr.write(
        f"ERROR: vendored CSA_OptMatcher not found at {CSA_DIR}.\n"
        f"Run: git clone --depth 1 https://github.com/ftamburin/CSA_OptMatcher "
        f"into corpus/bronze/code/ (gitignored; invariant 10).\n")
    sys.exit(2)


def _load_vendor_module():
    """Import CSA_OptMatcher as a REAL importable module so multiprocessing
    workers (fork) can unpickle <class 'CSA_OptMatcher.Problem'>. Loading via
    importlib under a synthetic name breaks pool pickling with PicklingError."""
    import torch
    torch.set_num_threads(1)  # avoid 8 workers x N-thread thrash
    import multiprocessing as mp
    try:
        mp.set_start_method("fork", force=True)  # his default for cpu
    except RuntimeError:
        pass
    if CSA_DIR not in sys.path:
        sys.path.insert(0, CSA_DIR)
    import CSA_OptMatcher as m  # noqa: F401  (also pulls EditDistanceWild, pycsa, lsa_2g)
    return m


# --- Benchmark registry. N/M/penf from Tamburini 2025 §3.3 (his stated rule).
# |L_s| = lost-script inventory, |K_s| = known-script inventory (paper §2).
# published_csa = his Table 3 cognate-ID accuracy (mean over 4 seeds).
# published_neuro = his decontaminated NeuroCipher (Luo 2019) re-run, Table 3.
BENCHMARKS = {
    "ugaritic-noiseless": dict(
        cog="uga-heb.no_speNL.cog", N=1, M=2, penf=4.0,
        published_csa=95.5, published_neuro=90.4),
    "ugaritic-noisy": dict(
        cog="uga-heb.no_speNoisy.cog", N=1, M=2, penf=8.0,   # lambda=8 (his exception)
        published_csa=74.7, published_neuro=87.6),
    "linearb-greek": dict(
        cog="linear_b-greek.cog", N=2, M=1, penf=4.0,
        published_csa=89.4, published_neuro=75.8),
    "cypriot-greek": dict(           # CS/AG (Cypriot syllabary / Arcadocypriot Greek)
        cog="csyl-greek.cog", N=2, M=1, penf=4.0,
        published_csa=86.3, published_neuro=None),
    "phoenician-ugaritic": dict(     # Ph/Ug (StarlingDB)
        cog="StarlingDB_Ph-Ug.cog", N=2, M=1, penf=4.0,
        published_csa=80.5, published_neuro=None),
    "luvian-hittite": dict(          # Luv/Hit (RWT2002)
        cog="RWT2002_Luv-Hit.cog", N=2, M=1, penf=4.0,
        published_csa=47.5, published_neuro=18.2),
}

ACC_RE = re.compile(r"Accuracy:\s*([0-9.]+)\s+(\d+)/(\d+)")


def _gold_matches(cog_path):
    """Reproduces his -o eval branch's goldMatches read (column 0 vs 1)."""
    gm = []
    with open(cog_path, "r", encoding="utf-8") as f:
        first = True
        for line in f:
            parts = line.rstrip().split()
            if first:
                first = False
                continue
            if len(parts) >= 2 and parts[0] != "_" and parts[1] != "_":
                gm.append((parts[0], parts[1]))
    return gm


def _eval_best(module, prob, cog_path, energy_best):
    """Evaluate the best state with his metric (his -o eval branch, unmodified
    functions: Problem.energy, lsa_2g, EvalModel). Returns (acc, found, total)."""
    # Recover the best state's assignment + cost matrix by re-running his energy
    # on it (his -o branch does exactly this).
    # NOTE: get_best returns (energy, state); we must turn state -> assignment ->
    # UsolMatch. Re-run his energy(state) to populate prob.costM/dynLex.
    state = energy_best[1]
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        prob.energy(state, freeMem=False)
        row_ind, col_ind, _ = module.lsa_2g(prob.costM, prob.lGroupsW, prob.kGroups)
        usol = [("".join(prob.dynLex[row_ind[l]]),
                 "".join(prob.kLex[col_ind[l]])) for l in range(len(row_ind))]
        module.EvalModel(usol, _gold_matches(cog_path))
    for line in log.getvalue().splitlines():
        mt = ACC_RE.search(line)
        if mt:
            return float(mt.group(1)), int(mt.group(2)), int(mt.group(3))
    return None, None, None


def _build_annealer(module, prob, steps, processes, device="cpu"):
    """Construct his CoupledAnnealer with his exact default hyperparameters
    (only steps/processes/device are exposed). ``device='cuda'`` is the H100 path — his
    energy (EditDistanceWild) is CUDA-capable; ``'cpu'`` is the default and preserves the
    validated CPU reproduction."""
    n_annealers = 16  # his constant
    stepsatsameT = max(math.ceil(len(prob.init_state) / n_annealers), 5)
    return module.CoupledAnnealer(
        prob.energy, prob.move,
        initial_state=[prob.init_state] * n_annealers,
        update_interval=stepsatsameT,
        steps=steps,
        processes=processes,
        n_annealers=n_annealers,
        tacc_initial=200.0, tacc_schedule=0.95,
        tgen_initial=1.0, tgen_schedule=0.999,
        qa=0.1, verbose=0, device=device), n_annealers


def run_one(module, bench_key, seed, steps, processes, checkpoint=0, sink=print, device="cpu",
            on_checkpoint=None, batched=False):
    """Run CSA on one benchmark/seed. Uses ONLY his Problem / CoupledAnnealer /
    energy / move / lsa_2g / EvalModel.

    checkpoint>0: call his anneal() in chunks of `checkpoint` steps (his annealer
    mutates instance temps/state, so the temperature schedule is CONTINUOUS across
    chunks) and evaluate+emit get_best() accuracy after each chunk. This yields a
    convergence trace and lets a long run be harvested even if it must stop early.

    ``device='cuda'`` runs his energy on the GPU (the H100 sweep path); default 'cpu'.
    ``on_checkpoint(last_dict) -> bool`` (checkpoint mode only): called after each chunk; return
    True to STOP early (e.g. energy plateau) — never alters the temperature schedule, only ends it.
    """
    cfg = BENCHMARKS[bench_key]
    cog_path = os.path.join(DATA_DIR, cfg["cog"])

    # Seed Python + numpy RNGs BEFORE constructing Problem (his Problem.__init__
    # calls random.shuffle on the initial state).
    random.seed(seed)
    try:
        import numpy as np
        np.random.seed(seed)
    except Exception:
        pass

    prob = module.Problem(cog_path, FIXNULL, "", cfg["N"], cfg["M"],
                          cfg["penf"], device)
    t0 = time.perf_counter()

    def _maybe_batch(ann):
        # Batched-parallel CUDA energy (bit-identical to serial; validated on CPU). Requires the
        # serial no_par path (processes<=1), which anneal() takes when processes<=1.
        if batched:
            from scripts.baselines import csa_batched
            csa_batched.install_batched(ann)

    if checkpoint > 0:
        # Chunked run: continuous schedule, harvest after each chunk.
        annealer, _ = _build_annealer(module, prob, checkpoint, processes, device)
        _maybe_batch(annealer)
        last = None
        done = 0
        while done < steps:
            with contextlib.redirect_stdout(io.StringIO()):
                annealer.anneal()  # his energy() prints per-eval; silence it
            done += checkpoint
            e, st = annealer.get_best()
            acc, found, total = _eval_best(module, prob, cog_path, (e, st))
            last = dict(benchmark=bench_key, seed=seed, steps=done,
                        processes=processes, N=cfg["N"], M=cfg["M"],
                        penf=cfg["penf"], acc=acc, found=found, total=total,
                        energy=float(e), wall_s=round(time.perf_counter() - t0, 2))
            sink("TAMBURINI_CHECKPOINT benchmark={benchmark} seed={seed} "
                 "steps={steps} acc={acc} found={found} total={total} "
                 "energy={energy:.4f} wall_s={wall_s}".format(**last))
            if on_checkpoint is not None and on_checkpoint(last):
                last["early_stopped"] = True
                break
        return last

    # Single run.
    annealer, _ = _build_annealer(module, prob, steps, processes, device)
    _maybe_batch(annealer)
    with contextlib.redirect_stdout(io.StringIO()):
        annealer.anneal()
    e, st = annealer.get_best()
    wall = time.perf_counter() - t0
    acc, found, total = _eval_best(module, prob, cog_path, (e, st))
    return dict(
        benchmark=bench_key, seed=seed, steps=steps, processes=processes,
        N=cfg["N"], M=cfg["M"], penf=cfg["penf"],
        acc=acc, found=found, total=total,
        energy=float(e), wall_s=round(wall, 2))


def main():
    ap = argparse.ArgumentParser(description="logos wrapper for Tamburini 2025 CSA_OptMatcher")
    ap.add_argument("--list", action="store_true", help="list benchmarks + published Table 3")
    ap.add_argument("--benchmark", "-b", choices=list(BENCHMARKS))
    ap.add_argument("--seeds", type=int, nargs="*", default=[0],
                    help="random seeds (paper uses 4). default: 0")
    ap.add_argument("--steps", type=int, default=1000,
                    help="CSA steps (his code hardcodes 100000; infeasible on CPU "
                         "for large lexica). default 1000")
    ap.add_argument("--processes", type=int, default=8,
                    help="parallel annealer processes (<= n_annealers=16). default 8")
    ap.add_argument("--device", default="cpu",
                    help="cpu (default, validated reproduction) | cuda (H100 sweep — his energy "
                         "EditDistanceWild is CUDA-capable)")
    ap.add_argument("--checkpoint-steps", type=int, default=0,
                    help="if >0, run his anneal() in chunks of this many steps and "
                         "emit a TAMBURINI_CHECKPOINT accuracy line after each (continuous "
                         "temperature schedule). Lets a long CPU run be harvested early.")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of parseable lines")
    args = ap.parse_args()

    if args.list:
        print(f"{'benchmark':22s} {'cog':26s} {'N':>2} {'M':>2} {'penf':>5} "
              f"{'CSA_pub':>8} {'Neuro_pub':>9}")
        for k, c in BENCHMARKS.items():
            neu = "-" if c["published_neuro"] is None else f"{c['published_neuro']:.1f}"
            print(f"{k:22s} {c['cog']:26s} {c['N']:>2} {c['M']:>2} {c['penf']:>5.1f} "
                  f"{c['published_csa']:>8.1f} {neu:>9}")
        print("\nNOTE: CSA_pub = Tamburini 2025 Table 3 (mean over 4 seeds, GPU). "
              "Our CPU runs use --steps (default 1000, NOT his 100000): "
              "treat under-converged numbers as lower bounds.")
        return

    if not args.benchmark:
        ap.error("--benchmark is required (or --list)")

    module = _load_vendor_module()
    results = []
    for s in args.seeds:
        r = run_one(module, args.benchmark, s, args.steps, args.processes,
                    checkpoint=args.checkpoint_steps, device=args.device)
        results.append(r)
        if not args.json:
            print("TAMBURINI_RESULT benchmark={benchmark} seed={seed} "
                  "steps={steps} processes={processes} N={N} M={M} penf={penf} "
                  "acc={acc} found={found} total={total} energy={energy:.4f} "
                  "wall_s={wall_s}".format(**r))
        else:
            print(json.dumps(r))

    if len(results) > 1:
        accs = [r["acc"] for r in results if r["acc"] is not None]
        if accs:
            mean = statistics.mean(accs)
            std = statistics.pstdev(accs) if len(accs) > 1 else 0.0
            pub = BENCHMARKS[args.benchmark]["published_csa"]
            summ = dict(benchmark=args.benchmark, n_seeds=len(accs),
                        mean=round(mean, 4), std=round(std, 4), published=pub,
                        steps=args.steps)
            if args.json:
                print(json.dumps(summ))
            else:
                print("TAMBURINI_SUMMARY benchmark={benchmark} n_seeds={n_seeds} "
                      "mean={mean} std={std} published={published} steps={steps} "
                      "(pub is GPU/100000-steps; ours is CPU/{steps})".format(**summ))


if __name__ == "__main__":
    main()
