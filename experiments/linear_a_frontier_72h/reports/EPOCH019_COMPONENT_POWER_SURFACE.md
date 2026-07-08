# EPOCH-019 — Component-channel value-recovery identifiability surface (§12 third power surface, gate A)

**Verdict (mechanical, fail-closed): `HARNESS_NOT_VALIDATED`.** The frozen positive control did
NOT pass — the recovery method (both the prereg's frozen nearest-centroid design AND a declared
posthoc seeded-KMeans alternative) fails to show anchor budget or channel quality reliably
*improve* value-class recovery over blind unsupervised clustering, even at oracle channel
quality. Per the prereg's own fail-closed rule, this correctly blocks any claim about LA's
operating point — LA's real numbers ARE located on the surface below (as pre-committed), but the
surface itself does not clear its own validation bar, so the point reading is reported
descriptively, not certified.

Frontier §12 (third power surface) · gate A · plan_hash
`af5d970eb54872fd1b10da8beded3256c952358b58d3a69abc728f21bcd91cb2` (prereg frozen 2026-07-08,
before any cell realized) · seed 20260708 · claim layer **L1** (identifiability geometry only;
no phonetic value, no transfer licence touched). Articles: V, VII, VIII, IX, XI, XII, XV, XVII,
XVIII, XXII.

## Question

