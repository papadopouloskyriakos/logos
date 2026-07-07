#!/usr/bin/env python3
"""F2 - Known-script calibration of cross-script shape/descent/function/chronology evidence.

Constitution v2.2 audit task F2. The campaign's surviving relative-structure candidate (the C3
substitution channel) will eventually want to lean on CROSS-SCRIPT evidence (Linear A signs that are
shape-homomorphic with Linear B can, the field assumes, borrow the Linear B value). Before any such
lean, F2 measures - on DECIPHERED scripts where the answer is known - how much each class of
cross-script evidence is actually worth. Four questions, each with an explicit null:

  Q1  relatedness/descent  -> value continuity   (Linear B <-> Cypriot Syllabary, both deciphered Greek)
  Q2  descent (homomorphy) -> functional/role continuity (Linear A <-> Linear B homomorphic value-signs)
  Q3  function             -> correspondence lift (within Linear B, known values)
  Q4  chronology           -> false-match reduction (Linear B -> Cypriot, ~800-yr gap grid attrition)

NON-CIRCULAR discipline: known phonetic values are used ONLY (a) as the join/identity of the
descent hypothesis being tested and (b) as grading labels. They are NEVER fed as a model input
feature - every profile feature is a pure distributional statistic over sign identities. Seed 20260708.

Data:
  - Linear A usage:  X.load_a()  -> 539 packed inscriptions, tokens already in the scholarly
                     LB-value transliteration for homomorphic signs (QE, RA2, KI ...) and *NNN for
                     Linear-A-only signs. The value-bearing vs *NNN split IS the descent relation.
  - Linear B usage:  X.load_b_damos() -> 13,562 DAMOS wordforms (sign-value lists).
  - Linear B / Cypriot value inventories: Unicode names (LINEAR B SYLLABLE ... / CYPRIOT SYLLABLE ...).
"""
from __future__ import annotations

import json
import math
import os
import random
import sys
import unicodedata as ud
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from a1_recompute import feature, auc, standardize, X  # noqa: E402  (a1 sets up the data loader)

DATA_DIR = os.path.join(HERE, "..", "data")
REPORT_DIR = os.path.join(HERE, "..", "reports")
SEED = 20260708
VOWELS = set("AEIOU")
random.seed(SEED)
np.random.seed(SEED)


def fast_auc(scores, y):
    """Vectorized Mann-Whitney AUC (ties -> 0.5). scores, y are 1-D numpy arrays; y in {0,1}."""
    order = np.argsort(scores, kind="mergesort")
    s = scores[order]
    ranks = np.empty(len(s), float)
    i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and s[j + 1] == s[i]:
            j += 1
        ranks[i:j + 1] = (i + j) / 2.0 + 1.0
        i = j + 1
    yr = y[order]
    n_pos = yr.sum(); n_neg = len(yr) - n_pos
    if n_pos == 0 or n_neg == 0:
        return 0.5
    return float((ranks[yr == 1].sum() - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg))


# ---------------------------------------------------------------------------------------------------
# value-inventory extraction from Unicode (deciphered scripts)
# ---------------------------------------------------------------------------------------------------
def unicode_values(lo, hi, marker):
    vals = []
    for cp in range(lo, hi):
        try:
            n = ud.name(chr(cp))
        except ValueError:
            continue
        if marker in n:
            vals.append(n.split()[-1] if marker == "LINEAR B SYLLABLE" else n.split("SYLLABLE")[1].strip())
    return vals


def parse_cv(v):
    """(onset, vowel) for a syllabic value; None if not a clean CV/vowel cell.

    Canonical grid only: pure vowels A E I O U -> onset ''; single-consonant + vowel -> (C, V).
    Complex/variant signs (A2, RA2, DWE, PTE, PU2, AU ...) are NOT canonical grid cells and return
    None so the grid comparison stays apples-to-apples.
    """
    if v in VOWELS:
        return ("", v)
    if len(v) == 2 and v[0] not in VOWELS and v[1] in VOWELS:
        return (v[0], v[1])
    return None


