"""Tests for scripts/comparison/searchlog.py — the N_eff instrumentation (design §B.2).

These lock the properties N_eff's honesty depends on: a duplicate triple is counted ONCE
(invariant 6 — replays/retries idempotent), distinct triples each count, the assignment key is
order-independent (and the segmentation key is input-shape-independent) so the same candidate
reached two ways collapses to one identity, the sanity bound is the documented product, and the
over-bound flag fires exactly when a logged n_eff exceeds the bound (an under-specified bound or a
canonicalization bug). Pure, deterministic.

Run from anywhere:
    python3 -m pytest tests/test_searchlog.py -q
"""
import os
import sys

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from scripts.comparison import searchlog  # noqa: E402


# --------------------------------------------------------------------------- #
# (a) duplicate triples counted once
# --------------------------------------------------------------------------- #
def test_exact_duplicate_counted_once():
    log = searchlog.SearchLog()
    assert log.log_candidate({"*301": "na"}, "nawaya", "na-wa-ya") is True
    # exact replay (a crashed-retry / re-score) — must be a no-op for n_eff
    assert log.log_candidate({"*301": "na"}, "nawaya", "na-wa-ya") is False
    assert log.log_candidate({"*301": "na"}, "nawaya", "na-wa-ya") is False
    assert log.n_eff == 1
    assert log.n_logged == 3          # gross count still records every call


# --------------------------------------------------------------------------- #
# (b) distinct triples each counted
# --------------------------------------------------------------------------- #
def test_distinct_triples_each_counted():
    log = searchlog.SearchLog()
    log.log_candidate({"*301": "na"}, "nawaya", "na-wa-ya")     # base
    log.log_candidate({"*301": "da"}, "nawaya", "na-wa-ya")     # different value
    log.log_candidate({"*301": "na"}, "kuro", "na-wa-ya")       # different lexeme
    log.log_candidate({"*301": "na"}, "nawaya", "naw-aya")      # different segmentation
    log.log_candidate({"*301": "na", "*311": "ki"}, "nawaya", "na-wa-ya")  # different assignment
    assert log.n_eff == 5
    assert log.n_logged == 5
    assert len(log) == 5


def test_distinct_differ_in_exactly_one_coordinate():
    """Two triples differing in only one of the three coordinates are still distinct."""
    log = searchlog.SearchLog()
    log.log_candidate({"*301": "na"}, "abd", "a-bd")
    log.log_candidate({"*301": "na"}, "abd", "ab-d")   # only segmentation differs
    assert log.n_eff == 2


# --------------------------------------------------------------------------- #
# (c) order-independence of the canonical assignment key (and segmentation shape)
# --------------------------------------------------------------------------- #
def test_assignment_key_order_independent():
    a = searchlog.canonical_assignment({"*301": "na", "*311": "ki", "*008": "a"})
    b = searchlog.canonical_assignment({"*008": "a", "*311": "ki", "*301": "na"})
    c = searchlog.canonical_assignment([("*311", "ki"), ("*008", "a"), ("*301", "na")])
    assert a == b == c


def test_reordered_assignment_dedups():
    log = searchlog.SearchLog()
    assert log.log_candidate({"*301": "na", "*311": "ki"}, "nakim", "na-kim") is True
    # same map, written in the opposite order, reached by another query path -> SAME identity
    assert log.log_candidate({"*311": "ki", "*301": "na"}, "nakim", "na-kim") is False
    # same map via list-of-pairs -> still the same identity
    assert log.log_candidate([("*311", "ki"), ("*301", "na")], "nakim", "na-kim") is False
    assert log.n_eff == 1


def test_segmentation_string_vs_sequence_dedups():
    log = searchlog.SearchLog()
    assert log.log_candidate({"*301": "na"}, "nawaya", "na\x1fwa\x1fya") is True
    # the same segmentation supplied as a list of segments must collapse to the same identity
    assert log.log_candidate({"*301": "na"}, "nawaya", ["na", "wa", "ya"]) is False
    assert log.n_eff == 1


def test_segmentation_distinct_when_boundaries_differ():
    """Same characters, different boundaries -> genuinely distinct candidates."""
    log = searchlog.SearchLog()
    log.log_candidate({"*301": "na"}, "nawaya", ["na", "wa", "ya"])
    log.log_candidate({"*301": "na"}, "nawaya", ["naw", "aya"])
    assert log.n_eff == 2


def test_sign_id_stringified_consistently():
    """An int sign id and its string form denote the same sign -> one identity."""
    log = searchlog.SearchLog()
    log.log_candidate({301: "na"}, "nawaya", "na-wa-ya")
    assert log.log_candidate({"301": "na"}, "nawaya", "na-wa-ya") is False
    assert log.n_eff == 1


# --------------------------------------------------------------------------- #
# (d) sanity bound arithmetic
# --------------------------------------------------------------------------- #
def test_sanity_bound_product():
    # S_unknown * V_branch * R_L * F * G_seg
    assert searchlog.sanity_upper_bound(90, 60, 2000, 5, 3) == 90 * 60 * 2000 * 5 * 3
    assert searchlog.sanity_upper_bound(2, 2, 2, 1, 2) == 16
    assert searchlog.sanity_upper_bound(1, 1, 1, 1, 1) == 1


