#!/usr/bin/env python3
"""EPOCH-009 POST-HOC audits (labeled; frozen verdict untouched).

PH1: LEG-2 doc-disjoint split — same-document (same tracing session) leakage check.
PH2: LEG-2 rank breakdown by label class (AB / A3xx / A4xx+).
PH3: LEG-1 top-hit list (descriptive only).
"""
import json, math, re
from collections import defaultdict
import numpy as np

W = "/home/claude-runner/gitlab/n8n/logos-linear-a-frontier-72h"
EXP = f"{W}/experiments/linear_a_frontier_72h"
DATA = f"{EXP}/data/stroke_corpus"
import random
rng = random.Random(20260708 + 99)

inst = json.load(open(f"{DATA}/features/instances.json"))["instances"]
ok = [r for r in inst if r.get("ok")]
by_label = defaultdict(list)
for r in ok:
    by_label[r["label"]].append(r)

def mrr(rs): return float(np.mean([1.0 / r for r in rs])) if rs else None

def self_retrieval(halfA, halfB, aspA, aspB, labels):
    Bmat = np.stack([halfB[l] for l in labels])
    bmu, bsd = Bmat.mean(0), Bmat.std(0); bsd[bsd == 0] = 1.0
    Bz = (Bmat - bmu) / bsd
    Basp = np.array([aspB[l] for l in labels])
    s_r, a_r = [], []
    for i, lab in enumerate(labels):
        q = (halfA[lab] - bmu) / bsd
        d = np.linalg.norm(Bz - q, axis=1)
        s_r.append(int(np.where(np.argsort(d, kind="stable") == i)[0][0]) + 1)
        da = np.abs(Basp - aspA[lab])
        a_r.append(int(np.where(np.argsort(da, kind="stable") == i)[0][0]) + 1)
    return s_r, a_r

# ---- PH1: doc-disjoint halves
halfA, halfB, aspA, aspB = {}, {}, {}, {}
labels = []
for lab, rs in sorted(by_label.items()):
    if len(rs) < 4:
        continue
    docs = sorted({r["doc"] for r in rs})
    if len(docs) < 2:
        continue
    dA = set(docs[0::2]); dB = set(docs[1::2])
    A = [r for r in rs if r["doc"] in dA]; B = [r for r in rs if r["doc"] in dB]
    if not A or not B:
        continue
    halfA[lab] = np.mean([r["feat"] for r in A], axis=0)
    halfB[lab] = np.mean([r["feat"] for r in B], axis=0)
    aspA[lab] = float(np.mean([math.log(r["aspect"]) for r in A]))
    aspB[lab] = float(np.mean([math.log(r["aspect"]) for r in B]))
    labels.append(lab)
s_r, a_r = self_retrieval(halfA, halfB, aspA, aspB, labels)
def perm_p(obs, n_q, gal_n, N=20000):
    cnt = 0
    for _ in range(N):
        if mrr([rng.randint(1, gal_n) for _ in range(n_q)]) >= obs: cnt += 1
    return (cnt + 1) / (N + 1)
ph1 = {"n_signs": len(labels), "self_mrr": mrr(s_r),
       "self_top1": sum(1 for r in s_r if r == 1),
       "self_top5": sum(1 for r in s_r if r <= 5),
       "aspect_self_mrr": mrr(a_r),
       "p_self": perm_p(mrr(s_r), len(s_r), len(labels)),
       "chance_mrr": float(np.mean([1.0 / rng.randint(1, len(labels))
                                    for _ in range(200000)]))}

# ---- PH2: class breakdown (even/odd frozen split ranks from leg2_detail)
leg2 = json.load(open(f"{DATA}/features/leg2_detail.json"))
ranks = leg2.get("ranks", {})
def cls(l):
    if l.startswith("AB"): return "AB"
    if re.fullmatch(r"A3\d\d", l): return "A3xx_dark"
    return "A_other"
ph2 = {}
for c in ("AB", "A3xx_dark", "A_other"):
    rs = [r for l, r in ranks.items() if cls(l) == c]
    ph2[c] = {"n": len(rs), "mrr": mrr(rs),
              "top5": sum(1 for r in rs if r <= 5) if rs else 0}

# doc-disjoint breakdown too
ph2_dd = {}
for c in ("AB", "A3xx_dark", "A_other"):
    rs = [r for l, r in zip(labels, s_r) if cls(l) == c]
    ph2_dd[c] = {"n": len(rs), "mrr": mrr(rs),
                 "top5": sum(1 for r in rs if r <= 5) if rs else 0}

# ---- PH3: LEG-1 hits
res = json.load(open(f"{EXP}/epochs/EPOCH-009/result.json"))
det = res["leg1_calibration"]["detail"]
ph3 = {"top1": [d["value"] for d in det if d["agg_stroke_rank"] == 1],
       "top5": [(d["value"], d["agg_stroke_rank"]) for d in det
                if d["agg_stroke_rank"] <= 5],
       "worst5": sorted(((d["value"], d["agg_stroke_rank"]) for d in det),
                        key=lambda t: -t[1])[:5]}

out = {"POSTHOC": True, "note": "labeled post-hoc; frozen verdict untouched",
       "PH1_doc_disjoint_leg2": ph1,
       "PH2_class_breakdown_evenodd": ph2,
       "PH2_class_breakdown_docdisjoint": ph2_dd,
       "PH3_leg1_hits": ph3}
json.dump(out, open(f"{EXP}/epochs/EPOCH-009/posthoc.json", "w"), indent=1)
print(json.dumps(out, indent=1))
