# E206 Stage-2 freeze (committed BEFORE any external-name content is inspected)

**Slot set:** verified SLOT_FREEZE.json (hash checked at run start) — 147 confirmatory
candidates; 4 contamination-flagged candidates form a separate EXPLORATORY stratum that can
never contribute to confirmatory graduation.

**External sources (frozen list; in-repo, licence-tracked in DATA_LICENSES.md):**
- INV1 `linear_b-greek.names.cog` LB column = the Linear B NAME inventory (Tamburini/
  NeuroDecipher lineage; sha256 in E201 manifest). The only confirmatory inventory family.
- REF1 `toponym_anchors.csv` = published LA-LB toponym equations — CONTAMINATION/PRIOR-ART
  REFERENCE ONLY (never evidence; candidates matching these pairs are auto-flagged prior-art).
- Chronology window: LB inventory = LMII-LMIIIB adjacency to LA LMIB (declared approximation);
  geography: Crete-centric (DAMOS-lineage); both recorded as assumptions, not filters, given
  single-inventory scope.

**Value-retention assumption (explicit, UNLICENSED):** LA sign-name sequence read via the A/B
same-sign convention (conditional-map status; every output carries this label).

**Drift matcher (frozen):** token-level Levenshtein over syllabic sign names: substitution
cost 0.5 when consonant class matches (same C, different V), else 1.0; insertion/deletion 1.0;
score = distance / max(len); MATCH iff score ≤ 0.34 (≈ at most one vowel-drift per 3 signs).
No per-candidate tuning; one model, no search over costs.

**Multiplicity family:** 147 candidates × 1 inventory × 1 matcher = 147 tests; Holm at α=.05.
Per-candidate p = plus-one MC percentile of its best-match score against its OWN canary battery.

**Canary battery (frozen; per candidate):** 200 length-matched fabricated names sampled from
LB sign-frequency distribution (seeded); 100 syllable-shuffled real inventory names; the
unrelated-language arm = Cypriot-Greek plain lexicon read as names (INV-control). Candidate
must beat ALL THREE families (Holm-adjusted p<.05 against fabricated; better best-score than
its shuffled and unrelated counterparts).

**Correspondence-system gate:** ≥3 Holm-surviving candidates whose matches share ONE coherent
recurring sign→sign mapping (no per-pair contradictions) — else no class claim.
**Held-out gate:** inventory split 70/30 seeded; the correspondence system induced on the 70%
fit-side matches must predict ≥1 additional 30%-side match (held-out prediction).
**Historical-replay validation:** the same matcher must recover ≥60% of true LB name pairs in
the names.cog benchmark itself (blinded lower bar) — detector qualification, run FIRST.

**Statuses:** L3_ONOMASTIC_CLASS_SUPPORTED | ONOMASTIC_CANDIDATES_EXPLORATORY_ONLY |
NO_MATCH_BEYOND_CANARIES | INSUFFICIENT_EXTERNAL_DATA | E206_INVALID. No L4 under any outcome
(second independent channel required). Seeds master 1336530913 prefix "E206S2".
