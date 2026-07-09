#!/usr/bin/env python3
"""
EPOCH-057 machinery: structural role of the 'div' token (L2, token TYPES only).

Frozen metric:
  S1 (WORD|WORD ENRICHMENT): fraction of divs whose bracketing content-gap is word|word.
  S2 (WORD|NUM AVOIDANCE):   count of divs whose bracketing content-gap is word|num or num|word.

Frozen NULL: within each inscription, re-place the same number of div tokens uniformly at random
among the inter-content-token gaps (gaps between word/num/other tokens), preserving the
content-token sequence and div count. >=500 reshuffles. One-sided p: S1 enrichment, S2 depletion.

NO sign values, NO readings, NO phonetics/meaning. L2 only.
"""
import json, random, hashlib, sys
from collections import Counter

CONTENT_TYPES = {"word", "num", "other"}

# ---------- gap extraction ----------

def content_gaps(stream):
    """Return list of (before_type, after_type) gaps between consecutive CONTENT tokens
    (word/num/other), in stream order. nl/div are skipped when forming the content skeleton."""
    cseq = [tok.get("t") for tok in stream if tok.get("t") in CONTENT_TYPES]
    gaps = []
    for i in range(len(cseq) - 1):
        gaps.append((cseq[i], cseq[i+1]))
    return gaps

def observed_div_gaps(stream):
    """For each observed div token, map it to the content-gap it occupies: nearest preceding
    content token and nearest following content token in the original stream. Returns list of
    (before_type, after_type) for divs that have BOTH a preceding and following content token.
    Divs at stream start/end with no content token on one side are dropped from the gap analysis
    (they have no bracketing gap)."""
    n = len(stream)
    # precompute for each index the nearest preceding content index and nearest following content index
    prev_content = [-1]*n
    last = -1
    for i in range(n):
        if stream[i].get("t") in CONTENT_TYPES:
            last = i
        prev_content[i] = last
    next_content = [-1]*n
    nxt = -1
    for i in range(n-1, -1, -1):
        if stream[i].get("t") in CONTENT_TYPES:
            nxt = i
        next_content[i] = nxt
    out = []
    for i, tok in enumerate(stream):
        if tok.get("t") == "div":
            b = prev_content[i]
            a = next_content[i]
            if b != -1 and a != -1 and b < i < a:
                out.append((stream[b].get("t"), stream[a].get("t")))
    return out

# ---------- statistics ----------

def s1_fraction(div_gaps):
    """fraction of divs whose gap is word|word."""
    if not div_gaps:
        return 0.0
    ww = sum(1 for (b,a) in div_gaps if b=="word" and a=="word")
    return ww / len(div_gaps)

def s2_count(div_gaps):
    """count of divs whose gap is word|num or num|word."""
    return sum(1 for (b,a) in div_gaps if {b,a}=={"word","num"})

# ---------- null: gap reshuffle per inscription ----------

def null_stats_for_inscription(stream, n_div, rng):
    """Re-place n_div divs uniformly at random among the content gaps of this inscription
    (with replacement allowed if n_div > n_gaps, matching 'uniformly at random among gaps').
    Returns (s1_frac, s2_count, n_placed) for this inscription's simulated divs."""
    gaps = content_gaps(stream)
    if not gaps or n_div == 0:
        return (0.0, 0, 0)
    placed = [gaps[rng.randrange(len(gaps))] for _ in range(n_div)]
    return (s1_fraction(placed), s2_count(placed), len(placed))

def corpus_observed(inscriptions):
    """Aggregate observed div-gaps across all inscriptions."""
    all_gaps = []
    per_ins = []
    for ins in inscriptions:
        g = observed_div_gaps(ins["stream"])
        all_gaps.extend(g)
        per_ins.append((ins, g))
    return all_gaps, per_ins

def null_distribution(inscriptions, per_ins_observed, n_perm=500, seed=12345):
    """Per-inscription gap-reshuffle null. For each permutation, re-place each inscription's
    observed div count among its content gaps; aggregate S1 (pooled fraction) and S2 (pooled count)
    across the corpus. Returns lists of null S1 fractions and null S2 counts."""
    rng = random.Random(seed)
    null_s1 = []
    null_s2 = []
    # precompute gaps per inscription
    gaps_per = [content_gaps(ins["stream"]) for ins,_ in per_ins_observed]
    n_divs = [len(g) for _,g in per_ins_observed]
    for _ in range(n_perm):
        tot_ww = 0
        tot_wn = 0
        tot_placed = 0
        for gaps, nd in zip(gaps_per, n_divs):
            if not gaps or nd == 0:
                continue
            placed = [gaps[rng.randrange(len(gaps))] for _ in range(nd)]
            tot_ww += sum(1 for (b,a) in placed if b=="word" and a=="word")
            tot_wn += sum(1 for (b,a) in placed if {b,a}=={"word","num"})
            tot_placed += len(placed)
        null_s1.append(tot_ww/tot_placed if tot_placed else 0.0)
        null_s2.append(tot_wn)
    return null_s1, null_s2

def perm_p_one_sided(observed, null_vals, side):
    """side='ge' for enrichment (S1), 'le' for depletion (S2)."""
    n = len(null_vals)
    if n == 0:
        return 1.0
    if side == "ge":
        ge = sum(1 for v in null_vals if v >= observed)
    else:
        ge = sum(1 for v in null_vals if v <= observed)
    return (ge + 1) / (n + 1)

