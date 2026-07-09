"""EPOCH-094 — Sequence/segmentation morphogenesis (blinded LB word-boundary recovery).

Distinct question from E091-093 (class recovery): given an UNSEGMENTED blinded-LB sign stream, does an RD /
morphogenesis boundary cue (activator-domain boundaries over a sign-type graph) recover word boundaries BETTER than
generic unsupervised cues (transition surprisal, branching entropy) + random? Held-out: bigram/entropy stats
estimated on TRAIN words, boundaries evaluated on TEST streams. Boundaries predicted at the true boundary rate
(top-k), so boundary-F1 is a fair cross-method comparison. Positive control: a synthetic lexicon-generated corpus
where the cues MUST recover planted boundaries. Verdicts: SEGMENTATION_MORPHOGENESIS_SUPPORTED / _GENERIC / _NULL /
_NO_POWER / _MODEL_INVALID. Prior (E091/E092): morphogenesis is expected to tie/lose to the generic cues (_GENERIC).
"""
import sys, os, json, time
import numpy as np
from collections import Counter, defaultdict
import warnings
warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
REPO = "/home/claude-runner/gitlab/n8n/logos-linear-a-frontier-72h"; sys.path.insert(0, REPO)
import rd
import graphs as GR

EPOCH_DIR = os.path.join(REPO, "experiments/linear_a_frontier_72h/epochs/EPOCH-094")
RESULT = os.path.join(EPOCH_DIR, "result.json")
WORDS_PER_STREAM = 15
SEEDS = [0, 1, 2, 3, 4]


def build_streams(words, seed, words_per=WORDS_PER_STREAM):
    """Concatenate words into sign streams; return list of (stream_signs, boundary_positions_set)."""
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(words))
    streams = []
    i = 0
    while i < len(order):
        chunk = [words[j] for j in order[i:i + words_per]]
        i += words_per
        stream = []; bounds = set(); pos = 0
        for w in chunk:
            stream.extend(w); pos += len(w); bounds.add(pos - 1)   # boundary AFTER last sign of each word
        bounds.discard(len(stream) - 1)                            # no boundary at stream end
        if len(stream) > 3:
            streams.append((stream, bounds))
    return streams


def bigram_stats(words):
    """Forward transition counts + forward branching sets, estimated on TRAIN words (with word-internal only)."""
    trans = defaultdict(Counter)
    for w in words:
        for a, b in zip(w[:-1], w[1:]):
            trans[a][b] += 1
    P = {a: {b: c / sum(cnt.values()) for b, c in cnt.items()} for a, cnt in trans.items()}
    Hbr = {a: -sum((c / sum(cnt.values())) * np.log(c / sum(cnt.values())) for c in cnt.values())
           for a, cnt in trans.items()}
    return P, Hbr


def cue_surprisal(stream, P):
    # boundary score at gap i = -log P(s_{i+1} | s_i): high surprisal -> likely boundary
    out = []
    for a, b in zip(stream[:-1], stream[1:]):
        p = P.get(a, {}).get(b, 1e-6)
        out.append(-np.log(max(p, 1e-6)))
    return np.array(out)


def cue_branching(stream, Hbr):
    # boundary score at gap i = branching entropy AFTER s_i (Harris/Tanaka-Ishii): spikes at boundaries
    return np.array([Hbr.get(a, 0.0) for a in stream[:-1]])


def cue_random(stream, seed):
    rng = np.random.default_rng(seed)
    return rng.random(len(stream) - 1)


def cue_morphogenesis(stream, type_u):
    # boundary score at gap i = |u(s_i) - u(s_{i+1})|: RD activator-domain boundary
    return np.array([abs(type_u.get(a, 0.0) - type_u.get(b, 0.0)) for a, b in zip(stream[:-1], stream[1:])])


