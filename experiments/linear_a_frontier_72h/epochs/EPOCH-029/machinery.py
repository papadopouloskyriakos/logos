"""
EPOCH-029 — WORD-INTERNAL SIGN-BIGRAM COLLOCATION STRUCTURE (optimized)
Linear A frontier-72h. L2/L3 positional/combinatorial statistics ONLY.

Frozen rule (see prereg.md):
  NULL = within-word sign shuffle (preserves each word's sign multiset + length).
  structure_score = #{bigrams with obs>=count_threshold and |z|>=3} where z is vs the shuffle null.
  search_adj_p = fraction of >=500 whole-statistic shuffle draws whose structure_score >= observed.
  PC: LB must be sig (search_adj_p<=0.05) AND i.i.d. synthetic-from-LB-unigram must reject <=0.10
      across >=20 corpora.

Optimized: words encoded as padded 2D int arrays grouped by length; within-word shuffle done
via vectorized numpy argsort per row (preserves multiset+length exactly).
"""
import os, sys, json, math, random
from collections import Counter, defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
CORPUS = os.path.join(REPO, "corpus", "silver", "inscriptions_structured.json")

COUNT_THRESHOLD = 5
BIGRAM_DRAWS = 1000
SEARCH_DRAWS = 500
LB_SEARCH_DRAWS = 500
N_SYNTHETIC = 20
SYNTH_REJECT_MAX = 0.10
SITE_MIN_WORDS = 40
SITE_SIG_ALPHA = 0.05
K_TOP = 10
REPL_FRAC_MIN = 0.50

# ---------- data loading ----------
def load_la_words_by_site():
    d = json.load(open(CORPUS))
    by_site = defaultdict(list)
    for ins in d:
        s = ins.get("site", "?")
        for tok in ins.get("stream", []):
            if tok.get("t") == "word":
                sg = tok.get("signs", [])
                if len(sg) >= 2:
                    by_site[s].append(tuple(sg))
    return dict(by_site)

def load_lb_words():
    if REPO not in sys.path:
        sys.path.insert(0, REPO)
    from scripts.cross_script.data import load_b_damos
    seqs, freq, v2g = load_b_damos()
    return [tuple(w) for w in seqs if len(w) >= 2], freq

# ---------- encoded corpus ----------
class Corpus:
    """Words encoded as int ids, grouped by length into 2D padded arrays for vectorized shuffle."""
    def __init__(self, words):
        vs = set()
        for w in words:
            for s in w:
                vs.add(s)
        self.vocab = {s: i for i, s in enumerate(sorted(vs))}
        self.inv = {i: s for s, i in self.vocab.items()}
        self.V = len(self.vocab)
        # group words by length
        by_len = defaultdict(list)
        for w in words:
            if len(w) >= 2:
                by_len[len(w)].append([self.vocab[s] for s in w])
        self.groups = {}  # length -> (2D array (n, L), valid mask for bigrams)
        for L, rows in by_len.items():
            arr = np.array(rows, dtype=np.int32)  # (n, L)
            self.groups[L] = arr
        self.n_words = sum(arr.shape[0] for arr in self.groups.values())

    def observed_bigram_counts(self):
        cnt = np.zeros(self.V * self.V, dtype=np.int64)
        for L, arr in self.groups.items():
            n = arr.shape[0]
            left = arr[:, :-1].reshape(-1).astype(np.int64)
            right = arr[:, 1:].reshape(-1).astype(np.int64)
            pid = left * self.V + right
            cnt += np.bincount(pid, minlength=self.V * self.V)
        return cnt

    def _shuffle_group(self, arr, rng_np):
        """Within-row shuffle preserving multiset: generate random keys per element, argsort per row."""
        n, L = arr.shape
        keys = rng_np.random((n, L))
        order = np.argsort(keys, axis=1)
        return np.take_along_axis(arr, order, axis=1)

    def null_bigram_matrix(self, draws, seed):
        """Return (draws, V*V) int64 matrix of bigram counts under within-word shuffle."""
        rng_np = np.random.default_rng(seed)
        out = np.zeros((draws, self.V * self.V), dtype=np.int64)
        # precompute group shapes
        group_data = [(L, arr) for L, arr in self.groups.items()]
        for d in range(draws):
            cnt = np.zeros(self.V * self.V, dtype=np.int64)
            for L, arr in group_data:
                sh = self._shuffle_group(arr, rng_np)
                n = sh.shape[0]
                left = sh[:, :-1].reshape(-1).astype(np.int64)
                right = sh[:, 1:].reshape(-1).astype(np.int64)
                pid = left * self.V + right
                cnt += np.bincount(pid, minlength=self.V * self.V)
            out[d] = cnt
        return out

