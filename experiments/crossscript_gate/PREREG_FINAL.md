# PREREG_FINAL — cross-script LA↔LB value-recovery gate (Phase 1, the freeze)

**Status:** FINAL pre-registration for the one-shot gate run. Supersedes `PREREG_DRAFT.md` as
the binding document for the run; the DRAFT's feature contract (§1) is inherited VERBATIM and
remains binding. Nothing under `paper/` is read or written. **The real held-out labels are read
exactly once, by exactly one frozen configuration, after the external timestamp (§K) exists.**

Operator decisions folded in (2026-07-03, pre-freeze Q&A): stratification = coverage ×
frequency with bridging re-certification; eligibility by principle (→ {SI, MU} ineligible);
**grid = 1** (no tuning step) with Šidák over confirmatory axes only.

---

## §A The frozen operative test (verbatim provenance)

From commit `00fb9ea` (`PREREG_DRAFT.md` §2, "Verdict thresholds (frozen now)"), quoted:

> - **INVALID (harness, not corpus):** false-fire rate at s=0 exceeds 0.14 (>7/50; binomial 95%
>   bound on nominal 0.05), OR power at s=13 is below 0.90 […]
> - **GO:** power ≥ 0.80 at some s ≤ 3.
> - **MARGINAL:** not GO, and power ≥ 0.80 at some s ≤ 8. […]
> - **NO-GO:** power < 0.80 for all s ≤ 8.

with the frozen simulation constants (same section): planted strengths {0, 0.5, 1, 2, 3, 5, 8,
13}, n_rep = 50, n_perm = 200 (power sims), master seed 20260703, PPMI window 2 / cds 0.75 /
SVD d = 24 value embeddings, Procrustes stand-in, permuted-graph null, add-one p.

From commit `33a3fec` (Addendum B), quoted: h = 20; toponym channel = "a held-out sign X is
**pinned** iff some non-queried toponym LA form contains X and ALL other signs of that form are
un-held-out […] A pinned sign's prediction = the toponym slot's value. Pinning assumes
**identification reliability = 1**"; null = "identical permuted-graph null; the pinning logic
runs unchanged in the null pipeline"; two configurations (a) machinery / (b) design, INVALID
checks evaluated on (a), bands applied to (b).

The Phase-0.5 GO was produced by exactly this design (`results/power_precheck_phase05.json`;
thresholds commit recorded inside). **The real run below is this design's lineage.**

## §B Hypothesis and operative statistic (real run)

**Hypothesis:** the conventional LB-transferred values of held-out anchor signs are recoverable
above chance from non-shape evidence (LA-internal distributional structure + DĀMOS-derived
LB-side structure + provenance-sourced toponym constraints), measured against the
permuted-graph null.

**Operative statistic (per axis):** held-out **top-1 value-recovery accuracy** of the single
frozen configuration (§C), candidates = the 73 DĀMOS-attested Unicode LB syllabary values.
**Null:** permute the anchor↔value assignment over all 51 robust anchors, refit the alignment
on the training pairs under the permutation, re-score held-out (pinning logic unchanged, scored
against the permuted assignment); **n_perm = 2000** (the B.2 real-run convention,
`phono_distributional.run_pilot` default; raised from the power-sim 200 for p-resolution only —
same null construction), null permutation seed 20260711. **p_raw** = add-one (Phipson–Smyth).
**Decision rule:** corrected_p = 1 − (1 − p_raw)^N with **N = the number of confirmatory axes**
(1 or 2, fixed by §E before the freeze completes); an axis clears iff corrected_p < 0.05.
Top-5 accuracy is reported descriptively, never gate-deciding.

## §C The single frozen configuration (grid = 1; config-provenance clause)

- E_A: PPMI (window 2, cds 0.75) → TruncatedSVD d = 24, seed 0 (`embeddings.embed`) over the LA
  conservative stream (`data.load_a`); E_B: identical recipe over the DĀMOS wordforms
  (`data.load_b_damos`); rows L2-normalised.
- Aligner: orthogonal Procrustes (`align_methods.Procrustes`) fit on TRAIN anchor pairs only;
  held-out prediction = cosine NN among the 73 candidates.
