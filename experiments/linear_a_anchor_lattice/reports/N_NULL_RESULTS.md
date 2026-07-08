# TASK N — FULL ADAPTIVE NULL PROGRAMME: RESULTS

**Campaign:** research/linear-a-anchor-lattice · **Seed:** 20260708 · **Constitution:** v2.2
**Spec:** `reports/N_NULL_SPEC.md` (frozen before the run; no positive definition added after).
**Script:** `scripts/n_adaptive_null_programme.py` — single deterministic run, 5.3 s; re-run
byte-identical. **Artifact:** `data/controls/n_adaptive_null.json`. Every number below is
printed by the script (Invariant 12).

**Stage header (Art. XXII):** articles_triggered = V, VII, VIII, IX, XI, XII, XV, XVII, XVIII.
Gates in force: C `DEPENDENCY_COLLAPSED_INDEPENDENT_ANCHORS=0`, G `LA_AT_IDENTIFIABILITY_ZERO`,
H `JOINT_INFERENCE_NULL`, I `ZERO_RETAINED`, J `NOT_AUTHORIZED`.

## Verdict

**`ADAPTIVE_NULL_COMPLETE — DISCIPLINED_GATE_HOLDS / NAIVE_PIPELINE_FIRES_ALWAYS /
UNSAT_IS_GENERIC / 0 BH DISCOVERIES`**

- The **disciplined** pipeline (Art. XI collapse + retention gate + licensed accounting) never
  retains a candidate under any null, in any tier (0 retained in 120 full-adaptive × 3 grains,
  400 new lattice nulls, and the 400 cited predecessor reps).
- The **naive-adaptive** pipeline (citation-stacking, raw-lineage accounting, best-of-everything)
  fires in **120/120** null replicates, "retaining" a mean of **20.7 signs per replicate** from
  pure noise — reproducing the decipherment-delusion generator that G quantified (84–90%
  "recovery" at FP ≈ 1.0).
- The campaign's one positive-flavoured finding — continuity × substitution **UNSAT (15/24)** —
  is **GENERIC**: a random pin-set of the same size is UNSAT with probability **1.000**, and 15
  violations is *fewer* than the matched-null mean (16.3–17.7).
- The gate is not vacuously closed: **20/20 planted** genuinely-independent-lineage positives
  are retained.

## 1. Counts (spec §3 satisfied)

| tier | new replicates | cited (identical component, not rerun) |
|---|---|---|
| Tier 1 component nulls (CN1–CN12) | **13,000** | Task H random-anchor N=200; Task G wrong-language bench |
| Tier 2 lattice nulls, full gate (LN1–LN3) | **400** | Task I random-hyperedge N=200 (retained_max=0, max_ia=2); Task H N=200 |
| Tier 3 full adaptive | **120** (+20 planted) | repo gate calibration 3/500 = 0.6% (paper) |

## 2. Tier 1 — component nulls

