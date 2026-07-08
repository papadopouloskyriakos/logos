"""
EPOCH-044 machinery — NUMERAL-GROUP CARDINALITY / COMPOUND-QUANTITY STRUCTURE.

Pure token-count structure (L2/L3). A NUMERAL-RUN = maximal run of consecutive
`num` tokens in an inscription's stream. p_compound = fraction of runs with
length >= 2. NULL = token-order shuffle WITHIN each inscription (preserves the
type multiset per inscription), >=1000 draws, two-sided p.

NO numeral-value interpretation. NO arithmetic. Tokens ANONYMOUS.
"""
import json, hashlib, random, sys
from collections import Counter

import os as _os
# Resolve corpus path relative to the repo root (this file lives 3 dirs deep).
_REPO_ROOT = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", "..", "..", ".."))
CORPUS = _os.path.join(_REPO_ROOT, "corpus", "silver", "inscriptions_structured.json")


# ---------- core structural primitives ----------
def load_corpus(path=CORPUS):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def runs_of_stream(stream):
    """Return list of numeral-run lengths in this stream (maximal consecutive num)."""
    runs, cur = [], 0
    for tok in stream:
        if isinstance(tok, dict) and tok.get("t") == "num":
            cur += 1
        else:
            if cur > 0:
                runs.append(cur); cur = 0
    if cur > 0:
        runs.append(cur)
    return runs

def p_compound_from_runs(runs):
    if not runs:
        return 0.0
    return sum(1 for r in runs if r >= 2) / len(runs)

def corpus_runs(inscriptions):
    """All numeral-runs across a list of inscriptions."""
    out = []
    for ins in inscriptions:
        out.extend(runs_of_stream(ins.get("stream", [])))
    return out

def p_compound_corpus(inscriptions):
    return p_compound_from_runs(corpus_runs(inscriptions))


# ---------- shuffle null ----------
def shuffle_inscription_stream(stream, rng):
    """Permute the token ORDER within one inscription, preserving the type multiset.
    Tokens are shuffled as whole objects (so 'num' identity is preserved)."""
    s = list(stream)
    rng.shuffle(s)
    return s

def shuffle_null(inscriptions, n_draws=1000, seed=44):
    """Token-order shuffle WITHIN each inscription. Returns list of p_compound draws."""
    rng = random.Random(seed)
    draws = []
    streams = [ins.get("stream", []) for ins in inscriptions]
    for _ in range(n_draws):
        shuf_ins = [{"stream": shuffle_inscription_stream(s, rng)} for s in streams]
        draws.append(p_compound_corpus(shuf_ins))
    return draws

def two_sided_p(observed, null_draws):
    """Two-sided p: 2 * min(P(null<=obs), P(null>=obs)), capped at 1.0."""
    n = len(null_draws)
    le = sum(1 for x in null_draws if x <= observed)
    ge = sum(1 for x in null_draws if x >= observed)
    p = 2 * min(le / n, ge / n)
    return min(p, 1.0)

def null_mean_and_direction(observed, null_draws):
    mean = sum(null_draws) / len(null_draws)
    if observed > mean:
        direction = "excess"
    elif observed < mean:
        direction = "deficit"
    else:
        direction = "equal"
    return mean, direction


# ---------- positive control ----------
def synthetic_stream_from_types(types_list, rng):
    """Build a synthetic stream as a list of token dicts from a list of type strings,
    shuffled (so the multiset is preserved but order is random)."""
    s = [{"t": t} for t in types_list]
    rng.shuffle(s)
    return s

