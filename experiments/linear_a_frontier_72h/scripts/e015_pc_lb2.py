#!/usr/bin/env python3
"""EPOCH-015 phase 1b — PC-LB under logged deviations D1+D2 (see epochs/EPOCH-015/DEVIATIONS.md).

D2: correlation-preserving stream-level marginalized null (uniform, both real + wrong-structure).
D1: posthoc scoring at p<=0.05 (target was empty at the preregistered 0.01 even on gold) +
    better-powered posthoc reference target G_full (all 11,908 gold words, n_null=1000, p<=0.01).
Original prereg-null run is preserved in pc_lb.json (append-only). Also exports the LB calibration
map for the LA phase.
"""
from __future__ import annotations
import json, os, random, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e015_lib as L


def pipeline(train_tabs, test_tabs):
    train_sg = [L.to_stream(t) for t in train_tabs]
    test_sg = [L.to_stream(t) for t in test_tabs]
    cue = L.CueModel([s for s, _ in train_sg])
    calib, calib_table = L.calibrate(cue, train_sg)
    train_probs = [L.gap_probs(cue, calib, s) for s, _ in train_sg]
    sel = {r: L.boundary_f1(L.frozen_gaps(train_probs, r), [g for _, g in train_sg])
           for r in ("MAP", "MEAN")}
    rule = "MAP" if sel["MAP"]["f1"] >= sel["MEAN"]["f1"] else "MEAN"
    test_probs = [L.gap_probs(cue, calib, s) for s, _ in test_sg]
    test_streams = [s for s, _ in test_sg]
    test_gold = [g for _, g in test_sg]
    fro_gaps = L.frozen_gaps(test_probs, rule)
    fro_words = [w for g, s in zip(fro_gaps, test_streams) for w in L.words_from_gaps(s, g)]
    gapsets_by_seed = {}
    for ms in (L.SEED, L.SEED + 1, L.SEED + 2):
        gapsets_by_seed[ms] = [L.sample_gaps(test_probs, seed=ms * 1000 + k)
                               for k in range(L.K_SAMPLES)]
    return {"calib": calib, "calib_table": calib_table, "rule": rule, "sel": sel,
            "test_streams": test_streams, "test_gold": test_gold,
            "fro_gaps": fro_gaps, "fro_words": fro_words,
            "gapsets_by_seed": gapsets_by_seed}


