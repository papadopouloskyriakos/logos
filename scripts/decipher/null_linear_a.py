#!/usr/bin/env python3
"""null_linear_a.py — the LINEAR-A NULL (the mechanical "no signal" control).

Runs the decipher engine with REAL Linear A sign-sequences as the cipher against an
UNCORRELATED plain vocabulary (a stand-in for "Hebrew with no true cognacy"; we use a
built-in English list because no Hebrew lexicon is wired into the repo yet). Because there is
no true cognate relationship between the cipher and plain, NO consistent cipher-token ->
plain-token substitution can explain the pairings: the E-step's length-only alignments carry
no character signal, so the M-step's global assignment is arbitrary, and word-level cognate
accuracy collapses to the CHANCE FLOOR (mean 1 / #same-length-window candidates).

This is the logos discipline (invariant: "a decipherment is guilty until proven innocent"):
BEFORE claiming any Linear-A reading, we show the engine scores ~chance on a known-null pair,
i.e. it does not hallucinate signal where none exists. The synthetic self-test
(``decipher.py --demo``) shows the engine CAN reach ~100% when signal is real; this null shows
it does not invent signal when signal is absent.

    python3 scripts/decipher/null_linear_a.py --demo        # tiny built-in Linear A subset
    python3 scripts/decipher/null_linear_a.py               # real corpus/silver/inscriptions.json

Citations: Berg-Kirkpatrick & Klein (2011); Luo, Cao & Barzilay (2019).
"""
import argparse
import json
import os
import sys
from collections import Counter
from typing import Dict, List, Tuple

if __package__ in (None, ""):
    _here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(_here)))
    from scripts.decipher import decipher, eval as evalmod
else:
    from . import decipher, eval as evalmod

CORPUS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "corpus", "silver", "inscriptions.json",
)

# A tiny built-in Linear A subset (echoes the Libation Formula + common sequences) so --demo
# runs with no corpus dependency. Real signs from GORILA-derived transliteration.
DEMO_LINEAR_A = [
    ("A", "TA", "I", "X301", "WA", "JA"),
    ("A", "TA", "I", "X301", "WA", "JA", "DI", "KI", "TU"),
    ("QE", "RA2", "U", "KI", "RO"),
    ("MA", "DI", "NA", "QE", "RA2", "JA"),
    ("KU", "PA", "DA", "TA", "RA", "TE"),
    ("KA", "RU", "SI", "TU", "RA2", "RE"),
    ("A", "RE", "DU", "RI", "TE", "PA", "RE"),
    ("QE", "TI", "I", "RU", "RE", "TA"),
    ("WA", "DU", "NI", "MI", "RA", "TI", "SE"),
    ("MA", "SI", "WI", "DU"),
    ("SA", "RA", "ME", "NI", "DA"),
    ("KI", "RE", "TA", "NA", "RE"),
    ("PU", "KA", "NA", "TI", "RA"),
    ("DI", "KU", "PA3", "NU", "MA", "DI", "DA"),
    ("TI", "KA", "A", "RE", "DU", "RI"),
    ("NA", "KA", "NA", "SI", "RE", "TA"),
    ("QA", "QA", "RU", "MA", "TI"),
    ("I", "PI", "NA", "MA", "TA", "JA"),
    ("KU", "NI", "SU", "PA", "RA", "TI"),
    ("E", "NI", "SA", "DI", "KI", "TU"),
]

# Uncorrelated plain vocabulary (English). Linear A has NO cognacy with English, so this is a
# valid "Hebrew with no true cognacy" stand-in for the mechanical null. Lengths 3-8 letters to
# overlap the Linear A sign-sequence lengths within --max-len-delta.
UNCORRELATED_PLAIN = """
the and that than this sand hand land read dead head said sail nail rain
train brain drain trail soil road load toad dark lark mark bark shark
milk silk drink stink think thank tank rank sank bank dusk husk musk tusk
disk risk hike bike like dike dime lime time tame same name dame shade
blade trade grade mist list fist wrist roast toast hoist moist round mound
hound sound storm short shirt skirt snort thorn horn born torn worn lord
sword word north south mouth mouse house horse
""".split()


def _linear_a_words(path: str, min_len=2, max_len=12, limit=80) -> List[Tuple[str, ...]]:
    """Load Linear A inscriptions as sign-sequence 'words' (dedup, length-filtered)."""
    docs = []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    docs = data if isinstance(data, list) else data.get("inscriptions", [])
    seen = set()
    out: List[Tuple[str, ...]] = []
    for d in docs:
        signs = d.get("signs") or []
        if min_len <= len(signs) <= max_len:
            t = tuple(signs)
            if t not in seen:
                seen.add(t)
                out.append(t)
    # Deterministic ordering: most common lengths first then lexicographic.
    return out[:limit] if limit else out


def _english_words(limit=80) -> List[Tuple[str, ...]]:
    out = []
    seen = set()
    for w in UNCORRELATED_PLAIN:
        t = tuple(w.lower())
        if t not in seen and t:
            seen.add(t)
            out.append(t)
    return out[:limit]


