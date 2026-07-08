#!/usr/bin/env python3
"""EPOCH-007 POST-HOC diagnostics. Exploratory ONLY — cannot change the prereg verdict
(Art. XVII: labeled post-hoc; informs successor hypotheses).

PH1 cluster composition + T/U lift on real LB derivation.
PH2 rare-class-aware decode (cluster -> argmax_class P(cluster|class), i.e. recall-lift
    decode) fitted on KN derivation, graded on non-KN held-out. Upper-bound probe for
    whether the failure is DECODE geometry (majority vote kills rare classes) vs features.
PH3 site convention divergence: gold class distribution per site.
"""
import json
import os
import sys
import numpy as np
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e007_ledger_roles import (
    OUTDIR, SEED, GOLD_CLASSES, parse_lb, gold_lb, ledger_filter,
    type_stats, fit_pipeline, predict, grade,
)

lb = ledger_filter(parse_lb())
deriv = [d for d in lb if d.site == "KN"]
held = [d for d in lb if d.site != "KN"]

out = {"label": "POST-HOC (exploratory, non-verdict-changing)"}

model = fit_pipeline(deriv, gold_lb)
roles_d, meta_d, cl_d = predict(model, deriv, model["deriv_stats"])
gold_d = [gold_lb(m[4]) for m in meta_d]

# PH1 cluster composition
comp = {}
class_tot = Counter(gold_d)
for c in range(12):
    cnt = Counter(g for g, l in zip(gold_d, cl_d) if l == c)
    n = sum(cnt.values())
    lift = {g: round((cnt[g] / n) / (class_tot[g] / len(gold_d)), 2) for g in cnt}
    comp[c] = {"n": n, "majority": model["mapping"][c], "counts": dict(cnt), "lift": lift}
out["PH1_cluster_composition_deriv"] = comp

# PH2 recall-lift decode: cluster -> class maximizing P(cluster | class)
p_cl_given_class = defaultdict(dict)
for c in range(12):
    for g in GOLD_CLASSES:
        n_cg = sum(1 for gg, l in zip(gold_d, cl_d) if l == c and gg == g)
        p_cl_given_class[c][g] = n_cg / max(1, class_tot[g])
alt_map = {c: max(GOLD_CLASSES, key=lambda g: p_cl_given_class[c][g]) for c in range(12)}
out["PH2_alt_mapping"] = {str(c): alt_map[c] for c in range(12)}

roles_h_cl = predict(model, held, type_stats(held))
roles_h, meta_h, cl_h = roles_h_cl
alt_roles_h = [alt_map[c] for c in cl_h]
out["PH2_heldout_altdecode"] = grade(alt_roles_h, meta_h, gold_lb)
out["PH2_heldout_majoritydecode"] = grade(roles_h, meta_h, gold_lb)

# PH3 site conventions
site_gold = defaultdict(Counter)
for d in lb:
    for li, ti, t in d.groups():
        site_gold[d.site][gold_lb(t)] += 1
out["PH3_gold_by_site"] = {s: dict(c) for s, c in sorted(site_gold.items(), key=lambda kv: -sum(kv[1].values()))[:8]}

json.dump(out, open(os.path.join(OUTDIR, "e007_posthoc.json"), "w"), indent=1)
print(json.dumps(out["PH2_heldout_altdecode"], indent=1))
print("alt map:", out["PH2_alt_mapping"])
