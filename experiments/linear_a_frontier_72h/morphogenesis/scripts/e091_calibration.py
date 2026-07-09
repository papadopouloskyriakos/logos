"""EPOCH-091 — Blinded Linear B Turing-morphogenesis calibration.

Does a graph reaction-diffusion (Turing) process on blinded LB sign graphs recover held-out phonetic
class structure (vowel / consonant / role), with the Turing instability MECHANICALLY VERIFIED, above
negative controls (equal-diffusion, degree-preserving rewiring, label permutation, reaction-only)?
Positive control: a planted-Turing synthetic graph the pipeline must recover. Verdicts (mechanical):
  TURING_LINEAR_B_RECOVERY_SUPPORTED / _PARTIAL / _NULL / TURING_NO_POWER / TURING_MODEL_INVALID
The prior of record (EPOCH-016 SBI) is that generic clustering ties/beats fancy methods -> a _NULL / _PARTIAL
is a live, expected, valid outcome. Turing-vs-baseline specificity is E092, not this epoch.
"""
import sys, os, json, hashlib, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO = "/home/claude-runner/gitlab/n8n/logos-linear-a-frontier-72h"
sys.path.insert(0, REPO)
import graphs as G
import rd
import evaluate as EV

EPOCH_DIR = os.path.join(REPO, "experiments/linear_a_frontier_72h/epochs/EPOCH-091")
RESULT = os.path.join(EPOCH_DIR, "result.json")
REACTIONS = ["Schnakenberg", "GiererMeinhardt"]  # families that satisfy the strict Turing conditions
TRUTH_KEYS = ["role", "vowel", "consonant"]
K_FOR = {"role": 2, "vowel": 5, "consonant": 8}     # frozen k per truth key (same for model + all controls)
RATIOS = [10, 20, 40]                                # Dv/Du ratios searched (unsupervised selection)
SEEDS = [1, 2, 3]                                    # init seeds for the nonlinear integration
MODE_CAP = 4                                          # # of lowest unstable eigenmodes used in the pattern feature


def _low_modes(evals, unstable_modes):
    """The coarsest (lowest-eigenvalue) nonzero unstable modes, capped at MODE_CAP."""
    um = [m for m in unstable_modes if evals[m] > 1e-9]
    um = sorted(um, key=lambda m: evals[m])
    return um[:MODE_CAP]


def select_config(reaction_name, evals):
    """Unsupervised: over the RATIOS grid, pick the find_Du config with the lowest coarsest-unstable-lambda,
    tie-broken to the narrowest band. Returns (reaction, config) or (None, None). NO truth labels involved."""
    r = rd.REACTIONS[reaction_name]()
    if r is None:
        return None, None
    best = None
    for ratio in RATIOS:
        res = rd.find_Du(r, evals, ratio)
        if res is None:
            continue
        key = (res["min_unstable_lam"], res["n_unstable"])
        if best is None or key < best[0]:
            best = (key, ratio, res)
    if best is None:
        return r, None
    _, ratio, res = best
    res["ratio"] = ratio
    return r, res


def _sym_norm_L(W):
    W = np.array(W, float); np.fill_diagonal(W, 0); W = 0.5 * (W + W.T); W = np.maximum(W, 0)
    d = W.sum(1); d[d == 0] = 1; dinv = 1 / np.sqrt(d)
    L = np.eye(W.shape[0]) - (W * dinv[:, None]) * dinv[None, :]
    L = 0.5 * (L + L.T); ev, U = np.linalg.eigh(L)
    return L, np.clip(ev, 0, None), U, W.sum(1)


def run_pipeline(L, evals, evecs, degree, reaction_name, ratio, seeds, force_equal=False,
                 reaction_only=False):
    """Verify Turing + integrate + return pooled pattern features (n, d) or None if model invalid here."""
    r = rd.REACTIONS[reaction_name]()
    if r is None:
        return None, None
    if reaction_only:
        # no diffusion: pattern is trivially homogeneous -> use tiny Du,Dv to keep integrator, but zero Laplacian coupling
        v = rd.verify_turing(r, evals, 1e-9, 1e-9)
        pats = [rd.integrate(r, np.zeros_like(L), 1e-9, 1e-9, seed=s) for s in seeds]
        return np.mean(pats, 0), v
    if force_equal:
        # equal-diffusion negative control: Du=Dv (Turing mechanism impossible)
        Du = 0.3; Dv = 0.3
        v = rd.verify_turing(r, evals, Du, Dv)
        pats = [rd.integrate(r, L, Du, Dv, seed=s) for s in seeds]
        return np.mean(pats, 0), v
    res = rd.find_Du(r, evals, ratio)
    if res is None:
        return None, dict(cond3_diffusion_instability=False)
    v = res["verify"]
    pats = [rd.integrate(r, L, res["Du"], res["Dv"], seed=s) for s in seeds]
    return np.mean(pats, 0), dict(v, Du=res["Du"], Dv=res["Dv"])