def bigram_counts(words):
    c = Counter()
    for w in words:
        for i in range(len(w) - 1):
            c[(w[i], w[i+1])] += 1
    return c

def structure_score(obs_cnt, null_mat, count_threshold=COUNT_THRESHOLD):
    mask = obs_cnt >= count_threshold
    if not mask.any():
        return 0
    idx = np.where(mask)[0]
    sub_obs = obs_cnt[idx].astype(np.float64)
    sub_null = null_mat[:, idx].astype(np.float64)
    mu = sub_null.mean(axis=0)
    var = sub_null.var(axis=0)
    sd = np.sqrt(var); sd = np.where(sd > 0, sd, 1e-9)
    z = (sub_obs - mu) / sd
    return int((np.abs(z) >= 3.0).sum())

def structure_score_with_detail(obs_cnt, null_mat, V, inv, count_threshold=COUNT_THRESHOLD):
    mask = obs_cnt >= count_threshold
    rows = []
    if not mask.any():
        return 0, rows
    idx = np.where(mask)[0]
    sub_obs = obs_cnt[idx].astype(np.float64)
    sub_null = null_mat[:, idx].astype(np.float64)
    mu = sub_null.mean(axis=0)
    var = sub_null.var(axis=0)
    sd = np.sqrt(var); sd = np.where(sd > 0, sd, 1e-9)
    z = (sub_obs - mu) / sd
    ge = (sub_null >= sub_obs[None, :]).sum(axis=0)
    p_over = (1 + ge) / (1 + null_mat.shape[0])
    for j in range(len(idx)):
        i1 = int(idx[j]) // V
        i2 = int(idx[j]) % V
        rows.append(((inv[i1], inv[i2]), int(sub_obs[j]), float(mu[j]), float(sd[j]),
                     float(z[j]), float(p_over[j])))
    score = int((np.abs(z) >= 3.0).sum())
    return score, rows

def search_adjusted_p(corpus, search_draws, bigram_draws=BIGRAM_DRAWS, seed=0,
                      count_threshold=COUNT_THRESHOLD):
    """Search-adjusted p for 'the corpus has more bigram structure than chance'.

    Exchangeability argument (correct & calibrated): under H0 (within-word sign order is random),
    the observed corpus and every within-word-shuffled corpus are exchangeable. We draw ONE pool of
    shuffled bigram-count vectors; the first `bigram_draws` define the per-cell null (mu, sd over the
    FULL V*V matrix); the remaining `search_draws` are pseudo-observed corpora. Each corpus (real
    observed + every test row) is scored IDENTICALLY: structure_score = #{cells with own count>=
    count_threshold and |z|>=3}, where z uses the shared per-cell mu/sd. Using each corpus's OWN
    >=count_threshold mask (its own bigram universe) is essential for exchangeability / calibration.
    p = (1 + #{test_score >= obs_score}) / (1 + n_test).  n_test >= SEARCH_DRAWS (frozen >=500).
    """
    pool_size = bigram_draws + search_draws
    pool = corpus.null_bigram_matrix(pool_size, seed=seed).astype(np.float64)
    null_mat = pool[:bigram_draws]
    test_mat = pool[bigram_draws:bigram_draws + search_draws]
    mu = null_mat.mean(axis=0)
    var = null_mat.var(axis=0)
    sd = np.sqrt(var); sd = np.where(sd > 0, sd, 1e-9)
    obs_cnt = corpus.observed_bigram_counts().astype(np.float64)
    z_obs = (obs_cnt - mu) / sd
    obs_score = int(((np.abs(z_obs) >= 3.0) & (obs_cnt >= count_threshold)).sum())
    # score each test row (its own >=count_threshold mask), vectorized in chunks
    n_test = test_mat.shape[0]
    test_scores = np.empty(n_test, dtype=int)
    chunk = 500
    for s0 in range(0, n_test, chunk):
        sl = slice(s0, min(s0 + chunk, n_test))
        tc = test_mat[sl]
        zt = (tc - mu[None, :]) / sd[None, :]
        test_scores[sl] = ((np.abs(zt) >= 3.0) & (tc >= count_threshold)).sum(axis=1)
    ge = int((test_scores >= obs_score).sum())
    p = (1 + ge) / (1 + n_test)
    return obs_score, p

# ---------- positive control ----------
def lb_positive_control():
    lb_words, lb_freq = load_lb_words()
    corpus = Corpus(lb_words)
    obs_score, p = search_adjusted_p(corpus, LB_SEARCH_DRAWS, BIGRAM_DRAWS, seed=229)
    return lb_words, lb_freq, corpus, obs_score, p

