#!/usr/bin/env python3
"""§VII — freeze the INTERNAL-ONLY Linear A candidate manifest (packet A).

Generation is BLIND: it runs the frozen slot classifier (internal LA distribution/position/recurrence
only) and NEVER reads the known-pair ledger, any LB target, projected phonetic values for selection,
or a match result. Enforced by test_la_candidate_leakage. Sign sequences are rendered to RAW SIGN IDs
(public Ventris numbering, notation only) so the review packet carries no phonetic transliteration
that would leak LA↔LB resemblance.

Sets: PRIMARY = tier-B TOPONYM_LIKE · SENSITIVITY_1 = tier-B + tier-C TOPONYM_LIKE ·
NEGATIVE_CONTROL = non-TOPONYM_LIKE forms matched to PRIMARY on length + frequency.
Splits: heldout_group = leave-one-site-out (from the classifier) · site_split · genre_split.

Outputs: data/gold/la_candidate_manifest.jsonl (internal, gitignored — keeps phonetic form for repro)
and data/gold/la_candidate_packet.jsonl (committed review packet A — RAW IDs, NO LB, NO similarity).
"""
import argparse, json, os, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "external_anchors", "src", "slot_classifier"))
sys.path.insert(0, os.path.join(HERE, "..", "common"))
sys.path.insert(0, os.path.join(HERE, "..", "sigla_reconcile"))
import slotlib  # noqa: E402  (inherited, UNMODIFIED frozen rules)
import syllabary as syl  # noqa: E402
import config  # noqa: E402

FREEZE_VERSION = "la-candidates-v1-2026-07-06"
NEG_CONTROL_PER_PRIMARY = 2
NEG_SEED = 20260706

# cross-source site notes (silver is internally consistent; these are alias/ambiguity annotations only,
# they do NOT change the classifier's within-silver n_sites/tier).
SITE_CANON = {"Malia": "Mallia", "Haghios Stehanos": "Haghios Stephanos"}
SITE_AMBIGUOUS = {"Arkhalkhori": "Arkalochori (silver) vs Arkhanes (SigLA) — cross-source disagreement"}
DOC_UNCERTAIN = ("(?)", "+", "<", ">")


def _periods(D_index, docs):
    ps = sorted({D_index.get(d, "") for d in docs if D_index.get(d, "")})
    return ps or ["unknown"]


def _doc_period_index(D):
    return {r["id"]: r.get("context", "") for r in D}


def build():
    D, idx = slotlib.load_corpus()
    silver_recs, gold = slotlib.build_records(D, idx)
    per = _doc_period_index(D)

    topo = [g for g in gold if g["candidate_class"] == "TOPONYM_LIKE"]
    primary = [g for g in topo if g["class_probability_or_tier"] == "B"]
    sensitivity = topo                                  # tier-B + tier-C TOPONYM_LIKE
    prim_ids = {g["candidate_id"] for g in primary}

    # negative controls: non-TOPONYM_LIKE, non-damaged, matched to PRIMARY on (len, occ)
    pool = [g for g in gold if g["candidate_class"] != "TOPONYM_LIKE"
            and not g["damaged_sign_flag"] and g["context_features"]["len_signs"] >= 2]
    chosen, used = [], set()
    for p in sorted(primary, key=lambda g: g["candidate_id"]):
        L, O = p["context_features"]["len_signs"], p["context_features"]["occ"]
        ranked = sorted((g for g in pool if g["candidate_id"] not in used),
                        key=lambda g: (abs(g["context_features"]["len_signs"] - L),
                                       abs(g["context_features"]["occ"] - O), g["candidate_id"]))
        for g in ranked[:NEG_CONTROL_PER_PRIMARY]:
            used.add(g["candidate_id"]); chosen.append(g)
    neg_ids = {g["candidate_id"] for g in chosen}

    def inclusion(g):
        if g["candidate_id"] in prim_ids: return "PRIMARY"
        if g["candidate_id"] in neg_ids: return "NEGATIVE_CONTROL"
        if g["candidate_class"] == "TOPONYM_LIKE": return "SENSITIVITY_1"
        return None

    keep = [g for g in gold if inclusion(g) is not None]
    manifest, packet = [], []
    for g in sorted(keep, key=lambda x: x["candidate_id"]):
        cf, pf = g["context_features"], g["position_features"]
        word = g["normalized_string_id"].split("-")
        raw = syl.render(word)
        site_raw = g["site"]
        composite_sensitive = any(not r.startswith("AB") for r in raw)   # A-series/unmapped: SigLA/silver differ
        join_uncertain = any(any(m in d for m in DOC_UNCERTAIN) for d in g["document_id"])
        flags = list(g["secondary_flags"])
        if cf["len_signs"] <= 2: flags.append("short_seq_high_coincidence")
        if cf["n_docs"] > 1 and cf["n_sites"] == 1: flags.append("single_site_possible_nonindependence")
        rec = {
            "candidate_id": g["candidate_id"],
            "raw_sign_ids": raw, "n_signs": len(raw),
            "documents": g["document_id"], "n_docs": cf["n_docs"],
            "site_raw": site_raw, "site_canonical": SITE_CANON.get(site_raw, site_raw),
            "site_ambiguity": SITE_AMBIGUOUS.get(site_raw),
            "chronology": _periods(per, g["document_id"]),
            "internal_context": {"occ": cf["occ"], "n_sites": cf["n_sites"], "n_docs": cf["n_docs"],
                                 "header_rate": pf["header_rate"], "pre_num_rate": pf["pre_num_rate"],
                                 "post_logo": pf["post_logo"], "ritual_genre_rate": cf["ritual_genre_rate"]},
            "classifier_class": g["candidate_class"], "tier": g["class_probability_or_tier"],
            "rule_version": slotlib.RULE_VERSION, "secondary_flags": flags,
            "uncertainty": {"damaged": g["damaged_sign_flag"], "transcription_status": g["transcription_status"],
                            "composite_sensitive": composite_sensitive, "join_or_uncertain_doc": join_uncertain},
            "inclusion_set": inclusion(g), "exclusion_reason": None,
            "heldout_group": g["heldout_group"],
            "site_split": SITE_CANON.get(site_raw, site_raw),
            "genre_split": g["genre"],
            "freeze_version": FREEZE_VERSION,
        }
        packet.append(rec)                              # RAW IDs, NO LB, NO similarity, NO phonetic
        manifest.append({**rec, "_phonetic_word": word})   # internal only (gitignored) for reproduction
    return manifest, packet


