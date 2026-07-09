"""
EPOCH-069 machinery: entry-initial vs entry-internal word length (L2).

word-length = len(signs); position = order within a line (between consecutive 'nl').
Null: within each line, uniformly shuffle the order of its word tokens; recompute diff.
A-exclusion: drop any word whose first sign is 'A' from both pools; re-derive each line's
first word among the remaining words.

Metric (conforms to frozen prereg): diff = mean(len of FIRST words) - mean(len of LATER
words), pooled over target lines.  Each target line contributes ONE first-word length and
ONE later-word mean (mean of its word[1:] lengths), so both pools are unweighted per-line.
Under the within-line shuffle null, first/later positions are exchangeable, so
E[first_mean] = E[later_mean] = unweighted mean of per-line means, hence E[diff] = 0
exactly — as required by the frozen prereg ("E[diff] = 0").

(Previous version used a flat count-weighted later pool, which introduced a bias because
lines with more words contributed disproportionately to the later pool. The unweighted
per-line pooling removes this asymmetry and restores E[diff]=0.)
"""
import json
import random
import sys
from collections import Counter

CORPUS = "corpus/silver/inscriptions_structured.json"


def load_corpus(path=CORPUS):
    with open(path) as f:
        return json.load(f)


def lines_of(insc):
    """Return list of lines; each line is a list of word-sign-lists in order between nl."""
    lines = []
    cur = []
    for tok in insc.get("stream", []):
        t = tok.get("t")
        if t == "nl":
            lines.append(cur)
            cur = []
        elif t == "word":
            cur.append(list(tok.get("signs", [])))
    if cur:
        lines.append(cur)
    return lines


def target_lines(corpus):
    """Return list of (site, line) for lines with >=2 word tokens."""
    out = []
    for x in corpus:
        site = x.get("site", "?")
        for line in lines_of(x):
            if len(line) >= 2:
                out.append((site, line))
    return out


def _diff_from_work(work):
    """Compute diff = unweighted-mean(per-line first len) - unweighted-mean(per-line later mean).

    work = list of per-line length lists (each len>=2).
    Returns (diff, first_mean, later_mean).
    """
    n = len(work)
    if n == 0:
        return 0.0, 0.0, 0.0
    tot_first = sum(L[0] for L in work)
    tot_later_mean = sum(sum(L[1:]) / (len(L) - 1) for L in work)
    fm = tot_first / n
    lm = tot_later_mean / n
    return fm - lm, fm, lm


def perm_test_fast(lines, n_perm=2000, seed=69, exclude_A=False):
    """One-sided perm p = frac(null diff >= observed diff). Null = within-line word shuffle.
    If exclude_A: drop A-initial words; keep only lines still >=2 words."""
    rng = random.Random(seed)
    work = []
    for site, line in lines:
        if exclude_A:
            kept = [len(w) for w in line if not (len(w) > 0 and w[0] == "A")]
            if len(kept) >= 2:
                work.append(kept)
        else:
            work.append([len(w) for w in line])
    if len(work) < 2:
        return {"observed": 0.0, "null_mean": 0.0, "perm_p": 1.0, "n_lines": len(work),
                "first_mean": 0.0, "later_mean": 0.0, "null_sd": 0.0}
    obs, fm, lm = _diff_from_work(work)
    null_diffs = []
    for _ in range(n_perm):
        shuf_work = []
        for L in work:
            shuf = L[:]
            rng.shuffle(shuf)
            shuf_work.append(shuf)
        d, _, _ = _diff_from_work(shuf_work)
        null_diffs.append(d)
    null_mean = sum(null_diffs) / len(null_diffs)
    null_sd = (sum((x - null_mean) ** 2 for x in null_diffs) / len(null_diffs)) ** 0.5
    ge = sum(1 for x in null_diffs if x >= obs)
    perm_p = (ge + 1) / (len(null_diffs) + 1)  # add-1
    return {"observed": obs, "null_mean": null_mean, "perm_p": perm_p,
            "n_lines": len(work), "first_mean": fm, "later_mean": lm, "null_sd": null_sd}


def positive_control_detect(seed=101, n_perm=1000):
    """DETECT: plant lines where first word is always longer. Expect perm p<=0.05."""
    rng = random.Random(seed)
    lines = []
    for _ in range(60):
        first = ["X"] * rng.randint(4, 6)
        rest = [["X"] * rng.randint(1, 2) for _ in range(rng.randint(1, 3))]
        lines.append(("SYN", [first] + rest))
    res = perm_test_fast(lines, n_perm=n_perm, seed=seed)
    return res


def positive_control_falsepos(seed=202, n_draws=30, n_perm=500):
    """FALSE-POSITIVE: word lengths independent of position. Expect rejection <=0.10."""
    rej = 0
    ps = []
    for i in range(n_draws):
        rng = random.Random(seed + i)
        lines = []
        for _ in range(60):
            pool = [rng.randint(1, 4) for _ in range(rng.randint(2, 4))]
            words = [["X"] * L for L in pool]
            rng.shuffle(words)
            lines.append(("SYN", words))
        res = perm_test_fast(lines, n_perm=n_perm, seed=seed + i)
        ps.append(res["perm_p"])
        if res["perm_p"] <= 0.05:
            rej += 1
    return {"false_pos_rate": rej / n_draws, "n_draws": n_draws, "ps": ps}


def self_check():
    """Validate the shuffle null: empirical null mean ~= 0 (as frozen prereg requires)."""
    corpus = load_corpus()
    tl = target_lines(corpus)
    res = perm_test_fast(tl, n_perm=2000, seed=42)
    print(f"[self-check] n_lines={res['n_lines']} observed diff={res['observed']:.4f} "
          f"null_mean={res['null_mean']:.4f} "
          f"perm_p={res['perm_p']:.4f}")
    assert abs(res["null_mean"]) < 0.02, \
        f"null mean {res['null_mean']} != 0: machinery broken (prereg requires E[diff]=0)"
    print("[self-check] PASS: empirical null mean ~= 0 "
          "(shuffle machinery valid, conforms to frozen prereg E[diff]=0)")
    return res


if __name__ == "__main__":
    print("=== SELF-CHECK ===")
    self_check()
    print()
    print("=== POSITIVE CONTROL DETECT ===")
    d = positive_control_detect(seed=101, n_perm=1000)
    print(f"detect: observed={d['observed']:.4f} perm_p={d['perm_p']:.4f} "
          f"(expect perm_p<=0.05)")
    print()
    print("=== POSITIVE CONTROL FALSE-POSITIVE ===")
    fp = positive_control_falsepos(seed=202, n_draws=30, n_perm=500)
    print(f"false_pos_rate={fp['false_pos_rate']:.3f} over {fp['n_draws']} draws "
          f"(expect <=0.10)")
