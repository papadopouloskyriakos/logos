#!/usr/bin/env python3
"""EPOCH-006 — SEED-EFFICIENT ESTIMATORS for the trigram-frame motif bridge (E003 open door).

Preregistered: epochs/EPOCH-006/prereg.md
plan_hash 23fc9fd26a77923466dc26a3d2c9d5dd84ea003442c9bf1ddfc4cfb20c8fd4df
(frozen 2026-07-08T04:13:52Z, before any corpus run)

Four global-transform estimators (EST_GW landmark-fused entropic GW, EST_SPEC landmark
spectral Procrustes, EST_OT anchor-regularized Sinkhorn on M2 signature cost, EST_CCA ridge
map on eigenmaps) that use b anchors ONLY to fix a transform/coupling over the full
unsupervised MF_A motif graph. KNOWN LB-cog<->Cyp-cog pair, E003 discipline + identical RNG
streams (replicate-paired with E003's M1 cells). NON-CIRCULAR (Art. XI/XII): similarities
from sign identity only; values grade afterward. Everything L2 / KNOWN-script calibration;
no LA data touched. Seed 20260708.
"""
from __future__ import annotations
import json, os, sys, time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e003_seed_poverty as E3
import e002_motif_common as M
import f2_cross_script_bridge as F2

SEED = 20260708
PLAN_HASH = "23fc9fd26a77923466dc26a3d2c9d5dd84ea003442c9bf1ddfc4cfb20c8fd4df"
HOLM_BAR = E3.HOLM_BAR                     # 0.05/12 = 0.0041667
R_CELL = 20
CAMP = "/home/claude-runner/gitlab/n8n/logos-linear-a-frontier-72h/experiments/linear_a_frontier_72h"
OUTDIR = os.path.join(CAMP, "data", "motifs", "seed_efficient")
os.makedirs(OUTDIR, exist_ok=True)

# frozen hyperparameters (prereg)
ALPHA = 0.5
EPS_GW, GW_OUTER, GW_INNER = 0.01, 200, 40
EPS_OT, OT_ITERS = 0.05, 500
K_EMB, LAM = 6, 0.1


# ------------------------------------------------------------------ estimators
def anchor_penalty(ns, nt, anchor):
    L = np.zeros((ns, nt))
    for i, j in anchor:
        L[i, :] = 1.0
    for i, j in anchor:
        L[:, j] = np.maximum(L[:, j], 1.0)
    for i, j in anchor:
        L[i, j] = 0.0
    return L


def _sinkhorn(cost, eps, iters):
    n, m = cost.shape
    p, q = np.ones(n) / n, np.ones(m) / m
    K = np.exp(-cost / eps) + 1e-300
    u, v = np.ones(n), np.ones(m)
    for _ in range(iters):
        u = p / (K @ v + 1e-300)
        v = q / (K.T @ u + 1e-300)
    return u[:, None] * K * v[None, :]


def est_gw(Ss, St, anchor):
    ns, nt = len(Ss), len(St)
    Ds, Dt = 1.0 - Ss, 1.0 - St
    np.fill_diagonal(Ds, 0.0)
    np.fill_diagonal(Dt, 0.0)
    p, q = np.ones(ns) / ns, np.ones(nt) / nt
    L = anchor_penalty(ns, nt, anchor)
    Ds2, Dt2 = Ds ** 2, Dt ** 2
    Cst = (Ds2 @ p)[:, None] + (Dt2 @ q)[None, :]
    T = np.outer(p, q)
    for _ in range(GW_OUTER):
        gw = Cst - 2.0 * (Ds @ T @ Dt)
        gw = gw - gw.min()
        mx = gw.max()
        gwn = gw / mx if mx > 0 else gw
        cost = (1 - ALPHA) * gwn + ALPHA * L
        K = np.exp(-cost / EPS_GW) + 1e-300
        u, v = np.ones(ns), np.ones(nt)
        for _s in range(GW_INNER):
            u = p / (K @ v + 1e-300)
            v = q / (K.T @ u + 1e-300)
        Tn = u[:, None] * K * v[None, :]
        if np.abs(Tn - T).sum() < 1e-9:
            T = Tn
            break
        T = Tn
    return -T


