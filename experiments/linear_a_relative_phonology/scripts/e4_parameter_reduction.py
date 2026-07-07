#!/usr/bin/env python3
"""E4 — PARAMETER REDUCTION (Constitution v2.2 Art. III/V/VII/VIII/IX/XII).

Does the E1 morphology (word = [prefix?] stem [suffix?], single-sign affixes; the Bayesian-PSS /
paradigm family) actually REDUCE the number of independent sign/word hypotheses, or does it merely
re-describe the training corpus?  We separate two things that a fitted morphology can do:

  (1) COMPRESSION on TRAINING data.  Two-part MDL (Rissanen / Morfessor form):
        L_total = L(lexicon codebook) + L(corpus | codebook).
      Flat model    = each WORD TYPE is one lexical unit.
      Morph model   = the lexical units are MORPHEMES (prefixes u stems u suffixes) shared across words.
      If morphemes are shared, the codebook shrinks; the corpus code may grow (3 units/word vs 1).
      Compression improvement = (DL_flat - DL_morph) / DL_flat.  This is a TRAINING statement.

  (2) HELD-OUT PREDICTIVE improvement.  5-fold CV over word tokens.  Each model is a PROPER
      generative distribution over sign-strings (a stop symbol makes the sign-unigram base proper),
      so held-out negative log-likelihood (bits/word, bits/sign) is directly comparable:
        P0    = sign-unigram-with-stop           (no morphology, no lexicon)          -- the floor
        FLAT  = Witten-Bell( whole-word lexicon , P0 )   (MEMORISE training words)
        MORPH = [prefix?] stem [suffix?] with each component smoothed and backing off to the P0 base
      Reported OVERALL and split by test-word-type SEEN vs UNSEEN in the training fold.  UNSEEN is
      the true generalization test: the flat model can only back off to P0 there, so any morph gain
      on UNSEEN types is real structure, not memorisation.

  THE HONEST RULE (stated up front): a morphology that COMPRESSES training but does NOT beat FLAT/P0
  on held-out prediction does NOT advance -- it re-describes the data it was fitted to.  Both numbers
  are reported; the verdict is a function of both.

  POSITIVE CONTROL.  The identical pipeline runs on Linear B DAMOS wordforms, whose -JO/-JA/-O/-A
  inflection is real and generalizes.  If the method shows a held-out morph advance on LB but not LA,
  the LA result is a real power/typology statement, not a dead detector (non-circular: LB values are
  never a model input; they are not used at all here -- only the anonymous string statistics are).

NON-CIRCULAR (Art. XII): every input is a distributional statistic over ANONYMOUS sign identities.
No phonetic value is assigned; no transfer licence is earned.  L2/L3.  Deterministic seed 20260708.
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
LOG2 = math.log(2.0)


def load_words(segfile):
    units = json.load(open(os.path.join(SEGDIR, segfile)))["units"]
    return [tuple(u["signs"]) for u in units]


def unigram(words):
    c = Counter(s for w in words for s in w)
    return c, sum(c.values())


# ============================================================ MAP prefix-stem-suffix segmentation
def fit_pss(words, ap=1.0, ast=2.0, a0=1.0, b0=1.0, epochs=30, seed=SEED):
    """Hard-EM MAP segmentation, word = [prefix?] stem [suffix?] (single-sign affixes), DP cache over a
    sign-by-sign base measure (identical model to E1 bayesian_pss).  Returns the fitted count tables and
    the per-word MAP analysis so both the MDL codebook and the held-out predictive can be built."""
    rng = random.Random(seed)
    words = [w for w in words if len(w) >= 1]
    Nw = len(words)
    uni, un = unigram(words)
    lpu = {s: math.log(uni[s] / un) for s in uni}

    def G0(s):
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

    for w in words:
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

    analysis = {}  # word tuple -> (hp, hs, stem) MAP (last-seen; deterministic given convergence)
    for k in keys:
        hp, hs, w = seg[k]
        analysis[w] = (hp, hs, stem_of(w, hp, hs))
    return {
        "Nw": Nw, "cpre": cpre, "csuf": csuf, "cstem": cstem,
        "npre": npre[0], "nsuf": nsuf[0], "nstem": nstem[0],
        "pi_p": (npre[0] + a0) / (Nw + a0 + b0), "pi_s": (nsuf[0] + a0) / (Nw + a0 + b0),
        "analysis": analysis,
    }


def fit_random_seg(words, pi_p, pi_s, seed=SEED):
    """NULL: assign each word a RANDOM (hp,hs) at the SAME marginal prefix/suffix rates as the learned
    model, then read off count tables.  Same PSS structure and rates; only the CUT LOCATIONS are random
    (no DP cache / no rich-get-richer).  If the learned MORPH beats this on held-out UNSEEN words, the
    generalization comes from the specific learned morphology, not from splitting words per se."""
    rng = random.Random(seed)
    words = [w for w in words if len(w) >= 1]
    cpre = Counter(); csuf = Counter(); cstem = Counter()
    npre = 0; nsuf = 0; nstem = 0
    analysis = {}
    for w in words:
        L = len(w)
        hp = 1 if (L >= 2 and rng.random() < pi_p) else 0
        hs = 1 if (L - hp >= 2 and rng.random() < pi_s) else 0
        stem = w[(1 if hp else 0):(L - 1 if hs else L)]
        if hp:
            cpre[w[0]] += 1; npre += 1
        if hs:
            csuf[w[-1]] += 1; nsuf += 1
        cstem[stem] += 1; nstem += 1
        analysis[w] = (hp, hs, stem)
    return {"Nw": len(words), "cpre": cpre, "csuf": csuf, "cstem": cstem,
            "npre": npre, "nsuf": nsuf, "nstem": nstem, "pi_p": pi_p, "pi_s": pi_s,
            "analysis": analysis}


# ============================================================ (1) two-part MDL compression (TRAINING)
def base_spell_bits(uni, un, V):
    """bits to spell an arbitrary sign-string using the sign-unigram-with-stop code (add-0.5)."""
    a = 0.5
    denom = un + a * (V + 1)
    lp = {s: -math.log((uni.get(s, 0) + a) / denom) / LOG2 for s in list(uni.keys())}
    lp_unk = -math.log(a / denom) / LOG2
    lp_stop = -math.log((0 + a) / denom) / LOG2  # STOP never seen as a sign; add-0.5 code slot

    def spell(seq):
        return sum(lp.get(s, lp_unk) for s in seq) + lp_stop
    return spell


def mdl_two_part(words, fit):
    """Two-part description length, in bits, for FLAT (word-type lexicon) vs MORPH (morpheme lexicon)."""
    uni, un = unigram(words)
    V = len(uni)
    spell = base_spell_bits(uni, un, V)

    N = len(words)
    typ = Counter(words)

    # ---- FLAT: lexicon = word types; corpus code = -log2 MLE type prob ----
    L_model_flat = sum(spell(w) for w in typ)                    # transmit each type once
    L_corpus_flat = sum(c * (-math.log(c / N) / LOG2) for c in typ.values())
    DL_flat = L_model_flat + L_corpus_flat

    # ---- MORPH: lexicon = distinct morphemes; corpus code = structure bits + 3 morph codes ----
    an = fit["analysis"]
    pref_types = set(); suf_types = set(); stem_types = set()
    for w in typ:
        hp, hs, stem = an[w]
        if hp:
            pref_types.add(w[0])
        if hs:
            suf_types.add(w[-1])
        stem_types.add(stem)
    morph_types = set()
    for x in pref_types:
        morph_types.add(("P", x))
    for x in suf_types:
        morph_types.add(("S", x))
    for t in stem_types:
        morph_types.add(("T", t))
    # codebook: spell each distinct morpheme once (prefix/suffix are single signs; stems are strings)
    L_model_morph = 0.0
    for x in pref_types:
        L_model_morph += spell((x,))
    for x in suf_types:
        L_model_morph += spell((x,))
    for t in stem_types:
        L_model_morph += spell(tuple(t))

    # corpus code: per token, structure (hp,hs gates) + prefix code + stem code + suffix code (MLE)
    cpre, csuf, cstem = fit["cpre"], fit["csuf"], fit["cstem"]
    npre, nsuf, nstem = fit["npre"], fit["nsuf"], fit["nstem"]
    pi_p, pi_s = fit["pi_p"], fit["pi_s"]
    bits_p1 = -math.log(pi_p) / LOG2; bits_p0 = -math.log(1 - pi_p) / LOG2
    bits_s1 = -math.log(pi_s) / LOG2; bits_s0 = -math.log(1 - pi_s) / LOG2
    L_corpus_morph = 0.0
    for w, c in typ.items():
        hp, hs, stem = an[w]
        b = 0.0
        b += bits_p1 if hp else bits_p0
        b += bits_s1 if hs else bits_s0
        if hp:
            b += -math.log(cpre[w[0]] / npre) / LOG2
        if hs:
            b += -math.log(csuf[w[-1]] / nsuf) / LOG2
        b += -math.log(cstem[stem] / nstem) / LOG2
        L_corpus_morph += c * b
    DL_morph = L_model_morph + L_corpus_morph

    return {
        "n_word_types": len(typ), "n_tokens": N,
        "flat": {"L_model_bits": round(L_model_flat, 1), "L_corpus_bits": round(L_corpus_flat, 1),
                 "DL_total_bits": round(DL_flat, 1), "n_lexical_units": len(typ)},
        "morph": {"L_model_bits": round(L_model_morph, 1), "L_corpus_bits": round(L_corpus_morph, 1),
                  "DL_total_bits": round(DL_morph, 1),
                  "n_prefix_types": len(pref_types), "n_suffix_types": len(suf_types),
                  "n_stem_types": len(stem_types), "n_lexical_units": len(morph_types)},
        "compression_improvement": round((DL_flat - DL_morph) / DL_flat, 4),
        "delta_DL_bits": round(DL_flat - DL_morph, 1),
        "param_reduction_ratio": round(len(morph_types) / len(typ), 4),
        "delta_lexical_units": len(typ) - len(morph_types),
    }


# ============================================================ (2) held-out predictive models
class P0:
    """Proper sign-unigram-with-stop distribution over nonempty sign-strings (add-0.5)."""
    def __init__(self, train_words):
        uni, un = unigram(train_words)
        self.V = len(uni)
        a = 0.5
        self.denom = un + a * (self.V + 1)
        self.a = a
        self.uni = uni
        self.lp = {s: math.log((uni[s] + a) / self.denom) for s in uni}
        self.lp_unk = math.log(a / self.denom)
        self.lp_stop = math.log(a / self.denom)  # stop token as an extra alphabet symbol

    def logp(self, w):
        return sum(self.lp.get(s, self.lp_unk) for s in w) + self.lp_stop


class Flat:
    """Witten-Bell interpolation of a whole-word MLE lexicon with the P0 base (proper)."""
    def __init__(self, train_words, p0):
        self.p0 = p0
        self.typ = Counter(train_words)
        self.N = sum(self.typ.values())
        self.T = len(self.typ)
        self.lam = self.N / (self.N + self.T)          # Witten-Bell mixing weight

    def logp(self, w):
        pl = self.typ.get(w, 0) / self.N if self.N else 0.0
        p = self.lam * pl + (1 - self.lam) * math.exp(self.p0.logp(w))
        return math.log(p)

    def seen(self, w):
        return w in self.typ


class Morph:
    """[prefix?] stem [suffix?] proper generative model; stem uses Witten-Bell(stem-lex, P0), affixes
    add-0.5 categorical over signs, gates = fitted pi.  Marginalises over the <=4 analyses."""
    def __init__(self, fit, p0):
        self.p0 = p0
        self.cpre, self.csuf, self.cstem = fit["cpre"], fit["csuf"], fit["cstem"]
        self.npre, self.nsuf, self.nstem = fit["npre"], fit["nsuf"], fit["nstem"]
        self.pi_p, self.pi_s = fit["pi_p"], fit["pi_s"]
        self.Vp = max(1, len(self.cpre)); self.Vs = max(1, len(self.csuf))
        self.nst_types = max(1, len(self.cstem))
        self.lam_stem = self.nstem / (self.nstem + self.nst_types)
        self.b = 0.5

    def _p_pre(self, x):
        return (self.cpre.get(x, 0) + self.b) / (self.npre + self.b * (self.Vp + 1))

    def _p_suf(self, x):
        return (self.csuf.get(x, 0) + self.b) / (self.nsuf + self.b * (self.Vs + 1))

    def _p_stem(self, t):
        pl = self.cstem.get(t, 0) / self.nstem if self.nstem else 0.0
        return self.lam_stem * pl + (1 - self.lam_stem) * math.exp(self.p0.logp(t))

    def logp(self, w):
        L = len(w)
        tot = 0.0
        for hp in (0, 1):
            for hs in (0, 1):
                if L - hp - hs < 1 or (hp and L < 2):
                    continue
                stem = w[(1 if hp else 0):(L - 1 if hs else L)]
                pr = (self.pi_p if hp else 1 - self.pi_p) * (self.pi_s if hs else 1 - self.pi_s)
                pr *= (self._p_pre(w[0]) if hp else 1.0)
                pr *= (self._p_suf(w[-1]) if hs else 1.0)
                pr *= self._p_stem(stem)
                tot += pr
        return math.log(tot) if tot > 0 else self.p0.logp(w)


def cv_heldout(words, k=5, seed=SEED):
    """k-fold CV over tokens; held-out bits/word and bits/sign for P0, FLAT, MORPH; SEEN/UNSEEN split."""
    rng = random.Random(seed)
    idx = list(range(len(words))); rng.shuffle(idx)
    folds = [idx[i::k] for i in range(k)]
    models = ("P0", "FLAT", "MORPH", "MORPH_RANDNULL")
    agg = {m: {"bits": 0.0, "signs": 0, "n": 0} for m in models}
    split = {"seen": {m: {"bits": 0.0, "n": 0} for m in models},
             "unseen": {m: {"bits": 0.0, "n": 0} for m in models}}
    per_fold = []
    for f in range(k):
        test_ix = set(folds[f])
        train = [words[i] for i in idx if i not in test_ix]
        test = [words[i] for i in folds[f]]
        p0 = P0(train); flat = Flat(train, p0); fit = fit_pss(train, seed=seed + f); morph = Morph(fit, p0)
        nullfit = fit_random_seg(train, fit["pi_p"], fit["pi_s"], seed=seed + f)
        morph_null = Morph(nullfit, p0)
        fb = {m: 0.0 for m in agg}; fn = 0
        for w in test:
            lp = {"P0": p0.logp(w), "FLAT": flat.logp(w), "MORPH": morph.logp(w),
                  "MORPH_RANDNULL": morph_null.logp(w)}
            seen = flat.seen(w)
            for m in agg:
                bits = -lp[m] / LOG2
                agg[m]["bits"] += bits; agg[m]["signs"] += len(w); agg[m]["n"] += 1
                fb[m] += bits
                s = "seen" if seen else "unseen"
                split[s][m]["bits"] += bits; split[s][m]["n"] += 1
            fn += 1
        per_fold.append({m: round(fb[m] / fn, 4) for m in agg})
    out = {"k": k, "n_tokens": len(words)}
    for m in agg:
        out[m] = {"bits_per_word": round(agg[m]["bits"] / agg[m]["n"], 4),
                  "bits_per_sign": round(agg[m]["bits"] / agg[m]["signs"], 4)}
    out["delta_bpw_morph_minus_flat"] = round(out["MORPH"]["bits_per_word"] - out["FLAT"]["bits_per_word"], 4)
    out["delta_bpw_morph_minus_p0"] = round(out["MORPH"]["bits_per_word"] - out["P0"]["bits_per_word"], 4)
    out["delta_bpw_flat_minus_p0"] = round(out["FLAT"]["bits_per_word"] - out["P0"]["bits_per_word"], 4)
    out["delta_bpw_morph_minus_randnull"] = round(out["MORPH"]["bits_per_word"] - out["MORPH_RANDNULL"]["bits_per_word"], 4)
    # per-fold paired sd of (morph - flat) and (morph - p0)
    dmf = [pf["MORPH"] - pf["FLAT"] for pf in per_fold]
    dmp = [pf["MORPH"] - pf["P0"] for pf in per_fold]
    dmn = [pf["MORPH"] - pf["MORPH_RANDNULL"] for pf in per_fold]

    def msd(a):
        mu = sum(a) / len(a)
        sd = (sum((x - mu) ** 2 for x in a) / (len(a) - 1)) ** 0.5 if len(a) > 1 else 0.0
        return round(mu, 4), round(sd, 4)
    out["per_fold_delta_morph_flat_mean_sd"] = msd(dmf)
    out["per_fold_delta_morph_p0_mean_sd"] = msd(dmp)
    out["per_fold_delta_morph_randnull_mean_sd"] = msd(dmn)
    for s in ("seen", "unseen"):
        d = {}
        for m in agg:
            n = split[s][m]["n"]
            d[m] = {"bits_per_word": round(split[s][m]["bits"] / n, 4) if n else None, "n": n}
        if d["MORPH"]["bits_per_word"] is not None and d["FLAT"]["bits_per_word"] is not None:
            d["delta_bpw_morph_minus_flat"] = round(d["MORPH"]["bits_per_word"] - d["FLAT"]["bits_per_word"], 4)
            d["delta_bpw_morph_minus_p0"] = round(d["MORPH"]["bits_per_word"] - d["P0"]["bits_per_word"], 4)
            d["delta_bpw_morph_minus_randnull"] = round(d["MORPH"]["bits_per_word"] - d["MORPH_RANDNULL"]["bits_per_word"], 4)
        out[s] = d
    return out


# ============================================================ main
def analyse(words, label):
    fit_full = fit_pss(words)
    mdl = mdl_two_part(words, fit_full)
    cv = cv_heldout(words)
    # verdict logic
    compresses = mdl["compression_improvement"] > 0
    dmf_mu, dmf_sd = cv["per_fold_delta_morph_flat_mean_sd"]
    dmp_mu, dmp_sd = cv["per_fold_delta_morph_p0_mean_sd"]
    beats_flat = dmf_mu < 0 and abs(dmf_mu) > dmf_sd            # lower bpw than flat, >1 sd
    beats_p0 = dmp_mu < 0 and abs(dmp_mu) > dmp_sd
    unseen = cv.get("unseen", {})
    # the HONEST generalization test lives on UNSEEN word types (the flat model can only back off there):
    #   - beats the sign-unigram floor P0  -> the morphology transfers structure to novel words
    #   - beats the rate-matched RANDOM-segmentation null -> the gain is the LEARNED structure, not cutting
    gen_beats_p0_unseen = unseen.get("delta_bpw_morph_minus_p0", 0.0) < 0
    gen_beats_randnull_unseen = unseen.get("delta_bpw_morph_minus_randnull", 0.0) < 0
    beats_flat_unseen = unseen.get("delta_bpw_morph_minus_flat", 0.0) < 0
    if compresses and gen_beats_p0_unseen and gen_beats_randnull_unseen:
        verdict = "REDUCES_HYPOTHESES_AND_GENERALIZES"
    elif compresses and gen_beats_p0_unseen:
        # beats the raw floor but NOT the rate-matched random segmentation -> the held-out gain is a
        # generic "any subword lexicon smooths better" effect, not the LEARNED structure
        verdict = "COMPRESSES_TRAINING__HELDOUT_GAIN_NOT_STRUCTURAL"
    elif compresses:
        verdict = "COMPRESSES_TRAINING_ONLY_NO_HELDOUT_ADVANCE"
    else:
        verdict = "NO_COMPRESSION"
    return {"label": label, "mdl_compression": mdl, "heldout_cv": cv,
            "verdict_flags": {"compresses": compresses,
                              "beats_flat_overall": beats_flat, "beats_p0_overall": beats_p0,
                              "gen_beats_p0_on_unseen": gen_beats_p0_unseen,
                              "gen_beats_randnull_on_unseen": gen_beats_randnull_unseen,
                              "beats_flat_on_unseen": beats_flat_unseen},
            "verdict": verdict}


def main():
    results = {"seed": SEED, "note": "L2/L3 anonymous relative structure; no value assigned; no licence.",
               "linear_a": {}, "linear_b_positive_control": {}}
    for label, seg in [("GORILA_WORD", "SEG_GORILA_WORD.json"),
                       ("ENTRY", "SEG_ENTRY.json"), ("FORMULA", "SEG_FORMULA.json")]:
        words = load_words(seg)
        results["linear_a"][label] = analyse(words, label)
        r = results["linear_a"][label]
        print(f"[LA {label}] compress={r['mdl_compression']['compression_improvement']:+.4f} "
              f"paramratio={r['mdl_compression']['param_reduction_ratio']} "
              f"dBPW(morph-flat)={r['heldout_cv']['delta_bpw_morph_minus_flat']:+.3f} "
              f"dBPW(morph-P0)={r['heldout_cv']['delta_bpw_morph_minus_p0']:+.3f} -> {r['verdict']}")

    # positive control: Linear B DAMOS wordforms (values never used; anonymous strings only)
    lb_words = [tuple(w) for w in X.load_b_damos()[0]]
    results["linear_b_positive_control"]["DAMOS"] = analyse(lb_words, "LINEAR_B_DAMOS")
    r = results["linear_b_positive_control"]["DAMOS"]
    print(f"[LB DAMOS] compress={r['mdl_compression']['compression_improvement']:+.4f} "
          f"paramratio={r['mdl_compression']['param_reduction_ratio']} "
          f"dBPW(morph-flat)={r['heldout_cv']['delta_bpw_morph_minus_flat']:+.3f} "
          f"dBPW(morph-P0)={r['heldout_cv']['delta_bpw_morph_minus_p0']:+.3f} -> {r['verdict']}")

    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "E4_paramreduce.json"), "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=lambda o: str(o))
    print("WROTE", os.path.join(DATA, "E4_paramreduce.json"))
    return results


if __name__ == "__main__":
    main()
