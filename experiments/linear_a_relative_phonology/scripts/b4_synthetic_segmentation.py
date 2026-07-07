#!/usr/bin/env python3
"""B4 -- SYNTHETIC SEGMENTATION CALIBRATION (Constitution v2.2 Art. III/VII/VIII/XII).

Generate CONTROLLED synthetic syllabic corpora with KNOWN morpheme boundaries, then run the
EXACT B3 unsupervised segmentation families and measure boundary F1 (and the over/under-
segmentation failure mode) as each real-corpus NUISANCE is dialed up:

  (phi)   FORMULAIC administrative sequences   -- fraction of tablets that are fixed multi-word
                                                  templates (repeated collocations).
  (hap)   HIGH HAPAX RATE                       -- fraction of word tokens replaced by freshly
                                                  minted, never-repeated nonce words.
  (dmg)   SIMULATED DAMAGE                       -- per-sign deletion probability (broken tablets);
                                                  empty words drop out, merging their boundaries.
  (gam)   SITE IMBALANCE                         -- S sub-lexicons; per-site token share follows a
                                                  Zipf(gam) law (gam=0 uniform, high => one site
                                                  dominates and rare-site vocab is under-trained).
  (mix)   MIXED BOUNDARY CONVENTIONS             -- fraction of tablets that use the "fine"
                                                  convention (split stem+suffix into two gold words)
                                                  vs the "coarse" convention (one word). The SAME
                                                  sign distribution then carries convention-dependent
                                                  gold => a learnable-boundary ceiling drop.

NON-CIRCULAR: the ground-truth boundaries are a property of the SYNTHETIC generator only; they are
used ONLY to grade. No model receives any boundary label (the B3 families are unsupervised: they
train by EM/cue rules on TRAIN sign streams, are frozen, and predict on held-out TEST streams).

For each (dial, level) we build ONE corpus, split 70/30 by tablet (seeded), train every family on
TRAIN, predict on TEST, and score boundary P/R/F1 against the KNOWN test boundaries. Failure mode =
n_pred_boundaries / n_gold_boundaries (>1 over-segments, <1 under-segments) plus P vs R.

Deterministic (seed 20260708). Writes reports/B_SYNTHETIC_SEGMENTATION.md + data/B4_synthetic.json.
"""
from __future__ import annotations
import json, os, random, sys
from collections import Counter

import numpy as np

ROOT = "/home/claude-runner/gitlab/n8n/logos-linear-a-relative-phonology-seals"
HERE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.dirname(HERE)
DATA = os.path.join(CAMP, "data")
REPORTS = os.path.join(CAMP, "reports")
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
import b3_known_script_segmentation as B3  # reuse the EXACT validated models  # noqa: E402

SEED = 20260708


