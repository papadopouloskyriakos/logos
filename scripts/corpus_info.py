#!/usr/bin/env python3
"""corpus_info.py — corpus statistics + the information floor (unicity distance).

The decisive number for any Linear A decipherment claim: given the corpus, is a
hypothesized phonetic map even *determinable*? Shannon's unicity distance U = H(K)/D
says how much ciphertext is needed to uniquely recover the "key" (here, the sign->sound
map). If U exceeds the available text N, no amount of cleverness can CONFIRM a unique
decipherment -- any internally-consistent reading is merely one of many that fit.

This is an honest information-balance estimate, NOT false precision:
  H(K)   = key/search-space entropy of the map = V * log2(P)   (V signs, P possible values)
  D      = per-symbol redundancy of the script's OWN observed sign sequences
           = log2(V) - H_rate   (H_rate = bigram conditional entropy, an upper bound on
             the true entropy rate; converges down with more data)
  U      = H(K) / D

ASSUMPTION (stated, not hidden): we use the script's own measured redundancy as a proxy
for the (unknown) plaintext language's redundancy. Defensible because the script encodes
a natural language, so the sign-sequence redundancy reflects the language's redundancy
modulo the script's efficiency. The true language's D is the irreducible uncertainty;
we BRACKET it, never pretend to resolve it. Vary --phonemes to bracket the other way.

Pure stdlib (mirrors agora_stats.py). No corpus needed to prove the harness:

    python3 scripts/corpus_info.py --demo

Once GORILA/SigLA is ingested into corpus/silver/:

    python3 scripts/corpus_info.py --corpus corpus/silver/inscriptions.json
"""
import argparse
import json
import math
import os
from collections import Counter


def _read_corpus(path):
    """Read silver corpus: JSON list of {id, site, signs:[str,...]} or JSONL, one per line."""
    docs = []
    if not os.path.exists(path):
        return docs
    if path.endswith(".jsonl"):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    docs.append(json.loads(line))
    else:
        with open(path) as f:
            data = json.load(f)
        docs = data if isinstance(data, list) else data.get("inscriptions", [])
    return [d for d in docs if d.get("signs")]


def _entropy(counter, total):
    if total <= 0:
        return 0.0
    return -sum((c / total) * math.log2(c / total) for c in counter.values() if c)


def stats(docs):
    """N, inventory size V, unigram entropy H0, and bigram conditional entropy H_rate."""
    seqs = [d["signs"] for d in docs]
    flat = [s for seq in seqs for s in seq]
    n = len(flat)
    uni = Counter(flat)
    V = len(uni)
    h0 = _entropy(uni, n)
    # bigrams WITHIN an inscription only (no spurious cross-boundary pairs)
    bi = Counter()
    ctx = Counter()
    for seq in seqs:
        for a, b in zip(seq, seq[1:]):
            bi[(a, b)] += 1
            ctx[a] += 1
    bi_total = sum(bi.values())
    h_joint = _entropy(bi, bi_total)        # H(A,B)
    h_ctx = _entropy(ctx, bi_total)         # H(A) over the bigram sample
    h_rate = max(0.0, min(h_joint - h_ctx, h0))   # H(B|A); upper bound on true rate
    return dict(n_ins=len(docs), n=n, V=V, h0=h0, h_rate=h_rate, bi_total=bi_total)


def unicity(V, h_rate, phonemes):
    logV = math.log2(V) if V else 0.0
    D = logV - h_rate                              # per-symbol redundancy (>=0 normally)
    H_K = V * math.log2(phonemes) if phonemes else 0.0
    U = (H_K / D) if D > 1e-9 else float("inf")    # chars needed to uniquely fix the map
    return dict(logV=logV, D=D, H_K=H_K, U=U)


def report(st, un, args):
    print("=" * 66)
    print("CORPUS INFORMATION FLOOR   (logos / corpus_info.py)")
    print("=" * 66)
    print(f"inscriptions            : {st['n_ins']}")
    print(f"total signs (N)         : {st['n']}")
    print(f"unique inventory (V)    : {st['V']}")
    print(f"unigram entropy H0      : {st['h0']:.3f} bits/sign")
    print(f"entropy rate H_rate     : {st['h_rate']:.3f} bits/sign  (bigram cond.; UPPER bound)")
    print("-" * 66)
    print(f"value set P             : {args.phonemes}  ->  log2(P) = {math.log2(args.phonemes):.3f}")
    print(f"max info / sign log2(V) : {un['logV']:.3f}")
    print(f"redundancy D            : {un['D']:.3f} bits/sign   (= log2(V) - H_rate)")
    print(f"map key entropy H(K)    : {un['H_K']:.0f} bits   (= V * log2(P))")
    u = un["U"]
    us = "INF  (no measured redundancy -> unicity undefined)" if u == float("inf") else f"{u:,.0f} signs"
    print(f"unicity distance U      : {us}   (= H(K) / D)")
    print("-" * 66)
    if u == float("inf"):
        verdict = "UNDERDETERMINED: zero measured redundancy -> a map cannot be pinned."
    elif st["n"] and u > st["n"]:
        verdict = (f"UNDERDETERMINED: ~{u:,.0f} signs needed to uniquely fix the map, "
                   f"only {st['n']:,} exist (gap {u - st['n']:,.0f}).")
    else:
        verdict = (f"potentially determinable: U ({u:,.0f}) <= N ({st['n']:,}) "
                   f"-- proceed to held-out tests.")
    print(f"VERDICT                 : {verdict}")
    print("=" * 66)


# A toy fixture (echoes the Libation Formula A-TA-I-*301-WA-JA across sites) so the
# harness is provably runnable before any real corpus is ingested.
DEMO = [
    {"id": "IOZa2", "site": "iouktas", "signs": ["A", "TA", "I", "X301", "WA", "JA", "JA", "DI", "KI", "TU"]},
    {"id": "PKZa1", "site": "psychro", "signs": ["A", "TA", "I", "X301", "WA", "JA", "JA", "SA", "SA", "RA", "ME"]},
    {"id": "PHZa1", "site": "phia",   "signs": ["A", "TA", "I", "X301", "WA", "JA", "U", "NA", "KA", "NA", "SI"]},
    {"id": "KNZa1", "site": "knossos", "signs": ["A", "TA", "I", "X301", "WA", "JA", "I", "PI", "NA", "MA"]},
    {"id": "list1", "site": "knossos", "signs": ["KU", "RO", "3"]},
]


def main():
    ap = argparse.ArgumentParser(description="corpus statistics + unicity-distance estimate")
    ap.add_argument("--corpus", default="corpus/silver/inscriptions.json",
                    help="silver corpus path (json list or jsonl)")
    ap.add_argument("--phonemes", type=int, default=60,
                    help="size of the value set P each sign maps onto (syllabary ~60; phoneme ~30)")
    ap.add_argument("--demo", action="store_true", help="run on the built-in tiny fixture")
    args = ap.parse_args()

    docs = DEMO if args.demo else _read_corpus(args.corpus)
    if not docs:
        print(f"no corpus found at {args.corpus} (and --demo not set).")
        print("ingest GORILA/SigLA -> corpus/silver/ (see docs/references.md), or run --demo.")
        return

    st = stats(docs)
    un = unicity(st["V"], st["h_rate"], args.phonemes)
    report(st, un, args)


if __name__ == "__main__":
    main()
