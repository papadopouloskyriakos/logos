#!/usr/bin/env python3
"""E204 soft-arm scorer/verifier (built BEFORE completion; frozen rule applied verbatim).
Validates schema + null completeness, hashes outputs, recomputes bounds, adjudicates the
terminal status, and emits E204_FINAL_STATUS.json. Test mode: --fixture runs on a synthetic
fixture only."""
import hashlib, json, os, sys
from scipy.stats import beta

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results_metrology", "METROLOGY_SOFT_RESULTS.json")

REQUIRED = ["arm","per_doc_satisfiable","soft_optimum","relations_at_opt",
            "loo_stable_relations","null_battery_soft","verdict","runtime_s"]

def validate(r):
    missing = [k for k in REQUIRED if k not in r]
    nb = r.get("null_battery_soft", {})
    ok_nulls = nb.get("n") == 200
    return {"missing_fields": missing, "nulls_complete_200": ok_nulls,
            "valid": not missing and ok_nulls}

def adjudicate(r):
    stable = r["loo_stable_relations"]
    ge = r["null_battery_soft"]["ge_observed_relations"]
    p1 = (1 + ge) / 201
    cp95 = float(beta.ppf(.95, ge + 1, 200 - ge)) if ge < 200 else 1.0
    nsat = r["soft_optimum"].get("n_satisfied") or 0
    if not stable:
        status = "UNDERDETERMINED_AFTER_ABLATION" if nsat else "NULL_NOT_DISTINCTIVE"
    elif p1 < 0.05:
        status = "L3_METROLOGICAL_CLASS_SUPPORTED"
    elif ge < 200:
        status = "METROLOGICAL_RELATIONS_PARTIAL"
    else:
        status = "NULL_NOT_DISTINCTIVE"
    return {"status": status, "p_plus1_recomputed": round(p1, 5),
            "cp95_upper_recomputed": round(cp95, 4),
            "n_loo_stable_relations": len(stable),
            "consistency_with_run_verdict": status == r.get("verdict")}

def main():
    if "--fixture" in sys.argv:
        fx = {"arm":"SOFT","per_doc_satisfiable":{"X":True},"soft_optimum":{"n_satisfied":3,"n_docs":5},
              "relations_at_opt":["a>b"],"loo_stable_relations":["a>b"],
              "null_battery_soft":{"n":200,"ge_observed_relations":2},"verdict":"L3_METROLOGICAL_CLASS_SUPPORTED","runtime_s":1}
        v = validate(fx); a = adjudicate(fx)
        assert v["valid"] and a["status"] == "L3_METROLOGICAL_CLASS_SUPPORTED" and abs(a["p_plus1_recomputed"] - 3/201) < 1e-4
        fx["loo_stable_relations"] = []
        assert adjudicate(fx)["status"] == "UNDERDETERMINED_AFTER_ABLATION"
        fx["loo_stable_relations"] = ["a>b"]; fx["null_battery_soft"]["ge_observed_relations"] = 150
        assert adjudicate(fx)["status"] == "METROLOGICAL_RELATIONS_PARTIAL"
        print("fixture tests: 3/3 PASS"); return 0
    r = json.load(open(RES))
    v = validate(r); a = adjudicate(r)
    out = {"validation": v, "adjudication": a,
           "output_sha256": hashlib.sha256(open(RES,'rb').read()).hexdigest(),
           "strict_arm_kept_separate": "METROLOGY_RESULTS.json (generic infeasibility)",
           "wording_rules": "no exact values unless forced in ALL solutions; relations only; no phonetic values; seal closed"}
    final = a["status"] if v["valid"] else "E204_INVALID"
    out["E204_TERMINAL_STATUS"] = final
    json.dump(out, open(os.path.join(HERE, "E204_FINAL_STATUS.json"), "w"), indent=1)
    print("E204 TERMINAL STATUS:", final, "| consistent with run:", a["consistency_with_run_verdict"])
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