- Toponym channel: Addendum B mechanics verbatim (§A quote); the five non-queried Table 6.4
  forms (`toponym_anchors.csv`); the queried a-tu-ṛị-si-ti variant EXCLUDED.
- **Config-provenance clause (operator rider, verbatim intent):** this configuration (d=24,
  window 2, cds 0.75, Procrustes) is fixed by the Phase-0.5 certified lineage; it was selected
  on synthetic planted-signal power simulations only and has never been evaluated against real
  held-out labels. **No tuning step exists in this experiment.** n_trials = 1 per axis.
- **SearchLog:** instruments everything regardless — the single candidate configuration per
  axis, every permutation draw, every LOTO variant (`scripts/comparison/searchlog.py`,
  deduplicating n_eff). The report states n_trials = 1 per axis explicitly.

## §D Axes (no other axis exists)

**Eligibility principle (operator-frozen):** ineligible for held-out membership = any robust
anchor whose VALUE entry carries the primary source's own query mark ('?') in the
confirmed-values grid (S&M Table 6.11) or candidate-not-member status (§3 p. 98). Query marks
on attestation gaps in intermediate scripts (PO's "Not attested?" Cypro-Minoan cell) query the
transmission chain, not the value, and do NOT trigger ineligibility. **Applied: ineligible =
{SI, MU}; eligible pool = 49 of the 51 robust anchors.** SI and MU remain training pairs with
their tier flags carried. Homomorphy grades remain `pending_primary` at freeze (Salgarella 2020
unacquired) — carried as flags, deciding nothing.

**Training set (both axes):** all 51 robust anchors minus the axis's held-out set.

**PRIMARY axis — stratified random h = 20 from the 49 eligible.**
- Strata: toponym-covered {yes, no} × LA-attestation tertiles. Tertiles are computed on the
  49-anchor eligible pool by deterministic rank: sort ascending by (la_attestations, sign_id);
  ranks 1–17 = T1 (attestations 8–45), 18–33 = T2 (45–109), 34–49 = T3 (110–195). (The value 45
  spans the T1/T2 boundary; the rank rule resolves it deterministically.)
- Cell populations and **population-proportional allocation, largest-remainder rounding**
  (h = 20):

  | cell | population | quota | allocation |
  |---|---|---|---|
  | uncovered × T1 | 16 | 6.531 | **7** |
  | uncovered × T2 | 9 | 3.673 | **4** |
  | uncovered × T3 | 10 | 4.082 | **4** |
  | covered × T1 | 1 (TO) | 0.408 | **0** |
  | covered × T2 | 7 | 2.857 | **3** |
  | covered × T3 | 6 | 2.449 | **2** |

  Disclosed quirk: the covered×T1 cell has population 1 (TO) and allocation 0 — TO can never be
  held out under this design; it always trains.
- Draw: within each cell, sample the allocated count without replacement using
  `np.random.default_rng(20260710)` (the committed **selection seed**), cells processed in the
  table's order, candidates within a cell in sorted sign_id order; any tie-break is taken from
  the same seeded generator.
- **Label-free statement:** both stratification variables (toponym coverage, LA attestation
  count) are feature-side properties computable without any value label — stratification leaks
  no held-out label.
- **Rationale (operator, verbatim):** population-proportional stratification is variance
  reduction for a single-draw experiment; it fixes the toponym channel's held-out share at its
  expected value rather than leaving the one shot exposed to pin-supply luck in the channel the
  GO is conditional on.

**SECONDARY axis — the Cypriot-stable eleven as a block** (S&M 2017 Table 6.2 membership
verbatim): **A, DA, I, NA, PA, PO, RO, SA, SE, TI, TO** held out together; train = the
remaining 40 robust anchors. PO included; its "Not attested?" CM caveat is reported with any
result. SI remains candidate, not member — excluded from the block (and ineligible anyway).
Status (confirmatory + Šidák, or descriptive) is fixed by §E.1 BEFORE the freeze completes.
The axes may overlap in membership (eligible eleven can be drawn by the primary); both axes
test the same single configuration, and N pays for both when confirmatory.

## §E Pre-stated §1 rules (power checks run AFTER this file's first commit, results appended)

Both checks reuse the Phase-0.5 machinery and the §A frozen bands VERBATIM (no threshold
edits), with one operator-directed refinement: **detection inside every replicate uses the
FINAL operative decision rule** — corrected_p = 1 − (1 − p_raw)^N < 0.05 — so certified power
and the fired test share one decision rule.

1. **Secondary-axis power check (block design):** held-out = the fixed eleven; train = 40;
   toponym channel per Addendum B; detection at N = 2 (the N it would carry if confirmed).
   - Design curve meets the frozen GO band (power ≥ 0.80 at some s ≤ 3) with machinery-config
     INVALID checks passing → the secondary is a **confirmatory** axis; final N = 2.
   - Otherwise → the secondary **demotes to DESCRIPTIVE** (reported in full, never
     gate-deciding); final N = 1. The curve is reported either way.
2. **Primary-axis bridging certification (operator rider 1):** the power analysis re-run under
   the EXACT stratified design that will fire (49-pool, strata table above, seeded stratified
   draws per replicate), detection at the final N from §E.1. The frozen GO band must hold.
   **If it does not: STOP and escalate — no silent fallback to uniform.**

### §E outcomes (2026-07-03, appended per §E — no rule changed; artifact
### `results/phase1_power.json`, rules commit `15c7032`, 28.0 s CPU)

1. **Secondary → DESCRIPTIVE.** Block-axis design curve (toponym channel on, detection at the
   N=2 bar p_raw < 0.02532): power 0.14 / 0.14 / 0.16 / 0.42 / **0.64** / 1.00 / 1.00 / 1.00
   at s = 0 / 0.5 / 1 / 2 / 3 / 5 / 8 / 13 — GO band (≥ 0.80 at s ≤ 3) NOT met; machinery
   config valid (s=0 false-fire 0.02; s=13 power 1.00). Structural cause, worth recording: the
   eleven cluster inside the toponym forms (pa-i-to and se-to-i-ja are mostly *inside* the
   block), so only SA is pinnable (mean pins 1.0 of 11) — the block axis loses the constraint
   channel almost entirely. **The Cypriot-eleven axis is reported descriptively, never
   gate-deciding. Final N = 1.**
2. **Primary bridging: GO RE-CERTIFIED** at the operative bar (N=1, p_raw < 0.05), exact
   stratified design (49-pool, §D table, seeded per-replicate draws): design-curve power
   **0.82 / 0.84 / 0.80 / 0.84 / 0.98** at s = 0 / 0.5 / 1 / 2 / 3 (1.00 beyond); machinery
   config valid (s=0 false-fire 0.04; s=13 power 1.00); mean pins 2.1–2.5 of 20 (stratification
   stabilized the channel as intended). The design that fires is the design certified.

## §F Toponym-reliability clause (the GO condition — binding)

Any positive verdict on any axis must survive **leave-one-toponym-out (LOTO)**: for each of the
five non-queried Table 6.4 equations, re-score the SAME one-shot predictions with that
toponym's pins removed (NN prediction replaces the pin; pure arithmetic on persisted artifacts
— no second model run, no re-reading of labels). Each LOTO variant must clear the operative bar
(same corrected N). LOTO variants are conjunctive robustness clauses of the single verdict
(AND-monotone), NOT additional trials. The **toponym-off (machinery) configuration** is
additionally reported as the floor, descriptive. The queried a-tu-ṛị-si-ti variant stays
excluded. The optional reliability-discount sensitivity sweep is NOT run (declared omitted).

