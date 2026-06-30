# Finding 2026-07-01 — Direction-A STRATIFIED morphology re-run (#20): NULL at the pre-registered bar, a disclosed near-miss

Executes the two dated pre-registration addenda (`prereg-morphology-stratification-addendum-2026-06-30`
+ `prereg-morphology-salgarella-addendum-2026-06-30`) over the full corpus
(`scripts/comparison/morphology_stratified.py`): induce the FROZEN pre-registered affix panel **per
genre stratum**, test **cross-stratum stability** above a **per-affix L_fake bigram floor**, with the
**abbreviation channel excluded** and within-SITE non-independence controlled. Graded from the
persisted artifact (`runtime/morphology-stratified.json`). **This finding was rewritten after an
independent adversarial review** flagged that the first draft overclaimed robustness — the disclosures
below are the result. CPU/laptop. NO phonetic claim; imports no `verdict.py`.

## Headline — NULL at the pre-registered α=0.01 (and the honest caveats)

| stratum (genre, from GORILA `support`) | inscriptions | words | sites |
|---|---|---|---|
| **admin** (tablets, bars) | 290 | 1,486 | 14 |
| **libation** (stone vessels only) | 99 | 370 | 15 |
| **other** (clay/metal/stone-object/inked/graffiti…) | 129 | 187 | 40 |

Abbreviation channel: 740 seal inscriptions (Nodule/Roundel/Sealing/Label) are **always** excluded
(they are ~1-sign seal markings, not candidate word morphology) + 333 admin list-headers (votive
first-words kept). Chronological CV **declined** (988/1341 ≈ 74% single-horizon LM IB).

- **`has_validated_morphology = False`.** No pre-registered affix is cross-stratum stable above the
  bigram floor at the pre-registered **α=0.01**.

## Threshold + bucketing sensitivity — DISCLOSED (the negative is a near-miss, not a comfortable null)

The independent review correctly flagged that the null is a *threshold call*. The full 2×2:

| | **α=0.01** (pre-registered) | **α=0.05** (conventional) |
|---|---|---|
| **defensible** bucketing (libation = stone vessels only) | NULL | NULL |
| **loose** bucketing (libation incl. stone objects + inked) | NULL | `i-`, `-te/-ti` **validate** |

Reading it honestly:
- **The pre-registered α=0.01 null is robust to the genre-bucketing choice** (NULL under both
  bucketings) — so the bucketing fix below is *not* cherry-picking the null.
- A positive appears **only in the doubly-relaxed corner** (α=0.05 *and* the loose bucketing): there,
  `i-` (locative "to/at") and `-te/-ti` (ablative "from/of") — the **Duhoux/Valério H3 nominal
  affixes, which Salgarella 2025 §8 independently endorses** — validate cross-stratum + site-robust.
- So the would-be positive is **fragile to both the α threshold and a defensible genre choice**. We
  report the null, and flag the **H3 nominal affixes as the borderline candidates** — the closest thing
  to recoverable morphology in the corpus, but not clearing the pre-registered bar. (The bucketing fix
  itself is independently justified: the module defines libation as "stone vessels bearing the
  formula," so stone objects + inked inscriptions belong in `other`, not libation — the review flagged
  the original inclusion as inconsistent.)

## What stratification ADDED over the pooled null

- **Even `i-*301` (Davis's verb stem) is bigram-reproducible in the libation register.** In the
  libation stratum the fabricated (markov sign-bigram) L_fake corpus *also* confirms `i-*301`, `a-`,
  `ja-` — the formula is so repetitive a bigram model manufactures the apparent verb morphology. Davis
  is not refuted (the slot grammar is real); the formula is simply **not statistically separable from
  sign bigrams** on this corpus. (Verified across seeds.)
- The residual signals are **register / single-stratum**, exactly the confound the within-permutation
  null — which preserves pooling — cannot catch.

## Discipline — two confounds caught (one by me, one by the reviewer)

1. **Panel-CONFIRM vs the bigram floor (caught mid-build).** The first cut graded on panel-CONFIRM,
   letting the bigram-trivial prefix `a-` free-ride (`real == L_fake` in admin). Fixed with the
   per-affix L_fake floor (`morphology = real_confirmed − L_fake_confirmed`); `a-` is excluded from
   every stratum (regression test).
2. **Overclaimed robustness + a mislabeled control (caught by the independent reviewer).** The original
   finding said "the null HOLDS and sharpens" without disclosing the α=0.05 flip, and the docstring
   claimed "deflate effective-n for within-site" when the code actually applies a **≥2-distinct-sites
   presence gate** (a conservative proxy — full effective-n deflation of the z-test is *not* applied; it
   would only **strengthen** the null; recorded as a known limitation in `within_site_control`). Both
   are now corrected here and in the code/docstrings.

## Method / discipline notes

- **Genre strata** from the `support` field (Salgarella 2025 §6); seal supports excluded structurally.
- **Within-site control (#19):** Linear A hands are not individuated (Salgarella 2019), so SITE is the
  independence unit; a candidate must be borne across **≥2 distinct sites**. This is a presence gate,
  **not** effective-n deflation (see above).
- **Survivor lists are n_null/L_fake-seed-specific** (the 3-draw union floor is noisy in thin strata);
  **only the grade bucket (validated vs null) is robust**. The descriptive per-stratum survivor lists
  are reported as run-specific, not as findings.
- **No phonetic claim.** A passing affix is a structural/paradigmatic object; no sign value is imputed.

## Verified

Full suite green (+6 stratified tests; partitioning deterministic — 740 seal / 290 admin / 99 libation
/ 129 other; the pre-reg α=0.01 null reproduces across seeds and both bucketings). Raw artifact
`runtime/morphology-stratified.json` (gitignored), including the recorded α-sensitivity.

## Implication for the draft

Direction A's negative is now precise and honestly bounded: **at the pre-registered α=0.01 there is no
validated cross-stratum morphology, robust to the genre bucketing; the closest candidates are the
Duhoux/Valério H3 nominal affixes (`i-`, `-te/-ti`), which surface only under a doubly-relaxed
(α=0.05 + loose-bucketing) setting and which the current synthesis (Salgarella §8) independently lists.**
That is a stronger, more credible referee artifact than a flat null — it names what is borderline, the
threshold, and the sensitivity — with two confounds caught and disclosed. Track-1 morphology is
complete; full effective-n deflation is the one recorded, deferred limitation.
