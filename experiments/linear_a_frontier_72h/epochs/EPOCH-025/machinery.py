"""EPOCH-025 core machinery: A- prefix PRODUCTIVITY (adversarial leave-top-type-out).

Reuses the E024 within-word uniform-permutation null (imported). Adds:
  - word-type extraction (full sign-sequence tuples)
  - leave-top-k-type-out robustness for a given initial sign
  - LB positive control with PRODUCTIVE vs FEW-TYPE separation
  - comparator type-diversity sweep
"""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
E024 = os.path.normpath(os.path.join(HERE, "..", "EPOCH-024"))
if E024 not in sys.path:
    sys.path.insert(0, E024)
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("e024mach", os.path.join(E024, "machinery.py"))
e024mach = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(e024mach)
permutation_null = e024mach.permutation_null
permutation_null_fast = e024mach.permutation_null_fast
a_initial_count = e024mach.a_initial_count

import numpy as np
from collections import Counter

CORPUS = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "corpus", "silver", "inscriptions_structured.json"))


def load_la_words():
    """Return list of sign-lists for >=2-sign words (order preserved)."""
    d = json.load(open(CORPUS))
    out = []
    for ins in d:
        for tok in ins.get("stream", []):
            if tok.get("t") == "word":
                sg = tok.get("signs", [])
                if len(sg) >= 2:
                    out.append(list(sg))
    return out


def distinct_types_and_seconds(words, sign):
    """Among >=2-sign words whose first sign == `sign`:
       return (n_distinct_word_types, n_distinct_second_signs, Counter of word-types)."""
    init = [tuple(w) for w in words if len(w) >= 2 and w[0] == sign]
    types = Counter(init)
    seconds = Counter(w[1] for w in init)
    return len(types), len(seconds), types


def leave_top_k_type_out(words, sign, k, n_draws=1000, seed=0):
    """Remove all occurrences of the top-k most-frequent `sign`-initial word-types,
       then recompute sign-initial count + null p on the REMAINING >=2-sign words.
       Returns dict. k>=1."""
    init_types = Counter(tuple(w) for w in words if len(w) >= 2 and w[0] == sign)
    topk = set(t for t, _ in init_types.most_common(k))
    remaining = [w for w in words if len(w) >= 2 and tuple(w) not in topk]
    if len(remaining) == 0:
        return {"k": k, "removed_types": [list(t) for t in sorted(topk)],
                "remaining_n": 0, "remaining_sign_initial": 0, "remaining_p": 1.0,
                "null_mean": 0.0, "underpowered": True}
    obs, nc, p, mean = permutation_null_fast(remaining, sign, n_draws, seed=seed)
    return {"k": k, "removed_types": [list(t) for t in sorted(topk)],
            "remaining_n": len(remaining), "remaining_sign_initial": obs,
            "remaining_p": p, "null_mean": round(mean, 3), "underpowered": False}


def comparator_type_diversity(words, sign, top_n=5):
    """For `sign` and the top_n next-most-word-initial signs, return dict
       sign -> n_distinct_initial_word-types."""
    init_counts = Counter(w[0] for w in words if len(w) >= 2)
    # comparator pool: signs that are word-initial at least once, excluding `sign`
    pool = [(s, c) for s, c in init_counts.items() if s != sign]
    pool.sort(key=lambda x: x[1], reverse=True)
    chosen = [sign] + [s for s, _ in pool[:top_n]]
    out = {}
    for s in chosen:
        types = Counter(tuple(w) for w in words if len(w) >= 2 and w[0] == s)
        out[s] = len(types)
    return out


