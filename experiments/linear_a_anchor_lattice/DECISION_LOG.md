# DECISION LOG — anchor-lattice campaign (append-only, Art. XVII)
- **Opened 2026-07-08** from red-team-verified 056e96d. §1 starting-state reconciled: 215 instances / 14 lineages /
  0 material errors — VERIFIED, no correction. main 6fd4f20 + paper a2ab89fa untouched; 38 tests pass; corpus
  symlinked. DO_NOT_REPEAT_UNCHANGED registry frozen (6 closed methods). Campaign pursues NEW channels only.

- **ERRATUM (Art. XVII, 2026-07-08, filed from frontier-72h EPOCH-005).** The Anetaki exposure audit's finding
  "no transliterated sign sequence of any length from KN Zg 57/58 is public" is FALSE for Zg 57: a public
  preliminary photo-reading (lineara.xyz, maintainer's own reading of Kanta et al. 2024 Fig. 7, committed
  2025-03-23: *401+RU, *652, *653, *401+RU, *418+L2, NI, VAS + lacunae) exists and had already leaked into
  corpus/silver as KNZg57a (5 tokens after letter-filtering). The Anetaki seal EXCLUSION LIST is hereby amended
  to add these 7 public tokens (Face-A-consistent vessel ligatures + NI). The seal's SCORING TARGETS are NOT
  exposed (no Face-B group, Face-C group, 4-sign Face-beta sequence, numeral grammar, or fraction identity is
  public) — the seal remains SEALED and scoreable. Provenance chain: frontier-72h EPOCH-005
  (reports/EPOCH005_KNZG57A_PROVENANCE.md). Supersedes the exposure claim only; no verdict changes.

- **SUPERSEDING NOTE (Art. XVII, 2026-07-08, filed from frontier-72h EPOCH-008).** WP-E's factual premise
  "SigLA carries ONLY axis-aligned bboxes — no strokes, vectors, contours, images" is FALSE: SigLA serves
  per-document raster renders of its hand-traced vector drawings (sigla.phis.me/document/<D>/<D>.png, ink in
  the ALPHA channel, CC BY-NC-SA 4.0). Combined with the on-disk bboxes these yield per-instance stroke
  graphs (frontier E008: 8/10 extraction after alpha+despeckle; held-out counterpart MRR 0.273 vs chance
  0.066). WP-E's SOURCE_BLOCKED verdict for TRUE-STROKE evidence is SUPERSEDED to PARTIALLY_UNBLOCKED; the
  bbox-aspect no-power finding stands. The stroke channel's LA value remains UNPROVEN (weak signal; full-corpus
  sweep pending on the frontier branch). No campaign verdict changes (the E-channel contributed nothing to the
  UNDERDETERMINED verdict either way).
