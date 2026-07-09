# EPOCH-095 — frozen prereg slice (geographic/scribal morphogenesis)

**Family:** TURING_MORPHOGENESIS (E091–E096) · **priority:** IMMEDIATE · **layer:** L2 · **gate:** A/E
**Parent prereg:** `morphogenesis/PREREGISTRATION.md` (E095 slice frozen for the plan_hash). Last reserved F11 leg.

## Question (frozen)
Does an RD/morphogenesis process over a DOCUMENT-similarity graph recover SITE / regional community structure
better than generic clustering (spectral, Louvain) and a frequency/length confound baseline? Truth = LA
inscription site label (L2 structural metadata; opaque signs, NO phonetic values).

## Design (frozen)
- **Corpus:** LA inscriptions (`corpus/silver/inscriptions.json`), sites with ≥25 docs (HT, Khania, Knossos,
  Phaistos, Zakros, Palaikastro, …). **Balanced** by subsampling each site to CAP=80 (HT dominates 63%), averaged
  over 5 subsample seeds.
- **Graph:** document nodes; edges = cosine of normalized sign-frequency vectors; largest CC; sym-norm Laplacian.
- **Methods:** morphogenesis (RD Schnakenberg activator communities, unsupervised coarsest-mode) · spectral
  clustering · Louvain · **length-only** (confound baseline) · random. k = n_sites.
- **Metric:** site-recovery ARI (+ NMI). A genuine geographic signal must beat length-only AND random.
- **Positive control:** synthetic planted-site corpus (site-specific Dirichlet sign distributions); generic
  clustering must recover planted sites (ARI > 0.25) else NO_POWER.

## Deviation (disclosed)
Parent prereg said "LB calibration then LA." LB per-document site metadata is not loadable via `load_b_damos`, so
the DETECTOR is calibrated on the synthetic planted-site corpus (Stage-1) and applied to LA (Stage-4). Recorded in
the ledger `deviations`.

## Verdicts (mechanical)
- **GEOGRAPHIC_MORPHOGENESIS_SUPPORTED** — morphogenesis beats length-only, random, AND generic baselines.
- **GEOGRAPHIC_MORPHOGENESIS_GENERIC** — beats the confound floor but not generic clustering.
- **GEOGRAPHIC_MORPHOGENESIS_NULL** — does not beat the length/random floor.
- **GEOGRAPHIC_MORPHOGENESIS_NO_POWER** — PC fails.

## Prior / scope
E091/E092/E094 established morphogenesis ties/loses to generic methods; the campaign's E012 doc→site was
NO_POWER/confounded. A _GENERIC or _NULL is expected. L2, opaque signs, site = structural metadata only; no
phonetic values, no dialect label without independent evidence.
