"""E204 metrology run — stack frozen at bc5599f. Scaled-integer CP-SAT enumeration over the
canonical dual-agreed fraction dataset; robust-relation extraction; ablations; 200
matched-notation selection-aware nulls. No phonetic value can result. Seal stays closed."""
import csv
import hashlib
import json
import os
import time
from collections import defaultdict

import numpy as np
from ortools.sat.python import cp_model

SITEMAP = json.load(open(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..",
    "E204R2_residual_canonicalization", "SCHEMA.json")))["site_prefix"]

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "E204R2_residual_canonicalization",
                    "CANONICAL_FRACTION_DATASET.csv")
OUT = os.path.join(HERE, "results_metrology")
os.makedirs(OUT, exist_ok=True)
MASTER = 1336530913
BASES = (60, 120, 240)
ENUM_CAP = 10**6


def seed_for(*p):
    return int(hashlib.sha256(("|".join(map(str, (MASTER, "E204M") + p))).encode()
                              ).hexdigest()[:8], 16) % 2**31


def load_docs():
    rows = list(csv.DictReader(open(DATA)))
    docs = defaultdict(lambda: {"entries": [], "kuro": None, "site": None})
    for r in rows:
        clean = (r["uncertain"] == "0" and r["restored"] == "0" and
                 r["damaged"] == "0" and r.get("anomaly", "0") == "0")
        if not clean or not r["integer"]:
            continue
        d = docs[r["doc_id"]]
        d["site"] = SITEMAP.get(r["doc_id"].split()[0], "?")
        item = (int(r["integer"]), r["fraction_seq"])
        if r["is_kuro"] == "1":
            if d["kuro"] is None:
                d["kuro"] = item
        else:
            d["entries"].append(item)
    arith = {k: v for k, v in docs.items()
             if v["kuro"] is not None and len(v["entries"]) >= 2}
    return arith


def letters_of(docs):
    ls = set()
    for d in docs.values():
        for _, f in d["entries"] + [d["kuro"]]:
            ls.update(f)
    return sorted(ls)


def build_and_enumerate(docs, base, atomic=False, timeout_s=120, enum_cap=ENUM_CAP):
    """CP-SAT: k_s in 1..base-1 per letter (or per atomic sequence); per doc:
    sum(entries)*base == kuro*base in scaled integers. Returns feasibility, count
    (exact if < cap), and the solution matrix for relation extraction (capped)."""
    letters = letters_of(docs)
    units = sorted({f for d in docs.values() for _, f in d["entries"] + [d["kuro"]]
                    if f}) if atomic else letters
    m = cp_model.CpModel()
    kv = {u: m.new_int_var(1, base - 1, f"k_{u}") for u in units}

    def frac_expr(seq):
        if not seq:
            return 0
        if atomic:
            return kv[seq] if seq in kv else 0
        return sum(kv[c] for c in seq)

    for d in docs.values():
        lhs = sum(e_int * base + 0 for e_int, _ in d["entries"])
        lhs_frac = sum(frac_expr(f) for _, f in d["entries"])
        k_int, k_frac = d["kuro"]
        m.add(lhs + lhs_frac == k_int * base + frac_expr(k_frac))
    sv = cp_model.CpSolver()
    sv.parameters.max_time_in_seconds = timeout_s
    sv.parameters.enumerate_all_solutions = True
    sv.parameters.num_workers = 1
    sols = []

    class Cb(cp_model.CpSolverSolutionCallback):
        def __init__(self):
            super().__init__()
            self.n = 0

        def on_solution_callback(self):
            self.n += 1
            if len(sols) < 20000:
                sols.append({u: self.value(kv[u]) for u in units})
            if self.n >= enum_cap:
                self.stop_search()
    cb = Cb()
    status = sv.solve(m, cb)
    return {"units": units, "n_solutions": cb.n, "hit_cap": cb.n >= enum_cap,
            "status": sv.status_name(status), "solutions": sols}


def robust_relations(res):
    """Order and small-ratio relations holding in ALL enumerated solutions."""
    sols, units = res["solutions"], res["units"]
    if not sols:
        return {"feasible": False}
    rel = []
    for i, a in enumerate(units):
        for b in units[i + 1:]:
            if all(s[a] > s[b] for s in sols):
                rel.append(f"{a}>{b}")
            elif all(s[a] < s[b] for s in sols):
                rel.append(f"{b}>{a}")
            for mlt in (2, 3, 4):
                if all(s[a] == mlt * s[b] for s in sols):
                    rel.append(f"{a}={mlt}*{b}")
                if all(s[b] == mlt * s[a] for s in sols):
                    rel.append(f"{b}={mlt}*{a}")
    forced = {u: sols[0][u] for u in units if all(s[u] == sols[0][u] for s in sols)}
    return {"feasible": True, "n_solutions": res["n_solutions"],
            "relations": sorted(rel), "forced_values_scaled": forced}


