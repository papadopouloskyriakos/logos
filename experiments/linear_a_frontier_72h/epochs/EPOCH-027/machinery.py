"""EPOCH-027 core machinery: INITIAL-vs-FINAL cross-site generalization asymmetry (LA).

Reuses the E024 within-word uniform-permutation null (imported) for the INITIAL slot,
and adds the symmetric FINAL-slot null. Computes per-sign, per-site (and per-fold for
the LB PC) significance counts, then the LA label-swap asymmetry test + Wilcoxon.

Positional/structural ONLY. No phonetic / meaning / reading inference.
"""
import sys, os, csv, json
HERE = os.path.dirname(os.path.abspath(__file__))
E024 = os.path.normpath(os.path.join(HERE, "..", "EPOCH-024"))
if E024 not in sys.path:
    sys.path.insert(0, E024)
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("e024mach", os.path.join(E024, "machinery.py"))
e024mach = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(e024mach)
permutation_null = e024mach.permutation_null
permutation_null_fast = e024mach.permutation_null_fast  # INITIAL slot

import numpy as np
from collections import Counter, defaultdict

CORPUS = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "corpus", "silver", "inscriptions_structured.json"))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))


# ---------- FINAL-slot null (symmetric to INITIAL) ----------
def final_count(words, sign):
    c = 0
    for w in words:
        if w and w[-1] == sign:
            c += 1
    return c

