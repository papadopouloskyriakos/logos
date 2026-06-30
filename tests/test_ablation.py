"""Tests for the §C.4 LLM-ablation delta (scripts/comparison/ablation).

NO network / NO GPU: the LLM arm is exercised only through a MONKEYPATCHED ollama_client.generate
returning a canned fenced-JSON proposal; everything else runs on the deterministic mechanical path +
small hand-built fixtures. Properties locked in:

  (a) mechanical_propose is DETERMINISTIC (same seed -> identical set) and RECURRENCE-GATED (a single
      chance alignment, emitted by only one form, never becomes a correspondence);
  (b) contamination() math — n_shared, jaccard, delta_only, delta_lit_hits, contamination_rate, and
      the honesty rule that contamination_rate is None (litindex_partial=True) when a_lit_hits == 0;
  (c) the LLM arm parses a canned fenced-JSON partial_map into the right (sign,value) set, restricts
      to signs actually shown, and a DEAD call yields an empty proposal without crashing;
  (d) doctrine grep — ablation.py does NOT import scripts.verdict (the proposer never grades).

Run from anywhere:
    python3 -m pytest tests/test_ablation.py -q
"""
import ast
import os
import sys

import pytest

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from scripts.comparison import ablation, litindex  # noqa: E402


# --------------------------------------------------------------------------- #
# (a) mechanical_propose — determinism + recurrence gate
# --------------------------------------------------------------------------- #
# A tiny "Hebrew" lexicon of exact 2-char consonant skeletons. At eps=0.34 a length-2 skeleton has an
# edit cap of 0, so a match is exact — keeping the fixture's alignment fully predictable.
_TINY_HEB = frozenset({"dr", "kt"})


def _mech_fixture_forms():
    # F1 and F2 are DISTINCT forms with the same signs -> the (DA,d)/(RE,r) correspondences recur
    # across 2 forms and SURVIVE. F3's (KI,k)/(TO,t) are emitted by ONE form and must be GATED OUT.
    return [
        ablation.build_form("F1", ["DA", "RE"]),
        ablation.build_form("F2", ["DA", "RE"]),
        ablation.build_form("F3", ["KI", "TO"]),
    ]


def test_mechanical_propose_is_deterministic():
    forms = _mech_fixture_forms()
    r1 = ablation.mechanical_propose(forms, _TINY_HEB, seed=0)
    r2 = ablation.mechanical_propose(forms, _TINY_HEB, seed=0)
    assert r1 == r2
    # seed is interface-symmetry only; a different seed yields the identical deterministic set.
    assert ablation.mechanical_propose(forms, _TINY_HEB, seed=99) == r1


def test_mechanical_propose_recurrence_gate():
    forms = _mech_fixture_forms()
    out = ablation.mechanical_propose(forms, _TINY_HEB, seed=0)
    # recurring (>=2 forms) correspondences survive ...
    assert out == {("DA", "d"), ("RE", "r")}
    # ... and the single-form chance alignment is filtered out.
    assert ("KI", "k") not in out
    assert ("TO", "t") not in out


def test_mechanical_propose_empty_lexicon_no_power():
    forms = _mech_fixture_forms()
    assert ablation.mechanical_propose(forms, frozenset(), seed=0) == set()


def test_mechanical_skeleton_excludes_vowels_and_logograms():
    # pure-vowel signs (A, U) and a commodity logogram (VIN, onset 'v' not in the syllabary) and a
    # numeral sign (*301) contribute NO skeleton character; only QE->q, RA2->r remain.
    f = ablation.build_form("X", ["A", "QE", "VIN", "RA₂", "U", "*301"])
    skel, owners = f.consonant_skeleton()
    assert skel == "qr"
    assert owners == ("QE", "RA2")


# --------------------------------------------------------------------------- #
# (b) contamination() math + the a_lit_hits==0 honesty rule
# --------------------------------------------------------------------------- #
def _claim(sign, value):
    return litindex.LitClaim(sign=sign, proposed_value=value, source="test", year=1976,
                             claim_type="lb_value_transfer")


def test_contamination_math():
    a_set = {("QE", "qe"), ("RA", "ra"), ("DA", "x")}
    b_set = {("RA", "ra"), ("DA", "y")}
    index = [_claim("QE", "qe"), _claim("RA", "ra")]
    c = ablation.contamination(a_set, b_set, index)

    assert c["n_a"] == 3
    assert c["n_b"] == 2
    assert c["n_shared"] == 1                 # {('RA','ra')}
    assert c["jaccard"] == pytest.approx(0.25)  # 1 / |union|=4
    assert c["delta_only"] == 2               # a\\b = {('QE','qe'),('DA','x')}
    assert c["a_lit_hits"] == 2               # ('QE','qe') and ('RA','ra') reproduce published values
    assert c["delta_lit_hits"] == 1           # of the LLM-only set, only ('QE','qe') is a lit hit
    assert c["contamination_rate"] == pytest.approx(0.5)  # 1 / 2
    # the project seed litindex is NON-EXHAUSTIVE, so even a finite rate is a partial, seed-only
    # lower bound — litindex_partial must stay True (it previously, wrongly, flipped to False here)
    assert c["litindex_partial"] is True
    assert c["seed_nonexhaustive"] is True


def test_contamination_rate_none_when_no_lit_hits():
    # The LLM's values match nothing in the (here empty) index -> a_lit_hits==0 -> rate UNDEFINED.
    a_set = {("XX", "foo"), ("YY", "bar")}
    b_set = {("YY", "bar")}
    c = ablation.contamination(a_set, b_set, index=[])

    assert c["a_lit_hits"] == 0
    assert c["delta_lit_hits"] == 0
    assert c["contamination_rate"] is None     # NOT a misleading 0.0
    assert c["litindex_partial"] is True
    # the raw structural signal is still reported regardless of literature coverage
    assert c["delta_only"] == 1                # a\\b = {('XX','foo')}
    assert c["n_shared"] == 1


