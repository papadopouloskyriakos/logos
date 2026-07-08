"""
EPOCH-030 machinery — Numeral / logogram attachment order in the ledger grammar (L2/L3).

Pure token-stream positional grammar. NO phonetics, NO meaning, NO numeral values.
Only token TYPE and POSITION. LB damos lacks an ordered word/numeral stream, so the
positive control is a SYNTHETIC known-order control built from the LA stream itself
(disclosed in prereg.md §5).

METRIC (frozen): among adjacent (token_i, token_{i+1}) pairs in a stream where one
token is 'word' and the other is 'num', the fraction that are WORD->NUM (word first):
    p_wordfirst = n(word->num) / ( n(word->num) + n(num->word) )

NULL (frozen, "stream-shuffle"): within each inscription, uniformly permute the token
order; >=1000 draws; two-sided p.  [primary, per frozen rule]

DEVIATION NULL ("pair-flip", disclosed): keep the real stream skeleton fixed and flip
the direction of each real word-num adjacency pair with prob 0.5. This isolates the
DIRECTION question (the mission's actual question) from adjacency-density structure
that the unrestricted stream-shuffle conflates. Reported alongside the frozen null.

Self-check: `python3 machinery.py` runs both positive controls + false-positive sweeps.
"""
from __future__ import annotations
import json, math, random, hashlib, os
from collections import defaultdict, Counter
import numpy as np

def _repo_root():
    p = os.getcwd()
    for _ in range(8):
        if os.path.isdir(os.path.join(p, "corpus", "silver")):
            return p
        p = os.path.dirname(p)
    return os.getcwd()

LA_PATH = os.path.join(_repo_root(), "corpus", "silver", "inscriptions_structured.json")
RNG_SEED = 20250301
N_DRAWS = 2000          # >= 1000
FP_NCORPORA = 25        # >= 20
FP_ALPHA = 0.05
FP_RATE_CAP = 0.10
MIN_SITE_ADJ = 15

# ---------- loaders ----------
def load_la(path=LA_PATH):
    return json.load(open(path))

def stream_types(ins):
    out = []
    for t in ins.get("stream", []):
        out.append(t.get("t", "?") if isinstance(t, dict) else "?")
    return out

def type_vocab(inscriptions):
    c = Counter()
    for ins in inscriptions:
        for ty in stream_types(ins):
            c[ty] += 1
    return dict(c)

# ---------- core metric ----------
def count_word_num(types_seq):
    wf = nf = 0
    for i in range(len(types_seq) - 1):
        a, b = types_seq[i], types_seq[i + 1]
        if a == "word" and b == "num":
            wf += 1
        elif a == "num" and b == "word":
            nf += 1
    return wf, nf

def global_counts(inscriptions):
    WF = NF = 0
    for ins in inscriptions:
        wf, nf = count_word_num(stream_types(ins))
        WF += wf; NF += nf
    return WF, NF

def p_wordfirst(wf, nf):
    return wf / (wf + nf) if (wf + nf) else float("nan")

# ---------- null model A: stream-shuffle (frozen) ----------
def stream_shuffle_p_wordfirst(inscriptions, rng):
    WF = NF = 0
    for ins in inscriptions:
        ty = stream_types(ins)
        if len(ty) < 2:
            continue
        perm = ty[:]; rng.shuffle(perm)
        wf, nf = count_word_num(perm)
        WF += wf; NF += nf
    return p_wordfirst(WF, NF)

# ---------- null model B: pair-flip (deviation, direction-matched) ----------
def pairflip_stream(ins, rng):
    """Return a copy of ins.stream with each real word-num adjacency pair flipped
    with prob 0.5. Preserves all positions, separators, and the adjacency count."""
    new = [dict(t) if isinstance(t, dict) else t for t in ins.get("stream", [])]
    i = 0
    while i < len(new) - 1:
        a = new[i].get("t") if isinstance(new[i], dict) else None
        b = new[i + 1].get("t") if isinstance(new[i + 1], dict) else None
        if {a, b} == {"word", "num"}:
            if rng.random() < 0.5:
                new[i], new[i + 1] = new[i + 1], new[i]
            i += 2
        else:
            i += 1
    return new

def pairflip_p_wordfirst(inscriptions, rng):
    WF = NF = 0
    for ins in inscriptions:
        new = pairflip_stream(ins, rng)
        wf, nf = count_word_num([t.get("t", "?") if isinstance(t, dict) else "?" for t in new])
        WF += wf; NF += nf
    return p_wordfirst(WF, NF)

