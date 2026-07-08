# EPOCH-002 — PREREGISTRATION (frozen BEFORE any analysis run)

**Campaign:** linear-a-frontier-72h · frontier **F3** (substitution-neighborhood bridges v2)
**Branch:** research/linear-a-frontier-72h · **Seed:** 20260708 · **Date frozen:** 2026-07-08
**Articles triggered:** V (claim layers), VII (search receipt), VIII (effective_n + multiplicity),
IX (info budget), XI/XII (non-circularity — no grading a target by the rule that created it),
XV (transfer licences: a relative-class result earns NO value), XXII (stage header).
**Claim layer of ANY result here: L2 (relative/structural), on KNOWN scripts (LB, Cypriot).
No Linear A value claim can emerge from this epoch.**

## Question

The FLAT substitution-neighborhood bridge failed even on known LB<->Cypriot
(anchor-lattice F2: best exact 0.064, ZERO Holm survivors → `CROSS_SCRIPT_SUBSTITUTION_BRIDGE_NO_POWER`),
while the within-script flat channel is real (F1/C_AUDIT: cofill-Jaccard same-C AUC 0.700 full,
0.750 frequency-disjoint, LOSO min 0.683). Does HIGHER-ORDER structure do better —
tested ON THE KNOWN SCRIPT FIRST (opaque LB; values grade only)?

## Non-circular contract (Art. XI/XII)

All motif graphs/similarities are built from sign IDENTITY, word co-occurrence, document
series/site membership ONLY. Known phonetic values are read ONLY afterward to GRADE
(relation(): same_consonant / same_vowel / spelling_variant / cross). Cross-script geometry
operates on opaque per-script node IDs with target order shuffled (seeded).

## Data / units (frozen)

- LB = DĀMOS wordform stream (`f_bridge_common.load_lb_damos`, expected 13,562 word tokens,
  3,856 docs, site + series metadata). Scorable signs: `parse_cv` non-None, support ≥ 2
  word-types (expected 72). Graded pairs expected {same_C 121, same_V 497, sv 9, cross 1929}.
- Cypriot = `csyl-greek.cog` column 0 (693 words); LB-cog = `linear_b-greek.cog` (919 words).
- Derivation set = full corpus (graph construction); held-out regimes = (a) frequency-disjoint
  pair restriction (4 support-quartile bands, within-band pairs only — the split that killed the
  position channel), (b) formula-disjoint leave-one-series-out (6 largest series by word count;
  graph REBUILT on complement per fold). Both inherited unchanged from F1.

## Motif families (frozen; exactly these 3, no post-hoc variants)

- **MF_A trigram_frame** — sign triples: for each word TYPE of length ≥ 2, each position p gets
  joint 2-sign frame (prev or '^', next or '$'). Per-sign frame set; similarity = Jaccard.
- **MF_B formula_slot** — flat whole-word one-slot frames keyed ADDITIONALLY by document series:
  key (series, L, p, ctx); fills = word types attested in docs of that series. Cofill-Jaccard.
  Substitutions count only within the same formula(series) slot.
- **MF_C site_stratified** — flat frames keyed by site; per-site cofill-Jaccard J_s(a,b);
  similarity = mean of J_s over sites where BOTH signs occupy ≥ 1 multi-fill frame; 0 if none.
  All sites used. Secondary descriptive: cross-site replication count.

**Flat baseline** = `f_bridge_common.similarity_matrix(kind="jaccard")` (corpus-wide whole-word
one-slot cofill-Jaccard), recomputed in-run for paired comparison.

## Positive control (run FIRST, gate on it)

Flat full-corpus same-C AUC must land in [0.68, 0.72] (F1 = 0.700; C_AUDIT 0.703/0.704).
Outside → `DETECTOR_BROKEN`, epoch aborts, no verdict.

## Negative / adversarial controls (frozen)

1. **Frequency-matched label null** — permute the sign→value map WITHIN frequency band
   (1000 perms, one-sided p on AUC); primary null for significance.
2. **Degree-preserving null** — permute sign labels on the sign–frame incidence list
   (preserves each sign's frame count AND each frame's fill count; bipartite configuration
   null), 200 perms, per family; report p; observed must exceed null p95.
