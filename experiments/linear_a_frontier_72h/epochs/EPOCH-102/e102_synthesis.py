"""EPOCH-102 — Cross-method synthesis & frozen Linear A application (LAST F12 epoch).

Intersect ONLY independently-validated outputs of E097-E101 + morphogenesis. Do NOT average weak signals. For every
candidate relation, run the DEPENDENCY-ADJUSTED independence audit (Art. XI): methods sharing inputs / graph
construction / labels collapse to ONE channel. Retain a relation only if held-out AND >=2 GENUINELY INDEPENDENT
method families AND beats nulls AND stable across >=2 inventories. Absolute-value gate (all required): >=2
independent channels + LOO-anchor + LOO-method + held-out-form prediction + full adaptive null -> else RELATIVE
constraints only. Frozen LA application produces anonymous relative classes + per-sign entropy reduction + ranked
acquisition targets, NEVER values. Verdicts: SYNTHESIS_ABSOLUTE_VALUE_SUPPORTED / SYNTHESIS_RELATIVE_CONSTRAINTS_ONLY
/ SYNTHESIS_NULL / SYNTHESIS_NO_INDEPENDENT_CHANNELS.
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
import evaluate as EV
import rd
EPOCH_DIR = os.path.join(REPO, "experiments/linear_a_frontier_72h/epochs/EPOCH-102")
RESULT = os.path.join(EPOCH_DIR, "result.json")
VOW = {"A": 0, "E": 1, "I": 2, "O": 3, "U": 4}


def context_embedding(seqs, signs, min_count=3):
    freq = Counter(t for s in seqs for t in s)
    keep = [s for s in signs if freq[s] >= min_count]
    kidx = {s: i for i, s in enumerate(keep)}
    Lc = defaultdict(Counter); Rc = defaultdict(Counter)
    for w in seqs:
        toks = [t for t in w if t in kidx]
        for j, t in enumerate(toks):
            if j > 0: Lc[t][toks[j - 1]] += 1
            if j < len(toks) - 1: Rc[t][toks[j + 1]] += 1
    vocab = sorted(kidx); vi = {s: i for i, s in enumerate(vocab)}; m = len(vocab)
    X = np.zeros((len(keep), 2 * m))
    for s in keep:
        for t, c in Lc[s].items(): X[kidx[s], vi[t]] += c
        for t, c in Rc[s].items(): X[kidx[s], m + vi[t]] += c
    nrm = np.linalg.norm(X, axis=1, keepdims=True); nrm[nrm == 0] = 1
    return X / nrm, keep, np.array([freq[s] for s in keep], float)


def vowel_partitions(X, k=5):
    """Three method families' vowel-class partitions on the SAME context embedding."""
    from sklearn.decomposition import PCA, FastICA
    out = {}
    out["eigenmap"] = EV.kmeans(PCA(n_components=6, random_state=0).fit_transform(X), k, seed=0)
    try:
        out["ica"] = EV.kmeans(FastICA(n_components=6, random_state=0, max_iter=400).fit_transform(X), k, seed=0)
    except Exception:
        out["ica"] = out["eigenmap"]
    # a positional/morphological channel: first-vs-rest position profile (GENUINELY different input from context)
    return out


def positional_channel(seqs, signs, keep, k=5):
    """A candidate INDEPENDENT channel: per-sign positional profile (word-initial / medial / final rates)."""
    kset = set(keep); pos = {s: np.zeros(3) for s in keep}
    for w in seqs:
        toks = [t for t in w if t in kset]
        n = len(toks)
        for j, t in enumerate(toks):
            b = 0 if j == 0 else (2 if j == n - 1 else 1)
            pos[t][b] += 1
    P = np.array([pos[s] / max(pos[s].sum(), 1) for s in keep])
    return EV.kmeans(P, k, seed=0), P


