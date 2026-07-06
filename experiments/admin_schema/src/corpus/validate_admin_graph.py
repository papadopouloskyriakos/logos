#!/usr/bin/env python3
"""Validate a graph JSONL against the canonical schema + the blinding firewall (Stage 4 acceptance).

Checks: (1) required top-level keys; (2) node/edge type ∈ enum; (3) NO forbidden semantic/phonetic field
names anywhere in the model-visible object; (4) provenance retained; (5) no opaque_id leaks a sound value
(opaque IDs must match B_SIGN/B_LOGO/B_MEAS/A_SIGN_ or composite). Returns (ok, report).
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import graph_common as gc

OPAQUE_RE = re.compile(r"^(?:[AB]_(?:SIGN|LOGO|MEAS|QUAL)_\d{3}|A_SIGN_UNK|B_SIGN_UNK|A_LOGO_UNRESOLVED)(?:\+(?:[AB]_(?:SIGN|LOGO|MEAS)_\d{3}))*$")
FC_RE = re.compile(r"^FC_[0-9a-f]{16}$")


def _forbidden_hit(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            kl = str(k).lower()
            for bad in gc.FORBIDDEN_FIELD_SUBSTRINGS:
                if bad in kl:
                    return f"{path}.{k} (forbidden field name '{bad}')"
            r = _forbidden_hit(v, f"{path}.{k}")
            if r:
                return r
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            r = _forbidden_hit(v, f"{path}[{i}]")
            if r:
                return r
    return None


def validate_graph(g):
    errs = []
    for k in ("graph_id", "script", "meta", "nodes", "edges", "provenance"):
        if k not in g:
            errs.append(f"missing top-level key {k}")
    if g.get("script") not in ("LINEAR_B", "LINEAR_A"):
        errs.append(f"bad script {g.get('script')}")
    for n in g.get("nodes", []):
        if n.get("type") not in gc.NODE_TYPES:
            errs.append(f"bad node type {n.get('type')}")
        oid = n.get("opaque_id")
        if oid and not (OPAQUE_RE.match(oid) or FC_RE.match(oid)):
            errs.append(f"suspicious opaque_id {oid!r} (possible sound leak)")
    for e in g.get("edges", []):
        if e.get("type") not in gc.EDGE_TYPES:
            errs.append(f"bad edge type {e.get('type')}")
    for k in ("source_record_id", "source_version", "source_hash", "builder_version", "build_timestamp"):
        if k not in g.get("provenance", {}):
            errs.append(f"missing provenance.{k}")
    hit = _forbidden_hit(g)
    if hit:
        errs.append(f"FORBIDDEN FIELD: {hit}")
    return errs


def validate_file(path, limit=None):
    n = 0
    all_errs = []
    for i, line in enumerate(open(path, encoding="utf-8")):
        if limit and i >= limit:
            break
        n += 1
        errs = validate_graph(json.loads(line))
        if errs:
            all_errs.append((i, errs))
    return {"file": os.path.basename(path), "graphs_checked": n, "invalid": len(all_errs),
            "errors": all_errs[:10]}


if __name__ == "__main__":
    for f in ("lb_graph.jsonl", "la_graph.jsonl"):
        p = os.path.join(gc.MODEL_VISIBLE, f)
        if os.path.exists(p):
            r = validate_file(p)
            print(f"{r['file']}: checked {r['graphs_checked']}, invalid {r['invalid']}")
            for i, errs in r["errors"]:
                print(f"  graph {i}: {errs[:3]}")
