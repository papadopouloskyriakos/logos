#!/usr/bin/env python3
"""EPOCH-017 — photograph/second-rendering allograph de-confound.

Runs exactly the preregistered plan in epochs/EPOCH-017/prereg.md
(sha256 3b527541f2ed427028fff73c5264394b874150257833c0f5f6cc32b0b48624c9,
frozen 2026-07-08T13:08:35Z, BEFORE this script was written or run).

STEP 0 (source audit) was done by hand before freezing (recorded in prereg.md + result.json);
photographs and a second rendering are both SOURCE_BLOCKED, evidenced. This script runs channel
(C) FEATURE-PARTITION only: synthetic PC first (fail => stop) -> E012 legs restricted to the
INV/SEN partitions -> rendering-shuffle null -> mechanical verdict.
Seed 20260708. Claim layer L1 only.
"""
import json, re, sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path("/home/claude-runner/gitlab/n8n/logos-linear-a-frontier-72h")
EXP = ROOT / "experiments/linear_a_frontier_72h"
EPOCH = EXP / "epochs/EPOCH-017"
OUTDIR = EXP / "data/allograph_deconfound"
OUTDIR.mkdir(parents=True, exist_ok=True)
SEED = 20260708
N_PERM = 10_000
N_PERM_PC = 2_000
N_RESAMPLE = 1_000
PLAN_HASH = "3b527541f2ed427028fff73c5264394b874150257833c0f5f6cc32b0b48624c9"

INV = [0, 1, 2, 3, 4]   # n_endpoints, n_junctions, n_loops, n_components, n_strokes (topology counts)
SEN = [5, 6, 7, 8, 9]   # skel_len_norm, orient_0..3 (continuous curve/orientation shape)

rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------- load (identical to E012)
data = json.loads((EXP / "data/stroke_corpus/features/instances.json").read_text())
instances = [i for i in data["instances"] if i["ok"]]
doc_meta = data["doc_meta"]
silver = {r["id"]: r for r in json.loads((ROOT / "corpus/silver/inscriptions_structured.json").read_text())}

def site_of(doc):
    return doc.lstrip("`").split()[0]

docs_all = sorted({i["doc"] for i in instances})
doc_idx = {d: k for k, d in enumerate(docs_all)}
doc_site = np.array([site_of(d) for d in docs_all])

X = np.array([i["feat"] for i in instances], float)
asp = np.log(np.array([i["aspect"] for i in instances], float))
labels = np.array([i["label"] for i in instances])
inst_doc = np.array([doc_idx[i["doc"]] for i in instances])
inst_site = doc_site[inst_doc]
ink = np.array([i["ink_fraction"] for i in instances], float)

mu, sd = X.mean(0), X.std(0); sd[sd == 0] = 1.0
Z = (X - mu) / sd
z_asp = (asp - asp.mean()) / asp.std()

lab_counts = Counter(labels)
robust = {l for l, c in lab_counts.items() if c >= 3}
by_sign = defaultdict(list)
for k, l in enumerate(labels):
    by_sign[l].append(k)

def sign_sites(idx):
    c = Counter(inst_site[idx].tolist())
    return [s for s, v in c.items() if v >= 3]

F_SIGN = sorted(l for l, idx in by_sign.items() if len(sign_sites(idx)) >= 2)
site_names = sorted(set(doc_site))
site_code = {s: k for k, s in enumerate(site_names)}
doc_site_code = np.array([site_code[s] for s in doc_site], np.int16)

