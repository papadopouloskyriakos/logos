# ROADMAP

Staged execution with explicit authority gates. Stages 0–1 authorized and running now; Stage 4 is a
hard human-approval gate before any external timestamp / confirmatory run.

| Stage | Content | Authority | Compute |
|---|---|---|---|
| **0 — Environment & isolation** | worktree/branch, scaffold, input manifest, charter/roadmap/status | **DONE (autonomous)** | trivial |
| **1 — Source audit & acquisition** | source register, bronze records, open-data pulls, material requests | **RUNNING (autonomous)** | light |
| **2 — Dataset & calibration build** | Anchor Corpus, Egyptian foreign-name calibration set, admin ontology, population-prior table, validators + tests | autonomous where data permit | light |
| **3 — Exploratory & power pilots** | power sim, end-to-end null prototype, Linear-B positive control, slot-classifier audit, toponym feasibility | autonomous **only if it does not compete with the live sweep**; report resources first | small; separate/idle host or wait |
| **4 — Confirmatory design** | full prereg, freeze gold inputs/controls/thresholds, go/no-go power decision | **STOP for explicit human approval** before timestamping | — |
| **5 — Confirmatory execution** | frozen one-shot runs; mechanical verdicts | only after approval + external prereg timestamp | per design |

## Experiment ledger (Section IX of the directive)

- **E1** Toponym feasibility & power audit → `NO_POWER` gate before any confirmatory match.
- **E2** Linear-B positive control (degraded to LA scale) → sensitivity gate; failure ⇒ stop.
- **E3** Toponym-anchor confirmatory test (frozen anchors/slots/correspondence-model/split; held-out).
- **E4** Personal-name channel (chronology + Minoan-vs-Greek gating; ambiguous held out).
- **E5** Mari/Ugarit/Egypt administrative ontology → LA schema (semantic, not phonetic).
- **E6** Keftiu ritual-language phonological constraints (exploratory).
- **E7** Population-prior audit (weak tiers only; genes ≠ language).
- **E8** Candidate-language tournament (equal budget; admits "none supported") — LAST, after anchors frozen.

## Ordering rationale

RQ1/E5 (semantic) and RQ2/E1–E3 (toponym) first — highest yield, lowest false-anchor risk. E4
(names) after E3 and gated on identity/chronology. E8 (language tournament) only after the anchor +
calibration + null layers are frozen, so it can't become thesaurus-fishing. E6/E7 feed priors, never
verdicts.

## Rough timeline (uncertainty-flagged; assumes no material compute contends with the halted sweep)

- **Source audit + register + material requests:** ~this session (Stage 1 core done now; expansion as sources arrive).
- **Bronze anchor records (open/knowledge-sourced) :** ~1–2 sessions; primary-edition spellings gated on `MATERIAL_REQUESTS`.
- **Egyptian foreign-name calibration corpus:** blocked on primary editions (see requests) — **the pacing item for RQ2/RQ3**; ~indeterminate until sources land.
- **Power analysis (E1) + Linear-B positive control (E2):** ~1–2 sessions of light compute once the anchor + calibration sets exist; can run on idle/local CPU without touching the fence.
- **Draft preregistration (Stage 4):** after E1/E2 give a go/no-go; then human gate.

The **binding constraint is source acquisition** (primary hieroglyphic editions + calibration
names), not compute. Everything downstream of a frozen correspondence model is cheap; the model
cannot be frozen without the calibration corpus.
