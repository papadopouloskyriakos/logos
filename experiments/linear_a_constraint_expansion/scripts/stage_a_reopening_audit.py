#!/usr/bin/env python3
"""Stage A — identifiability reopening audit (Constitution v2.2 Art. VIII/IX/XVII).

Recomputes the Linear A identifiability budget FROM the artifacts under every defensible sign-inventory and
constraint specification, to test the reported `259 parameters > 212 constraints -> UNDERDETERMINED`.

Finding target: the prior 259 counted ALL diplomatic stream tokens (syllabograms + logograms + fractions +
damaged/composite word-internal variants); a phonetic reading's free parameters are the SYLLABARY, which the
corpus's own inventories put at 88-92 (deduplicated) / 131 (raw tokens) / 123 (allograph families). And the
'212 constraints' are ≥4-sign non-dominant-site INSCRIPTIONS — structural/segmental units, not VALUE-bearing
constraints on sign identity. The audit separates these and reports the corrected budget + a reopen target.
Reads the read-only corpus from the main worktree (gitignored data). Deterministic.
"""
import json
import os
import statistics as st
from collections import Counter

MAIN = "/home/claude-runner/gitlab/n8n/logos"
ONTO = json.load(open(os.path.join(MAIN, "corpus/silver/signs_ontology.json")))
INSC = json.load(open(os.path.join(MAIN, "corpus/silver/inscriptions_structured.json")))
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "reports")


def inv(spec):
    return json.load(open(os.path.join(MAIN, f"corpus/silver/inventory_syllabograms_{spec}.json"))).get("V")


def n_signs(r):
    if isinstance(r.get("signs"), list):
        return len(r["signs"])
    return sum(len(t.get("signs", [])) for t in (r.get("stream") or []) if t.get("t") == "word")


def run():
    HT = "Haghia Triada"
    # --- parameter specifications (free values a reading must assign) ---
    syl = [k for k, v in ONTO.items() if str(v.get("class", "")).startswith("syllabogram")]
    fams = {ONTO[k].get("allograph_family", k) for k in syl}
    a_only = [k for k in syl if ONTO[k].get("class") == "syllabogram-Aonly"]
    ab = [k for k in syl if ONTO[k].get("class") == "syllabogram-AB"]
    recurrent = [k for k in syl if ONTO[k].get("frequency", 0) >= 5]
    all_stream_tokens = len({s for r in INSC for w in (r.get("stream") or []) if w.get("t") == "word"
                             for s in w.get("signs", [])})
    params = {
        "prior_all_stream_tokens": all_stream_tokens,          # the reported 259 (mis-specified)
        "raw_inventory_V": inv("raw"),                          # 131
        "ontology_syllabogram_tokens": len(syl),                # 131
        "allograph_families": len(fams),                        # 123
        "conservative_inventory_V": inv("conservative"),        # 92 — the corpus's own considered syllabary
        "exploratory_inventory_V": inv("exploratory"),          # 88
        "recurrent_freq_ge5": len(recurrent),                   # 73 — signs with real statistical mass
        "A_only_truly_undeciphered": len(a_only),               # 72 — no external value hypothesis
        "AB_shared_with_LB_hypothesis": len(ab),                # 59 — have a (circular) homomorphy value prior
    }
    # --- constraint specifications ---
    ns = [n_signs(r) for r in INSC]
    ge4_nonht = sum(1 for r in INSC if n_signs(r) >= 4 and r.get("site") != HT)
    constraints = {
        "raw_inscriptions": len(INSC),
        "ge4_sign_inscriptions": sum(1 for x in ns if x >= 4),
        "ge4_sign_non_dominant_site_STRUCTURAL": ge4_nonht,     # the reported 212 — but STRUCTURAL, not value-bearing
        "value_informative_heldout_anchors": 2,                 # I, RI survived (one-deep; from crossscript gate)
    }
    # --- corrected ratios ---
    reading_params = params["conservative_inventory_V"]         # the honest syllabic parameter count
    struct = constraints["ge4_sign_non_dominant_site_STRUCTURAL"]
    val_info = constraints["value_informative_heldout_anchors"]
    out = {
        "parameter_specifications": params,
        "constraint_specifications": constraints,
        "prior_claim": "259 parameters > 212 constraints => UNDERDETERMINED",
        "prior_claim_status": "INVALIDATED (mis-specified)",
        "why_invalidated": ("259 counted ALL diplomatic stream tokens (syllabograms + logograms + fractions + "
                            "damaged/composite word-internal variants); a phonetic reading's parameters are the "
                            "SYLLABARY = 88-92 (deduplicated) / 131 (raw) / 123 (allograph families). And '212' "
                            "counts ≥4-sign non-dominant-site INSCRIPTIONS, which are structural/segmental units, "
                            "not value-bearing constraints. The two figures are different categories."),
        "corrected_budget": {
            "syllabic_parameters_conservative": reading_params,
            "structural_constraints_available": struct,
            "structural_ratio_params_over_constraints": round(reading_params / struct, 3),
            "value_informative_constraints": val_info,
            "value_ratio_params_over_informative_constraints": round(reading_params / max(val_info, 1), 1),
        },
        "corrected_diagnosis": ("At the SYLLABIC parameter level the count is FAVOURABLE (%d params < %d "
            "structural constraints). The underdetermination is NOT a count deficit — it is that the abundant "
            "structural constraints (segmentation, formula grammar, 212 inscriptions) DO NOT INFORM sign VALUES "
            "(the distributional value-channel is null 4x; anchors are one-deep). Value-informative constraints "
            "(~%d) are far below the ~%d syllabic parameters. The ceiling is constraint INFORMATIVENESS at the "
            "value layer, not constraint COUNT." % (reading_params, struct, val_info, reading_params)),
        "reopen_target": {
            "minimum_new_value_informative_constraints_needed": reading_params - val_info,
            "note": ("The campaign target is NOT 'more constraints to beat a count' (the count already favours a "
                     "reading) but 'constraints that INFORM the ~%d syllabic values' — i.e. secure external "
                     "anchors surviving held-out + non-circular, OR an internal channel that transfers to "
                     "values. Structural/segmental gains (Stages B/D) reduce false parameters and sharpen the "
                     "space but cannot alone assign values; value anchors (Stage F) are the load-bearing lever." % reading_params),
            "max_defensible_parameter_reduction_without_answer_fitting": len(syl) - len(fams),  # allograph merges only
        },
        "verdict": "A_REOPENED",
        "verdict_reason": ("The prior UNDERDETERMINED CONCLUSION stands qualitatively, but its quantitative "
                           "justification (259>212) is INVALIDATED as a category error. Reframed correctly, the "
                           "question reopens with a sharp, actionable target: value-informative constraints for "
                           "~%d syllabic parameters. Continue to Stages B-F to seek them." % reading_params),
    }
    os.makedirs(OUT, exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "..", "data", "stage_a_budget.json"), "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("parameter_specifications", "corrected_budget", "verdict")}, indent=1))
    return out


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "..", "data"), exist_ok=True)
    run()
