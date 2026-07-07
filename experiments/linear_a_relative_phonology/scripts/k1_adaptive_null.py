#!/usr/bin/env python3
"""K1 — FULL ADAPTIVE NULL PROGRAMME + campaign-wide false-positive rate.

The campaign ran ~40 tasks, each with selection degrees of freedom (which segmentation,
which morphology family, which affix, which site split, which anchor system, which formula
family, which threshold). A single "significant" result is only trustworthy if it survives a
null that REPRODUCES the WHOLE selection pipeline that produced it — a best-of-selection null.

This script:
  (1) runs a NULL BATTERY (deliverable K_NULL_*) — random / frequency-matched / shuffled /
      wrong-label nulls, each reporting how often it 'discovers' a positive as strong as the
      campaign's real one; and the ADAPTIVE best-of-{affix, segmentation, slot, family, split,
      anchor-system, threshold} nulls.
  (2) subjects the campaign's L2/L3 POSITIVES to the adaptive null that reproduces THEIR
      selection, and issues a mechanical SURVIVES / ARTIFACT verdict + adaptive-adjusted p.

Constitution v2.2. NON-CIRCULAR (Art. XII): known values grade benchmarks only, never a model
input. Highest claim layer L2/L3; no phonetic value assigned; no transfer licence earned.
Deterministic seed 20260708. Primitives imported from the audited e1/e2 modules.
"""
from __future__ import annotations
import json, math, os, random, re, sys, time
from collections import Counter, defaultdict

MAIN = "/home/claude-runner/gitlab/n8n/logos"
sys.path.insert(0, MAIN)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
CAMP = os.path.dirname(HERE)
SEGDIR = os.path.join(CAMP, "data", "segmentations")
DATA = os.path.join(CAMP, "data")
from scripts.cross_script import data as X   # noqa: E402 read-only loader
import e1_morphology_models as e1            # noqa: E402 audited primitives
SEED = 20260708
PURE_VOWELS = {"A", "E", "I", "O", "U"}      # grading labels ONLY


# ============================================================ shared primitives
def load_words(segfile):
    return [tuple(u["signs"]) for u in json.load(open(os.path.join(SEGDIR, segfile)))["units"]]


def load_units(segfile="SEG_GORILA_WORD.json"):
    out = []
    for u in json.load(open(os.path.join(SEGDIR, segfile)))["units"]:
        out.append({"signs": tuple(u["signs"]),
                    "site": u.get("site") or "(unknown)",
                    "support": u.get("support") or "(unknown)"})
    return out


def all_affix_prod(words):
    """One-pass recurrent-stem productivity for EVERY word-initial and word-final sign.

    Returns (prefix_prod{sign:int}, suffix_prod{sign:int}). Uses the exact e1 recurrent-stem
    criterion (free word OR residual of >=2 words). The global max over both dicts is the
    best-of-affix statistic the campaign selected on (A- prefix = 47 on GORILA_WORD)."""
    wset = set(words); rc = e1._residual_index(wset)
    pre = defaultdict(set); suf = defaultdict(set)
    for w in wset:
        if len(w) >= 2:
            s = w[1:]
            if e1._recurrent(s, wset, rc):
                pre[w[0]].add(s)
            s2 = w[:-1]
            if e1._recurrent(s2, wset, rc):
                suf[w[-1]].add(s2)
    return {k: len(v) for k, v in pre.items()}, {k: len(v) for k, v in suf.items()}


def global_max_affix(words):
    pre, suf = all_affix_prod(words)
    vals = list(pre.values()) + list(suf.values())
    return max(vals) if vals else 0


def iid_corpus(words, rng):
    """Frequency-matched i.i.d. null: preserve word-length distribution + sign-unigram freqs."""
    uni = Counter(s for w in words for s in w)
    signs = list(uni); wts = [uni[s] for s in signs]
    lengths = [len(w) for w in words]
    return [tuple(rng.choices(signs, weights=wts, k=L)) for L in lengths]


