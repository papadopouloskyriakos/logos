#!/usr/bin/env python3
"""tests for scripts/comparison/metrology.py — Direction D metrology constraint-optimization.

No network. The synthetic accounting corpus has PLANTED fraction values and exactly-balancing
tablets so we can assert: (a) the solver recovers the planted values, (b) held-out tablets balance,
(c) the permutation (shuffled sign->value) null does NOT balance held-out — the overfitting guard.
Plus parse correctness (commodity-grouped sub-totals, KU-RO total, word/div/num), determinism, the
no-phonetic-claim invariant, and that metrology imports nothing from scripts.verdict.
"""
import importlib
import json
import os
import sys
from fractions import Fraction

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scripts.comparison import metrology as M  # noqa: E402

PLANTED = {"¹⁄₂": Fraction(1, 2), "¹⁄₄": Fraction(1, 4),
           "³⁄₄": Fraction(3, 4), "¹⁄₃": Fraction(1, 3)}


# ----------------------------------------------------------------------------- #
# token helpers for hand-built tablets
# ----------------------------------------------------------------------------- #
def _tab(doc, lines):
    """lines: list of token-tuples; ('w', s) word, ('n', v) num, ('f', s) frac, ('div',) divider."""
    toks = []
    for ln in lines:
        for tok in ln:
            if tok[0] == "w":
                toks.append({"k": "label", "s": tok[1]})
            elif tok[0] == "n":
                toks.append({"k": "num", "v": tok[1]})
            elif tok[0] == "f":
                toks.append({"k": "frac", "s": tok[1]})
            elif tok[0] == "div":
                toks.append({"k": "div"})
        toks.append({"k": "nl"})
    return {"doc": doc, "context": "LMIB", "tokens": toks}


# ----------------------------------------------------------------------------- #
# fraction-sign recognition
# ----------------------------------------------------------------------------- #
def test_is_fraction_sign_positive():
    assert M.is_fraction_sign("¹⁄₂")
    assert M.is_fraction_sign("³⁄₄")
    assert M.is_fraction_sign("≈ ¹⁄₆")
    assert M.is_fraction_sign("½")
    assert M.is_fraction_sign("double mina")
    assert M.is_fraction_sign("\U00010746")   # Aegean J glyph 𐝆
    assert M.is_fraction_sign("\U00010743")   # Aegean E glyph 𐝃


def test_is_fraction_sign_negative():
    # star-number commodity, em-dash, illegible-number glyph, words, integers are NOT fractions
    assert not M.is_fraction_sign("*308")
    assert not M.is_fraction_sign("—")
    assert not M.is_fraction_sign("\U0001076b")   # illegible NUMBER glyph used on HT67/HT74
    assert not M.is_fraction_sign("GRA")
    assert not M.is_fraction_sign("KU-RO")
    assert not M.is_fraction_sign("12")
    assert not M.is_fraction_sign("")


def test_editorial_value_parses_vulgar():
    assert M.editorial_value("¹⁄₂") == Fraction(1, 2)
    assert M.editorial_value("³⁄₄") == Fraction(3, 4)
    assert M.editorial_value("≈ ¹⁄₆") == Fraction(1, 6)
    assert M.editorial_value("¹⁄₁₆") == Fraction(1, 16)
    assert M.editorial_value("½") == Fraction(1, 2)
    assert M.editorial_value("double mina") is None       # named, no editorial numeric


def test_corazza_mapping_cited_not_assumed():
    # solved values are compared to Corazza letters/values; mapping is via Unicode name / value
    assert M.fraction_letter("\U00010746") == "J"          # 𐝆 -> J
    assert M.fraction_letter("¹⁄₂") == "J"                  # vulgar 1/2 -> J by value
    assert M.corazza_value("¹⁄₂") == Fraction(1, 2)
    assert M.corazza_value("¹⁄₄") == Fraction(1, 4)
    assert M.corazza_value("³⁄₄") == Fraction(3, 4)         # JE = J+E
    assert M.corazza_value("≈ ¹⁄₆") == Fraction(1, 6)       # D
    # CITATION present, values not hardcoded as ground truth in the report
    assert "Corazza" in M.CITATION_CORAZZA and "105214" in M.CITATION_CORAZZA


