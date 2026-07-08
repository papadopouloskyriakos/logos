#!/usr/bin/env python3
"""
EPOCH-049 machinery — INSCRIPTION-LEVEL SIGN CO-OCCURRENCE (document-topic; L2/L3).

Pure document-level co-occurrence of ANONYMOUS signs. No phonetics, no sound, no meaning, no reading.
Sign set of an inscription = set of distinct signs appearing anywhere in its words.

FROZEN METRIC: cooc_score = # sign PAIRS (s,t) with co-occurrence count >= COUNT_THRESH AND
              z >= Z_THRESH under an independent-placement (hypergeometric) per-pair null.
FROZEN NULL:   degree-preserving bipartite shuffle (curveball swaps) of the sign x inscription
               incidence matrix, preserving each inscription's sign-set SIZE and each sign's
               document frequency (row+col marginals exactly). >=N_DRAWS draws. One-sided p for
               "more co-occurrence structure than chance".

POSITIVE CONTROL (gates verdict):
  (a) DETECT — plant known co-occurring sign-groups (topics) into a synthetic incidence matrix;
      confirm cooc_score >> null (p<=0.05).
  (b) FALSE-POSITIVE — on a degree-matched RANDOM incidence matrix (no real topics), rejection
      rate <=0.10 across >=20 sets.
  If cannot detect planted topics OR fires on random-degree-matched matrices -> MACHINERY_UNINFORMATIVE.

Self-check: `python3 machinery.py` runs PC + global + cross-site and prints a JSON summary.
"""
import json, os, sys, math, random
from collections import Counter, defaultdict
from itertools import combinations

# ---------- paths ----------
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
CORPUS = os.path.join(REPO, "corpus", "silver", "inscriptions_structured.json")
SCRIPTS = os.path.join(REPO, "scripts")

# ---------- frozen constants ----------
SEED_GLOBAL = 49001
SEED_PC_DETECT = 49002
SEED_FP = 49003
SEED_SITE = 49004
N_DRAWS = 600          # >=500
N_FP_CONTROLS = 25    # >=20
Z_THRESH = 3.0
COUNT_THRESH = 5
SITE_MIN = 30

# ---------- corpus IO ----------
def load_corpus(path=CORPUS):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_b_damos():
    sys.path.insert(0, SCRIPTS)
    from cross_script import data as D
    seqs, freq, v2g = D.load_b_damos()
    return seqs

# ---------- build incidence ----------
def inscription_signset(insc):
    s = set()
    for tok in insc.get("stream", []) or []:
        if tok.get("t") == "word":
            for sg in tok.get("signs", []):
                if sg:
                    s.add(sg)
    return s

def build_incidence(corpus):
    """Return (docs, sign_index) where docs is a list of sets-of-signids.
    Only inscriptions with >=2 distinct signs."""
    sign_id = {}
    docs = []
    for ins in corpus:
        s = inscription_signset(ins)
        if len(s) >= 2:
            ids = set()
            for sg in s:
                if sg not in sign_id:
                    sign_id[sg] = len(sign_id)
                ids.add(sign_id[sg])
            docs.append(ids)
    return docs, sign_id

# ---------- per-pair z and cooc_score ----------
def pair_z_matrix(docs, S):
    """Compute cooc counts and per-pair z (hypergeometric) for all pairs.
    Returns dict (a,b)->(C, E, var, z) for a<b, plus cooc_score."""
    N = len(docs)
    df = [0] * S
    for d in docs:
        for a in d:
            df[a] += 1
    # co-occurrence counts
    cooc = Counter()
    for d in docs:
        dl = sorted(d)
        for i in range(len(dl)):
            for j in range(i + 1, len(dl)):
                cooc[(dl[i], dl[j])] += 1
    score = 0
    pair_info = {}
    for (a, b), C in cooc.items():
        Ea = df[a]; Eb = df[b]
        E = (Ea * Eb) / N
        var = E * (1.0 - Eb / N) * (N - Ea) / (N - 1.0)
        if var <= 0:
            z = 0.0
        else:
            z = (C - E) / math.sqrt(var)
        pair_info[(a, b)] = (C, E, var, z)
        if C >= COUNT_THRESH and z >= Z_THRESH:
            score += 1
    return score, pair_info, df, cooc

def cooc_score_only(docs, S):
    N = len(docs)
    df = [0] * S
    for d in docs:
        for a in d:
            df[a] += 1
    cooc = Counter()
    for d in docs:
        dl = sorted(d)
        for i in range(len(dl)):
            for j in range(i + 1, len(dl)):
                cooc[(dl[i], dl[j])] += 1
    score = 0
    for (a, b), C in cooc.items():
        if C < COUNT_THRESH:
            continue
        Ea = df[a]; Eb = df[b]
        E = (Ea * Eb) / N
        var = E * (1.0 - Eb / N) * (N - Ea) / (N - 1.0)
        if var <= 0:
            continue
        z = (C - E) / math.sqrt(var)
        if z >= Z_THRESH:
            score += 1
    return score

