#!/usr/bin/env python3
"""
EPOCH-031 machinery — LEDGER WORD->NUMERAL ORDER, CALIBRATED PAIR-FLIP NULL.

Token-ORDER structure only (L2/L3). No arithmetic on numeral values, no phonetics, no meaning.

Frozen null: for each observed adjacent word/num pair, independently keep or FLIP its order with p=0.5
(fair coin per pair), recompute p_wordfirst. Exchangeable by construction -> calibrated.
Equivalently #word_first ~ Binomial(n_adj, 0.5); exact binomial two-sided p must agree with pair-flip p.

Self-check (`python3 machinery.py`): runs the full pipeline on the real corpus and prints a JSON summary;
also runs the positive-control calibration check.
"""
import json, os, sys, hashlib
from collections import defaultdict
from math import comb

# ---------- deterministic RNG (seeded) ----------
import random
_RNG = random.Random(20240708)

# ---------- paths ----------
HERE = os.path.dirname(os.path.abspath(__file__))
# corpus is at repo root: <repo>/corpus/silver/inscriptions_structured.json
# HERE = .../experiments/linear_a_frontier_72h/epochs/EPOCH-031
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
CORPUS = os.path.join(REPO, "corpus", "silver", "inscriptions_structured.json")

# ---------- core: extract adjacent word/num pairs ----------
def adj_pairs(insc):
    """Return list of 'word_first'|'num_first' for adjacent (word,num) pairs in stream (type key 'num')."""
    s = insc.get("stream", []) or []
    out = []
    for i in range(len(s) - 1):
        ta = s[i].get("t"); tb = s[i+1].get("t")
        if {ta, tb} == {"word", "num"}:
            if ta == "word" and tb == "num":
                out.append("word_first")
            elif ta == "num" and tb == "word":
                out.append("num_first")
    return out

def load_corpus(path=CORPUS):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def global_counts(corpus):
    wf = nf = 0
    per_site = defaultdict(lambda: [0, 0])  # site -> [wf, nf]
    for ins in corpus:
        pairs = adj_pairs(ins)
        w = sum(1 for p in pairs if p == "word_first")
        n = sum(1 for p in pairs if p == "num_first")
        wf += w; nf += n
        per_site[ins.get("site", "?")][0] += w
        per_site[ins.get("site", "?")][1] += n
    return wf, nf, dict(per_site)

# ---------- statistics ----------
def p_wordfirst(wf, nf):
    n = wf + nf
    return (wf / n) if n else 0.0

def _log_binom_pmf(k, n, p0=0.5):
    """log P(X=k) for X~Binom(n,p0), numerically stable via log-factorials."""
    from math import lgamma, log
    if p0 <= 0.0:
        return 0.0 if k == n else float("-inf")
    if p0 >= 1.0:
        return 0.0 if k == 0 else float("-inf")
    logc = lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1)
    return logc + k * log(p0) + (n - k) * log(1.0 - p0)

def binom_two_sided_p(wf, n, p0=0.5):
    """Exact two-sided binomial p-value for H0: X~Binom(n,p0), observed X=wf.
    Two-sided = sum of P(X=k) over k with P(X=k) <= P(X=wf). Numerically stable (log-space)."""
    from math import exp, isinf
    if n == 0:
        return 1.0
    log_obs = _log_binom_pmf(wf, n, p0)
    total = 0.0
    for k in range(n + 1):
        lk = _log_binom_pmf(k, n, p0)
        if isinf(lk):
            continue
        if lk <= log_obs + 1e-9:
            total += exp(lk)
    return min(1.0, max(0.0, total))

def pairflip_p(wf, nf, n_draws=5000, seed=20240708):
    """Pair-flip null two-sided p.
    For each draw: for each of n_adj pairs, flip order w.p. 0.5; count word_first; compute p_wordfirst.
    Two-sided p = fraction of draws with |p_draw - 0.5| >= |p_obs - 0.5|.
    Returns (p, null_p_wordfirst_mean, null_p_wordfirst_dist_sample)."""
    rng = random.Random(seed)
    n_adj = wf + nf
    p_obs = wf / n_adj if n_adj else 0.5
    dev_obs = abs(p_obs - 0.5)
    ge = 0
    null_ps = []
    for _ in range(n_draws):
        # each pair independently word_first w.p. 0.5
        k = sum(rng.random() < 0.5 for _ in range(n_adj))  # = #word_first under H0
        p_draw = k / n_adj if n_adj else 0.5
        null_ps.append(p_draw)
        if abs(p_draw - 0.5) >= dev_obs - 1e-15:
            ge += 1
    p = ge / n_draws
    mean_null = sum(null_ps) / len(null_ps)
    return p, mean_null

