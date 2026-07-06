#!/usr/bin/env python3
"""§VIII independent drift-model feasibility.

Can a drift-tolerant model be specified WITHOUT learning transformations from the known LA↔LB pairs
(tu-ru-sa→tu-ri-so, di-ki-ta→di-ka-ta-de, i-da→i-da-i-jo)? Model families D0–D4. This module does NOT
run real matching; it audits whether the operations the phenomenon would need can be grounded in
independent evidence, and applies the frozen D3-admissibility criteria mechanically.
"""
import json, os, sys

HERE = os.path.dirname(__file__)

MODEL_FAMILIES = {
    "D0_exact_identity": {"drift_span": 0, "available": True,
                          "note": "exact raw sign identity; covers only spelling-identical continuities"},
    "D1_tierA_equivalence": {"drift_span": 0, "available": True,
                             "note": "frozen 77-sign tier-A map; == D0 until allographs clustered"},
    "D2_source_grounded_uncertainty": {"drift_span": "≤1 flagged", "available": True,
                                       "note": "allograph/damage/composite uncertainty from SigLA/independent "
                                               "sources; does NOT cover genuine vowel-quality substitution"},
    "D3_independent_constrained_edit": {"drift_span": "≥2 substitutions", "available": None,
                                        "note": "the model that WOULD span genuine drift — admissibility audited below"},
    "D4_permissive_edit": {"drift_span": "unbounded", "available": True,
                           "note": "false-positive STRESS TEST only; never a real model"},
}

# operations the known DRIFT pairs exhibit (OBSERVED for feasibility, NOT used to fit any model)
OBSERVED_DRIFT_OPERATIONS = {
    "vowel_quality_u_to_i": {"example_pairs": ["TU-RU-SA~tu-ri-so (RU→RI)"], "independent_support": "WEAK",
                             "independent_sources_checked": ["LB-internal spelling variation", "scribal variants"],
                             "verdict": "not independently attested as a systematic spelling rule; the clear "
                                        "example IS a quarantined known pair → circular if used"},
    "vowel_quality_a_to_o": {"example_pairs": ["TU-RU-SA~tu-ri-so (SA→SO)"], "independent_support": "WEAK",
                             "independent_sources_checked": ["LB-internal spelling variation"],
                             "verdict": "same — genuine linguistic change, not an independently-attested "
                                        "orthographic variant"},
    "derivational_suffix_insertion": {"example_pairs": ["I-DA~i-da-i-jo (+i-jo)", "DI-KI-TA~di-ka-ta-de (+de)"],
                                      "independent_support": "MODERATE",
                                      "independent_sources_checked": ["LB adjectival -i-jo / allative -de morphology"],
                                      "verdict": "the SUFFIXES are independently attested LB morphology, but "
                                                 "matching a bare LA form to a suffixed LB form is a length "
                                                 "change that a constrained edit model would have to permit — "
                                                 "and permitting free affixation inflates false positives"},
}

# frozen D3-admissibility criteria (a future constrained drift model is admissible ONLY if ALL hold)
def d3_admissibility():
    criteria = {
        "transformations_estimated_from_independent_data": False,   # the drift ops' clear examples ARE the known pairs
        "operation_inventory_frozen_before_pairing": True,          # possible in principle
        "weights_cross_validated_on_non_target_data": False,        # no independent training set exists
        "target_pairs_absent_from_training": False,                 # only training set = the known target pairs
        "complexity_receipt_counted": True,                         # possible
        "false_positive_calibrated_end_to_end": True,               # possible but permissive edits blow up FP
        "materially_outperforms_permissive_D4": None,               # untestable without a fitted D3
    }
    admissible = all(v is True for v in criteria.values() if v is not None) and \
        criteria["transformations_estimated_from_independent_data"] and \
        criteria["weights_cross_validated_on_non_target_data"] and \
        criteria["target_pairs_absent_from_training"]
    return {"criteria": criteria, "D3_admissible": admissible,
            "blocking_criteria": [k for k, v in criteria.items() if v is False]}


def run():
    d3 = d3_admissibility()
    feasible_families = ["D0_exact_identity", "D1_tierA_equivalence", "D2_source_grounded_uncertainty"]
    return {
        "channel_class": "EXPLORATORY_POSTHOC_CHANNEL",
        "model_families": MODEL_FAMILIES,
        "observed_drift_operations": OBSERVED_DRIFT_OPERATIONS,
        "d3_admissibility": d3,
        "feasible_families": feasible_families,
        "drift_model_feasible": d3["D3_admissible"],
        "verdict": "A constrained drift model (D3) is NOT independently specifiable: the vowel-quality "
                   "substitutions the known drift pairs require have only WEAK independent support and "
                   "their clear examples are the quarantined known pairs (circular). Only exact/tier-A "
                   "(D0/D1) and ≤1-flagged uncertainty (D2) are admissible — and those span 0 genuine "
                   "drift. Therefore the ritual channel, like the administrative one, can test only "
                   "EXACT/near-exact continuity, not the drift-inclusive phenomenon.",
    }


if __name__ == "__main__":
    r = run()
    print("D3 admissible:", r["d3_admissibility"]["D3_admissible"])
    print("blocking criteria:", r["d3_admissibility"]["blocking_criteria"])
    print("feasible families:", r["feasible_families"])
    print("drift_model_feasible:", r["drift_model_feasible"])
    import os as _os
    RES = _os.path.normpath(_os.path.join(HERE, "..", "..", "data", "results")); _os.makedirs(RES, exist_ok=True)
    json.dump(r, open(_os.path.join(RES, "drift_feasibility.json"), "w"), indent=1, default=str)
    print("saved drift_feasibility.json")