def grid(values):
    return {parse_cv(v) for v in values if parse_cv(v) is not None}


# ===================================================================================================
# Q1 - relatedness/descent -> value continuity   (Linear B <-> Cypriot Syllabary)
# ===================================================================================================
def q1_value_grid(n_null=20000):
    lb_vals = unicode_values(0x10000, 0x10100, "LINEAR B SYLLABLE")
    cy_vals = unicode_values(0x10800, 0x10840, "CYPRIOT")
    g_lb, g_cy = grid(lb_vals), grid(cy_vals)

    # attested value space shared by these related Greek syllabaries
    onsets = sorted({o for (o, _) in g_lb | g_cy})
    vspace = sorted({vw for (_, vw) in g_lb | g_cy})
    space = [(o, vw) for o in onsets for vw in vspace]
    G = len(space)

    inter = g_lb & g_cy
    union = g_lb | g_cy
    obs_jaccard = len(inter) / len(union)
    obs_cy_covered = len(inter) / len(g_cy)   # fraction of Cypriot cells that survive/exist in LB

    # NULL: two independent random syllabaries of the same sizes drawn from the C x V space
    rng = random.Random(SEED)
    nj = np.zeros(n_null)
    ncov = np.zeros(n_null)
    for i in range(n_null):
        ra = set(rng.sample(space, len(g_lb)))
        rb = set(rng.sample(space, len(g_cy)))
        it = ra & rb
        nj[i] = len(it) / len(ra | rb)
        ncov[i] = len(it) / len(rb)
    p_jac = float((nj >= obs_jaccard).mean())
    return {
        "pair": "Linear B (deciphered) <-> Cypriot Syllabary (deciphered)",
        "n_lb_cells": len(g_lb), "n_cy_cells": len(g_cy), "value_space_CxV": G,
        "onsets": onsets, "vowels": vspace,
        "shared_cells": sorted("".join(c) or c[1] for c in inter), "n_shared": len(inter),
        "observed_jaccard": round(obs_jaccard, 4),
        "observed_cypriot_grid_covered_by_lb": round(obs_cy_covered, 4),
        "null_jaccard_mean": round(float(nj.mean()), 4),
        "null_jaccard_p95": round(float(np.quantile(nj, 0.95)), 4),
        "lift_over_null": round(obs_jaccard / float(nj.mean()), 3),
        "p_value_jaccard_ge_obs": p_jac,
        "null_cy_covered_mean": round(float(ncov.mean()), 4),
        "interpretation": "system-level descent signal: two related deciphered Greek syllabaries",
    }


# ===================================================================================================
# Q2 - descent (homomorphy) -> functional/role continuity  (Linear A <-> Linear B value-signs)
# ===================================================================================================
def value_sign(tok):
    """True if a corpus token is a value-bearing (homomorphic, descended) sign, not a *NNN LA-only."""
    if not tok or tok.startswith("*"):
        return False
    return tok[0] not in "0123456789"


def profiles(words, min_count):
    F = feature(words)
    cnt = Counter()
    for w in words:
        for s in w:
            cnt[s] += 1
    return {s: v for s, v in F.items() if cnt[s] >= min_count and value_sign(s)}, cnt


