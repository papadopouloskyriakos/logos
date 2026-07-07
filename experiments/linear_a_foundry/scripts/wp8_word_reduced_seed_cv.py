#!/usr/bin/env python3
"""WP8 — REDUCED-SEED C/V bootstrap on GORILA WORD-segmented Linear A (packed-vs-word delta).

WP5(b) validated on opaque Linear B: semi-supervised label spreading with a few CORRECT
vowel seeds (+ consonant anchors) recovers held-out C/V (AUC>=0.75) far above the
fully-unsupervised null. The propagation runs on POSITION features (initial/final rate, mean
position, lone rate, neighbour entropy). On PACKED Linear A those "positions" are
INSCRIPTION-relative — a sign that is word-final but mid-inscription is mis-scored — so the
LA position channel is corrupted by packing. WP8 rebuilds the LA features from GORILA WORD
units (true word-initial/final/mean-position) and reports the packed-vs-word delta.

The opaque-LB benchmark is ALWAYS word-segmented (DĀMOS wordforms) and is the validation
gate; it is re-reported unchanged from WP5(b). The change is entirely on the LA side: packed
vs word position features feeding the SAME label-spread propagation.

LA seeding (per the task): A and I are the pure-vowel signs of the shared AB inventory — their
vowel identity is transcription-definitional, a TYPOLOGICAL anchor, not a graded LB value — so
we seed {A, I} as vowels + the lowest-frequency signs as consonant anchors, and measure how
far the label propagates (how many HELD-OUT, non-seed signs receive a confident vowel /
consonant assignment, and whether the vowel-like set agrees with the WP1 A/I/U candidates and
the WP3.1 ranking). NON-CIRCULAR: no Linear B value grades the LA side; A/I are seeds, not
scored. We also run the fully-operational FREQ-PRIOR seeding (no anchor at all) for contrast.

Deterministic (seed 20260708). Writes JSON to ../data/.
"""
from __future__ import annotations

import json
import math
import os
import sys
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wp5_reduced_seed_bootstrap as W5  # noqa: E402  (reuse validated features + spreading)
import wp3_2_scribal_substitution as SUB  # noqa: E402
from word_units import load_a_words       # noqa: E402
MAIN = "/home/claude-runner/gitlab/n8n/logos"
sys.path.insert(0, MAIN)
from scripts.cross_script import data as X  # noqa: E402

DATA = os.path.join(HERE, "..", "data")
SEED = 20260708
FREQ_MIN = W5.FREQ_MIN
POS_IDX = W5.POS_IDX
BETA_SUB = W5.BETA_SUB
WP1_VOWEL_CANDS = {"A", "I", "U"}          # WP1 top-initial LA vowel candidates (reporting only)
VOWEL_ANCHORS = ["A", "I"]                 # typological pure-vowel seeds (task-specified)


def build_la(seqs):
    F, tot = W5.features(seqs)
    signs = sorted((s for s in F if tot[s] >= FREQ_MIN), key=lambda s: -tot[s])
    Xm = np.array([[F[s][c] for c in POS_IDX] for s in signs], float)
    mu = Xm.mean(0); sd = Xm.std(0) + 1e-9
    Xs = (Xm - mu) / sd
    edge_weight, _, _ = SUB.substitution_graph(seqs)
    Wpos = W5.knn_rbf(Xs)
    Wsub = W5.sub_affinity(signs, edge_weight)
    return signs, tot, Xs, Wpos, Wsub


def propagate(signs, W, v_seed_names, c_seed_names):
    idx = {s: i for i, s in enumerate(signs)}
    v_seed = [idx[s] for s in v_seed_names if s in idx]
    c_seed = [idx[s] for s in c_seed_names if s in idx]
    n = len(signs)
    Y = np.zeros((n, 2))
    for i in v_seed:
        Y[i, 0] = 1.0
    for i in c_seed:
        Y[i, 1] = 1.0
    F = W5.label_spread(W, Y)
    vscore = F[:, 0] - F[:, 1]
    seedset = set(v_seed) | set(c_seed)
    ho = [i for i in range(n) if i not in seedset]
    ho_ranked = sorted(ho, key=lambda i: -vscore[i])
    vowel_like = [signs[i] for i in ho_ranked if vscore[i] > 0]
    return {
        "n_signs": n, "n_vowel_seeds_used": len(v_seed), "n_cons_seeds_used": len(c_seed),
        "n_heldout": len(ho),
        "n_heldout_vowel_like": len(vowel_like),
        "heldout_vowel_like_signs": vowel_like,
        "heldout_top8": [(signs[i], round(float(vscore[i]), 3)) for i in ho_ranked[:8]],
        "heldout_bottom5": [(signs[i], round(float(vscore[i]), 3)) for i in ho_ranked[-5:]],
        "wp1_vowel_cands_recovered": sorted(set(vowel_like) & WP1_VOWEL_CANDS),
        "vscore_spread": round(float(vscore.max() - vscore.min()), 4),
    }


