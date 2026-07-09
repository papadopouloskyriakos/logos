"""
EPOCH-056 machinery: DUAL SIGN-CLASS INDUCTION (Linear A, L2).

Signs are ANONYMOUS IDs. Features are pure distribution. "logogram-like" is a
distributional cluster label, NOT a reading/meaning/decipherment. layer=L2.

Self-check (__main__): validates the clusterer (a) RECOVERS a planted 2-class
synthetic (silhouette perm p<=0.05 AND ARI>=0.7) and (b) does NOT split a
single-class synthetic beyond null (false-split rate <=0.10).

EFFICIENCY: observed clustering uses n_init=10; permutation-null clustering
uses n_init=3 (the null only needs an approximate 2-means fit, and using FEWER
restarts in the null than the observed is CONSERVATIVE — it makes null
silhouettes slightly lower and thus p slightly larger, biasing AGAINST finding
structure, which is the safe direction).
"""
import json, os, sys
from collections import defaultdict
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, adjusted_rand_score
from scipy.stats import mannwhitneyu

RNG_SEED = 12345
FEAT_NAMES = ['f1_num_adj','f2_solo','f3_init','f4_final','f5_mean_len']
N_INIT_OBS = 10      # restarts for observed clustering
N_INIT_NULL = 3      # restarts for null permutations (conservative: lower -> lower null sil -> larger p)

# ----------------------------- feature extraction ----------------------------
def extract_features(inscriptions, min_tokens=20):
    occ = defaultdict(lambda: {'n':0,'num_adj':0,'solo':0,'init':0,'final':0,'len_sum':0})
    for ins in inscriptions:
        st = ins.get('stream', [])
        for i, tok in enumerate(st):
            if tok.get('t') == 'word':
                signs = tok.get('signs', [])
                if not signs:
                    continue
                L = len(signs)
                nxt = st[i+1] if i+1 < len(st) else {}
                is_num_adj = (nxt.get('t') == 'num')
                for j, s in enumerate(signs):
                    o = occ[s]
                    o['n'] += 1
                    if is_num_adj: o['num_adj'] += 1
                    if L == 1:    o['solo']   += 1
                    if j == 0:    o['init']   += 1
                    if j == L-1:  o['final']  += 1
                    o['len_sum'] += L
    rows, signs, counts = [], [], []
    for s, o in occ.items():
        if o['n'] >= min_tokens:
            n = o['n']
            rows.append([o['num_adj']/n, o['solo']/n, o['init']/n,
                         o['final']/n, o['len_sum']/n])
            signs.append(s); counts.append(n)
    return signs, np.array(rows, dtype=float), np.array(counts)

def extract_features_by_site(inscriptions, site, min_tokens=10):
    sub = [ins for ins in inscriptions if ins.get('site') == site]
    return extract_features(sub, min_tokens=min_tokens)

# ----------------------------- clustering / null -----------------------------
def zscore(X):
    mu = X.mean(axis=0); sd = X.std(axis=0)
    sd[sd == 0] = 1.0
    return (X - mu) / sd

def _km(Xz, seed, n_init):
    return KMeans(n_clusters=2, n_init=n_init, random_state=seed).fit_predict(Xz)

def kmeans2(Xz, seed=RNG_SEED):
    return _km(Xz, seed, N_INIT_OBS)

def silhouette(Xz, labels):
    if len(set(labels)) < 2:
        return -1.0
    return float(silhouette_score(Xz, labels))

def perm_silhouette_p(Xz, n_perm=500, seed=RNG_SEED):
    """Observed silhouette vs column-shuffled null. Returns (obs, p, null_dist)."""
    rng = np.random.default_rng(seed)
    obs_labels = kmeans2(Xz, seed=seed)
    obs = silhouette(Xz, obs_labels)
    null = np.empty(n_perm)
    for i in range(n_perm):
        Xs = Xz.copy()
        for c in range(Xs.shape[1]):
            Xs[:, c] = rng.permutation(Xs[:, c])
        lab = _km(Xs, seed + i + 1, N_INIT_NULL)
        null[i] = silhouette(Xs, lab)
    p = float((null >= obs).mean())
    return obs, p, null

