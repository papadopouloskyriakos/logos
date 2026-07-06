"""§V blindness guarantees: the A↔B equivalence map must be independent of the five known pairs and of
projected phonetic values. Some checks are source-only (always run); map-content checks skip without data."""
import os, re, sys
import pytest

HERE = os.path.dirname(__file__)
SRC = os.path.join(HERE, "..", "src", "ab_equivalence", "build_equivalence.py")
sys.path.insert(0, os.path.join(HERE, "..", "src", "ab_equivalence"))
sys.path.insert(0, os.path.join(HERE, "..", "src", "sigla_reconcile"))
import config  # noqa: E402
import build_equivalence as B  # noqa: E402

PAIR_TOKENS = ["pa-i-to", "tu-ru-sa", "di-ki-ta", "se-to-i-ja",
               "paito", "tylissos", "phaistos", "dikte", "di-de-ru", "pa-je-re"]
_have = all(os.path.exists(p) for p in config.INPUTS.values())


def test_builder_source_reads_no_pair_or_phonetic_source():
    """The builder must import only the sign catalogue + attestation; no phonetic table, no pair ledger."""
    src = open(SRC, encoding="utf-8").read()
    low = src.lower()
    # no known-pair literals anywhere in the builder
    for t in PAIR_TOKENS:
        assert t not in low, f"builder references known pair token {t!r}"
    # no import of a phonetic/value/known-pair module
    assert not re.search(r"import\s+\w*(phonet|syllab|value|pair|toponym)", low)
    # only the SigLA sign catalogue + documents are the data inputs
    assert "config.SIGLA_SIGNS" in src and "config.SIGLA_DOCUMENTS" in src


@pytest.mark.skipif(not _have, reason="SigLA inputs not present")
def test_frozen_map_has_no_pair_tokens():
    import json
    m = B.build()
    blob = json.dumps(m).lower()
    hits = [t for t in PAIR_TOKENS if t in blob]
    assert not hits, f"frozen map contains pair tokens {hits}"


@pytest.mark.skipif(not _have, reason="SigLA inputs not present")
def test_every_row_declares_no_phonetic_no_pair():
    m = B.build()
    for r in m["equivalence"]:
        assert r["phonetic_value_used"] is False
        assert r["target_pair_used_in_selection"] is False