# ---------- curveball degree-preserving shuffle ----------
def curveball_shuffle(docs, S, n_passes, rng):
    """Degree-preserving bipartite shuffle via curveball trades on the incidence matrix.
    Each pass: for each pair of docs (random order), swap their differing sign-memberships
    (subset of symmetric difference) so that each doc keeps its size and each sign keeps its df.
    Returns new list of sets."""
    # work on mutable lists
    cur = [sorted(d) for d in docs]
    # build sign->docs index for efficient trades
    nd = len(cur)
    for _ in range(n_passes):
        order = list(range(nd))
        rng.shuffle(order)
        # iterate random pairs
        for ii in range(0, nd - 1, 2):
            i = order[ii]; j = order[ii + 1]
            si = set(cur[i]); sj = set(cur[j])
            only_i = list(si - sj)
            only_j = list(sj - si)
            if not only_i or not only_j:
                continue
            k = min(len(only_i), len(only_j))
            rng.shuffle(only_i); rng.shuffle(only_j)
            take_i = set(only_i[:k])
            take_j = set(only_j[:k])
            new_i = (si - take_i) | take_j
            new_j = (sj - take_j) | take_i
            cur[i] = sorted(new_i)
            cur[j] = sorted(new_j)
    return [set(x) for x in cur]

def null_distribution(docs, S, n_draws, seed, n_passes=5):
    rng = random.Random(seed)
    scores = []
    obs = cooc_score_only(docs, S)
    for _ in range(n_draws):
        shuf = curveball_shuffle(docs, S, n_passes, rng)
        scores.append(cooc_score_only(shuf, S))
    mean = sum(scores) / len(scores)
    # one-sided p: P(null >= obs)
    ge = sum(1 for s in scores if s >= obs)
    p = (ge + 1) / (len(scores) + 1)
    return obs, mean, p, scores

# ---------- positive control ----------
def synthetic_topic_matrix(n_docs, S, topic_blocks, bg_fill, rng):
    """Build incidence with planted topics. topic_blocks: list of (set_of_signids, n_docs_using_topic).
    Each topic doc = topic signs + a few background signs. Plus pure-background docs.
    Returns list of sets."""
    docs = []
    for signs, nd in topic_blocks:
        for _ in range(nd):
            d = set(signs)
            # add a couple background signs
            nbg = rng.randint(0, bg_fill)
            for _ in range(nbg):
                d.add(rng.randint(0, S - 1))
            if len(d) >= 2:
                docs.append(d)
    # background docs (random sign-sets of size 3-6)
    n_bg = n_docs - len(docs)
    for _ in range(max(0, n_bg)):
        k = rng.randint(3, 6)
        d = set(rng.sample(range(S), k))
        docs.append(d)
    return docs

def random_degree_matched_matrix(target_sizes, S, rng):
    """Random incidence with given doc sizes and approximately matched sign frequencies
    (no planted topics). Sample signs for each doc independently by a shared frequency vector
    built to roughly match a uniform-ish distribution."""
    docs = []
    for k in target_sizes:
        d = set(rng.sample(range(S), k))
        docs.append(d)
    return docs

def positive_control_detect(seed):
    """Plant topics; expect cooc_score >> null, p<=0.05."""
    rng = random.Random(seed)
    S = 60
    # 4 topics, each a block of 5 signs used together in many docs
    topics = []
    used = set()
    for t in range(4):
        while True:
            blk = set(rng.sample(range(S), 5))
            if not (blk & used):
                used |= blk
                break
        topics.append((blk, 40))
    docs = synthetic_topic_matrix(n_docs=400, S=S, topic_blocks=topics, bg_fill=2, rng=rng)
    obs, mean, p, scores = null_distribution(docs, S, N_DRAWS, seed)
    return obs, mean, p

def positive_control_falsepos(seed):
    """Degree-matched RANDOM matrices (no topics); rejection rate must be <=0.10."""
    rng = random.Random(seed)
    S = 60
    # target doc sizes drawn from a realistic distribution
    target_sizes_pool = [3, 4, 4, 5, 5, 6, 6, 7]
    rej = 0
    ps = []
    for i in range(N_FP_CONTROLS):
        sizes = [rng.choice(target_sizes_pool) for _ in range(400)]
        docs = random_degree_matched_matrix(sizes, S, rng)
        # ensure >=2 distinct signs per doc
        docs = [d for d in docs if len(d) >= 2]
        obs, mean, p, scores = null_distribution(docs, S, 200, seed + i)
        ps.append(p)
        if p <= 0.05:
            rej += 1
    return rej / N_FP_CONTROLS, ps

# ---------- cross-site ----------
def build_site_incidence(corpus):
    sign_id = {}
    by_site = defaultdict(list)
    for ins in corpus:
        s = inscription_signset(ins)
        if len(s) >= 2:
            site = ins.get("site", "") or "UNKNOWN"
            ids = set()
            for sg in s:
                if sg not in sign_id:
                    sign_id[sg] = len(sign_id)
                ids.add(sign_id[sg])
            by_site[site].append(ids)
    return by_site, sign_id