def q2_cross_script(min_count=8):
    a_ids, a_words, _ = X.load_a()
    b_words, _, _ = X.load_b_damos()
    Fa, ca = profiles(a_words, min_count)
    Fb, cb = profiles(b_words, min_count)
    shared = sorted(set(Fa) & set(Fb))
    n = len(shared)

    # standardize each script's profiles within-script over the shared inventory (7 features)
    Xa = np.array([Fa[s] for s in shared]); Xb = np.array([Fb[s] for s in shared])
    Za, _, _ = standardize(Xa); Zb, _, _ = standardize(Xb)

    def cos(u, v):
        d = (np.linalg.norm(u) * np.linalg.norm(v))
        return float(u @ v / d) if d else 0.0

    # (a) matched-identity concordance vs shuffled-identity null
    obs_match = np.mean([cos(Za[i], Zb[i]) for i in range(n)])
    rng = random.Random(SEED)
    null = np.zeros(4000)
    idx = list(range(n))
    for k in range(4000):
        perm = idx[:]; rng.shuffle(perm)
        while any(perm[i] == i for i in range(n)):   # derangement: no sign matched to itself
            rng.shuffle(perm)
        null[k] = np.mean([cos(Za[i], Zb[perm[i]]) for i in range(n)])
    p_match = float((null >= obs_match).mean())

    # (b) cross-script retrieval: for each LA sign, rank all LB signs by profile cosine; where does
    #     its true homomorphic twin land? MRR and top-1 accuracy vs chance (1/n).
    ranks = []
    top1 = 0
    for i in range(n):
        sims = np.array([cos(Za[i], Zb[j]) for j in range(n)])
        order = list(np.argsort(-sims))
        r = order.index(i) + 1
        ranks.append(r)
        top1 += (r == 1)
    mrr = float(np.mean([1.0 / r for r in ranks]))
    return {
        "descent_relation": "value-bearing (homomorphic) signs shared by LA-usage and LB-usage",
        "min_count_each_script": min_count,
        "n_shared_homomorphic_signs": n,
        "shared_signs": shared,
        "observed_matched_profile_cosine": round(float(obs_match), 4),
        "null_shuffled_cosine_mean": round(float(null.mean()), 4),
        "null_shuffled_cosine_p95": round(float(np.quantile(null, 0.95)), 4),
        "p_value_match_ge_null": p_match,
        "retrieval_top1_accuracy": round(top1 / n, 4),
        "retrieval_chance_top1": round(1.0 / n, 4),
        "retrieval_mrr": round(mrr, 4),
        "retrieval_mrr_chance": round(sum(1.0 / r for r in range(1, n + 1)) / n / 1, 4),
        "interpretation": "does shape-homomorphic descent carry cross-script FUNCTIONAL continuity?",
    }


# ===================================================================================================
# Q3 - function -> correspondence lift  (within Linear B, known values)
# ===================================================================================================
def q3_function_lift(min_count=20, n_perm=1000):
    b_words, _, _ = X.load_b_damos()
    F = feature(b_words)
    cnt = Counter()
    for w in b_words:
        for s in w:
            cnt[s] += 1
    signs = [s for s in F if cnt[s] >= min_count and parse_cv(s) is not None]
    cv = {s: parse_cv(s) for s in signs}
    prof = {s: np.array(F[s]) for s in signs}
    freq = {s: F[s][6] for s in signs}   # log_freq is feature index 6

    # standardize profiles for distance
    M = np.array([prof[s] for s in signs]); Z, _, _ = standardize(M)
    zi = {s: Z[i] for i, s in enumerate(signs)}

    pairs = [(a, b) for i, a in enumerate(signs) for b in signs[i + 1:]]

    def eval_axis(same_fn):
        y = np.array([1 if same_fn(cv[a], cv[b]) else 0 for a, b in pairs])
        # function score: negative full-profile euclidean distance (closer -> more likely same axis)
        s_fun = np.array([-float(np.linalg.norm(zi[a] - zi[b])) for a, b in pairs])
        # baseline: negative |log-freq difference| (frequency-only)
        s_freq = np.array([-abs(freq[a] - freq[b]) for a, b in pairs])
        a_fun = fast_auc(s_fun, y)
        a_freq = fast_auc(s_freq, y)
        # permutation null on the lift: shuffle labels, recompute (a_fun - a_freq)
        rng = np.random.default_rng(SEED)
        obs_lift = a_fun - a_freq
        null = np.zeros(n_perm)
        for k in range(n_perm):
            yy = rng.permutation(y)
            null[k] = fast_auc(s_fun, yy) - fast_auc(s_freq, yy)
        p = float((null >= obs_lift).mean())
        return {
            "n_pos": int(y.sum()), "n_pairs": len(y),
            "auc_function_profile": round(a_fun, 4),
            "auc_frequency_baseline": round(a_freq, 4),
            "function_lift": round(obs_lift, 4),
            "null_lift_mean": round(float(null.mean()), 4),
            "null_lift_p95": round(float(np.quantile(null, 0.95)), 4),
            "p_value_lift_ge_null": p,
        }

    return {
        "script": "Linear B (known values, non-circular: values grade only)",
        "n_signs": len(signs), "min_count": min_count,
        "same_vowel_axis": eval_axis(lambda a, b: a[1] == b[1]),
        "same_consonant_axis": eval_axis(lambda a, b: a[0] == b[0] and a[0] != ""),
        "interpretation": "does distributional FUNCTION beat a pure frequency baseline at recovering "
                          "the value-relatedness axis?",
    }


