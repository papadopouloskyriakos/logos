#!/usr/bin/env python3
"""EPOCH-002 POST-HOC diagnostic audit (declared as such; does NOT alter the preregistered
verdicts). Questions:
 (1) Which KNOWN LB<->Cypriot signs does motif-M1 recover exactly? Are they frequency giants?
 (2) Adversarial frequency-rank baseline: match signs purely by within-script support rank —
     how many exact hits does that alone give (with its own permutation p)?
 (3) Same for CTRL.
Seed 20260708.
"""
from __future__ import annotations
import random, sys, os

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e002_motif_common as M
C = M.C
import f2_cross_script_bridge as F2  # noqa: E402
from e002_cross_script import build_problem_motif  # noqa: E402


def m1_predictions(Ss, St, gt_idx, s_signs, t_signs):
    preds = {}
    n = len(s_signs)
    for i in range(n):
        seed_idx = set(range(n)) - {i}
        cost = F2.method_M1_nn(Ss, St, gt_idx, seed_idx)
        preds[s_signs[i]] = t_signs[int(np.argmin(cost[i]))]
    return preds


def freq_rank_baseline(seqs_s, seqs_t, s_signs, t_signs, gt_partner, n_perm=1000):
    sup_s, sup_t = C.sign_support(seqs_s), C.sign_support(seqs_t)
    s_order = sorted(s_signs, key=lambda x: -sup_s[x])
    t_order = sorted(t_signs, key=lambda x: -sup_t[x])
    pred = dict(zip(s_order, t_order))
    ex = sum(pred[s] == gt_partner[s] for s in s_signs)
    rng = random.Random(M.SEED)
    tv = [gt_partner[s] for s in s_signs]
    null = []
    for _ in range(n_perm):
        perm = tv[:]
        rng.shuffle(perm)
        gp2 = dict(zip(s_signs, perm))
        null.append(sum(pred[s] == gp2[s] for s in s_signs))
    ge = sum(1 for x in null if x >= ex)
    return pred, ex, (ge + 1) / (n_perm + 1)


def audit(name, seqs_s, seqs_t, gt_pairs):
    s_signs, t_signs, Ss, St, gt_idx = build_problem_motif(seqs_s, seqs_t, gt_pairs)
    gt_partner = {s_signs[i]: t_signs[gt_idx[i]] for i in range(len(s_signs))}
    preds = m1_predictions(Ss, St, gt_idx, s_signs, t_signs)
    sup_s = C.sign_support(seqs_s)
    ranks = {s: r for r, s in enumerate(sorted(s_signs, key=lambda x: -sup_s[x]))}
    hits = sorted([s for s in s_signs if preds[s] == gt_partner[s]], key=lambda s: ranks[s])
    fpred, fex, fp = freq_rank_baseline(seqs_s, seqs_t, s_signs, t_signs, gt_partner)
    freq_hits = sorted([s for s in s_signs if fpred[s] == gt_partner[s]], key=lambda s: ranks[s])
    overlap = set(hits) & set(freq_hits)
    print(f"\n== {name} n={len(s_signs)}")
    print(f"M1 exact hits ({len(hits)}):", [(h, f"rank{ranks[h]}") for h in hits])
    print(f"freq-rank baseline exact = {fex}/{len(s_signs)} (perm p={fp:.4f}); hits:",
          [(h, f"rank{ranks[h]}") for h in freq_hits])
    print("overlap M1∩freq:", sorted(overlap))
    return {"pair": name, "n": len(s_signs),
            "m1_exact_hits": hits, "m1_hit_freq_ranks": [ranks[h] for h in hits],
            "freq_rank_exact": fex, "freq_rank_p": fp, "freq_rank_hits": freq_hits,
            "overlap": sorted(overlap)}


def run():
    lb, _, _ = C.load_lb_damos()
    cyp = C.load_cyp_cog()
    lbc = C.load_lb_cog()
    out = {"experiment": "EPOCH-002_posthoc_audit", "seed": M.SEED,
           "declared": "POST-HOC diagnostic; preregistered verdicts unchanged"}
    a, b = F2.half_split(lb)
    out["CTRL"] = audit("CTRL_LBdamos_split_half", a, b, F2.gt_same_value(a, b))
    out["KNOWN"] = audit("KNOWN_LBcog_vs_Cypcog", lbc, cyp, F2.gt_same_value(lbc, cyp))
    M.dump("E002_posthoc_audit.json", out)


if __name__ == "__main__":
    run()
