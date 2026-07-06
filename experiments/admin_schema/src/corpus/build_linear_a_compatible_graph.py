#!/usr/bin/env python3
"""Instantiate the SAME canonical schema for Linear A — STRUCTURAL DRY-RUN ONLY (Stage 4/4.1).

Stage 4.1 Correction 3: recovers Linear A NUMERAL / ROW / ENTRY / WORD_FORM / SIGN / (opaque) LOGOGRAM
channels from the silver `stream` (see linear_a_structural_recovery). Produces NO semantic output: no roles,
rankings, probabilities, or readings. Linear A signs use their OWN opaque vocab (A_SIGN) — never merged with
Linear B; Linear A logograms are NOT equated with Linear B logograms of similar shape.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import graph_common as gc
import linear_a_structural_recovery as lar


def run():
    recs = lar.load_structured()
    vocab = lar.build_sign_vocab(recs)
    graphs = []
    channel_counts = {"NUMERAL": 0, "WORD_FORM": 0, "ROW": 0, "ENTRY": 0, "LOGOGRAM_OR_OTHER": 0, "SIGN": 0}
    for r in recs:
        gid = f"LA-{r['id']}"
        doc_id = f"{gid}:DOC"
        nodes = [{"id": doc_id, "type": "DOCUMENT", "damage_flag": False}]
        edges = []
        ci = ti = si = ri = 0
        prev_tok = None
        # rows split on row_break; entries split on entry_break; open a first row/entry lazily
        cur_row = cur_entry = None

        def open_row():
            nonlocal cur_row, ri
            ri += 1; cur_row = f"{gid}:R{ri}"
            nodes.append({"id": cur_row, "type": "ROW", "position": ri, "damage_flag": False})
            edges.append({"src": doc_id, "dst": cur_row, "type": "CONTAINS"})
            channel_counts["ROW"] += 1

        def open_entry():
            nonlocal cur_entry, ci
            if cur_row is None:
                open_row()
            ci += 1; cur_entry = f"{gid}:E{ci}"
            nodes.append({"id": cur_entry, "type": "ENTRY", "position": ci, "damage_flag": False})
            edges.append({"src": cur_row, "dst": cur_entry, "type": "CONTAINS"})
            channel_counts["ENTRY"] += 1

        for kind, pl in lar.stream_tokens(r):
            if kind == "row_break":
                cur_row = None; cur_entry = None; continue
            if kind == "entry_break":
                cur_entry = None; continue
            if cur_entry is None:
                open_entry()
            ti += 1; nid = f"{gid}:T{ti}"
            if kind == "word":
                form = "+".join(vocab.opaque(str(s)) for s in pl) or "A_SIGN_UNK"
                nodes.append({"id": nid, "type": "WORD_FORM", "position": ti, "opaque_id": form,
                              "value": None, "damage_flag": False, "uncertain_flag": False,
                              "uncertain_boundary_flag": False, "n_alternatives": 0})
                edges.append({"src": cur_entry, "dst": nid, "type": "CONTAINS"})
                channel_counts["WORD_FORM"] += 1
                for pos, s in enumerate(pl, 1):
                    sid = f"{gid}:S{si}"; si += 1
                    nodes.append({"id": sid, "type": "SIGN", "position": pos, "opaque_id": vocab.opaque(str(s)),
                                  "damage_flag": False, "uncertain_flag": False, "allograph_class": None})
                    edges.append({"src": nid, "dst": sid, "type": "CONTAINS"})
                    channel_counts["SIGN"] += 1
            elif kind == "num":
                nodes.append({"id": nid, "type": "NUMERAL", "position": ti, "value": pl,
                              "damage_flag": False, "uncertain_flag": False})
                edges.append({"src": cur_entry, "dst": nid, "type": "CONTAINS"})
                channel_counts["NUMERAL"] += 1
            elif kind == "other":
                # PRESENT_BUT_NOT_PARSED: logogram/fraction/measure, subclass unresolved in silver -> opaque
                nodes.append({"id": nid, "type": "LOGOGRAM", "position": ti, "opaque_id": "A_LOGO_UNRESOLVED",
                              "qualifier": None, "damage_flag": False, "uncertain_flag": True})
                edges.append({"src": cur_entry, "dst": nid, "type": "CONTAINS"})
                channel_counts["LOGOGRAM_OR_OTHER"] += 1
            else:
                continue
            if prev_tok:
                edges.append({"src": prev_tok, "dst": nid, "type": "NEXT_TOKEN"})
                edges.append({"src": nid, "dst": prev_tok, "type": "PREVIOUS_TOKEN"})
            prev_tok = nid
        meta = {"source_document_id": r["id"], "document_series": None, "document_subseries": None,
                "document_set": None, "support_type": r.get("support"),
                "site_code": r.get("site"), "site_name": r.get("site"),
                "site_mapping_source": "silver LA site field (named site, no prefix)",
                "site_mapping_confidence": "SECURE" if r.get("site") else "NO_SITE",
                "site_mapping_version": "la-site-v1", "findspot_code": None, "area_code_raw": None,
                "document_identifier_prefix": None, "current_document_identifier": r["id"],
                "historical_document_identifier": None,
                "chronological_phase": r.get("context"), "scribe": None, "scribe_source": None,
                "scribe_assignment_type": None, "scribe_crosswalk_version": None,
                "n_sides": 1, "n_rows": max(ri, 1), "damage_flag": False, "joined_fragment_cluster": None}
        prov = {"source_record_id": r["id"], "source_version": "logos-silver-la-structured",
                "source_hash": gc.content_hash(json.dumps(r.get("stream"), ensure_ascii=False)),
                "builder_version": gc.BUILDER_VERSION, "build_timestamp": "DETERMINISTIC",
                "uncertainty_provenance": "silver LA stream; 'other' subclass (logogram/fraction/measure) unresolved -> opaque"}
        graphs.append({"graph_id": gid, "script": "LINEAR_A", "meta": meta, "nodes": nodes, "edges": edges, "provenance": prov})
    os.makedirs(gc.MODEL_VISIBLE, exist_ok=True); os.makedirs(gc.EVAL_ONLY, exist_ok=True)
    with open(os.path.join(gc.MODEL_VISIBLE, "la_graph.jsonl"), "w", encoding="utf-8") as f:
        for g in graphs:
            f.write(json.dumps(g, ensure_ascii=False, sort_keys=True) + "\n")
    json.dump({"A_SIGN": vocab.eval_map()}, open(os.path.join(gc.EVAL_ONLY, "la_dephon_vocab.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1, sort_keys=True)
    print(f"LA graphs: {len(graphs)}  | A_SIGN vocab: {len(vocab.eval_map())} (separate from LB)")
    print(f"recovered channels: {channel_counts}")
    print(f"channel status: {lar.CHANNEL_STATUS}")
    return graphs, channel_counts


if __name__ == "__main__":
    run()
