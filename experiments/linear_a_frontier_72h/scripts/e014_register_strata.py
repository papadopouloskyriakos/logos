#!/usr/bin/env python3
"""EPOCH-014 — register-stratified phonotactics (value-free strata test).

Prereg: epochs/EPOCH-014/prereg.md
plan_hash 017c615febb848749e72c941789542e5dce214ca0b956a8eda6400ede7be2ff9 (frozen 2026-07-08T05:14:39Z)

Pipeline (all mechanical, seed 20260708):
  registers by physical support -> word streams (>=2-sign words, signs as identities)
  -> bigram JSD (add-0.5 smoothing, union support) vs document-length-matched label
  permutation -> Holm over 3 LA pairs -> recurrent-word-removal attribution
  -> within-register site control -> frozen verdict.

Controls run FIRST: PC1 (LB KN-A vs KN-D must fire), PC2 (random split of KN-D must
not fire, FP<=3/20), PC3 (power at LA-matched sizes), LB single-language benchmark.
"""
from __future__ import annotations

import json
import math
import os
import sys
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.dirname(HERE)
WORKTREE = os.path.dirname(os.path.dirname(CAMP))
sys.path.insert(0, WORKTREE)

from scripts.cross_script.data import _damos_wordforms  # noqa: E402

LA_STRUCT = os.path.join(WORKTREE, "corpus", "silver", "inscriptions_structured.json")
DAMOS = os.path.join(WORKTREE, "corpus", "bronze", "linearb", "damos", "items.jsonl")
OUTDIR = os.path.join(CAMP, "data", "register_strata")
SEED = 20260708
N_PERM = 2000
N_PERM_FAST = 500
ALPHA = 0.05
MIN_SIGN_COUNT = 10          # pooled per-script; rarer signs -> OTH
LEN_BINS = [1, 2, 5, 10]     # word-count bins: 1 | 2 | 3-5 | 6-10 | >=11
RECUR_MIN_DOCS = 3

os.makedirs(OUTDIR, exist_ok=True)


# --------------------------------------------------------------------- loaders

def load_la_registers():
    reg_map = {"Stone vessel": "LIB", "Tablet": "LEDG",
               "Nodule": "SEAL", "Roundel": "SEAL", "Sealing": "SEAL"}
    docs = defaultdict(list)   # register -> list of (doc_id, site, [words])
    data = json.load(open(LA_STRUCT))
    for x in data:
        r = reg_map.get(x["support"])
        if not r:
            continue
        words = [tuple(w) for w in x["words"] if len(w) >= 2]
        if not words:
            continue
        docs[r].append((x["id"], x["site"], words))
    return docs


def load_lb_registers():
    docs = defaultdict(list)
    with open(DAMOS) as fh:
        for line in fh:
            rec = json.loads(line)
            it = rec.get("item") or {}
            h = it.get("heading") or ""
            site = h.split()[0] if h else "?"
            ser = it.get("series") or ""
            if site != "KN" or ser not in ("A", "D"):
                continue
            words = [tuple(w) for w in _damos_wordforms(it.get("content") or "")]
            if not words:
                continue
            docs["KN-" + ser].append((str(rec.get("_id")), site, words))
    return docs


def build_alphabet(all_docs_lists):
    """Pooled per-script alphabet; signs with count < MIN_SIGN_COUNT -> OTH."""
    c = Counter()
    for docs in all_docs_lists:
        for _, _, words in docs:
            for w in words:
                c.update(w)
    keep = {s for s, n in c.items() if n >= MIN_SIGN_COUNT}
    return keep


def doc_bigrams(words, keep):
    """Counter of bigram ids for one document (with # boundaries)."""
    c = Counter()
    for w in words:
        s = ["#"] + [x if x in keep else "OTH" for x in w] + ["#"]
        for a, b in zip(s, s[1:]):
            c[(a, b)] += 1
    return c


def doc_positional(words, keep):
    ini, fin = Counter(), Counter()
    for w in words:
        ini[w[0] if w[0] in keep else "OTH"] += 1
        fin[w[-1] if w[-1] in keep else "OTH"] += 1
    return ini, fin


# --------------------------------------------------------- JSD + permutation

def _jsd_from_counts(ca: np.ndarray, cb: np.ndarray, alpha=0.5) -> float:
    pa = ca + alpha
    pb = cb + alpha
    pa = pa / pa.sum()
    pb = pb / pb.sum()
    m = 0.5 * (pa + pb)
    def kl(p, q):
        return float(np.sum(p * (np.log2(p) - np.log2(q))))
    return 0.5 * kl(pa, m) + 0.5 * kl(pb, m)


def _len_bin(n_words: int) -> int:
    for i, b in enumerate(LEN_BINS):
        if n_words <= b:
            return i
    return len(LEN_BINS)


