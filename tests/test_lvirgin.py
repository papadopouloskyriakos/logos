"""Tests for the §C.2 L_virgin generalization test (scripts/comparison/lvirgin).

NO network / NO GPU: the LLM proposer is exercised only through a MONKEYPATCHED
ollama_client.generate returning canned fenced-JSON; the partition / probe-window / statistics paths
run on the real corpus + small deterministic fixtures. Properties locked in:

  (a) partition_by_class is CLASS-based and EXCLUDES logogram/fraction/numeral/uncertain entirely;
  (b) target_probe_forms builds REAL-context windows that CONTAIN their target sign;
  (c) the proposer loop accumulates per-sign value Counters across seeds from a canned response, and a
      DEAD call contributes nothing without crashing the batch (fail-closed);
  (d) analyze()'s excess-over-random is ~0 for a uniformly-drawn sign and >0 for a concentrated one
      (the sample-size control), the known−virgin gap + permutation p, and the matched-n path;
  (e) doctrine grep — lvirgin.py does NOT import scripts.verdict (the proposer never grades).

Run from anywhere:
    python3 -m pytest tests/test_lvirgin.py -q
"""
import ast
import os
import re
import sys
from collections import Counter

import numpy as np
import pytest

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from scripts.comparison import lvirgin  # noqa: E402


# --------------------------------------------------------------------------- #
# (a) partition by ontology class — excludes non-phonetic signs
# --------------------------------------------------------------------------- #
def test_partition_by_class_synthetic_excludes_nonphonetic():
    ont = {
        "DA": {"class": "syllabogram-AB"},
        "KU": {"class": "syllabogram-AB"},
        "*301": {"class": "syllabogram-Aonly"},
        "*118": {"class": "syllabogram-Aonly"},
        "LOGO:VIN": {"class": "logogram"},
        "NUM:0x10109": {"class": "numeral"},
        "*802": {"class": "fraction"},
        "QA2": {"class": "uncertain"},
    }
    part = lvirgin.partition_by_class(ont)
    assert part["L_known"] == {"DA", "KU"}
    # *301 carries Di Mino's published (quarantined) litindex proposal -> NOT virgin (could be memorized);
    # only the genuinely-unproposed *118 remains in L_virgin.
    assert part["L_virgin"] == {"*118"}
    assert part["lit_quarantined"] == ["*301"]
    # every non-phonetic class is excluded ENTIRELY (qwen is never scored on them)
    assert part["excluded"] == {"logogram": 1, "numeral": 1, "fraction": 1, "uncertain": 1}
    # the two phonetic classes are disjoint
    assert not (part["L_known"] & part["L_virgin"])


def test_partition_by_class_on_real_ontology():
    part = lvirgin.partition_by_class(lvirgin.load_ontology())
    # AB syllabograms (memorizable) land in L_known ...
    assert {"DA", "KU", "SI", "RO"} <= part["L_known"]
    # ... the genuinely-unproposed *-series land in L_virgin ...
    assert "*118" in part["L_virgin"]
    # ... but *301 (Di Mino's published reading) is QUARANTINED out of virgin (could be memorized) ...
    assert "*301" not in part["L_virgin"] and "*301" in part["lit_quarantined"]
    # ... and nothing non-phonetic leaks into either phonetic class.
    phonetic = part["L_known"] | part["L_virgin"]
    assert not any("LOGO" in s for s in phonetic)
    assert all(c in part["excluded"] for c in ("logogram", "fraction", "numeral", "uncertain"))


# --------------------------------------------------------------------------- #
# (b) probe forms — real context window containing the target sign
# --------------------------------------------------------------------------- #
def test_target_probe_forms_contain_target_and_are_real_context():
    ont = lvirgin.load_ontology()
    insc = lvirgin.load_inscriptions()
    pairs = lvirgin.target_probe_forms(ont, insc, n_known=3, n_virgin=3, n_context=5, seed=0)
    assert len(pairs) == 6                                  # 3 known + 3 virgin, all covered

    by_id = {rec["id"]: rec for rec in insc}
    for target_key, form in pairs:
        # the target sign is actually present in the window the model will see
        assert target_key in form.keys
        # the window is a CONTIGUOUS slice of a REAL inscription (provenance is in the fid)
        insc_id = form.fid.split(":")[0]
        assert insc_id in by_id
        m = re.search(r"\[(\d+):(\d+)\]$", form.fid)
        assert m is not None
        start, end = int(m.group(1)), int(m.group(2))
        assert list(form.signs) == list(by_id[insc_id]["signs"])[start:end]
        assert 2 <= len(form.signs) <= 5                    # bounded real context


def test_target_probe_forms_window_is_fixed_across_calls():
    # the same per-sign window must be produced every call (so it is identical across proposer seeds)
    ont = lvirgin.load_ontology()
    insc = lvirgin.load_inscriptions()
    a = lvirgin.target_probe_forms(ont, insc, n_known=4, n_virgin=4, n_context=6, seed=0)
    b = lvirgin.target_probe_forms(ont, insc, n_known=4, n_virgin=4, n_context=6, seed=0)
    assert [(k, f.fid, f.signs) for k, f in a] == [(k, f.fid, f.signs) for k, f in b]


