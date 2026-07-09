"""EPOCH-095 — Geographic/scribal morphogenesis (site-community recovery).

Last reserved F11 leg. Distinct channel: does an RD/morphogenesis process over a DOCUMENT-similarity graph recover
SITE/regional community structure better than generic clustering (spectral/Louvain) and a frequency/length
confound baseline? Truth = inscription site label (L2 structural metadata; opaque signs, no phonetic values). Sites
are balanced by subsampling (HT dominates 63%), averaged over subsample seeds. Positive control: synthetic
planted-site corpus (site-specific Dirichlet sign distributions) the methods must recover. Confound guard: a
document-length-only baseline (site recovery must not reduce to document length). Verdicts:
GEOGRAPHIC_MORPHOGENESIS_SUPPORTED / _GENERIC / _NULL / _NO_POWER. Prior (E091/E092/E094): _GENERIC/_NULL expected.
NOTE: parent prereg said 'LB calibration then LA'; LB doc-site metadata is not loadable via load_b_damos, so the
DETECTOR is calibrated on a synthetic planted-site corpus (Stage-1 PC) and applied to LA (Stage-4) -- disclosed.
"""
import sys, os, json, time
import numpy as np
from collections import Counter
import warnings
warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
REPO = "/home/claude-runner/gitlab/n8n/logos-linear-a-frontier-72h"; sys.path.insert(0, REPO)
import rd
import evaluate as EV

EPOCH_DIR = os.path.join(REPO, "experiments/linear_a_frontier_72h/epochs/EPOCH-095")
RESULT = os.path.join(EPOCH_DIR, "result.json")
MIN_SITE = 25
CAP = 80          # per-site cap for balance
SEEDS = [0, 1, 2, 3, 4]


def load_la_docs():
    ins = json.load(open(os.path.join(REPO, "corpus/silver/inscriptions.json")))
    docs = [(x["site"], [t for t in x["signs"]]) for x in ins if x.get("site") and x.get("signs")]
    sitec = Counter(s for s, _ in docs)
    keep_sites = [s for s, c in sitec.items() if c >= MIN_SITE]
    docs = [(s, w) for s, w in docs if s in keep_sites and len(w) >= 2]
    signs = sorted(set(t for _, w in docs for t in w))
    return docs, keep_sites, signs


def doc_vectors(docs, signs):
    idx = {s: i for i, s in enumerate(signs)}
    X = np.zeros((len(docs), len(signs)))
    for d, (_, w) in enumerate(docs):
        for t in w:
            if t in idx:
                X[d, idx[t]] += 1
    lens = X.sum(1, keepdims=True); lens[lens == 0] = 1
    Xn = X / lens                                  # normalized sign-frequency vector
    return Xn, X.sum(1)


def build_doc_graph(Xn):
    W = Xn @ Xn.T                                  # cosine-like (rows are L1-normalized freq; use dot)
    # cosine proper:
    nrm = np.linalg.norm(Xn, axis=1, keepdims=True); nrm[nrm == 0] = 1
    Xc = Xn / nrm; W = Xc @ Xc.T
    np.fill_diagonal(W, 0.0); W = np.maximum(W, 0.0)
    return W


def _sym_norm_L(W):
    d = W.sum(1); d = np.where(d == 0, 1, d); dinv = 1 / np.sqrt(d)
    L = np.eye(W.shape[0]) - (W * dinv[:, None]) * dinv[None, :]; L = 0.5 * (L + L.T)
    ev, U = np.linalg.eigh(L); return L, np.clip(ev, 0, None), U, W.sum(1)


