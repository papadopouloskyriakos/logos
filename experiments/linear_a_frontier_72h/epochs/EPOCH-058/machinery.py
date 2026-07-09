"""
EPOCH-058 machinery: unsupervised document typology (L2, structural counts only).

Features (log1p then z-score): x1 n_content, x2 num_density, x3 div_density,
x4 nl_density, x5 mean_word_len.

Methods:
  - global_kmeans(X): k in {2,3,4} by silhouette; returns chosen k, labels, sil.
  - silhouette_perm_p(X, k, observed, n_perm): per-column shuffle null.
  - support_ari(labels, support): ARI vs support label.
  - cross_site_train_apply(...): train k=2 on site A, apply to site B, ARI vs B's own.
  - positive_control_detect / positive_control_falsepos.

NO sign values, NO readings. Structural counts only. L2.
"""
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, adjusted_rand_score
from sklearn.preprocessing import StandardScaler

RNG_MASTER = 12345

def extract_features(ins):
    """Return (x1..x5) or None if <2 content tokens."""
    s = ins.get("stream", [])
    n_word = n_num = n_div = n_nl = 0
    word_lens = []
    for tok in s:
        if not isinstance(tok, dict):
            continue
        t = tok.get("t")
        if t == "word":
            n_word += 1
            word_lens.append(len(tok.get("signs", [])))
        elif t == "num":
            n_num += 1
        elif t == "div":
            n_div += 1
        elif t == "nl":
            n_nl += 1
    n_content = n_word + n_num
    if n_content < 2:
        return None
    x1 = n_content
    x2 = n_num / n_content
    x3 = n_div / n_content
    x4 = n_nl / n_content
    x5 = float(np.mean(word_lens)) if word_lens else 0.0
    return np.array([x1, x2, x3, x4, x5], dtype=float)

def transform(X):
    """log1p then z-score (standardize)."""
    Xl = np.log1p(np.maximum(X, 0.0))
    return StandardScaler().fit_transform(Xl)

def _kmeans(X, k, seed):
    km = KMeans(n_clusters=k, n_init=10, random_state=seed)
    return km.fit_predict(X), km

def global_kmeans(X, seed=RNG_MASTER):
    """k in {2,3,4} by silhouette. Returns (chosen_k, labels, silhouette, all_sils)."""
    best = None
    all_sils = {}
    for k in (2, 3, 4):
        if len(X) <= k:
            continue
        labels, _ = _kmeans(X, k, seed)
        sil = float(silhouette_score(X, labels))
        all_sils[k] = sil
        if best is None or sil > best[2]:
            best = (k, labels, sil)
    return best[0], best[1], best[2], all_sils

def silhouette_perm_p(X, k, observed, n_perm=500, seed=RNG_MASTER):
    """Per-column shuffle null: destroys joint structure, preserves marginals."""
    rng = np.random.default_rng(seed)
    n, d = X.shape
    ge = 0
    null_sils = np.empty(n_perm)
    for i in range(n_perm):
        Xs = np.empty_like(X)
        for j in range(d):
            Xs[:, j] = rng.permutation(X[:, j])
        labels, _ = _kmeans(Xs, k, seed + i)
        if len(np.unique(labels)) < 2:
            null_sils[i] = -1.0
        else:
            null_sils[i] = silhouette_score(Xs, labels)
        if null_sils[i] >= observed:
            ge += 1
    p = (ge + 1) / (n_perm + 1)
    return p, null_sils

def support_ari(labels, support):
    return float(adjusted_rand_score(labels, support))

def cross_site_train_apply(XA, XB, n_perm=200, seed=RNG_MASTER):
    """Train k=2 on site A, apply to site B (nearest centroid), compare to B's own
    induced k=2 labels via ARI. Null: permute B's predicted labels."""
    rng = np.random.default_rng(seed)
    labelsA, kmA = _kmeans(XA, 2, seed)
    labelsB, kmB = _kmeans(XB, 2, seed + 1)
    predB = kmA.predict(XB)
    ari = float(adjusted_rand_score(predB, labelsB))
    nulls = np.empty(n_perm)
    for i in range(n_perm):
        perm = rng.permutation(predB)
        nulls[i] = adjusted_rand_score(perm, labelsB)
    return ari, float(np.mean(nulls)), nulls

