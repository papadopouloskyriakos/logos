#!/usr/bin/env python3
"""EPOCH-010 — CHANNEL-CAPACITY BOUND + ENSEMBLE + HUB ANCHORS (close/reopen the E003/E006 door).

Preregistered: epochs/EPOCH-010/prereg.md
plan_hash 0380e6c327b72fa1a0e65d9d95dff93572de95b783fb70e2c4de9783daa878fe
(frozen 2026-07-08T04:47:58Z, before any corpus run)

Part 1  estimator-free capacity probes at b=5 (oracle ridge/CCA with deliberate GT leakage,
        best-of-battery selection envelope, PICK3 union, Fano report-only), graded against the
        mechanical required Holm rate c_req/H per replicate.
Part 2  ensemble fusion (fused-rank, product-of-experts) of {M1, EST_GW, EST_OT}; error-set
        overlap reported first.
Part 3  hub-stratified 5-seed draws (top-quartile support / motif-graph centrality) vs uniform.

KNOWN LB-cog<->Cyp-cog pair (+ CTRL LB-DAMOS split-half), E003 discipline + identical RNG
streams for everything uniform-seeded. NON-CIRCULAR (Art. XI/XII): similarities from sign
identity only; values grade afterward; oracle leakage is a declared BOUND, conservative for
DOOR_CLOSED, unable to REOPEN. L2 / KNOWN-script calibration only; no LA data. Seed 20260708.
"""
from __future__ import annotations
import json, math, os, sys, time

import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.stats import rankdata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e003_seed_poverty as E3
import e002_motif_common as M  # noqa: F401  (path side-effect for f2 import)
import e006_seed_efficient as E6
import f2_cross_script_bridge as F2  # noqa: F401

SEED = 20260708
PLAN_HASH = "0380e6c327b72fa1a0e65d9d95dff93572de95b783fb70e2c4de9783daa878fe"
HOLM_BAR = E3.HOLM_BAR            # 0.05/12 = 0.0041667
R_CELL = 20
N_PERM = 1000
B = 5
RIDGE_LAM = 0.01
CCA_REG = 1e-6
RHO_CLIP = 0.999
CAMP = "/home/claude-runner/gitlab/n8n/logos-linear-a-frontier-72h/experiments/linear_a_frontier_72h"
OUTDIR = os.path.join(CAMP, "data", "motifs", "capacity")
os.makedirs(OUTDIR, exist_ok=True)


# ------------------------------------------------------------------ null machinery
def exact_p_full(preds, truths, nrng, n_perm=N_PERM):
    """E003 exact_p + c_req: smallest c with #(null>=c) <= 3  (perm-p <= 0.0041667)."""
    preds = np.asarray(preds)
    truths = np.asarray(truths)
    obs = int((preds == truths).sum())
    counts = np.array([int((preds == nrng.permutation(truths)).sum())
                       for _ in range(n_perm)])
    p = (int((counts >= obs).sum()) + 1) / (n_perm + 1)
    c = 1
    while int((counts >= c).sum()) > 3:
        c += 1
    return obs, p, c


# ------------------------------------------------------------------ problems (E003 streams + support maps)
def build_problems():
    """Rebuild E003 problems with identical streams; attach per-draw support maps for hub pools."""
    probs = {}
    lbc, cyp, gtfn_k = E3.known_corpora()
    for f in (0.75, 1.0):
        draws = 1 if f >= 1.0 else E3.N_CORPUS_DRAWS
        for d in range(draws):
            crng, _ = E3.rng_for("KNOWN", "corpus", f, d)
            ss = E3.subsample(lbc, f, crng)
            tt = E3.subsample(cyp, f, crng)
            shuf, _ = E3.rng_for("KNOWN", "shuffle", f, d)
            prob = E3.build_problem(ss, tt, gtfn_k(ss, tt), shuf)
            if prob is not None:
                sup_s, sup_t = E3.C.sign_support(ss), E3.C.sign_support(tt)
                prob["pair_minsup"] = [min(sup_s.get(a, 0),
                                           sup_t.get(prob["t_signs"][prob["gt_idx"][i]], 0))
                                       for i, a in enumerate(prob["s_signs"])]
            probs[("KNOWN", f, d)] = prob
    a, b, gtfn_c = E3.ctrl_corpora()
    crng, _ = E3.rng_for("CTRL", "corpus", 1.0, 0)
    ss = E3.subsample(a, 1.0, crng)
    tt = E3.subsample(b, 1.0, crng)
    shuf, _ = E3.rng_for("CTRL", "shuffle", 1.0, 0)
    probs[("CTRL", 1.0, 0)] = E3.build_problem(ss, tt, gtfn_c(ss, tt), shuf)
    return probs


