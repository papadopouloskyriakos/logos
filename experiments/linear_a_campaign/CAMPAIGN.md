# Linear A decipherment campaign — autonomous run (2026-07-07, ~12h)

**Mandate (owner, AFK):** resume the three parked research branches and work autonomously to crack Linear A.

**Binding discipline (Constitution v2.2 — cannot be overridden by the mandate):** every confirmatory claim
goes prereg → held-out gate → adversarial verification → fail closed → append-only. A gated, held-out,
attack-surviving reading = a real (partial) decipherment. Rigorous nulls = the insurance policy. **I will not
fabricate a crack, re-run a refuted test under its old prereg, or modify any frozen manifest.** No overclaiming
above an earned licence (all LA transfer licences currently `NOT_EARNED`).

## Ground truth (what prior sessions already established — mostly frozen negatives)

| avenue | branch | verdict | frozen |
|---|---|---|---|
| cross-script toponym/phonetic anchor (2-way LA↔LB, procrustes d=24 + toponym pins) | la-lb-continuity | **`REFUTE_LOTO_FRAGILE`** — distributional channel 0.0000; only I+RI pins, each one-toponym-deep | prereg DOI 10.5281/zenodo.21168887, freeze 23da20d |
| administrative orthographic continuity | la-lb-continuity | `NULL_PUBLISHED` (H_exact, 0 observed) + `NO_POWER` (H_drift) | manifest acfd19b (immutable) |
| ritual/libation formula feasibility | la-lb-ritual-feasibility | `COMPLETE / NO_POWER` | — |
| external (Egyptian etc.) anchors | egyptian-calibration / external-anchors | `TRIVIAL_RECOVERY` / (audit pending) | — |
| + this session: label-route `NO_POWER`, observable-channels `REFUTED` | — | — | — |

This is the **6th–10th** rigorous negative across every major avenue. The corpus is showing its
identifiability ceiling — exactly the situation the Preamble anticipates. The frozen submitted paper already
reports "calibrated absence."

## Plan

- **Phase A — exhaustive audit** (`wf` recon): the complete verdict map + what is FROZEN vs genuinely OPEN vs
  `SOURCE_BLOCKED`, across all branches. Grounds everything; prevents re-treading refuted ground.
- **Phase B — pursue genuine openings** (new prereg each): leading candidate = **Cypriot triangulation**
  (3-way LA+LB+Cypriot; Steele & Meissner 2017 acquired) — more powered than the LOTO-fragile 2-way test, not
  yet run. Others as the audit surfaces them. Full discipline; adversarial verify any positive.
- **Phase C — if openings exhaust** → the definitive **identifiability / insurance-policy synthesis**: a
  rigorous, cross-referenced map of what the LA corpus can and cannot support, the strongest honest deliverable.

## Run log

- **T0** — campaign opened; ground truth established (branches are largely CLOSED negatives, not Stage-1 as the
  stale STATUS files claimed). Launching Phase A audit.
- **T1 — Phase A audit COMPLETE** (`wf_dd7be4bb`, 4 agents). Every avenue converges on one corpus-identifiability
  ceiling:
  - **Cross-script value recovery:** TWO preregistered/Zenodo-timestamped one-shots, BOTH fail-closed negatives
    (Phase 1 `REFUTE_LOTO_FRAGILE` DOI 21168887; Phase 2 `REFUTE` DOI 21173639). Distributional channel null
    4×; toponym pins irreducibly one-identification-deep. Frozen — no rerun.
  - **Cypriot triangulation** (the lead opening): `REFUTED_ALREADY` — circular (Cypriot labels = LB answer key),
    2 anchors both from the same {pa-i-to, se-to-i-ja} pair, Cypriot-eleven block already REFUTE (p=0.148).
  - **Drift continuity:** `NO_POWER` **fundamental** — non-circular sound-change model needs info the LA↔LB
    corpus lacks; permissive search FP≈99.6%. Ritual: `NO_POWER`, no in-domain exemplar (fundamental).
  - **External Egyptian anchor:** INCOMPLETE/underpowered (3–4 anchors, held-out FP≈0.25 vs recovery≈0.40) +
    confirmatory SOURCE_BLOCKED (Edel&Görg not collated). ONE unexecuted step: fit Kilani-2019 sound model,
    re-run power envelope `frozen=True`. Personal names read as GREEK (self-refuted); admin = Akkadian (nil).
  - **Verdict:** the ceiling is liftable only from outside the corpus, and the only outside lever (Egyptian)
    is underpowered/source-blocked. → Phase B: run the one executable step (Egyptian power pass); then Phase C
    identifiability synthesis.
