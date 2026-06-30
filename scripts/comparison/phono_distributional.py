#!/usr/bin/env python3
"""phono_distributional.py — distributional-phonology PILOT (Track-2, offensive; non-blocking).

PRE-REGISTERED TEST (fixed here BEFORE running): does the DISTRIBUTIONAL context of a sign — which signs
it sits beside in the corpus — carry information about its PHONETIC value, measured on the KNOWN `AB`
signs whose Linear B sound value we can borrow (GORILA convention)? Operationally: build a context
vector per sign (left+right neighbour bigram counts over the sign vocabulary, PPMI-weighted, L2-norm),
then by LEAVE-ONE-OUT nearest-neighbour ask whether a sign's closest distributional neighbour shares its
CONSONANT class and (separately) its VOWEL, ABOVE a label-permutation null (which holds the distributional
geometry fixed and shuffles the phonetic labels). Šidák-deflate over the 2 tests (C, V).

WHY this is the non-circular version: the FEATURES are raw co-occurrence (never the phonetic labels); the
LABELS are the LB-transferred C/V (assumed, but assigned independently of the geometry). We are NOT
clustering assumed values (that would be circular) — we are testing whether raw distribution PREDICTS the
independently-assigned values. A POSITIVE on the knowns is the prerequisite for imputing sound values to
the A-only (un-anchored) signs (the offensive goal); a NULL means the corpus is too thin and the sound
path needs DĀMOS.

TRUTH-LAYER CAP (invariant 5): a positive only PROPOSES a bridge; only held-out reads decide. NO phonetic
VALUE is asserted for any A-only sign here. Grades from the persisted artifact; imports no verdict.
"""
from __future__ import annotations

import argparse
import json
import os
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from .morphology import load_corpus, Inscription, DEFAULT_SILVER
from .litindex import LB_TRANSFER_SIGNS

VOWELS = set("AEIOU")


def cv_label(sign: str) -> Optional[Tuple[str, str]]:
    """(consonant, vowel) for a known AB syllabogram from its GORILA romanisation. The last char is the
    vowel; the preceding chars are the consonant ('' for the pure vowels A/E/I/O/U; 'NW' for NWA)."""
    s = sign.strip()
    if not s or s[-1] not in VOWELS:
        return None
    return (s[:-1], s[-1])          # ('' , 'A') for A; ('D','A') for DA; ('NW','A') for NWA


def known_cv_labels() -> Dict[str, Tuple[str, str]]:
    """The AB (Linear-B-value) signs with a parseable (C, V) — the labelled test set."""
    out = {}
    for s in LB_TRANSFER_SIGNS:
        lab = cv_label(s)
        if lab is not None:
            out[s] = lab
    return out


# --------------------------------------------------------------------------- #
# Context vectors: left+right neighbour bigram counts over the sign vocabulary, within each inscription
# (sequence of signs, word-boundaries flattened — Linear A words are too short for within-word context).
# Boundary markers (^, $) at inscription edges. PPMI-weighted, L2-normalised.
# --------------------------------------------------------------------------- #
def build_context_vectors(corpus: Sequence[Inscription]) -> Tuple[Dict[str, np.ndarray], List[str], Dict[str, int]]:
    seqs = [["^"] + ins.signs + ["$"] for ins in corpus]
    vocab = sorted({t for seq in seqs for t in seq})
    idx = {t: i for i, t in enumerate(vocab)}
    V = len(vocab)
    left = defaultdict(lambda: np.zeros(V))     # counts of left neighbours
    right = defaultdict(lambda: np.zeros(V))    # counts of right neighbours
    freq: Counter = Counter()
    for seq in seqs:
        for i in range(1, len(seq) - 1):        # skip the boundary tokens themselves as centres
            s = seq[i]
            left[s][idx[seq[i - 1]]] += 1
            right[s][idx[seq[i + 1]]] += 1
            freq[s] += 1
    # PPMI on the concatenated [left | right] count matrix, then L2-normalise each row
    vecs: Dict[str, np.ndarray] = {}
    for s in freq:
        raw = np.concatenate([left[s], right[s]])
        vecs[s] = raw
    # PPMI: pmi = log( p(c|s) / p(c) ), floored at 0
    M = np.vstack([vecs[s] for s in vecs]) if vecs else np.zeros((0, 2 * V))
    signs = list(vecs.keys())
    col = M.sum(axis=0); col = np.where(col == 0, 1, col)
    row = M.sum(axis=1, keepdims=True); row = np.where(row == 0, 1, row)
    total = M.sum() or 1.0
    with np.errstate(divide="ignore", invalid="ignore"):
        ppmi = np.log((M / row) / (col / total))
    ppmi = np.nan_to_num(np.maximum(ppmi, 0.0))
    norm = np.linalg.norm(ppmi, axis=1, keepdims=True); norm = np.where(norm == 0, 1, norm)
    ppmi = ppmi / norm
    out = {s: ppmi[i] for i, s in enumerate(signs)}
    return out, signs, dict(freq)


