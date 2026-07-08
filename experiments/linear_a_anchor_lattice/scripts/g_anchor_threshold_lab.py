#!/usr/bin/env python3
"""
TASK G — Counterfactual Identifiability / Anchor-Threshold Lab
==============================================================
Campaign: research/linear-a-anchor-lattice · v2.2 · seed 20260708

Question (Art. VIII power / Art. XI-XII non-circular): how many INDEPENDENT anchors of what
QUALITY does the full lattice need to recover a KNOWN syllabic script — and where does Linear A
actually sit on that surface?

Mechanical, non-circular recovery model (the "Ventris grid" identifiability model)
----------------------------------------------------------------------------------
A syllabary is a Consonant x Vowel grid: each syllabic sign s has a true value (C(s), V(s)).
Recovery of a sign's ABSOLUTE value requires knowing BOTH its consonant (row) and vowel (column).

Two kinds of evidence, kept strictly separate (Art. XV: relative reduction never implies value):
  * VALUE-FREE relative channel (substitution/morphology): tells the solver that two signs
    SHARE a row (same C) or SHARE a column (same V) -- never which C or V. Parametrised by
    `coverage` (fraction of within-class sign-pairs whose relation is observed). This is what
    the LA F4/morphology channels deliver, and it earns no value on its own.
  * ANCHORS: reveal the true (C,V) of a sign. Injected, varying n_anchors / slots-per-anchor /
    source-lineages / site-coverage / noise / incorrect-fraction / dependency-clones.

Ground-truth values are used ONLY (a) to build the true grid for synthetic/known benches and
(b) to GRADE recovery. The solver never sees a true value except through an injected anchor
(non-circular; Art. XII: known values grade benchmarks only).

Propagation (mechanical): union-find on observed same-row / same-column edges -> row-components
and column-components. A CORRECT propagating anchor labels its whole row-component's C and its
whole column-component's V. A sign's absolute value is recovered iff its row-component carries a
C and its column-component carries a V and neither is corrupted by a wrong anchor. WRONG anchors
seed a wrong label into their components -> every sign recovered through them is a FALSE POSITIVE.

Anchor QUALITY dims:
  * slots-per-anchor q (1..8): an anchor is a WORD EQUATION over q signs (EA-13's La = skeleton
    length). A correct q-slot anchor pins the true (C,V) of its q signs, each of which then labels
    its row-/col-component. Anchor words for the LB benches are sampled from REAL LB wordforms
    (so anchors are frequency-biased toward common signs, as real toponyms are — tail signs can
    stay dark exactly as in LA). Identification security vs q is a SEPARATE axis (f_wrong; in the
    EA-13 comparison f_wrong is set to EA-13's measured per-anchor FP_frozen at that La).
  * source_lineages L (1..5) + clones: an anchor is INDEPENDENT only if lineage-distinct
    (Art. XI). Clones (n_anchors>L) fall on already-covered cells -> zero new covering power.
  * incorrect_fraction f (0..): each anchor is wrong with prob f -> false positives.
  * site_coverage: fraction of the grid the anchor set is allowed to touch (regional bias);
    anchors confined to few sites cover fewer rows/columns.

Benches: opaque_LB (real 66-sign LB grid), degraded_LB (LA-matched sparsity), synth_syllabary
(clean random grids), synth_admin (Zipf+formula, tail-dark like LA ledgers), wrong_language
(model-misspecified: grid assumption false -> pure false-positive generator).
"""
import json, os, math, random, itertools, hashlib, csv
from collections import Counter, defaultdict

def stable_hash(obj):
    """Deterministic across processes (PYTHONHASHSEED-immune), unlike builtin hash()."""
    return int(hashlib.md5(repr(sorted(obj.items())).encode()).hexdigest()[:8], 16)