result = {
    "epoch": "EPOCH-017",
    "frontier": "F6 photograph/second-rendering allograph de-confound (gates A/B)",
    "plan_hash": PLAN_HASH,
    "prereg": "epochs/EPOCH-017/prereg.md (frozen 2026-07-08T13:08:35Z, before any run)",
    "seed": SEED,
    "claim_layer": "L1 palaeographic only; no values, no licence touched",
    "articles": ["V", "VII", "VIII", "IX", "XI", "XII", "XV", "XVII", "XVIII", "XXII"],
    "deviations": [],
    "step0_source_audit": {
        "photographs": {
            "checked": ["corpus/bronze/sigla_browse_2026/*.html (in-repo)",
                        "sigla.phis.me/about.html (live, 1 polite fetch)",
                        "sigla.phis.me/document/ARKH%207/ (live, 1 polite fetch)"],
            "finding": ("SigLA ships only vector line-drawings/traces. about.html: 'Dataset and "
                        "drawings are available under CC BY-NC-SA 4.0'. Document page: 'Link to "
                        "tablet drawing'; image files are .png vector traces (ARKH 7.png, "
                        "ARKH 7_1.png, ARKH 7_2.png); no photo/drawing toggle; no photograph "
                        "referenced anywhere on the site or in the in-repo snapshot."),
            "status": "SOURCE_BLOCKED",
        },
        "second_rendering": {
            "checked": ["corpus/bronze/sign_images/ (Aegean/UFAS font glyphs per idealized VALUE, "
                        "not per-instance, not a scholarly hand-copy of specific inscriptions)",
                        "corpus/bronze/younger_lineara/ (text-only, no images)",
                        "corpus/bronze/ full listing (no GORILA plate scans / GesA facsimiles)"],
            "finding": ("No second independent image rendering of the same inscribed signs exists "
                        "in-repo. SigLA states GORILA as its textual/attestation basis but no GORILA "
                        "plate images are shipped anywhere in this corpus."),
            "status": "SOURCE_BLOCKED",
        },
        "same_scribe_attribution": {
            "checked": ["corpus/silver/inscriptions_structured.json",
                        "corpus/bronze/palaeo/*.json", "corpus/bronze/sigla_browse_2026/*",
                        "corpus/bronze/younger_lineara/*"],
            "finding": "No GORILA/SigLA same-hand or scribe attribution found anywhere in-repo.",
            "status": "SOURCE_BLOCKED",
            "substitute": "rendering-shuffle null (needs no attribution data)",
        },
        "channel_run": "(C) FEATURE-PARTITION only, as pre-registered for this source state",
    },
    "partition": {"INV_idx": INV, "INV_names": ["n_endpoints", "n_junctions", "n_loops",
                  "n_components", "n_strokes"], "SEN_idx": SEN,
                  "SEN_names": ["skel_len_norm", "orient_0", "orient_1", "orient_2", "orient_3"]},
    "inventory": {
        "n_ok_instances": len(instances), "n_docs": len(docs_all),
        "n_robust_labels": len(robust), "n_F_SIGN": len(F_SIGN),
    },
}

# ================================================================== leg-1-style statistic (E012, parametrized by dim subset)
def build_sign_pairs(Zmat, signs, doc_of, labs_by_sign):
    out = {}
    for s in signs:
        idx = np.array(labs_by_sign[s])
        A, B = np.triu_indices(len(idx), 1)
        ia, ib = idx[A], idx[B]
        keep = doc_of[ia] != doc_of[ib]
        ia, ib = ia[keep], ib[keep]
        dist = np.linalg.norm(Zmat[ia] - Zmat[ib], axis=1)
        out[s] = (doc_of[ia], doc_of[ib], dist, float(dist.std()))
    return out

def leg1_T(site_by_doc, signs, pairs):
    nper = site_by_doc.shape[0]
    tsum = np.zeros(nper); tcnt = np.zeros(nper)
    for s in signs:
        da_, db_, dist, sig = pairs[s]
        if sig == 0:
            continue
        W = site_by_doc[:, da_] == site_by_doc[:, db_]
        nw = W.sum(1); nc = (~W).sum(1)
        ok = (nw > 0) & (nc > 0)
        mw = (W @ dist) / np.where(nw == 0, 1, nw)
        mc = ((~W) @ dist) / np.where(nc == 0, 1, nc)
        d = (mc - mw) / sig
        tsum[ok] += d[ok]; tcnt[ok] += 1
    return tsum / np.where(tcnt == 0, 1, tcnt)

def leg1_test(Zmat, signs, doc_of, labs_by_sign, site_code_arr, n_perm, prng):
    pairs = build_sign_pairs(Zmat, signs, doc_of, labs_by_sign)
    obs_map = site_code_arr[None, :]
    T_obs = float(leg1_T(obs_map, signs, pairs)[0])
    perm_maps = np.stack([prng.permutation(site_code_arr) for _ in range(n_perm)])
    T_perm = leg1_T(perm_maps, signs, pairs)
    p = float((np.sum(T_perm >= T_obs) + 1) / (n_perm + 1))
    return T_obs, p, T_perm

# ================================================================== leg-2-style statistic (doc embedding -> site)
def doc_embed(dev_matrix, rob_mask, inst_doc_arr, F_DOC):
    E = np.zeros((len(F_DOC), dev_matrix.shape[1]))
    for j, dk in enumerate(F_DOC):
        sel = rob_mask & (inst_doc_arr == dk)
        E[j] = dev_matrix[sel].mean(0)
    return E

