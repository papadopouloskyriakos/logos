#!/usr/bin/env python3
"""Feasibility simulation primitives — SYNTHETIC / within-script only. NEVER matches the real LA ritual
candidate sequences against the real LB ritual target sequences (that would be the forbidden real
matching). It reads the frozen packets only for their COUNTS, LENGTHS, and sign-frequency marginals."""
import json, os, random
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
GOLD = os.path.normpath(os.path.join(HERE, "..", "..", "data", "gold"))
RESULTS = os.path.normpath(os.path.join(HERE, "..", "..", "data", "results"))
SEED = 20260706


def _num(raw):
    out = []
    for s in raw:
        if s.startswith("AB") and s[2:].isdigit(): out.append(int(s[2:]))
        elif s.startswith("*") and s[1:].isdigit(): out.append(int(s[1:]))
        elif s.startswith("A") and s[1:].isdigit(): out.append(("A", int(s[1:])))
        else: out.append(s)
    return tuple(out)


def la_primary_seqs():
    rows = [json.loads(l) for l in open(f"{GOLD}/la_ritual_candidate_packet.jsonl")]
    return [_num(r["raw_sign_sequence"]) for r in rows if r["base_partition"] == "PRIMARY_RITUAL"]


def lb_eval_seqs():
    rows = [json.loads(l) for l in open(f"{GOLD}/lb_ritual_target_packet.jsonl")]
    return [_num(r["raw_sign_sequence"]) for r in rows if r["development_or_evaluation_role"] == "EVALUATION_TARGETS"]


def sign_freq(seqs):
    c = Counter()
    for s in seqs:
        c.update(x for x in s if isinstance(x, int))
    if not c:
        return [1], [1]
    signs, wts = zip(*c.items())
    return list(signs), list(wts)


def length_dist(seqs):
    return [len(s) for s in seqs] or [2]


def gen_seqs(n, lengths, signs, wts, rng):
    return [tuple(rng.choices(signs, weights=wts, k=rng.choice(lengths))) for _ in range(n)]


def count_exact(cseqs, tseqs):
    t = Counter(tseqs)
    return sum(t.get(c, 0) for c in cseqs)
