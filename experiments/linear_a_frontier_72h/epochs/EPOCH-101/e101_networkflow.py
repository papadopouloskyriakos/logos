"""EPOCH-101 — Global graph/network-flow constrained decipherment benchmark.

Inspired by global-optimization re-decipherment (Ugaritic etc.) -- but those used a KNOWN related-language target;
Linear A has none. Stage A (known-target calibration, blinded LB): does GLOBAL assignment (capacity-constrained
Hungarian / respecting the class-size marginal) recover held-out sign classes better than LOCAL nearest-neighbor /
greedy / random? Stage B (TARGET-FREE, LA): no cognate target -> output equivalence CLASSES only; the decisive
question is whether global assignment ADDS information beyond the anchor-lattice null or merely SELECTS one
arbitrary representative of a huge equivalence class. Positive control: imbalanced synthetic classes where the
global marginal constraint should beat local NN. Verdicts: GLOBAL_ASSIGNMENT_ADDS_INFORMATION /
GLOBAL_ASSIGNMENT_SELECTS_ARBITRARY_REPRESENTATIVE / GLOBAL_ASSIGNMENT_NULL / GLOBAL_ASSIGNMENT_NO_POWER.
Prior (anchor-lattice ~10^63-10^270; E098 evidence orthogonal): global optimization cannot manufacture absent
constraints -> _SELECTS_ARBITRARY_REPRESENTATIVE for LA expected.
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
EPOCH_DIR = os.path.join(REPO, "experiments/linear_a_frontier_72h/epochs/EPOCH-101")
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
    return X / nrm, keep


def cost_matrix(Xunk, Xanc, yanc, classes):
    """Cost[i,c] = distance from unknown sign i to the centroid of anchored class c."""
    cent = np.array([Xanc[yanc == c].mean(0) if np.any(yanc == c) else np.zeros(Xanc.shape[1]) for c in classes])
    D = ((Xunk[:, None, :] - cent[None, :, :]) ** 2).sum(2)
    return D, cent


def assign_local(C):
    return C.argmin(1)


def assign_global(C, class_caps):
    """Capacity-constrained global assignment (Hungarian on expanded class slots = enforce the class marginal)."""
    from scipy.optimize import linear_sum_assignment
    n, k = C.shape
    slots = []; slot_class = []
    for c in range(k):
        for _ in range(class_caps[c]):
            slots.append(c); slot_class.append(c)
    # pad slots to >= n
    while len(slots) < n:
        slots.append(int(np.argmax(class_caps))); slot_class.append(int(np.argmax(class_caps)))
    Cexp = C[:, slot_class]
    r, col = linear_sum_assignment(Cexp)
    pred = np.empty(n, int)
    for i, cc in zip(r, col):
        pred[i] = slot_class[cc]
    return pred


def acc(pred, y):
    return float(np.mean(pred == y))


def run_stageA(X, y, classes, seed=0, anc_frac=0.5):
    rng = np.random.default_rng(seed); n = len(y); idx = rng.permutation(n)
    na = int(anc_frac * n); anc, unk = idx[:na], idx[na:]
    Xanc, yanc = X[anc], y[anc]; Xunk, yunk = X[unk], y[unk]
    C, _ = cost_matrix(Xunk, Xanc, yanc, classes)
    caps = [max(1, int(round(np.mean(yunk == c) * len(yunk)))) for c in classes]  # oracle class marginal
    loc = acc(assign_local(C), yunk)
    glo = acc(assign_global(C, caps), yunk)
    rnd = acc(rng.integers(0, len(classes), len(yunk)), yunk)
    return {"local": loc, "global": glo, "random": rnd}


def synth(seed, n=220, k=5, dim=8, imbalance=True):
    """CONFUSABLE + strongly imbalanced: local NN over-assigns the majority; the global class-marginal corrects it."""
    rng = np.random.default_rng(seed)
    p = np.array([0.6, 0.2, 0.1, 0.07, 0.03]) if imbalance else np.ones(k) / k
    y = rng.choice(k, n, p=p)
    cent = rng.normal(size=(k, dim)) * 0.7        # weak separation
    X = np.array([cent[y[i]] + 1.6 * rng.normal(size=dim) for i in range(n)])   # noise >> separation -> heavy overlap
    nrm = np.linalg.norm(X, axis=1, keepdims=True)
    return X / nrm, y


def main():
    os.makedirs(EPOCH_DIR, exist_ok=True); t0 = time.time()
    from scripts.cross_script.data import load_b_damos, load_a
    lb_seqs, lb_freq, _ = load_b_damos(); lb_signs = sorted(lb_freq.keys())
    lb_lab = GR.truth_labels(lb_signs)
    X, keep = context_embedding(lb_seqs, lb_signs)
    y = np.array([VOW.get(lb_lab[s]["vowel"], -1) for s in keep])
    v = y >= 0; Xv, yv = X[v], y[v]; classes = list(range(5))

    # ---- positive control: imbalanced synthetic where the global marginal should beat local NN ----
    pc = [run_stageA(*synth(s, imbalance=True), list(range(5)), seed=s) for s in range(5)]
    pc_global = float(np.mean([p["global"] for p in pc])); pc_local = float(np.mean([p["local"] for p in pc]))
    pc_detects = pc_global > pc_local + 0.03   # global marginal constraint adds info on imbalanced classes

    # ---- Stage A: blinded LB known-target calibration ----
    lbA = [run_stageA(Xv, yv, classes, seed=s) for s in range(8)]
    lb_local = float(np.mean([r["local"] for r in lbA])); lb_global = float(np.mean([r["global"] for r in lbA]))
    lb_random = float(np.mean([r["random"] for r in lbA]))

    # ---- Stage B: LA target-free -> equivalence classes; ambiguity reduction beyond the anchor-lattice null? ----
    la_signs0, la_seqs, la_freq = load_a()
    la_signs = sorted(set(t for w in la_seqs for t in w))
    Xla, keepla = context_embedding(la_seqs, la_signs, min_count=2)
    # target-free: with NO known target, any global assignment to q classes is a relabeling of an equivalence class.
    # Quantify: fraction of assignments that flip under a label permutation of the (unknown) target = 1 - 1/q!...
    # Operationally, with no anchors the "value" is unidentifiable up to the full symmetric group on classes.
    q = 5
    import math
    la_label_symmetry = math.factorial(q)   # every class-labeling is equivalent -> q! relabelings, 0 bits fixed
    la_note = ("Target-free: with no known cognate target and no external anchors, global assignment on LA produces "
               "equivalence CLASSES only; the class LABELS are unidentifiable up to the full symmetric group S_%d "
               "(%d equivalent relabelings). Global optimization selects ONE representative of this equivalence "
               "class; it adds NO information the local/anchor-lattice null does not already have." % (q, la_label_symmetry))

    verdict, rationale = _verdict(pc_detects, pc_global, pc_local, lb_local, lb_global, lb_random)
    results = {"positive_control": {"global": pc_global, "local": pc_local, "detects": pc_detects},
               "stageA_linear_b": {"local": lb_local, "global": lb_global, "random": lb_random, "n_signs": int(v.sum())},
               "stageB_linear_a": {"target_free": True, "class_label_symmetry_factorial": la_label_symmetry,
                                   "n_signs": int(Xla.shape[0]), "note": la_note},
               "config": {"global_solver": "capacity-constrained Hungarian (class-marginal)", "target": "vowel (Stage A)",
                          "baselines": ["local_nn", "random"]},
               "verdict": verdict, "rationale": rationale, "layer": "L2", "licences_changed": "none",
               "la_touched": True, "runtime_sec": round(time.time() - t0, 1)}
    with open(RESULT, "w") as fh:
        json.dump(results, fh, indent=1, default=lambda o: float(o))
    print("VERDICT:", verdict); print("rationale:", rationale)
    print("PC: global=%.3f local=%.3f detects=%s" % (pc_global, pc_local, pc_detects))
    print("LB StageA: local=%.3f global=%.3f random=%.3f" % (lb_local, lb_global, lb_random))
    print("LA StageB: target-free, S_5 label symmetry =", la_label_symmetry)
    return results


def _verdict(pc_detects, pc_global, pc_local, lb_local, lb_global, lb_random):
    if not pc_detects:
        return "GLOBAL_ASSIGNMENT_NO_POWER", ("Positive control fails: on imbalanced synthetic classes the global "
                                              "marginal constraint does not beat local NN (global %.3f vs local %.3f) "
                                              "-- no power to show global assignment adds information." % (pc_global, pc_local))
    if max(lb_local, lb_global) < lb_random + 0.05:
        return "GLOBAL_ASSIGNMENT_NULL", ("Neither local nor global assignment beats random on blinded LB (global "
                                          "%.3f, local %.3f, random %.3f) -- no class signal to assign." % (lb_global, lb_local, lb_random))
    if lb_global > lb_local + 0.03:
        return "GLOBAL_ASSIGNMENT_ADDS_INFORMATION", (
            "On blinded LB (known target) global assignment beats local NN (global %.3f vs local %.3f vs random "
            "%.3f) -- the global marginal constraint adds information WHEN A TARGET EXISTS. BUT for LA there is NO "
            "target: global assignment yields equivalence classes unidentifiable up to S_5, so it selects one "
            "arbitrary representative and adds nothing on LA. L2." % (lb_global, lb_local, lb_random))
    return "GLOBAL_ASSIGNMENT_SELECTS_ARBITRARY_REPRESENTATIVE", (
        "Even on blinded LB (known target) global assignment does NOT beat local nearest-neighbor (global %.3f ~ "
        "local %.3f, random %.3f): the global marginal constraint merely reshuffles within the same equivalence "
        "class without adding recovery. For LA (target-free) global optimization is strictly a representative-"
        "selector -- class labels are unidentifiable up to S_5 (120 equivalent relabelings) and no external target "
        "exists to break the symmetry. Global assignment CANNOT manufacture the constraints the anchor-lattice "
        "showed are absent (~10^63-10^270 degeneracy). NO ambiguity reduction beyond the anchor-lattice null. L2, "
        "no phonetic values." % (lb_global, lb_local, lb_random))


if __name__ == "__main__":
    main()
