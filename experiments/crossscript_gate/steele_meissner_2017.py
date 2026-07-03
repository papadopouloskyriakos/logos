#!/usr/bin/env python3
"""steele_meissner_2017.py — page-cited data constants from the ACQUIRED primary text.

Source: P. M. Steele & T. Meißner, "From Linear B to Linear A: The problem of the backward
projection of sound values", in Steele (ed.), *Understanding Relations Between Scripts* (Oxbow
2017), pp. 93–110. File: corpus/bronze/steele_meissner_2017/chapter-6.pdf,
SHA-256 a80810e419eae8492e63ed7971e9e65d9f78d3506770a750b9e467f126d34553 (PROVENANCE.md).

Every constant below was VERIFIED against the PDF on 2026-07-03 (pages are the BOOK page
numbers printed on the pages). Nothing here is reconstructed from secondary summaries.
"""

CITATION = ("Steele & Meissner 2017, in Understanding Relations Between Scripts (Oxbow), "
            "93-110; local copy corpus/bronze/steele_meissner_2017/chapter-6.pdf "
            "sha256 a80810e4...d34553")

# ---------------------------------------------------------------------------
# §3 + Table 6.2 (p. 98): "Eleven signs can be identified with a high degree of certainty:
# a, i, da (=ta in the Cypriot Syllabary), na, pa, po, ro (=lo in the Cypriot Syllabary but
# ro/lo in Linear B), sa, se, ti and to (see Table 6.2)."
# Keys are the repo's GORILA/AB tokens; ab = the AB number given in Table 6.2 column 1.
# ---------------------------------------------------------------------------
CYPRIOT_STABLE_11 = {
    "A":  {"ab": "AB 08", "cm": "sign 102", "cs_value": "a",  "page": 98},
    "I":  {"ab": "AB 28", "cm": "sign 104", "cs_value": "i",  "page": 98},
    "DA": {"ab": "AB 01", "cm": "sign 004", "cs_value": "ta", "page": 98,
           "note": "= ta in the Cypriot Syllabary (d/t series discussion pp. 98-99)"},
    "NA": {"ab": "AB 06", "cm": "sign 013", "cs_value": "na", "page": 98},
    "PA": {"ab": "AB 03", "cm": "sign 006", "cs_value": "pa", "page": 98},
    "PO": {"ab": "AB 11", "cm": "Not attested?", "cs_value": "po", "page": 98,
           "note": "Cypro-Minoan cell reads VERBATIM 'Not attested?' (Table 6.2, p. 98)"},
    "RO": {"ab": "AB 02", "cm": "sign 005", "cs_value": "lo", "page": 98,
           "note": "= lo in the Cypriot Syllabary but ro/lo in Linear B (p. 98)"},
    "SA": {"ab": "AB 31", "cm": "sign 082", "cs_value": "sa", "page": 98},
    "SE": {"ab": "AB 09", "cm": "sign 044", "cs_value": "se", "page": 98},
    "TI": {"ab": "AB 37", "cm": "sign 021", "cs_value": "ti", "page": 98},
    "TO": {"ab": "AB 05", "cm": "sign 008", "cs_value": "to", "page": 98},
}

# §3, p. 98: "Without quite going as far as Masson (1987) ... we can perhaps add others to the
# list: si, for example, is a good contender."  CANDIDATE, not a member of the eleven.
CYPRIOT_CANDIDATES = {
    "SI": {"page": 98, "quote": "si, for example, is a good contender"},
}

# ---------------------------------------------------------------------------
# Table 6.4 (p. 102): "Possible place name equations between Linear B and Linear A".
# LA forms as printed (underdots = damaged/uncertain readings, kept as annotations).
# Attestations from Table 6.3 (p. 101, bold = place names). `queried` marks forms the
# chapter itself flags with '?' elsewhere (§5 s-series, p. 103).
# ---------------------------------------------------------------------------
TOPONYM_EQUATIONS = (
    {"lb": "pa-i-to", "la_signs": ("PA", "I", "TO"), "la_printed": "pa-i-ṭọ",
     "la_attestation": "HT 97a.3 +", "lb_attestation": "KN D +", "page": 102,
     "note": "LA to underdotted (damaged) in Tables 6.3/6.4", "queried": False},
    {"lb": "se-to-i-ja", "la_signs": ("SE", "TO", "I", "JA"), "la_printed": "se-to-i-ja",
     "la_attestation": "PR Za 1.b", "lb_attestation": "KN D +", "page": 102, "queried": False},
    {"lb": "tu-ri-so", "la_signs": ("TU", "RU", "SA"), "la_printed": "tu-ru-sa",
     "la_attestation": "KO Za 1", "lb_attestation": "KN Ce 59.3 +", "page": 102,
     "note": "second LA form a-tu-ṛị-si-ti (KN Zb 5) listed too; §5 marks both s-series "
             "attestations with '?' (p. 103) — the variant is recorded separately below",
     "queried": False},
    {"lb": "di-ka-ta(-jo)", "la_signs": ("DI", "KI", "TE"), "la_printed": "di-ki-te",
     "la_attestation": "PK Za 11 ((a-)di-ki-te(-te), Table 6.3)", "lb_attestation": "KN Fp 1",
     "page": 102, "queried": False},
    {"lb": "su-ki-ri-ta", "la_signs": ("SU", "KI", "RI", "TA"), "la_printed": "su-ki-ri-ta",
     "la_attestation": "PH Wa 32", "lb_attestation": "KN D", "page": 102, "queried": False},
    # the queried variant form (NOT used by the power sim's constraint channel):
    {"lb": "tu-ri-so", "la_signs": ("A", "TU", "RI", "SI", "TI"), "la_printed": "a-tu-ṛị-si-ti",
     "la_attestation": "KN Zb 5", "lb_attestation": "KN Ce 59.3 +", "page": 102,
     "note": "'? a-tu-ri-si-ti' in the §5 s-series list (p. 103) — chapter's own query mark",
     "queried": True},
)

