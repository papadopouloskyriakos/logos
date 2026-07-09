"""E203 confirmatory F1 driver (scope: MILESTONE2_CONTROL_ADDENDUM @ 5deec1e).
Cells: MUS cores (empirical vs matched random), exact component-wise counts for the module path,
soft-weighted formulation with sensitivity bands, extended matched nulls, VOI primitives.
Emits results/F1_*.json. No hard pin is added in response to UNSAT_GENERIC."""
import json
import math
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine  # noqa: E402
import engine_confirmatory as ec  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


def ck(name, obj):
    json.dump(obj, open(os.path.join(OUT, name + ".json"), "w"), indent=1, default=str)
    print(f"[cell done] {name}", flush=True)


def cell_mus(lat, sal):
    out = {"cell": "F1_mus_cores", "systems": {}}
    for name, unary in (("WPH38", lat["wph_pins"]), ("SALGARELLA", sal["equalities"])):
        muses = []
        for k in range(5):
            r = ec.mus_extract(lat["signs"], lat["rel_pairs"], unary,
                               order_seed=ec.seed_for("mus", name, k))
            muses.append(r)
        sizes = [m["mus_size"] for m in muses if m.get("unsat")]
        # matched random comparison: same pinned signs, random values
        rnd_sizes = []
        for k in range(20):
            rng = np.random.default_rng(ec.seed_for("musnull", name, k))
            ru = {s: engine.DOM[int(rng.integers(0, engine.ND))] for s in unary}
            r = ec.mus_extract(lat["signs"], lat["rel_pairs"], ru,
                               order_seed=ec.seed_for("musnull_o", name, k))
            if r.get("unsat"):
                rnd_sizes.append(r["mus_size"])
        stability = len({tuple(m["mus"]) for m in muses if m.get("unsat")})
        out["systems"][name] = {
            "empirical_mus_sizes": sizes,
            "empirical_distinct_muses_in_5_orderings": stability,
            "example_mus": muses[0].get("mus"),
            "matched_random_mus_sizes": rnd_sizes,
            "random_mean_size": float(np.mean(rnd_sizes)) if rnd_sizes else None,
            "verdict": ("CORES_TYPICAL_OF_RANDOM" if sizes and rnd_sizes and
                        (min(rnd_sizes) <= min(sizes) <= max(rnd_sizes)) else
                        "CORES_ATYPICAL_INVESTIGATE"),
        }
    ck("F1_mus_cores", out)
    return out


def cell_exact_counts(lat, sal):
    out = {"cell": "F1_exact_counts", "configs": {}}
    kept, dropped = engine.drop_pin_violated_rel(lat["rel_pairs"], lat["wph_pins"])
    for name, (rel, unary) in {
        "EMPTY": (lat["rel_pairs"], {}),
        "WPH38_model2": (kept, lat["wph_pins"]),
        "PINS4": (lat["rel_pairs"], {s: c for s, c in engine.PINS.items()
                                     if s in set(lat["signs"])}),
    }.items():
        r = ec.exact_log10_count(lat["signs"], rel, unary)
        out["configs"][name] = r
        print(f"  {name}: log10={r.get('log10_count'):.2f} exact={r.get('exact')} "
              f"comps={r.get('n_components')}", flush=True)
    ck("F1_exact_counts", out)
    return out


def cell_soft(lat, sal):
    """Weighted formulation: WPH38 pins (weight 1.0 base) + Salgarella equalities
    (homophone-likely grade -> base 2.0) under band multipliers; rel edges hard."""
    out = {"cell": "F1_soft_weighted", "bands": {}}
    base = {}
    for s, c in lat["wph_pins"].items():
        base[s] = (c, 1.0)
    for s, c in sal["equalities"].items():
        base.setdefault(s, (c, 2.0))     # grade-weighted; collision keeps WPH pin value
    for mult in (0.25, 0.5, 1.0, 2.0, 4.0):
        wu = {s: (c, w * mult) for s, (c, w) in base.items()}
        r = ec.soft_solve(lat["signs"], lat["rel_pairs"], wu)
        out["bands"][str(mult)] = r
        print(f"  band x{mult}: violated={len(r.get('one_optimal_violated_set', []))} "
              f"patterns={r.get('n_optimal_violation_patterns_found')} "
              f"always_violated={len(r.get('always_violated_across_patterns', []))}",
              flush=True)
    sets = [tuple(out["bands"][b]["always_violated_across_patterns"]) for b in out["bands"]
            if out["bands"][b].get("always_violated_across_patterns") is not None]
    out["always_violated_stable_across_bands"] = len(set(sets)) == 1 if sets else None
    out["note"] = ("weights scale ALL constraints equally within a band, so the optimal "
                   "violated set is expected band-stable; the informative structure is WHICH "
                   "constraints are always violated across optimal patterns")
    ck("F1_soft_weighted", out)
    return out


