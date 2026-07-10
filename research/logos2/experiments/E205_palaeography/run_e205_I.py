"""E205-I — identifiability impact of the palaeographic prior (prereg 8c3ef82).
Conditions: (1) NO_HOMOMORPHY_PRIOR baselines; (2) GRADED prior contraction vs 200
grade-permutation nulls; (3) HARD_IDENTITY_SENSITIVITY_ONLY = referenced pilot/F1 results.
Contraction metric: exact/bounded log10 count delta under model-2 semantics.
E205-A/B cells deferred to the next pass (recorded in STATUS with reason)."""
import hashlib
import json
import os
import sys
import time

import numpy as np

E203 = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "E203_identifiability_engine")
sys.path.insert(0, E203)
import engine  # noqa: E402
import engine_confirmatory as ec  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)
MASTER = 1336530913


def seed_for(*p):
    return int(hashlib.sha256(("|".join(map(str, (MASTER, "E205I") + p))).encode()
                              ).hexdigest()[:8], 16) % 2**31


def contraction(lat, equalities):
    kept, dropped = engine.drop_pin_violated_rel(lat["rel_pairs"], equalities)
    r = ec.exact_log10_count(lat["signs"], kept, equalities, per_component_limit=5 * 10**4)
    if not r.get("consistent"):
        return None, len(dropped)
    return r["log10_count"], len(dropped)


def main():
    t0 = time.time()
    lat = engine.load_lattice()
    sal = engine.load_salgarella_equalities()
    eq = sal["equalities"]
    graded_signs = sorted(eq)
    base_empty = ec.exact_log10_count(lat["signs"], lat["rel_pairs"], {},
                                      per_component_limit=5 * 10**4)["log10_count"]

    real_l10, real_drop = contraction(lat, eq)
    real_contraction = base_empty - real_l10 if real_l10 is not None else None

    null_contractions, null_drops, null_inconsistent = [], [], 0
    vals = [eq[s] for s in graded_signs]
    for k in range(200):
        rng = np.random.default_rng(seed_for("perm", k))
        perm = rng.permutation(len(vals))
        pe = {s: vals[perm[i]] for i, s in enumerate(graded_signs)}
        l10, nd = contraction(lat, pe)
        null_drops.append(nd)
        if l10 is None:
            null_inconsistent += 1
        else:
            null_contractions.append(base_empty - l10)
        if (k + 1) % 50 == 0:
            print(f"  perm nulls {k+1}/200", flush=True)

    nc = np.array(null_contractions)
    p_plus1 = (1 + int(np.sum(nc >= (real_contraction or 0)))) / (1 + len(nc)) \
        if real_contraction is not None and len(nc) else None
    if real_contraction is None:
        verdict = "PRIOR_GENERIC"  # even model-2 dropping cannot make the real grades consistent
        detail = "real grade assignment inconsistent after model-2 edge dropping"
    elif len(nc) and p_plus1 is not None and p_plus1 < 0.05:
        verdict = "PRIOR_CONTRACTS_DOMAINS"
        detail = "real contraction exceeds the grade-permutation null band"
    else:
        verdict = "PRIOR_GENERIC"
        detail = ("real contraction indistinguishable from grade-permutation nulls: the "
                  "contraction comes from PIN COUNT, not from WHICH signs carry the grades")
    res = {
        "cell": "E205_I", "conditions": {
            "1_NO_HOMOMORPHY_PRIOR": {"empty_log10": base_empty,
                                      "pins4_log10_upper": 286.84},
            "2_GRADED_PALAEOGRAPHIC_PRIOR": {
                "n_graded_equalities": len(eq),
                "real_contraction_log10": real_contraction,
                "real_rel_edges_dropped": real_drop,
                "null_contraction_mean": float(nc.mean()) if len(nc) else None,
                "null_contraction_band_5_95": [float(np.percentile(nc, 5)),
                                               float(np.percentile(nc, 95))] if len(nc) else None,
                "null_inconsistent_rate": null_inconsistent / 200,
                "null_edges_dropped_mean": float(np.mean(null_drops)),
                "p_plus1": p_plus1},
            "3_HARD_IDENTITY_SENSITIVITY_ONLY": {
                "reference": "pilot UNSAT_adjudication.json + F1_extended_nulls.json",
                "result": "UNSAT_GENERIC 200/200 under all matched-null families",
                "label": "aggressive sensitivity arm; never the default model"},
        },
        "verdict": verdict, "verdict_detail": detail,
        "vocabulary_note": ("palaeographic evidence only: sign-shape continuity, never "
                            "phonetic-value identity; condition-2 equalities exist only "
                            "under the UNLICENSED continuity hypothesis (conditional map)"),
        "runtime_s": round(time.time() - t0, 1),
    }
    json.dump(res, open(os.path.join(OUT, "E205_I.json"), "w"), indent=1)
    print("VERDICT:", verdict, "|", detail)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