# ---------------- Synthetic generators (per-feature noise) ----------------

# Per-feature noise std (realistic: counts noisier than densities)
_NOISE = np.array([1.0, 0.05, 0.05, 0.10, 0.20])

def _synth_three_types(n_per=60, seed=RNG_MASTER):
    """3 distinct structural-feature means (well-separated doc types)."""
    rng = np.random.default_rng(seed)
    centers = np.array([
        [3.0,  0.05, 0.05, 0.2, 1.4],   # short, few numerals, few dividers
        [12.0, 0.45, 0.10, 0.7, 2.0],   # long, numeral-heavy
        [6.0,  0.10, 0.60, 1.2, 3.0],   # divider/line-break heavy, long words
    ])
    X = np.vstack([c + _NOISE * rng.standard_normal((n_per, 5)) for c in centers])
    X = np.maximum(X, 0.0)
    y = np.concatenate([np.full(n_per, i) for i in range(3)])
    return X, y

def _synth_one_type(n=180, seed=RNG_MASTER):
    rng = np.random.default_rng(seed)
    c = np.array([7.0, 0.3, 0.15, 0.6, 2.0])
    X = np.maximum(c + _NOISE * rng.standard_normal((n, 5)), 0.0)
    return X

# ---------------- Positive controls ----------------

def positive_control_detect(seed=RNG_MASTER, n_perm=200):
    X, y = _synth_three_types(seed=seed)
    Xt = transform(X)
    k, labels, sil, _ = global_kmeans(Xt, seed=seed)
    labels3, _ = _kmeans(Xt, 3, seed)
    ari = float(adjusted_rand_score(labels3, y))
    p, _ = silhouette_perm_p(Xt, 3, sil, n_perm=n_perm, seed=seed + 7)
    return {"k_chosen": k, "silhouette": sil, "perm_p": p, "ari_vs_planted": ari}

def positive_control_falsepos(n_draws=20, seed=RNG_MASTER, n_perm=100):
    """Single-type synthetic; spurious 'significant structure' rate."""
    spur = 0
    for d in range(n_draws):
        s = seed + 100 + d
        X = _synth_one_type(n=180, seed=s)
        Xt = transform(X)
        k, labels, sil, _ = global_kmeans(Xt, seed=s)
        p, _ = silhouette_perm_p(Xt, k, sil, n_perm=n_perm, seed=s + 7)
        if p <= 0.05:
            spur += 1
    return spur / n_draws

def run_positive_control(seed=RNG_MASTER):
    det = positive_control_detect(seed=seed, n_perm=200)
    fp = positive_control_falsepos(n_draws=20, seed=seed, n_perm=100)
    passed = (det["perm_p"] <= 0.05 and det["ari_vs_planted"] >= 0.6 and fp <= 0.10)
    return {
        "pc_verdict": "PASSED" if passed else "FAILED",
        "detect_perm_p": det["perm_p"],
        "detect_ari": det["ari_vs_planted"],
        "detect_silhouette": det["silhouette"],
        "false_split_rate": fp,
    }

# ---------------- Self-check ----------------

def self_check():
    """Validate clusterer recovers a planted 3-type synthetic and does NOT split a
    single-type one (silhouette of single-type should be low)."""
    det = positive_control_detect(seed=999, n_perm=100)
    X1 = _synth_one_type(n=180, seed=999)
    Xt1 = transform(X1)
    k1, lab1, sil1, _ = global_kmeans(Xt1, seed=999)
    ok_detect = det["ari_vs_planted"] >= 0.6
    ok_nosplit = sil1 < 0.5
    return {
        "detect_ari": det["ari_vs_planted"],
        "detect_ok": ok_detect,
        "single_type_silhouette": sil1,
        "single_type_ok": ok_nosplit,
        "self_check_ok": ok_detect and ok_nosplit,
    }

if __name__ == "__main__":
    sc = self_check()
    print("SELF-CHECK:", sc)
    assert sc["self_check_ok"], "MACHINERY SELF-CHECK FAILED"
    print("self-check OK")
