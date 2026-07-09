"""E203 unit + synthetic-recovery tests (prereg tests/ requirement). Run with the campaign venv:
research/logos2/.venv/bin/python -m pytest tests/ -q   (from the experiment dir)"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import engine  # noqa: E402


def test_domain_matches_wph():
    assert engine.ND == 67
    assert abs(engine.H0_BITS - math.log2(67)) < 1e-12
    assert engine.DOM[-2:] == [("p", "u", 2), ("r", "a", 2)]


def test_parse_label_wph_semantics():
    assert engine.parse_label("a") == ("0", "a", 0)
    assert engine.parse_label("RI") == ("r", "i", 0)
    assert engine.parse_label("pu2") == ("p", "u", 2)
    assert engine.parse_label("pa3") == ("p", "a", 0)  # series fallback to base
    assert engine.parse_label("*301") is None
    assert engine.parse_label(None) is None


def test_compat_symmetric_and_sane():
    assert engine.COMPAT.shape == (67, 67)
    assert bool(np.all(engine.COMPAT == engine.COMPAT.T))
    assert bool(np.all(np.diag(engine.COMPAT)))
    # ('d','a') vs ('d','e'): same consonant -> compatible
    assert engine.COMPAT[engine.D_IDX[("d", "a", 0)], engine.D_IDX[("d", "e", 0)]]
    # ('d','a') vs ('k','e'): neither shared -> incompatible
    assert not engine.COMPAT[engine.D_IDX[("d", "a", 0)], engine.D_IDX[("k", "e", 0)]]


def test_propagation_pins_and_rel():
    signs = ["X", "Y"]
    inst = engine.Instance(signs, rel_pairs=[("X", "Y")], pins={"X": ("d", "a", 0)})
    dom, ok = inst.propagate()
    assert ok
    assert dom["X"].sum() == 1
    # Y must share consonant d or vowel a: 5 (d-row) + 13 (a-col) - 1 (d,a) + ('r','a',2) = 18
    assert dom["Y"].sum() == 18


def test_exact_enumeration_small():
    signs = ["X", "Y"]
    inst = engine.Instance(signs, rel_pairs=[("X", "Y")], pins={"X": ("d", "a", 0)})
    res = inst.enumerate_exact()
    assert res["n_solutions"] == 18 and not res["hit_limit"]


def test_count_bound_uncoupled_exactness():
    signs = ["X", "Y", "Z"]
    inst = engine.Instance(signs, rel_pairs=[("X", "Y")], pins={"X": ("d", "a", 0)})
    b = inst.log10_count_bound()
    assert b["consistent"] and b["bound_exact_if_uncoupled"]
    assert abs(b["log10_upper"] - (math.log10(18) + math.log10(67))) < 1e-9


def test_unsat_detected():
    # X pinned ('d','a'), Z pinned ('k','e'), rel X-Z incompatible -> inconsistent
    inst = engine.Instance(["X", "Z"], rel_pairs=[("X", "Z")],
                           pins={"X": ("d", "a", 0), "Z": ("k", "e", 0)})
    dom, ok = inst.propagate()
    assert not ok
    assert inst.feasible(timeout_s=10)["feasible"] is False


def test_drop_pin_violated_rel():
    kept, dropped = engine.drop_pin_violated_rel(
        [("X", "Z"), ("X", "Y")], {"X": ("d", "a", 0), "Z": ("k", "e", 0)})
    assert dropped == [("X", "Z")] and kept == [("X", "Y")]


def test_synthetic_recovery_gate_shape():
    rng = np.random.default_rng(1336530913)
    signs, truth, rel = engine.synthetic_instance(40, 60, rng)
    # planted truth satisfies every rel edge by construction
    for a, b in rel:
        assert engine.COMPAT[engine.D_IDX[truth[a]], engine.D_IDX[truth[b]]]
    # anchored instance is consistent and its backbone contains the anchors
    anchors = {s: truth[s] for s in signs[:10]}
    inst = engine.Instance(signs, rel_pairs=rel, pins=anchors)
    dom, ok = inst.propagate()
    assert ok
    bb = inst.backbone()
    assert bb["consistent"] and bb["n_backbone"] >= len(anchors)


def test_relabeling_invariance_witness():
    rng = np.random.default_rng(7)
    assert engine.relabeling_invariance_check(rng)