def draw_reps_for(f):
    if f >= 1.0:
        return [(0, r) for r in range(R_CELL)]
    per_draw = R_CELL // E3.N_CORPUS_DRAWS
    return [(d, r) for d in range(E3.N_CORPUS_DRAWS) for r in range(per_draw)]


def uniform_anchor(prob, srng, k_wrong=0):
    """E003 replicate seed-draw logic, byte-identical stream usage."""
    n = len(prob["s_signs"])
    gt_idx = prob["gt_idx"]
    seed_idx = sorted(srng.sample(range(n), B))
    anchor = [(i, gt_idx[i]) for i in seed_idx]
    if k_wrong:
        wrong_pos = srng.sample(range(len(anchor)), k_wrong)
        for w in wrong_pos:
            i, true_j = anchor[w]
            choices = [j for j in range(n) if j != true_j]
            anchor[w] = (i, srng.choice(choices))
    return seed_idx, anchor


# ------------------------------------------------------------------ capacity probes
def _zcols(A):
    return (A - A.mean(0)) / (A.std(0) + 1e-9)


def _acc(preds, truths):
    return float(np.mean([p == t for p, t in zip(preds, truths)]))


def _argmin_and_hungarian(cost, held, gt_idx):
    truths = [gt_idx[i] for i in held]
    preds_a = [int(np.argmin(cost[hi])) for hi in range(len(held))]
    ri, ci = linear_sum_assignment(cost)
    hung = {int(r): int(c) for r, c in zip(ri, ci)}
    preds_h = [hung.get(hi, preds_a[hi]) for hi in range(len(held))]
    return preds_a, preds_h, truths


def cap_oracle_lin(prob, seed_idx, gt_idx_use):
    Ss, St = prob["Ss"], prob["St"]
    n = len(Ss)
    s_seed = seed_idx
    t_seed = [gt_idx_use[i] for i in seed_idx]
    X = _zcols(Ss[:, s_seed])
    Y = _zcols(St[:, t_seed])
    Ytrue = Y[[gt_idx_use[i] for i in range(n)]]
    W = np.linalg.solve(X.T @ X + RIDGE_LAM * n * np.eye(X.shape[1]), X.T @ Ytrue)
    held = [i for i in range(n) if i not in set(seed_idx)]
    proj = X[held] @ W
    cost = np.linalg.norm(proj[:, None, :] - Y[None, :, :], axis=2)
    return cost, held


def cap_oracle_cca(prob, seed_idx, gt_idx_use):
    Ss, St = prob["Ss"], prob["St"]
    n = len(Ss)
    t_seed = [gt_idx_use[i] for i in seed_idx]
    X = Ss[:, seed_idx] - Ss[:, seed_idx].mean(0)
    Yc = St[:, t_seed]
    Ytrue = Yc[[gt_idx_use[i] for i in range(n)]]
    Ym = Ytrue.mean(0)
    Yt = Ytrue - Ym
    k = X.shape[1]
    Cxx = X.T @ X / n + CCA_REG * np.eye(k)
    Cyy = Yt.T @ Yt / n + CCA_REG * np.eye(k)
    Cxy = X.T @ Yt / n
    def invsqrt(C):
        w, V = np.linalg.eigh(C)
        w = np.maximum(w, 1e-12)
        return V @ np.diag(w ** -0.5) @ V.T
    Sx, Sy = invsqrt(Cxx), invsqrt(Cyy)
    Mm = Sx @ Cxy @ Sy
    U, sv, Vt = np.linalg.svd(Mm)
    rho = np.clip(sv, 0.0, RHO_CLIP)
    Wx, Wy = Sx @ U, Sy @ Vt.T
    held = [i for i in range(n) if i not in set(seed_idx)]
    Px = (X[held] @ Wx) * rho
    Py = ((Yc - Ym) @ Wy) * rho
    cost = np.linalg.norm(Px[:, None, :] - Py[None, :, :], axis=2)
    return cost, held, rho


