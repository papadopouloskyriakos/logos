"""§VI held-out: known-pair diagnostic (development only, quantifies the drift ceiling), administrative
evaluation = 0, effective-independence bookkeeping."""
import os, sys
import pytest

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "src", "continuity"))
sys.path.insert(0, os.path.join(HERE, "..", "src", "common"))
import cfg  # noqa: E402
import heldout as H  # noqa: E402

pytestmark = pytest.mark.skipif(not os.path.exists(cfg.LA_PACKET), reason="frozen packet absent")


def test_known_pairs_are_development_not_confirmatory():
    d = H.known_pair_diagnostic()
    assert d["n_known"] == 5
    for x in d["rows"]:
        assert "NOT_CONFIRMATORY" in x["label"]


def test_only_two_of_five_are_exact_representable():
    # PA-I-TO and SE-TO-I-JA are exact; TU-RU-SA (drift), I-DA (derived), DI-KI-TA (absent) are not
    d = H.known_pair_diagnostic()
    exact = {x["pair"] for x in d["rows"] if x["representable_exact"]}
    assert exact == {"PA-I-TO", "SE-TO-I-JA"}
    assert d["n_exact_representable"] == 2


def test_administrative_evaluation_is_zero():
    r = H.administrative_evaluation()
    assert all(v == 0 for v in r["primary_x_evaluation"].values())
    assert r["run_once_after_freeze"] is True


def test_effective_independence_by_unique_form():
    r = H.administrative_evaluation()
    ei = r["effective_independence"]
    assert ei["effective_independent_units"] == ei["unique_forms"] == 66


def test_determinism():
    assert H.run() == H.run()