E003 priced the whole-sign anchor-profile surface. E018 confirmed the component-decomposition
cross-script channel carries real form-matching structure (agg MRR 0.2470, survives an adaptive
null). Neither answers: treating the component channel as a feature space, how much (anchor
budget × channel quality) buys recovery of the *latent grid structure* — which signs share a
consonant row, which share a vowel column? This epoch built a synthetic, truth-known 18-row ×
5-column grid (K=90 signs), swept anchor budget b ∈ {0,2,4,8,12} × channel quality q ∈ {0.15,
**0.24701551940826028 (LA's real E013/E018 measured component-channel MRR)**, 0.30,
**0.39934712069259104 (LB's real E009 measured within-script MRR)**, 0.55, 0.75, 1.0 (oracle)},
measured value-class recovery via Adjusted Rand Index (ARI) of the recovered row/column
partition, R=30 replicates/cell, one frozen recovery method, one frozen positive control, one
frozen adversarial (shuffled-identity) null.

## Design as executed

- Grid: dense 18×5 = 90 signs, code = concat(one-hot(row,18), one-hot(col,5)), 23-dim.
- Channel: query-side embedding = code + N(0, σ(q)²·I); σ calibrated by bisection to hit each
  target retrieval-MRR (the identical statistic E009/E013/E018 use) within 0.004, verified:

| q label | target MRR | σ | achieved MRR |
|---|---|---|---|
| sub_LA_ref | 0.150 | 0.548 | 0.154 |
| **LA_measured** | **0.2470** | 0.416 | 0.246 |
| mid1 | 0.300 | 0.375 | 0.303 |
| **LB_within_script** | **0.3993** | 0.334 | 0.402 |
| mid2 | 0.550 | 0.281 | 0.547 |
| high | 0.750 | 0.229 | 0.751 |
| oracle | 1.000 | 0.000 | 1.000 |

- Recovery (frozen, primary): `b=0` → unsupervised `KMeans(k=18)`/`KMeans(k=5)` on the full
  embedding; `b>0` → nearest-centroid classifier seeded by `b` random anchors' true labels,
  scored held-out only. `ARI_combined = mean(ARI_row, ARI_col)`.
- Positive control (4 sub-checks, ALL required): PC-monotonic-b (Spearman ρ(b, ARI) at
  q=LB_within_script ≥0.8), PC-monotonic-q (ρ(q, ARI) at b=12 ≥0.8), PC-oracle-ceiling
  (ARI≥0.9 at q=oracle,b=12), PC-LB-point (ARI≥0.5 at q=LB_within_script,b=12 — "reproduces
  the LB operating point within tolerance," operationalized as clearing foothold).
- Adversarial: identical grid with grading truth independently permuted per replicate
  (embeddings unchanged) — tests whether the pipeline reports spurious recovery from generic
  cluster structure alone. Rule: max ARI_combined across all 35 cells < 0.05.

## Positive control: FAILED (primary method)

| sub-check | result | pass |
|---|---|---|
| PC-monotonic-b (ρ at q=LB) | **0.00** | **FAIL** |
| PC-monotonic-q (ρ at b=12) | 1.00 | PASS |
| PC-oracle-ceiling (q=oracle,b=12) | 0.4514 (need ≥0.9) | **FAIL** |
| PC-LB-point (q=LB,b=12) | 0.1145 (need ≥0.5) | **FAIL** |

**PC_PASS = False.** The smoking gun: mean ARI_combined is *highest at b=0* (blind, no anchors)
at **every single tested q**, and collapses at b=2 before partially recovering by b=12 — it
never catches back up to the b=0 level, even at oracle quality with 12 anchors (0.4514 vs
b=0's 0.4731). Adding anchors made recovery *worse*, not better, across the entire tested
budget range. Adversarial control (shuffled-identity null) PASSED cleanly: max ARI_combined
over all 35 cells = **0.0057** (≪ 0.05 bar) — the harness does not fabricate spurious recovery
from decoupled structure; it fails in the other direction (real signal, not enough of it
captured by the frozen anchor-based method).

## Declared posthoc diagnostic (Art. XVII, verdict-neutral — logged in DEVIATIONS.md)

Before accepting "anchors don't help" as a geometry fact, one alternative, still non-circular
recovery method was tried: **seeded KMeans** (anchor-label centroids seed as many of `k`'s
initial cluster centers as there are distinct anchor labels; remaining centers via
k-means++; standard Lloyd iterations to convergence over all points). This uses only anchor
LABELS as an initialization hint — never a privileged row/col feature-block split.

| sub-check | seeded-KMeans result | pass |
|---|---|---|
| PC-monotonic-b (ρ at q=LB) | **−0.30** | **FAIL** |
| PC-monotonic-q (ρ at b=12) | 1.00 | PASS |
| PC-oracle-ceiling | 0.4664 (need ≥0.9) | **FAIL** |
| PC-LB-point | 0.2378 (need ≥0.5) | **FAIL** |

**Also fails**, and the qualitative pattern is identical: mean ARI_combined highest at b=0
at every q; anchors help less than blind clustering throughout. **Two structurally different
recovery methods converge on the same failure** — this is not one bad implementation choice.
This posthoc pass does not change the frozen verdict (`HARNESS_NOT_VALIDATED` stands); it
sharpens the diagnosis below.

## Diagnosis: where the failure actually lives (per-axis breakdown)

Splitting `ARI_combined` into `ARI_row` and `ARI_col` localizes the problem entirely to the
**row axis** (18 classes):

- `ARI_row` sits at or below the adversarial floor (≈0.00–0.04, occasionally negative) at
  **every** (b,q) cell in **both** recovery methods, **including q=oracle** — i.e., row
  structure is never meaningfully recovered regardless of channel quality or anchor budget.
- `ARI_col` (5 classes) reaches **1.0000** at (q=oracle, b=0, unsupervised) and generally rises
  with q, but is *also* non-monotonic in b (drops when anchors are added, partially recovers).

**Why**: the benchmark's representation (row-block and col-block one-hot, concatenated,
i.i.d. equal-magnitude Gaussian noise on both) makes "two signs differ only in row" and "two
signs differ only in column" produce the *exact same* pairwise Euclidean distance (squared
distance 2 in both cases; 4 if they differ in both). Nothing in a Euclidean-distance-based
method (KMeans, nearest-centroid, seeded KMeans) can distinguish "this pair's closeness reflects
shared row" from "this pair's closeness reflects shared column" without already knowing which
23 coordinates are row-relevant versus column-relevant — exactly the information this surface
is trying to recover, so using it as an input would be circular. The K=5 (column) partition
search apparently converges more reliably in practice than the K=18 (row) partition search —
consistent with clustering into fewer, larger groups being a far less local-optima-prone
optimization landscape than clustering into many small groups — but this is an *empirical*
regularity of Lloyd's algorithm on this geometry, not a designed property. **This is a flaw in
the benchmark's representation choice** (equal-noise concatenated one-hot code), not evidence
about real component channels one way or the other.

## LA's operating point (descriptive only — NOT certified, PC failed)

Cited coordinates (both already-closed, non-circular external facts — neither is a re-derivation
here): `b=0` anchors (anchor-lattice campaign WP-C: dependency-collapsed independent
distinct-lineage anchor count for Linear A = 0 today, `research/linear-a-anchor-lattice` HEAD
`28bbd59`); `q=0.24701551940826028` (E013/E018's real, adaptive-null-surviving component-channel
agg MRR).

| | primary (nearest-centroid) | posthoc (seeded-KMeans) |
|---|---|---|
| ARI_row | 0.0362 | 0.0270 |
| ARI_col | 0.2256 | 0.2827 |
| **ARI_combined** | **0.1309** [95% CI 0.118, 0.144] | **0.1548** [95% CI 0.139, 0.170] |
| gap to foothold (0.5) | 0.369 | 0.345 |
| gap to absolute (0.9) | 0.769 | 0.745 |

Both methods land LA's point well below foothold (0.5) — but this reading carries the same
disclaimer as the whole surface: since PC failed, we do not know whether "0.13" reflects a
genuine information-poverty fact about LA's real channel+anchor combination, or is deflated by
the same row-axis representation flaw diagnosed above (which suppresses ARI at EVERY cell of
the grid, including the oracle ceiling). The one thing this epoch *can* certify: **b=0 is not
uniquely bad** — LA's `b=0` reading is *not* an outlier on this surface; b=0 is the best-scoring
budget at almost every quality level tested, for both methods. So the qualitative fact that "LA
has zero anchors" does not, by itself, additionally penalize LA's point relative to a
counterfactual world with a few more anchors, GIVEN this (flawed) surface design — a
genuinely surprising and non-obvious observation, but one that must be read as a property of
the harness, not (yet) a property of the real decipherment problem.

## Contour (reported for completeness, over the 35 measured cells only — not extrapolated)

Foothold (ARI_combined ≥ 0.5) is reached at 4 of 7 tested q-levels, always at `b=0` first (never
at b>0 within the tested budgets, both methods): mid2 (q=0.55) at b=0; high (q=0.75) at b=0;
oracle (q=1.0) at b=0 and (primary only) again at b=8/12. No tested q reaches absolute
(ARI≥0.9) at any budget. This contour is a symptom of the same row-axis flaw, not a usable
acquisition target.

## Honest interpretation

This epoch **does not price a valid identifiability surface** — it correctly, mechanically
fails its own preregistered positive control, and a declared posthoc alternative method fails
the identical way, converging on a specific, diagnosable design flaw (row/column geometric
indistinguishability under equal-noise concatenated one-hot encoding + Euclidean recovery).
The fail-closed discipline worked exactly as designed: it caught a broken harness before any
claim about LA's real anchor-count/channel-quality combination could be asserted. **This is a
genuine negative result** (Art. XVII: append-only, this is not deleted or reframed as a
success) — it closes this particular operationalization of the "component-channel →
value-class recovery" question and hands a sharply-diagnosed successor design to the next
epoch. The adversarial control's clean PASS (0.0057 ≪ 0.05) shows the failure is specifically
in recoverability, not in the harness fabricating false positives — an important asymmetry:
this surface, as built, is conservative (never over-claims) but under-powered on the row axis
by construction.

## What this closes and what it opens

Closes: this specific concatenated-one-hot/Euclidean-recovery operationalization of the
component-channel value-class surface — do not reuse it unmodified as a validated instrument.

Opens (ranked successors):
1. **Asymmetric-scaling redesign**: give the row-block and column-block *different* per-
   dimension noise/scale (motivated by the real prior that vowel structure is typically far
   easier to establish in undeciphered syllabaries than consonant identity — Linear B's own
   decipherment history), and re-run the identical PC/adversarial gates before trusting any LA
   point on the resulting surface.
2. **Non-Euclidean / block-aware recovery family**: test whether a recovery method that first
   *learns* (from anchors alone, no privileged knowledge) a linear projection separating the
   two blocks (e.g., anchor-supervised metric learning / partial least squares on the anchor
   set) clears the PC gate where raw-Euclidean clustering does not — directly tests whether the
   row-axis failure is fixable with more information-efficient (still non-circular) recovery,
   or is a harder ceiling.
3. **Split the surface**: since column recovery (5 classes) DOES reach ARI=1.0 at oracle+b=0,
   price the row axis (18 classes) and column axis (5 classes) as two independent surfaces
   with independent PC gates, rather than forcing one combined statistic — the combined metric
   masked a working sub-channel (column) behind a broken one (row).
4. **Vary K/(n_c,n_v) shape**: sweep grid aspect ratio (e.g., 9×10 instead of 18×5) to test
   whether the row-axis failure is a function of cluster COUNT (Lloyd's-algorithm local-optima
   density) rather than "role" (row vs column per se) — if a 9-class axis also fails at k=9 but
   a 5-class axis succeeds at k=5, that isolates cluster-count as the driver, independent of
   any row/column semantics, and would generalize the fix.
5. **Anchor-integrity interaction**: this campaign's E003 already showed wrong anchors are
   net-poisonous on a different channel; re-run this surface's (once fixed) PC with 1-2 wrong
   anchors injected, since Linear A's real candidate anchor pool (were it ever to grow above
   zero) is exactly the kind of noisy, contested source this surface should stress-test.
6. **Real (not oracle) LB positive-control leg**: EPOCH-018's actual LB gallery/query
   embeddings (not synthetic-calibrated) could replace the synthetic oracle/near-oracle points
   as a genuine known-truth positive control, closer to the real pipeline than a
   Gaussian-noise stand-in.

## Compliance (Art. XXII)

Prereg frozen and sha256-hashed (`af5d970eb54872fd1b10da8beded3256c952358b58d3a69abc728f21bcd91cb2`)
before any cell was realized; positive control computed before any interpretation of the main
sweep; adversarial control run in the same pass; verdict is the mechanical output of the
prereg's own frozen fail-closed rule (PC_PASS=False → `HARNESS_NOT_VALIDATED`), not a narrative
judgment. One declared posthoc diagnostic pass (seeded-KMeans) logged append-only in
`DEVIATIONS.md`, explicitly verdict-neutral. No known Linear A or Linear B sign value is used as
a model input anywhere in this epoch — the two real-world numbers entering (E013/E018's MRR,
the anchor-lattice's anchor count) are structural/calibration scalars from already-closed,
independently-verdicted epochs, cited not re-derived.

Artifacts: `data/component_power_surface/{E019_surface.json, E019_posthoc_seeded.json}` ·
`scripts/{epoch019_component_power_surface.py, epoch019_posthoc_seeded.py}` ·
`epochs/EPOCH-019/{prereg.md, plan_hash.txt, DEVIATIONS.md, result.json}`.
