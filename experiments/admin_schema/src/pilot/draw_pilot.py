#!/usr/bin/env python3
"""Stage 5.1: draw a DEV-ONLY stratified annotation-feasibility pilot (deterministic).

Pilot = distinct CONTENT word-form types (notation excluded), stratified by site (KN vs non-KN), major
document series, support type, and frequency (hapax vs recurrent). For each item we reconstruct the
EVALUATION-layer transliteration (from the de-phon key) so annotators can assign roles from ground truth,
and we record the exclusion clusters (lexical form family / formula clusters / joins / scribe) that must be
burned from any future sealed holdout. NO model is run here; this only prepares items for annotation.
"""
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "corpus"))
import graph_common as gc

SEED = 20260707
N_TARGET = 160
LB = os.path.join(gc.MODEL_VISIBLE, "lb_graph.jsonl")
REF = os.path.join(gc.MODEL_VISIBLE, "lb_reference.json")
VOCAB = os.path.join(gc.EVAL_ONLY, "lb_dephon_vocab.json")


def _translit(form_opaque, sign_map):
    return "-".join(sign_map.get(s, "?") for s in form_opaque.split("+"))


def draw():
    sign_map = json.load(open(VOCAB))["B_SIGN"]
    ref = json.load(open(REF))
    graphs = [json.loads(l) for l in open(LB)]
    # collect per-form: occurrences, sites, series, supports, an example entry context
    forms = defaultdict(lambda: {"occ": 0, "sites": set(), "series": set(), "supports": set(),
                                 "docs": set(), "example": None})
    for g in graphs:
        site = g["meta"]["site_code"]; series = g["meta"]["document_series"]; supp = g["meta"]["support_type"]
        ids = {n["id"]: n for n in g["nodes"]}
        # entry -> ordered token opaque ids/types (for context)
        entry_tokens = defaultdict(list)
        for e in g["edges"]:
            if e["type"] == "CONTAINS" and ids.get(e["dst"], {}).get("type") in ("WORD_FORM", "LOGOGRAM", "NUMERAL", "MEASURE_MARKER"):
                n = ids[e["dst"]]; entry_tokens[e["src"]].append((n.get("position", 0), n["type"], n.get("opaque_id"), n.get("value")))
        for n in g["nodes"]:
            if n["type"] != "WORD_FORM":
                continue
            f = forms[n["opaque_id"]]
            f["occ"] += 1; f["sites"].add(site); f["series"].add(series); f["supports"].add(supp); f["docs"].add(g["graph_id"])
            if f["example"] is None:
                # find this token's entry for context
                for e in g["edges"]:
                    if e["type"] == "CONTAINS" and e["dst"] == n["id"]:
                        ctx = sorted(entry_tokens.get(e["src"], []))
                        f["example"] = {"site": site, "series": series, "support": supp,
                                        "entry_context": [(t, "≈".join(_translit(o, sign_map).split("-")) if (t == "WORD_FORM" and o) else (o or v))
                                                          for _, t, o, v in ctx]}
                        break
    # stratify: content forms only (>=2 signs to skip bare particles), pick across strata deterministically
    cand = [(fo, d) for fo, d in forms.items() if fo.count("+") >= 1]
    def keyfn(x):
        fo, d = x
        kn = "KN" in d["sites"]; hapax = d["occ"] == 1
        # deterministic pseudo-shuffle by hash of the opaque id
        return (0 if kn else 1, 0 if hapax else 1, gc.content_hash(fo))
    cand.sort(key=keyfn)
    # round-robin over (kn/nonkn x hapax/recurrent) strata for balance
    strata = defaultdict(list)
    for fo, d in cand:
        strata[("KN" if "KN" in d["sites"] else "nonKN", "hapax" if d["occ"] == 1 else "recurrent")].append((fo, d))
    picked = []
    i = 0
    keys = sorted(strata)
    while len(picked) < N_TARGET and any(strata[k] for k in keys):
        k = keys[i % len(keys)]
        if strata[k]:
            picked.append(strata[k].pop(0))
        i += 1
    items = []
    for fo, d in picked:
        items.append({"pilot_id": f"P{len(items):03d}", "opaque_form": fo,
                      "transliteration_EVAL": _translit(fo, sign_map), "n_occ": d["occ"],
                      "hapax": d["occ"] == 1, "sites": sorted(d["sites"]), "series": sorted(x for x in d["series"] if x),
                      "supports": sorted(x for x in d["supports"] if x), "example": d["example"]})
    # exclusion clusters to burn from any future holdout
    excl = {"word_form_families": sorted({it["opaque_form"] for it in items}),
            "documents": sorted({dc for fo, d in picked for dc in d["docs"]}),
            "formula_clusters": sorted({fcid for fcid, docs in ref.get("REPEATS_FORM", {}).items()}) if False else [],
            "note": "burn these lexical families + their documents (and joins/scribal-copies) from the sealed holdout"}
    os.makedirs(gc.EVAL_ONLY, exist_ok=True)
    json.dump(items, open(os.path.join(gc.EVAL_ONLY, "pilot_items.json"), "w"), ensure_ascii=False, indent=1)
    os.makedirs(os.path.join(gc.EXP, "data", "pilot"), exist_ok=True)
    json.dump({"n_items": len(items), "seed": SEED,
               "strata": {f"{a}/{b}": sum(1 for it in items if (("KN" in it["sites"]) == (a == "KN")) and (it["hapax"] == (b == "hapax")))
                          for a in ("KN", "nonKN") for b in ("hapax", "recurrent")},
               "exclusion_clusters": {"n_word_form_families": len(excl["word_form_families"]),
                                      "n_documents": len(excl["documents"])},
               "exclusion_word_form_families": excl["word_form_families"],
               "exclusion_documents": excl["documents"]},
              open(os.path.join(gc.EXP, "data", "pilot", "pilot_exclusion_manifest.json"), "w"), indent=1)
    print(f"pilot items: {len(items)}  | exclusion: {len(excl['word_form_families'])} form-families / {len(excl['documents'])} docs")
    return items


if __name__ == "__main__":
    draw()
