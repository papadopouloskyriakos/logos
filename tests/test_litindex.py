"""Tests for the §C.1 literature index + §C.2 L_known/L_virgin partition (scripts/comparison/litindex).

These lock in the four properties the decontamination mechanism depends on:
  (a) partition correctness — a seeded sign lands in L_known, an unlisted *-series sign in L_virgin,
      and the two sets partition the input exactly;
  (b) virgin_support isolates the L_virgin contribution (and its honest no-power 0.0);
  (c) loader determinism (default seed is a pure function; JSON round-trips byte-stably);
  (d) seed integrity — every seed claim carries a non-empty source + a positive year.

Run from anywhere:
    python3 -m pytest tests/test_litindex.py -q
"""
import os
import sys

import pytest

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from scripts.comparison import litindex  # noqa: E402


# --------------------------------------------------------------------------- #
# (a) PARTITION CORRECTNESS — §C.2
# --------------------------------------------------------------------------- #
def test_seeded_sign_is_known_unlisted_sign_is_virgin():
    index = litindex.load_index()
    # "DA" is a seeded Linear-B-value transfer; "*118" is a *-series sign with no published value.
    part = litindex.partition_signs(["DA", "*118"], index)
    assert "DA" in part["L_known"]
    assert "*118" in part["L_virgin"]
    assert "*118" not in part["L_known"]
    assert "DA" not in part["L_virgin"]


def test_verified_semitic_proposals_present_and_unverified_omitted():
    """Locks the 2026-06-30 integrity decisions: the SIX independently-verified West-Semitic proposals
    are indexed; the two that FAILED corroboration (qa-pa=kappu, a Semitic ki-ro) are NOT — a wrong
    attribution in a DECONTAMINATION index is worse than a gap."""
    index = litindex.load_index()
    sem = {c.sign: c for c in index if c.claim_type == "semitic_proposal"}
    # the six independently-verified Gordon/Best claims, with their verified consonantal-cognate values
    verified = {"SU-PU", "KA-RO-PA", "SU-PA-RA", "KU-RO", "JA-NE", "A-SA-SA-RA-ME"}
    assert verified <= set(sem)
    assert sem["SU-PU"].proposed_value == "sp"
    assert sem["KA-RO-PA"].proposed_value == "krpn"     # Ugaritic krpn, NOT "Akkadian karpu" (corrected)
    assert sem["SU-PA-RA"].proposed_value == "spl"
    assert sem["KU-RO"].proposed_value == "kull"
    assert sem["JA-NE"].proposed_value == "yn"          # keyed JA (corpus convention), Gordon's "ya-ne"
    assert sem["A-SA-SA-RA-ME"].proposed_value == "asherah"
    # a-sa-sa-ra-me is Best (1981), NOT Gordon — the verification caught the attribution drift
    assert "Best" in sem["A-SA-SA-RA-ME"].source and sem["A-SA-SA-RA-ME"].year == 1981
    # *301 = Di Mino's DISPUTED/unverified quarantine anchor (NOT one of the 6 verified) — present + flagged,
    # and quarantining it makes *301 L_known so it can never sit in an L_virgin discovery set.
    assert sem["*301"].proposed_value == "na" and "Di Mino" in sem["*301"].source and sem["*301"].year == 2026
    assert "*301" in litindex.known_signs(index)
    assert all(c.year == 1966 and "Gordon" in c.source
               for k, c in sem.items() if k not in {"A-SA-SA-RA-ME", "*301"})
    # OMITTED (unverifiable) — no semitic_proposal for qa-pa, and ki-ro has only its accounting reading
    assert "QA-PA" not in sem
    assert not any(c.sign == "KI-RO" and c.claim_type == "semitic_proposal" for c in index)
    assert any(c.sign == "KI-RO" and c.claim_type == "lexical_reading" for c in index)  # accounting term stays


def test_spice_logographic_readings_quarantine_l_virgin_leak():
    """Audit 2026-06-30: the PUBLIC 2025 Salgarella/Bellinato/Ferrara spice readings must be indexed so
    a model cannot regurgitate them as an L_virgin 'discovery' — they go to L_known, flagged speculative."""
    index = litindex.load_index()
    logo = {c.sign: c for c in index if c.claim_type == "logographic_reading"}
    assert {"A646", "A341", "*127", "*157"} <= set(logo)
    assert logo["A646"].proposed_value == "root" and logo["*127"].proposed_value == "spice"
    assert all(c.year == 2025 and ("Salgarella" in c.source or "Kadmos" in c.source) for c in logo.values())
    # the hedging the paper itself carries must be recorded (so logos never presents them as confirmed)
    assert "hapax" in logo["A646"].note.lower() and "speculative" in logo["A646"].note.lower()
    # the whole point: these signs are now L_known, never L_virgin
    known = litindex.known_signs(index)
    assert {"A646", "A341", "*127", "*157"} <= known
    part = litindex.partition_signs(["A646", "*127", "*999"], index)
    assert "A646" in part["L_known"] and "*127" in part["L_known"]
    assert "*999" in part["L_virgin"]


