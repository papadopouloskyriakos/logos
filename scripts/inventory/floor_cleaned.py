#!/usr/bin/env python3
"""floor_cleaned.py -- Recompute the information floor on the CLEANED syllabogram stream.

Redteam (docs/findings/2026-06-30-expert-redteam-synthesis.md §1/§5):
  - The strong unicity conclusion is WITHDRAWN. This number is retained ONLY as a
    TOY-MODEL PRECONDITION diagnostic: "under a narrow symbol-substitution toy model,
    the corpus shows MEASURABLE RECURRENT STRUCTURE" -- NOT that a decipherment is
    identifiable. Unicity distance assumes a known plaintext-language oracle; measuring
    the redundancy D from the ciphertext makes that oracle = Linear A up to relabelling.
    If Linear A underspells (as Linear B does), the channel is lossy/non-injective and
    may have NO unicity distance at all. The real info-sufficiency test is
    pseudo-decipherment learning curves (downsample Linear B) -- task #16.
  - "Clean BEFORE the floor": logograms + numerals + fractions + ligatures contaminate
    both H_rate and any char map, so the floor is recomputed on the syllabogram-only
    stream from build_ontology.py.

PRIMARY  = conservative ~90-syllabogram stream (AB + clearly-A-only; ligatures decomposed;
           logograms/numerals/fractions/damaged separated out).
SENSITIVITY (two rows):
  (a) raw silver stream V=259 (all tokens conflated -- the old, contaminated number),
  (b) raw syllabogram stream V~131 (all syllabogram-class tokens, ligatures as single
      symbols -- shows the effect of curating the channel but not yet merging allographs).

Reuses the EXACT formulas in scripts/corpus_info.py (stats / unicity), over the (V,P)
grid, so the only thing that changes vs the withdrawn claim is the inventory. Pure stdlib.
"""
import argparse
import json
import math
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SILVER = os.path.join(ROOT, "corpus", "silver")

# import the floor math from the sibling module (no reimplementation)
import sys
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from corpus_info import stats as _stats_docs, unicity, _entropy  # noqa: E402


def _entropy_from_seqs(seqs):
    """N, V, H0, H_rate over per-inscription id sequences (bigrams WITHIN an
    inscription only -- mirrors corpus_info.stats, which we also call directly)."""
    docs = [{"id": i, "site": "", "signs": s} for i, s in enumerate(seqs)]
    return _stats_docs(docs)


def _grid_row(st, phonemes):
    un = unicity(st["V"], st["h_rate"], phonemes)
    return {
        "P": phonemes, "log2P": round(math.log2(phonemes), 3),
        "D": round(un["D"], 3),
        "H_K": round(un["H_K"], 1),
        "U": (None if un["U"] == float("inf") else round(un["U"])),
        "U_le_N": (un["U"] <= st["n"]) if un["U"] != float("inf") else False,
    }


def _print_block(title, st, note):
    print("-" * 72)
    print(title)
    print("-" * 72)
    print(f"  inscriptions used    : {st['n_ins']}")
    print(f"  total signs (N)      : {st['n']}")
    print(f"  unique inventory (V) : {st['V']}")
    print(f"  unigram entropy H0   : {st['h0']:.3f} bits/sign")
    print(f"  entropy rate H_rate  : {st['h_rate']:.3f} bits/sign  (bigram cond.; UPPER bound)")
    D = (math.log2(st["V"]) - st["h_rate"]) if st["V"] else 0.0
    print(f"  redundancy D         : {D:.3f} bits/sign  (= log2(V) - H_rate)")
    if note:
        print(f"  note                 : {note}")
    print()
    print("  unicity U = H(K)/D,  H(K) = V*log2(P),  over the (V,P) grid:")
    print(f"  {'P':>4} {'log2P':>7} {'D':>7} {'H(K)':>9} {'U':>9}  U<=N?")
    for p in (30, 60, 90):
        r = _grid_row(st, p)
        us = "INF" if r["U"] is None else f"{r['U']:,.0f}"
        print(f"  {r['P']:>4} {r['log2P']:>7} {r['D']:>7} {r['H_K']:>9} {us:>9}  {r['U_le_N']}")
    u30 = _grid_row(st, 30)["U"]
    gap = (u30 - st["n"]) if u30 is not None else None
    if u30 is None:
        verdict = "no measured redundancy -> unicity undefined"
    elif u30 > st["n"]:
        verdict = (f"UNDERDETERMINED (toy): ~{u30:,.0f} signs needed, only {st['n']:,} exist "
                   f"(gap {gap:,.0f}).")
    else:
        verdict = (f"recurrent structure measurable (toy): U({u30:,.0f}) <= N({st['n']:,}).")
    print()
    print(f"  TOY VERDICT (P=30)   : {verdict}")
    print(f"  -- NOT an identifiability claim. See redteam synthesis §1; real test = task #16.")


