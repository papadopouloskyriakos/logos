"""
EPOCH-067 machinery — within-word-shuffle null for per-position sign concentration.

Metric (frozen):
  H_k   = Shannon entropy (bits) of anonymous sign distribution at position k.
  A_k   = E_null[H] - H_k   (A_k>0  <=>  position k more concentrated than chance).
  Null  = within EACH word, uniformly permute its sign order; recompute H_k.
          Positions exchangeable under null => E[A_k] = 0.
  p_k   = frac(null A_k >= observed A_k), one-sided (concentration).

Anonymous signs only. Positional entropy only. L2/L3 typology.
"""
import json, math, random
from collections import Counter


def shannon(counter, n):
    h = 0.0
    for c in counter.values():
        if c:
            p = c / n
            h -= p * math.log2(p)
    return h


def pos_entropy(words, k):
    """H_k over a list of sign-lists."""
    c = Counter(w[k] for w in words)
    return shannon(c, len(words))


def position_entropies(words, ks=(0, 1, 2)):
    return [pos_entropy(words, k) for k in ks]


def shuffle_words(words, rng):
    return [rng.sample(w, len(w)) for w in words]  # uniform random permutation, in-place copy


def concentration_test(words, ks=(0, 1, 2), n_shuffles=1000, seed=12345,
                       return_null_H=False):
    """
    Returns dict with H_k (observed), null_expected_H (mean over shuffles),
    A_k, and perm p_k (one-sided, concentration: frac(null A_k >= obs A_k)).
    """
    rng = random.Random(seed)
    obs_H = position_entropies(words, ks)
    n = n_shuffles
    null_H_sum = [0.0] * len(ks)
    # A under null = E_null[H] - H_null_shuffle ; we need distribution of null A_k.
    # null A_k for shuffle s = (mean_null_H_k) - H_null_shuffle_k.
    # Collect H_null_shuffle per shuffle, then compute mean, then A_null per shuffle.
    null_H_per = [[] for _ in ks]  # null_H_per[k][s]
    for _ in range(n):
        sw = shuffle_words(words, rng)
        sh = position_entropies(sw, ks)
        for i, k in enumerate(ks):
            null_H_per[i].append(sh[i])
    mean_null_H = [sum(x) / n for x in null_H_per]
    # observed A_k
    A_obs = [mean_null_H[i] - obs_H[i] for i in range(len(ks))]
    # null A_k distribution
    p = []
    for i in range(len(ks)):
        null_A = [mean_null_H[i] - h for h in null_H_per[i]]
        ge = sum(1 for a in null_A if a >= A_obs[i])
        p.append(ge / n)
    out = {
        "H_obs": {f"H{k}": obs_H[i] for i, k in enumerate(ks)},
        "null_expected_H": {f"H{k}": mean_null_H[i] for i, k in enumerate(ks)},
        "A": {f"A{k}": A_obs[i] for i, k in enumerate(ks)},
        "p": {f"p{k}": p[i] for i, k in enumerate(ks)},
        "n_shuffles": n,
    }
    if return_null_H:
        out["null_H_per"] = null_H_per
    return out


# ---------------------------------------------------------------------------
# Synthetic generators for the positive control.
# ---------------------------------------------------------------------------

def _word_from_inventories(inv_by_pos, lengths, rng):
    L = rng.choice(lengths)
    return [rng.choice(inv_by_pos[min(p, len(inv_by_pos) - 1)]) for p in range(L)]


def gen_detect_depth2(n_words=400, seed=1):
    """Two concentrated slots (pos0, pos1) + diverse tail."""
    rng = random.Random(seed)
    restricted0 = ["P00", "P01", "P02", "P03"]            # 4 signs
    restricted1 = ["Q10", "Q11", "Q12", "Q13"]            # 4 signs
    diverse = [f"D{i:02d}" for i in range(60)]            # 60 signs
    inv = [restricted0, restricted1, diverse, diverse, diverse]
    words = []
    for _ in range(n_words):
        L = rng.choice([3, 3, 4, 4, 5])
        words.append([rng.choice(inv[min(p, len(inv) - 1)]) for p in range(L)])
    return words


def gen_detect_single(n_words=400, seed=1):
    """Only pos0 restricted; pos1+ diverse."""
    rng = random.Random(seed)
    restricted0 = ["P00", "P01", "P02", "P03"]
    diverse = [f"D{i:02d}" for i in range(60)]
    inv = [restricted0, diverse, diverse, diverse, diverse]
    words = []
    for _ in range(n_words):
        L = rng.choice([3, 3, 4, 4, 5])
        words.append([rng.choice(inv[min(p, len(inv) - 1)]) for p in range(L)])
    return words


def gen_uniform(n_words=400, seed=1):
    """All positions from the SAME distribution."""
    rng = random.Random(seed)
    diverse = [f"D{i:02d}" for i in range(60)]
    words = []
    for _ in range(n_words):
        L = rng.choice([3, 3, 4, 4, 5])
        words.append([rng.choice(diverse) for _ in range(L)])
    return words


# ---------------------------------------------------------------------------
# Self-check: validate the within-word permutation null on an EXCHANGEABLE
# synthetic corpus => E[A_k] should be ~0 (no spurious concentration).
# ---------------------------------------------------------------------------

def self_check():
    rng_master = random.Random(99)
    # exchangeable corpus: every position drawn iid from same inventory.
    inv = [f"S{i:02d}" for i in range(50)]
    reps = 200
    n_sh = 200
    As = [0.0, 0.0, 0.0]
    for r in range(reps):
        seed = rng_master.randrange(1 << 30)
        rng = random.Random(seed)
        words = []
        for _ in range(300):
            L = rng.choice([3, 3, 4, 4, 5])
            words.append([rng.choice(inv) for _ in range(L)])
        res = concentration_test(words, n_shuffles=n_sh, seed=seed)
        for i, k in enumerate((0, 1, 2)):
            As[i] += res["A"][f"A{k}"]
    meanA = [a / reps for a in As]
    ok = all(abs(a) < 0.05 for a in meanA)
    print("[self-check] mean A over exchangeable null (should be ~0):",
          [round(a, 4) for a in meanA], "PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    ok = self_check()
    print("self_check_ok =", ok)
