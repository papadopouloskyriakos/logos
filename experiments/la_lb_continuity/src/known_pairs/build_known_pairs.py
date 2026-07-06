#!/usr/bin/env python3
"""§VI — source-critical audit of the five known LA↔LB persistence pairs (+ 2 speculative morphological).

These pairs are ALREADY PUBLIC (Salgarella 2025 lecture; Younger; Davis). They are therefore
DEVELOPMENT_BENCHMARK material — pipeline debugging + positive-control behaviour — and NEVER untouched
confirmatory evidence. This ledger is QUARANTINED: the §VII candidate build and §VIII target build must
not read it (enforced by leakage tests). It is the only artifact that pairs LA and LB (permitted here
because the pairing is pre-existing public knowledge, not a discovery of this project).

LA attestation is read from the pinned silver corpus; LB-side facts are hardcoded from LB scholarship
with per-item confidence + citation. Output: data/quarantine/known_persistence_pairs.jsonl (quarantined).
"""
import json, os, sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "sigla_reconcile"))
import syllabary as syl  # noqa: E402
import config  # noqa: E402

_RITUAL_SUPPORTS = {"Stone vessel", "Clay vessel", "Metal object", "Stone object", "Libation Table",
                    "Libation table"}

# LB-side, from LB scholarship — selected on LB merits, independent of the LA form.
LB = {
    "pa-i-to":    dict(entity="Phaistos", conf=0.95, site="Knossos", period="LM II-IIIA",
                       cite="Chadwick, Documents² s.v.; KN Da/Db/Ga; secure"),
    "tu-ri-so":   dict(entity="Tylissos", conf=0.90, site="Knossos", period="LM II-IIIA",
                       cite="Chadwick, Documents²; KN toponym; secure"),
    "di-ka-ta":   dict(entity="Mt Dikte / Diktaian", conf=0.85, site="Knossos", period="LM II-IIIA",
                       cite="KN Fp 1 di-ka-ta-jo di-we 'to Diktaian Zeus'; religious toponym"),
    "i-da":       dict(entity="Mt Ida / Idaian (i-da-i-jo)", conf=0.55, site="Knossos", period="LM II-IIIA",
                       cite="proposed via i-da-i-jo 'Idaian'; identification debated"),
    "se-to-i-ja": dict(entity="Seteia district", conf=0.70, site="Knossos", period="LM II-IIIA",
                       cite="Chadwick; Bennet 1985 (KN district); location debated"),
}
# LA candidate form -> which LB target it is paired with in the literature
PAIRS = [
    ("PA-I-TO",    ("PA", "I", "TO"),      "pa-i-to",    "Younger; Salgarella 2025 lecture"),
    ("TU-RU-SA",   ("TU", "RU", "SA"),     "tu-ri-so",   "Salgarella 2025 lecture (LA tu-ru-sa ~ LB tu-ri-so)"),
    ("DI-KI-TA",   ("DI", "KI", "TA"),     "di-ka-ta",   "Salgarella 2025 lecture (Mt Dikte)"),
    ("I-DA",       ("I", "DA"),            "i-da",       "Salgarella 2025 lecture (Mt Ida)"),
    ("SE-TO-I-JA", ("SE", "TO", "I", "JA"), "se-to-i-ja", "Salgarella 2025 lecture (near-identical spelling)"),
]
SPECULATIVE = [
    ("DI-DE-RU", ("DI", "DE", "RU"), "di-de-ro", "Salgarella lecture — personal name + Greek -os; MORPHOLOGICAL, quarantined"),
    ("PA-JE-RE", ("PA", "JE", "RE"), "pa-je-ro", "Salgarella lecture — personal name + Greek -os; MORPHOLOGICAL, quarantined"),
]


def la_attestation(D, seq):
    recs = []
    for r in D:
        if tuple(seq) in [tuple(w) for w in r.get("words", [])]:
            recs.append((r["id"], r.get("site", ""), r.get("context", ""), r.get("support", "")))
    return recs


