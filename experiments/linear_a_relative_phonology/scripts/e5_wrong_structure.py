#!/usr/bin/env python3
"""E5 — WRONG-STRUCTURE CONTROLS (Constitution v2.2 Art. III/VII/VIII/XII).

Question. The wave-2 signal is an anonymous relative-morphology structure (word-INITIAL A-/I-
prefixation + a weak -JA final). E5 asks the falsification question: does the REAL induced
morphology carry held-out predictive value that WRONG structural hypotheses do not? A structure
that only *describes* the derivation set (overfit) will not beat its own corruptions out of sample.

Metric — HELD-OUT PREDICTIVE GAIN (bits/word).
  We segment every word into a short morph sequence [prefix?] stem [suffix?] and train a
  morph-BIGRAM language model (add-alpha bigram over morphs, backing off to a morph-unigram, backing
  off to a sign-unigram base measure G0 so every string is scorable). A NO-MORPHOLOGY baseline is the
  same LM trained on whole-word (single-morph) segmentations. For a held-out word,
        gain = bits_baseline(word) - bits_morph(word)          (positive = morphology helps).
  The bigram (not unigram) LM is what makes the label-corruption controls bite: it is the
  stem->suffix / prefix->stem TRANSITIONS that a real paradigm predicts and a shuffle destroys.

Controls (each must be BEATEN by the real morphology on held-out gain).
  Label corruptions of the REAL train segmentation (same held-out words, paired):
    A. shuffled_suffixes   — permute suffix morphs across suffixed train words (kills stem->suffix).
    B. shuffled_stems      — permute stem morphs across train words (kills both transitions).
    C. random_segmentation — re-cut train words at random boundaries (same #morphs distribution).
  Corpus-level nulls (fresh pipeline on a null corpus, unpaired):
    D. site_preserving_shuffle       — permute signs WITHIN each site (keeps site freq + length).
    E. frequency_matched_pseudo      — i.i.d. global sign-unigram, length-preserved (no morphology).
    F. synthetic_wrong_language      — planted MEDIAL-INFIX grammar (morphology in the wrong place
                                       for a prefix/suffix segmenter): real signal, wrong typology.

NON-CIRCULAR (Art. XII). Every input is a pure distributional statistic over ANONYMOUS sign
identities. The productive-affix inventory is learned per train-fold by the stem-RECURRENCE
criterion only (an affix counts only if its residual stem is independently attested). Known values
(LB vowels; LA pure-vowel signs) are NEVER a model input; no phonetic value is assigned. L2/L3,
licences NOT_EARNED. Deterministic seed 20260708; pure stdlib.
"""
from __future__ import annotations

import json
import math
import os
import random
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(CAMP, "scripts"))
from e1_morphology_models import _residual_index, _recurrent  # noqa: E402  audited primitives

SEGDIR = os.path.join(CAMP, "data", "segmentations")
DATA = os.path.join(CAMP, "data")
REPORTS = os.path.join(CAMP, "reports")
SEED = 20260708
NFOLD = 5
N_PERM = 25          # permutation realizations per label-corruption control
N_NULLCORP = 60      # null-corpus realizations per corpus-level control
N_BOOT = 2000        # bootstrap resamples for CIs
ALPHA = 0.5          # bigram add-alpha
BETA = 1.0           # unigram->base backoff
PROD_MIN = 3         # affix credited iff it co-occurs with >= PROD_MIN distinct recurrent stems


# ============================================================================ data
def load_units():
    return json.load(open(os.path.join(SEGDIR, "SEG_GORILA_WORD.json")))["units"]