def rd_type_field(train_words, signs, seed=0):
    """Build G_POSITION over sign types from TRAIN adjacency, run RD (unsupervised coarsest-mode), return u per type."""
    s2i, _ = GR.blind(signs, seed=seed)
    graphs = GR.build_graphs([w for w in train_words], signs, s2i, min_count=3)
    g = graphs["POSITION"]
    ev, U, L = g["evals"], g["evecs"], g["L"]
    r = rd.schnakenberg()
    best = None
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
    u = np.mean([rd.integrate(r, L, c["Du"], c["Dv"], seed=s) for s in (1, 2, 3)], 0)
    return {s: float(u[i]) for i, s in enumerate(g["signs_kept"])}


def boundary_f1(scores, bounds, k):
    """Predict the top-k gaps as boundaries; boundary-F1 (at matched count precision=recall)."""
    pred = set(np.argsort(scores)[::-1][:k].tolist())
    tp = len(pred & bounds)
    return tp / k if k else 0.0


def eval_method(streams, cue_fn, k_rate_from_truth=True):
    f1s = []
    for stream, bounds in streams:
        if len(bounds) == 0:
            continue
        sc = cue_fn(stream)
        f1s.append(boundary_f1(sc, bounds, len(bounds)))
    return float(np.mean(f1s)) if f1s else 0.0


def synthetic_pc(seed, n_types=40, n_words=2000, wlen=(2, 4)):
    """Planted-boundary corpus: sample words from a lexicon of pseudo-words; cues must recover boundaries."""
    rng = np.random.default_rng(seed)
    alpha = [f"X{i}" for i in range(n_types)]
    lexicon = []
    for _ in range(120):
        L = rng.integers(wlen[0], wlen[1] + 1)
        lexicon.append([alpha[rng.integers(0, n_types)] for _ in range(L)])
    words = [lexicon[rng.integers(0, len(lexicon))] for _ in range(n_words)]
    return words, alpha


def run_arm(words, signs, tag):
    """Split words train/test, estimate cues on train, evaluate boundary-F1 on test streams (avg over seeds)."""
    rng = np.random.default_rng(0); order = rng.permutation(len(words))
    ntr = int(0.7 * len(words))
    train = [words[i] for i in order[:ntr]]; test = [words[i] for i in order[ntr:]]
    P, Hbr = bigram_stats(train)
    type_u = rd_type_field(train, signs) if tag != "synthetic" else None
    if type_u is None:
        # synthetic: build a simple adjacency-RD field over the synthetic alphabet
        type_u = _synth_rd_field(train, signs)
    res = {}
    for name, fn in [
        ("random", lambda st, s=0: cue_random(st, 0)),
        ("surprisal", lambda st: cue_surprisal(st, P)),
        ("branching_entropy", lambda st: cue_branching(st, Hbr)),
        ("morphogenesis_rd", lambda st: cue_morphogenesis(st, type_u or {})),
    ]:
        f1_seeds = []
        for sd in SEEDS:
            streams = build_streams(test, sd)
            f1_seeds.append(eval_method(streams, fn))
        res[name] = {"f1_mean": float(np.mean(f1_seeds)), "f1_sd": float(np.std(f1_seeds))}
    return res


def _synth_rd_field(train, signs):
    s2i, _ = GR.blind(sorted(set(t for w in train for t in w)), seed=0)
    graphs = GR.build_graphs(train, sorted(set(t for w in train for t in w)), s2i, min_count=2)
    g = graphs["POSITION"]
    r = rd.schnakenberg()
    best = None
    for ratio in (10, 20, 40):
        c = rd.find_Du(r, g["evals"], ratio)
        if c is None:
            continue
        key = (c["min_unstable_lam"], c["n_unstable"])
        if best is None or key < best[0]:
            best = (key, c)
    if best is None:
        return {}
    c = best[1]
    u = np.mean([rd.integrate(r, g["L"], c["Du"], c["Dv"], seed=s) for s in (1, 2, 3)], 0)
    return {s: float(u[i]) for i, s in enumerate(g["signs_kept"])}


