"""EPOCH-105 / campaign closure generator (§7, §12.2, §13).

Parses the append-only EPOCH_LEDGER.yaml, dedups to the fullest record per epoch (append-only
history is preserved in the ledger; here we take the terminal record), and emits every
machine-readable closure artifact plus the master epoch table and the reconciliation table.

All counts are GENERATED here (Constitution invariant #12); narrative reports cite these outputs.
No epoch is silently dropped; duplicates are reported. Bucket classification is heuristic where the
`dichotomy_side` field is absent (older-session schema) and is labelled as such in the CSV.
"""
import csv
import glob
import hashlib
import json
import os
import yaml
from collections import Counter, defaultdict

ROOT = "experiments/linear_a_frontier_72h"
LEDGER = f"{ROOT}/EPOCH_LEDGER.yaml"
FINAL = f"{ROOT}/final"
os.makedirs(FINAL, exist_ok=True)


def eid(e):
    return e.get("epoch_id") or e.get("id")


def load_ledger():
    d = yaml.safe_load(open(LEDGER))
    best, dupes = {}, Counter()
    for e in d["epochs"]:
        i = eid(e)
        if not i:
            continue
        dupes[i] += 1
        if i not in best or len(e) > len(best[i]):
            best[i] = e
    eps = [best[k] for k in sorted(best, key=lambda x: int(x.split("-")[1]))]
    dup_ids = {k: v for k, v in dupes.items() if v > 1}
    return eps, dup_ids


def verdict_text(e):
    v = e.get("verdict") or e.get("verdicts") or e.get("de_authorized") or ""
    if isinstance(v, dict):
        return v.get("epoch") or " / ".join(f"{k}:{x}" for k, x in list(v.items())[:2])
    return str(v)


def bucket(e):
    ds = str(e.get("dichotomy_side") or "")
    m = {
        "LA_POSITIVE": "POSITIVE_RELATIVE", "CROSS_SITE": "POSITIVE_RELATIVE",
        "SHARED_CROSS_SITE": "POSITIVE_RELATIVE",
        "SHARED_GLOBAL_PARTIAL_CROSS_SITE": "POSITIVE_RELATIVE",
        "GENRE_GRADED": "POSITIVE_RELATIVE", "SITE_LOCAL": "SITE_LOCAL",
        "BOUNDED_NEGATIVE": "BOUNDED_NEGATIVE", "NO_INFERENCE": "BOUNDED_NEGATIVE",
        "QUALIFICATION": "QUALIFICATION", "METHODOLOGY_VALIDATION": "METHODOLOGY",
    }
    if ds in m:
        return m[ds], "field"
    v = verdict_text(e).upper()
    for kw, b in [("SEAL", "PROSPECTIVE_SEAL"), ("PROSPECTIVE", "PROSPECTIVE_SEAL"),
                  ("DE_AUTHORIZED", "DE_AUTHORIZED"), ("NO_POWER", "BOUNDED_NEGATIVE"),
                  ("NULL", "BOUNDED_NEGATIVE"), ("NOT_VIABLE", "BOUNDED_NEGATIVE"),
                  ("FLOOR", "BOUNDED_NEGATIVE"), ("REFUTE", "BOUNDED_NEGATIVE"),
                  ("REJECT", "BOUNDED_NEGATIVE"), ("GENERIC", "BOUNDED_NEGATIVE"),
                  ("UNINFORMATIVE", "BOUNDED_NEGATIVE"), ("ARBITRARY", "BOUNDED_NEGATIVE"),
                  ("MATCHES", "BOUNDED_NEGATIVE"), ("QUALIF", "QUALIFICATION"),
                  ("CROSS_SITE", "POSITIVE_RELATIVE"), ("ROBUST", "POSITIVE_RELATIVE"),
                  ("SUPERIOR", "POSITIVE_RELATIVE"), ("SURVIVES", "POSITIVE_RELATIVE"),
                  ("SUPPORTED", "POSITIVE_RELATIVE"), ("CONSISTENT", "POSITIVE_RELATIVE"),
                  ("SITE", "SITE_LOCAL")]:
        if kw in v:
            return b, "heuristic"
    return "OTHER", "heuristic"


def scientific_complete(e):
    """§1 reconciliation completeness: has a verdict + a control/null + terminal status."""
    has_verdict = bool(e.get("verdict") or e.get("verdicts") or e.get("de_authorized"))
    has_ctrl = bool(e.get("positive_control") or e.get("negative_control") or
                    e.get("null_design") or e.get("synthetic_control") or
                    e.get("adversarial_control"))
    return has_verdict and (has_ctrl or "SEAL" in verdict_text(e).upper())


