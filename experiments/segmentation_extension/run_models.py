#!/usr/bin/env python3
"""run_models.py — graded runs for the three pre-registered model classes (PREREG §5), under
the gate-verified protocol: identical corpus, identical LOSO folds (quirk included), identical
frozen metric, identical random reference (reused per-site counts from the Gate A run —
byte-identical pairing), reconstructed bootstrap at seed 20260703.

Phases:
  0. PYP sanity checks (non-graded, PREREG §5.1): planted lexicon; d=0/fixed-hypers in-sample
     neighborhood vs the DP baseline.
  1. Class 1 PYP — 3 chains x 52 folds in a process pool (chain-level jobs), posterior-mean
     decode, split-R-hat per fold.
  2. Class 2 tiny BiLSTM — graded seed 20260703 + stability seeds 20260704/05 (52 folds each).
  3. Class 3 Morfessor tuned corpusweight — 52 folds.
  4. Site-clustered bootstrap grading of every entry vs the random floor and vs the DP anchor.

Usage: python3 run_models.py [--workers N]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

from frozen_metric import (DPUnigramSegmenter, SignCodec, _score_segmenter_on, load_corpus)
from harness import save_json, site_cluster_bootstrap
import models_pyp as P

RESULTS = os.path.join(_HERE, "results")
BOOT_SEED = 20260703
NEURAL_SEEDS = (20260703, 20260704, 20260705)   # first = graded, rest = stability

_G: dict = {}


def _init_worker() -> None:
    corpus = load_corpus()
    codec = SignCodec.from_corpus(corpus)
    by_site: dict = {}
    for ins in corpus:
        by_site.setdefault(ins.site or "(unknown)", []).append(ins)
    _G.update(corpus=corpus, codec=codec, by_site=by_site,
              sites=sorted(by_site))


def _fold(site: str):
    corpus, codec, by_site = _G["corpus"], _G["codec"], _G["by_site"]
    train = [ins for ins in corpus if ins.site != site]          # gate-verified quirk kept
    test = by_site[site]
    train_utts = [codec.enc_word(ins.signs) for ins in train if len(ins.signs) >= 1]
    return train, test, train_utts


# ---------------- Class 1: PYP (chain-level jobs) ---------------- #
def _pyp_chain_job(args):
    site, fold_idx, chain_id = args
    _, _, train_utts = _fold(site)
    vocab = max(1, len({c for u in train_utts for c in u}))
    seed = P.SEED_BASE + 1000 * chain_id + fold_idx
    t0 = time.time()
    res = P.run_chain(train_utts, vocab, seed)
    res["site"], res["chain_id"] = site, chain_id
    res["secs"] = round(time.time() - t0, 1)
    return res


# ---------------- Class 2: neural (fold-level jobs) ---------------- #
def _neural_job(args):
    site, seed = args
    from models_neural import NeuralBoundarySegmenter
    train, test, _ = _fold(site)
    # PREREG Addendum A: the SUPERVISED class must never train on the held-out site's labels;
    # the gate quirk would otherwise put the "(unknown)" fold's 2 labeled test streams into
    # supervised training (no-op for the other 51 folds; unsupervised entries keep the quirk).
    train = [ins for ins in train if (ins.site or "(unknown)") != site]
    codec = _G["codec"]
    t0 = time.time()
    seg = NeuralBoundarySegmenter(train, codec, seed)
    return {"site": site, "seed": seed,
            "test": _score_segmenter_on(test, codec, seg),
            "train": _score_segmenter_on(train, codec, seg),
            "threshold": seg.threshold, "n_params": seg.n_params,
            "n_train_streams": seg.n_train_streams, "n_dev_streams": seg.n_dev_streams,
            "secs": round(time.time() - t0, 1)}


# ---------------- Class 3: morfessor tuned (fold-level jobs) ---------------- #
def _morf_job(site: str):
    from frozen_metric import _boundary_rate
    from models_morfessor import TunedMorfessorSegmenter
    train, test, train_utts = _fold(site)
    codec = _G["codec"]
    t0 = time.time()
    seg = TunedMorfessorSegmenter(train_utts, target_rate=_boundary_rate(train))
    return {"site": site,
            "test": _score_segmenter_on(test, codec, seg),
            "train": _score_segmenter_on(train, codec, seg),
            "corpusweight": seg.corpusweight, "train_pred_rate": seg.train_rate,
            "target_rate": seg.target_rate, "secs": round(time.time() - t0, 1)}


def _micro(counts_list):
    tp = sum(c["tp"] for c in counts_list)
    fp = sum(c["fp"] for c in counts_list)
    fn = sum(c["fn"] for c in counts_list)
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return {"micro_f1": round(f1, 4), "micro_precision": round(prec, 4),
            "micro_recall": round(rec, 4), "tp": tp, "fp": fp, "fn": fn}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=18)
    args = ap.parse_args()

    with open(os.path.join(RESULTS, "loso_baseline_counts.json"), encoding="utf-8") as f:
        base = json.load(f)
    sites = base["sites"]
    assert len(sites) == 52

    _init_worker()                                   # parent needs corpus/codec too
    corpus, codec = _G["corpus"], _G["codec"]

    # ---------- Phase 0: PYP sanity (non-graded) ----------
    print("[phase 0] PYP sanity checks", flush=True)
    utts = ["xy"] * 15 + ["ab"] * 15 + ["xyab", "abxy", "xyxy", "abab"]
    ch = [P.run_chain(utts, 4, s, sweeps=300, burnin=150) for s in (1, 2, 3)]
    dec = P.fit_fold(utts, 0, chain_results=ch)["decoder"]
    planted_ok = dec.segment("xyxy") == ["xy", "xy"] and dec.segment("xyab") == ["xy", "ab"]

    all_utts = [codec.enc_word(ins.signs) for ins in corpus if len(ins.signs) >= 1]
    vs = max(1, len({c for u in all_utts for c in u}))
    dz = [P.run_chain(all_utts, vs, 40 + i, fix_d_zero=True, fix_hypers=True) for i in (1, 2, 3)]
    dz_dec = P.PYPPosteriorMeanDecoder(dz, vs)
    dz_f1 = _score_segmenter_on(corpus, codec, dz_dec)["f1"]
    dp_in = DPUnigramSegmenter(iters=6, seed=0).fit(all_utts)
    dp_f1 = _score_segmenter_on(corpus, codec, dp_in)["f1"]
    sanity = {"planted_lexicon_recovered": planted_ok,
              "d0_fixed_hypers_insample_f1": round(dz_f1, 4),
              "dp_baseline_insample_f1": round(dp_f1, 4)}
    print("  sanity:", sanity, flush=True)
    if not planted_ok:
        print("STOP: PYP planted-lexicon sanity failed — implementation bug", flush=True)
        return 1

    per_site = {s: {"entries": {}, "random": base["per_site"][s]["random"],
                    "n_test": base["per_site"][s]["n_test"]} for s in sites}
    for s in sites:                                   # DP anchor from the gate-verified run
        per_site[s]["entries"]["dp_unigram"] = base["per_site"][s]["entries"]["dp_unigram"]

    diag: dict = {"sanity": sanity}
    wall: dict = {}

    with Pool(args.workers, initializer=_init_worker) as pool:
        # ---------- Phase 1: PYP ----------
        print("[phase 1] PYP unigram Gibbs: 3 chains x 52 folds", flush=True)
        t0 = time.time()
        jobs = [(s, i, c) for i, s in enumerate(sites) for c in (1, 2, 3)]
        chain_res = pool.map(_pyp_chain_job, jobs, chunksize=1)
        by_fold: dict = {}
        for r in chain_res:
            by_fold.setdefault(r["site"], []).append(r)
        pyp_diag = {}
        for i, s in enumerate(sites):
            train, test, train_utts = _fold(s)
            fold = P.fit_fold(train_utts, i, chain_results=sorted(by_fold[s], key=lambda r: r["chain_id"]))
            seg = fold["decoder"]
            per_site[s]["entries"]["pyp_unigram"] = _score_segmenter_on(test, codec, seg)
            pyp_diag[s] = {"rhat": round(fold["rhat"], 4), "post_mean": {
                k: round(v, 4) for k, v in fold["post_mean"].items()},
                "chain_seeds": fold["chain_seeds"],
                "train_f1": round(_score_segmenter_on(train, codec, seg)["f1"], 4)}
        wall["pyp_s"] = round(time.time() - t0, 1)
        diag["pyp"] = pyp_diag
        rh = [d["rhat"] for d in pyp_diag.values() if not np.isnan(d["rhat"])]
        print(f"  PYP done in {wall['pyp_s']}s; rhat max={max(rh):.3f} "
              f"median={np.median(rh):.3f}", flush=True)

        # ---------- Phase 2: neural ----------
        print("[phase 2] tiny BiLSTM: graded + 2 stability seeds x 52 folds", flush=True)
        t0 = time.time()
        njobs = [(s, seed) for seed in NEURAL_SEEDS for s in sites]
        nres = pool.map(_neural_job, njobs, chunksize=1)
        neural_diag: dict = {}
        for seed in NEURAL_SEEDS:
            rows = {r["site"]: r for r in nres if r["seed"] == seed}
            name = "neural_bilstm" if seed == NEURAL_SEEDS[0] else f"neural_bilstm_s{seed}"
            for s in sites:
                per_site[s]["entries"][name] = rows[s]["test"]
            train_micro = _micro([rows[s]["train"] for s in sites])
            test_micro = _micro([rows[s]["test"] for s in sites])
            neural_diag[name] = {
                "seed": seed, "n_params": rows[sites[0]]["n_params"],
                "train_micro_f1": train_micro["micro_f1"],
                "test_micro_f1": test_micro["micro_f1"],
                "train_test_gap": round(train_micro["micro_f1"] - test_micro["micro_f1"], 4),
                "memorization_flag": (train_micro["micro_f1"] - test_micro["micro_f1"]) > 0.20,
                "thresholds": {s: rows[s]["threshold"] for s in sites}}
        wall["neural_s"] = round(time.time() - t0, 1)
        diag["neural"] = neural_diag
        print(f"  neural done in {wall['neural_s']}s", flush=True)

        # ---------- Phase 3: morfessor tuned ----------
        print("[phase 3] Morfessor tuned corpusweight x 52 folds", flush=True)
        t0 = time.time()
        mres = pool.map(_morf_job, sites, chunksize=1)
        mrows = {r["site"]: r for r in mres}
        for s in sites:
            per_site[s]["entries"]["morfessor_tuned"] = mrows[s]["test"]
        diag["morfessor_tuned"] = {s: {"corpusweight": mrows[s]["corpusweight"],
                                       "train_pred_rate": round(mrows[s]["train_pred_rate"], 4),
                                       "target_rate": round(mrows[s]["target_rate"], 4)}
                                   for s in sites}
        wall["morfessor_s"] = round(time.time() - t0, 1)
        print(f"  morfessor done in {wall['morfessor_s']}s", flush=True)

    # ---------- Phase 4: bootstrap grading ----------
    print("[phase 4] site-clustered bootstrap grading", flush=True)
    loso = {"per_site": per_site, "sites": sites, "seed": 0}
    entries = ["dp_unigram", "pyp_unigram", "neural_bilstm", "morfessor_tuned",
               f"neural_bilstm_s{NEURAL_SEEDS[1]}", f"neural_bilstm_s{NEURAL_SEEDS[2]}"]
    vs_random = site_cluster_bootstrap(loso, entries, reference="random",
                                       B=4000, seed=BOOT_SEED)
    vs_dp = site_cluster_bootstrap(loso, [e for e in entries if e != "dp_unigram"],
                                   reference="dp_unigram", B=4000, seed=BOOT_SEED)

    micro = {nm: _micro([per_site[s]["entries"][nm] for s in sites]) for nm in entries}
    micro["random"] = _micro([per_site[s]["random"] for s in sites])

    summary = {"micro": micro, "bootstrap_vs_random": vs_random,
               "bootstrap_vs_dp_unigram": vs_dp, "wall_clock": wall,
               "boot_seed": BOOT_SEED, "sanity": sanity}
    save_json({"per_site": per_site, "sites": sites}, os.path.join(RESULTS, "models_loso_counts.json"))
    save_json(diag, os.path.join(RESULTS, "models_diagnostics.json"))
    save_json(summary, os.path.join(RESULTS, "models_summary.json"))

    print(json.dumps({k: v for k, v in summary.items() if k != "wall_clock"},
                     indent=2, default=str)[:4000], flush=True)
    print("wall_clock:", wall, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
