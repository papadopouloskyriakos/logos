#!/usr/bin/env python3
"""
EPOCH-034 machinery — A-INITIAL WORDS AS INSCRIPTION-INITIAL (HEADING) MARKERS.

Pure L2/L3 POSITIONAL / DOCUMENT-STRUCTURAL statistics on ANONYMOUS sign sequences.
No phonetics, no sound, no meaning, no reading. "A-" and "heading" are anonymous positional
labels; "heading" = DOCUMENT-INITIAL POSITION only.

FROZEN METRIC: among inscriptions with >=2 word tokens,
  p_A_first = fraction whose FIRST word is A-initial (first sign == 'A').
  p_A_last  = fraction whose LAST  word is A-initial (control axis).
  base_A_rate = per-inscription mean of (A-initial words / total words).

FROZEN NULL — WITHIN-INSCRIPTION POSITION PERMUTATION (calibrated by construction):
  For each inscription, randomly permute its word ORDER (word multiset fixed), recompute p_A_first;
  >=2000 draws; one-sided p = frac draws with permuted p_A_first >= observed.
  Holds each inscription's word multiset fixed and tests POSITION only (analogous to E023/E024
  within-word sign-position null, lifted to word-in-document level).

POSITIVE CONTROL (gates verdict) on LB (DĀMOS; NO site metadata -> SEEDED pseudo-inscription
partition, stated explicitly):
  - DETECT (planted heading bias): force a chosen sign-class to be inscription-initial in X% of
    pseudo-inscriptions; null MUST reject (p<=0.05) in the correct (initial-biased) direction.
  - FALSE-POSITIVE: on position-randomized pseudo-inscriptions (exact H0), rejection rate
    (frac p<=0.05) MUST be <=0.10 across >=30 independent sets.
  Failure of either -> MACHINERY_UNINFORMATIVE.

Self-check: `python3 machinery.py` runs the full pipeline + PC and prints a JSON summary.
"""
import json, os, sys, hashlib, random
from collections import Counter, defaultdict

# ---------- paths ----------
HERE = os.path.dirname(os.path.abspath(__file__))
# HERE = .../experiments/linear_a_frontier_72h/epochs/EPOCH-034
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
CORPUS = os.path.join(REPO, "corpus", "silver", "inscriptions_structured.json")
SCRIPTS = os.path.join(REPO, "scripts")

# ---------- seeds / knobs (FROZEN) ----------
SEED_GLOBAL      = 20240740
SEED_PC_DETECT   = 20240741
SEED_PC_FP       = 20240742
SEED_SITE_BASE   = 20240743
SEED_LOO         = 20240744
SEED_LB_PARTITION= 20240745
N_DRAWS          = 2000      # >=2000
PC_DETECT_DRAWS  = 2000
PC_FP_DRAWS      = 1000      # per control set
N_FP_SETS        = 30        # >=30
MIN_SITE_INSC    = 15        # >=15 qualifying inscriptions per site
MIN_SITES_ROBUST = 3
PLANT_FRAC       = 0.45      # plant heading bias: chosen sign forced initial in ~45% of pseudo-insc
LB_PSEUDO_LEN    = 6         # words per pseudo-inscription (chunk size)

# ---------- corpus IO ----------
def load_corpus(path=CORPUS):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_b_damos():
    """Linear B positive-control benchmark. DĀMOS has NO site/inscription metadata.
    Returns a flat list of wordforms (each a list of signs)."""
    sys.path.insert(0, SCRIPTS)
    from cross_script import data as D
    seqs, freq, v2g = D.load_b_damos()
    return seqs

# ---------- core: word sequences ----------
def words_of(insc):
    """Ordered list of word sign-lists for an inscription (non-word tokens ignored)."""
    out = []
    for tok in insc.get("stream", []) or []:
        if tok.get("t") == "word":
            sg = list(tok.get("signs", []) or [])
            if sg:
                out.append(sg)
    return out

def is_A(w):
    return len(w) > 0 and w[0] == "A"

def qualifying(corpus):
    """Inscriptions with >=2 non-empty word tokens."""
    return [ins for ins in corpus if len(words_of(ins)) >= 2]

# ---------- observed metrics ----------
def p_A_first(records):
    """records = list of word-sequences (one per inscription)."""
    if not records:
        return 0.0
    return sum(1 for ws in records if is_A(ws[0])) / len(records)

def p_A_last(records):
    if not records:
        return 0.0
    return sum(1 for ws in records if is_A(ws[-1])) / len(records)

def base_A_rate(records):
    """per-inscription mean of (A-initial words / total words)."""
    if not records:
        return 0.0
    rs = []
    for ws in records:
        if not ws:
            continue
        rs.append(sum(1 for w in ws if is_A(w)) / len(ws))
    return sum(rs) / len(rs) if rs else 0.0

