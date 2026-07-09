#!/usr/bin/env python3
"""
EPOCH-068 machinery: frequency-matched stratified permutation test for
A-prefix vs non-A cross-site sharing.

Anonymous word-forms only. 'A' = anonymous word-initial slot label (no phonetic value).
Sharing = appears at >=2 distinct sites. Frequency confound controlled by permuting
A/non-A labels WITHIN each token-count stratum.
"""
import json, os, sys, hashlib
from collections import defaultdict
import random

CORPUS_DEFAULT = "corpus/silver/inscriptions_structured.json"


# ---------- data loading ----------
def load_types(corpus_path):
    """Return dict: type_tuple -> {'count': int, 'sites': set} for multi-sign types."""
    data = json.load(open(corpus_path))
    types = {}
    for ins in data:
        site = ins.get("site")
        if not site:
            continue
        words = ins.get("words") or []
        for w in words:
            if not isinstance(w, list):
                continue
            if len(w) < 2:  # multi-sign only
                continue
            t = tuple(w)
            if t not in types:
                types[t] = {"count": 0, "sites": set()}
            types[t]["count"] += 1
            types[t]["sites"].add(site)
    return types


def classify(types):
    """Return (A_inf, nonA_inf) dicts over count>=2 types."""
    A_inf, nonA_inf = {}, {}
    for t, v in types.items():
        if v["count"] < 2:
            continue
        if t[0] == "A":
            A_inf[t] = v
        else:
            nonA_inf[t] = v
    return A_inf, nonA_inf


# ---------- metric ----------
def share_rate(d):
    if not d:
        return float("nan")
    sh = sum(1 for v in d.values() if len(v["sites"]) >= 2)
    return sh / len(d), sh


def D_stat(A_inf, nonA_inf):
    sa, _ = share_rate(A_inf)
    sn, _ = share_rate(nonA_inf)
    return sa - sn


# ---------- stratified permutation null ----------
def build_strata(A_inf, nonA_inf):
    """
    Return dict: count -> list of 'shared' flags (1 if shared else 0) for ALL types in that stratum,
    plus the number of A-labels assigned in that stratum (real per-stratum A-count).
    """
    strata = defaultdict(list)
    a_per_stratum = defaultdict(int)
    for t, v in A_inf.items():
        c = v["count"]
        strata[c].append(1 if len(v["sites"]) >= 2 else 0)
        a_per_stratum[c] += 1
    for t, v in nonA_inf.items():
        c = v["count"]
        strata[c].append(1 if len(v["sites"]) >= 2 else 0)
    return strata, a_per_stratum


def permuted_D(strata, a_per_stratum, rng):
    """Draw one null D by permuting A/non-A labels within each stratum."""
    sum_a = 0
    n_a = 0
    sum_n = 0
    n_n = 0
    for c, shared_flags in strata.items():
        flags = list(shared_flags)
        rng.shuffle(flags)
        k = a_per_stratum[c]  # number assigned A-label in this stratum
        a_flags = flags[:k]
        n_flags = flags[k:]
        sum_a += sum(a_flags)
        n_a += len(a_flags)
        sum_n += sum(n_flags)
        n_n += len(n_flags)
    sa = sum_a / n_a if n_a else float("nan")
    sn = sum_n / n_n if n_n else float("nan")
    return sa - sn


def permutation_test(A_inf, nonA_inf, n_draws=2000, seed=12345):
    rng = random.Random(seed)
    D_obs = D_stat(A_inf, nonA_inf)
    strata, a_per_stratum = build_strata(A_inf, nonA_inf)
    null = []
    ge = 0
    for _ in range(n_draws):
        d = permuted_D(strata, a_per_stratum, rng)
        null.append(d)
        if d >= D_obs:
            ge += 1
    p = (ge + 1) / (n_draws + 1)  # add-1 to avoid p=0
    mean_null = sum(null) / len(null)
    return {
        "D_obs": D_obs,
        "null_mean": mean_null,
        "perm_p": p,
        "n_draws": n_draws,
        "null": null,
    }


