#!/usr/bin/env python3
"""Locked properties of scripts/comparison/kuro_null.py (the KU-RO/KI-RO arithmetic-anchor
permutation harness):

(a) NULL-DESIGN LOCK: the shuffle pairs balance units with closing numbers drawn from the
    original multiset (preserved by construction, verified here) and a unit NEVER keeps its
    own closing number (self-pair excluded). On an all-distinct fixture every trial therefore
    scores 0 hits; on a duplicate-value fixture whose two derangements (n=3) each score
    exactly 1 hit, E[hits] under self-exclusion is EXACTLY 1.0 in every trial.
(b) SHADOW-WALKER LOCK: units_with_words is only a word-ordinal annotator — its unit
    skeletons must equal metrology.parse_tablet's output (the module raises on drift; here we
    exercise the commodity-column path that makes drift likely).
(c) KI-RO IDENTICAL DESIGN: the KI-RO leg is the KU-RO parse with the two labels exchanged —
    KI-RO lines close accumulations, KU-RO lines are skipped, symmetric with the primary leg.
(d) NO-NUMERAL EXCLUSION: a closing line without a numeral yields a unit that is excluded
    from the match statistic (no 0==0 pseudo-hits) and counted.
(e) DAMAGE BREAKDOWN: balance-unit lines map to annex word tokens through silver stream word
    order; matched/mismatched units split correctly by damaged-word presence; misaligned or
    absent annex data fail soft (damage fields None, breakdown unavailable).
(f) FRACTIONS ARE COMPARISON-ONLY: the editorial-fraction secondary never changes the primary
    integer statistic.
(g) determinism: identical seed -> identical serialized report; and kuro_null imports nothing
    from scripts.verdict.
(h) REAL-DATA SMOKE (licensed_data + runtime skip): widened scope = 34 KU-RO docs / 12 KI-RO
    docs, 37/35 KU-RO units total/scored with 9 integer-exact, KI-RO 0/7, annex fully aligned
    — the pinned values are script-generated (results/kuro_null.json), then pinned here.
"""
import importlib
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scripts.comparison import kuro_null as K  # noqa: E402
from scripts.comparison import metrology as M  # noqa: E402

SILVER = os.path.join(ROOT, "corpus", "silver", "inscriptions_structured.json")
ANNEX = os.path.join(ROOT, "corpus", "silver", "damage_annex.json")
_have_data = os.path.exists(SILVER) and os.path.exists(ANNEX)
needs_data = pytest.mark.skipif(not _have_data, reason="gitignored silver/annex not present")


# --------------------------------------------------------------------------- #
# token helpers for hand-built tablets (metrology token format)
# --------------------------------------------------------------------------- #
def L(s):
    return {"k": "label", "s": s}


def N(v):
    return {"k": "num", "v": v}


def F(s):
    return {"k": "frac", "s": s}


NL = {"k": "nl"}


def tab(doc, *toks):
    return {"doc": doc, "context": "LMIB", "tokens": list(toks)}


def simple_unit_tab(doc, item_vals, closing):
    """One tablet = one unit: each item on its own line, closed by a KU-RO line."""
    toks = []
    for i, v in enumerate(item_vals):
        toks += [L(f"W{i}"), N(v), NL]
    toks += [L("KU-RO"), N(closing), NL]
    return tab(doc, *toks)


# --------------------------------------------------------------------------- #
# (a) null-design lock
# --------------------------------------------------------------------------- #
class TestNullDesign:
    def test_derangement_is_self_excluded_permutation(self):
        import numpy as np
        rng = np.random.default_rng(7)
        for n in (2, 3, 5, 20):
            for _ in range(50):
                p = K.derangement(rng, n)
                assert sorted(p) == list(range(n))          # multiset/permutation preserved
                assert all(p[i] != i for i in range(n))     # never keeps its own closing number

    def test_derangement_needs_two(self):
        import numpy as np
        with pytest.raises(ValueError):
            K.derangement(np.random.default_rng(0), 1)

    def test_all_distinct_fixture_null_is_zero(self):
        # sums [1,2,3] / closings [1,2,3]: only a self-pair could match -> every trial 0
        hits = K.null_hits([1, 2, 3], [1, 2, 3], n_trials=300, seed=1)
        assert hits == [0] * 300

    def test_expected_hits_under_self_exclusion_exact(self):
        # sums [5,5,7] / closings [5,5,9]: the two derangements of n=3 are (1,2,0) and (2,0,1),
        # each scoring exactly 1 hit -> E[hits] = 1.0 and EVERY trial = 1
        hits = K.null_hits([5, 5, 7], [5, 5, 9], n_trials=400, seed=2)
        assert hits == [1] * 400

    def test_empirical_p_convention(self):
        s = K.null_summary(2, [0, 0, 1, 2, 0])
        assert s["p_empirical_primary"] == round((1 + 1) / (1 + 5), 6)
        assert s["n_trials"] == 5


