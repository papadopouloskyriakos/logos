"""§II freeze clarifications: mutually-exclusive base partitions, deterministic B+C union, ARKH policy,
unit of analysis. Skips if the frozen packet is absent."""
import os, sys
import pytest

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "src", "continuity"))
import cfg  # noqa: E402
import partitions as P  # noqa: E402

pytestmark = pytest.mark.skipif(not os.path.exists(cfg.LA_PACKET), reason="frozen packet absent")


def test_base_partitions_are_mutually_exclusive_and_sum_66():
    cands = P.load_candidates()
    seen = {}
    for c in cands:
        seen.setdefault(c["candidate_id"], []).append(P.base_partition(c))
    assert all(len(v) == 1 for v in seen.values())          # each form in exactly one base partition
    counts = {k: len(v) for k, v in P.partitioned().items()}
    assert counts == {"PRIMARY_B": 11, "SENSITIVITY_C_ADDITIONAL": 33,
                      "NEGATIVE_CONTROL": 21, "QUARANTINED": 1}
    assert sum(counts.values()) == 66


def test_primary_plus_sensitivity_union_deterministic():
    a = [c["candidate_id"] for c in P.primary_plus_sensitivity()]
    b = [c["candidate_id"] for c in P.primary_plus_sensitivity()]
    assert a == b and len(a) == 44 and len(set(a)) == 44


def test_arkh_policy():
    for c in P.load_candidates():
        if c.get("site_ambiguity"):
            assert P.site_assignment(c) == "AMBIGUOUS_ARKH"      # never opportunistically assigned


def test_unit_is_unique_form_not_tablet():
    u = P.unit_summary()
    assert u["effective_independent_units"] == u["unique_forms"] == 66
    assert u["raw_document_attestations"] >= u["unique_forms"]   # attestations don't multiply units


def test_frozen_inputs_unchanged():
    assert cfg.verify_inputs()                                    # membership manifests must not drift
