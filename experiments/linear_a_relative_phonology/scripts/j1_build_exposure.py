#!/usr/bin/env python3
"""J1 — Anetaki public-exposure audit: emit data/J1_exposure.json.

Counts/hashes are script-generated (Constitution Art. XII / invariant 12). Source SHA-256s are
the repo-recorded vault hashes (the licensed bronze PDFs are gitignored and NOT present in this
worktree); we cite them and hash our own captured artifacts (the web snapshot) directly.

NON-CIRCULAR: this audit records only public metadata; no held-out label is read, no model runs.
"""
import hashlib
import json
import os
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.dirname(HERE)
DATA = os.path.join(CAMP, "data")
WEB_CAPTURE = os.path.join(DATA, "source_watch", "J1_web_capture_2026-07-07.txt")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


# ---- Sources actually used (repo-recorded vault hashes; PDFs gitignored / absent here) ----
SOURCES = [
    {
        "id": "SRC-KANTA-2024",
        "role": "PRIMARY epigraphic overview — the ONLY scholarly source that describes the "
                "carriers; prints NO transliterated sign sequence.",
        "citation": "A. Kanta, D. Nakassis, T. G. Palaima & M. Perna, 'An archaeological and "
                    "epigraphical overview of some inscriptions found in the Cult Center of the "
                    "city of Knossos (Anetaki plot)', KO-RO-NO-WE-SA / Ariadne Suppl. 5 (2024/2025), "
                    "pp. 27-43. DOI 10.26248/ariadne.vi.1841. CC BY-NC-SA 4.0.",
        "sha256_repo_recorded": "87dad27b79ee3ef4539b844d7ed30a0069ac14acdd2ff75eed160f9baadf57d2",
        "vault": "corpus/bronze/kanta_etal_2024_anetaki/ (gitignored; 3,104,974 B; NOT in this worktree)",
        "verified_present_in_worktree": False,
        "fringe_flag": False,
    },
    {
        "id": "SRC-RJABCHIKOV-2025",
        "role": "REGISTRY quarantine object (fringe). Photograph-derived 'decipherment' predating "
                "any edition -> a committed, dated, mechanically-gradable external hypothesis. "
                "NEVER evidence about Linear A.",
        "citation": "S. V. Rjabchikov, 'The Decipherment of two Records of Linear A on the Ivory "
                    "Mirror from Knossos, Crete', in Ivanovskaya & Kuzmina (eds.), Tendentsii i "
                    "problemy razvitiya sovremennoy nauki (IV int. conf., Petrozavodsk, 2025-08-18), "
                    "MTsNP Novaya Nauka, pp. 100-106. ISBN 978-5-00215-841-6.",
        "sha256_repo_recorded": "b4ce36798ad0271c86509a2c8ff54cefe52194131f0a51ee2fd2e06864c40437",
        "vault": "corpus/bronze/rjabchikov_2025_sceptre/ (gitignored; NOT in this worktree)",
        "verified_present_in_worktree": False,
        "fringe_flag": True,
    },
    {
        "id": "SRC-CHIAPELLO-2024",
        "role": "REGISTRY prediction object (no fringe judgment). Dated pre-publication prediction "
                "(A/B similarity greater than assumed; Greek-reading reappraisal). Scorable when "
                "Anetaki II lands. PDF login-gated -> only the Wayback page HTML was captured.",
        "citation": "D. Chiapello, 'Deductions on an unknown find surrounded by mystery: the Linear "
                    "A inscribed ivory circle found at Knossos', Academia.edu (114586901), posted "
                    "2024-02-07.",
        "sha256_repo_recorded": "e52e31f9be01290d241f837e9acace8ce9048a61322f1bff242f255503cf92b5",
        "vault": "corpus/bronze/prepub_prediction_2024_ivory_circle/ (Wayback 20260703173735; gitignored)",
        "verified_present_in_worktree": False,
        "fringe_flag": False,
    },
    {
        "id": "SRC-J1-WEBCAPTURE-2026-07-07",
        "role": "This audit's own web-search capture (WebSearch x3; WebFetch of greekreporter 403'd). "
                "Confirms no public transliteration exists and Anetaki II is still unpublished; "
                "surfaces one new EVENT: Kanta & Charitos, June-2025 conference talk (not a text).",
        "citation": "WebSearch/WebFetch session 2026-07-07 (Anthropic tools). Snapshot on disk.",
        "sha256_of_captured_artifact": sha256_file(WEB_CAPTURE),
        "vault": os.path.relpath(WEB_CAPTURE, CAMP),
        "verified_present_in_worktree": True,
        "fringe_flag": False,
    },
]