def analyze_la(label, seqs):
    signs, tot, Xs, Wpos, Wsub = build_la(seqs)
    W = Wpos + BETA_SUB * Wsub
    n = len(signs)
    low = [signs[i] for i in range(n - 3, n)]      # 3 lowest-freq signs = consonant anchors
    out = {
        "unit": label, "n_units": len(seqs),
        "mean_signs_per_unit": round(sum(len(s) for s in seqs) / len(seqs), 3),
        "n_signs_freq>=%d" % FREQ_MIN: n,
        "vowel_anchors_present": [s for s in VOWEL_ANCHORS if s in signs],
        "cons_anchors_lowfreq": low,
    }
    # (i) typological A/I-anchor seeding (position+substitution affinity)
    out["AI_anchor_seeding"] = propagate(signs, W, VOWEL_ANCHORS, low)
    # (ii) fully-operational FREQ-PRIOR seeding (k=3 most/least frequent), pos+sub and pos-only
    out["freq_prior_k3_pos+sub"] = propagate(signs, W, signs[:3], signs[-3:])
    out["freq_prior_k3_pos_only"] = propagate(signs, Wpos, signs[:3], signs[-3:])
    return out


def run():
    # --- opaque-LB validation gate (word units; unchanged WP5(b) machinery) ---
    signs, tot, Xs, truth, Wpos, Wsub = W5.build_lb()
    lb = W5.run_lb(signs, tot, Xs, truth, Wpos, Wsub)
    msr = lb["minimal_seed_requirement"]

    _, packed_seqs, _ = X.load_a()
    _, word_seqs, _ = load_a_words()
    packed = analyze_la("packed_inscription", packed_seqs)
    word = analyze_la("gorila_word", word_seqs)

    def cov(a, key):
        return a[key]["n_heldout_vowel_like"]

    delta = {
        "n_signs_freq>=20": {"packed": packed["n_signs_freq>=20"], "word": word["n_signs_freq>=20"]},
        "AI_anchor_heldout_vowel_like": {
            "packed": cov(packed, "AI_anchor_seeding"), "word": cov(word, "AI_anchor_seeding"),
            "delta": cov(word, "AI_anchor_seeding") - cov(packed, "AI_anchor_seeding")},
        "AI_anchor_wp1_recovered": {
            "packed": packed["AI_anchor_seeding"]["wp1_vowel_cands_recovered"],
            "word": word["AI_anchor_seeding"]["wp1_vowel_cands_recovered"]},
        "freq_prior_pos+sub_heldout_vowel_like": {
            "packed": cov(packed, "freq_prior_k3_pos+sub"), "word": cov(word, "freq_prior_k3_pos+sub")},
        "vscore_spread_AI": {
            "packed": packed["AI_anchor_seeding"]["vscore_spread"],
            "word": word["AI_anchor_seeding"]["vscore_spread"]},
    }

    # Gate = opaque-LB benchmark (does reduced-seed propagation beat the unsupervised null?).
    beats_null = bool(msr["clean_seed_min_vowels_for_auc>=0.75"] is not None)
    # LA-side movement: does word segmentation let the bootstrap propagate to MORE held-out signs
    # from the A/I anchors than packed did?
    d_cov = delta["AI_anchor_heldout_vowel_like"]["delta"]
    if not beats_null:
        verdict = "NULL"
    elif d_cov > 0:
        verdict = "IMPROVED"          # word position features let A/I propagate to more held-out signs
    elif d_cov == 0:
        verdict = "BEATS_NULL"        # LB gate holds; word units neither help nor hurt LA propagation
    else:
        verdict = "AT_END_TO_END_NULL"  # word units REDUCED LA propagation coverage

    out = {
        "experiment": "WP8_word_segmented_reduced_seed_CV",
        "seed": SEED, "alpha": W5.ALPHA, "knn": W5.KNN, "beta_sub": BETA_SUB, "freq_min": FREQ_MIN,
        "non_circular": ("position features + sign-identity substitution edges on the LA side; A/I are "
                         "typological pure-vowel seeds (transcription-definitional), NOT graded LB values; "
                         "LB values grade only the opaque-LB benchmark"),
        "LB_benchmark_word_units": {
            "unsupervised_null": lb["unsupervised_null"],
            "freq_only_ranking_auc": lb["freq_only_ranking_auc"],
            "supervised_ceiling_auc": lb["supervised_ceiling_auc_WP3.1"],
            "minimal_seed_requirement": msr,
            "regime_B_pos": [r for r in lb["regime_B_clean_oracle_seeds"] if r["channel"] == "pos"],
        },
        "LA_packed_baseline": packed,
        "LA_word_segmented": word,
        "packed_vs_word_delta": delta,
        "verdict": verdict,
        "headline": (
            "Opaque-LB gate holds (reduced-seed propagation recovers held-out C/V with min %s clean vowel "
            "seed(s)). On LA, seeding {A,I} as typological vowels propagates to %d held-out vowel-like signs "
            "packed -> %d word (delta %+d). Word position features are word-relative (true initial/final), "
            "so the C/V bootstrap %s under word segmentation."
            % (msr["clean_seed_min_vowels_for_auc>=0.75"],
               cov(packed, "AI_anchor_seeding"), cov(word, "AI_anchor_seeding"), d_cov,
               "propagates further" if d_cov > 0 else ("is unchanged" if d_cov == 0 else "propagates LESS"))),
    }
    os.makedirs(DATA, exist_ok=True)
    outp = os.path.join(DATA, "wp8_word_reduced_seed_cv.json")
    json.dump(out, open(outp, "w"), indent=1)
    print(json.dumps({"verdict": verdict, "packed_vs_word_delta": delta,
                      "LB_minimal_seed": msr,
                      "word_AI_seeding": word["AI_anchor_seeding"],
                      "packed_AI_seeding": packed["AI_anchor_seeding"]}, indent=1))
    print("\nWROTE", os.path.abspath(outp))
    return out


if __name__ == "__main__":
    run()
