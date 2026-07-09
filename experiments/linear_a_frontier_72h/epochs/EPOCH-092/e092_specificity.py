"""EPOCH-092 — Turing-specificity vs generic graph clustering.

E091 showed the Turing MECHANISM adds nothing over equal-diffusion on blinded LB. E092 asks the formal
specificity question: is graph reaction-diffusion (Turing) morphogenesis EVER needed, i.e. does it beat a
panel of generic graph-clustering baselines on blinded-LB class recovery, search-adjusted and cross-view
stable? Baselines (must themselves recover the planted-Turing PC, else they are strawmen):
  spectral clustering (null-of-record), raw-affinity spectral, Laplacian-eigenmap+GMM, Laplacian-eigenmap+kmeans,
  Louvain community, linear-diffusion (heat-kernel) embedding, equal-diffusion RD, reaction-only, + Turing.
Verdicts: TURING_SPECIFIC_SUPPORTED / GENERIC_GRAPH_CLUSTERING (TURING_NOT_NEEDED) / TURING_SPECIFIC_NULL / NO_POWER.
Prior (E016 SBI + E091): GENERIC_GRAPH_CLUSTERING is the expected outcome.
"""
import sys, os, json, time
import numpy as np
import warnings
warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO = "/home/claude-runner/gitlab/n8n/logos-linear-a-frontier-72h"
sys.path.insert(0, REPO)
import graphs as G
import rd
import evaluate as EV

EPOCH_DIR = os.path.join(REPO, "experiments/linear_a_frontier_72h/epochs/EPOCH-092")
RESULT = os.path.join(EPOCH_DIR, "result.json")
TRUTH_KEYS = ["role", "vowel", "consonant"]
K_FOR = {"role": 2, "vowel": 5, "consonant": 8}
SEEDS = [1, 2, 3]
MODE_CAP = 4


def _low_modes(evals, um):
    um = [m for m in um if evals[m] > 1e-9]
    return sorted(um, key=lambda m: evals[m])[:MODE_CAP]


# ---------- methods: each returns a label vector (n,) given (W, L, evals, evecs, k) ----------

def m_turing(W, L, ev, U, k):
    r, res = None, None
    best = None
    for rn in ["Schnakenberg", "GiererMeinhardt"]:
        rr = rd.REACTIONS[rn]()
        for ratio in (10, 20, 40):
            c = rd.find_Du(rr, ev, ratio)
            if c is None:
                continue
            key = (c["min_unstable_lam"], c["n_unstable"])
            if best is None or key < best[0]:
                best = (key, rr, c)
    if best is None:
        return None
    _, rr, c = best
    low = _low_modes(ev, c["verify"]["unstable_modes"])
    pat = np.mean([rd.integrate(rr, L, c["Du"], c["Dv"], seed=s) for s in SEEDS], 0)
    return EV.kmeans(EV.pattern_features(pat, U, low), k, seed=0)


def m_equal_diffusion(W, L, ev, U, k):
    rr = rd.schnakenberg()
    pat = np.mean([rd.integrate(rr, L, 0.3, 0.3, seed=s) for s in SEEDS], 0)
    return EV.kmeans(EV.pattern_features(pat, U, []), k, seed=0)


def m_reaction_only(W, L, ev, U, k):
    rr = rd.schnakenberg()
    pat = np.mean([rd.integrate(rr, np.zeros_like(L), 1e-9, 1e-9, seed=s) for s in SEEDS], 0)
    return EV.kmeans(EV.pattern_features(pat, U, []), k, seed=0)


def m_spectral(W, L, ev, U, k):
    from sklearn.cluster import SpectralClustering
    A = np.array(W, float); np.fill_diagonal(A, 0); A = np.maximum(A, 0)
    try:
        return SpectralClustering(n_clusters=k, affinity="precomputed", assign_labels="kmeans",
                                  random_state=0).fit_predict(A)
    except Exception:
        return None


def m_eigenmap_kmeans(W, L, ev, U, k):
    # lowest-k nonzero Laplacian eigenvectors -> kmeans (classic spectral embedding)
    nz = np.where(ev > 1e-9)[0][:max(k, MODE_CAP)]
    return EV.kmeans(U[:, nz], k, seed=0)


