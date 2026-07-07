#!/usr/bin/env python3
"""Standalone: compute WP7's exploratory C/V-partition check (median-split) for the packed and
word LA strong-substitution subgraphs and patch the two `cv_partition_check` fields into the
already-saved wp7_word_substitution_channel.json. The primary WP7 numbers (graph stats, max
edge weight, packed-vs-word delta) are unchanged; only the exploratory check is filled in. This
runs WITHOUT the multi-minute opaque-LB threshold sweep, which the main WP7 already performed.
"""
from __future__ import annotations
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wp3_2_scribal_substitution as SUB  # noqa: E402
from word_units import load_a_words       # noqa: E402
MAIN = "/home/claude-runner/gitlab/n8n/logos"
sys.path.insert(0, MAIN)
from scripts.cross_script import data as X  # noqa: E402

DATA = os.path.join(HERE, "..", "data")
SEED = 20260708
THRESHOLDS = SUB.THRESHOLDS
N_CV_NULL = 150


def median_partition():
    j = json.load(open(os.path.join(DATA, "wp3_cv_recovery.json")))
    scored = [(s, float(p)) for s, p in j["LA_full_partition"]]
    vals = sorted(p for _, p in scored)
    med = vals[len(vals) // 2]
    return {s: (p >= med) for s, p in scored}, sum(1 for _, p in scored if p >= med), len(scored)


def strong_subgraph(seqs):
    ew, nf, _ = SUB.substitution_graph(seqs)
    maxw = max(ew.values())
    t = None
    for cand in sorted((c for c in THRESHOLDS if c <= maxw), reverse=True):
        if sum(1 for w in ew.values() if w >= cand) >= 30:
            t = cand
            break
    return {e: w for e, w in ew.items() if t and w >= t}, t


def cv_check(strong, part, seed_off):
    graded = {e: w for e, w in strong.items() if all(u in part for u in e)}
    gn = set(u for e in graded for u in e)
    classes = set(part[u] for u in gn)
    if len(graded) < 5 or len(classes) < 2:
        return {"skipped": "degenerate", "graded_edges": len(graded)}

    def rate(es):
        hit = tot = 0
        for e in es:
            u, v = tuple(e)
            tot += 1
            hit += (part[u] == part[v])
        return hit / tot if tot else 0.0

    obs = rate(set(graded))
    rng = random.Random(SEED + seed_off)
    el = list(graded)
    nulls = [rate(SUB.degree_preserving_rewire(el, rng, mult=3)) for _ in range(N_CV_NULL)]
    mu = sum(nulls) / len(nulls)
    sd = (sum((x - mu) ** 2 for x in nulls) / len(nulls)) ** 0.5
    p_hi = (sum(1 for x in nulls if x >= obs) + 1) / (len(nulls) + 1)
    p_lo = (sum(1 for x in nulls if x <= obs) + 1) / (len(nulls) + 1)
    return {"n_null": N_CV_NULL, "graded_edges": len(graded), "nodes": len(gn),
            "obs_same_CVclass_rate": round(obs, 4), "null_mean": round(mu, 4),
            "null_sd": round(sd, 4), "z": round((obs - mu) / sd, 2) if sd > 0 else None,
            "p_two_sided": round(min(1.0, 2 * min(p_hi, p_lo)), 4),
            "note": "exploratory median-split of WP3.1 vowel-likeness; NOT a gate, values never fed to graph"}


def run():
    part, nvl, ntot = median_partition()
    _, packed_seqs, _ = X.load_a()
    _, word_seqs, _ = load_a_words()
    p_strong, p_t = strong_subgraph(packed_seqs)
    w_strong, w_t = strong_subgraph(word_seqs)
    pk = cv_check(p_strong, part, 1)
    wd = cv_check(w_strong, part, 2)
    pk["threshold"] = p_t
    wd["threshold"] = w_t
    print("median vowel-like:", nvl, "of", ntot)
    print("packed cv:", json.dumps(pk))
    print("word   cv:", json.dumps(wd))

    outp = os.path.join(DATA, "wp7_word_substitution_channel.json")
    j = json.load(open(outp))
    j["LA_packed_baseline"]["cv_partition_check"] = pk
    j["LA_word_segmented"]["cv_partition_check"] = wd
    j["packed_vs_word_delta"]["cv_check_z"] = {"packed": pk.get("z"), "word": wd.get("z"),
                                               "same_CVclass_rate": {"packed": pk.get("obs_same_CVclass_rate"),
                                                                     "word": wd.get("obs_same_CVclass_rate")}}
    json.dump(j, open(outp, "w"), indent=1)
    print("PATCHED", os.path.abspath(outp))


if __name__ == "__main__":
    run()
