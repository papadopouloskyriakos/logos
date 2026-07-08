#!/usr/bin/env python3
"""EPOCH-015 phase 2 — synthetic admin-syllabary control (graceful-degradation).

V = 60 CV signs; stem types Zipf(1.1); stem length 2-4; 4 reserved affix signs
(P1 prefix .25, S1/S2/S3 suffix .30/.15/.08 exclusive draws); documents 2-8 words;
token budget 1200 words/corpus; hapax regimes N_stem in {150,600,2400}; 5 seeds/regime;
70/30 split; calibration on synthetic TRAIN gold. Gold = 4 planted (sign,POS) pairs.
"""
from __future__ import annotations
import json, os, random, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e015_lib as L

VOCAB = [f"S{i:02d}" for i in range(60)]           # 60 CV content signs
AFFIXES = {"P1": ("PRE", 0.25), "S1": ("SUF", 0.30), "S2": ("SUF", 0.15), "S3": ("SUF", 0.08)}
GOLD = {("P1", "PRE"), ("S1", "SUF"), ("S2", "SUF"), ("S3", "SUF")}
TOKEN_BUDGET = 1200


def zipf_weights(n, s=1.1):
    return [1.0 / (i + 1) ** s for i in range(n)]


def make_corpus(n_stem, seed):
    rng = random.Random(seed)
    stem_types = []
    for _ in range(n_stem):
        L_ = rng.randint(2, 4)
        stem_types.append(tuple(rng.choice(VOCAB) for _ in range(L_)))
    wts = zipf_weights(n_stem)
    docs, words_flat = [], []
    tot = 0
    while tot < TOKEN_BUDGET:
        ndoc = rng.randint(2, 8)
        doc_words = []
        for _ in range(ndoc):
            stem = rng.choices(stem_types, weights=wts, k=1)[0]
            w = list(stem)
            if rng.random() < AFFIXES["P1"][1]:
                w = ["P1"] + w
            r = rng.random()
            if r < AFFIXES["S1"][1]:
                w = w + ["S1"]
            elif r < AFFIXES["S1"][1] + AFFIXES["S2"][1]:
                w = w + ["S2"]
            elif r < AFFIXES["S1"][1] + AFFIXES["S2"][1] + AFFIXES["S3"][1]:
                w = w + ["S3"]
            w = tuple(w)
            doc_words.append(w)
            words_flat.append(w)
        docs.append(doc_words)
        tot += ndoc
    return docs, n_stem


