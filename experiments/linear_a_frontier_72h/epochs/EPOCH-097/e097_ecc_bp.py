"""EPOCH-097 — Error-correcting-code / belief-propagation decoding (masked-sign reconstruction).

Treat the blinded corpus as a noisy code: does belief propagation over a sign factor graph that exploits
REDUNDANCY (bidirectional context + higher-order/skip factors = message passing) reconstruct masked signs better
than local/independent baselines? Held-out masked-sign top-1 accuracy. Baselines: independent marginals (unigram),
forward-bigram only, backward-bigram only, random. BP methods: bidirectional sum-product (left+right messages),
loopy BP (add skip-2 factors + damping). Positive control: synthetic HMM corpus with tunable redundancy -- BP must
beat unigram as redundancy rises. Then degrade to LA data scale + apply to blinded LA (missing-sign prediction is
an authorized L2 output; sign identity, NOT phonetic value). Verdicts: ECC_BP_SUPPORTED / _PARTIAL / _NULL /
_NO_POWER / _MODEL_INVALID. Prior (E016/E091/E092): local context is strong; message-passing may not beat it.
"""
import sys, os, json, time
import numpy as np
from collections import Counter, defaultdict
import warnings
warnings.filterwarnings("ignore")

REPO = "/home/claude-runner/gitlab/n8n/logos-linear-a-frontier-72h"
sys.path.insert(0, REPO)
EPOCH_DIR = os.path.join(REPO, "experiments/linear_a_frontier_72h/epochs/EPOCH-097")
RESULT = os.path.join(EPOCH_DIR, "result.json")
DAMP = 0.5           # loopy BP damping on skip factors


def estimate(words, alphabet):
    """Unigram + forward/backward bigram + skip-2 conditionals (add-1 smoothed) on TRAIN words."""
    V = len(alphabet); idx = {s: i for i, s in enumerate(alphabet)}
    uni = np.ones(V)
    fwd = np.ones((V, V)); bwd = np.ones((V, V))          # fwd[a,b]=P(b|prev=a); bwd[a,b]=P(b|next=a)
    sk2f = np.ones((V, V)); sk2b = np.ones((V, V))        # skip-2: P(b|prevprev=a) / P(b|nextnext=a)
    for w in words:
        ii = [idx[s] for s in w if s in idx]
        for j, s in enumerate(ii):
            uni[s] += 1
            if j > 0: fwd[ii[j - 1], s] += 1
            if j < len(ii) - 1: bwd[ii[j + 1], s] += 1
            if j > 1: sk2f[ii[j - 2], s] += 1
            if j < len(ii) - 2: sk2b[ii[j + 2], s] += 1
    uni /= uni.sum()
    fwd /= fwd.sum(1, keepdims=True); bwd /= bwd.sum(1, keepdims=True)
    sk2f /= sk2f.sum(1, keepdims=True); sk2b /= sk2b.sum(1, keepdims=True)
    return dict(uni=uni, fwd=fwd, bwd=bwd, sk2f=sk2f, sk2b=sk2b, idx=idx, alphabet=alphabet)


def predict(model, ii, j, method):
    """Return predicted alphabet-index for masked position j in index-word ii, under `method`."""
    uni = model["uni"]; V = len(uni)
    L = ii[j - 1] if j > 0 else None
    R = ii[j + 1] if j < len(ii) - 1 else None
    L2 = ii[j - 2] if j > 1 else None
    R2 = ii[j + 2] if j < len(ii) - 2 else None
    eps = 1e-12
    if method == "random":
        return np.random.default_rng(j + 1).integers(0, V)
    if method == "unigram":
        return int(np.argmax(uni))
    if method == "forward":
        return int(np.argmax(model["fwd"][L] if L is not None else uni))
    if method == "backward":
        return int(np.argmax(model["bwd"][R] if R is not None else uni))
    # belief propagation: product of messages (log domain), normalized by the prior it double-counts
    logp = np.log(uni + eps)
    if method in ("bp_bidir", "bp_loopy"):
        if L is not None: logp += np.log(model["fwd"][L] + eps) - np.log(uni + eps)
        if R is not None: logp += np.log(model["bwd"][R] + eps) - np.log(uni + eps)
    if method == "bp_loopy":
        if L2 is not None: logp += DAMP * (np.log(model["sk2f"][L2] + eps) - np.log(uni + eps))
        if R2 is not None: logp += DAMP * (np.log(model["sk2b"][R2] + eps) - np.log(uni + eps))
    return int(np.argmax(logp))


METHODS = ["random", "unigram", "forward", "backward", "bp_bidir", "bp_loopy"]


def evaluate(train_words, test_words, alphabet):
    model = estimate(train_words, alphabet); idx = model["idx"]
    hits = {m: 0 for m in METHODS}; tot = 0
    for w in test_words:
        ii = [idx[s] for s in w if s in idx]
        if len(ii) < 2:
            continue
        for j in range(len(ii)):
            truth = ii[j]; tot += 1
            for m in METHODS:
                if predict(model, ii, j, m) == truth:
                    hits[m] += 1
    return {m: hits[m] / tot for m in METHODS} if tot else {m: 0.0 for m in METHODS}


def split(words, seed=0, frac=0.7):
    rng = np.random.default_rng(seed); order = rng.permutation(len(words))
    n = int(frac * len(words))
    return [words[i] for i in order[:n]], [words[i] for i in order[n:]]