def test_coverage_report_flags_signs_without_context():
    ont = lvirgin.load_ontology()
    insc = lvirgin.load_inscriptions()
    cov = lvirgin.coverage_report(ont, insc, n_context=6, seed=0)
    # every AB sign has a real bare context window
    assert cov["L_known"]["n_skipped_no_context"] == 0
    # some *-series signs occur only inside ligatures -> honestly skipped (not silently re-probed)
    assert cov["L_virgin"]["n_covered"] >= 1
    assert cov["L_virgin"]["n_covered"] + cov["L_virgin"]["n_skipped_no_context"] == \
        cov["L_virgin"]["n_candidates"]


# --------------------------------------------------------------------------- #
# (c) proposer loop — accumulation + fail-closed dead call (monkeypatched generate)
# --------------------------------------------------------------------------- #
def test_run_lvirgin_accumulates_per_sign_values(monkeypatch, tmp_path):
    canned = (
        "```json\n"
        '{"partial_map": {"KU": "ku", "*301": "na", "RO": "ro", "ZZ": "z"},'
        ' "cognates": [], "prediction": "x"}\n'
        "```\n"
    )

    def fake_generate(model, prompt, *, options=None, timeout=180, host=None):
        # the proposer requests seeded sampling at temperature 0.8
        assert options["temperature"] == 0.8 and "seed" in options
        return {"response": canned, "ok": True, "prompt_tokens": 1, "eval_tokens": 1,
                "eval_seconds": 0.0}

    monkeypatch.setattr(lvirgin.ablation.ollama_client, "generate", fake_generate)

    probe_pairs = [
        ("KU", lvirgin.ablation.build_form("F1", ["KU", "RO"])),
        ("*301", lvirgin.ablation.build_form("F2", ["*301", "DA"])),
    ]
    run = lvirgin.run_lvirgin("m", n_seeds=3, probe_pairs=probe_pairs,
                              log_path=str(tmp_path / "log.jsonl"))
    # each target accrued a value in all 3 seeds (canned, deterministic)
    assert run["per_sign_values"]["KU"] == {"ku": 3}
    assert run["per_sign_values"]["*301"] == {"na": 3}
    assert run["n_seeds_no_values"] == 0
    assert len(run["per_seed"]) == 3


def test_run_lvirgin_dead_call_contributes_nothing(monkeypatch, tmp_path):
    def dead_generate(model, prompt, *, options=None, timeout=180, host=None):
        return {"response": "", "ok": False, "prompt_tokens": 0, "eval_tokens": 0,
                "eval_seconds": 0.0}

    monkeypatch.setattr(lvirgin.ablation.ollama_client, "generate", dead_generate)
    probe_pairs = [("KU", lvirgin.ablation.build_form("F1", ["KU", "RO"])),
                   ("*301", lvirgin.ablation.build_form("F2", ["*301", "DA"]))]
    run = lvirgin.run_lvirgin("m", n_seeds=4, probe_pairs=probe_pairs,
                              log_path=str(tmp_path / "log.jsonl"))
    # a dead host degrades to NO values, every seed, without crashing the batch
    assert run["per_sign_values"] == {"KU": {}, "*301": {}}
    assert run["n_seeds_no_values"] == 4


def test_run_lvirgin_isolates_a_raising_generate(monkeypatch, tmp_path):
    def boom(model, prompt, *, options=None, timeout=180, host=None):
        raise RuntimeError("host down")

    monkeypatch.setattr(lvirgin.ablation.ollama_client, "generate", boom)
    probe_pairs = [("KU", lvirgin.ablation.build_form("F1", ["KU", "RO"]))]
    run = lvirgin.run_lvirgin("m", n_seeds=2, probe_pairs=probe_pairs,
                              log_path=str(tmp_path / "log.jsonl"))
    assert len(run["per_seed"]) == 2
    assert all("host down" in (row["error"] or "") for row in run["per_seed"])
    assert run["per_sign_values"] == {"KU": {}}


# --------------------------------------------------------------------------- #
# (d) analyze — excess-over-random control, permutation null, matched-n
# --------------------------------------------------------------------------- #
def _uniform_global_fillers(values, n_fillers=40, per_value=5):
    """Filler (unclassified) signs that make the pooled global distribution ~uniform over `values`.

    They shape the NULL sampling distribution but are not in either class, so they are not scored —
    exactly the role of qwen's bulk output relative to the handful of probed targets.
    """
    return {f"FILL{i}": {v: per_value for v in values} for i in range(n_fillers)}