def battery_costs(prob, seed_idx, gt_idx_use):
    Ss, St = prob["Ss"], prob["St"]
    n = len(Ss)
    t_seed = [gt_idx_use[i] for i in seed_idx]
    X = Ss[:, seed_idx]
    Y = St[:, t_seed]
    held = [i for i in range(n) if i not in set(seed_idx)]
    Xh = X[held]
    out = {}
    out["raw_l2"] = np.linalg.norm(Xh[:, None, :] - Y[None, :, :], axis=2)
    Xn = Xh / (np.linalg.norm(Xh, axis=1, keepdims=True) + 1e-9)
    Yn = Y / (np.linalg.norm(Y, axis=1, keepdims=True) + 1e-9)
    out["rownorm_l2"] = np.linalg.norm(Xn[:, None, :] - Yn[None, :, :], axis=2)
    out["cosine"] = 1.0 - Xn @ Yn.T
    Xz, Yz = _zcols(Xh), _zcols(Y)
    out["colz_l2"] = np.linalg.norm(Xz[:, None, :] - Yz[None, :, :], axis=2)
    Xr = np.apply_along_axis(rankdata, 1, Xh)
    Yr = np.apply_along_axis(rankdata, 1, Y)
    Xr = Xr - Xr.mean(1, keepdims=True)
    Yr = Yr - Yr.mean(1, keepdims=True)
    Xr = Xr / (np.linalg.norm(Xr, axis=1, keepdims=True) + 1e-9)
    Yr = Yr / (np.linalg.norm(Yr, axis=1, keepdims=True) + 1e-9)
    out["spearman"] = 1.0 - Xr @ Yr.T
    return out, held


def gauss_cca_mi_bound(prob, seed_idx, gt_idx_use):
    """Report-only Fano: Gaussian-CCA MI between HELD-OUT X rows and their true Y rows."""
    Ss, St = prob["Ss"], prob["St"]
    n = len(Ss)
    held = [i for i in range(n) if i not in set(seed_idx)]
    t_seed = [gt_idx_use[i] for i in seed_idx]
    X = Ss[np.ix_(held, seed_idx)]
    Y = St[:, t_seed][[gt_idx_use[i] for i in held]]
    X = X - X.mean(0)
    Y = Y - Y.mean(0)
    m = len(held)
    k = X.shape[1]
    Cxx = X.T @ X / m + CCA_REG * np.eye(k)
    Cyy = Y.T @ Y / m + CCA_REG * np.eye(k)
    Cxy = X.T @ Y / m
    def invsqrt(C):
        w, V = np.linalg.eigh(C)
        w = np.maximum(w, 1e-12)
        return V @ np.diag(w ** -0.5) @ V.T
    sv = np.linalg.svd(invsqrt(Cxx) @ Cxy @ invsqrt(Cyy), compute_uv=False)
    rho = np.clip(sv, 0.0, RHO_CLIP)
    I = float(-0.5 * np.sum(np.log(1.0 - rho ** 2)))
    bound = min(1.0, (I + math.log(2)) / math.log(m))
    return I, bound


