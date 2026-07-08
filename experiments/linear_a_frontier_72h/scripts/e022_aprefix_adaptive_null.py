#!/usr/bin/env python3
"""EPOCH-022 — dedicated adaptive-null family 3/3 (Constitution sec.12) for the A- prefixation
positive (E015/E1). Prereg d35... no: prereg 5b454760 (epochs/EPOCH-022/prereg.md).

Steps: (1) byte-for-byte reproduction of E015's A|PRE confirmatory statistic via e015_lib
(unchanged). (2) PERMUTE (primary) + BOOTSTRAP (weaker comparison) dedicated adaptive null,
>=200 realizations, over the SAME 72-candidate universe as E015's exploratory scan. (3) single-
confirmatory adaptive p + best-of-family deflated p (Bonferroni / Holm / maxT). (4) positive
control: PC-power (planted __PLANT__ prefix, out-of-alphabet marker) + PC-calibration (fresh
no-prefix PERMUTE draws scored against the reference pool, Holm family false-graduation rate).
(5) mechanical verdict per prereg's frozen rule.

Pure stdlib. Seed discipline: every stochastic step takes an explicit seed derived from 20260708.
"""
from __future__ import annotations
import json, math, os, random, sys, time

ROOT = "/home/claude-runner/gitlab/n8n/logos-linear-a-frontier-72h"
CAMP = os.path.join(ROOT, "experiments", "linear_a_frontier_72h")
sys.path.insert(0, os.path.join(CAMP, "scripts"))
import e015_lib as L  # noqa: E402

SEED = 20260708
DATA = os.path.join(CAMP, "data", "aprefix_adaptive_null")
os.makedirs(DATA, exist_ok=True)

M_PERMUTE = 5000
N_BOOTSTRAP = 2000
R_CALIB = 300
N_POWER_SEEDS = 25
N_POWER_NULL = 300
K_STEMS_PLANT = 45
ALPHA_PRIMARY = 0.01
ALPHA_FAMILY_SECONDARY = 0.05
PLANT = "__PLANT__"


def gorila_words(docs):
    return [w for d in docs for w in d["words"] if len(w) >= 1]


# ----------------------------------------------------------------- null generators
def permute_corpus(words, rng):
    """Exact-multiset-preserving null: shuffle the pooled sign-token stream, re-chop using the
    ORIGINAL per-word length sequence in original word order."""
    lens = [len(w) for w in words]
    pool = [s for w in words for s in w]
    rng.shuffle(pool)
    out, i = [], 0
    for ln in lens:
        out.append(tuple(pool[i:i + ln]))
        i += ln
    return out


def bootstrap_corpus(words, rng):
    """i.i.d.-with-replacement, sign-unigram-weighted (E015's own synth_corpus, reused)."""
    return L.synth_corpus(words, rng)


# ----------------------------------------------------------------- CP upper bound (one-sided, exact)
def clopper_pearson_upper(k, n, conf=0.95):
    if n == 0:
        return 1.0
    if k == n:
        return 1.0
    from math import comb
    alpha = 1 - conf
    # exact one-sided upper bound: smallest p s.t. P(Bin(n,p) <= k) = alpha
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        cdf = sum(comb(n, i) * mid ** i * (1 - mid) ** (n - i) for i in range(0, k + 1))
        if cdf > alpha:
            lo = mid
        else:
            hi = mid
    return round(hi, 6)


