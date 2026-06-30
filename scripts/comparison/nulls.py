#!/usr/bin/env python3
"""nulls.py — the deflation null generators for the logos comparison layer (design §B.1).

Each generator produces a CONTROL with the same structural freedom as a real hypothesis but no
genuine correspondence, so that the same held-out statistic computed on it contributes one draw to
the null distribution (mu0, sigma0) used by the deflated bar (§B.3). All generators are deterministic
(seeded) — a null must be reproducible to count as a scientific control.

Three generators, matching the design spec §B.1 and the Nair within-inscription permutation:

  (a) packard_banded_permutation  — frequency-banded sign-value permutation null
      (Packard 1974). Band characters by frequency rank, then within each band apply a random
      bijection (relabel) of the characters. Rewriting every form through that bijection preserves
      the within-band marginal frequencies and the word lengths while destroying the specific
      sign<->value correspondence — the canonical decipherment null.

  (b) random_lexeme_null          — keep the map, draw the anchor root randomly from the candidate
      lexicon (design §B.1 bullet 2). Produces a control set of forms sampled uniformly (with
      replacement) from the real candidate lexicon: real lexemes, real frequencies, but a RANDOM
      pairing that carries no systematic correspondence.

  (c) within_form_permutation     — within-inscription fixed-seed permutation null (Nair 2026,
      arXiv:2604.17828). Permute the characters INSIDE each form. Preserves every form's character
      multiset and length but destroys sequence/phonotactic structure — the tightest same-forms
      control (the only thing changed is order).

Citations: Packard 1974 (frequency-banded permutation); Nair 2026 (arXiv:2604.17828, within-
inscription fixed-seed permutation); logos design §B.1.
"""
from __future__ import annotations

from collections import Counter
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

CITATION_PACKARD = (
    "Packard 1974 — frequency-banded sign-value permutation null: shuffle sign->value assignments "
    "within frequency bands so the permuted map carries the same sign/value marginal frequencies "
    "but no genuine sign-value correspondence."
)
CITATION_NAIR = (
    "Nair 2026, arXiv:2604.17828 — within-inscription fixed-seed permutation: a deterministic "
    "same-forms control that preserves each form's character multiset and length, destroying only "
    "sequence/phonotactic structure."
)


