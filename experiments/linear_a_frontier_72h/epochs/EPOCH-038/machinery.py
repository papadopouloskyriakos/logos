#!/usr/bin/env python3
"""
EPOCH-038 machinery — POSITIONAL SIGN-ENTROPY ASYMMETRY (final-position suffix concentration;
morphology probe; L2/L3).

Pure L2/L3 DISTRIBUTIONAL positional-entropy statistics on ANONYMOUS sign ids. No phonetics,
no sound, no meaning, no reading. "Suffix concentration" = LOW word-FINAL sign-position
entropy relative to word-INITIAL; it is a distributional statistic, NOT a grammatical claim
with meaning.

FROZEN METRIC: Shannon entropy H (bits) of the sign distribution at a position.
  H_first = entropy of first-sign distribution over words (len>=2).
  H_last  = entropy of last-sign distribution.
  ASYMMETRY = H_first - H_last  (>0 => final more concentrated => suffix-like;
                                  <0 => initial more concentrated => prefix-like).

FROZEN NULL — WITHIN-WORD PERMUTATION (calibrated by construction): for each null draw,
permute the sign order WITHIN each word (preserves each word's multiset and length), recompute
H_first, H_last, asymmetry; >=2000 draws. One-sided p = frac draws with null asymmetry >=
observed (final MORE concentrated than random). Under H0 (no positional specialization)
asymmetry ~ 0.

POSITIVE CONTROL (gates verdict) on LB (DĀMOS; LB inflects word-finally, so final-position
entropy is expected LOWER than initial — validates the entropy machinery):
  - DETECT: LB asymmetry > 0 with p <= 0.05.
  - FALSE-POSITIVE: on a 5000-word LB subsample with signs shuffled within-word (no real
    positional structure; DETECT uses FULL LB), rejection rate (frac p <= 0.05) MUST be
    <= 0.10 across >= 20 control sets.
  Failure of either -> MACHINERY_UNINFORMATIVE.

Self-check: `python3 machinery.py` runs the full pipeline + PC and prints a JSON summary.
"""
import json, os, sys, math, random
from collections import Counter, defaultdict

# ---------- paths ----------
HERE = os.path.dirname(os.path.abspath(__file__))
# HERE = .../experiments/linear_a_frontier_72h/epochs/EPOCH-038
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
CORPUS = os.path.join(REPO, "corpus", "silver", "inscriptions_structured.json")
SCRIPTS = os.path.join(REPO, "scripts")

# ---------- seeds / knobs (FROZEN) ----------
SEED_GLOBAL    = 20380760
SEED_NULL      = 20380761
SEED_PC_DETECT = 20380762
SEED_PC_FP     = 20380763
SEED_PER_SITE  = 20380764
SEED_LOO       = 20380765
N_DRAWS        = 2000      # >=2000 within-word permutation null
PC_DETECT_DRAWS= 2000
PC_FP_DRAWS    = 1000      # per FP control set (protocol minimum)
N_FP_SETS      = 20        # >=20
FP_LB_SUBSAMPLE= 5000      # LB subsample size for FP control (DETECT uses FULL LB)
MIN_SITE_WORDS = 50        # qualifying-site threshold

# ---------- corpus IO ----------
def load_corpus(path=CORPUS):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def la_words(corpus):
    """Flat list of sign-lists for LA words with len(signs)>=2."""
    out = []
    for ins in corpus:
        for tok in ins.get("stream", []):
            if tok.get("t") == "word":
                sg = tok.get("signs", [])
                if isinstance(sg, list) and len(sg) >= 2:
                    out.append(list(sg))
    return out

def la_words_by_site(corpus):
    """site -> list of sign-lists (words len>=2)."""
    by = defaultdict(list)
    for ins in corpus:
        site = ins.get("site", "") or "(unknown)"
        for tok in ins.get("stream", []):
            if tok.get("t") == "word":
                sg = tok.get("signs", [])
                if isinstance(sg, list) and len(sg) >= 2:
                    by[site].append(list(sg))
    return by

def load_b_damos():
    """Linear B positive-control benchmark. Returns flat list of wordforms (sign-lists)."""
    sys.path.insert(0, SCRIPTS)
    from cross_script import data as D
    seqs, freq, v2g = D.load_b_damos()
    return [list(s) for s in seqs if isinstance(s, (list, tuple)) and len(s) >= 2]

# ---------- entropy ----------
def shannon_entropy(counter, n):
    if n <= 0:
        return 0.0
    h = 0.0
    for c in counter.values():
        if c <= 0:
            continue
        p = c / n
        h -= p * math.log2(p)
    return h

