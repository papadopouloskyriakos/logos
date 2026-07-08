# EPOCH-018 — Dedicated adaptive-null family for the E013 decomposition cross-script channel (Constitution §12, gate A)

**Frozen:** 2026-07-08, BEFORE any null realization is drawn or any adaptive-p is computed.
**Seed:** 20260708 (SEED). All realization seeds derive deterministically from SEED.
**Claim layer:** L1 (sign-form geometry / channel calibration) only. NO phonetic value, NO L2+
claim, NO transfer licence touched (Art. XV: none earned, none claimed). This epoch assigns
zero LA readings; it stress-tests a channel statistic that EPOCH-013 already reported.
**Articles triggered:** VII (search receipt — the channel's full architecture-search history is
enumerated below, not just E013's own frozen hyper-rules), VIII (effective n — the adaptive null
IS the effective-n correction: it replaces an iid-uniform-rank null with one that burns the real
nuisance degrees of freedom), IX (info budget — an adaptive p and null-mean/95th-pctile are
reported next to the observed MRR on every output), XI/XII (non-circularity — AB-value identity
and the LB font gallery are Unicode/font-standard ground truth, independent of the extraction
pipeline; component vectors are anonymous 13-dim shape features, no phonetic content anywhere;
grading uses the SAME matcher E013 committed to, never a rule invented after seeing which null
looks better), XVII (append-only — this is a stress test of EPOCH-013's own published verdict;
if the channel collapses, EPOCH-013's result.json is NOT edited — this epoch's own verdict
supersedes it declaratively and EPOCH-013 gets a cross-reference note, never a silent rewrite),
XVIII (assumption register — the trace-standardization caveat carried in EPOCH-013 applies
identically here; adaptive-null draws do not remove it), XXII (this header + compliance line).

## Question

EPOCH-013's frozen LEG-1 statistic (`e009_ok_only` pool, 57 shared AB values, 74-item LB font
gallery, `agg_mrr = 0.24701551940826028`, `p_agg = 4.9998e-05` against an **iid-uniform-rank**
null) is a +44.5% lift over E009's whole-sign baseline (0.1710). That p-value only rules out
"ranks are uniform noise" — it does NOT rule out "the lift is a generic artifact of shared
component-shape frequency (most components in both corpora are short strokes / dots / simple
junctions) rather than a genuine per-value LA↔LB shape correspondence." §12 of the campaign
requires 3 dedicated adaptive-null families (≥200 realizations each) that actually burn that
degree of freedom. This epoch supplies one, targeted at the newest apparent positive.

## Search receipt (Art. VII) — what this campaign actually tried on this channel

Grep of every epoch's `result.json` for the LB-font-gallery LEG1 signature (`"gallery_n": 74`)
finds exactly **3** architecture attempts that computed a comparable LA→LB cross-script MRR
statistic, in this order: **E008** (single-component stroke-graph pilot, addendum-1 held-out
MRR 0.273, n=4 queries — too small/noisy to itself confirm, but it is a real prior attempt at
this exact channel and it set the expectation that motivated E009); **E009** (whole-glyph
stroke-graph matcher, LEG1 agg MRR 0.1710, p=1.5e-4, n=57 — became the frozen baseline); **E013**
(bag-of-components/decomposition matcher, LEG1 agg MRR 0.2470, p=5.0e-5, n=57 — the positive
under test here, framed explicitly as "beats E009"). **K = 3.** No hyperparameter sweep occurred
*within* E013 (its K=12/SHARE_MIN=3%/KEEP_MIN=70%/13-dim-feature/λ-median-of-20000 rule was
frozen once, pre-run, per its own prereg) — the only real search DOF is architecture selection
across E008→E009→E013. Deflated significance = Bonferroni over K=3 applied to the epoch's
adaptive p (reported alongside the raw, per Art. VIII/IX; Holm shown too for reference).

## Step 1 — byte-for-byte reproduction (frozen, before any null)