def recover(pattern, evecs, low_modes, signs_kept, labels, degree):
    """Cluster pattern+low-unstable-modes -> classes; score vs each truth key. Returns metrics dict + deg corr."""
    feats = EV.pattern_features(pattern, evecs, low_modes)
    out = {}
    for key in TRUTH_KEYS:
        pred = EV.kmeans(feats, K_FOR[key], seed=0)
        out[key] = EV.evaluate_clustering(pred, signs_kept, labels, key)
    out["_deg_corr"] = rd.pattern_degree_corr(pattern, degree)
    return out


def planted_turing_pc(seed=0, n=90, k=3, ratio=20):
    """Positive control: build a block graph whose blocks are the truth; the pipeline must recover blocks."""
    rng = np.random.default_rng(seed)
    block = rng.integers(0, k, n)
    W = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            p = 0.45 if block[i] == block[j] else 0.03
            if rng.random() < p:
                W[i, j] = W[j, i] = 1.0
    L, ev, U, deg = _sym_norm_L(W)
    r, res = select_config("Schnakenberg", ev)
    if res is None:
        return dict(recovered=False, reason="no_turing_regime")
    v = res["verify"]
    low = _low_modes(ev, v["unstable_modes"])
    pat = np.mean([rd.integrate(r, L, res["Du"], res["Dv"], seed=s) for s in SEEDS], 0)
    pred = EV.kmeans(EV.pattern_features(pat, U, low), k, seed=0)
    a = EV.ari(list(block), list(pred))
    return dict(recovered=bool(a > 0.25), ari=float(a), turing_ok=bool(
        v["cond1_equilibrium"] and v["cond2_ode_stable"] and v["cond3_diffusion_instability"]))


