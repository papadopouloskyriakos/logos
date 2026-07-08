# EPOCH-046 — WORD-LENGTH DISTRIBUTION SHAPE / GENERATIVE PROCESS

**Campaign:** Linear A frontier-72h · **Epoch:** 046 · **Layer:** L2/L3 (morphological typology)
**Operator:** logos z.ai research worker (GLM-5.2) · **Discipline:** STRICT LOGOS

## QUESTION (frozen)
Does the Linear A word-length distribution follow a **GEOMETRIC / exponential** shape
(memoryless concatenation — each additional sign added with roughly constant continuation
probability; consistent with agglutinative / concatenative morphology) — OR is it
**PEAKED / templatic** (a preferred word size with mode >= 2; consistent with fixed templates
/ root-and-pattern)? And is the shape **CONSISTENT across sites**?

Pure length-distribution structure (L2/L3): signs are ANONYMOUS. No phonetics, no sound, no
meaning, no reading.

## NON-CIRCULAR / DISCIPLINE (hard)
- NO phonetic / sound / meaning / reading inference. L2/L3 ONLY.
- LB used as POSITIVE-CONTROL benchmark only (control-only).
- Prereg + plan_hash FROZEN BEFORE running. PC FIRST. Mechanical verdict from a FROZEN rule.

## DATA (verified)
- `corpus/silver/inscriptions_structured.json` — word tokens `t=='word'` with `signs`.
- Word length = `len(signs)`; use ALL words with `len(signs) >= 1`.
- Corpus path: BASE/corpus then repo-root.
- LB PC via `load_b_damos()[0]` (returns flat list of wordforms, each a list of signs).

## METHOD (frozen)
Fit the observed length distribution (lengths 1..L) to:
- (a) **GEOMETRIC** model `P(L=k) ~ (1-p)^(k-1) p` (memoryless, monotone-decreasing from k=1).
      MLE: `p_hat = 1 / mean`. Goodness-of-fit: chi-square on binned counts (tail collapsed so
      expected >= 5), `geometric_gof_p`.
- (b) **PEAKED** model: shifted-Poisson with mode >= 2 (lambda chosen so that the fitted mode
      is >= 2; if the data mode is 1 the peaked model is by construction not preferred). Fit by
      MLE on the shifted support; BIC computed on the same binned counts.

Compare by BIC on identical binned counts. Decision rule:
- **GEOMETRIC** iff geometric GoF p > 0.05 AND observed histogram is monotone-decreasing from
  k=1 (mode == 1).
- **PEAKED** iff observed mode >= 2 (non-monotone peak) AND peaked BIC < geometric BIC.
- Otherwise INCONCLUSIVE for that unit.

Also report raw length histogram, mode, mean.

## CROSS-SITE
Per-site histograms + mode + geometric GoF for every site with >= 50 words. Count sites by
classification. Require a CONSISTENT majority shape. Leave-one-site-out (LOO) on the largest
site (Haghia Triada): recompute global classification with HT excluded; report.

## PROTOCOL
0. Inspect: overall length histogram, mode, mean; per-site histograms.
1. FREEZE prereg (this file) + plan_hash; machinery.py with `__main__` self-check (validate
   geometric/peaked fit on synthetic data of known shape: geometric-generated -> 'geometric',
   peaked-generated -> 'peaked').
2. GLOBAL: geometric fit (p_hat, GoF), peaked fit, BIC comparison, mode, classification.
3. POSITIVE CONTROL FIRST (gates verdict):
   - (a) synthetic GEOMETRIC data labeled 'geometric' AND synthetic PEAKED (mode>=2) data
         labeled 'peaked' (DETECT, both directions). Mislabel -> MACHINERY_UNINFORMATIVE.
   - (b) LB word lengths classified + reported (expected geometric-ish).
4. LA MAIN — CROSS-SITE: per site (>=50 words) classify (mode + geometric GoF). Count sites by
   shape; require consistent majority. LOO on HT.
5. FROZEN MECHANICAL VERDICT (one token):
   - `WORD_LENGTH_GEOMETRIC_CROSS_SITE` iff PC passed AND global shape=geometric (monotone-
     decreasing, geometric GoF adequate) AND >=3 sites classify geometric AND survives LOO.
   - `WORD_LENGTH_TEMPLATIC_PEAKED` iff PC passed AND global mode>=2 (peaked) AND peaked beats
     geometric (BIC) AND >=3 sites peaked.
   - `WORD_LENGTH_SHAPE_SITE_LOCAL` iff sites disagree on shape (no consistent majority).
   - `WORD_LENGTH_INCONCLUSIVE` iff neither model fits adequately / ambiguous.
   - `MACHINERY_UNINFORMATIVE` iff PC (synthetic classification) failed.
6. WRITE OUTPUTS to the EXACT PATH CONTRACT paths.

## OUTPUT KEYS (result.json)
`task_id="EPOCH-046"`, `method`, `result`, `verdict` (one allowed token), `numbers`, `key_findings`
(>=3), `successor_hypotheses` (>=5), `layer="L2/L3"`, `la_touched=true`, `non_circular` (str),
`deviations` (list).

`numbers.global = {length_hist, mode, mean, geometric_p_hat, geometric_gof_p,
                   peaked_bic_minus_geom_bic, classification}`
`numbers.positive_control = {pc_verdict, synth_geometric_labeled, synth_peaked_labeled,
                             lb_classification, lb_mode}`
`numbers.cross_site = {n_sites, shape_counts, loo_excluded, loo_classification}`

## SEEDS (frozen)
SEED_SYNTH_GEOM = 20240770, SEED_SYNTH_PEAKED = 20240771, SEED_LB = 20240772.