def _loo_nn_accuracy(X: np.ndarray, labels: List[str]) -> float:
    """Leave-one-out 1-NN: fraction of signs whose nearest (cosine) neighbour shares the label."""
    S = X @ X.T                                  # cosine (rows are L2-normalised)
    np.fill_diagonal(S, -np.inf)
    nn = np.argmax(S, axis=1)
    return float(np.mean([labels[i] == labels[nn[i]] for i in range(len(labels))]))


def _power_control(labels: List[str], *, strengths: Sequence[float] = (1, 2, 3, 5, 8, 13),
                   n_perm: int = 500, seed: int = 0) -> Dict[str, object]:
    """POSITIVE CONTROL / POWER CURVE: plant context vectors that ARE informative about the label
    (one-hot of the class, signal `strength`, + unit Gaussian noise) and report at which strength the
    LOO-1NN + permutation test starts firing (perm p<0.05). This distinguishes the two reasons a real
    null can arise: (a) the test WORKS but the corpus/n is too small to detect a weak real signal
    (fires only at high planted strength) -> data-limited/underpowered null; (b) the test is BROKEN
    (never fires even at a near-perfect planted signal) -> uninterpretable, fix the test."""
    rng = np.random.default_rng(seed + 99)
    classes = sorted(set(labels))
    cidx = {c: i for i, c in enumerate(classes)}
    onehot = np.eye(len(classes))[[cidx[c] for c in labels]]
    curve = []
    min_firing = None
    for st in strengths:
        X = onehot * float(st) + rng.normal(0, 1.0, onehot.shape)
        norm = np.linalg.norm(X, axis=1, keepdims=True); norm = np.where(norm == 0, 1, norm)
        X = X / norm
        obs = _loo_nn_accuracy(X, labels)
        null = np.array([_loo_nn_accuracy(X, list(rng.permutation(np.array(labels, dtype=object))))
                         for _ in range(n_perm)])
        p = float((np.sum(null >= obs) + 1) / (n_perm + 1))
        fires = bool(p < 0.05)
        curve.append({"strength": float(st), "acc": obs, "perm_p": p, "fires": fires})
        if fires and min_firing is None:
            min_firing = float(st)
    return {"power_curve": curve, "min_firing_strength": min_firing,
            "test_has_power": min_firing is not None, "n_classes": len(classes), "n_points": len(labels)}