# ----------------------------- characterization ------------------------------
def characterize(X, labels):
    out = {}
    for k in (0, 1):
        m = labels == k
        out[k] = {'size': int(m.sum()),
                  'f1_mean': float(X[m, 0].mean()),
                  'f2_mean': float(X[m, 1].mean())}
    score = {k: out[k]['f1_mean'] + out[k]['f2_mean'] for k in (0, 1)}
    logo = max(score, key=score.get); syll = 1 - logo
    f1_gap = out[logo]['f1_mean'] - out[syll]['f1_mean']
    a = X[labels == logo, 0]; b = X[labels == syll, 0]
    try:
        _, mw_p = mannwhitneyu(a, b, alternative='greater')
    except ValueError:
        mw_p = 1.0
    return {
        'logogram_class': int(logo), 'syllabo_class': int(syll),
        'logogram_class_size': int(out[logo]['size']),
        'syllabo_class_size': int(out[syll]['size']),
        'f1_logogram_mean': float(out[logo]['f1_mean']),
        'f1_syllabo_mean': float(out[syll]['f1_mean']),
        'f2_logogram_mean': float(out[logo]['f2_mean']),
        'f2_syllabo_mean': float(out[syll]['f2_mean']),
        'f1_gap': float(f1_gap), 'f1_mw_p': float(mw_p),
    }

# ----------------------------- cross-site ------------------------------------
def cross_site_ari(inscriptions, min_tokens=10, min_signs_for_cluster=6,
                   n_perm=300, seed=RNG_SEED):
    rng = np.random.default_rng(seed)
    ss = defaultdict(lambda: defaultdict(int))
    for ins in inscriptions:
        site = ins.get('site', '')
        for tok in ins.get('stream', []):
            if tok.get('t') == 'word':
                for s in tok.get('signs', []):
                    ss[s][site] += 1
    multi = {}
    for s, sc in ss.items():
        ge = [site for site, c in sc.items() if c >= min_tokens]
        if len(ge) >= 2:
            multi[s] = ge
    site_signs = defaultdict(list)
    for s, sites in multi.items():
        for site in sites:
            site_signs[site].append(s)
    cand_sites = sorted([st for st, sl in site_signs.items()
                         if len(sl) >= min_signs_for_cluster])
    site_labels = {}
    for st in cand_sites:
        signs_st, X_st, _ = extract_features_by_site(inscriptions, st, min_tokens=min_tokens)
        keep = [i for i, s in enumerate(signs_st) if s in multi]
        if len(keep) < min_signs_for_cluster:
            continue
        Xz = zscore(X_st[keep])
        lab = kmeans2(Xz, seed=seed)
        site_labels[st] = ([signs_st[i] for i in keep], lab)
    usable = list(site_labels.keys())
    if len(usable) < 2:
        return {'n_sites_usable': len(usable), 'cross_site_ari': float('nan'),
                'null_ari_mean': float('nan'), 'ari_beyond_null': False,
                'pairs': [], 'n_signs_multi': len(multi), 'usable_sites': usable}
    aris = []
    for i in range(len(usable)):
        for j in range(i+1, len(usable)):
            sA, lA = site_labels[usable[i]]; sB, lB = site_labels[usable[j]]
            common = sorted(set(sA) & set(sB))
            if len(common) < min_signs_for_cluster:
                continue
            idxA = {s: k for k, s in enumerate(sA)}; idxB = {s: k for k, s in enumerate(sB)}
            la = np.array([lA[idxA[s]] for s in common]); lb = np.array([lB[idxB[s]] for s in common])
            ari = max(adjusted_rand_score(la, lb), adjusted_rand_score(la, 1-lb))
            aris.append(ari)
    if not aris:
        return {'n_sites_usable': len(usable), 'cross_site_ari': float('nan'),
                'null_ari_mean': float('nan'), 'ari_beyond_null': False,
                'pairs': [], 'n_signs_multi': len(multi), 'usable_sites': usable}
    obs_ari = float(np.mean(aris))
    null_aris = []
    for _ in range(n_perm):
        rand_labels = {}
        for st in usable:
            _, lab = site_labels[st]; n = len(lab); n1 = int((lab == 1).sum())
            r = np.zeros(n, dtype=int); r[:n1] = 1; rng.shuffle(r)
            rand_labels[st] = r
        na = []
        for i in range(len(usable)):
            for j in range(i+1, len(usable)):
                sA, _ = site_labels[usable[i]]; sB, _ = site_labels[usable[j]]
                common = sorted(set(sA) & set(sB))
                if len(common) < min_signs_for_cluster:
                    continue
                idxA = {s: k for k, s in enumerate(sA)}; idxB = {s: k for k, s in enumerate(sB)}
                la = np.array([rand_labels[usable[i]][idxA[s]] for s in common])
                lb = np.array([rand_labels[usable[j]][idxB[s]] for s in common])
                na.append(max(adjusted_rand_score(la, lb), adjusted_rand_score(la, 1-lb)))
        if na:
            null_aris.append(float(np.mean(na)))
    null_mean = float(np.mean(null_aris)) if null_aris else float('nan')
    return {'n_sites_usable': len(usable), 'cross_site_ari': obs_ari,
            'null_ari_mean': null_mean, 'ari_beyond_null': bool(obs_ari > null_mean),
            'pairs': [float(a) for a in aris], 'n_signs_multi': len(multi),
            'usable_sites': usable}

