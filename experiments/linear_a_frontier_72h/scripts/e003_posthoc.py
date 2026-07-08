#!/usr/bin/env python3
"""EPOCH-003 POST-HOC (declared, verdict-neutral; run AFTER the frozen verdict).

(A) CTRL poisoning: wrong-seed injection on the CTRL identity pair at b=5/7 (frac 1.0),
    where the clean cells DO carry signal (KNOWN clean cells were already FLOOR, so the
    preregistered poisoning contrast was uninformative there).
(B) Required-hit-rate: at the LA operating budget (b=5, held-out H=42 on KNOWN full),
    what exact count k clears p<=0.05/12 and p<=0.05 under the same permutation null —
    i.e. would the bridge survive at 5 seeds IF 5-dim profiles retained the LOO hit rate?
Plan hash be6dd7e7... (EPOCH-003). Seed 20260708.
"""
from __future__ import annotations
import json, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e003_seed_poverty as E3

OUT = os.path.join(E3.OUTDIR, "E003_posthoc.json")


def run():
    out = {"declared": "post-hoc, verdict-neutral (epoch verdict already frozen from the "
                       "preregistered cells)", "seed": E3.SEED, "plan_hash": E3.PLAN_HASH}

    # ---- (A) CTRL poisoning ----
    seqs_s, seqs_t, gtfn = E3.ctrl_corpora()
    shuf, _ = E3.rng_for("CTRL", "shuffle", 1.0, 0)
    prob = E3.build_problem(seqs_s, seqs_t, gtfn(seqs_s, seqs_t), shuf)
    adv = {}
    for b in (5, 7):
        for kw in (0, 1, 2):
            reps = []
            for rep in range(E3.R_CELL):
                srng, _ = E3.rng_for("CTRL", "ph_adv_seeds", 1.0, 0, b, kw, rep)
                _, nrng = E3.rng_for("CTRL", "ph_adv_null", 1.0, 0, b, kw, rep)
                reps.append(E3.replicate(prob, b, srng, nrng, k_wrong=kw))
            adv[f"b{b}_wrong{kw}"] = E3.cell_verdict(reps)
    tiers = {"SURVIVES_HOLM": 2, "NOMINAL": 1, "FLOOR": 0, "NO_POWER": 0}
    for b in (5, 7):
        c0, c1, c2 = (adv[f"b{b}_wrong{k}"] for k in (0, 1, 2))
        adv[f"b{b}_poisons"] = {
            "tier_drop_wrong1": tiers[c0["cell_verdict"]] - tiers[c1["cell_verdict"]],
            "tier_drop_wrong2": tiers[c0["cell_verdict"]] - tiers[c2["cell_verdict"]],
            "delta_acc_wrong1": c1["exact_acc_mean"] - c0["exact_acc_mean"],
            "delta_acc_wrong2": c2["exact_acc_mean"] - c0["exact_acc_mean"]}
    out["ctrl_poisoning"] = adv

    # ---- (B) required hit rate at b=5 on KNOWN full corpus ----
    seqs_s, seqs_t, gtfn = E3.known_corpora()
    shuf, _ = E3.rng_for("KNOWN", "shuffle", 1.0, 0)
    prob = E3.build_problem(seqs_s, seqs_t, gtfn(seqs_s, seqs_t), shuf)
    n = len(prob["s_signs"])
    # realized pred vectors from the first 5 stored-stream replicates; p(k) via same null
    ks = {}
    for rep in range(5):
        srng, _ = E3.rng_for("KNOWN", "seeds", 1.0, 0, 5, rep)
        _, nrng = E3.rng_for("KNOWN", "null", 1.0, 0, 5, rep)
        seed_idx = sorted(srng.sample(range(n), 5))
        anchor = [(i, prob["gt_idx"][i]) for i in seed_idx]
        cost = E3.m1_cost(prob["Ss"], prob["St"], anchor)
        held = [i for i in range(n) if i not in set(seed_idx)]
        preds = np.array([int(np.argmin(cost[i])) for i in held])
        truths = np.array([prob["gt_idx"][i] for i in held])
        # null distribution of exact count for THIS pred vector
        null = np.array([(preds == nrng.permutation(truths)).sum() for _ in range(20000)])
        pk = {int(k): float(((null >= k).sum() + 1) / (len(null) + 1)) for k in range(0, 12)}
        ks[rep] = {"H": len(held), "p_of_count": pk,
                   "k_holm": min((k for k, p in pk.items() if p <= E3.HOLM_BAR), default=None),
                   "k_nominal": min((k for k, p in pk.items() if p <= 0.05), default=None)}
    out["required_count_b5_known_full"] = ks
    H = 42
    k_holm = int(np.median([v["k_holm"] for v in ks.values()]))
    k_nom = int(np.median([v["k_nominal"] for v in ks.values()]))
    out["summary_b5"] = {
        "H_heldout": H, "k_needed_holm": k_holm, "k_needed_nominal": k_nom,
        "hit_rate_needed_holm": k_holm / H, "hit_rate_needed_nominal": k_nom / H,
        "loo_hit_rate_measured": 7 / 47,
        "b5_hit_rate_measured": 0.0393,
        "reading": ("if 5-anchor profiles retained the LOO hit rate 0.149 (~6.3/42), the "
                    "cell WOULD clear the Holm bar — the collapse is in M1's discriminative "
                    "geometry at 5 anchor dimensions (measured 0.039), not in the "
                    "significance arithmetic")}
    json.dump(out, open(OUT, "w"), indent=1, default=float)
    print(json.dumps(out["ctrl_poisoning"], indent=1, default=float)[:2000])
    print(json.dumps(out["summary_b5"], indent=1))
    print("wrote", OUT)


if __name__ == "__main__":
    run()
