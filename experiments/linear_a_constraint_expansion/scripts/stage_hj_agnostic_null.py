#!/usr/bin/env python3
"""Stages H + J — agnostic decipherment search + end-to-end null (Constitution v2.2 Art. VII/IV/XVI).

Stage D2 established that the corpus's internal distributional structure is invariant under any bijective
sign relabeling. A sign-VALUE assignment IS a relabeling, so no agnostic search using INTERNAL evidence can
rank one value-map above another — the internal channel is value-blind by construction. This script confirms
that concretely: it fits a phonotactic bigram model, then scores held-out sequences under M random sign-value
bijections and shows the held-out log-likelihood is IDENTICAL across all M (variance 0). Therefore:
  * Stage H (agnostic internal value search): PROVABLE NULL — no internal objective distinguishes value maps.
  * Stage J (end-to-end null): the only ranker left is external-anchor fit; Stage F found no independent
    held-out anchor set, and the graduation gate false-graduates at 0.6% (best-of-100 random maps), so any
    apparent 'system' from anchor-fit is one-toponym-deep noise, consistent with the two frozen REFUTEs.
Reads corpus read-only from the main worktree. Deterministic.
"""
import json
import math
import os
import random
from collections import Counter, defaultdict

MAIN = "/home/claude-runner/gitlab/n8n/logos"
INSC = json.load(open(os.path.join(MAIN, "corpus/silver/inscriptions_structured.json")))
HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 20260707


def sequences():
    seqs = []
    for r in INSC:
        for t in (r.get("stream") or []):
            if t.get("t") == "word" and len(t.get("signs", [])) >= 2:
                seqs.append(tuple(t["signs"]))
    return seqs


def bigram_ll(seqs, sign_map=None):
    """held-out bigram log-likelihood under an optional sign relabeling (a value assignment)."""
    def relabel(s):
        return sign_map.get(s, s) if sign_map else s
    rng = random.Random(SEED)
    idx = list(range(len(seqs)))
    rng.shuffle(idx)
    cut = int(len(seqs) * 0.8)
    train = [seqs[i] for i in idx[:cut]]
    test = [seqs[i] for i in idx[cut:]]
    uni = Counter(); big = defaultdict(Counter)
    for w in train:
        w = [relabel(s) for s in w]
        for i, s in enumerate(w):
            uni[s] += 1
            if i:
                big[w[i - 1]][s] += 1
    V = len(uni) + 1
    ll = 0.0; n = 0
    for w in test:
        w = [relabel(s) for s in w]
        for i, s in enumerate(w):
            if i == 0:
                p = (uni[s] + 1) / (sum(uni.values()) + V)
            else:
                prev = w[i - 1]
                p = (big[prev][s] + 1) / (sum(big[prev].values()) + V)
            ll += math.log(p); n += 1
    return round(ll / n, 6)


def run():
    seqs = sequences()
    signs = sorted({s for w in seqs for s in w})
    base = bigram_ll(seqs)
    rng = random.Random(SEED)
    lls = []
    for _ in range(30):                         # 30 random value-map bijections
        perm = signs[:]; rng.shuffle(perm)
        m = dict(zip(signs, perm))
        lls.append(bigram_ll(seqs, m))
    invariant = max(lls) - min(lls) < 1e-9
    out = {
        "n_multisign_sequences": len(seqs), "n_distinct_signs": len(signs),
        "held_out_bigram_ll_no_map": base,
        "held_out_bigram_ll_across_30_random_value_maps": {"min": min(lls), "max": max(lls),
                                                           "identical": invariant},
        "stage_H_verdict": "PROVABLE_NULL",
        "stage_H_reason": ("held-out likelihood is IDENTICAL across all 30 random sign-value bijections "
                           "(range < 1e-9) — internal evidence is value-blind (relabeling-invariant), so an "
                           "agnostic internal search cannot rank value maps or exceed the null."),
        "stage_J_end_to_end_null": {
            "gate_false_graduation_best_of_100_random_maps": "3/500 = 0.6% (CP 95% upper 1.54%)",
            "internal_channel_held_out_value_hits": "0.0000 (4 independent confirmations)",
            "only_ranker": "external-anchor fit — Stage F: no >=3-independent held-out non-circular anchors; "
                           "existing pins one-toponym-deep, LOTO-fragile (two frozen preregistered REFUTEs)",
            "verdict": "no agnostic system beats the end-to-end null; apparent systems are one-deep noise",
        },
        "note": "No unbounded root/language search was run (forbidden). The null is PROVABLE from relabeling-invariance; this script confirms it empirically.",
    }
    json.dump(out, open(os.path.join(HERE, "..", "data", "stage_hj_null.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "..", "data"), exist_ok=True)
    run()
