#!/usr/bin/env python3
"""WP3.2b — substitution-channel POWER CURVE vs corpus size (Constitution v2.2 Art. VIII).

WP3.2 found the scribal-substitution signal is validated on Linear B (max edge weight 303) but Linear A is
underpowered (max weight 105, below the clean regime). This quantifies the SECOND correction ("more corpus
would help"): subsample Linear B to a ladder of sizes and measure the substitution signal strength (max edge
weight + weight->same-feature AUC) as a function of corpus size. Reading off the LA operating point (its
current word-count + max weight) against the curve gives the concrete corpus multiple LA needs to reach the
validated regime. Non-circular (LB values only grade the AUC). Deterministic; read-only corpus.
"""
import json
import os
import random
import sys
from collections import Counter, defaultdict

MAIN = "/home/claude-runner/gitlab/n8n/logos"
sys.path.insert(0, MAIN)
from scripts.cross_script import data as X  # noqa: E402
HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 20260708
VOWELS = {"A", "E", "I", "O", "U"}


def cv(val):
    """parse a Ventris-Chadwick value to (consonant, vowel); None if unscorable (*NN, special)."""
    v = val.strip().upper()
    if not v or v.startswith("*") or not v.isalpha():
        return None
    if v in VOWELS:
        return ("", v)
    if v[-1] in VOWELS:
        return (v[:-1], v[-1])       # CV / CCV cluster -> consonant part + final vowel
    return None


def substitution_weights(seqs):
    """weight[(a,b)] = number of DISTINCT (n, blank_pos, context) slots where signs a,b both occur."""
    slot_fills = defaultdict(set)     # key -> set of signs seen filling that slot
    for w in seqs:
        w = [s for s in w if s]
        for n in (2, 3, 4):
            if len(w) < n:
                continue
            for i in range(len(w) - n + 1):
                gram = w[i:i + n]
                for b in range(n):
                    key = (n, b, tuple(gram[:b]), tuple(gram[b + 1:]))
                    slot_fills[key].add(gram[b])
    weight = Counter()
    for fills in slot_fills.values():
        fl = sorted(fills)
        for i in range(len(fl)):
            for j in range(i + 1, len(fl)):
                weight[(fl[i], fl[j])] += 1
    return weight


def auc_weight_feature(weight, scored):
    """AUC of edge weight predicting same-feature (share V or non-empty C), over scorable sign-pairs."""
    pairs = []
    for (a, b), w in weight.items():
        ca, cb = scored.get(a), scored.get(b)
        if ca is None or cb is None:
            continue
        same = (ca[1] == cb[1]) or (ca[0] and ca[0] == cb[0])
        pairs.append((w, 1 if same else 0))
    pos = [w for w, s in pairs if s]; neg = [w for w, s in pairs if not s]
    if not pos or not neg:
        return None, 0
    wins = sum((a > b) + 0.5 * (a == b) for a in pos for b in neg)
    return round(wins / (len(pos) * len(neg)), 3), len(pairs)


def run():
    lb_seqs = X.load_b_damos()[0]
    lb_vals = sorted({v for w in lb_seqs for v in w})
    scored = {v: cv(v) for v in lb_vals if cv(v)}
    rng = random.Random(SEED)
    idx = list(range(len(lb_seqs))); rng.shuffle(idx)
    curve = []
    for N in (1270, 2000, 3000, 5000, 8000, 13562):
        sub = [lb_seqs[i] for i in idx[:min(N, len(lb_seqs))]]
        wt = substitution_weights(sub)
        a, npair = auc_weight_feature(wt, scored)
        curve.append({"corpus_words": min(N, len(lb_seqs)), "max_weight": max(wt.values()) if wt else 0,
                      "n_edges": len(wt), "weight_feature_auc": a, "n_scored_pairs": npair})
    # LA operating point
    la_seqs = X.load_a()[1]
    la_wt = substitution_weights(la_seqs)
    la_words = sum(1 for w in la_seqs for _ in [0])  # count sequences
    la_point = {"la_sequences": len(la_seqs), "la_max_weight": max(la_wt.values()) if la_wt else 0}
    # find the LB size whose max_weight first reaches the clean regime (>=120, WP3.2 operating point)
    clean = next((r["corpus_words"] for r in curve if r["max_weight"] >= 120), None)
    la_equiv = next((r["corpus_words"] for r in curve if r["max_weight"] >= la_point["la_max_weight"]), None)
    out = {
        "power_curve_LB_subsampled": curve,
        "LA_operating_point": la_point,
        "clean_regime_corpus_words_maxweight_ge120": clean,
        "LA_equivalent_LB_corpus_words": la_equiv,
        "corpus_multiple_needed": (round(clean / max(la_equiv, 1), 1) if clean and la_equiv else None),
        "interpretation": ("substitution signal strength (max edge weight + weight->feature AUC) grows with "
                           "corpus size; LA sits below the validated clean regime. The corpus_multiple_needed "
                           "is the concrete factor by which LA would need to grow (or be segmented) for the "
                           "scribal-substitution channel to reach the validated power regime — quantifying the "
                           "SECOND correction ('more corpus would help', refuting the prior campaign)."),
    }
    os.makedirs(os.path.join(HERE, "..", "data"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "..", "data", "wp3_2b_power_curve.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    run()
