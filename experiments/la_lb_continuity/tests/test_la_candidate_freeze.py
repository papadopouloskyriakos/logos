"""§VII structure / chronology / site-normalization / duplicate-dependence / provenance / regeneration."""
import json, os, sys
import pytest

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "src", "candidate_freeze"))
sys.path.insert(0, os.path.join(HERE, "..", "src", "sigla_reconcile"))
import config  # noqa: E402
import build_la_candidates as B  # noqa: E402

pytestmark = pytest.mark.skipif(not os.path.exists(config.SILVER), reason="silver not present")


@pytest.fixture(scope="module")
def frozen():
    manifest, packet = B.build()
    B.apply_contamination_quarantine(manifest, packet, B.known_la_forms())
    return manifest, packet


def test_set_counts(frozen):
    _, packet = frozen
    from collections import Counter
    inc = Counter(r["inclusion_set"] for r in packet)
    assert inc["PRIMARY"] == 11
    assert inc["SENSITIVITY_1"] == 33
    assert inc["QUARANTINED"] == 1                        # I-DA contamination caught
    assert inc["NEGATIVE_CONTROL"] >= 20


def test_primary_are_toponymlike_tierB(frozen):
    _, packet = frozen
    for r in packet:
        if r["inclusion_set"] == "PRIMARY":
            assert r["classifier_class"] == "TOPONYM_LIKE" and r["tier"] == "B"


def test_raw_ids_and_no_phonetic_in_packet(frozen):
    _, packet = frozen
    for r in packet:
        assert r["raw_sign_ids"] and r["n_signs"] == len(r["raw_sign_ids"])
        for s in r["raw_sign_ids"]:
            assert s.startswith(("AB", "A", "?")), s      # raw sign ids, never lowercase phonetics
        assert "_phonetic_word" not in r


def test_chronology_recorded(frozen):
    _, packet = frozen
    for r in packet:
        assert isinstance(r["chronology"], list) and r["chronology"]


def test_site_normalization_and_ambiguity(frozen):
    _, packet = frozen
    malia = [r for r in packet if r["site_raw"] == "Malia"]
    for r in malia:
        assert r["site_canonical"] == "Mallia"
    ark = [r for r in packet if r["site_raw"] == "Arkhalkhori"]
    for r in ark:
        assert r["site_ambiguity"] is not None            # ARKH cross-source ambiguity surfaced


def test_duplicate_dependence_flagged(frozen):
    _, packet = frozen
    for r in packet:
        cf = r["internal_context"]
        if cf["n_docs"] > 1 and cf["n_sites"] == 1:
            assert "single_site_possible_nonindependence" in r["secondary_flags"]


def test_deterministic_regeneration(frozen):
    manifest, packet = frozen
    m2, p2 = B.build()
    B.apply_contamination_quarantine(m2, p2, B.known_la_forms())
    assert [r["candidate_id"] for r in p2] == [r["candidate_id"] for r in packet]
    assert [r["inclusion_set"] for r in p2] == [r["inclusion_set"] for r in packet]
    assert [r["raw_sign_ids"] for r in p2] == [r["raw_sign_ids"] for r in packet]