# ============================================================ SYNTHETIC GENERATOR
class SynthGen:
    """Synthetic administrative syllabary with planted word boundaries.

    Signs: n_vowel pure-vowel signs + n_cons*n_vowel CV signs (~85 types, LA/LB scale).
    Lexicon: n_roots Zipfian roots (len 1-3 signs). A small closed suffix class marks morphology.
    Sites: the root lexicon is partitioned into `n_sites` slabs (+ a shared common core); each
    tablet is drawn from one site's roots (+ core). Site token share ~ Zipf(gamma).
    """

    def __init__(self, rng, n_cons=16, n_vowel=5, n_roots=1200, zipf=0.9,
                 n_suffix=8, p_suffix=0.55, core_frac=0.25, n_sites=8,
                 root_len_dist=(0.30, 0.48, 0.22)):     # P(len=1,2,3)
        self.rng = rng
        self.n_vowel = n_vowel
        self.p_suffix = p_suffix
        self.vowel_signs = [f"V{v}" for v in range(n_vowel)]
        self.cv_signs = [f"C{c}{v}" for c in range(n_cons) for v in range(n_vowel)]
        self.signs = self.vowel_signs + self.cv_signs
        # suffix signs: a dedicated closed class (last few CV signs) used only as suffixes
        self.suffixes = self.cv_signs[-n_suffix:]
        skeleton_pool = self.vowel_signs + self.cv_signs[:-n_suffix]
        # ---- build Zipfian root lexicon
        self.roots = []
        rw = []
        lens = (1, 2, 3)
        for r in range(n_roots):
            L = rng.choices(lens, weights=root_len_dist)[0]
            self.roots.append(tuple(rng.choice(skeleton_pool) for _ in range(L)))
            rw.append(1.0 / ((r + 1) ** zipf))
        # ---- sites: partition roots into a shared CORE + n_sites disjoint slabs
        n_core = int(core_frac * n_roots)
        self.core_idx = list(range(n_core))
        rest = list(range(n_core, n_roots))
        self.site_idx = [rest[i::n_sites] for i in range(n_sites)]
        self.n_sites = n_sites
        self._rw = rw
        # per-root sampling weight (global Zipf)
        # formulaic template bank: fixed multi-word sequences (built lazily w/ common roots)
        self.templates = None

    def _weighted_choice(self, idxs, k=1):
        ws = [self._rw[i] for i in idxs]
        return self.rng.choices(idxs, weights=ws, k=k)

    def _build_templates(self, n_templates=24, tmpl_len=(3, 6)):
        self.templates = []
        for _ in range(n_templates):
            L = self.rng.randint(*tmpl_len)
            idxs = self._weighted_choice(self.core_idx + self.site_idx[0], k=L)
            tmpl = []
            for i in idxs:
                tmpl.extend(self._emit_word_from_root(i, force_suffix=(self.rng.random() < 0.5)))
            self.templates.append(tmpl)

    def _emit_word_from_root(self, ridx, force_suffix=None, fine=False):
        """Return a WORD as a list of gold-words (usually 1; 2 under the 'fine' convention when a
        suffix is present and split off)."""
        root = list(self.roots[ridx])
        add_suf = (self.rng.random() < self.p_suffix) if force_suffix is None else force_suffix
        if add_suf:
            suf = self.rng.choice(self.suffixes)
            if fine:
                return [root, [suf]]          # fine convention: stem | suffix = TWO gold words
            return [root + [suf]]             # coarse convention: one gold word
        return [root]

    def site_weights(self, gamma):
        """token share per site ~ Zipf(gamma) over a shuffled site order (deterministic)."""
        order = list(range(self.n_sites))
        w = np.array([1.0 / ((i + 1) ** gamma) for i in range(self.n_sites)])
        w = w / w.sum()
        return order, w

    def emit_tablet(self, gamma, phi, hap, mix, tab_words=(2, 8)):
        """Emit ONE tablet as a list of GOLD WORDS (each a list of sign strings).
        phi=formulaic frac, hap=hapax-inject frac, mix=fine-convention frac, gamma=site imbalance."""
        # choose site by imbalance law
        order, w = self.site_weights(gamma)
        site = int(np.searchsorted(np.cumsum(w), self.rng.random()))
        pool = self.core_idx + self.site_idx[order[site]]
        fine = (self.rng.random() < mix)         # this tablet's boundary convention
        # formulaic tablet?
        if self.rng.random() < phi:
            if self.templates is None:
                self._build_templates()
            tmpl = self.rng.choice(self.templates)
            return [list(x) for x in tmpl]
        nwords = self.rng.randint(*tab_words)
        words = []
        for _ in range(nwords):
            if self.rng.random() < hap:
                # freshly minted, never-repeated NONCE word (pure hapax)
                L = self.rng.choices((1, 2, 3), weights=(0.3, 0.48, 0.22))[0]
                words.append([self.rng.choice(self.signs) for _ in range(L)])
            else:
                ridx = self._weighted_choice(pool)[0]
                words.extend(self._emit_word_from_root(ridx, fine=fine))
        return words


