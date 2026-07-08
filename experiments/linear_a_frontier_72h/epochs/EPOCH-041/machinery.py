#!/usr/bin/env python3
"""EPOCH-041 machinery — sign positional-role specialization (L2/L3, anonymous signs).

Frozen metric (see prereg.md):
  For each sign S with >=15 occurrences (in len>=2 words), test whether S's observed
  count in EACH position (initial, final; medial for len>=3 words) exceeds its
  within-word permutation null (one-sided upper tail). Holm-correct across all
  (sign x position) tests at family alpha 0.05. A sign is POSITION-SPECIALIZED if
  it is significantly enriched in >=1 position after Holm.

Signs are ANONYMOUS tokens. No phonetics / meaning / reading. LB is a positive
control benchmark ONLY.

IMPLEMENTATION NOTE: the permutation null uses a VECTORIZED engine. Words are
flattened into one int-ID array with per-slot position tags; each draw shuffles
signs within each word (preserving word length + per-word multiset) via a single
vectorized within-word permutation, and position counts are accumulated with
np.bincount. Mathematically identical to a per-word Counter loop, ~100x faster.
"""
from __future__ import annotations
import json, os, sys
from collections import Counter
from typing import Dict, List, Tuple

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
LA_CORPUS = os.path.join(ROOT, "corpus", "silver", "inscriptions_structured.json")
EPOCH_DIR = os.path.dirname(os.path.abspath(__file__))

MIN_OCC = 15          # sign must occur >=15 times in len>=2 words to be tested
ALPHA = 0.05          # family-wise (Holm)
N_DRAWS = 2000        # permutation draws
RNG_SEED = 41041


# --------------------------------------------------------------------------- data
def load_la_words(corpus_path: str = LA_CORPUS) -> Tuple[List[List[str]], List[str]]:
    """Return (words, sites) — words are sign lists (len>=2), sites aligned per word."""
    data = json.load(open(corpus_path, encoding="utf-8"))
    words: List[List[str]] = []
    sites: List[str] = []
    for ins in data:
        site = ins.get("site", "") or ""
        for tok in ins.get("stream", []):
            if tok.get("t") == "word":
                sg = tok.get("signs", []) or []
                if len(sg) >= 2:
                    words.append(list(sg))
                    sites.append(site)
    return words, sites


def load_lb_words() -> List[List[str]]:
    _scripts = os.path.join(ROOT, "scripts")
    if _scripts not in sys.path:
        sys.path.insert(0, _scripts)
    from cross_script import data as D  # type: ignore
    seqs, _freq, _v2g = D.load_b_damos()
    return [list(s) for s in seqs if len(s) >= 2]


# ----------------------------------------------------------- vectorized encoding
def _encode(words: List[List[str]]):
    """Flatten words into int IDs + per-slot position tags. Words are contiguous."""
    vocab: List[str] = []
    sign2id: Dict[str, int] = {}
    flat_ids: List[int] = []
    flat_word: List[int] = []
    flat_init: List[bool] = []
    flat_final: List[bool] = []
    flat_med: List[bool] = []
    for wi, w in enumerate(words):
        L = len(w)
        for j, s in enumerate(w):
            if s not in sign2id:
                sign2id[s] = len(vocab); vocab.append(s)
            flat_ids.append(sign2id[s])
            flat_word.append(wi)
            flat_init.append(j == 0)
            flat_final.append(j == L - 1)
            flat_med.append(0 < j < L - 1)
    return {
        "ids": np.asarray(flat_ids, dtype=np.int64),
        "vocab": vocab, "sign2id": sign2id,
        "word_id": np.asarray(flat_word, dtype=np.int64),
        "pos_init": np.asarray(flat_init, dtype=bool),
        "pos_final": np.asarray(flat_final, dtype=bool),
        "pos_med": np.asarray(flat_med, dtype=bool),
    }


def _within_word_rank(word_id: np.ndarray) -> np.ndarray:
    """Within-word sequential rank (0..L-1) for each slot. Words must be contiguous."""
    w = np.asarray(word_id)
    boundaries = np.concatenate(([True], w[1:] != w[:-1]))
    run_start = np.zeros(len(w), dtype=np.int64)
    bidx = np.where(boundaries)[0]
    run_start[bidx] = bidx
    np.maximum.accumulate(run_start, out=run_start)
    return np.arange(len(w)) - run_start


def _permute_ids(enc, rng: np.random.Generator) -> np.ndarray:
    """Shuffle signs within each word (vectorized, exact, uniformly random).

    A within-word permutation is specified by an independent random reordering of
    each word's slots. We:
      1. orig_rank[slot] = slot's within-word index (0..L-1).
      2. keys[slot]      = uniform random.
      3. rand_order  = argsort by (word_id, keys)        -> slots grouped by word,
                                                            ordered by random key.
      4. orig_order  = argsort by (word_id, orig_rank)   -> slots grouped by word,
                                                            ordered by original rank.
      Both group identical word_ids into the SAME contiguous blocks (same lengths);
      only the within-word ordering differs. So position k within a word's block in
      rand_order corresponds to position k in orig_order.
      5. The permuted id for the slot at orig_order[block_base + k] is the id of the
         slot at rand_order[block_base + k]. Scatter back to flat slots.
    Preserves word length and per-word multiset exactly; uniform over within-word
    permutations.
    """
    ids = enc["ids"]
    word_id = enc["word_id"]
    keys = rng.random(len(ids))
    orig_rank = _within_word_rank(word_id)
    rand_order = np.lexsort((keys, word_id))        # primary word_id, secondary key
    orig_order = np.lexsort((orig_rank, word_id))   # primary word_id, secondary orig_rank
    new_ids = np.empty_like(ids)
    new_ids[orig_order] = ids[rand_order]
    return new_ids


