# LOGOS-2 PRECHECK — preflight and overlap audit (2026-07-10)

**Campaign:** LOGOS-2 Anchor-to-Identifiability · **Branch:** `research/logos2-anchor-identifiability`
(worktree `/home/claude-runner/gitlab/n8n/logos-logos2`, base `797c8c6` = main HEAD) · **Governance:**
Constitution v2.3 remains authoritative (see `CLAIM_LADDER.md` for the L0–L6 ↔ L0–L9 mapping).

## 1. Protections verified at start

- `git status` clean on main (one pre-existing untracked file, `experiments/crossscript_gate/phase3/sweep/scan_summary.json`, not ours, untouched).
- `paper/`, `governance/`, raw corpus, the 72h campaign + review bundle + seals: sha256 baseline frozen in
  `PROTECTED_ASSET_HASHES.sha256` (36 entries; the 72h bundle zip hash matches the remediation record
  `1e8df5d0…` — chain intact).
- **Worktree isolation rationale:** the main worktree hosts the RUNNING CSA sufficiency sweep whose cell
  subprocesses re-import repo modules per point (diagnosed 2026-07-10, RE-IMPORTED_PER_POINT). LOGOS-2 lives in
  its own worktree so no commit can change code under the running sweep.

## 2. Environment and standing constraints

- 32 logical CPUs / 32 GiB RAM / 352 GiB free disk; Python 3.11.2; numpy/scipy/torch-cpu/networkx/pandas/sklearn
  system-wide; **campaign venv `research/logos2/.venv`** with OR-Tools CP-SAT + Z3 + python-sat (smoke-tested;
  frozen in `ENVIRONMENT_BASE.txt`). Network available; download policy in `RESOURCE_BUDGET.json`.
- **Standing load:** the CSA sufficiency sweep occupies ~20 nice-10 workers until ~2026-07-13 19:00. LOGOS-2 is
  capped at 6 nice-15 workers / 8 GiB until then (see `RESOURCE_BUDGET.json`). This sweep also DELIVERS data
  LOGOS-2 needs (below).
- Master seed 1336530913; per-run seeds derived by sha256(master ‖ experiment ‖ cell ‖ fold ‖ replicate); no
  fork-inherited global RNG.

## 3. Inventory artifacts (committed alongside this file)

`DATA_INVENTORY.csv` (27 assets) · `DATA_LICENSES.md` · `PRIOR_METHOD_OVERLAP.csv` (24 rows) ·
`SEALS_REGISTER.md` (11 seals, contents unquoted) · `E200_PRIOR_EVIDENCE_CHANNELS.json` (22 prior-channel
nodes) · `EXPERIMENT_DAG.json` · `RESOURCE_BUDGET.json` · `CLAIM_LADDER.md` · `ledger.jsonl`.

## 4. Reconciled experiment classification (stricter scout reading wins)