def loo_balanced(E, codes, k_classes):
    D = ((E[:, None, :] - E[None, :, :]) ** 2).sum(-1)
    np.fill_diagonal(D, np.inf)
    pred = codes[D.argmin(1)]
    recs = [float((pred[codes == c] == c).mean()) for c in range(k_classes)]
    return float(np.mean(recs)), recs, D.argmin(1)

def leg2_test(dev_full, rob_mask, F_DOC, fd_code, F_sites, n_perm, n_resample, robust_labels,
              labels_arr, prng):
    E_obs = doc_embed(dev_full, rob_mask, inst_doc, F_DOC)
    bal, recs, nn_doc = loo_balanced(E_obs, fd_code, len(F_sites))
    null_bal = np.empty(n_perm)
    for t in range(n_perm):
        pc_ = prng.permutation(fd_code)
        pr = pc_[nn_doc]
        null_bal[t] = np.mean([float((pr[pc_ == c] == c).mean()) for c in range(len(F_sites))])
    p2 = float((np.sum(null_bal >= bal) + 1) / (n_perm + 1))
    lab_pool = {l: np.flatnonzero(labels_arr == l) for l in robust_labels}
    n2b = np.empty(n_resample)
    for t in range(n_resample):
        dev_r = dev_full.copy()
        for l, pool in lab_pool.items():
            if len(pool) < 2:
                continue
            off = prng.integers(1, len(pool), size=len(pool))
            draw = pool[(np.arange(len(pool)) + off) % len(pool)]
            dev_r[pool] = dev_full[draw]
        Er = doc_embed(dev_r, rob_mask, inst_doc, F_DOC)
        n2b[t], _, _ = loo_balanced(Er, fd_code, len(F_sites))
    n2b_p95 = float(np.quantile(n2b, 0.95))
    return bal, recs, p2, n2b_p95

# ================================================================== POSITIVE CONTROL (synthetic, run FIRST)
def synth_pc():
    pc_mask = np.array([l in robust for l in labels])
    idx_pc = np.flatnonzero(pc_mask)
    labs_pc = labels[pc_mask]
    doc_pc = inst_doc[pc_mask]
    site_pc_code = doc_site_code  # site-per-doc map is doc-indexed, unchanged
    by_sign_pc = defaultdict(list)
    for local_k, l in enumerate(labs_pc):
        by_sign_pc[l].append(local_k)
    signs_pc = sorted(l for l, ii in by_sign_pc.items() if len(sign_sites([idx_pc[i] for i in ii])) >= 2)
    n = pc_mask.sum()
    prng = np.random.default_rng(SEED + 17)
    site_arr = doc_site[doc_pc]
    site_names_pc = sorted(set(site_arr))
    d_eff = 1.2

    def make_synth(inv_signal, sen_signal):
        Zs = prng.standard_normal((n, 10))
        for s in site_names_pc:
            m = site_arr == s
            if inv_signal:
                off = prng.standard_normal(len(INV)) * d_eff
                Zs[np.ix_(m, INV)] += off
            if sen_signal:
                off = prng.standard_normal(len(SEN)) * d_eff
                Zs[np.ix_(m, SEN)] += off
        return Zs

    out = {}
    for scen, (inv_on, sen_on) in {"S1_site_only": (True, False),
                                    "S2_nuisance_only": (False, True),
                                    "S3_mixed": (True, True)}.items():
        Zs = make_synth(inv_on, sen_on)
        T_inv, p_inv, _ = leg1_test(Zs[:, INV], signs_pc, doc_pc, by_sign_pc, doc_site_code, N_PERM_PC, prng)
        T_sen, p_sen, _ = leg1_test(Zs[:, SEN], signs_pc, doc_pc, by_sign_pc, doc_site_code, N_PERM_PC, prng)
        out[scen] = {"T_obs_INV": round(T_inv, 4), "p_INV": p_inv,
                     "T_obs_SEN": round(T_sen, 4), "p_SEN": p_sen,
                     "fires_INV": bool(p_inv < 0.01), "fires_SEN": bool(p_sen < 0.01)}
    pc_pass = (out["S1_site_only"]["fires_INV"] and not out["S1_site_only"]["fires_SEN"]
               and not out["S2_nuisance_only"]["fires_INV"] and out["S2_nuisance_only"]["fires_SEN"]
               and out["S3_mixed"]["fires_INV"] and out["S3_mixed"]["fires_SEN"])
    return {"n_synth_instances": int(n), "n_signs": len(signs_pc), "d_eff": d_eff,
            "scenarios": out, "PC_PASS": bool(pc_pass)}