def run_null(cipher_words, plain_words, max_len_delta=2, iters=25, init="frequency",
             sub_cost=1.0, indel_cost=1.0, verbose=False):
    """Run the engine on the null pair and return (phi, alignments, true_pairs, metrics).

    The "true pairs" are defined by INDEX position (cipher_words[i] <-> plain_words[i mod P]).
    There is no linguistic cognacy behind this pairing — it exists only so cognate accuracy
    has a reference to be measured against, and so the chance floor is well defined.
    """
    # Index-pair the two uncorrelated vocabularies (arbitrary, fixed).
    true_pairs: Dict[Tuple, Tuple] = {}
    for i, cw in enumerate(cipher_words):
        true_pairs[cw] = plain_words[i % len(plain_words)]

    phi, alignments, history = decipher.run_em(
        cipher_words, plain_words, init=init, max_iters=iters,
        sub_cost=sub_cost, indel_cost=indel_cost,
        max_len_delta=max_len_delta, top_k=None, verbose=verbose,
    )
    best_matches = {cw: al[0] for cw, al in alignments.items()}
    chance = evalmod.chance_cognate_accuracy(
        cipher_words, plain_words, true_pairs, max_len_delta)
    cacc, ncc, nec = evalmod.cognate_accuracy(best_matches, true_pairs)
    metrics = dict(
        cognate_accuracy=cacc, cognate_correct=ncc, cognate_evaluated=nec,
        chance_cognate_accuracy=chance,
        n_cipher_words=len(cipher_words), n_plain_words=len(plain_words),
        n_alignments=len(alignments),
        mean_edit_distance=evalmod.mean_edit_distance(alignments, phi, sub_cost, indel_cost),
        iters_run=len(history),
    )
    return phi, alignments, true_pairs, metrics


def main(argv=None):
    ap = argparse.ArgumentParser(description="Linear-A null decipherment control")
    ap.add_argument("--corpus", default=CORPUS, help="Linear A silver corpus (json)")
    ap.add_argument("--demo", action="store_true", help="use a tiny built-in Linear A subset")
    ap.add_argument("--limit", type=int, default=80, help="max cipher words")
    ap.add_argument("--iters", type=int, default=25)
    ap.add_argument("--init", choices=("identity", "frequency"), default="frequency")
    ap.add_argument("--max-len-delta", type=int, default=2)
    ap.add_argument("--sub-cost", type=float, default=1.0)
    ap.add_argument("--indel-cost", type=float, default=1.0)
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args(argv)

    if args.demo:
        cipher_words = list(DEMO_LINEAR_A)[:args.limit]
        src = "built-in tiny Linear A subset (Libation-Formula-flavoured)"
    else:
        if not os.path.exists(args.corpus):
            ap.error(f"corpus not found at {args.corpus} (run with --demo)")
        cipher_words = _linear_a_words(args.corpus, limit=args.limit)
        src = args.corpus
    plain_words = _english_words()

    print("=" * 70)
    print("LINEAR-A NULL  (no cognate target -> map cannot be pinned)")
    print("=" * 70)
    print(f"cipher source  : {src}")
    print(f"cipher words   : {len(cipher_words)}  (Linear A sign-sequences)")
    inv = Counter(s for w in cipher_words for s in w)
    print(f"cipher signs   : {len(inv)} unique  (top: {', '.join(f'{s}({n})' for s,n in inv.most_common(5))})")
    print(f"plain words    : {len(plain_words)}  (English — uncorrelated, no cognacy)")
    print(f"cold start     : {args.init}")
    print("-" * 70)
    if args.verbose:
        print("EM trace:")

    phi, alignments, true_pairs, metrics = run_null(
        cipher_words, plain_words, max_len_delta=args.max_len_delta, iters=args.iters,
        init=args.init, sub_cost=args.sub_cost, indel_cost=args.indel_cost, verbose=args.verbose)

    print("-" * 70)
    print("RESULT:")
    print(f"    cognate_accuracy   : {metrics['cognate_accuracy']:.4f}  "
          f"({metrics['cognate_correct']}/{metrics['cognate_evaluated']})")
    print(f"    chance (null floor): {metrics['chance_cognate_accuracy']:.4f}")
    print(f"    mean_edit_distance : {metrics['mean_edit_distance']:.4f}")
    print(f"    iters run          : {metrics['iters_run']}")
    # A few of the learned (arbitrary) sign->letter assignments, to show they carry no sense.
    sample = sorted(phi.items())[:12]
    print("    learned phi sample (arbitrary — no consistent map exists by construction):")
    for s, p in sample:
        print(f"        {s:>6} -> {p}")
    print("-" * 70)
    acc = metrics["cognate_accuracy"]
    chance = metrics["chance_cognate_accuracy"]
    # "At chance" if within a small band of the floor (allow a little slack above).
    band = max(0.05, 1.5 * chance)
    verdict = ("AT CHANCE" if acc <= chance + band else
               "ABOVE CHANCE (unexpected — investigate spurious signal)")
    print(f"VERDICT: cognate accuracy {acc:.4f} vs chance {chance:.4f} -> {verdict}")
    print("        (no cognate target => the map cannot be pinned; this is the null.)")
    print("=" * 70)
    return metrics


if __name__ == "__main__":
    main()
