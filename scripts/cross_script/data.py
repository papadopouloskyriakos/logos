#!/usr/bin/env python3
"""data.py -- load Linear A & B sign sequences and build the A<->B bridge.

This is Track B (cross-script phonetic imputation). Reframed per the expert audit:

  This is NOT "manufacturing a cognate target". Linear A borrowed its script from
  the same tradition as Linear B (script borrowing), but the two scripts write
  DIFFERENT LANGUAGES -- Linear B writes Mycenaean Greek (deciphered, Ventris 1952);
  Linear A writes Minoan (UNdeciphered, isolate, Etruscan-grade). The output is a
  PHONETIC READOUT for A-only signs (a proposed syllabic value inherited from B),
  not a translation of Minoan. Honest ceiling = the Etruscan case (we may recover
  phonetic shape of some signs; we will NOT read the language).

THE BRIDGE (load-bearing join), documented exactly
---------------------------------------------------
We must join two representation spaces:

  * A-side identity : the Linear A Latin syllabogram TOKEN (uppercase: ``QE``,
    ``RA2``, ``PA3`` ...). These tokens are the GORILA / SigLA / lineara.xyz
    editorial convention for "this sign carries deciphered value V" -- they ARE
    the value, written in ASCII. Source tagger: ``scripts/inventory/build_ontology.py``.

  * B-side identity : the Linear B UNICODE CODEPOINT (U+10000 block). Each Linear B
    codepoint encodes one sign whose PHONETIC VALUE is part of its official Unicode
    character NAME, e.g. ``unicodedata.name("𐀤") == "LINEAR B SYLLABLE B078 QE"``.
    We parse the trailing token of the name -> the value. This is the authoritative
    Linear B syllabary (the standard published Unicode chart; cross-checked against
    the rendered Wikipedia "Linear B" syllabary table).

The join is therefore  **  A_token(uppercase)  ==  B_value(uppercase)  **   via the
shared phonetic value. It is a SCRIPT-BORROWING join (the same sign, attested in two
scripts with the same inherited value), NOT a word-translation / cognate join.
Bouchard-Cote 2013 needs cognates; we deliberately do NOT -- we exploit that the
borrowed glyph set shares phonetic values across scripts (Mikolov 2013 / MUSE
distributional-alignment setting, Conneau et al. 2017).

ANCHOR SET  = the signs that (a) are tagged AB (shared, known value) on the A side,
              (b) map to a B codepoint that is actually ATTESTED in the 919-row
              Linear-B cog corpus (so both sides have a distributional embedding).
              59 A-side AB signs -> 55 anchors (JU, PA3, TWE, ZU have no B-side
              attestation in the cog and are dropped -- a data-availability fact,
              documented, not a methodological choice).

A-only imputation targets = the 33 *-series signs that survive into the conservative
syllabogram stream (the ``inventory_syllabograms_conservative`` set). The ontology
tags 72 syllabogram-Aonly signs total; the conservative builder keeps the 33 with
enough attestations (the other 41 are hapax / allograph variants / ligatures).
"""
from __future__ import annotations

import json
import os
import re
import unicodedata
from collections import Counter
from typing import Dict, List, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))  # .../logos

SILVER = os.path.join(ROOT, "corpus", "silver")
A_INVENTORY = os.path.join(SILVER, "inventory_syllabograms_conservative.json")
A_INSCRIPTIONS = os.path.join(SILVER, "inscriptions.json")
B_COG = os.path.join(ROOT, "corpus", "bronze", "linearb", "linear_b-greek.cog")

# Unicode subscript digits -> ASCII (RA₂ -> RA2).  Source: inscriptions.json uses
# U+2080..U+2089 subscripts; the conservative inventory uses ASCII digits.
_SUB = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")


def _norm_a_token(t: str) -> str:
    """Normalize a Linear A token: subscript digits -> ASCII, strip editorial damage."""
    t = t.translate(_SUB)
    t = re.sub(r"[\[\]\?]", "", t)  # strip [, ], ? damage masks (GORILA convention)
    return t.strip()