# ---------------------------------------------------------------------------
# §5 (p. 103): internal-variation series evidence (the confidence channel), verbatim sets.
# ---------------------------------------------------------------------------
INTERNAL_VARIATION_SERIES = {
    "m-series": {"signs": ("MA", "ME", "MI"), "page": 103,
                 "evidence": "(j)a-sa-sa-ra-me / ja-sa-sa-ra-ma-na; i-pi-na-ma / i-pi-na-mi-na",
                 "note": "MU added 'by another, admittedly less certain, method' (cow ideogram "
                         "acrophony) -> mu? (p. 104)"},
    "t-series": {"signs": ("TA", "TE", "TI", "TO", "TU"), "page": 103,
                 "evidence": "su-ki-ri-ta / su-ki-ri-te-i-ja; (j)a-di-ki-te-te / ja-di-ki-tu; "
                             "'a whole consonantal series (the t-series)' (p. 102)"},
    "u-w-series": {"signs": ("U", "WA"), "page": 103,
                   "evidence": "? qe-ra2-u / ? qa-ra2-wa; ja-ta-i-*88-u-ja / a-ta-i-*88-wa-ja",
                   "note": "both marked '?' in the chapter; fn 19: 'reflexes of a semi-vowel', "
                           "not sensu stricto one series — recorded as evidence, NOT a "
                           "confirmed tier"},
    "s-series": {"signs": ("SA", "SI", "TI"), "page": 103,
                 "evidence": "? tu-ru-sa / ? a-tu-ri-si-ti",
                 "note": "both attestations carry the chapter's own '?'"},
}

# ---------------------------------------------------------------------------
# The chapter's cumulative "confirmed values" tiers (grids, by book page):
#   Table 6.5 (p. 102): Cypriot + place names — "19 or 20 signs" (si with '?').
#   Table 6.6 (p. 104): + internal variations (adds the m-series; mu with '?').
#   Table 6.11 (p. 108): + ideographic/acrophonic use (adds ni, ru; p. 107: "we can add ni
#   and ru to our grid and confirm some other entries (ma, ki, na)").
# Per-sign FIRST tier at which the sign enters the grid.
# ---------------------------------------------------------------------------
SM2017_TIER = {
    # Table 6.2 / §3 (p. 98) — the Cypriot-stable eleven
    **{s: "T6.2_cypriot_p98" for s in CYPRIOT_STABLE_11},
    # Table 6.5 (p. 102) — added by the place-name equations
    "DI": "T6.5_placenames_p102", "KI": "T6.5_placenames_p102", "RI": "T6.5_placenames_p102",
    "SU": "T6.5_placenames_p102", "TA": "T6.5_placenames_p102", "TE": "T6.5_placenames_p102",
    "TU": "T6.5_placenames_p102",
    "SI": "T6.5_placenames_p102(si?)",       # enters the grid as 'si?' (queried)
    # Table 6.6 (p. 104) — added by internal variations
    "MA": "T6.6_internal_variation_p104", "ME": "T6.6_internal_variation_p104",
    "MI": "T6.6_internal_variation_p104", "MU": "T6.6_internal_variation_p104(mu?)",
    # Table 6.11 (p. 108) — added by ideographic/acrophonic evidence
    "NI": "T6.11_ideographic_p108", "RU": "T6.11_ideographic_p108",
}

# LA sign coverage of the five non-queried toponym forms (the sim's constraint channel).
TOPONYM_COVERED_SIGNS = tuple(sorted({s for t in TOPONYM_EQUATIONS if not t["queried"]
                                      for s in t["la_signs"]}))
