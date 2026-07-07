#!/usr/bin/env python3
"""Stage 4: apply LFs, run WS0-WS4 label models, compute metrics. NO tuning on sealed/future eval labels.

WS0 majority · WS1 source-weighted (index LFs > structural) · WS2 generative (accuracy-weighted vote via
dev estimated-precision) · WS3 dependency-aware (collapse same-independence-class LF votes to one) · WS4
conservative intersection (label only on unanimous non-abstain).
"""
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "source_labels"))
import labeling_functions as LF
import graph_common as gc

NHS = gc.EXP.replace("admin_schema", "no_human_structure")
LABELS = os.path.join(NHS, "data", "source_labels", "linear_b_source_labels.jsonl")


def gold():
    g = {}
    for line in open(LABELS):
        r = json.loads(line)
        if r["label_category"] == "REFERENCE_GOLD_A" and r["nontrivial"]:
            g[r["form_id"]] = r["coarse_role"]
    return g


def vote_matrix(feats):
    V = {}
    for fo, ft in feats.items():
        V[fo] = {name: fn(fo, ft) for name, fn in LF.LFS.items()}
    return V


def ws0(votes):  # majority
    c = Counter(v for v in votes.values() if v)
    return c.most_common(1)[0][0] if c else None


def ws1(votes):  # source-weighted (index LFs weight 2)
    w = Counter()
    for name, v in votes.items():
        if v:
            w[v] += 2 if "INDEX" in name else 1
    return w.most_common(1)[0][0] if w else None


def ws2(votes, prec):  # accuracy-weighted
    w = Counter()
    for name, v in votes.items():
        if v:
            pv = prec.get(name)
            w[v] += pv if pv is not None else 0.5
    return w.most_common(1)[0][0] if w else None


def ws3(votes):  # dependency-aware: one vote per independence class
    by_class = defaultdict(Counter)
    for name, v in votes.items():
        if v:
            by_class[LF.LF_CLASS[name]][v] += 1
    tally = Counter()
    for cls, c in by_class.items():
        tally[c.most_common(1)[0][0]] += 1     # each class contributes ONE collapsed vote
    return tally.most_common(1)[0][0] if tally else None


def ws4(votes):  # conservative intersection: unanimous among non-abstain
    nz = [v for v in votes.values() if v]
    return nz[0] if nz and len(set(nz)) == 1 else None


def run():
    feats = LF.features()
    V = vote_matrix(feats)
    g = gold()
    # per-LF dev estimated precision (on REFERENCE_GOLD_A non-trivial forms only)
    prec = {}
    for name in LF.LFS:
        hits = [(V[fo][name], g[fo]) for fo in g if V[fo][name]]
        prec[name] = round(sum(1 for a, b in hits if a == b) / len(hits), 3) if hits else None
    cov = {name: round(sum(1 for fo in V if V[fo][name]) / len(V), 4) for name in LF.LFS}
    n_lf_firing = [sum(1 for v in V[fo].values() if v) for fo in V]
    conflict = sum(1 for fo in V if len({v for v in V[fo].values() if v}) > 1) / len(V)
    abst = round(sum(1 for fo in V if not any(V[fo].values())) / len(V), 4)
    # WS variants: coverage + estimated precision on gold
    def eval_ws(fn):
        pred = {fo: fn(V[fo]) for fo in V}
        labeled = [fo for fo in pred if pred[fo]]
        p = [(pred[fo], g[fo]) for fo in g if pred[fo]]
        return {"coverage": round(len(labeled) / len(V), 4),
                "est_precision_on_gold": round(sum(1 for a, b in p if a == b) / len(p), 3) if p else None,
                "n_gold_covered": len(p)}
    ws = {"WS0_majority": eval_ws(ws0), "WS1_source_weighted": eval_ws(ws1),
          "WS2_generative": eval_ws(lambda v: ws2(v, prec)), "WS3_dependency_aware": eval_ws(ws3),
          "WS4_conservative_intersection": eval_ws(ws4)}
    # dependency sensitivity: precision drop when collapsing SHARED_DECIPHERMENT LFs to one (WS3 vs WS1)
    dep_sens = None
    if ws["WS1_source_weighted"]["est_precision_on_gold"] and ws["WS3_dependency_aware"]["est_precision_on_gold"]:
        dep_sens = round(ws["WS1_source_weighted"]["est_precision_on_gold"] - ws["WS3_dependency_aware"]["est_precision_on_gold"], 3)
    out = {"n_forms": len(V), "n_gold_nontrivial": len(g),
           "lf_coverage": cov, "lf_est_precision_on_gold": prec,
           "mean_lfs_firing": round(sum(n_lf_firing) / len(n_lf_firing), 2), "conflict_rate": round(conflict, 4),
           "abstain_rate": abst, "ws_variants": ws, "dependency_sensitivity_WS1_vs_WS3": dep_sens,
           "class_balance_WS3": dict(Counter(ws3(V[fo]) for fo in V if ws3(V[fo])))}
    os.makedirs(os.path.join(NHS, "configs"), exist_ok=True)
    json.dump({"lf_class": LF.LF_CLASS, "ws_variants": list(ws), "frozen": True,
               "note": "LFs + WS frozen; not tuned on sealed/future eval"},
              open(os.path.join(NHS, "configs", "weak_supervision_freeze.json"), "w"), indent=1)
    json.dump(out, open(os.path.join(NHS, "data", "source_labels", "weak_supervision_metrics.json"), "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("n_forms", "n_gold_nontrivial", "mean_lfs_firing", "conflict_rate", "abstain_rate", "ws_variants", "dependency_sensitivity_WS1_vs_WS3")}, indent=1))
    return out


if __name__ == "__main__":
    run()
