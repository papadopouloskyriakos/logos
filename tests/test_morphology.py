"""Tests for Direction A — Linear A morphology / segmentation induction (scripts/comparison/morphology.py).

This module's whole reason to exist is to be CONFOUND-PROOF BY CONSTRUCTION (the contamination-arc
lesson: three metrics turned out to be structural confounds, each caught only by adversarial
verification + null tests). So these tests lock in the guards, not just the happy path:

  (a) a PLANTED productive suffix on many distinct stems across independent inscriptions  -> CONFIRM,
      and the SAME affix on the within-word-shuffled corpus AND in the L_fake fabricated corpus
      -> NOT confirmed (the falsification floor).
  (b) a PLANTED prefix is REPRODUCED by the markov L_fake floor (word-initial == a 1st-order
      sign-statistic) -> the floor is honestly CONSERVATIVE; the shuffle floor still falsifies it.
  (c) a single repeated word -> NO_POWER (the productivity gate; never a fake REFUTE).
  (d) word-boundary recovery F1 BEATS the random-boundary baseline on a synthetic segmentable corpus.
  (e) determinism (a control / verdict that is not reproducible is not a control).
  (f) morphology.py does NOT import scripts.verdict (invariant 2/4 — the model never grades itself).
  (g) NO phonetic-value claim anywhere in the output.
  (h) the pre-registered affix panel is the FROZEN set (no tuning to fit the data).

Fast: tiny fixtures, few null draws. Run:
    python3 -m pytest tests/test_morphology.py -q
"""
import os
import subprocess
import sys

import numpy as np
import pytest

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from scripts.comparison import morphology as M  # noqa: E402

_STEMS = [
    ["KA", "RU", "SI"], ["SI", "DA", "MU"], ["MU", "RE", "NA"], ["NA", "TI", "PA"],
    ["PA", "RO", "QE"], ["QE", "DI", "ZU"], ["ZU", "SU", "KI"], ["KI", "RO", "DA"],
    ["DU", "RI", "TE"], ["WA", "JA", "NU"],
]


def _planted_suffix_corpus(n=36, seed=7):
    """n independent inscriptions, each carrying suffix -XU on a FRESH 3-sign stem (productive)."""
    rng = np.random.default_rng(seed)
    out = []
    for i in range(n):
        s = _STEMS[int(rng.integers(0, len(_STEMS)))]
        other = _STEMS[int(rng.integers(0, len(_STEMS)))]
        out.append(M.Inscription(f"S{i}", "siteX", [list(s) + ["XU"], list(other)]))
    return out


def _planted_prefix_corpus(n=36, seed=11):
    rng = np.random.default_rng(seed)
    out = []
    for i in range(n):
        s = _STEMS[int(rng.integers(0, len(_STEMS)))]
        other = _STEMS[int(rng.integers(0, len(_STEMS)))]
        out.append(M.Inscription(f"P{i}", "siteY", [["QQ"] + list(s), list(other)]))
    return out


_SUFFIX = M.Affix("-xu", "suffix", (("XU",),), "XU", "synthetic-plant")
_PREFIX = M.Affix("qq-", "prefix", (("QQ",),), "QQ", "synthetic-plant")


# --------------------------------------------------------------------------- #
# (a) planted productive suffix -> CONFIRM; shuffle / L_fake -> NOT confirmed (the floor)
# --------------------------------------------------------------------------- #
def test_word_length_distribution_reconciles_fuls_2015():
    """The Direction-A 'short, mostly 1-2-sign words' premise vs Fuls 2015's reported 3.3-sign average:
    BOTH hold on the real corpus, counting different denominators. On the word-tokens the morphology
    test consumes, words are short (median/mode 1, ~76% <=2 signs) — exactly why morphology is not
    separable from bigram order. Fuls's 3.3 is recovered only on DISTINCT MULTI-sign words (~3.07,
    after dropping the ~56% single-sign admin/abbreviation tokens). Generated, not hand-written."""
    d = M.word_length_distribution(M.load_corpus())
    # premise holds for the test's denominator (token-level, scribe divisions)
    assert d["token_median"] == 1 and d["token_mode"] == 1
    assert d["token_mean"] < 2.0
    assert 0.70 < d["pct_len_le2"] < 0.82           # ~76% are <=2 signs
    # Fuls 2015's 3.3 is bracketed by the distinct-multi-sign cut (denominator difference, not conflict)
    assert 2.9 <= d["distinct_mean_ge2"] <= 3.4
    assert d["fuls_2015_reported"] == 3.3
    # the cuts are ordered as expected: all-tokens < distinct < distinct-multi-sign ~ Fuls
    assert d["token_mean"] < d["distinct_mean"] < d["distinct_mean_ge2"]


