#!/usr/bin/env python3
"""decipher.py — the EM decipherment loop + CLI.

Runs the Berg-Kirkpatrick & Klein (2011) / Luo, Cao & Barzilay (2019) combinatorial EM:
alternate the E-step (:func:`align.best_align`) and M-step (:func:`maplearn.fit_map`) until
the substitution map ``phi`` stabilises (or ``max_iters``). Deterministic — no RNG.

  python3 scripts/decipher/decipher.py --demo
  python3 scripts/decipher/decipher.py --cipher cipher.txt --plain plain.txt \\
         [--pairs pairs.txt] [--truth truth.txt] [--iters 25] [--init frequency]

Wordlist files: one word per line, tokens whitespace-separated (e.g. ``c a t`` for a char
cipher, or ``KA RU PA`` for signs). ``--pairs`` lines are ``<cipher tokens>\\t<plain
tokens>``; ``--truth`` lines are ``<cipher token>\\t<plain token>``.

Citations:
  * Berg-Kirkpatrick & Klein (2011) — unsupervised decipherment via EM + weighted edit dist.
  * Luo, Cao & Barzilay (2019), "Neural Decipherment via Minimum-Cost Flow" (NeuroCipher) —
    the future NEURAL upgrade (differentiable alignment + true min-cost flow); this engine is
    the non-neural baseline it warm-starts from and is benchmarked against.
"""
import argparse
import os
import sys
from typing import Dict, List, Sequence, Tuple

# Allow running both as a module (python3 -m scripts.decipher.decipher) and as a script
# (python3 scripts/decipher/decipher.py) from the logos repo root.
if __package__ in (None, ""):
    _here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(_here)))  # repo root
    from scripts.decipher import align, maplearn, eval as evalmod, demo_fixture
else:
    from . import align, maplearn, eval as evalmod, demo_fixture


def load_words(path: str) -> List[Tuple[str, ...]]:
    """Load a wordlist: one word per line, tokens split on whitespace -> tuple."""
    out: List[Tuple[str, ...]] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            toks = line.split()
            if toks:
                out.append(tuple(toks))
    return out


def load_pairs(path: str) -> Dict[Tuple, Tuple]:
    """Load true cognate pairs: ``<cipher tokens>\\t<plain tokens>`` per line."""
    out: Dict[Tuple, Tuple] = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or "\t" not in line:
                continue
            left, right = line.split("\t", 1)
            c = tuple(left.split())
            p = tuple(right.split())
            if c and p:
                out[c] = p
    return out


def load_truth(path: str) -> Dict:
    """Load the ground-truth map: ``<cipher token>\\t<plain token>`` per line."""
    out: Dict = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or "\t" not in line:
                continue
            left, right = line.split("\t", 1)
            c = left.strip()
            p = right.strip()
            if c and p:
                out[c] = p
    return out


def identity_map(cipher_words: Sequence[Sequence]) -> Dict:
    """The iter-0 ``identity`` cold start: every cipher token maps to ITSELF.

    With this phi the substitution cost ``0 if phi.get(c)==p else sub_cost`` reduces to
    *standard Levenshtein* (a cipher token c vs a plain token p is free iff c == p). On
    DISJOINT alphabets (cipher symbols never equal plain symbols) this naturally degenerates
    to "every substitution costs sub_cost" — the length-driven cold start. On a SHARED
    alphabet it is ordinary edit distance, the meaningful baseline.
    """
    phi: Dict = {}
    for cw in cipher_words:
        for tok in cw:
            phi.setdefault(tok, tok)
    return phi