def est_ot(Ss, St, anchor):
    base = F2.method_M2_signature(Ss, St)
    base = base - base.min()
    mx = base.max()
    if mx > 0:
        base = base / mx
    L = anchor_penalty(len(Ss), len(St), anchor)
    return -_sinkhorn((1 - ALPHA) * base + ALPHA * L, EPS_OT, OT_ITERS)


def _embed(Ss, St):
    n = len(Ss)
    k = min(K_EMB, n - 2)
    return F2.eigenmap(Ss, k), F2.eigenmap(St, k), k


def est_spec(Ss, St, anchor):
    Es, Et, k = _embed(Ss, St)
    ss = [i for i, _ in anchor]
    ts = [j for _, j in anchor]
    R = F2.procrustes(Es[ss], Et[ts])
    Esr = Es @ R
    return np.linalg.norm(Et[None, :, :] - Esr[:, None, :], axis=2)


def est_cca(Ss, St, anchor):
    Es, Et, k = _embed(Ss, St)
    ss = [i for i, _ in anchor]
    ts = [j for _, j in anchor]
    A, B = Es[ss], Et[ts]
    W = np.linalg.solve(A.T @ A + LAM * np.eye(k), A.T @ B)
    Esr = Es @ W
    return np.linalg.norm(Et[None, :, :] - Esr[:, None, :], axis=2)


ESTIMATORS = {"EST_GW": est_gw, "EST_SPEC": est_spec, "EST_OT": est_ot, "EST_CCA": est_cca}


# ------------------------------------------------------------------ replicate (E003 body, cost_fn swapped)
def replicate_est(prob, budget, cost_fn, srng, nrng, k_wrong=0):
    n = len(prob["s_signs"])
    gt_idx = prob["gt_idx"]
    if n - budget < E3.MIN_HELDOUT or budget >= n:
        return None
    seed_idx = sorted(srng.sample(range(n), budget))
    anchor = [(i, gt_idx[i]) for i in seed_idx]
    if k_wrong:
        wrong_pos = srng.sample(range(len(anchor)), k_wrong)
        for w in wrong_pos:
            i, true_j = anchor[w]
            choices = [j for j in range(n) if j != true_j]
            anchor[w] = (i, srng.choice(choices))
    cost = cost_fn(prob["Ss"], prob["St"], anchor)
    held = [i for i in range(n) if i not in set(seed_idx)]
    preds = [int(np.argmin(cost[i])) for i in held]
    truths = [gt_idx[i] for i in held]
    obs, p = E3.exact_p(preds, truths, nrng)
    return {"exact_acc": obs / len(held), "exact_count": obs, "p": p, "n_heldout": len(held)}


def loo_est(prob, cost_fn, nrng):
    n = len(prob["s_signs"])
    gt_idx = prob["gt_idx"]
    preds = []
    for i in range(n):
        anchor = [(k, gt_idx[k]) for k in range(n) if k != i]
        cost = cost_fn(prob["Ss"], prob["St"], anchor)
        preds.append(int(np.argmin(cost[i])))
    truths = [gt_idx[i] for i in range(n)]
    obs, p = E3.exact_p(preds, truths, nrng)
    return {"exact_acc": obs / n, "exact_count": obs, "p": p, "n_heldout": n}


# ------------------------------------------------------------------ problems (E003 streams, subset)
def build_problems():
    probs = {}
    lbc, cyp, gtfn_k = E3.known_corpora()
    for f in (0.75, 1.0):
        draws = 1 if f >= 1.0 else E3.N_CORPUS_DRAWS
        for d in range(draws):
            crng, _ = E3.rng_for("KNOWN", "corpus", f, d)
            ss = E3.subsample(lbc, f, crng)
            tt = E3.subsample(cyp, f, crng)
            shuf, _ = E3.rng_for("KNOWN", "shuffle", f, d)
            probs[("KNOWN", f, d)] = E3.build_problem(ss, tt, gtfn_k(ss, tt), shuf)
    a, b, gtfn_c = E3.ctrl_corpora()
    crng, _ = E3.rng_for("CTRL", "corpus", 1.0, 0)
    ss = E3.subsample(a, 1.0, crng)
    tt = E3.subsample(b, 1.0, crng)
    shuf, _ = E3.rng_for("CTRL", "shuffle", 1.0, 0)
    probs[("CTRL", 1.0, 0)] = E3.build_problem(ss, tt, gtfn_c(ss, tt), shuf)
    return probs