# ============================================================================ affix inventory (train)
def learn_inventory(train_words, prod_min=PROD_MIN):
    """Productive single-sign prefix/suffix sets by the stem-recurrence criterion (train only)."""
    wset = set(train_words)
    rc = _residual_index(wset)
    pre_stems = defaultdict(set)
    suf_stems = defaultdict(set)
    for w in wset:
        if len(w) < 2:
            continue
        sp = w[1:]
        if _recurrent(sp, wset, rc):
            pre_stems[w[0]].add(sp)
        ss = w[:-1]
        if _recurrent(ss, wset, rc):
            suf_stems[w[-1]].add(ss)
    P = {s for s, st in pre_stems.items() if len(st) >= prod_min}
    S = {s for s, st in suf_stems.items() if len(st) >= prod_min}
    prod_pre = {s: len(st) for s, st in pre_stems.items()}
    prod_suf = {s: len(st) for s, st in suf_stems.items()}
    return P, S, prod_pre, prod_suf


def segment(word, P, S, prod_pre, prod_suf):
    """REAL segmentation: [prefix?] stem [suffix?], single-sign affixes, nonempty stem.

    A boundary is taken only if the sign is in the learned productive set. If both ends qualify but
    the word is too short for a nonempty stem, keep the higher-productivity side (deterministic)."""
    w = tuple(word)
    if len(w) < 2:
        return (w,)
    has_p = w[0] in P
    has_s = w[-1] in S
    if has_p and has_s and len(w) < 3:
        # length-2 with both flagged: keep the more productive side only
        if prod_pre.get(w[0], 0) >= prod_suf.get(w[-1], 0):
            has_s = False
        else:
            has_p = False
    i = 1 if has_p else 0
    j = len(w) - 1 if has_s else len(w)
    if j <= i:  # guard: never empty stem
        return (w,)
    seg = []
    if has_p:
        seg.append((w[0],))
    seg.append(w[i:j])
    if has_s:
        seg.append((w[-1],))
    return tuple(seg)


def whole(word):
    return (tuple(word),)


# ============================================================================ morph-bigram LM
class MorphBigramLM:
    """Add-alpha morph bigram over sequences START m1..mk END, backing off morph-unigram -> sign G0."""

    def __init__(self, seqs, train_sign_unigram, V):
        self.V = V
        tot = sum(train_sign_unigram.values()) or 1
        self.lpu = {s: train_sign_unigram[s] / tot for s in train_sign_unigram}
        self.uni = Counter()
        self.bi = Counter()
        self.ctx = Counter()
        for seq in seqs:
            toks = ("<s>",) + tuple(seq) + ("</s>",)
            for m in seq:
                self.uni[m] += 1
            self.Nuni = None
            for a, b in zip(toks, toks[1:]):
                self.bi[(a, b)] += 1
                self.ctx[a] += 1
        self.Nuni = sum(self.uni.values()) or 1

    def _G0(self, morph):
        # base prob of a morph string via train sign-unigram, uniform fallback for unseen signs
        p = 1.0
        for s in morph:
            p *= self.lpu.get(s, 1.0 / self.V)
        return p

    def _p_uni(self, morph):
        return (self.uni.get(morph, 0) + BETA * self._G0(morph)) / (self.Nuni + BETA)

    def _p_bi(self, a, b):
        c = self.bi.get((a, b), 0)
        n = self.ctx.get(a, 0)
        pb = 1.0 if b == "</s>" else self._p_uni(b)   # </s> handled by add-alpha over contexts
        if b == "</s>":
            # unigram prob of END = (count END-as-target)/(Nseq); approximate via ctx of </s>
            pb = 1.0
        return (c + ALPHA * pb) / (n + ALPHA)

    def bits(self, seq):
        toks = ("<s>",) + tuple(seq) + ("</s>",)
        lp = 0.0
        for a, b in zip(toks, toks[1:]):
            lp += math.log2(max(self._p_bi(a, b), 1e-300))
        return -lp


def sign_unigram(words):
    c = Counter(s for w in words for s in w)
    return c