def m_morphogenesis(W, L, ev, U, k):
    r = rd.schnakenberg(); best = None
    for ratio in (10, 20, 40):
        c = rd.find_Du(r, ev, ratio)
        if c is None:
            continue
        key = (c["min_unstable_lam"], c["n_unstable"])
        if best is None or key < best[0]:
            best = (key, c)
    if best is None:
        return None
    c = best[1]
    low = [m for m in c["verify"]["unstable_modes"] if ev[m] > 1e-9]
    low = sorted(low, key=lambda m: ev[m])[:4]
    pat = np.mean([rd.integrate(r, L, c["Du"], c["Dv"], seed=s) for s in (1, 2, 3)], 0)
    F = EV.pattern_features(pat, U, low)
    return EV.kmeans(F, k, seed=0)


def m_spectral(W, k):
    from sklearn.cluster import SpectralClustering
    try:
        return SpectralClustering(n_clusters=k, affinity="precomputed", assign_labels="kmeans",
                                  random_state=0).fit_predict(np.maximum(W, 0))
    except Exception:
        return None


def m_louvain(W):
    import networkx as nx
    Gr = nx.from_numpy_array(np.maximum(W, 0))
    try:
        comms = nx.community.louvain_communities(Gr, seed=0, weight="weight")
    except Exception:
        return None
    lab = np.zeros(W.shape[0], int)
    for ci, c in enumerate(comms):
        for n in c:
            lab[n] = ci
    return lab


def m_length_only(lengths, k):
    return EV.kmeans(np.log(lengths.reshape(-1, 1) + 1), k, seed=0)


def eval_site(labels_pred, site_ids):
    return dict(ari=EV.ari(list(site_ids), list(labels_pred)),
                nmi=EV.nmi(list(site_ids), list(labels_pred)))


def run_la_arm(docs, sites, signs, seed):
    rng = np.random.default_rng(seed)
    # balance: subsample each site to CAP
    bysite = {}
    for i, (s, w) in enumerate(docs):
        bysite.setdefault(s, []).append(i)
    idx = []
    for s in sites:
        ids = bysite[s]; rng.shuffle(ids); idx += ids[:CAP]
    sub = [docs[i] for i in idx]
    site_ids = [sites.index(s) for s, _ in sub]
    Xn, lengths = doc_vectors(sub, signs)
    W = build_doc_graph(Xn)
    L, ev, U, deg = _sym_norm_L(W)
    k = len(sites)
    out = {}
    lab = m_morphogenesis(W, L, ev, U, k)
    out["morphogenesis"] = eval_site(lab, site_ids) if lab is not None else None
    lab = m_spectral(W, k); out["spectral"] = eval_site(lab, site_ids) if lab is not None else None
    lab = m_louvain(W); out["louvain"] = eval_site(lab, site_ids) if lab is not None else None
    out["length_only"] = eval_site(m_length_only(lengths, k), site_ids)
    out["random"] = eval_site(rng.integers(0, k, len(sub)), site_ids)
    return out


def synthetic_pc(seed, n_sites=5, per=80, vocab=90):
    rng = np.random.default_rng(seed)
    # each site has a Dirichlet sign distribution; docs sampled from it
    site_dist = [rng.dirichlet(np.ones(vocab) * 0.3) for _ in range(n_sites)]
    docs = []; site_ids = []
    for s in range(n_sites):
        for _ in range(per):
            L = rng.integers(4, 12)
            w = [str(x) for x in rng.choice(vocab, L, p=site_dist[s])]
            docs.append((str(s), w)); site_ids.append(s)
    signs = [str(i) for i in range(vocab)]
    Xn, lengths = doc_vectors(docs, signs)
    W = build_doc_graph(Xn); L, ev, U, deg = _sym_norm_L(W)
    k = n_sites
    res = {}
    lab = m_morphogenesis(W, L, ev, U, k); res["morphogenesis"] = EV.ari(site_ids, list(lab)) if lab is not None else None
    lab = m_spectral(W, k); res["spectral"] = EV.ari(site_ids, list(lab)) if lab is not None else None
    return res


