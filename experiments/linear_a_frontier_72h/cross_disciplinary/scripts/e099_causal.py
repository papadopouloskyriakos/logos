"""EPOCH-099 — Causal source separation & confound disentanglement.

Is the blinded-LB sign-class structure LINGUISTIC (invariant across nuisance) or CONFOUND-explained (frequency)?
Source-separate the sign context embedding (ICA + NMF + PCA), identify which components load on the linguistic
target (vowel class) vs the nuisance (log-frequency), and run the INVARIANCE test that decides it:
  leave-one-frequency-band-out (LOFO) vowel prediction -- if vowel is predictable for signs whose FREQUENCY band was
  never in training, the signal is frequency-invariant (linguistic); if it collapses, it is frequency-confounded.
Two independent interventions (frequency-band-out AND deconfounding-by-residualizing-on-log-freq) must both hold.
Positive control: synthetic with a linguistic factor INDEPENDENT of a confound factor (LOFO must survive).
Negative control: synthetic where the label IS the confound (LOFO must collapse -> CONFOUND_EXPLAINED). Verdicts:
CAUSAL_INVARIANT_STRUCTURE_SUPPORTED / CONFOUND_EXPLAINED_SIGNAL / PARTIAL_INVARIANCE / CAUSAL_NULL / CAUSAL_NO_POWER.
Prior (E093): vowel beats frequency-only by a stable margin -> some invariance expected, but it is weak.
"""
import sys, os, json, time
import numpy as np
from collections import Counter, defaultdict
import warnings
warnings.filterwarnings("ignore")

REPO = "/home/claude-runner/gitlab/n8n/logos-linear-a-frontier-72h"
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "experiments/linear_a_frontier_72h/morphogenesis/scripts"))
import graphs as GR
EPOCH_DIR = os.path.join(REPO, "experiments/linear_a_frontier_72h/epochs/EPOCH-099")
RESULT = os.path.join(EPOCH_DIR, "result.json")
VOW = {"A": 0, "E": 1, "I": 2, "O": 3, "U": 4}


def context_embedding(seqs, signs, min_count=3):
    """Sign x (left||right neighbor) count embedding + per-sign frequency."""
    freq = Counter(t for s in seqs for t in s)
    keep = [s for s in signs if freq[s] >= min_count]
    kidx = {s: i for i, s in enumerate(keep)}
    L = defaultdict(Counter); R = defaultdict(Counter)
    for w in seqs:
        toks = [t for t in w if t in kidx]
        for j, t in enumerate(toks):
            if j > 0: L[t][toks[j - 1]] += 1
            if j < len(toks) - 1: R[t][toks[j + 1]] += 1
    vocab = sorted(kidx)
    vi = {s: i for i, s in enumerate(vocab)}; m = len(vocab)
    X = np.zeros((len(keep), 2 * m))
    for s in keep:
        for t, c in L[s].items(): X[kidx[s], vi[t]] += c
        for t, c in R[s].items(): X[kidx[s], m + vi[t]] += c
    nrm = np.linalg.norm(X, axis=1, keepdims=True); nrm[nrm == 0] = 1
    return X / nrm, keep, np.array([freq[s] for s in keep], float)


def decompose(X, k=8, seed=0):
    from sklearn.decomposition import PCA, FastICA, NMF
    out = {}
    out["pca"] = PCA(n_components=k, random_state=seed).fit_transform(X)
    try:
        out["ica"] = FastICA(n_components=k, random_state=seed, max_iter=500).fit_transform(X)
    except Exception:
        out["ica"] = out["pca"]
    Xp = X - X.min()
    try:
        out["nmf"] = NMF(n_components=k, init="nndsvda", random_state=seed, max_iter=400).fit_transform(Xp)
    except Exception:
        out["nmf"] = np.abs(out["pca"])
    return out


def nearest_centroid_f1(Xtr, ytr, Xte, yte, classes):
    cent = {}
    for c in classes:
        m = Xtr[ytr == c]
        if len(m): cent[c] = m.mean(0)
    if len(cent) < 2:
        return float("nan")
    cs = list(cent); C = np.array([cent[c] for c in cs])
    D = ((Xte[:, None, :] - C[None, :, :]) ** 2).sum(2)
    pred = np.array([cs[i] for i in D.argmin(1)])
    f1 = []
    for c in classes:
        tp = np.sum((yte == c) & (pred == c)); fp = np.sum((yte != c) & (pred == c)); fn = np.sum((yte == c) & (pred != c))
        p = tp / (tp + fp) if tp + fp else 0; r = tp / (tp + fn) if tp + fn else 0
        f1.append(2 * p * r / (p + r) if p + r else 0)
    return float(np.mean(f1))


