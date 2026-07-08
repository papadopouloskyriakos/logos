# EPOCH-007 — Ledger-role induction as anchor constraints → **ROLE_INDUCTION_NO_POWER**

**Stage header (Art. XXII).** Frontier F5 · gate A/C · seed 20260708 · prereg
`epochs/EPOCH-007/prereg.md`, plan_hash `6c85277da7c4e5d30abdd12bca084db4076c4f12e334225f5a5c535dfc2be566`
(frozen 2026-07-08T04:13:24Z, before any run). Articles: V, VII, VIII, IX, XI, XII, XV, XVII, XVIII, XXII.
Claim layer: **L2/L3 functional-slot only**; no value/semantic claim possible from this design; **no licence
touched** (Art. XV). Verdict computed mechanically from the frozen criteria.

## Question

Can transaction-role slots (name-slot W / commodity-slot C / unit-slot U / totals-marker T; quantity = the
numeral itself) be induced BLIND from ledger document structure alone — no sign values, no editorial case —
calibrated on Linear B (known answers), then transferred to Linear A as slot-semantics constraints?

**Prior-art difference (mandatory):** the observable-channels programme REFUTED L3 *word-context → commodity
channel* (predicting WHICH commodity a word co-occurs with) and SUPPORTED L2 doc-structure
(templates/closure). This epoch is neither: it induces PER-OCCURRENCE SLOT ROLES from within-document
geometry (numeral adjacency, line position, repetition profile). A commodity-slot verdict says nothing about
which commodity; the refuted lexical-distributional task is not re-run.

## Design (frozen; deviations logged)

- Blinding: token = GROUP(sha1(casefold), n_signs) or NUM(value); editorial case erased; 15 structural
  features (13 prereg + 2 added under DEV-1); z-score → k-means (k=12 under DEV-2) fit on LB **derivation =
  KN** (660 ledger docs); many-to-one cluster→role decode by derivation majority; graded on **held-out =
  non-KN** (433 docs: PY 306, TH 90, MY 32, rest 5).
- **DEV-1/DEV-2 (Art. XVII deviation log):** the initial prereg machinery (13 features, k=5) FAILED its own
  synthetic positive control (macro-F1 0.692, recall(U)=0). Two machinery changes were calibrated **on the
  synthetic control only** (no real-corpus label was read): +2 preceding-token features; k 5→12 (synthetic
  sweep {6:.71, 8:.71, 10:.92, 12:1.00}). After freezing them, every real-corpus number below comes from a
  single run.
- Ledger filter: ≥2 numerals, ≥3 sign-groups, ≥2 lines. LB gold (grading only): T = to-so/to-sa…,
  U = {S,V,T,Z,M,N,L,P,Q}, C = other logograms, W = syllabic words.

## Results

**PC1 synthetic positive control (run first): PASS** — held-out macro-F1 **1.000** (threshold ≥ 0.80) on 150
planted ledgers after DEV-1/DEV-2. The machinery can recover planted slot structure perfectly.

**LB leg: detector does NOT fire.**

| unit | n docs | accuracy | macro-F1 | W F1 | C F1 | U F1 | T F1 |
|---|---|---|---|---|---|---|---|
| derivation (KN) | 660 | .858 | **.419** | .868 | .809 | .000 | .000 |
| held-out (non-KN) | 433 | .690 | **.341** | .813 | .552 | .000 | .000 |

Frozen fire criteria: (a) held-out macro-F1 ≥ .50 → **FAIL (.341)**; (d) recall(T) ≥ .50 and recall(C) ≥ .50
→ **FAIL (T recall .000; C recall .787)**. Structure nulls (b): N1 shuffled-document p95 macro-F1 = .3193
(max over 25 reps .3198), N2 numeral-detach p95 = .3204 (max .3217) — observed .3413 PASSES both (b PASS);
label-permutation floor (c): acc p95 = .4422, observed .6900 above it (p ≈ .001; c PASS). So the W-vs-C
separation that exists is genuinely structural (above every null) — but the roles that would anchor anything
(totals, units) are NOT recovered, and the overall level fails the pre-committed power bar (a, d FAIL →
detector does not fire; criteria are conjunctive by prereg).

**Why (post-hoc diagnostics, non-verdict-changing, `data/ledger_roles/e007_posthoc.json`):**