| exp | classification | the material difference REQUIRED for it to run (else it stays blocked/duplicate) |
|---|---|---|
| E200 | NEW (audit) | — (this preflight + evidence-channel graph is most of it) |
| E201 | **EXTENSION** | (i) fills the NAMED open defect: the sufficiency curve's 600–700-word LB/Cypriot cells were never measured (endpoint clamps; ERRATUM-class in the master inventory) — the RUNNING sweep delivers exactly these by ~2026-07-13; (ii) the genuinely new leg = **process replay** (would the gate have graduated Ventris-1952 at its actual evidence level, and rejected the failed decipherments?); mere re-run of Ugaritic→Hebrew recovery would be DUPLICATE of LIN-14. |
| E202 | **DUPLICATE as specced → recast** | anchor-ablation/VOI was priced and CLOSED by the anchor-lattice campaign (12×8-slot×12-lineage; foothold 2–3; LA at 0 anchors; ambiguity 10^63.4–10^270). The NEW delta (OPEN_AND_UNTESTED): a **sequential acquisition POLICY** (which sign/inscription/anchor to seek next, conditioned on the E203 engine), not a re-priced curve. |
| E203 | **NEW formalism, EXTENSION of question** | first industrial CP-SAT/SMT/model-counting engine (all prior solvers were custom numpy). Acceptance bar inherited: reproduce the gauge quotient (~10^63.4 operational; ≥10^270 classes), the 12×8×12 threshold surface, and the WP-N matched-null adjudication (its own UNSAT find must survive the "every matched random pin-set is also UNSAT" test or be labelled UNSAT_GENERIC). |
| E204 | **EXTENSION** | prior fraction work exists (E004 seal + Di Mino audit machinery). New: transparent CP/SAT re-implementation of the Corazza–Ferrara constraint system + the four-component evidence separation + selection-aware nulls. The FRACTION_ORDER_ANETAKI_SEAL stays CLOSED (opening event = Anetaki II publication, not available; §0.6). |
| E205 | **A: EXTENSION · B: EXTENSION · C: BLOCKED_DATA · D: NEW** | bbox geometry already mined (E076–E090); stroke/contours/3D SOURCE_BLOCKED → E205C blocked. Genuinely available and UNUSED: **Salgarella 2020 homomorphy grades (57 signs, acquired, extracted)** for allograph/merge-split tests (E205A), and **E205D transcription-uncertainty propagation** (never done). Site attribution (B) must control sign-identity confound. |
| E206 | **EXTENSION w/ hard gate** | exact toponym continuity is CLOSED (NULL_PUBLISHED, fully powered); drift leg was NO_POWER because **no drift-tolerant pre-registered edit-operation model was ever designed** — that design + a NEW input freeze (slots frozen before any external name is consulted) is E206's genuinely-new move. Existing pins (I, RI, SU, TO) are each one-toponym-deep; canaries mandatory. |
| E207 | **NEW (adaptor-grammar, subregular) + guarded MDL** | no adaptor-grammar or subregular implementation exists anywhere in the repo (verified). MDL leg must use dependency-deduplicated accounting (naive MDL rewards clone-stacking: +5.92 false bits precedent) and beat the cut-everywhere degenerate segmentation; reuse la_ensemble.json soft boundaries + the frozen 0.436/0.577-ceiling metric. |
| E208 | **DUPLICATE unless gate passes** | the 6-family tournament (W-Semitic, Pre-Greek/Anatolian, Hurrian, Luwian, Etruscan, Aegean-isolate) ran 3 ways — ALL AT_END_TO_END_NULL, random lexicons matched real languages, and WP-J formally DE-AUTHORIZED further tournaments (J_NOT_AUTHORIZED). E208 runs ONLY if (i) a J-style licence-clean authorization gate passes and (ii) the joint-segmentation+phonetic-prior delta demonstrably clears the same S/W/R null battery on a KNOWN script first. |
| E209 | conditional (upstream leads) | runs only on non-null E206/E208 leads; inherits their gates. |
| E210 | **EXTENSION w/ hard gate** | partial/UNBALANCED OT never tried (genuine delta) — but balanced OT/GW failed even the known LB↔Cypriot pair (WP-F NO_POWER; E006 SEED_EFFICIENCY_NOT_ACHIEVED). Gate: pass the known-pair bar that killed F2 before touching LA. |
| E211 | **EXTENSION** | profile-HMM/restoration is new machinery over a mapped channel (templates/closure L2 SUPPORTED in observable-channels); auxiliary structural channel, never independent of distribution. |

## 5. Key data facts the campaign builds on

- Silver corpus: 1,341 inscriptions (symlinked read-only from main). 7 cognate benchmark files for E201
  (LB→Greek incl. names variant, Cypriot→Greek, Ugaritic→Hebrew ×2, Phoenician→Ugaritic, Luvian→Hittite).
- Old Persian / Carian / Meroitic / Iberian replay datasets: not in-repo; classified BLOCKED_DATA at preflight
  unless a licence-clean citable source is found (documented per E201's prereg; approximation disclosed).
- SigLA bbox geometry (802 docs/376 signs) decoded; **Salgarella 2020 grades = unused primary source**;
  DĀMOS LB wordforms (13,562) available; Anetaki full edition NOT ingested (preliminary material only).
- 11 prospective seals registered (`SEALS_REGISTER.md`); none will be inspected before freezes (§0.6);
  FRACTION_ORDER + Anetaki-delta seals await an EXTERNAL opening event that has not occurred.

## 6. Immediate schedule (per `EXPERIMENT_DAG.json`)

E200 (this audit + independence graph) → E201 harness + E203 engine in parallel (pilot-scale under the
sweep-constrained budget) → E204/E205 data audits → E207 after corpus-interface freeze → E206 after
SLOT_FREEZE. E208–E210 strictly gate-conditional. The heavy E201 confirmatory cells wait for the CSA sweep's
LB/Cypriot at-scale measurements (~2026-07-13) — the sweep is part of this campaign's evidence base.