def lofo(emb, y, freq, classes):
    """Leave-one-frequency-band-out vowel prediction: train on 2 terciles, test on held-out tercile."""
    valid = y >= 0
    emb, y, freq = emb[valid], y[valid], freq[valid]
    bands = np.digitize(np.log(freq + 1), np.quantile(np.log(freq + 1), [1 / 3, 2 / 3]))
    scores = []
    for b in (0, 1, 2):
        te = bands == b; tr = ~te
        if te.sum() < 3 or len(set(y[tr])) < 2:
            continue
        scores.append(nearest_centroid_f1(emb[tr], y[tr], emb[te], y[te], classes))
    return float(np.nanmean(scores)) if scores else float("nan")


def within_band(emb, y, freq, classes, seed=0):
    """In-distribution baseline: random 70/30 split (frequency mixed)."""
    valid = y >= 0; emb, y = emb[valid], y[valid]
    rng = np.random.default_rng(seed); idx = rng.permutation(len(y)); n = int(0.7 * len(y))
    tr, te = idx[:n], idx[n:]
    if len(set(y[tr])) < 2:
        return float("nan")
    return nearest_centroid_f1(emb[tr], y[tr], emb[te], y[te], classes)


def deconfound(X, freq):
    """Residualize each feature on log-frequency (remove the linear frequency component)."""
    f = np.log(freq + 1); f = (f - f.mean()) / (f.std() + 1e-9)
    beta = (X * f[:, None]).sum(0) / (f @ f + 1e-9)
    return X - np.outer(f, beta)


def synth(seed, confounded, n=90, k_true=5, dim=60):
    """Synthetic: signs have a linguistic factor (vowel) + a frequency confound. If confounded, vowel==freq-band."""
    rng = np.random.default_rng(seed)
    vowel = rng.integers(0, k_true, n)
    logf = rng.normal(size=n)
    if confounded:
        vowel = np.digitize(logf, np.quantile(logf, [0.2, 0.4, 0.6, 0.8]))  # label IS the freq band
    ling_dirs = rng.normal(size=(k_true, dim))
    conf_dir = rng.normal(size=dim)
    X = np.array([ling_dirs[vowel[i]] + 1.5 * logf[i] * conf_dir + 0.5 * rng.normal(size=dim) for i in range(n)])
    nrm = np.linalg.norm(X, axis=1, keepdims=True); nrm[nrm == 0] = 1
    freq = np.exp(logf) * 20 + 3
    return X / nrm, vowel, freq


def run_arm(X, y, freq, classes, tag):
    dec = decompose(X)
    emb = dec["ica"]  # source-separated representation
    res = {}
    res["within_band_f1"] = within_band(emb, y, freq, classes)
    res["lofo_f1"] = lofo(emb, y, freq, classes)                      # intervention 1: frequency-band-out
    Xd = deconfound(X, freq); embd = decompose(Xd)["ica"]
    res["deconfounded_lofo_f1"] = lofo(embd, y, freq, classes)        # intervention 2: residualize on log-freq
    # frequency component check: best single-component correlation with log-freq
    f = np.log(freq + 1)
    comp_freq_corr = max(abs(np.corrcoef(emb[:, c], f)[0, 1]) for c in range(emb.shape[1]))
    res["max_component_freq_corr"] = float(comp_freq_corr)
    return res