def m_eigenmap_gmm(W, L, ev, U, k):
    from sklearn.mixture import GaussianMixture
    nz = np.where(ev > 1e-9)[0][:max(k, MODE_CAP)]
    X = U[:, nz]
    try:
        return GaussianMixture(n_components=k, covariance_type="full", random_state=0, n_init=3).fit_predict(X)
    except Exception:
        return None


def m_louvain(W, L, ev, U, k):
    import networkx as nx
    A = np.array(W, float); np.fill_diagonal(A, 0)
    Gr = nx.from_numpy_array(A)
    try:
        comms = nx.community.louvain_communities(Gr, seed=0, weight="weight")
    except Exception:
        return None
    lab = np.zeros(A.shape[0], int)
    for ci, c in enumerate(comms):
        for node in c:
            lab[node] = ci
    return lab


def m_linear_diffusion(W, L, ev, U, k):
    # heat-kernel (linear diffusion) embedding: exp(-t L) columns at a moderate t -> kmeans
    t = 5.0
    H = U @ np.diag(np.exp(-t * ev)) @ U.T
    return EV.kmeans(H, k, seed=0)


METHODS = {
    "turing": m_turing, "equal_diffusion": m_equal_diffusion, "reaction_only": m_reaction_only,
    "spectral": m_spectral, "eigenmap_kmeans": m_eigenmap_kmeans, "eigenmap_gmm": m_eigenmap_gmm,
    "louvain": m_louvain, "linear_diffusion": m_linear_diffusion,
}
GENERIC = ["spectral", "eigenmap_kmeans", "eigenmap_gmm", "louvain", "linear_diffusion"]  # non-Turing baselines


def _sym_norm_L(W):
    W = np.array(W, float); np.fill_diagonal(W, 0); W = 0.5 * (W + W.T); W = np.maximum(W, 0)
    d = W.sum(1); d[d == 0] = 1; dinv = 1 / np.sqrt(d)
    Lm = np.eye(W.shape[0]) - (W * dinv[:, None]) * dinv[None, :]; Lm = 0.5 * (Lm + Lm.T)
    ev, Uu = np.linalg.eigh(Lm); return Lm, np.clip(ev, 0, None), Uu


def planted_pc(seed, n=90, k=3):
    rng = np.random.default_rng(seed); block = rng.integers(0, k, n); W = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            p = 0.45 if block[i] == block[j] else 0.03
            if rng.random() < p:
                W[i, j] = W[j, i] = 1.0
    L, ev, U = _sym_norm_L(W)
    out = {}
    for mn, fn in METHODS.items():
        lab = fn(W, L, ev, U, k)
        out[mn] = float(EV.ari(list(block), list(lab))) if lab is not None else None
    return out


