#!/usr/bin/env python3
"""Shared helpers for the sealed-challenge programme (WP seals).

Non-circular, deterministic. Reads the READ-ONLY silver corpus from the main worktree
and never writes to it. All randomness is driven by SEED=20260708 via a per-seal
independent ``random.Random`` instance so each split is reproducible in isolation.

Provides:
  * ``load_inscriptions()``   -> list of raw inscription records (id/site/support/stream/words)
  * ``a_word_units(rec)``     -> conservative-inventory-filtered syllabic word units of a rec,
                                 using the SAME normalization as scripts/word_units.py
  * ``is_libation_carrier()`` -> deterministic canonical-formula membership test
  * ``sha256_canonical()``    -> stable hash over canonical JSON (the sealing commitment)

The word-unit filter reuses ``scripts.cross_script.data._norm_a_token`` and the conservative
syllabogram inventory, exactly like ``load_a_words`` in scripts/word_units.py, so the sealed
sets live in the same token space every WP measured in.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from typing import Dict, List

SEED = 20260708

MAIN = "/home/claude-runner/gitlab/n8n/logos"
sys.path.insert(0, MAIN)
from scripts.cross_script import data as X  # noqa: E402

SILVER = os.path.join(MAIN, "corpus", "silver")
A_STRUCTURED = os.path.join(SILVER, "inscriptions_structured.json")
A_INVENTORY = os.path.join(SILVER, "inventory_syllabograms_conservative.json")

# Canonical Linear A libation-formula words (GORILA transliteration values), from the
# standard cult-formula literature (Duhoux 1989; Davis 2014; Consani). A carrier is any
# inscription whose word stream contains one of these as a whole word or as its head.
# This is a FIXED published criterion applied identically to every inscription -- it defines
# the split, it does not read anything off the corpus for hypothesis formation.
LIBATION_FORMULA_WORDS: List[List[str]] = [
    ["JA", "SA", "SA", "RA", "ME"],
    ["JA", "SA", "SA", "RA"],
    ["A", "SA", "SA", "RA", "ME"],
    ["A", "TA", "I"],            # A-TA-I-*301-WA-JA head (the *301 sign is outside the
                                 # conservative inventory; the 3-sign head is the stable anchor)
    ["JA", "DI", "KI", "TU"],
    ["U", "NA", "KA", "NA", "SI"],
    ["I", "PI", "NA", "MA"],
    ["SI", "RU", "TE"],
    ["TA", "NA", "I"],           # TA-NA-I-*301-U-TI-NU head
    ["I", "NA", "JA", "PA", "QA"],
]


def _norm(w: List[str]) -> List[str]:
    return [X._norm_a_token(t) for t in w]


def load_inscriptions() -> List[Dict]:
    return json.load(open(A_STRUCTURED))


def conservative_inventory() -> set:
    return set(json.load(open(A_INVENTORY))["inventory"])


def a_word_units(rec: Dict, keep: set, min_len: int = 1) -> List[List[str]]:
    """Conservative-inventory-filtered syllabic word units of one inscription."""
    out: List[List[str]] = []
    for tok in rec.get("stream", []):
        if tok.get("t") != "word":
            continue
        s = [t for t in (X._norm_a_token(x) for x in tok.get("signs", [])) if t in keep and t != ""]
        if len(s) >= min_len:
            out.append(s)
    return out


def is_libation_carrier(rec: Dict) -> List[str]:
    """Return the sorted list of canonical formula heads present, or [] if not a carrier."""
    found = set()
    for w in rec.get("words", []):
        wn = _norm(w)
        for fw in LIBATION_FORMULA_WORDS:
            if wn == fw or wn[: len(fw)] == fw:
                found.add("-".join(fw))
    return sorted(found)


def numeral_tokens(rec: Dict) -> List[Dict]:
    """Return (stream_index, value) for every numeral token in an inscription."""
    out = []
    for i, tok in enumerate(rec.get("stream", [])):
        if tok.get("t") == "num":
            out.append({"stream_index": i, "value": tok.get("v")})
    return out


def sha256_canonical(obj) -> str:
    """Stable sha256 over canonical (sorted-key, compact) JSON -- the sealing commitment."""
    blob = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()