# ---------- positive controls (synthetic) ----------
def detect_control(types, n_draws=2000, seed=7):
    """
    (a) DETECT: within each stratum, assign the A-label to the MOST-shared types
    (i.e. shared types first, then non-shared). Confirm perm p<=0.05.
    """
    A_inf, nonA_inf = classify(types)
    strata, a_per_stratum = build_strata(A_inf, nonA_inf)
    # rebuild synthetic A_inf / nonA_inf: within each stratum, give A-label to shared types first
    syn_A, syn_nonA = {}, {}
    # need the actual type objects per stratum
    per_stratum_types = defaultdict(list)
    all_inf = {}
    all_inf.update(A_inf)
    all_inf.update(nonA_inf)
    for t, v in all_inf.items():
        per_stratum_types[v["count"]].append(t)
    for c, tlist in per_stratum_types.items():
        k = a_per_stratum[c]
        # sort: shared first
        tlist_sorted = sorted(tlist, key=lambda t: -(1 if len(all_inf[t]["sites"]) >= 2 else 0))
        for t in tlist_sorted[:k]:
            syn_A[t] = all_inf[t]
        for t in tlist_sorted[k:]:
            syn_nonA[t] = all_inf[t]
    res = permutation_test(syn_A, syn_nonA, n_draws=n_draws, seed=seed)
    return res["perm_p"]


def false_positive_control(types, n_trials=20, n_draws=1000, seed=101):
    """
    (b) FALSE-POSITIVE: assign A/non-A labels at RANDOM within strata (using real per-stratum A-counts);
    confirm rejection rate (perm p<=0.05) <= 0.10 across >=20 draws.
    """
    A_inf, nonA_inf = classify(types)
    strata, a_per_stratum = build_strata(A_inf, nonA_inf)
    all_inf = {}
    all_inf.update(A_inf)
    all_inf.update(nonA_inf)
    per_stratum_types = defaultdict(list)
    for t, v in all_inf.items():
        per_stratum_types[v["count"]].append(t)
    rejections = 0
    ps = []
    for trial in range(n_trials):
        rng = random.Random(seed + trial)
        syn_A, syn_nonA = {}, {}
        for c, tlist in per_stratum_types.items():
            k = a_per_stratum[c]
            tt = list(tlist)
            rng.shuffle(tt)
            for t in tt[:k]:
                syn_A[t] = all_inf[t]
            for t in tt[k:]:
                syn_nonA[t] = all_inf[t]
        res = permutation_test(syn_A, syn_nonA, n_draws=n_draws, seed=seed + 1000 + trial)
        p = res["perm_p"]
        ps.append(p)
        if p <= 0.05:
            rejections += 1
    return rejections / n_trials, ps


