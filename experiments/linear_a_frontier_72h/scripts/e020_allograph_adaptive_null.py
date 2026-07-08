#!/usr/bin/env python3
"""EPOCH-020 — dedicated adaptive-null (family 2 of 3) for E017's leg1'-INV site-allograph positive.

Runs exactly the preregistered plan in epochs/EPOCH-020/prereg.md
(sha256 in epochs/EPOCH-020/plan_hash.txt, frozen BEFORE this script was written or run).

Step 1: byte-for-byte reproduction of E017 leg1'-INV T_obs (must equal 0.1767).
Step 2: support-stratified restricted permutation null (M=10,000; matches site sizes, per-sign
        site-support diagnostic, document support/length imbalance) + free-shuffle comparison.
Step 3: per-sign T + Holm-family false-graduation calibration via leave-one-out over null draws.
Step 4: positive control (S1 power, S0 calibration) on synthetic scaffold, BEFORE the real verdict.
Step 5 (SEN): identical pipeline on SEN partition, for contrast only, no verdict.
Seed 20260708. Claim layer L1 only.
"""
import json, sys, time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path("/home/claude-runner/gitlab/n8n/logos-linear-a-frontier-72h")
EXP = ROOT / "experiments/linear_a_frontier_72h"
EPOCH = EXP / "epochs/EPOCH-020"
OUTDIR = EXP / "data/allograph_adaptive_null"
OUTDIR.mkdir(parents=True, exist_ok=True)
SEED = 20260708
PLAN_HASH = (EPOCH / "plan_hash.txt").read_text().strip()

M_MAIN = 10_000       # restricted-null realizations for the main real-data test (>=200 required)
M_PC = 1_000          # restricted-null realizations inside the PC (>=200 required)
R_CALIB = 100          # outer synthetic-no-signal replicates for calibration
ALPHA = 0.01
CALIB_ALPHA = 0.05    # deliberately generous PC calibration tolerance, frozen in prereg

INV = [0, 1, 2, 3, 4]
SEN = [5, 6, 7, 8, 9]

t0 = time.time()
rng = np.random.default_rng(SEED)

# ============================================================ load (identical to E017)
data = json.loads((EXP / "data/stroke_corpus/features/instances.json").read_text())
instances = [i for i in data["instances"] if i["ok"]]


def site_of(doc):
    return doc.lstrip("`").split()[0]


docs_all = sorted({i["doc"] for i in instances})
doc_idx = {d: k for k, d in enumerate(docs_all)}
doc_site = np.array([site_of(d) for d in docs_all])
n_docs = len(docs_all)

X = np.array([i["feat"] for i in instances], float)
labels = np.array([i["label"] for i in instances])
inst_doc = np.array([doc_idx[i["doc"]] for i in instances])
inst_site = doc_site[inst_doc]

mu, sd = X.mean(0), X.std(0)
sd[sd == 0] = 1.0
Z = (X - mu) / sd

lab_counts = Counter(labels)
robust = {l for l, c in lab_counts.items() if c >= 3}
by_sign = defaultdict(list)
for k, l in enumerate(labels):
    by_sign[l].append(k)


def sign_sites(idx):
    c = Counter(inst_site[idx].tolist())
    return [s for s, v in c.items() if v >= 3]


F_SIGN = sorted(l for l, idx in by_sign.items() if len(sign_sites(idx)) >= 2)
n_signs = len(F_SIGN)
site_names = sorted(set(doc_site))
site_code = {s: k for k, s in enumerate(site_names)}
doc_site_code = np.array([site_code[s] for s in doc_site], np.int16)

# document support (instance count per doc) — the corpus's own built-in support proxy
doc_support = np.bincount(inst_doc, minlength=n_docs)

