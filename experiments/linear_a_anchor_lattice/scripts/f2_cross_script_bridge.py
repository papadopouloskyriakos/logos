#!/usr/bin/env python3
"""TASK F2 + F3 — CROSS-SCRIPT SUBSTITUTION-NEIGHBORHOOD BRIDGE.

For a pair of scripts (S,T) we build each script's substitution-neighborhood SIMILARITY matrix
from sign IDENTITY only, assign each script its OWN opaque node IDs, then try to recover the
cross-script sign correspondence from neighborhood GEOMETRY ALONE — WITHOUT importing any
phonetic value. Four methods:

  M1 NN-TRANSFER (anchor-seeded, leave-one-out): each sign = its similarity profile to a seed set
     of known correspondences; match held-out signs by nearest anchor-profile (Hungarian).
  M2 STRUCTURAL-SIGNATURE (fully unsupervised): permutation-invariant node signature
     (sorted similarity profile + degree + row-entropy); Hungarian on signature distance.
  M3 GROMOV-WASSERSTEIN OT (fully unsupervised): entropic GW between the two intra-distance
     matrices with uniform marginals — the canonical label-free graph-alignment; argmax coupling.
  M4 SPECTRAL EMBEDDING + PROCRUSTES (anchor-seeded, LOO): Laplacian eigenmaps per graph,
     orthogonal Procrustes on seeds, nearest-neighbour in the aligned space.

GRADED PAIRS (values read ONLY to build ground truth + relative-class labels):
  CTRL  LB_damos half-A  <-> half-B     (identity GT; upper-bound positive control)
  KNOWN LB_cog          <-> Cyp_cog     (same syllabic value = counterpart; known cross-script)
  KNOWN LB_damos        <-> Cyp_cog     (register-mismatched known cross-script)
  REAL  LA_silver       <-> LB_damos    (AB shape-homomorphic label = proposed correspondence)

Each method reports: exact top-1 accuracy, top-3, same-CONSONANT-class and same-VOWEL-class
accuracy (F4 relative compatibility), and a permutation null (shuffle the ground-truth partner
labels). F3 = leave-one-sign-out relative-class prediction.

NON-CIRCULAR: geometry uses opaque IDs; labels grade only. A relative-class hit earns NO value.
Seed 20260708.
"""
from __future__ import annotations
import os, random, sys, math
from collections import Counter, defaultdict
import numpy as np
from scipy.optimize import linear_sum_assignment

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import f_bridge_common as C

SEED = C.SEED
np.random.seed(SEED)
N_PERM = 1000
MIN_SUP = 3          # min word-types a sign must occur in per script to be alignable
SIM_KIND = "jaccard"  # freq-robust cofill Jaccard (best same_C AUC in C_AUDIT/F1)


# ------------------------------------------------------------------ GW
def entropic_gw(Ds, Dt, p, q, eps=0.01, outer=200, inner=40):
    n, m = len(p), len(q)
    Ds2, Dt2 = Ds ** 2, Dt ** 2
    Cst = (Ds2 @ p)[:, None] + (Dt2 @ q)[None, :]
    T = np.outer(p, q)
    for _ in range(outer):
        cost = Cst - 2.0 * (Ds @ T @ Dt)
        cost -= cost.min()
        K = np.exp(-cost / eps) + 1e-300
        u, v = np.ones(n), np.ones(m)
        for _s in range(inner):
            u = p / (K @ v + 1e-300)
            v = q / (K.T @ u + 1e-300)
        Tn = u[:, None] * K * v[None, :]
        if np.abs(Tn - T).sum() < 1e-9:
            T = Tn
            break
        T = Tn
    return T


# ------------------------------------------------------------------ Laplacian eigenmap
def eigenmap(S, k):
    W = S.copy()
    np.fill_diagonal(W, 0.0)
    d = W.sum(1)
    d[d == 0] = 1e-9
    Dm = np.diag(1.0 / np.sqrt(d))
    L = np.eye(len(W)) - Dm @ W @ Dm
    w, V = np.linalg.eigh(L)
    return V[:, 1:k + 1]


def procrustes(A, B):
    """orthogonal R minimizing ||A R - B||; A,B are (k_seed x dim)."""
    U, _, Vt = np.linalg.svd(A.T @ B)
    return U @ Vt


# ------------------------------------------------------------------ scoring helpers
def relation_of(vs, vt):
    return C.relation(vs, vt)