1. **The derivation/held-out split crosses a real convention divide.** Totals words are essentially a Pylos
   habit: to-so/to-sa occurrences PY 261 vs KN 57 (whole corpus); inside KN multi-line ledgers, gold T = 28
   occurrences (0.4% of derivation tokens) vs 214 at held-out sites. Units: KN 319 vs PY 928 + TH 341. A
   majority decode fitted at KN structurally cannot learn either role.
2. **Rare-class-aware decode does not rescue T.** Re-decoding clusters by recall-lift (P(cluster|class),
   fitted on derivation) recovers units well (held-out U recall .862, F1 .588 — unit-slots ARE structurally
   identifiable: single-sign, group-preceded, numeral-followed) but totals stay unrecoverable: T precision
   .017 at recall .38 — chance-level smear. Best T cluster lift on derivation = 4.3× on a 0.4% base rate
   (≈1.8% purity). At KN, a totals line is structurally an ordinary line-initial word + big numeral; k-means
   geometry cannot isolate it.
3. **Post-hoc LA readout** (exploratory only, `e007_posthoc_la.json`; the gate never opened, so NO
   constraints were emitted): the KN-fitted decode predicts only W/C on LA (235 ledger docs), assigns all 35
   KU-RO occurrences to W, and only 119/363 known logogram occurrences to C — the transfer would have failed
   the consistency checks anyway.

## Mechanical verdict

Per the frozen rule (“LB leg does not fire → ROLE_INDUCTION_NO_POWER”):

> **ROLE_INDUCTION_NO_POWER** — an honest machinery-and-power negative: the pipeline is proven able to
> recover planted slot structure (PC1 = 1.0) but real LB ledger roles, under a site-held-out split, are not
> recoverable by blind k-means over per-occurrence structural features. NOT evidence that roles are
> unrecoverable in principle: units are near-recoverable (post-hoc U recall .86), totals fail for
> identifiable reasons (cross-site convention heterogeneity + 0.4% base rate + non-arithmetic features).

**What this does NOT claim:** nothing about LA; no constraint file was produced; no licence changes; the
known KU-RO/KI-RO/A-prefix structure (independent machinery) is untouched.

## Compliance line (Art. XXII)

Prereg frozen before run; PC1 run FIRST and honestly failed twice → machinery calibrated on synthetic only,
both deviations logged (DEV-1, DEV-2) — no real-corpus label was read during calibration; verdicts computed
by frozen arithmetic; multiplicity: one frozen config after synthetic calibration (the k sweep {6,8,10,12}
is declared and was scored on synthetic ground truth only); LA leg not run for record (gated), post-hoc LA
readout labeled exploratory; append-only artifacts under `epochs/EPOCH-007/` + `data/ledger_roles/`.

## Successor hypotheses

1. **Arithmetic totals feature is the missing discriminator:** a totals line satisfies num ≈ Σ(entry nums).
   Add exact/approximate sum-consistency features (doc-level subset-sum residuals) — this is structural,
   value-blind, and directly targets the T slot; re-run as a NEW epoch with its own prereg.
2. **Within-site document split, not cross-site:** derivation/held-out split KN-vs-rest confounds role
   induction with scribal-convention transfer. Split PY documents 50/50 (site-internal) to measure the
   role-induction ceiling separately from the convention-transfer question.
3. **Unit-slot channel is live:** the one structurally recoverable role (U recall .86 post-hoc) suggests a
   dedicated unit-slot detector (single-sign, group-preceded, numeral-followed, low type entropy) could be
   validated properly and transferred to LA fraction/metrogram signs — connects to the Bennett-credited
   metrology null and the fraction-order seal channel (F10).
4. **Supervised-on-LB transfer instead of unsupervised:** train a per-occurrence role classifier ON LB gold
   (allowed — LB is deciphered), transfer features-only to LA; the epoch's blindness constraint (unsupervised
   on both sides) was stronger than the mission requires (Art. XII only forbids circularity on LA).
5. **Sequence model over line grammars:** lines are short token-category strings (W C U N; W N; T C N…);
   an HMM/regular-grammar induction over category sequences (with numerals as anchors) models the SLOT
   as a position in a line grammar rather than a point in feature space — better suited to the totals-line
   syntax, testable first on PY.
6. **KI-RO/deficit slot needs entry-vs-annex geometry:** deficit terms live in structured sub-lists;
   per-occurrence features flatten this. A two-level (line-block) document model may expose the deficit slot
   that flat clustering cannot.
