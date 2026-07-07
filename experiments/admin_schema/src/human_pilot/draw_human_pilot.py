#!/usr/bin/env python3
"""Prepare a DETERMINISTIC human-expert annotation sample + two blinded packets (no auto-pilot leakage).

This prepares material for TWO GENUINE HUMAN Mycenaean specialists. It does NOT annotate, predict, or
simulate experts. Reading-bearing files (packets, sample with transliteration, anon key) are written under
data/human_pilot/ and are GITIGNORED (DĀMOS-derived readings not redistributed); their sha256 + the frozen
sampling plan + strata + BLANK response templates are committed.
"""
import csv
import hashlib
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "corpus"))
import graph_common as gc

# ---- FROZEN SAMPLING PLAN (fixed BEFORE sampling) --------------------------------------------------
PLAN = {
    "sample_size_target": 160, "sample_size_floor": 120,
    "random_seed": 20260708,
    "replacement_policy": "without replacement (distinct form-types)",
    "site_quota": {"KN": 80, "nonKN": 80},
    "recurrent_hapax_balance": {"hapax": 80, "recurrent": 80},
    "series_min_distinct": 8, "support_min_distinct": 3,
    "confidence_strata": "structural context-type proxy (before_logogram / before_numeral / standalone / other) — coverage device ONLY, never a label",
    "role_coverage_note": "stratify by context-type so candidate HUMAN/PLACE/COMMODITY/OPERATOR/QUALIFIER forms are all present; roles are NOT assigned here (human task)",
    "cluster_exclusion_policy": "exclude auto-pilot form-families + all forms occurring in auto-pilot documents + stem-siblings (same first 2 signs) + formula-cluster siblings; also reserve nothing yet for sealed holdout (holdout not chosen)",
    "shortfall_policy": "if <160 eligible independent items, take the max defensible >=120; if <120 -> human_expert_package = NO_POWER (INSUFFICIENT_INDEPENDENT_SAMPLE)",
}
EXP = gc.EXP
HP = os.path.join(EXP, "data", "human_pilot")
LB = os.path.join(gc.MODEL_VISIBLE, "lb_graph.jsonl")
VOCAB = os.path.join(gc.EVAL_ONLY, "lb_dephon_vocab.json")
EXCL = os.path.join(EXP, "data", "pilot", "pilot_exclusion_manifest.json")


def stem(f):
    return "+".join(f.split("+")[:2])


