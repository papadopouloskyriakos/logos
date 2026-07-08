#!/usr/bin/env python3
"""EPOCH-015 phase 3 — LA application: A- confirmatory test + exploratory scan (Holm).

Uses LB TRAIN-calibrated cell->P(boundary) map (from lb_calibration.json), LA cue statistics
re-estimated unsupervised on ALL LA streams, layout-mark boost P_MARK=0.9 on GORILA word-word
gaps carrying div/num/nl/other. Sensitivity re-run at P_MARK in {0.7,1.0}.
"""
from __future__ import annotations
import json, os, random, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e015_lib as L


def build_la_probs(docs, calib, p_mark):
    streams = [d["signs"] for d in docs]
    cue = L.CueModel(streams)  # unsupervised, ALL LA streams
    probs = []
    for d in docs:
        ps = L.gap_probs(cue, calib, d["signs"], marked_gaps=d["marked_gaps"], p_mark=p_mark)
        probs.append(ps)
    return probs, cue


def gorila_words(docs):
    return [w for d in docs for w in d["words"] if len(w) >= 1]


def run(p_mark_main=L.P_MARK):
    t0 = time.time()
    calib_raw = json.load(open(os.path.join(L.DATA, "lb_calibration.json")))
    calib = {tuple(int(c) for c in k): v for k, v in calib_raw["calib"].items()}
    rule = calib_raw["rule"]

    docs = L.load_la_docs()
    streams = [d["signs"] for d in docs]
    U_gorila = L.candidate_universe(gorila_words(docs))  # frozen: GORILA words only

    sens = {}
    for p_mark in (0.7, L.P_MARK, 1.0):
        probs, cue = build_la_probs(docs, calib, p_mark)
        fro_gaps = L.frozen_gaps(probs, rule)
        fro_words = [w for g, s in zip(fro_gaps, streams) for w in L.words_from_gaps(s, g)]
        gorila_gaps = [d["gorila_gaps"] for d in docs]
        # agreement between induced frozen boundaries and GORILA word gaps, as a sanity proxy
        agree = L.boundary_f1(fro_gaps, gorila_gaps)
        cut_fro = L.cut_rate(fro_gaps, streams)
        cut_gorila = L.cut_rate(gorila_gaps, streams)
        sens[str(p_mark)] = {"cut_rate_frozen": cut_fro, "cut_rate_gorila": cut_gorila,
                              "agreement_vs_gorila_f1": agree,
                              "n_frozen_words": len(fro_words)}
        if p_mark == p_mark_main:
            main_probs, main_fro_gaps, main_fro_words = probs, fro_gaps, fro_words

    # ---------------- A- confirmatory test (single preregistered test, n_null=2000) ----------
    A_target = [("A", "PRE")]
    words_gorila = gorila_words(docs)
    pv_a_gorila = L.null_pvals(words_gorila, A_target, 2000, seed=L.SEED + 100)
    pv_a_frozen = L.null_pvals(main_fro_words, A_target, 2000, seed=L.SEED + 101)
    gapsets = [L.sample_gaps(main_probs, seed=L.SEED * 1000 + k) for k in range(L.K_SAMPLES)]
    pv_a_marg = L.marg_null_pvals_stream(streams, gapsets, A_target, 2000, seed=L.SEED + 102)

    p_b = pv_a_frozen[A_target[0]]["p"]
    p_c = pv_a_marg[A_target[0]]["p"]
    a_robust = p_c <= 0.05
    a_direction = "IMPROVES" if p_c <= p_b else "DEGRADES"

    a_result = {
        "gorila_anchor": pv_a_gorila[A_target[0]],
        "frozen_induced": pv_a_frozen[A_target[0]],
        "marginalized": pv_a_marg[A_target[0]],
        "robust_under_marginalization": a_robust,
        "direction": a_direction,
    }

    # ---------------- Exploratory scan (Holm, 71 candidates) --------------------------------
    U_scan = [t for t in U_gorila if t != ("A", "PRE")]
    pv_marg_scan = L.marg_null_pvals_stream(streams, gapsets, U_scan, 2000, seed=L.SEED + 200)
    pv_frozen_scan = L.null_pvals(main_fro_words, U_scan, 2000, seed=L.SEED + 201)
    pv_gorila_scan = L.null_pvals(words_gorila, U_scan, 2000, seed=L.SEED + 202)

    raw_p = {L.tkey(t): pv_marg_scan[t]["p"] for t in U_scan}
    holm_p = L.holm(raw_p)
    survivors = sorted([k for k, p in holm_p.items() if p <= 0.05], key=lambda k: holm_p[k])

    scan_table = []
    for t in sorted(U_scan, key=lambda t: pv_marg_scan[t]["p"]):
        k = L.tkey(t)
        scan_table.append({
            "candidate": k,
            "marg_obs": pv_marg_scan[t]["obs"], "marg_null_mean": pv_marg_scan[t]["null_mean"],
            "marg_p_raw": pv_marg_scan[t]["p"], "marg_p_holm": holm_p[k],
            "frozen_p": pv_frozen_scan[t]["p"], "gorila_p": pv_gorila_scan[t]["p"],
        })

    out = {
        "seed": L.SEED, "p_mark_main": p_mark_main,
        "n_docs": len(docs), "n_gorila_words": len(words_gorila),
        "n_frozen_words_main": len(main_fro_words),
        "universe_n_gorila_full": len(U_gorila), "universe_n_scan": len(U_scan),
        "sensitivity_p_mark": sens,
        "a_prefix_confirmatory": a_result,
        "exploratory_scan": {
            "n_candidates": len(U_scan), "n_survivors_holm05": len(survivors),
            "survivors": survivors, "table_top20": scan_table[:20],
        },
        "runtime_s": None,
    }
    out["runtime_s"] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(L.DATA, "la_application.json"), "w"), indent=1)
    json.dump(scan_table, open(os.path.join(L.DATA, "la_scan_full.json"), "w"), indent=1)

    print(json.dumps({k: v for k, v in out.items() if k not in ("exploratory_scan",)}, indent=1, default=str))
    print("n_survivors_holm05:", out["exploratory_scan"]["n_survivors_holm05"], out["exploratory_scan"]["survivors"])
    print("runtime_s", out["runtime_s"])


if __name__ == "__main__":
    run()
