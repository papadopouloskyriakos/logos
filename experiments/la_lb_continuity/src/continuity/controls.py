#!/usr/bin/env python3
"""§IV positive controls PC1–PC3 (PC4 = PA-I-TO face-validity lives in model.py).

These prove the detector is not dead: can it recover persistence that IS present, at the real frozen
scarcity (11 PRIMARY / 44 B+C candidates, 16 EVALUATION targets, 2–3 signs)? No frozen membership is
mutated — implants operate on deep copies.
"""
import copy, json, os, random, sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
import cfg, model as M, partitions as P  # noqa: E402


def _pools():
    cands = [dict(candidate_id=c["candidate_id"], raw_sign_ids=list(c["raw_sign_ids"]),
                  uncertainty=dict(c["uncertainty"])) for c in P.partitioned()["PRIMARY_B"]]
    tgts = [t for t in P.load_targets() if t["development_or_evaluation_role"] == "EVALUATION"]
    return cands, tgts


def _to_ab(seq):
    """LB GORILA-number sequence -> LA raw AB ids (so an implanted LA candidate equals the LB target)."""
    return ["AB%02d" % n if isinstance(n, int) else str(n) for n in seq]


def pc1_synthetic_implant(K, seed):
    """Implant K exact persistence pairs (length-matched), measure recovery + incidental FP."""
    cands, tgts = _pools()
    rng = random.Random(seed)
    tby_len = {}
    for t in tgts:
        tby_len.setdefault(len(M.lb_seq(t)), []).append(t)
    implanted = []
    used_c, used_t = set(), set()
    order = cands[:]; rng.shuffle(order)
    for c in order:
        if len(implanted) >= K:
            break
        L = len(M.la_seq(c))
        opts = [t for t in tby_len.get(L, []) if t["lb_target_id"] not in used_t]
        if not opts:
            continue
        t = rng.choice(opts)
        c["raw_sign_ids"] = _to_ab(M.lb_seq(t))          # make candidate identical to target
        implanted.append((c["candidate_id"], t["lb_target_id"]))
        used_c.add(c["candidate_id"]); used_t.add(t["lb_target_id"])
    rec = {}
    for L in ("A1", "A2", "A3"):
        pairs = set(M.match_pairs(cands, tgts, L))
        got = sum(1 for imp in implanted if imp in pairs)
        incidental = len(pairs) - got
        rec[L] = {"implanted": len(implanted), "recovered": got,
                  "recovery_rate": round(got / len(implanted), 3) if implanted else None,
                  "incidental_fp_pairs": incidental}
    return rec


def pc2_degraded_implant(K, seed):
    """Implant K, then degrade the candidate by ONE sign change at a FLAGGED position (allograph/damage/
    composite proxy). A1/A2 should drop; A3 recovers only the flagged 1-mismatch."""
    cands, tgts = _pools()
    rng = random.Random(seed)
    tby_len = {}
    for t in tgts:
        tby_len.setdefault(len(M.lb_seq(t)), []).append(t)
    implanted = []
    for c in cands:
        if len(implanted) >= K:
            break
        L = len(M.la_seq(c))
        opts = tby_len.get(L, [])
        if not opts:
            continue
        t = rng.choice(opts)
        ab = _to_ab(M.lb_seq(t))
        i = rng.randrange(len(ab))
        ab[i] = "AB%02d" % ((int(ab[i][2:]) % 90) + 1)   # perturb one sign
        c["raw_sign_ids"] = ab
        c["uncertainty"]["composite_sensitive"] = True   # flag the degraded position class (prespecified)
        implanted.append((c["candidate_id"], t["lb_target_id"]))
    rec = {}
    for L in ("A1", "A2", "A3"):
        pairs = set(M.match_pairs(cands, tgts, L))
        rec[L] = {"implanted": len(implanted),
                  "recovered": sum(1 for imp in implanted if imp in pairs)}
    return rec


def pc3_lb_internal(seed):
    """Matched-scarcity LB-internal control: take a scarcity-matched subset of EVALUATION toponyms as
    both 'candidates' and 'targets'; a toponym must persist to itself; distinct toponyms must not match."""
    tgts = [t for t in P.load_targets() if t["development_or_evaluation_role"] == "EVALUATION"]
    rng = random.Random(seed)
    sub = tgts[:]; rng.shuffle(sub); sub = sub[:11]      # match the 11-candidate scarcity
    as_c = [dict(candidate_id="LBINT-" + t["lb_target_id"], raw_sign_ids=_to_ab(M.lb_seq(t)),
                 uncertainty={"composite_sensitive": False, "damaged": False}) for t in sub]
    self_hit = 0; cross = 0
    for c, t in zip(as_c, sub):
        if M.matches(c, t, "A1"):
            self_hit += 1
        for t2 in tgts:
            if t2["lb_target_id"] != t["lb_target_id"] and M.matches(c, t2, "A1"):
                cross += 1
    return {"n": len(sub), "self_persistence_recovered": self_hit,
            "recovery_rate": round(self_hit / len(sub), 3), "cross_toponym_fp": cross}


def run():
    cfg.verify_inputs()
    out = {"analysis_version": cfg.ANALYSIS_VERSION, "seed": cfg.SEED,
           "PC1_synthetic_implant": {K: pc1_synthetic_implant(K, cfg.SEED + K) for K in (1, 2, 3, 5, 8)},
           "PC2_degraded_implant": {K: pc2_degraded_implant(K, cfg.SEED + 100 + K) for K in (1, 2, 3, 5)},
           "PC3_lb_internal_matched_scarcity": pc3_lb_internal(cfg.SEED + 7),
           "PC4_face_validity": "PA-I-TO ≡ pa-i-to matches A1-A4, A5 breaks (see model/test); "
                                "DEVELOPMENT_FACE_VALIDITY_ONLY, sets no threshold, no confirmatory weight"}
    return out


if __name__ == "__main__":
    r = run()
    print("PC1 recovery (A1):", {K: r["PC1_synthetic_implant"][K]["A1"] for K in (1, 3, 8)})
    print("PC2 degraded recovery:", {K: r["PC2_degraded_implant"][K] for K in (1, 3)})
    print("PC3 LB-internal:", r["PC3_lb_internal_matched_scarcity"])
    os.makedirs(cfg.RESULTS, exist_ok=True)
    json.dump(r, open(os.path.join(cfg.RESULTS, "positive_controls.json"), "w"), indent=1, default=str)
    print("saved positive_controls.json")
