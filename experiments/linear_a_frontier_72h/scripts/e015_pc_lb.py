#!/usr/bin/env python3
"""EPOCH-015 phase 1 — LB opaque positive control + wrong-structure null (prereg d35828be).

Runs FIRST. Gold affix inventory from gold-boundary TEST words; FROZEN vs MARGINALIZED
recovery on opaque streams; wrong-structure (within-word sign shuffle) must collapse.
"""
from __future__ import annotations
import json, os, random, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e015_lib as L


def run_pipeline(train_tabs, test_tabs, tag, marg_seeds, out):
    """Full pipeline on given tablets. Returns dict with calib, frozen rule, inventories."""
    train_sg = [L.to_stream(t) for t in train_tabs]
    test_sg = [L.to_stream(t) for t in test_tabs]
    cue = L.CueModel([s for s, _ in train_sg])
    calib, calib_table = L.calibrate(cue, train_sg)

    # frozen-rule selection on TRAIN (gold boundary F1)
    train_probs = [L.gap_probs(cue, calib, s) for s, _ in train_sg]
    train_gold = [g for _, g in train_sg]
    train_streams = [s for s, _ in train_sg]
    sel = {}
    for rule in ("MAP", "MEAN"):
        gaps = L.frozen_gaps(train_probs, rule)
        sel[rule] = L.boundary_f1(gaps, train_gold)
    rule = "MAP" if sel["MAP"]["f1"] >= sel["MEAN"]["f1"] else "MEAN"

    # TEST arms
    test_probs = [L.gap_probs(cue, calib, s) for s, _ in test_sg]
    test_gold = [g for _, g in test_sg]
    test_streams = [s for s, _ in test_sg]
    fro_gaps = L.frozen_gaps(test_probs, rule)
    fro_bf1 = L.boundary_f1(fro_gaps, test_gold)
    fro_words = [w for gaps, (s, _) in zip(fro_gaps, test_sg)
                 for w in L.words_from_gaps(s, gaps)]

    marg_words_by_seed = {}
    samp_bf1 = None
    for ms in marg_seeds:
        wls = []
        for k in range(L.K_SAMPLES):
            gaps = L.sample_gaps(test_probs, seed=ms * 1000 + k)
            if ms == marg_seeds[0] and k == 0:
                samp_bf1 = L.boundary_f1(gaps, test_gold)
            wls.append([w for g, (s, _) in zip(gaps, test_sg)
                        for w in L.words_from_gaps(s, g)])
        marg_words_by_seed[ms] = wls

    out[tag] = {
        "calibration_table": calib_table,
        "frozen_rule_selected_on_train": {"rule": rule, "train_f1": sel},
        "test_boundary_f1_frozen": fro_bf1,
        "test_boundary_f1_first_sample": samp_bf1,
        "cut_rate_frozen": L.cut_rate(fro_gaps, test_streams),
        "gold_cut_rate": L.cut_rate(test_gold, test_streams),
    }
    return rule, fro_words, marg_words_by_seed, test_sg


