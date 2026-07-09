"""E203 pilot P1 (exploratory) — prereg cc3a73e. Cells: G1 synthetic-recovery gate (fail-closed),
G2 WP-H-domain comparability, marginal module path. Emits results/P1.json (checkpointed per cell).

G1 note (within prereg scope): the gate verifies the ENGINE recovers planted truth when the
instance carries SUFFICIENT information — the synthetic instance therefore uses dense relational
edges (1200) so that 64 correct pins uniquely determine most signs under COMPAT semantics. The
0-anchor arm must stay ambiguous (backbone <=5%). This tests engine correctness, not LA.
"""
import hashlib
import json
import math
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)
MASTER = 1336530913


def seed_for(cell, rep=0):
    h = hashlib.sha256(f"{MASTER}|E203|{cell}|{rep}".encode()).hexdigest()
    return int(h[:8], 16) % 2**31


def checkpoint(name, obj):
    json.dump(obj, open(os.path.join(OUT, name + ".json"), "w"), indent=1, default=str)
    print(f"[cell done] {name}", flush=True)


def g1_gate():
    reps = []
    for rep in range(5):
        rng = np.random.default_rng(seed_for("G1", rep))
        signs, truth, rel = engine.synthetic_instance(163, 1200, rng)
        anchor_signs = list(rng.choice(signs, 64, replace=False))
        anchors = {s: truth[s] for s in anchor_signs}
        inst = engine.Instance(signs, rel_pairs=rel, pins=anchors)
        bb = inst.backbone()
        n_correct = sum(1 for s, c in bb["backbone"].items() if tuple(c) == truth[s])
        n_wrong = len(bb["backbone"]) - n_correct
        # zero-anchor arm
        inst0 = engine.Instance(signs, rel_pairs=rel)
        bb0 = inst0.backbone()
        reps.append({
            "rep": rep, "n_backbone": bb["n_backbone"], "n_correct": n_correct,
            "n_wrong": n_wrong, "frac_planted_recovered": n_correct / 163,
            "zero_anchor_backbone": bb0["n_backbone"],
            "zero_anchor_frac": bb0["n_backbone"] / 163,
            "pass": (n_correct / 163 >= 0.90) and n_wrong == 0 and
                    (bb0["n_backbone"] / 163 <= 0.05),
        })
    ok = all(r["pass"] for r in reps)
    res = {"cell": "GATE_synthetic_recovery", "replicates": reps, "gate_passed": ok,
           "rule": "frac_planted_recovered>=0.90 AND n_wrong==0 AND zero_anchor_frac<=0.05, 5/5"}
    checkpoint("G1_gate", res)
    return res


def g2_wph_comparability(lat):
    pins = lat["wph_pins"]
    kept, dropped = engine.drop_pin_violated_rel(lat["rel_pairs"], pins)
    inst = engine.Instance(lat["signs"], rel_pairs=kept, pins=pins)
    feas = inst.feasible(timeout_s=120)
    cnt = inst.log10_count_bound()
    bb = inst.backbone()
    # also the fully-hard variant (no dropping) for the UNSAT record
    inst_hard = engine.Instance(lat["signs"], rel_pairs=lat["rel_pairs"], pins=pins)
    feas_hard = inst_hard.feasible(timeout_s=120)
    res = {
        "cell": "COMPARE_wph_domain",
        "n_signs": len(lat["signs"]), "n_rel_pairs": len(lat["rel_pairs"]),
        "n_wph_pins": len(pins),
        "hard_everything": feas_hard,
        "model2_semantics": {"rel_dropped_pin_violated": len(dropped),
                             "dropped_pairs": dropped, "feasible": feas,
                             "log10_count_upper": cnt.get("log10_upper"),
                             "bound_exact_if_uncoupled": cnt.get("bound_exact_if_uncoupled"),
                             "n_signs_reduced": cnt.get("n_reduced"),
                             "n_backbone": bb.get("n_backbone")},
        "comparability_statement": {
            "engine_raw_log10_solution_upper": cnt.get("log10_upper"),
            "wph_operational_log10": 63.4,
            "wph_gauge_quotient_log10_lower": 270.0,
            "attribution": (
                "Three DIFFERENT quantities: the engine's raw CSP solution-space upper bound "
                "(hard pins + surviving COMPAT edges only); WP-H's operational ambiguity "
                "(channel-quality-weighted G-surface, many soft channels); WP-H's gauge-"
                "quotient equivalence-class lower bound. The engine bound sits between them "
                "by construction: soft channels absent -> larger than operational; hard pins "
                "fix 38 signs -> smaller than the unpinned gauge count 163*log10(67)=297.7."),
        },
    }
    checkpoint("G2_wph", res)
    return res