def cross_site_analysis(corpus, seed):
    by_site, sign_id = build_site_incidence(corpus)
    S = len(sign_id)
    testable = [(st, ds) for st, ds in by_site.items() if len(ds) >= SITE_MIN]
    results = {}
    n_sig = 0
    for st, ds in testable:
        obs, mean, p, scores = null_distribution(ds, S, N_DRAWS, seed)
        results[st] = {"n": len(ds), "cooc_score": obs, "null_mean": mean, "p": p}
        if p <= 0.05:
            n_sig += 1
    # held-out replication: largest site top pairs vs pooled others
    heldout_frac = 0.0
    loo_p = 1.0
    loo_excluded = ""
    if testable:
        largest = max(testable, key=lambda x: len(x[1]))
        lst, lds = largest
        # top pairs in largest site
        score, pair_info, df, cooc = pair_z_matrix(lds, S)
        top_pairs = sorted(
            [(pair, info[0], info[3]) for pair, info in pair_info.items() if info[0] >= COUNT_THRESH],
            key=lambda x: -x[2]
        )[:20]
        # pooled others
        others = []
        for st, ds in by_site.items():
            if st != lst:
                others.extend(ds)
        if others:
            # compute cooc + z in others
            No = len(others)
            dfo = [0] * S
            for d in others:
                for a in d:
                    dfo[a] += 1
            cooco = Counter()
            for d in others:
                dl = sorted(d)
                for i in range(len(dl)):
                    for j in range(i + 1, len(dl)):
                        cooco[(dl[i], dl[j])] += 1
            replicated = 0
            for pair, C_l, z_l in top_pairs:
                C_o = cooco.get(pair, 0)
                if C_o < COUNT_THRESH:
                    continue
                a, b = pair
                E = (dfo[a] * dfo[b]) / No
                var = E * (1.0 - dfo[b] / No) * (No - dfo[a]) / (No - 1.0)
                if var <= 0:
                    continue
                z_o = (C_o - E) / math.sqrt(var)
                if z_o >= Z_THRESH:
                    replicated += 1
            heldout_frac = replicated / max(1, len(top_pairs))
        # leave-one-site-out on the largest site: drop largest, test pooled rest
        rest = []
        for st, ds in by_site.items():
            if st != lst:
                rest.extend(ds)
        if len(rest) >= SITE_MIN:
            obs, mean, p, scores = null_distribution(rest, S, N_DRAWS, seed + 7)
            loo_p = p
            loo_excluded = lst
    return {
        "n_sites_testable": len(testable),
        "n_sites_sig": n_sig,
        "per_site": results,
        "heldout_replication_frac": heldout_frac,
        "loo_excluded": loo_excluded,
        "loo_p": loo_p,
    }

# ---------- main self-check ----------
def main():
    print("=== EPOCH-049 machinery self-check ===", file=sys.stderr)
    corpus = load_corpus()
    docs, sign_id = build_incidence(corpus)
    S = len(sign_id)
    print(f"[inspect] n_inscriptions(>=2 signs)={len(docs)} S={S}", file=sys.stderr)

    # PC DETECT
    obs_d, mean_d, p_d = positive_control_detect(SEED_PC_DETECT)
    print(f"[PC detect] obs={obs_d} null_mean={mean_d:.2f} p={p_d:.4f}", file=sys.stderr)
    # PC FALSE-POS
    fpr, ps = positive_control_falsepos(SEED_FP)
    print(f"[PC falsepos] rate={fpr:.3f}", file=sys.stderr)
    pc_pass = (p_d <= 0.05) and (fpr <= 0.10)
    pc_verdict = "PASSED" if pc_pass else "FAILED"
    print(f"[PC verdict] {pc_verdict}", file=sys.stderr)

    # GLOBAL
    g_obs, g_mean, g_p, g_scores = null_distribution(docs, S, N_DRAWS, SEED_GLOBAL)
    print(f"[GLOBAL] cooc_score={g_obs} null_mean={g_mean:.2f} p={g_p:.4f}", file=sys.stderr)

    # CROSS-SITE
    cs = cross_site_analysis(corpus, SEED_SITE)
    print(f"[CROSS-SITE] testable={cs['n_sites_testable']} sig={cs['n_sites_sig']} "
          f"heldout_frac={cs['heldout_replication_frac']:.3f} loo_p={cs['loo_p']:.4f}", file=sys.stderr)

    summary = {
        "pc_verdict": pc_verdict,
        "pc_detect_p": p_d,
        "pc_false_pos_rate": fpr,
        "global": {"n_inscriptions": len(docs), "cooc_score": g_obs,
                   "null_mean": g_mean, "null_p": g_p, "count_threshold": COUNT_THRESH},
        "cross_site": cs,
    }
    print(json.dumps(summary, indent=2))
    return summary

if __name__ == "__main__":
    main()
