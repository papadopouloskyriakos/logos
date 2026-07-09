# EPOCH-058 — Unsupervised Document Typology (L2, structural counts only)

## Question
Do Linear A inscriptions partition into recoverable structural DOCUMENT TYPES from their
structural profile ALONE (length, numeral-density, divider/line-break density, mean word
length)? Is that partition BEYOND a feature-shuffled null? Is it CROSS-SITE STABLE (do the
same structural doc-types recur at multiple sites)? Does it merely RECOVER the archaeological
'support' label (typology = intrinsic vs just the physical object type)?

## Layer
L2 — pure document-structure statistics. Structural counts only. NO sign values, NO readings,
NO phonetics/meaning.

## Data
corpus/silver/inscriptions_structured.json. Use inscriptions with >=2 content (word/num)
tokens (n≈465). Each inscription has 'stream' (tokens word/num/div/nl/other) + 'site' + 'support'.

## Features (FROZEN; log1p then z-score), per inscription
- x1 = n content tokens (word+num)
- x2 = numeral density (n_num / n_content)
- x3 = divider density (n_div / n_content)
- x4 = line-break density (n_nl / n_content)
- x5 = mean word length (signs per word)

## Method (FROZEN)
1. GLOBAL: k-means, k in {2,3,4}; pick k by silhouette; report chosen k, silhouette, sizes.
2. NULL: shuffle EACH feature column across inscriptions independently (destroys joint
   structure, preserves marginals); recluster at chosen k; recompute silhouette; >=500 perms;
   perm p = frac null silhouettes >= observed.
3. SUPPORT ALIGNMENT: Adjusted Rand Index between induced clusters and 'support' label.
4. CROSS-SITE STABILITY: for the 2 largest sites (Haghia Triada, Khania), induce k=2 partition
   WITHIN each site separately; train typology (k=2) on site A, apply to site B, measure
   agreement with B's own induced labels via ARI vs a label-permutation null.

## NON-CIRCULAR / DISCIPLINE (hard)
- Clustering features are STRUCTURAL COUNTS only.
- The 'support' label is NOT a feature. It is used ONLY post-hoc to compute ARI
  (characterize clusters), never as clustering input.
- L2 ONLY. No sign values, no readings, no phonetics/meaning.

## Positive Control (gates verdict)
- DETECT: plant 3 synthetic document types with distinct structural-feature means; confirm
  recovery (silhouette perm p<=0.05 AND recovered-vs-planted ARI>=0.6).
- FALSE-POSITIVE: single-type synthetic (all docs one feature distribution); spurious
  'significant structure' rate <=0.10 across >=20 draws.
- If miscalibrated -> MACHINERY_UNINFORMATIVE.

## Frozen Mechanical Verdict
- DOC_TYPOLOGY_CROSS_SITE_STABLE iff PC passed AND global silhouette perm p<=0.05 AND
  cross-site train/apply ARI beyond null AND support-ARI < 0.5.
- DOC_TYPOLOGY_TRACKS_SUPPORT_ONLY iff clustering beyond null BUT support-ARI >= 0.5.
- DOC_TYPOLOGY_SITE_LOCAL iff clustering beyond null BUT cross-site train/apply ARI NOT beyond null.
- NO_DOC_TYPOLOGY iff global silhouette NOT beyond null.
- DOC_TYPOLOGY_UNDERPOWERED iff <2 sites have >=25 usable inscriptions.
- MACHINERY_UNINFORMATIVE iff PC failed.

## Order
PC FIRST. Mechanical verdict from FROZEN rule. Proposer/operator, never adjudicator.
