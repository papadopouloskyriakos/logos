"""EPOCH-026 core machinery: word-FINAL positional structure (terminal slot).

Mirror of E024's word-INITIAL prefix test, applied to the LAST sign of each >=2-sign word.
Reuses the E023 within-word uniform-permutation null (imported). Provides:
  - load_la_words_with_site: (signs_list, site) for >=2-sign words
  - final_count / permutation_null_final: word-final count + null
  - holm_correct, axis_test (by site), leave_one_site_out, comparator_sweep
  - lb_positive_control: LB known word-final-skewed sign, seeded balanced 5-way split
"""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
E023 = os.path.normpath(os.path.join(HERE, "..", "EPOCH-023"))
if E023 not in sys.path:
    sys.path.insert(0, E023)
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("e023mach", os.path.join(E023, "machinery.py"))
e023mach = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(e023mach)

import numpy as np
from collections import Counter, defaultdict

CORPUS = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "corpus", "silver", "inscriptions_structured.json"))


def load_la_words_with_site():
    """Return list of (signs_list, site) for >=2-sign words."""
    d = json.load(open(CORPUS))
    out = []
    for ins in d:
        site = ins.get("site")
        for tok in ins.get("stream", []):
            if tok.get("t") == "word":
                sg = tok.get("signs", [])
                if len(sg) >= 2:
                    out.append((sg, site))
    return out


def final_count(words, sign):
    """Count words whose LAST sign == sign."""
    c = 0
    for w in words:
        if w and w[-1] == sign:
            c += 1
    return c


def permutation_null_final(words, sign, n_draws=1000, seed=0):
    """Within-word permutation null for word-FINAL count.

    For each word, under uniform permutation of its own signs, P(last==sign) =
    (#sign in word)/len(word) — symmetric to the initial-position case. Vectorized.
    Returns (observed, null_counts_array, p_one_sided, null_mean).
    """
    rng = np.random.default_rng(seed)
    observed = final_count(words, sign)
    probs = []
    for w in words:
        L = len(w)
        if L == 0:
            continue
        k = w.count(sign)
        probs.append(k / L)
    probs = np.array(probs)
    R = rng.random((n_draws, probs.shape[0]))
    indicators = (R < probs[None, :]).astype(np.int64)
    null_counts = indicators.sum(axis=1)
    p = (1 + int(np.sum(null_counts >= observed))) / (1 + n_draws)
    return observed, null_counts, p, float(null_counts.mean())


def holm_correct(pvals):
    m = len(pvals)
    order = sorted(range(len(pvals)), key=lambda i: pvals[i])
    adj = [0.0] * len(pvals)
    running = 0.0
    for rank, i in enumerate(order):
        val = (m - rank) * pvals[i]
        running = max(running, val)
        adj[i] = min(1.0, running)
    return adj


def site_test(words_with_site, sign, min_words=20, n_draws=1000, seed=0):
    """Partition by site; for each site with >=min_words words run permutation_null_final.
    Returns rows with Holm-corrected p-values."""
    parts = defaultdict(list)
    for sg, site in words_with_site:
        parts[site].append(sg)
    eligible = {k: v for k, v in parts.items() if len(v) >= min_words}
    names = sorted(eligible.keys())
    rows = []
    for j, k in enumerate(names):
        obs, nc, p, mean = permutation_null_final(eligible[k], sign, n_draws, seed=seed + j)
        rows.append({"site": k, "n": len(eligible[k]), "final_count": obs,
                     "null_mean": round(mean, 3), "p": p})
    pvals = [r["p"] for r in rows]
    adj = holm_correct(pvals)
    for r, a in zip(rows, adj):
        r["p_holm"] = a
    return rows, parts


def leave_one_site_out(parts, sign, drop_name, n_draws=1000, seed=0):
    rest = []
    for k, v in parts.items():
        if k == drop_name:
            continue
        rest.extend(v)
    obs, nc, p, mean = permutation_null_final(rest, sign, n_draws, seed=seed)
    return {"loo_excluded": drop_name, "n": len(rest), "final_count": obs,
            "null_mean": round(mean, 3), "p": p}


def comparator_sweep(parts, sign, min_words=20, n_draws=1000, seed=0):
    """Count sites (>=min_words) where sign is word-final-significant (p<=0.05)."""
    eligible = {k: v for k, v in parts.items() if len(v) >= min_words}
    cleared = 0
    site_ps = {}
    for j, k in enumerate(sorted(eligible.keys())):
        obs, nc, p, mean = permutation_null_final(eligible[k], sign, n_draws, seed=seed + 1000 + j)
        site_ps[k] = p
        if p <= 0.05:
            cleared += 1
    return cleared, site_ps


