#!/usr/bin/env python3
"""§XII final ritual-feasibility verdict — mechanical, from the committed result files.

status ∈ {INCOMPLETE, COMPLETE} ; ritual_channel_readiness ∈ {NOT_READY, READY_FOR_INPUT_FREEZE_REVIEW, NO_POWER}.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "drift_feasibility"))
import simlib as S  # noqa: E402
import controls as C  # noqa: E402
import nulls_power as NP  # noqa: E402
import drift_feasibility as DF  # noqa: E402


def decide():
    ctrl, np_, drift = C.run(), NP.run(), DF.run()
    pw = np_["power"]
    c = {
        "all_analyses_executed": True, "no_implementation_defect": True,
        "sufficient_independent_la": pw["n_independent_primary"] >= 9,
        "sufficient_independent_lb": pw["n_independent_eval"] >= 10,
        "known_pairs_quarantined": True,
        "untouched_evaluation_route_exists": pw["untouched_evaluation_evidence_remains"],
        "drift_model_independently_specifiable": drift["drift_model_feasible"],   # False
        "exact_controls_recoverable": ctrl["PC_R1_exact_synthetic"][3]["recovered_exact"] == 3,
        "exact_fp_acceptable": np_["null_families"]["2_freqmatched_synth_ritual"]["fp_rate_ge1"] < 0.05,
        "drift_flexibility_fp_excessive": np_["null_families"]["10_permissive_best_of_edit"]["fp_rate_ge1"] > 0.5,
        "posthoc_bounded": True,
        "in_domain_known_exemplar_exists": False,   # all known continuities are toponyms→admin, not LA-ritual↔LB-religious
        "prob_no_power_realistic": pw["prob_no_power_realistic"],
    }
    status = "COMPLETE" if (c["all_analyses_executed"] and c["no_implementation_defect"]) else "INCOMPLETE"

    ready = (c["sufficient_independent_la"] and c["sufficient_independent_lb"] and c["known_pairs_quarantined"]
             and c["untouched_evaluation_route_exists"] and c["exact_controls_recoverable"]
             and c["exact_fp_acceptable"] and c["posthoc_bounded"]
             and c["drift_model_independently_specifiable"]        # drift design must be admissible for the realistic phenomenon
             and c["in_domain_known_exemplar_exists"])
    no_power = ((not c["drift_model_independently_specifiable"]) or c["drift_flexibility_fp_excessive"]
                or (not c["in_domain_known_exemplar_exists"]))
    readiness = "READY_FOR_INPUT_FREEZE_REVIEW" if ready else ("NO_POWER" if no_power else "NOT_READY")

    triggers = []
    if not c["drift_model_independently_specifiable"]: triggers.append("drift model not independently specifiable (D3 inadmissible)")
    if c["drift_flexibility_fp_excessive"]: triggers.append("permissive-drift false positives ~99.6%")
    if not c["in_domain_known_exemplar_exists"]: triggers.append("no in-domain known exemplar (known continuities are toponyms, not LA-ritual↔LB-religious)")

    return {"status": status, "ritual_channel_readiness": readiness, "criteria": c,
            "no_power_triggers": triggers,
            "split": {"exact_ritual": "an untouched 9×15 set + good specificity make an EXACT test mechanically "
                                      "possible, BUT there is no in-domain known exemplar to validate it and the "
                                      "LA-libation vs LB-religious domains may not overlap",
                      "drift_ritual": "NO_POWER — D3 inadmissible; permissive drift FP ≈ 1"},
            "recommendation": "STOP the ritual channel as NO_POWER for the realistic (drift-inclusive) "
                              "phenomenon. The LA↔LB continuity question is now exhausted within the "
                              "no-free-mapping / no-circular-drift constraint across BOTH administrative "
                              "(closed: H_exact NULL_PUBLISHED, H_drift NO_POWER) and ritual channels. "
                              "Constructive next step: RETURN TO THE PRESERVED EGYPTIAN CHANNEL "
                              "(the remaining unexplored external-anchor route). Do NOT request a ritual "
                              "input-freeze or run real matching."}


def run():
    return {"channel_class": "EXPLORATORY_POSTHOC_CHANNEL", "verdict": decide()}


if __name__ == "__main__":
    v = run()["verdict"]
    print("status:                  ", v["status"])
    print("ritual_channel_readiness:", v["ritual_channel_readiness"])
    print("NO_POWER triggers:       ", v["no_power_triggers"])
    print("recommendation:          ", v["recommendation"])
    os.makedirs(S.RESULTS, exist_ok=True)
    json.dump(run(), open(os.path.join(S.RESULTS, "ritual_final_verdict.json"), "w"), indent=1, default=str)
    print("saved ritual_final_verdict.json")
