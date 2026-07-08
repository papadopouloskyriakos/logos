#!/usr/bin/env python3
"""EPOCH-012 — scribal/site allograph structure in the E009 stroke corpus.

Runs exactly the preregistered plan in epochs/EPOCH-012/prereg.md
(sha256 a051ea371c3e6ac74f5b35d30fa52084e7023644a90f5135c29c75bf97818969,
frozen 2026-07-08T05:15:18Z, BEFORE this script was written or run).

Order: PC first (fail => stop) -> leg1 -> leg2 -> conditional legs 3-4 -> G-gates -> verdict.
Seed 20260708. Claim layer L1 only.
"""
import json, re, sys, hashlib
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path("/home/claude-runner/gitlab/n8n/logos-linear-a-frontier-72h")
EXP = ROOT / "experiments/linear_a_frontier_72h"
EPOCH = EXP / "epochs/EPOCH-012"
OUTDIR = EXP / "data/stroke_corpus/allograph_structure"
SEED = 20260708
N_PERM = 10_000
N_RESAMPLE = 1_000

rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------- load
data = json.loads((EXP / "data/stroke_corpus/features/instances.json").read_text())
instances = [i for i in data["instances"] if i["ok"]]
doc_meta = data["doc_meta"]
silver = {r["id"]: r for r in json.loads((ROOT / "corpus/silver/inscriptions_structured.json").read_text())}

def site_of(doc: str) -> str:
    return doc.lstrip("`").split()[0]

def silver_rec(doc: str):
    return silver.get(doc.lstrip("`").replace(" ", ""))

def support_of(doc: str) -> str:
    r = silver_rec(doc)
    if r:
        return r["support"]
    m = re.search(r"\b(W[a-z])\b", doc)
    return f"SERIES_{m.group(1)}" if m else "UNKNOWN"

def context_of(doc: str) -> str:
    r = silver_rec(doc)
    return r["context"] if r else ""

docs_all = sorted({i["doc"] for i in instances})
doc_idx = {d: k for k, d in enumerate(docs_all)}
doc_site = np.array([site_of(d) for d in docs_all])

X = np.array([i["feat"] for i in instances], float)          # (N,10)
asp = np.log(np.array([i["aspect"] for i in instances], float))
labels = np.array([i["label"] for i in instances])
inst_doc = np.array([doc_idx[i["doc"]] for i in instances])
inst_site = doc_site[inst_doc]
ink = np.array([i["ink_fraction"] for i in instances], float)

# z-space over ALL ok instances (frozen)
mu, sd = X.mean(0), X.std(0)
sd[sd == 0] = 1.0
Z = (X - mu) / sd
z_asp = (asp - asp.mean()) / asp.std()

lab_counts = Counter(labels)
robust = {l for l, c in lab_counts.items() if c >= 3}

result = {
    "epoch": "EPOCH-012",
    "frontier": "F6 scribal/site allograph structure (stroke channel, gates A/E)",
    "plan_hash": "a051ea371c3e6ac74f5b35d30fa52084e7023644a90f5135c29c75bf97818969",
    "prereg": "epochs/EPOCH-012/prereg.md (frozen 2026-07-08T05:15:18Z, before any run)",
    "seed": SEED,
    "claim_layer": "L1 palaeographic only; SigLA trace-standardization caveat applies; no values, no licence touched",
    "articles": ["V", "VII", "VIII", "IX", "XI", "XII", "XV", "XVII", "XVIII", "XXII"],
    "deviations": [],
    "inventory": {
        "n_ok_instances": len(instances),
        "n_docs": len(docs_all),
        "n_robust_labels": len(robust),
        "ok_by_site": dict(Counter(inst_site.tolist()).most_common()),
    },
}

# ---------------------------------------------------------------- PC (FIRST)
pc_mask = np.array([l in robust for l in labels])
Zr, lr = Z[pc_mask], labels[pc_mask]
ar = z_asp[pc_mask]
n = len(Zr)
# LOO 1-NN in stroke z-space
d2 = ((Zr[:, None, :] - Zr[None, :, :]) ** 2).sum(-1)
np.fill_diagonal(d2, np.inf)
nn = d2.argmin(1)
acc = float((lr[nn] == lr).mean())
# aspect-only 1-NN
da = np.abs(ar[:, None] - ar[None, :])
np.fill_diagonal(da, np.inf)
acc_asp = float((lr[da.argmin(1)] == lr).mean())
# label-permutation null on fixed NN graph
perm_acc = np.empty(1000)
for t in range(1000):
    p = rng.permutation(lr)
    perm_acc[t] = (p[nn] == p).mean()