SEED = 20260708
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "data", "controls", "anchor_threshold")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------------------
# LB grid from real values (grades benchmarks only; Art. XII)
# ---------------------------------------------------------------------------
def build_lb_grid():
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))  # repo root for scripts.cross_script
    from scripts.cross_script.data import load_b_damos
    seqs, freq, _ = load_b_damos()
    V = set("AEIOU")
    def parse(s):
        if not s or s.startswith("*"): return None
        if any(ch.isdigit() for ch in s): return None
        if s[-1] not in V: return None
        c = s[:-1] or "_"
        return (c, s[-1])
    signs = {}
    for s in freq:
        p = parse(s)
        if p: signs[s] = p
    # word sequences restricted to parseable syllabic signs (held-out reading test)
    words = [[w for w in seq if w in signs] for seq in seqs]
    words = [w for w in words if len(w) >= 2]
    return signs, words, freq

# ---------------------------------------------------------------------------
# Synthetic grid generators
# ---------------------------------------------------------------------------
def synth_grid(nC, nV, fill=1.0, rng=None):
    """Random syllabary: nC consonants x nV vowels, `fill` fraction of cells realised."""
    rng = rng or random.Random(SEED)
    Cs = [f"C{i}" for i in range(nC)]
    Vs = [f"V{j}" for j in range(nV)]
    signs = {}
    k = 0
    for c in Cs:
        for v in Vs:
            if rng.random() <= fill:
                signs[f"s{k}"] = (c, v); k += 1
    return signs

def zipf_words(signs, n_words, rng, alpha=1.1, maxlen=5):
    """Admin-style corpus: Zipfian sign freq, short formulaic words."""
    sl = list(signs)
    # zipf weights
    w = [1.0/((i+1)**alpha) for i in range(len(sl))]
    tot = sum(w); w = [x/tot for x in w]
    words = []
    for _ in range(n_words):
        L = rng.choices([2,3,4,5], weights=[0.35,0.4,0.2,0.05])[0]
        words.append(rng.choices(sl, weights=w, k=L))
    return words

# ---------------------------------------------------------------------------
# Recovery engine
# ---------------------------------------------------------------------------
class UF:
    def __init__(self, items):
        self.p = {x: x for x in items}
    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]; x = self.p[x]
        return x
    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb: self.p[ra] = rb

def observed_partition(signs, coverage, rng, mislabel=0.0):
    """Return same-row and same-col UF structures observed at `coverage`.
    `mislabel`: prob a relative edge is WRONG (links across true classes) -> model misspecification.
    """
    row_uf = UF(signs); col_uf = UF(signs)
    sl = list(signs)
    by_c = defaultdict(list); by_v = defaultdict(list)
    for s,(c,v) in signs.items():
        by_c[c].append(s); by_v[v].append(s)
    # same-row edges
    for c, members in by_c.items():
        for a, b in itertools.combinations(members, 2):
            if rng.random() <= coverage:
                row_uf.union(a, b)
    for v, members in by_v.items():
        for a, b in itertools.combinations(members, 2):
            if rng.random() <= coverage:
                col_uf.union(a, b)
    # mislabel edges (wrong-language / misspecification): link random cross-class pairs
    if mislabel > 0:
        npairs = int(mislabel * len(sl))
        for _ in range(npairs):
            a, b = rng.sample(sl, 2)
            if rng.random() < 0.5: row_uf.union(a, b)
            else: col_uf.union(a, b)
    return row_uf, col_uf

def anchor_word(pool, slots, rng, corpus_words=None):
    """Draw one q-slot anchor word.
    If corpus_words given (LB benches): sample a REAL wordform with >= q distinct in-pool signs
    (frequency-realistic — anchors use common signs, tail signs stay dark). Fallback: random
    distinct signs from the pool (synthetic benches / q longer than any real word)."""
    if corpus_words:
        pset = set(pool)
        for _ in range(200):
            w = corpus_words[rng.randrange(len(corpus_words))]
            distinct = [s for s in dict.fromkeys(w) if s in pset]
            if len(distinct) >= slots:
                return distinct[:slots]
    return rng.sample(pool, min(slots, len(pool)))