def run_em(
    cipher_words: Sequence[Sequence],
    plain_words: Sequence[Sequence],
    init: str = "frequency",
    max_iters: int = 25,
    sub_cost: float = 1.0,
    indel_cost: float = 1.0,
    max_len_delta: int = 2,
    top_k=None,
    verbose: bool = False,
) -> Tuple[Dict, Dict, List[Dict]]:
    """Run the EM decipherment loop. Returns ``(phi, alignments, history)``.

    ``history`` is a list of per-iteration dicts (for diagnostics): the iteration number, the
    number of aligned pairs, the mean edit distance under the current phi, and whether phi
    changed since the previous iteration.

    Cold start (``init``):
      * ``"identity"``  — phi = identity (c -> c); iter-0 E-step uses standard Levenshtein
                         (length-driven on disjoint alphabets, where it is degenerate: the
                         iter-0 length ties pile co-occurrence onto arbitrary words).
      * ``"frequency"`` — phi warm-started by frequency-rank matching
                         (:func:`maplearn.frequency_init`); the standard, principled cold
                         start (Snyder et al. 2010) that makes disjoint-alphabet recovery
                         work, and the default.
    """
    alignments: Dict = {}
    # Cold start.
    if init == "frequency":
        phi = maplearn.frequency_init(cipher_words, plain_words)
    elif init == "identity":
        phi = identity_map(cipher_words)
    else:
        raise ValueError(f"unknown init {init!r} (use 'identity' or 'frequency')")

    history: List[Dict] = []
    for it in range(max_iters):
        # E-step.
        alignments = align.best_align(
            cipher_words, plain_words, phi,
            sub_cost=sub_cost, indel_cost=indel_cost,
            max_len_delta=max_len_delta, top_k=top_k,
        )
        pairs = align.collect_pairs(alignments)
        med = evalmod.mean_edit_distance(alignments, phi, sub_cost, indel_cost)

        # M-step.
        new_phi = maplearn.fit_map(pairs)
        # Preserve any cold-start mappings for tokens the M-step did not observe this round
        # (keeps the frequency warm start alive across early iterations).
        merged = dict(phi)
        merged.update(new_phi)

        stable = (merged == phi)
        history.append(dict(iter=it, n_pairs=len(pairs), mean_edit=med, stable=stable,
                            n_mapped=len(merged)))
        if verbose:
            print(f"  [iter {it:2d}] pairs={len(pairs):5d}  mean_edit={med:.4f}  "
                  f"mapped={len(merged):3d}  stable={stable}")
        phi = merged
        if stable and it > 0:
            break  # converged

    return phi, alignments, history


def evaluate(phi, alignments, truth_map=None, true_pairs=None, cipher_words=None,
             plain_words=None, sub_cost=1.0, indel_cost=1.0, max_len_delta=2):
    """Compute the eval metrics dict. Missing ground truth => the relevant key is None."""
    best_matches = {cw: al[0] for cw, al in alignments.items()}
    med = evalmod.mean_edit_distance(alignments, phi, sub_cost, indel_cost)
    out = dict(
        mean_edit_distance=med,
        n_cipher_words=len(cipher_words) if cipher_words is not None else len(alignments),
        n_alignments=len(alignments),
        n_mapped=sum(1 for v in phi.values() if v is not None),
    )
    if truth_map:
        acc, nc, ne = evalmod.mapping_accuracy(phi, truth_map)
        out["mapping_accuracy"] = acc
        out["mapping_correct"] = nc
        out["mapping_evaluated"] = ne
    if true_pairs:
        cacc, ncc, nec = evalmod.cognate_accuracy(best_matches, true_pairs)
        out["cognate_accuracy"] = cacc
        out["cognate_correct"] = ncc
        out["cognate_evaluated"] = nec
        if cipher_words is not None and plain_words is not None:
            out["chance_cognate_accuracy"] = evalmod.chance_cognate_accuracy(
                cipher_words, plain_words, true_pairs, max_len_delta)
    return out


def _print_phi(phi, cipher_alphabet=None, limit=60):
    items = sorted(phi.items())
    if cipher_alphabet:
        order = {c: i for i, c in enumerate(cipher_alphabet)}
        items = sorted(phi.items(), key=lambda kv: (order.get(kv[0], 1 << 30), kv[0]))
    shown = items[:limit]
    print("learned phi (cipher -> plain):")
    for c, p in shown:
        print(f"    {c:>6} -> {p}")
    if len(items) > limit:
        print(f"    ... ({len(items) - limit} more)")


