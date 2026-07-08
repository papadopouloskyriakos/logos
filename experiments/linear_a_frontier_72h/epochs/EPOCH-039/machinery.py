#!/usr/bin/env python3
"""
EPOCH-039 machinery — PREFIX PARADIGM vs A-ONLY (morphology; L2/L3).

Pure L2/L3 DISTRIBUTIONAL positional-entropy statistics on ANONYMOUS sign ids.
No phonetics, no sound, no meaning, no reading. "prefix" = word-INITIAL positional
enrichment (a distributional statistic), NOT a grammatical morpheme with meaning.

FROZEN METRICS:
  H = Shannon entropy (bits) of the sign distribution at a position.
  (a) FULL asymmetry = H_first - H_last over ALL len>=2 words (negative =>
      initial-concentrated; from E038).
  (b) A-REMOVED asymmetry = same but EXCLUDING words whose first sign is A.
  (c) PREFIX INVENTORY = signs S (>=15 occ) whose word-INITIAL rate significantly
      exceeds the within-word permutation null (one-sided p<=0.05, Holm-corrected).

FROZEN NULL — WITHIN-WORD PERMUTATION (calibrated): permute sign order WITHIN each
word (preserves each word's multiset + length). >=2000 draws. One-sided p for
initial-concentration / initial-enrichment.

POSITIVE CONTROL (gates verdict) on LB:
  (a) DETECT — plant >=3 distinct signs as productive prefixes in an LB-derived
      corpus; confirm A-removed-style concentration SURVIVES removing ONE planted
      prefix (multi-prefix paradigm detected).
  (b) FALSE-POSITIVE — on within-word-shuffled words, initial-enriched-sign count
      and concentration must be at null (rejection rate <=0.10 across >=20 sets).
  Failure of either -> MACHINERY_UNINFORMATIVE.

Self-check: `python3 machinery.py` runs the full pipeline + PC and prints JSON.
"""
import json, os, sys, math, random
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
CORPUS = os.path.join(REPO, "corpus", "silver", "inscriptions_structured.json")
SCRIPTS = os.path.join(REPO, "scripts")

SEED_GLOBAL    = 20390760
SEED_NULL      = 20390761
SEED_PC_DETECT = 20390762
SEED_PC_FP     = 20390763
SEED_PC_PLANT  = 20390764
SEED_PER_SITE  = 20390765
SEED_LOO       = 20390766
SEED_INVENTORY = 20390767
N_DRAWS        = 2000
PC_DETECT_DRAWS= 2000
PC_FP_DRAWS    = 1000
N_FP_SETS      = 20
MIN_SIGN_OCC   = 15
MIN_SITE_WORDS = 50
FP_LB_SUBSAMPLE= 5000

def load_corpus(path=CORPUS):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def la_words(corpus):
    out = []
    for ins in corpus:
        for tok in ins.get("stream", []):
            if tok.get("t") == "word":
                sg = tok.get("signs", [])
                if isinstance(sg, list) and len(sg) >= 2:
                    out.append(list(sg))
    return out

def la_words_by_site(corpus):
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
    sys.path.insert(0, SCRIPTS)
    from cross_script import data as D
    seqs, freq, v2g = D.load_b_damos()
    return [list(s) for s in seqs if isinstance(s, (list, tuple)) and len(s) >= 2]

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
    firstc = Counter(w[0] for w in words)
    lastc = Counter(w[-1] for w in words)
    n = len(words)
    Hf = shannon_entropy(firstc, n)
    Hl = shannon_entropy(lastc, n)
    return Hf, Hl, len(firstc), len(lastc), firstc, lastc, n

def permute_words(words, rng):
    out = []
    for w in words:
        if len(w) <= 1:
            out.append(list(w))
        else:
            p = list(w)
            rng.shuffle(p)
            out.append(p)
    return out

def asymmetry_null_initial(words, n_draws, seed, observed_asym):
    """Within-word permutation null for asymmetry = H_first - H_last.
    INITIAL-concentration direction: observed is initial-concentrated iff asym<0 AND
    p = frac draws with null_asym <= observed_asym (observed at least as negative)."""
    rng = random.Random(seed)
    le = 0
    asyms = []
    for _ in range(n_draws):
        pw = permute_words(words, rng)
        Hf, Hl, *_ = positional_entropy(pw)
        a = Hf - Hl
        asyms.append(a)
        if a <= observed_asym:
            le += 1
    null_mean = sum(asyms) / len(asyms)
    p = (le + 1) / (n_draws + 1)
    return null_mean, p

def sign_initial_rate(words, sign):
    """Observed word-initial rate of `sign` = (# words with first sign==sign) / (# words
    containing sign at least once)."""
    contain = 0
    initial = 0
    for w in words:
        if sign in w:
            contain += 1
            if w[0] == sign:
                initial += 1
    if contain == 0:
        return 0.0, 0, 0
    return initial / contain, initial, contain

