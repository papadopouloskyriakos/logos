#!/usr/bin/env python3
"""phase1_power.py — PREREG_FINAL §E checks (run AFTER the §E rules were committed, 15c7032).

1. Secondary-axis (Cypriot-eleven block) power check at the operative bar with N=2.
2. Primary-axis bridging certification: the EXACT stratified design (49-pool, frozen strata
   table, seeded per-replicate stratified draws) at the final N determined by check 1.

Bands, strengths, n_rep, n_perm, master seed: VERBATIM from the frozen §A test (00fb9ea /
33a3fec) — the only §E refinement (operator rider) is that per-replicate detection uses the
FINAL operative decision rule corrected_p = 1-(1-p_raw)^N < 0.05.
"""
from __future__ import annotations

import csv
import json
import os
import sys
import time

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, _ROOT)

from power_precheck import (ALPHA, MASTER_SEED, N_PERM, N_REP, STRENGTHS,  # noqa: E402
                            _git, _nn_preds, _pinned, load_design)
import steele_meissner_2017 as SM                                          # noqa: E402

ELEVEN = ("A", "DA", "I", "NA", "PA", "PO", "RO", "SA", "SE", "TI", "TO")
INELIGIBLE = ("SI", "MU")
H_PRIMARY = 20
ALLOC = {("False", "T1"): 7, ("False", "T2"): 4, ("False", "T3"): 4,
         ("True", "T1"): 0, ("True", "T2"): 3, ("True", "T3"): 2}   # PREREG_FINAL §D table


def alpha_raw(n_axes: int) -> float:
    return 1.0 - (1.0 - ALPHA) ** (1.0 / n_axes)


def load_strata(anchors):
    """Cells over the 49 eligible anchors per the frozen §D spec (rank-rule tertiles)."""
    rows = [r for r in csv.DictReader(open(os.path.join(_HERE, "anchors.csv")))
            if r["robust_anchor"] == "True"]
    byid = {r["sign_id"]: r for r in rows}
    elig = [s for s in anchors if s not in INELIGIBLE]
    esorted = sorted(elig, key=lambda s: (int(byid[s]["la_attestations"]), s))
    tert = {}
    for rank, s in enumerate(esorted):
        tert[s] = "T1" if rank < 17 else ("T2" if rank < 33 else "T3")
    aidx = {s: i for i, s in enumerate(anchors)}
    cells = {}
    for s in elig:
        key = (byid[s]["toponym_covered"], tert[s])
        cells.setdefault(key, []).append(aidx[s])
    for k in cells:
        cells[k].sort(key=lambda i: anchors[i])          # sorted sign_id order within cell
    assert {k: len(v) for k, v in cells.items()} == {
        ("False", "T1"): 16, ("False", "T2"): 9, ("False", "T3"): 10,
        ("True", "T1"): 1, ("True", "T2"): 7, ("True", "T3"): 6}
    return cells


def replicate_split(U, true_val, n, s, seed, forms_idx, split_fn, a_raw):
    """One planted replicate with an arbitrary split function; detection at the operative bar."""
    rng = np.random.default_rng(seed)
    d = U.shape[1]
    Q, _ = np.linalg.qr(rng.normal(size=(d, d)))
    X = s * (U[true_val] @ Q.T) + rng.normal(size=(n, d))
    X = X / np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-12)

    held, train = split_fn(rng)
    held_set = set(held.tolist())
    pins = np.array([_pinned(held_set, int(x), forms_idx) for x in held])

    def _acc_both(assign):
        preds, _ = _nn_preds(X, U, assign, train, held)
        hits = preds == assign[held]
        acc_a = float(np.mean(hits))
        acc_b = float(np.mean(np.where(pins, true_val[held] == assign[held], hits)))
        return acc_a, acc_b

    obs_a, obs_b = _acc_both(true_val)
    null_a = np.empty(N_PERM)
    null_b = np.empty(N_PERM)
    for k in range(N_PERM):
        pi = true_val[rng.permutation(n)]
        null_a[k], null_b[k] = _acc_both(pi)
    p_a = float((1 + np.sum(null_a >= obs_a - 1e-12)) / (N_PERM + 1))
    p_b = float((1 + np.sum(null_b >= obs_b - 1e-12)) / (N_PERM + 1))
    return {"det_a": p_a < a_raw, "det_b": p_b < a_raw, "obs_a": obs_a, "obs_b": obs_b,
            "n_pinned": int(pins.sum())}