def damage_tablet(words, dmg, rng):
    """delete each sign with prob dmg; drop resulting empty gold-words (boundaries merge)."""
    if dmg <= 0:
        return words
    out = []
    for w in words:
        nw = [s for s in w if rng.random() >= dmg]
        if nw:
            out.append(nw)
    return out


def build_corpus(gen, n_tablets, gamma=0.0, phi=0.0, hap=0.0, dmg=0.0, mix=0.0,
                 rng=None, min_words=2):
    """Return list of tablets (each = list of gold-words), keeping only multi-word tablets
    (>=1 internal boundary) so boundary recovery is defined."""
    rng = rng or gen.rng
    tabs = []
    tries = 0
    while len(tabs) < n_tablets and tries < n_tablets * 6:
        tries += 1
        words = gen.emit_tablet(gamma, phi, hap, mix)
        words = damage_tablet(words, dmg, rng)
        words = [w for w in words if w]
        if len(words) >= min_words:
            tabs.append(words)
    return tabs


# ============================================================ MODEL RUNNER (B3 families)
def run_models(train_streams, test_streams, test_gold, train_gold, rate, period):
    """Run every B3 family + baselines; return {name: metrics} scored on TEST."""
    uni, fwd, bwd = B3.build_stats(train_streams)
    succ, pred = B3.build_be_trie(train_streams)

    preds = {}
    rb = random.Random(SEED + 1)
    preds["BASELINE_RANDOM"] = [B3.seg_random(s, rate, rb) for s in test_streams]
    preds["BASELINE_FIXED"] = [B3.seg_fixed(s, period) for s in test_streams]
    preds["BASELINE_ALL"] = [B3.seg_all(s) for s in test_streams]
    preds["CUE_TP_min"] = [B3.seg_tp(s, fwd, uni) for s in test_streams]
    be = [B3.seg_be(s, succ, pred) for s in test_streams]
    preds["CUE_BranchEntropy"] = be
    bp, _ = B3.run_bayes(train_streams, test_streams)
    preds["BAYESIAN_unigram"] = bp
    mp, _ = B3.run_mdl(train_streams, test_streams)
    preds["MDL"] = mp
    fp_, _ = B3.run_fst(train_streams, test_streams)
    preds["FINITE_STATE_bigram"] = fp_
    ens = []
    for i, s in enumerate(test_streams):
        votes = Counter()
        for src in (be[i], bp[i], mp[i], fp_[i]):
            for g in src:
                votes[g] += 1
        ens.append({g for g, v in votes.items() if v >= 2})
    preds["MULTISCALE_ENSEMBLE"] = ens

    n_gold = sum(len(g) for g in test_gold)
    out = {}
    for name, pl in preds.items():
        bs = B3.score_boundaries(pl, test_gold)
        n_pred = sum(len(p) for p in pl)
        ratio = (n_pred / n_gold) if n_gold else None
        if ratio is None:
            mode = "n/a"
        elif ratio > 1.15:
            mode = "OVER"
        elif ratio < 0.85:
            mode = "UNDER"
        else:
            mode = "balanced"
        out[name] = {"P": bs["precision"], "R": bs["recall"], "F1": bs["f1"],
                     "n_pred": n_pred, "n_gold": n_gold,
                     "pred_over_gold": round(ratio, 3) if ratio is not None else None,
                     "failure_mode": mode}
    return out


def corpus_diag(tabs):
    """realized nuisance stats: hapax fraction, boundary rate, mean word len, formulaic repetition."""
    word_counts = Counter()
    n_signs = n_gaps = n_bnd = 0
    for t in tabs:
        for w in t:
            word_counts[tuple(w)] += 1
        signs = sum(len(w) for w in t)
        n_signs += signs
        n_gaps += signs - 1
        n_bnd += len(t) - 1
    ntok = sum(word_counts.values())
    hapax = sum(1 for c in word_counts.values() if c == 1)
    return {
        "n_tablets": len(tabs), "n_signs": n_signs, "n_word_tokens": ntok,
        "n_word_types": len(word_counts),
        "word_hapax_frac": round(hapax / len(word_counts), 3) if word_counts else 0.0,
        "boundary_rate": round(n_bnd / n_gaps, 3) if n_gaps else 0.0,
        "mean_word_len": round(n_signs / ntok, 3) if ntok else 0.0,
        "type_token_ratio": round(len(word_counts) / ntok, 3) if ntok else 0.0,
    }