def class_hit(pred_val, true_val, kind):
    if pred_val == true_val:
        return True
    r = C.relation(pred_val, true_val)
    if kind == "exact":
        return False
    if kind == "consonant":
        return r in ("same_consonant", "spelling_variant")
    if kind == "vowel":
        return r in ("same_vowel", "spelling_variant")
    return False


def accuracy(pred_partner, gt_partner, val_of_t):
    """pred_partner, gt_partner: dict S-sign -> T-sign. Return exact/consonant/vowel acc."""
    keys = [s for s in gt_partner if s in pred_partner]
    if not keys:
        return {"n": 0}
    ex = con = vow = 0
    for s in keys:
        pv, tv = val_of_t[pred_partner[s]], val_of_t[gt_partner[s]]
        ex += (pred_partner[s] == gt_partner[s])
        con += class_hit(pv, tv, "consonant")
        vow += class_hit(pv, tv, "vowel")
    n = len(keys)
    return {"n": n, "exact": ex / n, "consonant_class": con / n, "vowel_class": vow / n,
            "exact_count": ex}


def topk_accuracy(cost, s_signs, t_signs, gt_idx, k=3):
    """cost[i,j] lower=better. gt_idx: i -> true j. top-k exact."""
    hit = 0
    n = 0
    for i, j in gt_idx.items():
        if j is None:
            continue
        n += 1
        order = np.argsort(cost[i])
        if j in order[:k]:
            hit += 1
    return hit / n if n else None


# ------------------------------------------------------------------ build an alignment problem
def build_problem(seqs_s, seqs_t, gt_pairs):
    """gt_pairs: list of (s_sign, t_sign) ground-truth correspondences.
    Keep only pairs whose both signs meet MIN_SUP; return ordered sign lists + matrices
    with T order SHUFFLED (so index never leaks the answer)."""
    sup_s, sup_t = C.sign_support(seqs_s), C.sign_support(seqs_t)
    pairs = [(a, b) for a, b in gt_pairs if sup_s.get(a, 0) >= MIN_SUP and sup_t.get(b, 0) >= MIN_SUP]
    s_signs = [a for a, b in pairs]
    t_true = [b for a, b in pairs]
    rng = random.Random(SEED)
    perm = list(range(len(t_true)))
    rng.shuffle(perm)
    t_signs = [t_true[i] for i in perm]          # shuffled T order
    gt_idx = {i: t_signs.index(t_true[i]) for i in range(len(s_signs))}
    Ss = C.similarity_matrix(seqs_s, s_signs, kind=SIM_KIND)
    St = C.similarity_matrix(seqs_t, t_signs, kind=SIM_KIND)
    return s_signs, t_signs, Ss, St, gt_idx


# ------------------------------------------------------------------ the four methods -> cost matrix
def method_M2_signature(Ss, St):
    n = len(Ss)

    def sig(S):
        rows = []
        for i in range(len(S)):
            r = np.sort(S[i][np.arange(len(S)) != i])[::-1]
            deg = S[i].sum()
            p = S[i][S[i] > 0]
            p = p / p.sum() if p.sum() > 0 else p
            ent = -np.sum(p * np.log(p + 1e-12)) if len(p) else 0.0
            rows.append(np.concatenate([r, [deg, ent]]))
        return np.array(rows)
    A, B = sig(Ss), sig(St)
    A = (A - A.mean(0)) / (A.std(0) + 1e-9)
    B = (B - B.mean(0)) / (B.std(0) + 1e-9)
    cost = np.zeros((n, n))
    for i in range(n):
        cost[i] = np.linalg.norm(B - A[i], axis=1)
    return cost


def method_M3_gw(Ss, St):
    n = len(Ss)
    Ds, Dt = 1.0 - Ss, 1.0 - St
    np.fill_diagonal(Ds, 0.0)
    np.fill_diagonal(Dt, 0.0)
    p = np.ones(n) / n
    T = entropic_gw(Ds, Dt, p, p, eps=0.01)
    return -T   # cost = -coupling


def method_M1_nn(Ss, St, gt_idx, seed_idx):
    """anchor-seeded: profile to seeds. seed_idx: set of S-indices used as anchors."""
    n = len(Ss)
    s_seed = sorted(seed_idx)
    t_seed = [gt_idx[i] for i in s_seed]
    A = Ss[:, s_seed]
    B = St[:, t_seed]
    A = A / (np.linalg.norm(A, axis=1, keepdims=True) + 1e-9)
    B = B / (np.linalg.norm(B, axis=1, keepdims=True) + 1e-9)
    cost = np.zeros((n, n))
    for i in range(n):
        cost[i] = np.linalg.norm(B - A[i], axis=1)
    return cost


