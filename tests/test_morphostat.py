"""Tests for S_morph — the deflated recurring-morphology statistic (logos comparison-layer §A.2, F.1).

S_morph is the STRONG (Kober) statistic: does L's affix/template inventory recur in the held-out
forms at above-null frequency AND consistently across INDEPENDENT inscriptions? The whole point of
THIS module is the F.1 no-power escape — a short, formulaic corpus may leave S_morph powerless
regardless of truth, and that must be reported as ``is_powered=False`` with a reason, NEVER collapsed
into a misleading low score. These tests lock in:

  (a) a REAL recurring affix across multiple independent inscriptions  -> is_powered=True, score>null
  (b) the same forms with characters shuffled within each form (Nair null) -> score ~ null, no power
  (c) too-sparse / flat / affix-starved corpora                        -> is_powered=False (distinct
      structural reasons, not a low score)
  (d) determinism (a control that is not reproducible is not a control).

Run from anywhere:
    python3 -m pytest tests/test_morphostat.py -q
"""
import os
import sys

import numpy as np

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from scripts.comparison import morphostat, nulls  # noqa: E402


# --------------------------------------------------------------------------- #
# Fixtures: a candidate L lexicon with a clear recurring morphology (prefix ma-,
# suffix -tu / -du / -lu / -ru) seated on varied stems, plus held-out inscriptions
# that bear the SAME affixes on FRESH stems (the systematic, truth-like case).
# --------------------------------------------------------------------------- #
_L_LEXICON = [
    "matabu", "makalu", "maradu", "masidu", "manaru", "kabtu", "rabtu", "sidtu", "naqtu", "baltu",
    "kalu", "radu", "sidu", "naru", "tabu", "kabu", "baru", "qatu", "milu", "gidu",
]

# five INDEPENDENT inscriptions, each carrying the ma- prefix and a -Vu suffix on new stems
_HELDOUT_REAL = [
    ["maluku", "zabtu", "gimru"],
    ["mazaru", "haptu", "kunnu"],
    ["mabiru", "litu", "dagal"],
    ["maruzu", "siptu", "wakal"],
    ["madilu", "nahtu", "pukar"],
]


# --------------------------------------------------------------------------- #
# (a) REAL recurring affix across independent inscriptions -> powered, above null
# --------------------------------------------------------------------------- #
def test_real_recurring_affix_is_powered_and_above_null():
    r = morphostat.s_morph(_HELDOUT_REAL, _L_LEXICON, seed=0)
    assert r["is_powered"] is True, r["reason"]
    assert r["score"] > r["null_mean"]                    # recurs ABOVE chance
    assert r["deflated"] > 0.0
    assert r["z"] >= 2.0
    assert r["n_inscriptions"] == 5
    # the structured result carries every honesty field
    for key in ("score", "null_mean", "null_std", "deflated", "z",
                "n_inscriptions", "n_affixes", "n_heldout_forms", "is_powered", "reason"):
        assert key in r


def test_affix_inventory_recovers_the_real_affixes():
    inv = morphostat.derive_affix_inventory(_L_LEXICON)
    assert ("prefix", "ma") in inv                        # the participle prefix
    assert ("suffix", "tu") in inv                        # a recurring suffix
    # an affix must be a PROPER affix (recurring in >= 2 lexemes, shorter than the word)
    assert all(len(s) <= 2 and kind in ("prefix", "suffix") for kind, s in inv)


