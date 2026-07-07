#!/usr/bin/env python3
"""Experiment 5: cross-site invariance of the L2 document-structure signal. Is the notation-type template
grammar the SAME across sites (transfers both KN->non-KN AND non-KN->KN, above each target site's own
baseline), or is it site-dependent? Plus the entry-type distribution divergence and a site-shuffle null.

Pure L2 (document structure). No word-form identity. Deterministic.
"""
import json
import os
import random
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "admin_schema", "src", "corpus"))
import graph_common as gc
from template_completion import docs_with_entry_types

SEED = 20260707
NHS = gc.EXP.replace("admin_schema", "observable_channels")


def template_acc(train, test):
    """Position->type + global-majority baselines learned on `train`; within-doc template evaluated on
    `test` (the template model is site-agnostic by design — this tests whether it TRANSFERS)."""
    from collections import defaultdict
    glob = Counter(t for d in train for t in d["types"]).most_common(1)[0][0]
    posc = {}
    bucket = defaultdict(Counter)
    for d in train:
        n = len(d["types"])
        for i, t in enumerate(d["types"]):
            bucket[round(3 * i / max(n - 1, 1))][t] += 1
    for p, c in bucket.items():
        posc[p] = c.most_common(1)[0][0]
    n = og = op = ot = 0
    for d in test:
        types = d["types"]; L = len(types)
        for i, t in enumerate(types):
            n += 1
            og += (glob == t)
            op += (posc.get(round(3 * i / max(L - 1, 1)), glob) == t)
            others = types[:i] + types[i + 1:]
            ot += (Counter(others).most_common(1)[0][0] == t)
    if not n:
        return None
    return {"n": n, "global_majority": round(og / n, 3), "position": round(op / n, 3),
            "template": round(ot / n, 3)}


def tvd(a, b):
    """total-variation distance between two entry-type distributions."""
    keys = set(a) | set(b)
    sa, sb = sum(a.values()) or 1, sum(b.values()) or 1
    return round(0.5 * sum(abs(a.get(k, 0) / sa - b.get(k, 0) / sb) for k in keys), 3)


def run():
    docs = docs_with_entry_types()
    kn = [d for d in docs if d["site"] == "KN"]
    non = [d for d in docs if d["site"] != "KN"]
    # two-direction transfer (train on one site, test on the OTHER)
    kn_to_non = template_acc(kn, non)
    non_to_kn = template_acc(non, kn)
    # does template beat the TARGET site's own baseline in each direction?
    inv_kn_to_non = kn_to_non["template"] > max(kn_to_non["global_majority"], kn_to_non["position"]) + 0.02
    inv_non_to_kn = non_to_kn["template"] > max(non_to_kn["global_majority"], non_to_kn["position"]) + 0.02
    bidirectional = bool(inv_kn_to_non and inv_non_to_kn)
    # entry-type distribution divergence
    dist_kn = Counter(t for d in kn for t in d["types"]); dist_non = Counter(t for d in non for t in d["types"])
    type_tvd = tvd(dist_kn, dist_non)
    # site-shuffle null: reassign site labels at random, recompute the KN-side template accuracy gap
    rng = random.Random(SEED)
    labels = ["KN"] * len(kn) + ["non"] * len(non)
    null_gaps = []
    for _ in range(200):
        rng.shuffle(labels)
        a = [d for d, l in zip(docs, labels) if l == "KN"]; b = [d for d, l in zip(docs, labels) if l == "non"]
        ta = template_acc(b, a)["template"]; tb = template_acc(a, b)["template"]
        null_gaps.append(abs(ta - tb))
    real_gap = abs(kn_to_non["template"] - non_to_kn["template"])
    null_p = round(sum(1 for g in null_gaps if g >= real_gap) / len(null_gaps), 3)
    out = {"n_docs": len(docs), "n_KN": len(kn), "n_nonKN": len(non),
           "KN_to_nonKN": kn_to_non, "nonKN_to_KN": non_to_kn,
           "template_beats_target_baseline": {"KN_to_nonKN": inv_kn_to_non, "nonKN_to_KN": inv_non_to_kn},
           "bidirectional_invariant": bidirectional,
           "entry_type_TVD_KN_vs_nonKN": type_tvd,
           "cross_site_gap": round(real_gap, 3), "site_shuffle_null_p": null_p,
           "layer": "L2 (document structure)",
           "verdict": "SITE_INVARIANT" if bidirectional and type_tvd < 0.15 else "SITE_DEPENDENT",
           "interpretation": "Is the L2 notation-type template grammar the SAME across sites (bidirectional transfer above each target baseline + low type-distribution divergence), or site-dependent?"}
    os.makedirs(os.path.join(NHS, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(NHS, "results", "cross_site_invariance.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    run()