def capacity_replicate(prob, seed_idx, gt_idx_use, f, d, rep, base_costs=None):
    """All probes on one replicate. Returns dict probe -> {acc, c_req, H, margin}."""
    n = len(prob["s_signs"])
    res = {}

    def grade(tag, preds_by_rule, held):
        """preds_by_rule: list of prediction lists; acc = max over rules (envelope);
        c_req from the FIRST rule's prediction structure (frozen: argmin of first)."""
        truths = [gt_idx_use[i] for i in held]
        accs = [_acc(p, truths) for p in preds_by_rule]
        best = int(np.argmax(accs))
        _, nrng = E3.rng_for("cap_null", tag, f, d, rep)
        _, _, c_req = exact_p_full(preds_by_rule[best], truths, nrng)
        H = len(held)
        acc = max(accs)
        res[tag] = {"acc": acc, "H": H, "c_req": c_req,
                    "required": c_req / H, "margin": acc - c_req / H}

    cost, held = cap_oracle_lin(prob, seed_idx, gt_idx_use)
    pa, ph, _ = _argmin_and_hungarian(cost, held, gt_idx_use)
    grade("CAP_ORACLE_LIN", [pa, ph], held)

    cost, held, _rho = cap_oracle_cca(prob, seed_idx, gt_idx_use)
    pa, ph, _ = _argmin_and_hungarian(cost, held, gt_idx_use)
    grade("CAP_ORACLE_CCA", [pa, ph], held)

    costs, held = battery_costs(prob, seed_idx, gt_idx_use)
    preds = []
    for name, cst in costs.items():
        pa, ph, _ = _argmin_and_hungarian(cst, held, gt_idx_use)
        preds.extend([pa, ph])
    grade("CAP_BEST_BATTERY", preds, held)

    if base_costs is not None:  # PICK3 union from {M1, EST_GW, EST_OT}
        truths = [gt_idx_use[i] for i in held]
        per = []
        for cst in base_costs:
            per.append([int(np.argmin(cst[i])) for i in held])
        union_ok = [any(per[m][hi] == truths[hi] for m in range(len(per)))
                    for hi in range(len(held))]
        # grade against c_req of the best single method's prediction vector
        accs = [_acc(p, truths) for p in per]
        best = int(np.argmax(accs))
        _, nrng = E3.rng_for("cap_null", "CAP_ORACLE_PICK3", f, d, rep)
        _, _, c_req = exact_p_full(per[best], truths, nrng)
        H = len(held)
        acc = float(np.mean(union_ok))
        res["CAP_ORACLE_PICK3"] = {"acc": acc, "H": H, "c_req": c_req,
                                   "required": c_req / H, "margin": acc - c_req / H}

    I, bound = gauss_cca_mi_bound(prob, seed_idx, gt_idx_use)
    res["CAP_FANO"] = {"mi_nats": I, "bound": bound,
                       "required": res["CAP_ORACLE_LIN"]["required"],
                       "margin": bound - res["CAP_ORACLE_LIN"]["required"]}
    return res


def summarize_probe(reps, tag):
    margins = [r[tag]["margin"] for r in reps if tag in r]
    accs = [r[tag].get("acc", r[tag].get("bound")) for r in reps if tag in r]
    reqs = [r[tag]["required"] for r in reps if tag in r]
    return {"probe": tag, "n_reps": len(margins),
            "acc_mean": float(np.mean(accs)), "acc_median": float(np.median(accs)),
            "required_median": float(np.median(reqs)),
            "margin_median": float(np.median(margins)),
            "exceeds": bool(np.median(margins) >= 0)}


# ------------------------------------------------------------------ base estimators + fusion
def base_cost_matrices(prob, anchor):
    return [E3.m1_cost(prob["Ss"], prob["St"], anchor),
            E6.est_gw(prob["Ss"], prob["St"], anchor),
            E6.est_ot(prob["Ss"], prob["St"], anchor)]


def fuse_rank(costs, held):
    R = [np.apply_along_axis(rankdata, 1, c[held]) for c in costs]
    fused = np.mean(R, axis=0)
    return [int(np.argmin(fused[hi])) for hi in range(len(held))]


def fuse_poe(costs, held):
    Ps = []
    for c in costs:
        tau = float(np.std(c)) + 1e-12
        z = -c[held] / tau
        z = z - z.max(1, keepdims=True)
        P = np.exp(z)
        P = P / P.sum(1, keepdims=True)
        Ps.append(P)
    fused = np.prod(Ps, axis=0)
    return [int(np.argmax(fused[hi])) for hi in range(len(held))]


