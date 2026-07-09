"""Blinded graph construction for Turing morphogenesis (E091+).

Signs are mapped to OPAQUE integer IDs before any graph is built. Phonetic values are used ONLY to build held-out
truth labels (vowel/consonant/role), never seen by the model. All graphs: symmetric, nonnegative, no self-loops,
largest connected component retained. Laplacian = symmetric normalized  L = I - D^-1/2 W D^-1/2  (eigenvalues in [0,2]).
"""
import sys, os, re, math
import numpy as np
from collections import Counter, defaultdict

REPO = "/home/claude-runner/gitlab/n8n/logos-linear-a-frontier-72h"
sys.path.insert(0, REPO)


def load_lb():
    """DAMOS Linear B: sequences (value-transliterated), freq, value2glyph. Returns (seqs, signs, freq)."""
    from scripts.cross_script.data import load_b_damos
    seqs, freq, _ = load_b_damos()
    signs = sorted(freq.keys())
    return seqs, signs, freq


VOWELS = set("AEIOU")


def truth_labels(signs):
    """Held-out truth from the CV structure of the LB sign VALUE (evaluation only).
    Returns dict: sign -> {vowel, consonant, role}. Syllabograms are 1-2 char CV values (e.g. 'DA','RO','A')."""
    lab = {}
    for s in signs:
        u = s.upper()
        role = "syllabogram"
        vowel = None
        cons = None
        if re.fullmatch(r"[AEIOU]", u):            # pure vowel
            vowel = u; cons = "V"
        elif re.fullmatch(r"[A-Z][AEIOU]", u):     # CV syllabogram
            cons = u[0]; vowel = u[1]
        elif re.fullmatch(r"[A-Z]{2}[AEIOU]", u):  # CCV (rare, e.g. spirant)
            cons = u[:2]; vowel = u[-1]
        else:
            role = "other"                          # logogram / numeral / ligature / uncertain
        lab[s] = {"vowel": vowel, "consonant": cons, "role": role}
    return lab


def blind(signs, seed=0):
    """Map signs -> opaque IDs. Returns (sign2id, id2sign). Deterministic per seed (shuffled so IDs carry no order)."""
    rng = np.random.default_rng(seed)
    order = list(signs); rng.shuffle(order)
    sign2id = {s: i for i, s in enumerate(order)}
    id2sign = {i: s for s, i in sign2id.items()}
    return sign2id, id2sign


def _largest_cc(W):
    """Keep the largest connected component. Returns (W_sub, node_index_map into original)."""
    import scipy.sparse as sp
    from scipy.sparse.csgraph import connected_components
    n_comp, labels = connected_components(sp.csr_matrix(W > 0), directed=False)
    if n_comp == 1:
        return W, np.arange(W.shape[0]), n_comp
    big = np.argmax(np.bincount(labels))
    idx = np.where(labels == big)[0]
    return W[np.ix_(idx, idx)], idx, n_comp


def _sym_norm_laplacian(W):
    d = W.sum(1)
    d[d == 0] = 1.0
    dinv = 1.0 / np.sqrt(d)
    L = np.eye(W.shape[0]) - (W * dinv[:, None]) * dinv[None, :]
    L = 0.5 * (L + L.T)
    return L


def _finalize(W):
    """Zero diagonal, symmetrize, keep largest CC, return dict with W, L, eigvals, eigvecs, degree, cc info."""
    W = np.array(W, float)
    np.fill_diagonal(W, 0.0)
    W = 0.5 * (W + W.T)
    W = np.maximum(W, 0.0)
    Wc, idx, n_comp = _largest_cc(W)
    L = _sym_norm_laplacian(Wc)
    evals, evecs = np.linalg.eigh(L)
    evals = np.clip(evals, 0, None)
    return {"W": Wc, "L": L, "evals": evals, "evecs": evecs,
            "degree": Wc.sum(1), "kept_idx": idx, "n_components_full": int(n_comp), "n": Wc.shape[0]}


def _ppmi(counts, n_total):
    """PPMI from a co-occurrence count matrix."""
    row = counts.sum(1, keepdims=True); col = counts.sum(0, keepdims=True); tot = counts.sum()
    with np.errstate(divide="ignore", invalid="ignore"):
        pmi = np.log((counts * tot) / (row * col + 1e-12) + 1e-12)
    return np.maximum(pmi, 0.0)


