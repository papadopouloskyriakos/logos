"""E203 confirmatory extensions (scope frozen in MILESTONE2_CONTROL_ADDENDUM.md @ 5deec1e):
MUS cores via CP-SAT assumption literals; component-wise EXACT model counting; soft-weighted
formulation with sensitivity bands; extended matched nulls; VOI primitives for E202.
No hard pins are ever ADDED in response to UNSAT_GENERIC — cores/weights analyze what exists."""
import hashlib
import json
import math
import os
import sys
from collections import Counter, defaultdict

import numpy as np
from ortools.sat.python import cp_model

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine  # noqa: E402

MASTER = 1336530913


def seed_for(*parts):
    return int(hashlib.sha256(("|".join(map(str, (MASTER, "E203C") + parts))).encode()
                              ).hexdigest()[:8], 16) % 2**31


# ---------------- guarded model: every unary constraint carries an assumption literal ----------
def build_guarded(signs, rel_pairs, unary):
    """unary: dict sign->cell. Returns (model, vars, guards) with rel edges HARD and each unary
    pin/equality enforced iff its guard literal is true."""
    m = cp_model.CpModel()
    var = {s: m.new_int_var(0, engine.ND - 1, f"v{i}") for i, s in enumerate(signs)}
    pairs = [(i, j) for i in range(engine.ND) for j in range(engine.ND) if engine.COMPAT[i, j]]
    for a, b in rel_pairs:
        if a in var and b in var:
            m.add_allowed_assignments([var[a], var[b]], pairs)
    guards = {}
    for s, cell in unary.items():
        if s in var:
            g = m.new_bool_var(f"g_{s}")
            m.add(var[s] == engine.D_IDX[cell]).only_enforce_if(g)
            guards[s] = g
    return m, var, guards


def solve_with_assumptions(m, lits, timeout_s=60):
    sv = cp_model.CpSolver()
    sv.parameters.max_time_in_seconds = timeout_s
    sv.parameters.num_workers = 1
    mm = m  # assumptions live on the model; cleared after each solve
    mm.clear_assumptions()
    mm.add_assumptions(lits)
    st = sv.solve(mm)
    core = []
    if st == cp_model.INFEASIBLE:
        idx = sv.sufficient_assumptions_for_infeasibility()
        core = list(idx)
    mm.clear_assumptions()
    return st, core, sv


def mus_extract(signs, rel_pairs, unary, order_seed=0, timeout_s=60):
    """Deletion-based minimal unsatisfiable subset over the UNARY constraints (rel edges hard).
    Randomized deletion order (order_seed) samples different MUSes."""
    m, var, guards = build_guarded(signs, rel_pairs, unary)
    names = list(guards)
    st, core_idx, sv = solve_with_assumptions(m, [guards[s] for s in names])
    if st != cp_model.INFEASIBLE:
        return {"unsat": False}
    # map core literal indices back to names
    lit_of = {guards[s].index: s for s in names}
    core = [lit_of[i] for i in core_idx if i in lit_of]
    rng = np.random.default_rng(order_seed)
    order = list(rng.permutation(core))
    mus = list(core)
    for s in order:
        trial = [x for x in mus if x != s]
        st, _, _ = solve_with_assumptions(m, [guards[x] for x in trial])
        if st == cp_model.INFEASIBLE:
            mus = trial
    return {"unsat": True, "initial_core_size": len(core), "mus": sorted(mus),
            "mus_size": len(mus)}


