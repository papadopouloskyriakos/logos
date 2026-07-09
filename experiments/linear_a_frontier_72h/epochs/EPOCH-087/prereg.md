# EPOCH-087 PREREGISTRATION — Linear A frontier-72h

## Task
EPOCH-087 — Do Haghia Triada's three document-layout registers CO-OCCUR (a coherent formal-layout TEMPLATE)
or are they INDEPENDENT? (spatial synthesis; L2; within-HT).

## Background
Prior epochs found THREE HT-local layout registers:
- E081: left-margin JUSTIFICATION
- E085: heading-SIZE salience
- E086: header-LENGTH (full-width top line)

If HT scribes followed a coherent formal-document TEMPLATE, these would CO-OCCUR (the same docs show all three).
If they are independent habits, the per-doc register scores are statistically INDEPENDENT.

## Data
- Source: experiments/linear_a_frontier_72h/data/sigla_glyphs_bbox.json
- Filter: site == "Haghia Triada" only.
- Per-doc inclusion: >=6 non-divider bbox glyphs AND >=2 rows AND first row >=2 glyphs AND rest >=3 glyphs
  (so h_size defined). Expected n ~ 128.
- Opaque IDs only (doc index). Geometry only. No phonetic/semantic values. L2.

## Per-doc register scores (3)
- justif: row left-edge alignment tighter than right = left-justified. (rsd-lsd)/((rsd+lsd)/2 + 1).
- h_size: log(median first-row glyph AREA / median rest AREA).
- h_len: log(count(first row) / mean count(rest)).

## Coherence statistic
C = mean of the 3 pairwise |Spearman correlations| among (justif, h_size, h_len).

## Null model (independence)
Permute each of the 3 score-columns INDEPENDENTLY (shuffle each column separately, preserving each register's
marginal distribution but destroying any cross-register co-occurrence); recompute C; 1000 draws;
perm_p = frac(null C >= observed C), tie-aware (+1)/(ndraw+1).

## Size control
Residualize each score on log(n_glyphs) (simple OLS), recompute C and perm_p.

## Positive control (synthetic, gates verdict)
- (a) DETECT: ~128 synthetic docs with shared latent formality f~N(0,1): justif=f+noise, h_size=f+noise,
  h_len=f+noise (all 3 positively correlated = coherent template). Confirm perm_p<=0.05; power_est over >=15 reps.
- (b) FALSE-POSITIVE: ~128 docs with 3 INDEPENDENT columns (no shared factor). Confirm fire-rate <=0.10 over >=15 reps.
- If can't DETECT a coherent template OR fires on independent columns -> MACHINERY_UNINFORMATIVE.

## Frozen verdict (mechanical)
- LAYOUT_REGISTERS_DEPENDENT_HT iff PC passed AND perm_p<=0.05. Report signed pairwise r (positive template vs
  mixed/tradeoff dependence).
- LAYOUT_REGISTERS_INDEPENDENT_HT iff PC passed AND perm_p>0.05.
- REGISTER_COHERENCE_UNDERPOWERED iff n<60 usable HT docs OR PC power<0.5.
- MACHINERY_UNINFORMATIVE iff PC calibration fails.

## Fixed seed
Seed fixed for reproducibility (in machinery.py).

## Plan hash
See plan_hash.txt = "<sha256>  prereg.md".
