#!/usr/bin/env python3
"""EPOCH-011 post-hoc diagnostics — EXPLORATORY, NON-VERDICT-CHANGING (E007 precedent).

Both detectors returned NO_POWER under the frozen LB criteria. These diagnostics ask WHY,
and take the exploratory LA readout that the closed gate forbids from becoming constraints.
Nothing here changes the verdict; no constraint file is emitted.
"""
import json
import os
import sys
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from e007_ledger_roles import parse_lb, parse_la, ledger_filter, gold_lb
from e011_detectors import (a_candidates, a_grade, RULES_A, b_candidates, b_grade,
                            doc_numerals, attribute, sum_consistent, VARIANTS_B, OUT, save)

res = {"label": "POST-HOC (exploratory, non-verdict-changing)"}

lb = ledger_filter(parse_lb())
kn = [d for d in lb if d.site == "KN"]
nonkn = [d for d in lb if d.site != "KN"]
la = ledger_filter(parse_la())

# ---- PH-A1: oracle rule table — every rule graded on KN-train/KN-test/nonKN + per-site
import hashlib
kn_tr = [d for d in kn if int(hashlib.sha1(d.doc_id.encode()).hexdigest(), 16) % 2 == 0]
kn_te = [d for d in kn if int(hashlib.sha1(d.doc_id.encode()).hexdigest(), 16) % 2 == 1]
tab = {}
for rule in RULES_A:
    row = {}
    for name, docs in (("KN_train", kn_tr), ("KN_test", kn_te), ("nonKN", nonkn)):
        row[name] = a_grade(docs, a_candidates(docs, rule), gold_lb)["f1"]
    for site in ("PY", "TH", "MY"):
        sd = [d for d in nonkn if d.site == site]
        row[site] = a_grade(sd, a_candidates(sd, rule), gold_lb)["f1"]
    tab[rule] = row
res["PH_A1_oracle_rule_table_f1"] = tab

# ---- PH-A2: why KN fails — U vs C composition of single-sign numeral-followed occurrences
comp = {}
for name, docs in (("KN", kn), ("nonKN", nonkn)):
    c = Counter()
    for d in docs:
        for li, ti, t in d.groups():
            line = d.lines[li]
            if t.n_signs == 1 and ti + 1 < len(line) and line[ti + 1].kind == "N":
                c[gold_lb(t)] += 1
    comp[name] = dict(c)
res["PH_A2_single_sign_numfollowed_gold_mix"] = comp

# ---- PH-B1: why totals fail on LB — denomination heterogeneity of gold-T docs
# For each nonKN doc containing gold-T: does ANY numeral pass V1/V2/V3? and how many
# distinct single-sign types (unit signs = denominations) intermix with its numerals?
diag = {"n_goldT_docs": 0, "docs_with_any_sumhit": {"V1": 0, "V2": 0, "V3": 0},
        "unitsign_types_per_goldT_doc": []}
for d in nonkn:
    has_t = any(gold_lb(t) == "T" for _, _, t in d.groups())
    if not has_t:
        continue
    diag["n_goldT_docs"] += 1
    nums = doc_numerals(d)
    for v in ("V1", "V2", "V3"):
        if sum_consistent(nums, v):
            diag["docs_with_any_sumhit"][v] += 1
    us = {t.raw for _, _, t in d.groups() if gold_lb(t) == "U"}
    diag["unitsign_types_per_goldT_doc"].append(len(us))
diag["mean_unitsign_types"] = round(float(np.mean(diag["unitsign_types_per_goldT_doc"])), 2)
diag["share_ge1_unitsign"] = round(float(np.mean([x >= 1 for x in diag["unitsign_types_per_goldT_doc"]])), 3)
del diag["unitsign_types_per_goldT_doc"]
res["PH_B1_lb_totals_denomination_diag"] = diag

# ---- PH-LA1: EXPLORATORY LA readout, detector B, all 6 variants — does the sum logic
# (which failed on multi-denomination LB) behave differently on LA's integer stream?
la_b = {}
for v, a in VARIANTS_B:
    cands, _ = b_candidates(la, v, a)
    types = Counter(g.raw for _, _, g, _ in cands)
    # chance share for KU-RO under attribution-of-all-numerals
    allp = {}
    for d in la:
        for li, ti, val in doc_numerals(d):
            g = attribute(d, li, ti, a)
            if g is not None:
                allp.setdefault((d.doc_id, g.bid), g.raw)
    share = Counter(allp.values())
    n_all = sum(share.values())
    la_b[f"{v}+{a}"] = {
        "n_candidates": len(cands),
        "KURO_hits": types.get("KU-RO", 0),
        "KURO_chance_share": round(share.get("KU-RO", 0) / n_all, 4) if n_all else 0,
        "POTOKURO_hits": types.get("PO-TO-KU-RO", 0),
        "top_types": dict(types.most_common(12)),
    }
res["PH_LA1_exploratory_totals_readout"] = la_b

# ---- PH-LA2: EXPLORATORY LA readout, detector A — what the frozen rule (R4) and the
# nonKN-oracle-best rule would flag on LA (types with >=3 hits; NOT constraints)
lb_res = json.load(open(os.path.join(OUT, "e011_lb.json")))
frozen_rule = lb_res["A"]["selected_rule"]
oracle_rule = max(RULES_A, key=lambda r: tab[r]["nonKN"])
la_a = {}
for tag, rule in (("frozen_" + frozen_rule, frozen_rule), ("oracle_" + oracle_rule, oracle_rule)):
    cands = a_candidates(la, rule)
    per = defaultdict(lambda: {"n": 0, "sites": set()})
    for doc_id, site, li, ti, t in cands:
        per[t.raw]["n"] += 1
        per[t.raw]["sites"].add(site)
    la_a[tag] = {k: {"n": v["n"], "sites": sorted(v["sites"])}
                 for k, v in sorted(per.items(), key=lambda kv: -kv[1]["n"]) if v["n"] >= 3}
res["PH_LA2_exploratory_unitslot_readout"] = la_a

save("e011_posthoc.json", res)
print(json.dumps(res, indent=1, default=str))
