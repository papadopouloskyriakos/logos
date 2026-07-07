#!/usr/bin/env python3
"""
T04 — Build the exact source-grounded *301 + Libation-Formula corpus.

Reads corpus/silver/inscriptions_structured.json (authoritative silver corpus,
GORILA-derived), extracts every *301-bearing form and every Libation-Formula
carrier structurally related to A-TA-I-*301-WA-JA, and records per-form metadata
+ DERIVATION vs HELD-OUT partition per the FROZEN prereg DI_MINO_EXACT_CLAIM_V1.

Non-circular: no phonetic value is assigned here. Partitions obey the prereg's
"no site/form in both" rule; where the prereg's own named held-out forms share a
site with a derivation inscription, BOTH the leave-form-out and leave-site-out
eligibility are recorded and the conflict is flagged (never silently resolved).

Seed 20260708. Emits data/libation_formula_exact/corpus.json.
"""
import json, hashlib, sys
from pathlib import Path
from collections import defaultdict

ROOT = Path("/home/claude-runner/gitlab/n8n/logos-di-mino-301-audit")
SILVER = ROOT / "corpus/silver/inscriptions_structured.json"
OUT_DIR = ROOT / "experiments/di_mino_301_audit/data/libation_formula_exact"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SEED = 20260708

# --- Libation-Formula recurring lexeme markers (structural, value-free) --------
# Well-known LA peak/rural-sanctuary Libation Formula components (GORILA / Davis
# 2014 formula frame). Used ONLY to tag formula membership, never as evidence.
LF_MARKERS = {
    "SA-SA-RA": "asasarame_theonym_slot",     # (JA-/A-)SA-SA-RA-ME
    "U-NA-KA-NA": "unakanasi_slot",
    "I-PI-NA-MA": "ipinama_slot",
    "SI-RU-TE": "sirute_slot",
    "A-TA-I": "invocation_verb_slot",          # A-TA-I-*301-WA-JA family
    "TA-NA-I": "invocation_verb_variant_slot",  # TA-NA-I-*301-...
    "JA-DI-KI": "adikite_slot",
    "O-SU-QA-RE": "osuqare_slot",
}

# Position-1 invocation-verb forms (word-initial slot Di Mino's Fig.1 targets)
INVOCATION_FORMS = {
    "A-TA-I-*301-WA-JA", "A-TA-I-*301-WA-E", "A-NA-TI-*301-WA-JA",
    "TA-NA-I-*301-U-TI-NU", "TA-NA-I-*301-TI", "A-TA-I-*301-DE-KA",
    "JA-TA-I-*301-U-JA",
}

TARGET = "A-TA-I-*301-WA-JA"  # the exact target word under audit

# --- Prereg partition definition ----------------------------------------------
# Derivation set (frozen religious language Di Mino derives on):
#   IOZa2 (Iouktas, his Figure 1), TLZa1 (Troullos), and the i-*301 core forms
#   (the I+*301 ligature attestations that anchor the "I stem-vowel invariant").
DERIVATION_INSCRIPTIONS = {"IOZa2", "TLZa1", "HTWa1022", "KN2"}
DERIVATION_SITES = {"Iouktas", "Troullos"}
# Named held-out multi-attestation variants (leave-form-out), per prereg:
NAMED_HELDOUT_FORMS = {"TA-NA-I-*301-U-TI-NU", "A-TA-I-*301-DE-KA"}

# The public claim (CLB-01, Fig.1) explicitly rests on: IOZa2 (primary) + the
# A-TA-I-*301-WA-JA "regional forms across five peak-sanctuary sites"
# (Iouktas, Kophinas, Syme, Palaikastro, Troullos). Admin *301 tablet forms are
# NOT part of the public claim — they are this audit's held-out generalization test.
PUBLIC_CLAIM_SANCTUARY_SITES = {"Iouktas", "Kophinas", "Syme", "Palaikastro", "Troullos"}

EDITION = "GORILA (Godart & Olivier 1976-1985), Recueil des inscriptions en Lineaire A; digitized via SigLA / logos silver corpus"