# ---------- synthetic corpora for positive control ----------

def synth_corpus_wordword_only(inscriptions, seed=1):
    """Build a synthetic corpus where, for each inscription, we place divs ONLY at word|word
    content gaps (never at word|num). Number of divs per inscription = observed div count
    (capped at #word|word gaps). Stream reconstructed as content tokens with divs inserted at
    chosen gaps (nl/other dropped for the synthetic skeleton — pure content+div stream)."""
    rng = random.Random(seed)
    out = []
    for ins in inscriptions:
        cseq = [tok.get("t") for tok in ins["stream"] if tok.get("t") in CONTENT_TYPES]
        ww_gaps_idx = [i for i in range(len(cseq)-1) if cseq[i]=="word" and cseq[i+1]=="word"]
        n_div = sum(1 for tok in ins["stream"] if tok.get("t")=="div")
        n_div = min(n_div, len(ww_gaps_idx))
        if n_div == 0 or not ww_gaps_idx:
            # no word|word gaps -> place no divs (consistent with the planted rule)
            stream = [{"t": t} for t in cseq]
            out.append({"site": ins.get("site"), "stream": stream})
            continue
        chosen = set(rng.sample(ww_gaps_idx, n_div))
        stream = []
        for i, t in enumerate(cseq):
            stream.append({"t": t})
            if i in chosen:
                stream.append({"t": "div"})
        out.append({"site": ins.get("site"), "stream": stream})
    return out

def synth_corpus_uniform(inscriptions, seed=1):
    """Build a synthetic corpus where divs are placed UNIFORMLY at random among ALL content gaps
    (including word|num). Number of divs per inscription = observed div count."""
    rng = random.Random(seed)
    out = []
    for ins in inscriptions:
        cseq = [tok.get("t") for tok in ins["stream"] if tok.get("t") in CONTENT_TYPES]
        gaps_idx = list(range(len(cseq)-1)) if len(cseq) > 1 else []
        n_div = sum(1 for tok in ins["stream"] if tok.get("t")=="div")
        n_div = min(n_div, len(gaps_idx))
        if n_div == 0 or not gaps_idx:
            stream = [{"t": t} for t in cseq]
            out.append({"site": ins.get("site"), "stream": stream})
            continue
        chosen = set(rng.sample(gaps_idx, n_div))
        stream = []
        for i, t in enumerate(cseq):
            stream.append({"t": t})
            if i in chosen:
                stream.append({"t": "div"})
        out.append({"site": ins.get("site"), "stream": stream})
    return out

# ---------- self-check ----------

def self_check():
    """Validate the gap-reshuffle null on a tiny synthetic where divs are placed only at word|word
    gaps. Expect S1 enriched (p<=0.05) and S2 depleted (p<=0.05). Also validate that a uniform
    placement is NOT flagged (sanity)."""
    # tiny synthetic: 1 inscription, content = word word num word word num ... repeated
    base = ["word","word","num","word","word","num"]*10
    stream = [{"t": t} for t in base]
    # place 10 divs only at word|word gaps
    ww_idx = [i for i in range(len(base)-1) if base[i]=="word" and base[i+1]=="word"]
    rng = random.Random(7)
    chosen = set(rng.sample(ww_idx, 10))
    s = []
    for i,t in enumerate(base):
        s.append({"t": t})
        if i in chosen:
            s.append({"t":"div"})
    ins = [{"site":"X","stream":s}]
    obs_gaps, per_ins = corpus_observed(ins)
    s1o = s1_fraction(obs_gaps); s2o = s2_count(obs_gaps)
    n1, n2 = null_distribution(ins, per_ins, n_perm=500, seed=99)
    p1 = perm_p_one_sided(s1o, n1, "ge")
    p2 = perm_p_one_sided(s2o, n2, "le")
    print(f"[self-check] word|word-only synthetic: S1 obs={s1o:.3f} null_mean={sum(n1)/len(n1):.3f} p={p1:.4f} | S2 obs={s2o} null_mean={sum(n2)/len(n2):.3f} p={p2:.4f}")
    ok_detect = (p1 <= 0.05 and p2 <= 0.05)
    # uniform placement sanity
    us = synth_corpus_uniform(ins, seed=3)
    uobs, uper = corpus_observed(us)
    us1 = s1_fraction(uobs); us2 = s2_count(uobs)
    un1, un2 = null_distribution(us, uper, n_perm=500, seed=101)
    up1 = perm_p_one_sided(us1, un1, "ge"); up2 = perm_p_one_sided(us2, un2, "le")
    print(f"[self-check] uniform synthetic: S1 obs={us1:.3f} null_mean={sum(un1)/len(un1):.3f} p={up1:.4f} | S2 obs={us2} null_mean={sum(un2)/len(un2):.3f} p={up2:.4f}")
    print(f"[self-check] detect_ok={ok_detect}")
    return ok_detect

if __name__ == "__main__":
    ok = self_check()
    print("SELF_CHECK_OK" if ok else "SELF_CHECK_FAIL")
    sys.exit(0 if ok else 1)