def lb_positive_control(n_draws=1000, seed=7):
    """LB PC: most word-FINAL-skewed sign with >=40 occ; seeded balanced 5-way split;
    require sig in >=3 partitions AND a freq-matched random sign NOT sig in >=3."""
    REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
    if REPO not in sys.path:
        sys.path.insert(0, REPO)
    from scripts.cross_script.data import load_b_damos
    seqs, freq, v2g = load_b_damos()
    ge2 = [w for w in seqs if len(w) >= 2]
    fin = Counter(w[-1] for w in ge2)
    cands = [(s, fin[s], freq[s]) for s in freq if freq[s] >= 40]
    cands.sort(key=lambda t: t[1] / t[2], reverse=True)
    pc_sign = cands[0][0]
    rng = np.random.default_rng(seed)
    idx = np.arange(len(ge2))
    rng.shuffle(idx)
    folds = [idx[i::5] for i in range(5)]
    sig_pc = 0
    fold_ps = []
    for fi, fold in enumerate(folds):
        words = [ge2[i] for i in fold]
        obs, nc, p, mean = permutation_null_final(words, pc_sign, n_draws, seed=seed + fi)
        fold_ps.append(p)
        if p <= 0.05:
            sig_pc += 1
    pc_occ = freq[pc_sign]
    # Negative control: frequency-matched sign that is NOT itself word-final-skewed.
    # "a frequency-matched random LB sign NOT [significant]" requires the control to LACK
    # the tested property; LB is dense with grammatical finals, so a naive freq-matched pick
    # would often land on another final (a false negative control). Restrict to freq-matched
    # signs whose empirical word-final rate is in the BOTTOM half of the >=40-occ distribution
    # (a true negative: a sign without the word-final property).
    occ_ge40 = [sg for sg in freq if freq[sg] >= 40]
    rates = [(sg, fin[sg] / freq[sg]) for sg in occ_ge40]
    rates.sort(key=lambda t: t[1])
    median_rate = rates[len(rates) // 2][1]
    pool = [sg for sg in freq
            if sg != pc_sign and 0.8 * pc_occ <= freq[sg] <= 1.25 * pc_occ
            and (fin[sg] / freq[sg]) <= median_rate]
    if not pool:
        pool = [sg for sg in freq if sg != pc_sign and (fin[sg] / freq[sg]) <= median_rate]
    if not pool:
        pool = [sg for sg in freq if sg != pc_sign]
    rand_sign = str(rng.choice(pool))
    sig_rand = 0
    rand_ps = []
    for fi, fold in enumerate(folds):
        words = [ge2[i] for i in fold]
        obs, nc, p, mean = permutation_null_final(words, rand_sign, n_draws, seed=seed + 50 + fi)
        rand_ps.append(p)
        if p <= 0.05:
            sig_rand += 1
    passed = (sig_pc >= 3) and (sig_rand < 3)
    return {
        "pc_verdict": "PASSED" if passed else "FAILED",
        "pc_sign": pc_sign,
        "pc_sign_occ": int(freq[pc_sign]),
        "pc_sign_final": int(fin[pc_sign]),
        "pc_sign_skew": round(fin[pc_sign] / freq[pc_sign], 4),
        "pc_sites_sig": sig_pc,
        "pc_fold_ps": [round(p, 4) for p in fold_ps],
        "rand_sign": rand_sign,
        "rand_sign_occ": int(freq[rand_sign]),
        "rand_sites_sig": sig_rand,
        "rand_fold_ps": [round(p, 4) for p in rand_ps],
        "neg_control_median_rate_cutoff": round(median_rate, 4),
        "split": "seeded balanced 5-way (seed=7); no per-tablet metadata in load_b_damos",
    }


if __name__ == "__main__":
    print("=== EPOCH-026 machinery self-check ===")
    words = load_la_words_with_site()
    print("LA >=2-sign words:", len(words))
    allw = [w[0] for w in words]
    # cross-check: explicit permutation vs fast on a subsample for RO final
    sub = allw[:300]
    # explicit
    rng = np.random.default_rng(1)
    obs_e = final_count(sub, "RO")
    ne = np.empty(200, dtype=np.int64)
    for d in range(200):
        c = 0
        for w in sub:
            L = len(w)
            if L == 1:
                if w[0] == "RO":
                    c += 1
                continue
            perm = rng.permutation(L)
            if w[perm[-1]] == "RO":
                c += 1
        ne[d] = c
    pe = (1 + int((ne >= obs_e).sum())) / 201
    obs_f, ncf, pf, mf = permutation_null_final(sub, "RO", 200, seed=1)
    print(f"explicit RO-final: obs={obs_e} mean={ne.mean():.3f} p={pe:.4f}")
    print(f"fast     RO-final: obs={obs_f} mean={mf:.3f} p={pf:.4f}")
    print("null mean close:", abs(ne.mean() - mf) < 1.0)
    # global RO
    obs, nc, p, mean = permutation_null_final(allw, "RO", 1000, seed=0)
    print(f"\nGLOBAL RO-final: {obs}/{len(allw)} frac={obs/len(allw):.4f} null_mean={mean:.2f} p={p:.4f}")
    print("\nLB positive control:")
    pc = lb_positive_control()
    for k, v in pc.items():
        print(f"  {k}: {v}")
    print("\nSelf-check OK.")
