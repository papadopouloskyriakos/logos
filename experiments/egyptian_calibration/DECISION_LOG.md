# DECISION LOG — Egyptian Calibration Gate

## 2026-07-06 — E1: isolation + source-status audit (chunk 1)
- Forked research/egyptian-calibration-gate from research/external-minoan-anchors@6d2e926. Preconditions:
  parent clean; main f6a5682 / admin 87b4dea / ritual e6ee2b4 / paper / runtime / CSA untouched; target
  path absent. Child HEAD 6d2e926.
- Source-status audit (§III): Hoch 1994 (sha 4df9bc09, 594pp) group-writing transliteration OCR-CORRUPT;
  Kilani 2019 (sha 4ecff477, CC-BY) clean but WRONG LAYER (native vocalization); Kitchen (8pp) discussion
  only; Muchiki 1999 NOT ACQUIRED; Cretan sources excluded by rule. **No fittable non-Cretan correspondence
  corpus exists.** REQ-01 primary edition NOT audited → future Cretan toponyms confirmatory-ineligible.
- Commit: _(on commit)_

## 2026-07-06 — E2..E3: design frozen + final verdict (chunks 2-3)
- Froze schema (27 fields), tiers A/B/C/X, inclusion rules, model prereg spec (M0-M9, sha 3c56ed71,
  SPEC_FROZEN_AWAITING_CORPUS). build_corpus() -> [] (buildable=False), tested.
- **FINAL VERDICT (mechanical): status=INCOMPLETE, egyptian_channel_readiness=NOT_READY.** Load-bearing
  calibration corpus unbuildable (Hoch OCR-corrupt / Kilani wrong-layer / Muchiki absent) -> model
  unfittable -> power unassessable. Explicitly NOT a disguised NO_POWER (no fittable-but-weak corpus
  exists). Recommendation: resolve REQ-02b (machine-readable Hoch / >=150-entry hand-verified subset /
  Muchiki 1999). No real matching / preregistration / sign-value claim. 8 tests pass.

## 2026-07-06 — E4: extensive online search + owned-Hoch extraction attempt
- Online: no downloadable open Egyptian->foreign correspondence dataset (TLA/Ramses native; Trismegistos
  Greco-Roman names; Hoch/Muchiki/Schneider copyrighted print).
- Derivation from owned Hoch (extract_hoch.py): 101 entries / 76 tier-A candidates; headwords clean but
  headword<->etymon PAIRING is OCR-noise-limited and un-cleanable without hand-verification or a
  forbidden (circular) similarity heuristic. Below the >=150 clean-entry threshold.
- Verdict UNCHANGED: INCOMPLETE / NOT_READY. Sharpened recommendation: clean Hoch/Muchiki OR authorize a
  hand-verification pass. Derived data gitignored (Hoch copyrighted); extractor code + counts committed.
