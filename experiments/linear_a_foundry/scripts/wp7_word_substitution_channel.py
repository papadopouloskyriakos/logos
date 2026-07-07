#!/usr/bin/env python3
"""WP7 — SUBSTITUTION channel on GORILA WORD-segmented Linear A (packed-vs-word delta).

The WP3.2 substitution channel was validated on opaque Linear B (strong minimal-pair edges
connect same-C / same-V signs above a degree-preserving null) but underpowered on Linear A:
the LA max substitution context-weight reached only ~105 packed, short of the high-weight
regime (~120) where the LB benchmark's enrichment is decisive. Packed LA sequences glue
unrelated GORILA words together, manufacturing minimal pairs that cross real word boundaries
(WP2: packing costs the segmentation channel AUC 0.685 vs 0.760). WP7 re-runs the SAME
substitution machinery on WORD-segmented LA and reports the packed-vs-word delta.

Two competing forces (report BOTH):
  (+) word boundaries remove cross-word spurious substitutions -> cleaner, and more real
      minimal pairs share a slot -> higher context-weight for genuine paradigmatic pairs.
  (-) GORILA words are SHORT (mean 1.84 signs) -> far fewer n>=2 contexts per pair, which can
      LOWER the max weight and shrink the strong subgraph (the substitution channel is
      context-hungry, and word units starve it of multi-sign context).

NON-CIRCULAR. Graph built from LA sign-identity contexts only; NO Linear B / known value is a
model input on the LA side. The opaque-LB benchmark (already word-segmented via load_b_damos)
is the validation gate and is re-reported unchanged. The exploratory LA C/V-partition check
reuses the WP3.1 partition (itself LB-validated) but never feeds a value into the graph.

Deterministic (seed 20260708). Writes JSON to ../data/.
"""
from __future__ import annotations

import json
import os
import random
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wp3_2_scribal_substitution as SUB  # noqa: E402  (reuse validated graph builder + null)
from word_units import load_a_words       # noqa: E402
MAIN = "/home/claude-runner/gitlab/n8n/logos"
sys.path.insert(0, MAIN)
from scripts.cross_script import data as X  # noqa: E402

DATA = os.path.join(HERE, "..", "data")
SEED = 20260708
THRESHOLDS = SUB.THRESHOLDS
N_NULL = SUB.N_NULL