# ----------------------------------------------------------------------------- #
# accounting parse
# ----------------------------------------------------------------------------- #
def test_parse_kuro_total_with_divider_between_word_and_num():
    # a line item whose recipient is separated from its count by a word-divider must still be counted
    comm = M.load_commodities()
    tab = _tab("Ta", [
        [("w", "PA-DE"), ("div",), ("n", 5), ("f", "³⁄₄")],
        [("w", "A-RU"), ("n", 4), ("f", "¹⁄₄")],
        [("w", "KU-RO"), ("n", 9), ("f", "³⁄₄")],     # 5+4 + (³⁄₄+¹⁄₄) = 9 + 1 ; total 9 ³⁄₄ ...
    ])
    units = M.parse_tablet(tab, comm)
    assert len(units) == 1
    u = units[0]
    assert u["total_int"] == 9 and u["total_fracs"] == ["³⁄₄"]
    # both items captured (the divider did not swallow PA-DE's count)
    assert sorted(v for v, _ in u["items"]) == [4, 5]


def test_parse_commodity_grouped_subtotals():
    # OLIV column and GRA column, each closed by its own commodity-tagged KU-RO subtotal
    comm = M.load_commodities()
    tab = _tab("Tb", [
        [("w", "A-KA"), ("w", "OLIV"), ("n", 10)],
        [("w", "BE-LO"), ("w", "OLIV"), ("n", 5), ("f", "¹⁄₂")],
        [("w", "KU-RO"), ("w", "OLIV"), ("n", 15), ("f", "¹⁄₂")],
        [("w", "CE"), ("w", "GRA"), ("n", 20)],
        [("w", "DE"), ("w", "GRA"), ("n", 4), ("f", "¹⁄₄")],
        [("w", "KU-RO"), ("w", "GRA"), ("n", 24), ("f", "¹⁄₄")],
    ])
    units = M.parse_tablet(tab, comm)
    assert len(units) == 2
    commodities = {u["commodity"] for u in units}
    assert commodities == {"OLIV", "GRA"}
    vals = {"¹⁄₂": Fraction(1, 2), "¹⁄₄": Fraction(1, 4)}
    for u in units:
        assert M.unit_balances(u, vals) is True


def test_inherited_column_commodity_for_untagged_line():
    comm = M.load_commodities()
    tab = _tab("Tc", [
        [("w", "X1"), ("w", "GRA"), ("n", 10)],
        [("w", "X2"), ("n", 6)],                       # no commodity -> inherits GRA column
        [("w", "KU-RO"), ("n", 16)],
    ])
    units = M.parse_tablet(tab, comm)
    assert len(units) == 1
    assert M.unit_balances(units[0], {}) is True       # integer-only balance 10+6==16


# ----------------------------------------------------------------------------- #
# exact rational solver
# ----------------------------------------------------------------------------- #
def test_solve_exact_recovers_known_system():
    labels = ["a", "b"]
    # a + b == 3/4 ; 2a == 1  ->  a=1/2, b=1/4
    rows = [({"a": 1, "b": 1}, Fraction(3, 4)), ({"a": 2}, Fraction(1))]
    sol = M._solve_exact(rows, labels, {"a": Fraction(0), "b": Fraction(0)})
    assert sol == {"a": Fraction(1, 2), "b": Fraction(1, 4)}


def test_solve_exact_detects_inconsistency():
    labels = ["a"]
    rows = [({"a": 1}, Fraction(1, 2)), ({"a": 1}, Fraction(1, 3))]
    assert M._solve_exact(rows, labels, {"a": Fraction(0)}) is None


# ----------------------------------------------------------------------------- #
# synthetic: recovery + held-out + null
# ----------------------------------------------------------------------------- #
def test_synthetic_clean_recovers_planted_values():
    tabs = M.synthetic_corpus(PLANTED, n_tablets=40, seed=1, noise_frac=0.0)
    rep = M.analyze(tabs, k=5, n_perms=200, seed=1)
    solved = {s: v["value"] for s, v in rep["solve"]["solved_values"].items()}
    for sign, val in PLANTED.items():
        assert solved.get(sign) == str(val), f"{sign}: {solved.get(sign)} != {val}"
    # every clean tablet's constraint is satisfied by the recovered system
    assert rep["solve"]["n_constraints_satisfied"] == rep["solve"]["n_fraction_constraints"]


def test_synthetic_heldout_balances_above_null():
    tabs = M.synthetic_corpus(PLANTED, n_tablets=40, seed=1, noise_frac=0.0)
    rep = M.analyze(tabs, k=5, n_perms=300, seed=1)
    assert rep["heldout"]["heldout_fraction_balance_rate"] == 1.0
    assert rep["null"]["separated"] is True
    assert rep["null"]["real_heldout_fraction_balance"] > rep["null"]["null_max"]
    assert rep["null"]["p_value"] < 0.05


