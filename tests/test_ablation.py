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


# --------------------------------------------------------------------------- #
# GATE 2 (e) — consonant-skeleton reconciliation vocabulary
# --------------------------------------------------------------------------- #
def test_skeleton_reconciles_the_three_sources():
    # the cross-source agreements gate 2 needs: LLM "kull" / litindex "kull" / Hebrew "kl" -> "kl"
    assert ablation.skeleton("kull") == ablation.skeleton("kl") == "kl"
    assert ablation.skeleton("kull") == ablation.skeleton("kull") == "kl"
    # LLM "yayin" / litindex "yn" -> "yn"
    assert ablation.skeleton("yayin") == ablation.skeleton("yn") == "yn"
    # gold-convention shin/aleph reconcile with the English romanization of Asherah
    assert ablation.skeleton("asherah") == ablation.skeleton("<$rh") == "srh"
    assert ablation.skeleton("ʔšr") == "sr"
    # l and r are kept DISTINCT (the su-pa-ra=spl l/r ambiguity lives in the litindex value, not here)
    assert ablation.skeleton("spl") == "spl"
    assert ablation.skeleton("spr") == "spr"
    assert ablation.skeleton("spl") != ablation.skeleton("spr")
    # a vowel-separated s…h (samekh+he) is NOT fused into a shin (digraph collapse precedes vowel-strip)
    assert ablation.skeleton("sahar") == "shr"
    # non-strings safe
    assert ablation.skeleton(None) == ""
    assert ablation.skeleton(42) == ""


# --------------------------------------------------------------------------- #
# GATE 2 (f) — parse_cognates (surface -> sign-sequence, skeletonize, drop unknown forms)
# --------------------------------------------------------------------------- #
def test_parse_cognates_maps_surface_skeletonizes_drops_unknown():
    forms = [ablation.build_form("PROBE:KU-RO", ["KU", "RO"]),
             ablation.build_form("PROBE:JA-NE", ["JA", "NE"])]
    text = (
        "```json\n"
        '{"partial_map": {}, "prediction": "x",'
        ' "cognates": [{"form": "ku-ro", "lexeme": "kull", "gloss": "all, total"},'
        '              {"form": "JA-NE", "lexeme": "yayin", "gloss": "Wine"},'
        '              {"form": "ZZ-YY", "lexeme": "nope", "gloss": "x"}]}\n'
        "```\n"
    )
    out = ablation.parse_cognates(text, forms)
    # surface case/spelling reconciled to canonical sign-KEY sequence; lexeme skeletonized; gloss lc'd
    assert ("KU-RO", "kl", "all, total") in out
    assert ("JA-NE", "yn", "wine") in out
    # a cognate whose form was NOT shown to the model is dropped (no invented words)
    assert not any(seq == "ZZ-YY" for seq, _, _ in out)
    # robust to garbage
    assert ablation.parse_cognates("not json", forms) == set()
    assert ablation.parse_cognates('{"cognates": "oops"}', forms) == set()
    assert ablation.parse_cognates(None, forms) == set()


# --------------------------------------------------------------------------- #
# GATE 2 (g) — litindex_cognate_hit (same word + same reading)
# --------------------------------------------------------------------------- #
def test_litindex_cognate_hit_fires_and_misses():
    index = litindex.load_index()
    # KU-RO + Semitic lexeme 'kull' (skeleton 'kl') reproduces the published kull reading
    assert ablation.litindex_cognate_hit("KU-RO", ablation.skeleton("kull"), "x", index)
    # JA-NE + 'yayin' (skeleton 'yn') reproduces the published 'yn' reading
    assert ablation.litindex_cognate_hit("JA-NE", ablation.skeleton("yayin"), "wine", index)
    # gloss path: gloss 'total' reproduces KU-RO's lexical_reading even with a non-matching skeleton
    assert ablation.litindex_cognate_hit("KU-RO", "zzz", "total", index)
    # an UNPUBLISHED word never fires
    assert not ablation.litindex_cognate_hit("QE-RA2", ablation.skeleton("anything"), "x", index)
    # right reading but WRONG word (atoms in the wrong order = different word) does not fire
    assert not ablation.litindex_cognate_hit("RO-KU", ablation.skeleton("kull"), "", index)
    # right word, WRONG reading (skeleton mismatch, empty gloss) does not fire
    assert not ablation.litindex_cognate_hit("SU-PU", ablation.skeleton("zzzz"), "", index)


# --------------------------------------------------------------------------- #
# GATE 2 (h) — cognate_contamination math + the no-power honesty rule + per-word table
# --------------------------------------------------------------------------- #
def test_cognate_contamination_math_and_per_word_table():
    index = litindex.load_index()
    # LLM reproduces KU-RO/kull AND JA-NE/yn; the model-free arm reproduces only JA-NE/yn
    llm = {("KU-RO", ablation.skeleton("kull"), "all"),
           ("JA-NE", ablation.skeleton("yayin"), "wine")}
    mech = {("JA-NE", ablation.skeleton("yn"))}
    c = ablation.cognate_contamination(llm, mech, index)

    assert c["n_llm_lit_cog_hits"] == 2
    assert c["n_mech_lit_cog_hits"] == 1
    assert c["n_shared_lit_cog"] == 1                         # JA-NE/yn
    # KU-RO/kull is LLM-reproduced but NOT mechanically reproduced -> 1/2
    assert c["cognate_contamination_rate"] == pytest.approx(0.5)
    assert c["cognate_no_power"] is False
    assert c["litindex_partial"] is True                      # seed is non-exhaustive
    # auditable per-word table (not an opaque 1.0)
    assert c["per_word"]["KU-RO"]["llm_reproduced"] is True
    assert c["per_word"]["KU-RO"]["mech_reproduced"] is False
    assert c["per_word"]["JA-NE"]["llm_reproduced"] is True
    assert c["per_word"]["JA-NE"]["mech_reproduced"] is True
    assert c["per_word"]["SU-PU"]["llm_reproduced"] is False  # an untouched word
    # the table covers all 7 cognate-level litindex words
    assert set(c["per_word"]) == {"SU-PU", "KA-RO-PA", "SU-PA-RA", "KU-RO",
                                  "JA-NE", "A-SA-SA-RA-ME", "KI-RO"}


