#!/usr/bin/env python3
"""EPOCH-002 leg 3 — CONDITIONAL LA application (triggered: cross leg = MOTIF_CROSS_SUPERIOR).

Mirror of anchor-lattice F2's REAL pair (LA-silver <-> LB-DAMOS, AB shape-homomorphic pairs as
the graded proposal) with the similarity swapped to MF_A trigram frames. IMPORTANT FRAMING
(Art. XI/XII/XV): the AB-homomorphic pairing is a PROPOSED correspondence, not ground truth.
"exact" here = agreement with the homomorphic proposal; a survivor is L2 relative support for
the homomorphic SYSTEM (capped <= 0.75 as a signal), never a phonetic value for any LA sign.
Flat baseline (F2 REAL): best exact 0.078, ZERO Holm survivors.

Preregistered: epochs/EPOCH-002/prereg.md (plan_hash 09c55c9e...), LA leg conditional clause.
Seed 20260708.
"""
from __future__ import annotations
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e002_motif_common as M
C = M.C
import f2_cross_script_bridge as F2  # noqa: E402
from e002_cross_script import run_pair_motif  # noqa: E402


def run():
    la, _ = C.load_la_words()
    lb, _, _ = C.load_lb_damos()
    ab = set(F2.gt_ab_homomorphic())
    la_signs = set(C.sign_support(la))
    lb_signs = set(C.sign_support(lb))
    gt = [(s, s) for s in sorted(ab) if s in la_signs and s in lb_signs]

    out = {"experiment": "EPOCH-002_la_leg_motif", "seed": M.SEED,
           "plan_hash": M.PLAN_HASH, "family": "MF_A_trigram",
           "trigger": "MOTIF_CROSS_SUPERIOR (prereg conditional clause)",
           "framing": "graded vs AB shape-homomorphic PROPOSAL, not ground truth; "
                      "L2 relative; capped <= 0.75; no value claim possible (Art. XV)"}
    pr = run_pair_motif("REAL_LAsilver_vs_LBdamos_MF_A", la, lb, gt)
    out["pair"] = pr
    f2p = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(F2.__file__)),
                                        "..", "data", "substitution_bridge",
                                        "F2_cross_script_bridge.json"))
    flat = json.load(open(f2p))["pairs"]["REAL_LAsilver_vs_LBdamos"]["multiplicity"]
    out["flat_baseline_from_F2"] = {"best_exact": flat["best_exact_accuracy"],
                                    "exact_survivors": flat["exact_survivors_holm05"],
                                    "any_survivors": flat["any_survivors_holm05"]}
    mult = pr["multiplicity"]
    if mult["exact_survivors_holm05"]:
        out["la_verdict"] = "LA_MOTIF_GEOMETRY_CONSISTENT_WITH_AB_HOMOMORPHY_L2"
    elif mult["any_survivors_holm05"]:
        out["la_verdict"] = "LA_MOTIF_RELATIVE_CLASS_SIGNAL_ONLY_L2"
    else:
        out["la_verdict"] = "LA_MOTIF_UNDERDETERMINED"
    p = M.dump("E002_la_leg.json", out)
    print("wrote", p)
    print("n =", pr["n_alignable_signs"])
    for m, md in pr["methods"].items():
        pn = md["perm_null"]
        print(f"  {m:26s} exact={md['exact']:.3f}(p{pn['exact']['p_one_sided']:.3f}) "
              f"conC={md['consonant_class']:.3f}(p{pn['consonant_class']['p_one_sided']:.3f}) "
              f"vowV={md['vowel_class']:.3f}(p{pn['vowel_class']['p_one_sided']:.3f})")
    print("exact Holm survivors:", mult["exact_survivors_holm05"],
          "| any:", mult["any_survivors_holm05"])
    print("LA VERDICT:", out["la_verdict"])
    return out


if __name__ == "__main__":
    run()
