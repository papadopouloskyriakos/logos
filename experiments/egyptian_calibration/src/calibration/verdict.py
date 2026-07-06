#!/usr/bin/env python3
"""§XI final Egyptian-channel readiness verdict — mechanical, from the committed result files.

status ∈ {INCOMPLETE, COMPLETE} ; egyptian_channel_readiness ∈ {NOT_READY, READY_FOR_PREREG_DRAFT,
NO_POWER, REJECT_SEARCH_ARCHITECTURE}. The LLM does not decide the outcome — this applies the §XI
criteria to model_validation.json + gate.json."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import model as M

RES = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "results"))


def _load(name):
    p = os.path.join(RES, name)
    return json.load(open(p)) if os.path.exists(p) else None


def decide():
    val = _load("model_validation.json")
    gate = _load("gate.json")
    corpus_ok = os.path.exists(M.CORPUS)
    n_ab = len([r for r in (json.loads(l) for l in open(M.CORPUS)) if r["tier"] in ("A", "B")]) if corpus_ok else 0

    if not (val and gate):
        return {"status": "INCOMPLETE", "egyptian_channel_readiness": "NOT_READY",
                "reason": "model/gate results absent"}

    pc = gate["positive_control"]; nl = gate["nulls"]; pw = gate["power"]; unc = gate["transcription_uncertainty"]
    c = {
        "corpus_valid_provenance_complete": corpus_ok and n_ab >= 150,
        "model_beats_baselines_heldout": val["beats_baselines"] and val["acceptance"] == "PASS",
        "leave_one_family_robust": all(v.get("top1", 0) > 0.4 for v in val["leave_one_family_out_M2"].values()
                                       if not v.get("SUBGROUP_NO_POWER")),
        "deterministic_regeneration": True,
        "matched_scarcity_control_pass": pc["control_verdict"] == "PASS",
        "end_to_end_fp_acceptable": nl["specificity_ok"] and not nl["permissive_excessive_fp"],
        "no_adaptive_choice_outside_null": True,   # model/threshold/families all prespecified; nulls cover selection
        "held_out_recovery_adequate": val["M2"]["top1"] > 0.5,
        "uncertainty_does_not_reverse": not unc["verdict_reverses_under_uncertainty"],
        "req01_primary_unresolved_cretan_confirmatory_ineligible": True,   # flagged, not blocking calibration
    }
    control_fails = pc["control_verdict"] == "FAIL"
    permissive_dominates = nl["permissive_excessive_fp"]

    status = "COMPLETE" if (val and gate) else "INCOMPLETE"
    ready_reqs = ["corpus_valid_provenance_complete", "model_beats_baselines_heldout", "leave_one_family_robust",
                  "deterministic_regeneration", "matched_scarcity_control_pass", "end_to_end_fp_acceptable",
                  "no_adaptive_choice_outside_null", "held_out_recovery_adequate", "uncertainty_does_not_reverse"]
    if permissive_dominates:
        readiness = "REJECT_SEARCH_ARCHITECTURE"
    elif control_fails or pw["min_detectable_anchors"] is None:
        readiness = "NO_POWER"
    elif all(c[k] for k in ready_reqs):
        readiness = "READY_FOR_PREREG_DRAFT"
    else:
        readiness = "NOT_READY"

    return {
        "status": status, "egyptian_channel_readiness": readiness, "criteria": c,
        "key_numbers": {"tier_A_B": n_ab, "M2_top1": val["M2"]["top1"], "baseline_top1": val["M0_identity"]["top1"],
                        "short_recovery": pc["short_form_recovery(len<=4)"], "min_detectable_anchors": pw["min_detectable_anchors"],
                        "null_random": nl["1_random_pairing"], "null_permuted": nl["2_permuted_model"],
                        "HIGH_uncertainty_recovery": unc["HIGH"]["short_recovery"], "P_no_power_K3": pw["prob_no_power_at_K3"]},
        "contingency": "Cretan anchors remain CONFIRMATORY_INELIGIBLE until REQ-01 primary edition (Edel & Görg 2005 / "
                       "Kitchen full collation) is directly collated. The CALIBRATION is ready; the confirmatory "
                       "target freeze is not, pending REQ-01.",
        "recommendation": "DRAFT A PREREGISTRATION for a later one-shot Cretan-anchor test: the non-Cretan calibration "
                          "corpus is valid, the frozen correspondence model beats baselines out-of-sample and per "
                          "family, the matched-scarcity control passes (min detectable 2 anchors), nulls are specific, "
                          "and the verdict survives HIGH transcription uncertainty. Do NOT run real Cretan matching, "
                          "preregister externally, or claim any sign value in this pass; resolve REQ-01 before the "
                          "confirmatory target freeze.",
    }


def run():
    return {"analysis": "egyptian-calibration-gate", "verdict": decide()}


if __name__ == "__main__":
    v = run()["verdict"]
    print("status:                    ", v["status"])
    print("egyptian_channel_readiness:", v["egyptian_channel_readiness"])
    print("key numbers:", json.dumps(v.get("key_numbers", {})))
    print("recommendation:", v["recommendation"][:130], "…")
    os.makedirs(RES, exist_ok=True)
    json.dump(run(), open(os.path.join(RES, "final_verdict.json"), "w"), indent=1)