def _print_metrics(m):
    print("eval:")
    print(f"    n_cipher_words     : {m.get('n_cipher_words')}")
    print(f"    n_alignments       : {m.get('n_alignments')}")
    print(f"    n_mapped_tokens    : {m.get('n_mapped_tokens', m.get('n_mapped'))}")
    print(f"    mean_edit_distance : {m.get('mean_edit_distance'):.4f}")
    if "mapping_accuracy" in m:
        print(f"    mapping_accuracy   : {m['mapping_accuracy']:.4f}  "
              f"({m['mapping_correct']}/{m['mapping_evaluated']})")
    if "cognate_accuracy" in m:
        print(f"    cognate_accuracy   : {m['cognate_accuracy']:.4f}  "
              f"({m['cognate_correct']}/{m['cognate_evaluated']})")
    if "chance_cognate_accuracy" in m:
        print(f"    chance (null floor): {m['chance_cognate_accuracy']:.4f}")


def main(argv=None):
    ap = argparse.ArgumentParser(description="combinatorial/EM decipherment engine")
    ap.add_argument("--cipher", help="cipher wordlist (whitespace-tokenised, one/line)")
    ap.add_argument("--plain", help="plain wordlist (whitespace-tokenised, one/line)")
    ap.add_argument("--pairs", help="true cognate pairs for eval (tab-sep)")
    ap.add_argument("--truth", help="true cipher->plain token map for eval (tab-sep)")
    ap.add_argument("--iters", type=int, default=25, help="max EM iterations")
    ap.add_argument("--init", choices=("identity", "frequency"), default="frequency",
                    help="cold start (frequency is the principled default; identity is the "
                         "spec's empty-phi cold start)")
    ap.add_argument("--sub-cost", type=float, default=1.0)
    ap.add_argument("--indel-cost", type=float, default=1.0)
    ap.add_argument("--max-len-delta", type=int, default=2)
    ap.add_argument("--top-k", type=int, default=None)
    ap.add_argument("--demo", action="store_true", help="run the synthetic self-test fixture")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args(argv)

    if args.demo:
        fix = demo_fixture.default_fixture()
        cipher_words = fix["cipher_words"]
        plain_words = fix["plain_words"]
        truth_map = fix["truth_map"]
        true_pairs = fix["true_pairs"]
        cipher_alphabet = fix["cipher_alphabet"]
        print("=" * 70)
        print("DECIPHER — synthetic self-test (KNOWN ground-truth substitution map)")
        print("=" * 70)
        print(f"plain alphabet : {' '.join(fix['plain_alphabet'])}")
        print(f"cipher alphabet: {' '.join(cipher_alphabet)}")
        print(f"vocab size     : {len(plain_words)} plain words")
        print(f"cold start     : {args.init}")
        print("-" * 70)
    else:
        if not args.cipher or not args.plain:
            ap.error("--cipher and --plain are required (or use --demo)")
        cipher_words = load_words(args.cipher)
        plain_words = load_words(args.plain)
        truth_map = load_truth(args.truth) if args.truth else None
        true_pairs = load_pairs(args.pairs) if args.pairs else None
        cipher_alphabet = None
        print("=" * 70)
        print("DECIPHER — EM over a substitution map (cipher -> plain)")
        print("=" * 70)
        print(f"cipher words   : {len(cipher_words)}")
        print(f"plain words    : {len(plain_words)}")
        print(f"cold start     : {args.init}")
        print("-" * 70)

    phi, alignments, history = run_em(
        cipher_words, plain_words, init=args.init, max_iters=args.iters,
        sub_cost=args.sub_cost, indel_cost=args.indel_cost,
        max_len_delta=args.max_len_delta, top_k=args.top_k, verbose=args.verbose,
    )
    if args.verbose:
        print(f"converged in {len(history)} iteration(s)")

    metrics = evaluate(
        phi, alignments, truth_map=truth_map, true_pairs=true_pairs,
        cipher_words=cipher_words, plain_words=plain_words,
        sub_cost=args.sub_cost, indel_cost=args.indel_cost,
        max_len_delta=args.max_len_delta,
    )
    print("-" * 70)
    _print_phi(phi, cipher_alphabet=cipher_alphabet)
    print("-" * 70)
    _print_metrics(metrics)
    print("=" * 70)
    return metrics


if __name__ == "__main__":
    main()
