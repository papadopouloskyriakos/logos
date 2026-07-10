#!/usr/bin/env python3
"""Machine-readable inventory of reusable corpus/method assets (generated, not hand-written)."""
import csv, hashlib, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
MAIN = "/home/claude-runner/gitlab/n8n/logos"
def h(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
assets = []
def add(path, kind, desc, licence, base=ROOT):
    p = os.path.join(base, path)
    if not os.path.exists(p): return
    assets.append({"path": path, "kind": kind, "sha256": h(p),
                   "bytes": os.path.getsize(p), "description": desc, "licence": licence})
add("experiments/E204R2_residual_canonicalization/CANONICAL_FRACTION_DATASET.csv", "dataset",
    "1,385 dual-parser-agreed Linear A fraction records (doc, locus, context word, logogram, integer, fraction sequence, restoration flag)",
    "campaign-derived from archived scholarly web corpus; internal factual use")
add("corpus/silver/inscriptions_structured.json", "dataset",
    "silver Linear A corpus: 1,341 inscriptions / 52 sites, structured words+context", "in-repo derivative", MAIN)
add("experiments/E201_replay_benchmark/harness.py", "instrument",
    "calibrated historical-replay harness (anchor ladders, abstention, leak detector); calibration certificate 0/200",
    "in-repo, open")
add("experiments/E203_identifiability_engine/engine.py", "instrument",
    "exact identifiability engine: CP-SAT constraint compilation + component-decomposition exact counting + MUS extraction", "in-repo, open")
add("experiments/E204_metrology/run_metrology_soft.py", "instrument",
    "soft metrological satisfiability pipeline w/ selection-aware whole-pipeline nulls", "in-repo, open")
add("experiments/E206_onomastic_linkage/stage2/run_stage2.py", "instrument",
    "qualified drift-matcher + canary battery + Holm framework for onomastic candidates", "in-repo, open")
add("rag/build_indexes.py", "instrument",
    "provenance-separated audit retrieval builder (5 epistemically separated FTS5 indexes; PIT cutoffs)", "in-repo, open")
add("verifiers/run_battery.py", "instrument",
    "closure verifier battery: wording/vocabulary/freeze/graph/append-only/seal checks", "in-repo, open")
add("experiments/E213_prospective_seal/SEALED_PREDICTIONS.json", "sealed-prediction",
    "2 sealed prospective predictions (sha256 5b50f21d…) scoreable on newly published inscriptions", "sealed; verify by hash only")
add("final/IDENTIFIABILITY_MAP.json", "result",
    "exact ambiguity by configuration + null adjudication + MUS core map", "open")
add("final/VALUE_OF_INFORMATION.csv", "result",
    "priced acquisition ranking (VOI per candidate evidence item)", "open")
out = {"generated": "2026-07-10", "campaign": "LOGOS-2 (closed)", "n_assets": len(assets), "assets": assets}
json.dump(out, open(os.path.join(HERE, "REUSABLE_ASSET_INVENTORY.json"), "w"), indent=1)
print(f"{len(assets)} assets inventoried")
