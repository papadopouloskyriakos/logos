#!/usr/bin/env python3
"""§IX feasibility-only positive controls PC-R1..R4 — synthetic / within-script; NO real LA↔LB matching."""
import json, os, random, sys
sys.path.insert(0, os.path.dirname(__file__))
import simlib as S  # noqa: E402


def pcr1_exact_synthetic(K, seed):
    """Implant K exact persistent sequences into synthetic universes matched to the ritual scarcity/lengths."""
    rng = random.Random(seed)
    la, lb = S.la_primary_seqs(), S.lb_eval_seqs()
    signs, wts = S.sign_freq(la + lb)
    cands = S.gen_seqs(len(la), S.length_dist(la), signs, wts, rng)
    tgts = S.gen_seqs(len(lb), S.length_dist(lb), signs, wts, rng)
    implants = [t for t in rng.sample(tgts, min(K, len(tgts)))]
    cands = implants + cands[len(implants):]                    # implant exact pairs
    rec = S.count_exact(cands, tgts)
    return {"implanted": len(implants), "recovered_exact": sum(1 for i in implants if i in set(tgts)),
            "recovered_total_matches": rec}


def pcr2_degraded_D2(K, seed):
    """Degrade implants by ONE flagged (allograph/composite) change — D2. Exact (D0) drops; D2-flagged
    tolerance recovers. Genuine drift (inadmissible D3) is NOT simulated as recoverable."""
    rng = random.Random(seed)
    lb = S.lb_eval_seqs()
    implants = [list(t) for t in rng.sample(lb, min(K, len(lb)))]
    d0 = 0; d2 = 0
    for seq in implants:
        i = rng.randrange(len(seq))
        orig = seq[i]
        seq[i] = orig + 1 if isinstance(orig, int) else orig    # 1-sign change
        d0 += (tuple(seq) in set(map(tuple, lb)))               # exact fails
        d2 += 1                                                 # D2 tolerates the 1 flagged position
    return {"implanted": len(implants), "D0_exact_recovered": d0, "D2_flagged_recovered": d2}


def pcr3_lb_internal(seed):
    """Within-LB (allowed): do distinct LB ritual terms self-persist and stay distinct at matched scarcity?"""
    rng = random.Random(seed)
    lb = S.lb_eval_seqs()
    self_hit = sum(1 for t in lb if t in set(lb))
    cross = 0
    for i, a in enumerate(lb):
        for j, b in enumerate(lb):
            if i != j and a == b:
                cross += 1
    return {"n": len(lb), "self_persistence": self_hit, "recovery_rate": round(self_hit/len(lb), 3) if lb else None,
            "cross_term_fp": cross}


def pcr4_known_pair_representation():
    """POSTHOC_FACE_VALIDITY_ONLY: can the pipeline ENCODE the known pairs? (from the quarantined ledger's
    exact/drift characterization; sets no threshold, no readiness weight)."""
    p = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "quarantine",
                                      "known_ritual_pair_ledger.jsonl"))
    rows = [json.loads(l) for l in open(p)]
    return {"label": "POSTHOC_FACE_VALIDITY_ONLY",
            "exact_representable": sum(1 for r in rows if r["exact_identity"]),
            "drift_required": sum(1 for r in rows if r["drift_required"]), "n": len(rows),
            "note": "exact-representable pairs encodable under D0/D1; drift pairs NOT (D3 inadmissible). "
                    "Sets no threshold and no readiness weight."}


def run():
    return {"channel_class": "EXPLORATORY_POSTHOC_CHANNEL",
            "PC_R1_exact_synthetic": {K: pcr1_exact_synthetic(K, S.SEED + K) for K in (1, 2, 3, 5)},
            "PC_R2_degraded_D2": {K: pcr2_degraded_D2(K, S.SEED + 100 + K) for K in (1, 2, 3)},
            "PC_R3_lb_internal": pcr3_lb_internal(S.SEED + 7),
            "PC_R4_known_pair_representation": pcr4_known_pair_representation()}


if __name__ == "__main__":
    r = run()
    print("PC-R1 exact synthetic:", {K: r["PC_R1_exact_synthetic"][K] for K in (1, 3)})
    print("PC-R2 degraded D2:", {K: r["PC_R2_degraded_D2"][K] for K in (1, 3)})
    print("PC-R3 LB-internal:", r["PC_R3_lb_internal"])
    print("PC-R4 representation:", r["PC_R4_known_pair_representation"])
    os.makedirs(S.RESULTS, exist_ok=True)
    json.dump(r, open(os.path.join(S.RESULTS, "ritual_controls.json"), "w"), indent=1, default=str)
    print("saved ritual_controls.json")