def context_kind(recs):
    if not recs:
        return "absent"
    ritual = sum(1 for _, _, _, sup in recs if sup in _RITUAL_SUPPORTS)
    return "ritual" if ritual > len(recs) / 2 else ("administrative" if ritual == 0 else "mixed")


def build():
    D = json.load(open(config.SILVER, encoding="utf-8"))
    rows = []
    for pairs, kind_default in ((PAIRS, "known"), (SPECULATIVE, "speculative")):
        for la_form, seq, lb_translit, prov in pairs:
            recs = la_attestation(D, seq)
            ck = context_kind(recs)
            sites = sorted({s for _, s, _, _ in recs})
            periods = sorted({c for _, _, c, _ in recs if c})
            lb = LB.get(lb_translit, dict(entity="(speculative morphological counterpart)", conf=0.2,
                                          site="", period="", cite=prov))
            absent = len(recs) == 0
            short = len(seq) <= 2
            single = len(recs) == 1
            if kind_default == "speculative":
                cls = "SPECULATIVE_MORPHOLOGICAL_CONTINUITY"
            elif absent:
                cls = "CONFIRMATORY_INELIGIBLE"     # LA form not attested in silver at all
            else:
                cls = "DEVELOPMENT_BENCHMARK"        # already public -> not confirmatory
            rows.append({
                "pair_id": f"KP-{la_form}",
                "linear_a_form": la_form,
                "linear_a_raw_sign_sequence": syl.render(list(seq)),
                "linear_a_phonetic_tokens": list(seq),
                "linear_a_source_documents": [r[0] for r in recs],
                "linear_a_site": sites,
                "linear_a_date_range": periods or ["unknown"],
                "linear_a_context": ck,
                "linear_a_internal_slot_class_expected": (
                    "n/a (absent)" if absent else
                    "RITUAL_FORMULA (not administrative TOPONYM_LIKE)" if ck == "ritual" else
                    "TOPONYM_LIKE-eligible" if ck == "administrative" else "mixed"),
                "linear_b_form": lb_translit,
                "linear_b_raw_sign_sequence": syl.lb_sequence(lb_translit),
                "linear_b_entity_identification": lb["entity"],
                "linear_b_identification_confidence": lb["conf"],
                "linear_b_site": lb["site"], "linear_b_date_range": lb["period"],
                "source_citation": prov, "linear_b_citation": lb["cite"],
                "pair_first_proposed_by": prov.split(";")[0],
                "selection_history": "observed in the Salgarella 2025 lecture audit before this pass began",
                "phonetic_values_used_in_original_identification": True,
                "la_candidate_selected_without_lb_reading": False,   # historically selected WITH the LB reading
                "lb_entity_identification_independent": lb["conf"] >= 0.7,
                "same_source_dependency": "LA(GORILA/silver) vs LB(KN tablets) — different corpora",
                "posthoc_discovery_risk": "HIGH — motivating example, known before selection",
                "flags": [f for f, on in (("absent_in_silver", absent), ("short_seq_high_coincidence", short),
                                          ("single_attestation", single), ("ritual_context_not_admin", ck == "ritual"))
                          if on],
                "confirmatory_eligibility": cls,
            })
    return rows


def main():
    out = os.path.join(os.path.dirname(__file__), "..", "..", "data", "quarantine")
    out = os.path.normpath(out); os.makedirs(out, exist_ok=True)
    rows = build()
    path = os.path.join(out, "known_persistence_pairs.jsonl")
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    cc = Counter(r["confirmatory_eligibility"] for r in rows)
    print("known/speculative pairs:", len(rows), "->", dict(cc))
    for r in rows:
        print(f"  {r['linear_a_form']:11} att={len(r['linear_a_source_documents'])} ctx={r['linear_a_context']:14} "
              f"-> {r['linear_b_form']:10} ({r['linear_b_entity_identification']}, conf {r['linear_b_identification_confidence']}) "
              f"[{r['confirmatory_eligibility']}] {r['flags']}")
    print("wrote (quarantined):", path)


if __name__ == "__main__":
    main()