def _load_cv_partition():
    """WP3.1 LA vowel-likeness ranking -> boolean vowel-like via MEDIAN split.

    The WP3.1 `LA_full_partition` scores are a relative vowel-likeness ranking (max 0.047, not
    calibrated to 0.5), so a >=0.5 cut leaves every sign consonant-like (degenerate). We split
    at the median so both classes are populated and the check is a real 2-class test: do LA
    strong-substitution edges connect signs of the SAME vowel-likeness half above a
    degree-preserving null? NOT a value input to the graph — exploratory only.
    """
    cvp = os.path.join(DATA, "wp3_cv_recovery.json")
    if not os.path.exists(cvp):
        return None
    j = json.load(open(cvp))
    scored = [(s, float(p)) for s, p in j.get("LA_full_partition", [])]
    if not scored:
        return None
    vals = sorted(p for _, p in scored)
    med = vals[len(vals) // 2]
    return {s: (p >= med) for s, p in scored}


def cv_partition_check(strong, part, seed_off):
    """Do LA strong-substitution edges respect the WP3.1 C/V boundary vs a degree-preserving null?"""
    if not part:
        return {"skipped": "no WP3.1 partition on disk"}
    graded = {e: w for e, w in strong.items() if all(u in part for u in e)}
    gn = set(u for e in graded for u in e)
    classes = set(part[u] for u in gn)
    if len(graded) < 5 or len(classes) < 2:
        return {"skipped": "degenerate/too few graded edges", "graded_edges": len(graded)}

    def same_class_rate(edge_set):
        hit = tot = 0
        for e in edge_set:
            u, v = tuple(e)
            tot += 1
            hit += (part[u] == part[v])
        return hit / tot if tot else 0.0

    obs = same_class_rate(set(graded))
    rng = random.Random(SEED + seed_off)
    el = list(graded)
    # exploratory-only: the LA strong subgraph is near-complete (density ~0.7), so Maslov-Sneppen
    # swaps are mostly rejected; use a light multiplier + 150 nulls (ample for a z on an
    # exploratory, non-gate check) to keep it from burning the full attempt budget.
    n_cv_null = 150
    nulls = [same_class_rate(SUB.degree_preserving_rewire(el, rng, mult=3)) for _ in range(n_cv_null)]
    mu = sum(nulls) / len(nulls)
    sd = (sum((x - mu) ** 2 for x in nulls) / len(nulls)) ** 0.5
    p_hi = (sum(1 for x in nulls if x >= obs) + 1) / (len(nulls) + 1)
    p_lo = (sum(1 for x in nulls if x <= obs) + 1) / (len(nulls) + 1)
    return {"graded_edges": len(graded), "nodes": len(gn),
            "obs_same_CVclass_rate": round(obs, 4), "null_mean": round(mu, 4),
            "null_sd": round(sd, 4), "z": round((obs - mu) / sd, 2) if sd > 0 else None,
            "p_two_sided": round(min(1.0, 2 * min(p_hi, p_lo)), 4)}


def analyze_la(seqs, part, label, seed_off):
    edge_weight, node_freq, n_ngrams = SUB.substitution_graph(seqs)
    stats = SUB.graph_stats(edge_weight, set(node_freq))
    max_w = max(edge_weight.values()) if edge_weight else 0
    weights = sorted(edge_weight.values(), reverse=True)
    # weight-distribution tail (how far into the high-weight regime the corpus reaches)
    tail = {f">={t}": sum(1 for w in weights if w >= t) for t in THRESHOLDS}
    # strong subgraph at the largest reachable threshold keeping >=30 edges
    t = None
    for cand in sorted((c for c in THRESHOLDS if c <= max_w), reverse=True):
        if sum(1 for w in edge_weight.values() if w >= cand) >= 30:
            t = cand
            break
    strong = {e: w for e, w in edge_weight.items() if t and w >= t}
    strong_nodes = set(u for e in strong for u in e)
    strong_stats = SUB.graph_stats(strong, strong_nodes) if strong else None
    return {
        "unit": label,
        "n_units": len(seqs),
        "mean_signs_per_unit": round(sum(len(s) for s in seqs) / len(seqs), 3),
        "n_ngrams": n_ngrams,
        "full_graph": stats,
        "max_edge_weight": max_w,
        "top3_weights": weights[:3],
        "weight_tail_counts": tail,
        "strong_threshold": t,
        "strong_subgraph": strong_stats,
        "top_substitution_edges": SUB.top_edges(edge_weight, 20),
        "cv_partition_check": cv_partition_check(strong, part, seed_off),
    }


def run():
    # --- opaque-LB validation gate (word-segmented; unchanged machinery) ---
    lb, lb_edges, lb_nodes = SUB.benchmark_lb()
    op = lb.get("operating_point")

    part = _load_cv_partition()
    _, packed_seqs, _ = X.load_a()
    _, word_seqs, _ = load_a_words()

    packed = analyze_la(packed_seqs, part, "packed_inscription", 1)
    word = analyze_la(word_seqs, part, "gorila_word", 2)

    d_max = word["max_edge_weight"] - packed["max_edge_weight"]
    ps, ws = packed["strong_subgraph"] or {}, word["strong_subgraph"] or {}
    delta = {
        "max_edge_weight": {"packed": packed["max_edge_weight"], "word": word["max_edge_weight"],
                            "delta": d_max},
        "clean_regime_target": 120,
        "reaches_clean_regime": {"packed": packed["max_edge_weight"] >= 120,
                                 "word": word["max_edge_weight"] >= 120},
        "strong_edges": {"packed": ps.get("edges", 0), "word": ws.get("edges", 0)},
        "strong_largest_component": {"packed": ps.get("largest_component", 0),
                                     "word": ws.get("largest_component", 0)},
        "cv_check_z": {"packed": packed["cv_partition_check"].get("z"),
                       "word": word["cv_partition_check"].get("z")},
    }

    lb_pass = lb["benchmark_passed"]
    # Did word segmentation move the LA substitution channel toward the validated clean regime?
    moved_up = d_max > 0
    if not lb_pass:
        verdict = "NULL"
    elif word["max_edge_weight"] >= 120:
        verdict = "SIGNAL_VALIDATED"      # word units reach the LB-decisive high-weight regime
    elif moved_up:
        verdict = "IMPROVED"              # moved toward it but still short -> still underpowered
    else:
        verdict = "AT_END_TO_END_NULL"    # word units did NOT help the substitution channel

    out = {
        "experiment": "WP7_word_segmented_substitution_channel",
        "seed": SEED, "n_null": N_NULL, "ngrams": list(SUB.NGRAMS),
        "non_circular": "LA sign-identity contexts only; LB values grade the LB benchmark only",
        "LB_benchmark_word_units": {
            "passed": lb_pass, "operating_point": op,
            "pair_auc_rawweight": lb["pair_auc_rawweight_predicts_feature"],
            "graded_edges_scored": lb["graded_edges_scored"],
            "lb_max_edge_weight": max(lb_edges.values()) if lb_edges else 0,
        },
        "LA_packed_baseline": packed,
        "LA_word_segmented": word,
        "packed_vs_word_delta": delta,
        "verdict": verdict,
        "headline": (
            "Word-segmentation moved LA substitution max context-weight %d -> %d (delta %+d; clean regime "
            "~120). Strong-subgraph edges %d -> %d. GORILA words are short (mean 1.84), which starves the "
            "substitution channel of multi-sign contexts; the %s direction dominates."
            % (packed["max_edge_weight"], word["max_edge_weight"], d_max,
               ps.get("edges", 0), ws.get("edges", 0),
               "context-starvation (-)" if d_max <= 0 else "boundary-cleaning (+)")),
    }
    os.makedirs(DATA, exist_ok=True)
    outp = os.path.join(DATA, "wp7_word_substitution_channel.json")
    json.dump(out, open(outp, "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items()
                      if k not in ("LA_packed_baseline", "LA_word_segmented")}, indent=1))
    print("\npacked strong:", ps)
    print("word   strong:", ws)
    print("WROTE", os.path.abspath(outp))
    return out


if __name__ == "__main__":
    run()