result = {
    "epoch": "EPOCH-020",
    "family": "S12 dedicated adaptive-null family 2 of 3, gate A (E017 leg1-INV site-allograph re-pricing)",
    "plan_hash": PLAN_HASH,
    "prereg": "epochs/EPOCH-020/prereg.md (frozen before any run)",
    "seed": SEED,
    "claim_layer": "L1 palaeographic only; leg2 (doc classification) stays CONFOUNDED/untouched",
    "articles": ["V", "VII", "VIII", "XI", "XII", "XVII", "XVIII", "XXII"],
    "deviations": [],
    "partition": {"INV_idx": INV, "SEN_idx": SEN},
    "inventory": {"n_ok_instances": len(instances), "n_docs": n_docs, "n_F_SIGN": n_signs,
                  "n_sites_total": len(site_names), "site_doc_counts": dict(Counter(doc_site.tolist()))},
}

# ============================================================ STEP 1 — byte-for-byte reproduction
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


def leg1_T_persign(site_by_doc, signs, pairs):
    """Returns (aggregate T vector over draws, per-sign T matrix [n_draws, n_signs])."""
    nper = site_by_doc.shape[0]
    tsum = np.zeros(nper)
    tcnt = np.zeros(nper)
    per_sign = np.full((nper, len(signs)), np.nan)
    for j, s in enumerate(signs):
        da_, db_, dist, sig = pairs[s]
        if sig == 0 or len(dist) == 0:
            continue
        W = site_by_doc[:, da_] == site_by_doc[:, db_]
        nw = W.sum(1)
        nc = (~W).sum(1)
        ok = (nw > 0) & (nc > 0)
        mw = (W @ dist) / np.where(nw == 0, 1, nw)
        mc = ((~W) @ dist) / np.where(nc == 0, 1, nc)
        d = (mc - mw) / sig
        per_sign[ok, j] = d[ok]
        tsum[ok] += d[ok]
        tcnt[ok] += 1
    agg = tsum / np.where(tcnt == 0, 1, tcnt)
    return agg, per_sign


pairs_INV = build_sign_pairs(Z[:, INV], F_SIGN, inst_doc, by_sign)
T_obs_INV_repro, _ = leg1_T_persign(doc_site_code[None, :], F_SIGN, pairs_INV)
T_obs_INV_repro = float(T_obs_INV_repro[0])
result["step1_reproduction"] = {
    "T_obs_INV_reproduced": round(T_obs_INV_repro, 4),
    "T_obs_INV_E017_reported": 0.1767,
    "matches_4dp": bool(round(T_obs_INV_repro, 4) == 0.1767),
}
print("STEP1 reproduction:", result["step1_reproduction"])
if not result["step1_reproduction"]["matches_4dp"]:
    with (EPOCH / "DEVIATIONS.md").open("a") as f:
        f.write(f"\n- {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}: STEP1 reproduction "
                f"mismatch: got {T_obs_INV_repro} vs E017's 0.1767. Prereg-blocking discrepancy, "
                f"logged before any further analysis (Art. XVII).\n")
    result["deviations"].append("STEP1_REPRODUCTION_MISMATCH")

# ============================================================ STEP 2 — restricted permutation (support-stratified)
edges = [(0, 1), (1, 2), (2, 4), (4, 8), (8, 9999)]  # {1}, {2}, {3,4}, {5..8}, {9+}
strata = np.zeros(n_docs, int)
for k, (lo, hi) in enumerate(edges):
    strata[(doc_support > lo) & (doc_support <= hi)] = k
strata_counts = Counter(strata.tolist())
result["support_strata"] = {
    "edges_lo_exclusive_hi_inclusive": edges,
    "stratum_doc_counts": {str(k): int(v) for k, v in sorted(strata_counts.items())},
}
print("support strata:", result["support_strata"])


def restricted_permutation(prng, n):
    perms = np.tile(doc_site_code, (n, 1))
    for s in sorted(set(strata.tolist())):
        idx = np.flatnonzero(strata == s)
        for r in range(n):
            perms[r, idx] = prng.permutation(doc_site_code[idx])
    return perms


def free_permutation(prng, n):
    return np.stack([prng.permutation(doc_site_code) for _ in range(n)])


