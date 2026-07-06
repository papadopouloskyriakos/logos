"""§V structural invariants for the frozen A↔B equivalence map."""
import os, sys
import pytest

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "src", "ab_equivalence"))
sys.path.insert(0, os.path.join(HERE, "..", "src", "sigla_reconcile"))
import config  # noqa: E402
import build_equivalence as B  # noqa: E402

pytestmark = pytest.mark.skipif(not all(os.path.exists(p) for p in config.INPUTS.values()),
                                reason="SigLA inputs not present")


@pytest.fixture(scope="module")
def m():
    return B.build()


def test_partition(m):
    rows = m["equivalence"]
    tierA = [r for r in rows if r["confidence_tier"] == "A"]
    tierX = [r for r in rows if r["confidence_tier"] == "X"]
    assert len(rows) == 376
    assert len(tierA) == 77 and len(tierX) == 299
    assert len(tierA) + len(tierX) == len(rows)          # A and X exhaust the repertoire here


def test_tierA_rows_are_level1_homomorphs(m):
    for r in (r for r in m["equivalence"] if r["confidence_tier"] == "A"):
        assert r["la_sign_id"].startswith("AB")
        assert r["lb_sign_id"] == f"*{r['gorila_number']:02d}"
        assert r["equivalence_level"] == "LEVEL_1"
        assert r["disputed_flag"] is False


def test_tierX_has_no_lb_equivalent(m):
    for r in (r for r in m["equivalence"] if r["confidence_tier"] == "X"):
        assert r["lb_sign_id"] is None and r["equivalence_level"] is None


def test_high_attestation_is_subset_of_tierA(m):
    hi = [r for r in m["equivalence"] if r["high_attestation"]]
    assert hi, "expected a non-empty high-attestation robustness subset"
    for r in hi:
        assert r["confidence_tier"] == "A"
        assert r["la_attestation"] >= m["meta"]["high_attestation_threshold"]


def test_determinism(m):
    assert B.build() == m
