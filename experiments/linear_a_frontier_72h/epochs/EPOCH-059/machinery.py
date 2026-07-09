"""
EPOCH-059 machinery: CROSS-SITE SUB-LEXICAL SHARING (sign bigrams beyond a unigram-preserving null).

Layer L2: pure distributional n-gram statistics. Anonymous sign IDs only.

Frozen null (the crux): for each site, regenerate its bigram multiset by sampling the SAME
number of sign-pairs, each pair = two INDEPENDENT draws from THAT SITE'S OWN unigram
(single-sign) frequency distribution. This preserves per-site sign frequencies but destroys
any sequence-specific structure. Therefore any detected cross-site bigram sharing is BEYOND
shared signs.

Statistic S = number of distinct bigram TYPES that recur across >=k of the qualifying sites.
"""
import json
import random
from collections import Counter, defaultdict
from itertools import combinations


# ---------- data extraction ----------

def extract_site_bigrams(inscriptions, ngram=2):
    """Return dict site -> list of word-internal ngram tuples (ngram=2 bigrams, 3 trigrams)."""
    site_ngrams = defaultdict(list)
    for ins in inscriptions:
        site = ins.get("site", "") or "UNKNOWN"
        for tok in ins.get("stream", []):
            if not isinstance(tok, dict):
                continue
            if tok.get("t") != "word":
                continue
            signs = [s for s in tok.get("signs", []) if s]
            if len(signs) >= ngram:
                for i in range(len(signs) - ngram + 1):
                    site_ngrams[site].append(tuple(signs[i:i + ngram]))
    return site_ngrams


def extract_site_unigrams(inscriptions):
    """Return dict site -> Counter of single signs (over the same word tokens)."""
    site_uni = defaultdict(Counter)
    for ins in inscriptions:
        site = ins.get("site", "") or "UNKNOWN"
        for tok in ins.get("stream", []):
            if not isinstance(tok, dict):
                continue
            if tok.get("t") != "word":
                continue
            for s in tok.get("signs", []):
                if s:
                    site_uni[site][s] += 1
    return site_uni


# ---------- statistics ----------

def statistic_S(site_ngram_lists, sites, k=3):
    """Number of distinct ngram TYPES recurring across >=k of the given sites."""
    site_sets = {s: set(site_ngram_lists[s]) for s in sites}
    ng_sites = defaultdict(set)
    for s in sites:
        for ng in site_sets[s]:
            ng_sites[ng].add(s)
    return sum(1 for ng, ss in ng_sites.items() if len(ss) >= k)


def mean_pairwise_jaccard(site_ngram_lists, sites):
    site_sets = {s: set(site_ngram_lists[s]) for s in sites}
    js = []
    for a, b in combinations(sorted(sites), 2):
        A, B = site_sets[a], site_sets[b]
        u = len(A | B)
        if u > 0:
            js.append(len(A & B) / u)
    return (sum(js) / len(js)) if js else 0.0, js


# ---------- unigram-preserving null ----------

def unigram_null_ngrams(site_uni_counter, n_pairs, ngram=2, rng=None):
    """Sample n_pairs ngrams; each ngram = ngram INDEPENDENT draws from the site's own unigram dist."""
    if rng is None:
        rng = random
    signs, weights = zip(*site_uni_counter.items())
    total = sum(weights)
    probs = [w / total for w in weights]
    out = []
    for _ in range(n_pairs):
        ng = tuple(rng.choices(signs, weights=probs, k=ngram))
        out.append(ng)
    return out


def null_distribution_S(site_unigrams, site_n_pairs, sites, n_realizations=500,
                        k=3, ngram=2, seed=0):
    """Return list of S values under the unigram-preserving null."""
    rng = random.Random(seed)
    S_null = []
    for _ in range(n_realizations):
        null_lists = {}
        for s in sites:
            null_lists[s] = unigram_null_ngrams(site_unigrams[s], site_n_pairs[s],
                                                ngram=ngram, rng=rng)
        S_null.append(statistic_S(null_lists, sites, k=k))
    return S_null


def permutation_p(obs_S, S_null):
    ge = sum(1 for x in S_null if x >= obs_S)
    return ge / len(S_null)


# ---------- self-check (synthetic) ----------

def self_check():
    """Validate the unigram-null generator + S statistic on a synthetic.

    Build 3 sites that SHARE a planted set of bigrams on top of shared unigrams, using a
    realistic alphabet size (40 signs) so the null background is not artificially inflated.
    The observed S should EXCEED the unigram-null S (perm p<=0.05), since the null destroys
    the planted sequence structure while preserving unigrams.
    """
    rng = random.Random(42)
    alphabet = [f"L{i}" for i in range(40)]  # realistic alphabet size
    uni = Counter({a: 5 for a in alphabet})
    planted = {("L0", "L1"), ("L2", "L3"), ("L4", "L5"), ("L6", "L7"), ("L8", "L9")}
    sites = ["A", "B", "C"]
    site_lists = {}
    for s in sites:
        lst = []
        for _ in range(60):  # strong planting of shared sub-lexical inventory
            lst.append(list(planted)[rng.randrange(len(planted))])
        signs, weights = zip(*uni.items())
        for _ in range(140):
            lst.append(tuple(rng.choices(signs, weights=weights, k=2)))
        site_lists[s] = lst
    obs = statistic_S(site_lists, sites, k=3)
    site_n_pairs = {s: len(site_lists[s]) for s in sites}
    S_null = null_distribution_S({s: uni for s in sites}, site_n_pairs, sites,
                                 n_realizations=300, k=3, ngram=2, seed=1)
    null_mean = sum(S_null) / len(S_null)
    p = permutation_p(obs, S_null)
    ok = (obs > null_mean) and (p <= 0.05)
    print(f"[self-check] obs_S={obs}  null_mean={null_mean:.2f}  perm_p={p}  ratio={obs/null_mean:.2f}")
    print(f"[self-check] DETECT planted sharing: {'OK' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    ok = self_check()
    print("SELF_CHECK:", "PASS" if ok else "FAIL")
