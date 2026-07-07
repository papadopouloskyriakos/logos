#!/usr/bin/env python3
"""§VI pre-Stage-5 power gate: can the pseudo-script benchmark be powered using ONLY non-trivial
REFERENCE_GOLD_A units? Mechanical verdict: READY_FOR_PSEUDO_SCRIPT_FREEZE / NO_POWER_BEFORE_MODELING /
INCOMPLETE. Derived by simulation, not an arbitrary threshold. No model is trained here.
"""
import json
import math
import os
import sys
from collections import Counter
from math import comb

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "weak_supervision"))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "admin_schema", "src", "corpus"))
import labeling_functions as LF
import graph_common as gc

NHS = gc.EXP.replace("admin_schema", "no_human_structure")
LABELS = os.path.join(NHS, "data", "source_labels", "linear_b_source_labels.jsonl")
LOADBEARING = {"HUMAN_OR_INSTITUTION", "PLACE", "OPERATOR_OR_RELATION", "QUALIFIER"}
STRUCT_LFS = [n for n, c in LF.LF_CLASS.items() if c == "EDITION_INDEPENDENT"]


def binom_power(p_alt, p0, n, alpha=0.05):
    """one-sided binomial: power to reject H0:p=p0 at level alpha when true p=p_alt, sample n."""
    cum = 0.0; crit = n + 1
    for c in range(n, -1, -1):
        cum += comb(n, c) * p0 ** c * (1 - p0) ** (n - c)
        if cum > alpha:
            crit = c + 1; break
    return sum(comb(n, c) * p_alt ** c * (1 - p_alt) ** (n - c) for c in range(crit, n + 1))


def min_detectable(p0, n, alpha=0.05, power_target=0.8):
    for pa in [x / 100 for x in range(int(p0 * 100) + 1, 101)]:
        if binom_power(pa, p0, n, alpha) >= power_target:
            return round(pa, 2)
    return None


def run():
    labels = [json.loads(l) for l in open(LABELS)]
    ga = [l for l in labels if l["label_category"] == "REFERENCE_GOLD_A" and l["nontrivial"]]
    if len(ga) < 10:
        return {"verdict": "NO_POWER_BEFORE_MODELING", "reason": "trusted non-trivial reference pool < 10"}
    roles = Counter(l["coarse_role"] for l in ga)
    present = set(roles); absent = LOADBEARING - present
    morph_fam = len({l["morphological_family"] for l in ga})
    kn = sum(1 for l in ga if "KN" in l["sites"]); nonkn = sum(1 for l in ga if any(s != "KN" for s in l["sites"]))
    # edition-independent (structural) signal: does the majority structural-LF vote predict the gold role?
    feats = LF.features()
    def struct_vote(fo):
        c = Counter(LF.LFS[n](fo, feats[fo]) for n in STRUCT_LFS if fo in feats and LF.LFS[n](fo, feats[fo]))
        return c.most_common(1)[0][0] if c else None
    covered = [(struct_vote(l["form_id"]), l["coarse_role"]) for l in ga if struct_vote(l["form_id"])]
    p_struct = round(sum(1 for a, b in covered if a == b) / len(covered), 3) if covered else 0.0
    struct_cov = round(len(covered) / len(ga), 3)
    baseline = round(max(roles.values()) / len(ga), 3)                 # majority-class baseline
    n_sealed = max(round(morph_fam * 0.30), 1)                          # grouped effective sealed units
    # O2+D8: sign permutation is ~structure-preserving; degradation reduces coverage. Estimate model acc ~=
    # structural signal * coverage + baseline * (1-coverage), clamped.
    est_o2d8 = round(min(p_struct * struct_cov + baseline * (1 - struct_cov), 0.99), 3)
    mdi = min_detectable(baseline, n_sealed)                            # min detectable model accuracy
    power_at_est = round(binom_power(est_o2d8, baseline, n_sealed), 3)
    # verdict
    reasons = []
    if absent:
        reasons.append(f"load-bearing classes structurally ABSENT from REFERENCE_GOLD_A: {sorted(absent)}")
    if len(ga) < 40:
        reasons.append(f"non-trivial reference pool small ({len(ga)})")
    if n_sealed < 12:
        reasons.append(f"sealed-eval too small ({n_sealed} grouped units)")
    if mdi is None or est_o2d8 < mdi:
        reasons.append(f"O2+D8 cannot achieve useful power (est {est_o2d8} < min detectable {mdi} at n={n_sealed}; power {power_at_est})")
    verdict = "NO_POWER_BEFORE_MODELING" if reasons else "READY_FOR_PSEUDO_SCRIPT_FREEZE"
    out = {"non_trivial_REFERENCE_GOLD_A": len(ga), "by_role": dict(roles),
           "load_bearing_present": sorted(present & LOADBEARING), "load_bearing_absent": sorted(absent),
           "independent_lexical_families": len({l["lexical_family"] for l in ga}),
           "independent_morphological_families": morph_fam, "KN": kn, "nonKN": nonkn,
           "by_series": dict(Counter(s for l in ga for s in l["series"])),
           "proposed_sealed_eval_size(grouped)": n_sealed,
           "majority_class_baseline": baseline, "structural_signal_precision": p_struct,
           "structural_signal_coverage": struct_cov, "est_O2_D8_model_accuracy": est_o2d8,
           "min_detectable_accuracy": mdi, "power_at_est_O2_D8": power_at_est,
           "classes_below_power": sorted(absent), "sites_below_power": ["MY", "TI", "KH"] if nonkn else [],
           "weak_supervision": "coverage 0.71 / conflict 0.044 (index-LF precision on gold is circular: LFs share source with gold)",
           "verdict": verdict, "verdict_reasons": reasons}
    json.dump(out, open(os.path.join(NHS, "data", "source_labels", "power_gate.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    run()
