#!/usr/bin/env python3
"""§VI LB ritual target inventory — INDEPENDENT of Linear A (packet B; no LA, no similarity).

LB religious/ritual vocabulary selected from LB scholarship + Knossos/Pylos cult series (Fp/Fs/Gg/V;
Gulizio; Weilhartner; Chadwick, Documents²) and verified as real DĀMOS wordforms — never by resemblance
to any LA form. This module reads no LA candidate/slot/silver (enforced by test). No similarity computed.
The LB forms of the known ritual-context pairs are quarantined to KNOWN_PAIR_DEVELOPMENT.
"""
import json, os, sys
from collections import Counter

HERE = os.path.dirname(__file__)
MAIN = os.environ.get("LOGOS_MAIN", "/home/claude-runner/gitlab/n8n/logos")
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "la_lb_continuity", "src", "common"))
sys.path.insert(0, os.path.join(MAIN, "scripts", "cross_script"))
import syllabary as syl  # noqa: E402

FREEZE_VERSION = "lb-ritual-v1-2026-07-06"
CHANNEL = {"channel_origin": "POSTHOC_GENRE_REDIRECT", "channel_class": "EXPLORATORY_POSTHOC_CHANNEL"}

# (translit, gloss, semantic_class, confidence, role, cite)
D, E, N, K = "DEVELOPMENT_TARGETS", "EVALUATION_TARGETS", "NEGATIVE_CONTROL_TARGETS", "KNOWN_PAIR_DEVELOPMENT"
TARGETS = [
    ("te-o-jo",       "of the god",           "OFFERING_TERM", 0.90, D, "Chadwick; very frequent"),
    ("do-so-mo",      "offering/contribution","OFFERING_TERM", 0.85, D, "Chadwick"),
    ("po-ti-ni-ja",   "Potnia (the Lady)",    "DIVINE_NAME",   0.90, D, "Gulizio; Chadwick"),
    ("i-je-re-ja",    "priestess",            "CULT_TITLE",    0.90, D, "Chadwick"),
    ("di-we",         "Zeus (dat.)",          "DIVINE_NAME",   0.85, E, "KN Fp 1; Gulizio"),
    ("di-wi-ja",      "Diwia (goddess)",      "DIVINE_NAME",   0.70, E, "Gulizio"),
    ("e-ma-a2",       "Hermes",               "DIVINE_NAME",   0.80, E, "Gulizio"),
    ("pa-ja-wo-ne",   "Paiawon (Paian)",      "DIVINE_NAME",   0.70, E, "Gulizio"),
    ("e-nu-wa-ri-jo", "Enyalios",             "DIVINE_NAME",   0.70, E, "Gulizio"),
    ("pa-de",         "Pade (Cretan deity)",  "DIVINE_NAME",   0.65, E, "KN cult; Gulizio"),
    ("qe-ra-si-ja",   "Qerasija (goddess)",   "DIVINE_NAME",   0.65, E, "KN Fp; Gulizio"),
    ("a-ne-mo",       "Winds (cult of)",      "DIVINE_NAME",   0.60, E, "KN Fp 1; wind cult"),
    ("i-je-re-u",     "priest",               "CULT_TITLE",    0.85, E, "Chadwick"),
    ("ka-ra-wi-po-ro","key-bearer (cult)",    "CULT_TITLE",    0.80, E, "Chadwick"),
    ("i-je-ro",       "sacred",               "RITUAL_TERM",   0.80, E, "Chadwick"),
    ("pa-si-te-o-i",  "to all the gods",      "OFFERING_TERM", 0.85, E, "KN Fp 1; Weilhartner"),
    ("qe-te-o",       "to be paid/offered",   "RITUAL_TERM",   0.70, E, "Chadwick; Weilhartner"),
    ("te-o",          "god",                  "DIVINE_NAME",   0.80, E, "Chadwick"),
    ("pa-ki-ja-ne",   "Sphagianes (sanctuary)","SANCTUARY",    0.75, E, "PY; sanctuary district"),
    # known ritual-context pairs' LB forms — QUARANTINED
    ("tu-ri-so",      "Tylissos",             "TOPONYM",       0.85, K, "known-pair LB form (TU-RU-SA)"),
    ("i-da-i-jo",     "Idaian",               "TOPONYM",       0.55, K, "known-pair LB form (I-DA)"),
    ("se-to-i-ja",    "Seteia",               "TOPONYM",       0.70, K, "known-pair LB form (SE-TO-I-JA)"),
    ("di-ka-ta-jo",   "Diktaian",             "TOPONYM",       0.80, K, "known-pair LB form (DI-KI-TA)"),
    # non-ritual controls
    ("wa-na-ka",      "king",                 "NON_RITUAL",    0.95, N, "Chadwick"),
    ("ko-wo",         "boy/son",              "NON_RITUAL",    0.90, N, "Chadwick"),
    ("ka-ko",         "bronze",               "NON_RITUAL",    0.90, N, "Chadwick"),
    ("po-me",         "shepherd",             "NON_RITUAL",    0.90, N, "Chadwick"),
    ("a-ko-ro",       "field/estate",         "NON_RITUAL",    0.80, N, "Chadwick"),
    ("ki-ri-ta",      "barley",               "NON_RITUAL",    0.80, N, "Chadwick"),
]


def damos_counts():
    import data as X
    return Counter(tuple(w) for w in X.load_b_damos()[0])


def build():
    wc = damos_counts()
    rows = []
    for translit, gloss, sclass, conf, role, cite in TARGETS:
        seq_u = tuple(s.upper() for s in translit.split("-"))
        rows.append({
            **CHANNEL,
            "lb_ritual_id": "LB-RIT-" + translit.replace("-", "_"),
            "raw_sign_sequence": syl.lb_sequence(translit),
            "standard_transliteration": translit,
            "gloss_or_entity": gloss, "semantic_class": sclass,
            "identification_confidence": conf,
            "documents": "DĀMOS attestations (see damos_attestation)",
            "site": "Knossos/Pylos cult series", "date_range": "LM II-IIIA / LH IIIB",
            "ritual_context": sclass,
            "damos_attestation": wc.get(seq_u, 0),
            "source_citations": cite,
            "unique_form_id": translit,
            "single_site_cluster": False, "cross_site_attestation": wc.get(seq_u, 0) >= 3,
            "known_pair_overlap": role == K,
            "development_or_evaluation_role": role,
            "confirmatory_eligibility": "CONFIRMATORY_INELIGIBLE" if role == K else "ELIGIBLE_PENDING_FREEZE",
            "freeze_version": FREEZE_VERSION,
        })
    return rows


def main():
    out = os.path.normpath(os.path.join(HERE, "..", "..", "data", "gold")); os.makedirs(out, exist_ok=True)
    rows = build()
    path = os.path.join(out, "lb_ritual_target_packet.jsonl")
    with open(path, "w", encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    role = Counter(r["development_or_evaluation_role"] for r in rows)
    unatt = [r["standard_transliteration"] for r in rows if r["damos_attestation"] == 0]
    print(f"freeze {FREEZE_VERSION}: {len(rows)} targets {dict(role)}")
    print(f"  DĀMOS-attested {sum(1 for r in rows if r['damos_attestation']>0)}/{len(rows)}; unattested {unatt}")
    print(f"  EVALUATION religious targets: {role[E]}  (independent of LA)")


if __name__ == "__main__":
    main()
