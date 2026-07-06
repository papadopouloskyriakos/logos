"""§VI LB ritual targets: independent of LA (no LA/slot/silver read), roles partitioned, known pairs
quarantined, all DĀMOS-attested, no LA/similarity in packet, deterministic."""
import inspect, os, re, sys
import pytest

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "src", "inventory"))
import build_lb_ritual as T  # noqa: E402

_DAMOS = os.path.exists("/home/claude-runner/gitlab/n8n/logos/corpus/bronze/linearb/damos/items.jsonl")


def test_independent_of_linear_a():
    code = "\n".join(l.split("#")[0] for l in inspect.getsource(T).splitlines()).lower()
    for f in ("la_ritual", "la_candidate", "slot", "slotlib", "inscriptions_structured", "silver"):
        assert f not in code, f"target builder references {f}"


def test_roles_partition():
    from collections import Counter
    rows = T.build()
    r = Counter(x["development_or_evaluation_role"] for x in rows)
    assert r["EVALUATION_TARGETS"] == 15 and r["DEVELOPMENT_TARGETS"] == 4
    assert r["KNOWN_PAIR_DEVELOPMENT"] == 4 and r["NEGATIVE_CONTROL_TARGETS"] == 6


def test_known_pairs_quarantined():
    for x in T.build():
        if x["development_or_evaluation_role"] == "KNOWN_PAIR_DEVELOPMENT":
            assert x["known_pair_overlap"] is True
            assert x["confirmatory_eligibility"] == "CONFIRMATORY_INELIGIBLE"


def test_packet_no_la_no_similarity():
    keys = set().union(*[set(r) for r in T.build()])
    for k in keys:
        assert not re.search(r"\bla_ritual|linear_a|candidate|similar|score|match\b", k.lower()), k
    for r in T.build():
        assert r["channel_class"] == "EXPLORATORY_POSTHOC_CHANNEL"


@pytest.mark.skipif(not _DAMOS, reason="DĀMOS absent")
def test_all_attested():
    for x in T.build():
        assert x["damos_attestation"] > 0, x["standard_transliteration"]


@pytest.mark.skipif(not _DAMOS, reason="DĀMOS absent")
def test_determinism():
    assert T.build() == T.build()
