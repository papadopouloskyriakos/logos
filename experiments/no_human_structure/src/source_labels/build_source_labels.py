#!/usr/bin/env python3
"""Stage 3: deterministic source-derived Linear B label corpus (NO LLM, provenance-preserving).

Categories (Stage-3 ontology): REFERENCE_GOLD_A (secure NON-TRIVIAL semantic role) · STRUCTURAL_CONTROL_A
(notation-recoverable; NOT load-bearing eval) · WEAK_SILVER_B (probable/source-dependent) ·
DISPUTED_OR_EXCLUDED. Content-role labels come ONLY from the cited published indexes (lb_indexes); numeral/
logogram/total labels come from structure. Source labels are EVAL-only, never model-visible.
"""
import hashlib
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "admin_schema", "src", "corpus"))
import graph_common as gc
import lb_indexes as IDX

BUILDER = "source-labels-v1-2026-07-07"
OUT = os.path.join(gc.EXP.replace("admin_schema", "no_human_structure"), "data", "source_labels")
LB = os.path.join(gc.MODEL_VISIBLE, "lb_graph.jsonl")
VOCAB = os.path.join(gc.EVAL_ONLY, "lb_dephon_vocab.json")
PRIORITY = ["PLACE", "HUMAN_OR_INSTITUTION", "OPERATOR_OR_RELATION", "QUALIFIER", "DOCUMENT_STRUCTURE"]
NONTRIVIAL = {"HUMAN_OR_INSTITUTION", "PLACE", "OPERATOR_OR_RELATION", "QUALIFIER"}


def stem(form_opaque):
    return "+".join(form_opaque.split("+")[:-1]) or form_opaque   # drop final (inflectional) sign


def build():
    sign_map = json.load(open(VOCAB))["B_SIGN"]
    def tr(fo):
        return "-".join(sign_map.get(s, "?") for s in fo.split("+"))
    forms = defaultdict(lambda: {"occ": 0, "sites": set(), "series": set(), "docs": set()})
    n_numeral = n_logogram = 0
    for line in open(LB):
        g = json.loads(line)
        for n in g["nodes"]:
            if n["type"] == "WORD_FORM" and n["opaque_id"].count("+") >= 1:
                f = forms[n["opaque_id"]]; f["occ"] += 1
                f["sites"].add(g["meta"]["site_code"]); f["series"].add(g["meta"]["document_series"]); f["docs"].add(g["graph_id"])
            elif n["type"] == "NUMERAL":
                n_numeral += 1
            elif n["type"] == "LOGOGRAM":
                n_logogram += 1
    labels = []
    for i, (fo, d) in enumerate(sorted(forms.items())):
        t = tr(fo)
        hits = IDX.lookup(t)
        if not hits:
            continue                                              # unindexed -> no source label (never fabricate a PN)
        coarses = {h[1] for h in hits}
        if len(coarses) > 1:                                      # genuine cross-index conflict
            best = min(hits, key=lambda h: PRIORITY.index(h[1]) if h[1] in PRIORITY else 99)
            _, coarse, fine, ev, cat = best; dispute = "CONFLICT_RESOLVED_BY_PRIORITY"
        else:
            _, coarse, fine, ev, cat = hits[0]; dispute = "NONE"
        labels.append({
            "label_id": f"SL-{i:05d}", "document_id": sorted(d["docs"])[0], "form_id": fo,
            "coarse_role": coarse, "fine_role_if_available": fine, "label_category": cat,
            "evidence_basis": ev, "source_id": [h[0] for h in hits], "source_record": t,
            "source_citation": IDX.CITATION, "source_dependency_cluster": IDX.DEP_CLUSTER,
            "upstream_edition": IDX.UPSTREAM, "derivation_rule": "cited-index membership",
            "confidence": 0.9 if cat == "REFERENCE_GOLD_A" else (0.6 if cat == "WEAK_SILVER_B" else 0.95),
            "dispute_status": dispute, "builder_version": BUILDER,
            "n_occ": d["occ"], "sites": sorted(d["sites"]), "series": sorted(x for x in d["series"] if x),
            "lexical_family": t, "morphological_family": tr(stem(fo)),
            "nontrivial": coarse in NONTRIVIAL and ev != "STRUCTURAL_ONLY"})
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "linear_b_source_labels.jsonl"), "w", encoding="utf-8") as f:
        for l in labels:
            f.write(json.dumps(l, ensure_ascii=False, sort_keys=True) + "\n")
    # counts
    cat = Counter(l["label_category"] for l in labels)
    cat["STRUCTURAL_CONTROL_A(notation)"] = n_numeral + n_logogram
    by = lambda field: {c: Counter(l[field] if not isinstance(l[field], list) else "|".join(l[field])
                                   for l in labels if l["label_category"] == c) for c in
                        ("REFERENCE_GOLD_A", "WEAK_SILVER_B", "STRUCTURAL_CONTROL_A", "DISPUTED_OR_EXCLUDED")}
    ga = [l for l in labels if l["label_category"] == "REFERENCE_GOLD_A" and l["nontrivial"]]
    summary = {
        "builder_version": BUILDER, "n_word_form_labels": len(labels),
        "category_counts": dict(cat),
        "REFERENCE_GOLD_A_nontrivial": len(ga),
        "REFERENCE_GOLD_A_nontrivial_by_role": dict(Counter(l["coarse_role"] for l in ga)),
        "REFERENCE_GOLD_A_lexical_families": len({l["lexical_family"] for l in ga}),
        "REFERENCE_GOLD_A_morphological_families": len({l["morphological_family"] for l in ga}),
        "REFERENCE_GOLD_A_KN": sum(1 for l in ga if "KN" in l["sites"]),
        "REFERENCE_GOLD_A_nonKN": sum(1 for l in ga if any(s != "KN" for s in l["sites"])),
        "REFERENCE_GOLD_A_by_series": dict(Counter(s for l in ga for s in l["series"])),
        "role_by_category": {c: dict(v) for c, v in by("coarse_role").items()},
        "structural_control_notation_nodes": {"numerals": n_numeral, "logograms": n_logogram},
        "dependency_clusters": dict(Counter(l["source_dependency_cluster"] for l in labels)),
        "note": "content-role labels all in ONE SHARED_DECIPHERMENT dependency cluster; structural controls are edition-independent but NOT load-bearing (they are excluded from the semantic eval per §II)",
    }
    json.dump(summary, open(os.path.join(OUT, "source_labels_summary.json"), "w"), ensure_ascii=False, indent=1)
    sha = hashlib.sha256(open(os.path.join(OUT, "linear_b_source_labels.jsonl"), "rb").read()).hexdigest()[:16]
    os.makedirs(os.path.join(os.path.dirname(OUT), "manifests"), exist_ok=True)
    open(os.path.join(os.path.dirname(OUT), "manifests", "linear_b_source_labels.sha256"), "w").write(f"linear_b_source_labels {sha}\n")
    print(f"labels: {len(labels)} | categories {dict(cat)}")
    print(f"REFERENCE_GOLD_A non-trivial: {len(ga)} ({summary['REFERENCE_GOLD_A_nontrivial_by_role']}) | "
          f"lex-fam {summary['REFERENCE_GOLD_A_lexical_families']} morph-fam {summary['REFERENCE_GOLD_A_morphological_families']} | "
          f"KN {summary['REFERENCE_GOLD_A_KN']} nonKN {summary['REFERENCE_GOLD_A_nonKN']}")
    return summary


if __name__ == "__main__":
    build()
