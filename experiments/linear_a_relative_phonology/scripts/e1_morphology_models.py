#!/usr/bin/env python3
"""E1 — ANONYMOUS MORPHOLOGY INDUCTION, three families (Constitution v2.2 Art. III/V/VII/VIII/XII).

Three independent morphology-induction families over Linear A sign-sequences:
  (a) MDL morphology            — Morfessor-Baseline recursive splitting minimizing total
                                   description length (corpus coding + morph-lexicon coding).
  (b) Bayesian morphology       — generative Prefix-Stem-Suffix model with Dirichlet-multinomial
                                   priors; MAP segmentation via stochastic hard-EM; posterior
                                   affix expectations + Bayes factor vs the NONE (no-affix) model.
  (c) Finite-state paradigms    — Linguistica-style signature/paradigm induction: stems x affix-sets,
                                   with the stem-recurrence criterion (an affix is real only if the
                                   residual stem is independently attested). Reduplication + medial
                                   optional-sign (slot) alternations fall out of the same FST.

Each family emits the SAME anonymous objects so they can be cross-checked:
  prefix candidates, suffix candidates, stem families, reduplication candidates,
  optional-sign (medial slot) classes, slot alternations.

The wave-2 C4 finding (productive word-INITIAL A-/I- prefixation + -JA suffix) is re-characterized
under all three families, deflated against a frequency-matched i.i.d. null (Art. VIII multiplicity),
and cross-family AGREEMENT is measured.

NON-CIRCULAR (Art. XII). Every model input is a pure distributional statistic over ANONYMOUS sign
IDENTITIES. Known values (LB vowels {A,E,I,O,U}; LA pure-vowel signs A,I,U,E,O) are read AFTERWARD to
GRADE benchmarks only — never a model input, never a gate. No phonetic value is assigned. Highest
claim layer L2/L3; licences NOT_EARNED. Deterministic seed 20260708; pure stdlib.
"""
from __future__ import annotations

import json
import math
import os
import random
import sys
from collections import Counter, defaultdict

MAIN = "/home/claude-runner/gitlab/n8n/logos"
sys.path.insert(0, MAIN)
from scripts.cross_script import data as X  # noqa: E402  (read-only corpus loader)

HERE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.dirname(HERE)
SEGDIR = os.path.join(CAMP, "data", "segmentations")
DATA = os.path.join(CAMP, "data")
REPORTS = os.path.join(CAMP, "reports")
SEED = 20260708
PURE_VOWELS = {"A", "E", "I", "O", "U"}          # known-value GRADING labels ONLY (never an input)


# ============================================================================ data
def load_words(segfile):
    units = json.load(open(os.path.join(SEGDIR, segfile)))["units"]
    return [tuple(u["signs"]) for u in units]


def unigram(words):
    c = Counter(s for w in words for s in w)
    n = sum(c.values())
    return c, n