def curves(U, true_val, n, forms_idx, split_fn, a_raw, label):
    ca, cb = [], []
    for si, s in enumerate(STRENGTHS):
        rows = [replicate_split(U, true_val, n, s, MASTER_SEED + 10000 * si + r,
                                forms_idx, split_fn, a_raw) for r in range(N_REP)]
        ca.append({"strength": s, "power": float(np.mean([r["det_a"] for r in rows])),
                   "mean_top1": float(np.mean([r["obs_a"] for r in rows]))})
        cb.append({"strength": s, "power": float(np.mean([r["det_b"] for r in rows])),
                   "mean_top1": float(np.mean([r["obs_b"] for r in rows])),
                   "mean_pinned": float(np.mean([r["n_pinned"] for r in rows]))})
        print(f"  [{label}] s={s:>4}: (a) {ca[-1]['power']:.2f} | (b) {cb[-1]['power']:.2f} "
              f"top1={cb[-1]['mean_top1']:.3f} pins={cb[-1]['mean_pinned']:.1f}", flush=True)
    return ca, cb


def band_checks(curve_a, curve_b):
    p0 = next(c["power"] for c in curve_a if c["strength"] == 0.0)
    p13 = next(c["power"] for c in curve_a if c["strength"] == 13.0)
    invalid = (p0 > 0.14) or (p13 < 0.90)
    go = any(c["power"] >= 0.80 for c in curve_b if c["strength"] <= 3.0)
    return {"false_fire_s0_a": p0, "power_s13_a": p13, "machinery_invalid": invalid,
            "go_band_met_b": go}


def main() -> int:
    t0 = time.time()
    anchors, candidates, U, true_val = load_design()
    n = len(anchors)
    aidx = {s: i for i, s in enumerate(anchors)}
    forms_idx = [tuple(aidx[s] for s in t["la_signs"])
                 for t in SM.TOPONYM_EQUATIONS if not t["queried"]]
    cells = load_strata(anchors)

    # ---- §E.1 secondary block axis at N=2 ----
    eleven_idx = np.array(sorted(aidx[s] for s in ELEVEN))
    train_block = np.array(sorted(set(range(n)) - set(eleven_idx.tolist())))

    def split_block(_rng):
        return eleven_idx, train_block

    print(f"[§E.1] secondary block axis: h={len(eleven_idx)} train={len(train_block)} "
          f"bar p_raw<{alpha_raw(2):.5f} (N=2)", flush=True)
    sec_a, sec_b = curves(U, true_val, n, forms_idx, split_block, alpha_raw(2), "block")
    sec_checks = band_checks(sec_a, sec_b)
    secondary_confirmatory = sec_checks["go_band_met_b"] and not sec_checks["machinery_invalid"]
    n_axes = 2 if secondary_confirmatory else 1
    print(f"[§E.1] secondary {'CONFIRMATORY' if secondary_confirmatory else 'DESCRIPTIVE'} "
          f"-> final N={n_axes}", flush=True)

    # ---- §E.2 primary stratified bridging at final N ----
    cell_order = [("False", "T1"), ("False", "T2"), ("False", "T3"),
                  ("True", "T1"), ("True", "T2"), ("True", "T3")]

    def split_strat(rng):
        held = []
        for k in cell_order:
            take = ALLOC[k]
            if take:
                held.extend(rng.choice(cells[k], size=take, replace=False).tolist())
        held = np.array(sorted(held))
        train = np.array(sorted(set(range(n)) - set(held.tolist())))
        return held, train

    print(f"[§E.2] primary stratified bridging: h={H_PRIMARY} bar p_raw<"
          f"{alpha_raw(n_axes):.5f} (N={n_axes})", flush=True)
    pri_a, pri_b = curves(U, true_val, n, forms_idx, split_strat, alpha_raw(n_axes), "strat")
    pri_checks = band_checks(pri_a, pri_b)
    bridging_go = pri_checks["go_band_met_b"] and not pri_checks["machinery_invalid"]

    out = {
        "prereg_rules_commit": _git("log", "-1", "--format=%H", "--",
                                    "experiments/crossscript_gate/PREREG_FINAL.md"),
        "thresholds_commit_frozen": "00fb9eaec78e6de8ba684263fabc5eed6a76f07f",
        "addendum_b_commit": "33a3fecf13b15ba2be7e7bf6c4619d27d5c36072",
        "secondary": {"curve_a": sec_a, "curve_b": sec_b, "checks": sec_checks,
                      "confirmatory": secondary_confirmatory,
                      "detection_bar_p_raw": alpha_raw(2)},
        "final_n_axes": n_axes,
        "primary_bridging": {"curve_a": pri_a, "curve_b": pri_b, "checks": pri_checks,
                             "go_recertified": bridging_go,
                             "detection_bar_p_raw": alpha_raw(n_axes)},
        "wall_clock_s": round(time.time() - t0, 1),
    }
    os.makedirs(os.path.join(_HERE, "results"), exist_ok=True)
    with open(os.path.join(_HERE, "results", "phase1_power.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\nsecondary: {'CONFIRMATORY' if secondary_confirmatory else 'DESCRIPTIVE'}; "
          f"final N={n_axes}; primary bridging GO: {bridging_go}; "
          f"wall={out['wall_clock_s']}s", flush=True)
    return 0 if bridging_go else 1


if __name__ == "__main__":
    raise SystemExit(main())