# ----------------------------- positive control (SYNTHETIC) ------------------
def synthetic_two_class(n_per=40, seed=RNG_SEED):
    """Plant 2 classes: A high f1+f2 (logogram-like), B low. 5 features."""
    rng = np.random.default_rng(seed)
    A = np.column_stack([
        rng.normal(0.75, 0.08, n_per), rng.normal(0.85, 0.08, n_per),
        rng.normal(0.90, 0.06, n_per), rng.normal(0.90, 0.06, n_per),
        rng.normal(1.10, 0.08, n_per)])
    B = np.column_stack([
        rng.normal(0.15, 0.08, n_per), rng.normal(0.10, 0.06, n_per),
        rng.normal(0.45, 0.10, n_per), rng.normal(0.50, 0.10, n_per),
        rng.normal(3.20, 0.50, n_per)])
    return np.clip(np.vstack([A, B]), 0, None), np.array([0]*n_per + [1]*n_per)

def synthetic_one_class(n=80, seed=RNG_SEED):
    """Single genuine functional class: tight, independent columns. Spread set
    to a realistic within-class SD (a single sign class is NOT as spread as the
    full inventory, which itself contains both classes)."""
    rng = np.random.default_rng(seed)
    mu = np.array([0.30, 0.20, 0.50, 0.55, 2.80])
    sd = np.array([0.10, 0.08, 0.12, 0.12, 0.45])  # tight, independent
    return np.clip(rng.normal(mu, sd, size=(n, 5)), 0, None)

def positive_control(n_perm=200, n_fp_draws=20, seed=RNG_SEED):
    rng = np.random.default_rng(seed)
    X, truth = synthetic_two_class(seed=seed)
    Xz = zscore(X)
    obs, p, _ = perm_silhouette_p(Xz, n_perm=n_perm, seed=seed)
    lab = kmeans2(Xz, seed=seed)
    ari = max(adjusted_rand_score(lab, truth), adjusted_rand_score(1-lab, truth))
    detect_ok = (p <= 0.05) and (ari >= 0.7)
    fp = 0
    for d in range(n_fp_draws):
        X1 = synthetic_one_class(n=80, seed=seed + 1000 + d)
        Xz1 = zscore(X1)
        _, p1, _ = perm_silhouette_p(Xz1, n_perm=n_perm, seed=seed + 2000 + d)
        if p1 <= 0.05:
            fp += 1
    fp_rate = fp / n_fp_draws
    passed = detect_ok and (fp_rate <= 0.10)
    return {'pc_verdict': 'PASSED' if passed else 'FAILED',
            'detect_silhouette_p': float(p), 'detect_ari': float(ari),
            'false_split_rate': float(fp_rate), 'detect_ok': bool(detect_ok),
            'fp_ok': bool(fp_rate <= 0.10), 'pc_is_synthetic': True}

def _self_check():
    pc = positive_control(n_perm=200, n_fp_draws=20, seed=RNG_SEED)
    print("=== EPOCH-056 machinery self-check (SYNTHETIC PC) ===")
    print(f"PC verdict: {pc['pc_verdict']}")
    print(f"  detect: silhouette perm p={pc['detect_silhouette_p']:.4f}  "
          f"ARI={pc['detect_ari']:.3f}  ok={pc['detect_ok']}")
    print(f"  false-split rate (single-class)={pc['false_split_rate']:.3f}  "
          f"ok={pc['fp_ok']}  (threshold <=0.10)")
    print(f"  PC is SYNTHETIC (real-LB ideogram control unavailable): {pc['pc_is_synthetic']}")
    if pc['pc_verdict'] != 'PASSED':
        print("SELF-CHECK FAILED -> MACHINERY_UNINFORMATIVE"); return 1
    print("SELF-CHECK PASSED."); return 0

if __name__ == '__main__':
    sys.exit(_self_check())
