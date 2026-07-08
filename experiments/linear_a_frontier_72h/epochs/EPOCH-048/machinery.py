#!/usr/bin/env python3
"""
EPOCH-048 machinery — SIGN-LEVEL HELD-OUT REDUNDANCY / ENTROPY RATE.

Pure L2/L3 sign-sequence statistics on ANONYMOUS sign ids. No phonetics, no sound, no meaning,
no reading, no language identification. "Redundancy" = a first-order sign Markov model beats a
sign-unigram baseline on HELD-OUT cross-entropy (bits/sign). It is an information-theoretic
statistic, NOT evidence of any language family or reading.

FROZEN MODELS:
  - UNIGRAM : P(sign) with add-k smoothing (context-free marginal).
  - MARKOV  : P(next_sign | cur_sign) first-order, add-k smoothing.
  Cross-entropy per word averaged over predicted positions (BOS->s1, ..., sL->EOS);
  denominator = number of signs in the word (L). BOS/EOS are boundary markers.

FROZEN SPLIT DISCIPLINE:
  - Train unigram/Markov on TRAIN words only; evaluate xent on TEST words only.
  - k chosen on TRAIN via internal train/val split (k in {0.01,0.05,0.1,0.2,0.5,1.0}).
  - RANDOM 5-fold CV (global) and SITE-BLOCKED (leave-one-site-out, sites with >=30 words).

FROZEN SIGNIFICANCE:
  - Order-shuffle null: permute interior signs of each TEST word; recompute Markov improvement.
    p = fraction of R=200 shuffles with shuffled_improvement >= observed_improvement.

POSITIVE CONTROL (gates verdict):
  - DETECT: on LB (DAMOS) word sign-sequences (a REAL language), Markov must beat unigram
    (improvement > 0, p <= 0.05).
  - FALSE-POSITIVE: on order-shuffled words, improvement ~ 0 (not significant) across >=20 sets.
  If DETECT fails OR FALSE-POSITIVE fires -> MACHINERY_UNINFORMATIVE.

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

# ---------- frozen constants ----------
BOS = "<BOS>"
EOS = "<EOS>"
K_GRID = [0.01, 0.05, 0.1, 0.2, 0.5, 1.0]
MIN_SITE_WORDS = 30
N_FOLDS = 5
N_SHUFFLE = 200
N_FALSEPOS_SETS = 20
SEED = 20240748
RNG = random.Random(SEED)

# ---------- corpus IO ----------
def load_corpus(path=CORPUS):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def la_words(corpus):
    """Return list of (site, sign_list) for every word token."""
    out = []
    for ins in corpus:
        s = ins.get("site", "") or "UNKNOWN"
        for tok in ins.get("stream", []):
            if tok.get("t") == "word":
                sg = tok.get("signs") or []
                if len(sg) >= 1:
                    out.append((s, list(sg)))
    return out

def lb_words():
    sys.path.insert(0, SCRIPTS)
    from cross_script import data as D
    seqs, freq, v2g = D.load_b_damos()
    return [("LB", list(w)) for w in seqs if len(w) >= 1]

# ---------- models ----------
def vocab_of(words):
    """words: list of sign_lists. Returns sorted vocab including BOS/EOS over observed signs."""
    v = set([BOS, EOS])
    for _, sg in words:
        v.update(sg)
    return sorted(v)

def train_unigram(words, k, vocab):
    """Return Counter of unigram counts and total. vocab is the full set (for smoothing denom)."""
    counts = Counter()
    for _, sg in words:
        for s in sg:
            counts[s] += 1
    total = sum(counts.values())
    V = len(vocab)
    log2 = math.log2
    # precompute log-probs
    logp = {}
    for s in vocab:
        logp[s] = -log2((counts.get(s, 0) + k) / (total + k * V))
    return {"counts": counts, "total": total, "V": V, "k": k, "logp": logp}

def unigram_xent(model, words):
    """Mean per-sign cross-entropy (bits) over TEST words. Denominator = L (signs in word)."""
    logp = model["logp"]
    tot_bits = 0.0
    tot_pos = 0
    for _, sg in words:
        L = len(sg)
        if L == 0:
            continue
        bits = 0.0
        for s in sg:
            bits += logp.get(s, 30.0)  # unseen -> heavy penalty (capped)
        tot_bits += bits
        tot_pos += L
    if tot_pos == 0:
        return float("nan")
    return tot_bits / tot_pos

def train_markov(words, k, vocab):
    """First-order Markov. Transitions prev->next. Contexts include BOS and each sign; targets
    include each sign and EOS."""
    trans = defaultdict(Counter)
    for _, sg in words:
        prev = BOS
        for s in sg:
            trans[prev][s] += 1
            prev = s
        trans[prev][EOS] += 1
    V = len(vocab)
    # precompute log-probs per context
    logp = {}
    for ctx in list(trans.keys()) + [c for c in vocab if c not in trans]:
        row = trans.get(ctx, Counter())
        tot = sum(row.values())
        d = {}
        for s in vocab:
            d[s] = -math.log2((row.get(s, 0) + k) / (tot + k * V))
        logp[ctx] = d
    return {"trans": trans, "V": V, "k": k, "logp": logp}

def markov_xent(model, words):
    """Mean per-sign cross-entropy (bits) over TEST words. Predicted positions: BOS->s1, ...,
    sL->EOS. Denominator = L (number of signs)."""
    logp = model["logp"]
    default_ctx = logp.get(BOS, {})
    tot_bits = 0.0
    tot_pos = 0
    for _, sg in words:
        L = len(sg)
        if L == 0:
            continue
        prev = BOS
        bits = 0.0
        for s in sg:
            row = logp.get(prev, default_ctx)
            bits += row.get(s, 30.0)
            prev = s
        # final EOS prediction
        row = logp.get(prev, default_ctx)
        bits += row.get(EOS, 30.0)
        tot_bits += bits
        tot_pos += L
    if tot_pos == 0:
        return float("nan")
    return tot_bits / tot_pos

# ---------- k selection on TRAIN ----------
def choose_k(train_words, vocab):
    """Internal train/val split of TRAIN to pick k minimizing val Markov xent."""
    idx = list(range(len(train_words)))
    RNG.shuffle(idx)
    cut = int(0.8 * len(idx))
    tr = [train_words[i] for i in idx[:cut]]
    va = [train_words[i] for i in idx[cut:]]
    if len(va) < 10:
        va = tr
    best_k, best_x = 0.1, float("inf")
    for k in K_GRID:
        m = train_markov(tr, k, vocab)
        x = markov_xent(m, va)
        if x < best_x:
            best_x, best_k = x, k
    return best_k

# ---------- order-shuffle null ----------
def shuffle_words(words, rng):
    out = []
    for site, sg in words:
        if len(sg) <= 1:
            out.append((site, list(sg)))
            continue
        interior = list(sg)
        rng.shuffle(interior)
        out.append((site, interior))
    return out

def order_shuffle_p(train_words, test_words, vocab, k, observed_improvement, n=N_SHUFFLE):
    """p = fraction of shuffles where shuffled_improvement >= observed_improvement.
    shuffled_improvement = unigram_xent(shuffled_test) - markov_xent(shuffled_test).
    Models trained on TRAIN (unshuffled)."""
    rng = random.Random(SEED + 99991)
    ge = 0
    uni = train_unigram(train_words, k, vocab)
    mar = train_markov(train_words, k, vocab)
    for _ in range(n):
        sh = shuffle_words(test_words, rng)
        u = unigram_xent(uni, sh)
        m = markov_xent(mar, sh)
        imp = u - m
        if imp >= observed_improvement:
            ge += 1
    return ge / n

# ---------- splits ----------
def kfold_indices(n, k, rng):
    idx = list(range(n))
    rng.shuffle(idx)
    folds = [[] for _ in range(k)]
    for i, ix in enumerate(idx):
        folds[i % k].append(ix)
    return folds

def run_cv(words, n_folds=N_FOLDS, seed=SEED):
    rng = random.Random(seed)
    folds = kfold_indices(len(words), n_folds, rng)
    results = []
    for f in range(n_folds):
        test_idx = set(folds[f])
        train = [words[i] for i in range(len(words)) if i not in test_idx]
        test = [words[i] for i in test_idx]
        vocab = vocab_of(train)
        k = choose_k(train, vocab)
        uni = train_unigram(train, k, vocab)
        mar = train_markov(train, k, vocab)
        ux = unigram_xent(uni, test)
        mx = markov_xent(mar, test)
        imp = ux - mx
        p = order_shuffle_p(train, test, vocab, k, imp)
        results.append({"k": k, "unigram_xent": ux, "markov_xent": mx,
                        "improvement": imp, "p": p, "n_test": len(test)})
    return results

def run_site_blocked(words, min_words=MIN_SITE_WORDS):
    by_site = defaultdict(list)
    for site, sg in words:
        by_site[site].append((site, sg))
    sites = sorted([s for s, ws in by_site.items() if len(ws) >= min_words],
                   key=lambda s: -len(by_site[s]))
    per_site = {}
    for held in sites:
        test = by_site[held]
        train = []
        for s in by_site:
            if s == held:
                continue
            train.extend(by_site[s])
        vocab = vocab_of(train)
        k = choose_k(train, vocab)
        uni = train_unigram(train, k, vocab)
        mar = train_markov(train, k, vocab)
        ux = unigram_xent(uni, test)
        mx = markov_xent(mar, test)
        imp = ux - mx
        p = order_shuffle_p(train, test, vocab, k, imp)
        per_site[held] = {"n_test": len(test), "k": k, "unigram_xent": ux,
                          "markov_xent": mx, "improvement": imp, "p": p}
    return per_site

# ---------- positive control ----------
def positive_control(la_words_all):
    """(a) DETECT on LB; (b) FALSE-POSITIVE on shuffled LA words."""
    out = {}
    # (a) DETECT on LB
    lb = lb_words()
    rng = random.Random(SEED + 1)
    folds = kfold_indices(len(lb), N_FOLDS, rng)
    imps, ps, mxs, uxs = [], [], [], []
    for f in range(N_FOLDS):
        test_idx = set(folds[f])
        train = [lb[i] for i in range(len(lb)) if i not in test_idx]
        test = [lb[i] for i in test_idx]
        vocab = vocab_of(train)
        k = choose_k(train, vocab)
        uni = train_unigram(train, k, vocab)
        mar = train_markov(train, k, vocab)
        ux = unigram_xent(uni, test)
        mx = markov_xent(mar, test)
        imp = ux - mx
        p = order_shuffle_p(train, test, vocab, k, imp, n=100)
        imps.append(imp); ps.append(p); mxs.append(mx); uxs.append(ux)
    out["lb_improvement_bits"] = float(np.mean(imps))
    out["lb_p"] = float(np.mean(ps))
    out["lb_markov_xent"] = float(np.mean(mxs))
    out["lb_unigram_xent"] = float(np.mean(uxs))
    out["detect"] = (out["lb_improvement_bits"] > 0.0) and (out["lb_p"] <= 0.05)

    # (b) FALSE-POSITIVE on shuffled LA words
    n_fire = 0
    n_sets = N_FALSEPOS_SETS
    for s_i in range(n_sets):
        sh = shuffle_words(la_words_all, random.Random(SEED + 100 + s_i))
        cv = run_cv(sh, N_FOLDS, seed=SEED + 200 + s_i)
        mean_imp = float(np.mean([r["improvement"] for r in cv]))
        mean_p = float(np.mean([r["p"] for r in cv]))
        if mean_imp > 0.0 and mean_p <= 0.05:
            n_fire += 1
    out["false_pos_rate"] = n_fire / n_sets
    out["false_pos_n_sets"] = n_sets
    out["passed"] = out["detect"] and (out["false_pos_rate"] < 0.5)
    return out


def verdict(pc, cv_results, site_results):
    if not pc.get("passed", False):
        return "MACHINERY_UNINFORMATIVE"
    mean_imp = float(np.mean([r["improvement"] for r in cv_results]))
    mean_p = float(np.mean([r["p"] for r in cv_results]))
    global_sig = (mean_imp > 0.0) and (mean_p <= 0.05)
    n_sites = len(site_results)
    n_improving = sum(1 for s, r in site_results.items()
                      if r["improvement"] > 0.0 and r["p"] <= 0.05)
    if n_sites < 3:
        return "SIGN_REDUNDANCY_UNDERPOWERED"
    if not global_sig:
        return "SIGN_SEQUENCE_NEAR_RANDOM"
    if n_improving >= 3:
        return "SIGN_REDUNDANCY_LANGUAGELIKE_HELDOUT"
    return "SIGN_REDUNDANCY_SITE_LOCAL"

# ---------- main ----------
def main():
    corpus = load_corpus()
    la = la_words(corpus)
    # inspect
    n_words = len(la)
    vocab = vocab_of(la)
    mean_len = float(np.mean([len(sg) for _, sg in la]))
    uni_full = train_unigram(la, 0.1, vocab)
    uni_ent = unigram_xent(uni_full, la)
    inspect = {"n_words": n_words, "sign_vocab": len(vocab) - 2,  # minus BOS/EOS
               "mean_word_len": mean_len, "unigram_entropy_bits": uni_ent}

    # POSITIVE CONTROL FIRST
    pc = positive_control(la)

    # GLOBAL CV
    cv = run_cv(la, N_FOLDS, seed=SEED)
    cv_mean_imp = float(np.mean([r["improvement"] for r in cv]))
    cv_mean_p = float(np.mean([r["p"] for r in cv]))
    cv_mx = float(np.mean([r["markov_xent"] for r in cv]))
    cv_ux = float(np.mean([r["unigram_xent"] for r in cv]))

    # SITE-BLOCKED
    sites = run_site_blocked(la)
    n_sites = len(sites)
    n_improving = sum(1 for s, r in sites.items()
                      if r["improvement"] > 0.0 and r["p"] <= 0.05)

    v = verdict(pc, cv, sites)

    summary = {
        "inspect": inspect,
        "positive_control": pc,
        "cv": {"markov_xent_bits_per_sign": cv_mx,
               "unigram_xent_bits_per_sign": cv_ux,
               "improvement_bits": cv_mean_imp,
               "order_shuffle_p": cv_mean_p,
               "sign_vocab": inspect["sign_vocab"],
               "folds": cv},
        "site_blocked": {"n_sites": n_sites, "n_sites_improving": n_improving,
                         "per_site": sites},
        "verdict": v,
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
