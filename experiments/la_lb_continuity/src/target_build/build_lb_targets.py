#!/usr/bin/env python3
"""§VIII — independent Linear B Cretan-toponym TARGET manifest (packet B).

Targets are selected by LB scholarship + Knossos administrative context (the canonical KN toponym
list: Bennet 1985; Chadwick, Documents²; Del Freo) and verified as real DĀMOS wordforms — NEVER by
resemblance to any Linear A candidate. This module does NOT read the LA candidate manifest (enforced
by test_lb_target_independence). No matching, no similarity is computed.

DEVELOPMENT_TARGETS = LB forms of the five known pairs (debug/positive-control only; not generalization).
EVALUATION_TARGETS  = independently-identified KN Cretan toponyms not in the five.
NEGATIVE_CONTROL_TARGETS = established LB non-toponyms (titles/commodities/function words), length-matched.

Output: data/gold/lb_toponym_target_manifest.jsonl (packet B — committed; raw sign sequence +
conventional transliteration + entity id + sources; NO LA candidates, NO similarity).
"""
import argparse, json, os, sys
from collections import Counter

HERE = os.path.dirname(__file__)
MAIN = os.environ.get("LOGOS_MAIN", "/home/claude-runner/gitlab/n8n/logos")
sys.path.insert(0, os.path.join(HERE, "..", "common"))
sys.path.insert(0, os.path.join(MAIN, "scripts", "cross_script"))   # main's DĀMOS loader (ROOT=main)
import syllabary as syl  # noqa: E402

FREEZE_VERSION = "lb-targets-v1-2026-07-06"
DAMOS_ITEMS = "/home/claude-runner/gitlab/n8n/logos/corpus/bronze/linearb/damos/items.jsonl"

# (translit, entity, id_confidence, role, in_known_five, citation, attest_site, chronology)
KN = "Knossos (KN archive)"; KH = "Khania (KH archive)"; ERA = "LM II-IIIA"
TARGETS = [
    # DEVELOPMENT — LB forms of the five known pairs (positive-control/debug ONLY)
    ("pa-i-to",     "Phaistos",            0.95, "DEVELOPMENT", True,  "Chadwick Documents²; KN Da/Db/Ga", KN, ERA),
    ("tu-ri-so",    "Tylissos",            0.85, "DEVELOPMENT", True,  "Chadwick; Bennet 1985", KN, ERA),
    ("se-to-i-ja",  "Seteia district",     0.70, "DEVELOPMENT", True,  "Bennet 1985 (KN district)", KN, ERA),
    ("di-ka-ta-de", "Mt Dikte (Diktaian, allative)", 0.80, "DEVELOPMENT", True, "KN Fp 1 di-ka-ta-jo di-we; bare di-ka-ta unattested", KN, ERA),
    ("i-da-i-jo",   "Mt Ida (Idaian, adj.)", 0.55, "DEVELOPMENT", True, "adjective; bare i-da unattested; identification debated", KN, ERA),
    # EVALUATION — independently-identified KN Cretan toponyms NOT in the five
    ("a-mi-ni-so",  "Amnisos (harbour of Knossos)", 0.90, "EVALUATION", False, "Chadwick; secure", KN, ERA),
    ("ku-do-ni-ja", "Kydonia / Chania",    0.90, "EVALUATION", False, "Chadwick; KH + KN; secure", KH, "LM IIIB"),
    ("ko-no-so",    "Knossos",             0.95, "EVALUATION", False, "the capital; secure", KN, ERA),
    ("ru-ki-to",    "Lyktos",              0.85, "EVALUATION", False, "Bennet 1985; major KN toponym", KN, ERA),
    ("ku-ta-to",    "Kytaion",             0.60, "EVALUATION", False, "major KN toponym; location debated", KN, ERA),
    ("e-ko-so",     "Axos (Oaxos)",        0.60, "EVALUATION", False, "Bennet 1985; probable", KN, ERA),
    ("da-wo",       "Dawos (Mesara)",      0.60, "EVALUATION", False, "large grain toponym; probable", KN, ERA),
    ("su-ki-ri-ta", "Sybrita",             0.70, "EVALUATION", False, "probable", KN, ERA),
    ("ra-su-to",    "Lasynthos (?)",       0.50, "EVALUATION", False, "KN toponym; identification uncertain", KN, ERA),
    ("ti-ri-to",    "Trit(t)os (?)",       0.50, "EVALUATION", False, "KN toponym; uncertain", KN, ERA),
    ("ri-jo-no",    "Rhion (?)",           0.50, "EVALUATION", False, "KN toponym; uncertain", KN, ERA),
    ("qa-ra",       "Wala/Bala (?)",       0.45, "EVALUATION", False, "KN toponym; uncertain", KN, ERA),
    ("u-ta-no",     "Utanos (?)",          0.50, "EVALUATION", False, "KN toponym; uncertain", KN, ERA),
    ("ra-ja",       "Raia (?)",            0.50, "EVALUATION", False, "KN toponym; uncertain", KN, ERA),
    ("a-pa-ta-wa",  "Aptara / Aptera (W. Crete)", 0.70, "EVALUATION", False, "West-Cretan toponym", KH, "LM IIIB"),
    ("da-*22-to",   "Da-?-to (major KN toponym; *22 undeciphered)", 0.50, "EVALUATION", False, "major KN toponym; *22 unread", KN, ERA),
    # NEGATIVE CONTROL — established LB NON-toponyms (length-matched)
    ("do-e-ro",     "'slave' (title)",     0.95, "NEGATIVE_CONTROL", False, "Chadwick; common LB word", KN, ERA),
    ("i-je-re-ja",  "'priestess' (title)", 0.95, "NEGATIVE_CONTROL", False, "Chadwick", KN, ERA),
    ("wa-na-ka",    "'king' (title)",      0.95, "NEGATIVE_CONTROL", False, "Chadwick", KN, ERA),
    ("ka-ko",       "'bronze' (commodity)", 0.90, "NEGATIVE_CONTROL", False, "Chadwick", KN, ERA),
    ("to-so",       "'so much' (function)", 0.95, "NEGATIVE_CONTROL", False, "Chadwick", KN, ERA),
    ("po-me",       "'shepherd' (title)",  0.90, "NEGATIVE_CONTROL", False, "Chadwick", KN, ERA),
    ("ko-wo",       "'boy/son' (kin term)", 0.90, "NEGATIVE_CONTROL", False, "Chadwick", KN, ERA),
    ("pa-ro",       "'beside/from' (prep.)", 0.95, "NEGATIVE_CONTROL", False, "Chadwick", KN, ERA),
    ("pe-mo",       "'seed' (commodity)",  0.90, "NEGATIVE_CONTROL", False, "Chadwick", KN, ERA),
    ("do-so-mo",    "'contribution'",      0.90, "NEGATIVE_CONTROL", False, "Chadwick", KN, ERA),
    ("ka-ke-we",    "'smiths' (title)",    0.90, "NEGATIVE_CONTROL", False, "Chadwick", KN, ERA),
    ("te-o-jo",     "'of god' (function)", 0.90, "NEGATIVE_CONTROL", False, "Chadwick", KN, ERA),
]


