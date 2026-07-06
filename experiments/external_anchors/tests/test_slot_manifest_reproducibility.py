"""Deterministic regeneration of the frozen slot manifest from the pinned licensed inputs.
Fails loudly on any drift (input hash, classifier version, split seed, or output hash)."""
import hashlib, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
EXPECT_GOLD = "dc9653a91d7ba14dcb76238968c368e6369813583d25bf41c97ffb0a5d024551"
GOLD = os.path.join(ROOT, "data/gold/slot_candidate_manifest.jsonl")

def _sha(p):
    h = hashlib.sha256(); h.update(open(p, "rb").read()); return h.hexdigest()

def test_manifest_regenerates_to_pinned_hash():
    if not os.path.exists(os.path.join(ROOT, "src/slot_classifier/build_manifest.py")):
        import pytest; pytest.skip("build script absent")
    try:
        import slotlib  # noqa
    except Exception:
        sys.path.insert(0, os.path.join(ROOT, "src/slot_classifier"))
    # licensed corpus must be present (skip gracefully if not — matches main-repo licensed_data pattern)
    from importlib import import_module
    sys.path.insert(0, os.path.join(ROOT, "src/slot_classifier"))
    sl = import_module("slotlib")
    if not os.path.exists("/home/claude-runner/gitlab/n8n/logos/corpus/silver/inscriptions_structured.json"):
        import pytest; pytest.skip("licensed corpus not present")
    subprocess.check_call([sys.executable, os.path.join(ROOT, "src/slot_classifier/build_manifest.py")],
                          stdout=subprocess.DEVNULL)
    got = _sha(GOLD)
    assert got == EXPECT_GOLD, f"MANIFEST DRIFT: {got} != pinned {EXPECT_GOLD} (rule {sl.RULE_VERSION}, seed {sl.SPLIT_SEED})"