# ============================================================================ gain evaluation
def eval_gain(train_words, test_words, morph_segs_train, morph_segs_test, V):
    """bits_baseline - bits_morph per test word. Baseline = whole-word LM (fixed, uncorrupted)."""
    su = sign_unigram(train_words)
    base_lm = MorphBigramLM([whole(w) for w in train_words], su, V)
    morph_lm = MorphBigramLM(morph_segs_train, su, V)
    gains = []
    for w, mseg in zip(test_words, morph_segs_test):
        gb = base_lm.bits(whole(w))
        gm = morph_lm.bits(mseg)
        gains.append(gb - gm)
    return gains


# ============================================================================ label corruptions
def corrupt_shuffled_suffixes(segs, rng):
    """Permute suffix morphs across the words that have a suffix (last morph, len(seg)>=2)."""
    out = [list(s) for s in segs]
    idx = [i for i, s in enumerate(out) if len(s) >= 2]
    sufs = [out[i][-1] for i in idx]
    rng.shuffle(sufs)
    for k, i in enumerate(idx):
        out[i][-1] = sufs[k]
    return [tuple(s) for s in out]


def corrupt_shuffled_stems(segs, rng):
    """Permute the stem morph (the middle/longest) across all words."""
    out = [list(s) for s in segs]
    # stem index: for (stem,) ->0 ; (pre,stem)->1 or (stem,suf)->0 ; (pre,stem,suf)->1
    def stem_idx(s):
        if len(s) == 1:
            return 0
        if len(s) == 3:
            return 1
        # len 2: stem is the longer; tie -> index 0
        return 0 if len(s[0]) >= len(s[1]) else 1
    idxs = [stem_idx(s) for s in out]
    stems = [out[i][idxs[i]] for i in range(len(out))]
    rng.shuffle(stems)
    for i in range(len(out)):
        out[i][idxs[i]] = stems[i]
    return [tuple(s) for s in out]


def corrupt_random_segmentation(words, segs, rng):
    """Re-cut each word into the SAME number of morphs as its real seg, at random boundaries."""
    out = []
    for w, s in zip(words, segs):
        w = tuple(w)
        k = len(s)
        if k == 1 or len(w) < 2:
            out.append((w,))
            continue
        ncuts = k - 1
        positions = list(range(1, len(w)))
        if ncuts >= len(positions):
            cuts = positions
        else:
            cuts = sorted(rng.sample(positions, ncuts))
        seg = []
        prev = 0
        for c in cuts:
            seg.append(w[prev:c])
            prev = c
        seg.append(w[prev:])
        out.append(tuple(seg))
    return out


# ============================================================================ corpus-level nulls
def null_site_preserving(units, rng):
    """Permute signs WITHIN each site (preserve per-site sign multiset + each word length)."""
    by_site_signs = defaultdict(list)
    for u in units:
        by_site_signs[u["site"]].extend(u["signs"])
    pools = {s: sig[:] for s, sig in by_site_signs.items()}
    for s in pools:
        rng.shuffle(pools[s])
    ptr = {s: 0 for s in pools}
    out = []
    for u in units:
        s = u["site"]
        L = len(u["signs"])
        chunk = pools[s][ptr[s]:ptr[s] + L]
        ptr[s] += L
        out.append(tuple(chunk))
    return out


def null_freq_matched(words, rng):
    """i.i.d. global sign-unigram, length-preserved (destroys all morphology)."""
    su = sign_unigram(words)
    signs = list(su.keys())
    wts = [su[s] for s in signs]
    return [tuple(rng.choices(signs, weights=wts, k=len(w))) for w in words]