def test_planted_suffix_confirms_and_floors_do_not():
    corpus = _planted_suffix_corpus()
    codec = M.SignCodec.from_corpus(corpus)
    # deflate as if part of the full 16-affix panel (conservative multiplicity)
    real = M.test_affix(corpus, _SUFFIX, codec, n_trials=16, n_null=80, seed=0)
    assert real["verdict"] == "CONFIRM", real["reason"]
    assert real["has_power"] is True
    assert real["n_distinct_stems"] >= 2
    assert real["observed_rate"] > real["deflated_bar"]

    shuf = M.test_affix(M.shuffle_corpus(corpus, codec, seed=3), _SUFFIX, codec,
                        n_trials=16, n_null=80, seed=0)
    assert shuf["verdict"] != "CONFIRM", shuf["reason"]      # within-word shuffle floor falsifies it

    lf = M.build_lfake_corpus(corpus, codec, seed=3)
    lfv = M.test_affix(lf, _SUFFIX, codec, n_trials=16, n_null=80, seed=0)
    assert lfv["verdict"] != "CONFIRM", lfv["reason"]        # L_fake fabricated floor falsifies it


def test_null_falsification_gate_has_power_on_genuine_suffix():
    corpus = _planted_suffix_corpus()
    codec = M.SignCodec.from_corpus(corpus)
    nf = M.null_falsification(corpus, codec, affixes=(_SUFFIX,), n_null=60, seed=0,
                              n_shuffle=1, n_lfake=1)
    assert nf["real_confirm_rate"] == 1.0
    assert nf["shuffle_confirm_rate"] == 0.0
    assert nf["lfake_confirm_rate"] == 0.0
    assert nf["has_morphology_power"] is True
    assert "NO PHONETIC" in nf["honesty_statement"].upper()


# --------------------------------------------------------------------------- #
# (b) a planted PREFIX is reproduced by the markov L_fake floor (honest conservatism)
# --------------------------------------------------------------------------- #
def test_planted_prefix_reproduced_by_markov_lfake_floor_is_conservative():
    corpus = _planted_prefix_corpus()
    codec = M.SignCodec.from_corpus(corpus)
    real = M.test_affix(corpus, _PREFIX, codec, n_trials=16, n_null=80, seed=0)
    assert real["verdict"] == "CONFIRM"                      # real shows it
    shuf = M.test_affix(M.shuffle_corpus(corpus, codec, 3), _PREFIX, codec,
                        n_trials=16, n_null=80, seed=0)
    assert shuf["verdict"] != "CONFIRM"                      # shuffle (symmetric) still falsifies
    # word-initial == start_counts == a 1st-order statistic the markov L_fake reproduces:
    nf = M.null_falsification(corpus, codec, affixes=(_PREFIX,), n_null=60, seed=0,
                              n_shuffle=1, n_lfake=1)
    assert nf["beats_shuffle_floor"] is True                 # there IS edge structure
    assert nf["lfake_confirm_rate"] > 0.0                    # but the bigram floor reproduces it
    assert nf["has_morphology_power"] is False               # so: do NOT claim morphology
    assert "DO NOT claim morphology" in nf["honesty_statement"]


# --------------------------------------------------------------------------- #
# (c) productivity gate: a single repeated word -> NO_POWER (never a fake REFUTE)
# --------------------------------------------------------------------------- #
def test_repeated_word_is_no_power_not_refute():
    corpus = [M.Inscription(f"R{i}", "siteZ", [["QQ", "KA", "RU"]]) for i in range(8)]
    codec = M.SignCodec.from_corpus(corpus)
    r = M.test_affix(corpus, _PREFIX, codec, n_trials=16, n_null=60, seed=0)
    assert r["verdict"] == "NO_POWER", r["reason"]
    assert r["has_power"] is False
    assert r["n_distinct_stems"] == 1                        # the gate: one stem only -> no productivity


