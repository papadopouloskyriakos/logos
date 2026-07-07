#!/usr/bin/env python3
"""Build an adjudication packet (disagreement items) — ONLY when both genuine submissions are valid.

Refuses otherwise. Does not adjudicate itself (a human adjudicator resolves); it only assembles the
disagreements + both original labels for the adjudicator.
"""
import csv, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import validate_human_submission as V
HP = V.HP


def run():
    va, vb = V.validate("A"), V.validate("B")
    if va["status"] != "VALID" or vb["status"] != "VALID":
        return {"status": "BLOCKED", "reason": "both genuine+valid human submissions required", "A": va["status"], "B": vb["status"]}
    A = {r["anon_item_id"]: r for r in csv.DictReader(open(os.path.join(HP, "completed", "annotator_A_completed.csv")))}
    B = {r["anon_item_id"]: r for r in csv.DictReader(open(os.path.join(HP, "completed", "annotator_B_completed.csv")))}
    disputes = [{"anon_item_id": i, "A_coarse": A[i]["coarse_role"], "B_coarse": B[i]["coarse_role"],
                 "A_tier": A[i]["gold_tier"], "B_tier": B[i]["gold_tier"], "A_rationale": A[i].get("rationale"),
                 "B_rationale": B[i].get("rationale"), "adjudicated_role": "", "adjudicated_tier": "", "adjudicator_note": ""}
                for i in sorted(set(A) & set(B)) if A[i]["coarse_role"] != B[i]["coarse_role"]]
    out = os.path.join(HP, "completed", "adjudication_packet.csv")
    if disputes:
        with open(out, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(disputes[0].keys())); w.writeheader(); [w.writerow(d) for d in disputes]
    return {"status": "BUILT", "n_disputes": len(disputes), "path": out}


if __name__ == "__main__":
    print(json.dumps(run(), indent=1))