def sign_initial_rate_null(words, sign, n_draws, seed, observed_rate):
    """Within-word permutation null for a sign's initial rate.
    p = frac draws with null_rate >= observed_rate (observed at least as enriched)."""
    rng = random.Random(seed)
    ge = 0
    for _ in range(n_draws):
        pw = permute_words(words, rng)
        r, _, _ = sign_initial_rate(pw, sign)
        if r >= observed_rate:
            ge += 1
    return (ge + 1) / (n_draws + 1)

def holm_correct(pvals):
    """Holm-Bonferroni. Returns list of corrected p-values aligned to input order."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    corrected = [0.0] * m
    running = 0.0
    for rank, idx in enumerate(order):
        val = (m - rank) * pvals[idx]
        if val > running:
            running = val
        corrected[idx] = min(running, 1.0)
    return corrected

def prefix_inventory(words, n_draws, seed):
    """Holm-corrected word-initial-enriched sign inventory.
    Tests every sign with >= MIN_SIGN_OCC occurrences. Returns list of
    [sign, initial_rate, holm_p, raw_p, n_initial, n_contain] for ALL tested signs,
    plus the significant subset (holm_p<=0.05)."""
    occ = Counter()
    for w in words:
        for s in set(w):
            occ[s] += 1
    candidates = [s for s, c in occ.items() if c >= MIN_SIGN_OCC]
    rows = []
    for s in candidates:
        r, ni, nc = sign_initial_rate(words, s)
        p = sign_initial_rate_null(words, s, n_draws, seed + hash(s) % 100000, r)
        rows.append([s, r, None, p, ni, nc])
    raw = [row[3] for row in rows]
    corr = holm_correct(raw)
    for i, row in enumerate(rows):
        row[2] = corr[i]
    sig = [row for row in rows if row[2] <= 0.05]
    return rows, sig

def positive_control(lb_words):
    """PC on LB.
    (a) DETECT: plant >=3 distinct signs as productive prefixes in an LB-derived
        corpus; confirm A-removed-style concentration SURVIVES removing ONE planted
        prefix (multi-prefix paradigm detected). detect_p = p of the A-removed-style
        asymmetry after removing one planted prefix.
    (b) FALSE-POSITIVE: within-word-shuffled words -> rejection rate (frac with
        significant initial-concentration, p<=0.05) <=0.10 across >=20 sets.
    """
    rng = random.Random(SEED_PC_PLANT)
    # Build a planted-prefix corpus from LB: take LB words, prepend one of K planted
    # prefix signs to a fraction of words (productive prefixes). K>=3 distinct.
    K = 4
    planted = ["PFX1", "PFX2", "PFX3", "PFX4"]
    attach_rate = 0.55  # fraction of words that get a prefix
    planted_corpus = []
    for w in lb_words:
        if rng.random() < attach_rate:
            pf = planted[rng.randrange(K)]
            planted_corpus.append([pf] + list(w))
        else:
            planted_corpus.append(list(w))
    # Remove ONE planted prefix (PFX1-initial words) and test that concentration
    # SURVIVES (still initial-concentrated, p<=0.05) -> multi-prefix detected.
    arem = [w for w in planted_corpus if w[0] != "PFX1"]
    Hf, Hl, *_ = positional_entropy(arem)
    obs = Hf - Hl
    _, detect_p = asymmetry_null_initial(arem, PC_DETECT_DRAWS, SEED_PC_DETECT, obs)
    detect = (obs < 0) and (detect_p <= 0.05)

    # FALSE-POSITIVE: within-word-shuffle a FIXED LB subsample; test initial-
    # concentration; rejection rate must be <=0.10.
    rng2 = random.Random(SEED_PC_FP)
    if len(lb_words) > FP_LB_SUBSAMPLE:
        lb_sub = rng2.sample(lb_words, FP_LB_SUBSAMPLE)
    else:
        lb_sub = list(lb_words)
    rejections = 0
    for i in range(N_FP_SETS):
        shuf = permute_words(lb_sub, rng2)
        Hfs, Hls, *_ = positional_entropy(shuf)
        o = Hfs - Hls
        _, ps = asymmetry_null_initial(shuf, PC_FP_DRAWS, SEED_PC_FP + 1 + i, o)
        if o < 0 and ps <= 0.05:
            rejections += 1
    fp_rate = rejections / N_FP_SETS
    fp_ok = fp_rate <= 0.10
    passed = bool(detect and fp_ok)
    return {
        "pc_verdict": "PASSED" if passed else "FAILED",
        "detect_p": detect_p,
        "detect_asymmetry": obs,
        "detect": detect,
        "false_pos_rate": fp_rate,
        "fp_ok": fp_ok,
        "n_fp_sets": N_FP_SETS,
        "n_planted_prefixes": K,
        "attach_rate": attach_rate,
    }

def per_site_a_removed(by_site):
    out = {}
    for site, words in by_site.items():
        if len(words) < MIN_SITE_WORDS:
            continue
        arem = [w for w in words if w[0] != "A"]
        if len(arem) < 20:
            continue
        Hf, Hl, *_ = positional_entropy(arem)
        a = Hf - Hl
        _, p = asymmetry_null_initial(arem, N_DRAWS, SEED_PER_SITE + hash(site) % 100000, a)
        out[site] = {"n": len(words), "n_a_removed": len(arem),
                     "asymmetry": a, "p": p, "H_first": Hf, "H_last": Hl}
    return out

def loo_a_removed(by_site, exclude="Haghia Triada"):
    pool = []
    for site, words in by_site.items():
        if site == exclude:
            continue
        pool.extend(words)
    arem = [w for w in pool if w[0] != "A"]
    Hf, Hl, *_ = positional_entropy(arem)
    a = Hf - Hl
    _, p = asymmetry_null_initial(arem, N_DRAWS, SEED_LOO, a)
    return {"loo_excluded": exclude, "loo_a_removed_p": p,
            "loo_a_removed_asymmetry": a, "loo_n_a_removed": len(arem)}

def run():
    corpus = load_corpus()
    words = la_words(corpus)
    by_site = la_words_by_site(corpus)

    # GLOBAL full
    Hf, Hl, *_ = positional_entropy(words)
    full_asym = Hf - Hl
    _, full_p = asymmetry_null_initial(words, N_DRAWS, SEED_NULL, full_asym)

    # GLOBAL A-removed
    arem = [w for w in words if w[0] != "A"]
    Hfa, Hla, *_ = positional_entropy(arem)
    arem_asym = Hfa - Hla
    _, arem_p = asymmetry_null_initial(arem, N_DRAWS, SEED_NULL + 1, arem_asym)

    # PREFIX INVENTORY (on FULL word set)
    rows, sig = prefix_inventory(words, N_DRAWS, SEED_INVENTORY)
    n_initial_enriched = len(sig)
    n_besides_A = len([r for r in sig if r[0] != "A"])
    signs_list = [[r[0], r[1], r[2]] for r in sig]

    # POSITIVE CONTROL FIRST
    lb_words = load_b_damos()
    pc = positive_control(lb_words)

    # CROSS-SITE
    psite = per_site_a_removed(by_site)
    n_sites_testable = len(psite)
    n_sites_sig = sum(1 for s, d in psite.items() if d["asymmetry"] < 0 and d["p"] <= 0.05)
    loo = loo_a_removed(by_site, "Haghia Triada")

    # VERDICT (frozen mechanical)
    pc_passed = pc["pc_verdict"] == "PASSED"
    full_init = (full_asym < 0 and full_p <= 0.05)
    arem_init = (arem_asym < 0 and arem_p <= 0.05)
    if not pc_passed:
        verdict = "MACHINERY_UNINFORMATIVE"
    elif n_sites_testable < 2:
        verdict = "PARADIGM_UNDERPOWERED"
    elif arem_init and n_besides_A >= 2 and n_sites_sig >= 2:
        verdict = "PREFIX_PARADIGM_BEYOND_A"
    elif full_init and (not arem_init) and n_besides_A < 2:
        verdict = "INITIAL_CONCENTRATION_A_ONLY"
    elif (not full_init) and (not arem_init):
        verdict = "NO_INITIAL_CONCENTRATION_WITHOUT_A"
    else:
        # intermediate / mixed: classify by dominant signal
        if arem_init and n_besides_A >= 2:
            verdict = "PREFIX_PARADIGM_BEYOND_A"
        elif arem_init:
            verdict = "PREFIX_PARADIGM_BEYOND_A" if n_sites_sig >= 2 else "INITIAL_CONCENTRATION_A_ONLY"
        else:
            verdict = "INITIAL_CONCENTRATION_A_ONLY"

    return {
        "verdict": verdict,
        "global": {
            "full_asymmetry": full_asym, "full_null_p": full_p,
            "a_removed_asymmetry": arem_asym, "a_removed_null_p": arem_p,
            "n_words": len(words), "n_a_initial_removed": len(words) - len(arem),
            "full_H_first": Hf, "full_H_last": Hl,
            "a_removed_H_first": Hfa, "a_removed_H_last": Hla,
            "full_initial_concentrated": full_init,
            "a_removed_initial_concentrated": arem_init,
        },
        "prefix_inventory": {
            "n_initial_enriched_signs": n_initial_enriched,
            "n_besides_A": n_besides_A,
            "signs": signs_list,
            "n_tested": len(rows),
        },
        "positive_control": pc,
        "cross_site": {
            "n_sites_testable": n_sites_testable,
            "n_sites_a_removed_sig": n_sites_sig,
            "loo_excluded": loo["loo_excluded"],
            "loo_a_removed_p": loo["loo_a_removed_p"],
            "loo_a_removed_asymmetry": loo["loo_a_removed_asymmetry"],
            "per_site": psite,
        },
    }

if __name__ == "__main__":
    res = run()
    print(json.dumps(res, indent=2, ensure_ascii=False))