def test_cognate_contamination_rate_none_when_no_llm_lit_hits():
    index = litindex.load_index()
    # the LLM proposes a cognate for a NON-litindex word -> reproduces no published reading
    c = ablation.cognate_contamination({("QE-RA2", "qr", "stuff")}, set(), index)
    assert c["n_llm_lit_cog_hits"] == 0
    assert c["cognate_contamination_rate"] is None            # UNDEFINED, NOT a misleading 0.0
    assert c["cognate_no_power"] is True
    assert c["litindex_partial"] is True


# --------------------------------------------------------------------------- #
# GATE 2 (i) — mechanical_cognates determinism
# --------------------------------------------------------------------------- #
def test_mechanical_cognates_deterministic():
    forms = [ablation.build_form("F1", ["DA", "RE"]),
             ablation.build_form("F2", ["KI", "TO"])]
    heb = frozenset({"dr", "kt"})
    r1 = ablation.mechanical_cognates(forms, heb, eps=0.34)
    r2 = ablation.mechanical_cognates(forms, heb, eps=0.34)
    assert r1 == r2
    assert ("DA-RE", ablation.skeleton("dr")) in r1
    assert ("KI-TO", ablation.skeleton("kt")) in r1
    # empty lexicon -> no power
    assert ablation.mechanical_cognates(forms, frozenset(), eps=0.34) == set()


def test_mechanical_propose_output_unchanged_after_refactor():
    # the refactor that extracted _form_nearest_matches must NOT change the (sign,value) output.
    forms = _mech_fixture_forms()
    assert ablation.mechanical_propose(forms, _TINY_HEB, seed=0) == {("DA", "d"), ("RE", "r")}


# --------------------------------------------------------------------------- #
# GATE 2 (j) — probe forms are the litindex words
# --------------------------------------------------------------------------- #
def test_litindex_probe_forms_are_the_litindex_words():
    index = litindex.load_index()
    probes = ablation.litindex_probe_forms(index)
    seqs = {"-".join(p.keys) for p in probes}
    assert seqs == {"SU-PU", "KA-RO-PA", "SU-PA-RA", "KU-RO",
                    "JA-NE", "A-SA-SA-RA-ME", "KI-RO"}
    assert all(p.fid.startswith("PROBE:") for p in probes)
    assert all(len(p.signs) >= 2 for p in probes)
    # the displayed surface (build_prompt) of a probe maps back to its own sign-sequence
    assert ablation._canon_seq("KU-RO") in seqs


# --------------------------------------------------------------------------- #
# GATE 2 (k) — run_ablation returns the cognate aggregate and survives (monkeypatched generate)
# --------------------------------------------------------------------------- #
def test_run_ablation_returns_cognate_aggregate(monkeypatch):
    canned = (
        "```json\n"
        '{"partial_map": {"KU": "k", "RO": "r"},'
        ' "cognates": [{"form": "KU-RO", "lexeme": "kull", "gloss": "all"},'
        '              {"form": "JA-NE", "lexeme": "yayin", "gloss": "wine"}],'
        ' "prediction": "x"}\n'
        "```\n"
    )

    def fake_generate(model, prompt, *, options=None, timeout=180, host=None):
        return {"response": canned, "ok": True, "prompt_tokens": 1, "eval_tokens": 1,
                "eval_seconds": 0.0}

    monkeypatch.setattr(ablation.ollama_client, "generate", fake_generate)
    # hermetic: no extra held-out forms (probes carry the litindex words); stub the Hebrew lexicon.
    monkeypatch.setattr(ablation, "heldout_forms", lambda n, seed, window=6: [])
    monkeypatch.setattr(ablation, "hebrew_lexicon", lambda: (frozenset({"kl", "yn", "sp"}), "test"))

    out = ablation.run_ablation("m", n_seeds=2, n_forms=0, seed0=0, with_llm=True)
    assert out["n_probe_forms"] == 7 and out["probe_included"] is True
    assert len(out["cognate_per_seed"]) == 2
    cagg = out["cognate_aggregate"]
    # the LLM reproduced KU-RO/kull and JA-NE/yn in EVERY seed (canned, deterministic)
    assert cagg["word_table"]["KU-RO"]["llm_reproduced_seeds"] == 2
    assert cagg["word_table"]["JA-NE"]["llm_reproduced_seeds"] == 2
    # the rate is defined (the LLM had lit hits) and in [0,1]
    cr = cagg["cognate_contamination_rate"]["mean"]
    assert cr is not None and 0.0 <= cr <= 1.0
    # the existing correspondence-level report is still present and INTACT
    assert "aggregate" in out and "contamination_rate" in out["aggregate"]


def test_run_ablation_no_probe_flag(monkeypatch):
    monkeypatch.setattr(ablation, "heldout_forms", lambda n, seed, window=6: [])
    monkeypatch.setattr(ablation, "hebrew_lexicon", lambda: (frozenset({"kl"}), "test"))
    out = ablation.run_ablation("m", n_seeds=1, n_forms=0, seed0=0, with_llm=False, no_probe=True)
    assert out["n_probe_forms"] == 0 and out["probe_included"] is False
    # with no probes and no held-out forms, the cognate metric has no power (honest, not a 0)
    assert out["cognate_aggregate"]["all_seeds_no_power"] is True
