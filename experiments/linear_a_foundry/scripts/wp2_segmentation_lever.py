#!/usr/bin/env python3
"""WP2 — the segmentation lever (Constitution v2.2 Art. VIII/XII).

The synthetic lab found a severe SEGMENTATION TAX: LA-scale word-SEGMENTED reaches position AUC ~0.71 while
LA-PACKED never clears 0.75. And load_a() returns 539 PACKED inscriptions (mean 7.88 signs) — so every prior
LA position/C/V analysis used inscription-internal positions, not word positions — while the corpus ships
3,147 GORILA WORD units (mean 1.84). This tests whether using the AVAILABLE GORILA word segmentation (no new
excavation) improves the LA value signal.

Test: the 5 Linear A pure-vowel signs are A,I,U,E,O (AB08/28/10/38/61). Train the WP3.1 C/V classifier on LB
WORD units; apply to LA under PACKED vs WORD units; compare where the 5 LA vowels rank (non-circular check:
their values come from the AB correspondence but are NOT model inputs — the features are word-position stats).
LB CV AUC validates the word-unit pipeline. Deterministic; read-only corpus.
"""
import json
import math
import os
import sys
from collections import Counter

import numpy as np

MAIN = "/home/claude-runner/gitlab/n8n/logos"
sys.path.insert(0, MAIN)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scripts.cross_script import data as X  # noqa: E402
import wp3_cv_recovery as W  # noqa: E402
HERE = os.path.dirname(os.path.abspath(__file__))
LA_VOWELS = {"A", "I", "U", "E", "O"}       # AB pure-vowel signs (transliteration)


def gorila_words():
    recs = json.load(open(os.path.join(MAIN, "corpus/silver/inscriptions_structured.json")))
    return [t["signs"] for r in recs for t in (r.get("stream") or []) if t.get("t") == "word"]


def train_lb_word_classifier():
    lb_word = W.X.load_b_damos()[0]      # DAMOS is already word-segmented
    F = W.features(lb_word)
    signs = sorted(s for s in F if math.exp(F[s][6]) >= 20)
    Xm = np.array([F[s] for s in signs]); y = np.array([1.0 if s in W.LB_VOWELS else 0.0 for s in signs])
    Xs, mu, sd = W.standardize(Xm)
    # CV AUC (validation)
    import random
    rng = random.Random(W.SEED); order = list(range(len(signs))); rng.shuffle(order); k = 7
    oof = np.zeros(len(signs))
    for f in range(k):
        te = [order[i] for i in range(len(order)) if i % k == f]; tr = [i for i in range(len(order)) if i not in te]
        w, b = W.logreg(Xs[tr], y[tr]); oof[te] = Xs[te] @ w + b
    cv_auc = W.auc(list(oof), list(y))
    w, b = W.logreg(Xs, y)
    return (w, b, mu, sd), cv_auc


def la_vowel_ranks(units, model):
    w, b, mu, sd = model
    F = W.features(units)
    signs = sorted(s for s in F if math.exp(F[s][6]) >= 20)
    Xm = (np.array([F[s] for s in signs]) - mu) / sd
    score = Xm @ w + b
    ranked = sorted(zip(signs, score), key=lambda t: -t[1])
    rank = {s: i + 1 for i, (s, _) in enumerate(ranked)}
    vr = {v: rank[v] for v in LA_VOWELS if v in rank}
    n = len(ranked)
    # AUC of the classifier ranking the 5 LA vowels above other signs (non-circular check)
    labels = [s in LA_VOWELS for s, _ in ranked]
    sc = [x for _, x in ranked]
    auc = W.auc(sc, labels)
    return {"n_signs": n, "la_vowel_ranks": vr, "mean_vowel_rank": round(sum(vr.values()) / max(len(vr), 1), 1),
            "vowel_vs_rest_AUC": auc}


def run():
    model, cv_auc = train_lb_word_classifier()
    packed = X.load_a()[1]               # 539 inscriptions (the regime prior analyses used)
    words = gorila_words()               # 3147 GORILA word units
    r_packed = la_vowel_ranks(packed, model)
    r_words = la_vowel_ranks(words, model)
    improved = bool((r_words["vowel_vs_rest_AUC"] or 0) > (r_packed["vowel_vs_rest_AUC"] or 0))
    out = {
        "LB_word_classifier_cv_auc": cv_auc,
        "LA_units": {"packed_inscriptions": len(packed), "gorila_words": len(words)},
        "PACKED_inscriptions": r_packed,
        "WORD_segmented_gorila": r_words,
        "segmentation_helps_vowel_recovery": improved,
        "verdict": "SEGMENTATION_LEVER_HELPS" if improved and (r_words["vowel_vs_rest_AUC"] or 0) >= 0.6 else ("SEGMENTATION_WEAK" if improved else "NO_SEGMENTATION_GAIN"),
        "interpretation": ("Comparing the LA pure-vowel signs' recovery under PACKED inscriptions (the regime "
                           "all prior LA analyses used) vs the AVAILABLE GORILA WORD segmentation. If word units "
                           "rank the 5 vowels (A,I,U,E,O) higher, the segmentation half of the obstacle is "
                           "partially addressable NOW, on existing data, without new excavation. Non-circular: "
                           "vowel identities are the check, not model inputs (features are word-position stats)."),
    }
    os.makedirs(os.path.join(HERE, "..", "data"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "..", "data", "wp2_segmentation_lever.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    run()
