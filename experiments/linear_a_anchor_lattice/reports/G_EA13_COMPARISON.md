# WP-G — Explicit Comparison with EA-13's La ≥ 4 Design-Power Finding

**Branch** `research/linear-a-anchor-lattice` · **v2.2** · **Seed** 20260708 · **Date** 2026-07-08
**Articles:** VIII, XI, XII, XV, XXII. **Truth-layer:** ≤ 0.75 (design/power).
**Companion:** `G_ANCHOR_THRESHOLD_SURFACE.md`, `D_EA13_POWER_REASSESSMENT.md`.
**Data:** `data/controls/anchor_threshold/surface.json` → `ea13_comparison_points`.

## What is being compared

- **EA-13** (frozen power envelope, Egyptian toponym channel) measured the **per-anchor identification**
  problem: at skeleton length La the probability a *single* anchor identification is a chance match
  (FP_frozen): La=3 → 0.24–0.26; **La=4 → 0.043**; La=5 → 0.07–0.08. Its verdict: `POWERED_DESIGN`
  conditional on **La ≥ 4** with n_anchors = 4.
- **WP-G** measures the **downstream lattice** problem: given n anchors of La slots each, what fraction of
  a known script's absolute values actually comes back, at what false-positive cost. Bridge: EA-13's
  FP_frozen is injected as WP-G's per-anchor `f_wrong` at the matching La (slots), on the opaque-LB bench
  (coverage 0.55, lineage-distinct anchors, real-word anchor sampling).

## Results

| config | f_wrong (=EA-13 FP_frozen) | abs recovery | held-out word | lattice FP | eq-red (log₁₀) |
|---|---|---|---|---|---|
| **EA-13 best: n=4, La=4** | 0.043 | **0.452** | 0.293 | **0.159** | 13.5 |
| EA-13 underpowered: n=4, La=3 | 0.25 | 0.207 | 0.097 | **0.544** | 12.5 |
| n=3, La=4 | 0.043 | 0.390 | 0.194 | 0.145 | 12.4 |
| n=4, La=5 | 0.075 | 0.436 | 0.329 | 0.258 | 14.7 |
| ideal twin: n=4, slots=4, f=0 | 0.0 | 0.547 | 0.354 | 0.000 | 14.1 |
| ideal twin: n=4, slots=3, f=0 | 0.0 | 0.455 | 0.232 | 0.000 | 12.5 |

## Three findings

1. **EA-13's La ≥ 4 threshold REPRODUCES from the lattice side, sharpened.** Dropping La 4 → 3 at n=4
   collapses absolute recovery 0.452 → 0.207 and explodes lattice FP 0.159 → **0.544** — below La 4 the
   anchor set is *net-poisonous* (more than half of everything "recovered" is wrong). The ideal twins show
   the split: of the La-3 penalty, the pure slot-coverage part is modest (f=0: 0.547 → 0.455); the
   identification-error part is catastrophic. **The quality bar is confirmed: La ≥ 4 or don't bother.**

2. **EA-13's per-anchor FP understates the downstream cost ≈ 3.7×.** Per-anchor FP_frozen 0.043 becomes
   lattice FP 0.159 at its own best config, because one wrong anchor poisons every sign in the components
   it touches (P(≥1 wrong of 4) ≈ 0.16, and each wrong one propagates). A channel "powered" at the anchor
   level (FP ≤ 0.05) is therefore **not** powered at the script level under the same threshold — EA-13's
   0.043 was necessary, never sufficient.

3. **Even EA-13's best config, granted for free, recovers less than half the script.** n=4 × La=4 with its
   measured error rate yields abs 0.452 / held-out word 0.293 — far from the (n=12, slots=8,
   lineage-distinct) frontier WP-G locates for abs ≥ 0.90 (and even the error-free ideal n=4 twin reaches
   only 0.547). EA-13's La ≥ 4 regime is thus a **foothold criterion** (it clears WP-G's abs ≥ 0.5-ish
   band only in the error-free ideal), not a decipherment criterion. Design-powered anchor *identification*
   and script *recovery* are separated by roughly a factor of 3 in required independent anchors.

## Where Linear A stands relative to both bars

WP-D measured the EA-13 eligibility set: **0 of the required ≥3** Cretan toponyms are simultaneously
Egyptian-rendered and LA-attested at ≥4 slots ({overlap} = Phaistos only, 3 slots / 1 site) — the La ≥ 4
regime is `UNREACHABLE_WITH_PRESENT_ANCHORS`. WP-G now adds the counterfactual: **even if** the EA-13
regime were populated exactly as designed (4 correct-ish La-4 anchors), Linear A would move from its zero
point (abs 0.000, eq-red 0.0, ambiguity 10^63) to roughly abs ≈ 0.45 *on an LB-density lattice* — and LA's
actual relative-channel density is the degraded bench (coverage ≈ 0.20), where the same anchor budget
yields only ≈ 0.18–0.21. The two results compose, they do not compete: EA-13 says the only channel with a
powered design cannot be populated; WP-G says that even populated, it would be a foothold, not a reading.

## Verdict (mechanical)

- `EA13_THRESHOLD_CONFIRMED_AND_SHARPENED`: La ≥ 4 reproduced as a cliff (lattice FP 0.54 below it);
  per-anchor FP → script FP amplification ≈ 3.7×; EA-13 best config = foothold-level (abs 0.45), not
  recovery-level (needs ~12 independent ≥8-slot lineage-distinct anchors).
- LA position: fails the EA-13 quantity/quality bar (0/3 eligible, WP-D) **and** sits at WP-G's
  identifiability zero. No licence movement; SEED_A = 0 unchanged.

**Compliance line:** comparison COMPLETE · EA-13 FP_frozen values taken from `FROZEN_POWER_PASS` re-read
(WP-D), injected mechanically as f_wrong · opaque-LB bench, known values grade only (Art. XII) · seed
20260708, byte-reproducible · truth-layer ≤ 0.75.