# ---------- positive control ----------
def pc_detect_planted(n_adj=1059, bias=0.90, n_draws=5000, seed=11):
    """Plant a 90% word-first bias: generate n_adj pairs each word_first w.p. bias.
    Run pair-flip null; expect reject (p<=0.05) in word-first direction."""
    rng = random.Random(seed)
    wf = sum(rng.random() < bias for _ in range(n_adj))
    nf = n_adj - wf
    p, _ = pairflip_p(wf, nf, n_draws=n_draws, seed=seed + 1)
    bp = binom_two_sided_p(wf, n_adj)
    direction_ok = (wf / n_adj) > 0.5
    return {"detect_planted_p": p, "binom_p": bp, "wf": wf, "nf": nf,
            "p_wordfirst": wf / n_adj, "direction_ok": direction_ok}

def pc_false_positive(n_adj=1059, n_sets=30, alpha=0.05, n_draws=2000, seed=101):
    """True H0: each pair's order set by fair coin. Rejection rate must be <=0.10."""
    rng = random.Random(seed)
    rejects = 0
    for s in range(n_sets):
        wf = sum(rng.random() < 0.5 for _ in range(n_adj))
        nf = n_adj - wf
        p, _ = pairflip_p(wf, nf, n_draws=n_draws, seed=seed + 1000 + s)
        if p <= alpha:
            rejects += 1
    return {"false_pos_rate": rejects / n_sets, "n_sets": n_sets, "rejects": rejects}

# ---------- cross-site ----------
def cross_site(per_site, min_adj=15, n_draws=5000, loo_site="Haghia Triada"):
    testable = {s: (wf, nf) for s, (wf, nf) in per_site.items() if wf + nf >= min_adj}
    per_site_out = {}
    n_sig = 0
    directions = []
    for s, (wf, nf) in testable.items():
        n = wf + nf
        p, _ = pairflip_p(wf, nf, n_draws=n_draws, seed=hash(s) % (2**31))
        bp = binom_two_sided_p(wf, n)
        pwf = wf / n
        sig = (p <= 0.05) and (pwf > 0.5)
        if sig:
            n_sig += 1
        directions.append("word_first" if pwf > 0.5 else ("num_first" if pwf < 0.5 else "tie"))
        per_site_out[s] = {"n_adj": n, "n_word_first": wf, "n_num_first": nf,
                           "p_wordfirst": pwf, "p": p, "binom_p": bp, "sig": sig}
    direction_consistent = len(set(directions)) == 1 and directions[0] == "word_first"
    # leave-one-site-out on the largest site
    loo_wf = 0; loo_nf = 0
    for s, (wf, nf) in per_site.items():
        if s == loo_site:
            continue
        loo_wf += wf; loo_nf += nf
    loo_n = loo_wf + loo_nf
    loo_p, _ = pairflip_p(loo_wf, loo_nf, n_draws=n_draws, seed=hash("loo") % (2**31))
    loo_bp = binom_two_sided_p(loo_wf, loo_n)
    loo_survives = (loo_p <= 0.05) and (loo_wf / loo_n > 0.5)
    return {
        "n_sites_testable": len(testable),
        "n_sites_sig": n_sig,
        "direction_consistent": direction_consistent,
        "loo_excluded": loo_site,
        "loo_p": loo_p,
        "loo_binom_p": loo_bp,
        "loo_survives": loo_survives,
        "loo_n_adj": loo_n,
        "loo_p_wordfirst": loo_wf / loo_n,
        "per_site": per_site_out,
    }