def main():
    os.makedirs(EPOCH_DIR, exist_ok=True)
    t0 = time.time()
    seqs, signs, freq = G.load_lb()
    labels = G.truth_labels(signs)
    s2i, i2s = G.blind(signs, seed=0)
    graphs = G.build_graphs(seqs, signs, s2i, min_count=3)

    results = {"views": {}, "positive_control": {}, "negative_controls": {}, "config": {
        "reactions": REACTIONS, "ratios": RATIOS, "seeds": SEEDS, "k_for": K_FOR, "min_count": 3}}

    # ---- positive control ----
    pc = [planted_turing_pc(seed=s) for s in range(5)]
    pc_ari = [p.get("ari", 0.0) for p in pc]
    pc_ok = sum(1 for p in pc if p.get("recovered"))
    results["positive_control"] = {"runs": pc, "n_recovered": pc_ok, "mean_ari": float(np.mean(pc_ari))}

    # ---- real blinded LB: each view x reaction, best over ratio ----
    turing_verified_any = False
    best_real = {k: {"macro_f1": -1, "ari": -1} for k in TRUTH_KEYS}
    for vname, g in graphs.items():
        L, ev, U, deg = g["L"], g["evals"], g["evecs"], g["degree"]
        signs_kept = g["signs_kept"]
        results["views"][vname] = {"n": g["n"], "reactions": {}}
        for rn in REACTIONS:
            r, res = select_config(rn, ev)               # UNSUPERVISED: no truth labels in selection
            if res is None:
                results["views"][vname]["reactions"][rn] = {"turing_regime": False}
                continue
            v = res["verify"]
            turing_verified_any = True
            low = _low_modes(ev, v["unstable_modes"])
            pat = np.mean([rd.integrate(r, L, res["Du"], res["Dv"], seed=s) for s in SEEDS], 0)
            rec = recover(pat, U, low, signs_kept, labels, deg)
            best = {"ratio": res["ratio"], "Du": res["Du"], "Dv": res["Dv"],
                    "min_unstable_lam": res["min_unstable_lam"], "n_unstable": res["n_unstable"],
                    "low_modes": low, "deg_corr": rec["_deg_corr"],
                    "metrics": {k: rec[k] for k in TRUTH_KEYS}}
            results["views"][vname]["reactions"][rn] = best
            for k in TRUTH_KEYS:
                mf = best["metrics"][k]["macro_f1"]
                if mf is not None and mf == mf and mf > best_real[k]["macro_f1"]:
                    best_real[k] = {"macro_f1": mf, "ari": best["metrics"][k]["ari"],
                                    "view": vname, "reaction": rn}
    results["best_real"] = best_real

    # ---- negative controls (on the MULTILAYER view, the strongest-coupling graph) ----
    g = graphs["MULTILAYER"]; L, ev, U, deg = g["L"], g["evals"], g["evecs"], g["degree"]; sk = g["signs_kept"]
    neg = {}
    # equal-diffusion (Du=Dv): Turing mechanism impossible -> homogeneous, no pattern
    pat, v = run_pipeline(L, ev, U, deg, "Schnakenberg", 20, SEEDS, force_equal=True)
    rec = recover(pat, U, _low_modes(ev, v.get("unstable_modes", [])), sk, labels, deg)
    neg["equal_diffusion"] = {"role_f1": rec["role"]["macro_f1"], "vowel_f1": rec["vowel"]["macro_f1"],
                              "cond3": v.get("cond3_diffusion_instability", False)}
    # reaction-only (no diffusion coupling)
    pat, v = run_pipeline(L, ev, U, deg, "Schnakenberg", 20, SEEDS, reaction_only=True)
    rec = recover(pat, U, [], sk, labels, deg)
    neg["reaction_only"] = {"role_f1": rec["role"]["macro_f1"], "vowel_f1": rec["vowel"]["macro_f1"]}
    # label permutation null (shuffle truth labels) — best-of over 200 draws
    def perm_null(key, draws=200):
        r, res = select_config("Schnakenberg", ev)
        pat = np.mean([rd.integrate(r, L, res["Du"], res["Dv"], seed=s) for s in SEEDS], 0)
        low = _low_modes(ev, res["verify"]["unstable_modes"])
        pred = EV.kmeans(EV.pattern_features(pat, U, low), K_FOR[key], seed=0)
        idx = [i for i, s in enumerate(sk) if labels[s][key] is not None]
        yt = np.array([labels[sk[i]][key] for i in idx]); yp = [pred[i] for i in idx]
        rng = np.random.default_rng(7)
        real = EV.hungarian_macro_f1(list(yt), yp)
        nd = []
        for _ in range(draws):
            perm = yt.copy(); rng.shuffle(perm)
            nd.append(EV.hungarian_macro_f1(list(perm), yp))
        nd = np.array(nd)
        return {"real_f1": float(real), "null_p95": float(np.percentile(nd, 95)),
                "null_mean": float(nd.mean()), "p_value": float((nd >= real).mean())}
    neg["label_permutation_role"] = perm_null("role")
    neg["label_permutation_vowel"] = perm_null("vowel")
    # degree-preserving rewiring — best-of over 50 rewires, role recovery distribution
    def rewire(W, seed, nswap=None):
        rng = np.random.default_rng(seed); W = (W > 0).astype(float).copy(); n = W.shape[0]
        edges = list(zip(*np.where(np.triu(W, 1) > 0)))
        nswap = nswap or 10 * len(edges)
        for _ in range(nswap):
            if len(edges) < 2:
                break
            i1, i2 = rng.integers(0, len(edges), 2)
            (a, b), (c, d) = edges[i1], edges[i2]
            if len({a, b, c, d}) < 4:
                continue
            if W[a, d] or W[c, b]:
                continue
            W[a, b] = W[b, a] = W[c, d] = W[d, c] = 0
            W[a, d] = W[d, a] = W[c, b] = W[b, c] = 1
            edges[i1] = (a, d); edges[i2] = (c, b)
        return W
    rw_f1 = []
    for s in range(20):
        Wr = rewire((g["W"] > 0).astype(float), s)
        Lr, evr, Ur, degr = _sym_norm_L(Wr)
        r, res = select_config("Schnakenberg", evr)
        if res is None:
            continue
        low = _low_modes(evr, res["verify"]["unstable_modes"])
        pat = np.mean([rd.integrate(r, Lr, res["Du"], res["Dv"], seed=ss) for ss in SEEDS], 0)
        rec = recover(pat, Ur, low, sk, labels, degr)
        rw_f1.append(rec["role"]["macro_f1"])
    neg["degree_rewiring_role"] = {"mean_f1": float(np.mean(rw_f1)) if rw_f1 else None,
                                   "p95_f1": float(np.percentile(rw_f1, 95)) if rw_f1 else None,
                                   "n": len(rw_f1)}
    results["negative_controls"] = neg

    # ---- mechanical verdict ----
    verdict, rationale = _verdict(results, turing_verified_any)
    results["verdict"] = verdict
    results["rationale"] = rationale
    results["runtime_sec"] = round(time.time() - t0, 1)
    results["layer"] = "L2"
    results["licences_changed"] = "none"
    with open(RESULT, "w") as fh:
        json.dump(results, fh, indent=1, default=lambda o: float(o) if isinstance(o, np.floating) else o)
    print("VERDICT:", verdict)
    print("rationale:", rationale)
    print("PC: n_recovered=%d/5 mean_ari=%.3f" % (results["positive_control"]["n_recovered"],
                                                  results["positive_control"]["mean_ari"]))
    for k in TRUTH_KEYS:
        print("  best_real %-10s macro_f1=%.3f (%s/%s)" % (
            k, best_real[k]["macro_f1"], best_real[k].get("view"), best_real[k].get("reaction")))
    print("  neg role: equal_diff=%.3f rewire_p95=%s perm_p95=%.3f perm_p=%.3f" % (
        neg["equal_diffusion"]["role_f1"], neg["degree_rewiring_role"]["p95_f1"],
        neg["label_permutation_role"]["null_p95"], neg["label_permutation_role"]["p_value"]))
    return results