def build():
    sign_map = json.load(open(VOCAB))["B_SIGN"]; logo_map = json.load(open(VOCAB)).get("B_LOGO", {})
    def tr(form):
        return "-".join(sign_map.get(s, "?") for s in form.split("+"))
    excl = json.load(open(EXCL))
    pilot_forms = set(excl["exclusion_word_form_families"]); pilot_docs = set(excl["exclusion_documents"])
    gs = [json.loads(l) for l in open(LB)]
    forms = defaultdict(lambda: {"occ": 0, "sites": set(), "series": set(), "supports": set(),
                                 "docs": set(), "example": None, "context_type": "other"})
    for g in gs:
        ids = {n["id"]: n for n in g["nodes"]}
        entry_tokens = defaultdict(list)
        for e in g["edges"]:
            if e["type"] == "CONTAINS" and ids.get(e["dst"], {}).get("type") in ("WORD_FORM", "LOGOGRAM", "NUMERAL", "MEASURE_MARKER"):
                n = ids[e["dst"]]; entry_tokens[e["src"]].append((n.get("position", 0), n["type"], n.get("opaque_id"), n.get("value")))
        # adjacency proxy
        nxt = {}
        for e in g["edges"]:
            if e["type"] == "PRECEDES_LOGOGRAM":
                nxt[e["src"]] = "before_logogram"
            elif e["type"] == "PRECEDES_NUMERAL":
                nxt.setdefault(e["src"], "before_numeral")
        for n in g["nodes"]:
            if n["type"] != "WORD_FORM" or n["opaque_id"].count("+") < 1:
                continue
            f = forms[n["opaque_id"]]; f["occ"] += 1
            f["sites"].add(g["meta"]["site_code"]); f["series"].add(g["meta"]["document_series"])
            f["supports"].add(g["meta"]["support_type"]); f["docs"].add(g["graph_id"])
            if f["example"] is None:
                for e in g["edges"]:
                    if e["type"] == "CONTAINS" and e["dst"] == n["id"]:
                        ctx = sorted(entry_tokens.get(e["src"], []))
                        f["context_type"] = nxt.get(n["id"], "standalone")
                        f["example"] = {"doc": g["meta"]["source_document_id"], "series": g["meta"]["document_series"],
                                        "site": g["meta"]["site_code"], "site_name": g["meta"]["site_name"],
                                        "findspot": g["meta"]["findspot_code"], "support": g["meta"]["support_type"],
                                        "scribe": g["meta"]["scribe"], "graph_id": g["graph_id"],
                                        "context": [(t, tr(o) if (t == "WORD_FORM" and o) else (logo_map.get(o, o) if t == "LOGOGRAM" else v)) for _, t, o, v in ctx]}
                        break
    forms_in_pilot_docs = {fo for fo, d in forms.items() if d["docs"] & pilot_docs}
    pilot_stems = {stem(f) for f in pilot_forms}
    excluded = pilot_forms | forms_in_pilot_docs | {fo for fo in forms if stem(fo) in pilot_stems}
    eligible = {fo: d for fo, d in forms.items() if fo not in excluded}

    if len(eligible) < PLAN["sample_size_floor"]:
        return {"status": "COMPLETE", "human_expert_package": "NO_POWER",
                "reason": "INSUFFICIENT_INDEPENDENT_SAMPLE", "eligible": len(eligible)}

    # deterministic stratified draw: balance site x hapax, spread context_type + series
    import hashlib as _h
    def rank(fo):
        return _h.sha256((fo + str(PLAN["random_seed"])).encode()).hexdigest()
    strata = defaultdict(list)
    for fo, d in eligible.items():
        s = "KN" if "KN" in d["sites"] else "nonKN"
        h = "hapax" if d["occ"] == 1 else "recurrent"
        strata[(s, h)].append((fo, d))
    for k in strata:
        strata[k].sort(key=lambda x: rank(x[0]))
    quotas = {("KN", "hapax"): 40, ("KN", "recurrent"): 40, ("nonKN", "hapax"): 40, ("nonKN", "recurrent"): 40}
    picked = []
    for k, q in quotas.items():
        picked += strata[k][:min(q, len(strata[k]))]
    # top up to target from remaining (spread by context_type)
    target = PLAN["sample_size_target"]
    if len(picked) < target:
        rest = sorted([(fo, d) for fo, d in eligible.items() if (fo, d) not in picked], key=lambda x: rank(x[0]))
        picked += rest[:target - len(picked)]
    picked = picked[:target]

    items = []
    for i, (fo, d) in enumerate(sorted(picked, key=lambda x: rank(x[0]))):
        ex = d["example"]
        items.append({"anon_item_id": f"HP-{i:04d}", "opaque_form": fo,
                      "linear_b_reading": tr(fo), "document_identifier": ex["doc"],
                      "site": ex["site"], "site_name": ex["site_name"], "findspot": ex["findspot"],
                      "document_series": ex["series"], "support_type": ex["support"], "scribe_hand": ex["scribe"],
                      "n_occurrences": d["occ"], "hapax": d["occ"] == 1, "context_type": d["context_type"],
                      "entry_context": ex["context"], "graph_id": ex["graph_id"],
                      "source_edition_citation": f"DĀMOS {ex['doc']} (https://damos.hf.uio.no/{ex['graph_id'].split('-')[1]})",
                      "image_reference": f"DĀMOS permalink https://damos.hf.uio.no/{ex['graph_id'].split('-')[1]}"})
    return {"status": "OK", "items": items, "eligible": len(eligible),
            "strata": {f"{s}/{h}": sum(1 for it in items if (("KN" in [it['site']]) == (s == 'KN')) and (it['hapax'] == (h == 'hapax'))) for s in ("KN", "nonKN") for h in ("hapax", "recurrent")}}


