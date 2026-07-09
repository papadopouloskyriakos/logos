"""Evaluation metrics for morphogenesis recovery (blinded LB, then LA).

Recovery task: cluster the emergent activator pattern u(inf) (and unstable-eigenmode span) into k anonymous classes,
then score against held-out truth labels (vowel / consonant / role). Cluster->label alignment by Hungarian matching.
All metrics are computed identically for the model and every control; k is fixed by the same frozen rule for all.
"""
import numpy as np
from collections import Counter


def _contingency(labels_true, labels_pred):
    ut = sorted(set(labels_true)); up = sorted(set(labels_pred))
    ti = {l: i for i, l in enumerate(ut)}; pi = {l: i for i, l in enumerate(up)}
    C = np.zeros((len(ut), len(up)))
    for a, b in zip(labels_true, labels_pred):
        C[ti[a], pi[b]] += 1
    return C, ut, up


def ari(labels_true, labels_pred):
    C, _, _ = _contingency(labels_true, labels_pred)
    from math import comb
    sum_comb = sum(comb(int(n), 2) for n in C.flatten())
    a = C.sum(1); b = C.sum(0)
    sa = sum(comb(int(x), 2) for x in a); sb = sum(comb(int(x), 2) for x in b)
    n = C.sum(); tot = comb(int(n), 2)
    exp = sa * sb / tot if tot else 0
    mx = 0.5 * (sa + sb)
    return float((sum_comb - exp) / (mx - exp)) if (mx - exp) else 0.0


def nmi(labels_true, labels_pred):
    C, _, _ = _contingency(labels_true, labels_pred)
    n = C.sum()
    if n == 0:
        return 0.0
    Pxy = C / n; Px = Pxy.sum(1); Py = Pxy.sum(0)
    with np.errstate(divide="ignore", invalid="ignore"):
        mi = np.nansum(Pxy * np.log((Pxy + 1e-12) / (np.outer(Px, Py) + 1e-12)))
        hx = -np.nansum(Px * np.log(Px + 1e-12)); hy = -np.nansum(Py * np.log(Py + 1e-12))
    denom = np.sqrt(hx * hy)
    return float(mi / denom) if denom > 0 else 0.0


def hungarian_macro_f1(labels_true, labels_pred):
    """Align clusters to truth labels (greedy on the contingency table) and compute macro-F1."""
    C, ut, up = _contingency(labels_true, labels_pred)
    # greedy assignment cluster->label maximizing overlap
    assign = {}
    Cc = C.copy()
    for _ in range(min(len(ut), len(up))):
        i, j = np.unravel_index(np.argmax(Cc), Cc.shape)
        if Cc[i, j] <= 0:
            break
        assign[up[j]] = ut[i]
        Cc[i, :] = -1; Cc[:, j] = -1
    mapped = [assign.get(p, None) for p in labels_pred]
    f1s = []
    for lab in ut:
        tp = sum(1 for t, m in zip(labels_true, mapped) if t == lab and m == lab)
        fp = sum(1 for t, m in zip(labels_true, mapped) if t != lab and m == lab)
        fn = sum(1 for t, m in zip(labels_true, mapped) if t == lab and m != lab)
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1s.append(2 * prec * rec / (prec + rec) if (prec + rec) else 0.0)
    return float(np.mean(f1s))


def kmeans(X, k, seed=0, n_init=8):
    """Small dependency-free k-means (Lloyd) with k-means++-ish restarts."""
    rng = np.random.default_rng(seed)
    X = np.atleast_2d(X.T).T if X.ndim == 1 else X
    if X.ndim == 1:
        X = X[:, None]
    best_lab, best_inertia = None, np.inf
    for _ in range(n_init):
        idx = rng.choice(len(X), k, replace=False)
        cent = X[idx].copy()
        for _ in range(100):
            d = ((X[:, None, :] - cent[None, :, :]) ** 2).sum(2)
            lab = d.argmin(1)
            new = np.array([X[lab == c].mean(0) if np.any(lab == c) else cent[c] for c in range(k)])
            if np.allclose(new, cent):
                cent = new; break
            cent = new
        inertia = ((X - cent[lab]) ** 2).sum()
        if inertia < best_inertia:
            best_inertia, best_lab = inertia, lab
    return best_lab


def pattern_features(u_pattern, evecs, low_modes, extra=None):
    """Feature matrix for clustering: the nonlinear activator field u(inf) + the LOW unstable eigenmode
    coordinates (the Turing pattern basis, capped to the coarsest few). low_modes must already be the
    selected low-eigenvalue unstable modes."""
    feats = [u_pattern.reshape(-1, 1)]
    if len(low_modes):
        feats.append(evecs[:, low_modes])
    if extra is not None:
        feats.append(extra)
    F = np.hstack(feats)
    F = (F - F.mean(0)) / (F.std(0) + 1e-9)
    return F


def neighbor_mrr(feature, signs, truth_key, labels):
    """Held-out retrieval: for each sign, rank others by feature-distance; MRR of first same-class neighbor."""
    n = len(signs)
    D = ((feature[:, None, :] - feature[None, :, :]) ** 2).sum(2)
    np.fill_diagonal(D, np.inf)
    y = [labels[s][truth_key] for s in signs]
    rr = []
    for i in range(n):
        if y[i] is None:
            continue
        order = np.argsort(D[i])
        for rank, j in enumerate(order, 1):
            if y[j] is None:
                continue
            if y[j] == y[i]:
                rr.append(1.0 / rank); break
    return float(np.mean(rr)) if rr else 0.0


def evaluate_clustering(pred_labels, signs, labels, key):
    """ARI/NMI/macro-F1 against a truth key ('vowel'|'consonant'|'role'), over signs with a non-null label."""
    idx = [i for i, s in enumerate(signs) if labels[s][key] is not None]
    yt = [labels[signs[i]][key] for i in idx]
    yp = [pred_labels[i] for i in idx]
    if len(set(yt)) < 2:
        return dict(ari=float("nan"), nmi=float("nan"), macro_f1=float("nan"), n=len(idx), n_classes=len(set(yt)))
    return dict(ari=ari(yt, yp), nmi=nmi(yt, yp), macro_f1=hungarian_macro_f1(yt, yp),
                n=len(idx), n_classes=len(set(yt)))