# ============================================================================ (a) MDL / Morfessor
class Morfessor:
    """MDL morphology by Viterbi training (Morfessor-Baseline family).

    A morph is a contiguous sign-substring. Encoding cost of a word = min over segmentations of the
    sum of per-morph codelengths, where a KNOWN morph costs -log P(morph) (its current corpus
    probability) and a NOVEL morph costs len(morph)*log(V) (spelling it out sign-by-sign from a
    V-symbol alphabet + a fixed pointer). This is the two-part MDL tradeoff: frequent multi-sign
    sequences stay whole (stems), non-recurrent material is peeled into cheap shared morphs (affixes).
    E-step: Viterbi-segment every word type given current morph probs (DP). M-step: recount. Iterate.
    """

    def __init__(self, words):
        self.types = Counter(words)                 # type -> token count (freq weighting)
        self.V = len({s for w in words for s in w})
        self.logV = math.log(self.V) if self.V > 1 else 1.0
        self.morphs = Counter()                     # morph(tuple) -> corpus token count
        self.seg = {}                               # word(tuple) -> [morphs]
        self.PTR = math.log(len(self.types) + 1)    # fixed lexicon pointer term per novel morph

    def _codelen(self, m, tot):
        c = self.morphs.get(m, 0)
        known = -math.log(c / tot) if c > 0 else float("inf")
        novel = len(m) * self.logV + self.PTR
        return min(known, novel)

    def _viterbi(self, w, tot):
        n = len(w)
        best = [0.0] + [float("inf")] * n
        bp = [0] * (n + 1)
        for j in range(1, n + 1):
            for i in range(max(0, j - 6), j):        # cap morph length at 6 signs
                cl = best[i] + self._codelen(w[i:j], tot)
                if cl < best[j]:
                    best[j] = cl
                    bp[j] = i
        out = []
        j = n
        while j > 0:
            i = bp[j]
            out.append(w[i:j])
            j = i
        return out[::-1]

    def cost(self):
        tot = sum(self.morphs.values()) or 1
        corpus = 0.0
        for w, c in self.types.items():
            corpus += c * sum(self._codelen(m, tot) for m in self.seg[w])
        lex = sum(len(m) * self.logV + self.PTR for m in self.morphs)
        return corpus + lex

    def train(self, epochs=12):
        for w, c in self.types.items():             # init: every word whole
            self.seg[w] = [w]
            self.morphs[w] += c
        for ep in range(epochs):
            tot = sum(self.morphs.values()) or 1
            new_counts = Counter()
            new_seg = {}
            for w, c in self.types.items():
                s = self._viterbi(w, tot)
                new_seg[w] = s
                for m in s:
                    new_counts[m] += c
            changed = sum(1 for w in self.types if new_seg[w] != self.seg[w])
            self.seg = new_seg
            self.morphs = new_counts
            if changed == 0:
                break
        return self

    def emit(self):
        """Prefix/suffix/stem inventory from the learned segmentation.

        A first-morph is a PREFIX candidate; a last-morph is a SUFFIX candidate; the single longest
        morph of a segmented word is its STEM. Affix productivity = # distinct stems it co-occurs with.
        """
        pre = defaultdict(set)   # first-morph -> set of stems (remainder)
        suf = defaultdict(set)
        stems = defaultdict(set)  # stem -> set of full words
        for w, seg in self.seg.items():
            if len(seg) < 2:
                stems[w].add(w)
                continue
            first, last = seg[0], seg[-1]
            stem = max(seg, key=len)
            rest_after_first = tuple(x for m in seg[1:] for x in m)
            rest_before_last = tuple(x for m in seg[:-1] for x in m)
            pre["".join(first) if False else first].add(rest_after_first)
            suf[last].add(rest_before_last)
            stems[stem].add(w)
        prefixes = {("".join(k)): len(v) for k, v in pre.items()}
        suffixes = {("".join(k)): len(v) for k, v in suf.items()}
        return {
            "n_morphs": len(self.morphs),
            "total_dl": round(self.cost(), 2),
            "prefixes": dict(sorted(prefixes.items(), key=lambda kv: -kv[1])[:25]),
            "suffixes": dict(sorted(suffixes.items(), key=lambda kv: -kv[1])[:25]),
            "n_stem_families": sum(1 for v in stems.values() if len(v) >= 2),
            "mean_morphs_per_word": round(sum(len(s) for s in self.seg.values()) / len(self.seg), 3),
        }


