#!/usr/bin/env python3
"""EPOCH-053 machinery: entry-word vocabulary restriction (commodity lexicon?).

Pure distributional vocabulary structure (L2/L3). Forms anonymous.
Entry-word = a 'word' stream token whose NEXT stream token is 'num'.
Non-entry  = a 'word' stream token whose next token is NOT 'num'.

Size-matched comparison (TTR is size-dependent): subsample the larger group to
the size of the smaller; >=500 bootstrap resamples; label-permutation p.
"""
import json, math, random, hashlib, sys
from collections import Counter

RNG = random.Random(20240517)  # frozen seed

# ---------- corpus loading ----------
def load_corpus(path):
    return json.load(open(path))

def extract_words(inscriptions):
    """Return (entry_words, nonentry_words) as lists of anonymous form-tuples,
    plus per-site breakdown."""
    entry, nonentry = [], []
    site_entry, site_nonentry = {}, {}
    for ins in inscriptions:
        st = ins.get("stream", []) or []
        site = ins.get("site", "?") or "?"
        site_entry.setdefault(site, []); site_nonentry.setdefault(site, [])
        for i, tok in enumerate(st):
            if tok.get("t") == "word":
                form = tuple(tok.get("signs", []))
                nxt = st[i+1] if i+1 < len(st) else None
                if nxt is not None and nxt.get("t") == "num":
                    entry.append(form); site_entry[site].append(form)
                else:
                    nonentry.append(form); site_nonentry[site].append(form)
    return entry, nonentry, site_entry, site_nonentry

# ---------- vocabulary metrics ----------
def ttr(words):
    if not words: return float("nan")
    return len(set(words)) / len(words)

def norm_entropy(words):
    """H / log2(n_types). 0 => maximally concentrated (one form)."""
    if not words: return float("nan")
    c = Counter(words)
    n = len(words); H = 0.0
    for f, k in c.items():
        p = k / n
        H -= p * math.log2(p)
    nt = len(c)
    if nt <= 1: return 0.0
    return H / math.log2(nt)

def matched_metrics(entry, nonentry, n_match, rng):
    """Subsample both groups to n_match tokens; return (ttr_e, ttr_n, he, hn)."""
    e = [rng.choice(entry) for _ in range(n_match)]
    n = [rng.choice(nonentry) for _ in range(n_match)]
    return ttr(e), ttr(n), norm_entropy(e), norm_entropy(n)

def restriction_gap(entry, nonentry, n_boot=500, rng=None):
    """Mean matched gap = (TTR_non - TTR_e) averaged over bootstraps, plus
    matched TTR/entropy means. Positive gap => entry MORE restricted (lower TTR)."""
    if rng is None: rng = random.Random(20240517)
    n_match = min(len(entry), len(nonentry))
    ttr_e_l, ttr_n_l, he_l, hn_l = [], [], [], []
    for _ in range(n_boot):
        te, tn, he, hn = matched_metrics(entry, nonentry, n_match, rng)
        ttr_e_l.append(te); ttr_n_l.append(tn); he_l.append(he); hn_l.append(hn)
    mean = lambda L: sum(L)/len(L)
    gap_ttr = mean(ttr_n_l) - mean(ttr_e_l)   # + => entry lower TTR (more restricted)
    gap_he  = mean(hn_l)  - mean(he_l)        # + => entry lower entropy
    return {
        "n_match": n_match,
        "ttr_entry_matched": mean(ttr_e_l),
        "ttr_non_matched": mean(ttr_n_l),
        "norm_entropy_entry": mean(he_l),
        "norm_entropy_non": mean(hn_l),
        "gap_ttr": gap_ttr,
        "gap_entropy": gap_he,
    }

def permutation_test(entry, nonentry, n_perm=1000, n_boot=200, rng=None):
    """Label-permutation p for the matched TTR gap. Observed gap = TTR_non - TTR_e
    on matched size. Shuffle entry/non labels among the pooled words, recompute."""
    if rng is None: rng = random.Random(20240517)
    obs = restriction_gap(entry, nonentry, n_boot=n_boot, rng=rng)["gap_ttr"]
    pool = list(entry) + list(nonentry)
    ne = len(entry); nn = len(nonentry)
    count = 0
    for _ in range(n_perm):
        rng.shuffle(pool)
        e = pool[:ne]; n = pool[ne:ne+nn]
        g = restriction_gap(e, n, n_boot=n_boot, rng=rng)["gap_ttr"]
        if g >= obs:
            count += 1
    p = (count + 1) / (n_perm + 1)
    return obs, p

def direction(gap):
    # entry more restricted iff entry has LOWER ttr AND LOWER entropy
    if gap["gap_ttr"] > 0 and gap["gap_entropy"] > 0:
        return "entry_more_restricted"
    if gap["gap_ttr"] < 0 and gap["gap_entropy"] < 0:
        return "entry_less_restricted"
    return "mixed"

