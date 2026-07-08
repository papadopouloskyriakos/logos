#!/usr/bin/env python3
"""EPOCH-012 POST-HOC (descriptive only, does NOT touch the frozen verdict).

Question for successors: is the leg-1 within-site<cross-site pairwise spread signal
medium-driven? Rerun the leg-1 global test restricted to TABLET-support docs only
(clay tablets at HT/KH/KN/PH; ZA stone vessels drop out), doc-level permutation.
Labeled POST-HOC everywhere; seed 20260708+1.
"""
import json, re
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

ROOT = Path("/home/claude-runner/gitlab/n8n/logos-linear-a-frontier-72h")
EXP = ROOT / "experiments/linear_a_frontier_72h"
rng = np.random.default_rng(20260709)
N_PERM = 10_000

data = json.loads((EXP / "data/stroke_corpus/features/instances.json").read_text())
instances = [i for i in data["instances"] if i["ok"]]
silver = {r["id"]: r for r in json.loads((ROOT / "corpus/silver/inscriptions_structured.json").read_text())}

def site_of(doc): return doc.lstrip("`").split()[0]
def support_of(doc):
    r = silver.get(doc.lstrip("`").replace(" ", ""))
    if r: return r["support"]
    m = re.search(r"\b(W[a-z])\b", doc)
    return f"SERIES_{m.group(1)}" if m else "UNKNOWN"

docs_all = sorted({i["doc"] for i in instances})
doc_idx = {d: k for k, d in enumerate(docs_all)}
tablet_doc = np.array([support_of(d) == "Tablet" for d in docs_all])
doc_site = np.array([site_of(d) for d in docs_all])

X = np.array([i["feat"] for i in instances], float)
labels = np.array([i["label"] for i in instances])
inst_doc = np.array([doc_idx[i["doc"]] for i in instances])
mu, sd = X.mean(0), X.std(0); sd[sd == 0] = 1
Z = (X - mu) / sd

keep = tablet_doc[inst_doc]
by_sign = defaultdict(list)
for k in np.flatnonzero(keep):
    by_sign[labels[k]].append(k)

elig = []
for s, idx in by_sign.items():
    c = Counter(doc_site[inst_doc[idx]].tolist())
    if sum(1 for v in c.values() if v >= 3) >= 2:
        elig.append(s)
elig.sort()

site_names = sorted(set(doc_site[tablet_doc]))
code = {s: i for i, s in enumerate(site_names)}
dsc = np.array([code.get(s, -1) for s in doc_site], np.int16)
tab_docs = np.flatnonzero(tablet_doc)

pairs = {}
for s in elig:
    idx = np.array(by_sign[s])
    A, B = np.triu_indices(len(idx), 1)
    ia, ib = idx[A], idx[B]
    m = inst_doc[ia] != inst_doc[ib]
    ia, ib = ia[m], ib[m]
    dist = np.linalg.norm(Z[ia] - Z[ib], axis=1)
    pairs[s] = (inst_doc[ia], inst_doc[ib], dist, float(dist.std()))

maps = np.tile(dsc, (N_PERM + 1, 1))
for t in range(1, N_PERM + 1):
    maps[t, tab_docs] = dsc[tab_docs][rng.permutation(len(tab_docs))]

tsum = np.zeros(N_PERM + 1); tcnt = np.zeros(N_PERM + 1)
for s in elig:
    a, b, dist, sig = pairs[s]
    if sig == 0: continue
    W = maps[:, a] == maps[:, b]
    nw, nc = W.sum(1), (~W).sum(1)
    ok = (nw > 0) & (nc > 0)
    mw = (W @ dist) / np.where(nw == 0, 1, nw)
    mc = ((~W) @ dist) / np.where(nc == 0, 1, nc)
    d = (mc - mw) / sig
    tsum[ok] += d[ok]; tcnt[ok] += 1
T = tsum / np.where(tcnt == 0, 1, tcnt)
p = float((np.sum(T[1:] >= T[0]) + 1) / (N_PERM + 1))
out = {
    "label": "POST-HOC (descriptive; frozen verdict untouched)",
    "question": "leg-1 spread signal restricted to Tablet-support docs (medium held fixed)",
    "n_signs": len(elig), "sites_in_frame": site_names,
    "tablet_docs": int(tablet_doc.sum()),
    "instances_kept": int(keep.sum()),
    "T_obs": round(float(T[0]), 4),
    "perm_p95": round(float(np.quantile(T[1:], 0.95)), 4),
    "p_raw": p, "seed": 20260709, "n_perm": N_PERM,
}
print(json.dumps(out, indent=1))
(EXP / "epochs/EPOCH-012/posthoc.json").write_text(json.dumps(out, indent=1))
