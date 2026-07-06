"""§VI validation: leave-one-out + leave-one-family-out recovery of the source skeleton from the
Egyptian rendering, M2 vs baselines M0/M1. Acceptance gate: M2 must beat the baselines on held-out data."""
import json, os, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(__file__))
import model as M


def _cands(recs):
    seen, out = set(), []
    for r in recs:
        k = tuple(r["_sem"])
        if k not in seen:
            seen.add(k); out.append(r["_sem"])
    return out


def loo(recs, kind):
    """Leave-one-out: rank the true skeleton among all distinct candidates."""
    cands = _cands(recs)
    ranks = []
    for i, held in enumerate(recs):
        train = recs[:i] + recs[i+1:]
        mdl = M.Correspondence().fit(train) if kind == "M2" else None
        r = M.recover_rank(mdl, held["_egy"], held["_sem"], cands, kind)
        ranks.append(r)
    n = len(ranks)
    return {"top1": round(sum(1 for r in ranks if r == 1) / n, 3),
            "top5": round(sum(1 for r in ranks if r <= 5) / n, 3),
            "mrr": round(sum(1.0 / r for r in ranks) / n, 3), "n": n}


def leave_one_family_out(recs):
    fams = sorted({r["fam"] for r in recs})
    out = {}
    for f in fams:
        test = [r for r in recs if r["fam"] == f]
        train = [r for r in recs if r["fam"] != f]
        if len(test) < 3 or len(train) < 30:
            out[f] = {"SUBGROUP_NO_POWER": True, "n_test": len(test)}
            continue
        cands = _cands(recs)
        mdl = M.Correspondence().fit(train)
        ranks = [M.recover_rank(mdl, h["_egy"], h["_sem"], cands, "M2") for h in test]
        out[f] = {"top1": round(sum(1 for r in ranks if r == 1)/len(ranks), 3), "n_test": len(test)}
    return out


def run():
    recs = M.load(("A", "B"))
    res = {"n_records": len(recs), "n_distinct_candidates": len(_cands(recs)),
           "M2": loo(recs, "M2"), "M0_identity": loo(recs, "M0"), "M1_editdist": loo(recs, "M1"),
           "leave_one_family_out_M2": leave_one_family_out(recs)}
    res["beats_baselines"] = (res["M2"]["top1"] >= res["M0_identity"]["top1"]
                              and res["M2"]["mrr"] >= res["M1_editdist"]["mrr"])
    res["acceptance"] = "PASS" if res["beats_baselines"] and res["M2"]["top1"] > 0.3 else "FAIL"
    return res


if __name__ == "__main__":
    r = run()
    print(f"records {r['n_records']}, candidate pool {r['n_distinct_candidates']}")
    for k in ("M2", "M0_identity", "M1_editdist"):
        print(f"  {k:12} top1={r[k]['top1']} top5={r[k]['top5']} mrr={r[k]['mrr']}")
    print("  leave-one-family-out (M2 top1):", {k: v.get('top1', v) for k, v in r['leave_one_family_out_M2'].items()})
    print(f"  beats baselines: {r['beats_baselines']}   ACCEPTANCE: {r['acceptance']}")
    RES = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "results"))
    os.makedirs(RES, exist_ok=True)
    json.dump(r, open(os.path.join(RES, "model_validation.json"), "w"), indent=1)
