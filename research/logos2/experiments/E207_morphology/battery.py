"""E207 model battery — prereg baeefa0. Models M0-M6 as held-out per-sign NLL scorers;
enrichment-matched synthetics; holdout axes; mechanical verdicts. λ, d, θ fixed (no tuning)."""
import hashlib
import json
import math
import os
from collections import Counter, defaultdict

import numpy as np

SILVER = "/home/claude-runner/gitlab/n8n/logos-logos2/corpus/silver/inscriptions_structured.json"
MASTER = 1336530913
LAM = 0.5          # lexicon-vs-compositional mix in M3/M4 stem model (fixed, declared)
PYP_D, PYP_T = 0.5, 1.0


def seed_for(*parts):
    return int(hashlib.sha256(("|".join(map(str, (MASTER, "E207") + parts))).encode()
                              ).hexdigest()[:8], 16) % 2**31


def load_words():
    d = json.load(open(SILVER))
    rows = []
    for ins in d:
        st = ins.get("stream", [])
        for i, t in enumerate(st):
            if t.get("t") != "word":
                continue
            w = tuple(t.get("signs", []))
            if len(w) < 2:
                continue
            nxt = st[i + 1]["t"] if i + 1 < len(st) else None
            rows.append({"w": w, "site": ins["site"], "support": ins.get("support"),
                         "context": ins.get("context"), "doc": ins["id"],
                         "entry_head": nxt == "num"})
    return rows


def type_split(rows, seed):
    types = sorted({r["w"] for r in rows})
    rng = np.random.default_rng(seed)
    rng.shuffle(types)
    k = int(0.8 * len(types))
    fit_t, hold_t = set(types[:k]), set(types[k:])
    return ([r for r in rows if r["w"] in fit_t], [r for r in rows if r["w"] in hold_t])


