#!/usr/bin/env python3
"""§XI final Egyptian-channel verdict — mechanical, from the corpus-build state.

status ∈ {INCOMPLETE, COMPLETE} ; egyptian_channel_readiness ∈ {NOT_READY, READY_FOR_PREREG_DRAFT,
NO_POWER, REJECT_SEARCH_ARCHITECTURE}. The gate cannot be scored past the load-bearing input: the
non-Cretan calibration corpus is not buildable (§III/§IV), so no model can be fit, validated, or
positive-controlled — hence no power/architecture assessment is possible."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import schema as SC  # noqa: E402


def decide():
    _, blocker = SC.build_corpus()
    corpus_buildable = blocker["buildable"]
    c = {
        "calibration_corpus_buildable": corpus_buildable,
        "model_fittable": corpus_buildable,                 # can't fit without a corpus
        "positive_control_evaluable": corpus_buildable,     # can't run without a frozen model
        "power_assessable": corpus_buildable,               # can't assess power without controls+nulls
        "design_frozen": True,                              # schema/rules/model-spec frozen (data-independent)
        "cretan_target_leakage": False,                     # excluded by rule + tested
        "is_a_power_question": False,                       # NO fittable-but-weak corpus exists to assess
        "is_a_source_extraction_blocker": True,             # Hoch OCR-corrupt + Kilani wrong-layer + Muchiki absent
    }
    # NO_POWER/REJECT require an evaluable model+controls; INCOMPLETE is the correct load-bearing-blocker verdict
    if corpus_buildable:
        status, readiness = "COMPLETE", "NOT_READY"         # (would be re-decided by downstream gates)
    else:
        status, readiness = "INCOMPLETE", "NOT_READY"
    return {
        "status": status, "egyptian_channel_readiness": readiness, "criteria": c,
        "why_not_no_power": "NO_POWER presupposes a fittable-but-weak corpus whose recovery/FP can be "
                            "measured. Here NO corpus can be populated to standard, so power is not "
                            "assessable — the honest verdict is INCOMPLETE (source/extraction blocker), "
                            "not a disguised NO_POWER.",
        "blocker": blocker,
        "recommendation": "RESOLVE ONE EXACT SOURCE BLOCKER (REQ-02b): supply a machine-readable Hoch 1994 "
                          "dataset, OR a transliteration-aware hand-verified Hoch subset of ≥~150 entries, "
                          "OR Muchiki 1999 in machine-readable form. The schema, inclusion rules, and model "
                          "prereg spec are frozen and will execute the fit→control→null→power→verdict gates "
                          "with no post-hoc freedom once the corpus can be populated. Do NOT run any real "
                          "Cretan/Linear A matching, preregister, or claim any sign value.",
    }


def run():
    return {"analysis": "egyptian-calibration-gate", "verdict": decide()}


if __name__ == "__main__":
    v = run()["verdict"]
    print("status:                    ", v["status"])
    print("egyptian_channel_readiness:", v["egyptian_channel_readiness"])
    print("source/extraction blocker: ", v["criteria"]["is_a_source_extraction_blocker"])
    print("recommendation:            ", v["recommendation"][:110], "…")
    import json
    RES = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "results"))
    os.makedirs(RES, exist_ok=True)
    json.dump(run(), open(os.path.join(RES, "final_verdict.json"), "w"), indent=1)
    print("saved results/final_verdict.json")