def synthetic_iid_words(n_words, lengths, unigram_pool, rng):
    out = []
    for _ in range(n_words):
        L = rng.choice(lengths)
        if L < 2:
            L = 2
        out.append(tuple(rng.choice(unigram_pool) for _ in range(L)))
    return out

def synthetic_false_positive(lb_words, lb_freq, n_synth=N_SYNTHETIC, seed=1029,
                             search_draws=SEARCH_DRAWS):
    rng = random.Random(seed)
    n_words = len(lb_words)
    lengths = [len(w) for w in lb_words]
    pool = []
    for s, f in lb_freq.items():
        pool.extend([s] * int(f))
    if not pool:
        pool = list(lb_freq.keys())
    rejections = 0
    ps = []
    for i in range(n_synth):
        sw = synthetic_iid_words(n_words, lengths, pool, rng)
        corpus = Corpus(sw)
        _, p = search_adjusted_p(corpus, search_draws, BIGRAM_DRAWS, seed=seed + i * 101)
        ps.append(p)
        if p <= SITE_SIG_ALPHA:
            rejections += 1
    rate = rejections / n_synth
    return rate, ps

# ---------- cross-site ----------
def per_site_analysis(by_site):
    sites = sorted([s for s, w in by_site.items() if len(w) >= SITE_MIN_WORDS],
                   key=lambda s: -len(by_site[s]))
    per_site = {}
    for idx, s in enumerate(sites):
        words = by_site[s]
        corpus = Corpus(words)
        sc, p = search_adjusted_p(corpus, SEARCH_DRAWS, BIGRAM_DRAWS, seed=2900 + idx)
        per_site[s] = {"n": len(words), "structure_score": int(sc), "p": float(p)}
    return sites, per_site

def top_overrep_bigrams(words, k=K_TOP, draws=BIGRAM_DRAWS, seed=0):
    corpus = Corpus(words)
    obs = corpus.observed_bigram_counts()
    null_mat = corpus.null_bigram_matrix(draws, seed=seed)
    score, rows = structure_score_with_detail(obs, null_mat, corpus.V, corpus.inv)
    rows.sort(key=lambda r: -r[4])  # by z desc
    return rows[:k], rows

def heldout_replication(ht_words, other_words, k=K_TOP, draws=BIGRAM_DRAWS, seed_ht=31, seed_ot=32):
    top, _ = top_overrep_bigrams(ht_words, k=k, draws=draws, seed=seed_ht)
    train = [r[0] for r in top]
    rng = random.Random(seed_ot)
    obs_o = Counter()
    for w in other_words:
        for i in range(len(w) - 1):
            obs_o[(w[i], w[i+1])] += 1
    keys = set(train)
    null_counts = defaultdict(list)
    owords_list = list(other_words)
    for _ in range(draws):
        sw = []
        for w in owords_list:
            if len(w) <= 1:
                sw.append(w); continue
            L = list(w); rng.shuffle(L); sw.append(tuple(L))
        sbc = Counter()
        for w in sw:
            for i in range(len(w) - 1):
                sbc[(w[i], w[i+1])] += 1
        for key in keys:
            null_counts[key].append(sbc.get(key, 0))
    replicated = 0
    detail = []
    for b in train:
        o = obs_o.get(b, 0)
        nc = null_counts.get(b, [0])
        ge = sum(1 for x in nc if x >= o)
        p_over = (1 + ge) / (1 + draws)
        rep = (o >= COUNT_THRESHOLD) and (p_over <= SITE_SIG_ALPHA)
        detail.append((b, o, p_over, rep))
        if rep:
            replicated += 1
    frac = replicated / len(train) if train else 0.0
    return len(train), replicated, frac, detail

# ---------- self-check ----------
def _selfcheck():
    rng = random.Random(0)
    words = []
    for _ in range(200):
        words.append(("A", "B", "C"))
    for _ in range(200):
        words.append(("X", "Y", "Z"))
    import string
    for _ in range(100):
        words.append(tuple(rng.choice(string.ascii_uppercase) for _ in range(3)))
    c = Corpus(words)
    obs = c.observed_bigram_counts()
    null = c.null_bigram_matrix(200, seed=1)
    sc = structure_score(obs, null)
    assert sc >= 4, f"selfcheck: expected >=4 structured bigrams, got {sc}"
    iid = [tuple(rng.choice(string.ascii_uppercase) for _ in range(3)) for _ in range(500)]
    c2 = Corpus(iid)
    obs2 = c2.observed_bigram_counts()
    null2 = c2.null_bigram_matrix(200, seed=2)
    sc2 = structure_score(obs2, null2)
    print(f"selfcheck OK: structured corpus score={sc}, iid corpus score={sc2}")

if __name__ == "__main__":
    _selfcheck()
    print("EPOCH-029 machinery self-check passed.")