# ===================================================================================================
# Q4 - chronology -> false-match reduction  (Linear B -> Cypriot Syllabary, ~800-yr gap)
# ===================================================================================================
def q4_chronology():
    lb_vals = unicode_values(0x10000, 0x10100, "LINEAR B SYLLABLE")
    cy_vals = unicode_values(0x10800, 0x10840, "CYPRIOT")
    g_lb, g_cy = grid(lb_vals), grid(cy_vals)

    # naive value-match (chronology-blind): match every LB canonical cell to a Cypriot cell of the
    # same value. Cells with NO Cypriot counterpart are FALSE/empty matches forced by the ~800-yr drift.
    survived = g_lb & g_cy
    lost = g_lb - g_cy   # LB value cells that did not survive into Cypriot -> naive false matches

    # which phonological SERIES were lost (mechanistic read of the attrition)
    lost_by_onset = Counter(o if o else "V" for (o, _) in lost)
    naive_false_rate = len(lost) / len(g_lb)
    chrono_aware_false_rate = 0.0  # restrict candidate set to survived grid -> no forced false match

    # NULL baseline: if the two grids were value-neutral (independent random draws of the same sizes)
    # what false-match rate would naive matching incur? (ties Q4 back to the Q1 space)
    onsets = sorted({o for (o, _) in g_lb | g_cy})
    vsp = sorted({vw for (_, vw) in g_lb | g_cy})
    space = [(o, vw) for o in onsets for vw in vsp]
    rng = random.Random(SEED)
    null_false = np.zeros(20000)
    for i in range(20000):
        ra = set(rng.sample(space, len(g_lb)))
        rb = set(rng.sample(space, len(g_cy)))
        null_false[i] = len(ra - rb) / len(ra)
    return {
        "pair": "Linear B (~1400 BCE) -> Cypriot Syllabary (~600 BCE), ~800-yr gap",
        "n_lb_cells": len(g_lb), "n_cy_cells": len(g_cy),
        "n_survived": len(survived), "n_lost": len(lost),
        "lost_cells": sorted("".join(c) or c[1] for c in lost),
        "lost_by_onset_series": dict(lost_by_onset),
        "naive_chronology_blind_false_match_rate": round(naive_false_rate, 4),
        "chronology_aware_false_match_rate": chrono_aware_false_rate,
        "false_matches_removed_by_chronology": len(lost),
        "null_value_neutral_false_match_rate_mean": round(float(null_false.mean()), 4),
        "interpretation": "chronological distance attrits the value grid; chronology-aware candidate "
                          "restriction removes the forced false matches naive matching would make.",
    }


def main():
    out = {
        "experiment": "F2_known_script_calibration",
        "seed": SEED,
        "non_circular": "known values used only as descent-hypothesis identity + grading labels; "
                        "never a model input feature.",
        "Q1_relatedness_to_value_continuity": q1_value_grid(),
        "Q2_descent_to_functional_continuity": q2_cross_script(),
        "Q3_function_to_correspondence_lift": q3_function_lift(),
        "Q4_chronology_to_false_match_reduction": q4_chronology(),
    }
    path = os.path.join(DATA_DIR, "F2_calibration.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print("WROTE", path)
    print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    main()