# --------------------------------------------------------------------------- #
# (b) shadow-walker lock vs metrology.parse_tablet
# --------------------------------------------------------------------------- #
class TestShadowWalker:
    COMM = {"GRA", "OLIV"}

    def _column_tab(self):
        # commodity columns: GRA sub-closed by a tagged KU-RO, then an untagged KU-RO closes OLIV
        return tab("FIX1",
                   L("X"), L("GRA"), N(5), NL,
                   L("Y"), N(3), NL,                      # inherits the GRA column
                   L("KU-RO"), L("GRA"), N(8), NL,        # closes the GRA column: exact
                   L("Z"), L("OLIV"), N(4), NL,
                   L("KU-RO"), N(4), NL)                  # closes the remainder: exact

    def test_skeleton_equals_parse_tablet(self):
        t = self._column_tab()
        units = K.units_with_words(t, self.COMM)          # raises internally on drift
        ref = M.parse_tablet(t, self.COMM)
        assert [u["total_int"] for u in units] == [u["total_int"] for u in ref]
        assert [u["commodity"] for u in units] == [u["commodity"] for u in ref]
        mine_items = [[(iv, list(ff)) for iv, ff in u["items"]] for u in units]
        ref_items = [[(iv, list(ff)) for iv, ff in u["items"]] for u in ref]
        assert mine_items == ref_items
        # word ordinals: unit 1 spans words 0..4 (X GRA Y KU-RO GRA), unit 2 words 5..7
        assert units[0]["word_ords"] == [0, 1, 2, 3, 4]
        assert units[1]["word_ords"] == [5, 6, 7]

    def test_both_units_integer_exact(self):
        units = K.units_with_words(self._column_tab(), self.COMM)
        assert [K.integer_exact(u) for u in units] == [True, True]


# --------------------------------------------------------------------------- #
# (c) KI-RO identical design + (d) no-numeral exclusion
# --------------------------------------------------------------------------- #
class TestKiroDesignAndExclusion:
    def test_kiro_swap_symmetry(self):
        # A 2 / B 3 / KI-RO 5 / C 4 / KU-RO 4
        t = tab("FIX2", L("A"), N(2), NL, L("B"), N(3), NL, L("KI-RO"), N(5), NL,
                L("C"), N(4), NL, L("KU-RO"), N(4), NL)
        # KU-RO leg: KI-RO skipped -> one unit, items 2+3+4=9 vs 4 -> mismatch
        ku = K.analyze_leg([t], set(), "KU-RO", n_trials=0, seed=0)
        assert ku["n_units_scored"] == 1 and ku["observed_integer_exact"] == 0
        assert ku["per_unit"][0]["item_sum_int"] == 9
        # KI-RO leg (labels exchanged): KI-RO closes 2+3=5 exact; KU-RO line skipped
        ki = K.analyze_leg([t], set(), "KI-RO", n_trials=0, seed=0)
        assert ki["n_units_scored"] == 1 and ki["observed_integer_exact"] == 1
        assert ki["per_unit"][0]["item_sum_int"] == 5

    def test_no_numeral_closing_line_excluded(self):
        t = tab("FIX3", L("KU-RO"), NL)                    # closing line, no numeral, no items
        leg = K.analyze_leg([t], set(), "KU-RO", n_trials=0, seed=0)
        assert leg["n_units"] == 1
        assert leg["n_units_scored"] == 0                  # no 0==0 pseudo-hit
        assert leg["n_units_excluded_no_closing_numeral"] == 1
        assert leg["observed_integer_exact"] == 0
        assert leg["null"] is None                         # < 2 scored units


# --------------------------------------------------------------------------- #
# (e) damage breakdown on a fixture annex
# --------------------------------------------------------------------------- #
class TestDamageBreakdown:
    def _fixture(self):
        t1 = tab("D1", L("A"), N(3), NL, L("B"), N(4), NL, L("KU-RO"), N(7), NL)   # exact
        t2 = tab("D2", L("C"), N(2), NL, L("D"), N(3), NL, L("KU-RO"), N(9), NL)   # mismatch
        annex = {"D1": {"types": ["A", "B", "KU-RO"], "w": ["", "T", ""]},
                 "D2": {"types": ["C", "D", "KU-RO"], "w": ["", "L", ""]}}
        return [t1, t2], annex

    def test_split_matched_mismatched_by_damage(self):
        tabs, annex = self._fixture()
        leg = K.analyze_leg(tabs, set(), "KU-RO", n_trials=100, seed=3, annex_docs=annex)
        db = leg["damage_breakdown"]
        assert db["available"] and db["docs_aligned"] == 2 and db["docs_not_aligned"] == []
        assert db["matched"] == {"n": 1, "with_damaged_word_token": 1}
        assert db["mismatched"]["n"] == 1
        assert db["mismatched"]["with_damaged_word_token"] == 1
        assert leg["per_unit"][0]["damage_codes"] == ["T"]
        assert leg["per_unit"][0]["word_ords"] == [0, 1, 2]

    def test_misaligned_and_absent_fail_soft(self):
        tabs, annex = self._fixture()
        annex["D2"] = {"types": ["C", "WRONG", "KU-RO"], "w": ["", "L", ""]}
        leg = K.analyze_leg(tabs, set(), "KU-RO", n_trials=0, seed=0, annex_docs=annex)
        db = leg["damage_breakdown"]
        assert db["docs_not_aligned"] == ["D2"]
        assert leg["per_unit"][1]["damage_codes"] is None
        no_annex = K.analyze_leg(tabs, set(), "KU-RO", n_trials=0, seed=0, annex_docs=None)
        assert no_annex["damage_breakdown"]["available"] is False
        assert all(u["damage_codes"] is None for u in no_annex["per_unit"])


