#!/usr/bin/env python3
"""EPOCH-002 — higher-order substitution-motif similarity builders + grading.

Preregistered: epochs/EPOCH-002/prereg.md
plan_hash 09c55c9e42406393d278299569007d085e1bc9c558ca388ca4715f76b34cadae

NON-CIRCULAR (Art. XI/XII): every similarity is built from sign IDENTITY, word co-occurrence
and document series/site membership ONLY. Known values are read AFTERWARD to GRADE.
Seed 20260708.
"""
from __future__ import annotations
import json, os, random, sys
from collections import Counter, defaultdict
from itertools import combinations

import numpy as np

SEED = 20260708
ANCHOR_SCRIPTS = "/home/claude-runner/gitlab/n8n/logos-linear-a-frontier-72h/experiments/linear_a_anchor_lattice/scripts"
sys.path.insert(0, ANCHOR_SCRIPTS)
import f_bridge_common as C  # noqa: E402  (read-only reuse of the calibrated F machinery)

CAMP = "/home/claude-runner/gitlab/n8n/logos-linear-a-frontier-72h/experiments/linear_a_frontier_72h"
DATA = os.path.join(CAMP, "data", "motifs")
os.makedirs(DATA, exist_ok=True)

PLAN_HASH = "09c55c9e42406393d278299569007d085e1bc9c558ca388ca4715f76b34cadae"


# ------------------------------------------------------------------ incidence builders
# Each motif family is expressed as a sign -> set(frame_key) incidence map; similarity is
# Jaccard over frame sets (MF_A, MF_B) or a per-site mean Jaccard (MF_C).

def inc_flat(seqs, doc_words=None, doc_meta=None):
    """FLAT baseline: corpus-wide whole-word one-slot frames (identical to
    f_bridge_common cofill sets; kept here so the degree-preserving null can treat all
    families uniformly)."""
    slots = C.build_frames(seqs)
    return _multi_fill_only(slots)


def inc_trigram(seqs, doc_words=None, doc_meta=None):
    """MF_A: joint (prev,next) 2-sign frames with boundary padding, word TYPES, L>=2."""
    slots = defaultdict(set)
    for t in set(seqs):
        L = len(t)
        if L < 2:
            continue
        for p in range(L):
            left = t[p - 1] if p > 0 else "^"
            right = t[p + 1] if p + 1 < L else "$"
            slots[(left, right)].add(t[p])
    return _multi_fill_only(slots)


def inc_formula(seqs, doc_words, doc_meta):
    """MF_B: whole-word one-slot frames keyed additionally by SERIES; fills = word types
    attested in docs of that series."""
    series_words = defaultdict(set)
    for did, ws in doc_words.items():
        ser = (doc_meta.get(did) or {}).get("series") or "NA"
        for w in ws:
            series_words[ser].add(w)
    slots = defaultdict(set)
    for ser, types in series_words.items():
        for t in types:
            L = len(t)
            if L < 2:
                continue
            for p in range(L):
                ctx = t[:p] + ("\x00",) + t[p + 1:]
                slots[(ser, L, p, ctx)].add(t[p])
    return _multi_fill_only(slots)


def site_slotmaps(doc_words, doc_meta):
    """MF_C helper: per-site whole-word one-slot frame -> fills."""
    site_words = defaultdict(set)
    for did, ws in doc_words.items():
        site = (doc_meta.get(did) or {}).get("site") or "NA"
        for w in ws:
            site_words[site].add(w)
    out = {}
    for site, types in site_words.items():
        slots = defaultdict(set)
        for t in types:
            L = len(t)
            if L < 2:
                continue
            for p in range(L):
                ctx = t[:p] + ("\x00",) + t[p + 1:]
                slots[(L, p, ctx)].add(t[p])
        mf = _multi_fill_only(slots)
        if mf:
            out[site] = mf
    return out


def _multi_fill_only(slots):
    """Keep frames with >=2 fills; return sign -> set(frame_key)."""
    fset = defaultdict(set)
    for key, fills in slots.items():
        if len(fills) < 2:
            continue
        for s in fills:
            fset[s].add(key)
    return dict(fset)


