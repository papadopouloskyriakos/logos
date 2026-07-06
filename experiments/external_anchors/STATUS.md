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

### Blocked (does not stall non-blocked work)
- **REQ-01** (Kom el-Hetan primary edition — hieroglyphic spellings/variants) → gates the E3
  confirmatory toponym target freeze.
- **REQ-02** (Egyptian foreign-name calibration editions) → gates freezing the Egyptian→foreign
  correspondence model (Section VII); **pacing item for RQ2/RQ3**.

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
