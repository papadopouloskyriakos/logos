"""EPOCH-093 — LB->LA degradation surface (generic-best graph method).

E092 settled that Turing is not needed; the operative question for the campaign is: does ANY graph method
recover class structure at LINEAR A's data scale, or is LA below the detection threshold? LA vs LB differ mainly
in DATA VOLUME (LA ~4,245 tokens vs LB ~43,868; vocab 85 vs 89, nearly equal). So we degrade LB by token budget
(x min_count x subsample seed = >=100 cells), measure role/vowel recovery of the generic-best method
(Laplacian-eigenmap k-means) vs a per-cell permutation-null floor, locate where recovery collapses to chance, and
place LA's actual token budget (structural stat only, no phonetic values read) on that surface.
Verdicts: LINEAR_A_ABOVE / _NEAR / _BELOW_THRESHOLD / DEGRADATION_MODEL_INCONCLUSIVE.
"""
import sys, os, json, time
import numpy as np
import warnings
warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
REPO = "/home/claude-runner/gitlab/n8n/logos-linear-a-frontier-72h"; sys.path.insert(0, REPO)
import graphs as G
import evaluate as EV

EPOCH_DIR = os.path.join(REPO, "experiments/linear_a_frontier_72h/epochs/EPOCH-093")
RESULT = os.path.join(EPOCH_DIR, "result.json")
TOKEN_BUDGETS = [2000, 4000, 6000, 10000, 20000, 43868]   # LA operating point ~4245 tokens
MIN_COUNTS = [2, 3, 5]
SEEDS = [0, 1, 2, 3, 4, 5]                                  # 6 x 3 x 6 = 108 cells
K_FOR = {"role": 2, "vowel": 5}


def subsample(seqs, budget, seed):
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(seqs))
    out, tok = [], 0
    for i in order:
        out.append(seqs[i]); tok += len(seqs[i])
        if tok >= budget:
            break
    return out


def eigenmap_kmeans(g, k):
    ev, U = g["evals"], g["evecs"]
    nz = np.where(ev > 1e-9)[0][:max(k, 4)]
    return EV.kmeans(U[:, nz], k, seed=0)


def _freq_only(sk, fr, k):
    """Frequency-only baseline: cluster signs by log-frequency alone (the frequency-artifact control)."""
    logf = np.array([[np.log(fr[s] + 1)] for s in sk])
    return EV.kmeans(logf, k, seed=0)


def cell_recovery(seqs_sub, signs, labels, s2i, min_count):
    from collections import Counter
    fr = Counter(t for s in seqs_sub for t in s)
    graphs = G.build_graphs(seqs_sub, signs, s2i, min_count=min_count)
    out = {}
    for key in K_FOR:
        best = -1.0; bsigns = None; bpred = None
        for vname in ("SUBSTITUTION", "MULTILAYER"):
            g = graphs[vname]
            if g["n"] < K_FOR[key] + 1:
                continue
            pred = eigenmap_kmeans(g, K_FOR[key])
            m = EV.evaluate_clustering(pred, g["signs_kept"], labels, key)
            if m["macro_f1"] == m["macro_f1"] and m["macro_f1"] > best:
                best = m["macro_f1"]; bpred = pred; bsigns = g["signs_kept"]
        out[key] = {"f1": best, "n": graphs["SUBSTITUTION"]["n"]}
        if best >= 0:
            idx = [i for i, s in enumerate(bsigns) if labels[s][key] is not None]
            yt = np.array([labels[bsigns[i]][key] for i in idx]); yp = [bpred[i] for i in idx]
            rng = np.random.default_rng(99)
            nd = [EV.hungarian_macro_f1(list(rng.permutation(yt)), yp) for _ in range(100)]
            p95 = float(np.percentile(nd, 95))
            # frequency-only control on the SAME node set (the frequency-artifact guard)
            fpred = _freq_only(bsigns, fr, K_FOR[key])
            fm = EV.evaluate_clustering(fpred, bsigns, labels, key)["macro_f1"]
            out[key]["null_p95"] = p95
            out[key]["freq_only_f1"] = float(fm) if fm == fm else None
            out[key]["above_floor"] = bool(best > p95)
            # a MEANINGFUL (non-frequency-artifact) detection: beats the permutation floor AND frequency-only
            out[key]["above_freq"] = bool(fm == fm and best > fm + 0.03)
            out[key]["detected"] = bool(out[key]["above_floor"] and out[key]["above_freq"])
    return out


