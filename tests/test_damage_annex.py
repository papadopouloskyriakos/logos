"""Locked properties of the D1 damage annex (scripts/audit_damage_markers.py):

(a) pure damage-flag semantics (no data needed): leading/trailing/internal U+1076B
    detection and the compact LTI code;
(b) SILVER BYTE-IDENTITY GUARD: the two silver files carry their pinned sha256 —
    the annex is a sidecar; any silver rebuild must be an explicit, recorded decision
    (standing rule; docs/2026-08-05-tsirkas-full-repo-audit.md §2);
(c) annex regression: the script-generated summary reproduces the pinned D1 numbers
    (3,147 word tokens / 911 damage-touching / 1,165 types / 359 phantom) and the
    silver doc-id cross-check is MATCH with zero misaligned silver docs;
(d) determinism: two builds serialize byte-identically;
(e) mechanism: no silver word token's transliterated signs contain the marker
    (word-attached damage exists only in the Unicode layer — the D1 stripping).

Data-dependent tests are licensed_data-marked AND runtime-skipped when the gitignored
bronze/silver are absent (house pattern).
"""
import hashlib
import json
import os
import sys

import pytest

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from scripts import audit_damage_markers as adm  # noqa: E402

SILVER_FLAT = os.path.join(_REPO_ROOT, "corpus", "silver", "inscriptions.json")
SILVER_STRUCT = os.path.join(_REPO_ROOT, "corpus", "silver", "inscriptions_structured.json")

# Pinned 2026-08-05 (the snapshot the paper-era analyses and the D1 audit ran on).
SILVER_FLAT_SHA = "4717a7e39157fad6b4a4d24e0d925f1c8a0cd33d6e7111b6822222aa24f1244a"
SILVER_STRUCT_SHA = "aaee1aeb5b186fa0e4d9d0adc71026e6786d47328b9ecee5236380756462b500"

_have_data = os.path.exists(adm.BRONZE) and os.path.exists(SILVER_STRUCT)
needs_data = pytest.mark.skipif(not _have_data, reason="gitignored bronze/silver not present")

M = adm.MARKER


class TestFlagSemantics:
    def test_leading(self):
        assert adm.code(adm.damage_flags(M + "\U00010600")) == "L"

    def test_trailing(self):
        assert adm.code(adm.damage_flags("\U00010600" + M)) == "T"

    def test_internal(self):
        assert adm.code(adm.damage_flags("\U00010600" + M + "\U00010601")) == "I"

    def test_both_edges_and_internal(self):
        tok = M + "\U00010600" + M + "\U00010601" + M
        assert adm.code(adm.damage_flags(tok)) == "LTI"

    def test_clean(self):
        assert adm.code(adm.damage_flags("\U00010600\U00010601")) == ""


@pytest.mark.licensed_data
@needs_data
class TestSilverByteIdentity:
    def test_flat_silver_pinned(self):
        h = hashlib.sha256(open(SILVER_FLAT, "rb").read()).hexdigest()
        assert h == SILVER_FLAT_SHA, (
            "silver inscriptions.json changed — a silver rebuild requires an explicit "
            "recorded decision (D4/D1 standing rule); if intended, re-pin here AND record it")

    def test_structured_silver_pinned(self):
        h = hashlib.sha256(open(SILVER_STRUCT, "rb").read()).hexdigest()
        assert h == SILVER_STRUCT_SHA, (
            "silver inscriptions_structured.json changed — see test_flat_silver_pinned")


@pytest.mark.licensed_data
@needs_data
class TestAnnexRegression:
    @pytest.fixture(scope="class")
    def built(self):
        per_doc, misaligned = adm.build_annex(adm.BRONZE)
        return per_doc, misaligned, adm.summarize(per_doc)

    def test_pinned_d1_numbers(self, built):
        _, _, s = built
        assert s["docs"] == 1341
        assert s["word_tokens"] == 3147
        assert s["damage_touching_tokens"] == 911
        assert s["distinct_types"] == 1165
        assert s["phantom_types"] == 359
        assert s["types_excluding_phantoms"] == 806

    def test_no_misaligned_silver_docs(self, built):
        _, misaligned, _ = built
        assert misaligned == []

    def test_silver_cross_check_match(self, built):
        per_doc, _, _ = built
        check = adm.cross_check_silver(per_doc)
        assert check["checked"] and check["match"]

    def test_determinism(self, built):
        per_doc, _, _ = built
        again, _ = adm.build_annex(adm.BRONZE)
        a = json.dumps(per_doc, sort_keys=True, ensure_ascii=False)
        b = json.dumps(again, sort_keys=True, ensure_ascii=False)
        assert a == b

    def test_marker_absent_from_word_signs(self, built):
        per_doc, _, _ = built
        for d in per_doc.values():
            for ty in d["types"]:
                assert M not in ty, "word-attached marker leaked into transliterated signs"