Reload `data/stroke_corpus/component_matcher/components.json` (E013's published per-instance
raw component bags + labels + status, Art. XI: published artifact, not re-derived from images)
and rebuild the LB-font gallery via E013's *own* `decompose`/`comp_features` functions (imported,
not reimplemented) applied to the same 74 `corpus/bronze/sign_images/linB/*.png`. Recompute
pooled (mean, sd) over ALL usable (expanded) instances, λ via the identical seeded
(`random.Random(SEED)`, 20,000 draws) cross-instance-component procedure, and the `e009_ok_only`
LEG1 aggregate MRR over the same 57-value eligible frame (via `linA_codepoint_map.json` +
`sign_images/manifest.json` `shared_values_all`, identical to E013). Report the reproduced value
against the stored `0.24701551940826028` (tolerance: exact match expected — deterministic
pipeline, fixed seeds, published inputs only; any nonzero difference is logged as a deviation).

## Step 2 — adaptive null design (the primary, required ≥200-realization family)

**Null model ("PERMUTE"):** the channel's own matcher machinery (bag_dist / Hungarian
assignment / λ) is reused unchanged; the null hypothesis is "LEG-1's elevated MRR is
attributable to the generic frequency/degree structure of components — not to which specific
real component actually belongs to which glyph instance." Realize this concretely as a
**closed-pool permutation**: pool every kept z-scored component vector across ALL `status=="ok"`
usable instances (the full LEG-1 query universe, not just the 57-value eligible subset — this
maximizes fidelity to the true corpus-wide component-frequency profile, Art. VIII), record each
instance's component COUNT (`n_kept`, i.e. its degree), draw a uniform random permutation of the
pooled component vectors (`numpy.random.default_rng` seeded per realization), and re-chop the
permuted pool back into bags using the ORIGINAL per-instance degree sequence (same instance
order). This is an exact bijection of the same multiset onto the same slot sizes — it
**exactly** preserves (a) the component-frequency profile (every real vector used exactly once,
globally, as before — a permutation, not a resample), (b) the component-count-per-instance
distribution (slot sizes are literally unchanged), and (c) the cross-script pairing DOF (the LB
gallery, held fixed as external Unicode/font ground truth, still has to be matched against
*something* — only the LA-side identity-to-slot mapping is randomized, exactly the coupling the
"generic artifact" hypothesis needs). Gallery bags, λ, pooled (mean,sd), and instance→AB-value
grouping are held at their Step-1 observed values in every realization (only the LA component
CONTENT changes). ≥200 realizations (target: 300); recompute `agg_mrr` over the same 57-value
eligible frame each time using the SAME `leg1`-equivalent aggregation E013 used (mean per-value
distance to each gallery item, then rank of truth).

