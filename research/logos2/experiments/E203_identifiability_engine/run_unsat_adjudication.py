"""E203 UNSAT adjudication cell (prereg-required): every UNSAT discovery is adjudicated against
>=200 matched random pin-sets (WP-N protocol) before any interpretation. Matched = same pinned
sign set and same constraint graph; random = values drawn uniformly from DOM per pinned sign.
UNSAT_SPECIFIC only if the matched-null UNSAT rate < 5% (exact CP95 upper reported, plus-one MC
correction on the p-value). Emits results/UNSAT_adjudication.json.
"""
import hashlib
import json
import os
import sys

import numpy as np
from scipy.stats import beta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
MASTER = 1336530913
N_NULL = 200


def seed_for(cell, rep):
    return int(hashlib.sha256(f"{MASTER}|E203|{cell}|{rep}".encode()).hexdigest()[:8], 16) % 2**31


def unsat_under(signs, rel_pairs, assignment):
    """UNSAT test for a full hard system (no edge dropping): AC wipeout is decisive UNSAT;
    otherwise CP-SAT decides."""
    inst = engine.Instance(signs, rel_pairs=rel_pairs, pins=assignment)
    dom, ok = inst.propagate()
    if not ok:
        return True
    return not inst.feasible(timeout_s=60)["feasible"]


def adjudicate(name, signs, rel_pairs, pinned_signs, observed_unsat):
    n_unsat = 0
    for rep in range(N_NULL):
        rng = np.random.default_rng(seed_for(f"NULL_{name}", rep))
        rand_assign = {s: engine.DOM[int(rng.integers(0, engine.ND))] for s in pinned_signs}
        if unsat_under(signs, rel_pairs, rand_assign):
            n_unsat += 1
    rate = n_unsat / N_NULL
    p_plus1 = (1 + n_unsat) / (1 + N_NULL)  # P(null >= observed UNSAT) with plus-one correction
    cp95_upper = 1.0 if n_unsat == N_NULL else float(beta.ppf(0.95, n_unsat + 1, N_NULL - n_unsat))
    cp95_lower = 0.0 if n_unsat == 0 else float(beta.ppf(0.05, n_unsat, N_NULL - n_unsat + 1))
    verdict = "UNSAT_SPECIFIC" if (observed_unsat and cp95_upper < 0.05) else \
              ("UNSAT_GENERIC" if observed_unsat else "NOT_UNSAT")
    return {"config": name, "observed_unsat": observed_unsat, "n_null": N_NULL,
            "null_unsat_count": n_unsat, "null_unsat_rate": rate,
            "null_rate_cp90_band": [round(cp95_lower, 4), round(cp95_upper, 4)],
            "p_null_ge_observed_plus1": round(p_plus1, 5), "verdict": verdict}


def main():
    lat = engine.load_lattice()
    sal = engine.load_salgarella_equalities()
    out = {"cell": "UNSAT_adjudication", "protocol": "WP-N matched random pin-sets, n=200",
           "results": []}

    # (1) hard-everything, WPH 38 pins (observed INFEASIBLE; 15 pin-violated edges)
    obs1 = unsat_under(lat["signs"], lat["rel_pairs"], lat["wph_pins"])
    out["results"].append(
        adjudicate("WPH38_hard_everything", lat["signs"], lat["rel_pairs"],
                   sorted(lat["wph_pins"]), obs1))

    # (2) Salgarella homophone-grade equalities alone (observed arc-inconsistent)
    obs2 = unsat_under(lat["signs"], lat["rel_pairs"], sal["equalities"])
    out["results"].append(
        adjudicate("SALGARELLA_HOM_CONT_only", lat["signs"], lat["rel_pairs"],
                   sorted(sal["equalities"]), obs2))

    json.dump(out, open(os.path.join(OUT, "UNSAT_adjudication.json"), "w"), indent=1)
    for r in out["results"]:
        print(f"{r['config']}: observed_unsat={r['observed_unsat']} "
              f"null_rate={r['null_unsat_rate']:.3f} band={r['null_rate_cp90_band']} "
              f"-> {r['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
