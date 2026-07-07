#!/usr/bin/env python3
"""Validate a COMPLETED human-expert submission against its response template.

This NEVER fabricates a submission. If the completed file is absent it returns status=NO_SUBMISSION. It
validates schema/integrity only; it does not compute agreement (that is compare_human_annotations, and only
when BOTH genuine submissions exist).
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = os.path.normpath(os.path.join(HERE, "..", ".."))
HP = os.path.join(EXP, "data", "human_pilot")

COARSE = {"HUMAN_OR_INSTITUTION", "PLACE", "COMMODITY_OR_COUNTED_CATEGORY", "MEASURE_OR_QUANTITY",
          "OPERATOR_OR_RELATION", "QUALIFIER", "DOCUMENT_STRUCTURE", "UNKNOWN", "AMBIGUOUS", "MULTILABEL", "EXCLUDED"}
TIERS = {"GOLD_A", "GOLD_B", "GOLD_C", "GOLD_X"}
TEMPLATE_FIELDS = ["anon_item_id", "coarse_role", "fine_role", "entry_relation", "gold_tier", "confidence",
                   "source_citation", "rationale", "alternative_labels", "uncertainty_type",
                   "dispute_flag", "abstain_flag"]


def _rows(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def validate(label):
    tmpl_p = os.path.join(HP, f"annotator_{label}_response_template.csv")
    done_p = os.path.join(HP, "completed", f"annotator_{label}_completed.csv")
    if not os.path.exists(done_p):
        return {"label": label, "status": "NO_SUBMISSION", "path_expected": done_p}
    tmpl = _rows(tmpl_p); done = _rows(done_p)
    tmpl_ids = [r["anon_item_id"] for r in tmpl]
    done_ids = [r["anon_item_id"] for r in done]
    errs = []
    if set(done_ids) - set(tmpl_ids):
        errs.append(f"unknown item ids: {sorted(set(done_ids) - set(tmpl_ids))[:5]}")
    if set(tmpl_ids) - set(done_ids):
        errs.append(f"MISSING rows: {sorted(set(tmpl_ids) - set(done_ids))[:5]}")
    if len(done_ids) != len(set(done_ids)):
        errs.append("DUPLICATE rows")
    if done_ids != tmpl_ids:
        errs.append("item ORDER changed vs template (annotator must not reorder ids)")
    for r in done:
        if r.get("abstain_flag", "").strip().lower() in ("1", "true", "yes"):
            continue
        if r.get("coarse_role") and r["coarse_role"] not in COARSE:
            errs.append(f"{r['anon_item_id']}: invalid coarse_role {r['coarse_role']!r}")
        if r.get("gold_tier") and r["gold_tier"] not in TIERS:
            errs.append(f"{r['anon_item_id']}: invalid gold_tier {r['gold_tier']!r}")
        if r.get("gold_tier") in ("GOLD_A", "GOLD_B") and not r.get("source_citation", "").strip():
            errs.append(f"{r['anon_item_id']}: {r['gold_tier']} requires source_citation")
    # accidental model-generated / non-human heuristics (WARN, do not auto-accept as human)
    warns = []
    confs = [r.get("confidence", "").strip() for r in done if r.get("confidence", "").strip()]
    if confs and len(set(confs)) == 1:
        warns.append("all confidences identical — possible non-human/auto-fill; verify provenance")
    if any("model" in (r.get("rationale", "") + r.get("source_citation", "")).lower() and "generated" in
           (r.get("rationale", "") + r.get("source_citation", "")).lower() for r in done):
        warns.append("'model generated' marker present — reject as non-human")
    return {"label": label, "status": "VALID" if not errs else "INVALID", "n_rows": len(done),
            "errors": errs[:20], "provenance_warnings": warns}


if __name__ == "__main__":
    import json
    print(json.dumps([validate("A"), validate("B")], indent=1))