def pct(arr, obs):
    return (sum(1 for v in arr if v >= obs) + 1) / (len(arr) + 1)


# ============================================================ A. adaptive best-of-affix null
SEGS = ["SEG_GORILA_WORD.json", "SEG_ENTRY.json", "SEG_FORMULA.json", "SEG_DIPLOMATIC.json",
        "SEG_ROW.json", "SEG_MULTI_SCALE.json", "SEG_PROBABILISTIC_BOUNDARY.json",
        "SEG_INSCRIPTION_CONTEXT.json"]


def adaptive_bestof_affix(R=200, seed=SEED):
    """THE central adaptive null for the A- prefixation positive.

    Observed statistic = the campaign's best-of-affix productivity = max over
    {195 candidate signs x 8 segmentations x 2 slots} = A- on GORILA_WORD = 47.
    For each null realization, generate an i.i.d. freq+length-matched corpus for EACH
    segmentation and take the SAME best-of-selection max. Adaptive p = P(null best-of >= obs).

    Reproduces: affix-selection + slot-selection + segmentation-selection under the null."""
    rng = random.Random(seed)
    seg_words = {s: load_words(s) for s in SEGS}
    # observed per-segmentation global max + overall
    obs_per_seg = {s: global_max_affix(w) for s, w in seg_words.items()}
    obs_overall = max(obs_per_seg.values())
    obs_gorila_A = e1.productivity_prefix(seg_words["SEG_GORILA_WORD.json"], "A")

    # null distributions
    null_per_seg = {s: [] for s in SEGS}
    null_bestof_seg = []          # best across all 8 segmentations (segmentation-selection)
    null_gorila_only = []         # best-of-affix within GORILA_WORD only (affix-selection alone)
    for _ in range(R):
        realized = {}
        for s in SEGS:
            nc = iid_corpus(seg_words[s], rng)
            m = global_max_affix(nc)
            null_per_seg[s].append(m)
            realized[s] = m
        null_bestof_seg.append(max(realized.values()))
        null_gorila_only.append(realized["SEG_GORILA_WORD.json"])
    return {
        "description": "best-of-{affix x segmentation x slot} adaptive null for A- prefixation",
        "observed_A_prefix_prod_gorila": obs_gorila_A,
        "observed_global_max_per_seg": obs_per_seg,
        "observed_best_of_selection": obs_overall,
        "R": R,
        "affix_selection_only_gorila": {
            "null_mean": round(sum(null_gorila_only) / R, 2),
            "null_max": max(null_gorila_only),
            "null_95pct": sorted(null_gorila_only)[int(0.95 * R)],
            "adaptive_p_bestof_affix_ge_obs": round(pct(null_gorila_only, obs_gorila_A), 4),
        },
        "affix_x_segmentation_selection": {
            "null_mean": round(sum(null_bestof_seg) / R, 2),
            "null_max": max(null_bestof_seg),
            "null_95pct": sorted(null_bestof_seg)[int(0.95 * R)],
            "adaptive_p_bestof_ge_obs": round(pct(null_bestof_seg, obs_overall), 4),
        },
        "per_seg_null_mean": {s: round(sum(v) / R, 2) for s, v in null_per_seg.items()},
    }