def run_pilot(path: str = DEFAULT_SILVER, *, min_count: int = 3, n_perm: int = 2000,
              seed: int = 0) -> Dict[str, object]:
    corpus = load_corpus(path)
    vecs, _signs, freq = build_context_vectors(corpus)
    labels = known_cv_labels()
    # testable AB signs: have a context vector AND occur >= min_count times (else the vector is noise)
    testable = [s for s in labels if s in vecs and freq.get(s, 0) >= min_count]
    X = np.vstack([vecs[s] for s in testable]) if testable else np.zeros((0, 0))
    cons = [labels[s][0] for s in testable]
    vow = [labels[s][1] for s in testable]
    rng = np.random.default_rng(seed)

    def _test(lab: List[str]) -> Dict[str, object]:
        obs = _loo_nn_accuracy(X, lab)
        null = np.empty(n_perm)
        arr = np.array(lab, dtype=object)
        for k in range(n_perm):
            perm = rng.permutation(len(arr))
            null[k] = _loo_nn_accuracy(X, list(arr[perm]))
        p = float((np.sum(null >= obs) + 1) / (n_perm + 1))     # add-one (Phipson-Smyth)
        base = max(Counter(lab).values()) / len(lab) if lab else 0.0
        return {"observed_acc": obs, "null_mean": float(null.mean()), "null_p95": float(np.percentile(null, 95)),
                "perm_p": p, "majority_base_rate": base, "n_classes": len(set(lab))}

    res_c = _test(cons) if testable else {}
    res_v = _test(vow) if testable else {}
    # POSITIVE CONTROL: the test must DETECT a planted signal (else a null is just a broken test).
    power = _power_control(cons, n_perm=min(500, n_perm), seed=seed) if testable else {}
    # Šidák over the 2 tests
    sidak = lambda p: 1 - (1 - p) ** 2
    pc = res_c.get("perm_p", 1.0); pv = res_v.get("perm_p", 1.0)
    c_sig = bool(testable) and sidak(pc) < 0.05
    v_sig = bool(testable) and sidak(pv) < 0.05
    bridge = c_sig or v_sig

    mfs = power.get("min_firing_strength")
    if not testable:
        verdict = "NO POWER — no AB sign meets the min-count threshold for a stable context vector."
    elif not power.get("test_has_power"):
        verdict = ("INVALID — the positive control NEVER fired, even at a near-perfect planted signal: "
                   "the test cannot detect signal on a 50-sign / 13-class problem, so the real result is "
                   "uninterpretable. The test (not Linear A) is the limit; do not read the real numbers.")
    elif bridge:
        verdict = (f"SIGNAL (truth-layer-capped, <=0.75): distribution predicts "
                   f"{'consonant' if c_sig else ''}{'+' if c_sig and v_sig else ''}{'vowel' if v_sig else ''} "
                   f"class above the permutation null on the known AB signs -> a distribution->phonetics "
                   f"bridge exists; this PROPOSES (never decides) sound-imputation for A-only signs, and "
                   f"justifies the DĀMOS-fed run. NOT a decipherment claim.")
    else:
        verdict = (f"DATA-LIMITED NULL: the test WORKS (positive control fires only at a strong planted "
                   f"signal, strength>={mfs}, on these {len(testable)} signs), but the REAL distributional "
                   f"context does not predict consonant or vowel class above the permutation null "
                   f"(Šidák-deflated). So we CANNOT distinguish 'no distribution->phonetics bridge' from "
                   f"'too few signs/contexts to detect a weak one' — both point the same way: the sound "
                   f"path is not recoverable from Linear A alone and needs the larger Linear B corpus "
                   f"(DĀMOS). No sound value is imputed for any sign.")

    return {
        "pilot": "distributional-phonology (Track-2, truth-layer-capped)",
        "n_inscriptions": len(corpus),
        "n_ab_signs_labelled": len(labels),
        "n_testable": len(testable),
        "min_count": min_count,
        "testable_signs": sorted(testable),
        "consonant_test": res_c,
        "vowel_test": res_v,
        "sidak_p_consonant": sidak(pc) if testable else None,
        "sidak_p_vowel": sidak(pv) if testable else None,
        "power_control": power,
        "bridge_detected": bridge,
        "verdict": verdict,
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Distributional-phonology pilot (Track-2)")
    p.add_argument("--corpus", default=DEFAULT_SILVER)
    p.add_argument("--min-count", type=int, default=3)
    p.add_argument("--n-perm", type=int, default=2000)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--json", default=None)
    args = p.parse_args(list(argv) if argv is not None else None)
    r = run_pilot(args.corpus, min_count=args.min_count, n_perm=args.n_perm, seed=args.seed)
    print("== distributional-phonology pilot (Track-2, truth-layer-capped) ==")
    print(f"AB signs labelled: {r['n_ab_signs_labelled']}; testable (>= {r['min_count']} occ): {r['n_testable']}")
    for name, key in [("consonant", "consonant_test"), ("vowel", "vowel_test")]:
        t = r[key]
        if t:
            print(f"  {name:9s}: LOO-1NN acc {t['observed_acc']:.3f} vs null {t['null_mean']:.3f} "
                  f"(p95 {t['null_p95']:.3f}); perm p={t['perm_p']:.4f}; base {t['majority_base_rate']:.3f} "
                  f"({t['n_classes']} classes)")
    print(f"  Šidák p: consonant={r['sidak_p_consonant']}, vowel={r['sidak_p_vowel']}")
    pw = r.get("power_control", {})
    if pw:
        parts = []
        for c in pw.get("power_curve", []):
            tag = "FIRE" if c["fires"] else ("p=%.2f" % c["perm_p"])
            parts.append("s%g:%s" % (c["strength"], tag))
        print("  POWER CURVE (planted signal): " + " ".join(parts))
        print(f"  test_has_power={pw.get('test_has_power')} (min firing strength={pw.get('min_firing_strength')})")
    print(f"bridge_detected: {r['bridge_detected']}")
    print(f"VERDICT: {r['verdict']}")
    if args.json:
        os.makedirs(os.path.dirname(os.path.abspath(args.json)), exist_ok=True)
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(r, f, indent=2, ensure_ascii=False)
        print(f"wrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
