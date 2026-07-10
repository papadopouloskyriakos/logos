# Reproducing LOGOS-2

Branch `research/logos2-anchor-identifiability`; all paths below relative to
`research/logos2/`. Master seed **1336530913**; every run derives per-cell seeds as
`sha256(master|experiment|cell|fold|replicate)` — no global RNG state is inherited.

## Environment
```bash
python3 -m venv .venv && .venv/bin/pip install ortools z3-solver python-sat scipy numpy pytest
```
(The committed `.venv` used OR-Tools CP-SAT for E203/E204, exact model counting via
component decomposition, scipy for Clopper–Pearson bounds.)

## One-command verifier
```bash
.venv/bin/python verifiers/run_battery.py
```
PASS required at closure. Checks: banned-wording sweep (disclaimer-aware), frozen status
vocabulary, every `*.sha256` freeze (with `*.sha256.ERRATUM.md` append-only coverage),
E212 graph finalization, append-only as-run preservation, E213 seal integrity *without
opening*. `PROTECTED_ASSET_HASHES.sha256` paths resolve against the MAIN worktree.

## Per-experiment re-execution (order-free unless noted)
```bash
# E203 identifiability engine + confirmatory (exact counts, MUS, 200+200 nulls)
experiments/E203_identifiability_engine: .venv/bin/python run_confirmatory.py

# E201 replay benchmark, F1a scoring under the frozen control addendum (5deec1e)
experiments/E201_replay_benchmark: .venv/bin/python run_f1a.py

# E204R2 dual-parser canonical extraction (parsers C2 tree + D2 FSM; gate >=98%)
experiments/E204R2_residual_canonicalization: .venv/bin/python parser_c2.py && .venv/bin/python parser_d2.py

# E204 metrology — strict then soft arm (soft is hours: LOO + 200 soft-pipeline nulls)
experiments/E204_metrology: .venv/bin/python run_metrology.py && .venv/bin/python run_metrology_soft.py
# terminal scoring (frozen 5-status rule; committed BEFORE the soft arm finished):
experiments/E204_metrology: .venv/bin/python score_soft_arm.py

# E205-I graded palaeographic prior vs matched nulls
experiments/E205_palaeography: .venv/bin/python run_e205_I.py

# E206 slot freeze -> Stage 2 (verify SLOT_FREEZE.sha256 first; matcher frozen)
experiments/E206_onomastic_linkage/stage2: .venv/bin/python run_stage2.py

# E207 morphology battery (M0-M6; amendment R1 applied; as-run R0 preserved INVALID)
experiments/E207_morphology: .venv/bin/python battery.py

# E211 RAG indexes + evaluation (db gitignored; INDEX_MANIFEST.sha256 is the cutoff)
rag: .venv/bin/python build_indexes.py && .venv/bin/python eval_rag.py
```

## Closure cascade (mechanical, fail-closed at every step)
```bash
experiments/E204_metrology/score_soft_arm.py   # refuses without the soft-arm result
verifiers/finalize_e212.py                     # refuses without E204_FINAL_STATUS.json
experiments/E213_prospective_seal/build_seal.py# refuses without terminal E204; append-only
verifiers/run_battery.py                       # must exit 0
final/generate_package.py                      # refuses until E212 FINAL + seal present
```

## What cannot be reproduced from this repo alone
Licensed raw sources (gitignored; hashes in `DATA_INVENTORY.csv`), the gitignored RAG
sqlite (rebuildable via `build_indexes.py`; snapshot hash pinned), and E201-F1b (external
CSA sweep; enters only via `imports/E201_F1B/import_f1b.py`).
