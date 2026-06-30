"""Adversarial unit tests for the logos comparison / discipline layer (scripts.comparison).

Locks in the properties the design depends on:
  - L_fake is DETERMINISTIC and contains ZERO real lexical content (the canary guarantee).
  - L_fake is calibrated to the candidate's marginal stats (frequency / length / size).
  - The null generators preserve exactly what they must and destroy what they should, deterministically.
  - S_lex / normalized edit distance are correct on known cases and the banded early-exit agrees
    with the naive DP.

Run from anywhere:
    pytest tests/test_comparison_canary.py -v
"""
import os
import sys

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from scripts.comparison import lfake, nulls, lexstat  # noqa: E402


# --------------------------------------------------------------------------- #
# lexstat — normalized edit distance correctness
# --------------------------------------------------------------------------- #
def test_ned_identical_is_zero():
    assert lexstat.normalized_edit_distance("abd", "abd") == 0.0


def test_ned_disjoint_singletons_is_one():
    assert lexstat.normalized_edit_distance("a", "b") == 1.0


def test_ned_single_substitution_normalised_by_length():
    # one substitution in a 2-char word = 1/2; in a 4-char word = 1/4
    assert abs(lexstat.normalized_edit_distance("ab", "ad") - 0.5) < 1e-9
    assert abs(lexstat.normalized_edit_distance("abcd", "abdd") - 0.25) < 1e-9


def test_ned_capped_matches_naive():
    cases = [("kab", "kab", 0.10), ("abd", "abc", 0.40), ("mlky", "mlk", 0.25),
             ("twrhm", "twrhn", 0.20), ("ab", "xyz", 0.50), ("abcd", "abdd", 0.30)]
    for a, b, eps in cases:
        ned = lexstat.normalized_edit_distance(a, b)
        assert lexstat.ned_capped(a, b, eps) == (ned <= eps + 1e-9), (a, b, eps, ned)


def test_s_lex_known_recall():
    # every held-out form has an exact match in the lexicon -> recall 1.0
    lex = ["abd", "mlk", "twr", "bn"]
    held = ["abd", "mlk"]
    assert lexstat.s_lex(held, lex, 0.0) == 1.0
    # nothing matches a lexicon of unrelated forms at eps=0 -> recall 0.0
    assert lexstat.s_lex(["zzz", "qq"], ["abd", "mlk"], 0.0) == 0.0


def test_deflated_s_lex_clamps_at_zero():
    # raw recall below the null mean => deflated value is 0 (never negative)
    held = ["ab"]
    lex = ["cd", "ef"]
    # null recall is set artificially above the raw recall (0.0 here)
    assert lexstat.deflated_s_lex(held, lex, 0.0, null_recalls=[0.5, 0.6]) == 0.0


# --------------------------------------------------------------------------- #
# lfake — determinism + canary guarantee + calibration
# --------------------------------------------------------------------------- #
_HEB_SAMPLE = [
    "abd", "abyw", "mlky", "twrhm", "bkr", "kab", "lab", "ibrd", "aprd", "adwn",
    "azn", "abn", "babn", "abnm", "abnym", "mlk", "kab", "byn", "byt", "sdq",
]


def test_lfake_deterministic_same_seed():
    cfg = lfake.calibrate_to(_HEB_SAMPLE, mode="semitic")
    g1 = lfake.LFakeGenerator(cfg, seed=42).generate_lexicon()
    g2 = lfake.LFakeGenerator(cfg, seed=42).generate_lexicon()
    assert [e["form"] for e in g1] == [e["form"] for e in g2]


def test_lfake_different_seeds_differ():
    cfg = lfake.calibrate_to(_HEB_SAMPLE, mode="semitic")
    g1 = [e["form"] for e in lfake.LFakeGenerator(cfg, seed=1).generate_lexicon()]
    g2 = [e["form"] for e in lfake.LFakeGenerator(cfg, seed=2).generate_lexicon()]
    assert g1 != g2


def test_lfake_zero_real_lexical_content():
    # the canary guarantee: NO generated form appears in the candidate lexicon
    cfg = lfake.calibrate_to(_HEB_SAMPLE, mode="semitic")
    cand = set(_HEB_SAMPLE)
    g = lfake.LFakeGenerator(cfg, seed=0).generate_lexicon()
    for e in g:
        assert e["form"] not in cand, e
        assert e["invented"] is True
    rep = lfake.divergence_report([e["form"] for e in g], _HEB_SAMPLE, cfg)
    assert rep["lexical_overlap_rate"] == 0.0


