"""Tests for the Direction-A STRATIFIED morphology re-run (#20).

Checks: (a) genre stratification from the `support` field; (b) the abbreviation-channel exclusion
(seal supports dropped; admin-only list-header strip; votive first-words kept); (c) the per-affix
L_fake bigram floor excludes the bigram-trivial `a-` prefix; (d) the headline grade is the NULL the
discipline expects (no cross-stratum-stable, site-robust morphology); (e) no verdict import.
"""
import ast
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts", "comparison"))
from scripts.comparison import morphology_stratified as MS  # noqa: E402
from scripts.comparison.morphology import Inscription  # noqa: E402


def test_genre_of_maps_support_to_strata():
    assert MS.genre_of("Tablet") == "admin"
    assert MS.genre_of("3-sided bar") == "admin"
    assert MS.genre_of("Nodule") == "seal"
    assert MS.genre_of("Roundel") == "seal"
    assert MS.genre_of("Stone vessel") == "libation"
    assert MS.genre_of("Clay vessel") == "other"
    assert MS.genre_of("") == "other"


def test_strip_abbreviation_seal_dropped_admin_header_only():
    ins = Inscription("x", "HT", [["A", "B"], ["KU", "RO", "SI"], ["DA"]])
    # seal: whole inscription excluded
    assert MS.strip_abbreviation(ins, "seal")[0] is None
    # admin: leading <=3-sign list-header dropped
    stripped, removed = MS.strip_abbreviation(ins, "admin")
    assert removed == 1 and stripped.words[0] == ["KU", "RO", "SI"]
    # libation/other: first word KEPT (dedicatory text, not a list-header)
    kept, removed2 = MS.strip_abbreviation(ins, "libation")
    assert removed2 == 0 and kept.words[0] == ["A", "B"]
    # admin long first word (>3 signs) is NOT a header -> kept
    long_first = Inscription("y", "HT", [["A", "B", "C", "D"], ["E"]])
    k2, r2 = MS.strip_abbreviation(long_first, "admin")
    assert r2 == 0 and k2.words[0] == ["A", "B", "C", "D"]


def test_partitioning_is_deterministic():
    """The seal exclusion + strata sizes are pure partitioning (n_null-independent, deterministic)."""
    recs = MS.load_stratified()
    strata, stats = MS.build_strata(recs, exclude_abbrev=True)
    assert stats["seal_inscriptions_excluded"] == 740      # all Nodule/Roundel/Sealing/Label
    assert len(strata["admin"]) == 290
    assert len(strata["libation"]) == 124
    assert len(strata["other"]) == 104
    # the LM IB single-horizon skew that justifies declining chronological CV
    assert stats["period_distribution"].get("LMIB", 0) > 0.6 * len(recs)


@pytest.mark.parametrize("seed", [0])
def test_stratified_run_is_the_null(seed):
    """Headline grade: no pre-registered affix is cross-stratum stable above the L_fake bigram floor,
    so there is NO validated morphology — the pooled null holds under stratification."""
    res = MS.run_stratified(n_null=60, seed=seed)
    assert res["has_validated_morphology"] is False
    assert res["cross_stratum"]["cross_stratum_stable"] == {}
    assert res["cross_stratum"]["morphology_validated"] == {}
    # the per-affix bigram floor must exclude the bigram-trivial `a-` prefix (commonest word-initial
    # sign) from EVERY stratum's morphology set — it confirms in L_fake too, so it is not morphology.
    for name in MS.INDUCTION_STRATA:
        assert "a-" not in (res["per_stratum"][name].get("morphology_affixes") or []), name


def test_imports_no_verdict():
    src = open(os.path.join(os.path.dirname(__file__), "..", "scripts", "comparison",
                            "morphology_stratified.py"), encoding="utf-8").read()
    tree = ast.parse(src)
    bad = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and "verdict" in node.module:
            bad.append(node.module)
        if isinstance(node, ast.Import):
            bad += [a.name for a in node.names if "verdict" in a.name]
    assert not bad, f"stratified morphology must not import verdict; found {bad}"
