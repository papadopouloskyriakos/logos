"""§VII leakage firewall: candidate GENERATION is blind; the packet exposes no LB / phonetic / similarity;
the contamination filter is one-directional. Skips without silver."""
import inspect, json, os, re, sys
import pytest

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "src", "candidate_freeze"))
sys.path.insert(0, os.path.join(HERE, "..", "src", "sigla_reconcile"))
import config  # noqa: E402
import build_la_candidates as B  # noqa: E402

pytestmark = pytest.mark.skipif(not os.path.exists(config.SILVER), reason="silver not present")


def test_generation_source_is_blind():
    """build() must not consult the ledger / LB / phonetic-selection — only the internal classifier.
    Scan CODE only (strip inline comments, which legitimately describe what the packet excludes)."""
    src = inspect.getsource(B.build)
    code = "\n".join(line.split("#")[0] for line in src.splitlines()).lower()
    for forbidden in ("known_la_forms", "known_persistence", "quarantine", "ledger",
                      "linear_b", "target", "similar", "score"):
        assert forbidden not in code, f"build() code references {forbidden!r} — not blind"


def test_quarantine_is_one_directional():
    """The contamination filter may only move NEGATIVE_CONTROL→QUARANTINED; PRIMARY/SENSITIVITY frozen."""
    manifest, packet = B.build()
    before = {r["candidate_id"]: r["inclusion_set"] for r in packet}
    prim_sens_before = {cid for cid, s in before.items() if s in ("PRIMARY", "SENSITIVITY_1")}
    B.apply_contamination_quarantine(manifest, packet, B.known_la_forms())
    after = {r["candidate_id"]: r["inclusion_set"] for r in packet}
    prim_sens_after = {cid for cid, s in after.items() if s in ("PRIMARY", "SENSITIVITY_1")}
    assert prim_sens_before == prim_sens_after                      # untouched
    for cid in before:
        if before[cid] != after[cid]:
            assert before[cid] == "NEGATIVE_CONTROL" and after[cid] == "QUARANTINED"


def test_packet_has_no_lb_no_phonetic_no_similarity():
    manifest, packet = B.build()
    B.apply_contamination_quarantine(manifest, packet, B.known_la_forms())
    keys = set().union(*[set(r) for r in packet])
    for k in keys:
        assert not re.search(r"lb|linear_b|target|similar|score|match|phonetic|reading", k.lower()), k
    blob = json.dumps(packet)
    assert "_phonetic_word" not in blob
    # no lowercase hyphenated transliteration leaked (e.g. 'pa-i-to'); raw ids are UPPERCASE AB##/A###
    assert not re.search(r"[a-z]{1,3}-[a-z]{1,3}-[a-z]", blob)
