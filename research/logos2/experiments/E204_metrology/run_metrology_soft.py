"""E204 metrology — SOFT arm (preregistered in the frozen stack @ bc5599f: 'Soft arm:
maximize #satisfied docs'). The strict arm's joint infeasibility (all bases; all 200 nulls)
established that visible-entry incompleteness, not value choice, blocks exact balancing.
This arm: per-doc satisfiability diagnosis (value-free), max-satisfied-subset optimization,
relations over optimal-subset solutions, and the selection-aware null battery under the SAME
soft pipeline. Seal stays closed. No phonetic value can result."""
import json
import os
import sys
import time

import numpy as np
from ortools.sat.python import cp_model
from scipy.stats import beta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_metrology import (load_docs, letters_of, null_notation, seed_for,  # noqa: E402
                           robust_relations)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results_metrology")


def doc_satisfiable(d, base=120):
    m = cp_model.CpModel()
    letters = sorted({c for _, f in d["entries"] + [d["kuro"]] for c in f})
    kv = {c: m.new_int_var(1, base - 1, c) for c in letters}
    fe = lambda seq: sum(kv[c] for c in seq) if seq else 0
    lhs = sum(i * base for i, _ in d["entries"]) + sum(fe(f) for _, f in d["entries"])
    m.add(lhs == d["kuro"][0] * base + fe(d["kuro"][1]))
    sv = cp_model.CpSolver(); sv.parameters.max_time_in_seconds = 10
    sv.parameters.num_workers = 1
    return sv.solve(m) in (cp_model.OPTIMAL, cp_model.FEASIBLE)


def soft_solve(docs, base=120, timeout_s=180, n_sample=20000):
    letters = letters_of(docs)
    m = cp_model.CpModel()
    kv = {c: m.new_int_var(1, base - 1, c) for c in letters}
    fe = lambda seq: sum(kv[c] for c in seq) if seq else 0
    sat = {}
    for k, d in docs.items():
        b = m.new_bool_var(f"s_{k}")
        lhs = sum(i * base for i, _ in d["entries"]) + sum(fe(f) for _, f in d["entries"])
        m.add(lhs == d["kuro"][0] * base + fe(d["kuro"][1])).only_enforce_if(b)
        sat[k] = b
    m.maximize(sum(sat.values()))
    sv = cp_model.CpSolver(); sv.parameters.max_time_in_seconds = timeout_s
    sv.parameters.num_workers = 2
    st = sv.solve(m)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {"status": sv.status_name(st)}
    n_opt = int(sv.objective_value)
    satisfied = sorted(k for k in sat if sv.value(sat[k]))
    # enumerate value solutions at the optimum for relation extraction
    m.add(sum(sat.values()) >= n_opt)
    m.clear_objective()
    sols = []

    class Cb(cp_model.CpSolverSolutionCallback):
        def __init__(self):
            super().__init__(); self.n = 0
        def on_solution_callback(self):
            self.n += 1
            if len(sols) < n_sample:
                sols.append({c: self.value(kv[c]) for c in letters})
            if self.n >= 10**6:
                self.stop_search()
    cb = Cb()
    sv2 = cp_model.CpSolver(); sv2.parameters.max_time_in_seconds = timeout_s
    sv2.parameters.enumerate_all_solutions = True
    sv2.parameters.num_workers = 1
    sv2.solve(m, cb)
    return {"status": "OPT", "n_satisfied": n_opt, "n_docs": len(docs),
            "satisfied_docs": satisfied, "n_value_solutions_at_opt": cb.n,
            "solutions": sols, "units": letters}


def main():
    t0 = time.time()
    docs = load_docs()
    frac_docs = {k: d for k, d in docs.items()
                 if any(f for _, f in d["entries"] + [d["kuro"]])}
    # per-doc diagnosis (value-free data property)
    diag = {k: doc_satisfiable(d) for k, d in frac_docs.items()}
    n_sat_docs = sum(diag.values())
    print(f"per-doc satisfiable: {n_sat_docs}/{len(frac_docs)}", flush=True)

    r = soft_solve(frac_docs)
    rel = robust_relations({"solutions": r.get("solutions", []),
                            "units": r.get("units", []),
                            "n_solutions": r.get("n_value_solutions_at_opt", 0)})
    print(f"soft optimum: {r.get('n_satisfied')}/{len(frac_docs)} docs; "
          f"{r.get('n_value_solutions_at_opt')} value solutions at opt; "
          f"relations: {rel.get('relations', [])}", flush=True)

    # LOO-doc stability of relations at the soft optimum
    base_rel = set(rel.get("relations", []))
    stable = base_rel
    for k in list(frac_docs):
        sub = {x: frac_docs[x] for x in frac_docs if x != k}
        rr = soft_solve(sub, timeout_s=60, n_sample=5000)
        rl = robust_relations({"solutions": rr.get("solutions", []),
                               "units": rr.get("units", []),
                               "n_solutions": rr.get("n_value_solutions_at_opt", 0)})
        stable &= set(rl.get("relations", []))
    stable = sorted(stable)
    print(f"LOO-stable soft relations: {stable}", flush=True)

    # selection-aware nulls under the SAME soft pipeline
    n_obs = len(stable)
    ge = 0
    opt_fracs = []
    for rep in range(200):
        nd = null_notation(frac_docs, rep)
        rr = soft_solve(nd, timeout_s=30, n_sample=2000)
        rl = robust_relations({"solutions": rr.get("solutions", []),
                               "units": rr.get("units", []),
                               "n_solutions": rr.get("n_value_solutions_at_opt", 0)})
        opt_fracs.append(rr.get("n_satisfied", 0))
        if len(rl.get("relations", [])) >= max(n_obs, 1):
            ge += 1
        if (rep + 1) % 50 == 0:
            print(f"  nulls {rep+1}/200 ge={ge}", flush=True)
    p_plus1 = (1 + ge) / 201

    if not stable:
        verdict = "UNDERDETERMINED_AFTER_ABLATION" if r.get("n_satisfied", 0) else \
                  "NULL_NOT_DISTINCTIVE"
    elif p_plus1 < 0.05:
        verdict = "L3_METROLOGICAL_CLASS_SUPPORTED"
    else:
        verdict = "METROLOGICAL_RELATIONS_PARTIAL" if ge < 200 else "NULL_NOT_DISTINCTIVE"
    out = {
        "arm": "SOFT (preregistered)",
        "strict_arm_reference": "METROLOGY_RESULTS.json (INFEASIBLE all bases + all nulls -> data-completeness property)",
        "per_doc_satisfiable": diag, "n_doc_satisfiable": n_sat_docs,
        "soft_optimum": {"n_satisfied": r.get("n_satisfied"), "n_docs": len(frac_docs),
                          "satisfied_docs": r.get("satisfied_docs"),
                          "n_value_solutions_at_opt": r.get("n_value_solutions_at_opt")},
        "relations_at_opt": rel.get("relations", []),
        "loo_stable_relations": stable,
        "null_battery_soft": {"n": 200, "ge_observed_relations": ge,
                               "p_plus1": round(p_plus1, 5),
                               "null_opt_mean": float(np.mean(opt_fracs)),
                               "cp95_upper": round(float(beta.ppf(.95, ge + 1, 200 - ge)), 4)
                               if ge < 200 else 1.0},
        "verdict": verdict, "runtime_s": round(time.time() - t0, 1),
        "no_phonetic_value": True,
    }
    json.dump(out, open(os.path.join(OUT, "METROLOGY_SOFT_RESULTS.json"), "w"), indent=1)
    print("VERDICT:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