def permutation_null_final_fast(words, sign, n_draws=1000, seed=0):
    """Within-word uniform-permutation null for the LAST position.

    Under a uniform permutation of a word's own signs, the LAST permuted sign is
    uniformly one of the word's signs, so P(last==sign) = count_sign/L -- exactly
    symmetric to the INITIAL null. Equivalent in distribution to explicit permutation.
    Returns (observed, null_counts, p_one_sided, null_mean).
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


# ---------- LA data ----------
def load_la_site_words():
    """Return dict site -> list of >=2-sign sign-lists."""
    d = json.load(open(CORPUS))
    site_words = defaultdict(list)
    for ins in d:
        site = ins.get("site")
        for tok in ins.get("stream", []):
            if tok.get("t") == "word":
                sg = tok.get("signs", [])
                if len(sg) >= 2:
                    site_words[site].append(sg)
    return dict(site_words)


def qualifying_signs(site_words, min_occ=30):
    """Signs with >=min_occ total occ across >=2-sign words."""
    occ = Counter()
    for site, words in site_words.items():
        for w in words:
            occ.update(w)
    return sorted([s for s, c in occ.items() if c >= min_occ]), occ


def qualifying_sites(site_words, min_words=20):
    return sorted([s for s, w in site_words.items() if len(w) >= min_words])


# ---------- per-sign per-site significance counts ----------
def per_sign_site_sig(site_words, signs, sites, n_draws=1000, base_seed=0):
    """For each sign, count sites where it is INITIAL-sig and FINAL-sig (p<=0.05)."""
    out = {}
    detail = []  # for CSV dump
    for si, S in enumerate(signs):
        n_init = 0
        n_final = 0
        for xi, X in enumerate(sites):
            words = site_words[X]
            seed_i = (base_seed + si * 1000 + xi) % (2**31)
            oi, nci, pi, mi = permutation_null_fast(words, S, n_draws, seed=seed_i)
            ofi, ncf, pf, mf = permutation_null_final_fast(words, S, n_draws, seed=seed_i + 500000)
            init_sig = int(pi <= 0.05)
            final_sig = int(pf <= 0.05)
            n_init += init_sig
            n_final += final_sig
            detail.append({"sign": S, "site": X, "n_words": len(words),
                           "init_obs": int(oi), "init_p": round(float(pi), 5), "init_sig": init_sig,
                           "final_obs": int(ofi), "final_p": round(float(pf), 5), "final_sig": final_sig})
        out[S] = {"init_sig_sites": n_init, "final_sig_sites": n_final}
    return out, detail


# ---------- LB positive control ----------
def lb_partitions(n_folds=5, seed=7):
    """Seeded balanced 5-way partition of LB >=2-sign wordforms (SAY SO)."""
    if REPO not in sys.path:
        sys.path.insert(0, REPO)
    from scripts.cross_script.data import load_b_damos
    seqs, freq, v2g = load_b_damos()
    ge2 = [w for w in seqs if len(w) >= 2]
    rng = np.random.default_rng(seed)
    idx = np.arange(len(ge2))
    rng.shuffle(idx)
    folds = [idx[i::n_folds] for i in range(n_folds)]
    fold_words = [[ge2[i] for i in fold] for fold in folds]
    return fold_words, freq


def lb_pc(n_draws=1000, base_seed=0, min_occ=30):
    """Per-sign init-vs-final cross-fold significance counts on LB.
    PC PASSED iff mean(final_sig_parts) >= mean(init_sig_parts)."""
    fold_words, freq = lb_partitions()
    # qualifying LB signs: >=30 occ across >=2-sign words
    occ = Counter()
    for fw in fold_words:
        for w in fw:
            occ.update(w)
    signs = sorted([s for s, c in occ.items() if c >= min_occ])
    per_sign = {}
    detail = []
    for si, S in enumerate(signs):
        ni = nf = 0
        for fi, fw in enumerate(fold_words):
            seed_i = (base_seed + si * 1000 + fi) % (2**31)
            oi, nci, pi, mi = permutation_null_fast(fw, S, n_draws, seed=seed_i)
            ofi, ncf, pf, mf = permutation_null_final_fast(fw, S, n_draws, seed=seed_i + 500000)
            isig = int(pi <= 0.05); fsig = int(pf <= 0.05)
            ni += isig; nf += fsig
            detail.append({"sign": S, "fold": fi, "n_words": len(fw),
                           "init_p": round(float(pi), 5), "init_sig": isig,
                           "final_p": round(float(pf), 5), "final_sig": fsig})
        per_sign[S] = {"init_sig_parts": ni, "final_sig_parts": nf}
    inits = [v["init_sig_parts"] for v in per_sign.values()]
    finals = [v["final_sig_parts"] for v in per_sign.values()]
    mi = float(np.mean(inits)) if inits else 0.0
    mf = float(np.mean(finals)) if finals else 0.0
    direction = "final>=init" if mf >= mi else "init>final"
    passed = (mf >= mi)
    return {
        "pc_verdict": "PASSED" if passed else "FAILED",
        "lb_mean_init": round(mi, 4),
        "lb_mean_final": round(mf, 4),
        "lb_direction": direction,
        "lb_diff_final_minus_init": round(mf - mi, 4),
        "n_lb_signs": len(signs),
        "split": "seeded balanced 5-way (seed=7); contiguous fold assignment after seeded shuffle",
        "per_sign": per_sign,
        "detail": detail,
    }


# ---------- LA asymmetry test ----------
def la_asymmetry(per_sign, n_draws=2000, seed=2027):
    """Label-swap permutation null on D = mean(init)-mean(final); two-sided p.
    Plus Wilcoxon signed-rank cross-check and sign-direction counts."""
    pairs = [(v["init_sig_sites"], v["final_sig_sites"]) for v in per_sign.values()]
    inits = np.array([p[0] for p in pairs], dtype=float)
    finals = np.array([p[1] for p in pairs], dtype=float)
    D_obs = float(inits.mean() - finals.mean())
    rng = np.random.default_rng(seed)
    N = len(pairs)
    geq = 0
    D_perms = np.empty(n_draws)
    for d in range(n_draws):
        swap = rng.random(N) < 0.5
        a = np.where(swap, finals, inits)
        b = np.where(swap, inits, finals)
        Dp = float(a.mean() - b.mean())
        D_perms[d] = Dp
        if abs(Dp) >= abs(D_obs):
            geq += 1
    p_labelswap = (1 + geq) / (1 + n_draws)
    # Wilcoxon signed-rank (scipy if available, else normal-approx fallback)
    try:
        from scipy.stats import wilcoxon
        diffs = inits - finals
        if np.all(diffs == 0):
            p_wil = 1.0
        else:
            w = wilcoxon(inits, finals, zero_method="wilcox", correction=False, alternative="two-sided")
            p_wil = float(w.pvalue)
    except Exception:
        # normal approximation fallback
        diffs = inits - finals
        nz = diffs[diffs != 0]
        if len(nz) == 0:
            p_wil = 1.0
        else:
            ab = np.abs(nz)
            ranks = ab.argsort().argsort().astype(float) + 1.0
            # average ranks for ties (simple)
            W = float(np.sum(np.where(nz > 0, ranks, 0)))
            mu = N * (N + 1) / 4.0
            sigma = np.sqrt(N * (N + 1) * (2 * N + 1) / 24.0)
            z = (W - mu) / sigma if sigma > 0 else 0.0
            from math import erf, sqrt
            p_wil = 2 * (1 - 0.5 * (1 + erf(abs(z) / sqrt(2))))
    n_init_gt = int(np.sum(inits > finals))
    n_final_gt = int(np.sum(finals > inits))
    n_tie = int(np.sum(inits == finals))
    return {
        "mean_init": round(float(inits.mean()), 4),
        "mean_final": round(float(finals.mean()), 4),
        "diff": round(D_obs, 4),
        "labelswap_p": round(float(p_labelswap), 5),
        "wilcoxon_p": round(float(p_wil), 5),
        "n_init_gt_final": n_init_gt,
        "n_final_gt_init": n_final_gt,
        "n_tie": n_tie,
    }


# ---------- frozen mechanical verdict ----------
def verdict(pc, asym, n_signs, n_sites):
    pc_passed = (pc["pc_verdict"] == "PASSED")
    if n_signs < 6 or n_sites < 5:
        return "ASYMMETRY_UNDERPOWERED"
    if not pc_passed:
        return "MACHINERY_UNINFORMATIVE"
    D = asym["diff"]
    p = asym["labelswap_p"]
    if p > 0.05:
        return "NO_POSITIONAL_ASYMMETRY"
    if D > 0 and asym["n_init_gt_final"] > asym["n_final_gt_init"]:
        return "INITIAL_GENERALIZES_MORE_LA"
    if D < 0 and asym["n_final_gt_init"] > asym["n_init_gt_final"]:
        return "FINAL_GENERALIZES_MORE_LA"
    # significant but direction/counts inconsistent -> no clean asymmetry
    return "NO_POSITIONAL_ASYMMETRY"


if __name__ == "__main__":
    print("=== EPOCH-027 machinery self-check ===")
    # 1. FINAL null sanity: on a tiny synthetic corpus, observed final count must equal
    #    the count of words whose last sign == S; null mean ~ sum(count_S/L).
    toy = [["A", "B"], ["A", "A", "B"], ["B", "A"]]
    of, ncf, pf, mf = permutation_null_final_fast(toy, "A", 2000, seed=0)
    # P(last==A): [A,B]->1/2, [A,A,B]->2/3, [B,A]->1/2 ; sum=1.667
    exp_mean = 1/2 + 2/3 + 1/2
    print(f"FINAL null toy: obs={of} (expect 1) mean={mf:.3f} (expect {exp_mean:.3f}) p={pf:.4f}")
    assert of == 1, "final observed wrong"
    assert abs(mf - exp_mean) < 0.05, "final null mean wrong"
    # 2. INITIAL vs FINAL symmetry on a palindrome-ish corpus: should be ~equal
    pal = [["A", "B", "A"]] * 50 + [["B", "A", "B"]] * 50
    oi, _, pi, mi = permutation_null_fast(pal, "A", 1000, seed=1)
    of2, _, pf2, mf2 = permutation_null_final_fast(pal, "A", 1000, seed=1)
    print(f"palindrome A: init_obs={oi} final_obs={of2} init_mean={mi:.3f} final_mean={mf2:.3f}")
    assert oi == of2 and abs(mi - mf2) < 0.05, "init/final not symmetric on palindrome"
    # 3. LA load
    sw = load_la_site_words()
    signs, occ = qualifying_signs(sw)
    sites = qualifying_sites(sw)
    print(f"LA: {len(signs)} qualifying signs, {len(sites)} qualifying sites")
    print("Self-check OK.")