NULL_MODELS = {
    "stream_shuffle": stream_shuffle_p_wordfirst,
    "pair_flip": pairflip_p_wordfirst,
}

def two_sided_p(obs, null_samples):
    null = np.asarray([x for x in null_samples if x == x], dtype=float)
    if len(null) == 0:
        return float("nan")
    ge = float(np.mean(null >= obs)); le = float(np.mean(null <= obs))
    return float(min(1.0, 2.0 * min(ge, le)))

def global_test(inscriptions, null_model="stream_shuffle", n_draws=N_DRAWS, seed=RNG_SEED):
    rng = random.Random(seed)
    WF, NF = global_counts(inscriptions)
    obs = p_wordfirst(WF, NF)
    fn = NULL_MODELS[null_model]
    null = [fn(inscriptions, rng) for _ in range(n_draws)]
    null = [x for x in null if x == x]
    null_mean = float(np.mean(null)) if null else float("nan")
    p = two_sided_p(obs, null)
    return {
        "n_word_numeral_adj": int(WF + NF),
        "n_word_first": int(WF),
        "n_num_first": int(NF),
        "p_wordfirst": float(obs),
        "null_mean_p_wordfirst": null_mean,
        "null_p": float(p),
        "null_model": null_model,
    }

def per_site_test(inscriptions, site, null_model="stream_shuffle", n_draws=N_DRAWS, seed=RNG_SEED):
    sub = [ins for ins in inscriptions if (ins.get("site") or "(none)") == site]
    if not sub:
        return None
    rng = random.Random(seed + (hash(site) & 0xFFFFF))
    WF, NF = global_counts(sub)
    n = WF + NF
    if n == 0:
        return {"site": site, "n_adj": 0, "p_wordfirst": float("nan"),
                "p": float("nan"), "direction": "none"}
    obs = p_wordfirst(WF, NF)
    fn = NULL_MODELS[null_model]
    null = [fn(sub, rng) for _ in range(n_draws)]
    p = two_sided_p(obs, null)
    direction = "word_first" if obs > 0.5 else ("numeral_first" if obs < 0.5 else "tie")
    return {"site": site, "n_adj": int(n), "p_wordfirst": float(obs),
            "p": float(p), "direction": direction}

# ---------- synthetic controls (PC) ----------
def synth_force_order(inscriptions, p_word_before, seed):
    """Plant a known word-num DIRECTION on the real adjacency pairs (pair-flip builder).
    Preserves stream skeleton; sets each real word-num pair to word->num with prob
    p_word_before. Realized p_wordfirst faithfully tracks p_word_before."""
    rng = random.Random(seed)
    out = []
    for ins in inscriptions:
        new = [dict(t) if isinstance(t, dict) else t for t in ins.get("stream", [])]
        i = 0
        while i < len(new) - 1:
            a = new[i].get("t") if isinstance(new[i], dict) else None
            b = new[i + 1].get("t") if isinstance(new[i + 1], dict) else None
            if {a, b} == {"word", "num"}:
                if rng.random() >= p_word_before:
                    new[i], new[i + 1] = new[i + 1], new[i]
                i += 2
            else:
                i += 1
        out.append({"id": ins.get("id", "?"), "stream": new})
    return out

def pc_detect_planted(inscriptions, null_model, p_plant=0.90, n_draws=N_DRAWS, seed=RNG_SEED):
    synth = synth_force_order(inscriptions, p_plant, seed)
    res = global_test(synth, null_model=null_model, n_draws=n_draws, seed=seed + 1)
    direction_ok = res["p_wordfirst"] > 0.5
    return res["null_p"], res["p_wordfirst"], direction_ok

def pc_false_positive(inscriptions, null_model, n_corpora=FP_NCORPORA, n_draws=N_DRAWS, seed=RNG_SEED):
    """Direction-randomized corpora (planted p_wordfirst=0.5 via pair-flip). The test
    (under the chosen null) must NOT reject at >0.10 across these corpora."""
    rejects = 0; pvals = []
    for k in range(n_corpora):
        synth = synth_force_order(inscriptions, 0.5, seed + 1000 + k)
        res = global_test(synth, null_model=null_model, n_draws=n_draws, seed=seed + 2000 + k)
        pvals.append(res["null_p"])
        if res["null_p"] <= FP_ALPHA:
            rejects += 1
    return rejects / n_corpora, pvals

