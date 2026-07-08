#!/usr/bin/env python3
"""EPOCH-003 — SEED-POVERTY + CORPUS-POWER SURFACE for the trigram-frame motif bridge.

Preregistered: epochs/EPOCH-003/prereg.md
plan_hash be6dd7e786d373df3cad5c9b9bdba9b1786e6d98629a6c211eee9e8901e025d6
(frozen 2026-07-08T03:46:58Z, before any run)

Measures, on the KNOWN LB-cog<->Cypriot-cog pair (+ CTRL LB-DAMOS split-half identity pair),
how EPOCH-002's only Holm-surviving cross-script recovery (MF_A trigram similarity + M1
NN-transfer) degrades along two axes: n_seeds in {3,4,5,7,10,15,20,30,LOO} and corpus
fraction in {0.05,0.1,0.25,0.5,0.75,1.0}; plus wrong-seed injection adversarial cells.
Then locates Linear A's operating point (~5 firm seeds, support-matched corpus fraction)
ON the measured surface. NON-CIRCULAR (Art. XI/XII): similarities from sign identity only;
values grade. Everything L2 / KNOWN-script calibration; no LA value claim. Seed 20260708.
"""
from __future__ import annotations
import hashlib, json, os, random, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e002_motif_common as M
C = M.C
import f2_cross_script_bridge as F2
import e002_cross_script as E2C

SEED = 20260708
PLAN_HASH = "be6dd7e786d373df3cad5c9b9bdba9b1786e6d98629a6c211eee9e8901e025d6"
MIN_SUP = 3
N_PERM = 1000
FRACS = [0.05, 0.1, 0.25, 0.5, 0.75, 1.0]
BUDGETS = [3, 4, 5, 7, 10, 15, 20, 30]          # + "LOO" handled separately
R_CELL = 20                                       # replicates per non-LOO cell
N_CORPUS_DRAWS = 5                                # corpus draws when frac < 1.0
HOLM_BAR = 0.05 / 12                              # per-test bar inherited from E002 Holm-12
MIN_HELDOUT = 10
LA_MINSIDE_MEDIAN = 47                            # LA-side median support (prereg, descriptive)

CAMP = "/home/claude-runner/gitlab/n8n/logos-linear-a-frontier-72h/experiments/linear_a_frontier_72h"
OUTDIR = os.path.join(CAMP, "data", "motifs", "seed_poverty")
os.makedirs(OUTDIR, exist_ok=True)


def rng_for(*key):
    """Deterministic, PYTHONHASHSEED-independent RNG stream per key."""
    s = "|".join(str(k) for k in key)
    h = int(hashlib.sha256(f"{SEED}|{s}".encode()).hexdigest()[:16], 16)
    return random.Random(h), np.random.default_rng(h)


# ------------------------------------------------------------------ problem construction
def motif_matrix(seqs, signs):
    fset = M.inc_trigram(seqs)
    look = M.jaccard_lookup(fset)
    n = len(signs)
    S = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            S[i, j] = S[j, i] = look(signs[i], signs[j])
    return S


def build_problem(seqs_s, seqs_t, gt_pairs, shuffle_rng):
    """Alignable pairs (MIN_SUP both sides), target order shuffled with shuffle_rng.
    Returns dict or None if < 2 alignable."""
    sup_s, sup_t = C.sign_support(seqs_s), C.sign_support(seqs_t)
    pairs = [(a, b) for a, b in gt_pairs
             if sup_s.get(a, 0) >= MIN_SUP and sup_t.get(b, 0) >= MIN_SUP]
    if len(pairs) < 2:
        return None
    s_signs = [a for a, b in pairs]
    t_true = [b for a, b in pairs]
    perm = list(range(len(t_true)))
    shuffle_rng.shuffle(perm)
    t_signs = [t_true[i] for i in perm]
    gt_idx = {i: t_signs.index(t_true[i]) for i in range(len(s_signs))}
    med_s = float(np.median([sup_s[a] for a, b in pairs]))
    med_t = float(np.median([sup_t[b] for a, b in pairs]))
    return {"s_signs": s_signs, "t_signs": t_signs, "gt_idx": gt_idx,
            "Ss": motif_matrix(seqs_s, s_signs), "St": motif_matrix(seqs_t, t_signs),
            "minside_median_support": min(med_s, med_t),
            "median_support_s": med_s, "median_support_t": med_t}