- **T2 — Phase B: Egyptian frozen-regime power pass** (external-anchors `3310e4b`). The unexecuted `frozen=True`
  milestone: the discipline (no mapping search) drops FP from ~0.25 → **0.04 at La=4**, so the channel is NOT
  NO_POWER by design — BUT it hinges on ≥4-slot skeletons (La=3 → FP 0.24), REC is an optimistic ceiling, and
  the REAL confirmatory attempt (egyptian-calibration, Edel&Görg collated) already returned `TRIVIAL_RECOVERY`
  (one-training-record correspondence). Net: **design-viable but scarcity-limited**; unlock = more independent
  ≥4-slot anchors. A truth-layer design signal (≤0.75), not a reading.
- **T3 — completeness critic COMPLETE** (`wf_fd653da2`, 3 diverse-lens agents). All converge, no genuine
  avenue: methods `ALREADY_TESTED` (admin arithmetic powered+non-circular but re-derives Bennett; libation
  underpowered), data `NO_GENUINE_AVENUE` (every source exploited/redundant; SigLA bbox redundant with
  editorial gold), assumptions `UNDERPOWERED` (the one non-circular L3 target lacks held-out mass; corpus
  hapax-dominated, median 1 sign/insc, 63% one site). Ceiling adversarially confirmed.
- **T4 — Phase C: identifiability synthesis** (`IDENTIFIABILITY_SYNTHESIS.md` + generated
  `identifiability_metrics.json`). Quantified: **259 sign-value parameters > 212 independent constraints
  (generous upper bound) ⇒ UNDERDETERMINED**; info-budget gate refuses an L6 reading. The only held-out
  positives (segmentation L2, KU-RO arithmetic L3) re-derive known structure. **Verdict: `UNDERDETERMINED` —
  the present corpus cannot support a non-circular held-out reading; not "uncrackable" but underdetermined,
  with precise unlock conditions (more multi-sign inscriptions / independent ≥4-slot anchors / a bilingual).**
- **T5 — positive control DONE** (`kuro_reconciliation.json`). The KU-RO arithmetic-reconciliation gate
  (KU-RO as opaque token; numerals language-independent): observed exact reconciliation **25% vs 1.47% null =
  17×, p=0.0005** → **the harness FIRES on a real LA structural fact** (it is not merely a null-detector; the
  corpus contains real structure). BUT the signal is **Haghia-Triada-locked (27 of 28 sections)** → cross-site
  held-out = **`NO_POWER`** (1 non-HT section). Even the clear positive hits the same single-site / one-deep
  ceiling. Non-circular; re-derives Bennett; no reading asserted.

## CONCLUSION — campaign concluded (honest null, well before 12h)

**`UNDERDETERMINED`.** Every LA decipherment avenue, under fail-closed held-out gates + adversarial
completeness-checking, converges on one quantified corpus-identifiability ceiling (259 sign-value parameters >
212 independent constraints; median 1 sign/inscription; 63% one site; 84% hapax words). The harness demonstrably
FIRES on real in-corpus structure (KU-RO 17× over null) and on the Linear B positive control — so the null is a
property of the CORPUS, not a dead detector. The only held-out positives (segmentation L2, KU-RO L3) re-derive
known structure and are single-site-locked. **Linear A is not shown uncrackable — it is underdetermined by the
present corpus + sources**, with precise unlock conditions in `IDENTIFIABILITY_SYNTHESIS.md`. I did not
manufacture a crack, and I did not pad the remaining hours with re-runs of refuted tests — the honest
deliverable (the insurance policy) is complete. Any of the three parked branches' frozen negatives stands.
