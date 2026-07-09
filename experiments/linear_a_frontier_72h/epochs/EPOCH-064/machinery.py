#!/usr/bin/env python3
"""EPOCH-064 machinery: word-initial vs word-final positional entropy asymmetry.

Anonymous sign IDs only. Positional entropy only. Within-word position-shuffle null.
No phonetic value, no reading, no meaning.
"""
import json, math, hashlib, random
from collections import Counter


def shannon_entropy(counter, n):
    h = 0.0
    for c in counter.values():
        if c <= 0:
            continue
        p = c / n
        h -= p * math.log2(p)
    return h


def A_of_words(words):
    """A = H(final) - H(initial). words = list of sign-lists (each len>=2)."""
    if not words:
        return 0.0, 0.0, 0.0
    init = Counter(w[0] for w in words)
    fin = Counter(w[-1] for w in words)
    n = len(words)
    Hi = shannon_entropy(init, n)
    Hf = shannon_entropy(fin, n)
    return Hf - Hi, Hi, Hf


def within_word_shuffle_A(words, rng):
    """Permute sign order WITHIN each word (uniform permutation of the sign list),
    then recompute A. Preserves each word's sign multiset + word-length distribution;
    makes initial/final exchangeable (E[A]=0)."""
    shuffled = []
    for w in words:
        if len(w) <= 1:
            shuffled.append(w)
            continue
        perm = list(w)
        rng.shuffle(perm)  # uniform permutation (Fisher-Yates)
        shuffled.append(perm)
    A, _, _ = A_of_words(shuffled)
    return A


def permutation_test(words, n_shuffles=2000, seed=12345, alt="initial"):
    """alt='initial' -> one-sided p = frac(null A >= obs A) (initial-concentration).
    Returns obs A, null mean, null list, perm_p (initial), reversed_p (final)."""
    rng = random.Random(seed)
    obs_A, _, _ = A_of_words(words)
    null = [within_word_shuffle_A(words, rng) for _ in range(n_shuffles)]
    null_mean = sum(null) / len(null)
    ge = sum(1 for a in null if a >= obs_A)
    le = sum(1 for a in null if a <= obs_A)
    perm_p = (ge + 1) / (n_shuffles + 1)        # initial-concentration (A large positive)
    reversed_p = (le + 1) / (n_shuffles + 1)    # final-concentration (A large negative)
    return {
        "A_obs": obs_A,
        "A_null_mean": null_mean,
        "perm_p": perm_p,
        "reversed_p": reversed_p,
        "n_shuffles": n_shuffles,
    }


# ---------------- Positive controls (synthetic) ----------------

def make_prefix_words(n_words=400, n_init_types=4, n_final_types=40, seed=1):
    """DETECT-PREFIX: restricted initial inventory + diverse final signs -> A>0 expected."""
    rng = random.Random(seed)
    init_pool = [f"I{i}" for i in range(n_init_types)]
    final_pool = [f"F{i}" for i in range(n_final_types)]
    words = []
    for _ in range(n_words):
        L = rng.randint(2, 4)
        mid = [f"M{rng.randint(0,30)}" for _ in range(L - 2)]
        words.append([rng.choice(init_pool)] + mid + [rng.choice(final_pool)])
    return words


def make_suffix_words(n_words=400, n_init_types=40, n_final_types=4, seed=2):
    """DETECT-SUFFIX: restricted FINAL inventory -> A<0 expected (reversed direction)."""
    rng = random.Random(seed)
    init_pool = [f"I{i}" for i in range(n_init_types)]
    final_pool = [f"F{i}" for i in range(n_final_types)]
    words = []
    for _ in range(n_words):
        L = rng.randint(2, 4)
        mid = [f"M{rng.randint(0,30)}" for _ in range(L - 2)]
        words.append([rng.choice(init_pool)] + mid + [rng.choice(final_pool)])
    return words


def make_symmetric_words(n_words=400, n_types=40, seed=3):
    """FALSE-POSITIVE: initial & final drawn from SAME distribution -> A not flagged."""
    rng = random.Random(seed)
    pool = [f"S{i}" for i in range(n_types)]
    words = []
    for _ in range(n_words):
        L = rng.randint(2, 4)
        mid = [rng.choice(pool) for _ in range(L - 2)]
        words.append([rng.choice(pool)] + mid + [rng.choice(pool)])
    return words


def run_positive_control(n_shuffles=1000):
    """Three arms. Returns dict with pc_verdict and details."""
    # (a) DETECT-PREFIX
    pw = make_prefix_words(seed=11)
    pr = permutation_test(pw, n_shuffles=n_shuffles, seed=101)
    detect_prefix_ok = (pr["A_obs"] > 0 and pr["perm_p"] <= 0.05)

    # (b) DETECT-SUFFIX (direction check): expect A<0 and reversed_p<=0.05, perm_p>0.05
    sw = make_suffix_words(seed=22)
    sr = permutation_test(sw, n_shuffles=n_shuffles, seed=102)
    detect_suffix_A_sign = "neg" if sr["A_obs"] < 0 else "pos"
    detect_suffix_ok = (sr["A_obs"] < 0 and sr["reversed_p"] <= 0.05 and sr["perm_p"] > 0.05)

    # (c) FALSE-POSITIVE: rejection rate across >=20 draws must be <=0.10
    rejections = 0
    n_draws = 30
    for k in range(n_draws):
        sym = make_symmetric_words(seed=1000 + k)
        res = permutation_test(sym, n_shuffles=n_shuffles, seed=2000 + k)
        if res["perm_p"] <= 0.05:   # flagged as initial-concentrated (false positive)
            rejections += 1
    false_pos_rate = rejections / n_draws
    false_pos_ok = (false_pos_rate <= 0.10)

    passed = detect_prefix_ok and detect_suffix_ok and false_pos_ok
    return {
        "pc_verdict": "PASSED" if passed else "FAILED",
        "detect_prefix_p": pr["perm_p"],
        "detect_prefix_A": pr["A_obs"],
        "detect_prefix_ok": detect_prefix_ok,
        "detect_suffix_A_sign": detect_suffix_A_sign,
        "detect_suffix_A": sr["A_obs"],
        "detect_suffix_reversed_p": sr["reversed_p"],
        "detect_suffix_perm_p": sr["perm_p"],
        "detect_suffix_ok": detect_suffix_ok,
        "false_pos_rate": false_pos_rate,
        "false_pos_ok": false_pos_ok,
        "n_draws_false_pos": n_draws,
        "pc_is_synthetic": True,
    }


# ---------------- Self-check ----------------

def self_check():
    """Validate within-word permutation null on a symmetric synthetic: null-mean(A) ~= 0."""
    rng = random.Random(7)
    # symmetric words -> true A should be ~0 and null mean ~0
    sym = make_symmetric_words(n_words=600, n_types=30, seed=99)
    obs, Hi, Hf = A_of_words(sym)
    nulls = [within_word_shuffle_A(sym, rng) for _ in range(2000)]
    nm = sum(nulls) / len(nulls)
    ok = abs(nm) < 0.05
    print(f"[self-check] symmetric obs A={obs:+.4f} null_mean={nm:+.4f} -> null_mean~=0: {ok}")
    # also confirm null preserves sign multiset per word (by construction shuffle does)
    return ok and abs(obs) < 0.10


if __name__ == "__main__":
    print("=== EPOCH-064 machinery self-check ===")
    sc = self_check()
    print(f"self_check_passed={sc}")
    print()
    print("=== Positive control (synthetic) ===")
    pc = run_positive_control(n_shuffles=1000)
    for k, v in pc.items():
        print(f"  {k}: {v}")