def run_pc(inscriptions, null_model):
    p_det, pwf_det, dir_ok = pc_detect_planted(inscriptions, null_model)
    fp_rate, fp_pvals = pc_false_positive(inscriptions, null_model)
    detect_pass = (p_det <= 0.05) and dir_ok
    fp_pass = fp_rate <= FP_RATE_CAP
    verdict = "PASSED" if (detect_pass and fp_pass) else "FAILED"
    return {
        "pc_verdict": verdict,
        "detect_planted_p": float(p_det),
        "detect_planted_p_wordfirst": float(pwf_det),
        "detect_direction_ok": bool(dir_ok),
        "false_pos_rate": float(fp_rate),
        "fp_pvals": [float(x) for x in fp_pvals],
        "null_model": null_model,
    }

# ---------- cross-site ----------
def cross_site(inscriptions, null_model="stream_shuffle", min_adj=MIN_SITE_ADJ,
               n_draws=N_DRAWS, seed=RNG_SEED):
    site_adj = defaultdict(int)
    for ins in inscriptions:
        s = ins.get("site") or "(none)"
        wf, nf = count_word_num(stream_types(ins))
        site_adj[s] += wf + nf
    testable = sorted([s for s, n in site_adj.items() if n >= min_adj])
    per_site = {}
    for s in testable:
        per_site[s] = per_site_test(inscriptions, s, null_model=null_model,
                                    n_draws=n_draws, seed=seed)
    site_nins = Counter(ins.get("site") or "(none)" for ins in inscriptions)
    largest = site_nins.most_common(1)[0][0]
    loo_corpus = [ins for ins in inscriptions if (ins.get("site") or "(none)") != largest]
    loo_res = global_test(loo_corpus, null_model=null_model, n_draws=n_draws, seed=seed + 7)
    return {
        "n_sites_testable": len(testable),
        "testable_sites": testable,
        "per_site": per_site,
        "loo_excluded": largest,
        "loo_p": float(loo_res["null_p"]),
        "loo_p_wordfirst": float(loo_res["p_wordfirst"]),
        "null_model": null_model,
    }

# ---------- verdict (frozen rule) ----------
def verdict(pc, glob, cs):
    if pc["pc_verdict"] != "PASSED":
        return "MACHINERY_UNINFORMATIVE"
    if cs["n_sites_testable"] < 2:
        return "NUMERAL_ORDER_UNDERPOWERED"
    if glob["null_p"] > 0.05:
        return "NUMERAL_ORDER_NO_SIGNAL"
    sig = {s: v for s, v in cs["per_site"].items() if v["p"] <= 0.05}
    if len(sig) < 2:
        return "NUMERAL_ORDER_SITE_LOCAL"
    dirs = set(v["direction"] for v in sig.values())
    if len(dirs) > 1:
        return "NUMERAL_ORDER_SITE_LOCAL"
    if cs["loo_p"] > 0.05:
        return "NUMERAL_ORDER_SITE_LOCAL"
    loo_dir = "word_first" if cs["loo_p_wordfirst"] > 0.5 else "numeral_first"
    if loo_dir not in dirs:
        return "NUMERAL_ORDER_SITE_LOCAL"
    return "NUMERAL_ORDER_CROSS_SITE_ROBUST"

# ---------- driver ----------
def run_all(inscriptions, null_model="stream_shuffle"):
    pc = run_pc(inscriptions, null_model)
    glob = global_test(inscriptions, null_model=null_model)
    cs = cross_site(inscriptions, null_model=null_model)
    v = verdict(pc, glob, cs)
    return {"verdict": v, "positive_control": pc, "global": glob, "cross_site": cs,
            "null_model": null_model}

# ---------- self-check / main ----------
def _selfcheck():
    ins = load_la()
    print("[self-check] loaded", len(ins), "inscriptions")
    print("[self-check] stream token types:", type_vocab(ins))
    for nm in ("stream_shuffle", "pair_flip"):
        print(f"\n[self-check] POSITIVE CONTROL under null = {nm}")
        pc = run_pc(ins, nm)
        print(f"  PC verdict           : {pc['pc_verdict']}")
        print(f"  detect planted p     : {pc['detect_planted_p']}  (planted p_wordfirst=0.90)")
        print(f"  detected p_wordfirst : {pc['detect_planted_p_wordfirst']}  dir_ok={pc['detect_direction_ok']}")
        print(f"  false-positive rate  : {pc['false_pos_rate']}  (cap 0.10)")
    return True

if __name__ == "__main__":
    _selfcheck()
    print("\nSELF_CHECK: DONE")