def test_lfake_all_unique():
    cfg = lfake.calibrate_to(_HEB_SAMPLE, mode="semitic")
    g = [e["form"] for e in lfake.LFakeGenerator(cfg, seed=7).generate_lexicon()]
    assert len(g) == len(set(g))


def test_lfake_calibration_matches_marginal_stats():
    # phoneme frequencies + length distribution + lexicon size should be close (small TV) even on a
    # small 20-form sample (calibration is much tighter on the full corpus — see run_canary.py).
    cfg = lfake.calibrate_to(_HEB_SAMPLE, mode="semitic")
    g = lfake.LFakeGenerator(cfg, seed=3).generate_lexicon()
    rep = lfake.divergence_report([e["form"] for e in g], _HEB_SAMPLE, cfg)
    assert rep["phoneme_freq_TV"] < 0.35, rep["phoneme_freq_TV"]
    assert rep["length_TV"] < 0.40, rep["length_TV"]
    # lexicon size honoured
    assert rep["n_generated"] == cfg.lexicon_size


def test_lfake_modes_all_run():
    for mode in ("semitic", "cv", "markov", "auto"):
        cfg = lfake.calibrate_to(_HEB_SAMPLE, mode=mode)
        g = lfake.LFakeGenerator(cfg, seed=0).generate_lexicon(n=8)
        assert len(g) == 8 and all(e["form"] for e in g), mode


def test_lfake_rejection_reported_on_tiny_inventory():
    # a 1-char inventory forces real-form collisions; rejection sampling must still return
    # INVENTED, UNIQUE output without crashing (it may return fewer than requested when the
    # inventory cannot support that many distinct invented forms).
    cfg = lfake.calibrate_to(["a", "aa", "aaa"], mode="semitic")
    gen = lfake.LFakeGenerator(cfg, seed=0)
    out = gen.generate_lexicon(n=4)
    forms = [e["form"] for e in out]
    assert len(forms) >= 1                       # never crashes; always returns something invented
    assert len(forms) == len(set(forms))         # unique
    assert all(f not in {"a", "aa", "aaa"} for f in forms)


# --------------------------------------------------------------------------- #
# nulls — invariants + determinism
# --------------------------------------------------------------------------- #
_NULL_FORMS = ["abd", "mlky", "twrhm", "bkr", "ab", "nym", "kab", "abd"]


def test_packard_preserves_lengths():
    out = nulls.packard_banded_permutation(_NULL_FORMS, seed=0)
    assert [len(w) for w in out] == [len(w) for w in _NULL_FORMS]


def test_packard_preserves_character_multiset():
    # a within-band bijection relabels chars; it preserves the MULTISET OF COUNTS (which label has
    # which count is permuted, but the sorted frequency list is invariant) and every word length.
    from collections import Counter
    out = nulls.packard_banded_permutation(_NULL_FORMS, seed=0)
    assert sorted(Counter("".join(out)).values()) == sorted(Counter("".join(_NULL_FORMS)).values())
    assert sorted(Counter("".join(out)).elements())[:0] == []  # types ok


def test_packard_deterministic():
    a = nulls.packard_banded_permutation(_NULL_FORMS, seed=11)
    b = nulls.packard_banded_permutation(_NULL_FORMS, seed=11)
    assert a == b


def test_packard_destroys_identity_when_able():
    # on a rich-enough inventory the relabelling must change at least one form
    out = nulls.packard_banded_permutation(_NULL_FORMS, seed=3)
    assert out != list(_NULL_FORMS)


def test_random_lexeme_stays_in_pool():
    out = nulls.random_lexeme_null(_NULL_FORMS, n=50, seed=0)
    pool = set(_NULL_FORMS)
    assert all(w in pool for w in out)
    assert len(out) == 50


def test_within_form_preserves_multiset_per_form():
    from collections import Counter
    out = nulls.within_form_permutation(_NULL_FORMS, seed=0)
    assert len(out) == len(_NULL_FORMS)
    for src, dst in zip(_NULL_FORMS, out):
        assert Counter(src) == Counter(dst), (src, dst)
        assert len(src) == len(dst)


def test_within_form_deterministic():
    a = nulls.within_form_permutation(_NULL_FORMS, seed=5)
    b = nulls.within_form_permutation(_NULL_FORMS, seed=5)
    assert a == b


def test_null_distribution_runs_all_three():
    # smoke: the assembled null distribution yields one draw per generator per call
    def stat(held, L):
        return lexstat.s_lex(held, L, 0.25)
    out = nulls.null_distribution(stat, _NULL_FORMS, _NULL_FORMS, seed=0,
                                  n_packard=2, n_random=2, n_within=2)
    assert set(out) == {"packard", "random_lexeme", "within_form"}
    assert all(len(v) == 2 for v in out.values())