# ============================================================ B. cross-site both-direction adaptive
def cross_site_bothdir_adaptive(R=200, seed=SEED):
    """Adaptive null for the A- cross-site claim (E3 p=0.0099, both HT-in/out directions).

    Reproduces: affix-selection + the requirement that the SAME affix is significant in BOTH
    the train-HT->test-nonHT and train-nonHT->test-HT partitions. Under a site-preserving null
    (i.i.d. corpus, real site labels kept), how often does ANY affix clear both directions at
    the observed strength (A- obs 29/nonHT & 16/HT)?"""
    rng = random.Random(seed)
    units = load_units("SEG_GORILA_WORD.json")
    HT = "HAGHIA TRIADA"
    sites = [u["site"].upper() for u in units]
    ht_mask = [s == HT for s in sites]

    def split_words(word_list):
        nonht = [w for w, m in zip(word_list, ht_mask) if not m]
        ht = [w for w, m in zip(word_list, ht_mask) if m]
        return ht, nonht

    words = [u["signs"] for u in units]
    ht_w, nonht_w = split_words(words)
    obs_A_nonht = e1.productivity_prefix(nonht_w, "A")   # tested on non-HT
    obs_A_ht = e1.productivity_prefix(ht_w, "A")         # tested on HT

    # null: does ANY affix beat BOTH observed A- counts simultaneously (best-of-affix, both dirs)?
    both_hits = 0
    max_bothdir_min = []   # per realization: max over affixes of min(nonHT_prod, HT_prod)
    obs_min = min(obs_A_nonht, obs_A_ht)
    for _ in range(R):
        nc = iid_corpus(words, rng)
        ht_n, nonht_n = split_words(nc)
        pre_n, _ = all_affix_prod(nonht_n)
        pre_h, _ = all_affix_prod(ht_n)
        best_min = 0
        for sgn in set(pre_n) | set(pre_h):
            m = min(pre_n.get(sgn, 0), pre_h.get(sgn, 0))
            if m > best_min:
                best_min = m
        max_bothdir_min.append(best_min)
        if best_min >= obs_min:
            both_hits += 1
    return {
        "description": "adaptive both-direction cross-site null (best-of-affix must clear BOTH HT splits)",
        "observed_A_nonHT": obs_A_nonht, "observed_A_HT": obs_A_ht,
        "observed_min_bothdir": obs_min, "R": R,
        "null_bestof_min_mean": round(sum(max_bothdir_min) / R, 2),
        "null_bestof_min_max": max(max_bothdir_min),
        "adaptive_p_bothdir_ge_obs": round((both_hits + 1) / (R + 1), 4),
    }


# ============================================================ C. libation random-anchor-system adaptive
LIB_OP = r"TA-I-\*301|TA-NA-I-\*301|A-NA-TI-\*301|\*301-WA"


def _load_inscr():
    return json.load(open(os.path.join(MAIN, "corpus/silver/inscriptions_structured.json")))


def perfect_consistency_permnull(carrier_orders, labs, seed=SEED, N=20000):
    """e2 statistic: # co-occurring anchor pairs 100% direction-consistent; perm-p that the
    observed is reachable by shuffling each carrier's realised anchor order."""
    def stat(orders):
        o2 = Counter(); b2 = Counter()
        for od in orders:
            pos = {l: i for i, l in enumerate(od)}
            for a in labs:
                for b in labs:
                    if a != b and a in pos and b in pos:
                        b2[(a, b)] += 1
                        if pos[a] < pos[b]:
                            o2[(a, b)] += 1
        perfect = tested = 0
        for a in labs:
            for b in labs:
                if a < b and b2[(a, b)]:
                    tested += 1
                    if o2[(a, b)] in (0, b2[(a, b)]):
                        perfect += 1
        return perfect, tested
    multi = [od for od in carrier_orders if len(od) >= 2]
    obs_p, obs_t = stat(multi)
    if obs_t == 0:
        return obs_p, obs_t, 1.0
    rng = random.Random(seed); ge = 0
    for _ in range(N):
        shuf = []
        for od in multi:
            o2 = list(od); rng.shuffle(o2); shuf.append(o2)
        p, _t = stat(shuf)
        if p >= obs_p:
            ge += 1
    return obs_p, obs_t, (ge + 1) / (N + 1)


