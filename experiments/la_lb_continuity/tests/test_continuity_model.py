"""§III model correctness: face-validity match, phonetic-specificity control, non-match, determinism,
and the observed primary result. Skips without the frozen packets."""
import os, sys
import pytest

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "src", "continuity"))
sys.path.insert(0, os.path.join(HERE, "..", "src", "common"))
import cfg  # noqa: E402
import model as M  # noqa: E402
import partitions as P  # noqa: E402

pytestmark = pytest.mark.skipif(not os.path.exists(cfg.LA_PACKET), reason="frozen packet absent")

PA_I_TO = {"candidate_id": "T-PA-I-TO", "raw_sign_ids": ["AB03", "AB28", "AB05"],
           "uncertainty": {"composite_sensitive": False, "damaged": False}}


def _tgt(translit):
    return next(t for t in P.load_targets() if t["standard_transliteration"] == translit)


def test_face_validity_pa_i_to_matches_a1_to_a4():
    for L in ("A1", "A2", "A3", "A4"):
        assert M.matches(PA_I_TO, _tgt("pa-i-to"), L) is True


def test_phonetic_specificity_control_a5_breaks_true_pair():
    # wrong projected values (A5) must NOT match a true pair -> phonetic-specificity control is live
    assert M.matches(PA_I_TO, _tgt("pa-i-to"), "A5") is False


def test_true_nonpair_does_not_match():
    assert M.matches(PA_I_TO, _tgt("ku-ta-to"), "A1") is False


def test_layers_are_exactly_a1_to_a5():
    r = M.run("PRIMARY_B", "EVALUATION")
    assert set(r) == {"A1", "A2", "A3", "A4", "A5"}


def test_observed_primary_result_is_zero_matches():
    # documents the mechanical primary finding; a change here flags input/rep drift
    r = M.run("PRIMARY_B", "EVALUATION")
    assert all(r[L]["n_pairs"] == 0 for L in ("A1", "A2", "A3", "A4", "A5"))


def test_determinism():
    assert M.run("PRIMARY_B", "EVALUATION") == M.run("PRIMARY_B", "EVALUATION")
