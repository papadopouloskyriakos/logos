#!/usr/bin/env python3
"""TASK F4 — LA RELATIVE-ONLY OUTPUT of the substitution-axis bridge.

Given F2's verdict (CROSS_SCRIPT_SUBSTITUTION_BRIDGE_NO_POWER — even the known LB<->Cypriot pair
is at the chance floor), the ONLY admissible LA output from this channel is:
  (i)   relative COMPATIBILITY: for each LA AB-sign, the ranked LB partners the neighborhood
        geometry (GW coupling) is compatible with, WITH its uncertainty (coupling entropy);
  (ii)  EQUIVALENCE-CLASS constraints: within-LA neighborhood classes (the C4 REL_CLASSes;
        vowel-alternation / shared-consonant axis) — relative, value-free;
  (iii) explicit UNCERTAINTY + an assertion that NO ABSOLUTE VALUE follows and NO licence is
        earned (Art. XV). A relative-class reduction does not become a phonetic value.

Reads F2_real_LA_LB_coupling.json. Seed 20260708.
"""
from __future__ import annotations
import json, math, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import f_bridge_common as C

REL_PHON = ("/home/claude-runner/gitlab/n8n/logos-linear-a-relative-phonology-seals/"
            "experiments/linear_a_relative_phonology/data/C_la_graph.json")


def entropy(p):
    p = np.asarray(p, float)
    p = p[p > 0]
    p = p / p.sum()
    return float(-(p * np.log2(p)).sum())


def run():
    cp = json.load(open(os.path.join(C.DATA, "F2_real_LA_LB_coupling.json")))
    s_signs = cp["s_signs"]            # LA AB signs (opaque geometry; label used only to report)
    t_signs = cp["t_signs"]            # LB signs (shuffled order)
    Tcoup = np.asarray(cp["gw_coupling_neg_cost"])  # >=0 coupling mass, rows=LA, cols=LB
    gt_idx = {int(k): v for k, v in cp["gt_partner_idx"].items()}
    n, m = Tcoup.shape
    maxent = math.log2(m)

    per_sign = []
    exact_top1 = 0
    for i, la in enumerate(s_signs):
        row = Tcoup[i].copy()
        row = np.clip(row, 0, None)
        if row.sum() <= 0:
            row = np.ones(m)
        p = row / row.sum()
        order = np.argsort(p)[::-1]
        top = [{"lb_sign": t_signs[j], "compat": float(p[j]),
                # relation of this LA sign's CONVENTIONAL label to the candidate LB value — GRADE ONLY
                "relative_class_vs_candidate": C.relation(la, t_signs[j])} for j in order[:5]]
        true_lb = t_signs[gt_idx[i]]
        ent = entropy(p)
        top1 = t_signs[int(order[0])]
        exact_top1 += (top1 == true_lb)
        per_sign.append({
            "la_sign": la,
            "homomorphic_lb_partner": true_lb,
            "top1_geometry_partner": top1,
            "top1_is_homomorph": top1 == true_lb,
            "coupling_entropy_bits": ent,
            "normalized_uncertainty": ent / maxent,
            "candidates": top,
        })

    # within-LA equivalence classes (relative, value-free) from the C4 substitution graph
    relc = []
    try:
        g = json.load(open(REL_PHON))
        for rc in g.get("rel_classes", []):
            relc.append({"rel_class": rc["rel_class"], "signs": rc["signs"],
                         "n_signs": rc["n_signs"],
                         "interpretation": "within-LA substitution-neighborhood class "
                                           "(vowel-alternation / shared-consonant axis); RELATIVE only"})
    except Exception as e:
        relc = [{"error": str(e)}]

    mean_unc = float(np.mean([s["normalized_uncertainty"] for s in per_sign]))
    out = {
        "experiment": "F4_la_relative_only_output",
        "seed": C.SEED,
        "channel_verdict": "CROSS_SCRIPT_SUBSTITUTION_BRIDGE_NO_POWER (from F2)",
        "n_la_ab_signs": n,
        "geometry_top1_equals_homomorph_count": exact_top1,
        "geometry_top1_equals_homomorph_rate": exact_top1 / n,
        "mean_normalized_uncertainty": mean_unc,
        "relative_compatibility_per_sign": per_sign,
        "within_la_equivalence_classes": relc,
        "absolute_value_claim": "NONE — no absolute phonetic value follows from this channel.",
        "licence_state": {"PHONETIC": "NOT_EARNED", "LEXICAL": "NOT_EARNED",
                          "SEMANTIC": "NOT_EARNED", "reason": "channel at chance floor on a "
                          "KNOWN cross-script pair; relative-class residual does not survive "
                          "multiplicity for LA<->LB (Art. XV: a relative reduction earns no value)."},
        "what_this_channel_DOES_license": ("relative-compatibility SETS with high per-sign "
            "uncertainty and value-free within-LA equivalence classes only; it CANNOT pin any "
            "LA sign to an LB/GORILA value, and it does not narrow the value lattice enough to "
            "change SEED_A (=0)."),
    }
    p = C.dump("F4_la_relative_constraints.json", out)
    print("wrote", p)
    print(f"LA AB signs={n}  geometry-top1==homomorph: {exact_top1}/{n} "
          f"({exact_top1/n:.3f})  mean normalized uncertainty={mean_unc:.3f}")
    print("licence PHONETIC:", out["licence_state"]["PHONETIC"])
    return out


if __name__ == "__main__":
    run()