def positional_entropy(words):
    """Return (H_first, H_last, n_distinct_first, n_distinct_last, first_counter, last_counter, n)."""
    firstc = Counter(w[0] for w in words)
    lastc = Counter(w[-1] for w in words)
    n = len(words)
    Hf = shannon_entropy(firstc, n)
    Hl = shannon_entropy(lastc, n)
    return Hf, Hl, len(firstc), len(lastc), firstc, lastc, n

# ---------- within-word permutation null ----------
def permute_words(words, rng):
    """Permute sign order WITHIN each word (preserves multiset + length)."""
    out = []
    for w in words:
        if len(w) <= 1:
            out.append(list(w))
        else:
            p = list(w)
            rng.shuffle(p)
            out.append(p)
    return out

def asymmetry_null(words, n_draws, seed, observed_asym):
    """Within-word permutation null for asymmetry = H_first - H_last.
    Returns (null_mean, p_one_sided) where p = frac draws with null_asym >= observed_asym
    (i.e. observed is at least as 'final-concentrated' as null)."""
    rng = random.Random(seed)
    Hf0, Hl0, *_ = positional_entropy(words)
    ge = 0
    asyms = []
    for _ in range(n_draws):
        pw = permute_words(words, rng)
        Hf, Hl, *_ = positional_entropy(pw)
        a = Hf - Hl
        asyms.append(a)
        if a >= observed_asym:
            ge += 1
    null_mean = sum(asyms) / len(asyms)
    p = (ge + 1) / (n_draws + 1)   # +1 smoothing (never exactly 0)
    return null_mean, p

# ---------- positive control ----------
def positive_control(lb_words):
    """Run DETECT + FALSE-POSITIVE on LB.
    DETECT: LB asymmetry > 0 with p <= 0.05.
    FALSE-POSITIVE: shuffle-within-word words (no positional structure) -> rejection rate
                    (frac p<=0.05) <= 0.10 across >=20 sets.
    Returns dict."""
    # DETECT
    Hf, Hl, *_ = positional_entropy(lb_words)
    lb_asym = Hf - Hl
    null_mean, p = asymmetry_null(lb_words, PC_DETECT_DRAWS, SEED_PC_DETECT, lb_asym)
    detect = (lb_asym > 0) and (p <= 0.05)

    # FALSE-POSITIVE: each set = a fresh within-word shuffle of a FIXED LB subsample
    # (destroys positional structure but preserves per-word multisets/lengths); run the
    # SAME test on it. DETECT above uses FULL LB; the subsample keeps the FP control
    # tractable while remaining far above the n needed for a stable null.
    rng = random.Random(SEED_PC_FP)
    if len(lb_words) > FP_LB_SUBSAMPLE:
        lb_sub = rng.sample(lb_words, FP_LB_SUBSAMPLE)
    else:
        lb_sub = list(lb_words)
    rejections = 0
    for i in range(N_FP_SETS):
        shuf = permute_words(lb_sub, rng)
        Hfs, Hls, *_ = positional_entropy(shuf)
        obs = Hfs - Hls
        _, ps = asymmetry_null(shuf, PC_FP_DRAWS, SEED_PC_FP + 1 + i, obs)
        if obs > 0 and ps <= 0.05:
            rejections += 1
    fp_rate = rejections / N_FP_SETS
    fp_ok = fp_rate <= 0.10
    passed = bool(detect and fp_ok)
    return {
        "pc_verdict": "PASSED" if passed else "FAILED",
        "lb_H_first": Hf, "lb_H_last": Hl, "lb_asymmetry": lb_asym,
        "lb_detect_p": p, "lb_detect": detect,
        "false_pos_rate": fp_rate, "fp_ok": fp_ok,
        "n_fp_sets": N_FP_SETS,
        "fp_lb_subsample": FP_LB_SUBSAMPLE,
    }

# ---------- per-site + LOO ----------
def per_site_tests(by_site):
    """For each site with >= MIN_SITE_WORDS: asymmetry + permutation p (same direction:
    asymmetry > 0). Returns dict site -> {n, asymmetry, p, H_first, H_last}."""
    out = {}
    for site, words in by_site.items():
        if len(words) < MIN_SITE_WORDS:
            continue
        Hf, Hl, *_ = positional_entropy(words)
        a = Hf - Hl
        _, p = asymmetry_null(words, N_DRAWS, SEED_PER_SITE + hash(site) % 100000, a)
        out[site] = {"n": len(words), "asymmetry": a, "p": p,
                     "H_first": Hf, "H_last": Hl}
    return out

def loo_test(by_site, exclude_site):
    """Leave-one-site-out: pool all sites EXCEPT exclude_site, run the global test."""
    pooled = []
    for site, words in by_site.items():
        if site == exclude_site:
            continue
        pooled.extend(words)
    Hf, Hl, *_ = positional_entropy(pooled)
    a = Hf - Hl
    _, p = asymmetry_null(pooled, N_DRAWS, SEED_LOO, a)
    return {"n": len(pooled), "asymmetry": a, "p": p, "H_first": Hf, "H_last": Hl}

