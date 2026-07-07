#!/usr/bin/env python3
"""GORILA WORD-segmented Linear A loader (shared helper).

The packed loader `scripts.cross_script.data.load_a()` returns 539 whole-inscription
sequences (mean ~7.9 signs). WP2 found the packing costs the segmentation channel AUC
(0.685 packed vs 0.760 word-segmented): a packed inscription glues unrelated words, so a
"minimal pair" or a "neighbour" crosses a real word boundary. GORILA marks word division
explicitly; the silver stream carries it as `t=='word'` tokens.

`load_a_words()` returns per-WORD sign lists, normalized identically to load_a() (subscript
digits -> ASCII, damage masks stripped) and filtered to the SAME conservative inventory, so
the packed-vs-word comparison is apples-to-apples (same vocabulary, same normalization; the
ONLY difference is the co-occurrence unit).

3,147 raw word tokens (mean 1.84 signs). After conservative-inventory filtering: 2,479
words with >=1 in-inventory sign (mean 2.00), of which 1,270 have >=2 signs (the units that
can carry a substitution n-gram). Read-only from the main worktree.
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter
from typing import List, Tuple

MAIN = "/home/claude-runner/gitlab/n8n/logos"
sys.path.insert(0, MAIN)
from scripts.cross_script import data as X  # noqa: E402

SILVER = os.path.join(MAIN, "corpus", "silver")
A_STRUCTURED = os.path.join(SILVER, "inscriptions_structured.json")
A_INVENTORY = os.path.join(SILVER, "inventory_syllabograms_conservative.json")


def load_a_words(min_len: int = 1) -> Tuple[List[str], List[List[str]], Counter]:
    """Return (inventory, word_sequences, freq).

    word_sequences: per-GORILA-word sign lists, conservative-inventory-filtered, in the same
    token space load_a() uses. `min_len` drops words with fewer than that many in-inventory
    signs (default 1 keeps singletons, which still feed position features; the substitution
    graph itself only ever consumes n>=2 grams).
    """
    inv = json.load(open(A_INVENTORY))
    keep = set(inv["inventory"])
    recs = json.load(open(A_STRUCTURED))
    seqs: List[List[str]] = []
    freq: Counter = Counter()
    for rec in recs:
        for tok in rec.get("stream", []):
            if tok.get("t") != "word":
                continue
            s = [X._norm_a_token(t) for t in tok.get("signs", [])]
            s = [t for t in s if t in keep and t != ""]
            if len(s) >= min_len:
                seqs.append(s)
                freq.update(s)
    return inv["inventory"], seqs, freq


if __name__ == "__main__":
    inv, w, f = load_a_words()
    _, p, pf = X.load_a()
    print("WORD  units:", len(w), "mean", round(sum(len(s) for s in w) / len(w), 3),
          "| vocab", len(f), "| >=2sign", sum(1 for s in w if len(s) >= 2))
    print("PACKED units:", len(p), "mean", round(sum(len(s) for s in p) / len(p), 3),
          "| vocab", len(pf))
