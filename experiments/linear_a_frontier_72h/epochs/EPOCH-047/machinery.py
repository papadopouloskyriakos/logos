#!/usr/bin/env python3
"""
EPOCH-047 machinery — HELD-OUT PREDICTABILITY OF THE DOCUMENT TOKEN-TYPE GRAMMAR.

Pure L2/L3 token-TYPE sequence statistics on the ORDERED per-inscription stream of token TYPES
(`word` / `num` / `nl` / `div` / `other`). NO sign identities, NO numeral values, NO phonetics,
NO meaning. The question: does a FIRST-ORDER MARKOV model of token-TYPE transitions achieve
lower HELD-OUT cross-entropy (bits/token) than a UNIGRAM baseline, and does that generalization
hold across a SITE-BLOCKED split?

FROZEN MODELS:
  - MARKOV : P(next_type | cur_type), Laplace-smoothed (add-1 over the type vocab incl. BOS/EOS),
             trained on TRAIN inscriptions. Each inscription = [BOS] + types + [EOS].
  - UNIGRAM: marginal type frequencies (incl. BOS/EOS), Laplace-smoothed, trained on TRAIN.
  - Cross-entropy on TEST: xent = -mean log2 P(t_i | context) over all non-BOS tokens
    (EOS counted as a predicted token). IMPROVEMENT = unigram_xent - markov_xent (>0 => Markov
    grammar is predictive).

FROZEN SPLITS:
  - (a) RANDOM 5-fold CV (seed-frozen): mean improvement across folds.
  - (b) SITE-BLOCKED: train on all-but-one site, test on the held-out site, for each site with
        >=15 inscriptions.

FROZEN SIGNIFICANCE: order-shuffle permutation null. For each TEST inscription, shuffle its type
order (BOS/EOS stay at ends), recompute Markov xent; permutation p-value by >=200 repeated
shuffles of the TEST set comparing real-vs-shuffled Markov xent.

POSITIVE CONTROL (gates verdict):
  - (a) DETECT: synthetic stream with KNOWN strong transition grammar (planted word->num->nl
        cycles with noise) => Markov beats unigram (improvement > 0, perm p <= 0.05).
  - (b) FALSE-POSITIVE: order-shuffled streams => improvement ~= 0 and NOT significant across
        >=20 sets.
  - If it cannot detect a planted grammar OR claims significant improvement on shuffled =>
    MACHINERY_UNINFORMATIVE.

Self-check: `python3 machinery.py` runs PC + global CV + site-blocked and prints a JSON summary.
"""
import json, os, sys, math, random
from collections import Counter, defaultdict

import numpy as np

# ---------- paths ----------
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
CORPUS = os.path.join(REPO, "corpus", "silver", "inscriptions_structured.json")
SCRIPTS = os.path.join(REPO, "scripts")
sys.path.insert(0, os.path.join(SCRIPTS, "cross_script"))

# ---------- frozen constants ----------
TYPES = ["word", "num", "nl", "div", "other"]
BOS = "BOS"
EOS = "EOS"
VOCAB = TYPES + [BOS, EOS]          # 7 symbols
V = len(VOCAB)
IDX = {t: i for i, t in enumerate(VOCAB)}

SEED_CV       = 20240780
SEED_SYNTH    = 20240781
SEED_PERM     = 20240782
SEED_FP       = 20240783

MIN_SITE_N    = 15                  # site-blocked qualifying threshold
N_FOLDS       = 5
N_PERM        = 200                 # permutation null shuffles
N_FP_SETS     = 20                  # false-positive control sets
ALPHA         = 0.05

# ---------- data loading ----------
def load_inscriptions():
    """Return list of (site, type_sequence) where type_sequence = [BOS] + types + [EOS]."""
    data = json.load(open(CORPUS, encoding="utf-8"))
    out = []
    for rec in data:
        stream = rec.get("stream") or []
        types = [tok["t"] for tok in stream if tok.get("t") in TYPES]
        if len(types) == 0:
            continue
        seq = [BOS] + types + [EOS]
        out.append((rec.get("site", ""), seq))
    return out

