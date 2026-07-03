# PREREG_FINAL_P2 — cross-script LA↔LB value-recovery gate, Phase 2 (the freeze)

**Status: FINAL pre-registration for the second and last one-shot in this program arc.** All
design elements below are fixed BEFORE any real-label contact. The run is FORBIDDEN until the
external timestamp exists (`PREREG_P2_TIMESTAMP.md`, §K). Nothing under `paper/` is read or
written. The Phase-1 shot is spent (verdict REFUTE_LOTO_FRAGILE; prereg DOI
10.5281/zenodo.21168887; results DOI 10.5281/zenodo.21169626); this experiment's real held-out
labels are compared against predictions **exactly once**, by the single frozen configuration.

## §A Frozen operative test (provenance: commits `00fb9ea`, `33a3fec`, `23da20d`)

Statistic: held-out **top-1 value-recovery accuracy** of the frozen configuration; candidates =
the 73 DĀMOS-attested Unicode LB syllabary values. Null: permuted-graph (permute the
anchor↔value assignment over all 51 robust anchors; refit on train pairs under the permutation;
re-score held-out with the pinning logic unchanged); **n_perm = 2000**, add-one p (Phipson–
Smyth). Configuration (certified lineage, grid = 1, NO tuning step): E_A = LA conservative
stream PPMI (w2/cds 0.75) → SVD d=24 seed 0; E_B = same over DĀMOS; Procrustes on train pairs;
NN among the 73; anchor channel = LB-lexicon word completion, pin mechanics verbatim
(`power_precheck._pinned`: a word pins a masked member iff ALL its other in-design members are
unmasked; identification reliability = 1, the disclosed optimistic bound).

## §B Cross-attempt decision rule (the §2 judgment call, adopted)

This is the SECOND pre-registered attempt at the backward-projection hypothesis. The operative
bar applies **Šidák with N_attempts = 2**: a scoring clears iff add-one **p_raw < 1 − 0.95^½ ≈
0.02532**. Certification ran at this corrected bar (P2_CERTIFICATION.md) so the certified and
fired designs share one decision rule. [If the operator vetoes at the §4 handoff, the bar
becomes unadjusted p < 0.05 with an explicit both-attempts-always-reported clause — the veto
RELAXES the bar, so the certification remains valid; whichever choice is in force at timestamp
time is the recorded one, never both.]

## §C The anchor set (frozen; selection rule `fcb0c34`, set commit `64d51b4`)

The 8 anchors of SELECTED_ANCHORS.md — su-ki-ri-ta, tu-ru-sa, di-ki-te, se-to-i-ja, pa-i-to
(S&M Table 6.4, primary), ku-ta, ku-ni-su, sa-ra₂ (Younger, archived secondary) — 17 covered
eligible signs, legs ≤ 2. Prose caveats carried: se-to-i-ja's geographic identification is
debated (Archanes vs eastern Crete) — its word-correspondence mechanics are not; sa-ra₂'s
identification is inferential (Younger: Ayia Triada?); the selection-filter fix trail is
disclosed in SELECTED_ANCHORS.md. Class-4 variation rows are constraints only and appear in no
scoring. **The set does not change after this freeze, regardless of outcome.**

## §D Axis (primary only)

Stratified random **h = 20** from the 49-eligible pool ({SI, MU} ineligible by the frozen
Phase-1 value-query principle). Strata = covered-by-the-selected-set {C, U} × LA-attestation
tertiles (Phase-1 rank rule on the 49): populations C 1/8/8, U 16/8/8; largest-remainder
allocation **C 1/3/3, U 7/3/3**; cells drawn in sorted order with
`np.random.default_rng(20260714)` (the committed selection seed). This draw is label-free; it
materializes deterministically as: DI JA KI MA ME NE O PO PU PU2 QE RA RI SU TA2 TE TI TO U WA
(7 covered). **Phase-1 overlap disclosed: 10 of 20** (DI ME NE O PO QE RI TA2 TE WA); results
are additionally reported stratified by previously-held-out vs fresh signs (descriptive
robustness row). The Cypriot-eleven block is reported DESCRIPTIVELY only — no gate authority,
no power claim (its Phase-1 power check failed and nothing here re-opens it).

