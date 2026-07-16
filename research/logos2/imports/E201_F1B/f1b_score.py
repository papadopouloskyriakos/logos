#!/usr/bin/env python3
"""E201-F1b — SCORE the imported Exit-B CSA sweep under the F1a-FROZEN decision rule, zero re-tuning.
Runs AFTER import_f1b.py (requires the receipt). Applies F1a's frozen per-dataset thresholds + the
mechanical comparability criteria; classifies as one of INDEPENDENT_REPLICATION | SCALE_EXTENSION |
NON_COMPARABLE | FAILED_IMPORT | INVALID. No matcher is re-run; no threshold is changed."""
from __future__ import annotations
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = "/home/claude-runner/gitlab/n8n/logos/results/csa/exitB_sweep_20260716"
F1A = json.load(open(f"{HERE}/../../experiments/E201_replay_benchmark/results/F1a_SCORED.json"))
REC = json.load(open(f"{BUNDLE}/recovery_by_benchmark.json"))
T0 = json.load(open(f"{BUNDLE}/T0_convergence.json"))
RECEIPT = json.load(open(f"{HERE}/IMPORT_RECEIPT.json"))
assert not RECEIPT.get("scored_yet"), "already scored"

# F1a frozen thresholds + engine
F1A_ENGINE = "EM (frequency-init, Hungarian M-step; scripts/decipher LIN-14)"
SWEEP_ENGINE = REC["recovery_method"]                      # CSA (Tamburini CSA_OptMatcher)
THR = {d: v["threshold"] for d, v in F1A["per_dataset_R_full_holdout"].items()}
# sweep-benchmark -> F1a-dataset map (only the syllabic pair is a genuine dataset match)
DMAP = {"linearb-greek": "linear_b-greek.cog", "cypriot-greek": "csyl-greek.cog"}
ALPHA_CONTROL = {"sweep": "ugaritic-noiseless", "f1a": "uga-heb.no_speNL.cog",
                 "match": False, "why": "different Ugaritic dataset (noiseless vs uga-heb Hebrew target)"}

# ---- mechanical comparability criteria ----
crit = {
    "recovery_engine_match": {"f1a": F1A_ENGINE, "sweep": SWEEP_ENGINE, "match": False},
    "converged": {"sweep_steps": REC["steps_budget"], "T0_verdict": T0["T0_VERDICT"],
                  "converged": (T0["T0_VERDICT"] != "CONVERGENCE_ARTIFACT"),
                  "why": "steps=2000 under-converged; T0 shows LinearB still climbing at 6000 -> recovery is a LOWER BOUND"},
    "alphabetic_control_dataset_match": ALPHA_CONTROL,
}
comparable = (crit["recovery_engine_match"]["match"] and crit["converged"]["converged"])

# ---- directional consistency: does ANY swept size reach the F1a threshold on a shared syllabic dataset? ----
consistency = {}
any_syllabic_reaches_threshold = False
for sweep_b, f1a_d in DMAP.items():
    mx = REC["benchmarks"][sweep_b]["max_recovery_any_size"]
    thr = THR[f1a_d]
    reaches = mx >= thr
    any_syllabic_reaches_threshold |= reaches
    consistency[sweep_b] = {"f1a_dataset": f1a_d, "f1a_threshold": thr,
                            "sweep_max_recovery_any_size": mx,
                            "f1a_full_recovery": F1A["per_dataset_R_full_holdout"][f1a_d]["acc"],
                            "reaches_threshold_at_any_size": reaches}

# ---- classification (mechanical) ----
n_cells = sum(b["n_cells"] for b in REC["benchmarks"].values())
if n_cells < 168:
    verdict = "FAILED_IMPORT"
elif comparable:
    verdict = "INDEPENDENT_REPLICATION" if not any_syllabic_reaches_threshold else "REVIEW_CONTRADICTION"
else:
    # engine mismatch and/or under-converged -> cannot be placed on F1a's axis
    verdict = "NON_COMPARABLE"

promotion = ("NOT_PROMOTED" if not any_syllabic_reaches_threshold else "REVIEW")

out = {
    "run": "E201_F1b", "scored_under": "F1a-frozen decision rule (decision_rule.json), zero re-tuning",
    "receipt_files": {r["file"]: r["sha256"] for r in RECEIPT["files"]},
    "n_cells_imported": n_cells,
    "comparability_criteria": crit,
    "comparable_to_F1a": comparable,
    "directional_consistency": consistency,
    "any_syllabic_reaches_F1a_threshold_at_any_size": any_syllabic_reaches_threshold,
    "promotion_under_F1a_gate": promotion,
    "VERDICT": verdict,
    "binding_result_unchanged": "F1a stands as the binding confirmatory result (NOT_QUALIFIED_FOR_LINEAR_A). "
        "E208 stays de-authorized; E213 seal intact; no closed LOGOS-2 conclusion altered (Art. XVII).",
    "interpretation": (
        "The Exit-B CSA sweep uses a DIFFERENT recovery engine than F1a (CSA_OptMatcher vs frequency-init EM) "
        "and ran under-converged (steps=2000; T0 verdict CONVERGENCE_ARTIFACT -> syllabic recovery is a LOWER "
        "BOUND), and its alphabetic control is a different dataset (ugaritic-noiseless vs uga-heb). Its recovery "
        "numbers therefore CANNOT be placed on F1a's axis -> NON_COMPARABLE. It is nonetheless DIRECTIONALLY "
        "CONSISTENT with F1a: no shared syllabic benchmark (Linear B, Cypriot) reaches its F1a threshold at ANY "
        "swept size (LB max %.3f < 0.5; CSYL max %.3f < 0.35), so the sweep does not overturn F1a's "
        "NOT_QUALIFIED verdict. As a lower bound it cannot CONFIRM a converged floor either." % (
            consistency["linearb-greek"]["sweep_max_recovery_any_size"],
            consistency["cypriot-greek"]["sweep_max_recovery_any_size"])),
    "compliance": "Art. XVII append-only; Art. XII (target not graded by the rule that created it); a lower "
                  "bound below threshold neither promotes nor converts the null into a positive.",
}
json.dump(out, open(f"{HERE}/F1B_SCORED.json", "w"), indent=1)
# flip the receipt's scored flag (append-only provenance)
RECEIPT["scored_yet"] = True
json.dump(RECEIPT, open(f"{HERE}/IMPORT_RECEIPT.json", "w"), indent=1)

print("F1B VERDICT:", verdict)
print("comparable_to_F1a:", comparable, "| promotion:", promotion)
for b, c in consistency.items():
    print(f"  {b:16s} max_any_size={c['sweep_max_recovery_any_size']:.4f} vs F1a_thr={c['f1a_threshold']} "
          f"-> reaches={c['reaches_threshold_at_any_size']} (F1a full={c['f1a_full_recovery']})")