def wjoin(w):
    return "-".join(w)


def sign_301_tokens(w):
    return [s for s in w if "301" in str(s)]


def classify_position(form, is_lf, markers):
    if form in INVOCATION_FORMS:
        return "position_1_invocation_verb"
    for m in markers:
        if m in form:
            return "formula_body:" + LF_MARKERS[m]
    if is_lf:
        return "formula_carrier_nonformula_word"
    return "administrative_or_other_context"


def main():
    data = json.loads(SILVER.read_text())
    byid = {i["id"]: i for i in data}

    # 1) all *301-bearing forms (per-attestation)
    forms_301 = []  # each attestation
    for ins in data:
        for w in ins.get("words", []):
            toks = sign_301_tokens(w)
            if not toks:
                continue
            forms_301.append((ins, w, toks))

    # 2) Libation-Formula carrier inscriptions (structural membership)
    lf_inscriptions = {}
    for ins in data:
        ws = [wjoin(w) for w in ins.get("words", [])]
        hit = {m for m in LF_MARKERS if any(m in w for w in ws)}
        if hit:
            lf_inscriptions[ins["id"]] = hit

    # ---- Assemble per-form records ----
    records = []
    seen_ids_301 = set()
    for ins, w, toks in forms_301:
        iid = ins["id"]
        seen_ids_301.add(iid)
        form = wjoin(w)
        site = ins.get("site") or "(unprovenanced)"
        is_lf = iid in lf_inscriptions
        markers = lf_inscriptions.get(iid, set())

        # partition assignment
        in_deriv_insc = iid in DERIVATION_INSCRIPTIONS
        in_deriv_site = site in DERIVATION_SITES
        is_target = form == TARGET
        is_named_heldout = form in NAMED_HELDOUT_FORMS

        if in_deriv_insc:
            partition = "DERIVATION"
        elif is_named_heldout:
            partition = "HELD_OUT"      # named variant, leave-form-out
        else:
            partition = "HELD_OUT"

        # eligibility flags (the load-bearing detail for H1's success clauses)
        leave_form_out_eligible = not is_target  # target removed under LTO
        leave_site_out_eligible = (site not in DERIVATION_SITES) and (site != "(unprovenanced)")
        # site-contamination flag: named held-out form sitting on a derivation site
        site_contaminated = (partition == "HELD_OUT") and in_deriv_site

        used_by_public_claim = bool(
            iid == "IOZa2"
            or (is_target and site in PUBLIC_CLAIM_SANCTUARY_SITES)
            or (iid == "TLZa1")
        )

        # source dependency: single source (GORILA) -> shared-source across all;
        # no independent second witness inside the corpus for any single form.
        source_dependency = "single_source:GORILA (no independent epigraphic re-collation in corpus)"

        rec = {
            "inscription_id": iid,
            "site": site,
            "support": ins.get("support") or "(unknown)",
            "context_period": ins.get("context") or "(undated)",
            "edition": EDITION,
            "diplomatic_reading": form,
            "sign_sequence": list(w),
            "n_signs": len(w),
            "the_301_tokens": toks,
            "301_is_ligature": any("+" in t for t in toks),
            "word_division_note": (
                "GORILA word-divider (·) bounded; single graphic word"
                if len(ins.get("words", [])) > 1 else
                "single-word inscription"
            ),
            "damage_note": "no damage flag in silver record; consult GORILA autopsy for lacunae",
            "is_libation_formula_carrier": is_lf,
            "lf_markers_present": sorted(markers),
            "formula_position": classify_position(form, is_lf, markers),
            "is_invocation_verb_slot": form in INVOCATION_FORMS,
            "is_target_word": is_target,
            "source_dependency": source_dependency,
            "used_by_public_claim": used_by_public_claim,
            "partition": partition,
            "leave_form_out_eligible": leave_form_out_eligible,
            "leave_site_out_eligible": leave_site_out_eligible,
            "site_contaminated_vs_derivation": site_contaminated,
            "full_inscription_words": [wjoin(x) for x in ins.get("words", [])],
        }
        records.append(rec)

    # ---- Libation-Formula carriers WITHOUT *301 (formula frame / held-out context) ----
    lf_only_records = []
    for iid, markers in sorted(lf_inscriptions.items()):
        if iid in seen_ids_301:
            continue
        ins = byid[iid]
        site = ins.get("site") or "(unprovenanced)"
        lf_only_records.append({
            "inscription_id": iid,
            "site": site,
            "support": ins.get("support") or "(unknown)",
            "context_period": ins.get("context") or "(undated)",
            "edition": EDITION,
            "lf_markers_present": sorted(markers),
            "full_inscription_words": [wjoin(x) for x in ins.get("words", [])],
            "partition": ("DERIVATION" if site in DERIVATION_SITES else "HELD_OUT"),
            "role": "libation_formula_frame_no_301 (context / non-301 formula slots)",
        })

    # ---- Distinct-form rollup ----
    by_form = defaultdict(list)
    for r in records:
        by_form[r["diplomatic_reading"]].append(r["inscription_id"])

    # ---- Partition power check (prereg NO_POWER threshold ~3 independent held-out) ----
    heldout_301 = [r for r in records if r["partition"] == "HELD_OUT"]
    heldout_301_lso = [r for r in heldout_301 if r["leave_site_out_eligible"]]
    heldout_invocation_lso = [r for r in heldout_301_lso if r["is_invocation_verb_slot"]]
    heldout_sites = sorted({r["site"] for r in heldout_301_lso})

    summary = {
        "seed": SEED,
        "total_301_attestations": len(records),
        "distinct_301_forms": len(by_form),
        "n_301_inscriptions": len(seen_ids_301),
        "n_libation_formula_carriers_total": len(lf_inscriptions),
        "n_lf_carriers_without_301": len(lf_only_records),
        "partition_counts": {
            "DERIVATION": sum(1 for r in records if r["partition"] == "DERIVATION"),
            "HELD_OUT": len(heldout_301),
        },
        "held_out_301_leave_site_out_eligible": len(heldout_301_lso),
        "held_out_invocation_slot_leave_site_out_eligible": len(heldout_invocation_lso),
        "held_out_sites_leave_site_out_eligible": heldout_sites,
        "site_contaminated_heldout_forms": [
            {"id": r["inscription_id"], "form": r["diplomatic_reading"], "site": r["site"]}
            for r in records if r["site_contaminated_vs_derivation"]
        ],
        "NO_POWER_threshold_independent_heldout": 3,
        "power_flag_H1": (
            "ADEQUATE" if len(heldout_301_lso) >= 3 else "NO_POWER"
        ),
        "power_flag_invocation_slot": (
            "ADEQUATE" if len(heldout_invocation_lso) >= 3 else "NO_POWER"
        ),
        "distinct_forms_index": {k: sorted(set(v)) for k, v in sorted(by_form.items())},
    }

    out = {
        "prereg": "DI_MINO_EXACT_CLAIM_V1 (sha 8b098a4c)",
        "constitution": "v2.2",
        "generated_by": "scripts/build_libation_formula_corpus.py",
        "seed": SEED,
        "note": (
            "NON-CIRCULAR corpus assembly. No phonetic value assigned to *301. "
            "Partitions per frozen prereg; site-contamination flagged, not resolved."
        ),
        "partition_definition": {
            "derivation_inscriptions": sorted(DERIVATION_INSCRIPTIONS),
            "derivation_sites": sorted(DERIVATION_SITES),
            "named_heldout_forms_leave_form_out": sorted(NAMED_HELDOUT_FORMS),
            "target_word_leave_target_out": TARGET,
            "cv_unit": "peak-sanctuary site",
            "grouping_unit": "inscription",
        },
        "summary": summary,
        "records_301": records,
        "libation_formula_frame_without_301": lf_only_records,
    }

    out_path = OUT_DIR / "corpus.json"
    payload = json.dumps(out, ensure_ascii=False, indent=2)
    out_path.write_text(payload)
    sha = hashlib.sha256(payload.encode()).hexdigest()
    print("WROTE", out_path)
    print("sha256", sha)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
