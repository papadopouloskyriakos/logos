#!/usr/bin/env python3
"""Experiment 3: accounting-closure — does the arithmetic of a document actually CLOSE (one entry = the
sum of the others, the 'list + total' pattern), and does that closure let us reconstruct a MASKED line
item that a frequency baseline cannot?

Pure numeral-structure test (Art. V layer L2 — document structure; NO word forms, NO logograms). Closure
is compared against a value-permutation null (does closure appear by chance at this density?), and the
masked-summand reconstruction is compared against a median baseline. Cross-site KN vs non-KN. Deterministic.
"""
import json
import os
import random
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "admin_schema", "src", "corpus"))
import graph_common as gc

SEED = 20260707
LB = os.path.join(gc.MODEL_VISIBLE, "lb_graph.jsonl")
NHS = gc.EXP.replace("admin_schema", "observable_channels")
MIN_ENTRIES = 3            # non-trivial closure needs >=3 numeric entries (else 2 equal values close trivially)


def doc_value_lists():
    """Per document: the list of per-entry integer quantities (entries carrying >=1 positive numeral),
    plus the site. One value per entry (sum of its numerals)."""
    docs = []
    for line in open(LB):
        g = json.loads(line)
        ids = {n["id"]: n for n in g["nodes"]}
        ent_vals = defaultdict(float)
        for e in g["edges"]:
            if e["type"] != "CONTAINS":
                continue
            d = ids.get(e["dst"], {})
            if d.get("type") == "NUMERAL":
                v = d.get("value")
                if isinstance(v, (int, float)) and v > 0 and not d.get("damage_flag"):
                    ent_vals[e["src"]] += v
        vals = sorted((round(v, 3) for v in ent_vals.values() if v > 0), reverse=True)
        if len(vals) >= MIN_ENTRIES:
            docs.append({"site": g["meta"]["site_code"], "vals": vals})
    return docs


def closes(vals, tol=0.0):
    """The largest value equals the sum of the rest (list+total), within absolute tolerance tol."""
    return abs(vals[0] - sum(vals[1:])) <= tol


def closure_rate(docs, tol=0.0):
    return round(sum(1 for d in docs if closes(d["vals"], tol)) / len(docs), 3) if docs else 0.0


def null_closure_rate(docs, tol=0.0):
    """Permutation null: redraw each doc's k values from the global value pool (same k), recompute
    closure. If real >> null, closure is a real accounting structure, not an artefact of the value density."""
    pool = [v for d in docs for v in d["vals"]]
    rng = random.Random(SEED)
    hits = 0
    for d in docs:
        vals = sorted(rng.choice(pool) for _ in d["vals"])
        vals.reverse()
        hits += closes(vals, tol)
    return round(hits / len(docs), 3) if docs else 0.0


def masked_reconstruction(docs, tol=0.0):
    """On EXACT-closing docs, mask a random SUMMAND (not the total) and reconstruct it as total - sum(rest).
    Compare exact-match vs a baseline that predicts the global median summand. Tests whether closure carries
    a recoverable hidden line item (the total==vals[0] is NOT masked, to avoid circularity)."""
    rng = random.Random(SEED + 1)
    closing = [d for d in docs if closes(d["vals"], tol) and len(d["vals"]) >= MIN_ENTRIES]
    if not closing:
        return {"n_closing": 0}
    summands = [v for d in closing for v in d["vals"][1:]]
    median = sorted(summands)[len(summands) // 2]
    ok_close = ok_base = 0
    for d in closing:
        total, rest = d["vals"][0], d["vals"][1:]
        j = rng.randrange(len(rest))
        masked = rest[j]
        recon = round(total - (sum(rest) - masked), 3)          # closure reconstruction
        ok_close += abs(recon - masked) <= tol
        ok_base += abs(median - masked) <= tol                  # frequency/median baseline
    n = len(closing)
    return {"n_closing": n, "closure_reconstruction_acc": round(ok_close / n, 3),
            "median_baseline_acc": round(ok_base / n, 3)}


def run():
    docs = doc_value_lists()
    kn = [d for d in docs if d["site"] == "KN"]
    nonkn = [d for d in docs if d["site"] != "KN"]
    out = {"n_docs_ge3_numeric": len(docs),
           "closure_rate_exact": closure_rate(docs, 0.0),
           "null_closure_rate_exact": null_closure_rate(docs, 0.0),
           "closure_rate_tol1": closure_rate(docs, 1.0),
           "null_closure_rate_tol1": null_closure_rate(docs, 1.0),
           "cross_site_closure_exact": {"KN": closure_rate(kn, 0.0), "nonKN": closure_rate(nonkn, 0.0),
                                        "n_KN": len(kn), "n_nonKN": len(nonkn)},
           "masked_summand_reconstruction": masked_reconstruction(docs, 0.0),
           "layer": "L2 (document structure) — numeral arithmetic only; no word forms/logograms",
           "interpretation": "Is the 'list + total' accounting closure a real, above-null document structure, and does it reconstruct a masked line item beyond a median baseline?"}
    os.makedirs(os.path.join(NHS, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(NHS, "results", "accounting_closure.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    run()
