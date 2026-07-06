#!/usr/bin/env python3
"""Build the canonical transferable document graph for Linear B from DĀMOS (Stage 4).

De-phoneticises: every syllabogram/logogram/metrogram -> an opaque graphic ID (B_SIGN/B_LOGO/B_MEAS_NNN);
the id<->sound maps are written to data/evaluation_only/ ONLY. The model-visible graph (data/model_visible/
lb_graph.jsonl) carries opaque IDs + structure + non-semantic metadata. Deterministic: same input -> same
bytes. Joined fragments and repeated formulae are grouped (not counted independent).
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import graph_common as gc

DAMOS = os.path.join(gc.MAIN_ROOT, "corpus", "bronze", "linearb", "damos", "items.jsonl")
LINE_RE = re.compile(r"^\s*\.([0-9]+)([a-z]?)\s*(.*)$")
NUM_RE = re.compile(r"^[0-9]+$")
LOGO_RE = re.compile(r"^(\*[0-9]+[A-Z]*|[A-Z]{2,}[0-9]*)$")   # ideogram *NNN or UPPERCASE(+digits)
METRO_RE = re.compile(r"^[A-Z]$")                              # single uppercase metrogram
SYLL_RE = re.compile(r"^[a-z][a-z0-9]*$")                      # transliterated syllabogram
FRAC_RE = re.compile(r"^(?:[A-Z]{1,3}\d?|½|¼|⅓)$")            # crude; fractions handled as opaque markers


def load_damos():
    return [json.loads(l) for l in open(DAMOS, encoding="utf-8")]


def build_vocabs(recs):
    syll, logo, meas, qual = (gc.OpaqueVocab("B_SIGN"), gc.OpaqueVocab("B_LOGO"),
                              gc.OpaqueVocab("B_MEAS"), gc.OpaqueVocab("B_QUAL"))
    for r in recs:
        for line in (r["item"].get("content") or "").splitlines():
            m = LINE_RE.match(line)
            body = m.group(3) if m else line
            for raw in re.split(r"\s+", body):
                if not raw:
                    continue
                bare, _, _ = gc.strip_marks(raw)
                base = bare.split(":")[0]                      # OVIS:f -> OVIS
                if ":" in bare and bare.split(":")[1]:
                    qual.add(bare.split(":")[1])              # de-phoneticise the qualifier too
                if "-" in base:                               # a word -> its syllabograms
                    for s in base.split("-"):
                        s = s.strip()
                        if SYLL_RE.match(s) and s not in gc.EDITORIAL_TOKENS:
                            syll.add(s)
                elif NUM_RE.match(base) or not base:
                    continue
                elif LOGO_RE.match(base):
                    logo.add(base)
                elif METRO_RE.match(base):
                    meas.add(base)
                elif SYLL_RE.match(base) and base not in gc.EDITORIAL_TOKENS:
                    syll.add(base)
    return syll.freeze(), logo.freeze(), meas.freeze(), qual.freeze()


def classify(raw, syll, logo, meas, qual):
    """-> (kind, payload) for one whitespace token. kind in word/logo/meas/num/frac/divider/editorial/other."""
    bare, dmg, unc = gc.strip_marks(raw)
    if raw.strip() in ("/", ","):
        return "divider", (raw.strip(), dmg, unc)
    base = bare.split(":")[0]
    q = qual.opaque(bare.split(":")[1]) if (":" in bare and bare.split(":")[1]) else None
    if not base:
        return "other", (bare, dmg, unc, None)
    if base in gc.EDITORIAL_TOKENS or base.rstrip(".") in gc.EDITORIAL_TOKENS:
        return "editorial", (base, dmg, unc)
    if NUM_RE.match(base):
        return "num", (int(base), dmg, unc)
    if "-" in base and all(SYLL_RE.match(s) or not s for s in base.split("-")):
        signs = [syll.opaque(s) for s in base.split("-") if s]
        return "word", (signs, base.count("-") + 1, dmg, unc)
    if LOGO_RE.match(base):
        return "logo", (logo.opaque(base), q, dmg, unc)
    if METRO_RE.match(base):
        return "meas", (meas.opaque(base), dmg, unc)
    if SYLL_RE.match(base):
        return "word", ([syll.opaque(base)], 1, dmg, unc)
    return "other", (bare, dmg, unc, q)


def build_doc(rec, syll, logo, meas, qual, formidx):
    it = rec["item"]
    gid = f"LB-{rec['_id']}"
    content = it.get("content") or ""
    heading = it.get("heading") or ""
    nodes, edges = [], []
    doc_id = f"{gid}:DOC"
    joined = heading.split("(")[0].strip() if "+" in heading else None
    doc_dmg = "[" in content or "]" in content or "mut" in content
    nodes.append({"id": doc_id, "type": "DOCUMENT", "damage_flag": doc_dmg})

    def add_edge(s, d, t):
        edges.append({"src": s, "dst": d, "type": t})

    rows = content.splitlines()
    row_nodes = []
    entry_ctr = tok_ctr = sign_ctr = 0
    prev_entry = None
    row_index = 0
    for line in rows:
        m = LINE_RE.match(line)
        body = m.group(3) if m else line
        if not body.strip():
            continue
        row_index += 1
        row_id = f"{gid}:R{row_index}"
        rdmg = "[" in line or "]" in line
        nodes.append({"id": row_id, "type": "ROW", "position": row_index, "damage_flag": rdmg})
        add_edge(doc_id, row_id, "CONTAINS")
        row_nodes.append(row_id)
        # segment row into entries by '/' dividers
        segments = re.split(r"\s+/\s+", body)
        for seg in segments:
            toks = [t for t in re.split(r"\s+", seg) if t]
            if not toks:
                continue
            entry_ctr += 1
            entry_id = f"{gid}:E{entry_ctr}"
            nodes.append({"id": entry_id, "type": "ENTRY", "position": entry_ctr, "damage_flag": rdmg})
            add_edge(row_id, entry_id, "CONTAINS")
            add_edge(doc_id, entry_id, "SAME_DOCUMENT")
            if prev_entry:
                add_edge(prev_entry, entry_id, "NEXT_ENTRY")
                add_edge(entry_id, prev_entry, "PREVIOUS_ENTRY")
            prev_entry = entry_id
            entry_form_seq = []
            prev_tok = None
            pos = 0
            entry_nodes = []
            for raw in toks:
                kind, pl = classify(raw, syll, logo, meas, qual)
                if kind == "divider" or kind == "editorial":
                    continue
                pos += 1
                tok_ctr += 1
                nid = f"{gid}:T{tok_ctr}"
                if kind == "word":
                    signs, ln, dmg, unc = pl
                    form_op = "+".join(s for s in signs if s) or "B_SIGN_UNK"
                    entry_form_seq.append(form_op)
                    nodes.append({"id": nid, "type": "WORD_FORM", "position": pos, "opaque_id": form_op,
                                  "value": None, "damage_flag": dmg, "uncertain_flag": unc,
                                  "uncertain_boundary_flag": dmg, "n_alternatives": 0})
                    add_edge(entry_id, nid, "CONTAINS")
                    formidx.setdefault(form_op, []).append(nid)
                    for si, s in enumerate([s for s in signs if s], 1):
                        sid = f"{gid}:S{sign_ctr}"; sign_ctr += 1
                        nodes.append({"id": sid, "type": "SIGN", "position": si, "opaque_id": s,
                                      "damage_flag": dmg, "uncertain_flag": unc, "allograph_class": None})
                        add_edge(nid, sid, "CONTAINS")
                elif kind == "logo":
                    op, qv, dmg, unc = pl
                    nodes.append({"id": nid, "type": "LOGOGRAM", "position": pos, "opaque_id": op,
                                  "qualifier": qv, "damage_flag": dmg, "uncertain_flag": unc})
                    add_edge(entry_id, nid, "CONTAINS")
                elif kind == "meas":
                    op, dmg, unc = pl
                    nodes.append({"id": nid, "type": "MEASURE_MARKER", "position": pos, "opaque_id": op,
                                  "damage_flag": dmg, "uncertain_flag": unc})
                    add_edge(entry_id, nid, "CONTAINS")
                elif kind == "num":
                    val, dmg, unc = pl
                    nodes.append({"id": nid, "type": "NUMERAL", "position": pos, "value": val,
                                  "damage_flag": dmg, "uncertain_flag": unc})
                    add_edge(entry_id, nid, "CONTAINS")
                else:
                    bare = pl[0]
                    nodes.append({"id": nid, "type": "TOKEN", "position": pos, "opaque_id": None,
                                  "value": None, "damage_flag": pl[1], "uncertain_flag": pl[2]})
                    add_edge(entry_id, nid, "CONTAINS")
                entry_nodes.append((nid, kind))
                if prev_tok:
                    add_edge(prev_tok, nid, "NEXT_TOKEN")
                    add_edge(nid, prev_tok, "PREVIOUS_TOKEN")
                prev_tok = nid
            # adjacency-to-numeral / -to-logogram edges within entry
            for i in range(len(entry_nodes) - 1):
                (a, ka), (b, kb) = entry_nodes[i], entry_nodes[i + 1]
                if kb == "num":
                    add_edge(a, b, "PRECEDES_NUMERAL"); add_edge(b, a, "FOLLOWS_NUMERAL")
                if kb == "logo":
                    add_edge(a, b, "PRECEDES_LOGOGRAM"); add_edge(b, a, "FOLLOWS_LOGOGRAM")
            # formula cluster = hash of the opaque word-form sequence
            if entry_form_seq:
                fc = "FC_" + gc.content_hash("|".join(entry_form_seq))
                nodes.append({"id": f"{entry_id}:FC", "type": "FORMULA_CLUSTER", "opaque_id": fc})
                add_edge(entry_id, f"{entry_id}:FC", "SAME_FORMULA_CLUSTER")

    meta = {
        "source_document_id": heading,
        "document_series": it.get("series"), "document_subseries": it.get("subseries"),
        "document_set": str(it.get("set")) if it.get("set") is not None else None,
        "support_type": it.get("object"), "site": it.get("area_code"), "findspot": it.get("find_area"),
        "chronological_phase": str(it.get("chronogroup")) if it.get("chronogroup") is not None else None,
        "scribe": str(it.get("vasewriter")) if it.get("vasewriter") else None,
        "n_sides": 1, "n_rows": row_index, "damage_flag": doc_dmg, "joined_fragment_cluster": joined,
    }
    prov = {"source_record_id": rec["_id"], "source_version": gc.SOURCE_VERSION_DAMOS,
            "source_hash": gc.content_hash(content), "builder_version": gc.BUILDER_VERSION,
            "build_timestamp": "DETERMINISTIC", "uncertainty_provenance": "DAMOS editorial marks (brackets, underdots, mut/vac)"}
    return {"graph_id": gid, "script": "LINEAR_B", "meta": meta, "nodes": nodes, "edges": edges, "provenance": prov}


def run():
    recs = load_damos()
    syll, logo, meas, qual = build_vocabs(recs)
    os.makedirs(gc.MODEL_VISIBLE, exist_ok=True)
    os.makedirs(gc.EVAL_ONLY, exist_ok=True)
    formidx = {}
    graphs = [build_doc(r, syll, logo, meas, qual, formidx) for r in recs if (r["item"].get("content") or "").strip()]
    # REPEATS_FORM edges across documents for shared word-forms (cross-doc recurrence, grouped not independent)
    out = os.path.join(gc.MODEL_VISIBLE, "lb_graph.jsonl")
    with open(out, "w", encoding="utf-8") as f:
        for g in graphs:
            f.write(json.dumps(g, ensure_ascii=False, sort_keys=True) + "\n")
    # EVALUATION-ONLY: the de-phoneticisation keys + original transliteration
    json.dump({"B_SIGN": syll.eval_map(), "B_LOGO": logo.eval_map(), "B_MEAS": meas.eval_map(),
               "B_QUAL": qual.eval_map()},
              open(os.path.join(gc.EVAL_ONLY, "lb_dephon_vocab.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1, sort_keys=True)
    with open(os.path.join(gc.EVAL_ONLY, "lb_source_transliteration.jsonl"), "w", encoding="utf-8") as f:
        for r in recs:
            c = r["item"].get("content") or ""
            if c.strip():
                f.write(json.dumps({"graph_id": f"LB-{r['_id']}", "transliteration": c}, ensure_ascii=False) + "\n")
    # Global reference clusters: document-level entity nodes (SAME_* grouping) + REPEATS_FORM + joins.
    # SAME_SITE/SAME_SERIES/... are represented as shared membership in a reference cluster (efficient,
    # linear) rather than O(n^2) pairwise edges. Joined fragments + repeated forms are grouped here so they
    # are NOT treated as independent by default (Stage 4 acceptance #8).
    ref = {"SITE": {}, "DOCUMENT_SERIES": {}, "SCRIBE": {}, "OBJECT_OR_SUPPORT": {},
           "CHRONOLOGICAL_PHASE": {}, "JOINED_FRAGMENT_CLUSTER": {}, "REPEATS_FORM": {}}
    key = {"SITE": "site", "DOCUMENT_SERIES": "document_series", "SCRIBE": "scribe",
           "OBJECT_OR_SUPPORT": "support_type", "CHRONOLOGICAL_PHASE": "chronological_phase",
           "JOINED_FRAGMENT_CLUSTER": "joined_fragment_cluster"}
    for g in graphs:
        for etype, mkey in key.items():
            v = g["meta"].get(mkey)
            if v:
                ref[etype].setdefault(v, []).append(g["graph_id"])
    ref["REPEATS_FORM"] = {form: docs for form, wids in formidx.items()
                           if len({w.split(':')[0] for w in wids}) >= 2
                           for docs in [sorted({w.split(':')[0] for w in wids})]}
    json.dump(ref, open(os.path.join(gc.MODEL_VISIBLE, "lb_reference.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1, sort_keys=True)
    print(f"LB graphs: {len(graphs)}  | vocab: syll={len(syll.eval_map())} logo={len(logo.eval_map())} meas={len(meas.eval_map())}")
    print(f"distinct cross-doc word-forms: {len(formidx)}  | repeated (>=2 docs): {len(ref['REPEATS_FORM'])}")
    print(f"reference clusters: sites={len(ref['SITE'])} series={len(ref['DOCUMENT_SERIES'])} "
          f"scribes={len(ref['SCRIBE'])} phases={len(ref['CHRONOLOGICAL_PHASE'])} joins={len(ref['JOINED_FRAGMENT_CLUSTER'])}")
    return graphs


if __name__ == "__main__":
    run()