# --------------------------------------------------------------------------- #
# (b) Nair within-form shuffle of the SAME forms -> score ~ null, NO spurious power
# --------------------------------------------------------------------------- #
def test_within_form_shuffled_corpus_collapses_to_null():
    """Structureless (within-form shuffled) held-out data must MOSTLY read as no-signal. A single
    shuffle is ONE draw from the null, so the nominal one-sided z>=2 tail (~2-3%) will spuriously clear
    the threshold now and then; the honest invariant is that the SIGNIFICANT FRACTION across many
    shuffle seeds stays at ~the nominal false-positive rate — not that any one arbitrary seed is always
    below (that would be testing noise). Deterministic over the fixed seed set, so non-flaky."""
    trials = 100
    n_sig = 0
    for t in range(trials):
        shuffled = [nulls.within_form_permutation(insc, seed=1000 * t + 311 + k)
                    for k, insc in enumerate(_HELDOUT_REAL)]
        r = morphostat.s_morph(shuffled, _L_LEXICON, seed=7)
        assert r["is_powered"] is r["is_significant"]      # is_powered == (has_power and is_significant)
        if r["is_significant"]:
            n_sig += 1
    # a one-sided z>=2 filter has a ~2-3% nominal false-positive rate; require the empirical rate to sit
    # FAR below "always significant" (and near nominal). This is the calibrated no-power demonstration.
    assert n_sig / trials <= 0.10, f"shuffled-corpus false-positive rate too high: {n_sig}/{trials}"


def test_no_power_is_visibly_distinct_from_a_real_low_score():
    """A genuinely powered-but-low result and a no-power result must never be confused: the powered
    real corpus reports is_powered=True; the shuffled corpus reports is_powered=False. The flag, not
    the magnitude, carries the distinction."""
    powered = morphostat.s_morph(_HELDOUT_REAL, _L_LEXICON, seed=0)
    shuffled = [nulls.within_form_permutation(insc, seed=5 + k)
                for k, insc in enumerate(_HELDOUT_REAL)]
    nopower = morphostat.s_morph(shuffled, _L_LEXICON, seed=0)
    assert powered["is_powered"] is True and nopower["is_powered"] is False
    assert powered["reason"] != nopower["reason"]


# --------------------------------------------------------------------------- #
# (b') Productivity gate: lexical REPETITION must NOT score as recurring MORPHOLOGY
#      (the Kober system-vs-scatter point; verifier-found HIGH defect — the dominant
#      false positive on a short, formulaic corpus). A single formula word copied across
#      inscriptions bears its "affix" on ONE stem and must read as no-signal; the SAME
#      affix on DISTINCT stems across inscriptions is genuine and must read as powered.
# --------------------------------------------------------------------------- #
def test_repeated_formula_word_is_not_productive_morphology():
    """One lexeme copied across five inscriptions -> the affix attaches to a single STEM ->
    is_significant must be False (repetition is not productive morphology)."""
    repeated = [["matabu"], ["matabu"], ["matabu"], ["matabu"], ["matabu"]]
    r = morphostat.s_morph(repeated, _L_LEXICON, seed=0)
    assert r["is_significant"] is False
    assert r["is_powered"] is False


def test_productive_affix_on_distinct_stems_beats_the_repeated_word():
    """Head-to-head: the SAME prefix on FIVE DISTINCT stems across five inscriptions is powered, while
    the identical-count repeated single word is not — the productivity gate is what separates them."""
    productive = [["mabibu"], ["malqbu"], ["maztbu"], ["margbu"], ["maknbu"]]   # ma- on 5 stems
    repeated = [["matabu"]] * 5                                                  # 1 stem, copied
    rp = morphostat.s_morph(productive, _L_LEXICON, seed=0)
    rr = morphostat.s_morph(repeated, _L_LEXICON, seed=0)
    assert rp["is_significant"] is True
    assert rr["is_significant"] is False
    assert rp["score"] > rr["score"]            # productivity is rewarded, repetition is not


def test_has_power_and_is_significant_are_separate_flags():
    """has_power (the corpus CAN test morphology) must be distinct from is_significant (it passed):
    the conflation made the verdict's morph gate clause a tautology. A powered-but-insignificant
    result has has_power=True, is_significant=False — a REAL negative the gate can act on."""
    # a corpus with enough structure to be testable but whose affixes do not productively recur
    nores = [["xabu", "yodu", "zinu"], ["wamu", "qelu", "tovu"], ["pidu", "rolu", "sunu"],
             ["hatu", "gemu", "fibu"], ["jaku", "lemu", "nipu"]]
    r = morphostat.s_morph(nores, _L_LEXICON, seed=3)
    if r["has_power"] and not r["is_significant"]:
        assert r["is_powered"] is False         # is_powered == has_power AND is_significant
    # in all cases the two flags are booleans and is_powered is their conjunction
    assert isinstance(r["has_power"], bool) and isinstance(r["is_significant"], bool)
    assert r["is_powered"] is (r["has_power"] and r["is_significant"])


