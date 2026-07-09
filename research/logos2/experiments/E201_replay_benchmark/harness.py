"""E201 replay-benchmark harness (pilot) — prereg 46d8da5.

Wraps the validated in-repo decipherment machinery (scripts/decipher: frequency-init EM with
Hungarian M-step, LIN-14 lineage) in evidence-ladder + control-battery form over the .cog
known-answer datasets. Dataset-type disclosures (prereg 'faithfulness caveat'):
- .cog files are cognate PAIR LISTS, not corpora: the 'formula boundaries' and 'semantic
  classes' ladder rungs are NOT_APPLICABLE; the 'related-language corpus' rung is inherent
  (the plain column IS the related lexicon); segmentation-degradation is NOT_APPLICABLE
  (words arrive pre-segmented).
- Anchors are SOFT (warm-start phi from anchor-pair character alignments); run_em has no
  clamping hook — disclosed, and identical across real and control arms.
No Linear A data is loaded anywhere in this experiment.
"""
import hashlib
import os
import sys
from collections import Counter

import numpy as np

_ROOT = "/home/claude-runner/gitlab/n8n/logos-logos2"
sys.path.insert(0, _ROOT)
from scripts.decipher import decipher, maplearn  # noqa: E402

DATA = "/home/claude-runner/gitlab/n8n/logos/corpus/bronze/code/CSA_OptMatcher/data"
MASTER = 1336530913


def seed_for(*parts):
    h = hashlib.sha256(("|".join(str(p) for p in (MASTER,) + parts)).encode()).hexdigest()
    return int(h[:8], 16) % 2**31


def load_cog(name):
    """Return (cipher_words, plain_words, true_pairs) as tuples of chars."""
    path = os.path.join(DATA, name)
    cw, pw, pairs = [], [], {}
    with open(path) as f:
        header = f.readline()
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 2 or not parts[0] or not parts[1]:
                continue
            c, p = tuple(parts[0]), tuple(parts[1])
            cw.append(c); pw.append(p); pairs[c] = p
    return cw, pw, pairs


def subsample(cw, pw, pairs, n, seed):
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(cw), size=min(n, len(cw)), replace=False)
    cw2 = [cw[i] for i in idx]; pw2 = [pw[i] for i in idx]
    return cw2, pw2, {c: pairs[c] for c in cw2 if c in pairs}


def anchor_phi(anchor_pairs):
    """SOFT anchors: positional character equalities from anchor word pairs."""
    phi = {}
    for c, p in anchor_pairs:
        for cc, pp in zip(c, p):
            phi.setdefault(cc, pp)
    return phi


def run_cell(cw, pw, pairs, anchors=(), bilingual_frac=0.0, iters=25, seed=0):
    """One harness cell: EM with optional soft anchors / bilingual seeding; returns metrics."""
    rng = np.random.default_rng(seed)
    seed_pairs = list(anchors)
    if bilingual_frac > 0:
        k = int(round(bilingual_frac * len(cw)))
        idx = rng.choice(len(cw), size=k, replace=False)
        seed_pairs += [(cw[i], pairs[cw[i]]) for i in idx if cw[i] in pairs]
    phi0 = anchor_phi(seed_pairs)
    # warm start: frequency init overridden by anchor equalities
    phi = maplearn.frequency_init(cw, pw)
    phi.update(phi0)
    # run EM manually to keep the seeded phi as cold-start (mirrors decipher.run_em)
    from scripts.decipher import align as alignmod, eval as evalmod
    alignments = {}
    for it in range(iters):
        alignments = alignmod.best_align(cw, pw, phi, sub_cost=1.0, indel_cost=1.0,
                                         max_len_delta=2)
        new_phi = maplearn.fit_map(alignmod.collect_pairs(alignments))
        merged = dict(phi); merged.update(new_phi)
        if merged == phi and it > 0:
            break
        phi = merged
    res = decipher.evaluate(phi, alignments, truth_map=None, true_pairs=pairs,
                            cipher_words=cw, plain_words=pw)
    # ambiguity proxy: cipher chars whose top-2 co-occurrence counts tie
    prs = alignmod.collect_pairs(alignments)
    M, rows, cols = maplearn.build_count_matrix(prs)
    ties = 0
    for i in range(M.shape[0]):
        srt = np.sort(M[i])[::-1]
        if len(srt) > 1 and srt[0] == srt[1]:
            ties += 1
    res["ambiguous_chars"] = int(ties)
    res["n_chars"] = len(rows)
    return res


def graduates(res, min_acc=0.3, chance_mult=2.0):
    """Mechanical graduation rule for the control battery (prereg: controls must yield 0)."""
    acc = res.get("cognate_accuracy") or 0.0
    ch = res.get("chance_cognate_accuracy") or 0.0
    return bool(acc >= min_acc and acc >= chance_mult * max(ch, 1e-9))


# ---------------- controls ----------------
def control_shuffled_inventory(cw, seed):
    rng = np.random.default_rng(seed)
    return [tuple(rng.permutation(list(w))) for w in cw]


def control_synthetic_isolate(cw, seed):
    """Random lexicon matched for word length + char frequency of the PLAIN side is built by
    the caller; here: match the cipher side's length/frequency profile."""
    rng = np.random.default_rng(seed)
    chars = [c for w in cw for c in w]
    freq = Counter(chars)
    pool = list(freq.keys()); p = np.array([freq[c] for c in pool], float); p /= p.sum()
    return [tuple(rng.choice(pool, size=len(w), p=p)) for w in cw]


def control_corrupt_anchors(anchors, pw, f_wrong, seed):
    rng = np.random.default_rng(seed)
    out = list(anchors)
    k = int(round(f_wrong * len(out)))
    for i in rng.choice(len(out), size=k, replace=False):
        c, _ = out[i]
        out[i] = (c, pw[int(rng.integers(0, len(pw)))])
    return out


def leak_detector(cw, pw):
    """Fires if >5% of cipher words are byte-identical to some plain word (leaked names)."""
    ps = set(pw)
    frac = sum(1 for w in cw if w in ps) / max(len(cw), 1)
    return {"identical_frac": frac, "fired": frac > 0.05}