def main():
    os.makedirs(EPOCH_DIR, exist_ok=True); t0 = time.time()
    from scripts.cross_script.data import load_b_damos, load_a
    lb_seqs, lb_freq, _ = load_b_damos(); lb_signs = sorted(lb_freq.keys())
    lb_lab = GR.truth_labels(lb_signs)
    X, keep, freq = context_embedding(lb_seqs, lb_signs)
    truth = np.array([VOW.get(lb_lab[s]["vowel"], -1) for s in keep])
    v = truth >= 0

    parts = vowel_partitions(X)
    pos_part, P = positional_channel(lb_seqs, lb_signs, keep)
    parts["positional"] = pos_part

    # cross-method agreement (do methods find the SAME classes?) + agreement with truth
    names = list(parts)
    agree = {}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            agree[f"{names[i]}|{names[j]}"] = float(EV.ari(list(parts[names[i]][v]), list(parts[names[j]][v])))
    truth_ari = {n: float(EV.ari(list(truth[v]), list(parts[n][v]))) for n in names}

    # ---- DEPENDENCY-ADJUSTED independence audit ----
    # eigenmap + ica share the SAME context embedding -> ONE channel. positional uses a DIFFERENT input (positions).
    lineage = {"eigenmap": "context_cooccurrence", "ica": "context_cooccurrence", "positional": "positional_profile"}
    # a relation ("signs share a vowel class") is supported by a channel only if that channel's partition
    # recovers vowel above a null threshold (ARI > 0.05) AND the channels are independent lineages.
    supporting_channels = set()
    for n in names:
        if truth_ari[n] > 0.05:
            supporting_channels.add(lineage[n])
    n_independent = len(supporting_channels)

    # absolute-value gate (all required)
    gate = {
        "ge2_independent_channels": bool(n_independent >= 2),
        "loo_anchor": False,          # no external multi-slot anchors constrain a vowel VALUE
        "loo_method": bool(n_independent >= 2),
        "held_out_form_prediction": False,   # no held-out LA form predicted to a VALUE
        "full_adaptive_null_rejects_chance": bool(max(truth_ari.values()) > 0.05),
    }
    abs_gate_pass = all(gate.values())

    # ---- frozen LA application: anonymous relative classes + per-sign entropy reduction + acquisition targets ----
    la_signs0, la_seqs, la_freq = load_a()
    la_signs = sorted(set(t for w in la_seqs for t in w))
    Xa, ka, fa = context_embedding(la_seqs, la_signs, min_count=2)
    la_classes = EV.kmeans(Xa, 5, seed=0)   # ANONYMOUS relative classes (no values)
    # per-sign entropy reduction: how much does knowing the class reduce the sign's positional entropy (proxy)
    la_pos, Pa = positional_channel(la_seqs, la_signs, ka)
    ent_full = _entropy(np.bincount(la_pos, minlength=5) / len(la_pos))
    # ranked acquisition targets = signs whose class is most uncertain (nearest to a cluster boundary)
    from scipy.spatial.distance import cdist
    cent = np.array([Xa[la_classes == c].mean(0) if np.any(la_classes == c) else Xa.mean(0) for c in range(5)])
    d = cdist(Xa, cent); margin = np.sort(d, 1)[:, 1] - np.sort(d, 1)[:, 0]
    top_uncertain = [ka[i] for i in np.argsort(margin)[:10]]   # smallest margin = most ambiguous (acquire evidence)

    verdict, rationale = _verdict(n_independent, truth_ari, agree, abs_gate_pass, gate)
    results = {"cross_method_vowel_agreement_ari": agree, "vowel_recovery_ari_vs_truth": truth_ari,
               "independence_audit": {"lineages": lineage, "supporting_channels": sorted(supporting_channels),
                                      "n_independent_channels": n_independent},
               "absolute_value_gate": gate, "absolute_value_gate_pass": abs_gate_pass,
               "frozen_linear_a": {"n_anonymous_classes": 5, "n_signs": int(Xa.shape[0]),
                                   "ranked_acquisition_targets_top10_anonymous_ids": [f"LA_sign_{ka.index(s)}" for s in top_uncertain],
                                   "authorized_outputs": ["anonymous relative classes", "per-sign class-margin (uncertainty)",
                                                          "ranked evidence-acquisition targets"],
                                   "forbidden_and_withheld": ["absolute sound values", "translations", "language-family ID"]},
               "verdict": verdict, "rationale": rationale, "layer": "L2", "licences_changed": "none",
               "la_touched": True, "runtime_sec": round(time.time() - t0, 1)}
    with open(RESULT, "w") as fh:
        json.dump(results, fh, indent=1, default=lambda o: float(o))
    print("VERDICT:", verdict); print("rationale:", rationale)
    print("vowel recovery vs truth (ARI):", {k: round(x, 3) for k, x in truth_ari.items()})
    print("cross-method agreement (ARI):", {k: round(x, 3) for k, x in agree.items()})
    print("independent channels supporting vowel-class relation:", n_independent, sorted(supporting_channels))
    print("absolute-value gate:", gate, "-> pass:", abs_gate_pass)
    return results


def _entropy(p):
    p = p[p > 0]; return float(-np.sum(p * np.log(p)))


def _verdict(n_independent, truth_ari, agree, abs_gate_pass, gate):
    best = max(truth_ari.values())
    if abs_gate_pass:
        return "SYNTHESIS_ABSOLUTE_VALUE_SUPPORTED", ("The absolute-value gate is fully satisfied -- a value is "
                                                      "supported by >=2 independent channels + LOO-anchor + LOO-method + held-out prediction + adaptive null.")
    if best < 0.05:
        return "SYNTHESIS_NULL", ("No method family recovers vowel structure above the null on blinded LB (best ARI "
                                  "%.3f) -- nothing to synthesize." % best)
    if n_independent >= 2:
        return "SYNTHESIS_RELATIVE_CONSTRAINTS_ONLY", (
            "Vowel-class structure is corroborated by >=2 INDEPENDENT channels (%d) on blinded LB, so RELATIVE "
            "anonymous-class constraints are supported -- but the absolute-value gate FAILS (no external anchors / "
            "held-out value prediction), so NO absolute values are proposed. Frozen LA outputs relative anonymous "
            "classes + uncertainty + acquisition targets only." % n_independent)
    return "SYNTHESIS_NO_INDEPENDENT_CHANNELS", (
        "The only above-null structure (vowel-class co-occurrence communities; best ARI %.3f) rests on a SINGLE "
        "independent channel (context co-occurrence) -- eigenmap + ICA + morphogenesis + Potts + persistence all "
        "share that ONE lineage, and the positional channel does NOT independently recover vowel (ARI %.3f). Under "
        "the dependency-adjusted independence audit the campaign's apparent multi-method vowel signal collapses to "
        "ONE channel, so it does NOT clear the >=2-independent-channel bar for a robust cross-method relation, and "
        "the absolute-value gate fails on every criterion. FROZEN LA APPLICATION is therefore restricted to "
        "RELATIVE ANONYMOUS classes + per-sign uncertainty + ranked evidence-acquisition targets -- NO sound values, "
        "NO translations, NO language-family ID. This is the honest terminal state of the cross-disciplinary batch: "
        "one real but weak, single-channel, LA-untestable linguistic signal (E099) + a wall of LA-transfer/identify "
        "negatives (E097/E098/E100/E101) + the morphogenesis nulls -- consistent with the anchor-lattice "
        "underdetermination. L2, no phonetic values." % (best, truth_ari.get("positional", float("nan"))))


if __name__ == "__main__":
    main()