pc = synth_pc()
result["positive_control_synthetic"] = pc
print("PC:", json.dumps(pc, indent=1))
if not pc["PC_PASS"]:
    result["verdict"] = "DECONFOUND_PC_FAIL"
    (EPOCH / "result.json").write_text(json.dumps(result, indent=1))
    sys.exit("Synthetic PC failed — stopped per prereg.")

# ================================================================== MAIN — leg1' INV/SEN on real data
T1i, p1i, _ = leg1_test(Z[:, INV], F_SIGN, inst_doc, by_sign, doc_site_code, N_PERM, rng)
T1s, p1s, _ = leg1_test(Z[:, SEN], F_SIGN, inst_doc, by_sign, doc_site_code, N_PERM, rng)
result["leg1_prime"] = {
    "INV": {"T_obs": round(T1i, 4), "p_raw": p1i, "n_signs": len(F_SIGN)},
    "SEN": {"T_obs": round(T1s, 4), "p_raw": p1s, "n_signs": len(F_SIGN)},
}
print("leg1' INV:", result["leg1_prime"]["INV"], " SEN:", result["leg1_prime"]["SEN"])

# ================================================================== MAIN — leg2' INV/SEN on real data (mirrors E012 leg2 frame)
lab_mean_full = {l: Z[labels == l].mean(0) for l in robust}
rob_mask = np.array([l in robust for l in labels])
dev = np.zeros_like(Z)
for l in robust:
    sel = labels == l
    dev[sel] = Z[sel] - lab_mean_full[l]

doc_rob_counts = Counter(inst_doc[rob_mask].tolist())
elig_docs = [k for k, c in doc_rob_counts.items() if c >= 3]
site_doc_counts = Counter(doc_site[elig_docs].tolist())
F_sites = sorted(s for s, c in site_doc_counts.items() if c >= 10)
F_DOC = np.array(sorted(k for k in elig_docs if doc_site[k] in F_sites))
fd_site = doc_site[F_DOC]
fd_code = np.array([F_sites.index(s) for s in fd_site])

bal_i, recs_i, p2i, n2b_p95_i = leg2_test(dev[:, INV], rob_mask, F_DOC, fd_code, F_sites, N_PERM, N_RESAMPLE, robust, labels, rng)
bal_s, recs_s, p2s, n2b_p95_s = leg2_test(dev[:, SEN], rob_mask, F_DOC, fd_code, F_sites, N_PERM, N_RESAMPLE, robust, labels, rng)

# nuisance comparator (identical definition to E012)
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
bal_nu, recs_nu, _ = loo_balanced(NU, fd_code, len(F_sites))

result["leg2_prime"] = {
    "F_sites": F_sites, "n_docs": int(len(F_DOC)),
    "INV": {"balanced_acc": round(bal_i, 4), "per_site_recall": {s: round(r, 4) for s, r in zip(F_sites, recs_i)},
            "p_raw": p2i, "N2b_p95": round(n2b_p95_i, 4), "beats_N2b": bool(bal_i > n2b_p95_i)},
    "SEN": {"balanced_acc": round(bal_s, 4), "per_site_recall": {s: round(r, 4) for s, r in zip(F_sites, recs_s)},
            "p_raw": p2s, "N2b_p95": round(n2b_p95_s, 4), "beats_N2b": bool(bal_s > n2b_p95_s)},
    "nuisance_balanced_acc": round(bal_nu, 4),
}
print("leg2' INV:", result["leg2_prime"]["INV"])
print("leg2' SEN:", result["leg2_prime"]["SEN"])
print("nuisance_bal:", bal_nu)

# ================================================================== multiplicity — Holm over {p1_INV, p1_SEN, p2_INV, p2_SEN}
raw = [p1i, p1s, p2i, p2s]
labs4 = ["p1_INV", "p1_SEN", "p2_INV", "p2_SEN"]
order = np.argsort(raw)
holm = [None, None, None, None]
prev = 0.0
for r_, i in enumerate(order):
    adj = max(prev, min(1.0, (4 - r_) * raw[i])); prev = adj
    holm[i] = adj
result["multiplicity"] = {"labels": labs4, "raw_p": raw, "holm": holm}

