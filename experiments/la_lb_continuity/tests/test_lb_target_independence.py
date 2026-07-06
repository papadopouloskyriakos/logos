"""§VIII: LB targets are selected independently of Linear A (no LA candidate ever read); packet B carries
no LA / similarity; targets are DĀMOS-attested; deterministic. DĀMOS-dependent checks skip if absent."""
import inspect, json, os, re, sys
import pytest

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "src", "target_build"))
import build_lb_targets as T  # noqa: E402

_DAMOS = os.path.exists(T.DAMOS_ITEMS) or os.path.exists(
    "/home/claude-runner/gitlab/n8n/logos/corpus/bronze/linearb/damos/items.jsonl")


def test_build_reads_no_linear_a():
    """The target builder must never import or read the LA candidate manifest / slot classifier."""
    src = inspect.getsource(T)
    code = "\n".join(l.split("#")[0] for l in src.splitlines()).lower()
    for forbidden in ("la_candidate", "candidate_freeze", "slot", "slotlib",
                      "la_candidate_packet", "inscriptions_structured", "silver"):
        assert forbidden not in code, f"target builder references {forbidden!r} — not LA-independent"


def test_target_roles_partition():
    rows = T.build()
    from collections import Counter
    role = Counter(r["development_or_evaluation_role"] for r in rows)
    assert role["DEVELOPMENT"] == 5           # the five known-pair LB forms
    assert role["EVALUATION"] >= 12           # independent KN toponyms
    assert role["NEGATIVE_CONTROL"] >= 10     # LB non-toponyms
    # exactly the five known are flagged in_known_five, all in the DEVELOPMENT role
    known = [r for r in rows if r["included_in_known_five"]]
    assert len(known) == 5 and all(r["development_or_evaluation_role"] == "DEVELOPMENT" for r in known)


def test_packet_has_no_la_no_similarity():
    rows = T.build()
    keys = set().union(*[set(r) for r in rows])
    for k in keys:
        assert not re.search(r"\bla_|linear_a|candidate|similar|score|match\b", k.lower()), k


def test_provenance_present():
    for r in T.build():
        assert r["source_citation"] and r["entity_identification"]
        assert 0.0 <= r["identification_confidence"] <= 1.0


@pytest.mark.skipif(not _DAMOS, reason="DĀMOS not present")
def test_all_targets_attested_in_damos():
    for r in T.build():
        assert r["damos_attestation"] > 0, f"{r['standard_transliteration']} not attested in DĀMOS"


@pytest.mark.skipif(not _DAMOS, reason="DĀMOS not present")
def test_determinism():
    assert T.build() == T.build()