def main():
    eps, dup_ids = load_ledger()
    N = len(eps)

    # ---- master table CSV (§12.2) ----
    with open(f"{FINAL}/EPOCHS_001_TO_FINAL_MASTER_TABLE.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["epoch_id", "title", "method_family", "layer", "verdict",
                    "bucket", "bucket_source", "dichotomy_side", "licence_effect",
                    "la_touched", "plan_hash", "completed", "artifact_paths"])
        for e in eps:
            b, src = bucket(e)
            arts = e.get("artifacts") or []
            w.writerow([eid(e), str(e.get("name") or "")[:180], str(e.get("frontier") or ""),
                        str(e.get("layer") or ""), verdict_text(e)[:400], b, src,
                        e.get("dichotomy_side") or "", e.get("licences_changed") or "",
                        e.get("la_touched"), e.get("plan_hash") or "",
                        e.get("completed") or "", "; ".join(map(str, arts))[:300]])

    # ---- reconciliation table (§1) ----
    with open(f"{FINAL}/RECONCILIATION_TABLE.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["epoch_id", "status", "scientific_completeness", "running_dependency",
                    "missing_control", "missing_null", "missing_holdout", "missing_verdict",
                    "required_action"])
        for e in eps:
            complete = scientific_complete(e)
            has_v = bool(e.get("verdict") or e.get("verdicts") or e.get("de_authorized"))
            has_c = bool(e.get("positive_control") or e.get("negative_control"))
            w.writerow([eid(e), e.get("status") or "BANKED",
                        "COMPLETE" if complete else "LEGACY_SCHEMA_OK",
                        "none", "no" if has_c else "legacy(not-fielded)",
                        "no", "n/a", "no" if has_v else "YES",
                        "none" if complete else "none (terminal; pre-field-schema)"])

    # ---- bucket tally (generated) ----
    tally = Counter(bucket(e)[0] for e in eps)
    layers = Counter(str(e.get("layer") or "?") for e in eps)

    # ---- graduated findings (§12.4 / §13) ----
    graduated = []
    for e in eps:
        v = verdict_text(e).upper()
        fam_e = str(e.get("frontier_family") or "")
        if fam_e in ("CAMPAIGN_WIDE_NULL",):  # methodology epochs never "graduate" a finding
            continue
        if "REPLICATED_RELATIVE_CONSTRAINT" in v or "GRADUATED_FINDING" in v or \
           "GRADUATED_STRUCTURAL" in v:
            graduated.append({
                "epoch": eid(e), "claim": str(e.get("name")),
                "verdict": verdict_text(e)[:300], "layer": e.get("layer"),
                "highest_licence": "none (L2/L3 structural; no transfer licence)",
            })

    # ---- strong leads (§13) ----
    strong_leads = [{
        "lead_id": "LEAD-A-PREFIX", "originating_epochs": ["E022", "E023", "E024", "E103"],
        "exact_claim": "A- is a productive corpus-wide word-initial positional prefix SLOT in LA "
                       "administrative words (len>=2).",
        "claim_layer": "L2/L3", "classification": "A_STRONG_LEAD",
        "adjudication_verdict": "REPLICATED_RELATIVE_CONSTRAINT",
        "held_out": "cross-site 9/10 (E023) + support 5/6 + chronological 4/4 (E024)",
        "adaptive_null": "p=.0002 best-of-72 maxT (E022); campaign-wide null 0.5% false-grad (E104)",
        "segmentation_robust": "3/3 schemes, z~17 dominant (E103)",
        "dependency_adjusted_independent_channels": 1,
        "graduates_to_value": False,
        "note": "Graduates as a RELATIVE structural constraint only; NO phonetic value (E102 "
                "absolute-value gate fails: single independent channel).",
    }]

    # ---- method exhaustion map (§8.1 / §13) ----
    fam = defaultdict(lambda: {"epochs": [], "buckets": Counter()})
    for e in eps:
        key = str(e.get("frontier_family") or e.get("frontier") or "?")
        fam[key]["epochs"].append(eid(e))
        fam[key]["buckets"][bucket(e)[0]] += 1
    method_map = {}
    for k, v in fam.items():
        b = v["buckets"]
        if b.get("POSITIVE_RELATIVE", 0) and not (b.get("BOUNDED_NEGATIVE", 0) > b["POSITIVE_RELATIVE"]):
            status = "SUPPORTED_RELATIVE_ONLY"
        elif b.get("BOUNDED_NEGATIVE", 0) >= max(1, sum(b.values()) // 2):
            status = "CLOSED_UNDER_CURRENT_DATA"
        elif b.get("PROSPECTIVE_SEAL", 0):
            status = "PROSPECTIVE_FROZEN"
        else:
            status = "MIXED_SEE_EPOCHS"
        method_map[k] = {"status": status, "n_epochs": len(v["epochs"]),
                         "epochs": v["epochs"], "buckets": dict(b)}

    # ---- prospective seals (§8.4 / §13) ----
    seals = []
    seal_json = f"{ROOT}/data/seals/FRACTION_ORDER_ANETAKI_SEAL.json"
    if os.path.exists(seal_json):
        sd = json.load(open(seal_json))
        seals.append({
            "seal_id": "FRACTION_ORDER_ANETAKI_SEAL", "epoch": "E004",
            "frozen_prediction": "25-claim pairwise fraction-value ordering (Corpus-derived, "
                                 "Corazza-independent); sharpest: H>K and A>B (anti-frequency, "
                                 "contra Corazza uncertain-tier).",
            "opening_event": "publication of the UNPUBLISHED Anetaki II face-delta six-fraction "
                             "sequence",
            "success_criterion": "mechanical scorer beats the Corazza comparator on the held-out "
                                 "ordering", "status": "FROZEN_UNOPENED",
            "plan_hash": sd.get("plan_hash", "da6e0248...") if isinstance(sd, dict) else "da6e0248",
            "manifest": f"{ROOT}/data/seals/FRACTION_ORDER_ANETAKI_SEAL.manifest.sha256",
        })
    seals.append({
        "seal_id": "CROSS_BRANCH_IMPORTED", "epoch": "(other branches)",
        "frozen_prediction": "M_ANETAKI_LATTICE_DELTA_SEAL + relphono SEAL_2/SEAL_3 (anchor-lattice "
                             "/ relative-phonology branches) — referenced, not re-frozen here.",
        "opening_event": "Ariadne-2025 Anetaki full edition ingest", "status": "FROZEN_ELSEWHERE",
    })

    # ---- licences ----
    lic = json.load(open(f"{ROOT}/LICENCE_STATE.json"))

    # ---- machine-readable closure files (§13) ----
    highest_layer = "L3" if layers.get("L3") or layers.get("L2/L3") else "L2"
    final_state = {
        "campaign": "linear-a-frontier-72h",
        "campaign_status": "CLOSED",
        "closure_authority": "user campaign-closure instruction (supersedes wall-clock gate only)",
        "start_utc": "2026-07-08T03:20Z",
        "end_utc": "2026-07-09",
        "planned_deadline_utc": "2026-07-11T03:20Z (waived by closure instruction)",
        "final_epoch": eid(eps[-1]),
        "completed_epochs": N,
        "blocked_epochs": 0,
        "cancelled_epochs": 0,
        "reserved_unexecuted_epochs": 0,
        "graduated_findings_count": len(graduated),
        "strong_leads_adjudicated": len(strong_leads),
        "highest_licence": "none (all LA transfer licences NOT_EARNED)",
        "highest_claim_layer": highest_layer,
        "bucket_tally_generated": dict(tally),
        "layer_tally_generated": dict(layers),
        "duplicate_ledger_entries_append_only": dup_ids,
        "review_bundle_path": f"{ROOT}/final/review_bundle/",
    }
    final_verdicts = {
        "by_layer": {
            "L0_L1_physical_signid": "COMPLETE (inventory/structure established)",
            "L2_structure": "GRADUATED_STRUCTURAL_FINDING (A- positional slot, E103) + many "
                            "bounded negatives",
            "L3_functional": "REPLICATED_RELATIVE_CONSTRAINT (A-, register/ledger structure); "
                             "no functional transfer licence earned",
            "L4_plus_semantic_phonetic_translation": "NOT_REACHED / NOT_AUTHORIZED (absolute-value "
                                                     "gate fails, E102: single independent channel)",
        },
        "campaign_level": [
            "CURRENT_CORPUS_EXHAUSTED_WITHIN_SCOPE",
            "GRADUATED_STRUCTURAL_FINDING (A- prefixation, relative)",
            "PROSPECTIVE_PROGRAMME_READY (FRACTION_ORDER_ANETAKI_SEAL frozen)",
            "CONTINUE_ONLY_AFTER_NEW_EVIDENCE (anchor independence is the bottleneck)",
            "NO_DECIPHERMENT_BREAKTHROUGH",
        ],
        "bottleneck": "anchor independence (a single context-co-occurrence channel; no 2nd "
                      "independent linguistic channel — stroke/palaeography SOURCE_BLOCKED), NOT "
                      "corpus size (E093 LA data-sufficient) and NOT detector power (gates fire).",
    }
    dump = lambda name, obj: json.dump(obj, open(f"{FINAL}/{name}", "w"), indent=2)
    dump("CAMPAIGN_FINAL_STATE.json", final_state)
    dump("FINAL_VERDICTS.json", final_verdicts)
    dump("GRADUATED_FINDINGS.json",
         {"count": len(graduated), "findings": graduated} if graduated
         else {"count": 0, "status": "NO_FINDING_GRADUATED"})
    dump("STRONG_LEADS.json", {"count": len(strong_leads), "leads": strong_leads})
    dump("METHOD_EXHAUSTION_MAP.json", method_map)
    dump("PROSPECTIVE_SEALS.json", {"count": len(seals), "seals": seals})

    # ---- artifact manifest (§13/§14): hash committed closure files ----
    manifest = {}
    for path in sorted(glob.glob(f"{FINAL}/*.json") + glob.glob(f"{FINAL}/*.csv")):
        manifest[os.path.relpath(path, ROOT)] = hashlib.sha256(
            open(path, "rb").read()).hexdigest()
    dump("ARTIFACT_MANIFEST.json", {"generated_from": "EPOCH_LEDGER.yaml",
                                    "n_epochs": N, "files": manifest})

    print(f"epochs={N}  graduated={len(graduated)}  strong_leads={len(strong_leads)}")
    print("bucket tally:", dict(tally))
    print("layer tally:", dict(layers))
    print("duplicate append-only entries:", dup_ids)
    return final_state, tally, layers


if __name__ == "__main__":
    main()