def error_overlap(costs, held, truths):
    per_preds = [[int(np.argmin(c[i])) for i in held] for c in costs]
    errsets = [set(hi for hi in range(len(held)) if per_preds[m][hi] != truths[hi])
               for m in range(3)]
    jac = {}
    names = ["M1", "EST_GW", "EST_OT"]
    for a in range(3):
        for b in range(a + 1, 3):
            u = errsets[a] | errsets[b]
            jac[f"{names[a]}|{names[b]}"] = len(errsets[a] & errsets[b]) / len(u) if u else 1.0
    all3 = errsets[0] & errsets[1] & errsets[2]
    anyerr = errsets[0] | errsets[1] | errsets[2]
    accs = {names[m]: _acc(per_preds[m], truths) for m in range(3)}
    union_acc = 1.0 - len(anyerr) / len(held) + (len(anyerr) - len(anyerr)) * 0  # PICK3 acc
    union_acc = float(np.mean([any(per_preds[m][hi] == truths[hi] for m in range(3))
                               for hi in range(len(held))]))
    return {"pairwise_jaccard": jac, "three_way_error_frac": len(all3) / len(held),
            "per_method_acc": accs, "pick3_union_acc": union_acc}, per_preds


# ------------------------------------------------------------------ cells
def run_ensemble_cell(probs, f):
    reps_rank, reps_poe, overlaps, cap_reps = [], [], [], []
    for d, rep in draw_reps_for(f):
        prob = probs[("KNOWN", f, d)]
        if prob is None:
            reps_rank.append(None)
            reps_poe.append(None)
            continue
        srng, _ = E3.rng_for("KNOWN", "seeds", f, d, B, rep)   # E003-paired stream
        seed_idx, anchor = uniform_anchor(prob, srng)
        held = [i for i in range(len(prob["s_signs"])) if i not in set(seed_idx)]
        truths = [prob["gt_idx"][i] for i in held]
        costs = base_cost_matrices(prob, anchor)
        ov, _ = error_overlap(costs, held, truths)
        overlaps.append(ov)
        for name, fusefn, store in (("ENS_RANK", fuse_rank, reps_rank),
                                    ("ENS_POE", fuse_poe, reps_poe)):
            preds = fusefn(costs, held)
            _, nrng = E3.rng_for("ens_null", name, f, d, rep)
            obs, p, _c = exact_p_full(preds, truths, nrng)
            store.append({"exact_acc": obs / len(held), "exact_count": obs,
                          "p": p, "n_heldout": len(held)})
        # capacity probes on the SAME replicate (uniform-seed capacity cells)
        cap_reps.append(capacity_replicate(prob, seed_idx, prob["gt_idx"], f, d, rep,
                                           base_costs=costs))
    cells = {}
    for name, store in (("ENS_RANK", reps_rank), ("ENS_POE", reps_poe)):
        rec = {"cell": name, "pair": "KNOWN", "frac": f, "budget": B}
        rec.update(E3.cell_verdict(store))
        cells[name] = rec
    jkeys = overlaps[0]["pairwise_jaccard"].keys() if overlaps else []
    ovsum = {"mean_pairwise_jaccard": {k: float(np.mean([o["pairwise_jaccard"][k]
                                                          for o in overlaps])) for k in jkeys},
             "mean_per_method_acc": {k: float(np.mean([o["per_method_acc"][k]
                                                       for o in overlaps]))
                                     for k in (overlaps[0]["per_method_acc"] if overlaps else [])},
             "mean_pick3_union_acc": float(np.mean([o["pick3_union_acc"] for o in overlaps])),
             "mean_three_way_error_frac": float(np.mean([o["three_way_error_frac"]
                                                         for o in overlaps]))}
    return cells, ovsum, cap_reps


def run_neg_ens(probs):
    prob = probs[("KNOWN", 1.0, 0)]
    reps = {"ENS_RANK": [], "ENS_POE": []}
    for rep in range(R_CELL):
        srng, _ = E3.rng_for("ens_adv_seeds", rep)
        seed_idx, anchor = uniform_anchor(prob, srng, k_wrong=5)
        held = [i for i in range(len(prob["s_signs"])) if i not in set(seed_idx)]
        truths = [prob["gt_idx"][i] for i in held]
        costs = base_cost_matrices(prob, anchor)
        for name, fusefn in (("ENS_RANK", fuse_rank), ("ENS_POE", fuse_poe)):
            preds = fusefn(costs, held)
            _, nrng = E3.rng_for("ens_adv_null", name, rep)
            obs, p, _c = exact_p_full(preds, truths, nrng)
            reps[name].append({"exact_acc": obs / len(held), "exact_count": obs,
                               "p": p, "n_heldout": len(held)})
    out = {}
    for name in reps:
        rec = {"cell": f"NEG_{name}", "k_wrong": 5}
        rec.update(E3.cell_verdict(reps[name]))
        out[name] = rec
    return out