def test_analyze_excess_zero_for_uniform_positive_for_concentrated():
    values = [f"v{i}" for i in range(8)]
    per = _uniform_global_fillers(values)
    # a CONCENTRATED classified sign: one value every seed -> modal_share 1.0
    per["KCONC"] = {"v0": 40}
    # a UNIFORMLY-DRAWN classified sign: values i.i.d. from the global -> modal_share ≈ expected
    rng = np.random.default_rng(7)
    per["VUNIF"] = dict(Counter(rng.choice(values, size=40)))
    partition = {"L_known": {"KCONC"}, "L_virgin": {"VUNIF"}}

    res = lvirgin.analyze(per, partition, seed=0, n_min=10, n_trials=4000, n_perm=500)
    rows = {r["sign"]: r for r in res["per_sign"]}
    # concentrated >> a random draw of the same size
    assert rows["KCONC"]["excess"] > 0.3
    # uniformly-drawn ≈ a random draw of the same size (the sample-size control works)
    assert abs(rows["VUNIF"]["excess"]) < 0.15


def test_analyze_n1_sign_is_not_mechanically_inflated():
    # a sign seen in ONE seed has modal_share 1.0 by construction; excess must be ~0, not ~1.
    values = [f"v{i}" for i in range(6)]
    per = _uniform_global_fillers(values, n_fillers=20)
    per["SOLO"] = {"v0": 1}
    partition = {"L_known": {"SOLO"}, "L_virgin": set()}
    res = lvirgin.analyze(per, partition, seed=0, n_trials=2000, n_perm=200)
    solo = next(r for r in res["per_sign"] if r["sign"] == "SOLO")
    assert solo["n"] == 1 and solo["modal_share"] == 1.0
    assert solo["expected_modal_share"] == 1.0 and solo["excess"] == 0.0


def test_analyze_headline_gap_permutation_and_matched_n():
    values = [f"v{i}" for i in range(8)]
    per = _uniform_global_fillers(values, n_fillers=30)
    rng = np.random.default_rng(3)
    partition = {"L_known": set(), "L_virgin": set()}
    # 5 known concentrated (high excess) vs 5 virgin uniformly-drawn (excess ≈ 0)
    for j in range(5):
        per[f"K{j}"] = {"v0": 30}
        partition["L_known"].add(f"K{j}")
        per[f"V{j}"] = dict(Counter(rng.choice(values, size=30)))
        partition["L_virgin"].add(f"V{j}")

    res = lvirgin.analyze(per, partition, seed=1, n_min=10, n_trials=2000, n_perm=2000)
    hl = res["headline"]
    assert hl["excess_gap"] > 0.3                       # known >> virgin
    assert hl["permutation_p"] is not None and hl["permutation_p"] < 0.05
    # all signs have n=30 >= n_min, so the matched-n comparison keeps every sign
    mn = res["matched_n"]
    assert mn["n_known"] == 5 and mn["n_virgin"] == 5
    assert mn["excess_gap"] is not None and mn["n_min"] == 10
    # the interpretation flags regurgitation-dominance and NEVER claims correctness
    assert "regurgitation" in res["interpretation"].lower()
    assert "correct" in res["interpretation"].lower()


def test_analyze_zero_gap_when_classes_identical():
    # identical per-sign distributions across classes -> gap exactly 0, permutation not significant
    base = {f"v{i}": 3 for i in range(6)}
    per = {}
    partition = {"L_known": set(), "L_virgin": set()}
    for j in range(4):
        per[f"K{j}"] = dict(base)
        partition["L_known"].add(f"K{j}")
        per[f"V{j}"] = dict(base)
        partition["L_virgin"].add(f"V{j}")
    res = lvirgin.analyze(per, partition, seed=0, n_perm=500)
    assert abs(res["headline"]["excess_gap"]) < 1e-9
    assert res["headline"]["permutation_p"] >= 0.5     # nowhere near significant
    assert "NON-RANDOMLY as known" in res["interpretation"]


def test_analyze_no_power_when_a_class_empty():
    per = {"KCONC": {"v0": 5, "v1": 5}}
    partition = {"L_known": {"KCONC"}, "L_virgin": set()}
    res = lvirgin.analyze(per, partition, seed=0, n_perm=100)
    assert res["headline"]["no_power"] is True
    assert res["headline"]["excess_gap"] is None
    assert res["headline"]["permutation_p"] is None
    assert "NO POWER" in res["interpretation"]


# --------------------------------------------------------------------------- #
# (e) doctrine grep — lvirgin.py never imports scripts.verdict (proposer != grader)
# --------------------------------------------------------------------------- #
def test_lvirgin_does_not_import_verdict():
    src_path = os.path.join(_REPO_ROOT, "scripts", "comparison", "lvirgin.py")
    with open(src_path, encoding="utf-8") as fh:
        tree = ast.parse(fh.read())

    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                imported.add(a.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported.add(node.module)
            for a in node.names:
                imported.add(f"{node.module}.{a.name}" if node.module else a.name)

    assert not any("verdict" in m for m in imported), (
        f"lvirgin.py must not import the verdict machinery; found {sorted(imported)}"
    )