def _obs_counts(enc) -> Dict[str, np.ndarray]:
    V = len(enc["vocab"])
    ids = enc["ids"]
    return {
        "initial": np.bincount(ids[enc["pos_init"]], minlength=V).astype(np.int64),
        "final":   np.bincount(ids[enc["pos_final"]], minlength=V).astype(np.int64),
        "medial":  np.bincount(ids[enc["pos_med"]], minlength=V).astype(np.int64),
    }


# ----------------------------------------------------------------- permutation null
def permute_words(words: List[List[str]], rng: np.random.Generator) -> List[List[str]]:
    """Permute signs WITHIN each word (list-of-lists form, for shuffling whole corpora)."""
    out = []
    for w in words:
        if len(w) <= 1:
            out.append(list(w)); continue
        idx = rng.permutation(len(w))
        out.append([w[i] for i in idx])
    return out


def positional_test(
    words: List[List[str]],
    min_occ: int = MIN_OCC,
    n_draws: int = N_DRAWS,
    seed: int = RNG_SEED,
) -> Dict:
    """Run the frozen positional-specialization test on `words` (vectorized engine)."""
    enc = _encode(words)
    V = len(enc["vocab"])
    tot = np.bincount(enc["ids"], minlength=V).astype(np.int64)
    signs_tested_idx = np.where(tot >= min_occ)[0]
    signs_tested = [enc["vocab"][i] for i in signs_tested_idx]
    n_tested = len(signs_tested)
    positions = ["initial", "final", "medial"]

    obs = _obs_counts(enc)
    obs_count = {p: obs[p][signs_tested_idx].astype(np.int64) for p in positions}

    rng = np.random.default_rng(seed)
    ge = {p: np.zeros(n_tested, dtype=np.int64) for p in positions}
    pos_masks = {"initial": enc["pos_init"], "final": enc["pos_final"],
                 "medial": enc["pos_med"]}
    for _ in range(n_draws):
        new_ids = _permute_ids(enc, rng)
        for p in positions:
            mask = pos_masks[p]
            cnt = np.bincount(new_ids[mask], minlength=V)
            ge[p] += (cnt[signs_tested_idx] >= obs_count[p]).astype(np.int64)

    tests = []
    for p in positions:
        pvals = (ge[p] + 1.0) / (n_draws + 1.0)
        for k, s in enumerate(signs_tested):
            tests.append([k, p, float(pvals[k]), int(obs_count[p][k])])

    # Holm correction across all (sign x position) tests
    m = len(tests)
    order = sorted(range(m), key=lambda k: tests[k][2])
    holm_p = [0.0] * m
    running = 0.0
    for rank, k in enumerate(order):
        running = max(running, (m - rank) * tests[k][2])
        holm_p[k] = min(1.0, running)
    for k in range(m):
        tests[k] = (tests[k][0], tests[k][1], tests[k][2], holm_p[k], tests[k][3])

    spec_signs = set()
    spec_by_pos = {p: set() for p in positions}
    for i, p, raw, adj, oc in tests:
        if adj < ALPHA:
            spec_signs.add(signs_tested[i])
            spec_by_pos[p].add(signs_tested[i])

    specialized_fraction = (len(spec_signs) / n_tested) if n_tested else 0.0

    return {
        "signs_tested": signs_tested,
        "n_tested": n_tested,
        "observed": {p: {s: int(obs_count[p][k]) for k, s in enumerate(signs_tested)}
                     for p in positions},
        "tests": tests,
        "spec_signs": spec_signs,
        "spec_by_pos": spec_by_pos,
        "specialized_fraction": specialized_fraction,
        "n_draws": n_draws,
        "min_occ": min_occ,
    }


def specialized_sign_table(res: Dict, words: List[List[str]]) -> List[List]:
    """For each specialized sign: [sign, preferred_pos, initial_rate, final_rate]."""
    enc = _encode(words)
    V = len(enc["vocab"])
    tot = np.bincount(enc["ids"], minlength=V).astype(np.int64)
    obs = res["observed"]
    out = []
    for s in res["spec_signs"]:
        pref = None
        for p in ["initial", "final", "medial"]:
            if s in res["spec_by_pos"][p]:
                pref = p; break
        sid = enc["sign2id"][s]
        ir = obs["initial"].get(s, 0) / max(1, int(tot[sid]))
        fr = obs["final"].get(s, 0) / max(1, int(tot[sid]))
        out.append([s, pref, round(float(ir), 4), round(float(fr), 4)])
    out.sort(key=lambda r: r[0])
    return out