def method_M4_spectral(Ss, St, gt_idx, seed_idx, k=6):
    n = len(Ss)
    k = min(k, n - 2)
    Es, Et = eigenmap(Ss, k), eigenmap(St, k)
    s_seed = sorted(seed_idx)
    t_seed = [gt_idx[i] for i in s_seed]
    R = procrustes(Es[s_seed], Et[t_seed])
    Esr = Es @ R
    cost = np.zeros((n, n))
    for i in range(n):
        cost[i] = np.linalg.norm(Et - Esr[i], axis=1)
    return cost


def hungarian_pred(cost, s_signs, t_signs):
    ri, ci = linear_sum_assignment(cost)
    return {s_signs[i]: t_signs[j] for i, j in zip(ri, ci)}


def argmin_pred(cost, s_signs, t_signs, restrict_cols=None):
    pred = {}
    for i in range(len(s_signs)):
        row = cost[i].copy()
        if restrict_cols is not None:
            mask = np.ones(len(row), bool)
            mask[list(restrict_cols)] = False
            row[mask] = np.inf
        pred[s_signs[i]] = t_signs[int(np.argmin(row))]
    return pred


# ------------------------------------------------------------------ scoring + permutation null
def score_pred(pred, gt_partner, val_of_t):
    """exact / consonant-class / vowel-class accuracy of a FIXED prediction dict."""
    keys = [s for s in gt_partner if s in pred]
    ex = con = vow = 0
    for s in keys:
        pv, tv = val_of_t[pred[s]], val_of_t[gt_partner[s]]
        ex += (pred[s] == gt_partner[s])
        con += class_hit(pv, tv, "consonant")
        vow += class_hit(pv, tv, "vowel")
    n = len(keys)
    return {"exact": ex / n, "consonant_class": con / n, "vowel_class": vow / n,
            "exact_count": ex, "n": n}


def perm_null_classes(pred, gt_partner, val_of_t, n=N_PERM, seed=SEED):
    """Null: hold predictions FIXED, permute which T-sign is the true partner of each S-sign;
    recompute exact/consonant/vowel accuracy. Tests whether the predicted partners land in the
    correct relative class more than random ground truth would give."""
    rng = random.Random(seed)
    obs = score_pred(pred, gt_partner, val_of_t)
    s_keys = list(gt_partner)
    t_vals = [gt_partner[s] for s in s_keys]
    nulls = {"exact": [], "consonant_class": [], "vowel_class": []}
    for _ in range(n):
        perm = t_vals[:]
        rng.shuffle(perm)
        gp2 = {s_keys[i]: perm[i] for i in range(len(s_keys))}
        sc = score_pred(pred, gp2, val_of_t)
        for k in nulls:
            nulls[k].append(sc[k])
    res = {}
    for k in nulls:
        arr = sorted(nulls[k])
        ge = sum(1 for x in arr if x >= obs[k])
        mu, sd = float(np.mean(arr)), float(np.std(arr) + 1e-12)
        res[k] = {"obs": obs[k], "null_mean": mu, "z": (obs[k] - mu) / sd,
                  "p_one_sided": (ge + 1) / (n + 1)}
    res["exact_count"] = obs["exact_count"]
    res["n"] = obs["n"]
    return res