def run_once(signs, coverage, n_anchors, slots, lineages, f_wrong,
             site_coverage, clone_extra, rng, mislabel=0.0, held_words=None,
             anchor_corpus=None):
    """One replicate. Returns metric dict.
    An anchor = a q-slot word equation. Correct -> pins true (C,V) of its q signs, each of which
    labels its row-/col-component. Wrong (prob f_wrong) -> pins WRONG values (chance-match
    identification), poisoning the components it touches. Clones (Art. XI) are re-citations of
    the same underlying identification: zero new information by construction."""
    sl = list(signs)
    Cs = sorted(set(c for c,v in signs.values()))
    Vs = sorted(set(v for c,v in signs.values()))
    row_uf, col_uf = observed_partition(signs, coverage, rng, mislabel=mislabel)

    # candidate anchor pool restricted by site_coverage (regional bias -> fewer distinct cells)
    pool = sl if site_coverage >= 1.0 else rng.sample(sl, max(2, int(len(sl)*site_coverage)))

    # INDEPENDENT anchors = min(n_anchors, lineages); the rest are clones (Art. XI)
    n_indep = min(n_anchors, lineages)
    anchors = [anchor_word(pool, slots, rng, anchor_corpus) for _ in range(n_indep)]
    # clone_extra re-citations: same identifications, no independent re-draw -> no effect.

    # seed labels
    row_label = {}   # row-component root -> C
    col_label = {}
    wrong_row = set(); wrong_col = set()
    for word in anchors:
        is_wrong = rng.random() < f_wrong
        for s in word:
            c, v = signs[s]
            rr, cc = row_uf.find(s), col_uf.find(s)
            if is_wrong:
                wc = rng.choice([x for x in Cs if x != c] or [c])
                wv = rng.choice([x for x in Vs if x != v] or [v])
                _seed(row_label, wrong_row, rr, wc)
                _seed(col_label, wrong_col, cc, wv)
            else:
                _seed(row_label, wrong_row, rr, c)
                _seed(col_label, wrong_col, cc, v)

    # grade every sign
    n = len(sl); abs_ok = 0; abs_wrong = 0; recovered = 0
    rel_ok = 0
    rmembers = defaultdict(list); cmembers = defaultdict(list)
    for x in sl:
        rmembers[row_uf.find(x)].append(x); cmembers[col_uf.find(x)].append(x)
    for s in sl:
        tc, tv = signs[s]
        rr, cc = row_uf.find(s), col_uf.find(s)
        gc = row_label.get(rr)
        gv = col_label.get(cc)
        if gc is not None and gv is not None:
            recovered += 1
            if gc == tc and gv == tv and rr not in wrong_row and cc not in wrong_col:
                abs_ok += 1
            else:
                abs_wrong += 1
        # relative-class recovery: sign sits in a PURE non-singleton row-comp or col-comp
        rcomp = rmembers[rr]; ccomp = cmembers[cc]
        pure_r = len(rcomp) > 1 and all(signs[x][0] == tc for x in rcomp)
        pure_c = len(ccomp) > 1 and all(signs[x][1] == tv for x in ccomp)
        if pure_r or pure_c:
            rel_ok += 1

    # equivalence-class reduction: log10 of #label-assignments consistent w/ evidence.
    # unlabeled row-components can carry any of the free consonant labels; same for cols.
    row_comps = set(row_uf.find(x) for x in sl)
    col_comps = set(col_uf.find(x) for x in sl)
    lab_rc = sum(1 for rc in row_comps if rc in row_label)
    lab_cc = sum(1 for cc in col_comps if cc in col_label)
    free_rows = max(0, len(row_comps) - lab_rc)
    free_cols = max(0, len(col_comps) - lab_cc)
    log_amb = _lfact(free_rows) + _lfact(free_cols)          # residual ambiguity (log10)
    log_amb0 = _lfact(len(row_comps)) + _lfact(len(col_comps))  # before anchors
    eq_reduction = log_amb0 - log_amb

    # held-out word recovery
    hw = 0.0
    if held_words:
        good = 0; tot = 0
        for w in held_words:
            tot += 1
            ok = True
            for s in w:
                rr, cc = row_uf.find(s), col_uf.find(s)
                gc = row_label.get(rr); gv = col_label.get(cc)
                if not (gc == signs[s][0] and gv == signs[s][1]):
                    ok = False; break
            good += int(ok)
        hw = good / tot if tot else 0.0

    fp_rate = abs_wrong / recovered if recovered else 0.0
    return dict(
        abs_recovery=abs_ok / n,
        rel_recovery=rel_ok / n,
        eq_reduction=eq_reduction,
        residual_ambiguity_log10=log_amb,
        heldout_word_recovery=hw,
        fp_rate=fp_rate,
        recovered_frac=recovered / n,
        n_independent=n_indep,
    )

