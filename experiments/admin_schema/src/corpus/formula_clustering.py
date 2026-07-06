#!/usr/bin/env python3
"""Stage 4.1 Correction 5: formula clustering — BLIND BY CONSTRUCTION.

A formula cluster id is the hash of an entry's OPAQUE word-form-id sequence (B_SIGN_… composites). The ONLY
input is the de-phoneticised opaque form sequence — never transliteration, lemma, gloss, role, or any future
label. Default classification = GROUPING_ONLY: a formula cluster is a leakage-control fold key, not a
model-visible semantic shortcut.
"""
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import graph_common as gc

CLASSIFICATION = "GROUPING_ONLY"

# inputs that MUST NOT influence a formula cluster id (audited by tests)
FORBIDDEN_INPUTS = ["transliteration", "lemma", "gloss", "translation", "role", "interpretation", "label",
                    "greek", "meaning"]


def cluster_id(opaque_form_seq):
    """opaque_form_seq: list of opaque word-form ids (e.g. ['B_SIGN_007+B_SIGN_081', ...]). -> 'FC_<hash16>'."""
    assert all(isinstance(f, str) and (f.startswith("B_SIGN") or f.startswith("A_SIGN") or f == "B_SIGN_UNK")
               for f in opaque_form_seq), "formula cluster input must be opaque form ids only"
    return "FC_" + gc.content_hash("|".join(opaque_form_seq))
