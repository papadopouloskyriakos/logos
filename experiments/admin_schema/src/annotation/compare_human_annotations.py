#!/usr/bin/env python3
"""Compare TWO genuine human submissions (agreement) — ONLY when both are present + valid.

Refuses (status BLOCKED) if either submission is missing/invalid. Never computes agreement on fabricated,
partial, or model-generated data. Reuses the nominal-Krippendorff estimator from the pilot stats module.
"""
import csv, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "pilot"))
sys.path.insert(0, HERE)
import validate_human_submission as V
from compute_pilot_stats import krippendorff_nominal

HP = V.HP


def run():
    va, vb = V.validate("A"), V.validate("B")
    if va["status"] != "VALID" or vb["status"] != "VALID":
        return {"status": "BLOCKED", "reason": "both genuine+valid human submissions required",
                "A": va["status"], "B": vb["status"]}
    A = {r["anon_item_id"]: r for r in csv.DictReader(open(os.path.join(HP, "completed", "annotator_A_completed.csv")))}
    B = {r["anon_item_id"]: r for r in csv.DictReader(open(os.path.join(HP, "completed", "annotator_B_completed.csv")))}
    ids = sorted(set(A) & set(B))
    pairs = [(A[i]["coarse_role"], B[i]["coarse_role"]) for i in ids if A[i]["coarse_role"] and B[i]["coarse_role"]]
    alpha, _ = krippendorff_nominal(pairs)
    raw = sum(1 for a, b in pairs if a == b) / max(len(pairs), 1)
    gate = "PRIMARY_ELIGIBLE" if alpha >= 0.80 else ("PROVISIONAL" if alpha >= 0.667 else "NOT_ELIGIBLE")
    return {"status": "COMPUTED", "n": len(pairs), "krippendorff_alpha": round(alpha, 3),
            "raw_agreement": round(raw, 3), "agreement_gate": gate,
            "note": "GENUINE human inter-annotator agreement (per the frozen QC gate a>=0.80 primary)"}


if __name__ == "__main__":
    import json; print(json.dumps(run(), indent=1))