p_pc = float((np.sum(perm_acc >= acc) + 1) / (1000 + 1))
PC_PASS = acc >= 0.15 and p_pc < 0.001 and acc > acc_asp
result["positive_control_run_first"] = {
    "protocol": "LOO 1-NN sign id, robust-label instances",
    "n_instances": n, "n_labels": len(set(lr)),
    "top1_acc": round(acc, 4), "aspect_top1_acc": round(acc_asp, 4),
    "chance_largest_class": round(max(Counter(lr.tolist()).values()) / n, 4),
    "perm_null_mean": round(float(perm_acc.mean()), 4), "p_perm": p_pc,
    "thresholds": "acc>=0.15 & p<0.001 & acc>aspect", "PASS": bool(PC_PASS),
}
print("PC:", result["positive_control_run_first"])
if not PC_PASS:
    result["verdict"] = "CHANNEL_PC_FAIL"
    (EPOCH / "result.json").write_text(json.dumps(result, indent=1))
    sys.exit("PC failed — stopped per prereg.")

# ---------------------------------------------------------------- leg 1
site_names = sorted(set(doc_site))
site_code = {s: k for k, s in enumerate(site_names)}
doc_site_code = np.array([site_code[s] for s in doc_site], np.int16)

by_sign = defaultdict(list)
for k, l in enumerate(labels):
    by_sign[l].append(k)

def sign_sites(idx):
    c = Counter(inst_site[idx].tolist())
    return [s for s, v in c.items() if v >= 3]

F_SIGN = sorted(l for l, idx in by_sign.items() if len(sign_sites(idx)) >= 2)
result["frames"] = {"F_SIGN_n": len(F_SIGN), "F_SIGN": F_SIGN}

# precompute per-sign pair structures (same-doc pairs excluded)
sign_pairs = {}
for s in F_SIGN:
    idx = np.array(by_sign[s])
    A, B = np.triu_indices(len(idx), 1)
    ia, ib = idx[A], idx[B]
    keep = inst_doc[ia] != inst_doc[ib]
    ia, ib = ia[keep], ib[keep]
    dist = np.linalg.norm(Z[ia] - Z[ib], axis=1)
    sign_pairs[s] = (inst_doc[ia], inst_doc[ib], dist, float(dist.std()))

def leg1_T(site_by_doc, signs, pairs):
    """mean over signs of (mean cross - mean within)/sigma_s; vectorized over perms."""
    nper = site_by_doc.shape[0]
    tsum = np.zeros(nper)
    tcnt = np.zeros(nper)
    for s in signs:
        da_, db_, dist, sig = pairs[s]
        if sig == 0:
            continue
        W = site_by_doc[:, da_] == site_by_doc[:, db_]        # (nper, P)
        nw = W.sum(1); nc = (~W).sum(1)
        ok = (nw > 0) & (nc > 0)
        mw = (W @ dist) / np.where(nw == 0, 1, nw)
        mc = ((~W) @ dist) / np.where(nc == 0, 1, nc)
        d = (mc - mw) / sig
        tsum[ok] += d[ok]; tcnt[ok] += 1
    return tsum / np.where(tcnt == 0, 1, tcnt)

