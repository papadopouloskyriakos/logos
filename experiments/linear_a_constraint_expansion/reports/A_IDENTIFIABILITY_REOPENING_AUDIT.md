# Stage A — identifiability reopening audit

**Claim layer:** meta (audit of L6 identifiability). **Articles:** VIII, IX, XVII (append-only — the prior
result is annotated, not deleted), XXII. **Verdict: `A_REOPENED`.** `data/stage_a_budget.json`.

## Entry / success / failure gates

- **entry:** the reported `259 parameters > 212 constraints ⇒ UNDERDETERMINED` (main campaign `bac88a5`).
- **success:** the budget is recomputed from artifacts under every defensible specification and either
  confirmed, invalidated, or reopened with a corrected target.
- **failure:** artifacts unavailable / non-reproducible → `A_INCOMPLETE`.

## Finding — the 259>212 arithmetic is a category error (INVALIDATED)

Recomputed from `signs_ontology.json` + the corpus's own three sign inventories:

| specification | count | what it is |
|---|---|---|
| prior "parameters" (259) | 259 | ALL diplomatic stream tokens — syllabograms + logograms + fractions + damaged/composite word-internal variants. **Not the syllabary.** |
| raw syllabary V | 131 | every syllabogram token (72 A-only + 59 AB) |
| allograph families | 123 | syllabograms merged by `allograph_family` (answer-neutral) |
| **conservative inventory V** | **92** | **the corpus's own considered syllabary** |
| exploratory inventory V | 88 | more aggressive allograph merging |
| recurrent (freq ≥ 5) | 73 | signs with real statistical mass |
| A-only, truly undeciphered | 72 | no external value hypothesis (the hard core) |

A phonetic reading assigns values to the **syllabary (~88–92)**, not to 259 diplomatic tokens (logograms are
ideographic; fractions are a known metrological system; damaged/composite variants are not free parameters).
The "212 constraints", meanwhile, are **≥4-sign non-dominant-site inscriptions** — *structural/segmental*
units. Comparing 259 diplomatic tokens to 212 inscriptions compares two different categories.

## Corrected budget

- **Structural layer (favourable):** 92 syllabic parameters **< 212 structural constraints** → ratio **0.43**.
  By count, the corpus is *not* underdetermined for a reading. Prior arithmetic overstated the deficit.
- **Value layer (the real ceiling):** only **~2 value-informative held-out constraints** (the I, RI anchor
  pins that survived the cross-script gate) vs 92 syllabic parameters → **46×** deficit. The abundant
  structural constraints (segmentation, formula grammar, 212 inscriptions) **do not inform sign values** — the
  distributional value-channel is null (4× confirmed) and anchors are one-deep.

## Corrected diagnosis + reopen target

**The underdetermination is real but its cause is constraint INFORMATIVENESS at the value layer, not
constraint COUNT.** The prior "UNDERDETERMINED under the current corpus" conclusion stands qualitatively; its
quantitative justification is replaced. This *reopens* the campaign with a sharp, actionable target:

> Find **value-informative constraints** for the ~92 syllabic parameters — secure non-circular external
> anchors that survive held-out (Stage F, the load-bearing lever), and/or an internal channel that transfers
> to values. Stages B/D can additionally *reduce false parameters* (allograph merges: 131→123→92) and sharpen
> the space, but structure alone cannot assign values.

`A_REOPENED` — continue. **Authorized next:** Stage B (corpus forensics: reduce false parameters + recover
lost channels) and Stage D (constraint mining). **Forbidden:** claiming the favourable structural ratio as
progress toward a reading (it is necessary, not sufficient).