def make_split(tabs, seed=SEED):
    r = random.Random(seed)
    tabs = list(tabs)
    r.shuffle(tabs)
    n_test = int(round(0.30 * len(tabs)))
    test, train = tabs[:n_test], tabs[n_test:]
    tr_s, tr_g, te_s, te_g = [], [], [], []
    for t in train:
        s, g = B3.to_stream(t); tr_s.append(s); tr_g.append(g)
    for t in test:
        s, g = B3.to_stream(t); te_s.append(s); te_g.append(g)
    # baseline params from TRAIN
    train_gaps = sum(len(s) - 1 for s in tr_s) or 1
    rate = sum(len(g) for g in tr_g) / train_gaps
    mean_wl = sum(len(w) for t in train for w in t) / max(1, sum(len(t) for t in train))
    period = max(2, int(round(mean_wl)))
    return tr_s, tr_g, te_s, te_g, rate, period, mean_wl


def evaluate_config(n_tablets, base_kwargs, dial_kwargs, seed=SEED):
    """Build a corpus with the given nuisance settings, split, run models. Returns diag+results."""
    gen = SynthGen(random.Random(seed), **base_kwargs)
    rng = random.Random(seed + 99)
    tabs = build_corpus(gen, n_tablets, rng=rng, **dial_kwargs)
    diag = corpus_diag(tabs)
    tr_s, tr_g, te_s, te_g, rate, period, mean_wl = make_split(tabs, seed=seed)
    diag["train_boundary_rate"] = round(rate, 3)
    diag["fixed_period"] = period
    diag["n_train"] = len(tr_s); diag["n_test"] = len(te_s)
    diag["test_gold_boundaries"] = sum(len(g) for g in te_g)
    res = run_models(tr_s, te_s, te_g, tr_g, rate, period)
    return {"diag": diag, "models": res}


MODELS_ORDER = ["BASELINE_RANDOM", "BASELINE_FIXED", "BASELINE_ALL",
                "CUE_TP_min", "CUE_BranchEntropy", "BAYESIAN_unigram",
                "MDL", "FINITE_STATE_bigram", "MULTISCALE_ENSEMBLE"]


