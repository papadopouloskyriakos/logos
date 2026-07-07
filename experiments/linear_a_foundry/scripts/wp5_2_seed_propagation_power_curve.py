#!/usr/bin/env python3
"""WP5.2 - SEED-PROPAGATION POWER CURVE (the decisive quantification of the LA obstacle).

BACKGROUND (established, this repo):
  * WP1 refuted the value-blind theorem.
  * WP3.2 scribal-substitution channel validated on LB (z=7.07); LA ~1.7x below the clean
    regime (WP3.2b).
  * WP5(b) reduced-seed C/V bootstrap: on OPAQUE Linear B, seeding 3-4 CORRECT vowels + a
    few consonant anchors and running semi-supervised label spreading over position+
    substitution affinity recovers held-out C/V at AUC>=0.75 (vs unsupervised NULL ~0.5).
    Applied to Linear A the same propagation is ~chance -> UNDERPOWERED / NULL.

THE OBSTACLE is LA-side PROPAGATION POWER (not the seeds, not the channel). This script
quantifies it precisely: how much CORPUS does the reduced-seed C/V bootstrap need before it
fires, and therefore what MULTIPLE of its current corpus Linear A would need.

METHOD (non-circular: LB phonetic values are used ONLY to GRADE, never as a model input):
  * Subsample Linear B (DAMOS, 13,562 wordforms) to a size ladder in #wordforms.
  * At each size, over N_SUB independent random subsamples:
      - rebuild the WP5 pipeline from scratch on the subsample: position features (WP3.1),
        substitution graph (WP3.2), affinity W = kNN-RBF(position) + beta*log1p(sub),
        signs with subsample-frequency >= FREQ_MIN (same floor WP3/WP5/LA all use);
      - run the reduced-seed CLEAN-seed bootstrap: kv genuine vowel seeds + kc consonant
        anchors, label-spread (Zhou 2004 closed form), score held-out (non-seed) signs,
        AUC vs the revealed {A,E,I,O,U}; average over all C(n_vowels,kv) vowel-seed combos
        (a few random consonant-anchor draws each).
  * Curve point = mean held-out AUC (+/- subsample-bootstrap CI) vs corpus size.
  * Find the corpus size at which mean held-out AUC first crosses 0.70 (log-linear interp).
  * Place Linear A on the curve: LA has N_LA wordforms and its post-seeding held-out AUC is
    ~chance (WP5); the corpus MULTIPLE LA needs = size@0.70 / N_LA. We also directly report
    what the LB curve itself does at LA's corpus size (539 wf) as an apples-to-apples anchor.

Deterministic (seed 20260708). Corpus read-only from main.
"""
from __future__ import annotations
import json
import math
import os
import sys
from collections import Counter
from itertools import combinations

import numpy as np

MAIN = "/home/claude-runner/gitlab/n8n/logos"
sys.path.insert(0, MAIN)
from scripts.cross_script import data as X  # noqa: E402
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wp3_2_scribal_substitution as SUB  # noqa: E402
import wp5_reduced_seed_bootstrap as W5  # reuse validated pieces  # noqa: E402

DATA = os.path.join(HERE, "..", "data")
SEED = 20260708
FREQ_MIN = W5.FREQ_MIN          # 20 -- same floor WP3/WP5/LA all use
LB_VOWELS = W5.LB_VOWELS
POS_IDX = W5.POS_IDX
BETA_SUB = W5.BETA_SUB
KNN = W5.KNN
BAR = 0.70                       # "useful" held-out C/V AUC bar

SIZE_LADDER = [300, 539, 750, 1000, 1500, 2000, 3500, 6000, 10000, 13562]
LA_SIZE_MARK = 539               # sizes at/near LA's wordform count get extra subsamples
N_SUB = 24                       # independent subsample draws per size (1 at full corpus)
KV_LIST = [3, 4]                 # "3-4 correct vowel seeds"
KC = 3                           # "a few consonant anchors"
N_CONS_DRAWS = 4                 # random consonant-anchor draws averaged per vowel combo