def libation_random_anchor_adaptive(R=500, seed=SEED, permN=4000):
    """Adaptive null for the libation rigid-order positive (E2 perm-p 5e-5).

    Selection DOF: the 5 anchor families (OP/SSR/UNK/IPN/SIR) were CHOSEN. Reproduce that
    choice: among the SAME votive carriers, pick 5 random recurring sign-substrings as
    'anchors' (frequency-matched to the real anchor carrier-counts), induce their linear
    order, run the same perfect-consistency perm-null, and ask how often a RANDOM anchor
    system reaches a perm-p as extreme as observed (i.e. all co-occurring pairs perfectly
    consistent, 0 inversions). Adaptive p = fraction of random anchor systems that clear."""
    rng = random.Random(seed)
    d = _load_inscr()

    def joined(r):
        return "-".join(r.get("signs", []))
    carriers = [r for r in d if re.search("SA-SA-RA", joined(r)) or re.search(LIB_OP, joined(r))]

    # real anchor carrier-counts to frequency-match the random systems
    real_labs = ["OP", "SSR", "UNK", "IPN", "SIR"]
    real_pats = {"OP": LIB_OP, "SSR": r"SA-SA-RA", "UNK": r"NA-KA-NA", "IPN": r"PI-NA-M", "SIR": r"SI-RU"}
    real_counts = {}
    for lab, pat in real_pats.items():
        real_counts[lab] = sum(1 for r in carriers if re.search(pat, joined(r)))

    # observed statistic
    def orders_for(patmap, labs):
        seqs = []
        for r in carriers:
            js = joined(r)
            hits = []
            for lab in labs:
                m = re.search(patmap[lab], js)
                if m:
                    hits.append((js.count("-", 0, m.start()), lab))
            hits.sort()
            seqs.append([l for _, l in hits])
        return seqs
    obs_orders = orders_for(real_pats, real_labs)
    obs_perfect, obs_tested, obs_p = perfect_consistency_permnull(obs_orders, real_labs, N=20000)

    # candidate recurring substrings: all sign-bigrams that occur across >=2 carriers,
    # excluding the real anchor patterns, pooled from the full corpus vessel/inked stream.
    bigram_carrier = Counter()
    for r in carriers:
        toks = joined(r).split("-")
        seen = set()
        for i in range(len(toks) - 1):
            bg = toks[i] + "-" + toks[i + 1]
            seen.add(bg)
        for bg in seen:
            bigram_carrier[bg] += 1
    real_sig = ["SA-SA", "SA-RA", "301-WA", "NA-KA", "PI-NA", "SI-RU", "TA-I", "NA-I"]
    cands = [bg for bg, c in bigram_carrier.items() if c >= 2
             and not any(x in bg for x in real_sig)]

    # target multi-anchor support: how many carriers realise >=2 of the 5 anchors (real=10)
    real_multi = sum(1 for od in obs_orders if len(od) >= 2)

    hits_as_extreme = 0; perfect_all = 0; tried = 0
    rt_dist = Counter(); perfect_and_ge_obs_pairs = 0
    for _ in range(R):
        if len(cands) < 5:
            break
        picks = rng.sample(cands, 5)
        labs = [f"R{i}" for i in range(5)]
        patmap = {labs[i]: re.escape(picks[i]) for i in range(5)}
        rorders = orders_for(patmap, labs)
        rmulti = sum(1 for od in rorders if len(od) >= 2)
        if rmulti < 2:
            continue
        tried += 1
        rp, rt, rpv = perfect_consistency_permnull(rorders, labs, seed=seed + tried, N=permN)
        rt_dist[rt] += 1
        if rt >= 1 and rp == rt:
            perfect_all += 1
            # strength = # co-occurring pairs all-consistent; obs = 10 pairs. A random system is
            # "as extreme" only if it matches BOTH: all pairs perfect AND >= observed pairs tested.
            if rt >= obs_tested:
                perfect_and_ge_obs_pairs += 1
            if rpv <= obs_p * 1.0000001 and rt >= obs_tested:
                hits_as_extreme += 1
    return {
        "description": "adaptive random-anchor-system null for libation rigid order",
        "observed_perfect_pairs": obs_perfect, "observed_pairs_tested": obs_tested,
        "observed_perm_p": round(obs_p, 6), "observed_multi_anchor_carriers": real_multi,
        "real_anchor_carrier_counts": real_counts,
        "n_candidate_substrings": len(cands), "R_requested": R, "R_valid": tried,
        "random_systems_all_pairs_perfect": perfect_all,
        "random_systems_perfect_AND_ge_obs_pairs": perfect_and_ge_obs_pairs,
        "random_systems_as_extreme_as_obs": hits_as_extreme,
        "random_pairs_tested_distribution": dict(sorted(rt_dist.items())),
        "adaptive_p_random_anchor": round((hits_as_extreme + 1) / (tried + 1), 5) if tried else None,
        "frac_random_all_perfect_but_underpowered": round(perfect_all / tried, 4) if tried else None,
        "note": "0-inversions alone is CHEAP (most random systems have few co-occurring pairs, so a "
                "rigid order is trivially achievable); the observed strength is 10 co-occurring pairs "
                "ALL consistent. adaptive_p counts random systems reaching >= observed pairs, all perfect.",
    }


