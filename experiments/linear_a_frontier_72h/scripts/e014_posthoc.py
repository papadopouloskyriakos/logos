#!/usr/bin/env python3
"""EPOCH-014 POST-HOC (non-verdict, exploratory; Art. XVII labeled).

The preregistered verdict is REGISTER_STRATA_NO_POWER (site gate). This post-hoc
characterizes the confound for successor design. Nothing here changes the verdict.

PH1  register-within-site: LEDG(HT) vs SEAL(HT)  and  LEDG(HT) vs LIB proxy is
     impossible (no HT stone vessels) -> note only. Also SEAL(Khania) vs LEDG(Khania).
PH2  recurrent-word removal (prereg step-3 rule) applied to ALL LA register pairs
     and both site pairs: vocabulary vs systemic attribution of every divergence.
PH3  SEAL site composition; SEAL support composition HT vs non-HT (nodule/roundel mix).
PH4  length-only adversary: how much of each pair's JSD survives if bigram identity
     is destroyed but word LENGTH kept (signs -> single symbol X)? (is divergence just
     word-length profiles?)
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from e014_register_strata import (  # noqa: E402
    CAMP, OUTDIR, SEED, N_PERM, load_la_registers, build_alphabet, pair_test,
    recurrent_types, remove_types)

rng = np.random.default_rng(SEED + 1)
la = load_la_registers()
keep = build_alphabet([la["LIB"], la["LEDG"], la["SEAL"]])
out = {"label": "POST-HOC NON-VERDICT (EPOCH-014)"}

HT = "Haghia Triada"


def sub(docs, site=None, not_site=None):
    if site:
        return [d for d in docs if d[1] == site]
    return [d for d in docs if d[1] != not_site]


# PH1 — register contrast WITHIN one site (unconfounded)
ph1 = {}
for site, tag in [(HT, "HT"), ("Khania", "KH")]:
    A = sub(la["LEDG"], site=site)
    B = sub(la["SEAL"], site=site)
    wa = sum(len(w) for _, _, w in A)
    wb = sum(len(w) for _, _, w in B)
    if min(wa, wb) < 30:
        ph1[f"LEDG-SEAL@{tag}"] = {"runnable": False, "words": [wa, wb]}
        continue
    r = pair_test(A, B, keep, N_PERM, rng)
    ph1[f"LEDG-SEAL@{tag}"] = r
    print(f"PH1 LEDG-SEAL@{tag}: jsd {r['jsd_obs']} p {r['p_perm']} xr {r['excess_ratio']}")
ph1["note"] = "LIB has no HT/Khania presence; libation-vs-admin cannot be de-confounded from site in this corpus"
out["PH1_register_within_site"] = ph1

# PH2 — recurrent-word removal everywhere (prereg step-3 rule, exploratory)
ph2 = {}
pairs = {
    "LIB-LEDG": (la["LIB"], la["LEDG"]),
    "LIB-SEAL": (la["LIB"], la["SEAL"]),
    "LEDG-SEAL": (la["LEDG"], la["SEAL"]),
    "LEDG@HT-LEDG@nonHT": (sub(la["LEDG"], site=HT), sub(la["LEDG"], not_site=HT)),
    "SEAL@HT-SEAL@nonHT": (sub(la["SEAL"], site=HT), sub(la["SEAL"], not_site=HT)),
    "LEDG-SEAL@HT": (sub(la["LEDG"], site=HT), sub(la["SEAL"], site=HT)),
}
for k, (A, B) in pairs.items():
    rt = recurrent_types(A) | recurrent_types(B)
    A2, B2 = remove_types(A, rt), remove_types(B, rt)
    wa = sum(len(w) for _, _, w in A2)
    wb = sum(len(w) for _, _, w in B2)
    if min(wa, wb) < 30:
        ph2[k] = {"runnable": False, "postremoval_words": [wa, wb],
                  "n_types_removed": len(rt)}
        continue
    r = pair_test(A2, B2, keep, N_PERM, rng)
    r["n_types_removed"] = len(rt)
    ph2[k] = r
    print(f"PH2 {k} post-removal: jsd {r['jsd_obs']} p {r['p_perm']} xr {r['excess_ratio']} (removed {len(rt)} types)")
out["PH2_recurrent_removal_everywhere"] = ph2

# PH3 — SEAL composition
ph3 = {
    "SEAL_site_counts": Counter(d[1] for d in la["SEAL"]).most_common(),
}
raw = json.load(open(os.path.join(os.path.dirname(os.path.dirname(CAMP)),
                                  "corpus", "silver", "inscriptions_structured.json")))
supp = {}
for x in raw:
    supp[x["id"]] = x["support"]
ph3["SEAL_support_HT"] = Counter(supp[d[0]] for d in sub(la["SEAL"], site=HT)).most_common()
ph3["SEAL_support_nonHT"] = Counter(supp[d[0]] for d in sub(la["SEAL"], not_site=HT)).most_common()
out["PH3_seal_composition"] = ph3
print("PH3", ph3)

# PH4 — length-only adversary: map every sign to X, keep boundaries
def lenify(docs):
    return [(i, s, [tuple("X" * len(w)) for w in ws]) for i, s, ws in docs]

ph4 = {}
for k, (A, B) in list(pairs.items())[:3] + [("SEAL@HT-SEAL@nonHT", pairs["SEAL@HT-SEAL@nonHT"])]:
    r = pair_test(lenify(A), lenify(B), {"X"}, N_PERM, rng, want_secondary=False)
    ph4[k] = {"jsd_lenonly": r["jsd_obs"], "p": r["p_perm"], "xr": r["excess_ratio"]}
    print(f"PH4 {k} length-only: jsd {r['jsd_obs']} p {r['p_perm']} xr {r['excess_ratio']}")
out["PH4_length_only_adversary"] = ph4

with open(os.path.join(OUTDIR, "e014_posthoc.json"), "w") as f:
    json.dump(out, f, indent=1, default=str)
print("wrote", os.path.join(OUTDIR, "e014_posthoc.json"))