def null_notation(docs, rep):
    """Matched artificial notation: per-doc structure preserved; the letter->slot mapping is
    permuted globally by a seeded permutation of the letter alphabet."""
    rng = np.random.default_rng(seed_for("null", rep))
    letters = letters_of(docs)
    perm = dict(zip(letters, rng.permutation(letters)))
    out = {}
    for k, d in docs.items():
        out[k] = {"site": d["site"],
                  "entries": [(i, "".join(perm[c] for c in f)) for i, f in d["entries"]],
                  "kuro": (d["kuro"][0], "".join(perm[c] for c in d["kuro"][1]))}
    return out


def main():
    t0 = time.time()
    docs = load_docs()
    letters = letters_of(docs)
    frac_docs = {k: d for k, d in docs.items()
                 if any(f for _, f in d["entries"] + [d["kuro"]])}
    print(f"arithmetic docs: {len(docs)} | with fractions in constraints: {len(frac_docs)} "
          f"| letters: {letters}", flush=True)

    results = {"arithmetic_docs": len(docs), "fraction_constrained_docs": len(frac_docs),
               "letters": letters, "bases": {}}
    for base in BASES:
        r = build_and_enumerate(frac_docs, base)
        rel = robust_relations(r)
        results["bases"][str(base)] = {"n_solutions": r["n_solutions"],
                                       "hit_cap": r["hit_cap"], "status": r["status"],
                                       "relations": rel}
        print(f"  base {base}: {r['n_solutions']} solutions ({r['status']}); "
              f"relations: {rel.get('relations', [])[:8]}", flush=True)
    # atomic compositional arm (base 120)
    r_at = build_and_enumerate(frac_docs, 120, atomic=True)
    results["atomic_arm_base120"] = {"n_solutions": r_at["n_solutions"],
                                     "relations": robust_relations(r_at)}
    # ablations (base 120, compositional): LOO-doc + LOO-site
    base_rel = set(results["bases"]["120"]["relations"].get("relations", []))
    loo = {}
    for k in frac_docs:
        sub = {x: frac_docs[x] for x in frac_docs if x != k}
        rr = robust_relations(build_and_enumerate(sub, 120, timeout_s=60))
        loo[k] = sorted(set(rr.get("relations", [])))
    stable = sorted(base_rel.intersection(*[set(v) for v in loo.values()])) if loo else []
    sites = {d["site"] for d in frac_docs.values()}
    loo_site = {}
    for s in sites:
        sub = {x: d for x, d in frac_docs.items() if d["site"] != s}
        rr = robust_relations(build_and_enumerate(sub, 120, timeout_s=60))
        loo_site[s] = sorted(set(rr.get("relations", [])))
    stable_site = sorted(set(stable).intersection(*[set(v) for v in loo_site.values()])) \
        if loo_site and stable else stable
    results["ablations"] = {"loo_doc_stable_relations": stable,
                            "loo_site_stable_relations": stable_site}
    print(f"  LOO-stable relations: {stable_site}", flush=True)

    # selection-aware nulls: 200 matched notations through the ENTIRE pipeline
    n_feasible, n_ge_relations = 0, 0
    n_obs_rel = len(stable_site)
    for rep in range(200):
        nd = null_notation(frac_docs, rep)
        rr = build_and_enumerate(nd, 120, timeout_s=30, enum_cap=20000)
        rel = robust_relations(rr)
        if rel.get("feasible"):
            n_feasible += 1
            if len(rel.get("relations", [])) >= max(n_obs_rel, 1):
                n_ge_relations += 1
        if (rep + 1) % 50 == 0:
            print(f"  nulls {rep+1}/200 feasible={n_feasible} >=obs_rel={n_ge_relations}",
                  flush=True)
    from scipy.stats import beta
    p_plus1 = (1 + n_ge_relations) / 201
    results["null_battery"] = {
        "n_null": 200, "null_feasible": n_feasible,
        "null_with_ge_observed_relations": n_ge_relations,
        "p_plus1_relations": round(p_plus1, 5),
        "cp95_upper_ge_rate": round(float(beta.ppf(0.95, n_ge_relations + 1,
                                                   200 - n_ge_relations)), 4)
        if n_ge_relations < 200 else 1.0}

    # mechanical verdict
    if not stable_site:
        verdict = ("UNDERDETERMINED_AFTER_ABLATION"
                   if results["bases"]["120"]["n_solutions"] > 0 else "E204_INVALID")
    elif p_plus1 < 0.05:
        verdict = "L3_METROLOGICAL_CLASS_SUPPORTED"
    elif n_ge_relations < 200:
        verdict = "METROLOGICAL_RELATIONS_PARTIAL"
    else:
        verdict = "NULL_NOT_DISTINCTIVE"
    results["verdict"] = verdict
    results["runtime_s"] = round(time.time() - t0, 1)
    results["no_phonetic_value"] = "no phonetic value can graduate from E204 (frozen ceiling L3)"
    json.dump(results, open(os.path.join(OUT, "METROLOGY_RESULTS.json"), "w"), indent=1)
    print("VERDICT:", verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