def m1_cost(Ss, St, anchor_pairs):
    """M1 NN-transfer cost from explicit (s_idx, t_idx) anchors — same math as
    F2.method_M1_nn (row-normalized seed-profile L2 distance)."""
    s_seed = [i for i, _ in anchor_pairs]
    t_seed = [j for _, j in anchor_pairs]
    A = Ss[:, s_seed]
    B = St[:, t_seed]
    A = A / (np.linalg.norm(A, axis=1, keepdims=True) + 1e-9)
    B = B / (np.linalg.norm(B, axis=1, keepdims=True) + 1e-9)
    cost = np.zeros((len(Ss), len(St)))
    for i in range(len(Ss)):
        cost[i] = np.linalg.norm(B - A[i], axis=1)
    return cost


def exact_p(preds, truths, nrng, n_perm=N_PERM):
    """One-sided permutation p on exact count: permute true partners among held-out signs."""
    preds = np.asarray(preds)
    truths = np.asarray(truths)
    obs = int((preds == truths).sum())
    ge = 0
    for _ in range(n_perm):
        ge += int((preds == nrng.permutation(truths)).sum()) >= obs
    return obs, (ge + 1) / (n_perm + 1)


# ------------------------------------------------------------------ replicates
def replicate(prob, budget, srng, nrng, k_wrong=0):
    """One seeded-anchor replicate. Returns (exact_acc, p, n_heldout) or None if invalid."""
    n = len(prob["s_signs"])
    gt_idx = prob["gt_idx"]
    if n - budget < MIN_HELDOUT or budget >= n:
        return None
    seed_idx = sorted(srng.sample(range(n), budget))
    anchor = [(i, gt_idx[i]) for i in seed_idx]
    if k_wrong:
        wrong_pos = srng.sample(range(len(anchor)), k_wrong)
        for w in wrong_pos:
            i, true_j = anchor[w]
            choices = [j for j in range(n) if j != true_j]
            anchor[w] = (i, srng.choice(choices))
    cost = m1_cost(prob["Ss"], prob["St"], anchor)
    held = [i for i in range(n) if i not in set(seed_idx)]
    preds = [int(np.argmin(cost[i])) for i in held]
    truths = [gt_idx[i] for i in held]
    obs, p = exact_p(preds, truths, nrng)
    return {"exact_acc": obs / len(held), "exact_count": obs, "p": p, "n_heldout": len(held)}


def replicate_loo(prob, nrng):
    """All-but-one aggregate (E002 convention): held-out = all signs."""
    n = len(prob["s_signs"])
    if n < MIN_HELDOUT + 1:
        return None
    gt_idx = prob["gt_idx"]
    preds = []
    for i in range(n):
        anchor = [(k, gt_idx[k]) for k in range(n) if k != i]
        cost = m1_cost(prob["Ss"], prob["St"], anchor)
        preds.append(int(np.argmin(cost[i])))
    truths = [gt_idx[i] for i in range(n)]
    obs, p = exact_p(preds, truths, nrng)
    return {"exact_acc": obs / n, "exact_count": obs, "p": p, "n_heldout": n}


