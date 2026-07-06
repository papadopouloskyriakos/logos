#!/usr/bin/env python3
"""§V/§VI Egyptian→foreign correspondence model + baselines + recovery scoring.

Each frozen record gives a Semitic consonantal skeleton (`cons`, e.g. ʾ-b-d) and the Egyptian
group-writing rendering (`egy`, e.g. ꜣa-ba-ti). The model estimates P(egyptian_grapheme | semitic_
consonant) from position-aligned pairs, then scores candidate source skeletons for a held-out Egyptian
rendering. Baselines: M0 identity, M1 uniform edit distance, M9 permissive (all-substitutions-free)
false-positive stress test. Fits ONLY on the frozen corpus; no Cretan/LA data ever enters."""
import json, math, os
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.normpath(os.path.join(HERE, "..", "..", "data", "gold", "egyptian_calibration_handverified.jsonl"))
VOWELS = set("aeiouāēīōūáéíóúàèìòù")


def egy_cons(egy):
    """Leading consonant of each hyphen-separated CV group: 'ꜣa-ba-ti' -> ['ꜣ','b','t']."""
    out = []
    for g in egy.split("-"):
        c = "".join(ch for ch in g if ch.lower() not in VOWELS)
        if c:
            out.append(c[0] if len(c) > 1 else c)   # first consonant symbol of the group
    return out


def sem_cons(cons):
    return [c for c in cons.split("-") if c]


def load(tiers=("A", "B")):
    recs = [json.loads(l) for l in open(CORPUS, encoding="utf-8")]
    recs = [r for r in recs if r["tier"] in tiers]
    for r in recs:
        r["_egy"] = egy_cons(r["egy"]); r["_sem"] = sem_cons(r["cons"])
    return recs


def _align(a, b):
    """Minimal-cost position alignment (Needleman-Wunsch, unit costs) -> list of (a_i|None, b_j|None)."""
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1): dp[i][0] = i
    for j in range(m + 1): dp[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            dp[i][j] = min(dp[i-1][j-1] + (a[i-1] != b[j-1]), dp[i-1][j] + 1, dp[i][j-1] + 1)
    i, j, al = n, m, []
    while i > 0 or j > 0:
        if i > 0 and j > 0 and dp[i][j] == dp[i-1][j-1] + (a[i-1] != b[j-1]):
            al.append((a[i-1], b[j-1])); i -= 1; j -= 1
        elif i > 0 and dp[i][j] == dp[i-1][j] + 1:
            al.append((a[i-1], None)); i -= 1
        else:
            al.append((None, b[j-1])); j -= 1
    return al[::-1]


class Correspondence:
    """M2 pooled probabilistic model: P(egy grapheme | sem consonant), add-alpha smoothed."""
    def __init__(self, alpha=0.5):
        self.alpha = alpha; self.cond = defaultdict(Counter); self.egy_vocab = set(); self.gap = 0.05

    def fit(self, recs):
        for r in recs:
            for s, e in _align(r["_sem"], r["_egy"]):
                if s is not None and e is not None:
                    self.cond[s][e] += 1; self.egy_vocab.add(e)
        return self

    def logp(self, sem_c, egy_g):
        c = self.cond[sem_c]; V = max(len(self.egy_vocab), 1)
        return math.log((c.get(egy_g, 0) + self.alpha) / (sum(c.values()) + self.alpha * V))

    def score(self, egy_seq, sem_seq):
        """log-likelihood that sem_seq produced egy_seq (best alignment)."""
        tot = 0.0
        for s, e in _align(sem_seq, egy_seq):
            if s is None or e is None:
                tot += math.log(self.gap)
            else:
                tot += self.logp(s, e)
        return tot


def score_baseline(egy_seq, sem_seq, kind):
    """M0 identity (-#mismatches, treating egy≈sem consonants); M1 uniform edit distance; M9 permissive."""
    al = _align(sem_seq, egy_seq)
    if kind == "M0":
        return -sum(1 for s, e in al if s != e)                 # exact identity reward
    if kind == "M1":
        return -sum(1 for s, e in al if (s is None or e is None or s != e))
    if kind == "M9":
        return 0.0                                              # permissive: everything matches equally
    raise ValueError(kind)


def recover_rank(model, egy_seq, true_sem, candidates, kind="M2"):
    """Rank of the true source skeleton among all candidate skeletons for this Egyptian rendering.

    LEGACY calibration helper (validation.py / gate.py) — NOT the Cretan-anchor grader. The one-shot
    Cretan test uses cretan_test.rank_of, which enforces 'tie at rank 1 => not recovered'; this helper
    awards rank 1 to the first exact match under sort order and must not be used as that grader."""
    def sc(sem):
        return model.score(egy_seq, sem) if kind == "M2" else score_baseline(egy_seq, sem, kind)
    scored = sorted(candidates, key=sc, reverse=True)
    # rank of true (first exact match)
    for i, sem in enumerate(scored):
        if sem == true_sem:
            return i + 1
    return len(scored) + 1


if __name__ == "__main__":
    recs = load()
    m = Correspondence().fit(recs)
    print(f"fitted on {len(recs)} tier-A/B records; sem consonants modelled: {len(m.cond)}; egy vocab: {len(m.egy_vocab)}")
    # show a few learned correspondences (the systematic shifts)
    for s in ["d", "l", "h", "ṣ", "ʾ", "b"]:
        if s in m.cond:
            top = m.cond[s].most_common(3)
            print(f"  P(egy|{s}): {top}")