def run_cell(probs, est_name, cost_fn, pair, f, b, k_wrong=0, adv=False):
    reps = []
    if f >= 1.0:
        draw_reps = [(0, r) for r in range(R_CELL)]
    else:
        per_draw = R_CELL // E3.N_CORPUS_DRAWS
        draw_reps = [(d, r) for d in range(E3.N_CORPUS_DRAWS) for r in range(per_draw)]
    for d, rep in draw_reps:
        prob = probs[(pair, f, d)]
        if prob is None:
            reps.append(None)
            continue
        if adv:
            srng, _ = E3.rng_for(pair, "adv_seeds", f, d, b, k_wrong, rep)
            _, nrng = E3.rng_for(pair, "adv_null", f, d, b, k_wrong, rep)
        else:
            srng, _ = E3.rng_for(pair, "seeds", f, d, b, rep)
            _, nrng = E3.rng_for(pair, "null", f, d, b, rep)
        reps.append(replicate_est(prob, b, cost_fn, srng, nrng, k_wrong=k_wrong))
    rec = {"estimator": est_name, "pair": pair, "frac": f, "budget": b, "k_wrong": k_wrong}
    rec.update(E3.cell_verdict(reps))
    return rec


TIER = {"SURVIVES_HOLM": 2, "NOMINAL": 1, "FLOOR": 0, "NO_POWER": 0}


