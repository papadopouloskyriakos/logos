#!/usr/bin/env python3
"""CANDIDATE-LANGUAGE ROUND 3 runner.

Families (prereg/candidate_round3_prereg.json):
  TYR_Etruscan            = Tyrrhenian / Etruscan-related (Bonfante 2002; Facchetti)
  AEG_isolate_substrate   = pre-Greek Aegean-isolate substrate model (Beekes 2014)
  CTRL_agnostic_random_r3 = agnostic random-lexicon negative control

Same rigorous protocol as round 1, via the shared engine. Honest expectation:
AT_END_TO_END_NULL. Deterministic seed 20260708. Reads only from the main worktree.
"""
from __future__ import annotations
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import candidate_engine as E  # noqa: E402

PREREG = os.path.join(HERE, "..", "prereg", "candidate_round3_prereg.json")
OUT = os.path.join(HERE, "..", "data", "candidate_round3_results.json")
MANIFEST = os.path.join(HERE, "..", "manifests", "candidate_round3_manifest.json")

if __name__ == "__main__":
    E.run_round(PREREG, OUT, MANIFEST, "candidate_language_round_3")