# ------------------------------------------------------------------ run one pair
def run_pair(name, seqs_s, seqs_t, gt_pairs, kfold=5):
    s_signs, t_signs, Ss, St, gt_idx = build_problem(seqs_s, seqs_t, gt_pairs)
    n = len(s_signs)
    val_of_t = {t: t for t in t_signs}   # value == label (already normalized)
    gt_partner = {s_signs[i]: t_signs[gt_idx[i]] for i in range(n)}
    res = {"pair": name, "n_alignable_signs": n,
           "s_signs": s_signs, "t_true_partner": [t_signs[gt_idx[i]] for i in range(n)]}
    methods = {}

    # ---- unsupervised M2, M3 : full bijection via Hungarian ----
    for mname, costfn in (("M2_structural_signature", method_M2_signature),
                          ("M3_gromov_wasserstein", method_M3_gw)):
        cost = costfn(Ss, St)
        pred = hungarian_pred(cost, s_signs, t_signs)
        top3 = topk_accuracy(cost, s_signs, t_signs, gt_idx, k=3)
        null = perm_null_classes(pred, gt_partner, val_of_t)
        methods[mname] = {"exact": null["exact"]["obs"],
                          "consonant_class": null["consonant_class"]["obs"],
                          "vowel_class": null["vowel_class"]["obs"], "top3_exact": top3,
                          "exact_count": null["exact_count"], "n": null["n"],
                          "perm_null": null, "supervised": False, "predictions": pred}

    # ---- seeded M1, M4 : genuine leave-one-out (seed on all-but-i, predict i) ----
    for mname, costfn in (("M1_nn_transfer", method_M1_nn),
                          ("M4_spectral_procrustes", method_M4_spectral)):
        preds = {}
        for i in range(n):
            seed_idx = set(range(n)) - {i}
            cost = costfn(Ss, St, gt_idx, seed_idx)
            pj = int(np.argmin(cost[i]))
            preds[s_signs[i]] = t_signs[pj]
        null = perm_null_classes(preds, gt_partner, val_of_t)
        methods[mname] = {"exact": null["exact"]["obs"],
                          "consonant_class": null["consonant_class"]["obs"],
                          "vowel_class": null["vowel_class"]["obs"],
                          "exact_count": null["exact_count"], "n": null["n"],
                          "perm_null": null, "supervised": True, "predictions": preds}

    res["methods"] = methods
    # ---- F3 leave-one-sign-out relative-class summary ----
    res["F3_loso_relative_class"] = {
        m: {"exact_acc": methods[m]["exact"], "exact_p": methods[m]["perm_null"]["exact"]["p_one_sided"],
            "consonant_class_acc": methods[m]["consonant_class"],
            "consonant_class_p": methods[m]["perm_null"]["consonant_class"]["p_one_sided"],
            "vowel_class_acc": methods[m]["vowel_class"],
            "vowel_class_p": methods[m]["perm_null"]["vowel_class"]["p_one_sided"]}
        for m in methods}
    return res, (s_signs, t_signs, Ss, St, gt_idx, methods)


# ------------------------------------------------------------------ ground-truth builders
def gt_same_value(seqs_s, seqs_t):
    sset, tset = set(C.sign_support(seqs_s)), set(C.sign_support(seqs_t))
    shared = sorted(v for v in sset & tset if C.parse_cv(v) is not None)
    return [(v, v) for v in shared]


def gt_ab_homomorphic():
    import json
    ont = json.load(open(os.path.join(C.SILVER, "signs_ontology.json")))
    ab = [C.norm(k) for k, v in ont.items() if v["class"] == "syllabogram-AB"]
    return ab


def half_split(seqs, seed=SEED):
    rng = random.Random(seed)
    s = list(seqs)
    rng.shuffle(s)
    h = len(s) // 2
    return s[:h], s[h:]


def holm(pairs):
    """pairs: list of (label, p). Return dict label -> holm-adjusted p."""
    order = sorted(pairs, key=lambda x: x[1])
    m = len(order)
    adj = {}
    running = 0.0
    for rank, (lab, p) in enumerate(order):
        running = max(running, (m - rank) * p)
        adj[lab] = min(1.0, running)
    return adj


def summarize_pair(pr):
    """Holm across all method x metric tests in a pair; flag surviving EXACT recoveries."""
    tests = []
    for m, md in pr["methods"].items():
        for metric in ("exact", "consonant_class", "vowel_class"):
            tests.append((f"{m}:{metric}", md["perm_null"][metric]["p_one_sided"]))
    adj = holm(tests)
    exact_survivors = [lab for lab, p in adj.items() if lab.endswith(":exact") and p < 0.05]
    any_survivor = [lab for lab, p in adj.items() if p < 0.05]
    best_exact = max(md["exact"] for md in pr["methods"].values())
    pr["multiplicity"] = {"n_tests": len(tests), "holm_adj": adj,
                          "exact_survivors_holm05": exact_survivors,
                          "any_survivors_holm05": any_survivor,
                          "best_exact_accuracy": best_exact}
    return pr


