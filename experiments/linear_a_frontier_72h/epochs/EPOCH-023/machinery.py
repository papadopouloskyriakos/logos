"""EPOCH-023 core machinery: within-word permutation null for sign-initial incidence."""
import numpy as np
from collections import Counter

def a_initial_count(words, sign):
    """Count words whose first sign == sign."""
    c = 0
    for w in words:
        if w and w[0] == sign:
            c += 1
    return c

def permutation_null(words, sign, n_draws=1000, seed=0):
    """Within-word permutation null for sign-initial count.

    For each draw, independently permute the sign order WITHIN each word (uniform
    random permutation of that word's own signs), then recompute sign-initial count.
    Preserves each partition's sign multiset and word lengths exactly.
    Returns (observed, null_counts_array, p_one_sided).
    """
    rng = np.random.default_rng(seed)
    observed = a_initial_count(words, sign)
    # Pre-extract word arrays for speed
    word_lists = [list(w) for w in words if len(w) > 0]
    null_counts = np.empty(n_draws, dtype=np.int64)
    n_words = len(word_lists)
    for d in range(n_draws):
        c = 0
        for w in word_lists:
            L = len(w)
            if L == 1:
                if w[0] == sign:
                    c += 1
                continue
            # uniform random permutation of this word's signs
            perm = rng.permutation(L)
            if w[perm[0]] == sign:
                c += 1
        null_counts[d] = c
    p = (1 + int(np.sum(null_counts >= observed))) / (1 + n_draws)
    null_mean = float(null_counts.mean())
    return observed, null_counts, p, null_mean

def permutation_null_fast(words, sign, n_draws=1000, seed=0):
    """Vectorized version: for each word, the probability its first permuted sign
    is `sign` equals (#sign in word)/len(word). The COUNT over words is the sum of
    Bernoulli indicators, but they are independent across words under per-word
    permutation. We can sample each word's indicator directly: first permuted sign
    is uniformly one of the word's signs, so P(first==sign) = count_sign/L.
    Equivalent in distribution to the explicit permutation. Much faster."""
    rng = np.random.default_rng(seed)
    observed = a_initial_count(words, sign)
    probs = []
    for w in words:
        L = len(w)
        if L == 0:
            continue
        k = w.count(sign)
        probs.append(k / L)
    probs = np.array(probs)
    # each draw: for each word, indicator ~ Bernoulli(p); sum
    # sample matrix (n_draws, n_words)
    R = rng.random((n_draws, probs.shape[0]))
    indicators = (R < probs[None, :]).astype(np.int64)
    null_counts = indicators.sum(axis=1)
    p = (1 + int(np.sum(null_counts >= observed))) / (1 + n_draws)
    return observed, null_counts, p, float(null_counts.mean())

if __name__ == "__main__":
    # self-check: fast vs explicit on a small sample
    import json
    d = json.load(open('corpus/silver/inscriptions_structured.json'))
    words = []
    for ins in d:
        for tok in ins.get('stream', []):
            if tok.get('t') == 'word':
                sg = tok.get('signs', [])
                if len(sg) >= 2:
                    words.append(sg)
    sub = words[:200]
    o1, nc1, p1, m1 = permutation_null(sub, 'A', 200, seed=1)
    o2, nc2, p2, m2 = permutation_null_fast(sub, 'A', 200, seed=1)
    print('explicit:', o1, m1, p1)
    print('fast    :', o2, m2, p2)
    print('null mean close:', abs(m1 - m2) < 1.0)