## §G Feature contract

Inherited VERBATIM from `PREREG_DRAFT.md` §1 (image/shape features banned — HOG, Hu,
shape-context, render/JEPA embeddings, anything downstream of sign images; conventional values
enter only as held-out labels / train-anchor supervision; DĀMOS lexical/phonotactic and
provenance-sourced toponym constraints allowed). The gate code must pass the grep-clean check
(pattern `(palaeo|jepa|sign_images|hog|hu_moment|shape|render|PIL|cv2|skimage|torchvision)`)
and the fresh-interpreter banned-module check; both outputs are recorded in the report.

## §H Verdict clauses (fail-closed) and vocabulary mapping

Per axis, computed mechanically from persisted artifacts (never asserted in prose first):

- **CONFIRM** iff (i) corrected_p < 0.05, AND (ii) all five LOTO variants have corrected_p
  < 0.05, AND (iii) instrumentation complete (SearchLog n_eff recorded; permutation null
  non-degenerate, i.e. null accuracies have nonzero spread).
- **REFUTE (honest null)** iff (i) fails with (iii) complete.
- **REFUTE_LOTO_FRAGILE** iff (i) passes but (ii) fails — a fail-closed negative; the failing
  toponym(s) are named. (A positive that depends on one identification is not a positive.)
- **INCOMPLETE** iff (iii) cannot be satisfied.
- Truth-layer (invariant 5): a CONFIRM here corroborates the VALUE CONVENTION on the tested
  anchors only; it assigns no value to any A-only sign, licenses no reading of Minoan, and
  enters downstream reasoning as a signal capped ≤ 0.75 like every model-side positive.