def _b_value_from_codepoint(ch: str) -> str | None:
    """Linear B codepoint -> its uppercase phonetic VALUE via the Unicode name.

    e.g. '𐀤' -> 'QE'   (LINEAR B SYLLABLE B078 QE).
    Returns None for reserved/unnamed codepoints (U+1000C, U+10027, U+1003B, U+1003E)
    and for non-syllable codepoints (logograms / numbers, whose names lack the
    'LINEAR B SYLLABLE B<hex> <VAL>' shape).
    """
    try:
        nm = unicodedata.name(ch)
    except ValueError:
        return None
    m = re.match(r"LINEAR B SYLLABLE B[0-9A-F]+ (\S+)", nm)
    return m.group(1) if m else None


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_a() -> Tuple[List[str], List[List[str]], Counter]:
    """Return (a_inventory_signs, a_sequences, a_freq).

    a_sequences : per-inscription sign lists (the natural co-occurrence unit for
                  Linear A -- an inscription is the document; words are not
                  reliably segmented in GORILA). Only signs in the conservative
                  inventory are kept; damage masks + subscripts are normalized.
    """
    inv = json.load(open(A_INVENTORY))
    keep = set(inv["inventory"])  # 92 conservative syllabograms (AB + A-only)
    ins = json.load(open(A_INSCRIPTIONS))
    seqs: List[List[str]] = []
    freq: Counter = Counter()
    for rec in ins:
        s = [_norm_a_token(t) for t in rec.get("signs", [])]
        s = [t for t in s if t in keep and t != ""]
        if len(s) >= 2:
            seqs.append(s)
            freq.update(s)
    return inv["inventory"], seqs, freq


def load_b() -> Tuple[List[List[str]], Counter, Dict[str, str]]:
    """Return (b_sequences, b_freq, value2glyph).

    b_sequences : per-word Linear B sign lists (a word is the natural co-occurrence
                  unit -- the cog rows are individual wordforms). Each sign is
                  represented by its uppercase VALUE (e.g. 'QE'), so the B-side
                  sign identity lives in the SAME token vocabulary as the A-side.
    value2glyph: map from B value -> the actual Unicode glyph (for reporting).
    """
    seqs: List[List[str]] = []
    freq: Counter = Counter()
    value2glyph: Dict[str, str] = {}
    with open(B_COG, encoding="utf-8") as f:
        next(f)  # 'linb\\tgreek' header
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if not parts or not parts[0].strip():
                continue
            vals = []
            for ch in parts[0]:
                if ord(ch) < 0x10000:
                    continue  # not a Linear B sign codepoint
                v = _b_value_from_codepoint(ch)
                if v is None:
                    continue
                vals.append(v)
                value2glyph.setdefault(v, ch)
            if len(vals) >= 2:
                seqs.append(vals)
                freq.update(vals)
    return seqs, freq, value2glyph


def build_anchor_set(a_freq: Counter, b_freq: Counter) -> Tuple[List[str], List[str]]:
    """The 55 shared signs with embeddings on BOTH sides.

    anchor_ab : the A-side AB tokens that map to an attested B value (sorted).
    a_only    : the A-only (*-series) tokens attested in the A stream (sorted).
    """
    a_inv = json.load(open(A_INVENTORY))["inventory"]
    a_ab = [t for t in a_inv if not t.startswith("*")]
    a_only = [t for t in a_inv if t.startswith("*")]
    # anchors: A-side AB token present as a B value with freq>=1 on both sides
    anchor_ab = sorted(
        t for t in a_ab if a_freq.get(t, 0) >= 1 and b_freq.get(t, 0) >= 1
    )
    a_only = sorted(t for t in a_only if a_freq.get(t, 0) >= 1)
    return anchor_ab, a_only


def report_data() -> dict:
    """One-shot summary of the data + bridge (for run_ab.py to print)."""
    a_inv, a_seqs, a_freq = load_a()
    b_seqs, b_freq, v2g = load_b()
    anchor_ab, a_only = build_anchor_set(a_freq, b_freq)
    a_tokens = sum(a_freq.values())
    b_tokens = sum(b_freq.values())
    return {
        "a_signstrings": len(a_seqs),
        "a_tokens": a_tokens,
        "a_distinct": len(a_freq),
        "b_signstrings": len(b_seqs),
        "b_tokens": b_tokens,
        "b_distinct": len(b_freq),
        "anchors": len(anchor_ab),
        "anchor_list": anchor_ab,
        "a_not_anchored": sorted(
            set(t for t in a_inv if not t.startswith("*")) - set(anchor_ab)
        ),
        "a_only_imputable": len(a_only),
        "a_only_total_tagged": 72,  # ontology syllabogram-Aonly count (documented)
        "a_only_freq_min": min(a_freq[t] for t in a_only),
        "a_only_freq_median": sorted(a_freq[t] for t in a_only)[len(a_only) // 2],
        "a_only_freq_max": max(a_freq[t] for t in a_only),
    }


if __name__ == "__main__":
    r = report_data()
    for k, v in r.items():
        print(f"{k:22s} {v}")