def power_check(types, target_gap=0.3, n_trials=200, n_draws=500, seed=2024):
    """
    (c) POWER: with REAL per-stratum A-counts, plant a +target_gap sharing advantage for A-labels
    and estimate detection power (frac of trials with perm p<=0.05).

    Planting: within each stratum, we want A-labeled types to have a sharing rate ~target_gap higher
    than nonA. We do this by, within each stratum, choosing which types are 'shared' for the A group
    to enforce an elevated rate, then assign A-labels preferentially to shared types up to the planted
    A-shared count, rest to non-shared.

    Implementation: for each stratum with k A-labels and S shared types total:
      planted_A_shared = min(k, round(k * (base_share_rate + target_gap))) but capped by S.
    Simpler & robust: assign A-labels to shared types first until planted_A_shared reached, then fill.
    """
    A_inf, nonA_inf = classify(types)
    strata, a_per_stratum = build_strata(A_inf, nonA_inf)
    all_inf = {}
    all_inf.update(A_inf)
    all_inf.update(nonA_inf)
    per_stratum_types = defaultdict(list)
    for t, v in all_inf.items():
        per_stratum_types[v["count"]].append(t)

    # compute observed per-stratum A share rate to plant from
    detections = 0
    ps = []
    for trial in range(n_trials):
        rng = random.Random(seed + trial)
        syn_A, syn_nonA = {}, {}
        for c, tlist in per_stratum_types.items():
            k = a_per_stratum[c]
            if k == 0:
                for t in tlist:
                    syn_nonA[t] = all_inf[t]
                continue
            shared = [t for t in tlist if len(all_inf[t]["sites"]) >= 2]
            nonshared = [t for t in tlist if len(all_inf[t]["sites"]) < 2]
            # base A share rate in this stratum (observed)
            base = sum(1 for t in tlist if len(all_inf[t]["sites"]) >= 2) / max(1, len(tlist))
            planted_rate = min(1.0, base + target_gap)
            planted_A_shared = min(k, round(planted_rate * k), len(shared))
            # take planted_A_shared shared types as A
            rng.shuffle(shared)
            rng.shuffle(nonshared)
            a_shared = shared[:planted_A_shared]
            a_nonshared = nonshared[: k - planted_A_shared]
            # if not enough nonshared, fill from remaining shared
            need = k - len(a_shared) - len(a_nonshared)
            if need > 0:
                a_shared += shared[planted_A_shared:planted_A_shared + need]
            a_types = a_shared + a_nonshared
            a_set = set(a_types)
            for t in tlist:
                if t in a_set:
                    syn_A[t] = all_inf[t]
                else:
                    syn_nonA[t] = all_inf[t]
        res = permutation_test(syn_A, syn_nonA, n_draws=n_draws, seed=seed + 5000 + trial)
        p = res["perm_p"]
        ps.append(p)
        if p <= 0.05:
            detections += 1
    return detections / n_trials, ps


# ---------- self-check ----------
def self_check():
    """Validate the stratified label-permutation null on a synthetic; confirm E[D]~=0."""
    # synthetic: 2 strata, random sharing, random A assignment -> E[D_null] should be ~0
    rng = random.Random(42)
    types = {}
    # stratum count=2: 40 types, ~50% shared
    for i in range(40):
        sites = set(["S1", "S2"]) if rng.random() < 0.5 else set(["S1"])
        types[("X", str(i))] = {"count": 2, "sites": sites}
    # stratum count=3: 30 types, ~50% shared
    for i in range(30):
        sites = set(["S1", "S2"]) if rng.random() < 0.5 else set(["S1"])
        types[("Y", str(i))] = {"count": 3, "sites": sites}
    # assign A-label randomly to ~half within each stratum
    A_inf, nonA_inf = {}, {}
    per_c = defaultdict(list)
    for t, v in types.items():
        per_c[v["count"]].append(t)
    for c, ts in per_c.items():
        rng.shuffle(ts)
        k = len(ts) // 2
        for t in ts[:k]:
            A_inf[t] = types[t]
        for t in ts[k:]:
            nonA_inf[t] = types[t]
    res = permutation_test(A_inf, nonA_inf, n_draws=2000, seed=99)
    # E[D_null] should be ~0 because labels random within stratum
    mean_null = res["null_mean"]
    D_obs = res["D_obs"]
    ok = abs(mean_null) < 0.05
    print(f"[self-check] D_obs={D_obs:.4f}  E[D_null]={mean_null:.4f}  perm_p={res['perm_p']:.4f}")
    print(f"[self-check] |E[D_null]|<0.05 : {ok}")
    # also: when A-label is random, perm_p should be uniform-ish (not systematically small)
    return ok


if __name__ == "__main__":
    print("=== EPOCH-068 machinery self-check ===")
    ok = self_check()
    print("self-check passed:", ok)
    sys.exit(0 if ok else 1)