# --------------------------------------------------------------------------- #
# (f) fractions comparison-only
# --------------------------------------------------------------------------- #
class TestFractionSecondary:
    def test_editorial_secondary_never_moves_primary(self):
        # items 1 + ½ + ½ close to 2: integer-mismatch (1 != 2) but editorial-exact
        t = tab("FR1", L("A"), N(1), F("¹⁄₂"), NL, L("B"), N(0), F("¹⁄₂"), NL,
                L("KU-RO"), N(2), NL)
        leg = K.analyze_leg([t], set(), "KU-RO", n_trials=0, seed=0)
        u = leg["per_unit"][0]
        assert u["fraction_bearing"] is True
        assert u["integer_exact"] is False                 # primary: integers only
        assert u["exact_with_editorial_fractions"] is True # secondary panel only
        assert leg["observed_integer_exact"] == 0
        assert leg["fraction_secondary"]["exact_with_editorial_fractions"] == 1

    def test_unglossed_fraction_uncomputable(self):
        t = tab("FR2", L("A"), N(1), F("\U00010746"), NL, L("KU-RO"), N(2), NL)
        leg = K.analyze_leg([t], set(), "KU-RO", n_trials=0, seed=0)
        assert leg["per_unit"][0]["exact_with_editorial_fractions"] is None
        assert leg["fraction_secondary"]["n_editorial_computable"] == 0


# --------------------------------------------------------------------------- #
# (g) determinism + no-verdict-import
# --------------------------------------------------------------------------- #
def test_leg_determinism_on_fixtures():
    tabs = [simple_unit_tab(f"S{i}", [i + 1, i + 2], 2 * i + 3) for i in range(6)]
    a = K.analyze_leg(tabs, set(), "KU-RO", n_trials=250, seed=K.SEED)
    b = K.analyze_leg(tabs, set(), "KU-RO", n_trials=250, seed=K.SEED)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_kuro_null_does_not_import_verdict():
    src = open(os.path.join(ROOT, "scripts", "comparison", "kuro_null.py"),
               encoding="utf-8").read()
    for line in src.splitlines():
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            assert "verdict" not in stripped, f"unexpected verdict import: {line}"
    sys.modules.pop("scripts.verdict", None)
    importlib.reload(K)
    assert "scripts.verdict" not in sys.modules


# --------------------------------------------------------------------------- #
# (h) real-data smoke — pinned from the script-generated results/kuro_null.json
# --------------------------------------------------------------------------- #
@pytest.mark.licensed_data
@needs_data
class TestRealDataSmoke:
    @pytest.fixture(scope="class")
    def report(self):
        return K.run(SILVER, ANNEX, n_trials=200, seed=K.SEED)

    def test_widened_scope_counts(self, report):
        assert report["scope"]["n_kuro_docs"] == 34       # vs metrology's 32 at HT/LM I
        assert report["scope"]["n_kiro_docs"] == 12

    def test_kuro_pinned_counts(self, report):
        k = report["kuro"]
        assert k["n_units"] == 37
        assert k["n_units_scored"] == 35
        assert k["n_units_excluded_no_closing_numeral"] == 2
        assert k["observed_integer_exact"] == 9
        assert k["null"]["p_empirical_primary"] < 0.05
        assert k["observed_integer_exact"] > k["null"]["mean"]

    def test_kiro_own_null_pinned(self, report):
        g = report["kiro"]
        assert [g["observed_integer_exact"], g["n_units_scored"]] == [0, 7]
        assert g["null"]["p_empirical_primary"] == 1.0    # 0/7 is exactly what chance yields

    def test_annex_fully_aligned(self, report):
        assert report["kuro"]["damage_breakdown"]["docs_aligned"] == 34
        assert report["kuro"]["damage_breakdown"]["docs_not_aligned"] == []
        assert report["kiro"]["damage_breakdown"]["docs_aligned"] == 12

    def test_ablation_near_inert(self, report):
        a = report["ablation_no_commodity_sectioning"]
        assert a["delta_units_vs_primary"] == 0
        assert abs(a["delta_observed_vs_primary"]) <= 1
        assert a["null"]["p_empirical_primary"] < 0.05

    def test_wording_discipline_no_translation_claim(self, report):
        blob = json.dumps(report, ensure_ascii=False).lower()
        # 'total' may appear only as metrology's internal field wording / explicit disclaimers,
        # never as a translation; the summation-FUNCTION framing must be present
        assert "summation-function" in blob
        assert "translation claim" in blob                 # the explicit NO-claim line
        for banned in ("means 'total'", 'means "total"', "translates as"):
            assert banned not in blob