def hub_pool(prob, strat):
    n = len(prob["s_signs"])
    q = math.ceil(n / 4)
    if strat == "SUP":
        key = prob["pair_minsup"]
    else:  # CEN
        Ss = prob["Ss"]
        key = (Ss.sum(1) - np.diag(Ss)).tolist()
    order = sorted(range(n), key=lambda i: -key[i])
    return order[:q]


def run_hub_cell(probs, strat, est_name, f, k_wrong=0, adv=False):
    est_fn = {"M1": E3.m1_cost, "EST_OT": E6.est_ot}[est_name]
    reps = []
    for d, rep in draw_reps_for(f):
        prob = probs[("KNOWN", f, d)]
        if prob is None:
            reps.append(None)
            continue
        pool = hub_pool(prob, strat)
        skey = ("hub_adv_seeds", strat, f, d, rep) if adv else ("hub_seeds", strat, f, d, rep)
        srng, _ = E3.rng_for(*skey)
        n = len(prob["s_signs"])
        gt_idx = prob["gt_idx"]
        if n - B < E3.MIN_HELDOUT:
            reps.append(None)
            continue
        seed_idx = sorted(srng.sample(pool, B))
        anchor = [(i, gt_idx[i]) for i in seed_idx]
        if k_wrong:
            wrong_pos = srng.sample(range(len(anchor)), k_wrong)
            for w in wrong_pos:
                i, true_j = anchor[w]
                choices = [j for j in range(n) if j != true_j]
                anchor[w] = (i, srng.choice(choices))
        cost = est_fn(prob["Ss"], prob["St"], anchor)
        held = [i for i in range(n) if i not in set(seed_idx)]
        preds = [int(np.argmin(cost[i])) for i in held]
        truths = [gt_idx[i] for i in held]
        nkey = (("hub_adv_null", strat, est_name, f, d, rep) if adv
                else ("hub_null", strat, est_name, f, d, rep))
        _, nrng = E3.rng_for(*nkey)
        obs, p, _c = exact_p_full(preds, truths, nrng)
        reps.append({"exact_acc": obs / len(held), "exact_count": obs,
                     "p": p, "n_heldout": len(held)})
    rec = {"cell": f"HUB_{strat}", "estimator": est_name, "pair": "KNOWN",
           "frac": f, "budget": B, "k_wrong": k_wrong}
    rec.update(E3.cell_verdict(reps))
    return rec


def run_capacity_control(probs, which):
    """which='PC' -> CTRL clean; which='NEG' -> KNOWN f=1.0 scrambled GT."""
    reps = []
    if which == "PC":
        prob = probs[("CTRL", 1.0, 0)]
        f, d = 1.0, 0
        for rep in range(R_CELL):
            srng, _ = E3.rng_for("CTRL", "seeds", f, d, B, rep)     # E003-paired
            seed_idx, anchor = uniform_anchor(prob, srng)
            costs = base_cost_matrices(prob, anchor)
            reps.append(capacity_replicate(prob, seed_idx, prob["gt_idx"],
                                           "CTRL", d, rep, base_costs=costs))
    else:
        prob = probs[("KNOWN", 1.0, 0)]
        f, d = 1.0, 0
        n = len(prob["s_signs"])
        for rep in range(R_CELL):
            srng, _ = E3.rng_for("KNOWN", "seeds", f, d, B, rep)
            seed_idx = sorted(srng.sample(range(n), B))
            scr, _ = E3.rng_for("cap_scramble", f, d, rep)
            perm = list(range(n))
            scr.shuffle(perm)
            gt_scr = {i: perm[prob["gt_idx"][i]] for i in range(n)}
            anchor = [(i, gt_scr[i]) for i in seed_idx]
            costs = base_cost_matrices(prob, anchor)
            reps.append(capacity_replicate(prob, seed_idx, gt_scr,
                                           "NEGCAP", d, rep, base_costs=costs))
    return reps


