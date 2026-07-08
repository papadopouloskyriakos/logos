#!/usr/bin/env python3
"""EPOCH-007 — ledger-role induction as anchor constraints.

Prereg: epochs/EPOCH-007/prereg.md
plan_hash 6c85277da7c4e5d30abdd12bca084db4076c4f12e334225f5a5c535dfc2be566 (frozen 2026-07-08T04:13:24Z)

Blind structural role induction on ledger documents:
  parse -> structural features (NO sign values, NO editorial case) -> kmeans k=5 ->
  many-to-one decode on LB derivation (KN) -> grade held-out (non-KN) -> nulls ->
  (if fires) transfer to LA, consistency checks + new constraints.

Everything mechanical; seed 20260708.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.dirname(HERE)
WORKTREE = os.path.dirname(os.path.dirname(CAMP))
DAMOS = os.path.join(WORKTREE, "corpus", "bronze", "linearb", "damos", "items.jsonl")
LA_STRUCT = os.path.join(WORKTREE, "corpus", "silver", "inscriptions_structured.json")
OUTDIR = os.path.join(CAMP, "data", "ledger_roles")
SEED = 20260708

GOLD_CLASSES = ["W", "C", "U", "T"]
UNITS = {"S", "V", "T", "Z", "M", "N", "L", "P", "Q"}
LA_LOGO_BASES = {"GRA", "VIN", "CYP", "OLIV", "OLE", "VIR", "FIC", "TELA",
                 "BOS", "SUS", "CAP", "OVIS", "AU"}

_SUB = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")

# ---------------------------------------------------------------- tokens/docs

@dataclass
class Tok:
    kind: str            # 'G' group | 'N' num
    raw: str = ""        # cleaned surface (used ONLY for gold grading + blind hash)
    n_signs: int = 0
    num: float = 0.0
    bid: str = ""        # blind id (sha1 of casefolded raw)

@dataclass
class Doc:
    doc_id: str
    site: str
    lines: list = field(default_factory=list)   # list[list[Tok]]

    def groups(self):
        for li, line in enumerate(self.lines):
            for ti, t in enumerate(line):
                if t.kind == "G":
                    yield li, ti, t


def _blind(tok: str) -> str:
    return hashlib.sha1(tok.casefold().encode()).hexdigest()[:12]


# ------------------------------------------------------------------ LB parse

_LINE_LABEL = re.compile(r"^(?:[a-zA-Z]{0,3}\.)?\.?[0-9]+[a-zA-Z]?$|^\.[A-Za-z]$")
_DROP = re.compile(r"^(vac|vacat|deest|mut|sup|inf|vest|reliqua|angustum|prius|graffito|lat|dex|sin|verso|recto|supra|infra)\.?,?$",
                   re.IGNORECASE)
_NUM = re.compile(r"^[0-9]+$")


def _clean_lb_line(line: str) -> list[str]:
    line = re.sub(r"⟦[^⟧]*⟧", " ", line)
    line = line.translate(_SUB)
    line = re.sub(r"[\[\]\?<>'\"⌞⌟‹›]", "", line)
    line = line.replace(",", " ")
    out = []
    for tok in line.split():
        tok = tok.strip(".-")
        if not tok or tok in {"/", "|", "s", "ss"}:
            continue
        out.append(tok)
    return out


def parse_lb() -> list[Doc]:
    docs = []
    with open(DAMOS) as fh:
        for row in fh:
            it = json.loads(row)
            content = (it.get("item") or {}).get("content")
            if not content:
                continue
            heading = it.get("heading") or ""
            site = heading.split()[0] if heading else "?"
            d = Doc(doc_id=heading or str(it.get("_id")), site=site)
            for raw_line in content.split("\n"):
                toks = _clean_lb_line(raw_line)
                if toks and (_LINE_LABEL.match(toks[0]) or toks[0].startswith(".")):
                    toks = toks[1:]
                line = []
                for tok in toks:
                    if _DROP.match(tok):
                        continue
                    if _NUM.match(tok):
                        line.append(Tok("N", num=float(tok)))
                    else:
                        n_signs = len([p for p in tok.split("-") if p])
                        if n_signs == 0:
                            continue
                        line.append(Tok("G", raw=tok, n_signs=n_signs, bid=_blind(tok)))
                if line:
                    d.lines.append(line)
            if d.lines:
                docs.append(d)
    return docs


def gold_lb(tok: Tok) -> str:
    t = tok.raw
    cf = t.casefold()
    if "-" in t:
        if cf.startswith("to-so") or cf.startswith("to-sa"):
            return "T"
        return "W"
    if t in UNITS:
        return "U"
    if re.search(r"[A-Z]", t) or t.startswith("*"):
        return "C"
    return "W"


def gold_lb_secondary_D(tok: Tok) -> bool:
    cf = tok.raw.casefold()
    return cf.startswith("o-pe-ro") or cf == "o"


# ------------------------------------------------------------------ LA parse

def parse_la() -> list[Doc]:
    data = json.load(open(LA_STRUCT))
    seen = {}
    for x in data:
        seen.setdefault(x["id"], x)
    docs = []
    for x in seen.values():
        d = Doc(doc_id=x["id"], site=x.get("site") or "?")
        cur = []
        for ev in x.get("stream", []):
            t = ev.get("t")
            if t == "word":
                signs = [s.translate(_SUB) for s in ev["signs"]]
                raw = "-".join(signs)
                cur.append(Tok("G", raw=raw, n_signs=len(signs), bid=_blind(raw)))
            elif t == "num":
                cur.append(Tok("N", num=float(ev["v"])))
            elif t == "nl":
                if cur:
                    d.lines.append(cur)
                cur = []
            # 'div' and 'other' (fractions) kept out of the token stream per prereg
        if cur:
            d.lines.append(cur)
        if d.lines:
            docs.append(d)
    return docs


# ------------------------------------------------------------------- filters

def ledger_filter(docs: list[Doc]) -> list[Doc]:
    keep = []
    for d in docs:
        toks = [t for line in d.lines for t in line]
        n_num = sum(1 for t in toks if t.kind == "N")
        n_grp = sum(1 for t in toks if t.kind == "G")
        if n_num >= 2 and n_grp >= 3 and len(d.lines) >= 2:
            keep.append(d)
    return keep


# ------------------------------------------------------------------ features

def type_stats(docs: list[Doc]) -> dict:
    df = Counter()
    li_n = Counter(); li_hit = Counter()
    fn_n = Counter(); fn_hit = Counter()
    n_docs = len(docs)
    for d in docs:
        seen_types = set()
        for li, ti, t in d.groups():
            seen_types.add(t.bid)
            line = d.lines[li]
            li_n[t.bid] += 1
            first_g = next(i for i, x in enumerate(line) if x.kind == "G")
            if ti == first_g:
                li_hit[t.bid] += 1
            fn_n[t.bid] += 1
            if ti + 1 < len(line) and line[ti + 1].kind == "N":
                fn_hit[t.bid] += 1
        for b in seen_types:
            df[b] += 1
    return {
        "df": {b: df[b] / n_docs for b in df},
        "li": {b: li_hit[b] / li_n[b] for b in li_n},
        "fn": {b: fn_hit[b] / fn_n[b] for b in fn_n},
    }


def featurize(docs: list[Doc], stats: dict):
    X, meta = [], []
    for d in docs:
        nums = [t.num for line in d.lines for t in line if t.kind == "N"]
        max_num = max(nums) if nums else 0.0
        content_lines = [i for i, line in enumerate(d.lines) if line]
        last_line = content_lines[-1]
        n_lines = len(d.lines)
        type_lines = defaultdict(set)
        for li, ti, t in d.groups():
            type_lines[t.bid].add(li)
        for li, ti, t in d.groups():
            line = d.lines[li]
            f_num = 0.0; v_num = 0.0
            if ti + 1 < len(line) and line[ti + 1].kind == "N":
                f_num = 1.0; v_num = line[ti + 1].num
            nxt = 0.0
            for j in range(ti + 1, len(line)):
                if line[j].kind == "N":
                    nxt = 1.0 / (1.0 + (j - ti - 1)); break
            first_g = next(i for i, x in enumerate(line) if x.kind == "G")
            X.append([
                min(t.n_signs, 6),
                f_num,
                math.log1p(v_num) if f_num else 0.0,
                (v_num / max_num) if (f_num and max_num > 0) else 0.0,
                ti / max(1, len(line) - 1),
                1.0 if ti == first_g else 0.0,
                li / max(1, n_lines - 1),
                1.0 if li == last_line else 0.0,
                min(len(type_lines[t.bid]), 5),
                stats["df"].get(t.bid, 0.0),
                stats["li"].get(t.bid, 0.0),
                stats["fn"].get(t.bid, 0.0),
                nxt,
                # DEV-1 (PC1 calibration, synthetic-only): preceding-token structure,
                # needed to separate unit-slot from commodity-slot. Logged as deviation.
                1.0 if (ti > 0 and line[ti - 1].kind == "G") else 0.0,
                min(line[ti - 1].n_signs, 6) if (ti > 0 and line[ti - 1].kind == "G") else 0.0,
            ])
            meta.append((d.doc_id, d.site, li, ti, t))
    return np.array(X, float), meta


# ------------------------------------------------------------------ pipeline

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


# DEV-2 (PC1 calibration, synthetic-only): k=5 could not allocate a unit-slot cluster
# (PC1 macro-F1 .69/.71, recall(U)=0); k sweep ON SYNTHETIC ONLY {6:.71, 8:.71, 10:.92,
# 12:1.00} -> k=12 frozen before touching any real-corpus label. Logged as deviation.
def fit_pipeline(deriv_docs: list[Doc], gold_fn, k: int = 12, seed: int = SEED):
    stats = type_stats(deriv_docs)
    X, meta = featurize(deriv_docs, stats)
    scaler = StandardScaler().fit(X)
    km = KMeans(n_clusters=k, n_init=50, random_state=seed).fit(scaler.transform(X))
    labels = km.labels_
    gold = [gold_fn(m[4]) for m in meta]
    mapping = {}
    for c in range(k):
        cnt = Counter(g for g, l in zip(gold, labels) if l == c)
        mapping[c] = cnt.most_common(1)[0][0] if cnt else "W"
    return {"scaler": scaler, "km": km, "mapping": mapping, "deriv_stats": stats}


def predict(model, docs: list[Doc], stats: dict):
    X, meta = featurize(docs, stats)
    cl = model["km"].predict(model["scaler"].transform(X))
    roles = [model["mapping"][c] for c in cl]
    return roles, meta, cl


def grade(roles, meta, gold_fn):
    gold = [gold_fn(m[4]) for m in meta]
    acc = float(np.mean([r == g for r, g in zip(roles, gold)]))
    per = {}
    f1s = []
    for cls in GOLD_CLASSES:
        tp = sum(1 for r, g in zip(roles, gold) if r == cls and g == cls)
        fp = sum(1 for r, g in zip(roles, gold) if r == cls and g != cls)
        fn = sum(1 for r, g in zip(roles, gold) if r != cls and g == cls)
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        per[cls] = {"n_gold": tp + fn, "precision": round(prec, 4),
                    "recall": round(rec, 4), "f1": round(f1, 4)}
        f1s.append(f1)
    return {"n": len(gold), "accuracy": round(acc, 4),
            "macro_f1": round(float(np.mean(f1s)), 4), "per_class": per,
            "gold_dist": dict(Counter(gold))}


# --------------------------------------------------------------------- nulls

def shuffle_doc_tokens(d: Doc, rng) -> Doc:
    toks = [t for line in d.lines for t in line]
    idx = rng.permutation(len(toks))
    toks = [toks[i] for i in idx]
    nd = Doc(d.doc_id, d.site)
    p = 0
    for line in d.lines:
        nd.lines.append(toks[p:p + len(line)])
        p += len(line)
    return nd


def detach_numerals(d: Doc, rng) -> Doc:
    """Wrong-structure null: numerals removed and re-inserted at random slots; group order kept."""
    toks = [t for line in d.lines for t in line]
    groups = [t for t in toks if t.kind == "G"]
    nums = [t for t in toks if t.kind == "N"]
    seq = list(groups)
    for t in nums:
        seq.insert(int(rng.integers(0, len(seq) + 1)), t)
    nd = Doc(d.doc_id, d.site)
    p = 0
    for line in d.lines:
        nd.lines.append(seq[p:p + len(line)])
        p += len(line)
    return nd


def run_null(deriv, held, gold_fn, kind: str, reps: int, seed0: int):
    out = []
    for r in range(reps):
        rng = np.random.default_rng(seed0 + r)
        f = shuffle_doc_tokens if kind == "shuffle" else detach_numerals
        nderiv = [f(d, rng) for d in deriv]
        nheld = [f(d, rng) for d in held]
        model = fit_pipeline(nderiv, gold_fn, seed=SEED + r + 1)
        roles, meta, _ = predict(model, nheld, type_stats(nheld))
        g = grade(roles, meta, gold_fn)
        out.append(g)
    return out


def label_perm_null(roles, meta, gold_fn, reps: int, seed0: int):
    gold = np.array([gold_fn(m[4]) for m in meta])
    roles = np.array(roles)
    rng = np.random.default_rng(seed0)
    accs = []
    for _ in range(reps):
        accs.append(float(np.mean(roles == rng.permutation(gold))))
    return accs


# ------------------------------------------------------------ synthetic PC1

def synth_corpus(n_docs: int, seed: int):
    rng = np.random.default_rng(seed)
    names = [f"n{i}" for i in range(400)]
    commods = [f"C{i}" for i in range(8)]
    units = [f"U{i}" for i in range(3)]
    totw = "totw"
    header_pool = [f"h{i}" for i in range(40)]
    docs, gold_map = [], {}

    def G(sym, n_signs):
        t = Tok("G", raw=sym, n_signs=n_signs, bid=_blind(sym))
        return t

    for di in range(n_docs):
        d = Doc(f"SYN{di}", "SYN")
        hdr = [G(rng.choice(header_pool), int(rng.integers(2, 5)))]
        if rng.random() < 0.5:
            hdr.append(G(rng.choice(header_pool), int(rng.integers(2, 5))))
        d.lines.append(hdr)
        total = 0
        for _ in range(int(rng.integers(3, 9))):
            line = [G(rng.choice(names), int(rng.integers(2, 5))),
                    G(rng.choice(commods), 1)]
            if rng.random() < 0.5:
                line.append(G(rng.choice(units), 1))
            q = int(rng.lognormal(2.0, 1.0)) + 1
            total += q
            line.append(Tok("N", num=float(q)))
            d.lines.append(line)
        d.lines.append([G(totw, 2), G(rng.choice(commods), 1), Tok("N", num=float(total))])
        docs.append(d)
    def gold_syn(t: Tok):
        if t.raw == totw:
            return "T"
        if t.raw.startswith("C"):
            return "C"
        if t.raw.startswith("U"):
            return "U"
        return "W"
    return docs, gold_syn


# ------------------------------------------------------------------ LA leg

def la_gold_check_sets(meta):
    """Returns dict check -> list of (doc_id, site, is_target_role_fn target)."""
    checks = {"C1_KURO": [], "C2_LOGO": [], "C3_KIRO": [], "C4_APREFIX": []}
    for i, (doc_id, site, li, ti, t) in enumerate(meta):
        raw = t.raw
        if raw == "KU-RO":
            checks["C1_KURO"].append(i)
        if raw == "KI-RO":
            checks["C3_KIRO"].append(i)
        if t.n_signs == 1 and raw.split("+")[0] in LA_LOGO_BASES:
            checks["C2_LOGO"].append(i)
        if t.n_signs >= 2 and raw.split("-")[0] == "A":
            checks["C4_APREFIX"].append(i)
    return checks


def binom_sf(k, n, p):
    """P(X >= k), exact."""
    from math import comb
    return sum(comb(n, i) * p**i * (1 - p)**(n - i) for i in range(k, n + 1))


def doc_level_check(idxs, roles, meta, target):
    """Doc-level: success if majority of the doc's check occurrences == target."""
    per_doc = defaultdict(list)
    for i in idxs:
        per_doc[meta[i][0]].append(roles[i] == target)
    succ = sum(1 for v in per_doc.values() if sum(v) * 2 > len(v))
    return succ, len(per_doc)


def holm(pvals: dict):
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    out, run = {}, 0.0
    for r, (k, p) in enumerate(items):
        adj = min(1.0, (m - r) * p)
        run = max(run, adj)
        out[k] = run
    return out