def build_pipeline(seqs):
    """From a list of wordform sign-sequences -> (signs, truth, Wpos, Wsub) or None if too small."""
    F, tot = W5.features(seqs)
    signs = sorted((s for s in F if tot[s] >= FREQ_MIN), key=lambda s: -tot[s])
    if len(signs) < 6:
        return None
    truth = [1 if s in LB_VOWELS else 0 for s in signs]
    if sum(truth) < 2:
        return None
    Xm = np.array([[F[s][c] for c in POS_IDX] for s in signs], float)
    mu = Xm.mean(0); sd = Xm.std(0) + 1e-9
    Xs = (Xm - mu) / sd
    edge_weight, _, _ = SUB.substitution_graph(seqs)
    Wpos = W5.knn_rbf(Xs)
    Wsub = W5.sub_affinity(signs, edge_weight)
    W = Wpos + BETA_SUB * Wsub
    return signs, truth, W


def reduced_seed_auc(signs, truth, W, kv, kc, rng):
    """Mean held-out AUC over all vowel-seed combos (a few consonant-anchor draws each)."""
    n = len(signs)
    v_idx = [i for i in range(n) if truth[i]]
    c_idx = [i for i in range(n) if not truth[i]]
    if len(v_idx) <= kv or len(c_idx) < kc:
        return None  # need >=1 held-out vowel and enough consonants
    combos = list(combinations(v_idx, kv))
    aucs = []
    for vc in combos:
        for _ in range(N_CONS_DRAWS):
            cc = list(rng.choice(c_idx, kc, replace=False))
            res = W5.spread_and_eval(W, signs, truth, list(vc), cc)
            if res["auc"] is not None:
                aucs.append(res["auc"])
    if not aucs:
        return None
    return float(np.mean(aucs))


def curve_point(seqs_full, size, rng, n_sub):
    """Mean held-out AUC (per-subsample means) at a given corpus size, for each kv."""
    N = len(seqs_full)
    out = {"size": size, "n_sub_requested": n_sub}
    per_kv = {kv: [] for kv in KV_LIST}
    n_signs_list = []
    n_vow_list = []
    draws = 1 if size >= N else n_sub
    for d in range(draws):
        if size >= N:
            sub = seqs_full
        else:
            idx = rng.choice(N, size, replace=False)
            sub = [seqs_full[i] for i in idx]
        pipe = build_pipeline(sub)
        if pipe is None:
            continue
        signs, truth, W = pipe
        n_signs_list.append(len(signs))
        n_vow_list.append(int(sum(truth)))
        for kv in KV_LIST:
            a = reduced_seed_auc(signs, truth, W, kv, KC, rng)
            if a is not None:
                per_kv[kv].append(a)
    out["n_effective_draws"] = len(n_signs_list)
    out["mean_n_signs"] = round(float(np.mean(n_signs_list)), 1) if n_signs_list else None
    out["mean_n_vowels"] = round(float(np.mean(n_vow_list)), 2) if n_vow_list else None
    # a point is trustworthy for kv only if it typically leaves >=2 held-out vowels
    # (all 5 revealed vowels present, so kv=3 -> ~2 held-out positives). Fewer positives
    # make held-out AUC high-variance and upward-biased (degenerate).
    out["valid_all5_vowels"] = bool(n_vow_list and np.mean(n_vow_list) >= 4.99)
    out["kv"] = {}
    for kv in KV_LIST:
        vals = per_kv[kv]
        if vals:
            arr = np.array(vals)
            # bootstrap 95% CI of the mean across subsamples
            bs = np.array([np.mean(rng.choice(arr, len(arr), replace=True)) for _ in range(2000)])
            out["kv"][str(kv)] = {
                "mean_auc": round(float(arr.mean()), 4),
                "sd_auc": round(float(arr.std()), 4),
                "ci95_lo": round(float(np.percentile(bs, 2.5)), 4),
                "ci95_hi": round(float(np.percentile(bs, 97.5)), 4),
                "n": len(vals),
            }
        else:
            out["kv"][str(kv)] = None
    return out


