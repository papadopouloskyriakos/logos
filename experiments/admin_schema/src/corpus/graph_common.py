#!/usr/bin/env python3
"""Shared constants + helpers for the canonical transferable admin document graph (Stage 4).

The MODEL-VISIBLE graph carries ONLY opaque IDs + structure + non-semantic metadata. The de-phoneticisation
vocabularies (opaque_id -> original phonetic value) are the KEY that must stay EVALUATION-ONLY: they live
under data/evaluation_only/ and are never read by model code.
"""
import hashlib
import os

BUILDER_VERSION = "admin-graph-builder-v1-2026-07-07"
SOURCE_VERSION_DAMOS = "damos-items-jsonl"

EXP = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
MAIN_ROOT = "/home/claude-runner/gitlab/n8n/logos"
MODEL_VISIBLE = os.path.join(EXP, "data", "model_visible")
EVAL_ONLY = os.path.join(EXP, "data", "evaluation_only")

NODE_TYPES = {"DOCUMENT", "SIDE_OR_FACE", "ROW", "COLUMN_OR_ZONE", "ENTRY", "TOKEN", "WORD_FORM", "SIGN",
              "LOGOGRAM", "NUMERAL", "FRACTION", "MEASURE_MARKER", "DOCUMENT_SERIES", "SITE", "FINDSPOT",
              "SCRIBE", "OBJECT_OR_SUPPORT", "CHRONOLOGICAL_PHASE", "JOINED_FRAGMENT_CLUSTER", "FORMULA_CLUSTER"}
EDGE_TYPES = {"CONTAINS", "NEXT_TOKEN", "PREVIOUS_TOKEN", "NEXT_ENTRY", "PREVIOUS_ENTRY", "SAME_WORD_FORM",
              "SAME_FORMULA_CLUSTER", "SAME_ROW", "SAME_COLUMN_OR_ZONE", "SAME_DOCUMENT", "SAME_DOCUMENT_SERIES",
              "SAME_SITE", "SAME_FINDSPOT", "SAME_SCRIBE", "SAME_PHASE", "SAME_SUPPORT_TYPE", "PRECEDES_NUMERAL",
              "FOLLOWS_NUMERAL", "PRECEDES_LOGOGRAM", "FOLLOWS_LOGOGRAM", "ALIGNED_WITH", "QUALIFIES", "TOTALS",
              "SUBTOTALS", "REPEATS_FORM", "VARIANT_OF", "JOINED_WITH", "UNCERTAIN_READING_OF", "COMPOSITE_OF"}

# Any model-visible field name containing one of these is a leakage bug (tests enforce).
FORBIDDEN_FIELD_SUBSTRINGS = ["translit", "phonetic", "sound", "greek", "lemma", "dictionary", "translation",
                              "gloss", "role", "entity", "meaning", "etymolog", "reading", "value_phon"]

# editorial abbreviations that appear lowercased in DĀMOS content but are NOT syllabograms
EDITORIAL_TOKENS = {"vac", "mut", "sup", "inf", "deest", "dext", "sin", "lat", "des", "reliqua", "vestigia",
                    "v", "r", "im", "graffito", "nil", "vestig", "cetera"}
# Damage/uncertainty marks stripped to recover the bare token (their presence sets flags).
_DAMAGE_CHARS = "[]⟦⟧⟨⟩()"
_UNCERTAIN_COMBINING = "̣̱"  # combining dot below / macron below (underdot = uncertain reading)


def sha256_16(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def content_hash(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def strip_marks(tok):
    """Return (bare_token, has_damage, has_uncertain). Removes brackets + combining underdots."""
    import unicodedata
    has_damage = any(ch in tok for ch in _DAMAGE_CHARS)
    nf = unicodedata.normalize("NFD", tok)
    has_uncertain = any(c in _UNCERTAIN_COMBINING for c in nf)
    bare = "".join(c for c in nf if c not in _UNCERTAIN_COMBINING)
    bare = unicodedata.normalize("NFC", "".join(c for c in bare if c not in _DAMAGE_CHARS))
    return bare.strip(":;,/ ").strip(), has_damage, has_uncertain


class OpaqueVocab:
    """Deterministic phonetic-token -> opaque-id map. The map itself is EVALUATION-ONLY (holds the sound)."""
    def __init__(self, prefix):
        self.prefix = prefix
        self._by_tok = {}

    def add(self, tok):
        if tok not in self._by_tok:
            self._by_tok[tok] = None  # id assigned in freeze()

    def freeze(self):
        for i, tok in enumerate(sorted(self._by_tok), 1):
            self._by_tok[tok] = f"{self.prefix}_{i:03d}"
        return self

    def opaque(self, tok):
        return self._by_tok.get(tok)

    def eval_map(self):
        """opaque_id -> original phonetic token (EVALUATION-ONLY key)."""
        return {v: k for k, v in self._by_tok.items()}
