"""§V LA ritual inventory: blind generation, known-pair quarantine one-directional, packet has no LB/
phonetic/similarity, deterministic."""
import inspect, json, os, re, sys
import pytest

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "src", "inventory"))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "external_anchors", "src", "slot_classifier"))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "la_lb_continuity", "src", "common"))
import build_la_ritual as B  # noqa: E402

_SILVER = "/home/claude-runner/gitlab/n8n/logos/corpus/silver/inscriptions_structured.json"
pytestmark = pytest.mark.skipif(not os.path.exists(_SILVER), reason="silver absent")


def test_generation_blind():
    code = "\n".join(l.split("#")[0] for l in inspect.getsource(B.build).splitlines()).lower()
    for f in ("known_forms", "quarantine", "linear_b", "lb_", "target", "similar", "score"):
        assert f not in code, f"build() references {f}"


def test_partitions_and_quarantine():
    m, p = B.build()
    n = B.apply_known_pair_quarantine(m, p, B.known_forms())
    from collections import Counter
    c = Counter(r["base_partition"] for r in p)
    assert c["PRIMARY_RITUAL"] == 9 and c["KNOWN_PAIR_DEVELOPMENT"] == n == 3
    # no known form remains in a confirmatory partition
    for mm, pp in zip(m, p):
        if tuple(mm["_phonetic_word"]) in B.known_forms():
            assert pp["base_partition"] == "KNOWN_PAIR_DEVELOPMENT"
            assert pp["confirmatory_eligibility"] == "CONFIRMATORY_INELIGIBLE"


def test_quarantine_one_directional():
    m, p = B.build()
    before = {r["la_ritual_id"]: r["base_partition"] for r in p}
    B.apply_known_pair_quarantine(m, p, B.known_forms())
    after = {r["la_ritual_id"]: r["base_partition"] for r in p}
    for cid in before:
        if before[cid] != after[cid]:
            assert before[cid] in ("PRIMARY_RITUAL", "SENSITIVITY_RITUAL") and after[cid] == "KNOWN_PAIR_DEVELOPMENT"


def test_packet_no_lb_no_phonetic_no_similarity():
    m, p = B.build(); B.apply_known_pair_quarantine(m, p, B.known_forms())
    keys = set().union(*[set(r) for r in p])
    for k in keys:
        assert not re.search(r"lb|linear_b|target|similar|score|match|phonetic|reading", k.lower()), k
    blob = json.dumps(p)
    assert "_phonetic_word" not in blob
    assert not re.search(r"[a-z]{1,3}-[a-z]{1,3}-[a-z]", blob)   # no lowercase transliteration
    for r in p:
        assert r["channel_class"] == "EXPLORATORY_POSTHOC_CHANNEL"


def test_determinism():
    a, _ = B.build(); b, _ = B.build()
    assert [x["la_ritual_id"] for x in a] == [x["la_ritual_id"] for x in b]
