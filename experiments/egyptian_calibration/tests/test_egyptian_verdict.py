"""§XI verdict: INCOMPLETE / NOT_READY at the load-bearing source blocker; not a disguised NO_POWER."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "calibration"))
import verdict as V  # noqa: E402

def test_status_incomplete():
    v = V.run()["verdict"]
    assert v["status"] == "INCOMPLETE"
    assert v["egyptian_channel_readiness"] == "NOT_READY"

def test_is_source_blocker_not_power_question():
    c = V.run()["verdict"]["criteria"]
    assert c["is_a_source_extraction_blocker"] is True
    assert c["is_a_power_question"] is False
    assert c["calibration_corpus_buildable"] is False

def test_design_frozen_and_no_leakage():
    c = V.run()["verdict"]["criteria"]
    assert c["design_frozen"] is True and c["cretan_target_leakage"] is False

def test_determinism():
    assert V.run() == V.run()