# ------------------------------------------------------------------ similarity from incidence
def jaccard_lookup(fset):
    def look(a, b):
        fa, fb = fset.get(a, set()), fset.get(b, set())
        u = len(fa | fb)
        return len(fa & fb) / u if u else 0.0
    return look


def site_mean_lookup(per_site_fsets):
    """MF_C: mean per-site Jaccard over sites where BOTH signs occupy >=1 multi-fill frame."""
    def look(a, b):
        vals = []
        for fset in per_site_fsets.values():
            fa, fb = fset.get(a), fset.get(b)
            if not fa or not fb:
                continue
            u = len(fa | fb)
            vals.append(len(fa & fb) / u if u else 0.0)
        return float(np.mean(vals)) if vals else 0.0
    return look


def site_replication_count(per_site_fsets, a, b):
    n = 0
    for fset in per_site_fsets.values():
        fa, fb = fset.get(a), fset.get(b)
        if fa and fb and (fa & fb):
            n += 1
    return n


# ------------------------------------------------------------------ pair table + AUC machinery
def scorable_signs(seqs):
    sup = C.sign_support(seqs)
    return sorted(s for s in sup if C.parse_cv(s) is not None and sup[s] >= 2)


def pair_relations(signs):
    rel = {}
    for a, b in combinations(signs, 2):
        r = C.relation(a, b)
        if r:
            rel[frozenset((a, b))] = r
    return rel


def pair_table(look, signs, rel):
    """Precompute (a, b, relation, sim) rows once; AUC/bootstrap re-aggregate from this."""
    rows = []
    for e, r in rel.items():
        a, b = tuple(e)
        rows.append((a, b, r, look(a, b)))
    return rows


def auc_from_rows(rows, cls, restrict=None):
    pos, neg = [], []
    for a, b, r, s in rows:
        if restrict is not None and frozenset((a, b)) not in restrict:
            continue
        if r == cls:
            pos.append(s)
        elif r == "cross":
            neg.append(s)
    return C.auc(pos, neg), len(pos), len(neg)