# --------------------------------------------------------------------------- #
# (a) Packard-1974 frequency-banded sign-value permutation null
# --------------------------------------------------------------------------- #
def _frequency_bands(char_counts: Dict[str, int], n_bands: int) -> Dict[str, int]:
    """Assign each character to a frequency band (0 = rare ... n_bands-1 = common) by rank.

    Characters are ranked by count (desc) and split into ``n_bands`` equal-size groups. This is the
    'frequency band' of Packard 1974: permutations happen WITHIN a band so that a common sign can
    only be relabelled as another common sign, preventing the trivial artifact where a rare sign is
    swapped onto a common value (which would invent signal).
    """
    if not char_counts:
        return {}
    chars = sorted(char_counts, key=lambda c: (-char_counts[c], c))
    band_of: Dict[str, int] = {}
    per = max(1, int(np.ceil(len(chars) / max(n_bands, 1))))
    for i, ch in enumerate(chars):
        band_of[ch] = min(i // per, n_bands - 1)
    return band_of


def packard_banded_permutation(forms: Sequence[str],
                               seed: int = 0,
                               n_bands: int = 4) -> List[str]:
    """Return a permuted form list (Packard 1974).

    A within-band random bijection of the character inventory is composed (seeded), then every form
    is rewritten through it. Output preserves word lengths and within-band marginal frequencies;
    it destroys the specific character identities and therefore any genuine correspondence.
    """
    rng = np.random.default_rng(seed)
    counts: Counter = Counter()
    for w in forms:
        counts.update(w)
    band_of = _frequency_bands(dict(counts), n_bands)

    # compose a within-band permutation (bijection) of the inventory
    by_band: Dict[int, List[str]] = {}
    for ch, b in band_of.items():
        by_band.setdefault(b, []).append(ch)
    mapping: Dict[str, str] = {}
    for b, chars in by_band.items():
        perm = list(chars)
        # seeded shuffle — deterministic bijection
        perm_arr = np.array(perm)
        rng.shuffle(perm_arr)
        perm = perm_arr.tolist()
        for src, dst in zip(chars, perm):
            mapping[src] = dst
    # any character unseen in forms maps to itself
    return ["".join(mapping.get(ch, ch) for ch in w) for w in forms]


# --------------------------------------------------------------------------- #
# (b) Random-lexeme null (design §B.1 bullet 2)
# --------------------------------------------------------------------------- #
def random_lexeme_null(candidate_forms: Sequence[str],
                       n: Optional[int] = None,
                       seed: int = 0) -> List[str]:
    """Draw ``n`` forms uniformly at random WITH REPLACEMENT from the candidate lexicon.

    Keeps the real lexeme inventory and its real forms, but the anchor pairing is random — there is
    no systematic correspondence to any held-out inscription. This is the lexeme-side analogue of
    'keep the map, draw the anchor root randomly from L's lexicon' (design §B.1).
    """
    rng = np.random.default_rng(seed)
    pool = [w for w in candidate_forms if w]
    if not pool:
        return []
    n = n if n is not None else len(pool)
    idx = rng.integers(0, len(pool), size=n)
    return [pool[int(i)] for i in idx]


# --------------------------------------------------------------------------- #
# (c) Within-inscription fixed-seed permutation null (Nair 2026)
# --------------------------------------------------------------------------- #
def within_form_permutation(forms: Sequence[str], seed: int = 0) -> List[str]:
    """Permute the characters WITHIN each form (Nair 2026, fixed-seed).

    The tightest possible same-forms control: every form keeps its exact character multiset and
    length; only the order is destroyed, taking phonotactic / root structure with it while leaving
    all marginal statistics identical. Deterministic per seed.
    """
    rng = np.random.default_rng(seed)
    out: List[str] = []
    for w in forms:
        if len(w) <= 1:
            out.append(w)
            continue
        arr = np.array(list(w))
        rng.shuffle(arr)
        out.append("".join(arr.tolist()))
    return out


# --------------------------------------------------------------------------- #
# Convenience: build the full null distribution of a held-out statistic
# --------------------------------------------------------------------------- #
def null_distribution(stat_fn, forms: Sequence[str], candidate: Sequence[str],
                      seed: int = 0, n_packard: int = 32, n_random: int = 32,
                      n_within: int = 32) -> Dict[str, List[float]]:
    """Compute the null distribution of a held-out statistic under all three null generators.

    ``stat_fn(heldout_forms, candidate_lexicon) -> float`` (see lexstat.s_lex). Returns a dict of
    per-null-type score lists; the caller assembles mu0/sigma0 from the concatenation or per-type.
    """
    scores: Dict[str, List[float]] = {"packard": [], "random_lexeme": [], "within_form": []}
    for i in range(n_packard):
        perm = packard_banded_permutation(candidate, seed=seed + i)
        scores["packard"].append(float(stat_fn(list(forms), perm)))
    for i in range(n_random):
        rnd = random_lexeme_null(candidate, n=len(candidate), seed=seed + 1000 + i)
        scores["random_lexeme"].append(float(stat_fn(list(forms), rnd)))
    for i in range(n_within):
        win = within_form_permutation(candidate, seed=seed + 2000 + i)
        scores["within_form"].append(float(stat_fn(list(forms), win)))
    return scores


def main(argv: Optional[Sequence[str]] = None) -> int:
    import argparse, json
    p = argparse.ArgumentParser(description="Deflation null generators (Packard / random / Nair)")
    p.add_argument("--forms", nargs="+", default=["abd", "mlky", "twrhm", "bkr"])
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    forms = args.forms
    out = {
        "input": forms,
        "packard": packard_banded_permutation(forms, seed=args.seed),
        "random_lexeme": random_lexeme_null(forms, n=len(forms), seed=args.seed),
        "within_form": within_form_permutation(forms, seed=args.seed),
        "citations": [CITATION_PACKARD, CITATION_NAIR],
    }
    print(json.dumps(out, indent=2) if args.json else
          "\n".join(f"{k}: {v}" for k, v in out.items() if k != "citations"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
