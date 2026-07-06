#!/usr/bin/env python3
"""Public Linear A/B syllabic grid (phonetic value → GORILA/AB sign number).

This is the PUBLIC Ventris–Chadwick / GORILA sign numbering — standard scholarly notation, NOT a
logos projection or a reading of Linear A. It is used ONLY as a rendering/notation transform:
  * §VII — to present LA candidates as raw sign IDs (AB##), stripping the phonetic transliteration
    that would otherwise leak LA↔LB resemblance into the candidate packet;
  * §VIII — to give LB toponym targets their raw sign sequence alongside the conventional
    transliteration.
It is NEVER a selection input and NEVER a similarity/score. Verified against the data-learned
AB→value concordance (see verify_against_learned / test_syllabary_matches_learned).
"""
# value (lowercase, subscripts as digits: pa3, ra2) -> GORILA sign number
GRID = {
    "a": 8, "e": 38, "i": 28, "o": 61, "u": 10,
    "da": 1, "de": 45, "di": 7, "do": 14, "du": 51,
    "ja": 57, "je": 46, "jo": 36, "ju": 65,
    "ka": 77, "ke": 44, "ki": 67, "ko": 70, "ku": 81,
    "ma": 80, "me": 13, "mi": 73, "mo": 15, "mu": 23,
    "na": 6, "ne": 24, "ni": 30, "no": 52, "nu": 55,
    "pa": 3, "pe": 72, "pi": 39, "po": 11, "pu": 50,
    "qa": 16, "qe": 78, "qi": 21, "qo": 32,
    "ra": 60, "re": 27, "ri": 53, "ro": 2, "ru": 26,
    "sa": 31, "se": 9, "si": 41, "so": 12, "su": 58,
    "ta": 59, "te": 4, "ti": 37, "to": 5, "tu": 69,
    "wa": 54, "we": 75, "wi": 40, "wo": 42,
    "za": 17, "ze": 74, "zo": 20,
    "a2": 25, "a3": 43, "pa3": 56, "ra2": 76, "ra3": 33, "ro2": 68,
    "ta2": 66, "pu2": 29, "nwa": 48, "dwe": 71, "dwo": 90, "twe": 87, "pte": 62,
}


def value_norm(tok):
    """silver token -> grid key: 'PA₃'->'pa3', 'RA₂'->'ra2', 'KU'->'ku'. Non-syllabic returns None."""
    sub = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
    t = tok.translate(sub).lower()
    return t if t in GRID else None


def to_sign_id(tok):
    """A silver/LB phonetic token -> raw sign id. Syllabogram -> 'AB##'; already-a-sign (*###, logogram)
    -> passthrough tagged; unmapped -> '?<tok>' (flagged, never silently dropped)."""
    v = value_norm(tok)
    if v is not None:
        return "AB%02d" % GRID[v]
    t = str(tok)
    if t.startswith("*"):
        return "A" + t[1:]            # silver '*301' -> raw A-sign 'A301'
    return "?" + t                    # logogram / fraction / unmapped -> flagged raw token


def render(word):
    """list of phonetic tokens -> list of raw sign ids (order preserved)."""
    return [to_sign_id(t) for t in word]


def lb_sequence(translit):
    """LB conventional transliteration 'pa-i-to' -> raw sign sequence ['*03','*28','*05']."""
    out = []
    for syl in translit.split("-"):
        v = value_norm(syl)
        out.append("*%02d" % GRID[v] if v is not None else "?" + syl)
    return out


def verify_against_learned(learned_ab_to_value):
    """learned_ab_to_value: {'AB81':'KU', ...} -> (agreements, conflicts[list])."""
    agree, conflict = 0, []
    for ab, val in learned_ab_to_value.items():
        n = int(ab[2:]); v = value_norm(val)
        if v is None:
            continue
        if GRID.get(v) == n:
            agree += 1
        else:
            conflict.append((ab, val, GRID.get(v)))
    return agree, conflict