leg1_INV_fire = holm[0] < 0.01
leg1_SEN_fire = holm[1] < 0.01
leg2_INV_fire = holm[2] < 0.01 and bal_i > n2b_p95_i
leg2_SEN_fire = holm[3] < 0.01 and bal_s > n2b_p95_s
FIRE_INV = bool(leg1_INV_fire or (leg2_INV_fire and bal_i > bal_nu))
FIRE_SEN = bool(leg1_SEN_fire or (leg2_SEN_fire and bal_s > bal_nu))
result["fires"] = {"leg1_INV_fire": bool(leg1_INV_fire), "leg1_SEN_fire": bool(leg1_SEN_fire),
                   "leg2_INV_fire": bool(leg2_INV_fire), "leg2_SEN_fire": bool(leg2_SEN_fire),
                   "FIRE_INV": FIRE_INV, "FIRE_SEN": FIRE_SEN}
print("fires:", result["fires"])

# ================================================================== rendering-shuffle null (adversarial)
def shuffle_null(n_reps=200):
    outs_leg1, outs_leg2 = [], []
    for rep in range(n_reps):
        perm = rng.permutation(len(instances))
        Z_shuf = Z.copy()
        Z_shuf[:, SEN] = Z[perm][:, SEN]
        _, p1sh, _ = leg1_test(Z_shuf[:, SEN], F_SIGN, inst_doc, by_sign, doc_site_code, 500, rng)
        outs_leg1.append(p1sh)
        dev_shuf = dev.copy()
        dev_shuf[:, SEN] = dev[perm][:, SEN]
        bal_sh, _, p2sh, n2bp95_sh = leg2_test(dev_shuf[:, SEN], rob_mask, F_DOC, fd_code, F_sites, 500, 200, robust, labels, rng)
        outs_leg2.append((bal_sh, p2sh, n2bp95_sh))
    return outs_leg1, outs_leg2

n_shuffle_reps = 30
sh1, sh2 = shuffle_null(n_shuffle_reps)
sh1_collapse_rate = float(np.mean([p >= 0.05 for p in sh1]))
sh2_collapse_rate = float(np.mean([(bal <= n95) or (p >= 0.05) for bal, p, n95 in sh2]))
result["rendering_shuffle_null"] = {
    "n_reps": n_shuffle_reps,
    "leg1_SEN_shuffled_p_median": round(float(np.median(sh1)), 4),
    "leg1_SEN_collapse_rate": sh1_collapse_rate,
    "leg2_SEN_shuffled_bal_median": round(float(np.median([b for b, _, _ in sh2])), 4),
    "leg2_SEN_collapse_rate": sh2_collapse_rate,
    "COLLAPSES": bool(sh1_collapse_rate >= 0.90 and sh2_collapse_rate >= 0.90),
}
print("rendering_shuffle_null:", result["rendering_shuffle_null"])

# ================================================================== mechanical verdict
COLLAPSES = result["rendering_shuffle_null"]["COLLAPSES"]
if FIRE_INV and COLLAPSES:
    verdict = "SITE_ALLOGRAPH_REAL"
elif (not FIRE_INV) and FIRE_SEN:
    verdict = "TRACER_ARTIFACT"
elif FIRE_INV and FIRE_SEN and not COLLAPSES:
    verdict = "MIXED_PARTITION"
elif FIRE_INV and FIRE_SEN and COLLAPSES:
    # INV fires cleanly and the shuffle null (apparatus check) collapses as required;
    # SEN also firing on real (non-shuffled) data is reported but non-blocking for SITE_ALLOGRAPH_REAL
    verdict = "SITE_ALLOGRAPH_REAL"
else:
    verdict = "NULL_UNDER_PARTITION"
result["verdict"] = verdict
result["honest_accounting"] = (
    "A SITE_ALLOGRAPH_REAL verdict is STILL L1 palaeographic, STILL bounded by 'one trace per "
    "document' (tracer-vs-scribe inseparable at the document level, per E012) -- this epoch only "
    "removes the SPECIFIC rendering-style confound G3 caught (continuous curve/orientation "
    "nuisance); it does not and cannot certify photograph-level truth, because no photograph "
    "channel is obtainable (STEP 0)."
)
print("VERDICT:", verdict)

(EPOCH / "result.json").write_text(json.dumps(result, indent=1))
(OUTDIR / "leg_details.json").write_text(json.dumps({
    "leg1_prime": result["leg1_prime"], "leg2_prime": result["leg2_prime"],
    "rendering_shuffle_null": result["rendering_shuffle_null"],
    "positive_control_synthetic": pc,
}, indent=1))
print("wrote", EPOCH / "result.json")