# ----------------------------------------------------------------- main
def run():
    t0 = time.time()
    deviations = []

    docs = L.load_la_docs()
    words = gorila_words(docs)
    U_full = L.candidate_universe(words)  # frozen deterministic
    A = ("A", "PRE")

    deviations.append({
        "id": "D1", "kind": "pre-result-fix", "status": "APPLIED_BEFORE_RESULT_WRITTEN",
        "text": ("PC-power planted-corpus construction: productivities() dedupes the word list "
                 "into a set, so two IDENTICAL PLANT+stem words (the prereg's literal reading) "
                 "collapse to one and do not mechanically guarantee rc[stem]>=2. Fixed to insert "
                 "the bare stem as a standalone word (satisfies the `t in wset` branch directly) "
                 "before any run's result.json was finalized -- same status as E020's pre-result "
                 "bugfix, not an erratum. First-pass (flawed) run already showed power_pass=True "
                 "(obs_plant 30-37, p_plant~0.0033); corrected run gives obs_plant=45 exactly on "
                 "all 25 seeds, same p_plant, same power_pass=True. See DEVIATIONS.md."),
    })

    # ---------------- STEP 1: byte-for-byte reproduction -------------------------------------
    pv1 = L.null_pvals(words, [A], 2000, seed=SEED + 100)
    step1 = {"obs": pv1[A]["obs"], "p": pv1[A]["p"], "null_mean": pv1[A]["null_mean"],
             "expected_obs": 47, "expected_p_approx": 0.0004998, "expected_null_mean_approx": 24.947}
    step1["match"] = (step1["obs"] == 47 and abs(step1["null_mean"] - 24.947) < 0.01
                       and abs(step1["p"] - 0.0004998) < 1e-4)
    if not step1["match"]:
        deviations.append({"id": "D0-BLOCKING", "text": f"Step-1 reproduction mismatch: {step1}"})
    if len(U_full) != 72:
        deviations.append({"id": "D0b", "text": f"U_full size {len(U_full)} != expected 72"})

    obs_real = L.productivities(words, U_full)
    assert obs_real[A] == step1["obs"] == 47, "obs mismatch between productivities() and null_pvals()"

    # ---------------- STEP 2: dedicated adaptive null -----------------------------------------
    rng_perm = random.Random(SEED + 300)
    V = {c: [0] * M_PERMUTE for c in U_full}   # value matrix: candidate -> [realizations]
    for j in range(M_PERMUTE):
        pc = permute_corpus(words, rng_perm)
        prod = L.productivities(pc, U_full)
        for c in U_full:
            V[c][j] = prod[c]

    rng_boot = random.Random(SEED + 301)
    Vb_A = [0] * N_BOOTSTRAP
    for j in range(N_BOOTSTRAP):
        bc = bootstrap_corpus(words, rng_boot)
        Vb_A[j] = L.productivities(bc, [A])[A]

    def summarize(arr):
        s = sorted(arr)
        n = len(s)
        mean = sum(s) / n
        var = sum((x - mean) ** 2 for x in s) / max(1, n - 1)
        return {"mean": round(mean, 4), "sd": round(var ** 0.5, 4),
                "p50": s[n // 2], "p95": s[int(0.95 * n)] if n else None,
                "max": s[-1] if n else None}

    permute_A_summary = summarize(V[A])
    bootstrap_A_summary = summarize(Vb_A)

    def count_ge_p(arr, obs, n):
        ge = sum(1 for x in arr if x >= obs)
        return (1 + ge) / (1 + n)

    p_single_permute = count_ge_p(V[A], 47, M_PERMUTE)
    p_single_bootstrap = count_ge_p(Vb_A, 47, N_BOOTSTRAP)

    step2 = {
        "M_permute": M_PERMUTE, "N_bootstrap": N_BOOTSTRAP,
        "permute_A_null_summary": permute_A_summary,
        "bootstrap_A_null_summary": bootstrap_A_summary,
        "p_single_permute": p_single_permute,
        "p_single_bootstrap": p_single_bootstrap,
        "lift_over_permute_null_mean": round(47 / permute_A_summary["mean"], 3) if permute_A_summary["mean"] else None,
    }

    # ---------------- STEP 3: best-of-family deflation (Bonferroni / Holm / maxT) -------------
    raw_p = {}
    mean_c, sd_c = {}, {}
    for c in U_full:
        arr = V[c]
        n = len(arr)
        mean = sum(arr) / n
        var = sum((x - mean) ** 2 for x in arr) / max(1, n - 1)
        sd = var ** 0.5
        mean_c[c] = mean
        sd_c[c] = sd
        raw_p[c] = count_ge_p(arr, obs_real[c], M_PERMUTE)

    # Bonferroni
    p_bonferroni = min(1.0, 72 * p_single_permute)

    # Holm (reuse e015_lib.holm, keyed by tkey string)
    raw_p_keyed = {L.tkey(c): raw_p[c] for c in U_full}
    holm_p_keyed = L.holm(raw_p_keyed)
    p_holm_A = holm_p_keyed[L.tkey(A)]

    # maxT
    degenerate = [L.tkey(c) for c in U_full if sd_c[c] < 1e-9]
    EPS = 1e-9
    Z = {c: [] for c in U_full}
    for c in U_full:
        s = max(sd_c[c], EPS)
        Z[c] = [(v - mean_c[c]) / s for v in V[c]]
    maxT_null = [max(Z[c][j] for c in U_full) for j in range(M_PERMUTE)]
    sA = max(sd_c[A], EPS)
    z_obs_A = (47 - mean_c[A]) / sA
    p_maxT = count_ge_p(maxT_null, z_obs_A, M_PERMUTE)

    maxT_summary = summarize(maxT_null)

    step3 = {
        "n_candidates": len(U_full),
        "p_single_confirmatory": p_single_permute,
        "p_bonferroni": round(p_bonferroni, 6),
        "p_holm": p_holm_A,
        "p_maxT": p_maxT,
        "z_obs_A": round(z_obs_A, 4),
        "maxT_null_summary": maxT_summary,
        "degenerate_sd_candidates": degenerate,
        "per_candidate_top10_by_raw_p": sorted(
            [{"candidate": L.tkey(c), "obs": obs_real[c], "null_mean": round(mean_c[c], 3),
              "raw_p": raw_p[c], "holm_p": holm_p_keyed[L.tkey(c)]} for c in U_full],
            key=lambda r: r["raw_p"])[:10],
    }

    # ---------------- STEP 4: positive control -------------------------------------------------
    def make_plant_corpus(rng, real_words, k_stems=K_STEMS_PLANT):
        # length profile from real GORILA words
        lens = [len(w) for w in real_words]
        uni = {}
        for w in real_words:
            for s in w:
                uni[s] = uni.get(s, 0) + 1
        signs = list(uni.keys())
        wts = [uni[s] for s in signs]
        n_total = len(real_words)
        n_plant_words = 2 * k_stems
        # stems: distinct 1-2 sign tuples drawn i.i.d. from real unigram
        stems = []
        tries = 0
        seen = set()
        while len(stems) < k_stems and tries < k_stems * 50:
            tries += 1
            slen = 1 if rng.random() < 0.6 else 2
            st = tuple(rng.choices(signs, weights=wts, k=slen))
            if st in seen:
                continue
            seen.add(st)
            stems.append(st)
        assert len(stems) == k_stems
        # NOTE (pre-result fix, logged in DEVIATIONS.md): productivities() dedupes the word list
        # into a set before computing recurrence, so two IDENTICAL plant words (PLANT+stem twice)
        # collapse to one and do NOT guarantee rc[stem]>=2 by themselves. Guarantee determinism
        # instead by inserting the bare stem as its own standalone word (satisfies the `t in wset`
        # branch of the recurrence test directly) alongside one PLANT+stem carrier word.
        plant_words = []
        stem_words = []
        for st in stems:
            plant_words.append((PLANT,) + st)
            stem_words.append(st)
        n_plant_words = k_stems + k_stems  # 1 carrier + 1 bare-stem word per stem
        n_filler = n_total - n_plant_words
        filler_lens = rng.choices(lens, k=n_filler)
        filler_words = [tuple(rng.choices(signs, weights=wts, k=fl)) for fl in filler_lens]
        corpus = plant_words + stem_words + filler_words
        rng.shuffle(corpus)
        return corpus

    rng_power = random.Random(SEED + 400)
    power_results = []
    for seed_i in range(N_POWER_SEEDS):
        r1 = random.Random(SEED + 500 + seed_i)
        plant_corpus = make_plant_corpus(r1, words)
        obs_plant = L.productivities(plant_corpus, [(PLANT, "PRE")])[(PLANT, "PRE")]
        r2 = random.Random(SEED + 600 + seed_i)
        null_vals = []
        for _ in range(N_POWER_NULL):
            pc = permute_corpus(plant_corpus, r2)
            null_vals.append(L.productivities(pc, [(PLANT, "PRE")])[(PLANT, "PRE")])
        p_plant = count_ge_p(null_vals, obs_plant, N_POWER_NULL)
        power_results.append({"seed": seed_i, "obs_plant": obs_plant, "p_plant": p_plant,
                               "k_stems_target": K_STEMS_PLANT})

    n_power_pass = sum(1 for r in power_results if r["p_plant"] <= ALPHA_PRIMARY)
    power_pass = (n_power_pass / N_POWER_SEEDS) >= 0.8

    # PC-calibration: R fresh independent PERMUTE draws of the REAL corpus, no true prefix
    # structure by construction, scored against the Step-2 M_PERMUTE reference pool.
    rng_calib = random.Random(SEED + 700)
    n_false_grad = 0
    calib_detail = []
    for r in range(R_CALIB):
        cand_corpus = permute_corpus(words, rng_calib)
        prod = L.productivities(cand_corpus, U_full)
        p_r = {}
        for c in U_full:
            p_r[L.tkey(c)] = count_ge_p(V[c], prod[c], M_PERMUTE)
        holm_r = L.holm(p_r)
        survivors = [k for k, p in holm_r.items() if p <= ALPHA_PRIMARY]
        if survivors:
            n_false_grad += 1
        calib_detail.append({"draw": r, "n_survivors": len(survivors), "survivors": survivors})

    false_grad_rate = n_false_grad / R_CALIB
    false_grad_cp_upper = clopper_pearson_upper(n_false_grad, R_CALIB)
    calibration_pass = false_grad_cp_upper <= ALPHA_FAMILY_SECONDARY

    pc_pass = bool(power_pass and calibration_pass)

    step4 = {
        "power": {"n_seeds": N_POWER_SEEDS, "n_pass_at_0.01": n_power_pass,
                  "pass_rate": round(n_power_pass / N_POWER_SEEDS, 3),
                  "pass_condition": ">=0.8 (20/25)", "power_pass": power_pass,
                  "detail": power_results},
        "calibration": {"R": R_CALIB, "n_false_graduations": n_false_grad,
                         "false_grad_rate": round(false_grad_rate, 4),
                         "false_grad_cp_upper_95": false_grad_cp_upper,
                         "pass_condition": "CP-upper-95% <= 0.05", "calibration_pass": calibration_pass},
        "pc_pass": pc_pass,
    }

    # ---------------- STEP 5: mechanical verdict ------------------------------------------------
    if not pc_pass:
        verdict = "HARNESS_NOT_VALIDATED"
    else:
        if p_single_permute > ALPHA_PRIMARY:
            verdict = "A_PREFIX_COLLAPSES"
        elif p_maxT <= ALPHA_FAMILY_SECONDARY:
            verdict = "A_PREFIX_SURVIVES_ADAPTIVE_NULL"
        else:
            verdict = "A_PREFIX_SURVIVES_CONFIRMATORY_BUT_NOT_BEST_OF_FAMILY"

    out = {
        "task_id": "EPOCH-022",
        "epoch": "EPOCH-022",
        "frontier": "sec12-adaptive-null-family-3-of-3",
        "gate": "A",
        "name": "dedicated adaptive-null family for A- prefixation (E015/E1 positive), independent of PC-LB",
        "plan_hash": open(os.path.join(CAMP, "epochs", "EPOCH-022", "plan_hash.txt")).read().strip(),
        "seed": SEED,
        "claim_ceiling": "L2/L3",
        "la_touched": True,
        "step1_reproduction": step1,
        "step2_adaptive_null": step2,
        "step3_family_deflation": step3,
        "step4_positive_control": step4,
        "verdict": verdict,
        "deviations": deviations,
        "n_docs": len(docs), "n_gorila_words": len(words), "n_candidates_universe": len(U_full),
        "search_receipt": {"K_prior_epochs_computing_this_statistic": 2,
                            "prior_epochs": ["E1(relphono)", "E015"]},
        "runtime_s": None,
    }
    out["runtime_s"] = round(time.time() - t0, 1)

    with open(os.path.join(CAMP, "epochs", "EPOCH-022", "result.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    with open(os.path.join(DATA, "calibration_detail.json"), "w") as fh:
        json.dump(calib_detail, fh, indent=1)
    with open(os.path.join(DATA, "power_detail.json"), "w") as fh:
        json.dump(power_results, fh, indent=1)
    with open(os.path.join(DATA, "permute_null_pool_A.json"), "w") as fh:
        json.dump(V[A], fh)
    with open(os.path.join(DATA, "family_top10.json"), "w") as fh:
        json.dump(step3["per_candidate_top10_by_raw_p"], fh, indent=1)

    print(json.dumps({k: v for k, v in out.items() if k not in
                       ("step4_positive_control",)}, indent=1, default=str)[:6000])
    print("VERDICT:", verdict)
    print("runtime_s", out["runtime_s"])
    return out


if __name__ == "__main__":
    run()
