"""§XII final feasibility verdict: COMPLETE / NO_POWER, mechanically derived, deterministic."""
import os, sys
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "sim"))
import simlib as S, ritual_verdict as V  # noqa: E402
pytestmark = pytest.mark.skipif(not os.path.exists(f"{S.GOLD}/la_ritual_candidate_packet.jsonl"), reason="packets absent")

@pytest.fixture(scope="module")
def v(): return V.run()["verdict"]

def test_status_complete(v): assert v["status"] == "COMPLETE"
def test_readiness_no_power(v):
    assert v["ritual_channel_readiness"] == "NO_POWER"
    assert v["criteria"]["drift_model_independently_specifiable"] is False
    assert v["criteria"]["drift_flexibility_fp_excessive"] is True
def test_not_ready_review(v): assert v["ritual_channel_readiness"] != "READY_FOR_INPUT_FREEZE_REVIEW"
def test_determinism(v): assert V.run()["verdict"] == v