def load_lb_synthetic_type_stream():
    """LB DĀMOS has NO token-type stream (only wordforms). Build a SYNTHETIC type-stream
    control: each LB wordform -> 'word', with synthetic 'nl' separators between wordforms of
    the same tablet and a synthetic 'num' inserted at a fixed rate. This is a CONTROL ONLY and
    is explicitly labelled synthetic."""
    try:
        from data import load_b_damos
    except Exception:
        return []
    try:
        seqs, freq, v2g = load_b_damos()
    except Exception:
        return []
    rng = random.Random(SEED_SYNTH + 999)
    out = []
    # group wordforms into pseudo-tablets of ~8 words (DĀMOS gives a flat list)
    chunk = 8
    for i in range(0, len(seqs), chunk):
        words = seqs[i:i + chunk]
        if not words:
            continue
        types = []
        for j, w in enumerate(words):
            types.append("word")
            if rng.random() < 0.5:        # synthetic numeral after ~half of words
                types.append("num")
            if j < len(words) - 1:
                types.append("nl")
        if len(types) == 0:
            continue
        out.append(("", [BOS] + types + [EOS]))
    return out

# ---------- models ----------
def train_markov(seqs):
    """First-order transition counts -> Laplace-smoothed log2-prob matrix [V, V].
    row i = distribution over NEXT symbol given current = VOCAB[i]."""
    trans = np.ones((V, V), dtype=np.float64)   # add-1 Laplace
    for s in seqs:
        for a, b in zip(s[:-1], s[1:]):
            trans[IDX[a], IDX[b]] += 1.0
    rowsum = trans.sum(axis=1, keepdims=True)
    logp = np.log2(trans / rowsum)
    return logp

def train_unigram(seqs):
    """Marginal type frequencies incl. BOS/EOS, Laplace-smoothed -> log2-prob vector."""
    counts = np.ones(V, dtype=np.float64)
    for s in seqs:
        for t in s:
            counts[IDX[t]] += 1.0
    return np.log2(counts / counts.sum())

def xent_markov(seqs, logp):
    """Mean per-token cross-entropy (bits/token) over all non-BOS tokens (EOS counted)."""
    total = 0.0
    n = 0
    for s in seqs:
        for a, b in zip(s[:-1], s[1:]):
            total += logp[IDX[a], IDX[b]]
            n += 1
    if n == 0:
        return float("nan")
    return -total / n

def xent_unigram(seqs, logu):
    total = 0.0
    n = 0
    for s in seqs:
        for t in s[1:]:           # all non-BOS tokens (incl EOS)
            total += logu[IDX[t]]
            n += 1
    if n == 0:
        return float("nan")
    return -total / n

# ---------- permutation null (order-shuffle) ----------
def shuffle_seq(s, rng):
    """Shuffle the interior types (keep BOS at start, EOS at end)."""
    if len(s) <= 2:
        return list(s)
    interior = s[1:-1]
    interior = interior[:]
    rng.shuffle(interior)
    return [s[0]] + interior + [s[-1]]

def order_shuffle_pvalue(test_seqs, logp, rng, n_perm=N_PERM):
    """Permutation p-value: fraction of shuffles whose Markov xent is <= real Markov xent
    (i.e. shuffling does NOT raise xent). Real grammar predictive => real xent < shuffled."""
    real = xent_markov(test_seqs, logp)
    ge = 0      # count shuffles with xent <= real (i.e. as good or better than real)
    for _ in range(n_perm):
        shuf = [shuffle_seq(s, rng) for s in test_seqs]
        sx = xent_markov(shuf, logp)
        if sx <= real:
            ge += 1
    p = (ge + 1) / (n_perm + 1)
    return real, p