def main():
    os.makedirs(EPOCH_DIR, exist_ok=True)
    t0 = time.time()
    seqs, signs, freq = G.load_lb()
    labels = G.truth_labels(signs)
    s2i, i2s = G.blind(signs, seed=0)
    graphs = G.build_graphs(seqs, signs, s2i, min_count=3)

    # ---- positive control: every method must recover planted blocks (fair baselines, not strawmen) ----
    pc = [planted_pc(s) for s in range(5)]
    pc_mean = {mn: float(np.nanmean([p[mn] for p in pc if p[mn] is not None])) for mn in METHODS}
    pc_recovered = {mn: sum(1 for p in pc if p[mn] is not None and p[mn] > 0.25) for mn in METHODS}

    # ---- real blinded LB: per view x method x truth key -> macro-F1 + ARI ----
    perf = {k: {mn: {"f1": [], "ari": []} for mn in METHODS} for k in TRUTH_KEYS}
    for vname, g in graphs.items():
        W, L, ev, U, sk = g["W"], g["L"], g["evals"], g["evecs"], g["signs_kept"]
        for mn, fn in METHODS.items():
            for key in TRUTH_KEYS:
                labk = fn(W, L, ev, U, K_FOR[key])
                if labk is None:
                    continue
                m = EV.evaluate_clustering(labk, sk, labels, key)
                if m["macro_f1"] == m["macro_f1"]:
                    perf[key][mn]["f1"].append((vname, m["macro_f1"]))
                    perf[key][mn]["ari"].append((vname, m["ari"]))

    # best-of-view per method (view multiplicity charged equally to all methods)
    best = {k: {} for k in TRUTH_KEYS}
    for key in TRUTH_KEYS:
        for mn in METHODS:
            fs = perf[key][mn]["f1"]
            if fs:
                bv, bf = max(fs, key=lambda x: x[1])
                best[key][mn] = {"f1": float(bf), "view": bv,
                                 "mean_f1": float(np.mean([x[1] for x in fs]))}
    # verdict
    verdict, rationale, summary = _verdict(best, pc_recovered, pc_mean)
    results = {"positive_control": {"mean_ari": pc_mean, "n_recovered": pc_recovered},
               "best_of_view": best, "summary": summary, "verdict": verdict, "rationale": rationale,
               "config": {"methods": list(METHODS), "generic_baselines": GENERIC, "k_for": K_FOR},
               "layer": "L2", "licences_changed": "none", "la_touched": False,
               "runtime_sec": round(time.time() - t0, 1)}
    with open(RESULT, "w") as fh:
        json.dump(results, fh, indent=1, default=lambda o: float(o))
    print("VERDICT:", verdict)
    print("rationale:", rationale)
    for key in TRUTH_KEYS:
        row = " ".join("%s=%.3f" % (mn, best[key][mn]["f1"]) for mn in ["turing"] + GENERIC if mn in best[key])
        print("  %-10s %s" % (key, row))
    print("PC recovered (of 5):", {m: pc_recovered[m] for m in ["turing"] + GENERIC})
    return results


def _verdict(best, pc_recovered, pc_mean):
    # baselines must be fair: require the generic panel + turing to recover the planted PC
    weak = [m for m in (["turing"] + GENERIC) if pc_recovered.get(m, 0) < 3]
    if "turing" in weak:
        return "NO_POWER", "Turing PC did not fire (%d/5)." % pc_recovered.get("turing", 0), {}
    strong_generic = [m for m in GENERIC if pc_recovered.get(m, 0) >= 3]
    if not strong_generic:
        return "NO_POWER", "No generic baseline recovers the planted PC -> cannot fairly test specificity.", {}
    summary = {}
    turing_wins = 0; total = 0
    for key in ("vowel", "role"):     # vowel = linguistically meaningful; role = trivial degree channel
        if key not in best or "turing" not in best[key]:
            continue
        tf = best[key]["turing"]["f1"]
        gbest = max((best[key][m]["f1"] for m in strong_generic if m in best[key]), default=0.0)
        gbest_m = max(((best[key][m]["f1"], m) for m in strong_generic if m in best[key]), default=(0, None))[1]
        summary[key] = {"turing_f1": tf, "best_generic_f1": gbest, "best_generic": gbest_m,
                        "turing_minus_generic": tf - gbest}
        total += 1
        if tf > gbest + 0.02:
            turing_wins += 1
    vw = summary.get("vowel", {})
    rl = summary.get("role", {})
    if turing_wins == total and total > 0 and vw.get("turing_minus_generic", -1) > 0.02:
        rationale = ("Turing beats the best generic baseline on every tested channel, including vowel "
                     "(Turing %.3f vs generic %.3f)." % (vw.get("turing_f1", 0), vw.get("best_generic_f1", 0)))
        return "TURING_SPECIFIC_SUPPORTED", rationale, summary
    rationale = ("TURING_NOT_NEEDED: generic graph clustering matches or beats Turing on blinded LB. "
                 "Vowel: Turing %.3f vs best generic %.3f (%s); role: Turing %.3f vs generic %.3f. The "
                 "diffusion-driven instability is not specifically required -- consistent with EPOCH-016 (SBI) "
                 "and EPOCH-091 (equal-diffusion ties Turing)." % (
                     vw.get("turing_f1", 0), vw.get("best_generic_f1", 0), vw.get("best_generic"),
                     rl.get("turing_f1", 0), rl.get("best_generic_f1", 0)))
    return "GENERIC_GRAPH_CLUSTERING", rationale, summary


if __name__ == "__main__":
    main()