def run_null(Zpart, signs, pairs, perm_fn, n_draws, prng, label):
    t_start = time.time()
    obs_agg, obs_persign = leg1_T_persign(doc_site_code[None, :], signs, pairs)
    T_obs = float(obs_agg[0])
    perm_maps = perm_fn(prng, n_draws)
    null_agg, null_persign = leg1_T_persign(perm_maps, signs, pairs)
    p = float((np.sum(null_agg >= T_obs) + 1) / (n_draws + 1))
    dt = time.time() - t_start
    print(f"  [{label}] n={n_draws} T_obs={T_obs:.4f} p={p:.5f} "
          f"null_mean={null_agg.mean():.4f} p95={np.quantile(null_agg,0.95):.4f} "
          f"max={null_agg.max():.4f} ({dt:.1f}s)")
    return {
        "T_obs": round(T_obs, 4), "p": p,
        "null_T_mean": round(float(null_agg.mean()), 4),
        "null_T_p95": round(float(np.quantile(null_agg, 0.95)), 4),
        "null_T_max": round(float(null_agg.max()), 4),
        "n_draws": n_draws,
    }, null_persign, obs_persign[0], perm_maps


def per_sign_diagnostic(perm_maps, signs, doc_of, labs_by_sign):
    """Realized distinct-site count per sign under a set of permutation draws, vs real."""
    real_counts = []
    for s in signs:
        idx = np.array(labs_by_sign[s])
        real_counts.append(len(set(doc_site_code[doc_of[idx]].tolist())))
    real_counts = np.array(real_counts)
    n_draws = perm_maps.shape[0]
    realized = np.zeros((n_draws, len(signs)), int)
    for j, s in enumerate(signs):
        idx = np.array(labs_by_sign[s])
        docs_for_sign = doc_of[idx]
        sub = perm_maps[:, docs_for_sign]
        for r in range(n_draws):
            realized[r, j] = len(set(sub[r].tolist()))
    return real_counts, realized


print("STEP2/3 -- INV partition, restricted null (M=%d):" % M_MAIN)
inv_restricted_summary, inv_restr_null_persign, inv_obs_persign, inv_restr_maps = run_null(
    Z[:, INV], F_SIGN, pairs_INV, restricted_permutation, M_MAIN, np.random.default_rng(SEED + 1), "INV restricted")

print("STEP2 -- INV partition, free-shuffle null (M=%d, weaker comparison):" % M_MAIN)
inv_free_summary, inv_free_null_persign, _, inv_free_maps = run_null(
    Z[:, INV], F_SIGN, pairs_INV, free_permutation, M_MAIN, np.random.default_rng(SEED + 2), "INV free")

# per-sign site-support diagnostic (restricted vs free, subsample of 500 draws each for speed)
diag_n = 500
real_dc, restr_dc = per_sign_diagnostic(inv_restr_maps[:diag_n], F_SIGN, inst_doc, by_sign)
_, free_dc = per_sign_diagnostic(inv_free_maps[:diag_n], F_SIGN, inst_doc, by_sign)
restr_dev = np.abs(restr_dc - real_dc[None, :]).mean(0)
free_dev = np.abs(free_dc - real_dc[None, :]).mean(0)
n_signs_restr_better = int((restr_dev < free_dev).sum())
result["step2_persign_sitesupport_diagnostic"] = {
    "n_signs": n_signs,
    "n_signs_restricted_closer_to_real": n_signs_restr_better,
    "n_signs_free_closer_to_real": int((free_dev < restr_dev).sum()),
    "n_signs_tied": int((free_dev == restr_dev).sum()),
    "mean_abs_dev_restricted": round(float(restr_dev.mean()), 4),
    "mean_abs_dev_free": round(float(free_dev.mean()), 4),
    "pass_majority_restricted_better": bool(n_signs_restr_better > n_signs / 2),
}
print("per-sign site-support diagnostic:", result["step2_persign_sitesupport_diagnostic"])


# ============================================================ STEP 3 — Holm-family false-graduation (leave-one-out over null draws)
def holm_n_survivors(pvals, alpha=ALPHA):
    """Standard Holm step-down: sort ascending, walk up while p_(rank) <= alpha/(n-rank);
    the count of ranks passed before the first failure = number of survivors (can be 0)."""
    order = np.argsort(pvals)
    n = len(pvals)
    surv = 0
    for rank, i in enumerate(order):
        if pvals[i] <= alpha / (n - rank):
            surv += 1
        else:
            break
    return surv


