#!/usr/bin/env python3
"""§V LA ritual candidate inventory — INTERNAL EVIDENCE ONLY (packet A; no LB, no similarity).

Generation is BLIND: the frozen slot classifier's RITUAL_FORMULA class (ritual-support context +
internal recurrence), rendered to raw GORILA IDs. NEVER reads LB forms, the known-pair ledger, phonetic
values for selection, or any match score. A one-directional quarantine then moves KNOWN ritual forms
out of the confirmatory partitions into KNOWN_PAIR_DEVELOPMENT (it can only remove, never add/retier a
PRIMARY_RITUAL/SENSITIVITY_RITUAL member). Unit = unique form.
"""
import copy, json, os, sys
from collections import Counter

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "external_anchors", "src", "slot_classifier"))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "la_lb_continuity", "src", "common"))
import slotlib  # noqa: E402  (inherited, UNMODIFIED)
import syllabary as syl  # noqa: E402

FREEZE_VERSION = "la-ritual-v1-2026-07-06"
CHANNEL = {"channel_origin": "POSTHOC_GENRE_REDIRECT", "channel_class": "EXPLORATORY_POSTHOC_CHANNEL"}
# known ritual/localized forms (+ PA-I-TO admin comparison) — used ONLY by the quarantine filter
KNOWN_FORMS = {("TU", "RU", "SA"), ("I", "DA"), ("SE", "TO", "I", "JA"), ("DI", "KI", "TA"), ("PA", "I", "TO")}


def build():
    D, idx = slotlib.load_corpus()
    _, gold = slotlib.build_records(D, idx)
    per = {r["id"]: r.get("context", "") for r in D}
    rit = [g for g in gold if g["candidate_class"] == "RITUAL_FORMULA"]
    prim = [g for g in rit if g["class_probability_or_tier"] == "B"]
    sens = [g for g in rit if g["class_probability_or_tier"] == "C"]
    prim_ids = {g["candidate_id"] for g in prim}
    # negative controls: non-ritual, non-damaged, length-matched to PRIMARY_RITUAL
    pool = [g for g in gold if g["candidate_class"] != "RITUAL_FORMULA" and not g["damaged_sign_flag"]
            and g["context_features"]["len_signs"] >= 2]
    import random
    rng = random.Random(20260706)
    chosen, used = [], set()
    for p in sorted(prim, key=lambda g: g["candidate_id"]):
        L = p["context_features"]["len_signs"]
        ranked = sorted((g for g in pool if g["candidate_id"] not in used),
                        key=lambda g: (abs(g["context_features"]["len_signs"] - L), g["candidate_id"]))
        for g in ranked[:2]:
            used.add(g["candidate_id"]); chosen.append(g)
    neg_ids = {g["candidate_id"] for g in chosen}

    def part(g):
        if g["candidate_id"] in prim_ids: return "PRIMARY_RITUAL"
        if g["candidate_id"] in neg_ids: return "NEGATIVE_CONTROL"
        if g["candidate_class"] == "RITUAL_FORMULA": return "SENSITIVITY_RITUAL"
        return None

    keep = [g for g in gold if part(g) is not None]
    packet, manifest = [], []
    for g in sorted(keep, key=lambda x: x["candidate_id"]):
        cf, pf = g["context_features"], g["position_features"]
        word = g["normalized_string_id"].split("-")
        raw = syl.render(word)
        rec = {
            **CHANNEL,
            "la_ritual_id": g["candidate_id"],
            "raw_sign_sequence": raw, "n_signs": len(raw),
            "source_documents": g["document_id"], "recurrence_count": cf["occ"],
            "object_type": g["genre"], "site": g["site"],
            "date_range": sorted({per.get(d, "") for d in g["document_id"] if per.get(d, "")}) or ["unknown"],
            "ritual_context": {"ritual_genre_rate": cf["ritual_genre_rate"], "header_rate": pf["header_rate"]},
            "formula_position": {"header_rate": pf["header_rate"], "pre_num_rate": pf["pre_num_rate"]},
            "unique_form_id": g["normalized_string_id"],
            "single_site_cluster": cf["n_docs"] > 1 and cf["n_sites"] == 1,
            "cross_site_attestation": cf["n_sites"] >= 2,
            "n_sites": cf["n_sites"], "n_docs": cf["n_docs"],
            "transcription_status": g["transcription_status"], "damaged_sign_flag": g["damaged_sign_flag"],
            "composite_sensitive": any(not r.startswith("AB") for r in raw),
            "alternative_transcriptions": [],
            "internal_selection_rule": "slot RITUAL_FORMULA (ritual-support context + recurrence); "
                                       "internal-only",
            "confidence_tier": g["class_probability_or_tier"],
            "known_pair_overlap": False,
            "development_or_evaluation_role": "EVALUATION_CANDIDATE",
            "confirmatory_eligibility": "ELIGIBLE_PENDING_FREEZE",
            "base_partition": part(g),
            "freeze_version": FREEZE_VERSION,
        }
        packet.append(rec); manifest.append({**rec, "_phonetic_word": word})
    return manifest, packet


def known_forms():
    return KNOWN_FORMS


def apply_known_pair_quarantine(manifest, packet, known):
    """ONE-DIRECTIONAL: move a KNOWN ritual form out of PRIMARY_RITUAL/SENSITIVITY_RITUAL into
    KNOWN_PAIR_DEVELOPMENT + CONFIRMATORY_INELIGIBLE. Never adds/retiers a confirmatory candidate."""
    n = 0
    for m, p in zip(manifest, packet):
        if tuple(m["_phonetic_word"]) in known and p["base_partition"] in ("PRIMARY_RITUAL", "SENSITIVITY_RITUAL"):
            for r in (m, p):
                r["base_partition"] = "KNOWN_PAIR_DEVELOPMENT"
                r["known_pair_overlap"] = True
                r["confirmatory_eligibility"] = "CONFIRMATORY_INELIGIBLE"
                r["development_or_evaluation_role"] = "KNOWN_PAIR_DEVELOPMENT"
            n += 1
    return n


def main():
    out = os.path.normpath(os.path.join(HERE, "..", "..", "data", "gold")); os.makedirs(out, exist_ok=True)
    manifest, packet = build()
    nq = apply_known_pair_quarantine(manifest, packet, known_forms())
    with open(os.path.join(out, "la_ritual_candidate_manifest.jsonl"), "w", encoding="utf-8") as f:
        for r in manifest: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(os.path.join(out, "la_ritual_candidate_packet.jsonl"), "w", encoding="utf-8") as f:
        for r in packet: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    c = Counter(r["base_partition"] for r in packet)
    prim = [r for r in packet if r["base_partition"] == "PRIMARY_RITUAL"]
    eff_indep = sum(1 for r in prim if r["cross_site_attestation"])
    print(f"freeze {FREEZE_VERSION}: {len(packet)} candidates  (quarantined {nq} known ritual form(s))")
    print(f"  {dict(c)}")
    print(f"  PRIMARY_RITUAL cross-site-independent: {eff_indep}/{len(prim)}; "
          f"single-site clusters in PRIMARY: {sum(1 for r in prim if r['single_site_cluster'])}")
    print(f"  PRIMARY length dist: {dict(sorted(Counter(r['n_signs'] for r in prim).items()))}")


if __name__ == "__main__":
    main()
