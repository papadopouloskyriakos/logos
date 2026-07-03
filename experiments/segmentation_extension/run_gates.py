#!/usr/bin/env python3
"""run_gates.py — PREREG §3 hard equivalence gates. Runs BEFORE any model class; exits nonzero
(and prints a STOP report) on any failure. Gate criteria are frozen in PREREG.md.

Gate A: the experiment LOSO driver + frozen snapshot must reproduce the published deterministic
        point estimates to 4 decimals EXACTLY: DP-unigram micro-F1 0.4361, random 0.3888
        (Morfessor 0.1556 recorded informatively). Mismatch => STOP (a real discrepancy).
Gate B: the reconstructed bootstrap (B=4000, seed 20260703) on DP-unigram vs random must give
        95% CI bounds each within ±0.005 of [0.021, 0.099] and P(gap>0) >= 0.99.
        Seeds 20260704-20260707 reported as stability (informative, non-blocking).
"""
import json
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

from frozen_metric import DPUnigramSegmenter, MorfessorSegmenter, SignCodec, load_corpus
from harness import loso_counts, site_cluster_bootstrap, save_json

PUBLISHED = {"dp_unigram": 0.4361, "random": 0.3888, "morfessor_informative": 0.1556}
PUBLISHED_CI = (0.021, 0.099)
CI_TOL = 0.005
P_MIN = 0.99
BOOT_SEED = 20260703
STABILITY_SEEDS = (20260704, 20260705, 20260706, 20260707)


def main() -> int:
    corpus = load_corpus()
    codec = SignCodec.from_corpus(corpus)

    factories = {
        "dp_unigram": lambda ctx: DPUnigramSegmenter(iters=6, seed=0).fit(ctx.train_utts),
        "morfessor": lambda ctx: MorfessorSegmenter(seed=0).fit(ctx.train_utts),
    }
    t0 = time.time()
    loso = loso_counts(corpus, codec, factories, seed=0)
    loso_secs = time.time() - t0

    got = {"dp_unigram": loso["micro"]["dp_unigram"]["micro_f1"],
           "random": loso["micro"]["random"]["micro_f1"],
           "morfessor": loso["micro"]["morfessor"]["micro_f1"]}

    gate_a_pass = (got["dp_unigram"] == PUBLISHED["dp_unigram"]
                   and got["random"] == PUBLISHED["random"])

    results = {"gate_a": {"published": PUBLISHED, "reproduced": got,
                          "criterion": "4-decimal EXACT match on dp_unigram + random",
                          "pass": gate_a_pass, "loso_wall_clock_s": round(loso_secs, 1)}}

    if not gate_a_pass:
        results["verdict"] = "STOP — Gate A point estimates do not match exactly"
        save_json(results, os.path.join(_HERE, "results", "gate_results.json"))
        print(json.dumps(results, indent=2))
        return 1

    boot = site_cluster_bootstrap(loso, ["dp_unigram"], reference="random",
                                  B=4000, seed=BOOT_SEED)
    e = boot["entries"]["dp_unigram"]
    lo, hi = e["gap_ci95"]
    gate_b_pass = (abs(lo - PUBLISHED_CI[0]) <= CI_TOL and abs(hi - PUBLISHED_CI[1]) <= CI_TOL
                   and e["p_gap_gt_0"] >= P_MIN)

    stability = {}
    for s in STABILITY_SEEDS:
        bs = site_cluster_bootstrap(loso, ["dp_unigram"], reference="random", B=4000, seed=s)
        es = bs["entries"]["dp_unigram"]
        stability[s] = {"gap_ci95": [round(x, 4) for x in es["gap_ci95"]],
                        "p_gap_gt_0": es["p_gap_gt_0"]}

    results["gate_b"] = {
        "published_ci": list(PUBLISHED_CI), "tolerance": CI_TOL, "p_min": P_MIN,
        "seed": BOOT_SEED, "B": boot["B"],
        "reconstructed": {"gap_ci95": [round(lo, 4), round(hi, 4)],
                          "gap_mean": round(e["gap_mean"], 4),
                          "p_gap_gt_0": e["p_gap_gt_0"],
                          "gap_ci9833": [round(x, 4) for x in e["gap_ci9833"]]},
        "stability_seeds": stability,
        "pass": gate_b_pass,
    }
    results["verdict"] = ("GATES PASSED — model classes may run"
                          if gate_b_pass else "STOP — Gate B outside tolerance")

    save_json(results, os.path.join(_HERE, "results", "gate_results.json"))
    save_json(loso, os.path.join(_HERE, "results", "loso_baseline_counts.json"))
    print(json.dumps(results, indent=2))
    return 0 if gate_b_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