# ---- Already-public inventory (editor-printed ONLY; nothing read off photographs) ----
ALREADY_PUBLIC = {
    "carriers": {
        "KN Zg 57": "ivory Ring, single elephant-tusk slice, outer dia c.13.5-14 cm; faces A(top)/"
                    "B(bottom)/C(external)/D(internal); provisionally a religious scepter.",
        "KN Zg 58": "ivory handle, quadrangular section c.13 cm; faces alpha/beta/gamma/delta; "
                    "'an accounting text' with numerals & fractions.",
    },
    "length_and_totals": {
        "ring_signs_total_approx": 119,
        "ring_signs_preserved_or_partial_approx": 84,
        "ring_signs_traces_or_probable_approx": 35,
        "status": "longest known Linear A inscription; NO numerals at all on the Ring.",
    },
    "layout_public": {
        "Face A": "left half = 12 quadruped metopes (all facing left; iconography DEFERRED). "
                  "right half = 16 preserved + >=18 originally present signs, one per metope; "
                  ">=10 engraved vases, some with syllabogram in ligature (VAS+PA, VAS+RU...); "
                  "6 amphora-type vases share a typology. NO phonetic sign-groups on Face A.",
        "Face B": "6 well-preserved 'perfectly recognizable' sign-GROUPS + 3 logograms "
                  "(LB values GRA, prob. FAR, OLIV), each in own metope; no numbers/fractions. "
                  "Direction L->R judged from AB81(KU),AB40(WI),AB60(RA).",
        "Face C": ">=9 sign-groups + 5 textile logograms (differ by fringe count); one textile "
                  "ligatured with AB77(KA); >=40% surface damage. Direction L->R from "
                  "'AB60(RA),AB01(TA),AB81(KU)' [printed verbatim; note AB01 std = da].",
        "Face D": "long sequence of ~9 animal-hide signs (AB180), each in a metope; extremely "
                  "damaged; a ligatured sign restorable as upper part of AB77(KA)/AB78(QE)/AB70(KO).",
        "Handle alpha": "2 probable vases each ligatured with a phonetic sign; sign for ten; then "
                        "a PROBABLE NEW Linear A sign; then Hieroglyphic *180 and *181.",
        "Handle beta": "at right end a SEQUENCE OF FOUR SIGNS (only first doubtful/damaged); left "
                       "half likely an animal-hide sign.",
        "Handle gamma": "signs for a boar and probably a pig; no numerals.",
        "Handle delta": "2 vases with ligatured sign above, followed by units and fractions; a "
                        "SEQUENCE OF SIX DIFFERENT FRACTION SIGNS with a new relative-value order.",
    },
    "signs_individually_printed_public": {
        "comparanda_to_KN_Zf31": ["AB60(RA)", "AB28(I)", "AB24(NE)", "AB09(SE)"],
        "direction_indicator": "A664 'rhyton' (cf. PH 8a.3, faces right)",
        "repeated_calligraphic_on_ring": ["AB08(A)", "AB81(KU)", "AB07(DI)", "AB77(KA)"],
        "cross_carrier_ligature": "AB08+AB77 (A+KA) on BOTH Ring and handle, stacked oppositely "
                                  "(two hands)",
        "other_printed": ["AB40(WI)", "'AB01(TA)'[printed thus]", "GRA/FAR/OLIV logograms",
                          "5 textile logograms", "AB180 hide ideogram",
                          "Hieroglyphic *180/*181 in LA use", "one probable NEW LA sign"],
    },
    "interpretations_public": [
        "KN Zg 57 = ritual/religious scepter (Kanta); Ring = calligraphic display text, NO numerals.",
        "KN Zg 58 = accounting text (numerals + fractions).",
        "Genre: Knossos Cult Center ('Fetish Shrine' / Neopalatial Room 1, Ivory Repository).",
        "Authors' caution: 'few parallels of the sign-groups on the Ring with sign-groups on "
        "extant Linear A texts'.",
    ],
    "NOT_public_in_overview": "No transliterated sign SEQUENCE of any length is printed anywhere. "
        "All sign-group content is deferred to Anetaki II (forthcoming).",
}

# ---- The unseen final-edition delta (what Anetaki II will FIRST reveal) ----
UNSEEN_DELTA = [
    "Transliteration of the 6 'perfectly recognizable' Face-B sign-groups (with certainty marks).",
    "Transliteration of the >=9 Face-C sign-groups.",
    "Transliteration of the Handle Face-beta FOUR-sign sequence.",
    "Handle Face-alpha ligature readings + identity of the probable NEW Linear A sign.",
    "The Face-delta SIX fraction signs in sequence and their relative-value ordering.",
    "Full Face-A syllabogram inventory (the 16-18 metope signs) beyond the comparanda list, "
    "and the VAS+X ligature resolutions.",
    "Face-D restoration of the ~9 hide-sequence signs and the AB77/78/70 ligature choice.",
    "Final CORRECTED sign readings (e.g. resolution of the printed 'AB01(TA)' vs standard da), "
    "final sign order, joins/corrections, damaged-sign restorations.",
    "Final layout/reading order per face; new photographs, drawings, 3D.",
    "Any editorial identification of groups as NAMES / TOPONYMS / FORMULA words (with confidence).",
    "Edition-specific contextual revisions (dating, findspot, object function).",
]