**Weaker comparison null ("BOOTSTRAP", not the confirmatory statistic):** identical procedure
except the pool is resampled **with replacement** (i.i.d.) rather than permuted — this breaks
the *exact* frequency-multiset guarantee (some real components used 0×, others many×) and is
included only as the "raw i.i.d. shuffle that ignores component frequency" comparison the brief
requires; it is expected to be *weaker* (i.e. its own agg-MRR distribution should look similar
to or even slightly more dispersed than PERMUTE's, and is NOT used for the channel verdict).
≥200 realizations (target: 250).

## Step 3 — search adjustment

Deflated p = Bonferroni over K=3 (architecture-search receipt above) applied to the PERMUTE
adaptive p: `p_deflated = min(1, 3 × p_adaptive)`. Holm-style value also reported for reference
(with K=3, Holm and Bonferroni coincide for a single test). alpha = 0.01 (the threshold E013 and
its siblings use throughout this campaign).

## Step 4 — positive control (run BEFORE the real-data null is interpreted)

Two synthetic 13-dim-feature corpora built from a small closed vocabulary of canonical
component "types" (discrete topology tuples + jittered continuous features), never touching any
real LA/LB image or the real λ/pooled stats:

- **PC-signal:** M=25 synthetic "signs", each assigned a fixed per-slot component prototype
  (1–3 slots); 6 jittered query instances/sign (Gaussian noise, fixed seed) + 1 jittered gallery
  instance/sign — a GENUINE planted per-sign correspondence between query and gallery component
  content. Compute observed agg_mrr (same `leg1_agg_mrr` code path used everywhere else in this
  epoch), then run the SAME PERMUTE null (≥200 realizations) on this synthetic pair. **Required
  to pass:** adaptive p < 0.01 (null correctly rejects H0 given a real signal) AND observed
  agg_mrr exceeds the null's 95th percentile.
- **PC-null (no signal):** identical vocabulary/M/slot-structure, but every query instance's
  components are drawn i.i.d. from the GLOBAL prototype pool independent of its nominal sign
  (no true correspondence to construct). Calibration check: leave-one-out on the PC-null's own
  ≥200 PERMUTE-null realizations (each realization in turn scored as "observed" against the
  other N−1) — false-positive rate at alpha=0.01 must be ≤0.03 (3× nominal, allowing for Monte
  Carlo slack at N≈200–300) and consistent with Binomial(N, 0.01) at the 95% level.
  PC-1 PASS := PC-signal passes AND PC-null FPR check passes. FAIL ⇒ verdict
  `NULL_MISCALIBRATED`, stop before interpreting the real-data null.

## Mechanical verdict (frozen)

Let `p*` = Bonferroni-deflated PERMUTE adaptive p on the REAL E013 statistic, `lift_null` =
observed_agg_mrr / null_mean(PERMUTE), `obs_vs_p95` = observed_agg_mrr − null_p95(PERMUTE).

- **NULL_MISCALIBRATED** := PC-1 FAIL. Stop; no channel verdict is drawn.
- **CHANNEL_COLLAPSES** := PC-1 PASS ∧ (`p* ≥ 0.01` ∨ `obs_vs_p95 ≤ 0`) — the real observed MRR
  is statistically indistinguishable from (or below) what generic frequency/degree-matched
  component shuffling already produces.
- **CHANNEL_ATTENUATED** := PC-1 PASS ∧ `p* < 0.01` ∧ `obs_vs_p95 > 0` ∧ `lift_null < 1.30` —
  survives but the *material* excess over the matched null is small (<30% relative lift over
  the null mean), i.e. most of the naively-reported +44%-vs-E009 lift is attributable to the
  nuisance structure the null now credits away.
- **CHANNEL_SURVIVES_ADAPTIVE_NULL** := PC-1 PASS ∧ `p* < 0.01` ∧ `obs_vs_p95 > 0` ∧
  `lift_null ≥ 1.30`.

Numbers (adaptive p raw + deflated, PERMUTE null mean/95th pctile, BOOTSTRAP null mean/95th
pctile for contrast, observed MRR, lift_null) are reported regardless of which bucket fires.

## Honest-accounting commitments

- This epoch does not touch `epochs/EPOCH-013/result.json`; if the verdict is
  `CHANNEL_COLLAPSES` or `CHANNEL_ATTENUATED`, EPOCH-013's own file is left as the historical
  record of what its *own* (weaker) null showed, and this epoch's result is the append-only
  correction (Art. XVII) — cross-referenced in both reports.
- No LA phonetic values, sign readings, or language claims appear anywhere in outputs; component
  identities remain anonymous 13-dim vectors throughout, including in the synthetic PC (Art.
  XI/XII non-circularity — synthetic prototypes are arbitrary integers, not real values).
- Trace-standardization caveat (Art. XVIII) is inherited unchanged from E013 and re-stated in
  the report; this epoch adds a stronger channel-level chance-model caveat (adaptive null still
  cannot detect confounds shared by BOTH the real LA extraction and the real LB font rendering
  process, e.g. shared despeckle/skeletonization artifacts — flagged as an open limitation, not
  fixed by this design).
- Compute: local CPU, `multiprocessing.Pool`, deterministic per-realization seeds
  (`SEED*10_000 + mode_offset + realization_index`); no GPU needed (bag_dist ≈ 11µs/call
  benchmarked in-session, ≈190k calls/realization ⇒ ≈2s/realization at full LEG-1 fidelity).