def test_structural_readings_indexed_as_l_known():
    """2026-07-01: Davis/Salgarella STRUCTURAL readings (no phonetic value) are indexed so a model
    cannot regurgitate the morphology as discovery — i-*301='gives/dedicates' + the §8 affix set."""
    index = litindex.load_index()
    st = {c.sign: c for c in index if c.claim_type == "structural_reading"}
    assert {"I-*301", "-TE", "-TI", "I-", "J-", "-JA", "-RU", "-RE", "-A"} <= set(st)
    assert "gives/dedicates" in st["I-*301"].proposed_value
    assert "Davis" in st["I-*301"].source and "Salgarella" in st["I-*301"].source
    assert "Salgarella 2025 §7.2" in st["I-*301"].note
    # the §8 affix attributions are preserved (so logos cites the primary source, not just Salgarella)
    assert "Valerio" in st["-TE"].source and "Duhoux" in st["I-"].source
    assert "Younger" in st["-JA"].source and "Steele" in st["-RU"].source and "Meissner" in st["-RU"].source
    # these are STRUCTURAL (no phonetic value) — the value names a function, never a sound
    assert st["I-*301"].proposed_value.startswith(("verb", "object", "suffix", "prefix"))


def test_dimino_star301_three_part_refutation():
    """2026-07-01 field intel: the *301 quarantine carries the three-part self-refutation, incl. the
    strongest point — his own agglutinative segmentation contradicts the Semitic family he assigns."""
    cit = litindex.CITATION_DIMINO
    assert "SEGMENTATION NOT NOVEL" in cit and "ta-na-i-*301-u-ti-nu" in cit
    assert "GLOSS CONTESTED" in cit and "give/dedicate" in cit
    assert "MORPHOLOGY CONTRADICTS" in cit and "AGGLUTINATIVE" in cit and "OPPOSITE of Semitic" in cit
    assert "ISOLATE" in cit and "Salgarella 2025" in cit
    assert "no cross-script anchor" in cit and "free-parameter" in cit
    assert "do NOT re-attribute to Steele 2024" in cit


def test_dimino_attribution_keeps_davis_not_steele():
    """The i-*301='give/dedicate' counter is DAVIS's (Kadmos 52, 2013), endorsed by Salgarella 2025 §7.2.
    The Steele-2024 item in hand is a Dickinson review with no *301 gloss, so it must NOT be cited for it;
    Salgarella 2025 §8 does not mention *301 but concludes ISOLATE + rejects the Semitic-etymology method."""
    cit = litindex.CITATION_DIMINO
    assert "Davis" in cit and "Salgarella 2025 §7.2" in cit
    assert "do NOT re-attribute to Steele 2024" in cit
    assert "Semitic-ETYMOLOGY method" in cit


def test_partition_is_exact_disjoint_cover():
    index = litindex.load_index()
    signs = ["A", "DA", "KU", "RO", "*118", "*301", "*531", "ZQ_not_a_sign"]
    part = litindex.partition_signs(signs, index)
    known, virgin = part["L_known"], part["L_virgin"]
    assert known.isdisjoint(virgin)
    assert known | virgin == set(signs)
    # *301 now carries Di Mino's DISPUTED published reading -> it is QUARANTINED (L_known), never virgin
    assert "*301" in known
    # the remaining *-series + a nonsense token have no published proposal -> literature-virgin
    assert {"*118", "*531", "ZQ_not_a_sign"} <= virgin


def test_sequence_reading_marks_component_signs_known():
    """KU-RO ('total') is an indexed sequence reading; both component signs are literature-touched."""
    index = litindex.load_index()
    part = litindex.partition_signs(["KU", "RO", "KI"], index)
    assert {"KU", "RO", "KI"} <= part["L_known"]


def test_index_signs_absent_from_inventory_are_ignored():
    # A sign referenced by the index but not in all_signs must not appear in either output set.
    index = litindex.load_index()
    part = litindex.partition_signs(["*118"], index)
    assert part["L_known"] == set()
    assert part["L_virgin"] == {"*118"}


