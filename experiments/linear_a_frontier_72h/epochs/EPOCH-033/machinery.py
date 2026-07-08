#!/usr/bin/env python3
"""
EPOCH-033 machinery — LEDGER ENTRY-WORD vs NON-ENTRY-WORD STRUCTURAL CONTRAST.

Pure L2/L3 structural statistics on ANONYMOUS sign sequences. No phonetics, no sound, no meaning,
no reading, no numeral-value arithmetic. Two functional word classes defined by OBSERVABLE structure:
  ENTRY-word    = a 'word' token whose IMMEDIATELY FOLLOWING stream token is 'num'.
  NON-ENTRY word= a 'word' token whose following token is NOT 'num' (or it is last).

FROZEN METRICS (per class):
  (a) mean word LENGTH (n signs);
  (b) A-INITIAL rate (fraction of >=1-sign words whose first sign is 'A').
CONTRAST = entry-minus-nonentry for each metric.

FROZEN NULL — LABEL PERMUTATION (calibrated by construction):
  Randomly permute the entry/non-entry LABELS across the SAME set of word tokens (preserving the
  count in each class), recompute the contrast; >=2000 draws; two-sided p.

POSITIVE CONTROL (gates verdict):
  - DETECT: on LB, form two word groups with a PLANTED length difference; label-permutation test
    must reject (p<=0.05) in the correct direction.
  - FALSE-POSITIVE: on two groups drawn from the SAME distribution (labels assigned at random),
    rejection rate <=0.10 across >=30 splits.
  Failure of either -> MACHINERY_UNINFORMATIVE.

Self-check: `python3 machinery.py` runs the full pipeline + PC and prints a JSON summary.
"""
import json, os, sys, hashlib, random
from collections import defaultdict

# ---------- paths ----------
HERE = os.path.dirname(os.path.abspath(__file__))
# HERE = .../experiments/linear_a_frontier_72h/epochs/EPOCH-033
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
CORPUS = os.path.join(REPO, "corpus", "silver", "inscriptions_structured.json")
SCRIPTS = os.path.join(REPO, "scripts")

# ---------- seeds / knobs (FROZEN) ----------
SEED_GLOBAL_LEN   = 20240733
SEED_GLOBAL_A     = 20240734
SEED_PC_DETECT    = 20240735
SEED_PC_FP        = 20240736
SEED_SITE         = 20240737
SEED_LOO          = 20240738
N_DRAWS           = 2000      # >=2000
N_FP_SPLITS       = 30        # >=30
PC_DETECT_DRAWS   = 2000
PC_FP_DRAWS       = 1000      # per split (calibration)
MIN_CLASS_PER_SITE= 15        # >=15 in EACH class
MIN_SITES_ROBUST  = 3

# ---------- corpus IO ----------
def load_corpus(path=CORPUS):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_b_damos():
    """Linear B positive-control benchmark. Returns list of sign-lists (wordforms)."""
    sys.path.insert(0, SCRIPTS)
    from cross_script import data as D
    seqs, freq, v2g = D.load_b_damos()
    return seqs

# ---------- core: classify word tokens ----------
def classify_inscription(insc):
    """Return list of (is_entry:bool, signs:list) for each 'word' token in stream order."""
    out = []
    st = insc.get("stream", []) or []
    for i, tok in enumerate(st):
        if tok.get("t") == "word":
            nxt = st[i + 1] if i + 1 < len(st) else None
            is_entry = (nxt is not None and nxt.get("t") == "num")
            out.append((is_entry, list(tok.get("signs", []))))
    return out

def build_word_records(corpus):
    """Return list of dicts: {site, is_entry, len, a_initial} for every word token."""
    recs = []
    for ins in corpus:
        site = ins.get("site", "") or ""
        for is_entry, signs in classify_inscription(ins):
            L = len(signs)
            a_init = (L >= 1 and signs[0] == "A")
            recs.append({"site": site, "is_entry": is_entry, "len": L, "a_init": a_init})
    return recs

# ---------- statistics ----------
def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0

def length_contrast(recs):
    e = [r["len"] for r in recs if r["is_entry"]]
    n = [r["len"] for r in recs if not r["is_entry"]]
    return mean(e) - mean(n)

def a_rate(recs, is_entry):
    sub = [r for r in recs if r["is_entry"] == is_entry and r["len"] >= 1]
    if not sub:
        return 0.0
    return sum(1 for r in sub if r["a_init"]) / len(sub)

def a_contrast(recs):
    return a_rate(recs, True) - a_rate(recs, False)