obs_map = doc_site_code[None, :]
T_obs = float(leg1_T(obs_map, F_SIGN, sign_pairs)[0])
perm_maps = np.stack([rng.permutation(doc_site_code) for _ in range(N_PERM)])
# per-sign observed + perm stats for localization
per_sign = {}
Tperm_sum = np.zeros(N_PERM); Tperm_cnt = np.zeros(N_PERM)
for s in F_SIGN:
    da_, db_, dist, sig = sign_pairs[s]
    W = obs_map[:, da_] == obs_map[:, db_]
    mw = (W @ dist) / W.sum(1); mc = ((~W) @ dist) / (~W).sum(1)
    d_obs = float((mc - mw)[0] / sig) if sig > 0 else 0.0
    Wp = perm_maps[:, da_] == perm_maps[:, db_]
    nw = Wp.sum(1); nc = (~Wp).sum(1); okp = (nw > 0) & (nc > 0)
    mwp = (Wp @ dist) / np.where(nw == 0, 1, nw)
    mcp = ((~Wp) @ dist) / np.where(nc == 0, 1, nc)
    dp = (mcp - mwp) / (sig if sig > 0 else 1.0)
    Tperm_sum[okp] += dp[okp]; Tperm_cnt[okp] += 1
    p_s = float((np.sum(dp[okp] >= d_obs) + 1) / (okp.sum() + 1))
    per_sign[s] = {"n_inst": len(by_sign[s]), "n_pairs": len(dist),
                   "D_std": round(d_obs, 4), "p_raw": p_s}
T_perm = Tperm_sum / np.where(Tperm_cnt == 0, 1, Tperm_cnt)
p1 = float((np.sum(T_perm >= T_obs) + 1) / (N_PERM + 1))
# Holm over per-sign
ps = sorted(per_sign.items(), key=lambda kv: kv[1]["p_raw"])
m = len(ps); n_holm_sig = 0
# Holm step-down
prev = 0.0
for r_, (s, v) in enumerate(ps):
    adj = max(prev, min(1.0, (m - r_) * v["p_raw"])); prev = adj
    v["p_holm"] = round(adj, 5)
    if adj < 0.05:
        n_holm_sig += 1
result["leg1_spread"] = {
    "T_obs": round(T_obs, 4), "perm_null_mean": round(float(T_perm.mean()), 4),
    "perm_null_p95": round(float(np.quantile(T_perm, 0.95)), 4),
    "p1_raw": p1, "n_signs": m, "n_signs_holm05": n_holm_sig,
    "top_signs": [{"sign": s, **v} for s, v in ps[:12]],
}
print("leg1:", {k: v for k, v in result["leg1_spread"].items() if k != "top_signs"})

# ---------------------------------------------------------------- leg 2
lab_mean = {l: Z[labels == l].mean(0) for l in robust}
dev = np.zeros_like(Z)
rob_mask = np.array([l in robust for l in labels])
for l in robust:
    sel = labels == l
    dev[sel] = Z[sel] - lab_mean[l]

doc_rob_counts = Counter(inst_doc[rob_mask].tolist())
elig_docs = [k for k, c in doc_rob_counts.items() if c >= 3]
site_doc_counts = Counter(doc_site[elig_docs].tolist())
F_sites = sorted(s for s, c in site_doc_counts.items() if c >= 10)
F_DOC = np.array(sorted(k for k in elig_docs if doc_site[k] in F_sites))
fd_site = doc_site[F_DOC]
fd_code = np.array([F_sites.index(s) for s in fd_site])

def doc_embed(dev_matrix):
    E = np.zeros((len(F_DOC), dev_matrix.shape[1]))
    for j, dk in enumerate(F_DOC):
        sel = rob_mask & (inst_doc == dk)
        E[j] = dev_matrix[sel].mean(0)
    return E

def loo_balanced(E, codes, k_classes):
    D = ((E[:, None, :] - E[None, :, :]) ** 2).sum(-1)
    np.fill_diagonal(D, np.inf)
    pred = codes[D.argmin(1)]
    recs = [float((pred[codes == c] == c).mean()) for c in range(k_classes)]
    return float(np.mean(recs)), recs, D.argmin(1), pred

E_obs = doc_embed(dev)
bal, recs, nn_doc, pred = loo_balanced(E_obs, fd_code, len(F_sites))
# N2a: site-label permutation on fixed NN graph (balanced over permuted classes)
p2_hits = 0
null_bal = np.empty(N_PERM)
for t in range(N_PERM):
    pc_ = rng.permutation(fd_code)
    pr = pc_[nn_doc]
    null_bal[t] = np.mean([float((pr[pc_ == c] == c).mean()) for c in range(len(F_sites))])