def test_unattested_affix_is_no_power():
    corpus = _planted_suffix_corpus(n=12)
    codec = M.SignCodec.from_corpus(corpus)
    ghost = M.Affix("-zz", "suffix", (("ZZZ",),), "ZZZ", "absent")
    r = M.test_affix(corpus, ghost, codec, n_trials=16, n_null=40, seed=0)
    assert r["verdict"] == "NO_POWER"
    assert r["n_words_bearing"] == 0


# --------------------------------------------------------------------------- #
# affix_residual / productivity logic at the sign level
# --------------------------------------------------------------------------- #
def test_affix_residual_proper_edges_only():
    pre = M.Affix("a-", "prefix", (("A",),), "A", "x")
    suf = M.Affix("-wa", "suffix", (("WA",),), "WA", "x")
    stem = M.Affix("i-*301", "stem", (("I", "*301"),), "I-*301", "x")
    assert M.affix_residual(["A", "KA", "RU"], pre) == ("P", "KA", "RU")
    assert M.affix_residual(["A"], pre) is None              # whole word is not a proper prefix
    assert M.affix_residual(["KA", "WA"], suf) == ("S", "KA")
    # interior stem with variable surrounding affixes
    assert M.affix_residual(["A", "TA", "I", "*301", "WA", "JA"], stem) == ("M", ("A", "TA"), ("WA", "JA"))
    assert M.affix_residual(["I", "*301"], stem) is None     # bare stem (no affix) does not count


# --------------------------------------------------------------------------- #
# (d) word-boundary recovery beats the random baseline on a segmentable corpus
# --------------------------------------------------------------------------- #
def _segmentable_corpus(seed=1):
    rng = np.random.default_rng(seed)
    dictw = [["KA", "RU"], ["SI", "DA", "MU"], ["RE", "NA"], ["TI", "PA"],
             ["RO", "QE", "DI"], ["ZU", "SU"]]

    def mk(site, n):
        out = []
        for i in range(n):
            k = int(rng.integers(2, 5))
            out.append(M.Inscription(f"{site}{i}", site,
                                     [list(dictw[int(rng.integers(0, len(dictw)))]) for _ in range(k)]))
        return out
    return mk("A", 24) + mk("B", 24)


def test_boundary_recovery_beats_random():
    corpus = _segmentable_corpus()
    br = M.boundary_recovery(corpus, seed=0, dp_iters=8, use_morfessor=True)
    rand_f1 = br["random_baseline"]["micro_f1"]
    dp = br["segmenters"]["dp_unigram"]
    assert dp["micro_f1"] > rand_f1
    assert dp["beats_random"] is True
    assert "dp_unigram" in br["usable_segmenters"]
    # Morfessor (installed) should also be usable here
    if "morfessor" in br["segmenters"]:
        assert br["segmenters"]["morfessor"]["beats_random"] is True


def test_dp_segmenter_recovers_known_lexicon():
    """The DP unigram segmenter, trained where 'xy'/'ab' recur as units, recovers the boundaries."""
    seg = M.DPUnigramSegmenter(iters=12, seed=0)
    seg.fit(["xy"] * 15 + ["ab"] * 15 + ["xyab", "abxy", "xyxy", "abab"])  # atoms a,b,x,y as 'signs'
    assert seg.segment("xyxy") == ["xy", "xy"]
    assert seg.segment("xyab") == ["xy", "ab"]


# --------------------------------------------------------------------------- #
# (e) determinism — same seed -> identical verdicts, observed, nulls
# --------------------------------------------------------------------------- #
def test_affix_panel_is_deterministic():
    corpus = _planted_suffix_corpus()
    codec = M.SignCodec.from_corpus(corpus)
    panel = (_SUFFIX, _PREFIX)
    a = M.run_affix_panel(corpus, codec, affixes=panel, n_null=40, seed=0)
    b = M.run_affix_panel(corpus, codec, affixes=panel, n_null=40, seed=0)
    assert a["confirmed_affixes"] == b["confirmed_affixes"]
    for ra, rb in zip(a["affixes"], b["affixes"]):
        assert ra["verdict"] == rb["verdict"]
        assert ra["observed_rate"] == rb["observed_rate"]
        assert ra["null_mean"] == rb["null_mean"]
        assert ra["z"] == rb["z"]