def main():
    os.makedirs(EPOCH_DIR, exist_ok=True); t0 = time.time()
    from scripts.cross_script.data import load_b_damos
    words, freq, _ = load_b_damos()
    signs = sorted(freq.keys())

    # positive control
    pc_words, pc_alpha = synthetic_pc(0)
    pc = run_arm(pc_words, pc_alpha, "synthetic")
    pc_detects = pc["branching_entropy"]["f1_mean"] > pc["random"]["f1_mean"] + 0.10 or \
                 pc["surprisal"]["f1_mean"] > pc["random"]["f1_mean"] + 0.10

    # real blinded LB
    lb = run_arm(list(words), signs, "lb")

    verdict, rationale = _verdict(lb, pc, pc_detects)
    results = {"positive_control": pc, "pc_detects": bool(pc_detects), "linear_b": lb,
               "verdict": verdict, "rationale": rationale,
               "config": {"words_per_stream": WORDS_PER_STREAM, "seeds": SEEDS, "split": "0.7 train / 0.3 test",
                          "boundary_pred": "top-k at true boundary rate", "cue_morphogenesis": "|u(a)-u(b)| RD activator"},
               "layer": "L2", "licences_changed": "none", "la_touched": False,
               "runtime_sec": round(time.time() - t0, 1)}
    with open(RESULT, "w") as fh:
        json.dump(results, fh, indent=1, default=lambda o: float(o))
    print("VERDICT:", verdict); print("rationale:", rationale)
    print("PC :", {k: round(v["f1_mean"], 3) for k, v in pc.items()}, "detects:", pc_detects)
    print("LB :", {k: round(v["f1_mean"], 3) for k, v in lb.items()})
    return results


def _verdict(lb, pc, pc_detects):
    if not pc_detects:
        return "SEGMENTATION_MORPHOGENESIS_NO_POWER", (
            "Positive control fails: on a planted-boundary synthetic corpus the generic cues do not beat random "
            "(branching %.3f, surprisal %.3f vs random %.3f) -- the boundary task is not detectable by the harness, "
            "so nothing can be read from the LB arm." % (
                pc["branching_entropy"]["f1_mean"], pc["surprisal"]["f1_mean"], pc["random"]["f1_mean"]))
    rnd = lb["random"]["f1_mean"]
    morph = lb["morphogenesis_rd"]["f1_mean"]
    best_generic = max(lb["surprisal"]["f1_mean"], lb["branching_entropy"]["f1_mean"])
    best_generic_name = "surprisal" if lb["surprisal"]["f1_mean"] >= lb["branching_entropy"]["f1_mean"] else "branching_entropy"
    if morph <= rnd + 0.02:
        return "SEGMENTATION_MORPHOGENESIS_NULL", (
            "The RD/morphogenesis boundary cue does not beat random on blinded LB (morphogenesis %.3f vs random "
            "%.3f); generic cues do (best %s %.3f). Morphogenesis carries no word-boundary signal." % (
                morph, rnd, best_generic_name, best_generic))
    if morph > best_generic + 0.02:
        return "SEGMENTATION_MORPHOGENESIS_SUPPORTED", (
            "The RD/morphogenesis cue beats BOTH random and the best generic cue on blinded LB (morphogenesis %.3f "
            "vs %s %.3f vs random %.3f)." % (morph, best_generic_name, best_generic, rnd))
    return "SEGMENTATION_MORPHOGENESIS_GENERIC", (
        "The RD/morphogenesis cue beats random (%.3f vs %.3f) but does NOT beat the generic transition/branching "
        "cues (best %s %.3f >= morphogenesis %.3f). Morphogenesis adds a weak boundary signal but nothing beyond "
        "generic unsupervised segmentation -- consistent with the E091/E092 pattern (generic ties/beats fancy)." % (
            morph, rnd, best_generic_name, best_generic, morph))


if __name__ == "__main__":
    main()