def main():
    os.makedirs(EPOCH_DIR, exist_ok=True); t0 = time.time()
    seqs, signs, freq = G.load_lb()
    labels = G.truth_labels(signs)
    s2i, i2s = G.blind(signs, seed=0)

    # LA operating point (structural only: token count; NO phonetic values read)
    from scripts.cross_script.data import load_a
    signs_a, seqs_a, freq_a = load_a()
    la_tokens = int(sum(len(s) for s in seqs_a))
    la_vocab = len(set(t for s in seqs_a for t in s))

    surface = []
    for budget in TOKEN_BUDGETS:
        for mc in MIN_COUNTS:
            role_fs, vowel_fs, role_det, vowel_det, vowel_freq, vowel_above = [], [], [], [], [], []
            for seed in SEEDS:
                sub = subsample(seqs, budget, seed)
                rec = cell_recovery(sub, signs, labels, s2i, mc)
                role_fs.append(rec["role"]["f1"]); vowel_fs.append(rec["vowel"]["f1"])
                role_det.append(rec["role"].get("detected", False))
                vowel_det.append(rec["vowel"].get("detected", False))
                vowel_above.append(rec["vowel"].get("above_floor", False))
                vowel_freq.append(rec["vowel"].get("freq_only_f1") or 0.0)
            surface.append({"budget": budget, "min_count": mc,
                            "role_f1_mean": float(np.mean(role_fs)), "role_f1_sd": float(np.std(role_fs)),
                            "vowel_f1_mean": float(np.mean(vowel_fs)), "vowel_f1_sd": float(np.std(vowel_fs)),
                            "vowel_freq_only_mean": float(np.mean(vowel_freq)),
                            "role_detected_frac": float(np.mean(role_det)),
                            "vowel_detected_frac": float(np.mean(vowel_det)),
                            "vowel_above_floor_frac": float(np.mean(vowel_above))})

    # locate LA on the surface: nearest budget to la_tokens, min_count=3 (matches E091/E092)
    la_budget = min(TOKEN_BUDGETS, key=lambda b: abs(b - la_tokens))
    la_cell = [c for c in surface if c["min_count"] == 3 and c["budget"] == la_budget][0]
    full_cell = [c for c in surface if c["min_count"] == 3 and c["budget"] == max(TOKEN_BUDGETS)][0]

    verdict, rationale = _verdict(la_cell, full_cell, la_tokens, la_budget)
    results = {"surface": surface, "la_operating_point": {"la_tokens": la_tokens, "la_vocab": la_vocab,
               "nearest_budget": la_budget, "la_cell": la_cell, "full_budget_cell": full_cell},
               "verdict": verdict, "rationale": rationale, "config": {"token_budgets": TOKEN_BUDGETS,
               "min_counts": MIN_COUNTS, "seeds": SEEDS, "method": "eigenmap_kmeans (generic-best, E092)",
               "k_for": K_FOR, "n_cells": len(surface) * len(SEEDS)},
               "layer": "L2", "licences_changed": "none", "la_touched": True,
               "runtime_sec": round(time.time() - t0, 1)}
    with open(RESULT, "w") as fh:
        json.dump(results, fh, indent=1, default=lambda o: float(o))
    print("VERDICT:", verdict); print("rationale:", rationale)
    print("LA: tokens=%d vocab=%d -> nearest budget %d" % (la_tokens, la_vocab, la_budget))
    print("\nbudget  mc  vowel_f1  vowel_freq_only  vowel_detected  role_f1  role_detected")
    for c in surface:
        if c["min_count"] == 3:
            print("%6d  %d   %.3f     %.3f            %.2f            %.3f    %.2f" % (
                c["budget"], c["min_count"], c["vowel_f1_mean"], c["vowel_freq_only_mean"],
                c["vowel_detected_frac"], c["role_f1_mean"], c["role_detected_frac"]))
    return results


def _verdict(la_cell, full_cell, la_tokens, la_budget):
    # The MEANINGFUL threshold uses the vowel (phonetic-class) channel and demands a NON-frequency-artifact
    # detection: above the permutation floor AND above a frequency-only baseline (+0.03). The frequency guard is
    # mandatory -- position->C/V and reduced-seed were both refuted as frequency artifacts in this campaign.
    v_full = full_cell["vowel_detected_frac"]        # meaningful detection at max data
    v_la = la_cell["vowel_detected_frac"]            # meaningful detection at LA scale
    r_la = la_cell["role_detected_frac"]
    if v_full < 0.5:
        return "DEGRADATION_MODEL_INCONCLUSIVE", (
            "The MEANINGFUL (vowel/phonetic-class) channel does not survive the frequency-artifact guard even at "
            "full LB budget: a graph-eigenmap partition beats a frequency-only baseline in only %.0f%% of "
            "subsamples (vowel macro-F1 %.3f vs frequency-only %.3f). With no stable phonetic-class detection "
            "regime at maximum data, the surface cannot place a reliable threshold for LA. The trivial role "
            "(syllabogram-vs-other/degree) channel IS data-sensitive -- detected in %.0f%% of cells at LA scale vs "
            "%.0f%% at full budget -- so LA's data volume constrains even the trivial structural channel, but the "
            "phonetic-class signal is frequency-confounded, not merely data-limited. No LA reading licensed (L2)." % (
                100 * v_full, full_cell["vowel_f1_mean"], full_cell["vowel_freq_only_mean"],
                100 * r_la, 100 * full_cell["role_detected_frac"]))
    if v_la >= 0.5:
        return "LINEAR_A_ABOVE_THRESHOLD", (
            "At LA's data scale (~%d tokens) the graph method's vowel recovery beats BOTH its permutation floor and "
            "a frequency-only baseline in %.0f%% of subsamples -- a non-frequency-artifact phonetic-class signal "
            "survives at LA's data volume. WEAK in absolute terms (vowel macro-F1 %.3f) and blinded-LB only: this "
            "licenses NO LA sound values (L2)." % (la_tokens, 100 * v_la, la_cell["vowel_f1_mean"]))
    if v_la >= 0.2:
        return "LINEAR_A_NEAR_THRESHOLD", (
            "At LA's scale (~%d tokens) a non-frequency-artifact vowel signal survives in only %.0f%% of subsamples "
            "-- LA sits NEAR the threshold where the phonetic-class signal separates from a frequency baseline." % (
                la_tokens, 100 * v_la))
    return "LINEAR_A_BELOW_THRESHOLD", (
        "At LA's data scale (~%d tokens) the vowel channel does NOT beat a frequency-only baseline (meaningful "
        "detection in %.0f%% of subsamples) even though it does at full LB budget (%.0f%%). The non-frequency "
        "phonetic-class signal is below the detection threshold at LA's data volume." % (
            la_tokens, 100 * v_la, 100 * v_full))


if __name__ == "__main__":
    main()
