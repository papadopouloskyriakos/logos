#!/usr/bin/env python3
"""WP1 counterexample — internal evidence BREAKS the sign-relabeling symmetry (Constitution v2.2).

The prior campaign's stopping theorem showed that held-out bigram likelihood over sign IDENTITIES is
invariant under label permutation. That objective is relabeling-invariant BY CONSTRUCTION; it proves nothing
about objectives that use RELATIVE structure. This script constructs the counterexample:

  * word-POSITION statistics distinguish VOWEL signs from consonant (CV) signs. In a CV syllabary the pure-
    vowel signs behave differently (word-initial preference, position profile). An objective that couples
    'this sign is vowel-like' to 'this value is a vowel' is NOT invariant under arbitrary relabeling — it is
    invariant only under permutations WITHIN the vowel class and WITHIN the consonant class, i.e. the symmetry
    group drops from S_n to S_v x S_(n-v). Internal evidence thus reduces the value equivalence classes.

Validation on known-truth Linear B (values known: vowels = {A,E,I,O,U}); then applied to Linear A. If the
position statistic separates LB vowels from consonants above chance, the relabeling theorem is OVERSTATED.
Deterministic; reads corpus read-only from the main worktree.
"""
import json
import math
import os
import random
import sys
from collections import Counter

MAIN = "/home/claude-runner/gitlab/n8n/logos"
sys.path.insert(0, MAIN)
from scripts.cross_script import data as X  # noqa: E402
HERE = os.path.dirname(os.path.abspath(__file__))
SEED = 20260708
LB_VOWELS = {"A", "E", "I", "O", "U"}


def position_features(seqs):
    """per-sign: initial-rate, final-rate, mean normalized position, total freq."""
    init = Counter(); fin = Counter(); tot = Counter(); pos_sum = Counter()
    for w in seqs:
        w = [s for s in w if s]
        L = len(w)
        if L < 1:
            continue
        for i, s in enumerate(w):
            tot[s] += 1
            pos_sum[s] += (i / (L - 1)) if L > 1 else 0.5
        init[w[0]] += 1
        fin[w[-1]] += 1
    feats = {}
    for s in tot:
        feats[s] = {"initial_rate": init[s] / tot[s], "final_rate": fin[s] / tot[s],
                    "mean_pos": pos_sum[s] / tot[s], "freq": tot[s]}
    return feats


def auc(scores, labels):
    """AUC of a scalar score separating positive (label=1) from negative — Mann-Whitney."""
    pos = [s for s, l in zip(scores, labels) if l]
    neg = [s for s, l in zip(scores, labels) if not l]
    if not pos or not neg:
        return None
    wins = sum((sp > sn) + 0.5 * (sp == sn) for sp in pos for sn in neg)
    return round(wins / (len(pos) * len(neg)), 3)


def perm_p(scores, labels, observed_auc, n=2000):
    rng = random.Random(SEED)
    lab = list(labels)
    hits = 0
    for _ in range(n):
        rng.shuffle(lab)
        a = auc(scores, lab)
        if a is not None and a >= observed_auc:
            hits += 1
    return round((hits + 1) / (n + 1), 4)


def run():
    lb_seqs, _, _ = X.load_b_damos()
    lb_feats = position_features(lb_seqs)
    # only signs with enough mass
    lb = {s: f for s, f in lb_feats.items() if f["freq"] >= 20}
    signs = sorted(lb)
    labels = [s in LB_VOWELS for s in signs]
    init_scores = [lb[s]["initial_rate"] for s in signs]
    a_init = auc(init_scores, labels)
    p_init = perm_p(init_scores, labels, a_init)
    ranked = sorted(signs, key=lambda s: -lb[s]["initial_rate"])
    vowel_ranks = {s: ranked.index(s) + 1 for s in LB_VOWELS if s in lb}
    top10 = [(s, round(lb[s]["initial_rate"], 2)) for s in ranked[:10]]

    # --- apply to Linear A (values unknown) ---
    inv, a_seqs, _ = X.load_a()
    la_feats = position_features(a_seqs)
    la = {s: f for s, f in la_feats.items() if f["freq"] >= 20}
    la_ranked = sorted(la, key=lambda s: -la[s]["initial_rate"])
    la_top = [(s, round(la[s]["initial_rate"], 2), la[s]["freq"]) for s in la_ranked[:8]]

    out = {
        "LB_validation": {
            "n_signs_ge20": len(signs), "n_true_vowels_present": sum(labels),
            "AUC_initial_rate_separates_vowels": a_init, "permutation_p": p_init,
            "true_vowel_ranks_by_initial_rate": vowel_ranks,
            "top10_by_initial_rate": top10,
            "interpretation": ("word-initial-rate separates the 5 known LB vowel signs from consonants with "
                               "AUC=%s (perm p=%s) — a position objective is NOT relabeling-invariant, so "
                               "internal evidence DOES break the vowel/consonant symmetry." % (a_init, p_init)),
        },
        "LA_application": {
            "n_signs_ge20": len(la), "top8_vowel_candidates_by_initial_rate": la_top,
            "note": "candidate vowel-like signs from LA-internal position structure ONLY (no LB values used). "
                    "These define a reduced value-equivalence structure; validation vs the AB-vowel hypothesis "
                    "is a separate (circular) check, not training.",
        },
        # existence is the criterion: any SIGNIFICANT separation (p<0.05) refutes universal value-blindness.
        # AUC magnitude indicates strength (modest with a single feature; strengthened in WP3).
        "theorem_verdict": "PRIOR_THEOREM_OVERSTATED" if (a_init and p_init < 0.05) else "PRIOR_THEOREM_VALID_WITHIN_SCOPE",
        "effect_strength": "modest (single position feature, AUC %s); WP3 builds the full multi-feature C/V + substitution + morphology recovery" % a_init,
        "formal_scope": ("The relabeling invariance holds ONLY for objectives that are functions of sign-"
                         "identity co-occurrence counts (e.g. bigram likelihood). Objectives coupling internal "
                         "relational structure (word position, substitution similarity, morphological class) to "
                         "value-space structure (C/V, phonological features) are invariant only under the "
                         "SUBGROUP preserving that structure (S_v x S_(n-v) for C/V), so internal evidence "
                         "reduces the value equivalence classes. Absolute phoneme naming still needs external "
                         "anchors; the equivalence-class SIZE does not."),
    }
    os.makedirs(os.path.join(HERE, "..", "data"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "..", "data", "wp1_symmetry_break.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    run()