def crossing(points, kv, bar=BAR, valid_only=True):
    """First size where mean AUC crosses `bar`; log-linear interpolate the exact size.

    valid_only restricts to points with all 5 vowels present (>=2 held-out positives),
    excluding degenerate small-corpus points whose AUC is inflated by a tiny positive set.
    """
    xs = []
    for p in points:
        if valid_only and not p.get("valid_all5_vowels", True):
            continue
        e = p["kv"].get(str(kv))
        if e is not None:
            xs.append((p["size"], e["mean_auc"]))
    xs.sort()
    for i in range(1, len(xs)):
        (x0, y0), (x1, y1) = xs[i - 1], xs[i]
        if y0 < bar <= y1:
            # interpolate in log-size
            lx0, lx1 = math.log(x0), math.log(x1)
            frac = (bar - y0) / (y1 - y0)
            lx = lx0 + frac * (lx1 - lx0)
            return {"below": (x0, y0), "above": (x1, y1),
                    "size_at_bar": int(round(math.exp(lx)))}
    # already above at smallest, or never reaches
    if xs and xs[0][1] >= bar:
        return {"note": "at/above bar at smallest measured size", "smallest": xs[0]}
    if xs and xs[-1][1] < bar:
        return {"note": "does not reach bar within ladder (max = full corpus)", "max": xs[-1]}
    return {"note": "insufficient points"}


