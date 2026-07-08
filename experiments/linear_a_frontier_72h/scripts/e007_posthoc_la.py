#!/usr/bin/env python3
"""EPOCH-007 POST-HOC LA readout. Exploratory ONLY (prereg gates the LA leg on LB firing;
LB did NOT fire). This produces NO constraints file and NO claims — it records what the
(unvalidated) transfer WOULD have said, to sharpen successor hypotheses (Art. XVII label).
"""
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e007_ledger_roles import (
    OUTDIR, parse_lb, parse_la, gold_lb, ledger_filter, type_stats,
    fit_pipeline, predict, la_gold_check_sets,
)

lb = ledger_filter(parse_lb())
deriv = [d for d in lb if d.site == "KN"]
model = fit_pipeline(deriv, gold_lb)

la = ledger_filter(parse_la())
roles, meta, cl = predict(model, la, type_stats(la))
checks = la_gold_check_sets(meta)
out = {"label": "POST-HOC exploratory; LB detector did NOT fire; NO validated constraints",
       "la_ledger_docs": len(la),
       "la_sites": dict(Counter(d.site for d in la)),
       "predicted_role_share": dict(Counter(roles))}
for ck, idxs in checks.items():
    out[ck] = {"n_occ": len(idxs), "predicted_roles": dict(Counter(roles[i] for i in idxs))}
json.dump(out, open(os.path.join(OUTDIR, "e007_posthoc_la.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