def damos_counts():
    """LB wordform frequencies via the project's canonical DĀMOS loader (parity with corpus figures)."""
    import data as X
    return Counter(tuple(w) for w in X.load_b_damos()[0])


def build():
    wc = damos_counts()
    rows = []
    for translit, entity, conf, role, known5, cite, site, chrono in TARGETS:
        seq_upper = tuple(s.upper() for s in translit.split("-"))
        rows.append({
            "lb_target_id": "LB-TOPO-%s" % translit.replace("-", "_").replace("*", "s"),
            "raw_sign_sequence": syl.lb_sequence(translit),
            "standard_transliteration": translit,
            "entity_identification": entity,
            "identification_confidence": conf,
            "attestation_site": site,
            "date_range": chrono,
            "context": "Knossos-class administrative" if role != "NEGATIVE_CONTROL" else "administrative (non-toponym)",
            "damos_attestation": wc.get(seq_upper, 0),
            "source_citation": cite,
            "included_in_known_five": known5,
            "development_or_evaluation_role": role,
            "freeze_version": FREEZE_VERSION,
        })
    return rows


def main():
    out = os.path.normpath(os.path.join(HERE, "..", "..", "data", "gold")); os.makedirs(out, exist_ok=True)
    rows = build()
    path = os.path.join(out, "lb_toponym_target_manifest.jsonl")
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    role = Counter(r["development_or_evaluation_role"] for r in rows)
    unattested = [r["standard_transliteration"] for r in rows if r["damos_attestation"] == 0]
    print(f"freeze {FREEZE_VERSION}: {len(rows)} targets  {dict(role)}")
    print(f"  DĀMOS-attested: {sum(1 for r in rows if r['damos_attestation']>0)}/{len(rows)}; "
          f"unattested-as-bare-form: {unattested}")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