def pair_test(docs_a, docs_b, keep, n_perm, rng, want_secondary=True):
    """docs_*: list of (id, site, words). Returns dict of results."""
    # per-doc bigram vectors over union support
    ca = [doc_bigrams(w, keep) for _, _, w in docs_a]
    cb = [doc_bigrams(w, keep) for _, _, w in docs_b]
    support = sorted(set().union(*ca, *cb))
    idx = {bg: i for i, bg in enumerate(support)}
    M = np.zeros((len(ca) + len(cb), len(support)))
    for r, c in enumerate(ca + cb):
        for bg, n in c.items():
            M[r, idx[bg]] = n
    lab = np.array([0] * len(ca) + [1] * len(cb))
    bins = np.array([_len_bin(len(w)) for _, _, w in docs_a] +
                    [_len_bin(len(w)) for _, _, w in docs_b])

    def jsd_for(labels):
        return _jsd_from_counts(M[labels == 0].sum(0), M[labels == 1].sum(0))

    obs = jsd_for(lab)
    perm = np.empty(n_perm)
    for k in range(n_perm):
        pl = lab.copy()
        for b in np.unique(bins):
            m = bins == b
            pl[m] = rng.permutation(pl[m])
        perm[k] = jsd_for(pl)
    p = (1 + int((perm >= obs).sum())) / (1 + n_perm)
    mean_null = float(perm.mean())
    excess = obs - mean_null
    out = {
        "n_docs": [len(ca), len(cb)],
        "n_words": [int(sum(len(w) for _, _, w in docs_a)),
                    int(sum(len(w) for _, _, w in docs_b))],
        "n_bigram_tokens": [int(M[lab == 0].sum()), int(M[lab == 1].sum())],
        "jsd_obs": round(obs, 6), "null_mean": round(mean_null, 6),
        "null_p95": round(float(np.quantile(perm, 0.95)), 6),
        "excess": round(excess, 6),
        "excess_ratio": round(excess / mean_null, 4) if mean_null > 0 else None,
        "p_perm": round(p, 6), "n_perm": n_perm,
    }
    if want_secondary:
        for name, fn in (("initial", 0), ("final", 1)):
            da = Counter(); db = Counter()
            for _, _, w in docs_a:
                x = doc_positional(w, keep)[fn]; da.update(x)
            for _, _, w in docs_b:
                x = doc_positional(w, keep)[fn]; db.update(x)
            sup = sorted(set(da) | set(db))
            va = np.array([da[s] for s in sup], float)
            vb = np.array([db[s] for s in sup], float)
            out[f"jsd_{name}_descriptive"] = round(_jsd_from_counts(va, vb), 6)
        out["mean_word_len"] = [
            round(float(np.mean([len(x) for _, _, w in docs_a for x in w])), 3),
            round(float(np.mean([len(x) for _, _, w in docs_b for x in w])), 3)]
    return out


def holm(pvals: dict) -> dict:
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    adj = {}
    prev = 0.0
    for i, (k, p) in enumerate(items):
        a = min(1.0, (m - i) * p)
        prev = max(prev, a)
        adj[k] = round(prev, 6)
    return adj


def recurrent_types(docs, min_docs=RECUR_MIN_DOCS):
    dcount = Counter()
    for _, _, words in docs:
        for t in set(words):
            dcount[t] += 1
    return {t for t, n in dcount.items() if n >= min_docs}


def remove_types(docs, types):
    out = []
    for did, site, words in docs:
        w2 = [w for w in words if w not in types]
        if w2:
            out.append((did, site, w2))
    return out


def subsample_to_words(docs, target_words, rng):
    order = rng.permutation(len(docs))
    got, sel = 0, []
    for i in order:
        sel.append(docs[i])
        got += len(docs[i][2])
        if got >= target_words:
            break
    return sel


# ---------------------------------------------------------------------- main

