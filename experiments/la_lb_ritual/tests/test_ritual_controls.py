"""§IX feasibility controls: exact synthetic recovers, D2 tolerates 1 flag, LB-internal specific, PC-R4
face-validity only. No real LA<->LB matching."""
import os, sys
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "sim"))
import simlib as S, controls as C  # noqa: E402
pytestmark = pytest.mark.skipif(not os.path.exists(f"{S.GOLD}/la_ritual_candidate_packet.jsonl"), reason="packets absent")

def test_pcr1_exact_recovered():
    r = C.pcr1_exact_synthetic(3, S.SEED + 3)
    assert r["recovered_exact"] == r["implanted"]

def test_pcr3_lb_internal_specific():
    r = C.pcr3_lb_internal(S.SEED + 7)
    assert r["recovery_rate"] == 1.0 and r["cross_term_fp"] == 0

def test_pcr4_face_validity_only():
    r = C.pcr4_known_pair_representation()
    assert r["label"] == "POSTHOC_FACE_VALIDITY_ONLY"
    assert r["exact_representable"] == 2 and r["drift_required"] == 3

def test_determinism():
    assert C.pcr1_exact_synthetic(3, 5) == C.pcr1_exact_synthetic(3, 5)
