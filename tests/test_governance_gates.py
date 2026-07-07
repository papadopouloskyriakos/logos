"""Art. XVIII assumption gate + Art. XV licence gate + Art. XXII stage header — regression lock."""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts import assumption_gate as ag  # noqa: E402
from scripts import licence_gate as lg  # noqa: E402
from scripts import stage_header as sh  # noqa: E402


# ---- Art. XVIII assumption gate ----

def test_false_load_bearing_assumptions_are_blocking():
    blk = ag.blocking()
    # A04 (source independence), A09 (CSA serial) are FALSE + load-bearing
    assert "A04" in blk and "A09" in blk


def test_require_blocks_on_false_assumption():
    with pytest.raises(RuntimeError):
        ag.require(["A04"])                     # source-independence FALSE -> blocked
    assert ag.require(["A01", "A06"]) is True   # VERIFIED premises -> pass


def test_unknown_assumption_fails_loud():
    with pytest.raises(KeyError):
        ag.check(["A99"])


def test_partial_load_bearing_assumption_blocks():
    """Art. XVIII 'verified': a PARTIAL load-bearing premise (A03) is NOT affirmatively verified -> blocks."""
    assert "A03" in ag.blocking()
    with pytest.raises(RuntimeError):
        ag.require(["A03"])


# ---- Art. XV licence gate ----

def test_linear_a_functional_output_blocked_without_licence():
    r = lg.check_claim("L3", "SUPPORTED", linear_a=True)
    assert r["allowed"] is False and "FUNCTIONAL" in r["licence"]


def test_confidence_capped_at_supported_without_licence():
    # L2 structural, not LA-blocked outright, but confidence above SUPPORTED needs the (unearned) licence
    r = lg.check_claim("L2", "REPLICATED", linear_a=False)
    assert r["allowed"] is False and r["max_confidence"] == "SUPPORTED"
    assert lg.check_claim("L2", "SUPPORTED", linear_a=False)["allowed"] is True


def test_l0_l1_observation_needs_no_licence():
    assert lg.check_claim("L1", "ACCEPTED")["allowed"] is True


def test_licence_gate_fails_closed_on_layer_typo():
    """A whitespace/case/out-of-range layer must NOT slip past the gate (the critical review finding)."""
    assert lg.check_claim("L4 ", "ACCEPTED")["allowed"] is False    # normalizes to L4 -> SEMANTIC block
    assert lg.check_claim("l4", "ACCEPTED")["allowed"] is False
    assert lg.check_claim("L10", "ACCEPTED")["allowed"] is False    # out of range -> fail closed
    assert lg.check_claim("banana", "ACCEPTED")["allowed"] is False


def test_licence_gate_fails_closed_on_unknown_confidence():
    r = lg.check_claim("L2", "REPLICATED_PLUS", linear_a=False)     # L2 not LA-blocked, but bad confidence
    assert r["allowed"] is False and "unrecognized confidence" in r["reason"]


# ---- Art. XXII stage header ----

def test_valid_header_passes():
    h = sh.open_header("s", ["V", "VIII"], ["XIII"], ["gate"], ["A06"], ["out"], ["forbidden"])
    assert sh.validate(h) == []


def test_header_flags_bad_article_and_false_assumption():
    h = sh.open_header("s", ["V", "XXV"], ["XIII"], ["gate"], ["A04"], ["out"], ["forbidden"])
    problems = sh.validate(h)
    assert any("XXV" in p for p in problems)          # invalid article
    assert any("A04" in p for p in problems)          # FALSE assumption blocks (Art. XVIII)


def test_header_missing_field():
    assert any("missing" in p for p in sh.validate({"stage": "s"}))


def test_validate_close_requires_compliance():
    assert sh.validate_close(sh.close_block("COMPLIANT")) == []
    assert sh.validate_close(sh.close_block("")) != []        # empty compliance -> flagged
    assert sh.validate_close(None) != []                      # missing close block -> flagged