# ---------- FROZEN NULL: within-inscription position permutation ----------
def null_permutation(records, n_draws, seed, observed_first):
    """For each inscription, permute word order; recompute p_A_first each draw.
    One-sided p = frac draws with permuted p_A_first >= observed."""
    rng = random.Random(seed)
    counts = [0, 0]  # [ge, total]
    means = []
    for _ in range(n_draws):
        perm_first = []
        for ws in records:
            if len(ws) <= 1:
                perm_first.append(ws[0] if ws else [])
            else:
                p = ws[:]
                rng.shuffle(p)
                perm_first.append(p[0])
        pf = sum(1 for w in perm_first if is_A(w)) / len(records)
        means.append(pf)
        counts[1] += 1
        if pf >= observed_first - 1e-15:
            counts[0] += 1
    null_mean = sum(means) / len(means)
    p = counts[0] / counts[1]
    return null_mean, p

# ---------- POSITIVE CONTROL ----------
def build_lb_pseudo_inscriptions(seqs, seed):
    """Chunk flat DĀMOS wordform list into ordered pseudo-inscriptions of LB_PSEUDO_LEN words.
    DĀMOS has no site/inscription metadata -> SEEDED partition (stated)."""
    rng = random.Random(seed)
    pool = [list(s) for s in seqs if len(s) > 0]
    rng.shuffle(pool)
    recs = []
    i = 0
    while i + LB_PSEUDO_LEN <= len(pool):
        recs.append(pool[i:i + LB_PSEUDO_LEN])
        i += LB_PSEUDO_LEN
    return recs

def plant_heading_bias(records, sign, frac, seed):
    """Force `sign` to be the FIRST word of a pseudo-inscription in `frac` of records,
    by swapping an existing word starting with `sign` into position 0 (or prepending a sampled
    such word if none exists). Returns new records with a planted initial-position bias."""
    rng = random.Random(seed)
    # collect sign-initial words from the pool
    pool_sign = [w for rec in records for w in rec if w[0] == sign]
    pool_other= [w for rec in records for w in rec if w[0] != sign]
    out = []
    for rec in records:
        rec = [list(w) for w in rec]
        if rng.random() < frac:
            # ensure first word is sign-initial
            if rec[0][0] != sign:
                if pool_sign:
                    rec[0] = list(rng.choice(pool_sign))
                else:
                    rec[0] = [sign] + rec[0]
        out.append(rec)
    return out

def position_randomize(records, seed):
    """Exact H0: permute word order within each pseudo-inscription."""
    rng = random.Random(seed)
    out = []
    for rec in records:
        p = [list(w) for w in rec]
        rng.shuffle(p)
        out.append(p)
    return out

def pc_detect(seqs, seed):
    """DETECT arm: plant a heading bias on sign 'A' (a common LB first sign) and confirm the
    position-permutation null rejects in the correct (initial-biased) direction."""
    base = build_lb_pseudo_inscriptions(seqs, SEED_LB_PARTITION)
    planted = plant_heading_bias(base, "A", PLANT_FRAC, seed)
    obs = p_A_first(planted)
    null_mean, p = null_permutation(planted, PC_DETECT_DRAWS, seed ^ 0x9e37, obs)
    return {"obs": obs, "null_mean": null_mean, "p": p,
            "reject_correct_direction": (p <= 0.05 and obs > null_mean)}

def pc_false_positive(seqs, seed):
    """FALSE-POSITIVE arm: on position-randomized pseudo-inscriptions (exact H0), measure the
    rejection rate across N_FP_SETS independent sets. Must be <=0.10."""
    rng = random.Random(seed)
    rejects = 0
    ps = []
    for k in range(N_FP_SETS):
        s = rng.randrange(1 << 30)
        base = build_lb_pseudo_inscriptions(seqs, SEED_LB_PARTITION + k)
        # exact H0: randomize positions within each pseudo-inscription
        h0 = position_randomize(base, s)
        obs = p_A_first(h0)
        # the null permutes positions again; under exact H0 obs should be a typical draw
        _, p = null_permutation(h0, PC_FP_DRAWS, s ^ 0x517, obs)
        ps.append(p)
        if p <= 0.05:
            rejects += 1
    fpr = rejects / N_FP_SETS
    return {"false_pos_rate": fpr, "n_sets": N_FP_SETS, "ps": ps}

def run_positive_control(seqs):
    det = pc_detect(seqs, SEED_PC_DETECT)
    fp  = pc_false_positive(seqs, SEED_PC_FP)
    passed = det["reject_correct_direction"] and fp["false_pos_rate"] <= 0.10
    return {"pc_verdict": "PASSED" if passed else "FAILED",
            "detect_obs": det["obs"], "detect_null_mean": det["null_mean"],
            "detect_planted_p": det["p"],
            "detect_reject_correct_direction": det["reject_correct_direction"],
            "false_pos_rate": fp["false_pos_rate"], "n_fp_sets": fp["n_sets"]}

