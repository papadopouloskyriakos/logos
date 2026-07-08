# TASK H — Joint Anchor-Lattice Inference: RESULTS

**Campaign:** research/linear-a-anchor-lattice · **Seed:** 20260708 · **Constitution:** v2.2
**Script:** `scripts/h_joint_inference.py` (single run, deterministic; all numbers below are
printed by the script — Invariant 12). **Artifacts:** `data/candidates/h_*.json` (7 files).
**Spec:** `reports/H_JOINT_INFERENCE_SPEC.md` (predictions P1–P5 committed before the run).

**Stage header (Art. XXII):** articles_triggered = V, VII, VIII, IX, XI, XII, XV, XVII.
Gates: DEPENDENCY_COLLAPSED_INDEPENDENT_ANCHORS=0 (Task C); WP-D SEED_A=0; WP-E SOURCE_BLOCKED;
WP-F NO_POWER. Assumptions: C1 lattice complete; META_CONTINUITY_LA_eq_LB circular-for-values.

## Verdict

**`JOINT_INFERENCE_NULL — LATTICE_UNDERDETERMINED (3/3 solvers agree)`**

The complete dependency-aware lattice, fed to three genuinely different joint solvers, moves
**only the 38 continuity-pinned AB/logogram signs**, and only **conditionally on the unearned
META_CONTINUITY licence**. For the 69 A-only signs: **0.000 bits** of absolute value-entropy
reduction in every solver × every scenario × every sign inventory — and that is **strictly below
the random-anchor null** (p = 0.000), because the real anchors never touch A-only signs at all.
All predictions P1–P5 SUPPORTED. No licence changes; SEMANTIC+ remains NOT_AUTHORIZED.

## 1. Setup (from the lattice, mechanically)

163 signs (69 A-only) · value domain |D| = 67 CV cells · baseline H0 = 6.066 bits/sign ·
47 value-bearing edges → 148 raw pin slots → **38 pinned signs after Art.-XI clone collapse**
(all AB-shared/logogram; the single A-only pin `*49` is vacuous — its label is `*49` itself) ·
30 unique relative-substitution pairs over 33 signs (value-free, Art. XV) · Egyptian lineage:
0 edges with content (WP-D SEED_A=0).

**Channel calibration (before solving):**

| Channel | Calibrated strength | Consequence |
|---|---|---|
| Rel-substitution (same-C-or-same-V vs graded benchmark) | 9/28 sat = 0.321 vs chance 0.251, one-sided binomial **p = 0.252** → AT CHANCE | 0.359 bits/edge max; soft factor only |
| Cross-script bridge (WP-F F4) | 1 − 0.9995 normalized uncertainty → **0.0027 bits/sign** | recorded, weight ≈ 0 |
| Stroke (WP-E) | bbox aspect AUC 0.57–0.60, SOURCE_BLOCKED | excluded, recorded |
| Morphology/formula (22+6 edges) | value-free structural roles | 0 bits to value posteriors |
| ρ_META posterior from the lattice itself | clone edges agree with prob. 1 whether or not the convention is true → Bayes factor = 1 | posterior(ρ) = prior(ρ): the lattice contains **no internal evidence** for its own value-bearing channel |

## 2. H_MODEL_1 — Bayesian factor graph (Gibbs, 3×3000 sweeps)

Mean entropy reduction (bits/sign; A-only column is the campaign question):

| Scenario (ρ_META) | pinned-sign H | mean red. all 163 | mean red. 69 A-only | signs > 0.1 bit |
|---|---|---|---|---|
| S0 collapse-compliant (ρ=0, the licensed state) | 6.066 | 0.0002 (MC noise) | 0.00001 | **0** |
| S2 held-out-calibrated (ρ=2/26) | 5.935 | 0.032 | **0.000** | 38 |
| S3 truth-layer cap (ρ=0.75) | 2.294 | 0.888 | 0.0002 | 38 |
| S1 conditional-on-continuity (ρ→1) | 0.000 | 1.415 | 0.0002 | 38 |

A-only signs above 0.1 bit: **none, in any scenario.** The Art.-XI clone-stacking error,
quantified: sign A carries 9 clone edges; naive stacking drives its entropy 5.92 → **0.00 bits
at ρ = 0.077** (mean pinned entropy 2.25 vs 5.93 collapsed) — i.e. treating citations as
independent manufactures near-certainty out of a 7.7%-reliable channel.

## 3. H_MODEL_2 — CP / exact domains + model counting

- **Mutual-consistency audit (new sharp negative):** anchors-hard + rel-hard is **UNSAT** —
  15/24 both-pinned substitution pairs violate same-C-or-same-V under the graded labels
  (e.g. PA–TE, KI–WA, JA–U, KU–MA, KU–SA). Confirmed by counting: 0 solutions (log10 = −inf).
  The continuity pins and the LA substitution neighborhoods are **mutually inconsistent** under
  any strict phonological-axis semantics — the LA substitution channel is not the LB consonant
  axis (WP-F), and is at chance (§1).
- **Arc-consistent domains** (anchors hard, 15 violated edges dropped): 42/163 signs reduced —
  the 38 pins (singletons, = backbone) + 4 unpinned neighbors: QE→5 values, *324→18, PA3→18,
  WI→18. Residual solution space on the rel subgraph: 10^5.69.
