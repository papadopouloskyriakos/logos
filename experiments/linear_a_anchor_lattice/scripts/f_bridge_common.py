#!/usr/bin/env python3
"""TASK F — shared corpus loaders + substitution-neighborhood machinery for the
cross-script SUBSTITUTION-AXIS bridge.

NON-CIRCULAR CONTRACT (Art. XI/XII):
  * Every substitution graph / neighborhood representation is built from sign IDENTITY,
    co-occurrence, and minimal-frame membership ONLY — never from a phonetic value.
  * Known LB / Cypriot / GORILA values are read AFTERWARD to GRADE an alignment
    (ground truth + relative-class labels). They are NEVER a model input, and the
    alignment methods operate on OPAQUE per-script node IDs (LA_/LB_/CY_ prefixed) so
    the shared transcription label can never leak into the geometry.
  * A relative-class reduction earns NO absolute value (Art. XV). F4 emits relative
    compatibility + equivalence classes + uncertainty only.

Seed 20260708. stdlib + numpy/scipy only.
"""
from __future__ import annotations
import json, math, os, re, sys, unicodedata
from collections import Counter, defaultdict
from itertools import combinations

SEED = 20260708
VOW = set("AEIOU")
LOGOS = "/home/claude-runner/gitlab/n8n/logos"
sys.path.insert(0, LOGOS)

HERE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.dirname(HERE)
DATA = os.path.join(CAMP, "data", "substitution_bridge")
os.makedirs(DATA, exist_ok=True)

SILVER = os.path.join(LOGOS, "corpus", "silver")
COG_DIR = os.path.join(LOGOS, "corpus", "bronze", "code", "CSA_OptMatcher", "data")

_SUB = {"₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4",
        "₅": "5", "₆": "6", "₇": "7", "₈": "8", "₉": "9"}


def norm(s: str) -> str:
    return "".join(_SUB.get(c, c) for c in s)


# ---------------------------------------------------------------- value parse (GRADE ONLY)
def parse_cv(v):
    v = norm(v)
    if v.startswith("*"):
        return None
    if v in VOW:
        return ("", v)
    if len(v) >= 2 and v[-1] in VOW and v[:-1].isalpha():
        return (v[:-1], v[-1])
    if len(v) >= 2 and v[-1].isdigit():
        core = v[:-1]
        if core in VOW:
            return ("", core)
        if len(core) >= 2 and core[-1] in VOW and core[:-1].isalpha():
            return (core[:-1], core[-1])
    return None


def core_value(v):
    v = norm(v)
    if v.startswith("*"):
        return v
    return re.sub(r"\d+$", "", v)


def relation(a, b):
    """GRADE-ONLY relation between two known values (same_consonant / same_vowel /
    spelling_variant / cross). Used to label ground-truth classes, never as model input."""
    pa, pb = parse_cv(a), parse_cv(b)
    if pa is None or pb is None:
        return None
    if core_value(a) == core_value(b):
        return "spelling_variant"
    (ca, va), (cb, vb) = pa, pb
    if va == vb:
        return "same_vowel"
    if ca and cb and ca == cb:
        return "same_consonant"
    return "cross"


# ---------------------------------------------------------------- corpus loaders
def load_la_words():
    """Linear A silver: ordered sign sequences per word (t=='word' stream)."""
    d = json.load(open(os.path.join(SILVER, "inscriptions_structured.json")))
    seqs, doc_words = [], defaultdict(list)
    for ins in d:
        did = ins.get("id")
        for ev in ins.get("stream", []):
            if ev.get("t") == "word":
                w = tuple(norm(s) for s in ev["signs"])
                if w:
                    seqs.append(w)
                    doc_words[did].append(w)
    return seqs, doc_words