p2 = float((np.sum(null_bal >= bal) + 1) / (N_PERM + 1))
# N2b: inventory-resample null
lab_pool = {l: np.flatnonzero(labels == l) for l in robust}
n2b = np.empty(N_RESAMPLE)
for t in range(N_RESAMPLE):
    dev_r = dev.copy()
    for l, pool in lab_pool.items():
        if len(pool) < 2:
            continue
        # draw an OTHER instance's dev for each instance of l: offset in [1, len-1]
        off = rng.integers(1, len(pool), size=len(pool))
        draw = pool[(np.arange(len(pool)) + off) % len(pool)]
        dev_r[pool] = dev[draw]
    Er = doc_embed(dev_r)
    n2b[t], _, _, _ = loo_balanced(Er, fd_code, len(F_sites))
n2b_p95 = float(np.quantile(n2b, 0.95))
p_n2b = float((np.sum(n2b >= bal) + 1) / (N_RESAMPLE + 1))
# nuisance comparator
NU = []
for dk in F_DOC:
    d = docs_all[dk]; md = doc_meta.get(d, {})
    dens = md.get("density", {})
    sel = rob_mask & (inst_doc == dk)
    NU.append([md.get("global_ink", 0.0), dens.get("xywh", 0.0), dens.get("xyxy", 0.0),
               1.0 if md.get("mode") == "xywh" else 0.0, float(sel.sum()),
               float(ink[sel].mean()), float(z_asp[sel].mean())])
NU = np.array(NU)
NU = (NU - NU.mean(0)) / np.where(NU.std(0) == 0, 1, NU.std(0))
bal_nu, recs_nu, _, _ = loo_balanced(NU, fd_code, len(F_sites))

result["leg2_doc_site"] = {
    "F_sites": F_sites, "n_docs": int(len(F_DOC)),
    "docs_per_site": {s: int(site_doc_counts[s]) for s in F_sites},
    "balanced_acc": round(bal, 4), "per_site_recall": {s: round(r, 4) for s, r in zip(F_sites, recs)},
    "p2_raw": p2, "N2a_null_mean": round(float(null_bal.mean()), 4),
    "N2b_inventory_null_mean": round(float(n2b.mean()), 4), "N2b_p95": round(n2b_p95, 4),
    "p_vs_N2b": p_n2b, "nuisance_balanced_acc": round(bal_nu, 4),
    "nuisance_per_site_recall": {s: round(r, 4) for s, r in zip(F_sites, recs_nu)},
}
print("leg2:", result["leg2_doc_site"])

# Holm over confirmatory family {p1, p2}
raw = [p1, p2]
order = np.argsort(raw)
holm = [None, None]
prev = 0.0
for r_, i in enumerate(order):
    adj = max(prev, min(1.0, (2 - r_) * raw[i])); prev = adj
    holm[i] = adj
LEG1_FIRE = holm[0] < 0.01
LEG2_FIRE = holm[1] < 0.01 and bal > n2b_p95
result["multiplicity"] = {"raw_p": raw, "holm": holm}
result["fires"] = {"LEG1_FIRE": bool(LEG1_FIRE), "LEG2_FIRE": bool(LEG2_FIRE)}

