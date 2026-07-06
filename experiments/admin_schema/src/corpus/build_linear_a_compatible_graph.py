#!/usr/bin/env python3
"""Instantiate the SAME canonical schema for Linear A — STRUCTURAL DRY-RUN ONLY (Stage 4 acceptance #5).

Proves the transferable schema instantiates for Linear A and reports missing feature channels. Produces NO
semantic output: no roles, no rankings, no probabilities, no readings. Linear A signs get their OWN opaque
vocab (A_SIGN_NNN) — NEVER merged with the Linear B vocab (§II-E). Silver LA `signs` = list of words (each a
list of sign labels); no scribe / numerals / layout coordinates in silver → those channels are reported
missing, not fabricated.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import graph_common as gc

SILVER = os.path.join(gc.MAIN_ROOT, "corpus", "silver", "inscriptions.json")


def run():
    recs = json.load(open(SILVER, encoding="utf-8"))
    vocab = gc.OpaqueVocab("A_SIGN")
    for r in recs:
        for word in r.get("signs") or []:
            for s in word:
                vocab.add(str(s))
    vocab.freeze()
    graphs = []
    for r in recs:
        gid = f"LA-{r['id']}"
        doc_id = f"{gid}:DOC"
        nodes = [{"id": doc_id, "type": "DOCUMENT", "damage_flag": False}]
        edges = []
        tok = sign = 0
        prev_tok = None
        for wi, word in enumerate(r.get("signs") or [], 1):
            entry_id = f"{gid}:E{wi}"
            nodes.append({"id": entry_id, "type": "ENTRY", "position": wi, "damage_flag": False})
            edges.append({"src": doc_id, "dst": entry_id, "type": "CONTAINS"})
            tok += 1
            wid = f"{gid}:T{tok}"
            form_op = "+".join(vocab.opaque(str(s)) for s in word) or "A_SIGN_UNK"
            nodes.append({"id": wid, "type": "WORD_FORM", "position": wi, "opaque_id": form_op,
                          "value": None, "damage_flag": False, "uncertain_flag": False,
                          "uncertain_boundary_flag": False, "n_alternatives": 0})
            edges.append({"src": entry_id, "dst": wid, "type": "CONTAINS"})
            if prev_tok:
                edges.append({"src": prev_tok, "dst": wid, "type": "NEXT_TOKEN"})
                edges.append({"src": wid, "dst": prev_tok, "type": "PREVIOUS_TOKEN"})
            prev_tok = wid
            for si, s in enumerate(word, 1):
                sid = f"{gid}:S{sign}"; sign += 1
                nodes.append({"id": sid, "type": "SIGN", "position": si, "opaque_id": vocab.opaque(str(s)),
                              "damage_flag": False, "uncertain_flag": False, "allograph_class": None})
                edges.append({"src": wid, "dst": sid, "type": "CONTAINS"})
        meta = {"source_document_id": r["id"], "document_series": None, "document_subseries": None,
                "document_set": None, "support_type": r.get("support"), "site": r.get("site"),
                "findspot": None, "chronological_phase": r.get("context"), "scribe": None,
                "n_sides": 1, "n_rows": 1, "damage_flag": False, "joined_fragment_cluster": None}
        prov = {"source_record_id": r["id"], "source_version": "logos-silver-la",
                "source_hash": gc.content_hash(json.dumps(r.get("signs"), ensure_ascii=False)),
                "builder_version": gc.BUILDER_VERSION, "build_timestamp": "DETERMINISTIC",
                "uncertainty_provenance": "silver LA (structural dry-run; no numerals/logograms/layout channel)"}
        graphs.append({"graph_id": gid, "script": "LINEAR_A", "meta": meta, "nodes": nodes, "edges": edges, "provenance": prov})
    os.makedirs(gc.MODEL_VISIBLE, exist_ok=True); os.makedirs(gc.EVAL_ONLY, exist_ok=True)
    with open(os.path.join(gc.MODEL_VISIBLE, "la_graph.jsonl"), "w", encoding="utf-8") as f:
        for g in graphs:
            f.write(json.dumps(g, ensure_ascii=False, sort_keys=True) + "\n")
    json.dump({"A_SIGN": vocab.eval_map()}, open(os.path.join(gc.EVAL_ONLY, "la_dephon_vocab.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1, sort_keys=True)
    missing = ["NUMERAL", "FRACTION", "LOGOGRAM", "MEASURE_MARKER", "SCRIBE", "ROW/layout-coordinates", "DOCUMENT_SERIES"]
    print(f"LA graphs: {len(graphs)}  | A_SIGN vocab: {len(vocab.eval_map())}  (separate from LB)")
    print(f"missing channels in silver LA (reported, not fabricated): {missing}")
    return graphs, missing


if __name__ == "__main__":
    run()
