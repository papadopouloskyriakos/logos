#!/usr/bin/env python3
"""run_ugaritic.py — Ugaritic -> Hebrew known-answer recovery (the credibility milestone).

The right fit for the 1-1 heuristic engine: Ugaritic and (Old) Hebrew are both consonantal
abjads, so a 1-1 char (consonant) map is WELL-POSED — unlike Linear B's syllabary, where a
sign encodes a CV syllable and a 1-1 sign->letter map is the wrong granularity. Loads the gold
cognate pairs (corpus/bronze/ugaritic/uga-heb.gold.cog, 2,214 pairs — the Luo 2019 / Snyder
2010 / B-K&K benchmark), runs the EM engine, and reports cognate-translation accuracy vs the
length-only chance floor. This is the known-answer recovery the expert audits asked for.

Note (per audit): this is the SIMPLIFIED heuristic (1-1, hard-argmax, no restarts, no neural),
so expect it to LAND BELOW Luo 2019's neural ~67% — that gap is the documented upgrade headroom,
not a bug.

    python3 scripts/decipher/run_ugaritic.py
"""
import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))          # scripts/decipher
REPO = os.path.dirname(os.path.dirname(_here))               # logos repo root
sys.path.insert(0, REPO)
from scripts.decipher import decipher  # noqa: E402

GOLD = os.path.join(REPO, "corpus", "bronze", "ugaritic", "uga-heb.gold.cog")


def load_gold(path):
    """Return (true_pairs {cipher_tuple: plain_tuple}, plain_vocab set)."""
    true_pairs, plain_vocab = {}, set()
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.rstrip("\n")
            if not line or i == 0 or "\t" not in line:
                continue  # skip header + blanks
            uga, heb = line.split("\t", 1)
            uga = uga.strip()
            if not uga:
                continue
            cands = [h.strip() for h in heb.split("|") if h.strip()]
            if not cands:
                continue
            cw = tuple(uga)           # char-tokenised consonant sequence
            true_pairs.setdefault(cw, tuple(cands[0]))   # first candidate = gold cognate
            for h in cands:
                plain_vocab.add(tuple(h))
    return true_pairs, plain_vocab


def main():
    if not os.path.exists(GOLD):
        sys.exit(f"gold corpus not found: {GOLD} (run scripts/fetch_ugaritic.py first)")
    true_pairs, plain_vocab = load_gold(GOLD)
    cipher_words = list(true_pairs.keys())
    plain_words = list(plain_vocab)
    print("=" * 70)
    print("UGARITIC -> HEBREW — known-answer recovery (gold 2,214 cognate pairs)")
    print("=" * 70)
    print(f"cipher words (Ugaritic, unique) : {len(cipher_words)}")
    print(f"plain candidates (Hebrew vocab) : {len(plain_words)}")
    print("-" * 70)
    phi, alignments, hist = decipher.run_em(
        cipher_words, plain_words, init="frequency", max_iters=25, verbose=False)
    m = decipher.evaluate(phi, alignments, true_pairs=true_pairs,
                          cipher_words=cipher_words, plain_words=plain_words)
    print(f"converged in {len(hist)} iteration(s)")
    print("-" * 70)
    print("learned Ugaritic -> Hebrew consonant map (sample):")
    for c, p in sorted(phi.items())[:25]:
        print(f"    {c} -> {p}")
    print("-" * 70)
    print("eval:")
    if "cognate_accuracy" in m:
        print(f"    cognate_accuracy   : {m['cognate_accuracy']:.4f}  "
              f"({m['cognate_correct']}/{m['cognate_evaluated']})")
    if "chance_cognate_accuracy" in m:
        print(f"    chance (null floor): {m['chance_cognate_accuracy']:.4f}")
    print(f"    mean_edit_distance : {m.get('mean_edit_distance', 0):.4f}")
    print(f"    (Luo 2019 neural reference: ~0.67 cognate accuracy; this is the non-neural floor)")
    print("=" * 70)


if __name__ == "__main__":
    main()
