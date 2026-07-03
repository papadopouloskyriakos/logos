#!/usr/bin/env python3
"""gap_analysis.py — Phase 2 §4: census supply vs the Step-1 quota (mechanical, provenance-only).

Quota-eligibility rule (provenance-based, fixed before the census was read):
  independence_class in {1,2,3}; fringe_flag false; sm_trust != 'debunked'; source_status in
  {primary, secondary}; LA form >= 2 signs (a pin needs visible co-signs); rows whose notes mark
  the WHOLE equation as queried by the source ('queried') are excluded from counting (reported).
Class-4 rows are CONSTRAINTS, never pins — reported separately, never quota-counted.

Verdict rule vs the quota cell (n=8, R-cap regimes 1-3 all band-passing at n=8):
  SUPPLY MEETS QUOTA iff >= 8 quota-eligible anchors AND realized max legs/sign <= 3 (inside the
  swept redundancy regimes). Legs computed over ELIGIBLE (pinnable) signs only.
"""
import csv
import json
import os
import sys
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
_GATE = os.path.dirname(_HERE)

QUOTA_N = 8
SWEPT_R_MAX = 3


def main() -> int:
    rows = list(csv.DictReader(open(os.path.join(_HERE, "anchor_census.csv"), encoding="utf-8")))
    quota = json.load(open(os.path.join(_HERE, "results", "phase2_quota_sweep.json")))["quota"]
    anchors = {r["sign_id"]: r for r in
               csv.DictReader(open(os.path.join(_GATE, "anchors.csv"), encoding="utf-8"))}
    eligible = {s for s, r in anchors.items()
                if r["robust_anchor"] == "True" and s not in ("SI", "MU")}

    def signs(r):
        return [s.strip().upper() for s in r["covered_signs"].split(",") if s.strip()]

    def queried(r):
        return "queried" in (r.get("disagreement_notes", "") or "").lower()

    def hedged(r):
        notes = (r.get("disagreement_notes", "") or "").lower()
        return any(m in notes for m in ("hedge", "'?'", "=?", "perhaps", "do not assert"))

    elig_rows, excluded = [], Counter()
    for r in rows:
        if r["class"] == "variation_constraint":
            excluded["class4_constraint"] += 1
            continue
        if r["fringe_flag"].strip().lower() == "true":
            excluded["fringe"] += 1
            continue
        if r["sm_trust"].strip().lower() == "debunked":
            excluded["sm_debunked"] += 1
            continue
        if r["source_status"].strip().lower() not in ("primary", "secondary"):
            excluded["pending_primary"] += 1
            continue
        if len(signs(r)) < 2:
            excluded["single_sign_form"] += 1
            continue
        if queried(r):
            excluded["source_queried_equation"] += 1
            continue
        elig_rows.append(r)

    legs = Counter()
    for r in elig_rows:
        for s in set(signs(r)):
            if s in eligible:
                legs[s] += 1
    covered = sorted(legs)
    max_legs = max(legs.values()) if legs else 0
    per_class = Counter(r["class"] for r in elig_rows)
    per_trust = Counter(r["sm_trust"] for r in elig_rows)
    per_status = Counter(r["source_status"] for r in elig_rows)

    n_supply = len(elig_rows)
    # The quota asks whether >= QUOTA_N anchors can be fielded WITHIN a swept redundancy
    # regime — i.e. whether such a SUBSET exists, not whether the whole pool satisfies the
    # cap at once. Greedy certificates (deterministic, anchor_id order): the largest prefix
    # subsets under R=1 (sign-disjoint) and R=SWEPT_R_MAX.
    def greedy_subset(rmax):
        used = Counter()
        chosen = []
        for r in sorted(elig_rows, key=lambda x: x["anchor_id"]):
            ss = [s for s in set(signs(r)) if s in eligible]
            if ss and all(used[s] < rmax for s in ss):
                for s in ss:
                    used[s] += 1
                chosen.append(r["anchor_id"])
        return chosen

    strict_rows = [r for r in elig_rows if not hedged(r)]

    import random

    def best_r1(pool):
        rnd = random.Random(0)
        order = list(range(len(pool)))
        best = []
        for _ in range(20000):
            used, chosen = set(), []
            for i in order:
                ss = [s for s in set(signs(pool[i])) if s in eligible]
                if ss and not (set(ss) & used):
                    used |= set(ss)
                    chosen.append(pool[i]["anchor_id"])
            if len(chosen) > len(best):
                best = chosen
            rnd.shuffle(order)
        return best

    subset_r1 = best_r1(elig_rows)
    subset_r1_strict = best_r1(strict_rows)
    subset_r3 = greedy_subset(SWEPT_R_MAX)
    # Verdict criterion (v3, disclosed): the sweep grid shows ALL swept regimes pass the band
    # at n=8 (LOTO-survival 0.93/0.86/0.93 for R=1/2/3), so the supply meets the quota iff a
    # subset of >= QUOTA_N anchors exists within ANY swept regime, i.e. legs <= SWEPT_R_MAX.
    meets = n_supply >= QUOTA_N and max(len(subset_r1), len(subset_r3)) >= QUOTA_N
    pending = excluded.get("pending_primary", 0)
    deficit = QUOTA_N - n_supply
    if meets:
        verdict = "SUPPLY MEETS QUOTA"
    elif deficit > 0 and pending >= deficit:
        verdict = "PENDING-DOMINATED"
    else:
        verdict = f"SHORTFALL (K = {max(deficit, 0)})"

    out = {
        "quota": quota, "n_quota_eligible_anchors": n_supply,
        "per_class": dict(per_class), "per_sm_trust": dict(per_trust),
        "per_source_status": dict(per_status), "excluded": dict(excluded),
        "distinct_covered_eligible_signs": len(covered),
        "legs_per_sign": dict(sorted(legs.items())),
        "max_legs": max_legs, "signs_over_swept_R": [s for s, c in legs.items() if c > SWEPT_R_MAX],
        "greedy_sign_disjoint_subset_R1": subset_r1,
        "strict_tier": {"n_anchors_after_hedge_exclusions": len(strict_rows),
                        "r1_subset": subset_r1_strict,
                        "meets_quota": len(subset_r1_strict) >= QUOTA_N},
        "greedy_subset_R3_size": len(subset_r3),
        "verdict": verdict,
        "fix_disclosure": "v2: original script mis-fired PENDING-DOMINATED on a negative deficit "
                          "and tested the legs cap over the whole pool instead of subset "
                          "existence; fixed per the prompt's verdict definitions, disclosed.",
        "quota_cell_reference": "8 anchors; all R regimes 1-3 band-passing at n=8 "
                                "(0.86-0.93); quota-cell realized coverage ~26 slots",
    }
    with open(os.path.join(_HERE, "results", "gap_analysis.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
