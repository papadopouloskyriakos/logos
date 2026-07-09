# EPOCH-103 preregistration ADDENDUM R — corrected joint maxT null (E103R)

**Type:** APPEND-ONLY addendum (Art. XVII). The original `prereg.md`
(sha256 `1f8c82a3bdfa74b47d490d3b99c1fb8228c4514316bb52281096bcc04dae9747`) and the original
`result.json` are FROZEN and are not edited. This addendum is hashed and committed BEFORE the
rerun executes (freeze-before-run). The rerun is recorded as **E103R** with outputs written
alongside (never overwriting) the originals.

## Trigger — audit-confirmed defect in the original joint null

`universe_maxT()` in the frozen `machinery.py` draws ONE shared uniform matrix `U` of shape
(n_draws, n_words) and counts each candidate sign by `U < p_sign(word)`. For a single
(draw, word), every sign whose marginal first-position probability exceeds that word's single
uniform fires SIMULTANEOUSLY — comonotone dependence across signs. The true within-word
permutation null is categorical: exactly ONE sign occupies first position per word per draw
(probability = count/len), and the sign indicators are mutually exclusive (negatively
dependent). Consequences:

- Per-sign MARGINALS are exact under both constructions → `perm_null_fast` and every
  single-permute p-value in the original run are UNTOUCHED by this defect.
- The JOINT null's max-z distribution is suppressed under comonotone dependence → the
  family-wise maxT p-values in the original run are ANTI-CONSERVATIVE → the original p≤.01
  survivor set is inflated. The corrected categorical null yields a stochastically LARGER
  null max-z, hence more conservative maxT p-values.

## Committed fix (frozen before execution)

Per (draw, word): sample ONE categorical first sign. For each unit, precompute the cumulative
probability vector over its distinct signs (count/len, in fixed sorted sign order); draw a
single uniform per (draw, word); assign the realized first sign by interval (searchsorted).
All candidate-sign counts for that draw derive from the SAME categorical realization, then
max-z over candidate signs per draw as before. Implemented in `machinery_R.py` (this epoch
dir), which REUSES the frozen `machinery.py` functions `load_schemes`, `initial_count`,
`perm_null_fast`, and `positive_control` unchanged, so scheme construction, marginal nulls,
and the positive control are bit-identical in design to the original.

## Committed rerun parameters

- Same three segmentation/selection variants (`A_editor`, `B_divider_strict`,
  `C_numeral_anchored`), constructed by the frozen `load_schemes()`.
- Same candidate-universe rule: signs with ≥5 initial occurrences in the given variant.
- **M = 10,000** draws for the corrected joint maxT null (resolution floor 1/10001 ≈ 0.0001,
  clear air under the .01 threshold). `perm_null_fast` (marginal, semantics unchanged) also
  run at M = 10,000.
- Seeds identical to the original run where meaningful: permutation/maxT seed = 42; positive
  control seed = 7 (plant rate 0.15, n_draws = 2000, unchanged).
- Reported per variant: corrected null max-z distribution summary (per-draw max mean, p95,
  and the M-draw extreme), A's corrected maxT p and rank, the FULL corrected p≤.01 survivor
  set, and a survivor-set diff vs the original run.
- Descriptive scheme-overlap block (for the closure-doc disclosure): exact unit-level overlap
  between A_editor and B_divider_strict, and the subset relation of C_numeral_anchored to
  A_editor.

## Verdict rule — UNCHANGED (restated verbatim from the frozen prereg)

REPLICATED_RELATIVE_CONSTRAINT iff PC power+cal clean AND A- is top survivor at maxT p<=.01
under >=2/3 schemes. CONDITIONAL_SIGNAL_ONLY iff exactly 1/3. GENERIC_UNDER_NULL iff 0/3.
NO_POWER iff PC fails.

## LOMO mechanization (audit item A3; committed extraction rule)

The original run HARDCODED `"each_independently_significant": true`. E103R evaluates the LOMO
condition mechanically from the FROZEN artifacts, with no recomputation from corpus data:

1. Load `epochs/EPOCH-022/result.json`, `epochs/EPOCH-023/result.json`,
   `epochs/EPOCH-024/result.json` from the branch; record each file's sha256 in
   `result_R.json`.
2. Extract recorded statistics only:
   - E022: `step3_family_deflation.p_maxT`, `step4_positive_control.pc_pass`, `verdict`.
   - E023: `numbers.global.p_one_sided_1000draws`,
     `numbers.la_per_site_A.sites_significant_holm_adj_le_0.05`,
     `numbers.la_leave_one_site_out.survives`, `numbers.positive_control.pc_verdict`,
     `verdict`.
   - E024: `numbers.global.p`, `numbers.verdict_inputs.pc_passed`,
     `numbers.verdict_inputs.loo_ok`, `numbers.verdict_inputs.comp_ok`, `verdict`.
3. A method counts as INDEPENDENTLY SIGNIFICANT iff its recorded PC passed AND its recorded
   headline significance is p ≤ 0.01 (E022: p_maxT; E023: global one-sided p; E024: global p)
   AND its recorded verdict is its positive class (A_PREFIX_SURVIVES_ADAPTIVE_NULL /
   A_PREFIX_CROSS_SITE_ROBUST / A_PREFIX_MULTIAXIS_ROBUST respectively).
4. LOMO condition: dropping any ONE method leaves ≥2 independently significant confirmations.
   Evaluated mechanically; the contributing numbers are written into the LOMO block.
5. STOP rule: if any recorded statistic contradicts the LOMO condition, halt and report
   before writing anything downstream.

## Outputs (append-only)

- `result_R.json` in this epoch dir, containing: per-variant corrected results, PC, mechanized
  LOMO, mechanical verdict under the unchanged rule, survivor-set diff, corrected
  qualification-of-E022 note (secondary survivor set stated EXACTLY as measured), plan_hash =
  sha256 of THIS addendum, code_manifest = sha256 of `machinery_R.py`, and sha256 of the
  frozen original `result.json` for chain of custody.
- `plan_hash_R.txt` = sha256 of this addendum.

## STOP rule (campaign-level)

If the corrected rerun changes the verdict class from REPLICATED_RELATIVE_CONSTRAINT, STOP:
report before any downstream wording, closure regeneration, or packaging proceeds.

## Forbidden (unchanged)

No phonetic value, sound, translation, or language-family inference; additionally no
assertion of morphological prefixhood or productivity. The finding, under either verdict, is
a RELATIVE A-initial positional-enrichment constraint (L2/L3) at most.