# ---------------- component-wise EXACT counting ----------------
def exact_log10_count(signs, rel_pairs, unary, per_component_limit=2 * 10**5, timeout_s=120):
    """Exact solution count: propagate, split into rel-connected components, enumerate each
    coupled component with CP-SAT, multiply. Returns exact log10 unless a component exceeds
    the enumeration limit (then bounds)."""
    inst = engine.Instance(signs, rel_pairs=rel_pairs, pins=unary)
    dom, ok = inst.propagate()
    if not ok:
        return {"consistent": False}
    adj = defaultdict(set)
    for a, b in inst.rel_pairs:
        adj[a].add(b); adj[b].add(a)
    seen, comps = set(), []
    for s in signs:
        if s in seen:
            continue
        comp, stack = [], [s]
        seen.add(s)
        while stack:
            x = stack.pop(); comp.append(x)
            for y in adj[x]:
                if y not in seen:
                    seen.add(y); stack.append(y)
        comps.append(comp)
    log10 = 0.0
    exact = True
    comp_stats = []
    for comp in comps:
        sizes = {s: int(dom[s].sum()) for s in comp}
        prod = 1
        for z in sizes.values():
            prod *= z
        has_edges = any(a in set(comp) and b in set(comp) for a, b in inst.rel_pairs)
        if not has_edges or len(comp) == 1 or all(z == 1 for z in sizes.values()):
            log10 += sum(math.log10(max(z, 1)) for z in sizes.values())
            comp_stats.append({"n": len(comp), "exact": True, "log10": sum(
                math.log10(max(z, 1)) for z in sizes.values())})
            continue
        if prod <= per_component_limit:
            sub_unary = {s: c for s, c in unary.items() if s in set(comp)}
            sub_rel = [(a, b) for a, b in inst.rel_pairs if a in set(comp) and b in set(comp)]
            sub = engine.Instance(comp, rel_pairs=sub_rel, pins=sub_unary)
            n = sub.enumerate_exact(limit=per_component_limit + 1, timeout_s=timeout_s)
            if n["hit_limit"]:
                exact = False
                log10 += sum(math.log10(max(z, 1)) for z in sizes.values())
                comp_stats.append({"n": len(comp), "exact": False, "note": "enum limit"})
            else:
                log10 += math.log10(max(n["n_solutions"], 1))
                comp_stats.append({"n": len(comp), "exact": True,
                                   "log10": math.log10(max(n["n_solutions"], 1))})
        else:
            exact = False
            log10 += sum(math.log10(max(z, 1)) for z in sizes.values())
            comp_stats.append({"n": len(comp), "exact": False, "note": "product too large",
                               "log10_upper": sum(math.log10(max(z, 1)) for z in sizes.values())})
    return {"consistent": True, "log10_count": log10, "exact": exact,
            "n_components": len(comps),
            "largest_component": max(len(c) for c in comps),
            "coupled_components": [c for c in comp_stats if c.get("note") or
                                   (c["n"] > 1 and not c.get("exact", True))][:5]}


# ---------------- soft/weighted formulation ----------------
def soft_solve(signs, rel_pairs, weighted_unary, timeout_s=120, n_optimal_sample=200):
    """Maximize total weight of satisfied unary constraints (rel edges hard). Returns optimum,
    the violated set, and near-optimal multiplicity/marginal structure via enumeration of
    optimal indicator patterns."""
    m, var, guards = build_guarded(signs, rel_pairs,
                                   {s: c for s, (c, w) in weighted_unary.items()})
    m.clear_assumptions()
    m.maximize(sum(int(round(w * 100)) * guards[s]
                   for s, (c, w) in weighted_unary.items() if s in guards))
    sv = cp_model.CpSolver()
    sv.parameters.max_time_in_seconds = timeout_s
    sv.parameters.num_workers = 2
    st = sv.solve(m)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {"status": sv.status_name(st)}
    opt = sv.objective_value
    violated = sorted(s for s in guards if sv.value(guards[s]) == 0)
    # optimal-pattern multiplicity: enumerate distinct guard patterns at the optimum
    m.add(sum(int(round(w * 100)) * guards[s]
              for s, (c, w) in weighted_unary.items() if s in guards) >= int(opt))
    m.clear_objective()

    class Cb(cp_model.CpSolverSolutionCallback):
        def __init__(self, guards):
            super().__init__(); self.pats = set(); self.guards = guards
        def on_solution_callback(self):
            self.pats.add(tuple(sorted(s for s in self.guards
                                       if self.value(self.guards[s]) == 0)))
            if len(self.pats) >= n_optimal_sample:
                self.stop_search()
    cb = Cb(guards)
    sv2 = cp_model.CpSolver()
    sv2.parameters.max_time_in_seconds = timeout_s
    sv2.parameters.enumerate_all_solutions = True
    sv2.parameters.num_workers = 1
    sv2.solve(m, cb)
    pats = cb.pats
    always_violated = set.intersection(*[set(p) for p in pats]) if pats else set(violated)
    return {"status": "OPTIMAL" if st == cp_model.OPTIMAL else "FEASIBLE",
            "optimum_weight": opt / 100.0,
            "n_unary": len(guards),
            "one_optimal_violated_set": violated,
            "n_optimal_violation_patterns_found": len(pats),
            "patterns_capped": len(pats) >= n_optimal_sample,
            "always_violated_across_patterns": sorted(always_violated)}
