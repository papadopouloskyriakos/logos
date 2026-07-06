"""§VII power: full power for exact continuity, zero for genuine drift, transcription-uncertainty
recovered by A3, realistic P(NO_POWER). Skips without frozen packets."""
import os, sys
import pytest

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "src", "continuity"))
sys.path.insert(0, os.path.join(HERE, "..", "src", "common"))
import cfg  # noqa: E402
import power as W  # noqa: E402

pytestmark = pytest.mark.skipif(not os.path.exists(cfg.LA_PACKET), reason="frozen packet absent")


@pytest.fixture(scope="module")
def r():
    return W.run()


def test_full_power_for_exact_continuity(r):
    ex = r["summary"]["exact_continuity"]
    assert ex["min_detectable_pairs"] == 1 and ex["detected_at_1"] is True


def test_zero_power_for_genuine_drift(r):
    assert r["summary"]["genuine_drift_1"]["A1_detected"] is False
    assert r["summary"]["genuine_drift_1"]["A3_detected"] is False    # genuine drift is unflagged
    assert r["summary"]["genuine_drift_2"]["A3_detected"] is False


def test_transcription_uncertainty_recovered_by_a3(r):
    assert r["summary"]["transcription_uncertainty_1"]["A3_detected"] is True


def test_realistic_no_power_probability(r):
    assert r["summary"]["prob_no_power_realistic"] == 0.6         # ~60% of known continuities drift
    assert r["summary"]["min_detectable_pairs_drifted"] is None


def test_determinism(r):
    assert W.run()["summary"] == r["summary"]