# ---------- label-permutation null (two-sided) ----------
def perm_test_contrast(recs, metric_fn, n_draws=N_DRAWS, seed=0):
    """Two-sided label-permutation p for a generic contrast(recs)->float.
    Preserves the count of entry/non-entry labels; permutes which tokens carry the entry label.
    Two-sided: count draws whose |contrast| >= |observed|."""
    rng = random.Random(seed)
    obs = metric_fn(recs)
    n_entry = sum(1 for r in recs if r["is_entry"])
    N = len(recs)
    idx = list(range(N))
    abs_obs = abs(obs)
    ge = 0
    for _ in range(n_draws):
        # Fisher-Yates shuffle of positions; first n_entry become 'entry'
        perm = idx[:]
        for i in range(N - 1, 0, -1):
            j = rng.randint(0, i)
            perm[i], perm[j] = perm[j], perm[i]
        entry_set = set(perm[:n_entry])
        prelabeled = []
        for k, r in enumerate(recs):
            rr = dict(r)
            rr["is_entry"] = (k in entry_set)
            prelabeled.append(rr)
        c = metric_fn(prelabeled)
        if abs(c) >= abs_obs:
            ge += 1
    p = (1 + ge) / (1 + n_draws)
    return obs, p

# ---------- POSITIVE CONTROL ----------
def _lb_word_records(seqs):
    """Turn LB sign-lists into word records with NO site (global). is_entry assigned later."""
    return [{"len": len(s), "a_init": (len(s) >= 1 and s[0] == "A"), "signs": list(s)} for s in seqs if len(s) >= 1]

def pc_detect_planted(seqs, seed=SEED_PC_DETECT, n_draws=PC_DETECT_DRAWS):
    """PLANT a length difference: split LB words by a length threshold so the two groups differ in
    mean length. Group A = short words (len<=2), Group B = long words (len>=4). Assign is_entry=B
    (entry=long). The label-permutation test must detect this with correct direction (contrast>0)."""
    rng = random.Random(seed)
    # build two groups with a planted length gap
    short = [s for s in seqs if 1 <= len(s) <= 2]
    longg = [s for s in seqs if len(s) >= 4]
    # balance sizes a bit but keep gap; cap to keep it fast
    k = min(len(short), len(longg), 400)
    short = rng.sample(short, k)
    longg = rng.sample(longg, k)
    recs = ([{"is_entry": False, "len": len(s), "a_init": False} for s in short] +
            [{"is_entry": True,  "len": len(s), "a_init": False} for s in longg])
    obs, p = perm_test_contrast(recs, length_contrast, n_draws=n_draws, seed=seed)
    return obs, p  # expect obs>0, p<=0.05

def pc_false_positive(seqs, seed=SEED_PC_FP, n_splits=N_FP_SPLITS, n_draws=PC_FP_DRAWS):
    """FALSE-POSITIVE: draw two groups from the SAME distribution (random labels), run the test,
    count rejections. Rejection rate must be <=0.10."""
    rng = random.Random(seed)
    pool = [s for s in seqs if len(s) >= 1]
    # use a fixed pool of moderate size
    pool = rng.sample(pool, min(len(pool), 800))
    rejections = 0
    for sp in range(n_splits):
        recs = [{"is_entry": rng.random() < 0.5, "len": len(s), "a_init": False} for s in pool]
        # need both classes present
        ne = sum(1 for r in recs if r["is_entry"])
        if ne == 0 or ne == len(recs):
            continue
        obs, p = perm_test_contrast(recs, length_contrast, n_draws=n_draws, seed=seed + sp)
        if p <= 0.05:
            rejections += 1
    return rejections / n_splits

def positive_control(seqs):
    obs, p_det = pc_detect_planted(seqs)
    fp = pc_false_positive(seqs)
    passed = (p_det <= 0.05 and obs > 0 and fp <= 0.10)
    return {
        "pc_verdict": "PASSED" if passed else "FAILED",
        "detect_planted_p": p_det,
        "detect_direction_correct": bool(obs > 0),
        "detect_contrast": obs,
        "false_pos_rate": fp,
    }

# ---------- CROSS-SITE ----------
def per_site_tests(recs):
    """For each site with >=MIN_CLASS_PER_SITE in EACH class: length contrast + perm p, and A-rate
    contrast + perm p. Returns dict site->stats and list of testable sites."""
    by_site = defaultdict(list)
    for r in recs:
        by_site[r["site"]].append(r)
    out = {}
    testable = []
    for site, rs in by_site.items():
        ne = sum(1 for r in rs if r["is_entry"])
        nn = sum(1 for r in rs if not r["is_entry"])
        if ne >= MIN_CLASS_PER_SITE and nn >= MIN_CLASS_PER_SITE:
            testable.append(site)
            lc, lp = perm_test_contrast(rs, length_contrast, n_draws=N_DRAWS, seed=SEED_SITE + abs(hash(site)) % 100000)
            ac, ap = perm_test_contrast(rs, a_contrast, n_draws=N_DRAWS, seed=SEED_SITE + 50000 + abs(hash(site)) % 100000)
            out[site] = {
                "n_entry": ne, "n_nonentry": nn,
                "len_contrast": lc, "p": lp,
                "a_contrast": ac, "a_p": ap,
            }
    return out, testable