def freq_bands(seqs, signs, nb=4):
    sup = C.sign_support(seqs)
    order = sorted(signs, key=lambda s: sup[s])
    return {s: min(nb - 1, i * nb // len(order)) for i, s in enumerate(order)}


def within_band_pairs(rel, band):
    return {e for e in rel if band[tuple(e)[0]] == band[tuple(e)[1]]}


# ------------------------------------------------------------------ nulls
def label_null_freq_matched(rows_by_sign_lookup, signs, band, rel_builder, cls, obs,
                            restrict=None, n=1000, seed=SEED):
    """Frequency-matched label null: permute the sign->value map WITHIN band; regrade the
    SAME similarity rows. rows_by_sign_lookup: dict frozenset(pair)->sim."""
    rng = random.Random(seed)
    by_band = defaultdict(list)
    for s in signs:
        by_band[band[s]].append(s)
    null = []
    pairs = list(rows_by_sign_lookup)
    for _ in range(n):
        relabel = {}
        for b, group in by_band.items():
            perm = group[:]
            rng.shuffle(perm)
            relabel.update(dict(zip(group, perm)))
        pos, neg = [], []
        for e in pairs:
            if restrict is not None and e not in restrict:
                continue
            a, b_ = tuple(e)
            r = C.relation(relabel[a], relabel[b_])
            if r == cls:
                pos.append(rows_by_sign_lookup[e])
            elif r == "cross":
                neg.append(rows_by_sign_lookup[e])
        a_ = C.auc(pos, neg)
        if a_ is not None:
            null.append(a_)
    null.sort()
    ge = sum(1 for x in null if x >= obs)
    return {"obs": obs, "n_null": len(null), "null_mean": float(np.mean(null)),
            "null_p95": float(np.quantile(null, 0.95)),
            "p_one_sided": (ge + 1) / (len(null) + 1)}


def degree_preserving_null(fset, signs, rel, cls, restrict=None, n=200, seed=SEED):
    """Bipartite configuration null: permute sign labels on the (sign,frame) incidence list —
    preserves each sign's frame count and each frame's fill count."""
    rng = random.Random(seed)
    incid = [(s, f) for s, fs in fset.items() for f in fs]
    sign_col = [s for s, _ in incid]
    frame_col = [f for _, f in incid]
    look = jaccard_lookup(fset)
    rows = pair_table(look, signs, rel)
    obs, _, _ = auc_from_rows(rows, cls, restrict)
    null = []
    for _ in range(n):
        perm = sign_col[:]
        rng.shuffle(perm)
        f2 = defaultdict(set)
        for s, f in zip(perm, frame_col):
            f2[s].add(f)
        rows2 = pair_table(jaccard_lookup(f2), signs, rel)
        a_, _, _ = auc_from_rows(rows2, cls, restrict)
        if a_ is not None:
            null.append(a_)
    null.sort()
    ge = sum(1 for x in null if x >= obs)
    return {"obs": obs, "n_null": len(null), "null_mean": float(np.mean(null)),
            "null_p95": float(np.quantile(null, 0.95)),
            "p_one_sided": (ge + 1) / (len(null) + 1)}


def shuffle_within_words(seqs, seed=SEED):
    rng = random.Random(seed)
    out = []
    for t in seqs:
        w = list(t)
        rng.shuffle(w)
        out.append(tuple(w))
    return out


def shuffle_doc_words(doc_words, seed=SEED):
    rng = random.Random(seed)
    out = {}
    for did, ws in doc_words.items():
        nws = []
        for t in ws:
            w = list(t)
            rng.shuffle(w)
            nws.append(tuple(w))
        out[did] = nws
    return out


# ------------------------------------------------------------------ paired sign bootstrap
def sign_bootstrap_delta(look_m, look_f, signs, n=1000, seed=SEED, restrict_band=None):
    """Resample SIGNS with replacement; pairs = index combinations excluding same-sign pairs;
    Δ = AUC_motif - AUC_flat on the identical resample. restrict_band: dict sign->band, only
    within-band pairs graded (freq-disjoint regime)."""
    rng = random.Random(seed)
    m = len(signs)
    simcache_m, simcache_f, relcache = {}, {}, {}

    def get(a, b):
        e = (a, b) if a < b else (b, a)
        if e not in relcache:
            relcache[e] = C.relation(a, b)
            simcache_m[e] = look_m(a, b)
            simcache_f[e] = look_f(a, b)
        return relcache[e], simcache_m[e], simcache_f[e]

    deltas = []
    for _ in range(n):
        sample = [signs[rng.randrange(m)] for _ in range(m)]
        pm, nm, pf, nf = [], [], [], []
        for i, j in combinations(range(m), 2):
            a, b = sample[i], sample[j]
            if a == b:
                continue
            if restrict_band is not None and restrict_band[a] != restrict_band[b]:
                continue
            r, sm, sf = get(a, b)
            if r == "same_consonant":
                pm.append(sm)
                pf.append(sf)
            elif r == "cross":
                nm.append(sm)
                nf.append(sf)
        am, af = C.auc(pm, nm), C.auc(pf, nf)
        if am is not None and af is not None:
            deltas.append(am - af)
    deltas = np.array(deltas)
    return {"n_boot": len(deltas), "delta_mean": float(deltas.mean()),
            "ci95": [float(np.quantile(deltas, 0.025)), float(np.quantile(deltas, 0.975))],
            "frac_gt0": float((deltas > 0).mean())}


def holm(pairs):
    order = sorted(pairs, key=lambda x: x[1])
    m = len(order)
    adj, running = {}, 0.0
    for rank, (lab, p) in enumerate(order):
        running = max(running, (m - rank) * p)
        adj[lab] = min(1.0, running)
    return adj


def dump(name, obj):
    p = os.path.join(DATA, name)
    json.dump(obj, open(p, "w"), indent=1, default=float)
    return p
