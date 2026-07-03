#!/usr/bin/env python3
"""quota_sweep.py — Phase 2 Step 1: synthetic anchor-quota sweep per SWEEP_SPEC.md (42618ac).

Entirely synthetic: abstract anchor words over the 49-eligible pool; no real candidate anchor,
no real held-out label, no recovery model on real data. Reuses the certified harness
(power_precheck.load_design/_nn_preds); pin semantics verbatim (a word with >=2 masked member
signs pins none of them; any qualifying word pins).

Usage:
  python3 quota_sweep.py --selftest          # planted redundancy/collision checks
  python3 quota_sweep.py --profile           # ONE cell, measured wall-clock + projection
  python3 quota_sweep.py --sweep [--workers N]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_GATE = os.path.dirname(_HERE)
sys.path.insert(0, _GATE)

from power_precheck import _git, _nn_preds, load_design          # noqa: E402
from phase1_power import INELIGIBLE                              # noqa: E402

SPEC_COMMIT = "42618ac"
MASTER = 20260712
STRENGTHS = (0.0, 0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 13.0)
N_REP = 100
N_PERM = 200
H = 20
ALPHA = 0.05
LEN_VALUES = (3, 4)
LEN_PROBS = (23 / 30, 7 / 30)
N_GRID = (5, 8, 10, 15, 20, 25, 30, 40)
R_GRID = (1, 2, 3)

CELLS = [(n, r) for n in N_GRID for r in R_GRID if 3 * n <= 49 * r]   # spec feasibility pre-rule
CELLS.sort(key=lambda c: (c[0], c[1]))
SKIPPED = sorted(set((n, r) for n in N_GRID for r in R_GRID) - set(CELLS))

_G: dict = {}


def _init():
    anchors, candidates, U, true_val = load_design()
    elig = np.array([i for i, s in enumerate(anchors) if s not in INELIGIBLE])
    _G.update(anchors=anchors, U=U, true_val=true_val, elig=elig, n=len(anchors))


def gen_words(rng, n_anchors, R, elig):
    """Synthetic anchor words under the redundancy cap; None if the set cannot be realized."""
    legs = {}
    words = []
    for _ in range(n_anchors):
        L = int(rng.choice(LEN_VALUES, p=LEN_PROBS))
        allowed = np.array([x for x in elig if legs.get(int(x), 0) < R])
        if len(allowed) < L:
            return None
        w = tuple(int(x) for x in rng.choice(allowed, size=L, replace=False))
        for x in w:
            legs[x] = legs.get(x, 0) + 1
        words.append(w)
    return words


def replicate(n_anchors, R, s, seed, pins_on=True):
    """One replicate: (survival_detect, full_detect, n_pinned, n_pinning_words, regens)."""
    U, true_val, elig, n = _G["U"], _G["true_val"], _G["elig"], _G["n"]
    rng = np.random.default_rng(seed)
    regens = 0
    words = gen_words(rng, n_anchors, R, elig)
    while words is None:
        regens += 1
        words = gen_words(rng, n_anchors, R, elig)
        if regens > 50:
            raise RuntimeError(f"cell ({n_anchors},{R}) unrealizable")

    d = U.shape[1]
    Q, _ = np.linalg.qr(rng.normal(size=(d, d)))
    X = s * (U[true_val] @ Q.T) + rng.normal(size=(n, d))
    X = X / np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-12)

    held = np.sort(rng.choice(elig, size=H, replace=False))
    train = np.array(sorted(set(range(n)) - set(held.tolist())))
    held_set = set(held.tolist())

    pin_words = {}
    if pins_on:
        for x in held:
            pw = [j for j, w in enumerate(words)
                  if x in w and all((y == int(x)) or (y not in held_set) for y in w)]
            if pw:
                pin_words[int(x)] = pw
    pinning = sorted({j for pws in pin_words.values() for j in pws})

    def score(assign, preds, drop=None):
        hits = 0
        for k, x in enumerate(held):
            pws = pin_words.get(int(x), [])
            if drop is not None:
                pws = [j for j in pws if j != drop]
            hits += int(true_val[x] == assign[x]) if pws else int(preds[k] == assign[x])
        return hits / H

    scorings = [None] + pinning                       # full + LOAO for each pinning word
    preds_obs, _ = _nn_preds(X, U, true_val, train, held)
    obs = [score(true_val, preds_obs, dr) for dr in scorings]
    null = np.zeros((len(scorings), N_PERM))
    for k in range(N_PERM):
        pi = true_val[rng.permutation(n)]
        preds_k, _ = _nn_preds(X, U, pi, train, held)
        for si, dr in enumerate(scorings):
            null[si, k] = score(pi, preds_k, dr)
    p = (1 + np.sum(null >= np.array(obs)[:, None] - 1e-12, axis=1)) / (N_PERM + 1)
    full_det = p[0] < ALPHA
    survival = bool(full_det and all(pv < ALPHA for pv in p[1:]))
    return survival, bool(full_det), len(pin_words), len(pinning), regens


def run_block(args):
    ci, si, reps, pins_on = args
    n_anchors, R = CELLS[ci] if ci >= 0 else (0, 1)   # ci=-1 => machinery (pins off, no words)
    s = STRENGTHS[si]
    out = []
    for r in reps:
        seed = MASTER + 100000 * (ci if ci >= 0 else 99) + 1000 * si + r
        if ci >= 0:
            out.append(replicate(n_anchors, R, s, seed, pins_on=pins_on))
        else:
            out.append(replicate(5, 3, s, seed, pins_on=False))   # words irrelevant when pins off
    return ci, si, out


def selftest():
    _init()
    U, true_val, elig = _G["U"], _G["true_val"], _G["elig"]
    held = [int(elig[0]), int(elig[1])]
    held_set = set(held)
    # (i) collision: a word with BOTH masked signs pins neither
    w_coll = (held[0], held[1], int(elig[2]))
    pins = [x for x in held if all((y == x) or (y not in held_set) for y in w_coll)]
    assert pins == [], "collision word must pin nothing"
    # (ii) redundancy: sign covered by two clean words survives either drop
    w1 = (held[0], int(elig[3]), int(elig[4]))
    w2 = (held[0], int(elig[5]), int(elig[6]))
    pw = [j for j, w in enumerate([w1, w2])
          if held[0] in w and all((y == held[0]) or (y not in held_set) for y in w)]
    assert pw == [0, 1], "doubly-covered sign must carry two legs"
    for drop in (0, 1):
        assert [j for j in pw if j != drop], "one leg must survive either drop"
    print("selftest OK: collision pins nothing; double coverage survives either drop")


def sweep(workers, profile_only=False):
    _init()
    os.makedirs(os.path.join(_HERE, "results"), exist_ok=True)
    t0 = time.time()

    # profile: ONE cell, serial
    ci0 = 0
    tprof = time.time()
    prof = [run_block((ci0, si, list(range(N_REP)), True)) for si in range(len(STRENGTHS))]
    cell_secs = time.time() - tprof
    # LOAO scoring cost grows with pinning words; scale projection by mean pinning count bound
    proj_serial = cell_secs * len(CELLS) * 1.6            # 1.6 = headroom for large-n cells
    proj_wall = proj_serial / max(1, workers)
    print(f"[profile] cell {CELLS[ci0]}: {cell_secs:.1f}s (8 strengths x {N_REP} reps). "
          f"Projection: ~{proj_serial/60:.1f} min serial, ~{proj_wall/60:.1f} min on "
          f"{workers} workers ({len(CELLS)} cells). 6h limit: "
          f"{'OK' if proj_wall < 6*3600 else 'EXCEEDED — STOP'}", flush=True)
    if profile_only or proj_wall >= 6 * 3600:
        return None

    jobs = [(ci, si, list(range(N_REP)), True)
            for ci in range(len(CELLS)) for si in range(len(STRENGTHS)) if ci != ci0]
    jobs += [(-1, si, list(range(N_REP)), False) for si in range(len(STRENGTHS))]   # machinery
    with Pool(workers, initializer=_init) as pool:
        results = pool.map(run_block, jobs, chunksize=1)
    results += prof

    cells_out = {f"{n}x{r}": {"n_anchors": n, "R": r, "curve": [None] * len(STRENGTHS)}
                 for (n, r) in CELLS}
    machinery = [None] * len(STRENGTHS)
    for ci, si, rows in results:
        surv = float(np.mean([r[0] for r in rows]))
        full = float(np.mean([r[1] for r in rows]))
        pins = float(np.mean([r[2] for r in rows]))
        pwords = float(np.mean([r[3] for r in rows]))
        regen = int(sum(r[4] for r in rows))
        rec = {"strength": STRENGTHS[si], "loto_survival_power": surv, "raw_power": full,
               "mean_pinned_signs": pins, "mean_pinning_words": pwords, "regens": regen}
        if ci < 0:
            machinery[si] = rec
        else:
            n, r = CELLS[ci]
            cells_out[f"{n}x{r}"]["curve"][si] = rec

    m0 = machinery[0]["raw_power"]
    m13 = machinery[-1]["raw_power"]
    invalid = (m0 > 0.14) or (m13 < 0.90)

    quota = None
    for (n, r) in CELLS:                               # spec §5 mechanical rule
        curve = cells_out[f"{n}x{r}"]["curve"]
        if any(c["loto_survival_power"] >= 0.80 for c in curve if c["strength"] <= 3.0):
            quota = {"n_anchors": n, "R": r}
            break

    out = {"spec_commit": SPEC_COMMIT,
           "spec_commit_full": _git("log", "-1", "--format=%H", "--",
                                    "experiments/crossscript_gate/phase2/SWEEP_SPEC.md"),
           "cells": cells_out, "skipped_cells_infeasible": SKIPPED,
           "machinery": {"curve": machinery, "false_fire_s0": m0, "power_s13": m13,
                         "invalid": invalid},
           "quota": quota, "n_rep": N_REP, "n_perm": N_PERM, "h": H,
           "master_seed": MASTER, "profile_cell_secs": round(cell_secs, 1),
           "wall_clock_s": round(time.time() - t0, 1)}
    with open(os.path.join(_HERE, "results", "phase2_quota_sweep.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(f"[sweep] done in {out['wall_clock_s']}s; machinery invalid={invalid}; "
          f"quota={quota}", flush=True)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--profile", action="store_true")
    ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--workers", type=int, default=18)
    a = ap.parse_args()
    if a.selftest:
        selftest()
    elif a.profile:
        sweep(a.workers, profile_only=True)
    elif a.sweep:
        sweep(a.workers)
    else:
        print("choose --selftest / --profile / --sweep")