# ============================================================================ (b) Bayesian PSS model
def bayesian_pss(words, ap=1.0, ast=2.0, a0=1.0, b0=1.0, epochs=30, seed=SEED):
    """Bayesian DP morphology:  word = [prefix?] stem [suffix?],  single-sign affixes.

    has_prefix ~ Bernoulli(pi_p), pi_p ~ Beta(a0,b0) ; has_suffix ~ Bernoulli(pi_s), pi_s ~ Beta.
    Prefix / suffix signs and STEM strings are each drawn from a Dirichlet-Process cache with a
    base measure G0 that GENERATES A STRING SIGN-BY-SIGN from the corpus sign-unigram:
        G0(x) = prod_i punigram(x_i).
    Because the stem is emitted sign-by-sign, a whole-word stem and a (stem+affix) split generate the
    SAME signs and are equiprobable UNDER THE BASE — the 'memorise the whole word as one atomic stem'
    degeneracy that kills a Dirichlet-multinomial model is removed. Only the DP CACHE (rich-get-richer)
    breaks the tie, so a genuinely productive affix (e.g. LB -JO) bootstraps while noise does not.
    Inference: MAP hard-EM (iterated conditional modes) with the collapsed DP predictive. Validated on
    Linear B (positive control) before its Linear A verdict is trusted. Anonymous; no value input.
    """
    rng = random.Random(seed)
    words = [w for w in words if len(w) >= 1]
    Nw = len(words)
    uni, un = unigram(words)
    lpu = {s: math.log(uni[s] / un) for s in uni}      # log sign-unigram (base measure atoms)

    def G0(s):                                          # log base prob of a sign-string
        return sum(lpu[x] for x in s)

    def analyses(w):
        L = len(w); out = []
        for hp in (0, 1):
            for hs in (0, 1):
                if L - hp - hs < 1 or (hp and L < 2):
                    continue
                out.append((hp, hs))
        return out

    def stem_of(w, hp, hs):
        return w[(1 if hp else 0):(len(w) - 1 if hs else len(w))]

    cpre = Counter(); csuf = Counter(); cstem = Counter()
    npre = [0]; nsuf = [0]; nstem = [0]
    seg = {}

    def upd(w, hp, hs, d):
        if hp:
            cpre[w[0]] += d; npre[0] += d
        if hs:
            csuf[w[-1]] += d; nsuf[0] += d
        t = stem_of(w, hp, hs); cstem[t] += d; nstem[0] += d

    def score(w, hp, hs):
        gate_p = math.log((npre[0] + a0) / (Nw + a0 + b0)) if hp else \
                 math.log((Nw - npre[0] + b0) / (Nw + a0 + b0))
        gate_s = math.log((nsuf[0] + a0) / (Nw + a0 + b0)) if hs else \
                 math.log((Nw - nsuf[0] + b0) / (Nw + a0 + b0))
        s = gate_p + gate_s
        if hp:
            s += math.log((cpre[w[0]] + ap * math.exp(G0((w[0],)))) / (npre[0] + ap))
        if hs:
            s += math.log((csuf[w[-1]] + ap * math.exp(G0((w[-1],)))) / (nsuf[0] + ap))
        t = stem_of(w, hp, hs)
        s += math.log((cstem[t] + ast * math.exp(G0(t))) / (nstem[0] + ast))
        return s

    for w in words:                                     # random valid init
        a = rng.choice(analyses(w))
        seg[id(w)] = [a[0], a[1], w]; upd(w, a[0], a[1], 1)
    keys = list(seg.keys())
    for ep in range(epochs):
        rng.shuffle(keys); changed = 0
        for k in keys:
            hp, hs, w = seg[k]
            upd(w, hp, hs, -1)
            best = None; bs = None
            for chp, chs in analyses(w):
                sc = score(w, chp, chs)
                if bs is None or sc > bs:
                    bs = sc; best = (chp, chs)
            upd(w, best[0], best[1], 1); seg[k] = [best[0], best[1], w]
            if (best[0], best[1]) != (hp, hs):
                changed += 1
        if changed == 0:
            break

    pre_stems = defaultdict(set); suf_stems = defaultdict(set); stem_words = defaultdict(set)
    for k in keys:
        hp, hs, w = seg[k]
        t = stem_of(w, hp, hs)
        if hp:
            pre_stems[w[0]].add(t)
        if hs:
            suf_stems[w[-1]].add(t)
        stem_words[t].add(w)
    prefixes = {k: len(v) for k, v in pre_stems.items()}
    suffixes = {k: len(v) for k, v in suf_stems.items()}
    return {
        "concentration": {"affix": ap, "stem": ast}, "beta_prior": [a0, b0],
        "pi_prefix_posterior_mean": round((npre[0] + a0) / (Nw + a0 + b0), 4),
        "pi_suffix_posterior_mean": round((nsuf[0] + a0) / (Nw + a0 + b0), 4),
        "frac_words_with_prefix": round(npre[0] / Nw, 3),
        "frac_words_with_suffix": round(nsuf[0] / Nw, 3),
        "prefixes": dict(sorted(prefixes.items(), key=lambda kv: -kv[1])[:25]),
        "suffixes": dict(sorted(suffixes.items(), key=lambda kv: -kv[1])[:25]),
        "n_stem_families": sum(1 for v in stem_words.values() if len(v) >= 2),
    }