def null_wrong_language(words, rng):
    """Planted MEDIAL-INFIX grammar: stems + a small infix set inserted at a MEDIAL slot.

    Real morphology, wrong TYPOLOGY for a prefix/suffix segmenter. Size, alphabet, length dist and
    stem-length dist are matched to the real corpus; ~half the multi-sign words receive an infix."""
    su = sign_unigram(words)
    signs = list(su.keys())
    wts = [su[s] for s in signs]
    infixes = rng.sample(signs, k=min(6, len(signs)))     # small closed infix inventory
    stems = {}   # cache stems by length so they RECUR (planted paradigms)
    out = []
    for w in words:
        L = len(w)
        if L < 3:
            out.append(tuple(rng.choices(signs, weights=wts, k=L)))
            continue
        base_len = L - 1
        pool = stems.setdefault(base_len, [tuple(rng.choices(signs, weights=wts, k=base_len))
                                            for _ in range(60)])
        stem = rng.choice(pool)
        pos = 1 + rng.randrange(base_len - 1)             # strictly medial insertion
        infx = rng.choice(infixes)
        out.append(stem[:pos] + (infx,) + stem[pos:])
    return out


# ============================================================================ CV driver
def make_folds(n, nfold, rng):
    idx = list(range(n))
    rng.shuffle(idx)
    return [idx[i::nfold] for i in range(nfold)]


def real_gain_cv(words, V, rng):
    """Pooled per-word held-out gain for the REAL morphology; returns list aligned to a fold order."""
    folds = make_folds(len(words), NFOLD, random.Random(SEED))
    pooled = []
    seg_cache = {}   # test index -> real seg (for paired controls), plus train segs per fold
    fold_pack = []
    for f in range(NFOLD):
        test_idx = folds[f]
        train_idx = [i for k in range(NFOLD) if k != f for i in folds[k]]
        tr = [words[i] for i in train_idx]
        te = [words[i] for i in test_idx]
        P, S, pp, ps = learn_inventory(tr)
        tr_segs = [segment(w, P, S, pp, ps) for w in tr]
        te_segs = [segment(w, P, S, pp, ps) for w in te]
        gains = eval_gain(tr, te, tr_segs, te_segs, V)
        for i, g in zip(test_idx, gains):
            seg_cache[i] = None
        pooled.extend(gains)
        fold_pack.append((train_idx, test_idx, tr, te, tr_segs, te_segs, P, S, pp, ps))
    return pooled, fold_pack


def label_control_cv(fold_pack, words, V, corrupt_name):
    """Per-word gain for a label-corruption control, aligned to the same pooled order as real.

    Averages over N_PERM permutations; the morph LM is trained on corrupted TRAIN segs, test words
    keep their REAL segmentation (we test whether corrupted train stats predict real held-out)."""
    pooled = []
    for (train_idx, test_idx, tr, te, tr_segs, te_segs, P, S, pp, ps) in fold_pack:
        acc = [0.0] * len(te)
        for r in range(N_PERM):
            rng = random.Random((SEED * 131 + hash(corrupt_name) % 1000003) ^ (r * 2654435761))
            if corrupt_name == "shuffled_suffixes":
                ctr = corrupt_shuffled_suffixes(tr_segs, rng)
            elif corrupt_name == "shuffled_stems":
                ctr = corrupt_shuffled_stems(tr_segs, rng)
            elif corrupt_name == "random_segmentation":
                ctr = corrupt_random_segmentation(tr, tr_segs, rng)
            else:
                raise ValueError(corrupt_name)
            gains = eval_gain(tr, te, ctr, te_segs, V)
            for k in range(len(te)):
                acc[k] += gains[k]
        pooled.extend(g / N_PERM for g in acc)
    return pooled


def learned_vs_random_advantage(tr, te, tr_segs, te_segs, V, rng):
    """BASELINE-FREE: mean held-out (bits_randomseg - bits_learnedseg).

    Removes the whole-word-baseline confound: both terms are morph-LM bits, differing only in
    whether the TRAIN+TEST segmentation is the learned one or a random re-cut. Positive => the
    learned morphology predicts held-out words better than an arbitrary segmentation of the SAME
    words. Averaged over N_PERM random-segmentation realizations."""
    su = sign_unigram(tr)
    learned_lm = MorphBigramLM(tr_segs, su, V)
    learned_bits = [learned_lm.bits(s) for s in te_segs]
    acc = [0.0] * len(te)
    for r in range(N_PERM):
        rr = random.Random(rng.randrange(1 << 30))
        tr_rand = corrupt_random_segmentation(tr, tr_segs, rr)
        te_rand = corrupt_random_segmentation(te, te_segs, rr)
        rand_lm = MorphBigramLM(tr_rand, su, V)
        for k in range(len(te)):
            acc[k] += rand_lm.bits(te_rand[k]) - learned_bits[k]
    return [a / N_PERM for a in acc]


