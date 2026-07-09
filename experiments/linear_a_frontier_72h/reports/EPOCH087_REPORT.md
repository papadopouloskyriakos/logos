# EPOCH-087 REPORT — Linear A frontier-72h

## Task
Do Haghia Triada's three document-layout registers (E081 left-margin justification, E085 heading-size salience,
E086 header-length) CO-OCCUR as a coherent formal-layout TEMPLATE, or are they INDEPENDENT habits?
(L2; within-HT; geometry only; opaque IDs.)

## Method
Per HT doc (site == "Haghia Triada"; >=6 non-divider bbox glyphs; >=2 rows; first row >=2 glyphs; rest >=3 glyphs;
n=128) compute three register scores:
- `justif` = (rsd - lsd) / ((rsd+lsd)/2 + 1)  — positive = left-justified (right edge more ragged)
- `h_size` = log(median first-row glyph area / median rest area)
- `h_len`  = log(count(first row) / mean count(rest))

Coherence C = mean of the 3 pairwise |Spearman r|. Independence null: permute each of the 3 score-columns
INDEPENDENTLY (preserving each register's marginal, destroying cross-register co-occurrence), 1000 draws,
tie-aware p = (ge+1)/(ndraw+1). Size control: OLS-residualize each score on log(n_glyphs), recompute C and p.
Positive control: synthetic DETECT arm (shared formality factor -> all-positive template) and FALSE-POSITIVE arm
(3 independent columns), 15 reps each.

## Results

| quantity | value |
|---|---|
| n_docs (HT, usable) | 128 |
| C_obs | 0.1603 |
| perm_p (independence null) | 0.0070 |
| size-controlled C_obs | 0.1557 |
| size-controlled perm_p | 0.0110 |

Signed pairwise Spearman r:

| pair | r |
|---|---|
| justif ~ h_size | **-0.143** |
| justif ~ h_len  | **+0.149** |
| h_size ~ h_len  | **-0.189** |

Positive control: **PASSED** — detect power = 1.0 (median detect_p = 0.001 over 15 reps); false-positive rate =
0.067 (<= 0.10) over 15 reps.

## Verdict (mechanical, frozen rule)
**LAYOUT_REGISTERS_DEPENDENT_HT** — PC passed AND perm_p = 0.007 <= 0.05.

## Interpretation
The three HT layout registers are NOT independent habits: their per-doc scores co-occur above the
per-column-independence null (C_obs=0.160 vs null, p=0.007), and this survives size control (p=0.011).

BUT the dependence is MIXED-SIGN, not a coherent all-positive formal template. Two of three pairwise
correlations are negative. The dominant structure is a **heading-size <-> header-length TRADEOFF** (r=-0.189):
HT documents whose first row carries larger glyphs have SHORTER first rows. An all-positive template would
predict formal docs simultaneously show large AND long headers — the data show the opposite along that axis.

This refines the picture of E081/E085/E086: they are not three separate independent conventions, but neither
do they reduce to one shared "formality" standard. They form a structured (size-vs-length tradeoff) dependence.

## Bottom line
The HT layout registers are **dependent but via a mixed-sign tradeoff, not a coherent positive template** —
E081/E085/E086 are neither fully independent habits nor a single shared formal standard; their joint structure
is dominated by a big-glyph-short-header / small-glyph-long-header tradeoff that survives size control.

## Layer / scope
L2, opaque doc IDs, bbox geometry only, no phonetic/semantic values. Within-Haghia Triada.
