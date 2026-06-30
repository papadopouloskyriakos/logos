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


def test_partition_is_exact_disjoint_cover():
    index = litindex.load_index()
    signs = ["A", "DA", "KU", "RO", "*118", "*301", "*531", "ZQ_not_a_sign"]
    part = litindex.partition_signs(signs, index)
    known, virgin = part["L_known"], part["L_virgin"]
    assert known.isdisjoint(virgin)
    assert known | virgin == set(signs)
    # the *-series + a nonsense token are all literature-virgin under the seed
    assert {"*118", "*301", "*531", "ZQ_not_a_sign"} <= virgin


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