def test_shuffle_corpus_is_deterministic():
    corpus = _planted_suffix_corpus(n=10)
    codec = M.SignCodec.from_corpus(corpus)
    s1 = M.shuffle_corpus(corpus, codec, seed=5)
    s2 = M.shuffle_corpus(corpus, codec, seed=5)
    assert [ins.words for ins in s1] == [ins.words for ins in s2]


def test_sign_codec_round_trip():
    corpus = _planted_suffix_corpus(n=6)
    codec = M.SignCodec.from_corpus(corpus)
    for ins in corpus:
        for w in ins.words:
            assert codec.dec_word(codec.enc_word(w)) == w
        # each sign maps to exactly one char (atomicity)
    assert len(set(codec.to_char.values())) == len(codec.to_char)


# --------------------------------------------------------------------------- #
# (f) does NOT import scripts.verdict  (invariant 2/4)
# --------------------------------------------------------------------------- #
def test_does_not_import_verdict():
    import ast
    src = open(os.path.join(_REPO_ROOT, "scripts", "comparison", "morphology.py"),
               encoding="utf-8").read()
    tree = ast.parse(src)
    for node in ast.walk(tree):                              # no ACTUAL import of verdict (prose is fine)
        if isinstance(node, ast.Import):
            assert all("verdict" not in n.name for n in node.names)
        if isinstance(node, ast.ImportFrom):
            assert "verdict" not in (node.module or "")
            assert all("verdict" not in n.name for n in node.names)
    # robust: importing the module in a fresh interpreter must not pull scripts.verdict
    code = ("import sys; import scripts.comparison.morphology; "
            "assert 'scripts.verdict' not in sys.modules, 'morphology imported scripts.verdict'; "
            "print('clean')")
    out = subprocess.run([sys.executable, "-c", code], cwd=_REPO_ROOT,
                         capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert "clean" in out.stdout


# --------------------------------------------------------------------------- #
# (g) NO phonetic-value claim anywhere; (h) the FROZEN pre-registered panel
# --------------------------------------------------------------------------- #
def test_no_phonetic_claim_present():
    assert "NO phonetic-value" in M.NO_PHONETIC_CLAIM
    corpus = _planted_suffix_corpus(n=8)
    rep = M.build_report(corpus, seed=0, n_null=20, boundary=False, n_shuffle=1, n_lfake=1)
    assert "no_phonetic_claim" in rep
    # the affix rows never carry a phonetic value field
    for r in rep["affix_test"]["affixes"]:
        joined = " ".join(str(v) for v in r.values()).lower()
        assert "phoneme" not in joined and "sound value" not in joined


def test_prereg_affix_panel_is_frozen():
    labels = M.prereg_affix_labels()
    expected = ["i-*301", "a-", "ja-", "ta-", "na-", "t-", "-wa", "-u", "-ja", "-ti", "-nu",
                "-e", "-de", "-ka", "i-", "-te/-ti"]
    assert labels == expected
    assert len(M.PREREG_AFFIXES) == 16
    # the broadened (fuzzy) predictions are flagged as such
    by = {a.affix: a for a in M.PREREG_AFFIXES}
    assert by["t-"].broadened is True and len(by["t-"].sign_seqs) >= 5
    assert by["-te/-ti"].broadened is True
    assert by["i-*301"].edge == "stem"


def test_build_report_smoke():
    corpus = _planted_suffix_corpus(n=10)
    rep = M.build_report(corpus, seed=0, n_null=20, boundary=False, n_shuffle=1, n_lfake=1)
    assert rep["affix_test"]["n_affixes_tested"] == 16
    assert "null_falsification" in rep
    assert "headline" in rep
    # morpheme induction produced an inventory for at least the DP segmenter
    assert "dp_unigram" in rep["morpheme_induction"]["inventories"]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
