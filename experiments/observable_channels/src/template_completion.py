#!/usr/bin/env python3
"""Experiment 4: document-template completion — mask one entry's NOTATION TYPE (which observable channels
it carries: word / logogram / numeral) and reconstruct it from the rest of the document's template + its
position. Tests whether Linear B documents are internally templated beyond the global base rate.

Pure document-structure test (Art. V layer L2). Held out by DOCUMENT (unseen documents), so the template
regularity must generalize, not be memorized. Baselines: global-majority type; position-conditioned type.
Template model: the majority type among the document's OTHER entries. Cross-site KN vs non-KN. Deterministic.
"""
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "admin_schema", "src", "corpus"))
import graph_common as gc

SEED = 20260707
LB = os.path.join(gc.MODEL_VISIBLE, "lb_graph.jsonl")
NHS = gc.EXP.replace("admin_schema", "observable_channels")
MIN_ENTRIES = 3


def docs_with_entry_types():
    """Per document: ordered list of entry notation-types (has_word, has_logo, has_numeral) + site."""
    out = []
    for line in open(LB):
        g = json.loads(line)
        ids = {n["id"]: n for n in g["nodes"]}
        order = {}; has_w = defaultdict(bool); has_l = defaultdict(bool); has_n = defaultdict(bool)
        for e in g["edges"]:
            if e["type"] != "CONTAINS":
                continue
            d = ids.get(e["dst"], {})
            t = d.get("type")
            if t in ("WORD_FORM", "LOGOGRAM", "NUMERAL"):
                order.setdefault(e["src"], len(order))
                if t == "WORD_FORM":
                    has_w[e["src"]] = True
                elif t == "LOGOGRAM":
                    has_l[e["src"]] = True
                else:
                    has_n[e["src"]] = True
        ents = sorted(order, key=lambda x: order[x])
        types = [(has_w[e], has_l[e], has_n[e]) for e in ents]
        types = [t for t in types if any(t)]
        if len(types) >= MIN_ENTRIES:
            out.append({"site": g["meta"]["site_code"], "types": types})
    return out


def split(docs, test_frac=0.25):
    def h(i):
        return int(gc.content_hash(str(i) + str(SEED)), 16) % 1000
    tr = [d for i, d in enumerate(docs) if h(i) >= test_frac * 1000]
    te = [d for i, d in enumerate(docs) if h(i) < test_frac * 1000]
    return tr, te


def run():
    docs = docs_with_entry_types()
    tr, te = split(docs)
    # baselines learned on train
    glob = Counter(t for d in tr for t in d["types"]).most_common(1)[0][0]
    pos_maj = {}
    by_pos = defaultdict(Counter)
    for d in tr:
        n = len(d["types"])
        for i, t in enumerate(d["types"]):
            by_pos[round(3 * i / max(n - 1, 1))][t] += 1     # position bucket 0..3
    for p, c in by_pos.items():
        pos_maj[p] = c.most_common(1)[0][0]

    def eval_on(test):
        n = ok_glob = ok_pos = ok_tmpl = 0
        for d in test:
            types = d["types"]; L = len(types)
            for i, t in enumerate(types):
                n += 1
                ok_glob += (glob == t)
                ok_pos += (pos_maj.get(round(3 * i / max(L - 1, 1)), glob) == t)
                others = types[:i] + types[i + 1:]                       # template = rest of the document
                tmpl = Counter(others).most_common(1)[0][0]
                ok_tmpl += (tmpl == t)
        if not n:
            return None
        return {"n_masked": n, "baseline_global_majority": round(ok_glob / n, 3),
                "baseline_position": round(ok_pos / n, 3), "M_template_A_unseen_doc": round(ok_tmpl / n, 3)}

    overall = eval_on(te)
    kn = eval_on([d for d in te if d["site"] == "KN"])
    nonkn = eval_on([d for d in te if d["site"] != "KN"])
    out = {"n_docs_ge3": len(docs), "n_train": len(tr), "n_test_docs": len(te),
           "distinct_entry_types": len({t for d in docs for t in d["types"]}),
           "type_distribution": {str(k): v for k, v in Counter(t for d in docs for t in d["types"]).most_common()},
           "held_out_unseen_documents": overall,
           "template_beats_baselines": bool(overall and overall["M_template_A_unseen_doc"] > max(overall["baseline_global_majority"], overall["baseline_position"]) + 0.02),
           "cross_site": {"KN": kn, "nonKN": nonkn},
           "layer": "L2 (document structure) — notation-type template only; no word-form identity",
           "interpretation": "Are LB documents internally templated — does the rest of a document predict a masked entry's notation type beyond the global/position base rate, on UNSEEN documents?"}
    os.makedirs(os.path.join(NHS, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(NHS, "results", "template_completion.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    run()