def path_cells(lat, sal):
    """Marginal module path on the real lattice signs. Every cell records log10 ambiguity."""
    signs = lat["signs"]
    cells = []

    def measure(name, rel, pins, eqs, note=""):
        kept, dropped = engine.drop_pin_violated_rel(rel, {**pins, **eqs})
        inst = engine.Instance(signs, rel_pairs=kept, pins=pins, equalities=eqs)
        cnt = inst.log10_count_bound()
        cells.append({"path_cell": name, "log10_upper": cnt.get("log10_upper"),
                      "consistent": cnt.get("consistent"),
                      "n_reduced": cnt.get("n_reduced"),
                      "rel_dropped": len(dropped), "note": note})

    base = 163 * engine.LOG10_ND
    cells.append({"path_cell": "EMPTY", "log10_upper": base,
                  "note": "unconstrained baseline 163*log10(67)"})
    # M_STRUCTURE: relabeling-invariance witness -> 0 bits by construction
    rng = np.random.default_rng(seed_for("PATH_structure"))
    cells.append({"path_cell": "+M_STRUCTURE", "log10_upper": base,
                  "relabeling_invariance_witness": engine.relabeling_invariance_check(rng),
                  "note": "graduated relative constraints are value-blind (0 bits); mechanical witness recorded — reproduces the prior relabeling-invariance result in the new formalism"})
    # M_NUMERAL: lattice sign set is syllabary-only -> NO_OP
    cells.append({"path_cell": "+M_NUMERAL", "log10_upper": base,
                  "note": "NO_OP on the WP-H lattice sign set (logograms/numerals excluded upstream); module retained for the full 92-sign inventory run"})
    # M_REL alone
    measure("+M_REL(65 substitution edges)", lat["rel_pairs"], {}, {},
            "COMPAT edges alone (no pins): coupled bound, upper only")
    # + HOM x CONTINUITY (conditional map)
    measure("+M_HOM_CONT(conditional)", lat["rel_pairs"], {}, sal["equalities"],
            "CONDITIONAL on the UNLICENSED continuity hypothesis; Salgarella homophone-grade equalities hard")
    # + 4 pins
    measure("+M_PINS(I,RI,SU,TO)", lat["rel_pairs"],
            {s: c for s, c in engine.PINS.items() if s in set(signs)}, sal["equalities"],
            "adds the four one-toponym-deep pins on top of the conditional map")
    res = {"cell": "PATH_marginal_modules", "cells": cells}
    checkpoint("PATH_cells", res)
    return res


def main():
    t0 = time.time()
    g1 = g1_gate()
    if not g1["gate_passed"]:
        summary = {"pilot": "P1", "verdict": "ENGINE_NOT_VALIDATED",
                   "reason": "G1 synthetic-recovery gate failed (fail-closed): no LA cell interpreted",
                   "g1": g1}
        checkpoint("P1_summary", summary)
        print("VERDICT: ENGINE_NOT_VALIDATED"); return 1
    lat = engine.load_lattice()
    sal = engine.load_salgarella_equalities()
    g2 = g2_wph_comparability(lat)
    path = path_cells(lat, sal)
    summary = {
        "pilot": "P1", "exploratory": True,
        "verdict": "ENGINE_VALIDATED",
        "g1_gate": {"passed": True, "replicates": 5},
        "wph_comparability": g2["comparability_statement"],
        "inputs": {"lattice_sha256": lat["lattice_sha256"],
                    "salgarella_sha256": sal["sha256"],
                    "n_hom_cont_equalities": len(sal["equalities"])},
        "runtime_s": round(time.time() - t0, 1),
        "no_value_claim": ("No phonetic value is asserted. Cells using M_HOM_CONT are "
                            "conditional maps under the UNLICENSED continuity hypothesis."),
    }
    checkpoint("P1_summary", summary)
    print("VERDICT: ENGINE_VALIDATED (pilot, exploratory)")
    print(json.dumps(summary["wph_comparability"], indent=1)[:600])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