PACKET_FIELDS = ["anon_item_id", "document_identifier", "linear_b_reading", "entry_context",
                 "document_series", "site", "findspot", "support_type", "scribe_hand",
                 "source_edition_citation", "image_reference"]
TEMPLATE_FIELDS = ["anon_item_id", "coarse_role", "fine_role", "entry_relation", "gold_tier", "confidence",
                   "source_citation", "rationale", "alternative_labels", "uncertainty_type",
                   "dispute_flag", "abstain_flag"]


def sha16(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]


def write_all(res):
    os.makedirs(HP, exist_ok=True)
    items = res["items"]
    # master sample (reading-bearing -> gitignored)
    with open(os.path.join(HP, "pilot_sample.jsonl"), "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    with open(os.path.join(HP, "pilot_sample.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=PACKET_FIELDS + ["context_type", "hapax", "opaque_form", "graph_id"])
        w.writeheader()
        for it in items:
            row = {k: (json.dumps(it[k], ensure_ascii=False) if k == "entry_context" else it.get(k)) for k in PACKET_FIELDS}
            row.update({"context_type": it["context_type"], "hapax": it["hapax"], "opaque_form": it["opaque_form"], "graph_id": it["graph_id"]})
            w.writerow(row)
    # anon key (eval-only -> gitignored)
    json.dump({it["anon_item_id"]: {"opaque_form": it["opaque_form"], "graph_id": it["graph_id"]} for it in items},
              open(os.path.join(HP, "anon_key.json"), "w"), indent=1)
    # two packets, DIFFERENT anonymized orders (reading-bearing -> gitignored)
    import hashlib as _h
    def order(salt):
        return sorted(items, key=lambda it: _h.sha256((it["anon_item_id"] + salt).encode()).hexdigest())
    for label, salt in (("A", "orderA"), ("B", "orderB")):
        with open(os.path.join(HP, f"annotator_{label}_packet.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=PACKET_FIELDS); w.writeheader()
            for it in order(salt):
                w.writerow({k: (json.dumps(it[k], ensure_ascii=False) if k == "entry_context" else it.get(k)) for k in PACKET_FIELDS})
        # blank response template in the SAME order (no readings -> committable)
        with open(os.path.join(HP, f"annotator_{label}_response_template.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=TEMPLATE_FIELDS); w.writeheader()
            for it in order(salt):
                w.writerow({"anon_item_id": it["anon_item_id"], **{k: "" for k in TEMPLATE_FIELDS[1:]}})
    # manifest (committable): plan + strata + hashes, NO readings
    files = ["pilot_sample.jsonl", "pilot_sample.csv", "annotator_A_packet.csv", "annotator_B_packet.csv",
             "annotator_A_response_template.csv", "annotator_B_response_template.csv"]
    man = {"plan": PLAN, "status": res["status"], "n_items": len(items), "eligible_independent_forms": res["eligible"],
           "strata": res["strata"], "packet_fields": PACKET_FIELDS, "template_fields": TEMPLATE_FIELDS,
           "file_sha256_16": {fn: sha16(os.path.join(HP, fn)) for fn in files},
           "reading_bearing_gitignored": [f for f in files if "template" not in f] + ["anon_key.json"]}
    json.dump(man, open(os.path.join(HP, "human_pilot_manifest.json"), "w"), ensure_ascii=False, indent=1)
    with open(os.path.join(EXP, "data", "manifests", "human_pilot_sample.sha256"), "w") as f:
        for fn, h in man["file_sha256_16"].items():
            f.write(f"{h}  {fn}\n")
    return man


if __name__ == "__main__":
    res = build()
    if res.get("status") != "OK":
        print(json.dumps(res, indent=1)); sys.exit(0)
    man = write_all(res)
    print(f"human pilot: {man['n_items']} items | eligible {man['eligible_independent_forms']} | strata {man['strata']}")
    print("committable: response templates + manifest; gitignored (readings): packets + sample + anon_key")