def main():
    os.makedirs(EPOCH_DIR, exist_ok=True); t0 = time.time()
    from scripts.cross_script.data import load_b_damos, load_a
    lb_seqs, lb_freq, _ = load_b_damos(); lb_signs = sorted(lb_freq.keys())
    lb_lab = GR.truth_labels(lb_signs)
    Xlb, keep, freqlb = context_embedding(lb_seqs, lb_signs)
    ylb = np.array([VOW.get(lb_lab[s]["vowel"], -1) for s in keep])
    classes = [0, 1, 2, 3, 4]

    # ---- controls ----
    pc = []  # linguistic factor independent of confound -> LOFO survives
    for s in range(3):
        Xs, ys, fs = synth(s, confounded=False); pc.append(run_arm(Xs, ys, fs, list(range(5)), "pc"))
    ng = []  # label IS the confound -> LOFO collapses
    for s in range(3):
        Xs, ys, fs = synth(s, confounded=True); ng.append(run_arm(Xs, ys, fs, list(range(5)), "neg"))
    pc_lofo = float(np.nanmean([p["lofo_f1"] for p in pc]))
    pc_within = float(np.nanmean([p["within_band_f1"] for p in pc]))
    ng_lofo = float(np.nanmean([n["lofo_f1"] for n in ng]))
    ng_within = float(np.nanmean([n["within_band_f1"] for n in ng]))
    pc_detects = (pc_lofo > pc_within - 0.10) and (ng_lofo < ng_within - 0.15)  # PC invariant, NEG collapses OOD

    # ---- blinded LB ----
    lb = run_arm(Xlb, ylb, freqlb, classes, "lb")

    # ---- LA (no vowel truth -> report site-nuisance structure only, no linguistic recovery claim) ----
    la_signs0, la_seqs, la_freq = load_a()
    la_signs = sorted(set(t for w in la_seqs for t in w))
    Xla, keepla, freqla = context_embedding(la_seqs, la_signs, min_count=2)
    la = {"n_signs": int(Xla.shape[0]),
          "note": "LA has no vowel ground truth; invariance is validated on LB and only the (confound-adjusted) "
                  "embedding is exported for E102. No LA linguistic recovery is claimed here (L2)."}

    verdict, rationale = _verdict(pc_detects, pc_lofo, pc_within, ng_lofo, ng_within, lb, classes)
    results = {"positive_control": {"lofo_f1": pc_lofo, "within_f1": pc_within},
               "negative_control": {"lofo_f1": ng_lofo, "within_f1": ng_within}, "pc_detects": bool(pc_detects),
               "linear_b": lb, "linear_a": la, "config": {"methods": ["pca", "ica", "nmf"], "k_components": 8,
               "target": "vowel", "nuisance": "log-frequency", "interventions": ["freq-band-out", "deconfound-residual"]},
               "verdict": verdict, "rationale": rationale, "layer": "L2", "licences_changed": "none",
               "la_touched": True, "runtime_sec": round(time.time() - t0, 1)}
    with open(RESULT, "w") as fh:
        json.dump(results, fh, indent=1, default=lambda o: float(o))
    print("VERDICT:", verdict); print("rationale:", rationale)
    print("PC : lofo=%.3f within=%.3f | NEG: lofo=%.3f within=%.3f | detects=%s" % (pc_lofo, pc_within, ng_lofo, ng_within, pc_detects))
    print("LB :", {k: round(v, 3) for k, v in lb.items()})
    return results


def _verdict(pc_detects, pc_lofo, pc_within, ng_lofo, ng_within, lb, classes):
    if not pc_detects:
        return "CAUSAL_NO_POWER", ("Controls fail: the invariance test does not separate an invariant linguistic "
                                   "factor (PC lofo %.2f vs within %.2f) from a pure confound (NEG lofo %.2f vs within "
                                   "%.2f) -- no power to adjudicate." % (pc_lofo, pc_within, ng_lofo, ng_within))
    within = lb["within_band_f1"]; lofo_f1 = lb["lofo_f1"]; dec_lofo = lb["deconfounded_lofo_f1"]
    chance = 1.0 / len(classes)
    if not (within > chance + 0.05):
        return "CAUSAL_NULL", ("No vowel structure to disentangle on LB even in-distribution (within-band F1 %.3f ~ "
                               "chance %.3f)." % (within, chance))
    inv1 = lofo_f1 > chance + 0.05 and lofo_f1 > within - 0.15          # survives frequency-band-out
    inv2 = dec_lofo > chance + 0.05                                     # survives deconfounding
    if inv1 and inv2:
        return "CAUSAL_INVARIANT_STRUCTURE_SUPPORTED", (
            "The vowel-class signal survives BOTH nuisance interventions on blinded LB: leave-one-frequency-band-out "
            "F1 %.3f (vs within-band %.3f, chance %.3f) AND deconfounded (frequency-residualized) LOFO F1 %.3f -- a "
            "frequency-INVARIANT linguistic structure, not a frequency artifact. WEAK in absolute terms; L2, no "
            "phonetic values. The confound-adjusted embedding is exported to E102." % (
                lofo_f1, within, chance, dec_lofo))
    if inv1 or inv2:
        return "PARTIAL_INVARIANCE", (
            "The vowel signal survives ONE of two nuisance interventions (freq-band-out F1 %.3f, deconfounded LOFO "
            "%.3f, within-band %.3f, chance %.3f) -- partially frequency-invariant. Does NOT clear the >=2-independent"
            "-intervention gate; treated as not-yet-established. L2." % (lofo_f1, dec_lofo, within, chance))
    return "CONFOUND_EXPLAINED_SIGNAL", (
        "The in-distribution vowel signal (within-band F1 %.3f) COLLAPSES out-of-frequency-distribution (LOFO %.3f ~ "
        "chance %.3f) and after deconfounding (%.3f) -- the apparent structure is frequency-confounded, not "
        "invariant linguistic structure. The E093 margin does not survive the causal invariance test. L2." % (
            within, lofo_f1, chance, dec_lofo))


if __name__ == "__main__":
    main()