def run():
    seqs_lb, _, _ = X.load_b_damos()
    N_full = len(seqs_lb)
    rng = np.random.default_rng(SEED)

    # ---- LA reference facts (its corpus size + qualifying-sign count under the same pipeline) ----
    inv, seqs_la, freq = X.load_a()
    la_pipe = build_pipeline(seqs_la)
    la_n_signs = len(la_pipe[0]) if la_pipe else None
    la_n_vow = int(sum(la_pipe[1])) if la_pipe else None
    N_LA = len(seqs_la)

    # ---- build the curve ----
    points = []
    for size in SIZE_LADDER:
        n_sub = N_SUB if size != LA_SIZE_MARK else N_SUB  # keep uniform
        p = curve_point(seqs_lb, size, rng, n_sub)
        points.append(p)
        km = p["kv"].get("3")
        print(f"size={size:6d}  n_signs~{p['mean_n_signs']}  kv3_AUC="
              f"{km['mean_auc'] if km else None}  (CI {km['ci95_lo'] if km else '-'}"
              f"-{km['ci95_hi'] if km else '-'})")

    cross = {str(kv): crossing(points, kv) for kv in KV_LIST}

    # ---- LA placement + corpus multiple ----
    def lb_auc_at(size, kv):
        for p in points:
            if p["size"] == size and p["kv"].get(str(kv)):
                return p["kv"][str(kv)]["mean_auc"]
        return None

    la_placement = {}
    for kv in KV_LIST:
        c = cross[str(kv)]
        s_bar = c.get("size_at_bar")
        la_placement[str(kv)] = {
            "LA_wordforms": N_LA,
            "LA_qualifying_signs_freq>=%d" % FREQ_MIN: la_n_signs,
            "LA_heldout_AUC_after_seeding": "~0.50 (chance; WP5(b): LA propagation NULL, no gold to grade)",
            "LB_curve_AUC_at_LA_wordcount(539)": lb_auc_at(LA_SIZE_MARK, kv),
            "size_at_AUC>=0.70": s_bar,
            "LA_corpus_multiple_needed": (round(s_bar / N_LA, 1) if s_bar else None),
            "interpretation_of_multiple": (
                "LA would need ~%sx its current wordform count for the reduced-seed C/V "
                "bootstrap to reach held-out AUC 0.70, IF LA behaved like subsampled Linear B."
                % (round(s_bar / N_LA, 1) if s_bar else "N/A")),
        }

    out = {
        "experiment": "WP5.2_seed_propagation_power_curve",
        "seed": SEED, "bar_auc": BAR, "freq_min": FREQ_MIN, "beta_sub": BETA_SUB,
        "knn": KNN, "kv_list": KV_LIST, "kc": KC, "n_cons_draws": N_CONS_DRAWS,
        "n_sub_per_size": N_SUB, "size_ladder": SIZE_LADDER,
        "non_circular": ("position + substitution-graph features only; LB {A,E,I,O,U} used "
                         "solely to GRADE held-out AUC, never as a model input"),
        "LB_full_wordforms": N_full,
        "LA_wordforms": N_LA, "LA_qualifying_signs": la_n_signs, "LA_qualifying_vowels": la_n_vow,
        "curve": points,
        "crossing_0.70": cross,
        "LA_placement": la_placement,
        "headline": None,
    }
    # conservative bracket for kv=3: the two ladder sizes straddling the bar
    kv3c = cross["3"]
    bracket = None
    if "below" in kv3c and "above" in kv3c:
        lo_wf, hi_wf = kv3c["below"][0], kv3c["above"][0]
        bracket = {"wordform_bracket": [lo_wf, hi_wf],
                   "LA_multiple_bracket": [round(lo_wf / N_LA, 1), round(hi_wf / N_LA, 1)]}
    out["primary_estimate_kv3"] = {
        "size_at_AUC>=0.70": kv3c.get("size_at_bar"),
        "LA_corpus_multiple": (round(kv3c["size_at_bar"] / N_LA, 1) if kv3c.get("size_at_bar") else None),
        "conservative_bracket": bracket,
        "why_kv3_primary": ("kv=3 leaves ~2 held-out vowels -> stable AUC; kv=4 leaves ~1 "
                            "held-out vowel and size=300 has <5 qualifying vowels -> both "
                            "degenerate/upward-biased and excluded from the crossing."),
    }
    out["caveats"] = [
        "AUC graded on only 5 true vowels; kv=3 -> 2 held-out positives. Averaged over all "
        "C(5,3)=10 vowel-seed combos x %d consonant-anchor draws x %d subsamples to stabilise." % (N_CONS_DRAWS, N_SUB),
        "size=300 (mean ~3.9 vowels qualify) and the kv=4 column (~1 held-out vowel) are "
        "DEGENERATE (tiny positive set inflates AUC); excluded from the crossing. Valid "
        "curve region = size>=539 where all 5 vowels clear FREQ_MIN.",
        "Multiple assumes LA behaves like size-matched Linear B per wordform. LA wordforms "
        "are longer (more sign-tokens each: LA ~46 signs clear freq>=20 at 539 wf vs LB ~36), "
        "so in TOKENS LA is less corpus-starved than in wordforms; yet LA post-seeding AUC is "
        "still ~chance (WP5), i.e. LA underperforms even its wordform-matched LB point (0.647) "
        "-> the multiple is a LOWER bound on the corpus LA needs.",
    ]

    kv3 = cross["3"]; sb = kv3.get("size_at_bar")
    out["headline"] = (
        "Reduced-seed (3 vowel + 3 consonant) C/V bootstrap on subsampled Linear B crosses "
        "held-out AUC 0.70 at ~%s wordforms; at Linear A's 539 wordforms the same LB pipeline "
        "sits at AUC~%s (near chance), and Linear A itself is ~chance. => LA needs roughly %sx "
        "its current corpus for the C/V bootstrap to fire (kv=3 estimate)."
        % (sb, lb_auc_at(LA_SIZE_MARK, 3),
           (round(sb / N_LA, 1) if sb else "N/A")))

    os.makedirs(DATA, exist_ok=True)
    outp = os.path.join(DATA, "wp5_2_seed_propagation_power_curve.json")
    json.dump(out, open(outp, "w"), indent=1)
    print("\n=== CROSSING 0.70 ===")
    print(json.dumps(cross, indent=1))
    print("\n=== LA PLACEMENT ===")
    print(json.dumps(la_placement, indent=1))
    print("\n" + out["headline"])
    print("\nWROTE", os.path.abspath(outp))
    return out


if __name__ == "__main__":
    run()
