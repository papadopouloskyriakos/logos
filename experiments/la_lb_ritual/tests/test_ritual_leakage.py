"""§XI leakage firewall — proven BEFORE any matching interface exists.

Verifies: LA builder can't read LB / LB builder can't read LA / neither's blind generation reads the
ledger / drift feasibility doesn't fit on known pairs / packets carry no cross-content / no phonetic
transliteration in packet A / no LA sequence in packet B / no similarity function operates on the real
inventories in this pass.
"""
import glob, inspect, json, os, re, sys

HERE = os.path.dirname(__file__)
INV = os.path.join(HERE, "..", "src", "inventory")
DF = os.path.join(HERE, "..", "src", "drift_feasibility")
sys.path.insert(0, INV); sys.path.insert(0, DF)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "external_anchors", "src", "slot_classifier"))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "la_lb_continuity", "src", "common"))
import build_la_ritual as LA  # noqa: E402
import build_lb_ritual as LB  # noqa: E402
import drift_feasibility as DRIFT  # noqa: E402

GOLD = os.path.join(HERE, "..", "data", "gold")
REPORTS = os.path.join(HERE, "..", "reports")


def _code(fn):
    src = re.sub(r'"""(?:.|\n)*?"""', "", inspect.getsource(fn), count=1)
    return "\n".join(l.split("#")[0] for l in src.splitlines()).lower()


def test_la_generation_cannot_read_lb_or_ledger():
    code = _code(LA.build)
    for f in ("lb_ritual", "lb_target", "linear_b", "known_ritual", "ledger", "target", "similar", "score"):
        assert f not in code, f"LA build() references {f}"


def test_lb_generation_cannot_read_la():
    code = _code(LB.build)
    for f in ("la_ritual", "la_candidate", "slotlib", "silver", "known_ritual", "ledger", "similar", "score"):
        assert f not in code, f"LB build() references {f}"


def test_drift_feasibility_does_not_fit_on_known_pairs():
    # it may OBSERVE operations for feasibility, but must not import/fit the candidate/target packets
    code = _code(DRIFT.run)
    for f in ("build_la_ritual", "build_lb_ritual", "match", "fit(", "train("):
        assert f not in code, f"drift feasibility references {f}"


def test_packet_a_has_no_lb_no_phonetic():
    if not os.path.exists(f"{GOLD}/la_ritual_candidate_packet.jsonl"):
        return
    blob = open(f"{GOLD}/la_ritual_candidate_packet.jsonl").read()
    assert "lb_" not in blob and "linear_b" not in blob.lower()
    assert not re.search(r"[a-z]{1,3}-[a-z]{1,3}-[a-z]", blob)     # no lowercase transliteration


def test_packet_b_has_no_la_sequence():
    if not os.path.exists(f"{GOLD}/lb_ritual_target_packet.jsonl"):
        return
    for r in (json.loads(l) for l in open(f"{GOLD}/lb_ritual_target_packet.jsonl")):
        assert "la_ritual_id" not in r and "la_raw_sign_sequence" not in r


def test_no_report_shows_la_and_lb_inventories_side_by_side():
    for p in glob.glob(f"{REPORTS}/*.md"):
        base = os.path.basename(p)
        if base == "KNOWN_RITUAL_PAIR_AUDIT.md":
            continue   # the quarantined public ledger is permitted to pair LA~LB
        t = open(p).read()
        assert not ("la_ritual_id" in t and "lb_ritual_id" in t), f"{base} shows both inventories"


def test_no_similarity_function_on_real_inventories():
    # no src module imports the admin real matcher (model.py) to match the real ritual packets
    for p in glob.glob(os.path.join(HERE, "..", "src", "**", "*.py"), recursive=True):
        code = _code_of_file(p)
        assert "import model" not in code and "continuity.model" not in code, p


def _code_of_file(p):
    src = re.sub(r'"""(?:.|\n)*?"""', "", open(p).read())
    return "\n".join(l.split("#")[0] for l in src.splitlines()).lower()