def test_contamination_value_mismatch_is_not_a_lit_hit():
    # Same SIGN as a published claim but a DIFFERENT value is not a literature hit (sign+value match).
    a_set = {("QE", "ka")}                      # published QE value is 'qe', not 'ka'
    c = ablation.contamination(a_set, set(), index=[_claim("QE", "qe")])
    assert c["a_lit_hits"] == 0
    assert c["contamination_rate"] is None


# --------------------------------------------------------------------------- #
# (c) the LLM arm — monkeypatched generate (no GPU)
# --------------------------------------------------------------------------- #
def test_llm_propose_parses_canned_json(monkeypatch, tmp_path):
    canned = (
        "Here is my partial decipherment:\n"
        "```json\n"
        '{"partial_map": {"QE": "/k/", "RA2": "r", "ZZ": "z"},'
        ' "cognates": [], "prediction": "a held-out claim"}\n'
        "```\n"
    )

    def fake_generate(model, prompt, *, options=None, timeout=180, host=None):
        # seeded sampling must be requested by the proposer
        assert options == {"temperature": 0.8, "seed": 0}
        return {"response": canned, "prompt_tokens": 5, "eval_tokens": 9,
                "eval_seconds": 0.1, "ok": True}

    monkeypatch.setattr(ablation.ollama_client, "generate", fake_generate)

    forms = [ablation.build_form("F1", ["QE", "RA₂", "U"])]
    out = ablation.llm_propose(forms, "gemma3", 0, log_path=str(tmp_path / "log.jsonl"))
    # 'ZZ' is dropped (not shown to the model); '/k/' normalizes to 'k'.
    assert out == {("QE", "k"), ("RA2", "r")}


def test_llm_propose_dead_call_is_empty_no_crash(monkeypatch, tmp_path):
    def dead_generate(model, prompt, *, options=None, timeout=180, host=None):
        return {"response": "", "prompt_tokens": 0, "eval_tokens": 0,
                "eval_seconds": 0.0, "ok": False}

    monkeypatch.setattr(ablation.ollama_client, "generate", dead_generate)
    forms = [ablation.build_form("F1", ["QE", "RA₂", "U"])]
    out = ablation.llm_propose(forms, "gemma3", 1, log_path=str(tmp_path / "log.jsonl"))
    assert out == set()


def test_llm_propose_garbled_response_is_empty(monkeypatch, tmp_path):
    def garbled(model, prompt, *, options=None, timeout=180, host=None):
        return {"response": "no json here, just rambling prose", "prompt_tokens": 1,
                "eval_tokens": 1, "eval_seconds": 0.0, "ok": True}

    monkeypatch.setattr(ablation.ollama_client, "generate", garbled)
    forms = [ablation.build_form("F1", ["QE", "RA₂"])]
    assert ablation.llm_propose(forms, "gemma3", 2, log_path=str(tmp_path / "log.jsonl")) == set()


def test_run_ablation_isolates_a_raising_generate(monkeypatch):
    """Verifier-found regression: a generate() that RAISES (violating its no-raise contract) must not
    abort the whole multi-seed batch — each seed is isolated, the LLM arm degrades to an empty
    proposal, and the run still aggregates over every seed (mechanical arm + survival preserved)."""
    def boom(model, prompt, *, options=None, timeout=180, host=None):
        raise RuntimeError("host down")
    monkeypatch.setattr(ablation.ollama_client, "generate", boom)
    # hermetic: stub the data loaders so the test needs no silver corpus / bhsa clone
    fixture = [ablation.build_form("F1", ["QE", "RA₂", "U"]),
               ablation.build_form("F2", ["DA", "RO", "NA"])]
    monkeypatch.setattr(ablation, "heldout_forms", lambda n, seed, window=6: list(fixture))
    monkeypatch.setattr(ablation, "hebrew_lexicon", lambda: (frozenset({"qru", "drn"}), "test"))
    out = ablation.run_ablation("qwen2.5:72b", n_seeds=3, n_forms=2, seed0=0, with_llm=True)
    assert isinstance(out, dict) and len(out["per_seed"]) == 3        # batch survived all 3 seeds
    for row in out["per_seed"]:
        assert row["n_a"] == 0                                        # LLM arm degraded to empty
        assert row["llm_error"] and "host down" in row["llm_error"]   # the failure is recorded, not swallowed


def test_parse_proposal_robust_to_non_dict_partial_map():
    forms = [ablation.build_form("F1", ["QE", "RA₂"])]
    valid = {sk for f in forms for sk in f.keys}
    assert ablation.parse_proposal('{"partial_map": "oops"}', valid) == set()
    assert ablation.parse_proposal("totally not json", valid) == set()
    assert ablation.parse_proposal(None, valid) == set()


# --------------------------------------------------------------------------- #
# (d) doctrine grep — ablation.py never imports scripts.verdict (proposer != grader)
# --------------------------------------------------------------------------- #
def test_ablation_does_not_import_verdict():
    src_path = os.path.join(_REPO_ROOT, "scripts", "comparison", "ablation.py")
    with open(src_path, encoding="utf-8") as fh:
        tree = ast.parse(fh.read())

    imported_modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                imported_modules.add(a.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported_modules.add(node.module)
            for a in node.names:
                imported_modules.add(f"{node.module}.{a.name}" if node.module else a.name)

    assert not any("verdict" in m for m in imported_modules), (
        f"ablation.py must not import the verdict machinery; found {sorted(imported_modules)}"
    )
