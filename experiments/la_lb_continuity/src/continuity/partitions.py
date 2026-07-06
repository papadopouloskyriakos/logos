#!/usr/bin/env python3
"""§II metadata-only freeze clarifications — mutually-exclusive partitions, ARKH policy, unit of analysis.

Reads the frozen packets READ-ONLY and re-expresses membership without changing it:
  PRIMARY_B (11)  ·  SENSITIVITY_C_ADDITIONAL (33)  ·  NEGATIVE_CONTROL (21)  ·  QUARANTINED (1)  = 66
PRIMARY_PLUS_SENSITIVITY = PRIMARY_B ∪ SENSITIVITY_C_ADDITIONAL (constructed programmatically).
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(__file__))
import cfg  # noqa: E402

# frozen inclusion_set (packet A) -> base partition name
_BASE = {"PRIMARY": "PRIMARY_B", "SENSITIVITY_1": "SENSITIVITY_C_ADDITIONAL",
         "NEGATIVE_CONTROL": "NEGATIVE_CONTROL", "QUARANTINED": "QUARANTINED"}


def load_candidates():
    return [json.loads(l) for l in open(cfg.LA_PACKET, encoding="utf-8")]


def load_targets():
    return [json.loads(l) for l in open(cfg.LB_PACKET, encoding="utf-8")]


def base_partition(c):
    return _BASE[c["inclusion_set"]]


def gorila_seq(raw_ids):
    """raw sign IDs -> comparable GORILA tokens. AB## -> int ##  ·  A### -> ('A',###) (LA-only namespace)
    ·  *## -> int ##  ·  ?X -> the raw string. LA AB## and LB *## share the int → the identity axis."""
    out = []
    for s in raw_ids:
        if s.startswith("AB") and s[2:].isdigit():
            out.append(int(s[2:]))
        elif s.startswith("*") and s[1:].isdigit():
            out.append(int(s[1:]))
        elif s.startswith("A") and s[1:].isdigit():
            out.append(("A", int(s[1:])))          # A-series: LA-specific, no LB homomorph
        else:
            out.append(s)                           # ?logogram / unmapped
    return tuple(out)


def site_assignment(c):
    return "AMBIGUOUS_ARKH" if c.get("site_ambiguity") else c.get("site_canonical", c.get("site_raw"))


def partitioned():
    """Return dict partition -> list of candidate rows (mutually exclusive)."""
    cands = load_candidates()
    parts = {}
    for c in cands:
        parts.setdefault(base_partition(c), []).append(c)
    return parts


def primary_plus_sensitivity():
    """Deterministic union used by B+C sensitivity analyses — sorted by candidate_id."""
    p = partitioned()
    union = p.get("PRIMARY_B", []) + p.get("SENSITIVITY_C_ADDITIONAL", [])
    return sorted(union, key=lambda c: c["candidate_id"])


def unit_summary():
    """Unit of analysis = unique word form (one row per candidate). Effective-independence bookkeeping."""
    cands = load_candidates()
    raw_attest = sum(c["internal_context"]["occ"] for c in cands)
    single_site_clusters = sum(1 for c in cands
                               if c["internal_context"]["n_docs"] > 1 and c["internal_context"]["n_sites"] == 1)
    cross_site = sum(1 for c in cands if c["internal_context"]["n_sites"] >= 2)
    return {"unique_forms": len(cands), "raw_document_attestations": raw_attest,
            "effective_independent_units": len(cands),          # 1 per unique form (no tablet multiplication)
            "single_site_repeated_form_clusters": single_site_clusters,
            "cross_site_forms": cross_site}


if __name__ == "__main__":
    cfg.verify_inputs()
    p = partitioned()
    counts = {k: len(v) for k, v in sorted(p.items())}
    print("base partitions:", counts, " sum:", sum(counts.values()))
    print("PRIMARY_PLUS_SENSITIVITY:", len(primary_plus_sensitivity()))
    print("ARKH-ambiguous candidates:", sum(1 for c in load_candidates() if c.get("site_ambiguity")))
    print("unit summary:", unit_summary())
    print("targets:", len(load_targets()))