def test_literature_match_quarantine_helper():
    index = litindex.load_index()
    assert litindex.literature_match("DA", index) is True
    assert litindex.literature_match("DA", index, proposed_value="da") is True
    assert litindex.literature_match("DA", index, proposed_value="xy") is False   # wrong value
    assert litindex.literature_match("*118", index) is False                      # virgin sign
    # a candidate that proposes the published KU-RO sequence reading is a literature_match
    assert litindex.literature_match("KU-RO", index, proposed_value="total") is True


# --------------------------------------------------------------------------- #
# (b) VIRGIN_SUPPORT — §E generalization clause
# --------------------------------------------------------------------------- #
def test_virgin_support_isolates_virgin_contribution():
    part = {"L_known": {"DA", "KU"}, "L_virgin": {"*118", "*301"}}
    # 3 units of support on known signs, 1 on a virgin sign -> 1/4 of the mass is virgin
    support = {"DA": 2.0, "KU": 1.0, "*118": 1.0}
    assert litindex.virgin_support(support, part) == pytest.approx(0.25)
    # all support on virgin signs -> fraction 1.0
    assert litindex.virgin_support({"*118": 3.0, "*301": 1.0}, part) == pytest.approx(1.0)
    # all support on known signs -> fraction 0.0 (concentrated on already-published values)
    assert litindex.virgin_support({"DA": 5.0}, part) == pytest.approx(0.0)


def test_virgin_support_ignores_unclassified_signs():
    part = {"L_known": {"DA"}, "L_virgin": {"*118"}}
    # "ZZ" is in neither set; it must not enter numerator OR denominator
    support = {"*118": 1.0, "DA": 1.0, "ZZ": 100.0}
    assert litindex.virgin_support(support, part) == pytest.approx(0.5)


def test_virgin_support_degenerate_returns_honest_zero():
    part = {"L_known": {"DA"}, "L_virgin": {"*118"}}
    # empty mapping -> no power -> 0.0
    assert litindex.virgin_support({}, part) == 0.0
    # all-zero / non-positive support -> no power -> 0.0 (NOT a real generalization-failure null)
    assert litindex.virgin_support({"*118": 0.0, "DA": 0.0}, part) == 0.0
    assert litindex.virgin_support({"*118": -3.0}, part) == 0.0
    # support only on unclassified signs -> no classified mass -> 0.0
    assert litindex.virgin_support({"ZZ": 9.0}, part) == 0.0


# --------------------------------------------------------------------------- #
# (c) LOADER DETERMINISM
# --------------------------------------------------------------------------- #
def test_load_index_default_is_deterministic_and_pure():
    a = litindex.load_index()
    b = litindex.load_index()
    assert a == b                                   # value-equal across calls
    assert a is not b                               # but a fresh list (no shared mutable state)
    assert a is not litindex.SEED_CLAIMS            # default returns a copy, not the module list


def test_load_index_default_order_is_stable():
    a = litindex.load_index()
    keys = [(c.claim_type, c.sign) for c in a]
    assert keys == sorted(keys)                     # deterministic (claim_type, sign) order


def test_json_roundtrip_is_stable(tmp_path):
    index = litindex.load_index()
    p = os.path.join(str(tmp_path), "idx.json")
    litindex.dump_index(index, p)
    reloaded = litindex.load_index(p)
    assert reloaded == index
    # and re-dumping the reloaded index produces byte-identical JSON
    p2 = os.path.join(str(tmp_path), "idx2.json")
    litindex.dump_index(reloaded, p2)
    with open(p, "rb") as f1, open(p2, "rb") as f2:
        assert f1.read() == f2.read()


# --------------------------------------------------------------------------- #
# (d) SEED INTEGRITY
# --------------------------------------------------------------------------- #
def test_seed_is_nonempty_and_flagged_nonexhaustive():
    index = litindex.load_index()
    assert len(index) > 0
    assert litindex.SEED_NONEXHAUSTIVE is True
    assert "NON-EXHAUSTIVE" in litindex.SEED_NOTE.upper()


def test_every_seed_claim_has_source_and_year():
    for c in litindex.load_index():
        assert isinstance(c.source, str) and c.source.strip(), c
        assert isinstance(c.year, int) and c.year > 0, c
        assert isinstance(c.proposed_value, str) and c.proposed_value.strip(), c
        assert isinstance(c.sign, str) and c.sign.strip(), c
        assert isinstance(c.claim_type, str) and c.claim_type.strip(), c


def test_lb_transfer_value_equals_romanized_name():
    # the LB-transfer claims encode value == lowercased GORILA sign-name (the transferred value)
    for c in litindex.load_index():
        if c.claim_type == "lb_value_transfer":
            assert c.proposed_value == c.sign.lower(), c


def test_claim_is_frozen():
    c = litindex.load_index()[0]
    with pytest.raises(Exception):
        c.sign = "mutated"           # frozen dataclass -> immutable index entries