def plant_clustering(types_list, frac_compound, rng):
    """Take a type multiset; force a fraction `frac_compound` of num tokens to be
    in adjacent pairs (compound runs of length 2). Returns a synthetic stream
    (list of token dicts) with the SAME type multiset but arranged so that
    ~frac_compound of num tokens are paired adjacently."""
    types = list(types_list)
    nums = [t for t in types if t == "num"]
    others = [t for t in types if t != "num"]
    n_num = len(nums)
    n_pair = int(round(frac_compound * n_num / 2.0))  # number of pairs
    # build blocks: pairs (num,num) and singletons (num)
    blocks = []
    used = 0
    for _ in range(n_pair):
        blocks.append(["num", "num"]); used += 2
    for _ in range(n_num - used):
        blocks.append(["num"])
    # interleave with 'other' tokens so blocks are separated (use others as separators)
    rng.shuffle(blocks)
    rng.shuffle(others)
    stream = []
    # place an 'other' between consecutive blocks when available
    oi = 0
    for i, b in enumerate(blocks):
        if i > 0 and oi < len(others):
            stream.append(others[oi]); oi += 1
        stream.extend(b)
    # append remaining others
    while oi < len(others):
        stream.append(others[oi]); oi += 1
    return [{"t": t} for t in stream]

def plant_spreading(types_list, rng):
    """Force ALL num tokens to be isolated (one-per-entry): insert at least one
    non-num token between every pair of num tokens. Same type multiset."""
    types = list(types_list)
    nums = [t for t in types if t == "num"]
    others = [t for t in types if t != "num"]
    rng.shuffle(others)
    stream = []
    oi = 0
    # interleave: num, other, num, other, ... then trailing others
    for i, n in enumerate(nums):
        stream.append(n)
        if i < len(nums) - 1:
            if oi < len(others):
                stream.append(others[oi]); oi += 1
            else:
                # no separator available -> cannot fully isolate; this is a real
                # constraint of the multiset. Append remaining nums (will cluster).
                stream.extend(nums[i+1:]); break
    while oi < len(others):
        stream.append(others[oi]); oi += 1
    return [{"t": t} for t in stream]

def positive_control(inscriptions, n_draws=1000, seed=4400,
                     frac_compound=0.5, n_fp_sets=20, fp_seed=4401):
    """PC: (a) detect planted clustering (excess) and planted spreading (deficit);
    (b) false-positive rate on shuffled (true H0) streams."""
    rng = random.Random(seed)
    # Use the pooled type multiset of the whole corpus as the synthetic base.
    pooled = []
    for ins in inscriptions:
        for tok in ins.get("stream", []):
            pooled.append(tok.get("t"))

    # (a) DETECT excess: plant clustering, compute p_compound, run shuffle null
    # on the SAME synthetic stream's type multiset.
    synth_excess = plant_clustering(pooled, frac_compound, rng)
    obs_excess = p_compound_from_runs(runs_of_stream(synth_excess))
    types_excess = [tok["t"] for tok in synth_excess]
    null_excess = []
    r2 = random.Random(seed + 1)
    for _ in range(n_draws):
        s = synthetic_stream_from_types(types_excess, r2)
        null_excess.append(p_compound_from_runs(runs_of_stream(s)))
    p_excess = two_sided_p(obs_excess, null_excess)
    mean_excess, dir_excess = null_mean_and_direction(obs_excess, null_excess)

    # (a) DETECT deficit: plant spreading, compute p_compound + null.
    synth_def = plant_spreading(pooled, rng)
    obs_def = p_compound_from_runs(runs_of_stream(synth_def))
    types_def = [tok["t"] for tok in synth_def]
    null_def = []
    r3 = random.Random(seed + 2)
    for _ in range(n_draws):
        s = synthetic_stream_from_types(types_def, r3)
        null_def.append(p_compound_from_runs(runs_of_stream(s)))
    p_def = two_sided_p(obs_def, null_def)
    mean_def, dir_def = null_mean_and_direction(obs_def, null_def)

    # (b) FALSE POSITIVE: on token-order-shuffled TRUE-H0 streams, rejection rate.
    # Build a "true H0" corpus = each inscription's stream shuffled once; then run
    # the full shuffle-null test on it; count rejections across n_fp_sets.
    rejections = 0
    rfp = random.Random(fp_seed)
    for s_i in range(n_fp_sets):
        h0_ins = [{"stream": shuffle_inscription_stream(ins.get("stream", []), rfp)}
                  for ins in inscriptions]
        obs0 = p_compound_corpus(h0_ins)
        null0 = shuffle_null(h0_ins, n_draws=n_draws, seed=fp_seed + 1000 + s_i)
        p0 = two_sided_p(obs0, null0)
        if p0 <= 0.05:
            rejections += 1
    fp_rate = rejections / n_fp_sets

    # PC verdict
    detect_ok = (p_excess <= 0.05 and dir_excess == "excess"
                 and p_def <= 0.05 and dir_def == "deficit")
    fp_ok = fp_rate <= 0.10
    pc_verdict = "PASSED" if (detect_ok and fp_ok) else "FAILED"

    return {
        "pc_verdict": pc_verdict,
        "detect_excess_p": p_excess,
        "detect_excess_obs": obs_excess,
        "detect_excess_dir": dir_excess,
        "detect_deficit_p": p_def,
        "detect_deficit_obs": obs_def,
        "detect_deficit_dir": dir_def,
        "false_pos_rate": fp_rate,
        "n_fp_sets": n_fp_sets,
    }