# ----------------------------------------------------------------- positive control
def positive_control(lb_words: List[List[str]], n_sets: int = 20,
                     n_draws: int = N_DRAWS, seed: int = RNG_SEED) -> Dict:
    real = positional_test(lb_words, n_draws=n_draws, seed=seed)
    lb_frac = real["specialized_fraction"]

    rng = np.random.default_rng(seed + 1)
    shuf_fracs = []
    for k in range(n_sets):
        sw = permute_words(lb_words, rng)
        r = positional_test(sw, n_draws=n_draws, seed=seed + 100 + k)
        shuf_fracs.append(r["specialized_fraction"])
    shuf_frac = float(np.mean(shuf_fracs))
    false_pos_rate = shuf_frac

    detect = (lb_frac > ALPHA) and (lb_frac > shuf_frac)
    fp_ok = (false_pos_rate <= 0.10)
    pc_passed = bool(detect and fp_ok)

    return {
        "pc_verdict": "PASSED" if pc_passed else "FAILED",
        "lb_specialized_fraction": lb_frac,
        "lb_shuffled_fraction": shuf_frac,
        "false_pos_rate": false_pos_rate,
        "shuf_fracs": shuf_fracs,
        "detect": detect,
        "fp_ok": fp_ok,
        "n_sets": n_sets,
    }


# ----------------------------------------------------------------- cross-site
def cross_site(words: List[List[str]], sites: List[str], min_tokens: int = 200,
               n_draws: int = N_DRAWS, seed: int = RNG_SEED) -> Dict:
    by_site: Dict[str, List[List[str]]] = {}
    for w, s in zip(words, sites):
        by_site.setdefault(s, []).append(w)
    per_site = {}
    for s, ws in by_site.items():
        if len(ws) >= min_tokens:
            r = positional_test(ws, n_draws=n_draws, seed=seed)
            per_site[s] = r["specialized_fraction"]
    loo_words = [w for w, s in zip(words, sites) if s != "Haghia Triada"]
    loo_excluded = "Haghia Triada"
    loo_res = positional_test(loo_words, n_draws=n_draws, seed=seed)
    return {
        "n_sites_testable": len(per_site),
        "per_site_fraction": per_site,
        "loo_excluded": loo_excluded,
        "loo_fraction": loo_res["specialized_fraction"],
    }


# ----------------------------------------------------------------- verdict
def verdict(pc: Dict, glob: Dict, cs: Dict) -> str:
    if pc["pc_verdict"] != "PASSED":
        return "MACHINERY_UNINFORMATIVE"
    if cs["n_sites_testable"] < 3 or glob["n_tested"] < 15:
        return "SPECIALIZATION_UNDERPOWERED"
    g = glob["specialized_fraction"]
    n_sites_ge = sum(1 for v in cs["per_site_fraction"].values() if v >= 0.15)
    if g >= 0.20 and n_sites_ge >= 3:
        return "HIGH_POSITIONAL_SPECIALIZATION_CROSS_SITE"
    if g >= 0.20:
        return "POSITIONAL_SPECIALIZATION_SITE_LOCAL"
    return "LOW_POSITIONAL_SPECIALIZATION"


# ----------------------------------------------------------------- self-check
def _selfcheck() -> None:
    rng = np.random.default_rng(0)
    words = []
    for _ in range(60):
        words.append(["ZZ", str(rng.choice(["A", "B", "C", "D"]))])
    for _ in range(60):
        words.append([str(rng.choice(["A", "B", "C", "D"])), "YY"])
    for _ in range(60):
        words.append([str(rng.choice(["A", "B", "C", "D", "E"])),
                      str(rng.choice(["A", "B", "C", "D", "E"])),
                      str(rng.choice(["A", "B", "C", "D", "E"]))])
    r = positional_test(words, min_occ=15, n_draws=500, seed=1)
    assert "ZZ" in r["spec_signs"], ("ZZ should be initial-specialized", r["spec_signs"])
    assert "YY" in r["spec_signs"], ("YY should be final-specialized", r["spec_signs"])
    # verify _permute_ids preserves per-word multiset
    enc = _encode(words)
    prng = np.random.default_rng(2)
    for _ in range(5):
        nid = _permute_ids(enc, prng)
        # per-word multiset preserved: sort each word's ids == sort original
        ok = True
        wi = 0
        # rebuild per-word via word_id
        for w in words:
            L = len(w)
            orig = sorted(enc["ids"][enc["word_id"] == wi][:L].tolist() if False else
                          [enc["ids"][k] for k in range(len(enc["ids"])) if enc["word_id"][k] == wi])
            new = sorted([nid[k] for k in range(len(nid)) if enc["word_id"][k] == wi])
            if orig != new:
                ok = False; break
            wi += 1
        assert ok, "permutation must preserve per-word multiset"
    print("SELF-CHECK OK: synthetic initial/final specialists detected;",
          "specialized_fraction=%.3f" % r["specialized_fraction"],
          "spec=", sorted(r["spec_signs"]))


if __name__ == "__main__":
    _selfcheck()