def main():
    os.makedirs(EPOCH_DIR, exist_ok=True); t0 = time.time()
    docs, sites, signs = load_la_docs()
    # order sites by frequency for stable indexing
    sites = [s for s, _ in Counter(s for s, _ in docs).most_common()]

    pc = [synthetic_pc(s) for s in range(5)]
    pc_spec = float(np.mean([p["spectral"] for p in pc if p["spectral"] is not None]))
    pc_morph = float(np.mean([p["morphogenesis"] for p in pc if p["morphogenesis"] is not None]))
    pc_detects = pc_spec > 0.25   # generic detector recovers planted sites

    arms = [run_la_arm(docs, sites, signs, s) for s in SEEDS]
    def agg(method, metric="ari"):
        vals = [a[method][metric] for a in arms if a.get(method)]
        return float(np.mean(vals)) if vals else None
    la = {m: {"ari": agg(m, "ari"), "nmi": agg(m, "nmi")} for m in
          ["morphogenesis", "spectral", "louvain", "length_only", "random"]}

    verdict, rationale = _verdict(la, pc_spec, pc_morph, pc_detects)
    results = {"positive_control": {"spectral_ari": pc_spec, "morphogenesis_ari": pc_morph, "detects": pc_detects},
               "linear_a_site_recovery": la, "sites": sites, "n_sites": len(sites), "cap": CAP,
               "verdict": verdict, "rationale": rationale, "layer": "L2", "licences_changed": "none",
               "la_touched": True, "runtime_sec": round(time.time() - t0, 1)}
    with open(RESULT, "w") as fh:
        json.dump(results, fh, indent=1, default=lambda o: float(o))
    print("VERDICT:", verdict); print("rationale:", rationale)
    print("PC: spectral_ari=%.3f morphogenesis_ari=%.3f detects=%s" % (pc_spec, pc_morph, pc_detects))
    print("LA site recovery (ARI):", {m: round(la[m]["ari"], 3) for m in la if la[m]["ari"] is not None})
    return results


def _verdict(la, pc_spec, pc_morph, pc_detects):
    if not pc_detects:
        return "GEOGRAPHIC_MORPHOGENESIS_NO_POWER", (
            "Positive control fails: generic clustering does not recover planted sites (spectral ARI %.3f) -- the "
            "site-recovery harness has no power, so the LA arm is uninterpretable." % pc_spec)
    morph = la["morphogenesis"]["ari"] or 0.0
    rnd = la["random"]["ari"] or 0.0
    length = la["length_only"]["ari"] or 0.0
    generic = max(la["spectral"]["ari"] or 0.0, la["louvain"]["ari"] or 0.0)
    gname = "spectral" if (la["spectral"]["ari"] or 0) >= (la["louvain"]["ari"] or 0) else "louvain"
    # site recovery must beat the length confound + random to be a genuine geographic signal
    if morph <= max(rnd, length) + 0.02:
        return "GEOGRAPHIC_MORPHOGENESIS_NULL", (
            "Morphogenesis does not recover LA site structure beyond the confound floor (morphogenesis ARI %.3f vs "
            "length-only %.3f, random %.3f); generic clustering %s reaches %.3f. No morphogenetic geographic signal." % (
                morph, length, rnd, gname, generic))
    if morph > generic + 0.02:
        return "GEOGRAPHIC_MORPHOGENESIS_SUPPORTED", (
            "Morphogenesis recovers LA site structure above the length confound AND the generic baselines "
            "(morphogenesis ARI %.3f vs %s %.3f, length-only %.3f)." % (morph, gname, generic, length))
    return "GEOGRAPHIC_MORPHOGENESIS_GENERIC", (
        "Morphogenesis recovers some LA site structure above the length confound (ARI %.3f vs length %.3f, random "
        "%.3f) but NOT beyond generic clustering (%s %.3f >= morphogenesis). Regional structure is recoverable but "
        "morphogenesis adds nothing over generic methods -- the E091/E092/E094 pattern holds for the geographic "
        "channel too. L2 (site = structural metadata), no phonetic values, no licence." % (
            morph, length, rnd, gname, generic))


if __name__ == "__main__":
    main()