# ---------- cross-site ----------
def cross_site(inscriptions, n_draws=1000, seed=44000, min_runs=20):
    by_site = {}
    for ins in inscriptions:
        s = ins.get("site", "?") or "?"
        by_site.setdefault(s, []).append(ins)
    per_site = {}
    for site, ins_list in by_site.items():
        runs = corpus_runs(ins_list)
        if len(runs) >= min_runs:
            obs = p_compound_from_runs(runs)
            null = shuffle_null(ins_list, n_draws=n_draws, seed=seed + hash(site) % 100000)
            p = two_sided_p(obs, null)
            mean, direction = null_mean_and_direction(obs, null)
            per_site[site] = {
                "n_runs": len(runs), "p_compound": obs,
                "null_mean": mean, "p": p, "direction": direction,
            }
    return per_site

def leave_one_site_out(inscriptions, excluded_site, n_draws=1000, seed=44100):
    rest = [ins for ins in inscriptions if (ins.get("site", "?") or "?") != excluded_site]
    obs = p_compound_corpus(rest)
    null = shuffle_null(rest, n_draws=n_draws, seed=seed)
    p = two_sided_p(obs, null)
    mean, direction = null_mean_and_direction(obs, null)
    return {"loo_excluded": excluded_site, "loo_p_compound": obs,
            "loo_null_mean": mean, "loo_p": p, "loo_direction": direction}


# ---------- self-check ----------
def _selfcheck():
    # tiny synthetic: stream word,num,nl,word,num,nl -> two runs of length 1
    s = [{"t": "word"}, {"t": "num"}, {"t": "nl"}, {"t": "word"}, {"t": "num"}, {"t": "nl"}]
    assert runs_of_stream(s) == [1, 1], runs_of_stream(s)
    # compound: word,num,num,nl -> one run of length 2
    s2 = [{"t": "word"}, {"t": "num"}, {"t": "num"}, {"t": "nl"}]
    assert runs_of_stream(s2) == [2], runs_of_stream(s2)
    assert p_compound_from_runs([1, 2, 1]) == 1 / 3
    # shuffle preserves multiset
    rng = random.Random(0)
    s3 = [{"t": "num"}, {"t": "word"}, {"t": "num"}]
    sh = shuffle_inscription_stream(s3, rng)
    assert sorted(t.get("t") for t in sh) == ["num", "num", "word"]
    # two_sided_p sanity
    assert two_sided_p(0.0, [0.0] * 1000) <= 1.0
    print("SELF-CHECK OK")


if __name__ == "__main__":
    _selfcheck()