# ---------------------------------------------------------------- legs 3-4 (conditional)
any_fire = LEG1_FIRE or LEG2_FIRE
if any_fire:
    # leg 3: support proxy within HT
    ht_docs = [k for k in range(len(docs_all)) if doc_site[k] == "HT"]
    sup = {k: support_of(docs_all[k]) for k in ht_docs}
    grp = {k: ("T" if sup[k] == "Tablet" else ("S" if sup[k] in ("Roundel", "SERIES_Wc") else None))
           for k in ht_docs}
    gdocs = [k for k, g in grp.items() if g]
    minority = sum(1 for k in gdocs if grp[k] == "S")
    # signs with >=3 ok inst in each class (HT only)
    qual = []
    for s, idx in by_sign.items():
        idx = [i for i in idx if inst_doc[i] in grp and grp.get(inst_doc[i])]
        cT = sum(1 for i in idx if grp[inst_doc[i]] == "T")
        cS = sum(1 for i in idx if grp[inst_doc[i]] == "S")
        if cT >= 3 and cS >= 3:
            qual.append(s)
    if len(qual) >= 5 and minority >= 10:
        gcode = np.full(len(docs_all), -1, np.int16)
        for k in gdocs:
            gcode[k] = 0 if grp[k] == "T" else 1
        pairs3 = {}
        for s in qual:
            idx = np.array([i for i in by_sign[s] if gcode[inst_doc[i]] >= 0])
            A, B = np.triu_indices(len(idx), 1)
            ia, ib = idx[A], idx[B]
            keep = inst_doc[ia] != inst_doc[ib]
            ia, ib = ia[keep], ib[keep]
            dist = np.linalg.norm(Z[ia] - Z[ib], axis=1)
            pairs3[s] = (inst_doc[ia], inst_doc[ib], dist, float(dist.std()))
        gd = np.array(gdocs)
        maps3 = np.tile(gcode, (N_PERM + 1, 1))
        for t in range(1, N_PERM + 1):
            maps3[t, gd] = gcode[gd][rng.permutation(len(gd))]
        T3 = leg1_T(maps3, qual, pairs3)
        p3 = float((np.sum(T3[1:] >= T3[0]) + 1) / (N_PERM + 1))
        leg3_status = "SUPPORT_STRUCTURE_DETECTED" if p3 < 0.01 else "SUPPORT_STRUCTURE_ABSENT"
        result["leg3_support_HT"] = {"n_signs": len(qual), "minority_docs": minority,
                                     "T_obs": round(float(T3[0]), 4), "p3_raw": p3,
                                     "status": leg3_status}
    else:
        result["leg3_support_HT"] = {"n_signs": len(qual), "minority_docs": minority,
                                     "status": "SUPPORT_NO_POWER"}
    # leg 4: context — mechanical frame gate
    ctx = Counter(context_of(docs_all[k]) for k in F_DOC.tolist() if context_of(docs_all[k]))
    qual_ctx = [c for c, v in ctx.items() if v >= 8]
    result["leg4_context"] = {"classes_ge8": qual_ctx, "counts": dict(ctx),
                              "status": "CHRONOLOGY_CONTEXT_NO_POWER" if len(qual_ctx) < 2 else "RUNNABLE"}
else:
    result["leg3_support_HT"] = {"status": "SKIPPED_NO_FIRE"}
    result["leg4_context"] = {"status": "SKIPPED_NO_FIRE"}

# ---------------------------------------------------------------- G-gates
gates = {}
if LEG1_FIRE:
    many = [s for s in F_SIGN if len(set(inst_doc[by_sign[s]].tolist())) >= 20]
    maps = np.vstack([obs_map, perm_maps])
    Tm = leg1_T(maps, many, {s: sign_pairs[s] for s in many})
    p_g1 = float((np.sum(Tm[1:] >= Tm[0]) + 1) / (N_PERM + 1))
    gates["G1"] = {"n_signs": len(many), "T_obs": round(float(Tm[0]), 4), "p": p_g1,
                   "survive": bool(p_g1 < 0.05)}
if LEG2_FIRE:
    # G2 tablet-only
    tab = [j for j, dk in enumerate(F_DOC) if support_of(docs_all[dk]) == "Tablet"]
    tab_sites = Counter(fd_site[tab].tolist())
    keep_sites = sorted(s for s, c in tab_sites.items() if c >= 10)
    tj = [j for j in tab if fd_site[j] in keep_sites]
    Et = E_obs[tj]
    ct = np.array([keep_sites.index(fd_site[j]) for j in tj])
    bal_t, recs_t, nn_t, _ = loo_balanced(Et, ct, len(keep_sites))
    nulls_t = np.empty(N_PERM)
    for t in range(N_PERM):
        pc_ = rng.permutation(ct)
        pr = pc_[nn_t]
        nulls_t[t] = np.mean([float((pr[pc_ == c] == c).mean()) for c in range(len(keep_sites))])
    p_g2 = float((np.sum(nulls_t >= bal_t) + 1) / (N_PERM + 1))
    gates["G2"] = {"sites": keep_sites, "n_docs": len(tj), "balanced_acc": round(bal_t, 4),
                   "null_p95": round(float(np.quantile(nulls_t, 0.95)), 4), "p": p_g2,
                   "survive": bool(bal_t > np.quantile(nulls_t, 0.95))}
    gates["G3"] = {"allograph_bal": round(bal, 4), "nuisance_bal": round(bal_nu, 4),
                   "survive": bool(bal > bal_nu)}
    # G4 residualization (reported, non-gating)
    C = []
    for i in range(len(instances)):
        d = docs_all[inst_doc[i]]; md = doc_meta.get(d, {})
        C.append([md.get("global_ink", 0.0), md.get("density", {}).get("xywh", 0.0),
                  1.0 if md.get("mode") == "xywh" else 0.0])
    C = np.array(C); C = np.hstack([np.ones((len(C), 1)), C])
    beta, *_ = np.linalg.lstsq(C[rob_mask], dev[rob_mask], rcond=None)
    dev_res = dev.copy()
    dev_res[rob_mask] = dev[rob_mask] - C[rob_mask] @ beta
    Er = doc_embed(dev_res)
    bal_r, recs_r, _, _ = loo_balanced(Er, fd_code, len(F_sites))
    gates["G4_residualized_bal"] = {"balanced_acc": round(bal_r, 4), "non_gating": True}