def _seed(label, wrongset, comp, val):
    if comp in label and label[comp] != val:
        wrongset.add(comp)  # conflict -> corrupted
    label.setdefault(comp, val)

def _lfact(k):
    return sum(math.log10(i) for i in range(2, k+1)) if k > 1 else 0.0

def aggregate(signs, params, reps, base_seed, held_words=None, mislabel=0.0, anchor_corpus=None):
    acc = defaultdict(list)
    for r in range(reps):
        rng = random.Random(base_seed + r*7919 + stable_hash(params) % 100000)
        m = run_once(signs, held_words=held_words, mislabel=mislabel, rng=rng,
                     anchor_corpus=anchor_corpus, **params)
        for k, v in m.items(): acc[k].append(v)
    return {k: sum(v)/len(v) for k, v in acc.items()}

# ---------------------------------------------------------------------------
# Morphology recovery (connectivity of true relative pairs at given coverage)
# ---------------------------------------------------------------------------
def morphology_recovery(signs, coverage, reps, base_seed):
    vals = []
    for r in range(reps):
        rng = random.Random(base_seed + 101*r)
        row_uf, col_uf = observed_partition(signs, coverage, rng)
        by_c = defaultdict(list); by_v = defaultdict(list)
        for s,(c,v) in signs.items():
            by_c[c].append(s); by_v[v].append(s)
        good = tot = 0
        for members in list(by_c.values()) + list(by_v.values()):
            for a, b in itertools.combinations(members, 2):
                tot += 1
                if row_uf.find(a) == row_uf.find(b) or col_uf.find(a) == col_uf.find(b):
                    good += 1
        vals.append(good/tot if tot else 0.0)
    return sum(vals)/len(vals)

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    print("[G] building LB grid ...")
    lb_signs, lb_words, _ = build_lb_grid()
    print(f"    LB syllabic grid: {len(lb_signs)} signs, "
          f"{len(set(c for c,v in lb_signs.values()))}C x {len(set(v for c,v in lb_signs.values()))}V, "
          f"{len(lb_words)} words")
    rng0 = random.Random(SEED)
    lb_held = rng0.sample(lb_words, min(400, len(lb_words)))

    REPS = 80
    # baseline (favourable-but-honest) context for the MAIN surface
    BASE = dict(coverage=0.55, f_wrong=0.0, site_coverage=1.0, clone_extra=0)

    results = {"seed": SEED, "reps": REPS, "engine": "grid-identifiability (union-find propagation)"}

    # ---- MAIN SURFACE: n_anchors x slots x lineages on opaque LB ----
    print("[G] main surface (opaque LB): n_anchors x slots x lineages ...")
    N_ANCHORS = [0,1,2,3,4,5,6,8,10]
    SLOTS     = [1,2,4,8]
    LINEAGES  = [1,2,3,5]
    surface = []
    for na in N_ANCHORS:
        for sl in SLOTS:
            for ln in LINEAGES:
                p = dict(n_anchors=na, slots=sl, lineages=ln, **BASE)
                agg = aggregate(lb_signs, p, REPS, SEED, held_words=lb_held, anchor_corpus=lb_words)
                surface.append({"n_anchors":na,"slots":sl,"lineages":ln, **{k:round(v,4) for k,v in agg.items()}})
    results["surface_opaque_LB"] = surface

    # extended sweep beyond the prescribed grid, to LOCATE the abs>=0.90 frontier if it lies
    # outside n_anchors<=10 / lineages<=5 (lineages = n_anchors: every anchor independent)
    print("[G] extended surface (locating the abs>=0.90 frontier) ...")
    surface_ext = []
    for na in [12,14,16,18,22,26]:
        for sl2 in [2,4,8]:
            p = dict(n_anchors=na, slots=sl2, lineages=na, **BASE)
            agg = aggregate(lb_signs, p, REPS, SEED, held_words=lb_held, anchor_corpus=lb_words)
            surface_ext.append({"n_anchors":na,"slots":sl2,"lineages":na, **{k:round(v,4) for k,v in agg.items()}})
    results["surface_extended_LB"] = surface_ext

    # minimum config for ABSOLUTE-value recovery (abs>=0.90 AND fp<=0.05)
    def min_config(surf, abs_thr=0.90, fp_thr=0.05):
        ok = [r for r in surf if r["abs_recovery"]>=abs_thr and r["fp_rate"]<=fp_thr]
        if not ok: return None
        # rank by (n_anchors, slots, lineages) cost
        ok.sort(key=lambda r:(r["n_anchors"], r["slots"], r.get("lineages", r["n_anchors"])))
        return ok[0]
    results["min_config_abs90_LB"] = min_config(surface + surface_ext)
    results["min_config_abs75_LB"] = min_config(surface + surface_ext, abs_thr=0.75, fp_thr=0.10)
    results["min_config_abs50_LB"] = min_config(surface + surface_ext, abs_thr=0.50, fp_thr=0.10)

    # ---- 1-D sensitivity sweeps (opaque LB), holding a powered anchor set ----
    print("[G] sensitivity sweeps ...")
    POW = dict(n_anchors=5, slots=4, lineages=5)  # a nominally-powered set
    sens = {}
    sens["coverage"] = [{"coverage":c, **{k:round(v,4) for k,v in
        aggregate(lb_signs, dict(POW, coverage=c, f_wrong=0.0, site_coverage=1.0, clone_extra=0), REPS, SEED, lb_held, anchor_corpus=lb_words).items()}}
        for c in [0.1,0.2,0.3,0.4,0.55,0.7,0.85,1.0]]
    sens["incorrect_fraction"] = [{"f_wrong":f, **{k:round(v,4) for k,v in
        aggregate(lb_signs, dict(POW, coverage=0.55, f_wrong=f, site_coverage=1.0, clone_extra=0), REPS, SEED, lb_held, anchor_corpus=lb_words).items()}}
        for f in [0.0,0.1,0.2,0.3,0.5]]
    sens["site_coverage"] = [{"site_coverage":sc, **{k:round(v,4) for k,v in
        aggregate(lb_signs, dict(POW, coverage=0.55, f_wrong=0.0, site_coverage=sc, clone_extra=0), REPS, SEED, lb_held, anchor_corpus=lb_words).items()}}
        for sc in [0.2,0.4,0.6,0.8,1.0]]
    sens["dependency_clones"] = [{"clone_extra":ce, "n_anchors":2, "lineages":2, **{k:round(v,4) for k,v in
        aggregate(lb_signs, dict(n_anchors=2, slots=4, lineages=2, coverage=0.55, f_wrong=0.0, site_coverage=1.0, clone_extra=ce), REPS, SEED, lb_held, anchor_corpus=lb_words).items()}}
        for ce in [0,2,4,8]]
    results["sensitivity_opaque_LB"] = sens

    # morphology recovery vs coverage
    results["morphology_recovery_LB"] = [{"coverage":c, "morph_pair_recovery":round(morphology_recovery(lb_signs,c,REPS,SEED),4)}
                                         for c in [0.1,0.2,0.3,0.55,0.85,1.0]]

    # ---- BENCHES: degraded-LB, synth syllabary, synth admin, wrong-language ----
    print("[G] alternate benches ...")
    benches = {}

    # degraded-LB matched to LA: LA-observed relative coverage ~ subst 32/131 + morph 22/131
    # -> effective value-free coverage ~0.20; LA words are short so max reliable slots ~2.
    la_cov = 0.20
    deg = []
    for na in [0,1,2,3,4,5,10]:
        for sl in [1,2]:
            p = dict(n_anchors=na, slots=sl, lineages=min(na, 5), coverage=la_cov, f_wrong=0.0, site_coverage=1.0, clone_extra=0)
            agg = aggregate(lb_signs, p, REPS, SEED, lb_held, anchor_corpus=lb_words)
            deg.append({"n_anchors":na,"slots":sl, **{k:round(v,4) for k,v in agg.items()}})
    benches["degraded_LB_LA_matched"] = {"coverage":la_cov, "grid":len(lb_signs), "rows":deg}

    # synthetic syllabaries: clean identifiability
    for tag, (nC,nV) in [("synth_15x5",(15,5)), ("synth_8x5",(8,5))]:
        g = synth_grid(nC, nV, fill=0.95, rng=random.Random(SEED+nC))
        hw = zipf_words(g, 3000, random.Random(SEED+1), maxlen=5)
        hw = random.Random(SEED).sample(hw, 300)
        rows = []
        for na in [0,1,2,3,4,5,6,8]:
            for sl in [1,4,8]:
                p = dict(n_anchors=na, slots=sl, lineages=na, coverage=0.55, f_wrong=0.0, site_coverage=1.0, clone_extra=0)
                agg = aggregate(g, p, REPS, SEED, hw)
                rows.append({"n_anchors":na,"slots":sl, **{k:round(v,4) for k,v in agg.items()}})
        benches[tag] = {"grid":len(g), "dims":f"{nC}x{nV}", "min_config_abs90":min_config(rows), "rows":rows}

    # synthetic admin: Zipf + formula, tail-dark. Coverage concentrated on high-freq signs;
    # anchors drawn from the Zipf corpus itself (frequency-biased, as real toponyms are).
    g_adm = synth_grid(15, 5, fill=0.95, rng=random.Random(SEED+55))
    adm_words = zipf_words(g_adm, 4000, random.Random(SEED+2))
    adm_hw = random.Random(SEED).sample(adm_words, 300)
    adm = []
    # admin coverage is skewed: model as low overall coverage (tail dark)
    for na in [0,2,3,4,5,8]:
        for cov in [0.15, 0.35]:
            p = dict(n_anchors=na, slots=4, lineages=na, coverage=cov, f_wrong=0.05, site_coverage=1.0, clone_extra=0)
            agg = aggregate(g_adm, p, REPS, SEED, adm_hw, anchor_corpus=adm_words)
            adm.append({"n_anchors":na,"coverage":cov, **{k:round(v,4) for k,v in agg.items()}})
    benches["synth_admin_tail_dark"] = {"grid":len(g_adm), "rows":adm}

    # wrong-language: model misspecification. Grid assumption FALSE -> relative edges cross true
    # classes (mislabel high). Anchors + assumed grid mostly generate FALSE POSITIVES.
    wl = []
    for na in [0,2,4,6,8]:
        p = dict(n_anchors=na, slots=4, lineages=na, coverage=0.4, f_wrong=0.0, site_coverage=1.0, clone_extra=0)
        agg = aggregate(lb_signs, p, REPS, SEED, lb_held, mislabel=0.8, anchor_corpus=lb_words)
        wl.append({"n_anchors":na, **{k:round(v,4) for k,v in agg.items()}})
    benches["wrong_language_misspecified"] = {"note":"CV-grid assumption false; relative edges cross true classes (mislabel=0.8)", "rows":wl}

    results["benches"] = benches

    # ---- LINEAR A OPERATING POINT ----
    print("[G] Linear A operating point ...")
    # Dependency-collapsed truth (Art. XI, from C-lattice + do_not_repeat): 0 independent anchors,
    # 1 value-bearing meta-lineage, pins are 1-slot (one-toponym-deep), value-free coverage ~0.20.
    la_points = {}
    # (a) honest collapsed point
    p_collapsed = dict(n_anchors=0, slots=1, lineages=1, coverage=0.20, f_wrong=0.0, site_coverage=0.4, clone_extra=0)
    la_points["collapsed_SEED_A_0"] = {"params":p_collapsed,
        **{k:round(v,4) for k,v in aggregate(lb_signs, p_collapsed, 200, SEED, lb_held, anchor_corpus=lb_words).items()}}
    # (b) the 3 one-toponym-deep pins (*49,*79,ZU) taken at face value: 1 meta-lineage, 1-slot,
    #     uncalibrated identification (EA-13-like short-skeleton FP ~0.25 per pin)
    p_pins = dict(n_anchors=3, slots=1, lineages=1, coverage=0.20, f_wrong=0.25, site_coverage=0.4, clone_extra=2)
    la_points["three_pins_1lineage_1slot"] = {"params":p_pins,
        **{k:round(v,4) for k,v in aggregate(lb_signs, p_pins, 200, SEED, lb_held, anchor_corpus=lb_words).items()}}
    # (c) OPTIMISTIC/inflated: pretend all 26 "multi-channel" signs are independent (ignore Art.XI collapse)
    p_infl = dict(n_anchors=10, slots=2, lineages=5, coverage=0.20, f_wrong=0.0, site_coverage=0.6, clone_extra=16)
    la_points["inflated_26_ignore_collapse"] = {"params":p_infl,
        **{k:round(v,4) for k,v in aggregate(lb_signs, p_infl, 200, SEED, lb_held, anchor_corpus=lb_words).items()}}
    results["linear_A_operating_point"] = la_points

    # ---- EA-13 comparison point ----
    # EA-13 best_config: n_anchors 4, La(=slots) 4 -> FP 0.043 powered; La>=4 threshold.
    # Bridge: EA-13's FP_frozen is a PER-ANCHOR wrong-identification rate at skeleton length La
    # (chance skeleton matches). We map it onto f_wrong so the downstream lattice cost of a
    # short-skeleton anchor set is measured, not assumed:
    #   La=3 -> f_wrong 0.25 (EA-13 FP_frozen 0.24-0.26)
    #   La=4 -> f_wrong 0.043 ; La=5 -> f_wrong 0.075 (EA-13 measured envelope)
    EA13_FP = {3: 0.25, 4: 0.043, 5: 0.075}
    ea13 = {}
    for (na, sl, tag) in [(4,4,"EA13_best_La4"),(4,3,"EA13_La3_underpowered"),
                          (3,4,"EA13_n3_La4"),(4,5,"EA13_La5")]:
        p = dict(n_anchors=na, slots=sl, lineages=na, coverage=0.55,
                 f_wrong=EA13_FP[sl], site_coverage=1.0, clone_extra=0)
        ea13[tag] = {"n_anchors":na,"slots":sl,"f_wrong_from_EA13_FP_frozen":EA13_FP[sl],
            **{k:round(v,4) for k,v in aggregate(lb_signs, p, REPS, SEED, lb_held, anchor_corpus=lb_words).items()}}
    # idealised (f_wrong=0) twins, to separate the propagation axis from the identification axis
    for (na, sl, tag) in [(4,4,"IDEAL_n4_slots4_f0"),(4,3,"IDEAL_n4_slots3_f0")]:
        p = dict(n_anchors=na, slots=sl, lineages=na, coverage=0.55, f_wrong=0.0,
                 site_coverage=1.0, clone_extra=0)
        ea13[tag] = {"n_anchors":na,"slots":sl,"f_wrong_from_EA13_FP_frozen":0.0,
            **{k:round(v,4) for k,v in aggregate(lb_signs, p, REPS, SEED, lb_held, anchor_corpus=lb_words).items()}}
    results["ea13_comparison_points"] = ea13

    with open(os.path.join(OUT, "surface.json"), "w") as f:
        json.dump(results, f, indent=1)
    print(f"[G] wrote {os.path.join(OUT,'surface.json')}")
    # CSV of the main surface for downstream WPs
    with open(os.path.join(OUT, "surface_opaque_LB.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(surface[0].keys()))
        w.writeheader(); w.writerows(surface)
    print(f"[G] wrote {os.path.join(OUT,'surface_opaque_LB.csv')}")

    # compact console summary
    mc = results["min_config_abs90_LB"]
    print("\n=== SUMMARY ===")
    print("min config abs>=0.90 fp<=0.05 (opaque LB):", mc)
    print("LA collapsed point:", la_points["collapsed_SEED_A_0"]["abs_recovery"], "abs;",
          la_points["collapsed_SEED_A_0"]["eq_reduction"], "eqred")
    print("LA inflated point:", la_points["inflated_26_ignore_collapse"]["abs_recovery"], "abs")
    print("EA13 best (n4,La4):", ea13["EA13_best_La4"]["abs_recovery"], "abs;", ea13["EA13_best_La4"]["fp_rate"], "fp")
    return results

if __name__ == "__main__":
    main()
