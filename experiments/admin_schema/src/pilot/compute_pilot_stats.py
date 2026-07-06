#!/usr/bin/env python3
"""Stage 5.1: agreement (Krippendorff nominal α) + GOLD_A yield + class balance + effective units +
unseen-form & KN-vs-rest power simulation + mechanical verdict. Consumes the double-annotation output.

CAVEAT (stated, load-bearing): the two 'annotators' are two instances of the same model family, so this α
is an OPTIMISTIC UPPER BOUND on true independent (human) inter-annotator agreement, and the verdict is a
FEASIBILITY signal — never a substitute for real human double annotation before the sealed benchmark.
"""
import json
import math
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "corpus"))
import graph_common as gc

ANNOT = os.path.join(gc.EVAL_ONLY, "pilot_annotations.json")   # {annotator_A:[...], annotator_B:[...]}
ITEMS = os.path.join(gc.EVAL_ONLY, "pilot_items.json")
LB = os.path.join(gc.MODEL_VISIBLE, "lb_graph.jsonl")
TRIVIAL_ROLES = {"COMMODITY_OR_COUNTED_CATEGORY", "MEASURE_OR_QUANTITY", "DOCUMENT_STRUCTURE"}


def krippendorff_nominal(pairs):
    """pairs: list of (labelA, labelB). Returns nominal alpha via the coincidence-matrix method."""
    cats = sorted({c for p in pairs for c in p})
    idx = {c: i for i, c in enumerate(cats)}
    n = len(cats)
    coinc = [[0.0] * n for _ in range(n)]
    for a, b in pairs:                      # each unit has 2 coders -> m_u=2; each ordered pair weight 1/(m_u-1)=1
        coinc[idx[a]][idx[b]] += 1
        coinc[idx[b]][idx[a]] += 1
    total = sum(sum(r) for r in coinc)
    nc = [sum(coinc[i]) for i in range(n)]
    Do = sum(coinc[i][j] for i in range(n) for j in range(n) if i != j)
    De = sum(nc[i] * nc[j] for i in range(n) for j in range(n) if i != j) / (total - 1)
    alpha = 1 - (Do / De) if De else float("nan")
    return alpha, cats


def corpus_pools():
    """distinct content word-form types, hapax subset, KN vs non-KN — to scale the pilot yields."""
    forms = defaultdict(lambda: {"occ": 0, "kn": False, "nonkn": False})
    for line in open(LB):
        g = json.loads(line)
        kn = g["meta"]["site_code"] == "KN"
        for nd in g["nodes"]:
            if nd["type"] == "WORD_FORM" and nd["opaque_id"].count("+") >= 1:
                f = forms[nd["opaque_id"]]; f["occ"] += 1
                if kn: f["kn"] = True
                else: f["nonkn"] = True
    hapax = [k for k, v in forms.items() if v["occ"] == 1]
    return {"distinct_content_forms": len(forms), "hapax_content_forms": len(hapax),
            "kn_only_forms": sum(1 for v in forms.values() if v["kn"] and not v["nonkn"]),
            "nonkn_forms": sum(1 for v in forms.values() if v["nonkn"])}


def binom_min_detectable(p_alt, p_null=0.125, alpha=0.05):
    """smallest K s.t. a one-sided binomial test can reject p_null at level alpha with power ~0.8 at p_alt."""
    from math import comb
    for K in range(5, 2000):
        # critical count c: smallest c with P(X>=c | p_null) < alpha
        cum = 0.0; crit = None
        for x in range(K, -1, -1):
            cum += comb(K, x) * p_null ** x * (1 - p_null) ** (K - x)
            if cum >= alpha:
                crit = x + 1; break
        if crit is None:
            crit = 0
        # power at p_alt: P(X>=crit | p_alt)
        power = sum(comb(K, x) * p_alt ** x * (1 - p_alt) ** (K - x) for x in range(crit, K + 1))
        if power >= 0.8:
            return K
    return None


