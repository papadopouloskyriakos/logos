#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the pseudo-decipherment learning curves (scripts/comparison/learning_curves.py),
the information-sufficiency capstone that replaces the withdrawn unicity-distance claim.

These are FAST and run NO CSA / NO GPU (the real CSA sweep is the H100 job; see compute_placement).
They lock in the parts that, if silently wrong, would make the whole capstone meaningless:

  - downsample is deterministic, hits the requested target size exactly, and length-matching shifts
    the lost-word-length distribution toward Linear A (mean ~2.3 signs/word);
  - the chance floor is computed correctly (analytic = 1/n_known; empirical >= analytic; floor RISES
    as the corpus shrinks);
  - the Linear-A locator places Linear-A scale on the size axis and reads the verdict correctly
    (ABOVE_CHANCE / AT_FLOOR / PENDING);
  - a tiny synthetic recovery curve (the torch-free stub) is monotone-ish in corpus size;
  - learning_curves imports NO scripts.verdict (invariant 1/4 — this is a diagnostic, not a verdict);
  - the assembled report carries the UPPER-BOUND honesty framing and makes no phonetic claim.

Run:  python3 -m pytest tests/test_learning_curves.py -q
"""
import ast
import os
import sys

import numpy as np
import pytest

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from scripts.comparison import learning_curves as lc  # noqa: E402


# --------------------------------------------------------------------------- #
# Synthetic known-answer benchmarks (no real corpus, no CSA)
# --------------------------------------------------------------------------- #
def _cipher_benchmark(n_alph=40, n_words=110, corrupt=0.2, seed=7, lo=2, hi=4):
    """A clean(ish) substitution cipher: known word -> lost word via a fixed sign bijection, with a
    per-sign corruption rate (cognates are not identical). The answer is known, so recovery accuracy
    is well-defined and rises with corpus size as the inventory becomes attested."""
    rng = np.random.default_rng(seed)
    known_alph = [chr(0x4E00 + i) for i in range(n_alph)]
    lost_alph = [chr(0xAC00 + i) for i in range(n_alph)]
    sub = dict(zip(known_alph, lost_alph))
    seen, rows, tries = set(), [], 0
    while len(rows) < n_words and tries < n_words * 200:
        tries += 1
        L = int(rng.integers(lo, hi + 1))
        kw = "".join(rng.choice(known_alph, size=L))
        if kw in seen:
            continue
        seen.add(kw)
        lw = "".join((sub[c] if rng.random() > corrupt else rng.choice(lost_alph)) for c in kw)
        rows.append((lw, kw))
    true_map = {v: k for k, v in sub.items()}  # the recovery target: lost sign -> known sign
    return lc.Benchmark("LOST", "KNOWN", rows), true_map


def _bimodal_length_benchmark(seed=3):
    """A benchmark whose lost words are half length-2 and half length-6, so length-matching toward
    Linear A (mean ~2.3) has a measurable effect on the sampled mean."""
    rng = np.random.default_rng(seed)
    alph = [chr(0x4E00 + i) for i in range(20)]
    rows, seen = [], set()
    for target_len in (2, 6):
        made = 0
        while made < 40:
            w = "".join(rng.choice(alph, size=target_len))
            if w in seen:
                continue
            seen.add(w)
            rows.append((w, w))  # known == lost; we only test the lost-length shaping
            made += 1
    return lc.Benchmark("LOST", "KNOWN", rows)


# --------------------------------------------------------------------------- #
# (0) No verdict import — invariant 1/4
# --------------------------------------------------------------------------- #
def test_imports_no_scripts_verdict():
    src = open(lc.__file__, "r", encoding="utf-8").read()
    tree = ast.parse(src)
    bad = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            bad += [a.name for a in node.names if "verdict" in a.name]
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if "verdict" in mod:
                bad.append(mod)
            bad += [a.name for a in node.names if "verdict" in a.name]
    assert not bad, f"learning_curves must not import verdict; found {bad}"
    # (We deliberately do NOT assert on sys.modules: pytest shares it across the whole session and a
    # sibling verdict test may legitimately import scripts.verdict — the AST scan above is the real,
    # module-local invariant.)


# --------------------------------------------------------------------------- #
# (1) parse / stats / size_sweep
# --------------------------------------------------------------------------- #
def test_parse_cog_roundtrip(tmp_path):
    bench = lc.Benchmark("luv", "hit", [("ab", "cd"), ("_", "ef"), ("gh", "_"), ("ij", "kl")])
    p = tmp_path / "x.cog"
    lc.write_cog(bench, str(p))
    back = lc.parse_cog(str(p))
    assert (back.lost_label, back.known_label) == ("luv", "hit")
    assert back.rows == bench.rows
    assert back.n_gold == 2  # ab/cd and ij/kl are gold; _/ef and gh/_ are distractors


def test_gold_rows_excludes_distractors():
    bench = lc.Benchmark("L", "K", [("a", "b"), ("_", "c"), ("d", "_"), ("e", "f")])
    assert bench.n_gold == 2
    assert ("_", "c") not in bench.gold_rows


def test_benchmark_stats_basic():
    bench = lc.Benchmark("L", "K", [("AB", "xy"), ("CDE", "zw")])
    s = lc.benchmark_stats(bench)
    assert s["n_gold_pairs"] == 2
    assert s["n_known_groups"] == 2
    assert s["V_lost"] == 5  # A,B,C,D,E
    assert abs(s["mean_signs_per_word"] - 2.5) < 1e-9  # (2+3)/2


def test_size_sweep_clamped_sorted_unique():
    sw = lc.size_sweep(900, fractions=(1.0, 0.5, 0.1), absolute=(650, 200, 50, 5000))
    assert sw == sorted(sw)
    assert len(sw) == len(set(sw))
    assert all(lc.MIN_SIZE <= s <= 900 for s in sw)
    assert 900 in sw and 650 in sw and 450 in sw and 90 in sw  # 1.0*900, abs650, 0.5*900, 0.1*900
    assert 5000 not in sw  # cannot upsample above full


def test_size_sweep_drops_below_min():
    sw = lc.size_sweep(100, fractions=(0.1,), absolute=(5,))
    assert all(s >= lc.MIN_SIZE for s in sw)


# --------------------------------------------------------------------------- #
# (2) downsample: deterministic, hits target, length-matching
# --------------------------------------------------------------------------- #
def test_downsample_hits_target_size():
    bench, _ = _cipher_benchmark()
    for size in (20, 40, 70, bench.n_gold):
        sub = lc.downsample(bench, size, seed=0)
        assert sub.n_gold == size


def test_downsample_deterministic_same_seed():
    bench, _ = _cipher_benchmark()
    a = lc.downsample(bench, 50, seed=11)
    b = lc.downsample(bench, 50, seed=11)
    assert a.rows == b.rows


def test_downsample_different_seed_differs():
    bench, _ = _cipher_benchmark()
    a = lc.downsample(bench, 50, seed=1)
    b = lc.downsample(bench, 50, seed=2)
    assert a.rows != b.rows  # overwhelmingly likely for 50-of-110


def test_downsample_preserves_subset_membership():
    bench, _ = _cipher_benchmark()
    full_set = set(bench.gold_rows)
    sub = lc.downsample(bench, 30, seed=5)
    assert set(sub.gold_rows).issubset(full_set)


def test_downsample_keeps_proportional_distractors():
    rows = [(f"L{i}", f"K{i}") for i in range(100)]
    rows += [("_", f"D{i}") for i in range(40)]  # 40 distractors
    bench = lc.Benchmark("L", "K", rows)
    sub = lc.downsample(bench, 50, seed=0, keep_distractors=True)
    n_distract = sum(1 for a, b in sub.rows if a == "_" or b == "_")
    assert sub.n_gold == 50
    assert n_distract == 20  # 50/100 * 40
    sub0 = lc.downsample(bench, 50, seed=0, keep_distractors=False)
    assert all(a != "_" and b != "_" for a, b in sub0.rows)


def test_downsample_length_match_shifts_toward_linear_a():
    bench = _bimodal_length_benchmark()
    unmatched = lc.downsample(bench, 30, seed=0, length_match=False)
    matched = lc.downsample(bench, 30, seed=0, length_match=True)
    mu_un = lc.benchmark_stats(unmatched)["mean_signs_per_word"]
    mu_ma = lc.benchmark_stats(matched)["mean_signs_per_word"]
    # Linear A mean ~2.3: the matched draw should be closer to it (and clearly smaller than the
    # unmatched ~4.0 mean of a 2-vs-6 bimodal benchmark).
    assert mu_ma < mu_un
    assert abs(mu_ma - lc.LINEAR_A["mean_signs_per_word"]) < abs(mu_un - lc.LINEAR_A["mean_signs_per_word"])


def test_downsample_length_match_deterministic():
    bench = _bimodal_length_benchmark()
    a = lc.downsample(bench, 30, seed=2, length_match=True)
    b = lc.downsample(bench, 30, seed=2, length_match=True)
    assert a.rows == b.rows


# --------------------------------------------------------------------------- #
# (3) Luo scorer + chance floor
# --------------------------------------------------------------------------- #
def test_luo_accuracy_perfect_map_is_one():
    bench, sub = _cipher_benchmark(corrupt=0.0)  # clean cipher
    acc = lc.luo_accuracy(bench.gold_rows, sub)  # the TRUE sign map
    assert acc == 1.0


def test_luo_accuracy_empty_map_is_low():
    bench, _ = _cipher_benchmark(corrupt=0.0)
    acc = lc.luo_accuracy(bench.gold_rows, {})  # no signs mapped -> all lost words map to ""
    assert acc < 0.1


def test_chance_floor_analytic_is_one_over_nknown():
    pairs = [("AB", "ab"), ("CD", "cd"), ("EF", "ef"), ("GH", "gh")]
    f = lc.chance_floor(pairs, empirical=False)
    assert abs(f["analytic"] - 1.0 / 4) < 1e-12
    assert f["n_known_groups"] == 4


def test_chance_floor_empirical_ge_analytic_and_bounded():
    pairs = [("AB", "ab"), ("CD", "cd"), ("EF", "ef"), ("GH", "gh"), ("AC", "ac"), ("BD", "bd")]
    f = lc.chance_floor(pairs, n_maps=30, seed=0, empirical=True)
    assert 0.0 <= f["empirical_mean"] <= 1.0
    assert f["empirical_mean"] >= f["analytic"] - 1e-9
    assert f["n_maps"] == 30


def test_chance_floor_rises_as_corpus_shrinks():
    bench, _ = _cipher_benchmark(n_words=110)
    big = lc.chance_floor(lc.downsample(bench, 100, seed=0).gold_rows, empirical=False)["analytic"]
    small = lc.chance_floor(lc.downsample(bench, 30, seed=0).gold_rows, empirical=False)["analytic"]
    assert small > big  # fewer candidates -> easier to match by chance -> higher floor


def test_chance_floor_deterministic():
    pairs = [("AB", "ab"), ("CD", "cd"), ("EF", "ef"), ("GH", "gh")]
    a = lc.chance_floor(pairs, n_maps=15, seed=4, empirical=True)
    b = lc.chance_floor(pairs, n_maps=15, seed=4, empirical=True)
    assert a["empirical_mean"] == b["empirical_mean"]


# --------------------------------------------------------------------------- #
# (4) stub recovery + a monotone-ish learning curve
# --------------------------------------------------------------------------- #
def test_stub_recovers_clean_cipher():
    bench, _ = _cipher_benchmark(corrupt=0.0)
    acc = lc.stub_recover(bench.gold_rows, seed=0, min_votes=1)
    assert acc > 0.9


def test_recovery_curve_monotone_in_size():
    bench, _ = _cipher_benchmark(n_alph=40, n_words=110, corrupt=0.2, seed=7)
    # data-hungry stub (a sign needs >=5 attestations to be mapped) so the curve genuinely degrades
    # toward the floor as the corpus shrinks — the phenomenon the capstone must surface.
    rec = lambda sub, seed: lc.stub_recover(sub.gold_rows, seed=seed, min_votes=5)
    sizes = lc.size_sweep(bench.n_gold, fractions=(1.0,), absolute=(90, 70, 55, 40))
    curve = lc.build_curve(bench, sizes=sizes, seeds=(0, 1, 2, 3), recovery=rec, n_floor_maps=0)
    szs = [p["size"] for p in curve]
    accs = [p["recovery_mean"] for p in curve]
    assert all(a is not None for a in accs)
    # monotone-ish: strong positive size/accuracy trend, near-zero violations, clear endpoint gap.
    rho = float(np.corrcoef(szs, accs)[0, 1])
    violations = sum(1 for x, y in zip(accs, accs[1:]) if y < x - 1e-6)
    assert rho > 0.6, f"expected rising curve, rho={rho:.3f} accs={accs}"
    assert violations <= 1, f"too many monotonicity violations: {accs}"
    assert accs[-1] - accs[0] > 0.25, f"endpoint gap too small: {accs}"
    # and every point is at least at its analytic chance floor
    for p in curve:
        assert p["recovery_mean"] >= p["chance_analytic"]


def test_build_curve_aggregates_seeds_and_marks_lower_bound():
    bench, _ = _cipher_benchmark(n_words=60)
    # a recovery callable returning (acc, is_lower_bound=True) to check the flag propagates
    rec = lambda sub, seed: (0.5, True)
    curve = lc.build_curve(bench, sizes=[30, 60], seeds=(0, 1), recovery=rec, n_floor_maps=0)
    assert all(p["recovery_is_lower_bound"] for p in curve)
    assert all(abs(p["recovery_mean"] - 0.5) < 1e-9 for p in curve)


# --------------------------------------------------------------------------- #
# (5) above_chance helper + Linear-A locator
# --------------------------------------------------------------------------- #
def test_above_chance_helper():
    floor = {"analytic": 0.01, "empirical_mean": 0.02, "empirical_std": 0.01}
    assert lc.above_chance(0.8, floor) is True
    assert lc.above_chance(0.02, floor) is False
    assert lc.above_chance(None, floor) is None


def _synthetic_curve(recovery_at):
    """A hand-built curve dict list with a given recovery value at each size (chance fixed low)."""
    out = []
    for size, rec in recovery_at.items():
        out.append({
            "size": size, "recovery_mean": rec, "chance_analytic": 1.0 / size,
            "chance_empirical_mean": 1.0 / size, "chance_empirical_std": 0.0,
        })
    return out


def test_linear_a_locator_above_chance():
    curve = _synthetic_curve({900: 0.85, 650: 0.70, 400: 0.55, 200: 0.40, 100: 0.30})
    loc = lc.linear_a_locator(curve, la_words=650)
    assert loc["verdict"] == "ABOVE_CHANCE"
    assert loc["above_chance"] is True
    assert abs(loc["interp_recovery_acc"] - 0.70) < 1e-9
    assert loc["la_scale_in_swept_range"] is True


def test_linear_a_locator_at_floor():
    # recovery sits ON the chance floor at every size
    curve = [{"size": s, "recovery_mean": 1.0 / s, "chance_analytic": 1.0 / s,
              "chance_empirical_mean": 1.0 / s, "chance_empirical_std": 0.0}
             for s in (900, 650, 400, 200, 100)]
    loc = lc.linear_a_locator(curve, la_words=650)
    assert loc["verdict"] == "AT_FLOOR"
    assert loc["above_chance"] is False


def test_linear_a_locator_at_floor_lower_bound_is_not_definitive():
    # at floor, BUT every recovery point is an under-converged LOWER BOUND -> must NOT emit the
    # definitive AT_FLOOR verdict (a fuller CSA budget could lift it above floor). HIGH-defect guard.
    curve = [{"size": s, "recovery_mean": 1.0 / s, "recovery_is_lower_bound": True,
              "chance_analytic": 1.0 / s, "chance_empirical_mean": 1.0 / s, "chance_empirical_std": 0.0}
             for s in (900, 650, 400, 200, 100)]
    loc = lc.linear_a_locator(curve, la_words=650)
    assert loc["verdict"] == "AT_FLOOR_LOWER_BOUND"
    assert loc["above_chance"] is False
    assert loc["recovery_is_lower_bound"] is True
    assert "lower bound" in loc["reading"].lower()


def test_linear_a_locator_above_chance_survives_lower_bound():
    # a lower bound that ALREADY clears the floor is safe: true acc >= measured >= floor -> ABOVE_CHANCE
    curve = _synthetic_curve({900: 0.85, 650: 0.70, 400: 0.55, 200: 0.40, 100: 0.30})
    for p in curve:
        p["recovery_is_lower_bound"] = True
    loc = lc.linear_a_locator(curve, la_words=650)
    assert loc["verdict"] == "ABOVE_CHANCE"


def test_linear_a_locator_pending_when_no_recovery():
    curve = [{"size": s, "recovery_mean": None, "chance_analytic": 1.0 / s,
              "chance_empirical_mean": 1.0 / s, "chance_empirical_std": 0.0}
             for s in (900, 650, 400, 200, 100)]
    loc = lc.linear_a_locator(curve, la_words=650)
    assert loc["verdict"] == "PENDING_CSA_SWEEP"
    assert loc["above_chance"] is None


def test_linear_a_locator_interpolates_between_points():
    curve = _synthetic_curve({800: 0.80, 500: 0.50})
    loc = lc.linear_a_locator(curve, la_words=650)  # midpoint -> 0.65
    assert abs(loc["interp_recovery_acc"] - 0.65) < 1e-9


def test_linear_a_locator_extrapolation_flag():
    # LA scale (650) ABOVE the full swept benchmark (luv/hit-style, max 100) -> out of range
    curve = _synthetic_curve({100: 0.40, 60: 0.30, 40: 0.25})
    loc = lc.linear_a_locator(curve, la_words=650)
    assert loc["la_scale_in_swept_range"] is False
    # clamps to the nearest endpoint (the largest swept size)
    assert abs(loc["interp_recovery_acc"] - 0.40) < 1e-9


# --------------------------------------------------------------------------- #
# (6) Linear-A scale constants + honesty framing in the report
# --------------------------------------------------------------------------- #
def test_linear_a_scale_constants_sane():
    la = lc.LINEAR_A
    assert la["V_syllabic"] == 92
    assert la["distinct_words_lo"] <= la["distinct_words"] <= la["distinct_words_hi"]
    assert 600 <= la["distinct_words"] <= 700
    assert abs(la["mean_signs_per_word"] - 2.3) < 1e-9
    assert la["n_sign_tokens"] == 5792


def test_upper_bound_statement_is_honest():
    s = lc.UPPER_BOUND_STATEMENT.lower()
    assert "upper bound" in s
    assert "no known cognate" in s
    assert "strictly worse" in s
    assert "no phonetic claim" in s


def test_build_report_carries_honesty_and_no_phonetic_claim():
    # Use synthetic in-memory benchmarks via build_curve directly (no real corpus needed): assemble a
    # minimal report shape by calling build_report on whatever real cog files happen to be present;
    # if none are present (corpus is gitignored), assert the honesty fields on an empty-benchmark run.
    rep = lc.build_report(benchmarks=[], recovery="none", n_floor_maps=0)
    assert rep["no_phonetic_claim"] is True
    assert "UPPER BOUND" in rep["honest_framing"]
    assert "H100" in rep["compute_placement"]
    assert rep["recovery_method"] == "none"


def test_build_report_on_real_benchmark_if_present():
    path = os.path.join(lc._DATA_DIR, lc.KNOWN_ANSWER_BENCHMARKS["linearb-greek"]["cog"])
    if not os.path.isfile(path):
        pytest.skip("linear_b-greek.cog not present (corpus is gitignored)")
    rep = lc.build_report(benchmarks=["linearb-greek"], recovery="none", seeds=(0, 1),
                          n_floor_maps=0)
    b = rep["benchmarks"]["linearb-greek"]
    assert b["full_n_gold"] == 919  # counts are generated, not hand-written (invariant 12)
    assert b["is_primary_linear_a_analog"] is True
    assert b["full_above_linear_a_scale"] is True
    # recovery='none' -> locator is PENDING (the real numbers come from the H100 CSA sweep)
    assert b["linear_a_locator"]["verdict"] == "PENDING_CSA_SWEEP"
    # 650 distinct-word Linear-A scale is INSIDE the swept range of a 919-pair benchmark
    assert b["linear_a_locator"]["la_scale_in_swept_range"] is True
    assert rep["headline"]["primary_benchmark"] == "linearb-greek"


def test_csa_recovery_requires_cfg():
    with pytest.raises(ValueError):
        lc._recovery_fn("csa", None, steps=10, tmp_dir="/tmp")