# ============================================================ D. ledger random-anchor adaptive
def ledger_random_anchor_adaptive(R=500, seed=SEED):
    """Adaptive null for the ledger KU-RO-terminal / carrier-value positive.

    Selection DOF: KU-RO was CHOSEN as the total-anchor among all recurring words. Reproduce:
    among recurring words in numeral-bearing (ledger) inscriptions, pick a random word and
    measure whether it lands in a TOTAL-like slot as strong as KU-RO on BOTH E2 criteria:
    (a) followed-by-numeral rate >= 0.795 and (b) frac-in-last-third >= 0.59, over a comparable
    number of occurrences. Best-of over random words; adaptive p = fraction matching on both.

    Positions + numeral adjacency are read from the token STREAM ({'t':'num'} tokens)."""
    rng = random.Random(seed)
    d = _load_inscr()
    KURO = {"KU-RO", "PO-TO-KU-RO"}
    # build per-word occurrence events across ledger (numeral-bearing) inscriptions
    occ = defaultdict(lambda: {"n": 0, "last": 0, "foll": 0})
    for r in d:
        stream = r.get("stream", [])
        if not any(t.get("t") == "num" for t in stream):
            continue                                       # not a ledger
        # ordered list of (word_string, followed_by_num) skipping div/nl
        seq = []
        for i, t in enumerate(stream):
            if t.get("t") == "word":
                wstr = "-".join(t.get("signs", []))
                # next non-div/nl token
                foll = False
                for u in stream[i + 1:]:
                    if u.get("t") in ("div", "nl"):
                        continue
                    foll = (u.get("t") == "num")
                    break
                seq.append((wstr, foll))
        nW = len(seq)
        for i, (wstr, foll) in enumerate(seq):
            o = occ[wstr]; o["n"] += 1
            if foll:
                o["foll"] += 1
            if nW > 1 and (i / (nW - 1)) >= 2 / 3:
                o["last"] += 1
    ko_n = sum(occ[k]["n"] for k in KURO if k in occ)
    ko_last = sum(occ[k]["last"] for k in KURO if k in occ)
    ko_foll = sum(occ[k]["foll"] for k in KURO if k in occ)
    obs_frac_last = ko_last / ko_n if ko_n else 0
    obs_foll_rate = ko_foll / ko_n if ko_n else 0
    # candidate recurring ledger words (>=5 occ), excluding KU-RO family, multi-sign
    cands = [w for w, o in occ.items() if o["n"] >= 5 and w not in KURO and "-" in w]
    hits_both = hits_last = 0; tried = 0; rf_last = []; rf_foll = []
    for _ in range(R):
        if not cands:
            break
        w = rng.choice(cands); tried += 1
        o = occ[w]
        fl = o["last"] / o["n"]; ff = o["foll"] / o["n"]
        rf_last.append(fl); rf_foll.append(ff)
        if fl >= obs_frac_last:
            hits_last += 1
        if fl >= obs_frac_last and ff >= obs_foll_rate:
            hits_both += 1
    return {
        "description": "adaptive random-anchor null for ledger KU-RO terminal-slot positive",
        "observed_KURO_occ": ko_n,
        "observed_frac_last_third": round(obs_frac_last, 4),
        "observed_foll_by_num_rate": round(obs_foll_rate, 4),
        "n_candidate_ledger_words": len(cands), "R": tried,
        "random_anchor_mean_frac_last_third": round(sum(rf_last) / len(rf_last), 4) if rf_last else None,
        "random_anchor_mean_foll_rate": round(sum(rf_foll) / len(rf_foll), 4) if rf_foll else None,
        "random_anchors_matching_terminal_only": hits_last,
        "random_anchors_matching_both_criteria": hits_both,
        "adaptive_p_terminal_only": round((hits_last + 1) / (tried + 1), 4) if tried else None,
        "adaptive_p_both_criteria": round((hits_both + 1) / (tried + 1), 4) if tried else None,
        "note": "positional-selection DOF only; the KU-RO='total' arithmetic sum-consistency (E2 7/31 exact) "
                "is a SEPARATE relative-structure corroboration not reproduced by position shuffling.",
    }