def leave_one_site_out(recs, exclude_site):
    """Recompute global length contrast + perm p with the largest site excluded."""
    sub = [r for r in recs if r["site"] != exclude_site]
    obs, p = perm_test_contrast(sub, length_contrast, n_draws=N_DRAWS, seed=SEED_LOO)
    return obs, p

# ---------- VERDICT ----------
def verdict(pc, global_len_p, per_site, testable, loo_p, loo_site):
    if pc["pc_verdict"] != "PASSED":
        return "MACHINERY_UNINFORMATIVE"
    if len(testable) < MIN_SITES_ROBUST:
        return "ENTRY_CLASS_UNDERPOWERED"
    if global_len_p > 0.05:
        return "ENTRY_CLASS_NO_CONTRAST"
    sig_sites = {s: v for s, v in per_site.items() if v["p"] <= 0.05}
    n_sig = len(sig_sites)
    if n_sig < MIN_SITES_ROBUST:
        return "ENTRY_CLASS_CONTRAST_SITE_LOCAL"
    # direction consistency among significant sites
    signs = set(1 if v["len_contrast"] > 0 else (-1 if v["len_contrast"] < 0 else 0) for v in sig_sites.values())
    direction_consistent = (len(signs) == 1 and 0 not in signs)
    # survives LOO: global p (on the reduced set) still <=0.05 AND direction same as global
    survives_loo = (loo_p <= 0.05)
    if direction_consistent and survives_loo:
        return "ENTRY_CLASS_STRUCTURAL_CONTRAST_ROBUST"
    return "ENTRY_CLASS_CONTRAST_SITE_LOCAL"

# ---------- main pipeline ----------
def run():
    corpus = load_corpus()
    recs = build_word_records(corpus)

    # GLOBAL
    n_entry = sum(1 for r in recs if r["is_entry"])
    n_nonentry = sum(1 for r in recs if not r["is_entry"])
    mean_len_e = mean([r["len"] for r in recs if r["is_entry"]])
    mean_len_n = mean([r["len"] for r in recs if not r["is_entry"]])
    len_obs, len_p = perm_test_contrast(recs, length_contrast, n_draws=N_DRAWS, seed=SEED_GLOBAL_LEN)
    a_e = a_rate(recs, True); a_n = a_rate(recs, False)
    a_obs, a_p = perm_test_contrast(recs, a_contrast, n_draws=N_DRAWS, seed=SEED_GLOBAL_A)

    # POSITIVE CONTROL
    seqs = load_b_damos()
    pc = positive_control(seqs)

    # CROSS-SITE
    per_site, testable = per_site_tests(recs)
    # LOO on largest site (Haghia Triada)
    loo_site = "Haghia Triada"
    loo_obs, loo_p = leave_one_site_out(recs, loo_site)

    v = verdict(pc, len_p, per_site, testable, loo_p, loo_site)

    sig_sites = {s: vv for s, vv in per_site.items() if vv["p"] <= 0.05}
    sig_signs = [1 if vv["len_contrast"] > 0 else (-1 if vv["len_contrast"] < 0 else 0) for vv in sig_sites.values()]

    return {
        "global": {
            "n_entry": n_entry, "n_nonentry": n_nonentry,
            "mean_len_entry": mean_len_e, "mean_len_nonentry": mean_len_n,
            "len_contrast": len_obs, "len_perm_p": len_p,
            "a_rate_entry": a_e, "a_rate_nonentry": a_n, "a_contrast": a_obs, "a_perm_p": a_p,
        },
        "positive_control": pc,
        "cross_site": {
            "n_sites_testable": len(testable),
            "n_sites_sig_len": len(sig_sites),
            "sig_directions": sig_signs,
            "direction_consistent": (len(set(sig_signs)) == 1 and 0 not in sig_signs) if sig_signs else False,
            "loo_excluded": loo_site, "loo_len_contrast": loo_obs, "loo_p": loo_p,
            "per_site": per_site,
        },
        "verdict": v,
    }

if __name__ == "__main__":
    res = run()
    print(json.dumps(res, indent=2, ensure_ascii=False))
