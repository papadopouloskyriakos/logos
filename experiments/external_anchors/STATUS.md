# STATUS

**As of:** 2026-07-06 · **Branch:** `research/external-minoan-anchors` · **Fork:** `main@762f48d`

## Current stage: **Stage 1 (source audit) — in progress.** Stage 0 complete.

### Done
- **Stage 0:** isolated worktree + branch created from `762f48d`; live-sweep isolation verified
  (`runtime/` gitignored ⇒ absent from this worktree; sweep 96/168 untouched). Project scaffold (25
  dirs). Read-only Linear A input manifest checksummed (6 files, referenced in place, not copied).
  Charter / Roadmap / Data-Dictionary written.
- **Stage 1 (initial):** `SOURCE_REGISTER.csv` (12 seed sources across RQ1–RQ6);
  `MATERIAL_REQUESTS.md` (6 requests; 2 `BLOCKING`); first bronze toponym records
  (Knossos/Amnisos/Lyktos from Kom el-Hetan, spellings pending REQ-01); README.

### Acquisition (2026-07-06 — 7 PDFs supplied) — **both BLOCKING items cleared**
- **REQ-02 SATISFIED** — Hoch *Semitic Words in Egyptian Texts* (594 pp) = the Egyptian foreign-name
  calibration corpus (the RQ2/RQ3 pacing item).
- **REQ-01 substantially satisfied** — Cline & Stannish 2011 gives the toponym group-writing
  transliterations (Knossos/Amnisos/Lyktos) + IDs + caveats; bronze v2 records written. Downgraded
  to USEFUL.
- **Still open:** REQ-04 (Mari — supplied scan is 1-page image-only, needs OCR / the ARM texts),
  REQ-03 (EA5647 edition). Neither on the RQ2 critical path.
- PDFs stored local-only in `data/bronze/pdf_local/` (gitignored; checksums in
  `data/manifests/acquired_sources.sha256`); never committed/redistributed.

### Next autonomous actions (Stage 1→2, no sweep contention)
1. Expand `SOURCE_REGISTER.csv` + per-source notes in `bibliography/source_notes/`.
2. Bronze records for the remaining families (Mari goods/roles → RQ1/E5; off-Crete LA finds; Ugaritic
   kptr; aDNA prior table) at the confidence the current evidence supports; flag gaps to requests.
3. **Slot-classifier audit (E-prep):** using the read-only LA corpus + the exploratory schema work,
   define preregisterable candidate toponym/name/commodity slot sets with explicit rules — *without*
   consulting any external resemblance. (Light, local, no fence contention.)
4. Draft the **Linear-B positive-control** design (E2) and the **end-to-end null** framework (X) on
   paper before any compute.

### Compute posture
Everything above is I/O + light CPU on local/idle resources; **zero** interference with the halted
CSA sweep or its fenced cores. Any material compute (power sim E1, positive control E2) will report
cores/mem/wall/host first and use a separate host or wait — never oversubscribe the fence.

### Verdict state
`status=INCOMPLETE` (data/calibration/controls pending). No confirmatory run; no external timestamp.
Stage 4 human gate not reached.

---
## MILESTONE (2026-07-06) — methodological foundation

**design_readiness = READY_FOR_CALIBRATION** (leans NO_POWER for the naive design). Isolation held
throughout (branch `research/external-minoan-anchors`; `main@762f48d`, `paper/`, `runtime/`, sweep
untouched; no fenced compute used).

- **Task A — slot classifier FROZEN** (`slot-rules-v1-2026-07-06`): 1165 internal-only candidates;
  **11 tier-B TOPONYM_LIKE** = the E3 targets; 27 COMMODITY, 3 TRANSACTION_TERM; LOSO held-out;
  leakage-proven (11 tests). Manifest data gitignored/local (licensed-derived); hash committed.
- **Task C — end-to-end null framework**: adaptive-choice inventory (21 choices; #9 mapping-search &
  #14 best-of-search flagged as the FP engines), null spec (10 families, 5 with working generators),
  search-receipt spec; scaffold + 5 tests.
- **Task D — power envelope (pilot)**: **in-sample matching FP≈1.0 (NO_POWER); held-out drops FP to
  ≈0.25 but recovery only ≈0.40** at 2–6 anchors → under-powered as naively scoped. Verdict pending
  the frozen-model re-run.
- **Task B — matched-scarcity LB positive control**: protocol + design + provisional degradation
  scaffold (3 tests). **Not executed**; no sensitivity claimed.
- **Task E/VII — schema**: `minoan_vs_greek_confidence`, `temporal_tier`/`linear_a_overlap_tier`
  present; EA5647 tagged Greek negative-control. `phonetic_anchor_eligibility` / `linguistic_phase_risk`
  to be added to the anchor schema when the confirmatory anchor set is frozen.

### Blockers
No **source** blocker remains on the toponym path (REQ-01 Cline forms + REQ-02 Hoch corpus in hand).
The pending work is **fitting the frozen Egyptian→foreign correspondence model from Hoch** (not yet
done) and **re-running the power envelope + positive control under it** — the next milestone. Until
then all matching parameters are PROVISIONAL and the power verdict is provisional NO_POWER-leaning.