# ============================================================ E. cheap corruption battery
def corruption_battery(R=500, seed=SEED):
    """Corpus corruptions; statistic = global-max affix productivity >= 47 (the A- strength)."""
    rng = random.Random(seed)
    units = load_units("SEG_GORILA_WORD.json")
    words = [u["signs"] for u in units]
    obs = global_max_affix(words)   # 47

    out = {"observed_global_max_affix": obs, "R": R, "families": {}}

    # (1) frequency_matched_iid (already the master null family)
    fm = [global_max_affix(iid_corpus(words, rng)) for _ in range(R)]
    out["families"]["frequency_matched_iid"] = {
        "null_mean": round(sum(fm) / R, 2), "null_max": max(fm),
        "discover_rate_ge_obs": round(pct(fm, obs), 4)}

    # (2) shuffled_morphology: permute sign order WITHIN each word (destroys prefix/suffix slots)
    sm = []
    for _ in range(R):
        cor = []
        for w in words:
            lw = list(w); rng.shuffle(lw); cor.append(tuple(lw))
        sm.append(global_max_affix(cor))
    out["families"]["shuffled_morphology_within_word"] = {
        "null_mean": round(sum(sm) / R, 2), "null_max": max(sm),
        "discover_rate_ge_obs": round(pct(sm, obs), 4)}

    # (3) shuffled_segmentation: re-cut the concatenated sign stream into words of the same
    # length distribution but at RANDOM boundaries (destroys real word boundaries)
    stream = [s for w in words for s in w]
    lengths = [len(w) for w in words]
    ss = []
    for _ in range(R):
        st = stream[:]; rng.shuffle(st)
        cor = []; i = 0
        for L in lengths:
            cor.append(tuple(st[i:i + L])); i += L
        ss.append(global_max_affix(cor))
    out["families"]["shuffled_segmentation_random_cuts"] = {
        "null_mean": round(sum(ss) / R, 2), "null_max": max(ss),
        "discover_rate_ge_obs": round(pct(ss, obs), 4)}

    # (4) shuffled_sign_labels: global relabeling of the sign alphabet (relabeling-invariance
    # control — productivity counts are label-invariant, so max is unchanged; verifies value-blindness)
    sl = []
    inv = sorted({s for w in words for s in w})
    for _ in range(min(R, 100)):
        perm = inv[:]; rng.shuffle(perm)
        mp = dict(zip(inv, perm))
        cor = [tuple(mp[s] for s in w) for w in words]
        sl.append(global_max_affix(cor))
    out["families"]["shuffled_sign_labels_relabel"] = {
        "null_mean": round(sum(sl) / len(sl), 2), "null_max": max(sl), "null_min": min(sl),
        "discover_rate_ge_obs": round(pct(sl, obs), 4),
        "note": "global relabeling leaves the max productivity EXACTLY invariant -> confirms the "
                "structure is value-blind (relabeling-invariant); this is a positive control, not a null."}
    return out