def lb_positive_control(n_draws=1000, seed=11):
    """LB PC: exhibit PRODUCTIVE vs FEW-TYPE separation via leave-top-type-out.
       (a) PRODUCTIVE initial sign: strongly word-initial AND spans many distinct
           initial word-types. Must (i) be sig under null AND (ii) SURVIVE removing
           its single most-frequent initial word-type.
       (b) FEW-TYPE / mono-word initial sign: a sign that IS globally significant
           (so collapse is demonstrable) but whose initial occurrences are concentrated
           in 1-2 word-types. Must COLLAPSE (lose sig, p>0.05) when its top word-type
           is removed.
       Selection is principled and data-driven (no hand-picking):
         - PRODUCTIVE = globally-sig sign with the MOST distinct initial word-types
           (high type-diversity) among high-frequency signs.
         - FEW-TYPE   = globally-sig sign with the HIGHEST top-type-share
           (top_type_count / initial_count), i.e. most concentrated.
       Returns dict with pc_verdict PASSED/FAILED."""
    import statistics
    REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
    if REPO not in sys.path:
        sys.path.insert(0, REPO)
    from scripts.cross_script.data import load_b_damos
    seqs, freq, v2g = load_b_damos()
    ge2 = [w for w in seqs if len(w) >= 2]
    init = Counter(w[0] for w in ge2)
    types_by_sign = {}
    for w in ge2:
        types_by_sign.setdefault(w[0], Counter())[tuple(w)] += 1

    # candidate initial signs: occ>=20, initial>=15 (enough to test significance)
    cands = []
    for s in freq:
        if freq[s] >= 20 and init.get(s, 0) >= 15:
            ntypes = len(types_by_sign.get(s, {}))
            top_share = types_by_sign[s].most_common(1)[0][1] / init[s]
            cands.append((s, init[s], freq[s], ntypes, top_share))
    if len(cands) < 4:
        return {"pc_verdict": "FAILED", "reason": "too few LB candidate signs"}

    # Step 1: determine global significance for each candidate
    sig_rows = []
    for s, ini, occ, ntypes, top_share in cands:
        obs, nc, p, mean = permutation_null_fast(ge2, s, n_draws, seed=seed + hash(s) % 1000)
        sig_rows.append((s, ini, occ, ntypes, top_share, p))
    globally_sig = [r for r in sig_rows if r[5] <= 0.05]
    if len(globally_sig) < 4:
        return {"pc_verdict": "FAILED", "reason": "too few globally-significant LB signs"}

    # PRODUCTIVE: among globally-sig, the one with MOST distinct initial word-types
    globally_sig.sort(key=lambda r: r[3], reverse=True)
    prod_sign = globally_sig[0][0]

    # FEW-TYPE: among globally-sig (excluding prod_sign), the one with HIGHEST top_share
    few_pool = [r for r in globally_sig if r[0] != prod_sign]
    few_pool.sort(key=lambda r: r[4], reverse=True)
    few_sign = few_pool[0][0]

    def test_sign(s):
        obs, nc, p, mean = permutation_null_fast(ge2, s, n_draws, seed=seed)
        top_type = types_by_sign[s].most_common(1)[0][0]
        rem = [w for w in ge2 if tuple(w) != top_type]
        if len(rem) == 0:
            return p, 1.0, top_type, 0, 0
        o2, nc2, p2, m2 = permutation_null_fast(rem, s, n_draws, seed=seed + 1)
        return p, p2, top_type, len(rem), o2

    p_prod, p_prod_lo, prod_top, prod_rem_n, prod_rem_init = test_sign(prod_sign)
    p_few, p_few_lo, few_top, few_rem_n, few_rem_init = test_sign(few_sign)

    prod_ok = (p_prod <= 0.05) and (p_prod_lo <= 0.05)
    few_collapses = (p_few <= 0.05) and (p_few_lo > 0.05)
    passed = prod_ok and few_collapses

    return {
        "pc_verdict": "PASSED" if passed else "FAILED",
        "productive_sign": prod_sign,
        "productive_sign_occ": int(freq[prod_sign]),
        "productive_sign_initial": int(init[prod_sign]),
        "productive_n_distinct_initial_types": len(types_by_sign[prod_sign]),
        "productive_p_global": round(p_prod, 4),
        "productive_p_leave_top_type_out": round(p_prod_lo, 4),
        "productive_top_type": list(prod_top),
        "productive_survives": bool(prod_ok),
        "monoword_sign": few_sign,
        "monoword_sign_occ": int(freq[few_sign]),
        "monoword_sign_initial": int(init[few_sign]),
        "monoword_n_distinct_initial_types": len(types_by_sign[few_sign]),
        "monoword_p_global": round(p_few, 4),
        "monoword_p_leave_top_type_out": round(p_few_lo, 4),
        "monoword_top_type": list(few_top),
        "monoword_collapses": bool(few_collapses),
        "monoword_top_type_share_of_initial": round(
            types_by_sign[few_sign].most_common(1)[0][1] / init[few_sign], 4),
        "selection_rule": "PRODUCTIVE = globally-sig sign with most distinct initial types; "
                          "FEW-TYPE = globally-sig sign with highest top-type-share",
    }



def verdict(pc_passed, leave1_p, n_distinct_A_types, a_diversity, comp_diversity):
    """Frozen mechanical verdict. comp_diversity is the dict from comparator_type_diversity
       (includes 'A'). a_diversity = comp_diversity['A']."""
    if not pc_passed:
        return "MACHINERY_UNINFORMATIVE"
    comps = [v for k, v in comp_diversity.items() if k != "A"]
    comp_median = float(np.median(comps)) if comps else 0.0
    if leave1_p <= 0.05 and n_distinct_A_types >= 8 and a_diversity > comp_median:
        return "A_PREFIX_PRODUCTIVE_ROBUST"
    if leave1_p > 0.05 or n_distinct_A_types < 8 or a_diversity <= comp_median:
        return "A_PREFIX_FEW_TYPE_DRIVEN"
    return "A_PREFIX_UNDERPOWERED"


if __name__ == "__main__":
    print("=== EPOCH-025 machinery self-check ===")
    words = load_la_words()
    print("LA >=2-sign words:", len(words))
    nd, ns, types = distinct_types_and_seconds(words, "A")
    print(f"A: n_distinct_types={nd} n_distinct_second_signs={ns}")
    print("top A types:", types.most_common(5))
    obs, nc, p, mean = permutation_null_fast(words, "A", 1000, seed=0)
    print(f"GLOBAL A-initial: {obs}/{len(words)} frac={obs/len(words):.4f} null_mean={mean:.2f} p={p:.4f}")
    lo1 = leave_top_k_type_out(words, "A", 1, seed=1)
    lo2 = leave_top_k_type_out(words, "A", 2, seed=2)
    lo3 = leave_top_k_type_out(words, "A", 3, seed=3)
    print("leave-top-1:", lo1["remaining_n"], lo1["remaining_sign_initial"], "p=", lo1["remaining_p"])
    print("leave-top-2:", lo2["remaining_n"], lo2["remaining_sign_initial"], "p=", lo2["remaining_p"])
    print("leave-top-3:", lo3["remaining_n"], lo3["remaining_sign_initial"], "p=", lo3["remaining_p"])
    div = comparator_type_diversity(words, "A", top_n=5)
    print("type diversity:", div)
    print("\nLB positive control:")
    pc = lb_positive_control()
    for k, v in pc.items():
        print(f"  {k}: {v}")
    print("\nSelf-check OK.")
