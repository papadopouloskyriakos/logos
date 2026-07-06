"""§VII calibrated power analysis + risk-adjusted channel comparison.

Detection rule (from §V nulls): the null match-count distribution has mean ≈ 0.0125 and P(≥1) ≈ 1.25%
< 5%, so the null 95th percentile is 0 → **any ≥1 recovered match is significant (detected)**.

Crucial modelling point: A3's ≤1-wildcard tolerates TRANSCRIPTION uncertainty (a damage/composite-
FLAGGED position), NOT genuine orthographic DRIFT (a real spelling change like RU→RI, which is
unflagged). So a genuinely drifted true pair is unrecoverable under the no-free-mapping constraint.
"""
import json, os, random, sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
import cfg, model as M, partitions as P  # noqa: E402

NULL_95_THRESHOLD = 1          # ≥1 match exceeds the null 95th pct (0) → detected
KNOWN_EXACT_FRACTION = 2 / 5   # empirical: PA-I-TO, SE-TO-I-JA exact; TU-RU-SA/I-DA/DI-KI-TA drifted/derived/absent


def _to_ab(seq):
    return ["AB%02d" % n if isinstance(n, int) else str(n) for n in seq]


def implant_recovery(n_true, drift, genuine_drift, seed):
    """Implant n_true continuity pairs with `drift` sign changes; genuine_drift=True → positions unflagged
    (A3 can't help); False → flagged transcription uncertainty (A3's tolerance applies). Return recovery."""
    prim = [dict(candidate_id=c["candidate_id"], raw_sign_ids=list(c["raw_sign_ids"]),
                 uncertainty=dict(c["uncertainty"])) for c in P.partitioned()["PRIMARY_B"]]
    ev = [t for t in P.load_targets() if t["development_or_evaluation_role"] == "EVALUATION"]
    rng = random.Random(seed)
    tby_len = {}
    for t in ev:
        tby_len.setdefault(len(M.lb_seq(t)), []).append(t)
    implanted = []
    for c in prim:
        if len(implanted) >= n_true:
            break
        L = len(M.la_seq(c))
        opts = tby_len.get(L, [])
        if not opts:
            continue
        t = rng.choice(opts)
        ab = _to_ab(M.lb_seq(t))
        pos = rng.sample(range(len(ab)), min(drift, len(ab)))
        for i in pos:
            ab[i] = "AB%02d" % ((int(ab[i][2:]) % 90) + 1)
        c["raw_sign_ids"] = ab
        c["uncertainty"]["composite_sensitive"] = (not genuine_drift and drift >= 1)
        implanted.append((c["candidate_id"], t["lb_target_id"]))
    out = {}
    for Ly in ("A1", "A2", "A3"):
        pairs = set(M.match_pairs(prim, ev, Ly))
        got = sum(1 for imp in implanted if imp in pairs)
        out[Ly] = {"implanted": len(implanted), "recovered": got,
                   "detected": got >= NULL_95_THRESHOLD}
    return out


def power_envelope():
    grid = {}
    for drift in (0, 1, 2):
        for gd in ((False,) if drift == 0 else (True, False)):
            key = "drift0" if drift == 0 else f"drift{drift}_{'genuine' if gd else 'transcription'}"
            grid[key] = {n: implant_recovery(n, drift, gd, cfg.SEED + drift * 10 + n) for n in (1, 2, 3, 5)}
    return grid