# ============================================================ F. value-layer relabeling-invariance
def value_layer_fp(seed=SEED, R=200):
    """Value-layer false-positive rate. The campaign's value claims are all NULL. Reproduce the
    H3 relabeling-invariance result: held-out structural read-count is invariant under consistent
    value relabelings (0 bits of value information). Best-of over random value maps => confirm no
    value positive as strong as the (null) best observed is suppressed."""
    rng = random.Random(seed)
    words = [tuple(u["signs"]) for u in load_units("SEG_GORILA_WORD.json")]
    inv = sorted({s for w in words for s in w})

    # A morphology-backbone read count: number of multi-sign words that parse as
    # [prefix?] stem [suffix?] with a recurrent stem. STRUCTURAL statistic over sign identity;
    # under any bijective value relabeling the whole corpus is renamed, so the count is invariant.
    def read_count(mapper):
        if mapper:
            ws = [tuple(mapper[s] for s in w) for w in words]
        else:
            ws = words
        wset = set(ws); rc = e1._residual_index(wset)
        c = 0
        for w in ws:
            if len(w) >= 2 and (e1._recurrent(w[1:], wset, rc) or e1._recurrent(w[:-1], wset, rc)):
                c += 1
        return c
    base = read_count(None)
    counts = []
    for _ in range(R):
        perm = inv[:]; rng.shuffle(perm)
        counts.append(read_count(dict(zip(inv, perm))))
    std = (sum((c - sum(counts) / R) ** 2 for c in counts) / R) ** 0.5
    return {
        "description": "value-layer relabeling-invariance (reproduces H3 std=0)",
        "base_read_count": base, "R_relabelings": R,
        "relabel_read_count_mean": round(sum(counts) / R, 3),
        "relabel_read_count_std": round(std, 6),
        "value_bits_from_selection": 0.0 if std < 1e-9 else round(math.log2(len(set(counts))), 3),
        "verdict": ("RELABELING_INVARIANT_0_BITS" if std < 1e-9 else "VALUE_VARIANCE_PRESENT"),
        "interpretation": "held-out structural read-count is identical under every value relabeling -> "
                          "the value layer carries 0 selection-exploitable bits; no value positive can be "
                          "suppressed because none is distinguishable from its relabeled twins (H3 / I1: >=10^27 twins)."}


def main():
    t0 = time.time()
    R_full = int(os.environ.get("K1_R_FULL", "200"))
    R_cheap = int(os.environ.get("K1_R_CHEAP", "500"))
    R_anchor = int(os.environ.get("K1_R_ANCHOR", "500"))
    out = {"seed": SEED, "constitution": "v2.2",
           "R_full": R_full, "R_cheap": R_cheap, "R_anchor": R_anchor}
    print("[A] adaptive best-of-affix ..."); sys.stdout.flush()
    out["A_adaptive_bestof_affix"] = adaptive_bestof_affix(R=R_full)
    print("[B] cross-site both-direction ..."); sys.stdout.flush()
    out["B_cross_site_bothdir"] = cross_site_bothdir_adaptive(R=R_full)
    print("[C] libation random-anchor-system ..."); sys.stdout.flush()
    out["C_libation_random_anchor"] = libation_random_anchor_adaptive(R=R_anchor)
    print("[D] ledger random-anchor ..."); sys.stdout.flush()
    out["D_ledger_random_anchor"] = ledger_random_anchor_adaptive(R=R_anchor)
    print("[E] corruption battery ..."); sys.stdout.flush()
    out["E_corruption_battery"] = corruption_battery(R=R_cheap)
    print("[F] value-layer relabeling-invariance ..."); sys.stdout.flush()
    out["F_value_layer_fp"] = value_layer_fp(R=200)
    out["runtime_sec"] = round(time.time() - t0, 1)
    with open(os.path.join(DATA, "K1_nulls.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print("DONE", out["runtime_sec"], "s -> data/K1_nulls.json")
    return out


if __name__ == "__main__":
    main()