3. **Wrong-language (shuffled) corpus** — signs shuffled WITHIN each word token (seeded),
   full rebuild of all similarities; PASS = same-C AUC of every family < 0.55 on the
   shuffled corpus (structure, not frequency, carries the signal).

## Endpoints + multiplicity (Art. VIII)

- Primary endpoint (within leg): same-C AUC on frequency-disjoint pairs; secondary: same-V AUC.
- **Holm across 3 motif families × 2 axes = 6 tests** on the frequency-matched label null p's.
- Superiority vs flat: paired SIGN bootstrap (resample the 72 signs with replacement, 1000×,
  same resample scores motif and flat; self-pairs excluded), 95% percentile CI of
  Δ = AUC_motif − AUC_flat, computed full-corpus and frequency-disjoint.
- LOSO: 6 folds; per fold, family beats flat if same-C AUC_family > AUC_flat (both rebuilt
  on the fold's complement corpus).

## Mechanical verdict — WITHIN-SCRIPT leg, per family (frozen order)

1. Holm-adj p(same-C, freq-disjoint, label null) ≥ 0.05 → **NO_POWER**
2. elif 95% CI of Δsame-C(freq-disjoint) > 0 entirely AND LOSO wins ≥ 5/6 → **SUPERIOR**
3. elif 95% CI < 0 entirely → **INFERIOR**
4. else → **EQUIVALENT**

Leg verdict `MOTIF_WITHIN = SUPERIOR` if any family SUPERIOR; `NO_POWER` if all NO_POWER;
`INFERIOR` if best family INFERIOR; else `EQUIVALENT`.

## Mechanical verdict — CROSS-SCRIPT leg

Family MF_A only (MF_B/MF_C are **SOURCE_BLOCKED** cross-script: the Cypriot/LB cog lexical
lists carry no series/site metadata — declared here, before the run). Pairs:
CTRL = LB-DĀMOS split-half (identity GT, seeded half-split as F2, expected n≈71);
KNOWN = LB-cog ↔ Cypriot-cog (same-value GT, MIN_SUP 3, expected n≈47).
Methods = F2's M1 (NN-transfer LOO), M2 (structural signature), M3 (entropic GW),
M4 (spectral+Procrustes LOO), unchanged, with the similarity matrix swapped to MF_A.
Permutation null 1000×; **Holm across 4 methods × 3 metrics = 12 tests per pair** (as flat F2).

1. KNOWN motif has ≥1 `:exact` Holm-0.05 survivor (flat had ZERO) → **SUPERIOR**
2. elif CTRL motif has ≥1 `:exact` Holm survivor → **EQUIVALENT** (identity carried; KNOWN
   still at floor, as flat)
3. elif flat CTRL had survivors (it did: M1/M3/M4) → **INFERIOR** (motif loses the identity
   ceiling flat kept)
4. else → **NO_POWER**

## Linear A application (conditional; frozen)

Run LA↔LB with MF_A ONLY IF cross leg = SUPERIOR. Otherwise `LA_LEG=NOT_RUN` — bounded by
known-script calibration (this is the F2 discipline; running it anyway would be multiplicity
farming).

## Search receipt (Art. VII)

Everything tried is listed above: 3 families × {full, freq-disjoint, LOSO×6} × 2 axes within;
1 family × 2 pairs × 4 methods × 3 metrics cross; 3 adversarial controls; no other variants,
kernels, thresholds, or hyperparameters will be tried; any deviation = new preregistration.
Parameters inherited frozen from F1/F2: bands nb=4, folds=6, MIN_SUP=3, N_PERM=1000 (200 for
degree null), seed 20260708.

## Falsifiable prediction (committed)

If higher-order motif structure genuinely adds cross-script-transportable signal, MF_A must
(i) at least match flat within-script under both holdouts AND (ii) produce a Holm-surviving
exact recovery on KNOWN LB↔Cypriot where flat produced zero. Confidence it does: 0.15
(the F2 failure looked like corpus-size power, which motifs sparsify further, not densify).