| family | n | headline result |
|---|---|---|
| CN1 random value maps | 2000 | mean violations 17.71/24; P(viol≥15)=0.9315; **P(UNSAT)=1.000**; P(sat≥9)=0.152 |
| CN2 frequency-matched values | 2000 | mean violations 16.26/24; P(viol≥15)=0.7745; **P(UNSAT)=1.000**; P(sat≥9)=0.3725 |
| CN3 random anchors (extends H N=200) | 1000 | A-only mean reduction 0.039 bits (p5–p95 0.0304–0.0475); real = **0.000, below all 1000** (p_null≤real = 0.000) |
| CN4 dependency-CLONED anchors | 1000 | max independent anchors ever = **2**; branch A (≥3) opens **0/1000** — the collapse is invariant to re-targeting |
| CN5 random external names | 1000 | mean sat rate 0.3233 (chance 0.2615); P(UNSAT)=1.000 |
| CN6 random lexica on real pins | 1000 | 6 fully-readable forms; mean 0.075 matches/lexicon, max 2 — but G's corpus-scale bench: 0.836–0.895 "recovered" at FP 0.9998–1.0 (cited) |
| CN7 random stroke correspondences | 1000 | real top-1 combined-score percentile p = 0.0759 (ns; channel already SOURCE_BLOCKED) |
| CN8 random substitution graphs | 1000 | real pins on random graphs: sat rate 0.3192 vs real 0.375; P(UNSAT)=1.000; P(viol-rate ≥ real) = 0.728 |
| CN9 shuffled morphology | 1000 | structurally inert: 0 gate outcomes changed (value-free channel; invariance check, not power) |
| CN10 shuffled formula roles | 1000 | structurally inert: 0 changed |
| CN11 shuffled sites | 1000 | real signs passing leave-one-site = 10 vs null mean 4.51 (p = 0.005 nominal; ×12 component families → 0.06, ns; loo_site is a value-free robustness leg — it can never create a positive without a branch A/B/C) |
| CN12 alternate inventories | 3 grains | syllabic 128/131/124; lattice-side pins 38/38/36 (H's inventory-side extraction: 38/38/37 — one merged-grain counting-path difference, no effect: A-only-with-pin = ∅ in all grains) |

## 3. Tier 2 — lattice nulls with the full retention gate (400 new)

| family | n | disciplined retained | max indep anchors | naive retained |
|---|---|---|---|---|
| LN1 re-target + random values + shuffled sites + per-rep 200-perm rel check | 150 | **max 0** (mean 0.0) | 2 | mean **19.91**/rep; ≥1 in **150/150** |
| LN2 dependency-cloned, full gate | 100 | **max 0** | 2 | — |
| LN3 grain-alternate (50 × 3 grains) | 150 | **max 0** (all grains) | 2 (all grains) | — |
| (cited) Task I random-hyperedge | 200 | max 0 | 2 | — |

## 4. Tier 3 — full adaptive nulls (120 reps; see N_ADAPTIVE_FALSE_POSITIVE_RATE.md)

Each replicate ran the complete selection stack of the spec (§3 a–j: source sets, greedy
anchor-subset, lineage-accounting choice, 12 stroke features, 4 bridge methods, 3 grains,
3 solvers + 5 seed restarts, top-3 value selection, 3 p-thresholds × 2 slot bars, 8 lexica)
and reported the best of everything.

| arm | FWER | breakdown |
|---|---|---|
| DISCIPLINED (frozen D1–D3) | **10/120 = 0.083** (CP95 ≤ 0.137) | d1 retained: **0/120**; d2 conditional-S2 ≥ 0.1 bits: **10/120**; d3 rel Bonferroni: **0/120** |
| NAIVE-ADAPTIVE (frozen N1–N5) | **120/120 = 1.000** | n1 naive-retained: 120; n2 ≥3 stacked channels: 120; n3 min nominal p < 0.10: 117; n4 naive MDL < 0: 120; n5 language: 8 |

The 10 disciplined "positives" all come from the **d2 conditional-S2 leg** (values 0.100–0.106
bits, just over the 0.1 bar) — the statistic the constitution refuses to license (conditional on
the unearned META_CONTINUITY lineage, Art. XV) and which the campaign only ever reported as
conditional. The **licence-gated legs fired 0/120** (d1, d3; joint CP95 upper 2.46% each),
consistent with the repo-level gate calibration (3/500 = 0.6%). Real-data reference: the
campaign's observed conditional-S2 A-only value is **0.000 bits — below every one of the 120
null replicates**. Lesson recorded: conditional-S2 numbers are anticonservative under adaptive
search (≈8% standalone FWER) and must never be promoted to positives; the campaign never did.

**Planted-positive calibration: 20/20 retained** (3 value-consistent, lineage-distinct edges +
2 sites + 1 non-vacuous held-out edge on one A-only sign) → `GATE_OPENS_ON_GENUINE_INDEPENDENCE`.
The zero on real data is a property of the evidence (one collapsed meta-lineage), not of the gate.

## 5. UNSAT adjudication (the committed question, spec §4)

Observed: 15/24 both-pinned substitution pairs violate same-C-or-same-V (Task H M2, UNSAT).

| null | mean violations | P(viol ≥ 15) | P(UNSAT, ≥1 viol) |
|---|---|---|---|
| CN1 uniform value maps (2000) | 17.71 | 0.9315 | **1.000** |
| CN2 frequency-matched (2000) | 16.26 | 0.7745 | **1.000** |
| CN8 random substitution graphs (1000) | — | (viol-rate ≥ real) 0.728 | **1.000** |

**Verdict (frozen vocabulary): `UNSAT_GENERIC`.** 15/24 violations is *not* more than a random
pin-set produces — it is **fewer than the matched-null mean**; the sat-high direction is likewise
ns (perm p = 0.2794, Task I, cited). Every random pin-set of this size on this rel graph is UNSAT
(P = 1.000 in all three matched families). The Task-H UNSAT therefore demonstrates only that the
substitution channel and the continuity pins are *generically* incompatible under strict
axis-semantics at this density — it is **not** evidence of a specific, structured conflict, and
symmetrically it provides **no** evidence that the continuity values are wrong (they violate
slightly less than chance). It remains what H said it was: the channels cannot both be taken as
hard constraints; nothing more.

## 6. FDR over the campaign's recorded p-values (BH, q = 0.05)

| test | p | BH q |
|---|---|---|
| CN7 stroke top-1 percentile | 0.0759 | 0.4554 |
| rel binomial calibration (H) | 0.2521 | 0.5588 |
| rel perm global (I) | 0.2794 | 0.5588 |
| F2 bridge best-exact (Holm survivors = 0) | 1.0 | 1.0 |
| UNSAT viol≥15, ×2 directions | 1.0 | 1.0 |
| rel best per-sign ×24 (I) | 1.0 | 1.0 |

**Discoveries at q < 0.05: 0.** The campaign made no positive claim, and none was available to
make.

## 7. The spec's question 4, answered

*Does the full adaptive pipeline, run under null, ever produce a retained candidate or an
apparent entropy reduction as large as any observed?*

- **Retained candidate: never.** 0 retained across 120 adaptive replicates × 3 grains, 400 new
  lattice nulls, 200 cited hyperedge nulls, under the disciplined gate.
- **Apparent entropy reduction: always.** The observed A-only reduction is 0.000 bits;
  **120/120** null replicates produce a conditional-S2 reduction ≥ observed (max 0.106 bits) —
  i.e. the real lattice sits at or below null in every replicate (the H `REAL_BELOW_NULL`
  corollary, now confirmed under the full selection stack). The campaign's larger conditional
  numbers (S2 all-sign 0.032; S3 0.888; S1 1.415 bits) are pin-count artifacts reproduced
  identically by construction under null pins and were never licensed as positives.

## 8. Compliance line

Art. V: all wording ≤ L2; no value claim. Art. VII: full search receipt = the spec's frozen
selection stack, all layers run, nothing withheld; identical predecessor nulls cited rather than
laundered as new evidence. Art. VIII/XI: effective-n and clone collapse are the *object under
test* and were applied and stress-tested (CN4, LN2). Art. XII: no null grades a target by the
rule that created it; the planted control uses synthetic independent lineages. Art. XV: relative/
conditional reductions reported as such; the d2 anticonservatism is recorded as a lesson, not a
result. Art. XVII: append-only; nothing supersedes H/I — this stage *confirms* them. Art. XVIII:
assumptions A-N1–A-N3 held (S2 surrogate max MC deviation 0.0002 bits; no held-out edge
manufactured). **COMPLIANT.** No licence changes; SEMANTIC+ remains NOT_AUTHORIZED.