def load_lb_damos():
    """Linear B DĀMOS wordform streams + per-doc site/series meta (for holdouts)."""
    from scripts.cross_script import data as X
    DAMOS = os.path.join(LOGOS, "corpus", "bronze", "linearb", "damos", "items.jsonl")
    seqs, doc_words, doc_meta = [], defaultdict(list), {}
    with open(DAMOS, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            it = rec.get("item", {}) or {}
            did = rec.get("_id")
            doc_meta[did] = {"site": it.get("ishort"),
                             "series": it.get("seriessicura") or it.get("series")}
            for w in X._damos_wordforms(it.get("content", "") or ""):
                w = tuple(norm(x) for x in w)
                if w:
                    seqs.append(w)
                    doc_words[did].append(w)
    return seqs, doc_words, doc_meta


def _cyval(ch):
    try:
        n = unicodedata.name(ch)
    except ValueError:
        return None
    return n.replace("CYPRIOT SYLLABLE ", "").replace(" ", "") \
        if n.startswith("CYPRIOT SYLLABLE ") else None


def load_cog_col(fname, col, decoder):
    """Decode one column of a .cog cognate list into value tuples (only fully-decodable words)."""
    seqs = []
    with open(os.path.join(COG_DIR, fname), encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 2:
                continue
            w = parts[col].split("|")[0]
            vals = [decoder(c) for c in w]
            if vals and all(v is not None for v in vals):
                seqs.append(tuple(norm(v) for v in vals))
    return seqs


def load_cyp_cog():
    return load_cog_col("csyl-greek.cog", 0, _cyval)


def load_lb_cog():
    from scripts.cross_script.data import _b_value_from_codepoint
    return load_cog_col("linear_b-greek.cog", 0, _b_value_from_codepoint)


# ---------------------------------------------------------------- substitution neighborhoods
def build_frames(seqs, long_only=False):
    slots = defaultdict(set)
    for t in set(seqs):
        L = len(t)
        if L < 2 or (long_only and L < 3):
            continue
        for p in range(L):
            ctx = t[:p] + ("\x00",) + t[p + 1:]
            slots[(L, p, ctx)].add(t[p])
    return slots


def edge_weights(slots):
    ew = Counter()
    for fills in slots.values():
        if len(fills) < 2:
            continue
        for a, b in combinations(sorted(fills), 2):
            ew[frozenset((a, b))] += 1
    return ew


def cofill_sets(slots):
    fset = defaultdict(set)
    for key, fills in slots.items():
        if len(fills) < 2:
            continue
        for s in fills:
            fset[s].add(key)
    return fset


def neighbour_vectors(seqs):
    """Adjacency (prev/next) bag-of-context vectors per sign, over word TYPES."""
    vec = defaultdict(Counter)
    for t in set(seqs):
        for k in range(len(t)):
            s = t[k]
            if k > 0:
                vec[s][("<", t[k - 1])] += 1
            if k + 1 < len(t):
                vec[s][(">", t[k + 1])] += 1
    norm_ = {s: math.sqrt(sum(v * v for v in c.values())) for s, c in vec.items()}
    return vec, norm_


def sign_support(seqs):
    """#word-types each sign occurs in (support for filtering)."""
    sup = Counter()
    for t in set(seqs):
        for s in set(t):
            sup[s] += 1
    return sup


def similarity_matrix(seqs, signs, kind="jaccard"):
    """Build an intra-script sign x sign SIMILARITY matrix over `signs` (opaque order),
    from IDENTITY-only substitution structure. kind in {jaccard, cosine, subst}."""
    import numpy as np
    slots = build_frames(seqs)
    idx = {s: i for i, s in enumerate(signs)}
    n = len(signs)
    S = np.zeros((n, n))
    if kind == "jaccard":
        fset = cofill_sets(slots)
        for i, a in enumerate(signs):
            fa = fset.get(a, set())
            for j in range(i + 1, n):
                fb = fset.get(signs[j], set())
                u = len(fa | fb)
                v = len(fa & fb) / u if u else 0.0
                S[i, j] = S[j, i] = v
    elif kind == "cosine":
        vec, nrm = neighbour_vectors(seqs)
        for i, a in enumerate(signs):
            ca = vec.get(a, {})
            na = nrm.get(a, 0.0)
            for j in range(i + 1, n):
                cb = vec.get(signs[j], {})
                nb = nrm.get(signs[j], 0.0)
                if na == 0 or nb == 0:
                    continue
                small, big = (ca, cb) if len(ca) <= len(cb) else (cb, ca)
                dot = sum(v * big.get(k, 0) for k, v in small.items())
                S[i, j] = S[j, i] = dot / (na * nb)
    elif kind == "subst":
        ew = edge_weights(slots)
        for e, w in ew.items():
            a, b = tuple(e)
            if a in idx and b in idx:
                S[idx[a], idx[b]] = S[idx[b], idx[a]] = w
        mx = S.max() or 1.0
        S = S / mx
    return S


# ---------------------------------------------------------------- small stats
def auc(pos, neg):
    if not pos or not neg:
        return None
    import bisect
    ns = sorted(neg)
    m = len(neg)
    tot = 0.0
    for s in pos:
        lo = bisect.bisect_left(ns, s)
        hi = bisect.bisect_right(ns, s)
        tot += lo + 0.5 * (hi - lo)
    return tot / (len(pos) * m)


def dump(name, obj):
    p = os.path.join(DATA, name)
    json.dump(obj, open(p, "w"), indent=1, default=float)
    return p


if __name__ == "__main__":
    la, _ = load_la_words()
    lb, _, _ = load_lb_damos()
    cyp = load_cyp_cog()
    lbc = load_lb_cog()
    print("LA words", len(la), "distinct", len(sign_support(la)))
    print("LB damos", len(lb), "distinct", len(sign_support(lb)))
    print("Cyp cog", len(cyp), "distinct", len(sign_support(cyp)))
    print("LB cog", len(lbc), "distinct", len(sign_support(lbc)))