def main():
    rng = np.random.default_rng(SEED)
    res = {"seed": SEED}

    la = load_la_registers()
    lb = load_lb_registers()
    keep_la = build_alphabet([la["LIB"], la["LEDG"], la["SEAL"]])
    keep_lb = build_alphabet([lb["KN-A"], lb["KN-D"]])
    res["alphabet"] = {"LA_kept_signs": len(keep_la), "LB_kept_signs": len(keep_lb)}
    res["corpus"] = {r: {"docs": len(v), "words": sum(len(w) for _, _, w in v)}
                     for r, v in list(la.items()) + list(lb.items())}

    # ---------------- PC1: LB known register contrast must fire (FIRST)
    print("PC1: LB KN-A vs KN-D ...")
    pc1 = pair_test(lb["KN-A"], lb["KN-D"], keep_lb, N_PERM, rng)
    pc1["pass"] = pc1["p_perm"] < ALPHA
    res["PC1_LB_A_vs_D"] = pc1
    print("  ", pc1["jsd_obs"], "p", pc1["p_perm"], "pass", pc1["pass"])

    # ---------------- PC2: random split of KN-D must NOT fire
    print("PC2: 20 random splits of KN-D ...")
    fp = 0
    pc2_ps = []
    for rep in range(20):
        d = lb["KN-D"]
        perm = rng.permutation(len(d))
        half = len(d) // 2
        A = [d[i] for i in perm[:half]]
        B = [d[i] for i in perm[half:]]
        r = pair_test(A, B, keep_lb, N_PERM_FAST, rng, want_secondary=False)
        pc2_ps.append(r["p_perm"])
        if r["p_perm"] < ALPHA:
            fp += 1
    res["PC2_random_split"] = {"fp": fp, "of": 20, "pass": fp <= 3,
                               "pvals": [round(p, 4) for p in pc2_ps]}
    print("   FP", fp, "/20")

    machinery_ok = pc1["pass"] and res["PC2_random_split"]["pass"]
    res["machinery_ok"] = machinery_ok

    # ---------------- PC3: power at LA-matched sizes
    la_pairs = [("LIB", "LEDG"), ("LIB", "SEAL"), ("LEDG", "SEAL")]
    print("PC3: power at LA pair sizes ...")
    pc3 = {}
    for a, b in la_pairs:
        wa = sum(len(w) for _, _, w in la[a])
        wb = sum(len(w) for _, _, w in la[b])
        lo, hi = min(wa, wb), max(wa, wb)
        det = 0
        for rep in range(10):
            A = subsample_to_words(lb["KN-A"], lo, rng)
            B = subsample_to_words(lb["KN-D"], hi, rng)
            r = pair_test(A, B, keep_lb, N_PERM_FAST, rng, want_secondary=False)
            if r["p_perm"] < ALPHA:
                det += 1
        pc3[f"{a}-{b}"] = {"target_words": [lo, hi], "detect": det, "of": 10,
                           "power": det >= 7}
        print(f"   {a}-{b}: {det}/10")
    res["PC3_power"] = pc3

    # ---------------- LB single-language benchmark (step-3 calibration)
    print("LB benchmark: recurrent-word removal on KN-A vs KN-D ...")
    rt = recurrent_types(lb["KN-A"]) | recurrent_types(lb["KN-D"])
    A2 = remove_types(lb["KN-A"], rt)
    D2 = remove_types(lb["KN-D"], rt)
    blb = pair_test(A2, D2, keep_lb, N_PERM, rng)
    blb["n_recurrent_types_removed"] = len(rt)
    res["LB_benchmark_postremoval"] = blb
    B_LB = blb["excess_ratio"] if blb["excess_ratio"] is not None else 0.0
    print("   post-removal p", blb["p_perm"], "excess_ratio", B_LB)

    # ---------------- LA pairwise tests
    print("LA pairs ...")
    la_res = {}
    for a, b in la_pairs:
        r = pair_test(la[a], la[b], keep_la, N_PERM, rng)
        la_res[f"{a}-{b}"] = r
        print(f"   {a}-{b}: jsd {r['jsd_obs']} p {r['p_perm']} xr {r['excess_ratio']}")
    adj = holm({k: v["p_perm"] for k, v in la_res.items()})
    for k in la_res:
        la_res[k]["p_holm"] = adj[k]
        la_res[k]["holm_significant"] = adj[k] < ALPHA
    res["LA_pairs"] = la_res

    sig_pairs = [k for k, v in la_res.items() if v["holm_significant"]]

    # ---------------- Step 4: within-register site control
    print("Site control ...")
    site_res = {}
    for reg in ("LEDG", "SEAL"):
        ht = [d for d in la[reg] if d[1] == "Haghia Triada"]
        nht = [d for d in la[reg] if d[1] != "Haghia Triada"]
        wh = sum(len(w) for _, _, w in ht)
        wn = sum(len(w) for _, _, w in nht)
        if wh < 30 or wn < 30:
            site_res[reg] = {"runnable": False, "words": [wh, wn]}
            continue
        r = pair_test(ht, nht, keep_la, N_PERM, rng)
        r["runnable"] = True
        site_res[reg] = r
        print(f"   {reg} HT/nonHT: jsd {r['jsd_obs']} p {r['p_perm']} xr {r['excess_ratio']}")
    res["site_control"] = site_res
    S = max([v["excess_ratio"] for v in site_res.values()
             if v.get("runnable") and v["excess_ratio"] is not None], default=0.0)
    res["site_benchmark_S"] = S

    surviving = []
    for k in sig_pairs:
        discounted = la_res[k]["excess_ratio"] is not None and la_res[k]["excess_ratio"] <= S
        la_res[k]["site_discounted"] = discounted
        if not discounted:
            surviving.append(k)

    # ---------------- Step 3: vocabulary attribution on surviving pairs
    post = {}
    if surviving:
        print("Step 3: recurrent-word removal on surviving pairs ...")
        for k in surviving:
            a, b = k.split("-")
            rt = recurrent_types(la[a]) | recurrent_types(la[b])
            A2 = remove_types(la[a], rt)
            B2 = remove_types(la[b], rt)
            r = pair_test(A2, B2, keep_la, N_PERM, rng)
            r["n_recurrent_types_removed"] = len(rt)
            post[k] = r
            print(f"   {k}: post jsd {r['jsd_obs']} p {r['p_perm']} xr {r['excess_ratio']}")
        adj2 = holm({k: v["p_perm"] for k, v in post.items()})
        for k in post:
            post[k]["p_holm"] = adj2[k]
            post[k]["holm_significant"] = adj2[k] < ALPHA
    res["LA_postremoval"] = post

    # non-gating robustness: strongest surviving pair token-matched to site-pair size
    if surviving and any(v.get("runnable") for v in site_res.values()):
        k = max(surviving, key=lambda k: la_res[k]["excess_ratio"] or 0)
        a, b = k.split("-")
        sreg = max((r for r in site_res if site_res[r].get("runnable")),
                   key=lambda r: site_res[r]["excess_ratio"] or 0)
        tw = sorted(site_res[sreg]["n_words"])
        xrs, ps = [], []
        for rep in range(10):
            A = subsample_to_words(la[a] if sum(len(w) for _, _, w in la[a]) <= sum(len(w) for _, _, w in la[b]) else la[b], tw[0], rng)
            B = subsample_to_words(la[b] if sum(len(w) for _, _, w in la[a]) <= sum(len(w) for _, _, w in la[b]) else la[a], tw[1], rng)
            r = pair_test(A, B, keep_la, N_PERM_FAST, rng, want_secondary=False)
            xrs.append(r["excess_ratio"]); ps.append(r["p_perm"])
        res["robustness_matched_subsample"] = {
            "pair": k, "matched_to_site_pair": sreg, "target_words": tw,
            "median_excess_ratio": round(float(np.median([x for x in xrs if x is not None])), 4),
            "median_p": round(float(np.median(ps)), 4),
            "site_excess_ratio": site_res[sreg]["excess_ratio"]}

    # ---------------- verdict (frozen rules)
    if not machinery_ok:
        verdict = "REGISTER_STRATA_NO_POWER"
        why = "machinery gate failed (PC1/PC2)"
    elif not sig_pairs:
        if all(pc3[f"{a}-{b}"]["power"] for a, b in la_pairs):
            verdict = "REGISTER_STRATA_ABSENT"
            why = "no Holm-significant pair; PC3 power at all pair sizes"
        else:
            verdict = "REGISTER_STRATA_NO_POWER"
            why = "no Holm-significant pair and PC3 power missing for >=1 pair"
    elif not surviving:
        verdict = "REGISTER_STRATA_NO_POWER"
        why = "all significant pairs site-discounted (excess_ratio <= site benchmark)"
    else:
        systemic = [k for k in post
                    if post[k]["holm_significant"] and post[k]["excess"] > 0]
        if systemic:
            verdict = "REGISTER_STRATA_SYSTEMIC"
            drv = max(systemic, key=lambda k: post[k]["excess_ratio"] or 0)
            exceeds = (post[drv]["excess_ratio"] or 0) > B_LB
            why = (f"driving pair {drv}; post-removal excess_ratio "
                   f"{post[drv]['excess_ratio']} vs LB single-language benchmark {B_LB} "
                   f"-> interpretation gate {'EXCEEDED: wording -consistent with distinct strata- allowed' if exceeds else 'NOT exceeded: within single-language range'}")
            res["interpretation_gate"] = {"driving_pair": drv, "B_LB": B_LB,
                                          "exceeded": bool(exceeds)}
        else:
            verdict = "REGISTER_STRATA_VOCABULARY_ONLY"
            why = "significant pair(s) lose Holm significance after recurrent-word removal"

    res["verdict"] = verdict
    res["verdict_basis"] = why
    print("\nVERDICT:", verdict, "|", why)

    with open(os.path.join(OUTDIR, "e014_results.json"), "w") as f:
        json.dump(res, f, indent=1)
    print("wrote", os.path.join(OUTDIR, "e014_results.json"))
    return res


if __name__ == "__main__":
    main()
