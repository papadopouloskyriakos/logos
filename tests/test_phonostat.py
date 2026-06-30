"""Adversarial tests for S_phono (scripts/comparison/phonostat.py) — the WEAK §A.2 statistic.

These lock in the five properties S_phono must have to be a usable surface-plausibility floor:
  (a) DISCRIMINATION  — an in-lexicon-shaped form outscores a random-alphabet string;
  (b) DETERMINISM     — same inputs -> byte-identical float (a control must be reproducible);
  (c) SMOOTHING       — an unseen n-gram / OOV character never yields -inf;
  (d) LENGTH-NORM     — per-symbol scores are comparable across form lengths;
  (e) DEGENERATE      — empty lexicon / empty held-out -> honest NaN, never a misleading finite 0.

Run from anywhere:
    python3 -m pytest tests/test_phonostat.py -q
"""
import math
import os
import sys

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from scripts.comparison import phonostat  # noqa: E402


# A small, fixed Semitic-romanization-shaped lexicon (same transcription space as lexstat.s_lex).
_LEX = [
    "abd", "abyw", "mlky", "twrhm", "bkr", "kab", "lab", "ibrd", "aprd", "adwn",
    "azn", "abn", "babn", "abnm", "abnym", "mlk", "byn", "byt", "sdq", "mlkm",
]


# --------------------------------------------------------------------------- #
# (a) DISCRIMINATION — phonotactically L-shaped > random alphabet string
# --------------------------------------------------------------------------- #
def test_in_lexicon_form_outscores_random_string():
    """A form drawn from the training lexicon must score higher than a same-alphabet random string
    whose n-grams the model has (mostly) never seen. This is the entire point of the statistic."""
    held_real = ["mlky"]                       # verbatim training form: every n-gram is attested
    held_rand = ["zqxjv"]                       # alphabet-plausible but n-gram-implausible
    s_real = phonostat.s_phono(held_real, _LEX, order=3)
    s_rand = phonostat.s_phono(held_rand, _LEX, order=3)
    assert s_real > s_rand, (s_real, s_rand)


def test_discrimination_holds_at_order_2():
    """Order 2 (bigram) is an explicitly supported setting; discrimination must survive there too."""
    s_real = phonostat.s_phono(["abnym"], _LEX, order=2)
    s_rand = phonostat.s_phono(["qjxzv"], _LEX, order=2)
    assert s_real > s_rand, (s_real, s_rand)


def test_per_form_mirrors_mean():
    """s_phono is exactly the mean of s_phono_per_form (the bootstrap/CI hook)."""
    held = ["mlky", "abd", "twrhm"]
    per = phonostat.s_phono_per_form(held, _LEX, order=3)
    assert len(per) == len(held)
    assert math.isclose(phonostat.s_phono(held, _LEX, order=3),
                        math.fsum(per) / len(per), rel_tol=1e-12)


# --------------------------------------------------------------------------- #
# (b) DETERMINISM — identical inputs -> identical float, every run
# --------------------------------------------------------------------------- #
def test_determinism_same_inputs_identical_float():
    held = ["mlky", "qjxzv", "abnym"]
    a = phonostat.s_phono(held, _LEX, order=3)
    b = phonostat.s_phono(held, _LEX, order=3)
    assert a == b                               # byte-identical, not just close
    pa = phonostat.s_phono_per_form(held, _LEX, order=3)
    pb = phonostat.s_phono_per_form(held, _LEX, order=3)
    assert pa == pb


def test_fit_is_pure():
    m1 = phonostat.fit(_LEX, order=3)
    m2 = phonostat.fit(_LEX, order=3)
    assert m1.context_counts == m2.context_counts
    assert m1.context_totals == m2.context_totals
    assert m1.vocab == m2.vocab
    assert m1.vocab_size == m2.vocab_size