result["gates"] = gates

# doc-level coherence descriptive
same_doc_d, diff_doc_d = [], []
for s in F_SIGN:
    idx = np.array(by_sign[s])
    A, B = np.triu_indices(len(idx), 1)
    ia, ib = idx[A], idx[B]
    dist = np.linalg.norm(Z[ia] - Z[ib], axis=1)
    same = (inst_doc[ia] == inst_doc[ib])
    same_site = inst_site[ia] == inst_site[ib]
    same_doc_d.extend(dist[same].tolist())
    diff_doc_d.extend(dist[~same & same_site].tolist())
result["doc_coherence_descriptive"] = {
    "mean_same_doc_pair_dist": round(float(np.mean(same_doc_d)), 4),
    "mean_within_site_cross_doc_dist": round(float(np.mean(diff_doc_d)), 4),
    "note": "tracer style and scribal hand are inseparable at doc level (one trace per doc)",
}

# ---------------------------------------------------------------- verdict
if any_fire:
    need = []
    if LEG1_FIRE:
        need.append(gates.get("G1", {}).get("survive", False))
    if LEG2_FIRE:
        need.append(gates.get("G2", {}).get("survive", False))
        need.append(gates.get("G3", {}).get("survive", False))
    if not all(need):
        verdict = "ALLOGRAPH_STRUCTURE_CONFOUNDED"
    elif LEG1_FIRE and LEG2_FIRE:
        verdict = "ALLOGRAPH_STRUCTURE_SITE_LEVEL_DETECTED"
    else:
        verdict = "ALLOGRAPH_STRUCTURE_WEAK"
else:
    verdict = "ALLOGRAPH_STRUCTURE_ABSENT"
result["verdict"] = verdict
print("VERDICT:", verdict)

# ---------------------------------------------------------------- outputs
OUTDIR.mkdir(parents=True, exist_ok=True)
assign = []
for j, dk in enumerate(F_DOC):
    assign.append({"doc": docs_all[dk], "site": fd_site[j],
                   "loo_pred_site": F_sites[pred[j]],
                   "embedding": [round(float(x), 5) for x in E_obs[j]]})
# agglomerative average-linkage at k=n_sites (descriptive)
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist
from sklearn.metrics import adjusted_rand_score
Lk = linkage(pdist(E_obs), method="average")
cl = fcluster(Lk, t=len(F_sites), criterion="maxclust")
ari = float(adjusted_rand_score(fd_code, cl))
for j, a in enumerate(assign):
    a["agglom_cluster"] = int(cl[j])
result["clustering_descriptive"] = {"k": len(F_sites), "ARI_vs_site": round(ari, 4)}
(OUTDIR / "doc_assignments.json").write_text(json.dumps({
    "epoch": "EPOCH-012", "plan_hash": result["plan_hash"], "claim_layer": result["claim_layer"],
    "caveat": "SigLA trace-standardization: tracer style and scribal hand inseparable at doc level.",
    "F_sites": F_sites, "verdict": verdict, "docs": assign}, indent=1))
(OUTDIR / "per_sign_spread.json").write_text(json.dumps({
    "epoch": "EPOCH-012", "plan_hash": result["plan_hash"],
    "per_sign": {s: v for s, v in per_sign.items()}}, indent=1))
(EPOCH / "result.json").write_text(json.dumps(result, indent=1))
print("written", EPOCH / "result.json")