def main():
    N_TAB = 1400
    BASE = dict(n_cons=16, n_vowel=5, n_roots=1200, zipf=0.9, n_suffix=8,
                p_suffix=0.55, core_frac=0.25, n_sites=8)
    # baseline (clean) nuisance settings -- everything off
    CLEAN = dict(gamma=0.0, phi=0.0, hap=0.0, dmg=0.0, mix=0.0)

    result = {"task": "B4_synthetic_segmentation_calibration", "seed": SEED,
              "constitution": "v2.2", "n_tablets_target": N_TAB,
              "generator_config": BASE, "models": MODELS_ORDER}

    # ---- (0) CLEAN baseline
    print("[0] clean baseline ...", flush=True)
    result["clean_baseline"] = evaluate_config(N_TAB, BASE, CLEAN)

    # ---- (1) NUISANCE SWEEPS: dial each up, hold the others at clean
    sweeps = {
        "formulaic_phi":   ("phi", [0.0, 0.15, 0.30, 0.50, 0.75]),
        "hapax_inject":    ("hap", [0.0, 0.15, 0.30, 0.50, 0.70]),
        "damage_dmg":      ("dmg", [0.0, 0.10, 0.20, 0.35, 0.50]),
        "site_imbalance":  ("gam", [0.0, 0.6, 1.0, 1.6, 2.4]),
        "mixed_convention":("mix", [0.0, 0.15, 0.30, 0.50, 0.75]),
    }
    dial_map = {"phi": "phi", "hap": "hap", "dmg": "dmg", "gam": "gamma", "mix": "mix"}
    result["sweeps"] = {}
    for sname, (key, levels) in sweeps.items():
        print(f"[1] sweep {sname} ...", flush=True)
        rows = []
        for lv in levels:
            dk = dict(CLEAN); dk[dial_map[key]] = lv
            ev = evaluate_config(N_TAB, BASE, dk, seed=SEED)
            rows.append({"level": lv, "diag": ev["diag"], "models": ev["models"]})
            f1s = {m: ev["models"][m]["F1"] for m in ("BAYESIAN_unigram", "MDL", "CUE_BranchEntropy")}
            print(f"    {key}={lv}: boundary_rate={ev['diag']['boundary_rate']} "
                  f"hapax={ev['diag']['word_hapax_frac']} F1 {f1s}", flush=True)
        result["sweeps"][sname] = {"dial": key, "levels": levels, "rows": rows}

    # ---- (2) LA-LIKE combined config (short words + high hapax + damage + imbalance + some mixing)
    #      calibrated toward LA nuisance levels: GORILA-word mean ~1.84 signs, sign-hapax high,
    #      packed/broken tablets, site-imbalanced corpus.
    print("[2] LA-like combined config ...", flush=True)
    LA_BASE = dict(BASE); LA_BASE.update(root_len_dist=(0.55, 0.35, 0.10), p_suffix=0.35, zipf=1.05)
    LA_DIAL = dict(gamma=1.6, phi=0.20, hap=0.45, dmg=0.15, mix=0.25)
    result["LA_like_combined"] = evaluate_config(N_TAB, LA_BASE, LA_DIAL, seed=SEED)
    print("    LA-like diag:", result["LA_like_combined"]["diag"], flush=True)

    # ---- (3) LB-LIKE clean reference (longer words, low hapax) -- upper anchor
    print("[3] LB-like clean reference ...", flush=True)
    LB_BASE = dict(BASE); LB_BASE.update(root_len_dist=(0.15, 0.45, 0.40), p_suffix=0.6, zipf=0.8)
    result["LB_like_reference"] = evaluate_config(N_TAB, LB_BASE, CLEAN, seed=SEED)
    print("    LB-like diag:", result["LB_like_reference"]["diag"], flush=True)

    # ---- (4) annotate every config with baseline-relative margins (the HONEST metric).
    #      Absolute F1 is confounded by boundary rate (damage/mixing shorten words => the all-cut
    #      baseline and any over-cutter both rise); margin over the STRONGEST baseline is what
    #      isolates genuine segmentation skill.
    def annotate(ev):
        m = ev["models"]
        best_bl = max(m["BASELINE_RANDOM"]["F1"], m["BASELINE_FIXED"]["F1"])
        all_cut = m["BASELINE_ALL"]["F1"]
        ev["baselines"] = {"best_random_or_fixed_F1": round(best_bl, 4), "all_cut_F1": round(all_cut, 4)}
        for nm, r in m.items():
            if nm.startswith("BASELINE"):
                continue
            r["margin_vs_best_baseline"] = round(r["F1"] - best_bl, 4)
            r["margin_vs_all_cut"] = round(r["F1"] - all_cut, 4)
        return ev

    annotate(result["clean_baseline"])
    annotate(result["LA_like_combined"])
    annotate(result["LB_like_reference"])
    for sw in result["sweeps"].values():
        for row in sw["rows"]:
            annotate(row)

    os.makedirs(DATA, exist_ok=True)
    outp = os.path.join(DATA, "B4_synthetic.json")
    json.dump(result, open(outp, "w"), indent=1, default=str)
    print("\nWROTE", outp)
    return result


if __name__ == "__main__":
    main()