def main():
    t0 = time.time()
    tabs = L.load_lb_tablets()
    rng = random.Random(L.SEED)
    idx = list(range(len(tabs)))
    rng.shuffle(idx)
    n_train = int(0.7 * len(tabs))
    train = [tabs[i] for i in idx[:n_train]]
    test = [tabs[i] for i in idx[n_train:]]
    gold_words = [w for t in test for w in t]
    U = L.candidate_universe(gold_words)

    out = {"deviations_applied": ["D1", "D2"], "K": L.K_SAMPLES, "universe_n": len(U)}

    P = pipeline(train, test)
    # export calibration for LA phase
    json.dump({"calib": {"".join(map(str, k)): v for k, v in P["calib"].items()},
               "rule": P["rule"], "calib_table": P["calib_table"]},
              open(os.path.join(L.DATA, "lb_calibration.json"), "w"), indent=1)

    # gold + frozen arm p-values (unchanged machinery, E1 word-level null)
    pv_gold = L.null_pvals(gold_words, U, L.N_NULL_INV, seed=L.SEED)
    pv_fro = L.null_pvals(P["fro_words"], U, L.N_NULL_INV, seed=L.SEED + 10)

    # D2 marginalized arm, 3 sampling-seed replicates
    pv_marg = {}
    for ms, gapsets in P["gapsets_by_seed"].items():
        pv_marg[ms] = L.marg_null_pvals_stream(P["test_streams"], gapsets, U,
                                               L.N_NULL_INV, seed=L.SEED + 20 + ms % 10)

    # wrong-structure arm (full re-run on within-word shuffled corpus)
    wrng = random.Random(L.SEED + 777)
    def shuf(tablets):
        res = []
        for t in tablets:
            nt = []
            for w in t:
                w = list(w); wrng.shuffle(w); nt.append(tuple(w))
            res.append(nt)
        return res
    PW = pipeline(shuf(train), shuf(test))
    pv_fro_w = L.null_pvals(PW["fro_words"], U, L.N_NULL_INV, seed=L.SEED + 30)
    pv_marg_w = L.marg_null_pvals_stream(PW["test_streams"], PW["gapsets_by_seed"][L.SEED],
                                         U, L.N_NULL_INV, seed=L.SEED + 31)

    # posthoc G_full reference target (all gold words, n_null=1000, p<=0.01)
    all_gold_words = [w for t in tabs for w in t]
    pv_gfull = L.null_pvals(all_gold_words, U, 1000, seed=L.SEED + 40)
    G_full = {t for t in U if pv_gfull[t]["p"] <= 0.01}

    def inv(pv, thr):
        return {t for t in U if pv[t]["p"] <= thr}

    scoring = {}
    for thr, tag in ((0.01, "prereg_0.01"), (0.05, "D1_0.05")):
        G = inv(pv_gold, thr)
        A_f, A_fw = inv(pv_fro, thr), inv(pv_fro_w, thr)
        A_m = {ms: inv(pv_marg[ms], thr) for ms in pv_marg}
        A_mw = inv(pv_marg_w, thr)
        main_m = A_m[L.SEED]
        fro_rec = L.set_f1(A_f, G, U)
        marg_rec = {str(ms): L.set_f1(A_m[ms], G, U) for ms in A_m}
        deltas = {str(ms): round(marg_rec[str(ms)]["f1"] - fro_rec["f1"], 4) for ms in A_m}
        mc = L.mcnemar_exact(A_f, main_m, G, U)
        wf, wm = L.set_f1(A_fw, G, U), L.set_f1(A_mw, G, U)
        gate = (fro_rec["f1"] > wf["f1"] and marg_rec[str(L.SEED)]["f1"] > wm["f1"])
        d_main = deltas[str(L.SEED)]
        if not gate:
            v = "MACHINERY_UNINFORMATIVE"
        elif d_main > 0 and mc["p"] <= 0.05 and all(d > 0 for d in deltas.values()):
            v = "MARGINALIZATION_IMPROVES"
        elif d_main < 0 and mc["p"] <= 0.05 and all(d < 0 for d in deltas.values()):
            v = "MARGINALIZATION_DEGRADES"
        else:
            v = "MARGINALIZATION_NEUTRAL"
        scoring[tag] = {
            "gold_inventory": sorted(L.tkey(t) for t in G),
            "frozen_inventory": sorted(L.tkey(t) for t in A_f),
            "marg_inventory_main": sorted(L.tkey(t) for t in main_m),
            "frozen_recovery": fro_rec, "marg_recovery": marg_rec, "delta_f1": deltas,
            "mcnemar": mc,
            "wrong_structure": {"frozen": wf, "marg": wm,
                                "frozen_inv": sorted(L.tkey(t) for t in A_fw),
                                "marg_inv": sorted(L.tkey(t) for t in A_mw)},
            "machinery_informative": gate, "verdict": v}

    # G_full-target scoring (posthoc, decision rule 0.01 on arms)
    G = G_full
    A_f = inv(pv_fro, 0.01)
    A_m_main = inv(pv_marg[L.SEED], 0.01)
    scoring["Gfull_target"] = {
        "gold_inventory_full": sorted(L.tkey(t) for t in G_full),
        "gfull_stats_top": {L.tkey(t): pv_gfull[t] for t in
                            sorted(U, key=lambda t: pv_gfull[t]["p"])[:15]},
        "frozen_recovery": L.set_f1(A_f, G, U),
        "marg_recovery_main": L.set_f1(A_m_main, G, U),
        "mcnemar": L.mcnemar_exact(A_f, A_m_main, G, U),
        "wrong_structure": {"frozen": L.set_f1(inv(pv_fro_w, 0.01), G, U),
                            "marg": L.set_f1(inv(pv_marg_w, 0.01), G, U)}}

    out["boundary"] = {
        "rule": P["rule"], "train_sel": P["sel"],
        "test_frozen_f1": L.boundary_f1(P["fro_gaps"], P["test_gold"]),
        "test_sample0_f1": L.boundary_f1(P["gapsets_by_seed"][L.SEED][0], P["test_gold"]),
        "cut_rate_frozen": L.cut_rate(P["fro_gaps"], P["test_streams"]),
        "cut_rate_sample0": L.cut_rate(P["gapsets_by_seed"][L.SEED][0], P["test_streams"]),
        "gold_cut_rate": L.cut_rate(P["test_gold"], P["test_streams"])}
    out["scoring"] = scoring
    out["per_candidate"] = {L.tkey(t): {"gold": pv_gold[t], "frozen": pv_fro[t],
                                        "marg_D2_main": pv_marg[L.SEED][t],
                                        "gfull": pv_gfull[t]} for t in U}
    out["runtime_s"] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(L.DATA, "pc_lb_d2.json"), "w"), indent=1)

    slim = {"boundary": out["boundary"]}
    for tag in scoring:
        s = dict(scoring[tag])
        s.pop("marg_recovery", None)
        slim[tag] = s
    print(json.dumps(slim, indent=1, default=str))
    print("runtime_s", out["runtime_s"])


if __name__ == "__main__":
    main()
