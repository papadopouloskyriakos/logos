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
