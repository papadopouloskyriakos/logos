# EPOCH-104 preregistration ADDENDUM R — campaign-wide null under a bound-based criterion (E104R)

**Type:** APPEND-ONLY addendum (Art. XVII). The original `prereg.md`
(sha256 `a06fe20ab706fc5be9653a4003fa3de11a8be1959d1454e67678bb303be4f474`) and the original
`result.json` are FROZEN and untouched. This addendum is hashed and committed BEFORE the rerun
executes (freeze-before-run). Outputs are written alongside the originals as **E104R**.

## Trigger

1. The E103 joint maxT null was corrected (comonotone → categorical; see
   `epochs/EPOCH-103/prereg_addendum_R.md`, E103R). E104 exercises the E103 graduation rule
   end-to-end, so it must be rerun with the CORRECTED maxT.
2. The original E104 established the observed rate 1/200 as a valid empirical calibration of
   the rule-as-implemented (its null corpora used genuine `rng.shuffle`, i.e. correct
   categorical realizations), but it does NOT establish "true false-graduation rate ≤ 2% at
   95% confidence": the one-sided exact Clopper–Pearson 95% upper bound was 2.35%. E104R
   replaces the point-estimate criterion with a bound-based criterion, committed blind —
   before any corrected-machinery null has been run.

## Committed design (frozen before execution)

- **n_null = 400** structure-matched signal-free null corpora (real editor words,
  within-word sign order shuffled; preserves per-word multiset + length + per-inscription
  content; destroys positional signal), each rebuilt into the 3 segmentation/selection
  variants. Construction semantically identical to the frozen E104 `null_corpus_words`
  (the corpus is parsed once and per-null shuffles are applied to fresh copies, preserving
  the original iteration order so a given seed yields the identical null corpus).
- **Graduation rule under test = E103's preregistered rule with the CORRECTED categorical
  maxT** (E103R `universe_maxT_categorical`): a run "graduates" iff the same top sign is a
  passing top-survivor (maxT p ≤ .01) under ≥2 of the 3 variants.
- **maxT draws M = 5,000.** Alignment stated explicitly: E103's ORIGINAL prereg committed
  M = 5,000 for the maxT null; the original E104 implementation used n_draws = 2,000 inside
  `graduates()` (an implementation economy). E104R aligns to M = 5,000, matching E103's
  original commitment.
- **Ablation arm on the SAME 400 nulls:** naive best-of raw-p — the extreme (top-|z|) initial
  sign "passes" a variant iff its RAW single-permute p ≤ .01 (no family deflation), same
  ≥2-variant same-top-sign graduation logic. Report the suppression factor
  (naive count / corrected-maxT count).
- **Planted-positive power: n_plant = 40.** Plant sign 'PX' as initial in 12% of units in
  every variant of a fresh null; recovery = graduation with top sign PX under the corrected
  rule.
- **Seeds fixed and recorded:** null corpora `default_rng(1000+i)`, i = 0..399 (the first 200
  coincide with the original run's null seeds by construction); `graduates` maxT seed = i;
  planted corpora `default_rng(5000+i)`, i = 0..39.

## Committed verdict rule (bound-based; replaces the point-estimate criterion; committed blind)

**CAMPAIGN_NULL_GATES_CERTIFIED** iff the one-sided exact Clopper–Pearson 95% UPPER BOUND on
the false-graduation rate (corrected-maxT arm, k of 400) is ≤ 0.02 AND planted recovery
≥ 0.8; else **CAMPAIGN_NULL_PILOT_ONLY**. (At n = 400 this tolerates k ≤ 3; k = 4 gives an
upper bound ≈ 0.0229 and fails.) The ORIGINAL E104 run is henceforth characterized as a
PILOT (valid empirical calibration of the rule-as-implemented; certification language
attaches only to E104R's bound-based verdict, if earned).

## Committed narrative scope notes (to be carried into the E104 narrative wherever it appears)

1. The 12% planted prefix establishes power only for effects of that general magnitude.
2. "End-to-end" means the graduation DECISION RULE end-to-end — the positive control and
   LOMO are not re-executed per null.
3. The absolute-value-gate zero is structural (by construction: a positional-shuffle null has
   a single axis and cannot satisfy the ≥2-independent-channels requirement), and is labeled
   as such.

## Outputs (append-only)

`result_R.json` in this epoch dir: counts and rates for both arms, exact one-sided
Clopper–Pearson 95% upper bounds for BOTH arms, suppression factor, planted recovery, verdict
under the committed bound rule, the three scope notes, plan_hash = sha256 of THIS addendum,
code_manifest = sha256 of `machinery_R.py` (this dir) + the E103R machinery it imports.
`plan_hash_R.txt` = sha256 of this addendum.