# ---------- verdict (FROZEN mechanical) ----------
def verdict(pc_passed, glob, per_site, loo, n_testable_sites):
    g_asym = glob["asymmetry"]
    g_p = glob["null_p"]
    g_sig = (g_asym > 0) and (g_p <= 0.05)
    n_sig = sum(1 for v in per_site.values() if v["asymmetry"] > 0 and v["p"] <= 0.05)
    direction_consistent = all(v["asymmetry"] > 0 for v in per_site.values()) if per_site else False
    loo_survives = (loo["asymmetry"] > 0) and (loo["p"] <= 0.05)

    if not pc_passed:
        return "MACHINERY_UNINFORMATIVE", dict(g_sig=g_sig, n_sig=n_sig,
               direction_consistent=direction_consistent, loo_survives=loo_survives)
    if n_testable_sites < 3:
        return "ENTROPY_UNDERPOWERED", dict(g_sig=g_sig, n_sig=n_sig,
               direction_consistent=direction_consistent, loo_survives=loo_survives)
    if g_sig and n_sig >= 3 and direction_consistent and loo_survives:
        return "FINAL_SUFFIX_CONCENTRATION_CROSS_SITE", dict(g_sig=g_sig, n_sig=n_sig,
               direction_consistent=direction_consistent, loo_survives=loo_survives)
    if g_sig:  # global significant but not cross-site robust
        return "SUFFIX_CONCENTRATION_SITE_LOCAL", dict(g_sig=g_sig, n_sig=n_sig,
               direction_consistent=direction_consistent, loo_survives=loo_survives)
    # global not significant OR reversed
    return "NO_POSITIONAL_ENTROPY_ASYMMETRY", dict(g_sig=g_sig, n_sig=n_sig,
           direction_consistent=direction_consistent, loo_survives=loo_survives)

# ---------- main pipeline ----------
def run():
    corpus = load_corpus()
    words = la_words(corpus)
    by_site = la_words_by_site(corpus)

    # GLOBAL
    Hf, Hl, ndf, ndl, firstc, lastc, n = positional_entropy(words)
    g_asym = Hf - Hl
    null_mean, g_p = asymmetry_null(words, N_DRAWS, SEED_NULL, g_asym)
    top5_final = lastc.most_common(5)
    top5_final_share = sum(c for _, c in top5_final) / n

    glob = {"n_words": n, "H_first": Hf, "H_last": Hl, "asymmetry": g_asym,
            "null_mean_asym": null_mean, "null_p": g_p,
            "n_distinct_first": ndf, "n_distinct_last": ndl,
            "top5_final": top5_final, "top5_final_share": top5_final_share,
            "norm_H_first": Hf / math.log2(ndf) if ndf > 1 else 0.0,
            "norm_H_last": Hl / math.log2(ndl) if ndl > 1 else 0.0}

    # POSITIVE CONTROL FIRST
    lb_words = load_b_damos()
    pc = positive_control(lb_words)
    pc_passed = (pc["pc_verdict"] == "PASSED")

    # PER-SITE
    per_site = per_site_tests(by_site)
    n_testable = len(per_site)
    n_sig = sum(1 for v in per_site.values() if v["asymmetry"] > 0 and v["p"] <= 0.05)
    direction_consistent = (all(v["asymmetry"] > 0 for v in per_site.values())
                            if per_site else False)

    # LOO on largest site (Haghia Triada)
    largest = max(by_site.items(), key=lambda kv: len(kv[1]))[0]
    loo = loo_test(by_site, largest)

    # REVERSE-direction characterization: is INITIAL more concentrated?
    # i.e. asymmetry < 0 significant in the OTHER tail.
    rev_p = None
    if g_asym < 0:
        rng = random.Random(SEED_NULL + 7)
        ge = 0
        for _ in range(N_DRAWS):
            pw = permute_words(words, rng)
            Hfp, Hlp, *_ = positional_entropy(pw)
            if (Hfp - Hlp) <= g_asym:
                ge += 1
        rev_p = (ge + 1) / (N_DRAWS + 1)

    v, vmeta = verdict(pc_passed, glob, per_site, loo, n_testable)

    return {
        "global": glob,
        "positive_control": pc,
        "cross_site": {
            "n_sites_testable": n_testable,
            "n_sites_sig": n_sig,
            "direction_consistent": direction_consistent,
            "loo_excluded": largest,
            "loo": loo,
            "per_site": per_site,
        },
        "reverse_initial_concentration": {
            "asymmetry": g_asym, "p_initial_more_concentrated": rev_p,
        },
        "verdict": v,
        "verdict_meta": vmeta,
    }

if __name__ == "__main__":
    res = run()
    print(json.dumps(res, ensure_ascii=False, indent=2))