def holm_survives_any(pvals, alpha=ALPHA):
    return holm_n_survivors(pvals, alpha) >= 1


def per_sign_pvals(T_target, null_persign_matrix):
    """Empirical per-sign p for T_target (n_signs,) against null_persign_matrix (M, n_signs)."""
    n_signs_ = T_target.shape[0]
    M = null_persign_matrix.shape[0]
    pv = np.full(n_signs_, np.nan)
    for j in range(n_signs_):
        col = null_persign_matrix[:, j]
        valid = ~np.isnan(col)
        if valid.sum() < 10 or np.isnan(T_target[j]):
            continue
        pv[j] = (1 + np.sum(col[valid] >= T_target[j])) / (valid.sum() + 1)
    return pv


def holm_calibration_rate(null_persign_matrix, alpha=ALPHA):
    """Leave-one-out FWER calibration: each draw in turn as pseudo-observed vs the rest."""
    M = null_persign_matrix.shape[0]
    grad = np.zeros(M, bool)
    for m in range(M):
        pv = per_sign_pvals(null_persign_matrix[m], null_persign_matrix)
        pv_valid = pv[~np.isnan(pv)]
        if len(pv_valid) == 0:
            continue
        grad[m] = holm_survives_any(pv_valid, alpha)
    return float(grad.mean()), grad


# real-data per-sign Holm test (against restricted null, M_MAIN)
inv_real_pvals = per_sign_pvals(inv_obs_persign, inv_restr_null_persign)
inv_real_pvals_valid_mask = ~np.isnan(inv_real_pvals)
inv_real_pvals_valid = inv_real_pvals[inv_real_pvals_valid_mask]
n_inv_signs_surviving = holm_n_survivors(inv_real_pvals_valid, ALPHA) if len(inv_real_pvals_valid) else 0
inv_real_survives_any = n_inv_signs_surviving >= 1

# false-graduation rate under matched (restricted) null, via leave-one-out (subsample of null draws for tractability)
loo_n = 2000  # subset of M_MAIN restricted draws used for the O(M^2)-ish LOO calibration
loo_subset = inv_restr_null_persign[:loo_n]
inv_fgr, inv_fgr_grad = holm_calibration_rate(loo_subset, ALPHA)

result["step3_inv"] = {
    "n_signs_tested": int(inv_real_pvals_valid_mask.sum()),
    "n_signs_holm_surviving_real": n_inv_signs_surviving,
    "any_sign_survives_holm_real": bool(inv_real_survives_any),
    "false_graduation_rate_matched_null": round(inv_fgr, 4),
    "false_graduation_rate_n_loo_draws": loo_n,
    "false_graduation_alpha_target": ALPHA,
}
print("STEP3 INV per-sign Holm:", result["step3_inv"])