def known_la_forms():
    """LA phonetic word-tuples from the quarantined known-pair ledger. Used ONLY by the contamination
    filter below — NEVER by build()."""
    p = os.path.normpath(os.path.join(HERE, "..", "..", "data", "quarantine", "known_persistence_pairs.jsonl"))
    return {tuple(json.loads(l)["linear_a_phonetic_tokens"]) for l in open(p, encoding="utf-8")}


def apply_contamination_quarantine(manifest, packet, known):
    """INTEGRITY FILTER, applied AFTER blind generation. A NEGATIVE_CONTROL that coincides with a known
    persistence LA form is not a true negative → quarantine it. ONE-DIRECTIONAL: only touches
    NEGATIVE_CONTROL → QUARANTINED; it can NEVER add/remove/alter a PRIMARY or SENSITIVITY_1 member
    (asserted by test_la_candidate_leakage). This is the only place the ledger is consulted."""
    n = 0
    for m, p in zip(manifest, packet):
        if p["inclusion_set"] == "NEGATIVE_CONTROL" and tuple(m["_phonetic_word"]) in known:
            p["inclusion_set"] = m["inclusion_set"] = "QUARANTINED"
            p["exclusion_reason"] = m["exclusion_reason"] = "contaminated_negative_control_known_persistence_form"
            n += 1
    return n


def main():
    out = os.path.normpath(os.path.join(HERE, "..", "..", "data", "gold")); os.makedirs(out, exist_ok=True)
    manifest, packet = build()                                   # BLIND generation
    nq = apply_contamination_quarantine(manifest, packet, known_la_forms())   # integrity filter
    with open(os.path.join(out, "la_candidate_manifest.jsonl"), "w", encoding="utf-8") as f:
        for r in manifest: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(os.path.join(out, "la_candidate_packet.jsonl"), "w", encoding="utf-8") as f:
        for r in packet: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    inc = Counter(r["inclusion_set"] for r in packet)
    print(f"freeze {FREEZE_VERSION}: {len(packet)} candidates  (quarantined {nq} contaminated control(s))")
    print(f"  PRIMARY {inc['PRIMARY']}  SENSITIVITY_1 {inc['SENSITIVITY_1']}  NEGATIVE_CONTROL {inc['NEGATIVE_CONTROL']}  QUARANTINED {inc['QUARANTINED']}")
    print(f"  short(≤2 signs) in PRIMARY: {sum(1 for r in packet if r['inclusion_set']=='PRIMARY' and r['n_signs']<=2)}")
    print(f"  composite-sensitive: {sum(1 for r in packet if r['uncertainty']['composite_sensitive'])}")
    print(f"  site-ambiguous (ARKH): {sum(1 for r in packet if r['site_ambiguity'])}")
    print(f"wrote {out}/la_candidate_packet.jsonl (committed) + la_candidate_manifest.jsonl (internal)")


if __name__ == "__main__":
    main()
