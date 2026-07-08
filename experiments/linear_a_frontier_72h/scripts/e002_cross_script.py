#!/usr/bin/env python3
"""EPOCH-002 leg 2 — CROSS-SCRIPT motif bridge (MF_A trigram frames) on KNOWN scripts.

Does motif geometry align known LB<->Cypriot shared-value signs better than the failed flat
bridge (anchor-lattice F2: zero Holm survivors on KNOWN)? MF_B/MF_C are SOURCE_BLOCKED
cross-script (cog lexical lists carry no series/site metadata) — declared in prereg.

Pairs: CTRL = LB-DAMOS split-half (identity GT); KNOWN = LB-cog <-> Cypriot-cog (same-value GT).
Methods: F2's M1-M4 unchanged, similarity swapped to MF_A. Holm across 4 methods x 3 metrics.
Preregistered: epochs/EPOCH-002/prereg.md (plan_hash 09c55c9e...). Seed 20260708.
"""
from __future__ import annotations
import json, os, random, sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e002_motif_common as M
C = M.C
import f2_cross_script_bridge as F2  # noqa: E402 (read-only reuse; __main__-guarded)

SEED = M.SEED
MIN_SUP = 3


def motif_similarity_matrix(seqs, signs):
    """MF_A trigram-frame cofill-Jaccard over an ordered (opaque) sign list."""
    fset = M.inc_trigram(seqs)
    look = M.jaccard_lookup(fset)
    n = len(signs)
    S = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            S[i, j] = S[j, i] = look(signs[i], signs[j])
    return S


def build_problem_motif(seqs_s, seqs_t, gt_pairs):
    """As F2.build_problem (same seed, same shuffle) but with MF_A similarity."""
    sup_s, sup_t = C.sign_support(seqs_s), C.sign_support(seqs_t)
    pairs = [(a, b) for a, b in gt_pairs
             if sup_s.get(a, 0) >= MIN_SUP and sup_t.get(b, 0) >= MIN_SUP]
    s_signs = [a for a, b in pairs]
    t_true = [b for a, b in pairs]
    rng = random.Random(SEED)
    perm = list(range(len(t_true)))
    rng.shuffle(perm)
    t_signs = [t_true[i] for i in perm]
    gt_idx = {i: t_signs.index(t_true[i]) for i in range(len(s_signs))}
    Ss = motif_similarity_matrix(seqs_s, s_signs)
    St = motif_similarity_matrix(seqs_t, t_signs)
    return s_signs, t_signs, Ss, St, gt_idx


def run_pair_motif(name, seqs_s, seqs_t, gt_pairs):
    s_signs, t_signs, Ss, St, gt_idx = build_problem_motif(seqs_s, seqs_t, gt_pairs)
    n = len(s_signs)
    val_of_t = {t: t for t in t_signs}
    gt_partner = {s_signs[i]: t_signs[gt_idx[i]] for i in range(n)}
    res = {"pair": name, "n_alignable_signs": n}
    methods = {}
    for mname, costfn in (("M2_structural_signature", F2.method_M2_signature),
                          ("M3_gromov_wasserstein", F2.method_M3_gw)):
        cost = costfn(Ss, St)
        pred = F2.hungarian_pred(cost, s_signs, t_signs)
        top3 = F2.topk_accuracy(cost, s_signs, t_signs, gt_idx, k=3)
        null = F2.perm_null_classes(pred, gt_partner, val_of_t)
        methods[mname] = {"exact": null["exact"]["obs"],
                          "consonant_class": null["consonant_class"]["obs"],
                          "vowel_class": null["vowel_class"]["obs"], "top3_exact": top3,
                          "exact_count": null["exact_count"], "n": null["n"],
                          "perm_null": null, "supervised": False}
    for mname, costfn in (("M1_nn_transfer", F2.method_M1_nn),
                          ("M4_spectral_procrustes", F2.method_M4_spectral)):
        preds = {}
        for i in range(n):
            seed_idx = set(range(n)) - {i}
            cost = costfn(Ss, St, gt_idx, seed_idx)
            preds[s_signs[i]] = t_signs[int(np.argmin(cost[i]))]
        null = F2.perm_null_classes(preds, gt_partner, val_of_t)
        methods[mname] = {"exact": null["exact"]["obs"],
                          "consonant_class": null["consonant_class"]["obs"],
                          "vowel_class": null["vowel_class"]["obs"],
                          "exact_count": null["exact_count"], "n": null["n"],
                          "perm_null": null, "supervised": True}
    res["methods"] = methods
    return F2.summarize_pair(res)