# --------------------------------------------------------------------------- #
# (c) SMOOTHING — an unseen n-gram / OOV character is finite, never -inf
# --------------------------------------------------------------------------- #
def test_unseen_ngram_is_finite_not_neg_inf():
    """A held-out form whose every context is unseen must still score a finite log-likelihood."""
    model = phonostat.fit(_LEX, order=3)
    lp = phonostat.logprob_form(model, "qqqq")   # no 'q'-context exists in _LEX
    assert math.isfinite(lp), lp


def test_oov_character_is_finite():
    """A held-out character entirely absent from L's inventory folds onto UNK — finite, not -inf."""
    model = phonostat.fit(_LEX, order=3)
    lp = phonostat.logprob_form(model, "ʔxyz")  # symbols never seen in training
    assert math.isfinite(lp), lp
    # and the whole-statistic path stays finite too
    s = phonostat.s_phono(["ʔxyz"], _LEX, order=3)
    assert math.isfinite(s), s


def test_empty_string_form_scores_finite():
    """An empty form emits only END given the begin context — finite, no crash."""
    model = phonostat.fit(_LEX, order=3)
    assert math.isfinite(phonostat.logprob_form(model, ""))


# --------------------------------------------------------------------------- #
# (d) LENGTH-NORMALIZATION — per-symbol scores comparable across lengths
# --------------------------------------------------------------------------- #
def test_length_normalization_invariant_under_repetition():
    """On a perfectly periodic lexicon, a short and a long form of the SAME texture should have
    near-equal PER-SYMBOL log-likelihood (length-normalization working), while their UN-normalized
    totals diverge with length. This pins the per-symbol invariance the statistic promises."""
    lex = ["ababab", "ababab", "abab", "ababab"]   # a single 'ab' texture
    model = phonostat.fit(lex, order=2)
    short, long = "abab", "abababab"
    pn_short = phonostat.logprob_form(model, short) / phonostat._emitted_len(short)
    pn_long = phonostat.logprob_form(model, long) / phonostat._emitted_len(long)
    # per-symbol scores are close...
    assert abs(pn_short - pn_long) < 0.20, (pn_short, pn_long)
    # ...while the raw totals are NOT (the longer form accumulates more negative log-prob)
    assert phonostat.logprob_form(model, long) < phonostat.logprob_form(model, short)


def test_length_normalization_uses_emitted_len():
    assert phonostat._emitted_len("abc") == 4      # 3 chars + terminal END
    assert phonostat._emitted_len("") == 1         # just END


# --------------------------------------------------------------------------- #
# (e) DEGENERATE — honest NaN, never a misleading finite number
# --------------------------------------------------------------------------- #
def test_empty_lexicon_is_degenerate_nan():
    assert math.isnan(phonostat.s_phono(["abd"], [], order=3))
    model = phonostat.fit([], order=3)
    assert phonostat.is_degenerate(model)
    assert math.isnan(phonostat.logprob_form(model, "abd"))
    # per-form returns a NaN per held-out form (right length, all NaN)
    per = phonostat.s_phono_per_form(["abd", "mlk"], [], order=3)
    assert len(per) == 2 and all(math.isnan(x) for x in per)


def test_empty_heldout_is_degenerate_nan():
    assert math.isnan(phonostat.s_phono([], _LEX, order=3))
    assert phonostat.s_phono_per_form([], _LEX, order=3) == []


def test_report_flags_degenerate_honestly():
    ok = phonostat.s_phono_report(["mlky"], _LEX, order=3)
    assert ok["is_degenerate"] is False and math.isfinite(ok["s_phono"])
    bad = phonostat.s_phono_report(["mlky"], [], order=3)
    assert bad["is_degenerate"] is True and math.isnan(bad["s_phono"])


def test_invalid_params_raise():
    import pytest
    with pytest.raises(ValueError):
        phonostat.fit(_LEX, order=0)
    with pytest.raises(ValueError):
        phonostat.fit(_LEX, order=3, k=0.0)
