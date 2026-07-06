#!/usr/bin/env python3
"""Shared frozen config for the §IX–§XV ADMINISTRATIVE_TOPONYM_CONTINUITY analysis.

All randomness is seeded from SEED; every Monte-Carlo count below is deterministic given these values.
Membership manifests (packet A / packet B) are READ-ONLY here and must not change (a defect → STOP →
manifest-v2 → new freeze review, per the authorization)."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
GOLD = os.path.normpath(os.path.join(HERE, "..", "..", "data", "gold"))
LA_PACKET = os.path.join(GOLD, "la_candidate_packet.jsonl")          # committed, raw sign IDs
LB_PACKET = os.path.join(GOLD, "lb_toponym_target_manifest.jsonl")   # committed
RESULTS = os.path.normpath(os.path.join(HERE, "..", "..", "data", "results"))

SEED = 20260706
N_NULL = 4000        # Monte-Carlo draws per null family
N_POWER = 1500       # draws per power grid cell
ANALYSIS_VERSION = "admin-toponym-continuity-v1-2026-07-06"

# frozen input hashes (verified at run start; anti-drift)
EXPECT_SHA = {
    LA_PACKET: "eb2bb2933daf40c292e1169a181876463ad1d938d3268a88d8bbed1c7eec0e48",
    LB_PACKET: "29e25d49535183207f77ab24dec5da9d0b31cbff38c48d81099871f2285c1bba",
}


def sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()


def verify_inputs():
    bad = {p: sha256(p) for p, exp in EXPECT_SHA.items() if sha256(p) != exp}
    if bad:
        raise RuntimeError(f"FROZEN INPUT DRIFT — STOP, do not score. {bad}")
    return True