def test_synthetic_robust_to_noise():
    # 20% of tablets corrupted (unbalanced); robust solver must still recover the planted values
    tabs = M.synthetic_corpus(PLANTED, n_tablets=44, seed=3, noise_frac=0.2)
    rep = M.analyze(tabs, k=5, n_perms=200, seed=3)
    solved = {s: v["value"] for s, v in rep["solve"]["solved_values"].items()}
    for sign, val in PLANTED.items():
        assert solved.get(sign) == str(val)
    assert rep["null"]["separated"] is True


def test_shuffled_assignment_does_not_balance_heldout():
    # THE overfitting guard, asserted directly: solve on train, then a shuffled sign->value map
    # balances far fewer held-out fraction-bearing units than the true solved map.
    tabs = M.synthetic_corpus(PLANTED, n_tablets=40, seed=1, noise_frac=0.0)
    units = []
    for t in tabs:
        units.extend(M.parse_tablet(t, M.load_commodities()))
    docs = sorted({u["doc"] for u in units})
    test_docs = set(docs[::5])               # hold out every 5th document
    train = [u for u in units if u["doc"] not in test_docs]
    test_fb = [u for u in units if u["doc"] in test_docs and M.is_fraction_bearing(u)]
    train_fb = [u for u in train if M.is_fraction_bearing(u)]
    solved, _ = M.consensus_solve(train_fb, seed=1)
    true_bal = sum(1 for u in test_fb if M.unit_balances(u, solved) is True)
    # a deterministic non-identity shuffle of the value assignment
    labels = sorted(solved)
    rotated = {labels[i]: solved[labels[(i + 1) % len(labels)]] for i in range(len(labels))}
    shuf_bal = sum(1 for u in test_fb if M.unit_balances(u, rotated) is True)
    assert true_bal > shuf_bal
    assert true_bal == len(test_fb)          # true map balances ALL held-out fraction units


# ----------------------------------------------------------------------------- #
# determinism + invariants
# ----------------------------------------------------------------------------- #
def _strip_private(rep):
    return json.loads(json.dumps(rep, default=str))


def test_determinism_same_seed():
    tabs = M.synthetic_corpus(PLANTED, n_tablets=30, seed=7, noise_frac=0.1)
    r1 = _strip_private(M.analyze(tabs, k=4, n_perms=100, seed=7))
    r2 = _strip_private(M.analyze(tabs, k=4, n_perms=100, seed=7))
    assert r1["solve"] == r2["solve"]
    assert r1["heldout"] == r2["heldout"]
    assert r1["null"] == r2["null"]


def test_no_phonetic_claim_flag():
    tabs = M.synthetic_corpus(PLANTED, n_tablets=20, seed=0)
    rep = M.analyze(tabs, k=4, n_perms=50, seed=0)
    assert rep["no_phonetic_claim"] is True
    blob = json.dumps(rep, ensure_ascii=False).lower()
    for banned in ("phonetic", "syllab", "reads as", "language is"):
        # the only allowed mention is the explicit NO-claim caveat
        assert banned not in blob or "no phonetic" in blob


def test_metrology_does_not_import_verdict():
    # no IMPORT statement references verdict (the docstring may mention it in prose)
    src = open(os.path.join(ROOT, "scripts", "comparison", "metrology.py"), encoding="utf-8").read()
    for line in src.splitlines():
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            assert "verdict" not in stripped, f"unexpected verdict import: {line}"
    # and importing the module does not pull verdict into sys.modules
    sys.modules.pop("scripts.verdict", None)
    importlib.reload(M)
    assert "scripts.verdict" not in sys.modules


def test_main_demo_runs():
    rc = M.main(["--demo", "--n-perms", "50", "--seed", "0"])
    assert rc == 0


# ----------------------------------------------------------------------------- #
# real corpus smoke (skipped if the structured silver is absent)
# ----------------------------------------------------------------------------- #
@pytest.mark.skipif(not os.path.exists(M.SILVER), reason="structured silver corpus not present")
def test_real_corpus_smoke():
    rep = M.run(k=5, n_perms=100, seed=0)
    assert rep["corpus"]["site_prefix"] == "HT"
    assert rep["corpus"]["horizon"] == "LMI"
    pc = rep["parse_coverage"]
    assert pc["n_units"] > 0
    assert 0.0 <= pc["integer_balance_rate"] <= 1.0
    # the null is a real probability and the headline is computable
    assert 0.0 <= rep["null"]["p_value"] <= 1.0
    assert isinstance(M.headline(rep), str)
    assert rep["no_phonetic_claim"] is True