# ============================================================ STEP 4 — positive control (synthetic, before verdict trusted)
def synth_pc():
    pc_mask = np.array([l in robust for l in labels])
    idx_pc = np.flatnonzero(pc_mask)
    labs_pc = labels[pc_mask]
    doc_pc = inst_doc[pc_mask]
    by_sign_pc = defaultdict(list)
    for local_k, l in enumerate(labs_pc):
        by_sign_pc[l].append(local_k)
    signs_pc = sorted(l for l, ii in by_sign_pc.items() if len(sign_sites([idx_pc[i] for i in ii])) >= 2)
    n = int(pc_mask.sum())
    site_arr = doc_site[doc_pc]
    site_names_pc = sorted(set(site_arr))
    d_eff = 1.2
    strata_pc = strata[doc_pc]

    def make_synth(prng, inv_signal):
        Zs = prng.standard_normal((n, 10))
        if inv_signal:
            for s in site_names_pc:
                m = site_arr == s
                off = prng.standard_normal(len(INV)) * d_eff
                Zs[np.ix_(m, INV)] += off
        return Zs

    def restricted_perm_pc(prng, ndr):
        perms = np.tile(doc_site_code, (ndr, 1))
        for s in sorted(set(strata.tolist())):
            idx = np.flatnonzero(strata == s)
            for r in range(ndr):
                perms[r, idx] = prng.permutation(doc_site_code[idx])
        return perms

    prng_scaffold = np.random.default_rng(SEED + 100)
    perm_maps_pc = restricted_perm_pc(prng_scaffold, M_PC)  # shared across power+calibration (data-independent)

    # ---- POWER: S1 (site signal in INV)
    prng_s1 = np.random.default_rng(SEED + 200)
    Zs1 = make_synth(prng_s1, inv_signal=True)
    pairs_s1 = build_sign_pairs(Zs1[:, INV], signs_pc, doc_pc, by_sign_pc)
    obs_agg_s1, _ = leg1_T_persign(doc_site_code[None, :], signs_pc, pairs_s1)
    null_agg_s1, _ = leg1_T_persign(perm_maps_pc, signs_pc, pairs_s1)
    T_obs_s1 = float(obs_agg_s1[0])
    p_s1 = float((np.sum(null_agg_s1 >= T_obs_s1) + 1) / (M_PC + 1))
    power_pass = p_s1 < ALPHA

    # ---- CALIBRATION: S0 (no signal), R replicates
    grad_flags = []
    for rep in range(R_CALIB):
        prng_r = np.random.default_rng(SEED + 300 + rep)
        Zs0 = make_synth(prng_r, inv_signal=False)
        pairs_s0 = build_sign_pairs(Zs0[:, INV], signs_pc, doc_pc, by_sign_pc)
        obs_persign_s0, = (leg1_T_persign(doc_site_code[None, :], signs_pc, pairs_s0)[1],)
        null_agg_s0, null_persign_s0 = leg1_T_persign(perm_maps_pc, signs_pc, pairs_s0)
        pv0 = per_sign_pvals(obs_persign_s0[0], null_persign_s0)
        pv0v = pv0[~np.isnan(pv0)]
        grad_flags.append(holm_survives_any(pv0v, ALPHA) if len(pv0v) else False)
    grad_flags = np.array(grad_flags)
    fgr_calib = float(grad_flags.mean())
    # one-sided 95% Clopper-Pearson upper bound
    from math import comb
    def cp_upper(k, n, conf=0.95):
        if k == n:
            return 1.0
        lo, hi = 0.0, 1.0
        target = 1 - conf
        for _ in range(100):
            mid = (lo + hi) / 2
            # P(X <= k | p=mid) via betainc relation is heavier; use simple binomial survival sum
            from scipy.stats import binom
            sf = 1 - binom.cdf(k, n, mid)
            if sf > target:
                hi = mid
            else:
                lo = mid
        return hi
    try:
        cp_hi = cp_upper(int(grad_flags.sum()), R_CALIB)
    except Exception:
        cp_hi = None

    calib_pass = (cp_hi is not None) and (cp_hi <= CALIB_ALPHA)

    return {
        "n_synth_instances": n, "n_signs": len(signs_pc), "d_eff": d_eff, "M_PC": M_PC,
        "power": {"T_obs_S1": round(T_obs_s1, 4), "p_S1": p_s1, "power_pass": bool(power_pass)},
        "calibration": {"R": R_CALIB, "false_graduation_rate": round(fgr_calib, 4),
                        "n_graduated": int(grad_flags.sum()),
                        "clopper_pearson_upper_95": round(cp_hi, 4) if cp_hi is not None else None,
                        "target_alpha": CALIB_ALPHA, "calib_pass": bool(calib_pass)},
        "PC_PASS": bool(power_pass and calib_pass),
    }


print("STEP4 -- positive control (synthetic scaffold)...")
pc = synth_pc()
result["step4_positive_control"] = pc
print("PC:", json.dumps(pc, indent=1))

if not pc["PC_PASS"]:
    result["verdict_INV"] = "ADAPTIVE_NULL_PC_FAIL"
    result["verdict_SEN_contrast"] = "NOT_RUN_PC_FAILED"
    (EPOCH / "result.json").write_text(json.dumps(result, indent=1))
    print("PC FAILED -- stopping per prereg.")
    sys.exit(0)

