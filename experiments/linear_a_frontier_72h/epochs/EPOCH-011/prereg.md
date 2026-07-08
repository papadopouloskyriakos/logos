# EPOCH-011 — PREREGISTRATION (frozen BEFORE any analysis run)

**Campaign:** linear-a-frontier-72h · frontier **F5** (gate A) — unit-slot + arithmetic-totals detectors,
the two channels EPOCH-007 left live (post-hoc U recall .862; totals failed for want of arithmetic features).
**Epoch question:** (1) Can a dedicated, preregistered UNIT-SLOT detector — formalizing the E007 post-hoc
geometry — be validated on LB under a WITHIN-SITE split (killing the KN-vs-rest convention confound) and
transferred blind to LA to yield a candidate metrogram class (L2/L3)? (2) Can a value-blind ARITHMETIC
TOTALS detector (doc-level sum-consistency, the KU-RO logic generalized) be calibrated on LB to-so docs and,
applied blind to LA, recover KU-RO / PO-TO-KU-RO and surface NEW totals-word candidates? (3) Do the two
detections cohere with the E004 fraction-sequence channel (do fractions follow unit/quantity slots)?
**Branch:** research/linear-a-frontier-72h · **Seed:** 20260708 · **Date frozen:** 2026-07-08
**Substantive gate:** A.
**Articles triggered:** V (all claims L2/L3 functional-slot / notation-structure; NO value/semantic claim can
emerge), VII (search receipt: rule/variant spaces enumerated below, selection on train folds only), VIII
(effective_n: (doc,type)-deduped counts for all binomials), IX (info budget: candidate lists carry per-type
n and site spread), XI/XII (features never read sign values; LB gold labels grade only; KU-RO/PO-TO-KU-RO
are held-out TARGETS of the LA leg, never inputs to it), XV (no licence earned or touched), XVII
(append-only; deviations logged in result.json), XVIII (assumptions below), XXII (this header).

## Prior art cited + differenced (do-not-repeat check)

- **EPOCH-007 (ROLE_INDUCTION_NO_POWER):** blind k-means over 15 structural features failed the conjunctive
  bar (held-out macro-F1 .341; U/T F1 = 0 under majority decode); post-hoc: units near-recoverable (lift
  decode U recall .862), totals unrecoverable at KN (0.4% base rate, no arithmetic feature, convention
  divide). **Difference here:** (i) dedicated per-role detectors instead of one 4-class clustering; (ii)
  WITHIN-SITE (KN-train/KN-test) split so role-induction power is not confounded with convention transfer;
  (iii) an explicit arithmetic sum-consistency feature — the successor hypotheses #1–#3 of E007, run as a
  new epoch with its own prereg.
- **Observable-channels programme:** L3 word-context→commodity-identity REFUTED — NOT re-run; a unit-slot
  or totals-slot verdict says nothing about which commodity/quantity a sign denotes.