def synthetic_hmm(seed, redundancy, n_words=4000, V=25):
    """HMM corpus: higher redundancy => peakier transition rows => context predicts the next sign strongly."""
    rng = np.random.default_rng(seed)
    T = rng.dirichlet(np.ones(V) * (1.0 / max(redundancy, 1e-3)), size=V)  # low alpha => peaky => redundant
    words = []
    for _ in range(n_words):
        L = rng.integers(3, 8); s = rng.integers(0, V); w = [s]
        for _ in range(L - 1):
            s = rng.choice(V, p=T[s]); w.append(s)
        words.append([str(x) for x in w])
    return words, [str(i) for i in range(V)]


def main():
    os.makedirs(EPOCH_DIR, exist_ok=True); t0 = time.time()
    from scripts.cross_script.data import load_b_damos, load_a
    lb_words, freq, _ = load_b_damos()
    lb_alpha = sorted(freq.keys())

    # ---- positive control: recovery must rise with redundancy, and BP must beat unigram ----
    pc = {}
    for red in ("low", "high"):
        r = 5.0 if red == "high" else 0.3
        w, alpha = synthetic_hmm(0, r)
        tr, te = split(w); pc[red] = evaluate(tr, te, alpha)
    pc_detects = pc["high"]["bp_bidir"] > pc["high"]["unigram"] + 0.05 and \
                 pc["high"]["bp_bidir"] > pc["low"]["bp_bidir"]

    # ---- blinded LB ----
    tr, te = split(list(lb_words)); lb = evaluate(tr, te, lb_alpha)

    # ---- degrade to LA scale (subsample LB to ~4245 tokens worth of words) then blinded LA ----
    rng = np.random.default_rng(0)
    order = rng.permutation(len(lb_words)); sub = []; tok = 0
    for i in order:
        sub.append(lb_words[i]); tok += len(lb_words[i])
        if tok >= 4245:
            break
    tr2, te2 = split(sub); lb_degraded = evaluate(tr2, te2, lb_alpha)

    signs_a, seqs_a, freq_a = load_a()
    la_alpha = sorted(set(t for w in seqs_a for t in w))
    tra, tea = split(list(seqs_a)); la = evaluate(tra, tea, la_alpha)

    verdict, rationale = _verdict(lb, pc, pc_detects)
    results = {"positive_control": pc, "pc_detects": bool(pc_detects), "linear_b": lb,
               "linear_b_degraded_to_la_scale": lb_degraded, "linear_a": la,
               "config": {"methods": METHODS, "damping": DAMP, "split": "0.7/0.3",
                          "task": "held-out masked-sign top-1 accuracy", "la_scale_tokens": 4245},
               "verdict": verdict, "rationale": rationale, "layer": "L2", "licences_changed": "none",
               "la_touched": True, "runtime_sec": round(time.time() - t0, 1)}
    with open(RESULT, "w") as fh:
        json.dump(results, fh, indent=1, default=lambda o: float(o))
    print("VERDICT:", verdict); print("rationale:", rationale)
    print("PC high:", {k: round(v, 3) for k, v in pc["high"].items()})
    print("PC low :", {k: round(v, 3) for k, v in pc["low"].items()}, "detects:", pc_detects)
    print("LB     :", {k: round(v, 3) for k, v in lb.items()})
    print("LB@LA  :", {k: round(v, 3) for k, v in lb_degraded.items()})
    print("LA     :", {k: round(v, 3) for k, v in la.items()})
    return results


def _verdict(lb, pc, pc_detects):
    if not pc_detects:
        return "ECC_BP_NO_POWER", ("Positive control fails: BP does not beat unigram on a high-redundancy synthetic "
                                   "code (bp_bidir %.3f vs unigram %.3f) or recovery does not rise with redundancy." %
                                   (pc["high"]["bp_bidir"], pc["high"]["unigram"]))
    uni = lb["unigram"]; bp = lb["bp_bidir"]; loopy = lb["bp_loopy"]
    local = max(lb["forward"], lb["backward"])
    best_bp = max(bp, loopy)
    if best_bp <= uni + 0.02:
        return "ECC_BP_NULL", ("BP does not beat the unigram (frequency) baseline on blinded LB (bp %.3f vs unigram "
                               "%.3f). No recoverable code redundancy." % (best_bp, uni))
    if best_bp > local + 0.02:
        return "ECC_BP_SUPPORTED", (
            "BP message-passing beats BOTH the unigram baseline AND single-direction local context on blinded LB "
            "(bp %.3f vs local %.3f vs unigram %.3f) -- combining bidirectional + higher-order redundancy recovers "
            "masked signs beyond local context. L2 (sign identity, no phonetic values)." % (best_bp, local, uni))
    return "ECC_BP_PARTIAL", (
        "BP beats the unigram baseline (bp %.3f vs unigram %.3f) but does NOT beat single-direction local context "
        "(local %.3f >= bp) -- masked signs are recoverable from context, but the bidirectional/higher-order "
        "redundancy adds nothing over a single local factor. Consistent with the campaign prior that local/simple "
        "structure carries the signal. L2, no phonetic values." % (best_bp, uni, local))


if __name__ == "__main__":
    main()