def test_sanity_bound_degenerate_zero():
    # any factor <= 0 -> empty search space -> honest 0 (not a misleading positive)
    assert searchlog.sanity_upper_bound(0, 60, 2000, 5, 3) == 0
    assert searchlog.sanity_upper_bound(90, 0, 2000, 5, 3) == 0
    assert searchlog.sanity_upper_bound(90, 60, 2000, 5, 0) == 0
    assert searchlog.sanity_upper_bound(-1, 60, 2000, 5, 3) == 0


# --------------------------------------------------------------------------- #
# (e) over-bound flag fires when n_eff exceeds the bound
# --------------------------------------------------------------------------- #
def test_over_bound_flag_fires_when_exceeded():
    assert searchlog.over_bound_flag(17, 16) is True       # n_eff > bound -> bug/under-specified
    assert searchlog.over_bound_flag(16, 16) is False      # equal is admissible (space full)
    assert searchlog.over_bound_flag(5, 16) is False       # under-full is fine


def test_over_bound_flag_against_degenerate_bound():
    # a degenerate (0) bound with ANY logged candidate is an over-bound by construction
    assert searchlog.over_bound_flag(1, 0) is True
    assert searchlog.over_bound_flag(0, 0) is False


def test_check_bound_reports_fill_ratio_and_flag():
    log = searchlog.SearchLog()
    log.log_candidate({"*301": "na"}, "nawaya", "na-wa-ya")
    log.log_candidate({"*301": "da"}, "nawaya", "na-wa-ya")
    info = searchlog.check_bound(log, s_unknown=2, v_branch=2, r_l=2, f=1, g_seg=2)
    assert info["n_eff"] == 2
    assert info["bound"] == 16                      # atomic product reference scale, unchanged
    assert info["over_bound"] is False              # per-dimension: nothing exceeds its cap
    assert info["fill_ratio"] == 2 / 16
    pd = info["per_dimension"]
    assert pd["pairs"]["observed"] == 2 and pd["pairs"]["cap"] == 4    # {(*301,na),(*301,da)} <= S*V
    assert pd["signs"]["observed"] == 1 and pd["lexemes"]["observed"] == 1


def test_check_bound_joint_map_is_not_a_false_over_bound():
    """Regression (verifier-found): logging every distinct full MAP over a tiny free-sign set must NOT
    trip over_bound. Comparing the joint n_eff to the per-pair product (the original defect) flagged
    this honest log as a dedup bug; the per-dimension check (distinct pairs <= S*V) does not."""
    log = searchlog.SearchLog()
    signs = ["*1", "*2", "*3"]
    for bits in range(8):                                   # all 2^3 = 8 full {a,b} assignments
        amap = {s: ("a" if (bits >> i) & 1 else "b") for i, s in enumerate(signs)}
        log.log_candidate(amap, "lex", "seg")
    info = searchlog.check_bound(log, s_unknown=3, v_branch=2, r_l=1, f=1, g_seg=1)
    assert info["n_eff"] == 8                                # 8 distinct joint maps, honestly logged
    assert info["per_dimension"]["pairs"]["observed"] == 6   # only 6 distinct (sign,value) pairs
    assert info["per_dimension"]["pairs"]["cap"] == 6        # = S*V = 3*2
    assert info["over_bound"] is False                       # the fix: no false positive


def test_check_bound_over_bound_fires_on_real_excess():
    """A genuinely over-specified search (more distinct pairs than S*V allows) DOES fire."""
    log = searchlog.SearchLog()
    for s, v in [("*1", "a"), ("*1", "b"), ("*2", "a")]:    # 3 distinct pairs over 2 signs, 1 value cap
        log.log_candidate({s: v}, "lex", "seg")
    info = searchlog.check_bound(log, s_unknown=2, v_branch=1, r_l=1, f=1, g_seg=1)  # cap pairs = 2
    assert info["per_dimension"]["pairs"]["observed"] == 3 and info["per_dimension"]["pairs"]["cap"] == 2
    assert info["over_bound"] is True


def test_check_bound_degenerate_fill_ratio_is_none():
    info = searchlog.check_bound(searchlog.SearchLog(), s_unknown=0, v_branch=2, r_l=2, f=1, g_seg=2)
    assert info["bound"] == 0
    assert info["fill_ratio"] is None
    assert info["over_bound"] is False


# --------------------------------------------------------------------------- #
# Determinism + ordering of the distinct candidate list
# --------------------------------------------------------------------------- #
def test_candidates_first_seen_order_deterministic():
    log = searchlog.SearchLog()
    log.log_candidate({"*301": "na"}, "b", "b")
    log.log_candidate({"*301": "na"}, "a", "a")
    log.log_candidate({"*301": "na"}, "b", "b")   # dup, must not reappear
    log.log_candidate({"*301": "na"}, "c", "c")
    lexemes = [k[1] for k in log.candidates()]
    assert lexemes == ["b", "a", "c"]             # first-seen order, dedup preserved


def test_contains_uses_canonical_key():
    log = searchlog.SearchLog()
    log.log_candidate({"*301": "na", "*311": "ki"}, "nakim", ["na", "kim"])
    # canonical key from a reordered map + the \x1f-joined form of the SAME segmentation
    key = searchlog.candidate_key({"*311": "ki", "*301": "na"}, "nakim", "na\x1fkim")
    assert key in log


# --------------------------------------------------------------------------- #
# Empty / degenerate log
# --------------------------------------------------------------------------- #
def test_empty_log_is_zero():
    log = searchlog.SearchLog()
    assert log.n_eff == 0
    assert log.n_logged == 0
    assert log.candidates() == []


def test_main_demo_runs():
    assert searchlog.main([]) == 0
    assert searchlog.main(["--json"]) == 0
