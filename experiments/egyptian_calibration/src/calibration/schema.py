#!/usr/bin/env python3
"""§IV calibration record schema + inclusion rules + eligibility tiers (frozen DESIGN; data-independent).

The corpus is EMPTY because the load-bearing source is unavailable (§III). This module freezes the
schema/rules so that IF a fittable Hoch/Muchiki dataset arrives (REQ-02b), the corpus can be populated
with NO post-hoc design freedom. `build_corpus()` returns [] with the documented blocker — the empty
state is a tested, reproducible fact, not a silent gap."""

ITEM_CLASSES = ["PERSONAL_NAME", "TOPONYM", "ETHNONYM", "DIVINE_NAME", "TITLE", "LOANWORD", "OTHER"]
ELIGIBILITY_TIERS = {
    "A": "high-confidence Egyptian reading + high-confidence foreign source form",
    "B": "usable with one bounded uncertainty",
    "C": "disputed / sensitivity-only",
    "X": "excluded",
}
CRETAN_EXCLUSIONS = ["kom_el_hetan", "keftiu", "ea5647", "linear_a", "cretan_confirmatory_anchor"]

REQUIRED_FIELDS = [
    "calibration_id", "source_id", "entry_number", "egyptian_original_form", "egyptian_transliteration",
    "editorial_variants", "foreign_source_form", "source_language", "source_language_family", "item_class",
    "period_start_bce", "period_end_bce", "dynasty_or_phase", "genre", "scribal_context",
    "direct_vs_intermediary_transmission", "source_form_confidence", "egyptian_reading_confidence",
    "segmentation_confidence", "etymology_status", "phonological_notes", "citation", "page_or_entry",
    "license_status", "calibration_eligibility", "exclusion_reason", "record_version",
]

# frozen inclusion rules (data-independent)
INCLUSION_RULES = {
    "disputed_etymology": "sensitivity tier (C) only; never primary",
    "donor_language_uncertain": "down-tier to B; if unresolvable → C",
    "intermediary_transmission": "excluded from primary (exclusion_reason=intermediary); may enter sensitivity",
    "duplicate_attestation": "keep highest-confidence; aggregate the rest",
    "multiple_spellings_of_one_form": "all kept, weighted by attestation, grouped to one fold",
    "multiple_source_proposals": "excluded from primary (ambiguous target)",
    "genre_mismatch_to_LMIB": "down-weight; period-matched model built separately; NO_POWER if too sparse",
    "period_mismatch": "same as genre_mismatch",
    "names_vs_loanwords": "both admissible; item_class-stratified models fit separately",
    "short_forms": "flagged; min-length sensitivity",
    "damaged_egyptian_spelling": "egyptian_reading_confidence<0.7 → B/C per severity",
    "uncertain_segmentation": "segmentation_confidence<0.7 → B/C",
    "cretan_or_keftiu_or_LA": "X excluded by rule (target leakage) — verified by test",
}


def validate_record(r):
    missing = [f for f in REQUIRED_FIELDS if f not in r]
    if missing:
        return False, f"missing fields {missing}"
    if r["calibration_eligibility"] not in ELIGIBILITY_TIERS:
        return False, "bad tier"
    if r["item_class"] not in ITEM_CLASSES:
        return False, "bad item_class"
    low = (str(r.get("source_id", "")) + str(r.get("citation", ""))).lower()
    if any(x in low for x in CRETAN_EXCLUSIONS):
        return False, "cretan target leakage"
    return True, "ok"


def build_corpus():
    """Populate from a fittable non-Cretan source. Returns (records, blocker). Currently BLOCKED (§III)."""
    blocker = {"buildable": False,
               "reason": "no fittable non-Cretan Egyptian→foreign correspondence source (Hoch OCR-corrupt at "
                         "the transliteration layer; Kilani is native-vocalization wrong-layer; Muchiki "
                         "unavailable; Kitchen discussion-only)",
               "unblock": "REQ-02b — machine-readable Hoch OR ≥150-entry hand-verified Hoch subset OR Muchiki 1999"}
    return [], blocker


if __name__ == "__main__":
    recs, blocker = build_corpus()
    print(f"schema fields: {len(REQUIRED_FIELDS)}; item classes: {len(ITEM_CLASSES)}; tiers: {list(ELIGIBILITY_TIERS)}")
    print(f"corpus records: {len(recs)}  buildable: {blocker['buildable']}")
    print(f"blocker: {blocker['reason']}")