def run():
    lb, _, _ = C.load_lb_damos()
    cyp = C.load_cyp_cog()
    lbc = C.load_lb_cog()

    out = {"experiment": "EPOCH-002_cross_script_motif_bridge", "seed": SEED,
           "plan_hash": M.PLAN_HASH, "family": "MF_A_trigram",
           "source_blocked": {"MF_B_formula": "no series metadata on cog lexical lists",
                              "MF_C_site": "no site metadata on cog lexical lists"},
           "pairs": {}}

    # CTRL: LB damos split-half, identity GT (same seeded split as flat F2)
    a, b = F2.half_split(lb)
    gt = F2.gt_same_value(a, b)
    out["pairs"]["CTRL_LBdamos_split_half"] = run_pair_motif("CTRL_LBdamos_split_half", a, b, gt)

    # KNOWN: LB cog <-> Cypriot cog, same-value GT
    gt = F2.gt_same_value(lbc, cyp)
    out["pairs"]["KNOWN_LBcog_vs_Cypcog"] = run_pair_motif("KNOWN_LBcog_vs_Cypcog", lbc, cyp, gt)

    # flat baseline numbers from the frozen F2 artifact (same seed/code, read-only)
    f2p = os.path.join(os.path.dirname(os.path.abspath(F2.__file__)),
                       "..", "data", "substitution_bridge", "F2_cross_script_bridge.json")
    flat = json.load(open(os.path.normpath(f2p)))
    out["flat_baseline_from_F2"] = {
        k: {"best_exact": flat["pairs"][k]["multiplicity"]["best_exact_accuracy"],
            "exact_survivors": flat["pairs"][k]["multiplicity"]["exact_survivors_holm05"],
            "any_survivors": flat["pairs"][k]["multiplicity"]["any_survivors_holm05"]}
        for k in ("CTRL_LBdamos_split_half", "KNOWN_LBcog_vs_Cypcog")}

    ctrl = out["pairs"]["CTRL_LBdamos_split_half"]["multiplicity"]
    known = out["pairs"]["KNOWN_LBcog_vs_Cypcog"]["multiplicity"]
    flat_ctrl_surv = bool(out["flat_baseline_from_F2"]["CTRL_LBdamos_split_half"]["exact_survivors"])
    if known["exact_survivors_holm05"]:
        leg = "SUPERIOR"
    elif ctrl["exact_survivors_holm05"]:
        leg = "EQUIVALENT"
    elif flat_ctrl_surv:
        leg = "INFERIOR"
    else:
        leg = "NO_POWER"
    out["leg_verdict"] = f"MOTIF_CROSS_{leg}"
    out["la_leg"] = ("RUN" if leg == "SUPERIOR" else
                     "NOT_RUN (prereg: only if cross leg SUPERIOR; bounded by known-script calibration)")

    p = M.dump("E002_cross_script.json", out)
    print("wrote", p)
    for k, pr in out["pairs"].items():
        print("\n==", k, "n=", pr["n_alignable_signs"])
        for m, md in pr["methods"].items():
            pn = md["perm_null"]
            print(f"  {m:26s} exact={md['exact']:.3f}(p{pn['exact']['p_one_sided']:.3f}) "
                  f"conC={md['consonant_class']:.3f}(p{pn['consonant_class']['p_one_sided']:.3f}) "
                  f"vowV={md['vowel_class']:.3f}(p{pn['vowel_class']['p_one_sided']:.3f})")
        print("  exact Holm survivors:", pr["multiplicity"]["exact_survivors_holm05"],
              "| any:", pr["multiplicity"]["any_survivors_holm05"])
    print("\nCROSS LEG VERDICT:", out["leg_verdict"], "| LA leg:", out["la_leg"])
    return out


if __name__ == "__main__":
    run()
