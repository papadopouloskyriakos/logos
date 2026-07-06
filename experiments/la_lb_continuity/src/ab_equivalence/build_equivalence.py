#!/usr/bin/env python3
"""Freeze the palaeographic A↔B sign-equivalence layer (§V) — BLIND to the five known pairs.

Basis (pair-independent, phonetic-independent): SigLA classifies every sign as **AB** (attested in
BOTH Linear A and Linear B — a conventional homomorph, GORILA shared numbering) or **A** (Linear-A
only). That classification is a property of the sign *repertoire* (Salgarella & Castellan / GORILA /
Ventris–Chadwick), established with no reference to any toponym pair or projected sound value. So:

  LEVEL_1  exact raw sign-ID identity: the AB## graph carries the same GORILA number in both scripts
  LEVEL_2  frozen palaeographic equivalence classes keyed by that GORILA number  ← primary map here
  LEVEL_3  projected LB phonetic values                                          ← firewalled, §IX ablation only

Tiers: A = SigLA AB-class (conventional homomorph, the authority's own judgement); X = A-only
(no LB equivalent → excluded from primary). Per-graph palaeographic B/C sub-tiering is a DOCUMENTED
deferred refinement (Salgarella 2020 monograph, held locally) — not fabricated here. In its place the
robustness handle is `high_attestation` (LA-side token frequency ≥ THRESHOLD): pair-blind, non-phonetic.

Every row records phonetic_value_used=false and target_pair_used_in_selection=false BY CONSTRUCTION —
this builder never reads a phonetic value, a toponym, or the pair ledger. See the blindness test.
"""
import argparse, json, os, sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "sigla_reconcile"))
import config  # noqa: E402

HIGH_ATTESTATION_THRESHOLD = 10   # prespecified, non-phonetic, non-pair; frozen before matching
RULE_VERSION = "ab-equiv-v1-2026-07-06"


def la_attestation(docs):
    """Token frequency of each SigLA sign-id across all LA document transcriptions."""
    c = Counter()
    for d in docs:
        for s in d.get("transcription", []):
            c[s] += 1
    return c


def build():
    signs = json.load(open(config.SIGLA_SIGNS, encoding="utf-8"))
    docs = json.load(open(config.SIGLA_DOCUMENTS, encoding="utf-8"))
    att = la_attestation(docs)

    rows = []
    for key, s in sorted(signs.items(), key=lambda kv: (kv[1]["class"], kv[1]["gorila_number"])):
        cls, n, name = s["class"], s["gorila_number"], s["name"]
        la_att = att.get(name, 0)
        if cls == "AB":
            rows.append({
                "gorila_number": n,
                "la_sign_id": name,                 # AB## in Linear A usage
                "lb_sign_id": f"*{n:02d}",          # same GORILA number in Linear B convention
                "equivalence_level": "LEVEL_1",     # directly shared sign-ID
                "confidence_tier": "A",
                "graphic_similarity_basis": "SigLA AB-class (conventional A/B homomorph); GORILA shared numbering",
                "source_authority": "SigLA (Salgarella & Castellan); GORILA (Godart & Olivier); Ventris-Chadwick AB convention",
                "allograph_scope": "canonical sign-id (per-glyph allograph clustering deferred)",
                "site_scope": "pan-Cretan (repertoire-level)",
                "chronological_scope": "LA (MM II-LM IB) vs LB (LM II-III) — cross-horizon by construction",
                "la_attestation": la_att,
                "high_attestation": la_att >= HIGH_ATTESTATION_THRESHOLD,
                "disputed_flag": False,             # default; palaeographic dispute review deferred (Salgarella 2020)
                "phonetic_value_used": False,
                "target_pair_used_in_selection": False,
            })
        else:  # A-only -> excluded from primary (no LB equivalent)
            rows.append({
                "gorila_number": n, "la_sign_id": name, "lb_sign_id": None,
                "equivalence_level": None, "confidence_tier": "X",
                "graphic_similarity_basis": "SigLA A-only (Linear-A-specific; no LB homomorph)",
                "source_authority": "SigLA (Salgarella & Castellan); GORILA",
                "allograph_scope": "n/a", "site_scope": "n/a", "chronological_scope": "n/a",
                "la_attestation": la_att, "high_attestation": False, "disputed_flag": False,
                "phonetic_value_used": False, "target_pair_used_in_selection": False,
            })

    tierA = [r for r in rows if r["confidence_tier"] == "A"]
    meta = {
        "rule_version": RULE_VERSION,
        "high_attestation_threshold": HIGH_ATTESTATION_THRESHOLD,
        "counts": {
            "total_signs": len(rows),
            "tier_A_AB_homomorphs": len(tierA),
            "tier_X_A_only_excluded": sum(1 for r in rows if r["confidence_tier"] == "X"),
            "tier_A_high_attestation": sum(1 for r in tierA if r["high_attestation"]),
        },
        "levels": {"LEVEL_1": "exact shared GORILA sign-ID (the tier-A AB set)",
                   "LEVEL_2": "palaeographic equivalence classes (== LEVEL_1 until allographs clustered)",
                   "LEVEL_3": "projected LB phonetic values — FIREWALLED, ablation only"},
        "blindness": "built only from the SigLA sign catalogue + LA attestation counts; no phonetic "
                     "value, no toponym, no pair ledger is read (enforced by test_ab_equivalence_blindness)",
        "deferred_refinement": "per-graph palaeographic B/C sub-tiering + disputed flags via Salgarella "
                               "2020 (corpus/bronze/salgarella_2020/, held locally) — NOT applied; tier A "
                               "rests on SigLA's AB-class designation.",
    }
    return {"meta": meta, "equivalence": rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "..", "data", "gold"))
    a = ap.parse_args()
    out = os.path.normpath(a.out); os.makedirs(out, exist_ok=True)
    m = build()
    path = os.path.join(out, "ab_sign_equivalence.json")
    json.dump(m, open(path, "w"), ensure_ascii=False, indent=1)
    c = m["meta"]["counts"]
    print(f"rule {m['meta']['rule_version']}")
    print(f"tier A (AB homomorphs): {c['tier_A_AB_homomorphs']}  "
          f"(high-attestation ≥{HIGH_ATTESTATION_THRESHOLD}: {c['tier_A_high_attestation']})")
    print(f"tier X (A-only excluded): {c['tier_X_A_only_excluded']}   total {c['total_signs']}")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