# ---------- splits ----------
def random_cv(seqs, k=N_FOLDS, seed=SEED_CV):
    rng = random.Random(seed)
    idx = list(range(len(seqs)))
    rng.shuffle(idx)
    folds = [idx[i::k] for i in range(k)]
    results = []
    for fi in range(k):
        test_idx = set(folds[fi])
        train = [seqs[i] for i in idx if i not in test_idx]
        test  = [seqs[i] for i in folds[fi]]
        logp = train_markov(train)
        logu = train_unigram(train)
        xm = xent_markov(test, logp)
        xu = xent_unigram(test, logu)
        rngp = random.Random(seed + fi + 1)
        _, pp = order_shuffle_pvalue(test, logp, rngp)
        results.append({
            "fold": fi,
            "n_train": len(train), "n_test": len(test),
            "markov_xent": xm, "unigram_xent": xu,
            "improvement": xu - xm,
            "perm_p": pp,
        })
    return results

def site_blocked(site_seqs):
    """site_seqs: dict site -> list of seqs. For each site with >=MIN_SITE_N inscriptions,
    train on all other sites' seqs, test on the held-out site."""
    sites = sorted(site_seqs.keys())
    big = [s for s in sites if len(site_seqs[s]) >= MIN_SITE_N]
    results = []
    for held in big:
        train = []
        for s in sites:
            if s == held:
                continue
            train.extend(site_seqs[s])
        test = site_seqs[held]
        logp = train_markov(train)
        logu = train_unigram(train)
        xm = xent_markov(test, logp)
        xu = xent_unigram(test, logu)
        rngp = random.Random(SEED_PERM + abs(hash(held)) % 100000)
        _, pp = order_shuffle_pvalue(test, logp, rngp)
        results.append({
            "site": held, "n_test": len(test),
            "markov_xent": xm, "unigram_xent": xu,
            "improvement": xu - xm,
            "perm_p": pp,
            "improves": (xu - xm) > 0 and pp <= ALPHA,
        })
    return results, big

# ---------- positive control ----------
def synth_planted_grammar(n=400, seed=SEED_SYNTH):
    """Synthetic stream with a KNOWN strong transition grammar: planted word->num->nl cycles
    with noise. Each 'line': word, then num with prob 0.85, then nl; occasionally div/other."""
    rng = random.Random(seed)
    seqs = []
    for _ in range(n):
        nlines = rng.randint(2, 8)
        types = []
        for _ in range(nlines):
            types.append("word")
            if rng.random() < 0.85:
                types.append("num")
            if rng.random() < 0.15:
                types.append("div")
            if rng.random() < 0.10:
                types.append("other")
            types.append("nl")
        seqs.append([BOS] + types + [EOS])
    return seqs

def order_destroy(seqs, seed):
    """Destroy sequential grammar by shuffling interior order (BOS/EOS fixed)."""
    rng = random.Random(seed)
    return [shuffle_seq(s, rng) for s in seqs]