- **Prior campaigns' KU-RO sum-check** (12h campaign: "KU-RO 17×"): used KU-RO as a KNOWN anchor to test
  arithmetic. Here the direction is inverted and blind: the detector never sees which word is KU-RO; KU-RO
  recovery is the held-out SCORING event (Art. XII: the target is not created by the rule that grades it —
  KU-RO's totals role was established by independent prior scholarship + campaigns).
- **E004 fraction-order seal:** fraction-sign sequence structure (L2/L3). Used here only in cross-check C
  (fraction events' positional relation to detected slots); no seal content re-derived.

## Data / units (frozen; pre-freeze DESCRIPTIVE audit only — counts, no role analysis, no geometry peeked)

- **LB:** DĀMOS via `scripts/e007_ledger_roles.py::parse_lb` (unchanged). Ledger filter (unchanged): ≥2
  numerals AND ≥3 sign-groups AND ≥2 lines → 1,093 docs (KN 660, non-KN 433). Gold (grading ONLY, E007
  rules): T = hyphenated casefold to-so/to-sa…; U = single-part ∈ {S,V,T,Z,M,N,L,P,Q}; C = other
  logogram; W = syllabic word. Pre-audit: 91 LB ledger docs contain gold-T; **0 gold-T tokens are
  immediately numeral-followed** → totals attribution must bridge intervening tokens (variant space below).
- **LA:** `corpus/silver/inscriptions_structured.json` via `parse_la` (unchanged; fractions = `other`
  events, excluded from the group/numeral token stream, tracked separately for cross-check C). Ledger
  filter → 207 docs (Haghia Triada 134, Khania 23, Zakros 23, rest ≤7). Pre-audit: 809 single-sign group
  occurrences; 961 numeral-followed group occurrences; KU-RO 35 occ; PO-TO-KU-RO 2 occ.
- **Splits:** Detector A derivation = KN docs, split 50/50 into KN-train / KN-test by sha1(doc_id) parity
  (seeded, frozen); site-transfer grade = all non-KN docs. Detector B variant selection = KN docs only;
  grade = non-KN docs. LA folds for robustness: HT vs pooled non-HT.

## Blinding contract (Art. XI — identical to E007)

Detector inputs: token category (group/numeral), numeral VALUES (L1), n_signs, line/doc position, hashed
type identity + unlabeled type-level stats computed within the partition being scored. Editorial case
erased. Gold labels and raw readings enter ONLY the grading/reporting modules (unblinding candidate lists
for the report is presentation, not feature use).

## Detector A — unit-slot (frozen rule space, 6 rules)

Candidate occurrence iff `n_signs == 1 AND followed_by_num AND X`, X ∈:
  R1 TRUE; R2 prev_is_num; R3 prev_is_group; R4 not_line_initial;
  R5 prev_is_num AND type_fn ≥ 0.5; R6 type_fn ≥ 0.5
(prev = previous token in line; type_fn = type's followed-by-numeral rate in the partition, unlabeled).
Selection: the rule maximizing F1(gold U) on KN-train. Frozen thereafter.
Grade: F1(U) on KN-test (within-site) and on non-KN (site transfer; type stats recomputed on non-KN,
unlabeled). **PC-A (run FIRST):** two synthetic families (150 docs each, 50/50 split, seeded): geomA = unit
sign between commodity and numeral (E007 generator geometry); geomB = unit sign after the first quantity
numeral with its own numeral (LB metrological geometry). Full pipeline (selection on synth-train, grade
synth-test) must reach F1(U) ≥ 0.90 on BOTH families, else machinery FAIL → NO_POWER, stop detector A.
**Null N-A1:** numeral-detach (E007 `detach_numerals`), 25 reps on non-KN, full re-featurize + re-grade
with the frozen rule → p95 F1(U).
**LB fire criteria (conjunctive):** (A-a) KN-test F1(U) ≥ 0.60; (A-b) non-KN F1(U) ≥ 0.50;
(A-c) non-KN F1(U) > p95 of N-A1.
**LA leg (only if A fires):** apply frozen rule (LA-partition type stats). Outputs: per single-sign type,
n candidate hits + site spread → candidate metrogram class = types with ≥3 hits.
Transfer criteria: (A-d) ≥2 types with ≥3 hits; (A-e) ≥1 such type with hits at ≥2 sites.
LOSO robustness (reported, non-gating): recompute type stats within HT-only and non-HT-only folds;
report candidate-type overlap.

## Detector B — arithmetic totals (frozen variant space, 3 sums × 2 attributions = 6)

Numerals of a doc in reading order n_1..n_k (values as parsed; LA fractions excluded — noted as a recall
limitation). A numeral n_i is SUM-CONSISTENT under:
  V1 GLOBAL: k ≥ 3 AND n_i == Σ_{j≠i} n_j;
  V2 PREFIX: ≥2 prior numerals AND n_i == Σ_{j<i} n_j;
  V3 SUFFIX-BLOCK: ∃ j ≤ i−2 with n_i == Σ_{m=j..i−1} n_m (≥2 terms; handles multi-section docs and
  grand totals over subtotal blocks).
Attribution of a sum-consistent n_i to a word: A1 NEAREST = last group token before n_i in its line;
A2 LINE-INITIAL = first group token of n_i's line occurring before n_i. No attributable group → no candidate.
Candidates deduped to (doc, type) pairs (Art. VIII).
Selection: variant (V,A) maximizing F1(gold T) on KN ledger docs; if all variants score 0 true positives on
KN, fallback = the variant selected on synthetic PC-B (declared fallback). Frozen thereafter.
**PC-B (run FIRST):** synthetic family (150 docs, E007 generator: totals line = totals-word + commodity +
exact-sum numeral; distractor entry quantities) — the KN-selection procedure run on synth-train, graded on
synth-test, must reach precision ≥ 0.90 AND recall ≥ 0.90 for the planted totals word, else NO_POWER, stop.
**Null N-B1:** permute numeral values among numeral positions within each doc (25 reps, frozen variant) →
p95 precision(T) on non-KN. **Adversarial baseline (reported, non-gating):** MAX-NUM = attribute the doc's
maximum numeral by the same attribution rule — does sum-logic beat "big number"?
**LB fire criteria (conjunctive):** (B-a) non-KN precision(T) ≥ 0.30; (B-b) non-KN recall(T) ≥ 0.10 (denom
= all gold-T occurrences in non-KN ledger docs); (B-c) precision(T) > p95 of N-B1; (B-d) ≥10 candidate
(doc,type) pairs on non-KN.
**LA leg (only if B fires):** apply frozen variant blind. Checks (Holm α = .05, m = 2), one-sided binomial
on (doc,type)-deduped counts; chance p for a type = its share among (doc,type) pairs obtained by applying
the SAME attribution rule to ALL numerals (no sum test):
  T1 (primary): KU-RO enriched among candidates; T2: PO-TO-KU-RO enriched.
LOSO (reported): KU-RO enrichment direction in HT fold and non-HT fold where KU-RO occurs.
NEW totals-word candidates: types ∉ {KU-RO, PO-TO-KU-RO} with ≥2 (doc,type) hits → each reported with n,
sites, split-half replication flag (sha1(doc_id) parity halves; replicated = ≥1 hit in each half). These
are PROPOSED L2/L3 constraints only.

## Cross-check C (non-gating, reported)

LA fraction events = `other` events whose raw contains a vulgar-fraction glyph (¹⁄ₓ / ³⁄₄ / ≈-variants) or a
codepoint in the Linear A block U+10760–U+10774 (fraction/klasmatogram range). For each fraction event with
a preceding same-line stream event, classify the predecessor: numeral / detector-A LA candidate type /
other single-sign word / multi-sign word / fraction. Report the distribution + one-sided binomial: is
P(predecessor ∈ detector-A candidate types) > those types' base rate among all in-line token positions in
fraction-bearing LA ledger docs? Coherence statement only; no verdict weight.

## Mechanical verdicts (frozen; per detector)

- PC fails → **NO_POWER** (machinery).
- LB fire criteria not all met → **NO_POWER** (an honest power negative; report which criterion failed).
- LB fires; LA transfer criteria fail (A: A-d/A-e; B: T1 not Holm-significant) → **VALIDATED_LB_ONLY**.
- LB fires AND LA criteria met → **VALIDATED_AND_TRANSFERS** (A: emit `la_unit_slot_candidates.json`;
  B: emit `la_totals_candidates.json`; all entries PROPOSED L2/L3, lattice-ready, each with its own
  replication flags).
Epoch verdict = the pair (A, B) + cross-check C narrative.

## Multiplicity receipt (Art. VII/VIII)

Detector A: 6 rules, selected on KN-train only. Detector B: 6 variants, selected on KN only (declared
synthetic fallback). LA checks: Holm m=2 (detector B); detector A LA criteria are count thresholds, not
p-values. No other sweeps; any deviation logged in result.json.

## Assumptions (Art. XVIII)

A1: DAMOS editorial case yields reliable GOLD labels (grading only) — inherited E007.
A2: within-partition unlabeled type-stats are transduction, not leakage — inherited E007.
A3: LA `stream` segmentation + numeral values (GORILA) trusted at L1 — inherited.
A4: excluding LA fractions from sums biases detector B toward integer-total docs (recall loss, direction
conservative for T1 since KU-RO totals with fractions are missed, not invented).
A5: chance model for T1/T2 (attribution-of-all-numerals share) is the right null for "sum test adds
nothing"; N-B1 additionally tests the value-position link.
A6: sha1(doc_id) parity is an exchangeable doc split.