def main():
    ap = argparse.ArgumentParser(description="Information floor on cleaned syllabogram stream")
    ap.add_argument("--silver", default=os.path.join(SILVER, "inscriptions.json"))
    ap.add_argument("--cons", default=os.path.join(SILVER,
                        "inventory_syllabograms_conservative.stream.json"))
    ap.add_argument("--expl", default=os.path.join(SILVER,
                        "inventory_syllabograms_exploratory.stream.json"))
    ap.add_argument("--rawsyll", default=os.path.join(SILVER,
                        "inventory_syllabograms_raw.stream.json"))
    args = ap.parse_args()

    print("=" * 72)
    print("INFORMATION FLOOR ON CLEANED SYLLABOGRAM STREAM   (floor_cleaned.py)")
    print("=" * 72)
    print("Toy-model precondition ONLY. The unicity refutation was WITHDRAWN")
    print("(redteam synthesis §1): U<=N shows measurable structure, NOT that a")
    print("decipherment is identifiable. Real test = pseudo-decipherment curves (#16).")
    print("Reuses scripts/corpus_info.py formulas verbatim; only the inventory changes.")

    # ---- PRIMARY: conservative cleaned stream ----
    with open(args.cons) as f:
        cons = json.load(f)
    st_cons = _entropy_from_seqs(cons["sequences"])

    # ---- SENSITIVITY (a): raw silver V=259 (contaminated, the old number) ----
    with open(args.silver) as f:
        docs = json.load(f)
    docs = [d for d in docs if d.get("signs")]
    st_raw259 = _stats_docs(docs)

    # ---- SENSITIVITY (b): raw syllabogram stream V~131 (curated channel, no merges) ----
    with open(args.rawsyll) as f:
        rawsyll = json.load(f)
    st_rawsyll = _entropy_from_seqs(rawsyll["sequences"])

    # ---- SENSITIVITY (c): exploratory stream V~88 (aggressive allograph merges) ----
    with open(args.expl) as f:
        expl = json.load(f)
    st_expl = _entropy_from_seqs(expl["sequences"])

    _print_block("PRIMARY -- conservative cleaned syllabogram stream (V~90)",
                 st_cons, "logograms/numerals/fractions/ligatures SEPARATED OUT; "
                          "clearly-A-only + AB; ligatures decomposed.")
    _print_block("SENSITIVITY -- exploratory stream (V~88, aggressive merges)",
                 st_expl, "conservative + subscripted AB collapsed into base family "
                          "(RA2->RA, PA3->PA ...). Lower bound on the syllabary size.")
    _print_block("SENSITIVITY -- raw syllabogram stream (V~131)",
                 st_rawsyll, "syllabogram-class tokens only, but NO allograph merges; "
                             "ligatures counted as single symbols; hapax A-only included.")
    _print_block("SENSITIVITY -- raw silver conflated stream (V=259)",
                 st_raw259, "the OLD, contaminated number: syllabograms + logograms + "
                            "numerals + ligatures all in one inventory.")

    print("=" * 72)
    print("SIDE-BY-SIDE  (N, V, H0, H_rate, D at log2(V))")
    print("=" * 72)
    print(f"  {'stream':42} {'N':>6} {'V':>5} {'H0':>7} {'H_rate':>8} {'D':>7}")
    for name, st in [("conservative cleaned (PRIMARY)", st_cons),
                     ("exploratory aggressive merges", st_expl),
                     ("raw syllabogram (sensitivity)", st_rawsyll),
                     ("raw silver V=259 (sensitivity)", st_raw259)]:
        D = (math.log2(st["V"]) - st["h_rate"]) if st["V"] else 0.0
        print(f"  {name:42} {st['n']:>6} {st['V']:>5} {st['h0']:>7.3f} "
              f"{st['h_rate']:>8.3f} {D:>7.3f}")
    print("=" * 72)


if __name__ == "__main__":
    main()
