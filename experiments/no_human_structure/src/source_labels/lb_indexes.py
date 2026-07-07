#!/usr/bin/env python3
"""Cited, published Linear B reference indexes (NOT LLM-generated).

Every entry is a standard, uncontested Mycenaean reading from the published lexica (Ventris–Chadwick,
*Documents in Mycenaean Greek*² glossary; Aura Jorro, *Diccionario Micénico*). These two share upstream
ancestry (DMic builds on V–C), so ALL entries here belong to ONE dependency cluster: `SHARED_DECIPHERMENT`.
That is recorded, but per the Stage-3 ontology it does not by itself disqualify a *secure* label.

These indexes are EVALUATION-side ground-truth material; they are NEVER exposed to the transferable model.
"""
DEP_CLUSTER = "SHARED_DECIPHERMENT"
CITATION = "Ventris–Chadwick, Documents² glossary; Aura Jorro, Diccionario Micénico (shared lineage)"
UPSTREAM = "Ventris 1952 decipherment + primary editions"

# PLACE — securely-identified Linear B toponyms (Knossos + Pylos provinces). evidence_basis LEXICAL_SEMANTIC.
TOPONYMS = {
    # Knossos / Crete
    "ko-no-so", "a-mi-ni-so", "pa-i-to", "ku-do-ni-ja", "ru-ki-to", "se-to-i-ja", "su-ki-ri-ta", "da-wo",
    "do-ti-ja", "ti-ri-to", "qa-mo", "ra-to", "ra-su-to", "e-ko-so", "u-ta-no", "ku-ta-to", "tu-ri-so",
    "pu-na-so", "e-ra", "ku-ru-mo-no", "ri-jo-no", "si-ja-du-we", "da-*22-to", "pa-ra-i-jo",
    # Pylos / Messenia — Hither & Further Province towns
    "pu-ro", "pa-ki-ja-ne", "pa-ki-ja-na", "ro-u-so", "a-ke-re-wa", "e-ra-te-re-we", "ka-ra-do-ro",
    "ri-jo", "me-ta-pa", "pe-to-no", "a-pu2-we", "a-si-ja-ti-ja", "e-re-e", "za-ma-e-wi-ja", "e-sa-re-wi-ja",
    "ti-mi-to-a-ke-e", "ra-wa-ra-ta2", "sa-ma-ra", "a-si-ja-ti-ja", "e-ni-pa-te-we", "za-e-to-ro",
    "o-ru-ma-to", "ne-do-wo-ta", "e-u-de-we-ro",
}
# HUMAN_OR_INSTITUTION — titles/offices (fine TITLE_OR_OFFICE). evidence_basis LEXICAL_SEMANTIC.
TITLES = {
    "wa-na-ka", "ra-wa-ke-ta", "te-re-ta", "e-qe-ta", "ka-ra-wi-po-ro", "i-je-re-ja", "i-je-re-u",
    "ko-re-te", "po-ro-ko-re-te", "da-mo-ko-ro", "mo-ro-qa", "qa-si-re-u", "po-ro-du-ma", "du-ma",
    "ke-ro-ta", "po-ru-da-si-jo", "o-pi-da-mi-jo", "ka-ma-e-u", "te-o-jo-do-e-ro", "te-o-jo-do-e-ra",
}
# HUMAN_OR_INSTITUTION — institution/collective terms
INSTITUTIONS = {"da-mo", "ke-ro-si-ja", "wo-ro-ki-jo-ne-jo", "ka-ma", "ko-to-na", "wa-tu"}
# OPERATOR_OR_RELATION — transaction/relation operators (evidence_basis GRAMMATICAL/DOCUMENT_INTERPRETATION)
OPERATORS = {"a-pu-do-si", "a-pe-do-ke", "a-pe-e-ke", "di-do-si", "di-do-to", "de-ka-sa-to", "o-di-do-si",
             "e-ke", "e-ke-qe", "pa-ro", "o-pe-ro", "o-pe-ro-sa", "o-pe-ro-si", "qe-te-o", "o-no"}
# DOCUMENT_STRUCTURE — totalling / boilerplate forms (STRUCTURAL_CONTROL_A; evidence STRUCTURAL_ONLY)
TOTALS = {"to-so", "to-sa", "to-so-de", "to-sa-de", "to-so-pa", "to-to", "o-da-a2", "a-pu-do-si"}
# QUALIFIER — common adjectival/qualifier forms (evidence_basis GRAMMATICAL)
QUALIFIERS = {"pe-ru-si-nu-wo", "ne-wo", "ne-wa", "pa-ra-jo", "e-me", "ke-ke-me-na", "ki-ti-me-na"}

# INDEX -> (coarse_role, fine_role, evidence_basis, default_category)
INDEXES = {
    "LF_TOPONYM_INDEX":     (TOPONYMS,     "PLACE", "TOPONYM", "LEXICAL_SEMANTIC", "REFERENCE_GOLD_A"),
    "LF_TITLE_INDEX":       (TITLES,       "HUMAN_OR_INSTITUTION", "TITLE_OR_OFFICE", "LEXICAL_SEMANTIC", "REFERENCE_GOLD_A"),
    "LF_INSTITUTION_INDEX": (INSTITUTIONS, "HUMAN_OR_INSTITUTION", "INSTITUTION", "LEXICAL_SEMANTIC", "REFERENCE_GOLD_A"),
    "LF_OPERATOR_INDEX":    (OPERATORS,    "OPERATOR_OR_RELATION", "TRANSACTION_OR_ALLOCATION_OPERATOR", "GRAMMATICAL", "WEAK_SILVER_B"),
    "LF_TOTAL_INDEX":       (TOTALS,       "DOCUMENT_STRUCTURE", "TOTAL_OR_SUBTOTAL", "STRUCTURAL_ONLY", "STRUCTURAL_CONTROL_A"),
    "LF_QUALIFIER_INDEX":   (QUALIFIERS,   "QUALIFIER", "QUALIFIER", "GRAMMATICAL", "WEAK_SILVER_B"),
}


def lookup(translit):
    """Return list of (index_name, coarse, fine, evidence, category) hits for a transliteration."""
    hits = []
    for name, (idx, coarse, fine, ev, cat) in INDEXES.items():
        if translit in idx:
            hits.append((name, coarse, fine, ev, cat))
    return hits
