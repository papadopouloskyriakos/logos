"""§IX circularity verdict — component-wise, mechanical.

Each load-bearing component is rated by whether a known-pair / LB-target / phonetic value could have
influenced it (evidence = the leakage/independence/blindness tests already committed). The overall
verdict is the worst load-bearing component; non-load-bearing post-hoc elements are listed but do not
raise the verdict, per the authorization ("the known five being seen does not automatically make the
primary channel circular provided they did not influence membership/map/thresholds/nulls")."""
import os, sys

sys.path.insert(0, os.path.dirname(__file__))
import cfg  # noqa: E402

RANK = {"LOW": 0, "MANAGED": 1, "HIGH": 2, "FATAL": 3}
NAME = {v: "CIRCULARITY_" + k for k, v in RANK.items()}

COMPONENTS = [
    ("LA_candidate_selection", "LOW", True,
     "internal slot classifier only; blindness proven source+content (test_la_candidate_leakage)"),
    ("LB_target_selection", "LOW", True,
     "canonical KN toponym list + DĀMOS; builder reads no LA/slot/silver (test_lb_target_independence)"),
    ("AB_equivalence_construction", "LOW", True,
     "SigLA AB-class; no pair/phonetic input; blindness tested (test_ab_equivalence_blindness)"),
    ("threshold_selection", "LOW", True,
     "no threshold exists — match = exact identity; nothing tuned"),
    ("null_design", "LOW", True,
     "10 families fixed a priori; frozen input hashes verified; site/genre shown non-load-bearing"),
    ("held_out_evaluation", "LOW", True,
     "PRIMARY×EVALUATION run once after all freezes; hashes verified before scoring"),
    ("projected_phonetic_ablation_A4_A5", "LOW", True,
     "LEVEL_3 firewalled; A1 (not A4) defines the primary result; A4 recovers exact, A5 does not"),
    ("known_pair_use", "MANAGED", False,
     "DEVELOPMENT diagnostic only; the ONE ledger touch is the one-directional contamination filter that "
     "quarantined I-DA from NEGATIVE_CONTROL — proven not to alter PRIMARY/SENSITIVITY membership"),
    ("human_review_exposure", "MANAGED", False,
     "analyst saw the five pairs (§VI) before scoring, but all frozen inputs were blind/independent and "
     "hash-locked before any match was computed; exposure is firewalled and non-load-bearing"),
]

POSTHOC_NONLOADBEARING = [
    "known-pair LOO diagnostic (§VI) — labelled POSTHOC_DEVELOPMENT_BENCHMARK / NOT_CONFIRMATORY",
    "genre-mismatch observation motivating a future ritual channel (§VIII) — labelled EXPLORATORY_POSTHOC_CHANNEL, not created/run",
]


def verdict():
    load_bearing = [c for c in COMPONENTS if c[2]]
    worst = max(RANK[c[1]] for c in load_bearing)
    overall = NAME[worst]
    return {
        "overall": overall,
        "rule": "overall = worst LOAD-BEARING component; non-load-bearing post-hoc elements do not raise it",
        "components": [{"component": n, "rating": r, "load_bearing": lb, "basis": b}
                       for (n, r, lb, b) in COMPONENTS],
        "remaining_posthoc_nonloadbearing": POSTHOC_NONLOADBEARING,
        "note": "All load-bearing components are LOW (candidate blind, target independent, map blind, no "
                "thresholds, nulls fixed, held-out genuine). Known-pair use and human exposure are MANAGED "
                "and NON-load-bearing (firewalled). Per the authorization, the primary channel is not "
                "circular.",
    }


def run():
    cfg.verify_inputs()
    return {"analysis_version": cfg.ANALYSIS_VERSION, "circularity": verdict()}


if __name__ == "__main__":
    import json
    r = run()
    v = r["circularity"]
    print("OVERALL:", v["overall"])
    for c in v["components"]:
        print(f"  {c['component']:34} {c['rating']:8} load_bearing={c['load_bearing']}")
    os.makedirs(cfg.RESULTS, exist_ok=True)
    json.dump(r, open(os.path.join(cfg.RESULTS, "circularity.json"), "w"), indent=1)
    print("saved circularity.json")
