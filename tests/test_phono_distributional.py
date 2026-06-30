"""Tests for the distributional-phonology PILOT (Track-2).

Locks: (a) C/V parsing from GORILA names; (b) the POSITIVE CONTROL has power (detects a planted signal)
— without it a null is uninterpretable; (c) the real result is the DATA-LIMITED NULL (no distribution->
phonetics bridge detectable, and honestly framed as data-limited, not 'no bridge'); (d) no verdict import.
"""
import ast
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts", "comparison"))
from scripts.comparison import phono_distributional as PD  # noqa: E402


def test_cv_label_parses_gorila_names():
    assert PD.cv_label("DA") == ("D", "A")
    assert PD.cv_label("A") == ("", "A")          # pure vowel -> empty consonant
    assert PD.cv_label("NWA") == ("NW", "A")      # cluster consonant
    assert PD.cv_label("QE") == ("Q", "E")
    assert PD.cv_label("*301") is None            # not a vowel-final AB syllabogram
    assert PD.cv_label("") is None


def test_known_labels_cover_the_ab_signs():
    labels = PD.known_cv_labels()
    assert 50 <= len(labels) <= 60                # the ~55 AB syllabograms
    assert all(v in set("AEIOU") for _, v in labels.values())


def test_pilot_is_a_data_limited_null_with_a_powered_test():
    r = PD.run_pilot(n_perm=300, seed=0)
    # the real bridge is NOT detected
    assert r["bridge_detected"] is False
    # ...but the POSITIVE CONTROL has power (it fires at some planted strength) -> the null is
    # interpretable as data-limited, not a broken/always-null test.
    pw = r["power_control"]
    assert pw["test_has_power"] is True
    assert pw["min_firing_strength"] is not None
    # the verdict must frame it honestly as DATA-LIMITED (not "no bridge exists")
    assert "DATA-LIMITED NULL" in r["verdict"] and "DĀMOS" in r["verdict"]
    # truth-layer: no consonant/vowel test clears Šidák 0.05
    assert r["sidak_p_consonant"] > 0.05 and r["sidak_p_vowel"] > 0.05


def test_imports_no_verdict():
    src = open(os.path.join(os.path.dirname(__file__), "..", "scripts", "comparison",
                            "phono_distributional.py"), encoding="utf-8").read()
    tree = ast.parse(src)
    bad = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and "verdict" in node.module:
            bad.append(node.module)
        if isinstance(node, ast.Import):
            bad += [a.name for a in node.names if "verdict" in a.name]
    assert not bad, f"pilot must not import verdict; found {bad}"
