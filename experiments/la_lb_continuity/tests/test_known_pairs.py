"""§VI: the five known pairs are DEVELOPMENT_BENCHMARK or stricter — never confirmatory; speculative
morphology is quarantined. Skips without silver."""
import os, sys
import pytest

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "src", "known_pairs"))
sys.path.insert(0, os.path.join(HERE, "..", "src", "sigla_reconcile"))
import config  # noqa: E402
import build_known_pairs as K  # noqa: E402

pytestmark = pytest.mark.skipif(not os.path.exists(config.SILVER), reason="silver not present")

ALLOWED = {"DEVELOPMENT_BENCHMARK", "EXPLORATORY_ONLY", "POTENTIAL_HELDOUT",
           "CONFIRMATORY_INELIGIBLE", "SPECULATIVE_MORPHOLOGICAL_CONTINUITY"}
CONFIRMATORY_FORBIDDEN = {"CONFIRMATORY", "CONFIRMATORY_ELIGIBLE", "EVALUATION", "HELDOUT_CONFIRMED"}


@pytest.fixture(scope="module")
def rows():
    return K.build()


def test_no_pair_is_confirmatory(rows):
    for r in rows:
        assert r["confirmatory_eligibility"] in ALLOWED
        assert r["confirmatory_eligibility"] not in CONFIRMATORY_FORBIDDEN
        assert r["posthoc_discovery_risk"].startswith("HIGH")
        assert r["la_candidate_selected_without_lb_reading"] is False


def test_five_known_are_benchmark_or_stricter(rows):
    known = [r for r in rows if not r["confirmatory_eligibility"].startswith("SPECULATIVE")]
    assert len(known) == 5
    for r in known:
        assert r["confirmatory_eligibility"] in {"DEVELOPMENT_BENCHMARK", "CONFIRMATORY_INELIGIBLE",
                                                 "EXPLORATORY_ONLY"}


def test_speculative_quarantined(rows):
    spec = [r for r in rows if r["confirmatory_eligibility"] == "SPECULATIVE_MORPHOLOGICAL_CONTINUITY"]
    assert {r["linear_a_form"] for r in spec} == {"DI-DE-RU", "PA-JE-RE"}


def test_absent_forms_flagged_ineligible(rows):
    for r in rows:
        if not r["linear_a_source_documents"] and not r["confirmatory_eligibility"].startswith("SPECULATIVE"):
            assert r["confirmatory_eligibility"] == "CONFIRMATORY_INELIGIBLE"


def test_determinism(rows):
    assert K.build() == rows
