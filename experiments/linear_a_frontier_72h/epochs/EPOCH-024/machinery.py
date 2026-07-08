"""EPOCH-024 core machinery: A- prefixation multi-axis held-out robustness.

Reuses the E023 within-word uniform-permutation null (imported). Adds:
  - partition extraction by `support` / `context`
  - Holm correction across a family
  - leave-one-partition-out
  - comparator sweep
  - LB positive control (seeded balanced 5-way split)
"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
E023 = os.path.normpath(os.path.join(HERE, "..", "EPOCH-023"))
if E023 not in sys.path:
    sys.path.insert(0, E023)
# import E023 machinery (as e023mach to avoid name collision with this module)
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("e023mach", os.path.join(E023, "machinery.py"))
e023mach = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(e023mach)
permutation_null = e023mach.permutation_null
permutation_null_fast = e023mach.permutation_null_fast
a_initial_count = e023mach.a_initial_count

import json
import numpy as np
from collections import Counter, defaultdict

CORPUS = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "corpus", "silver", "inscriptions_structured.json"))


def load_la_words():
    """Return list of (signs_list, support, context) for >=2-sign words."""
    d = json.load(open(CORPUS))
    out = []
    for ins in d:
        sup = ins.get("support")
        ctx = ins.get("context")
        for tok in ins.get("stream", []):
            if tok.get("t") == "word":
                sg = tok.get("signs", [])
                if len(sg) >= 2:
                    out.append((sg, sup, ctx))
    return out


def partition_by(words_with_meta, key):
    """key in {'support','context'} -> dict value -> list of sign-lists."""
    idx = 0 if key == "support" else 1
    parts = defaultdict(list)
    for sg, sup, ctx in words_with_meta:
        parts[(sup, ctx)[idx]].append(sg)
    return dict(parts)


def holm_correct(pvals):
    """Return list of Holm-adjusted p-values aligned to input order."""
    m = len(pvals)
    order = sorted(range(len(pvals)), key=lambda i: pvals[i])
    adj = [0.0] * len(pvals)
    running = 0.0
    for rank, i in enumerate(order):
        val = (m - rank) * pvals[i]
        running = max(running, val)
        adj[i] = min(1.0, running)
    return adj


def axis_test(parts, sign, min_words=20, n_draws=1000, seed=0):
    """For each partition with >=min_words words, run permutation_null.
    Returns dict with per-partition results + Holm-corrected p-values."""
    eligible = {k: v for k, v in parts.items() if len(v) >= min_words}
    names = sorted(eligible.keys())
    rows = []
    for j, k in enumerate(names):
        obs, nc, p, mean = permutation_null_fast(eligible[k], sign, n_draws, seed=seed + j)
        rows.append({"name": k, "n": len(eligible[k]), "A_initial": obs,
                     "null_mean": round(mean, 3), "p": p})
    pvals = [r["p"] for r in rows]
    adj = holm_correct(pvals)
    for r, a in zip(rows, adj):
        r["p_holm"] = a
    return rows


def leave_one_out(parts, sign, drop_name, min_words=20, n_draws=1000, seed=0):
    rest = []
    for k, v in parts.items():
        if k == drop_name:
            continue
        rest.extend(v)
    obs, nc, p, mean = permutation_null_fast(rest, sign, n_draws, seed=seed)
    return {"loo_excluded": drop_name, "n": len(rest), "A_initial": obs,
            "null_mean": round(mean, 3), "p": p}


def comparator_sweep(parts, sign, min_words=20, n_draws=1000, seed=0):
    """Count partitions (>=min_words) where sign is significant (p<=0.05)."""
    eligible = {k: v for k, v in parts.items() if len(v) >= min_words}
    cleared = 0
    for j, k in enumerate(sorted(eligible.keys())):
        obs, nc, p, mean = permutation_null_fast(eligible[k], sign, n_draws, seed=seed + 1000 + j)
        if p <= 0.05:
            cleared += 1
    return cleared


def lb_positive_control(n_draws=1000, seed=7):
    """LB PC: most word-initial-skewed sign with >=40 occ; seeded balanced 5-way split;
    require sig in >=3 partitions AND a freq-matched random sign NOT sig in >=3."""
    REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
    if REPO not in sys.path:
        sys.path.insert(0, REPO)
    from scripts.cross_script.data import load_b_damos
    seqs, freq, v2g = load_b_damos()
    ge2 = [w for w in seqs if len(w) >= 2]
    # initial counts
    init = Counter(w[0] for w in ge2)
    # candidates: >=40 occ
    cands = [(s, init[s], freq[s]) for s in freq if freq[s] >= 40]
    # skew = initial / total occ
    def skew(t):
        return t[1] / t[2]
    cands.sort(key=skew, reverse=True)
    pc_sign = cands[0][0]
    # seeded balanced 5-way split
    rng = np.random.default_rng(seed)
    idx = np.arange(len(ge2))
    rng.shuffle(idx)
    folds = [idx[i::5] for i in range(5)]
    sig_pc = 0
    fold_ps = []
    for fi, fold in enumerate(folds):
        words = [ge2[i] for i in fold]
        obs, nc, p, mean = permutation_null_fast(words, pc_sign, n_draws, seed=seed + fi)
        fold_ps.append(p)
        if p <= 0.05:
            sig_pc += 1
    # frequency-matched random sign: pick a sign with occ within 20% of pc_sign occ, not pc_sign
    pc_occ = freq[pc_sign]
    pool = [s for s in freq if s != pc_sign and 0.8 * pc_occ <= freq[s] <= 1.25 * pc_occ]
    if not pool:
        pool = [s for s in freq if s != pc_sign]
    rand_sign = rng.choice(pool)
    sig_rand = 0
    rand_ps = []
    for fi, fold in enumerate(folds):
        words = [ge2[i] for i in fold]
        obs, nc, p, mean = permutation_null_fast(words, rand_sign, n_draws, seed=seed + 50 + fi)
        rand_ps.append(p)
        if p <= 0.05:
            sig_rand += 1
    passed = (sig_pc >= 3) and (sig_rand < 3)
    return {
        "pc_verdict": "PASSED" if passed else "FAILED",
        "pc_sign": pc_sign,
        "pc_sign_occ": int(freq[pc_sign]),
        "pc_sign_initial": int(init[pc_sign]),
        "pc_sign_skew": round(skew((pc_sign, init[pc_sign], freq[pc_sign])), 4),
        "pc_partitions_significant": sig_pc,
        "pc_fold_ps": [round(p, 4) for p in fold_ps],
        "rand_sign": str(rand_sign),
        "rand_sign_occ": int(freq[rand_sign]),
        "rand_partitions_significant": sig_rand,
        "rand_fold_ps": [round(p, 4) for p in rand_ps],
        "split": "seeded balanced 5-way (seed=7); no per-tablet metadata in load_b_damos",
    }


if __name__ == "__main__":
    print("=== EPOCH-024 machinery self-check ===")
    words = load_la_words()
    print("LA >=2-sign words:", len(words))
    # global A
    allw = [w[0] for w in words]
    obs, nc, p, mean = permutation_null_fast(allw, "A", 1000, seed=0)
    print(f"GLOBAL A-initial: {obs}/{len(allw)} frac={obs/len(allw):.4f} null_mean={mean:.2f} p={p:.4f}")
    # axis tests
    sup = partition_by(words, "support")
    ctx = partition_by(words, "context")
    print("\nSUPPORT axis (A):")
    for r in axis_test(sup, "A"):
        print(f"  {r['name']:<22} n={r['n']:4d} A_init={r['A_initial']:3d} mean={r['null_mean']:.2f} p={r['p']:.4f} p_holm={r['p_holm']:.4f}")
    print("\nCONTEXT axis (A):")
    for r in axis_test(ctx, "A"):
        print(f"  {r['name']:<22} n={r['n']:4d} A_init={r['A_initial']:3d} mean={r['null_mean']:.2f} p={r['p']:.4f} p_holm={r['p_holm']:.4f}")
    print("\nLB positive control:")
    pc = lb_positive_control()
    for k, v in pc.items():
        print(f"  {k}: {v}")
    print("\nSelf-check OK.")