def build_graphs(seqs, signs, sign2id, min_count=3):
    """Build G_POSITION, G_SUBSTITUTION, G_FORMULA, G_MULTILAYER (blinded). Nodes = signs with freq>=min_count."""
    freq = Counter(t for s in seqs for t in s)
    keep = [s for s in signs if freq[s] >= min_count and s in sign2id]
    ids = sorted(sign2id[s] for s in keep)
    id_local = {gid: i for i, gid in enumerate(ids)}
    n = len(ids)
    tok2local = {}
    for s in keep:
        tok2local[s] = id_local[sign2id[s]]

    # POSITION: adjacent left->right co-occurrence -> PPMI (symmetrized)
    co = np.zeros((n, n))
    Lctx = defaultdict(Counter); Rctx = defaultdict(Counter)
    doc_membership = defaultdict(set)
    for di, s in enumerate(seqs):
        toks = [t for t in s if t in tok2local]
        for j, t in enumerate(toks):
            doc_membership[tok2local[t]].add(di)
            if j + 1 < len(toks):
                a, b = tok2local[t], tok2local[toks[j + 1]]
                co[a, b] += 1
                Rctx[a][toks[j + 1]] += 1; Lctx[tok2local[toks[j + 1]]][t] += 1
    Gpos = _ppmi(co + co.T, co.sum())

    # SUBSTITUTION: cosine similarity of (left||right) context distributions
    vocab = sorted(set([t for c in Lctx.values() for t in c] + [t for c in Rctx.values() for t in c]))
    vidx = {t: i for i, t in enumerate(vocab)}; m = len(vocab)
    ctx = np.zeros((n, 2 * m))
    for s in keep:
        li = tok2local[s]
        for t, c in Lctx.get(li, {}).items():
            if t in vidx: ctx[li, vidx[t]] += c
        for t, c in Rctx.get(li, {}).items():
            if t in vidx: ctx[li, m + vidx[t]] += c
    norm = np.linalg.norm(ctx, axis=1, keepdims=True); norm[norm == 0] = 1
    ctxn = ctx / norm
    Gsub = ctxn @ ctxn.T
    np.fill_diagonal(Gsub, 0.0); Gsub = np.maximum(Gsub, 0.0)

    # FORMULA: shared-document co-membership, df-normalized (approximates shared slots)
    Gform = np.zeros((n, n))
    docs_of = {li: doc_membership[li] for li in range(n)}
    df = np.array([len(docs_of[li]) for li in range(n)], float); df[df == 0] = 1
    for a in range(n):
        for b in range(a + 1, n):
            inter = len(docs_of[a] & docs_of[b])
            if inter:
                w = inter / math.sqrt(df[a] * df[b])
                Gform[a, b] = Gform[b, a] = w

    def rn(M):
        M = M.copy(); s = M.sum(); return M / s if s > 0 else M
    Gmulti = rn(Gpos) + rn(Gsub) + rn(Gform)

    local2sign = {i: id2 for id2, i in id_local.items()}  # local -> global id
    id2sign_local = None
    graphs = {
        "POSITION": _finalize(Gpos), "SUBSTITUTION": _finalize(Gsub),
        "FORMULA": _finalize(Gform), "MULTILAYER": _finalize(Gmulti),
    }
    # attach the sign order (local index -> sign string) for evaluation
    inv = {tok2local[s]: s for s in keep}
    for g in graphs.values():
        g["signs"] = [inv[i] for i in range(n)]
        g["signs_kept"] = [inv[i] for i in g["kept_idx"]]
    return graphs


if __name__ == "__main__":
    seqs, signs, freq = load_lb()
    lab = truth_labels(signs)
    s2i, i2s = blind(signs, seed=0)
    G = build_graphs(seqs, signs, s2i, min_count=3)
    for name, g in G.items():
        print(f"{name}: n={g['n']} components_full={g['n_components_full']} "
              f"lambda_max={g['evals'][-1]:.3f} lambda_2={g['evals'][1]:.4f}")
    roles = Counter(lab[s]["role"] for s in G["POSITION"]["signs_kept"])
    vowels = Counter(lab[s]["vowel"] for s in G["POSITION"]["signs_kept"])
    print("roles(kept):", dict(roles)); print("vowels(kept):", dict(vowels))