class Battery:
    """Fit all models on fit tokens; score any word list by total NLL / total signs."""

    def __init__(self, fit_rows, affix_cap=8):
        toks = [r["w"] for r in fit_rows]
        self.alphabet = sorted({s for w in toks for s in w})
        self.V = len(self.alphabet)
        self.uni = Counter(s for w in toks for s in w)
        self.N_uni = sum(self.uni.values())
        self.pos = {p: Counter() for p in ("F", "M", "L")}
        for w in toks:
            for i, s in enumerate(w):
                self.pos[self._pc(i, len(w))][s] += 1
        self.pos_n = {p: sum(c.values()) for p, c in self.pos.items()}
        # affix inventory: top initial-lift signs (fit only)
        lift = {}
        for s in self.alphabet:
            pi = (self.pos["F"][s] + 1) / (self.pos_n["F"] + self.V)
            pu = (self.uni[s] + 1) / (self.N_uni + self.V)
            lift[s] = pi / pu
        self.affixes = [s for s, _ in sorted(lift.items(), key=lambda kv: -kv[1])[:affix_cap]]
        # stem lexicon + affix stats (M3); context-conditioned (M4)
        self.stem_count = Counter()
        self.affix_count = Counter()
        self.affix_ctx = {True: Counter(), False: Counter()}
        self.stems_with = defaultdict(set)      # stem -> set of affixes ('' = none)
        for r in fit_rows:
            w = r["w"]
            if w[0] in self.affixes and len(w) >= 3:
                a, stem = w[0], w[1:]
            else:
                a, stem = "", w
            self.stem_count[stem] += 1
            self.affix_count[a] += 1
            self.affix_ctx[bool(r["entry_head"])][a] += 1
            self.stems_with[stem].add(a)
        self.N_stem = sum(self.stem_count.values())
        self.N_aff = sum(self.affix_count.values())
        # word memory for M6
        self.word_count = Counter(toks)
        self.N_words = len(toks)
        self.T_types = len(self.word_count)
        # bigram (M5)
        self.bi = defaultdict(Counter)
        for w in toks:
            prev = "<s>"
            for s in w:
                self.bi[prev][s] += 1
                prev = s
        self.bi_n = {p: sum(c.values()) for p, c in self.bi.items()}

    @staticmethod
    def _pc(i, L):
        return "F" if i == 0 else ("L" if i == L - 1 else "M")

    def p_uni(self, s):
        return (self.uni[s] + 1) / (self.N_uni + self.V)

    def p_pos(self, s, i, L):
        p = self._pc(i, L)
        return (self.pos[p][s] + 1) / (self.pos_n[p] + self.V)

    def nll_M0(self, w):
        return -sum(math.log(self.p_uni(s)) for s in w)

    def nll_M2(self, w):
        return -sum(math.log(self.p_pos(s, i, len(w))) for i, s in enumerate(w))

    def _p_stem(self, stem):
        comp = math.exp(sum(math.log(self.p_pos(s, i, len(stem)))
                            for i, s in enumerate(stem)))
        lex = self.stem_count[stem] / self.N_stem if self.N_stem else 0.0
        return LAM * lex + (1 - LAM) * comp

    def _p_affix(self, a, ctx=None):
        if ctx is None:
            return (self.affix_count[a] + 1) / (self.N_aff + len(self.affixes) + 1)
        c = self.affix_ctx[ctx]
        return (c[a] + 1) / (sum(c.values()) + len(self.affixes) + 1)

    def _p_word_parse(self, w, ctx=None):
        p = self._p_affix("", ctx) * self._p_stem(w)
        if w[0] in self.affixes and len(w) >= 3:
            p += self._p_affix(w[0], ctx) * self._p_stem(w[1:])
        return max(p, 1e-300)

    def nll_M3(self, w):
        return -math.log(self._p_word_parse(w))

    def nll_M4(self, w, ctx):
        return -math.log(self._p_word_parse(w, ctx))

    def nll_M5(self, w):
        nll, prev = 0.0, "<s>"
        for s in w:
            nll -= math.log((self.bi[prev][s] + 1) / (self.bi_n.get(prev, 0) + self.V))
            prev = s
        return nll

    def nll_M6(self, w):
        p0 = self._p_word_parse(w)
        c = self.word_count[w]
        p = (max(c - PYP_D, 0) + (self.T_types * PYP_D + PYP_T) * p0) / (self.N_words + PYP_T)
        return -math.log(max(p, 1e-300))

    def mdl_bits(self, model):
        """Two-part complexity charge (bits): lexicons + parameter tables."""
        b_sign = math.log2(self.V)
        if model in ("M0", "M1"):
            return self.V * 8
        if model == "M2":
            return 3 * self.V * 8
        if model == "M5":
            return (self.V + 1) * self.V * 2
        lex = sum(len(st) for st in self.stem_count) * b_sign
        aff = (len(self.affixes) + 1) * 8
        if model in ("M3", "M4"):
            return lex + aff + (aff if model == "M4" else 0)
        if model == "M6":
            return lex + aff + sum(len(w) for w in self.word_count) * b_sign * 0.1
        return 0.0

    def score(self, rows):
        out = {}
        tot_signs = sum(len(r["w"]) for r in rows)
        for m in ("M0", "M2", "M3", "M4", "M5", "M6"):
            tot = 0.0
            for r in rows:
                w = r["w"]
                if m == "M0":
                    tot += self.nll_M0(w)
                elif m == "M2":
                    tot += self.nll_M2(w)
                elif m == "M3":
                    tot += self.nll_M3(w)
                elif m == "M4":
                    tot += self.nll_M4(w, bool(r["entry_head"]))
                elif m == "M5":
                    tot += self.nll_M5(w)
                elif m == "M6":
                    tot += self.nll_M6(w)
            fit_signs = self.N_uni
            out[m] = tot / (tot_signs * math.log(2)) + self.mdl_bits(m) / max(fit_signs, 1)
        return out  # bits per held-out sign, MDL-charged

    def paradigm_stats(self):
        rec = [st for st, affs in self.stems_with.items()
               if "" in affs and any(a != "" for a in affs) and self.stem_count[st] >= 2]
        alt = [st for st, affs in self.stems_with.items()
               if len([a for a in affs if a != ""]) >= 2]
        return {"recurring_stems_with_and_without_affix": len(rec),
                "stems_with_2plus_distinct_affixes": len(alt),
                "affix_inventory": self.affixes}


def synthetic_rows(rows, seed):
    """Enrichment-matched synthetic: within-site shuffle of NON-INITIAL signs across words
    (initial signs stay; lengths, unigram freqs, site distribution, A-initial rate preserved)."""
    rng = np.random.default_rng(seed)
    by_site = defaultdict(list)
    for i, r in enumerate(rows):
        by_site[r["site"]].append(i)
    out = [dict(r) for r in rows]
    for site, idxs in by_site.items():
        pool = [s for i in idxs for s in rows[i]["w"][1:]]
        rng.shuffle(pool)
        k = 0
        for i in idxs:
            L = len(rows[i]["w"])
            out[i]["w"] = (rows[i]["w"][0],) + tuple(pool[k:k + L - 1])
            k += L - 1
    return out