## §E Binding clauses (fail-closed; verdict map exactly as Phase 1)

- **(i)** full statistic clears the corrected permuted-graph bar (§B);
- **(ii)** conjunctive LOTO over EVERY selected anchor: all 8 leave-one-anchor-out re-scores
  (pure arithmetic on the single run's persisted artifacts) clear the same corrected bar;
- **(iii)** instrumentation complete: SearchLog n_eff recorded, n_trials = 1, permutation null
  non-degenerate.
- **Verdicts:** CONFIRM iff (i)∧(ii)∧(iii); REFUTE iff ¬(i)∧(iii); REFUTE_LOTO_FRAGILE iff
  (i)∧¬(ii) (failing anchors named); INCOMPLETE iff ¬(iii). Truth-layer: any CONFIRM
  corroborates the value convention on the tested anchors only; no A-only sign value, no
  reading of Minoan; capped ≤ 0.75 as a signal (invariant 5).
- **Descriptive rows (never gate-deciding):** toponym-off floor; secondary-drop re-score (the
  3 Younger anchors' pins removed); personal-name-drop row is VACUOUS for this all-toponym set
  (stated, not computed); Phase-1-overlap stratified accuracy; Cypriot-eleven block.

## §F Feature contract & enforcement

Inherited VERBATIM from PREREG_DRAFT §1 / PREREG_FINAL §G (image/shape features banned; values
enter only as held-out labels / train supervision; DĀMOS lexical constraints and
provenance-sourced anchors allowed). The grep-clean check (frozen pattern) + fresh-interpreter
banned-module check run on the final code; outputs recorded in the report.

## §G Dual abstracts (finalized)

**(i) CLEARED:** Under a pre-registered, externally timestamped, one-shot protocol — the second
and final attempt of this arc, graded at a two-attempt Šidák-corrected bar — masked Linear A
anchor signs' conventional Linear B values were recovered above a permuted-graph null from
non-shape evidence alone (distributional structure + eight provenance-vetted place-name
anchors), and the positive survived leave-one-anchor-out over every anchor. This is the first
LOTO-robust, gate-cleared empirical corroboration of the backward projection for any subset of
the syllabary; shape circularity is excluded by construction. N signs recovered at top-1 of 73;
values validated, language unread.

**(ii) NULL (evidential, power-bounded):** At a certified LOTO-survival power of 0.82 (planted
s=3) for the fielded eight-anchor design, the one-shot did not produce a LOTO-robust positive
at the corrected bar. Combined with Phase 1, the arc's evidential statement is: the LA↔LB value
convention's non-shape support remains bounded by the place-name identifications themselves —
now shown insufficient even at quota-certified anchor supply, at current corpus scale. The
identifiability bound tightens; both attempts are reported in full.

## §H Run protocol

Master/run seeds: held-out draw 20260714 (§D); permutation null **20260715**; embeddings seed
0. n_perm = 2000. Command: `python3 p2_oneshot.py` (to be written post-timestamp, importing
the frozen machinery; its grep-clean output recorded). Artifacts:
`results/p2_oneshot_gate.json` (+ SHA-256 in the report). Real labels are read exactly once,
inside that script; LOTO/descriptive rows are deterministic re-scorings of its persisted
artifacts. SearchLog instruments the single config, every draw, every re-score.

## §K External timestamp (hard gate)

After this file's freeze commit is pushed: STOP. The operator deposits THIS EXACT FILE
externally (new standalone record, their method) and returns DOI + timestamp, recorded in
`PREREG_P2_TIMESTAMP.md` and committed. The one-shot is FORBIDDEN before that commit exists.