PROBES = ["CAP_ORACLE_LIN", "CAP_ORACLE_CCA", "CAP_BEST_BATTERY", "CAP_ORACLE_PICK3"]
TIER = {"SURVIVES_HOLM": 2, "NOMINAL": 1, "FLOOR": 0, "NO_POWER": 0}


def run():
    t0 = time.time()
    print("== PC0: harness identity gate ==", flush=True)
    pc0 = E3.positive_control()
    json.dump(pc0, open(os.path.join(OUTDIR, "E010_pc0.json"), "w"), indent=1)
    print("PC0 gate:", pc0["gate"], flush=True)
    if pc0["gate"] != "PASS":
        print("DETECTOR_BROKEN — aborting per prereg")
        return None

    probs = build_problems()

    # ---- PC_CAP (CTRL) ----
    print("== PC_CAP: capacity probes on CTRL identity (b=5, f=1.0) ==", flush=True)
    pc_reps = run_capacity_control(probs, "PC")
    pc_cap = {t: summarize_probe(pc_reps, t) for t in PROBES + ["CAP_FANO"]}
    pc_cap_pass = pc_cap["CAP_ORACLE_LIN"]["exceeds"] and pc_cap["CAP_BEST_BATTERY"]["exceeds"]
    for t in PROBES:
        print(f"PC_CAP {t}: acc_med {pc_cap[t]['acc_median']:.3f} req_med "
              f"{pc_cap[t]['required_median']:.3f} exceeds={pc_cap[t]['exceeds']}", flush=True)
    print("PC_CAP gate:", "PASS" if pc_cap_pass else "NO_POWER", flush=True)

    # ---- NEG_CAP (scrambled GT) ----
    print("== NEG_CAP: capacity probes on scrambled GT (b=5, f=1.0) ==", flush=True)
    neg_reps = run_capacity_control(probs, "NEG")
    neg_cap = {t: summarize_probe(neg_reps, t) for t in PROBES + ["CAP_FANO"]}
    overfit_broken = [t for t in PROBES if neg_cap[t]["exceeds"]]
    for t in PROBES:
        print(f"NEG_CAP {t}: acc_med {neg_cap[t]['acc_median']:.3f} margin_med "
              f"{neg_cap[t]['margin_median']:+.3f} "
              f"{'OVERFIT_BROKEN' if t in overfit_broken else 'ok'}", flush=True)
    valid_probes = [t for t in PROBES if t not in overfit_broken]

    # ---- ensemble + capacity clean cells (KNOWN, both fractions) ----
    ens_cells, overlaps, cap_summ = {}, {}, {}
    for f in (0.75, 1.0):
        print(f"== ENSEMBLE + CAPACITY: KNOWN b=5 f={f} ==", flush=True)
        cells, ovsum, cap_reps = run_ensemble_cell(probs, f)
        ens_cells[f] = cells
        overlaps[f] = ovsum
        cap_summ[f] = {t: summarize_probe(cap_reps, t) for t in PROBES + ["CAP_FANO"]}
        for name, rec in cells.items():
            print(f"{name} f={f}: {rec['cell_verdict']} acc={rec.get('exact_acc_mean', float('nan')):.3f}"
                  f" med_p={rec.get('median_p', float('nan')):.4f}", flush=True)
        for t in PROBES + ["CAP_FANO"]:
            s = cap_summ[f][t]
            print(f"  {t}: acc_med {s['acc_median']:.3f} req_med {s['required_median']:.3f} "
                  f"margin_med {s['margin_median']:+.3f} exceeds={s['exceeds']}", flush=True)
        print(f"  overlap: {overlaps[f]['mean_pairwise_jaccard']} pick3 "
              f"{overlaps[f]['mean_pick3_union_acc']:.3f}  [{time.time()-t0:.0f}s]", flush=True)

    # ---- NEG_ENS ----
    neg_ens = run_neg_ens(probs)
    ens_family_ok = all(neg_ens[n]["cell_verdict"] == "FLOOR" for n in neg_ens)
    print("NEG_ENS:", {n: neg_ens[n]["cell_verdict"] for n in neg_ens},
          "family_ok" if ens_family_ok else "ESTIMATOR_DETECTOR_BROKEN", flush=True)

    # ---- hub cells ----
    hub_cells = []
    for strat in ("SUP", "CEN"):
        for est in ("M1", "EST_OT"):
            for f in (0.75, 1.0):
                rec = run_hub_cell(probs, strat, est, f)
                hub_cells.append(rec)
                print(f"HUB_{strat} {est} f={f}: {rec['cell_verdict']} "
                      f"acc={rec.get('exact_acc_mean', float('nan')):.3f} "
                      f"med_p={rec.get('median_p', float('nan')):.4f}  [{time.time()-t0:.0f}s]",
                      flush=True)
    neg_hub = run_hub_cell(probs, "SUP", "M1", 1.0, k_wrong=5, adv=True)
    hub_family_ok = neg_hub["cell_verdict"] == "FLOOR"
    print("NEG_HUB:", neg_hub["cell_verdict"],
          "family_ok" if hub_family_ok else "ESTIMATOR_DETECTOR_BROKEN", flush=True)

    # ---- mechanical verdict ----
    claim_cells = []
    for f in (0.75, 1.0):
        for name in ("ENS_RANK", "ENS_POE"):
            claim_cells.append(("ensemble", ens_cells[f][name], ens_family_ok))
    for rec in hub_cells:
        claim_cells.append(("hub", rec, hub_family_ok))

    survivors = [(fam, rec["cell"], rec.get("estimator"), rec["frac"])
                 for fam, rec, ok in claim_cells
                 if ok and rec["cell_verdict"] == "SURVIVES_HOLM"]
    nominal = [(fam, rec["cell"], rec.get("estimator"), rec["frac"])
               for fam, rec, ok in claim_cells
               if ok and rec["cell_verdict"] == "NOMINAL"]

    cap_verdict_f075 = ("NO_POWER" if (not pc_cap_pass or not valid_probes) else
                        "CAPACITY_EXCEEDS" if any(cap_summ[0.75][t]["exceeds"]
                                                  for t in valid_probes)
                        else "CAPACITY_BELOW_REQUIRED")

    if survivors:
        door = "DOOR_REOPENED"
    elif (pc_cap_pass and valid_probes and cap_verdict_f075 == "CAPACITY_BELOW_REQUIRED"
          and not nominal):
        door = "DOOR_CLOSED"
    else:
        door = "DOOR_MARGINAL"

    out = {"plan_hash": PLAN_HASH, "seed": SEED, "pc0": pc0,
           "pc_cap": pc_cap, "pc_cap_pass": bool(pc_cap_pass),
           "neg_cap": neg_cap, "overfit_broken_probes": overfit_broken,
           "valid_probes": valid_probes,
           "capacity": {str(f): cap_summ[f] for f in cap_summ},
           "capacity_verdict_f075": cap_verdict_f075,
           "ensemble_cells": {str(f): ens_cells[f] for f in ens_cells},
           "error_overlap": {str(f): overlaps[f] for f in overlaps},
           "neg_ens": neg_ens, "ens_family_ok": bool(ens_family_ok),
           "hub_cells": hub_cells, "neg_hub": neg_hub, "hub_family_ok": bool(hub_family_ok),
           "holm_survivors": survivors, "nominal_cells": nominal,
           "epoch_verdict": door,
           "references": {"e003_m1_b5_f075": {"acc": 0.034, "median_p": 0.599},
                          "e003_m1_b5_f1": {"acc": 0.039, "median_p": 0.417},
                          "e006_est_ot_b5_f075": {"acc": 0.071, "median_p": 0.081},
                          "e006_est_gw_b5_f075": {"acc": 0.051, "median_p": 0.267},
                          "required_rate_e003_headline": 0.119},
           "runtime_s": round(time.time() - t0, 1)}
    json.dump(out, open(os.path.join(OUTDIR, "E010_result.json"), "w"), indent=1, default=float)
    print("\ncapacity verdict (f=0.75):", cap_verdict_f075)
    print("survivors:", survivors, "| nominal:", nominal)
    print("EPOCH VERDICT:", door)
    return out


if __name__ == "__main__":
    run()
