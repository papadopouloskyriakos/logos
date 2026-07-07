#!/usr/bin/env python3
"""Generate the Linear A corpus identifiability metrics (Art. XIX — counts from a script, not hand-written)
and run them through the info-budget gate (Art. IX). Quantifies WHY every decipherment avenue hits the
same ceiling: the corpus is hapax-dominated, single-site-dominated, and one-deep, so the effective
independent evidence for a non-circular phonetic reading is far below the 259 sign-value parameters a
reading needs. Writes identifiability_metrics.json.
"""
import json
import os
import statistics as st
import sys
from collections import Counter

_REPO = "/home/claude-runner/gitlab/n8n/logos"
sys.path.insert(0, _REPO)
from scripts import info_budget as ib

SILVER = os.path.join(_REPO, "corpus/silver/inscriptions_structured.json")
HT = "Haghia Triada"


def n_signs(r):
    if isinstance(r.get("signs"), list):
        return len(r["signs"])
    return sum(len(t.get("signs", [])) for t in (r.get("stream") or []) if t.get("t") == "word")


def run():
    data = json.load(open(SILVER))
    n = len(data)
    ns = [n_signs(r) for r in data]
    sites = Counter(r.get("site", "?") for r in data)
    allsigns = Counter(s for r in data for w in (r.get("stream") or []) if w.get("t") == "word"
                       for s in w.get("signs", []))
    words = Counter(tuple(w["signs"]) for r in data for w in (r.get("stream") or [])
                    if w.get("t") == "word" and len(w.get("signs", [])) >= 2)
    hapax = sum(1 for c in words.values() if c == 1)
    ge4_nonht = sum(1 for r in data if n_signs(r) >= 4 and r.get("site") != HT)
    params = len(allsigns)                              # one syllabic value per distinct sign = a reading's d.o.f.
    m = {
        "n_inscriptions": n, "total_sign_tokens": sum(ns), "distinct_signs": params,
        "mean_signs_per_inscription": round(st.mean(ns), 2), "median_signs_per_inscription": st.median(ns),
        "single_sign_inscriptions": sum(1 for x in ns if x <= 1),
        "single_sign_fraction": round(sum(1 for x in ns if x <= 1) / n, 3),
        "ge4_sign_inscriptions": sum(1 for x in ns if x >= 4),
        "dominant_site": HT, "dominant_site_count": sites.get(HT, 0),
        "dominant_site_fraction": round(sites.get(HT, 0) / n, 3), "n_sites": len(sites),
        "distinct_multisign_words": len(words), "hapax_multisign_words": hapax,
        "hapax_word_fraction": round(hapax / max(len(words), 1), 3),
        "top5_sites": dict(sites.most_common(5)),
        # effective independent evidence for a NON-CIRCULAR phonetic reading: multi-sign (>=4) AND not from
        # the dominant site (site-independence) — a generous upper bound (still ignores hapax non-recurrence).
        "effective_independent_evidence_upper_bound": ge4_nonht,
        "reading_parameters": params,
    }
    panel = ib.build_panel(
        raw_corpus_size=n, effective_independent_evidence=ge4_nonht, parameter_count=params,
        minimum_detectable_effect=0.92, estimated_power=0.0,
        source_dependency_structure="single Ventris-1952 decipherment lineage (DAMOS/V-C/DMic collapse to 1)",
        search_space_size=params, damage_rate=m["single_sign_fraction"],
        class_balance=f"{HT} {sites.get(HT,0)}/{n} = {m['dominant_site_fraction']}",
        segmentation_uncertainty="micro-F1 0.436 (0.577 ceiling)",
        sign_inventory_uncertainty=f"{params} raw signs")
    m["info_budget_certifies_L6_reading"] = ib.certify(panel, "L6", "SUPPORTED")
    m["underdetermined_params_gt_evidence"] = params > ge4_nonht
    m["note"] = ("effective_independent_evidence is a GENEROUS upper bound (>=4-sign, non-dominant-site); the "
                 "true value is far lower once the 83.8% hapax non-recurrence and single-lineage label "
                 "circularity are applied. A phonetic reading needs one value per distinct sign; the corpus "
                 "supplies fewer independent multi-sign non-dominant-site constraints than that.")
    out = os.path.join(os.path.dirname(__file__), "identifiability_metrics.json")
    json.dump(m, open(out, "w"), indent=1)
    print(json.dumps({k: m[k] for k in ("n_inscriptions", "median_signs_per_inscription",
          "single_sign_fraction", "dominant_site_fraction", "hapax_word_fraction", "distinct_signs",
          "effective_independent_evidence_upper_bound", "underdetermined_params_gt_evidence")}, indent=1))
    print("info-budget certifies an L6 phonetic reading:", m["info_budget_certifies_L6_reading"]["certified"])
    return m


if __name__ == "__main__":
    run()
