# TASK N — FULL ADAPTIVE NULL PROGRAMME: SPECIFICATION (preregistered before the run)

**Campaign:** research/linear-a-anchor-lattice · **Seed:** 20260708 · **Constitution:** v2.2
**Stage header (Art. XXII):** articles_triggered = V, VII, VIII, IX, XI, XII, XV, XVII, XVIII.
Gates in force: `DEPENDENCY_COLLAPSED_INDEPENDENT_ANCHORS=0` (C), `LA_AT_IDENTIFIABILITY_ZERO`
(G), `JOINT_INFERENCE_NULL` (H), `ZERO_RETAINED` (I), `J_NOT_AUTHORIZED` (J).
**Script:** `scripts/n_adaptive_null_programme.py` (single deterministic run; every number in
the results reports is printed by the script — Invariant 12).
**Written BEFORE the programme was executed.** The thresholds and definitions below are frozen;
the results reports may not add post-hoc "positive" definitions.

## 1. Question

The campaign performed a large ADAPTIVE search: source selection (WP-D), anchor selection +
dependency-lineage assignment (WP-C), stroke-feature selection (WP-E), substitution-bridge
method selection (WP-F: M1_nn / M2_ot / M3_gw / M4_spectral), sign-inventory selection (3
grains), solver selection (3 solvers), candidate-value selection (65-slot grid), threshold /
restart / subgroup selection, and best-result reporting. Task N must reproduce that COMPLETE
adaptive search under null data and measure:

1. the family-wise false-positive rate of the DISCIPLINED pipeline (the Art. VII/VIII/XI/XII
   gate as actually run in Tasks C/H/I);
2. the family-wise false-positive rate of the NAIVE-ADAPTIVE pipeline (same search, no
   dependency collapse, no multiplicity deflation, best-of-everything reporting) — the
   calibration that the instruments can detect a fitted positive;
3. the search-adjusted significance of the campaign's ONE nontrivial positive-flavoured
   finding: the continuity-pins × LA-substitution **UNSAT** (15/24 both-pinned pairs violate
   same-C-or-same-V). Adjudication question, committed here: **is 15/24 violations MORE than a
   random pin-set of the same size/marginals would produce on the same rel graph?** If a random
   pin-set is also (almost) always UNSAT, the finding is GENERIC, not a real conflict.
4. whether the full adaptive pipeline, run under null, EVER produces a retained candidate or an
   apparent entropy reduction as large as any observed in the campaign.

## 2. Observed campaign statistics (frozen targets, from existing artifacts)

| id | statistic | observed | artifact |
|---|---|---|---|
| T1 | retained candidates (Art. XI gate) | 0 / 151 | `per_sign_table.json` |
| T2 | A-only mean abs. entropy reduction, conditional S2 | 0.000 bits | `h_null_random_anchor.json` |
| T3 | max independent (collapsed) anchors on any sign | 1 | `per_sign_table.json` |
| T4 | rel-channel satisfaction of the 38 continuity pins | 9/24 sat, 15/24 violated (UNSAT) | `h_model2_cp_domains.json` |
| T5 | licensed (S0) per-sign absolute bits | 0 | `h_setup_and_calibration.json` |
| T6 | naive contrasts recorded as violations: naive MDL ΔDL = −660.2; naive channel-stacking signs ≥3 "channels"; wrong-language 84–90% "recovery" @ FP≈1.0 | — | H §4, C §4, G bench |

## 3. Null families (16) and tiers

**Tier 1 — component nulls (cheap, ≥1000 total; planned ≈11,000).**
CN1 random value maps (uniform 65-grid on the 38 pinned signs), N=2000.
CN2 frequency-matched value maps (resampled from the real pin-value multiset), N=2000.
CN3 random anchors (38 pins on random signs, random values; analytic S2 surrogate), N=1000
    — component identical to Task H's 200-rep random-anchor null: CITED + extended, not replaced.
CN4 dependency-CLONED anchors (re-target the 47 value-bearing edges, PRESERVING the real
    lineage tags and their META_CONTINUITY ancestry), N=1000.
CN5 random external names (per edge, a random syllable string of the same slot length pins the
    re-targeted signs), N=1000.
CN6 wrong-language / random lexica (read the 43 anchored LA forms under the real pins against
    random lexica of matched size/length distribution; match = exact or ≤1 syllable edit),
    N=1000 lexica — Task G's wrong-language bench (84–90% @ FP≈1.0) is CITED as the
    corpus-scale version.
CN7 random stroke correspondences (metadata-shuffle of the 60 E4 pair records; top-1 combined
    score percentile), N=1000.
CN8 random substitution graphs (30 rel edges re-paired uniformly among the 33 rel-participating
    signs; real pins scored on the random graph), N=1000.
CN9 shuffled morphology labels (22 signs), N=1000 — expected structurally inert (value-free
    channel; recorded as an invariance check, not a power claim).
CN10 shuffled formula roles (6 signs), N=1000 — same status as CN9.
CN11 shuffled sites (geography permuted across the 47 value-bearing edges; leave-one-site leg
    re-evaluated), N=1000.
CN12 alternate sign inventories (conservative/split/merged) — deterministic (3 grains; H found
    38/38/37 pins, grain-invariant); becomes a SELECTION dimension in Tier 3.

**Tier 2 — moderate lattice nulls (full retention gate per replicate, ≥300 new).**
LN1 full re-targeting + random values + shuffled sites + per-replicate rel permutation check
    (200 perms), N=150.