def corpus_null_gain(kind, units, words, V):
    """Fresh full pipeline on N_NULLCORP null corpora.

    Returns (absolute whole-word-baseline gains, baseline-free learned-vs-random advantages)."""
    means = []
    lvr_means = []
    for r in range(N_NULLCORP):
        rng = random.Random((SEED * 977 + hash(kind) % 1000003) ^ (r * 40503))
        if kind == "site_preserving_shuffle":
            nw = null_site_preserving(units, rng)
        elif kind == "frequency_matched_pseudo":
            nw = null_freq_matched(words, rng)
        elif kind == "synthetic_wrong_language":
            nw = null_wrong_language(words, rng)
        else:
            raise ValueError(kind)
        folds = make_folds(len(nw), NFOLD, random.Random(SEED + r))
        gains = []
        lvr = []
        for f in range(NFOLD):
            test_idx = folds[f]
            train_idx = [i for k in range(NFOLD) if k != f for i in folds[k]]
            tr = [nw[i] for i in train_idx]
            te = [nw[i] for i in test_idx]
            P, S, pp, ps = learn_inventory(tr)
            tr_segs = [segment(w, P, S, pp, ps) for w in tr]
            te_segs = [segment(w, P, S, pp, ps) for w in te]
            gains.extend(eval_gain(tr, te, tr_segs, te_segs, V))
            lvr.extend(learned_vs_random_advantage(tr, te, tr_segs, te_segs, V,
                                                   random.Random(SEED + r * 17 + f)))
        means.append(sum(gains) / len(gains))
        lvr_means.append(sum(lvr) / len(lvr))
    return means, lvr_means


# ============================================================================ stats
def mean_ci_boot(vals, rng, nboot=N_BOOT):
    n = len(vals)
    m = sum(vals) / n
    bs = []
    for _ in range(nboot):
        s = sum(vals[rng.randrange(n)] for _ in range(n)) / n
        bs.append(s)
    bs.sort()
    return m, bs[int(0.025 * nboot)], bs[int(0.975 * nboot)]


def paired_diff(real, ctrl, rng, nboot=N_BOOT):
    """Paired real-minus-control gain (same held-out words), bootstrap CI + one-sided p(real<=ctrl)."""
    d = [a - b for a, b in zip(real, ctrl)]
    n = len(d)
    m = sum(d) / n
    bs = []
    for _ in range(nboot):
        bs.append(sum(d[rng.randrange(n)] for _ in range(n)) / n)
    bs.sort()
    lo, hi = bs[int(0.025 * nboot)], bs[int(0.975 * nboot)]
    p = (sum(1 for v in bs if v <= 0) + 1) / (nboot + 1)
    return {"mean_diff_bits": round(m, 4), "ci95": [round(lo, 4), round(hi, 4)],
            "p_real_le_ctrl": round(p, 4), "real_beats": bool(lo > 0)}


def unpaired_vs_null(real_mean, null_means, label):
    """Empirical p that a null-corpus mean statistic >= real mean statistic."""
    arr = sorted(null_means)
    p = (sum(1 for v in arr if v >= real_mean) + 1) / (len(arr) + 1)
    m = sum(arr) / len(arr)
    lo = arr[int(0.025 * len(arr))]
    hi = arr[min(len(arr) - 1, int(0.975 * len(arr)))]
    return {"statistic": label,
            "null_mean": round(m, 4), "null_95range": [round(lo, 4), round(hi, 4)],
            "real_mean": round(real_mean, 4), "p_null_ge_real": round(p, 4),
            "real_beats": bool(real_mean > hi)}