def run_regime(n_stem, seed):
    docs, _ = make_corpus(n_stem, seed)
    rng = random.Random(seed + 5000)
    idx = list(range(len(docs)))
    rng.shuffle(idx)
    n_train = max(1, int(0.7 * len(docs)))
    train_docs = [docs[i] for i in idx[:n_train]]
    test_docs = [docs[i] for i in idx[n_train:]]

    train_sg = [L.to_stream(d) for d in train_docs]
    test_sg = [L.to_stream(d) for d in test_docs]
    cue = L.CueModel([s for s, _ in train_sg])
    calib, _ = L.calibrate(cue, train_sg)
    train_probs = [L.gap_probs(cue, calib, s) for s, _ in train_sg]
    sel = {r: L.boundary_f1(L.frozen_gaps(train_probs, r), [g for _, g in train_sg])
           for r in ("MAP", "MEAN")}
    rule = "MAP" if sel["MAP"]["f1"] >= sel["MEAN"]["f1"] else "MEAN"

    test_probs = [L.gap_probs(cue, calib, s) for s, _ in test_sg]
    test_streams = [s for s, _ in test_sg]
    test_gold_gaps = [g for _, g in test_sg]
    fro_gaps = L.frozen_gaps(test_probs, rule)
    fro_words = [w for g, s in zip(fro_gaps, test_streams) for w in L.words_from_gaps(s, g)]
    gold_words = [w for d in test_docs for w in d]

    gapsets = [L.sample_gaps(test_probs, seed=(seed * 1000 + k)) for k in range(L.K_SAMPLES)]

    U = L.candidate_universe(gold_words, min_att=5)  # lower min_att: synthetic corpora are small
    if not U:
        U = list(GOLD)

    pv_gold = L.null_pvals(gold_words, U, 200, seed=seed + 10)
    pv_fro = L.null_pvals(fro_words, U, 200, seed=seed + 11)
    pv_marg = L.marg_null_pvals_stream(test_streams, gapsets, U, 200, seed=seed + 12)

    G = {t for t in U if pv_gold[t]["p"] <= 0.01} & GOLD  # only score against true planted set
    # Use the TRUE planted gold set restricted to U (fair even if gold-inventory rule misses one)
    G_true = GOLD & set(U)
    A_f = {t for t in U if pv_fro[t]["p"] <= 0.01}
    A_m = {t for t in U if pv_marg[t]["p"] <= 0.01}

    fro_rec = L.set_f1(A_f, G_true, U)
    marg_rec = L.set_f1(A_m, G_true, U)
    return {
        "n_stem": n_stem, "seed": seed, "n_docs": len(docs), "n_train": len(train_docs),
        "n_test": len(test_docs), "n_test_words": len(gold_words),
        "boundary_rule": rule,
        "boundary_test_f1": L.boundary_f1(fro_gaps, test_gold_gaps),
        "cut_rate_frozen": L.cut_rate(fro_gaps, test_streams),
        "gold_cut_rate": L.cut_rate(test_gold_gaps, test_streams),
        "universe_n": len(U), "gold_true_in_universe": sorted(L.tkey(t) for t in G_true),
        "frozen_recovery": fro_rec, "marg_recovery": marg_rec,
        "delta_f1": round(marg_rec["f1"] - fro_rec["f1"], 4),
        "frozen_inventory": sorted(L.tkey(t) for t in A_f),
        "marg_inventory": sorted(L.tkey(t) for t in A_m),
    }


def main():
    t0 = time.time()
    regimes = [150, 600, 2400]
    seeds = [L.SEED + i for i in range(5)]
    results = []
    for n_stem in regimes:
        for s in seeds:
            results.append(run_regime(n_stem, s))
            print(f"n_stem={n_stem} seed={s} done", file=sys.stderr)

    by_regime = {}
    for n_stem in regimes:
        rows = [r for r in results if r["n_stem"] == n_stem]
        mean_delta = sum(r["delta_f1"] for r in rows) / len(rows)
        mean_fro = sum(r["frozen_recovery"]["f1"] for r in rows) / len(rows)
        mean_marg = sum(r["marg_recovery"]["f1"] for r in rows) / len(rows)
        by_regime[str(n_stem)] = {
            "mean_frozen_f1": round(mean_fro, 4), "mean_marg_f1": round(mean_marg, 4),
            "mean_delta_f1": round(mean_delta, 4),
            "n_seeds_delta_positive": sum(1 for r in rows if r["delta_f1"] > 0),
            "n_seeds_delta_nonneg": sum(1 for r in rows if r["delta_f1"] >= 0),
            "mean_gold_cut_rate": round(sum(r["gold_cut_rate"] for r in rows) / len(rows), 4),
            "mean_frozen_cut_rate": round(sum(r["cut_rate_frozen"] for r in rows) / len(rows), 4),
        }
    most_hapax = str(max(int(k) for k in by_regime))
    graceful = by_regime[most_hapax]["mean_delta_f1"] >= 0
    out = {"regimes": regimes, "seeds": seeds, "per_run": results, "by_regime": by_regime,
           "most_hapax_regime": most_hapax, "graceful": graceful,
           "verdict": "GRACEFUL" if graceful else "NOT_GRACEFUL",
           "runtime_s": round(time.time() - t0, 1)}
    json.dump(out, open(os.path.join(L.DATA, "synthetic_control.json"), "w"), indent=1)
    print(json.dumps(by_regime, indent=1))
    print("verdict", out["verdict"], "runtime_s", out["runtime_s"])


if __name__ == "__main__":
    main()
