# Egyptian calibration corpus — inclusion rules (DESIGN, frozen-in-principle; corpus not yet populated)

The corpus (once a usable source exists — see the audit blocker) is **non-Cretan only**: excludes
Kom el-Hetan Cretan toponyms, EA5647 Keftiu material, alleged Keftiu ritual strings, any Linear A
form, and any reserved confirmatory anchor. Layers: bronze (raw) → silver (normalized) → gold
`egyptian_calibration_primary` + `egyptian_calibration_sensitivity`.

## Record schema
`calibration_id · source_id · egyptian_form_original · egyptian_transliteration · foreign_source_form
· source_language · source_language_family · item_class{PERSONAL_NAME|TOPONYM|LOANWORD|TITLE|ETHNONYM|
DIVINE_NAME|OTHER} · period_start_bce · period_end_bce · dynasty_or_phase · genre · scribal_context ·
direct_vs_intermediary_transmission · source_form_confidence · egyptian_reading_confidence ·
segmentation_confidence · editorial_variants · phonological_notes · citation · page_or_entry ·
license_status · calibration_eligibility · exclusion_reason · record_version`.

## Eligibility (frozen rules)
1. **Source-form confidence** ≥ 0.7 for the PRIMARY set (independently attested source form);
   0.4–0.7 → sensitivity tier; < 0.4 → excluded.
2. **Egyptian-reading confidence** ≥ 0.7 for primary (unambiguous group-writing); else sensitivity.
3. **Disputed etymologies** → sensitivity tier only, never primary.
4. **Likely intermediary transmission** (e.g. via a third language) → excluded from primary
   (`exclusion_reason=intermediary`); may enter sensitivity.
5. **Duplicate attestations** of one foreign form → keep the highest-confidence, aggregate the rest.
6. **Multiple Egyptian spellings of one form** → all kept, weighted by attestation.
7. **Multiple foreign candidates for one Egyptian form** → excluded from primary (ambiguous target).
8. **Loanwords vs names** → both admissible; `item_class`-stratified models fit separately.
9. **Period/genre mismatch** to the LM-IB target horizon → down-weight; period-matched model built
   separately (NO_POWER-reported if too sparse).

## Freeze discipline
The eligibility thresholds above are the frozen rules; the PRIMARY calibration manifest is
checksum-pinned **before** model fitting. Sensitivity-tier inclusion is a prespecified alternative,
not a post-hoc addition. **Cretan target leakage is structurally impossible** — the corpus construction
excludes every Cretan/Keftiu/Linear-A record by rule, verified by an automated exclusion test when
the corpus is populated.

## Status
Rules frozen-in-principle; **corpus NOT populated** — blocked on a usable calibration source
(`EGYPTIAN_CALIBRATION_CORPUS_AUDIT.md`). No model may be fit until the primary manifest exists and
is pinned.