# ---------- verdict (frozen mechanical) ----------
def verdict(pc_passed, global_p, global_pwf, n_sites_sig, direction_consistent,
            loo_survives, n_sites_testable):
    if not pc_passed:
        return "MACHINERY_UNINFORMATIVE"
    if n_sites_testable < 3:
        return "LEDGER_UNDERPOWERED"
    if global_p > 0.05:
        return "LEDGER_WORD_NUMERAL_NO_SIGNAL"
    if (global_p <= 0.05 and global_pwf > 0.5 and n_sites_sig >= 3
            and direction_consistent and loo_survives):
        return "LEDGER_WORD_NUMERAL_CROSS_SITE_ROBUST"
    return "LEDGER_WORD_NUMERAL_SITE_LOCAL"

# ---------- full pipeline ----------
def run(corpus_path=CORPUS, n_draws=5000, pc_draws=5000, fp_sets=30, fp_draws=2000, verbose=True):
    corpus = load_corpus(corpus_path)
    wf, nf, per_site = global_counts(corpus)
    n_adj = wf + nf
    pwf = p_wordfirst(wf, nf)
    g_p, g_mean_null = pairflip_p(wf, nf, n_draws=n_draws, seed=20240708)
    g_bp = binom_two_sided_p(wf, n_adj)

    # positive control
    det = pc_detect_planted(n_adj=n_adj, bias=0.90, n_draws=pc_draws, seed=11)
    fp = pc_false_positive(n_adj=n_adj, n_sets=fp_sets, alpha=0.05, n_draws=fp_draws, seed=101)
    pc_passed = bool(det["detect_planted_p"] <= 0.05 and det["direction_ok"] and fp["false_pos_rate"] <= 0.10)

    # cross-site
    cs = cross_site(per_site, min_adj=15, n_draws=n_draws, loo_site="Haghia Triada")

    v = verdict(pc_passed, g_p, pwf, cs["n_sites_sig"], cs["direction_consistent"],
                cs["loo_survives"], cs["n_sites_testable"])

    out = {
        "global": {"n_adj": n_adj, "n_word_first": wf, "n_num_first": nf,
                   "p_wordfirst": pwf, "pairflip_p": g_p, "binom_p": g_bp,
                   "null_mean_p_wordfirst": g_mean_null},
        "positive_control": {"pc_verdict": "PASSED" if pc_passed else "FAILED",
                             "detect_planted_p": det["detect_planted_p"],
                             "detect_direction_ok": det["direction_ok"],
                             "false_pos_rate": fp["false_pos_rate"],
                             "fp_n_sets": fp["n_sets"], "fp_rejects": fp["rejects"]},
        "cross_site": cs,
        "verdict": v,
    }
    if verbose:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    return out

if __name__ == "__main__":
    # self-check: run full pipeline + sanity asserts
    out = run()
    g = out["global"]; pc = out["positive_control"]; cs = out["cross_site"]
    # sanity: pair-flip p and binom p should agree (both ~0 for this extreme signal)
    print("\n--- SELF-CHECK ---", file=sys.stderr)
    print(f"global n_adj={g['n_adj']} p_wordfirst={g['p_wordfirst']:.6f}", file=sys.stderr)
    print(f"pairflip_p={g['pairflip_p']:.6f}  binom_p={g['binom_p']:.3e}  null_mean={g['null_mean_p_wordfirst']:.4f}", file=sys.stderr)
    print(f"PC: {pc['pc_verdict']}  detect_p={pc['detect_planted_p']:.4f}  fp_rate={pc['false_pos_rate']:.4f}", file=sys.stderr)
    print(f"cross_site: testable={cs['n_sites_testable']} sig={cs['n_sites_sig']} consistent={cs['direction_consistent']} loo_survives={cs['loo_survives']} loo_p={cs['loo_p']:.6f}", file=sys.stderr)
    print(f"VERDICT: {out['verdict']}", file=sys.stderr)
    # hard asserts
    assert g["n_adj"] == 1059, f"n_adj mismatch {g['n_adj']}"
    assert g["n_word_first"] == 1040 and g["n_num_first"] == 19
    assert abs(g["null_mean_p_wordfirst"] - 0.5) < 0.02, "null mean not ~0.5"
    assert pc["detect_planted_p"] <= 0.05, "PC detect failed"
    assert pc["false_pos_rate"] <= 0.10, f"PC fp rate too high {pc['false_pos_rate']}"
    assert cs["n_sites_testable"] == 8, f"testable sites {cs['n_sites_testable']}"
    print("SELF-CHECK: ALL ASSERTS PASSED", file=sys.stderr)