# --------------------------------------------------------------------------- #
# (c) Too-sparse / flat / affix-starved corpora -> is_powered=False, distinct reasons
# --------------------------------------------------------------------------- #
def test_too_few_inscriptions_is_no_power():
    r = morphostat.s_morph([["maluku", "zabtu"], ["mazaru", "haptu"]], _L_LEXICON, seed=0)
    assert r["is_powered"] is False
    assert "too few independent inscriptions" in r["reason"]


def test_flat_list_fallback_cannot_test_consistency():
    """A flat list of forms is the documented fallback: treated as ONE group, so cross-inscription
    consistency cannot be tested -> no power, by construction."""
    flat = ["maluku", "zabtu", "mazaru", "haptu", "mabiru", "litu"]
    r = morphostat.s_morph(flat, _L_LEXICON, seed=0)
    assert r["is_powered"] is False
    assert r["n_inscriptions"] == 1
    assert "flat held-out list" in r["reason"]


def test_no_affix_inventory_is_no_power():
    """A candidate with no recurring affix above the floor yields an empty inventory -> no power
    (there is no L morphology to look for)."""
    r = morphostat.s_morph([["ab", "cd", "ef"], ["gh", "ij", "kl"], ["mn", "op", "qr"]],
                           ["xy", "zw", "uv"], seed=0)
    assert r["is_powered"] is False
    assert r["n_affixes"] == 0
    assert "too few L affixes" in r["reason"]


def test_empty_heldout_is_degenerate_no_power_not_zero_signal():
    r = morphostat.s_morph([], _L_LEXICON, seed=0)
    assert r["is_powered"] is False
    assert r["n_heldout_forms"] == 0
    assert "no held-out forms" in r["reason"]


# --------------------------------------------------------------------------- #
# (d) Determinism — a statistic that is not reproducible is not a control
# --------------------------------------------------------------------------- #
def test_s_morph_is_deterministic():
    a = morphostat.s_morph(_HELDOUT_REAL, _L_LEXICON, seed=7)
    b = morphostat.s_morph(_HELDOUT_REAL, _L_LEXICON, seed=7)
    assert a == b


def test_different_seed_perturbs_only_the_null_not_the_observed_score():
    """The observed recurrence is a deterministic function of the inputs (no seed); only the null
    draws move with the seed. Score must be identical across seeds; null_mean may differ slightly."""
    a = morphostat.s_morph(_HELDOUT_REAL, _L_LEXICON, seed=1)
    b = morphostat.s_morph(_HELDOUT_REAL, _L_LEXICON, seed=2)
    assert a["score"] == b["score"]
    assert a["n_affixes"] == b["n_affixes"]


def test_derive_affix_inventory_is_deterministic_and_sorted():
    inv1 = morphostat.derive_affix_inventory(_L_LEXICON)
    inv2 = morphostat.derive_affix_inventory(_L_LEXICON)
    assert inv1 == inv2
    assert inv1 == sorted(inv1)


# --------------------------------------------------------------------------- #
# Cross-inscription breadth: clustering inside ONE inscription must NOT score like
# the SAME number of hits spread across many (the independence crux).
# --------------------------------------------------------------------------- #
def test_breadth_counts_distinct_inscriptions_not_raw_occurrences():
    inv = [("suffix", "tu")]
    clustered = [["abtu", "cdtu", "eftu"], ["ghij", "klmn"], ["opqr", "stuv"]]   # 3 hits, 1 insc
    spread = [["abtu", "wxyz"], ["cdtu", "wxyz"], ["eftu", "wxyz"]]              # 3 hits, 3 insc
    rc = morphostat.cross_inscription_recurrence(clustered, inv)
    rs = morphostat.cross_inscription_recurrence(spread, inv)
    assert rs > rc                                         # breadth rewards independent recurrence
    assert rc == 1.0 / 3.0 and rs == 1.0
