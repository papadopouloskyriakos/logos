#!/usr/bin/env python3
"""Stage 4.1 Correction 3: recover Linear A structural channels from the silver STREAM.

The Stage-4 LA builder read only `signs` (words) and reported numerals/logograms as 'absent'. That was a
PARSER absence, not a corpus absence: `inscriptions_structured.json` carries a `stream` of typed tokens —
`word` / `num`(with value) / `nl`(row) / `div`(entry) / `other`(logogram/fraction/measure, subclass
unresolved in silver). This module classifies each stream token into an opaque, NON-SEMANTIC structural
class. Linear A logograms are NOT equated with Linear B logograms of similar shape; no LB meaning imported.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import graph_common as gc

STRUCTURED = os.path.join(gc.MAIN_ROOT, "corpus", "silver", "inscriptions_structured.json")

# channel status per §V taxonomy
CHANNEL_STATUS = {
    "NUMERAL": "CHANNEL_PRESENT_AND_PARSED",         # stream 'num' with integer value
    "ROW": "CHANNEL_PRESENT_AND_PARSED",             # stream 'nl'
    "ENTRY": "CHANNEL_PRESENT_AND_PARSED",           # stream 'div'
    "WORD_FORM": "CHANNEL_PRESENT_AND_PARSED",       # stream 'word'
    "LOGOGRAM": "CHANNEL_PRESENT_BUT_NOT_PARSED",    # inside 'other'; silver does not sub-type it
    "FRACTION": "CHANNEL_PRESENT_BUT_NOT_PARSED",    # inside 'other'
    "MEASURE_MARKER": "CHANNEL_UNKNOWN",             # not separately marked in silver
    "DOCUMENT_SERIES": "CHANNEL_GENUINELY_ABSENT",   # Linear A has no named administrative series
}


def load_structured():
    return json.load(open(STRUCTURED, encoding="utf-8"))


def build_sign_vocab(recs):
    v = gc.OpaqueVocab("A_SIGN")
    for r in recs:
        for tok in r.get("stream") or []:
            if tok.get("t") == "word":
                for s in tok.get("signs") or []:
                    v.add(str(s))
    return v.freeze()


import re as _re

_FRAC_CHARS = set("¼½¾⅓⅔⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞⁄")
_DAMAGE_CHARS = set("[]?…")
_AEGEAN = lambda ch: 0x10600 <= ord(ch) <= 0x107FF          # Linear A / Aegean numbers+ideograms block


def classify_other(raw):
    """Source-grounded classification of a silver 'other' raw glyph string. NO Linear B meaning imported."""
    if raw is None or not str(raw).strip():
        return "DAMAGED_OR_UNKNOWN", ""
    r = str(raw).strip()
    if any(c in _FRAC_CHARS for c in r) or _re.search(r"[⁰-₟].*[₀-₟]", r):
        return "FRACTION", r
    if _re.fullmatch(r"\*[0-9]+[A-Za-z]*", r) or any(_AEGEAN(c) for c in r):
        return "LOGOGRAM", r
    if any(c in _DAMAGE_CHARS for c in r):
        return "DAMAGED_OR_UNKNOWN", r
    if r in ("—", "-", "·", "|", ",", "/"):
        return "OTHER_NOTATION", r
    return "UNRESOLVED", r


def build_notation_vocabs(recs):
    """Opaque vocabs for LA logograms / fractions / other-notation, keyed by raw glyph (never LB meaning)."""
    logo, frac, other = gc.OpaqueVocab("A_LOGO"), gc.OpaqueVocab("A_FRAC"), gc.OpaqueVocab("A_NOTE")
    for r in recs:
        for tok in r.get("stream") or []:
            if tok.get("t") == "other":
                cls, norm = classify_other(tok.get("raw"))
                if cls == "LOGOGRAM":
                    logo.add(norm)
                elif cls == "FRACTION":
                    frac.add(norm)
                elif cls == "OTHER_NOTATION":
                    other.add(norm)
    return logo.freeze(), frac.freeze(), other.freeze()


def stream_tokens(rec):
    """Yield (kind, payload) recovering structure: rows (nl), entries (div), words, numerals, other."""
    for tok in rec.get("stream") or []:
        t = tok.get("t")
        if t == "word":
            yield "word", tok.get("signs") or []
        elif t == "num":
            yield "num", tok.get("v")
        elif t == "nl":
            yield "row_break", None
        elif t == "div":
            yield "entry_break", None
        elif t == "other":
            yield "other", tok.get("raw")
        else:
            yield "unknown", None
