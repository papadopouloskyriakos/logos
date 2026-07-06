#!/usr/bin/env python3
"""§III primary ADMINISTRATIVE_TOPONYM_CONTINUITY model + ablations A1–A5.

A match is EXACT sign-sequence identity under a fixed representation — NO learned mapping, NO
best-of-many reassignment, NO manual exceptions, NO target-specific edits. Layers:

  A1  exact raw sign-sequence identity (GORILA-number sequence equality)
  A2  via the frozen 77-sign tier-A A↔B equivalence map (AB##(LA) ≡ *##(LB))
  A3  A2 + a prespecified ≤1-position wildcard AT a damaged/composite-flagged position (same length)
  A4  projected LB phonetic values (base value, subscripts merged — homophone-tolerant)
  A5  deliberately PERMUTED projected values (wrong map) — the phonetic-specificity control

Interpretation: A1≥A2≥A3-only≥A4-only. If A4≈A5 → no phonetic specificity. Signal only under A4 →
circularity risk high; the orthographic channel does not graduate.
"""
import json, os, sys
from functools import lru_cache

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
import cfg  # noqa: E402
import partitions as P  # noqa: E402
import syllabary as syl  # noqa: E402

_AB_EQUIV = os.path.join(cfg.GOLD, "ab_sign_equivalence.json")


@lru_cache(maxsize=1)
def tier_a_numbers():
    m = json.load(open(_AB_EQUIV, encoding="utf-8"))
    return frozenset(r["gorila_number"] for r in m["equivalence"] if r["confidence_tier"] == "A")


@lru_cache(maxsize=1)
def num_to_base_value():
    """GORILA number -> base phonetic value (subscripts stripped): 3->'pa', 56->'pa'(pa3), 76->'ra'(ra2)."""
    out = {}
    for val, n in syl.GRID.items():
        base = val.rstrip("0123456789")
        out.setdefault(n, base)          # first (lowest-form) wins deterministically
    return out


def _perm_base_value(seed=cfg.SEED):
    """A5: a fixed derangement of the number->value assignment (wrong values), deterministic."""
    import random
    nv = num_to_base_value()
    nums = sorted(nv)
    vals = [nv[n] for n in nums]
    rng = random.Random(seed)
    shuffled = vals[:]
    rng.shuffle(shuffled)
    return dict(zip(nums, shuffled))


_PERM = None


def la_seq(cand):
    return P.gorila_seq(cand["raw_sign_ids"])


def lb_seq(tgt):
    return P.gorila_seq(tgt["raw_sign_sequence"])


def _val_seq(seq, mapping):
    return tuple(mapping.get(x, ("?", x)) if isinstance(x, int) else x for x in seq)


def matches(cand, tgt, layer):
    a, b = la_seq(cand), lb_seq(tgt)
    if layer in ("A1", "A2"):
        if layer == "A2" and any(not (isinstance(x, int) and x in tier_a_numbers()) for x in a):
            return False                 # A2 requires every LA sign be a tier-A homomorph
        return a == b
    if layer == "A3":
        if len(a) != len(b):
            return False
        flagged = cand["uncertainty"]["composite_sensitive"] or cand["uncertainty"]["damaged"]
        mism = [i for i in range(len(a)) if a[i] != b[i]]
        if not mism:
            return all(isinstance(x, int) and x in tier_a_numbers() for x in a)
        return len(mism) == 1 and flagged   # one prespecified wildcard at a flagged candidate
    if layer == "A4":
        nv = num_to_base_value()
        return _val_seq(a, nv) == _val_seq(b, nv)
    if layer == "A5":
        global _PERM
        if _PERM is None:
            _PERM = _perm_base_value()
        return _val_seq(a, _PERM) == _val_seq(b, num_to_base_value())
    raise ValueError(layer)


def match_pairs(cands, tgts, layer):
    return [(c["candidate_id"], t["lb_target_id"]) for c in cands for t in tgts if matches(c, t, layer)]


def summary(cands, tgts, layer):
    pairs = match_pairs(cands, tgts, layer)
    cset = {p[0] for p in pairs}; tset = {p[1] for p in pairs}
    return {"layer": layer, "n_pairs": len(pairs), "n_candidates_matched": len(cset),
            "n_targets_matched": len(tset), "pairs": pairs}


def run(cand_set="PRIMARY_B", tgt_role="EVALUATION"):
    cfg.verify_inputs()
    parts = P.partitioned()
    if cand_set == "PRIMARY_PLUS_SENSITIVITY":
        cands = P.primary_plus_sensitivity()
    else:
        cands = parts[cand_set]
    tgts = [t for t in P.load_targets() if t["development_or_evaluation_role"] == tgt_role]
    return {L: summary(cands, tgts, L) for L in ("A1", "A2", "A3", "A4", "A5")}


if __name__ == "__main__":
    cfg.verify_inputs()
    for cand_set in ("PRIMARY_B", "PRIMARY_PLUS_SENSITIVITY"):
        print(f"\n=== {cand_set} × EVALUATION targets ===")
        r = run(cand_set, "EVALUATION")
        for L in ("A1", "A2", "A3", "A4", "A5"):
            s = r[L]
            print(f"  {L}: pairs={s['n_pairs']}  cands_matched={s['n_candidates_matched']}  "
                  f"targets_matched={s['n_targets_matched']}  {s['pairs'][:5]}")