def run():
    la, _ = C.load_la_words()
    lb, _, _ = C.load_lb_damos()
    cyp = C.load_cyp_cog()
    lbc = C.load_lb_cog()

    out = {"experiment": "F2_cross_script_substitution_bridge", "seed": SEED,
           "sim_kind": SIM_KIND, "min_support": MIN_SUP, "n_perm": N_PERM,
           "non_circular": "neighborhood geometry uses opaque per-script IDs; values GRADE only; "
                           "no absolute value follows (Art. XV).",
           "pairs": {}}
    saved = {}

    # CTRL: LB damos split-half (identity GT) — methods' upper bound
    a, b = half_split(lb)
    gt = gt_same_value(a, b)
    r, sv = run_pair("CTRL_LBdamos_halfA_vs_halfB", a, b, gt)
    out["pairs"]["CTRL_LBdamos_split_half"] = r
    saved["ctrl"] = sv

    # KNOWN: LB cog vs Cyp cog (same-value ground truth) — matched lexical register
    gt = gt_same_value(lbc, cyp)
    r, sv = run_pair("KNOWN_LBcog_vs_Cypcog", lbc, cyp, gt)
    out["pairs"]["KNOWN_LBcog_vs_Cypcog"] = r
    saved["known_cog"] = sv

    # KNOWN: LB damos vs Cyp cog (register-mismatched)
    gt = gt_same_value(lb, cyp)
    r, sv = run_pair("KNOWN_LBdamos_vs_Cypcog", lb, cyp, gt)
    out["pairs"]["KNOWN_LBdamos_vs_Cypcog"] = r
    saved["known_damos"] = sv

    # REAL: LA silver vs LB damos (AB shape-homomorphic proposed correspondences)
    ab = set(gt_ab_homomorphic())
    la_signs = set(C.sign_support(la))
    lb_signs = set(C.sign_support(lb))
    gt = [(s, s) for s in sorted(ab) if s in la_signs and s in lb_signs]
    r, sv = run_pair("REAL_LAsilver_vs_LBdamos", la, lb, gt)
    out["pairs"]["REAL_LAsilver_vs_LBdamos"] = r
    saved["real"] = sv

    for k in out["pairs"]:
        out["pairs"][k] = summarize_pair(out["pairs"][k])

    # ---- overall verdict ----
    known = out["pairs"]["KNOWN_LBcog_vs_Cypcog"]["multiplicity"]
    real = out["pairs"]["REAL_LAsilver_vs_LBdamos"]["multiplicity"]
    ctrl = out["pairs"]["CTRL_LBdamos_split_half"]["multiplicity"]
    out["verdict"] = {
        "ctrl_identity_best_exact": ctrl["best_exact_accuracy"],
        "ctrl_exact_survivors": ctrl["exact_survivors_holm05"],
        "known_crossscript_exact_survivors_holm05": known["exact_survivors_holm05"],
        "known_crossscript_best_exact": known["best_exact_accuracy"],
        "real_LA_LB_exact_survivors_holm05": real["exact_survivors_holm05"],
        "real_LA_LB_any_survivors_holm05": real["any_survivors_holm05"],
        "real_LA_LB_best_exact": real["best_exact_accuracy"],
        "bridge_transfers_correspondence": bool(known["exact_survivors_holm05"]) and bool(real["exact_survivors_holm05"]),
        "label": None,
    }
    if not known["exact_survivors_holm05"]:
        out["verdict"]["label"] = "CROSS_SCRIPT_SUBSTITUTION_BRIDGE_NO_POWER"
        out["verdict"]["reason"] = ("even the KNOWN LB<->Cypriot cross-script pair sits at the "
            "chance floor after multiplicity (Holm) at Linear-A-scale corpora; the channel cannot "
            "carry a correspondence, so the LA<->LB application is UNDERDETERMINED a fortiori.")
    elif real["exact_survivors_holm05"]:
        out["verdict"]["label"] = "BRIDGE_TRANSFERS"
    else:
        out["verdict"]["label"] = "BRIDGE_CALIBRATED_BUT_LA_UNDERDETERMINED"

    p = C.dump("F2_cross_script_bridge.json", out)
    # persist the REAL coupling artifacts for F4
    import json as _j
    s_signs, t_signs, Ss, St, gt_idx, methods = saved["real"]
    cost_gw = method_M3_gw(Ss, St)
    _j.dump({"s_signs": s_signs, "t_signs": t_signs,
             "gw_coupling_neg_cost": (-cost_gw).tolist(),
             "gt_partner_idx": gt_idx},
            open(os.path.join(C.DATA, "F2_real_LA_LB_coupling.json"), "w"))
    print("wrote", p)
    for k, pr in out["pairs"].items():
        print("\n==", k, "n=", pr["n_alignable_signs"])
        for m, md in pr["methods"].items():
            pn = md["perm_null"]
            print(f"  {m:26s} exact={md['exact']:.3f}(p{pn['exact']['p_one_sided']:.3f}) "
                  f"conC={md['consonant_class']:.3f}(p{pn['consonant_class']['p_one_sided']:.3f}) "
                  f"vowV={md['vowel_class']:.3f}(p{pn['vowel_class']['p_one_sided']:.3f})")
    return out


if __name__ == "__main__":
    run()
