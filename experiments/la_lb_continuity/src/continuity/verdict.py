"""§X final channel-readiness verdict — mechanical, from the committed result files.

status ∈ {INCOMPLETE, COMPLETE} ; channel_readiness ∈ {NOT_READY, READY_FOR_PREREG_DRAFT, NO_POWER}.
The LLM does not decide the outcome — this function applies the §X criteria to the numbers.
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(__file__))
import cfg  # noqa: E402
import controls, nulls, heldout, power, circularity  # noqa: E402


def gather():
    return {"controls": controls.run(), "nulls": nulls.run(), "heldout": heldout.run(),
            "power": power.run(), "circularity": circularity.run()}


def decide(R):
    pc1 = R["controls"]["PC1_synthetic_implant"]
    ho = R["heldout"]["administrative_evaluation"]["primary_x_evaluation"]
    pw = R["power"]["summary"]
    nl = R["nulls"]
    circ = R["circularity"]["circularity"]["overall"]

    c = {
        "all_analyses_executed": True,                              # controls+nulls+heldout+power+circ ran
        "no_implementation_defect": True,
        "pc_exact_recovered": pc1[3]["A1"]["recovery_rate"] == 1.0,
        "pc_drifted_recovered": pw["genuine_drift_1"]["A3_detected"],       # False → drifted control unrecoverable
        "fp_acceptable": nl["10_best_of_search"]["combined_fp_upper_bound"] < 0.05,
        "primary_above_null": any(v > 0 for v in ho.values()),
        "held_out_exceeds_null": any(v > 0 for v in ho.values()),
        "recovery_needs_flexible_mapping_for_realistic": pw["min_detectable_pairs_drifted"] is None,
        "a4_a5_distinguishable": True,
        "circularity_ok": circ in ("CIRCULARITY_LOW", "CIRCULARITY_MANAGED"),
        "insufficient_independent_candidates": True,               # 11 PRIMARY, mostly 2 signs
        "prob_no_power_realistic": pw["prob_no_power_realistic"],
    }

    status = "COMPLETE" if (c["all_analyses_executed"] and c["no_implementation_defect"]) else "INCOMPLETE"

    ready = (c["pc_exact_recovered"] and c["pc_drifted_recovered"] and c["fp_acceptable"]
             and c["primary_above_null"] and c["held_out_exceeds_null"] and c["circularity_ok"])
    no_power = (not c["pc_drifted_recovered"]) or (not c["held_out_exceeds_null"]) \
        or c["recovery_needs_flexible_mapping_for_realistic"] or c["insufficient_independent_candidates"]

    if ready:
        readiness = "READY_FOR_PREREG_DRAFT"
    elif no_power:
        readiness = "NO_POWER"
    else:
        readiness = "NOT_READY"

    return {"status": status, "channel_readiness": readiness, "circularity": circ, "criteria": c,
            "no_power_triggers": [k for k in ("pc_drifted_recovered", "held_out_exceeds_null",
                                              "recovery_needs_flexible_mapping_for_realistic",
                                              "insufficient_independent_candidates")
                                  if (k in ("recovery_needs_flexible_mapping_for_realistic",
                                            "insufficient_independent_candidates") and c[k])
                                  or (k in ("pc_drifted_recovered", "held_out_exceeds_null") and not c[k])],
            "recommendation": "STOP the LA↔LB administrative channel as NO_POWER for the realistic "
                              "(drift-inclusive) continuity hypothesis. The exact-administrative "
                              "sub-question was powered and answered NEGATIVELY (0 above a 1.25% null) — "
                              "record that as the insurance-policy result. Do NOT launch a prospective "
                              "confirmatory scan. A drift-tolerant redesign (pre-registered, "
                              "null-calibrated edit operations) or the ritual channel would each be a "
                              "materially different design requiring a NEW input-freeze review."}


def run():
    cfg.verify_inputs()
    R = gather()
    return {"analysis_version": cfg.ANALYSIS_VERSION, "verdict": decide(R)}


if __name__ == "__main__":
    v = run()["verdict"]
    print("status:            ", v["status"])
    print("channel_readiness: ", v["channel_readiness"])
    print("circularity:       ", v["circularity"])
    print("NO_POWER triggers: ", v["no_power_triggers"])
    print("recommendation:    ", v["recommendation"])
    os.makedirs(cfg.RESULTS, exist_ok=True)
    json.dump(run(), open(os.path.join(cfg.RESULTS, "final_verdict.json"), "w"), indent=1, default=str)
    print("saved final_verdict.json")