def run():
    t0 = time.time()
    print("== PC0: harness identity gate (E003 positive_control) ==", flush=True)
    pc0 = E3.positive_control()
    json.dump(pc0, open(os.path.join(OUTDIR, "E006_pc0.json"), "w"), indent=1)
    print("PC0 gate:", pc0["gate"], flush=True)
    if pc0["gate"] != "PASS":
        print("DETECTOR_BROKEN — aborting per prereg")
        return None

    probs = build_problems()
    known_full = probs[("KNOWN", 1.0, 0)]

    # ---- PC1: per-estimator LOO expressiveness at b=46 ----
    pc1 = {}
    for name, fn in ESTIMATORS.items():
        _, nrng = E3.rng_for("KNOWN", "e006_pc1", name)
        r = loo_est(known_full, fn, nrng)
        r["pass"] = bool(r["exact_count"] >= 7 and r["p"] <= HOLM_BAR)
        pc1[name] = r
        print(f"PC1 {name}: exact {r['exact_count']}/{r['n_heldout']} p={r['p']:.4f} "
              f"-> {'PASS' if r['pass'] else 'FAIL'}", flush=True)
    json.dump(pc1, open(os.path.join(OUTDIR, "E006_pc1.json"), "w"), indent=1, default=float)
    # declared reproduction check: EST_SPEC LOO must equal E002 M4 = 4/47
    if pc1["EST_SPEC"]["exact_count"] != 4:
        print("WARNING: EST_SPEC LOO != 4/47 (E002 M4) — implementation drift; ABORT per prereg")
        return None

    # ---- cells ----
    cells = []
    for name, fn in ESTIMATORS.items():
        specs = ([("KNOWN", 0.75, 5, 0, False)] +
                 [("KNOWN", 1.0, b, 0, False) for b in (3, 5, 7, 10)] +
                 [("CTRL", 1.0, 5, 0, False),
                  ("KNOWN", 1.0, 5, 1, True),
                  ("KNOWN", 1.0, 5, 5, True)])
        for pair, f, b, kw, adv in specs:
            rec = run_cell(probs, name, fn, pair, f, b, k_wrong=kw, adv=adv)
            cells.append(rec)
            print(f"{name} {pair} f={f} b={b} kw={kw}: {rec['cell_verdict']}"
                  f" acc={rec.get('exact_acc_mean', float('nan')):.3f}"
                  f" med_p={rec.get('median_p', float('nan')):.4f}"
                  f"  [{time.time()-t0:.0f}s]", flush=True)
            json.dump(cells, open(os.path.join(OUTDIR, "E006_cells_partial.json"), "w"),
                      indent=1, default=float)

    def cv(est, pair, f, b, kw=0):
        return next(c for c in cells if c["estimator"] == est and c["pair"] == pair
                    and c["frac"] == f and c["budget"] == b and c["k_wrong"] == kw)

    # ---- mechanical verdicts ----
    verdicts, robustness = {}, {}
    for name in ESTIMATORS:
        neg = cv(name, "KNOWN", 1.0, 5, kw=5)
        vc = cv(name, "KNOWN", 0.75, 5)
        clean5 = cv(name, "KNOWN", 1.0, 5)
        adv1 = cv(name, "KNOWN", 1.0, 5, kw=1)
        anomaly = False
        if neg["cell_verdict"] != "FLOOR":
            v = "ESTIMATOR_DETECTOR_BROKEN"
        elif not pc1[name]["pass"]:
            v = "SEED_EFFICIENT_NOT_ACHIEVED (PC1_FAIL)"
            anomaly = TIER.get(vc["cell_verdict"], 0) >= 1
        elif vc["cell_verdict"] == "SURVIVES_HOLM":
            v = "SEED_EFFICIENT_ACHIEVED"
        elif vc["cell_verdict"] == "NOMINAL":
            v = "SEED_EFFICIENT_PARTIAL_NOMINAL"
        else:
            v = "SEED_EFFICIENT_NOT_ACHIEVED"
        verdicts[name] = {"verdict": v, "anomaly_flag": bool(anomaly),
                          "verdict_cell": vc["cell_verdict"],
                          "verdict_cell_acc": vc.get("exact_acc_mean"),
                          "verdict_cell_median_p": vc.get("median_p"),
                          "pc1_pass": pc1[name]["pass"], "neg": neg["cell_verdict"]}
        ct, at = TIER.get(clean5["cell_verdict"], 0), TIER.get(adv1["cell_verdict"], 0)
        robustness[name] = {
            "clean_b5_f1": clean5["cell_verdict"], "adv1_b5_f1": adv1["cell_verdict"],
            "delta_acc": (adv1.get("exact_acc_mean", 0.0) - clean5.get("exact_acc_mean", 0.0)),
            "flag": ("UNINFORMATIVE" if ct == 0 else "ROBUST" if at >= ct else "FRAGILE")}

    if any(d["verdict"] == "SEED_EFFICIENT_ACHIEVED" for d in verdicts.values()):
        epoch_verdict = "NEW_SYMMETRY_BREAKING_CHANNEL_CANDIDATE"
    elif any(d["verdict"] == "SEED_EFFICIENT_PARTIAL_NOMINAL" for d in verdicts.values()):
        epoch_verdict = "SEED_EFFICIENCY_PARTIAL_ONLY"
    else:
        epoch_verdict = "SEED_EFFICIENCY_NOT_ACHIEVED"

    out = {"plan_hash": PLAN_HASH, "seed": SEED, "pc0": pc0, "pc1": pc1, "cells": cells,
           "estimator_verdicts": verdicts, "wrong_anchor_robustness": robustness,
           "epoch_verdict": epoch_verdict,
           "e003_m1_reference": {"verdict_cell_b5_f075": {"acc": 0.034, "median_p": 0.599,
                                                          "verdict": "FLOOR"},
                                 "b5_f1": {"acc": 0.039, "median_p": 0.417, "verdict": "FLOOR"},
                                 "required_hit_rate_holm_b5": 0.119,
                                 "available_loo_rate": 0.149},
           "runtime_s": round(time.time() - t0, 1)}
    json.dump(out, open(os.path.join(OUTDIR, "E006_result.json"), "w"), indent=1, default=float)
    print("\n== verdicts ==")
    for name, d in verdicts.items():
        print(f"{name}: {d['verdict']} (verdict cell {d['verdict_cell']}, "
              f"acc {d['verdict_cell_acc']}, med_p {d['verdict_cell_median_p']}; "
              f"robustness {robustness[name]['flag']})")
    print("EPOCH VERDICT:", epoch_verdict)
    return out


if __name__ == "__main__":
    run()