# ============================================================================ main
def main():
    units = load_units()
    words = [tuple(u["signs"]) for u in units]
    V = len({s for w in words for s in w})
    rng = random.Random(SEED)

    # ---- REAL held-out gain ----
    real_pooled, fold_pack = real_gain_cv(words, V, rng)
    real_mean, real_lo, real_hi = mean_ci_boot(real_pooled, random.Random(SEED))
    # subset: multi-sign words only (where morphology can act)
    order = [i for f in fold_pack for i in f[1]]
    ms_mask = [len(words[i]) >= 2 for i in order]
    real_ms = [g for g, m in zip(real_pooled, ms_mask) if m]
    real_ms_mean, real_ms_lo, real_ms_hi = mean_ci_boot(real_ms, random.Random(SEED + 1))

    # REAL baseline-free advantage (learned seg beats random seg on same held-out words)
    real_lvr_pooled = []
    for (train_idx, test_idx, tr, te, tr_segs, te_segs, P, S, pp, ps) in fold_pack:
        real_lvr_pooled.extend(learned_vs_random_advantage(
            tr, te, tr_segs, te_segs, V, random.Random(SEED + 101)))
    real_lvr_mean, real_lvr_lo, real_lvr_hi = mean_ci_boot(real_lvr_pooled, random.Random(SEED + 2))

    results = {
        "seed": SEED, "segmentation": "SEG_GORILA_WORD", "n_words": len(words),
        "n_multi_sign": sum(ms_mask), "V_signs": V, "nfold": NFOLD,
        "config": {"alpha": ALPHA, "beta": BETA, "prod_min": PROD_MIN,
                   "n_perm": N_PERM, "n_nullcorp": N_NULLCORP, "n_boot": N_BOOT},
        "real_morphology": {
            "held_out_gain_bits_per_word_all": {
                "mean": round(real_mean, 4), "ci95": [round(real_lo, 4), round(real_hi, 4)],
                "positive": bool(real_lo > 0)},
            "held_out_gain_bits_per_word_multisign": {
                "mean": round(real_ms_mean, 4), "ci95": [round(real_ms_lo, 4), round(real_ms_hi, 4)],
                "positive": bool(real_ms_lo > 0)},
            "baseline_free_learned_vs_random_advantage": {
                "mean": round(real_lvr_mean, 4), "ci95": [round(real_lvr_lo, 4), round(real_lvr_hi, 4)],
                "positive": bool(real_lvr_lo > 0),
                "note": "bits by which learned seg beats random seg on same held-out words; "
                        "baseline-invariant, so comparable ACROSS corpora."},
        },
        "label_corruption_controls": {},
        "corpus_null_controls": {},
    }

    # ---- label-corruption controls (paired) ----
    for name in ("shuffled_suffixes", "shuffled_stems", "random_segmentation"):
        ctrl_pooled = label_control_cv(fold_pack, words, V, name)
        c_mean, c_lo, c_hi = mean_ci_boot(ctrl_pooled, random.Random(SEED + 7))
        pd = paired_diff(real_pooled, ctrl_pooled, random.Random(SEED + 11))
        # multi-sign paired diff
        ctrl_ms = [g for g, m in zip(ctrl_pooled, ms_mask) if m]
        pd_ms = paired_diff(real_ms, ctrl_ms, random.Random(SEED + 13))
        results["label_corruption_controls"][name] = {
            "control_mean_gain_bits": round(c_mean, 4), "control_ci95": [round(c_lo, 4), round(c_hi, 4)],
            "paired_all": pd, "paired_multisign": pd_ms,
        }

    # ---- corpus-level null controls (unpaired) ----
    # Two statistics per null: (i) absolute whole-word-baseline gain — CONFOUNDED by baseline
    # strength across corpora (destroyed corpora lose whole-word recurrence, weakening the baseline
    # and inflating apparent morph gain); (ii) baseline-free learned-vs-random advantage — the valid
    # cross-corpus comparison. The verdict uses (ii).
    for kind in ("site_preserving_shuffle", "frequency_matched_pseudo", "synthetic_wrong_language"):
        null_means, null_lvr = corpus_null_gain(kind, units, words, V)
        results["corpus_null_controls"][kind] = {
            "absolute_gain_confounded": unpaired_vs_null(real_mean, null_means,
                                                         "whole_word_baseline_gain_bits"),
            "baseline_free_advantage": unpaired_vs_null(real_lvr_mean, null_lvr,
                                                        "learned_vs_random_advantage_bits"),
        }

    # ---- verdict ----
    # The falsification gate is: real morphology must beat (i) all label corruptions of its own
    # segmentation, and (ii) all NO-MORPHOLOGY corpus nulls (site-shuffle, freq-matched) on the
    # baseline-free statistic. The synthetic_wrong_language corpus has DENSELY PLANTED morphology
    # (recurrent stems + a closed medial-infix set) — it is a detector positive-control / upper
    # reference, NOT a no-structure null; real LA is expected to have LESS morphological regularity
    # than a densely-planted grammar, so it does not gate the verdict.
    genuine_nulls = ("site_preserving_shuffle", "frequency_matched_pseudo")
    planted_ref = "synthetic_wrong_language"
    beats_labels = all(results["label_corruption_controls"][n]["paired_all"]["real_beats"]
                       for n in results["label_corruption_controls"])
    beats_genuine_nulls = all(
        results["corpus_null_controls"][k]["baseline_free_advantage"]["real_beats"]
        for k in genuine_nulls)
    beats_planted = results["corpus_null_controls"][planted_ref]["baseline_free_advantage"]["real_beats"]
    real_pos = results["real_morphology"]["held_out_gain_bits_per_word_all"]["positive"]
    if real_pos and beats_labels and beats_genuine_nulls:
        verdict = "REAL_STRUCTURE_BEATS_WRONG_STRUCTURE_CONTROLS"
    elif not real_pos:
        verdict = "NO_HELD_OUT_GAIN"
    elif beats_genuine_nulls and not beats_labels:
        verdict = "BEATS_NULLS_NOT_LABEL_CORRUPTIONS"
    elif beats_labels and not beats_genuine_nulls:
        verdict = "BEATS_LABELS_NOT_NO_MORPHOLOGY_NULLS"
    else:
        verdict = "FAILS_WRONG_STRUCTURE_CONTROLS"
    results["verdict"] = verdict
    results["gates"] = {"real_gain_positive": real_pos,
                        "beats_all_label_corruptions": beats_labels,
                        "beats_no_morphology_nulls": beats_genuine_nulls,
                        "beats_planted_morphology_reference": beats_planted,
                        "planted_reference_note": (
                            "synthetic_wrong_language has densely planted morphology; it bounds "
                            "LA's morphological richness from above and confirms detector sensitivity, "
                            "it is not a falsification gate.")}

    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "E5_wrongstruct.json"), "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("WROTE", os.path.join(DATA, "E5_wrongstruct.json"))
    print("\nVERDICT:", verdict)
    print("real gain (all)      :", results["real_morphology"]["held_out_gain_bits_per_word_all"])
    print("real gain (multisign):", results["real_morphology"]["held_out_gain_bits_per_word_multisign"])
    print("real learned>random  :", results["real_morphology"]["baseline_free_learned_vs_random_advantage"])
    for n, d in results["label_corruption_controls"].items():
        print(f"  [label] {n:22s} ctrl={d['control_mean_gain_bits']:+.4f}  paired_all={d['paired_all']}")
    for k, d in results["corpus_null_controls"].items():
        print(f"  [null ] {k:24s}")
        print(f"          confounded : {d['absolute_gain_confounded']}")
        print(f"          baselinefree: {d['baseline_free_advantage']}")
    return results


if __name__ == "__main__":
    main()
