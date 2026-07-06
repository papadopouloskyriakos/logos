"""§IX circularity verdict is CIRCULARITY_LOW; all load-bearing components LOW; known-pair use and
human exposure are MANAGED and non-load-bearing."""
import os, sys
import pytest

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "src", "continuity"))
import cfg  # noqa: E402
import circularity as X  # noqa: E402

pytestmark = pytest.mark.skipif(not os.path.exists(cfg.LA_PACKET), reason="frozen packet absent")


def test_overall_is_low():
    assert X.verdict()["overall"] == "CIRCULARITY_LOW"


def test_all_load_bearing_components_are_low():
    for c in X.verdict()["components"]:
        if c["load_bearing"]:
            assert c["rating"] == "LOW", c["component"]


def test_known_pair_and_human_exposure_are_nonloadbearing():
    by = {c["component"]: c for c in X.verdict()["components"]}
    assert by["known_pair_use"]["load_bearing"] is False
    assert by["human_review_exposure"]["load_bearing"] is False


def test_determinism():
    assert X.verdict() == X.verdict()