# ---- What must be EXCLUDED from prospective scoring (already public -> not held out) ----
EXCLUSIONS = [
    "Object identity, carrier count (2: KN Zg 57 ring + KN Zg 58 handle), and provenance "
    "(Anetaki Cult Center) — public.",
    "Approximate length (~119 Ring signs; ~84 preserved) and 'longest LA inscription' — public.",
    "Genre split: Ring = display/cult (no numerals); handle = accounting (numerals+fractions) — public.",
    "Face-level LAYOUT skeleton: which faces carry sign-groups vs logograms vs metopes, and the "
    "COUNTS (6 Face-B groups; >=9 Face-C; 4-sign Face-beta; 6 fractions Face-delta; ~9 Face-D hides; "
    "12 Face-A quadrupeds) — public. A prospective test may NOT be scored for 'predicting' these counts.",
    "Every INDIVIDUALLY-printed sign / comparandum: A, KU, DI, KA (repeated), RA, I, NE, SE, WI, "
    "'TA'(AB01 as printed), the A+KA ligature, GRA/FAR/OLIV & textile & AB180 logograms, "
    "Hieroglyphic *180/*181, the A664 rhyton, the probable-new-sign EXISTENCE — public. "
    "These signs cannot count as blind recovery.",
    "Directionality per face (L->R on B and C) — public.",
    "The existence/positions of the six-fraction sequence and its 'new ordering' claim — public "
    "(the VALUES/order themselves are the held-out delta).",
    "Any reading already committed by the fringe/prediction registry (Rjabchikov's 15 photo-derived "
    "values; Chiapello's two predictions) — these are graded AS external claims, and a logos "
    "candidate may not launder them as its own recovery.",
]

SCOREABLE_PROSPECTIVE = (
    "ONLY the currently-UNPUBLISHED transliterated sign-group content and its held-out attributes: "
    "the actual sign VALUES of the 6 Face-B groups, >=9 Face-C groups, the 4-sign Face-beta sequence, "
    "the Face-alpha ligatures + new-sign identity, and the six fraction VALUES/ordering — none of "
    "which is public as of the as_of date. A blind reading is scored against THESE, not against the "
    "public metadata above. Do NOT claim the whole inscription is prospectively sealed."
)

payload = {
    "task": "J1_ANETAKI_PUBLIC_EXPOSURE_AUDIT",
    "as_of": "2026-07-07",
    "seed": 20260708,
    "web_leg": {
        "web_available": True,
        "webfetch_greekreporter": "HTTP_403 (popular-press block); snippet-level only",
        "finding": "No public source (scholarly OR popular) carries a transliterated sign-group "
                   "sequence from KN Zg 57 or KN Zg 58. Anetaki II confirmed still UNPUBLISHED "
                   "as of 2026-07-07. New event surfaced: Kanta & Charitos, June-2025 conference "
                   "talk 'Knossos Anetaki plot: The Neopalatial Room 1 and its Ivory Repository' "
                   "(a talk, no transliteration).",
    },
    "sources": SOURCES,
    "already_public": ALREADY_PUBLIC,
    "unseen_final_edition_delta": UNSEEN_DELTA,
    "excluded_from_prospective_scoring": EXCLUSIONS,
    "scoreable_prospective_payload": SCOREABLE_PROSPECTIVE,
    "seal_link": "experiments/linear_a_foundry/manifests/SEAL_5_prospective_gold_anetaki_II.json "
                 "(status NO_CANDIDATE_TO_SEAL; commitment_sha256 "
                 "9e412e55883e83b42262b9829103e4e84ebf74ae114d4ceb0dc100ff41425885).",
    "non_circular_note": "Audit records only public metadata + source hashes; no held-out label "
                         "read, no model run, no known Linear A value used as a model input.",
    "counts": {
        "sources_used": len(SOURCES),
        "primary_epigraphic_sources": 1,
        "registry_quarantine_sources": 2,
        "public_sign_groups_transliterated": 0,
        "unseen_delta_items": len(UNSEEN_DELTA),
        "exclusion_items": len(EXCLUSIONS),
        "ring_signs_total_approx": 119,
    },
}

out = os.path.join(DATA, "J1_exposure.json")
with open(out, "w") as f:
    json.dump(payload, f, indent=2, ensure_ascii=False)
print("wrote", out)
print("web_capture_sha256", SOURCES[-1]["sha256_of_captured_artifact"])
print("counts", json.dumps(payload["counts"]))