def summarize(grid):
    exact = grid["drift0"]
    det_exact_1 = exact[1]["A1"]["detected"]
    drift1_gen = grid["drift1_genuine"]
    drift2_gen = grid["drift2_genuine"]
    drift1_trans = grid["drift1_transcription"]
    return {
        "detection_rule": "≥1 recovered match (null 95th pct = 0; FP≥1 ≈ 1.25%)",
        "exact_continuity": {"min_detectable_pairs": 1, "recovery_at_1": exact[1]["A1"]["recovered"],
                             "detected_at_1": det_exact_1, "power": "FULL for exact continuity"},
        "genuine_drift_1": {"A1_detected": drift1_gen[1]["A1"]["detected"],
                            "A3_detected": drift1_gen[1]["A3"]["detected"],
                            "note": "genuine 1-sign drift is UNFLAGGED → A3 cannot help → undetectable"},
        "genuine_drift_2": {"A3_detected": drift2_gen[1]["A3"]["detected"], "note": "undetectable"},
        "transcription_uncertainty_1": {"A3_detected": drift1_trans[1]["A3"]["detected"],
                                        "note": "a FLAGGED transcription-uncertain position IS recovered by A3"},
        "min_detectable_pairs_exact": 1,
        "min_detectable_pairs_drifted": None,           # undetectable by design
        "a4_vs_a5_specificity": "A4 recovers exact, A5 (wrong values) does not (§III/PC4) → phonetic "
                                "specificity present; moot given 0 observed",
        "high_attestation_effect": {"n_primary": 11, "note": "restricting to high-attestation shrinks the "
                                    "already tiny candidate set; does not create signal"},
        "primary_vs_bc": {"primary_observed": 0, "bc_observed": 0, "note": "B+C (44) also yields 0"},
        "prob_no_power_realistic": round(1 - KNOWN_EXACT_FRACTION, 3),   # fraction of true continuity that drifts → undetectable
        "interpretation": "The design has FULL power for EXACT administrative continuity (min detectable "
                          "= 1 pair, FP≈1.25%) and found 0. It has ZERO power for genuinely DRIFTED "
                          "continuity (the realistic case; ~60% of known continuities drift), because "
                          "recovery would require the forbidden free mapping search.",
    }


def channel_comparison():
    return {
        "LA_LB_administrative": {"end_to_end_fp": 0.0125, "combined_best_of_search_fp": 0.0321,
                                 "recovery_exact": 1.0, "recovery_genuine_drift": 0.0,
                                 "major_assumptions": ["no free mapping", "exact/near-exact identity",
                                                       "administrative domain only"],
                                 "circularity_risk": "LOW (candidate blind, target independent, map blind)",
                                 "source_dependencies": ["silver (lineara.xyz)", "SigLA AB-class", "DĀMOS"]},
        "egyptian_pilot": {"provisional_held_out_fp": "0.22-0.30", "provisional_recovery": "0.35-0.45",
                           "distortion_model_dependence": "HIGH (Egyptian group-writing model, unfit)",
                           "source_dependencies": ["Kilani 2019 (unfit)", "Cline&Stannish secondary"]},
        "verdict": "LA↔LB is far MORE SPECIFIC (FP 1.25% vs 22-30%) but has near-zero sensitivity to "
                   "drifted continuity; the Egyptian channel is less specific and its model is unfit. "
                   "Neither channel currently supports a confirmatory claim; LA↔LB is preferable ONLY "
                   "for the narrow exact-continuity sub-question, which it answered negatively.",
    }


def run():
    cfg.verify_inputs()
    grid = power_envelope()
    return {"analysis_version": cfg.ANALYSIS_VERSION, "grid": grid,
            "summary": summarize(grid), "channel_comparison": channel_comparison()}


if __name__ == "__main__":
    r = run()
    s = r["summary"]
    print("exact continuity:", s["exact_continuity"])
    print("genuine drift-1:", s["genuine_drift_1"])
    print("transcription-uncertain-1:", s["transcription_uncertainty_1"])
    print("P(NO_POWER realistic):", s["prob_no_power_realistic"])
    print("channel verdict:", r["channel_comparison"]["verdict"])
    os.makedirs(cfg.RESULTS, exist_ok=True)
    json.dump(r, open(os.path.join(cfg.RESULTS, "power.json"), "w"), indent=1, default=str)
    print("saved power.json")