def main():
    t0 = time.time()
    os.makedirs(L.DATA, exist_ok=True)
    tabs = L.load_lb_tablets()
    rng = random.Random(L.SEED)
    idx = list(range(len(tabs)))
    rng.shuffle(idx)
    n_train = int(0.7 * len(tabs))
    train = [tabs[i] for i in idx[:n_train]]
    test = [tabs[i] for i in idx[n_train:]]

    out = {"n_tablets": len(tabs), "n_train": len(train), "n_test": len(test),
           "seed": L.SEED, "K": L.K_SAMPLES}

    marg_seeds = [L.SEED, L.SEED + 1, L.SEED + 2]
    rule, fro_words, marg_by_seed, test_sg = run_pipeline(train, test, "real", marg_seeds, out)

    # gold reference on TEST
    gold_words = [w for t in test for w in t]
    U = L.candidate_universe(gold_words)
    G, pv_gold = L.inventory(gold_words, U, seed=L.SEED)
    out["universe"] = [L.tkey(u) for u in U]
    out["gold_inventory"] = sorted(L.tkey(t) for t in G)
    out["gold_stats"] = {L.tkey(t): pv_gold[t] for t in U}
    out["n_gold_words_test"] = len(gold_words)
    out["n_frozen_words_test"] = len(fro_words)

    # FROZEN inventory
    A_f, pv_f = L.inventory(fro_words, U, seed=L.SEED + 10)
    out["frozen_inventory"] = sorted(L.tkey(t) for t in A_f)
    out["frozen_recovery"] = L.set_f1(A_f, G, U)

    # MARGINALIZED inventory (3 sampling-seed replicates)
    marg_res = {}
    A_m_main = None
    for ms in marg_seeds:
        A_m, pv_m = L.marg_inventory(marg_by_seed[ms], U, seed=L.SEED + 20 + ms % 10)
        marg_res[str(ms)] = {"inventory": sorted(L.tkey(t) for t in A_m),
                             "recovery": L.set_f1(A_m, G, U)}
        if ms == L.SEED:
            A_m_main = A_m
            out["marg_stats_main"] = {L.tkey(t): pv_m[t] for t in U}
    out["marg_replicates"] = marg_res
    out["marg_recovery_main"] = marg_res[str(L.SEED)]["recovery"]

    # McNemar frozen vs marginalized (main seed)
    out["mcnemar_frozen_vs_marg"] = L.mcnemar_exact(A_f, A_m_main, G, U)
    out["delta_f1_by_seed"] = {str(ms): round(marg_res[str(ms)]["recovery"]["f1"] -
                                              out["frozen_recovery"]["f1"], 4)
                               for ms in marg_seeds}

    # -------- wrong-structure null: shuffle signs WITHIN each gold word, full re-run
    wrng = random.Random(L.SEED + 777)
    def shuf(tablets):
        out_t = []
        for t in tablets:
            nt = []
            for w in t:
                w = list(w)
                wrng.shuffle(w)
                nt.append(tuple(w))
            out_t.append(nt)
        return out_t
    train_w, test_w = shuf(train), shuf(test)
    rule_w, fro_words_w, marg_by_seed_w, _ = run_pipeline(train_w, test_w, "wrong_structure",
                                                          [L.SEED], out)
    A_fw, _ = L.inventory(fro_words_w, U, seed=L.SEED + 30)
    A_mw, _ = L.marg_inventory(marg_by_seed_w[L.SEED], U, seed=L.SEED + 31)
    out["wrong_structure_frozen_recovery"] = L.set_f1(A_fw, G, U)
    out["wrong_structure_marg_recovery"] = L.set_f1(A_mw, G, U)

    # -------- machinery gate + primary verdict components (prereg rules)
    gate = (out["frozen_recovery"]["f1"] > out["wrong_structure_frozen_recovery"]["f1"] and
            out["marg_recovery_main"]["f1"] > out["wrong_structure_marg_recovery"]["f1"])
    out["machinery_informative"] = gate
    d_main = out["delta_f1_by_seed"][str(L.SEED)]
    deltas = list(out["delta_f1_by_seed"].values())
    mc_p = out["mcnemar_frozen_vs_marg"]["p"]
    if not gate:
        verdict = "MACHINERY_UNINFORMATIVE"
    elif d_main > 0 and mc_p <= 0.05 and all(d > 0 for d in deltas):
        verdict = "MARGINALIZATION_IMPROVES"
    elif d_main < 0 and mc_p <= 0.05 and all(d < 0 for d in deltas):
        verdict = "MARGINALIZATION_DEGRADES"
    else:
        verdict = "MARGINALIZATION_NEUTRAL"
    out["pc_lb_verdict"] = verdict
    out["runtime_s"] = round(time.time() - t0, 1)

    with open(os.path.join(L.DATA, "pc_lb.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    summary = {k: out[k] for k in
               ["gold_inventory", "frozen_recovery", "marg_recovery_main",
                "delta_f1_by_seed", "mcnemar_frozen_vs_marg",
                "wrong_structure_frozen_recovery", "wrong_structure_marg_recovery",
                "machinery_informative", "pc_lb_verdict", "runtime_s"]}
    summary["real_arm"] = {k: out["real"][k] for k in
                           ["frozen_rule_selected_on_train", "test_boundary_f1_frozen",
                            "cut_rate_frozen", "gold_cut_rate"]}
    print(json.dumps(summary, indent=1, default=str))


if __name__ == "__main__":
    main()