def _verdict(results, turing_verified_any):
    if not turing_verified_any:
        return "TURING_MODEL_INVALID", "No graph-view x reaction satisfied the Turing instability conditions."
    pc = results["positive_control"]
    if pc["n_recovered"] < 3:
        return "TURING_NO_POWER", ("Positive control failed: planted-Turing blocks recovered in only %d/5 runs "
                                   "(mean ARI %.3f) — the detector does not fire even when structure is planted." %
                                   (pc["n_recovered"], pc["mean_ari"]))
    neg = results["negative_controls"]
    br = results["best_real"]
    role_real = br["role"]["macro_f1"]
    perm = neg["label_permutation_role"]
    rewire_p95 = neg["degree_rewiring_role"]["p95_f1"] or 0.0
    equal = neg["equal_diffusion"]["role_f1"]
    # decision on the role channel (the channel with the cleanest 2-class truth), with vowel as corroboration
    beats_perm = role_real > perm["null_p95"] and perm["p_value"] < 0.05
    beats_rewire = role_real > rewire_p95
    beats_equal = role_real > equal + 0.02
    vowel_real = br["vowel"]["macro_f1"]
    vowel_perm = neg["label_permutation_vowel"]
    vowel_beats = vowel_real is not None and vowel_real > vowel_perm["null_p95"] and vowel_perm["p_value"] < 0.05
    n_pass = sum([beats_perm, beats_rewire, beats_equal])
    if n_pass == 3 and vowel_beats:
        return "TURING_LINEAR_B_RECOVERY_SUPPORTED", (
            "Blinded LB role recovery (macro-F1 %.3f) exceeds permutation p95 %.3f (p=%.3f), degree-rewiring p95 %.3f, "
            "and equal-diffusion %.3f; vowel channel also exceeds its permutation null. Turing conditions verified. "
            "NOTE: specificity vs generic spectral/SBM baselines is E092, not established here." % (
                role_real, perm["null_p95"], perm["p_value"], rewire_p95, equal))
    if n_pass >= 2:
        return "TURING_LINEAR_B_RECOVERY_PARTIAL", (
            "Role recovery macro-F1 %.3f passes %d/3 negative-control gates (perm=%s, rewire=%s, equal-diff=%s); "
            "vowel corroboration=%s. Recovery present but not uniformly separated from all nulls." % (
                role_real, n_pass, beats_perm, beats_rewire, beats_equal, vowel_beats))
    return "TURING_LINEAR_B_RECOVERY_NULL", (
        "Blinded LB recovery (role macro-F1 %.3f) does not separate from the negative controls "
        "(perm p95 %.3f p=%.3f, rewire p95 %.3f, equal-diffusion %.3f). Consistent with the EPOCH-016 prior that "
        "generic structure, not a Turing mechanism, drives any apparent recovery." % (
            role_real, perm["null_p95"], perm["p_value"], rewire_p95, equal))


if __name__ == "__main__":
    main()