def cell_verdict(reps):
    valid = [r for r in reps if r is not None]
    n_invalid = len(reps) - len(valid)
    if len(valid) < max(1, len(reps) - len(reps) // 2):   # > R/2 invalid -> NO_POWER
        return {"replicates": len(reps), "invalid": n_invalid, "cell_verdict": "NO_POWER"}
    accs = np.array([r["exact_acc"] for r in valid])
    ps = np.array([r["p"] for r in valid])
    med_p = float(np.median(ps))
    v = ("SURVIVES_HOLM" if med_p <= HOLM_BAR else
         "NOMINAL" if med_p <= 0.05 else "FLOOR")
    return {"replicates": len(reps), "invalid": n_invalid,
            "exact_acc_mean": float(accs.mean()), "exact_acc_median": float(np.median(accs)),
            "acc_ci95": [float(np.quantile(accs, 0.025)), float(np.quantile(accs, 0.975))],
            "median_p": med_p, "survival_rate": float((ps <= HOLM_BAR).mean()),
            "nominal_rate": float((ps <= 0.05).mean()),
            "n_heldout_mean": float(np.mean([r["n_heldout"] for r in valid])),
            "cell_verdict": v}


# ------------------------------------------------------------------ corpus draws
def known_corpora():
    lbc = C.load_lb_cog()
    cyp = C.load_cyp_cog()
    return lbc, cyp, lambda s, t: F2.gt_same_value(s, t)


def ctrl_corpora():
    lb, _, _ = C.load_lb_damos()
    a, b = F2.half_split(lb)
    return a, b, lambda s, t: F2.gt_same_value(s, t)


def subsample(seqs, frac, rng):
    if frac >= 1.0:
        return list(seqs)
    k = max(1, round(frac * len(seqs)))
    return rng.sample(list(seqs), k)


def build_pair_problems(pair_name, seqs_s, seqs_t, gtfn):
    """corpus problems per (frac, draw)."""
    probs = {}
    for f in FRACS:
        draws = 1 if f >= 1.0 else N_CORPUS_DRAWS
        for d in range(draws):
            crng, _ = rng_for(pair_name, "corpus", f, d)
            ss = subsample(seqs_s, f, crng)
            tt = subsample(seqs_t, f, crng)
            shuf, _ = rng_for(pair_name, "shuffle", f, d)
            probs[(f, d)] = build_problem(ss, tt, gtfn(ss, tt), shuf)
    return probs


# ------------------------------------------------------------------ positive control
def positive_control():
    """Reproduce E002 KNOWN M1-LOO 7/47 and CTRL M1-LOO 55/71 through BOTH code paths."""
    lb, _, _ = C.load_lb_damos()
    cyp, lbc = C.load_cyp_cog(), C.load_lb_cog()
    out = {}

    # E002 path (frozen machinery, byte-identical seeding)
    for name, (ss, tt) in {
        "CTRL_LBdamos_split_half": (F2.half_split(lb)),
        "KNOWN_LBcog_vs_Cypcog": (lbc, cyp)}.items():
        s_signs, t_signs, Ss, St, gt_idx = E2C.build_problem_motif(ss, tt, F2.gt_same_value(ss, tt))
        n = len(s_signs)
        preds_e002, preds_e003 = [], []
        for i in range(n):
            cost = F2.method_M1_nn(Ss, St, gt_idx, set(range(n)) - {i})
            preds_e002.append(int(np.argmin(cost[i])))
            cost2 = m1_cost(Ss, St, [(k, gt_idx[k]) for k in range(n) if k != i])
            preds_e003.append(int(np.argmin(cost2[i])))
        exact_e002 = sum(preds_e002[i] == gt_idx[i] for i in range(n))
        exact_e003 = sum(preds_e003[i] == gt_idx[i] for i in range(n))
        out[name] = {"n": n, "exact_count_e002_path": int(exact_e002),
                     "exact_count_e003_path": int(exact_e003),
                     "paths_identical": preds_e002 == preds_e003}

    gate = (out["KNOWN_LBcog_vs_Cypcog"]["exact_count_e002_path"] == 7
            and out["KNOWN_LBcog_vs_Cypcog"]["n"] == 47
            and out["CTRL_LBdamos_split_half"]["exact_count_e002_path"] == 55
            and out["CTRL_LBdamos_split_half"]["n"] == 71
            and all(v["paths_identical"] and
                    v["exact_count_e002_path"] == v["exact_count_e003_path"]
                    for v in out.values()))
    out["gate"] = "PASS" if gate else "DETECTOR_BROKEN"
    return out


# ------------------------------------------------------------------ main sweep
def run():
    print("== positive control (gate) ==", flush=True)
    pc = positive_control()
    print(json.dumps(pc, indent=1))
    json.dump(pc, open(os.path.join(OUTDIR, "E003_positive_control.json"), "w"), indent=1)
    if pc["gate"] != "PASS":
        print("DETECTOR_BROKEN — aborting per prereg")
        return None

    cells = []
    surfaces = {}
    for pair_name, loader in (("KNOWN", known_corpora), ("CTRL", ctrl_corpora)):
        seqs_s, seqs_t, gtfn = loader()
        print(f"== building corpus problems: {pair_name} ==", flush=True)
        probs = build_pair_problems(pair_name, seqs_s, seqs_t, gtfn)
        surfaces[pair_name] = probs
        for f in FRACS:
            draws = [(f, d) for (ff, d) in probs if ff == f]
            for b in BUDGETS + ["LOO"]:
                reps = []
                if b == "LOO":
                    for (ff, d) in draws:
                        prob = probs[(ff, d)]
                        if prob is None:
                            reps.append(None)
                            continue
                        _, nrng = rng_for(pair_name, "null", f, d, "LOO")
                        reps.append(replicate_loo(prob, nrng))
                else:
                    per_draw = R_CELL if f >= 1.0 else R_CELL // N_CORPUS_DRAWS
                    for (ff, d) in draws:
                        prob = probs[(ff, d)]
                        for rep in range(per_draw):
                            if prob is None:
                                reps.append(None)
                                continue
                            srng, _ = rng_for(pair_name, "seeds", f, d, b, rep)
                            _, nrng = rng_for(pair_name, "null", f, d, b, rep)
                            reps.append(replicate(prob, b, srng, nrng))
                rec = {"pair": pair_name, "frac": f, "budget": b, "k_wrong": 0}
                rec.update(cell_verdict(reps))
                cells.append(rec)
                print(f"{pair_name} f={f} b={b}: {rec['cell_verdict']}"
                      f" acc={rec.get('exact_acc_mean', float('nan')):.3f}"
                      f" med_p={rec.get('median_p', float('nan')):.4f}", flush=True)
        json.dump(cells, open(os.path.join(OUTDIR, "E003_surface_partial.json"), "w"),
                  indent=1, default=float)

    # ---- adversarial wrong-seed cells (KNOWN, frac=1.0) ----
    prob = surfaces["KNOWN"][(1.0, 0)]
    for (b, kw) in [(5, 1), (5, 2), (7, 1), (7, 2), (5, 5)]:
        reps = []
        for rep in range(R_CELL):
            srng, _ = rng_for("KNOWN", "adv_seeds", 1.0, 0, b, kw, rep)
            _, nrng = rng_for("KNOWN", "adv_null", 1.0, 0, b, kw, rep)
            reps.append(replicate(prob, b, srng, nrng, k_wrong=kw))
        rec = {"pair": "KNOWN", "frac": 1.0, "budget": b, "k_wrong": kw}
        rec.update(cell_verdict(reps))
        cells.append(rec)
        print(f"ADV KNOWN b={b} wrong={kw}: {rec['cell_verdict']}"
              f" acc={rec.get('exact_acc_mean', float('nan')):.3f}"
              f" med_p={rec.get('median_p', float('nan')):.4f}", flush=True)

    # negative-control gate: full scramble must be FLOOR
    neg = next(c for c in cells if c["k_wrong"] == 5)
    if neg["cell_verdict"] != "FLOOR":
        print("NEGATIVE CONTROL NOT AT FLOOR — DETECTOR_BROKEN, aborting per prereg")
        json.dump(cells, open(os.path.join(OUTDIR, "E003_surface.json"), "w"),
                  indent=1, default=float)
        return None

    # ---- minimum seed budget (KNOWN, frac=1.0, monotone closure) ----
    def cv(pair, f, b, kw=0):
        return next(c for c in cells if c["pair"] == pair and c["frac"] == f
                    and c["budget"] == b and c["k_wrong"] == kw)
    order = BUDGETS + ["LOO"]
    min_budget = None
    for i, b in enumerate(order):
        if all(cv("KNOWN", 1.0, bb)["cell_verdict"] == "SURVIVES_HOLM" for bb in order[i:]):
            min_budget = b
            break
    min_budget = min_budget if min_budget is not None else "NONE_BELOW_LOO"

    # ---- LA operating point: f_LA by min-side median support (KNOWN pair) ----
    f_support = {}
    for f in FRACS:
        vals = [surfaces["KNOWN"][(f, d)]["minside_median_support"]
                for (ff, d) in surfaces["KNOWN"] if ff == f
                and surfaces["KNOWN"][(f, d)] is not None]
        f_support[f] = float(np.mean(vals)) if vals else None
    valid_f = [f for f in FRACS if f_support[f] is not None]
    f_la = min(valid_f, key=lambda f: abs(f_support[f] - LA_MINSIDE_MEDIAN))

    cell_la = cv("KNOWN", f_la, 5)
    wrong1 = cv("KNOWN", 1.0, 5, kw=1)
    v_la, v_w1 = cell_la["cell_verdict"], wrong1["cell_verdict"]
    if v_la == "SURVIVES_HOLM" and v_w1 in ("SURVIVES_HOLM", "NOMINAL"):
        verdict = "BRIDGE_VIABLE_AT_LA_SEED_BUDGET"
    elif v_la in ("SURVIVES_HOLM", "NOMINAL"):
        verdict = "BRIDGE_MARGINAL_AT_LA_SEED_BUDGET"
    else:
        verdict = "BRIDGE_NOT_VIABLE_AT_LA_SEED_BUDGET"

    # poisoning verdicts
    poison = {}
    for b in (5, 7):
        clean, w1 = cv("KNOWN", 1.0, b), cv("KNOWN", 1.0, b, kw=1)
        tiers = {"SURVIVES_HOLM": 2, "NOMINAL": 1, "FLOOR": 0, "NO_POWER": 0}
        poison[f"b{b}"] = {
            "clean": clean["cell_verdict"], "wrong1": w1["cell_verdict"],
            "wrong2": cv("KNOWN", 1.0, b, kw=2)["cell_verdict"],
            "delta_mean_exact_wrong1": (w1.get("exact_acc_mean", 0.0)
                                        - clean.get("exact_acc_mean", 0.0)),
            "poisons": (tiers[clean["cell_verdict"]] >= 1
                        and tiers[w1["cell_verdict"]] < tiers[clean["cell_verdict"]])}

    out = {"cells": cells, "positive_control": pc, "min_seed_budget_known_full": min_budget,
           "f_support_known": f_support, "f_la": f_la,
           "la_cell": cell_la, "wrong1_cell": wrong1, "poisoning": poison,
           "epoch_verdict": verdict, "plan_hash": PLAN_HASH, "seed": SEED}
    json.dump(out, open(os.path.join(OUTDIR, "E003_surface.json"), "w"),
              indent=1, default=float)
    print("\nmin_seed_budget (KNOWN, full corpus):", min_budget)
    print("f_LA =", f_la, "| support map:", f_support)
    print("LA cell:", {k: cell_la[k] for k in ("cell_verdict", "exact_acc_mean", "median_p")
                       if k in cell_la})
    print("EPOCH VERDICT:", verdict)
    return out


if __name__ == "__main__":
    run()