# ============================================================ STEP 2/3 mirrored for SEN (contrast only, no verdict)
pairs_SEN = build_sign_pairs(Z[:, SEN], F_SIGN, inst_doc, by_sign)
print("STEP2/3 -- SEN partition (contrast only), restricted null (M=%d):" % M_MAIN)
sen_restricted_summary, sen_restr_null_persign, sen_obs_persign, sen_restr_maps = run_null(
    Z[:, SEN], F_SIGN, pairs_SEN, restricted_permutation, M_MAIN, np.random.default_rng(SEED + 3), "SEN restricted")
sen_real_pvals = per_sign_pvals(sen_obs_persign, sen_restr_null_persign)
sen_valid_mask = ~np.isnan(sen_real_pvals)
sen_valid = sen_real_pvals[sen_valid_mask]
n_sen_surviving = holm_n_survivors(sen_valid, ALPHA) if len(sen_valid) else 0
sen_survives_any = n_sen_surviving >= 1
sen_fgr, _ = holm_calibration_rate(sen_restr_null_persign[:loo_n], ALPHA)

result["step2_inv_restricted"] = inv_restricted_summary
result["step2_inv_free_weaker_comparison"] = inv_free_summary
result["step2_sen_restricted_contrast"] = sen_restricted_summary
result["step3_sen_contrast"] = {
    "n_signs_tested": int(sen_valid_mask.sum()),
    "n_signs_holm_surviving_real": n_sen_surviving,
    "any_sign_survives_holm_real": bool(sen_survives_any),
    "false_graduation_rate_matched_null": round(sen_fgr, 4),
}
print("STEP3 SEN (contrast):", result["step3_sen_contrast"])

# deflated significance: adaptive p already IS the deflated figure relative to the free-shuffle
# p reported by E017 (E017's family-of-4 Holm p_INV was 0.0004; report the ratio as the deflation factor)
e017_holm_p_inv = 0.00039996000399960006
deflation_factor = (inv_restricted_summary["p"] / e017_holm_p_inv) if e017_holm_p_inv > 0 else None
result["deflated_significance"] = {
    "adaptive_p_restricted_INV": inv_restricted_summary["p"],
    "E017_free_shuffle_holm_p_INV": e017_holm_p_inv,
    "inflation_factor_adaptive_over_E017": round(deflation_factor, 2) if deflation_factor else None,
    "note": ("adaptive p uses the matched-marginal restricted null directly (M=10,000, single test, "
             "no further Holm needed at the aggregate level since this is the sole confirmatory "
             "aggregate test for INV in this epoch); E017's figure was Holm-adjusted across its "
             "4-test {p1_INV,p1_SEN,p2_INV,p2_SEN} family -- the two are not the same quantity, "
             "reported side by side for scale, not as a strict before/after ratio."),
}

# ============================================================ mechanical verdict (INV)
p_adapt = inv_restricted_summary["p"]
if p_adapt < ALPHA and n_inv_signs_surviving >= 1:
    verdict_inv = "SITE_ALLOGRAPH_SURVIVES_ADAPTIVE_NULL"
elif p_adapt < ALPHA and n_inv_signs_surviving == 0:
    verdict_inv = "ATTENUATED"
else:
    verdict_inv = "COLLAPSES"
result["verdict_INV"] = verdict_inv
result["verdict_SEN_contrast"] = "CONTRAST_ONLY_NO_VERDICT"
result["leg2_note"] = "E017 leg2 (doc-level site classification) stays CONFOUNDED / not re-opened here."
result["honest_accounting"] = (
    "This is a re-pricing of E017's leg1'-INV finding under a stricter, matched-marginal null, not a "
    "new discovery channel. It stays L1 palaeographic and touches no transfer licence regardless of "
    "verdict; E017's CONFOUNDED leg2 (doc classification) is untouched."
)
print("VERDICT INV:", verdict_inv)
print(f"total runtime: {time.time()-t0:.1f}s")

(EPOCH / "result.json").write_text(json.dumps(result, indent=1))
(OUTDIR / "persign_detail.json").write_text(json.dumps({
    "F_SIGN": F_SIGN,
    "inv_real_pvals": [None if np.isnan(x) else round(float(x), 5) for x in inv_real_pvals],
    "sen_real_pvals": [None if np.isnan(x) else round(float(x), 5) for x in sen_real_pvals],
}, indent=1))
print("wrote", EPOCH / "result.json")