LN2 dependency-cloned re-targeting with full gate, N=100.
LN3 grain-alternate re-targeting (50 per grain), N=150.
The existing 200-rep random-hyperedge null (Task I) and 200-rep random-anchor null (Task H) are
identical-component predecessors: CITED, not rerun.

**Tier 3 — FULL ADAPTIVE nulls (≥100; planned 120) + planted-positive calibration (20).**
Each replicate draws a null world (cycle: uniform re-target / frequency-matched values /
dependency-cloned) and then runs the ENTIRE selection stack an adaptive analyst had available,
reporting the best result of each layer:
  a. source-set selection (3: L-only / L+EG / all value-bearing) — WP-D;
  b. anchor-subset selection (greedy drop of up to 50% of pins to maximize rel-satisfaction) —
     best-of-anchor-subset;
  c. dependency-lineage accounting selection (collapsed vs naive-raw vs citation-stacking with
     H/C channels) — WP-C;
  d. stroke-feature selection (best of 12 random features on the E4 pair table) — WP-E;
  e. bridge-method selection (best of 4 simulated chance-level methods, each with its own
     1000-perm nominal p) — WP-F;
  f. sign-inventory selection (best of 3 grains) — CN12 as selection;
  g. solver selection (best of 3: M1 analytic-Gibbs surrogate, M2 arc-consistency count,
     M3 naive-MDL ΔDL) with best-of-5 seed restarts on M1;
  h. candidate-value selection (per pinned sign, best of top-3 alternative grid values for
     local rel-satisfaction);
  i. threshold selection (nominal p ∈ {0.01, 0.05, 0.10}; slot bar ∈ {3, 4}; naive gC drops
     the held-out leg);
  j. best-of-language (best of 8 random lexica per replicate).

**Planted-positive calibration (20 reps):** one random A-only sign receives 3 value-consistent
edges on 3 genuinely DISTINCT collapsed lineages (META_CONTINUITY, LIN_EG, synthetic
LIN_BILINGUAL), ≥2 concrete sites, and 1 non-vacuous held-out edge, on top of an otherwise-null
world. The DISCIPLINED gate must retain the planted sign (expected 20/20); otherwise the gate is
vacuously closed and the campaign zero is uninformative.

## 4. Frozen positive definitions (fail CLOSED; no additions after the run)

**DISCIPLINED positive** (any of):
- D1: disciplined retained ≥ 1 (Art. XI collapsed accounting, full Task-I gate: branches A/B/C
  + leave-one-anchor/-lineage/-site + adaptive-null band);
- D2: licensed (S0) A-only absolute reduction > 0, or conditional-S2 A-only mean reduction
  ≥ 0.1 bits/sign (the campaign's own reporting bar, H §2);
- D3: rel-channel global permutation p < 0.05 / 648 (Bonferroni over the enumerated selection
  cardinality 3 grains × 3 solvers × 4 bridge methods × 3 source sets × 6 thresholds = 648).

**NAIVE-ADAPTIVE positive** (any of, at the analyst's most favourable selection):
- N1: naive retained ≥ 1 (raw-lineage or citation-stacked accounting, no adaptive-null band,
  gC without the held-out leg);
- N2: any sign with ≥3 stacked "channels";
- N3: min nominal p across ALL selection layers < 0.10 (loosest threshold tried);
- N4: naive MDL ΔDL < 0 (anchored "wins" raw accounting);
- N5: best-of-language match nominal p < 0.05.

**FWER** = fraction of Tier-3 replicates with ≥1 positive (per arm), with one-sided exact
Clopper–Pearson 95% upper bound when the count is 0.
**FDR**: Benjamini–Hochberg over the campaign's mechanically recorded p-values
(p_rel_binom = 0.2521, p_rel_perm = 0.2794, best per-sign rel p = 0.0855 with ×24 multiplicity,
F2 bridge Holm-surviving pairs = 0, CN7 stroke percentile) at q = 0.05.

**UNSAT adjudication (T4), committed direction:** report P(violations ≥ 15 | CN1), P(violations
≥ 15 | CN2), P(UNSAT i.e. ≥1 violation | CN1/CN2), and the same on CN8 random graphs. Verdict
vocabulary: `UNSAT_GENERIC` if P(UNSAT | matched null) ≥ 0.95 and P(viol ≥ 15) > 0.05;
`UNSAT_SPECIFIC_CONFLICT` if P(viol ≥ 15 | both CN1 and CN2) < 0.05 after ×2 direction
correction; else `UNSAT_UNDERDETERMINED`.

## 5. Assumptions (Art. XVIII)

- A-N1: the analytic S2 surrogate for M1 (reduction = 0.1311 bits per parseable pinned sign,
  ρ=2/26) equals the Gibbs estimate up to MC noise ≤ 0.0002 bits (verified in H §2).
- A-N2: re-targeted edges keep their real slots/geography/derivation flags — the null cannot
  manufacture held-out edges (matches reality: all 208 edges are derivation-side); the planted
  control verifies the held-out leg separately.
- A-N3: chance compat rate on the 65-grid is computed exactly (P(same-C or same-V) = 0.2615)
  and empirically per family.

Compliance: no do_not_repeat lineage re-run (this is a null-calibration stage, not a value
search); no claim above L2 will be worded in the results; append-only.
