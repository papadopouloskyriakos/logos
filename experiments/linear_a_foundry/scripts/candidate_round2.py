#!/usr/bin/env python3
"""CANDIDATE-LANGUAGE ROUND 2 runner.

Families (prereg/candidate_round2_prereg.json):
  HUR_Hurrian            = Hurro-Urartian (Wegner 2000; Wilhelm 1989)
  LUW2_Luwian            = Luwian / Anatolian-2 (Melchert 1993; Yakubovich 2010)
  CTRL_agnostic_random_r2 = agnostic random-lexicon negative control

Same rigorous protocol as round 1, via the shared engine. Honest expectation:
AT_END_TO_END_NULL. Deterministic seed 20260708. Reads only from the main worktree.
"""
from __future__ import annotations
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import candidate_engine as E  # noqa: E402

PREREG = os.path.join(HERE, "..", "prereg", "candidate_round2_prereg.json")
OUT = os.path.join(HERE, "..", "data", "candidate_round2_results.json")
MANIFEST = os.path.join(HERE, "..", "manifests", "candidate_round2_manifest.json")

if __name__ == "__main__":
    E.run_round(PREREG, OUT, MANIFEST, "candidate_language_round_2")