def positive_control():
    """(a) DETECT planted grammar; (b) FALSE-POSITIVE on shuffled streams."""
    # (a) DETECT
    synth = synth_planted_grammar()
    rng = random.Random(SEED_CV + 100)
    idx = list(range(len(synth)))
    rng.shuffle(idx)
    folds = [idx[i::N_FOLDS] for i in range(N_FOLDS)]
    detect_imps = []
    detect_ps = []
    for fi in range(N_FOLDS):
        test_idx = set(folds[fi])
        train = [synth[i] for i in idx if i not in test_idx]
        test  = [synth[i] for i in folds[fi]]
        logp = train_markov(train)
        logu = train_unigram(train)
        xm = xent_markov(test, logp)
        xu = xent_unigram(test, logu)
        detect_imps.append(xu - xm)
        rngp = random.Random(SEED_PERM + 500 + fi)
        _, pp = order_shuffle_pvalue(test, logp, rngp)
        detect_ps.append(pp)
    detect_mean_imp = float(np.mean(detect_imps))
    detect_mean_p   = float(np.mean(detect_ps))
    detect_ok = (detect_mean_imp > 0) and (detect_mean_p <= ALPHA)

    # (b) FALSE-POSITIVE: on order-shuffled streams, improvement ~= 0 and NOT significant
    fp_significant = 0
    fp_imps = []
    for i in range(N_FP_SETS):
        sh = order_destroy(synth, SEED_FP + i)
        rng = random.Random(SEED_FP + 1000 + i)
        j = list(range(len(sh)))
        rng.shuffle(j)
        tf = [j[k::N_FOLDS] for k in range(N_FOLDS)]
        # single fold eval for speed
        test_idx = set(tf[0])
        train = [sh[k] for k in j if k not in test_idx]
        test  = [sh[k] for k in tf[0]]
        logp = train_markov(train)
        logu = train_unigram(train)
        xm = xent_markov(test, logp)
        xu = xent_unigram(test, logu)
        imp = xu - xm
        fp_imps.append(imp)
        rngp = random.Random(SEED_PERM + 9000 + i)
        _, pp = order_shuffle_pvalue(test, logp, rngp, n_perm=100)
        if imp > 0 and pp <= ALPHA:
            fp_significant += 1
    fp_mean_imp = float(np.mean(fp_imps))
    fp_ok = (fp_significant < max(1, N_FP_SETS // 4))   # not significant on most shuffled sets

    pc_pass = detect_ok and fp_ok
    return {
        "pc_verdict": "PASSED" if pc_pass else "FAILED",
        "detect_mean_improvement": detect_mean_imp,
        "detect_mean_perm_p": detect_mean_p,
        "detect_ok": detect_ok,
        "fp_mean_improvement": fp_mean_imp,
        "fp_significant_sets": fp_significant,
        "fp_total_sets": N_FP_SETS,
        "fp_ok": fp_ok,
    }

# ---------- verdict ----------
def verdict(pc, cv_results, site_results, n_big_sites):
    pc_pass = (pc["pc_verdict"] == "PASSED")
    if not pc_pass:
        return "MACHINERY_UNINFORMATIVE"
    if n_big_sites < 3:
        return "DOC_GRAMMAR_UNDERPOWERED"
    cv_mean_imp = float(np.mean([r["improvement"] for r in cv_results]))
    cv_mean_p   = float(np.mean([r["perm_p"] for r in cv_results]))
    cv_sig = (cv_mean_imp > 0) and (cv_mean_p <= ALPHA)
    n_sites_improve = sum(1 for r in site_results if r["improves"])
    if cv_sig and n_sites_improve >= 3:
        return "DOC_GRAMMAR_PREDICTIVE_HELDOUT"
    if cv_sig and n_sites_improve < 3:
        return "DOC_GRAMMAR_PREDICTIVE_SITE_LOCAL"
    return "DOC_GRAMMAR_NOT_PREDICTIVE"

# ---------- main ----------
def main():
    insc = load_inscriptions()
    seqs = [s for (_, s) in insc]
    site_seqs = defaultdict(list)
    for site, s in insc:
        site_seqs[site].append(s)

    pc = positive_control()
    cv = random_cv(seqs)
    site_res, big_sites = site_blocked(site_seqs)

    cv_mean_imp = float(np.mean([r["improvement"] for r in cv]))
    cv_mean_p   = float(np.mean([r["perm_p"] for r in cv]))
    n_sites_improve = sum(1 for r in site_res if r["improves"])

    v = verdict(pc, cv, site_res, len(big_sites))

    summary = {
        "task_id": "EPOCH-047",
        "n_inscriptions": len(seqs),
        "n_big_sites": len(big_sites),
        "big_sites": big_sites,
        "positive_control": pc,
        "cv": {
            "n_folds": N_FOLDS,
            "mean_improvement_bits_per_token": cv_mean_imp,
            "mean_perm_p": cv_mean_p,
            "folds": cv,
        },
        "site_blocked": {
            "n_sites_improving": n_sites_improve,
            "n_sites_total": len(site_res),
            "per_site": site_res,
        },
        "verdict": v,
    }
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