def run():
    if not os.path.exists(ANNOT):
        return {"verdict": "INCOMPLETE", "reason": "annotations absent"}
    A = {a["pilot_id"]: a for a in json.load(open(ANNOT))["annotator_A"]["annotations"]}
    B = {a["pilot_id"]: a for a in json.load(open(ANNOT))["annotator_B"]["annotations"]}
    items = {it["pilot_id"]: it for it in json.load(open(ITEMS))}
    ids = sorted(set(A) & set(B) & set(items))
    pairs = [(A[i]["coarse_role"], B[i]["coarse_role"]) for i in ids]
    alpha, cats = krippendorff_nominal(pairs)
    raw_agree = sum(1 for a, b in pairs if a == b) / len(pairs)
    # per-class agreement, class balance (adjudicated = A where agree)
    both_A = sum(1 for i in ids if A[i]["gold_tier"] == "GOLD_A" and B[i]["gold_tier"] == "GOLD_A" and A[i]["coarse_role"] == B[i]["coarse_role"])
    gold_a_yield = both_A / len(ids)
    agreed_role = {i: A[i]["coarse_role"] for i in ids if A[i]["coarse_role"] == B[i]["coarse_role"]}
    balance = Counter(agreed_role.values())
    # non-trivial GOLD_A among AGREED (content roles only) -> the load-bearing subset
    nontrivial_gold_a = [i for i in agreed_role if agreed_role[i] not in TRIVIAL_ROLES
                         and A[i]["gold_tier"] == "GOLD_A" and B[i]["gold_tier"] == "GOLD_A"]
    # split by KN / non-KN and hapax
    kn_nt = [i for i in nontrivial_gold_a if "KN" in items[i]["sites"]]
    nonkn_nt = [i for i in nontrivial_gold_a if "KN" not in items[i]["sites"]]
    hapax_nt = [i for i in nontrivial_gold_a if items[i]["hapax"]]
    pools = corpus_pools()
    # scale pilot non-trivial-GOLD_A yield to the corpus pools
    nt_ga_rate = len(nontrivial_gold_a) / len(ids)
    est_unseen_units = round(pools["hapax_content_forms"] * (len(hapax_nt) / max(len([i for i in ids if items[i]["hapax"]]), 1)))
    est_nonkn_units = round(pools["nonkn_forms"] * (len(nonkn_nt) / max(len([i for i in ids if "KN" not in items[i]["sites"]]), 1)))
    min_K = binom_min_detectable(0.40)          # assume a modest 0.40 recovery vs 1/8 null
    unseen_powered = est_unseen_units >= (min_K or 9999)
    nonkn_powered = est_nonkn_units >= (min_K or 9999)
    # verdict
    sparse = [c for c in cats if balance.get(c, 0) <= 2 and c != "UNKNOWN"]
    if alpha < 0.667:
        verdict = "NO_POWER"; why = f"alpha {alpha:.2f} < 0.667 (not eligible as primary gold)"
    elif not unseen_powered:
        verdict = "NO_POWER"; why = f"est unseen-form GOLD_A non-trivial units {est_unseen_units} < min detectable {min_K}"
    elif sparse:
        verdict = "MERGE_PREDECLARED_SPARSE_CLASSES"; why = f"sparse coarse classes {sparse} (semantic/agreement grounds)"
    else:
        verdict = "PROCEED_TO_FULL_ANNOTATION"; why = f"alpha {alpha:.2f}; unseen units {est_unseen_units}>={min_K}; balance ok"
    return {"n_items": len(ids), "krippendorff_alpha": round(alpha, 3), "alpha_caveat": "model-based double annotation -> OPTIMISTIC upper bound",
            "raw_agreement": round(raw_agree, 3), "gold_a_agreed_yield": round(gold_a_yield, 3),
            "class_balance_agreed": dict(balance), "nontrivial_gold_a_agreed": len(nontrivial_gold_a),
            "nontrivial_gold_a_KN": len(kn_nt), "nontrivial_gold_a_nonKN": len(nonkn_nt), "nontrivial_gold_a_hapax": len(hapax_nt),
            "corpus_pools": pools, "min_detectable_K(p=.40,null=.125)": min_K,
            "est_unseen_form_gold_a_units": est_unseen_units, "unseen_form_powered": unseen_powered,
            "est_nonKN_gold_a_units": est_nonkn_units, "nonKN_vs_rest_powered": nonkn_powered,
            "SITE_TEST_A": "train eligible non-KN -> test KN", "SITE_TEST_B": "train KN -> test eligible non-KN",
            "sparse_classes": sparse, "verdict": verdict, "verdict_reason": why}


if __name__ == "__main__":
    r = run()
    os.makedirs(os.path.join(gc.EXP, "data", "pilot"), exist_ok=True)
    json.dump(r, open(os.path.join(gc.EXP, "data", "pilot", "pilot_stats.json"), "w"), indent=1)
    print(json.dumps(r, indent=1))