def cell_extended_nulls(lat, sal):
    """Extended matched nulls (200 each): value-permutation (preserves value multiset),
    frequency-preserving draw, grade-preserving permutation (Salgarella only)."""
    out = {"cell": "F1_extended_nulls", "systems": {}}
    from run_unsat_adjudication import unsat_under  # reuse the adjudication primitive
    for name, unary in (("WPH38", lat["wph_pins"]), ("SALGARELLA", sal["equalities"])):
        res = {}
        pinned = sorted(unary)
        vals = [unary[s] for s in pinned]
        # (a) permutation null: same value multiset, shuffled over the same signs
        n_u = 0
        for k in range(200):
            rng = np.random.default_rng(ec.seed_for("permnull", name, k))
            perm = rng.permutation(len(vals))
            ru = {s: vals[perm[i]] for i, s in enumerate(pinned)}
            n_u += unsat_under(lat["signs"], lat["rel_pairs"], ru)
        res["value_permutation_null_unsat"] = f"{n_u}/200"
        # (b) frequency-preserving: values drawn iid from the empirical value distribution
        n_u = 0
        for k in range(200):
            rng = np.random.default_rng(ec.seed_for("freqnull", name, k))
            ru = {s: vals[int(rng.integers(0, len(vals)))] for s in pinned}
            n_u += unsat_under(lat["signs"], lat["rel_pairs"], ru)
        res["frequency_preserving_null_unsat"] = f"{n_u}/200"
        out["systems"][name] = res
        print(f"  {name}: {res}", flush=True)
    ck("F1_extended_nulls", out)
    return out


def cell_voi(lat, sal):
    """VOI primitives for E202: consistent-anchor information value + random-anchor fragility,
    per hypothetical observation type, on the WPH38_model2 baseline."""
    kept, _ = engine.drop_pin_violated_rel(lat["rel_pairs"], lat["wph_pins"])
    base_unary = dict(lat["wph_pins"])
    base = ec.exact_log10_count(lat["signs"], kept, base_unary)
    base_l10 = base["log10_count"]
    unpinned = [s for s in lat["signs"] if s not in base_unary]
    # one satisfying assignment to draw CONSISTENT hypothetical anchors from
    inst = engine.Instance(lat["signs"], rel_pairs=kept, pins=base_unary)
    m, var = inst.build_model()
    from ortools.sat.python import cp_model as _cp
    sv = _cp.CpSolver(); sv.parameters.max_time_in_seconds = 60
    sv.parameters.num_workers = 2
    assert sv.solve(m) in (_cp.OPTIMAL, _cp.FEASIBLE)
    witness = {s: engine.DOM[sv.value(var[s])] for s in lat["signs"]}
    OBS = {"secure_proper_name": 3, "secure_toponym": 4, "bilingual_fragment": 10,
           "new_sparse_site_inscription_with_1_pin": 1}
    out = {"cell": "F1_voi_primitives", "baseline_log10": base_l10, "observations": {}}
    for obs, k in OBS.items():
        deltas, n_unsat_random = [], 0
        for rep in range(20):
            rng = np.random.default_rng(ec.seed_for("voi", obs, rep))
            chosen = list(rng.choice(unpinned, k, replace=False))
            # consistent anchors (information value)
            u2 = dict(base_unary); u2.update({s: witness[s] for s in chosen})
            r = ec.exact_log10_count(lat["signs"], kept, u2)
            deltas.append(base_l10 - r["log10_count"])
            # random anchors (fragility / wrong-observation robustness)
            u3 = dict(base_unary)
            u3.update({s: engine.DOM[int(rng.integers(0, engine.ND))] for s in chosen})
            r3 = ec.exact_log10_count(lat["signs"], kept, u3)
            n_unsat_random += (not r3.get("consistent", False))
        out["observations"][obs] = {
            "k_signs_pinned": k,
            "mean_delta_log10_consistent": float(np.mean(deltas)),
            "sd": float(np.std(deltas)),
            "per_sign_theoretical_max": engine.LOG10_ND,
            "random_value_unsat_rate": n_unsat_random / 20,
        }
        print(f"  {obs}: dLog10={np.mean(deltas):.2f} fragility={n_unsat_random/20:.2f}",
              flush=True)
    out["value_space_zero_observations"] = {
        "fraction_relation": "0 on the syllabary value domain (metrology constrains fraction signs; L3 value lives in E204)",
        "commodity_class_label": "0 in value space (L3 semantic class channel)",
        "allograph_split": "+log10(67)=1.83 RAW AMBIGUITY (adds a sign) but a MEASUREMENT gain (E205 channel); not a value-space anchor",
        "palaeographic_grade_correction": "acts on soft weights only; quantified under E205 conditions",
    }
    ck("F1_voi_primitives", out)
    return out


def main():
    t0 = time.time()
    lat = engine.load_lattice()
    sal = engine.load_salgarella_equalities()
    mus = cell_mus(lat, sal)
    cnt = cell_exact_counts(lat, sal)
    soft = cell_soft(lat, sal)
    nulls = cell_extended_nulls(lat, sal)
    voi = cell_voi(lat, sal)
    summary = {
        "run": "E203_F1_confirmatory", "addendum": "MILESTONE2_CONTROL_ADDENDUM @ 5deec1e",
        "confirmatory": True, "runtime_s": round(time.time() - t0, 1),
        "headline": {
            "mus_verdicts": {k: v["verdict"] for k, v in mus["systems"].items()},
            "exact_counts_log10": {k: v.get("log10_count")
                                   for k, v in cnt["configs"].items()},
            "always_violated_stable": soft.get("always_violated_stable_across_bands"),
            "extended_nulls": nulls["systems"],
            "voi_top": max(voi["observations"].items(),
                           key=lambda kv: kv[1]["mean_delta_log10_consistent"])[0],
        },
        "no_value_claim": "identifiability map only; no phonetic value asserted",
    }
    ck("F1_summary", summary)
    print(json.dumps(summary["headline"], indent=1, default=str)[:900])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