## §I Dual abstracts (finalized)

**(i) CLEARED:** The syllabic values of Linear A's shared (AB) signs are conventionally
back-projected from Linear B — a transfer argued on principle (Steele & Meißner 2017) but never
gate-tested at the value level. We pre-registered, externally timestamped, and ran exactly once
a held-out value-recovery gate: h=20 stratified-random masked anchors (secondary: the
Cypriot-stable eleven as a block), values predicted from non-shape evidence only — LA-internal
distributional structure, DĀMOS-derived Linear B structure (13,562 wordforms), and five
provenance-sourced toponym constraints — against a permuted-graph null with Šidák-corrected
thresholds and leave-one-toponym-out robustness, all frozen before the run. Recovery cleared
the corrected bar and survived every LOTO variant (N signs at top-1 of 73 candidates). This is
the first gate-cleared empirical corroboration of backward projection for any subset of the
syllabary; shape circularity is excluded by construction. No value is assigned to any
unmatched sign; Minoan remains unread.

**(ii) NULL:** The syllabic values of Linear A's shared (AB) signs are conventionally
back-projected from Linear B; we tested, under a pre-registered and externally timestamped
one-shot protocol, whether that convention is independently recoverable from non-shape
evidence — LA distributional structure, DĀMOS-derived Linear B structure, and five
provenance-sourced toponym constraints — against a permuted-graph null with Šidák correction
and leave-one-toponym-out robustness. Held-out recovery did not clear the frozen bar (or did
not survive toponym removal), extending the repo's alignment-geometry null: at current corpus
scale, no non-shape channel independently carries the LA↔LB value convention, whose empirical
basis remains shape homomorphy plus unfalsified-in-principle arguments. With the planted-value
power analysis certifying the design could have detected a moderate signal, this is a
quantitative identifiability bound on the most-cited "known" element of Linear A — and a
concrete statement of what evidence a future decipherment claim must first produce.

## §J Run protocol

- Seeds: held-out selection **20260710**; real-run permutation null **20260711**; embeddings
  seed 0; §E power checks keep the frozen 20260703 scheme.
- Commands: `python3 phase1_power.py` (§E checks; before the freeze completes),
  `python3 oneshot_run.py` (§4; ONLY after §K). Artifacts:
  `results/phase1_power.json`, `results/oneshot_gate.json` (+ SHA-256 of both recorded in the
  report). Wall-clock recorded.
- The real held-out labels are compared against predictions exactly once, inside
  `oneshot_run.py`, by the §C configuration; the LOTO battery and the toponym-off floor are
  deterministic re-scorings of that single run's persisted artifacts.

## §K External timestamp (hard gate)

After the freeze commit is pushed, the one-shot run is FORBIDDEN until the operator deposits
this file to Zenodo and returns the DOI + timestamp, recorded in `PREREG_FINAL_TIMESTAMP.md`
and committed. Rationale: the submitted paper's own chronology audit conceded its deposit
postdated its runs; this experiment closes that gap — external priority must exist BEFORE the
result exists.