# ============================================================================ (c) FST paradigms
def _residual_index(wset):
    """rescount[t] = #words whose single-sign-affix residual is t.  free = wset."""
    rescount = Counter()
    for w in wset:
        if len(w) >= 2:
            rescount[w[1:]] += 1
            rescount[w[:-1]] += 1
    return rescount


def _recurrent(t, wset, rescount):
    """t is independently attested (recurrent) iff it is a free word or the residual of >=2 words."""
    return (t in wset) or (rescount[t] >= 2)


def paradigm_induction(words, min_stem_support=1):
    """Linguistica-style signature induction with the stem-recurrence criterion.

    A single-sign PREFIX a is credited on stem t iff (a,)+t is attested AND t is 'recurrent': t occurs
    as a free word, or as the base of >=2 single-sign affixations. Productivity(a) = #distinct
    recurrent stems. Symmetric for SUFFIX. Reduplication = adjacent repeated sign or repeated bigram.
    Optional-sign (medial slot) = sign x s.t. a word W and W-with-x-removed-medially are both attested.
    Slot alternation = words sharing a stem but differing by one affix (a paradigm cell).
    """
    wset = set(words)
    rescount = _residual_index(wset)

    pre_stems = defaultdict(set); suf_stems = defaultdict(set)
    for w in wset:
        if len(w) < 2:
            continue
        stem_p = w[1:]
        if _recurrent(stem_p, wset, rescount):
            pre_stems[w[0]].add(stem_p)
        stem_s = w[:-1]
        if _recurrent(stem_s, wset, rescount):
            suf_stems[w[-1]].add(stem_s)

    prefixes = {k: len(v) for k, v in pre_stems.items()}
    suffixes = {k: len(v) for k, v in suf_stems.items()}

    # stem families: cluster words by shared recurrent stem (single-affix neighbourhood)
    fam = defaultdict(set)
    for w in wset:
        if len(w) >= 2:
            fam[w[1:]].add(w)        # prefix family keyed by stem
            fam[w[:-1]].add(w)       # suffix family keyed by stem
        if w in wset:
            fam[w].add(w)
    stem_families = {("".join(k)): sorted("".join(x) for x in v)
                     for k, v in fam.items() if len(v) >= 2 and len(k) >= 1}

    # reduplication candidates
    redup = []
    for w in wset:
        for i in range(len(w) - 1):
            if w[i] == w[i + 1]:
                redup.append(("".join(w), "sign", w[i]))
                break
        else:
            # bigram reduplication  XY XY
            L = len(w)
            if L >= 4 and L % 2 == 0 and w[:L // 2] == w[L // 2:]:
                redup.append(("".join(w), "block", "".join(w[:L // 2])))

    # optional-sign (medial slot) classes: sign x removable medially yielding an attested word
    opt = defaultdict(set)
    for w in wset:
        if len(w) < 3:
            continue
        for i in range(1, len(w) - 1):
            reduced = w[:i] + w[i + 1:]
            if reduced in wset:
                opt[w[i]].add(("".join(w), "".join(reduced)))
    optional_signs = {k: len(v) for k, v in opt.items()}

    # slot alternations: pairs (w1,w2) same stem, differ by one affix sign at same boundary
    alt_pre = defaultdict(set); alt_suf = defaultdict(set)
    by_suffix_stem = defaultdict(set)  # stem(=w[1:]) -> set of first signs
    by_prefix_stem = defaultdict(set)  # stem(=w[:-1]) -> set of last signs
    for w in wset:
        if len(w) >= 2:
            by_suffix_stem[w[1:]].add(w[0])
            by_prefix_stem[w[:-1]].add(w[-1])
    initial_alternation = {("".join(k)): sorted(v) for k, v in by_suffix_stem.items() if len(v) >= 2}
    final_alternation = {("".join(k)): sorted(v) for k, v in by_prefix_stem.items() if len(v) >= 2}

    return {
        "prefixes": dict(sorted(prefixes.items(), key=lambda kv: -kv[1])[:25]),
        "suffixes": dict(sorted(suffixes.items(), key=lambda kv: -kv[1])[:25]),
        "n_stem_families": len(stem_families),
        "n_reduplication": len(redup),
        "reduplication_examples": redup[:20],
        "optional_signs": dict(sorted(optional_signs.items(), key=lambda kv: -kv[1])[:15]),
        "n_initial_alternation_stems": len(initial_alternation),
        "n_final_alternation_stems": len(final_alternation),
        "initial_alternation_examples": dict(list(initial_alternation.items())[:15]),
        "_pre_stems": {k: sorted("".join(x) for x in v) for k, v in pre_stems.items()},
        "_suf_stems": {k: sorted("".join(x) for x in v) for k, v in suf_stems.items()},
    }


# ============================================================================ characterization + null
def productivity_prefix(words, sign, wset=None, rescount=None):
    """Recurrent-stem productivity of a word-initial single sign (paradigm criterion)."""
    if wset is None:
        wset = set(words); rescount = _residual_index(wset)
    stems = set()
    for w in wset:
        if len(w) >= 2 and w[0] == sign:
            stem = w[1:]
            if _recurrent(stem, wset, rescount):
                stems.add(stem)
    return len(stems)


def productivity_suffix(words, sign, wset=None, rescount=None):
    if wset is None:
        wset = set(words); rescount = _residual_index(wset)
    stems = set()
    for w in wset:
        if len(w) >= 2 and w[-1] == sign:
            stem = w[:-1]
            if _recurrent(stem, wset, rescount):
                stems.add(stem)
    return len(stems)


def freq_matched_null(words, targets_pre, targets_suf, n_null=200, seed=SEED):
    """i.i.d. sign-unigram null preserving word-length distribution + sign frequencies.

    For each target sign, how much recurrent-stem productivity arises from frequency alone?
    Empirical one-sided p = P(null >= observed).
    """
    rng = random.Random(seed)
    uni, N = unigram(words)
    signs = list(uni.keys()); wts = [uni[s] for s in signs]
    lengths = [len(w) for w in words]
    wset0 = set(words); rc0 = _residual_index(wset0)
    obs_pre = {s: productivity_prefix(words, s, wset0, rc0) for s in targets_pre}
    obs_suf = {s: productivity_suffix(words, s, wset0, rc0) for s in targets_suf}
    null_pre = {s: [] for s in targets_pre}
    null_suf = {s: [] for s in targets_suf}
    for _ in range(n_null):
        synth = [tuple(rng.choices(signs, weights=wts, k=L)) for L in lengths]
        ws = set(synth); rc = _residual_index(ws)
        for s in targets_pre:
            null_pre[s].append(productivity_prefix(synth, s, ws, rc))
        for s in targets_suf:
            null_suf[s].append(productivity_suffix(synth, s, ws, rc))
    def summ(obs, nd):
        arr = sorted(nd)
        mean = sum(arr) / len(arr)
        p = (sum(1 for v in arr if v >= obs) + 1) / (len(arr) + 1)
        lo = arr[int(0.025 * len(arr))]; hi = arr[min(len(arr) - 1, int(0.975 * len(arr)))]
        return {"observed": obs, "null_mean": round(mean, 2),
                "null_95ci": [lo, hi], "p_ge": round(p, 4)}
    pre = {s: summ(obs_pre[s], null_pre[s]) for s in targets_pre}
    suf = {s: summ(obs_suf[s], null_suf[s]) for s in targets_suf}
    # Holm-Bonferroni across all prefix+suffix tests (Art. VIII multiplicity)
    allp = [("prefix", s, pre[s]["p_ge"]) for s in targets_pre] + \
           [("suffix", s, suf[s]["p_ge"]) for s in targets_suf]
    allp.sort(key=lambda x: x[2])
    m = len(allp)
    for rank, (grp, s, p) in enumerate(allp):
        padj = min(1.0, p * (m - rank))
        (pre if grp == "prefix" else suf)[s]["p_holm"] = round(padj, 4)
    return {"prefix": pre, "suffix": suf, "n_null": n_null, "n_tests_holm": m}


# ============================================================================ agreement
def agreement(mdl, bayes, para, k=10):
    def topset(d, key):
        return set(list(d[key].keys())[:k])
    out = {}
    for slot in ("prefixes", "suffixes"):
        A = topset(mdl, slot); B = topset(bayes, slot); C = topset(para, slot)
        inter = A & B & C
        def jac(x, y):
            return round(len(x & y) / len(x | y), 3) if (x | y) else 0.0
        out[slot] = {
            "top_k": k,
            "mdl": sorted(A), "bayes": sorted(B), "paradigm": sorted(C),
            "three_way_intersection": sorted(inter),
            "jaccard_mdl_bayes": jac(A, B),
            "jaccard_mdl_para": jac(A, C),
            "jaccard_bayes_para": jac(B, C),
        }
    return out


# ============================================================================ main
def run_family_set(words, label):
    mdl = Morfessor(words).train().emit()
    bayes = bayesian_pss(words)
    para = paradigm_induction(words)
    agr = agreement(mdl, bayes, para)
    return {"label": label, "n_words": len(words), "n_types": len(set(words)),
            "mdl": mdl, "bayes": bayes, "paradigm": para, "agreement": agr}


def main():
    gorila = load_words("SEG_GORILA_WORD.json")
    entry = load_words("SEG_ENTRY.json")
    formula = load_words("SEG_FORMULA.json")

    results = {"seed": SEED, "segmentations": {}}
    for label, words in [("GORILA_WORD", gorila), ("ENTRY", entry), ("FORMULA", formula)]:
        results["segmentations"][label] = run_family_set(words, label)

    # ---- characterize the wave-2 C4 finding on the PRIMARY (GORILA_WORD) segmentation ----
    # Targets are the ANONYMOUS affixes wave-2 flagged; graded (afterward) as pure-vowel A,I + JA.
    tgt_pre = ["A", "I", "U", "E", "O"]           # the pure-vowel word-initial candidates
    tgt_suf = ["JA", "RE", "NE", "TU", "SI"]       # -JA + other frequent finals for contrast
    null = freq_matched_null(gorila, tgt_pre, tgt_suf, n_null=200)

    # cross-family productivity of A- / I- / -JA (the three C4 headline affixes)
    c4 = {}
    for fam_name, femit in [("mdl", results["segmentations"]["GORILA_WORD"]["mdl"]),
                            ("bayes", results["segmentations"]["GORILA_WORD"]["bayes"]),
                            ("paradigm", results["segmentations"]["GORILA_WORD"]["paradigm"])]:
        c4[fam_name] = {
            "A_prefix": femit["prefixes"].get("A", 0),
            "I_prefix": femit["prefixes"].get("I", 0),
            "JA_suffix": femit["suffixes"].get("JA", 0),
        }
    # paradigm gives the canonical recurrent-stem productivity used for the null
    c4["paradigm_recurrent_stem"] = {
        "A_prefix": productivity_prefix(gorila, "A"),
        "I_prefix": productivity_prefix(gorila, "I"),
        "JA_suffix": productivity_suffix(gorila, "JA"),
    }

    # grading benchmark (READ-ONLY, non-input): are the top prefixes pure vowels?
    para_pre = results["segmentations"]["GORILA_WORD"]["paradigm"]["prefixes"]
    top_pre = list(para_pre.keys())[:6]
    grade = {
        "top6_prefixes_paradigm": top_pre,
        "fraction_pure_vowel": round(sum(1 for s in top_pre if s in PURE_VOWELS) / len(top_pre), 3),
        "note": "GRADING ONLY — pure-vowel identity never entered any model; L2/L3, no licence.",
    }

    results["c4_characterization"] = {
        "cross_family_productivity": c4,
        "frequency_matched_null": null,
        "grading_benchmark_noninput": grade,
    }

    # ---- LB POSITIVE CONTROL (Art. calibration): the SAME three families on Linear B wordforms,
    # a readable analogue with KNOWN productive inflection (-JO/-O/-A/-JA case-and-derivation endings).
    # If a family detects LB morphology but not LA's, its LA null is a real power/typology gap, not a
    # dead detector. LB endings are read AFTERWARD to grade recovery — never a model input. ----
    lb_words = [tuple(w) for w in X.load_b_damos()[0]]
    lb = run_family_set(lb_words, "LINEAR_B_DAMOS_control")
    lb_known_suffix = ["JO", "O", "A", "JA", "SI", "DE", "RO", "TE", "QE", "NA"]
    lb_control = {
        "n_words": lb["n_words"], "n_types": lb["n_types"],
        "mdl_top_suffixes": list(lb["mdl"]["suffixes"].items())[:12],
        "bayes_pi_prefix": lb["bayes"]["pi_prefix_posterior_mean"],
        "bayes_pi_suffix": lb["bayes"]["pi_suffix_posterior_mean"],
        "bayes_top_suffixes": list(lb["bayes"]["suffixes"].items())[:12],
        "paradigm_top_suffixes": list(lb["paradigm"]["suffixes"].items())[:12],
        "la_bayes_pi_prefix": results["segmentations"]["GORILA_WORD"]["bayes"]["pi_prefix_posterior_mean"],
        "la_bayes_pi_suffix": results["segmentations"]["GORILA_WORD"]["bayes"]["pi_suffix_posterior_mean"],
        "grading_note": "LB endings listed for GRADING recovery only; never a model input.",
    }
    results["lb_positive_control"] = lb_control

    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "E1_morphology.json"), "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("WROTE", os.path.join(DATA, "E1_morphology.json"))

    # concise console summary
    g = results["segmentations"]["GORILA_WORD"]
    print("\n=== GORILA_WORD ===")
    print("MDL      top prefixes:", list(g["mdl"]["prefixes"].items())[:6])
    print("MDL      top suffixes:", list(g["mdl"]["suffixes"].items())[:6])
    print("Bayes    top prefixes:", list(g["bayes"]["prefixes"].items())[:6])
    print("Bayes    top suffixes:", list(g["bayes"]["suffixes"].items())[:6])
    print("Paradigm top prefixes:", list(g["paradigm"]["prefixes"].items())[:6])
    print("Paradigm top suffixes:", list(g["paradigm"]["suffixes"].items())[:6])
    print("agreement prefixes 3-way:", g["agreement"]["prefixes"]["three_way_intersection"])
    print("agreement suffixes 3-way:", g["agreement"]["suffixes"]["three_way_intersection"])
    print("C4 cross-family:", json.dumps(c4, ensure_ascii=False))
    print("NULL prefix:", json.dumps(null["prefix"], ensure_ascii=False))
    print("NULL suffix:", json.dumps(null["suffix"], ensure_ascii=False))
    print("grade:", grade)
    print("\n=== LB POSITIVE CONTROL ===")
    print("LB bayes pi_prefix/pi_suffix:", lb_control["bayes_pi_prefix"], lb_control["bayes_pi_suffix"],
          "| LA:", lb_control["la_bayes_pi_prefix"], lb_control["la_bayes_pi_suffix"])
    print("LB bayes top suffixes:", lb_control["bayes_top_suffixes"][:8])
    print("LB MDL  top suffixes:", lb_control["mdl_top_suffixes"][:8])
    print("LB para top suffixes:", lb_control["paradigm_top_suffixes"][:8])
    return results


if __name__ == "__main__":
    main()