- **S0 (licensed state) counting:** rel-hard removes **56.0 JOINT bits** across the 33-sign
  subgraph (10^43.4 solutions vs 10^60.3 free) but per-sign marginals stay uniform — gauge
  symmetry; **0 absolute bits** (Art. XV). Whole-system solution space ≈ **10^280.8**; quotient
  by the relabeling gauge group (12!·5! ≈ 10^10.8) leaves **≥ 10^270 equivalence classes**.
- A-only: `*324` (via ZU) is the only A-only sign with any domain reduction — 18/67 values,
  conditional on ρ=1 AND a rel semantics that is globally UNSAT/at-chance; relative-only,
  relabeling-invariant, 0 absolute bits.

## 4. H_MODEL_3 — MDL / penalized beam search

Anchored system vs unanchored null system, ΔDL = DL(anchored) − DL(unanchored):

| Evidence accounting | credited slots | ΔDL (bits) | winner |
|---|---|---|---|
| naive_raw (clones counted) | 147 | **−660.2** | ANCHORED — TRIVIAL_RECOVERY of the generating convention (Art. XII violation, shown for contrast) |
| dedup (unique sign-pins) | 38 | **+1.0** | UNANCHORED (credit = cost exactly; the 1-bit flag decides) |
| art12_discounted (effective_n, Art. VIII/XI) | 0 | **+231.5** | UNANCHORED |

The MDL verdict **flips entirely with dependency accounting** — the anchored system only wins
when clone edges are counted as independent data. Rel structure never pays: max data credit
10.06 bits vs 200.2 bits to specify the subgraph → UNSTRUCTURED wins. Tied-system enumeration
(beam K=500, Δ=1 bit): the 24-sign component alone holds ≥196 equivalence classes in a truncated
beam; exact tie counts are the §3 solution counts (10^x scale). Signs value-stable across ties =
exactly the 38 pins.

## 5. Random-anchor null (N=200)

Real A-only mean reduction = **0.000 bits** (0 parseable A-only pins). Null (47 edges re-attached
to random signs): mean 0.0316 bits, 5th–95th pct [0.0228, 0.0381], mean 16.6/69 A-only pinned.
**p(null ≤ real) = 0.000** → the real lattice sits *below every one of 200 nulls*. **No solver
reduces A-only value entropy below the random-anchor null** — the answer to the campaign question
is NO, with the stronger corollary that the real anchor topology systematically avoids the A-only
signs (they are dark because nothing external ever touches them, not because solvers are weak).

## 6. Sensitivity + agreement

- **Inventories:** conservative/split/merged → 38/38/37 pinned signs; A-only-with-parseable-pin =
  [] in all three. Merged introduces 1 pin conflict (RA←{(r,a), (r,a)₂} from the RA/RA2 merge).
  Split adds 3 A-only variables (72), all dark. Results are grain-invariant.
- **Solver agreement:** constrained-sign sets Jaccard M1–M2 = 0.905, M1–M3 = 1.0, M2–M3 = 0.905
  (the gap is exactly the 4 conditional unpinned-neighbor domain reductions QE/*324/PA3/WI that
  only the hard-CP view counts). **A-only sign constrained by any solver: {*324} — relative-only,
  conditional, 0 absolute bits.** P4 (Jaccard ≥ 0.9) SUPPORTED.

## 7. Information budget (Art. IX)

Needed for a value map: ~151 unresolved signs × 6.066 ≈ **916 bits**. Available: held-out-
calibrated conditional anchor information 38 × 0.131 ≈ **5.0 bits** (conditional, single circular
lineage); rel channel 56 joint / **0 absolute** bits; bridge ≈ 0.09 bits total; stroke 0 (blocked);
Egyptian 0 (empty). Parameters ≫ information at every scenario below S1; and S1 is not a scenario
the constitution licenses — it is the assumption under audit.

## 8. Predictions scorecard (from the SPEC)

P1 SUPPORTED (S0 max 0.0002 bits = MC noise, 0 signs > 0.1). P2 SUPPORTED (only the 38 pins move;
0/69 A-only in all scenarios). P3 SUPPORTED (real strictly below all 200 nulls). P4 SUPPORTED
(Jaccard ≥ 0.9). P5 SUPPORTED with one nuance recorded verbatim: under dedup accounting the
contest is an exact wash (credit = cost) and the 1-bit validity flag alone favors UNANCHORED;
the decisive reversal (+231.5 bits) comes from Art.-XII discounting.

## 9. Compliance line

Art. V: all statements worded at L0–L2 (structure/consistency); no value claim asserted. Art. VII:
search space = 4 scenarios × 3 solvers × 3 inventories, fully enumerated here, nothing withheld.
Art. VIII/XI: clone collapse applied throughout; the naive variants are shown only as quantified
violations. Art. XII: pins are never graded by the continuity rule (the graded-LB labels grade
benchmarks only). Art. XV: relative reductions reported as joint/relative bits, never absolute.
Art. XVII: appended; nothing deleted. **COMPLIANT.** Tasks I/J should treat
`JOINT_INFERENCE_NULL` as their input state: J's entropy-reduction precondition is NOT met.