# ---------- CROSS-SITE ----------
def per_site_test(records_by_site, n_draws, seed_base):
    out = {}
    for site, recs in records_by_site.items():
        obs = p_A_first(recs)
        nm, p = null_permutation(recs, n_draws, seed_base + hash(site) % 100000, obs)
        out[site] = {"n_insc": len(recs), "p_A_first": obs, "null_mean": nm, "p": p,
                     "sig_initial": (p <= 0.05 and obs > nm)}
    return out

def loo_largest(records_by_site, n_draws, seed):
    """Leave-one-site-out on the largest site (Haghia Triada)."""
    largest = max(records_by_site.keys(), key=lambda s: len(records_by_site[s]))
    rest = [r for s, rs in records_by_site.items() if s != largest for r in rs]
    obs = p_A_first(rest)
    nm, p = null_permutation(rest, n_draws, seed, obs)
    return largest, obs, nm, p

# ---------- VERDICT ----------
def verdict(pc_passed, global_p, global_obs, global_null_mean,
            n_sites_testable, n_sites_sig, direction_consistent,
            loo_p, loo_survives):
    if not pc_passed:
        return "MACHINERY_UNINFORMATIVE"
    if n_sites_testable < MIN_SITES_ROBUST:
        return "A_HEADING_UNDERPOWERED"
    if global_p > 0.05:
        return "A_HEADING_ROLE_NO_SIGNAL"
    if (n_sites_sig >= MIN_SITES_ROBUST and direction_consistent and loo_survives):
        return "A_HEADING_ROLE_CROSS_SITE_ROBUST"
    return "A_HEADING_ROLE_SITE_LOCAL"

# ---------- MAIN PIPELINE ----------
def run():
    corpus = load_corpus()
    qual = qualifying(corpus)
    records = [words_of(ins) for ins in qual]

    # GLOBAL
    obs_first = p_A_first(records)
    obs_last  = p_A_last(records)
    base_rate = base_A_rate(records)
    null_mean, g_p = null_permutation(records, N_DRAWS, SEED_GLOBAL, obs_first)

    # POSITIVE CONTROL (gates)
    seqs = load_b_damos()
    pc = run_positive_control(seqs)
    pc_passed = (pc["pc_verdict"] == "PASSED")

    # CROSS-SITE
    by_site = defaultdict(list)
    for ins in qual:
        by_site[ins.get("site", "") or "?"].append(words_of(ins))
    testable = {s: r for s, r in by_site.items() if len(r) >= MIN_SITE_INSC}
    per_site = per_site_test(testable, N_DRAWS, SEED_SITE_BASE)
    n_sites_testable = len(testable)
    sig_sites = [s for s, d in per_site.items() if d["sig_initial"]]
    n_sites_sig = len(sig_sites)
    # direction consistency: all significant sites initial-biased (sig_initial already requires obs>null_mean)
    # plus global direction initial-biased
    direction_consistent = (obs_first > null_mean) and all(per_site[k]["sig_initial"] for k in sig_sites)

    # LOO on largest site
    loo_site, loo_obs, loo_nm, loo_p = loo_largest(by_site, N_DRAWS, SEED_LOO)
    loo_survives = (loo_p <= 0.05 and loo_obs > loo_nm)

    v = verdict(pc_passed, g_p, obs_first, null_mean,
                n_sites_testable, n_sites_sig, direction_consistent,
                loo_p, loo_survives)

    return {
        "global": {"n_inscriptions_ge2w": len(records),
                   "p_A_first_observed": obs_first,
                   "null_mean_p_A_first": null_mean,
                   "null_p": g_p,
                   "p_A_last_observed": obs_last,
                   "base_A_rate": base_rate},
        "positive_control": pc,
        "cross_site": {"n_sites_testable": n_sites_testable,
                       "n_sites_sig": n_sites_sig,
                       "direction_consistent": bool(direction_consistent),
                       "loo_excluded": loo_site,
                       "loo_p": loo_p,
                       "loo_obs": loo_obs,
                       "loo_survives": bool(loo_survives),
                       "per_site": {s: {"n_insc": d["n_insc"], "p_A_first": d["p_A_first"],
                                        "p": d["p"], "null_mean": d["null_mean"],
                                        "sig_initial": d["sig_initial"]}
                                    for s, d in per_site.items()}},
        "verdict": v,
    }

if __name__ == "__main__":
    res = run()
    print(json.dumps(res, indent=2, ensure_ascii=False))