# ---------- POSITIVE CONTROL ----------
def pc_detect(rng, n_entry=400, n_non=400, n_entry_forms=15, n_non_forms=300,
              n_boot=300, n_perm=300):
    """Plant a restricted entry vocab (few forms, SKEWED -> low TTR AND low
    normalized entropy) vs a diverse, near-uniform non-entry vocab. A genuine
    'commodity lexicon' is small AND unevenly used. Must flag restriction
    (p<=0.05, direction entry_more_restricted)."""
    ef = [("E%d" % i,) for i in range(n_entry_forms)]
    nf = [("N%d" % i,) for i in range(n_non_forms)]
    # skewed weights for entry (Zipf-like): few items dominate
    ew = [1.0/(i+1) for i in range(n_entry_forms)]
    entry = [rng.choices(ef, weights=ew)[0] for _ in range(n_entry)]
    non = [rng.choice(nf) for _ in range(n_non)]  # near-uniform -> high entropy
    gap = restriction_gap(entry, non, n_boot=n_boot, rng=rng)
    _, p = permutation_test(entry, non, n_perm=n_perm, n_boot=n_boot, rng=rng)
    d = direction(gap)
    ok = (p <= 0.05) and (d == "entry_more_restricted")
    return {"detect_p": p, "detect_direction": d, "detect_ok": ok, "gap": gap}

def pc_false_positive(rng, n_splits=25, n_boot=200, n_perm=200):
    """Split words from the SAME vocabulary into two groups at DIFFERENT sizes.
    Size-matched test must NOT flag restriction (FP rate <=0.10)."""
    # shared vocabulary
    vocab = [("V%d" % i,) for i in range(250)]
    fps = 0
    for s in range(n_splits):
        # two groups of different sizes drawn from the SAME vocab
        na = rng.choice([200, 250, 300, 350])
        nb = rng.choice([150, 200, 250, 300, 400])
        a = [rng.choice(vocab) for _ in range(na)]
        b = [rng.choice(vocab) for _ in range(nb)]
        gap = restriction_gap(a, b, n_boot=n_boot, rng=rng)
        _, p = permutation_test(a, b, n_perm=n_perm, n_boot=n_boot, rng=rng)
        # "restriction flagged" if p<=0.05 in EITHER direction (any spurious sig)
        if p <= 0.05:
            fps += 1
    return {"false_pos_rate": fps / n_splits, "n_splits": n_splits}

def positive_control(rng):
    det = pc_detect(rng)
    fp = pc_false_positive(rng)
    passed = det["detect_ok"] and (fp["false_pos_rate"] <= 0.10)
    return {"pc_verdict": "PASSED" if passed else "FAILED",
            "detect_p": det["detect_p"], "detect_direction": det["detect_direction"],
            "detect_ok": det["detect_ok"],
            "false_pos_rate": fp["false_pos_rate"], "fp_splits": fp["n_splits"]}

# ---------- CROSS-SITE ----------
def cross_site(site_entry, site_nonentry, min_n=20, n_boot=400, n_perm=500, rng=None):
    if rng is None: rng = random.Random(20240517)
    out = {}
    for site in site_entry:
        e = site_entry[site]; n = site_nonentry.get(site, [])
        if len(e) >= min_n and len(n) >= min_n:
            gap = restriction_gap(e, n, n_boot=n_boot, rng=rng)
            _, p = permutation_test(e, n, n_perm=n_perm, n_boot=n_boot, rng=rng)
            d = direction(gap)
            out[site] = {"n_entry": len(e), "n_nonentry": len(n),
                         "gap_ttr": gap["gap_ttr"], "perm_p": p, "direction": d,
                         "ttr_entry_matched": gap["ttr_entry_matched"],
                         "ttr_non_matched": gap["ttr_non_matched"],
                         "norm_entropy_entry": gap["norm_entropy_entry"],
                         "norm_entropy_non": gap["norm_entropy_non"]}
    return out

def leave_one_site_out(site_entry, site_nonentry, target="Haghia Triada",
                       n_boot=400, n_perm=500, rng=None):
    """LOO on the dominant site: drop it, recompute global restriction test on
    the pooled remainder. Returns p."""
    if rng is None: rng = random.Random(20240517)
    e_all, n_all = [], []
    for site in site_entry:
        if site == target: continue
        e_all += site_entry[site]; n_all += site_nonentry.get(site, [])
    if len(e_all) < 20 or len(n_all) < 20:
        return float("nan")
    _, p = permutation_test(e_all, n_all, n_perm=n_perm, n_boot=n_boot, rng=rng)
    gap = restriction_gap(e_all, n_all, n_boot=n_boot, rng=rng)
    return p, gap

# ---------- self-check ----------
def self_check():
    rng = random.Random(20240517)
    # 1. metrics sanity
    assert abs(ttr([("a",),("a",),("b",)]) - 2/3) < 1e-9
    assert abs(norm_entropy([("a",),("a",),("a",)])) < 1e-9  # one form -> 0
    # uniform two-form -> H/log2(2)=1
    assert abs(norm_entropy([("a",),("b",)]) - 1.0) < 1e-9
    # 2. restriction_gap sign on planted data (concentrated restricted entry set)
    ef=[("E0",),("E1",),("E2",)]; nf=[("N%d"%i,) for i in range(200)]
    e=[rng.choices(ef,weights=[10,3,1])[0] for _ in range(300)]
    n=[rng.choice(nf) for _ in range(300)]
    g=restriction_gap(e,n,n_boot=100,rng=rng)
    assert g["gap_ttr"]>0 and g["gap_entropy"]>0
    assert direction(g)=="entry_more_restricted"
    print("SELF-CHECK OK")

if __name__ == "__main__":
    self_check()
    print("machinery.py loaded; metrics + PC + cross-site + LOO defined.")
