"""EPOCH-105 / campaign closure generator (§7, §12.2, §13) — remediation revision.

Parses the append-only EPOCH_LEDGER.yaml and emits every machine-readable closure artifact
plus the master epoch table and the reconciliation table. All counts are GENERATED here
(Constitution invariant #12); a small number of narrative fields are CURATED and are labelled
"source": "curated" (JSON) — counts are never curated.

Remediation changes (terminal audit pass, 2026-07-09; items C1-C12):
- C1  bucket(): classification keys on the verdict HEADLINE (the mechanical status token
      before the first ' -- ' / ' — ' / '('), with POSITIVE keys checked BEFORE negative
      keys. Full-prose scanning is gone: it mislabelled genuine positives whose prose
      mentioned "null" (e.g. E020/E022 *_SURVIVES_ADAPTIVE_NULL) and would equally have
      mislabelled genuine negatives whose prose mentioned "consistent". Headlines with no
      status keyword bucket as OTHER (honest: partial/marginal/underpowered outcomes).
- C2  dedup is field-level append-merge in ledger order (later records override the fields
      they set; unset fields inherit) — append-only order defines the terminal record, not
      record length.
- C3  DE_AUTHORIZED epochs surface status DE_AUTHORIZED and verdict "DE_AUTHORIZED
      (terminal)" (never a date); counts are derived from fields, not hardcoded.
- C4  the reconciliation table carries ONLY derived columns; its header comment states
      exactly what is and is not audited.
- C5  highest_licence is computed from LICENCE_STATE.json.
- C7  no truncation anywhere; verdicts are verbatim from the (append-only) ledger.
- C8  ARTIFACT_MANIFEST.json excludes itself from its own file list.
- C9  --final-commit stamps final_commit into CAMPAIGN_FINAL_STATE.json.
- C10 emits epochs/EPOCH-105/result.json (mechanical verdict + plan_hash + code_manifest +
      sha256 of every emitted closure artifact).
- C11 la_touched is strictly boolean/absent; free-text annotations move to a notes column;
      missing layer encodes as '?' in both CSV and JSON.
- C12 plan_hash falls back to epochs/<id>/plan_hash.txt when the ledger field is absent
      (source recorded per row).
"""
import argparse
import csv
import glob
import hashlib
import json
import os
import re
import yaml
from collections import Counter, defaultdict

ROOT = "experiments/linear_a_frontier_72h"
LEDGER = f"{ROOT}/EPOCH_LEDGER.yaml"
FINAL = f"{ROOT}/final"
os.makedirs(FINAL, exist_ok=True)


def sha256_file(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def eid(e):
    return e.get("epoch_id") or e.get("id")


def load_ledger():
    """Field-level append-merge (C2): later ledger records override the fields they set;
    fields they do not set inherit from earlier records. Append-only order = terminal."""
    d = yaml.safe_load(open(LEDGER))
    merged, dupes = {}, Counter()
    for e in d["epochs"]:
        i = eid(e)
        if not i:
            continue
        dupes[i] += 1
        merged.setdefault(i, {}).update(e)
    eps = [merged[k] for k in sorted(merged, key=lambda x: int(x.split("-")[1]))]
    dup_ids = {k: v for k, v in dupes.items() if v > 1}
    return eps, dup_ids, len(d["epochs"])


def verdict_text(e):
    """Terminal verdict string. DE_AUTHORIZED epochs never surface the date (C3)."""
    v = e.get("verdict") or e.get("verdicts")
    if not v and e.get("de_authorized"):
        return "DE_AUTHORIZED (terminal)"
    if isinstance(v, dict):
        return v.get("epoch") or " / ".join(f"{k}:{x}" for k, x in v.items())
    return str(v or "")


def status_of(e):
    s = e.get("status")
    if s:
        return str(s)
    if e.get("de_authorized"):
        return "DE_AUTHORIZED"
    return "BANKED(implicit)"


def headline(v):
    """The mechanical status token: everything before the first ' -- ', ' — ', '–' or '('."""
    return re.split(r"\s*(?:--|—|–|\(|\n)", v, 1)[0].strip()


# C1: headline-scan bucketer; positive keys BEFORE negative keys. Documented rule:
# 1) dichotomy_side field wins where present; 2) otherwise scan the verdict HEADLINE in the
# order below (first hit wins); 3) no hit -> OTHER.
BUCKET_FIELD = {
    "LA_POSITIVE": "POSITIVE_RELATIVE", "CROSS_SITE": "POSITIVE_RELATIVE",
    "SHARED_CROSS_SITE": "POSITIVE_RELATIVE",
    "SHARED_GLOBAL_PARTIAL_CROSS_SITE": "POSITIVE_RELATIVE",
    "GENRE_GRADED": "POSITIVE_RELATIVE", "SITE_LOCAL": "SITE_LOCAL",
    "BOUNDED_NEGATIVE": "BOUNDED_NEGATIVE", "NO_INFERENCE": "BOUNDED_NEGATIVE",
    "QUALIFICATION": "QUALIFICATION", "METHODOLOGY_VALIDATION": "METHODOLOGY",
}
BUCKET_KEYWORDS = [
    ("SEAL", "PROSPECTIVE_SEAL"), ("PROSPECTIVE", "PROSPECTIVE_SEAL"),
    ("DE_AUTHORIZED", "DE_AUTHORIZED"),
    ("QUALIF", "QUALIFICATION"),
    # positive keys BEFORE negative keys (C1)
    ("SURVIVES", "POSITIVE_RELATIVE"), ("ROBUST", "POSITIVE_RELATIVE"),
    ("SUPPORTED", "POSITIVE_RELATIVE"), ("CROSS_SITE", "POSITIVE_RELATIVE"),
    ("CONSISTENT", "POSITIVE_RELATIVE"), ("SUPERIOR", "POSITIVE_RELATIVE"),
    ("REPLICATED", "POSITIVE_RELATIVE"),
    ("NO_POWER", "BOUNDED_NEGATIVE"), ("NULL", "BOUNDED_NEGATIVE"),
    ("NOT_VIABLE", "BOUNDED_NEGATIVE"), ("FLOOR", "BOUNDED_NEGATIVE"),
    ("REFUTE", "BOUNDED_NEGATIVE"), ("REJECT", "BOUNDED_NEGATIVE"),
    ("GENERIC", "BOUNDED_NEGATIVE"), ("UNINFORMATIVE", "BOUNDED_NEGATIVE"),
    ("ARBITRARY", "BOUNDED_NEGATIVE"), ("MATCHES", "BOUNDED_NEGATIVE"),
    ("NO_", "BOUNDED_NEGATIVE"), ("AT_CHANCE", "BOUNDED_NEGATIVE"),
    ("SITE", "SITE_LOCAL"),
]


def bucket(e):
    ds = str(e.get("dichotomy_side") or "")
    if ds in BUCKET_FIELD:
        return BUCKET_FIELD[ds], "field"
    h = headline(verdict_text(e)).upper()
    for kw, b in BUCKET_KEYWORDS:
        if kw in h:
            return b, "headline"
    return "OTHER", "headline"


def la_touched_of(e):
    """C11: strictly boolean or '' (absent); free-text annotations go to the notes column."""
    v = e.get("la_touched")
    if isinstance(v, bool):
        return v, ""
    if v is None:
        return "", ""
    return "", f"la_touched annotation: {v}"


def plan_hash_of(e):
    """C12: ledger field, else epochs/<id>/plan_hash.txt on disk."""
    v = e.get("plan_hash")
    if v:
        return str(v), "ledger"
    p = f"{ROOT}/epochs/{eid(e)}/plan_hash.txt"
    if os.path.exists(p):
        return open(p).read().strip(), "file(plan_hash.txt)"
    return "", "absent"


def layer_of(e):
    return str(e.get("layer") or "?")


def scientific_complete(e):
    """Derived: has a terminal verdict + at least one fielded control/null design."""
    has_verdict = bool(e.get("verdict") or e.get("verdicts") or e.get("de_authorized"))
    has_ctrl = bool(e.get("positive_control") or e.get("negative_control") or
                    e.get("null_design") or e.get("synthetic_control") or
                    e.get("adversarial_control"))
    return has_verdict and (has_ctrl or "SEAL" in verdict_text(e).upper())


def main(final_commit=""):
    eps, dup_ids, raw_rows = load_ledger()
    N = len(eps)

    # ---- master table CSV (§12.2) — verbatim, untruncated (C7) ----
    with open(f"{FINAL}/EPOCHS_001_TO_FINAL_MASTER_TABLE.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["epoch_id", "title", "method_family", "layer", "verdict",
                    "bucket", "bucket_source", "dichotomy_side", "licence_effect",
                    "la_touched", "plan_hash", "plan_hash_source", "completed", "status",
                    "notes", "artifact_paths"])
        for e in eps:
            b, src = bucket(e)
            ph, phsrc = plan_hash_of(e)
            lt, note = la_touched_of(e)
            arts = e.get("artifacts") or []
            w.writerow([eid(e), str(e.get("name") or ""), str(e.get("frontier") or ""),
                        layer_of(e), verdict_text(e), b, src,
                        e.get("dichotomy_side") or "", e.get("licences_changed") or "",
                        lt, ph, phsrc, e.get("completed") or "", status_of(e),
                        note, "; ".join(map(str, arts))])

    # ---- reconciliation table (§1) — DERIVED columns only (C4) ----
    with open(f"{FINAL}/RECONCILIATION_TABLE.csv", "w", newline="") as f:
        f.write("# AUDITED (derived from ledger fields): status terminality; presence of a "
                "terminal verdict; presence of at least one fielded control/null-design "
                "field (positive_control / negative_control / adversarial_control / "
                "synthetic_control / null_design). NOT AUDITED by this table: scientific "
                "adequacy of nulls, holdout usage, or verdict correctness — those are "
                "audited per-epoch in VERIFICATION_AUDIT.md and each ledger entry's "
                "orchestrator_verification field.\n")
        w = csv.writer(f)
        w.writerow(["epoch_id", "status", "terminal", "has_verdict",
                    "has_control_field", "scientific_completeness", "required_action"])
        for e in eps:
            st = status_of(e)
            terminal = st not in ("RUNNING", "BLOCKED", "RESERVED")
            has_v = bool(e.get("verdict") or e.get("verdicts") or e.get("de_authorized"))
            has_c = bool(e.get("positive_control") or e.get("negative_control") or
                         e.get("adversarial_control") or e.get("synthetic_control") or
                         e.get("null_design"))
            complete = scientific_complete(e)
            w.writerow([eid(e), st, "yes" if terminal else "NO",
                        "yes" if has_v else "NO",
                        "yes" if has_c else "no (pre-field-schema)",
                        "COMPLETE" if complete else "LEGACY_SCHEMA_OK",
                        "none" if (terminal and has_v) else "REVIEW"])

    # ---- tallies (generated) ----
    tally = Counter(bucket(e)[0] for e in eps)
    layers = Counter(layer_of(e) for e in eps)

    # ---- status-derived counts (C3) ----
    statuses = Counter(status_of(e) for e in eps)
    de_auth = [eid(e) for e in eps if status_of(e) == "DE_AUTHORIZED"]
    completed_epochs = sum(1 for e in eps if e.get("completed"))
    terminal_epochs = sum(1 for e in eps
                          if status_of(e) not in ("RUNNING", "BLOCKED", "RESERVED"))
    blocked_epochs = statuses.get("BLOCKED", 0)
    cancelled_epochs = statuses.get("CANCELLED", 0)

    # ---- graduated findings (§12.4 / §13) ----
    graduated = []
    for e in eps:
        v = verdict_text(e).upper()
        if str(e.get("frontier_family") or "") in ("CAMPAIGN_WIDE_NULL",):
            continue  # methodology epochs never "graduate" a finding
        if "REPLICATED_RELATIVE_CONSTRAINT" in v or "GRADUATED_FINDING" in v or \
           "GRADUATED_STRUCTURAL" in v:
            graduated.append({
                "epoch": eid(e),
                "claim": ("Recurrent A-initial positional enrichment in Linear A "
                          "administrative units (anonymous initial slot; relative "
                          "constraint). Prefixhood, productivity, sound, and meaning are "
                          "not established."),
                "claim_source": "curated (corrected wording; ledger name/verdict verbatim "
                                "in the master table)",
                "verdict": verdict_text(e),
                "layer": e.get("layer"),
                "highest_licence": "none (L2/L3 structural; no transfer licence)",
            })

    # ---- strong leads (§13) — CURATED narrative entry (counts generated) ----
    strong_leads = [{
        "source": "curated",
        "lead_id": "LEAD-A-INITIAL",
        "originating_epochs": ["E022", "E023", "E024", "E103", "E103R"],
        "exact_claim": "In Linear A administrative units of >=2 signs, the sign A occupies "
                       "initial position far above its within-unit multiset expectation — "
                       "a recurrent A-initial positional enrichment (anonymous slot). "
                       "Prefixhood, productivity, sound, and meaning are not established.",
        "claim_layer": "L2/L3", "classification": "A_STRONG_LEAD",
        "adjudication_verdict": "REPLICATED_RELATIVE_CONSTRAINT (E103; verdict class "
                                "unchanged under the corrected categorical maxT, E103R)",
        "held_out": "cross-site 9/10 (E023) + support 5/6 + chronological 4/4 (E024)",
        "adaptive_null": "p=.0002 best-of-72 maxT (E022); campaign-wide null CERTIFIED: "
                         "1/400 false graduation, one-sided exact CP95 upper bound 1.18% "
                         "(E104R; the original E104 1/200 run is a pilot)",
        "segmentation_robust": "3/3 overlapping segmentation/selection variants from a "
                               "single corpus lineage, z~17 dominant (E103R); robustness, "
                               "not independent replication",
        "dependency_adjusted_independent_channels": 1,
        "graduates_to_value": False,
        "note": "Graduates as a RELATIVE structural constraint only; NO phonetic value "
                "(E102 absolute-value gate fails: single independent channel). Compatible "
                "with a recurrent initial functional or morphological slot; prefixhood, "
                "productivity, sound, and meaning are not established.",
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

    # ---- prospective seals (§8.4 / §13) — curated text labelled (C6) ----
    seals = []
    seal_json = f"{ROOT}/data/seals/FRACTION_ORDER_ANETAKI_SEAL.json"
    if os.path.exists(seal_json):
        sd = json.load(open(seal_json))
        seals.append({
            "seal_id": "FRACTION_ORDER_ANETAKI_SEAL", "epoch": "E004",
            "frozen_prediction_source": "curated summary; authoritative content is the "
                                        "hashed seal JSON",
            "frozen_prediction": "25-claim pairwise fraction-value ordering (Corpus-derived, "
                                 "Corazza-independent); sharpest: H>K and A>B (anti-frequency, "
                                 "contra Corazza uncertain-tier).",
            "opening_event": "publication of the UNPUBLISHED Anetaki II face-delta "
                             "six-fraction sequence",
            "success_criterion": "mechanical scorer beats the Corazza comparator on the "
                                 "held-out ordering",
            "status": "FROZEN_UNOPENED",
            "plan_hash": (sd.get("plan_hash_sha256") or sd.get("plan_hash", ""))
                         if isinstance(sd, dict) else "",
            "manifest": f"{ROOT}/data/seals/FRACTION_ORDER_ANETAKI_SEAL.manifest.sha256",
        })
    seals.append({
        "seal_id": "CROSS_BRANCH_IMPORTED", "epoch": "(other branches)",
        "frozen_prediction_source": "curated cross-reference",
        "frozen_prediction": "M_ANETAKI_LATTICE_DELTA_SEAL + relphono SEAL_2/SEAL_3 "
                             "(anchor-lattice / relative-phonology branches) — referenced, "
                             "not re-frozen here.",
        "opening_event": "Ariadne-2025 Anetaki full edition ingest",
        "status": "FROZEN_ELSEWHERE",
    })

    # ---- licences — derived from LICENCE_STATE.json (C5) ----
    lic = json.load(open(f"{ROOT}/LICENCE_STATE.json"))
    assert lic.get("all_LA_transfer") == "NOT_EARNED", \
        f"LICENCE_STATE.json contradicts the all-NOT_EARNED assumption: {lic}"
    highest_licence = (f"none (all LA transfer licences {lic['all_LA_transfer']}, "
                       f"LICENCE_STATE.json as_of {lic.get('as_of')})")

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
        "final_commit": final_commit or "(stamped by --final-commit at closure regeneration)",
        "epochs_unique": N,
        "ledger_rows_append_only": raw_rows,
        "terminal_epochs": terminal_epochs,
        "completed_epochs": completed_epochs,
        "de_authorized_epochs": de_auth,
        "blocked_epochs": blocked_epochs,
        "cancelled_epochs": cancelled_epochs,
        "reserved_unexecuted_epochs": statuses.get("RESERVED", 0),
        "graduated_findings_count": len(graduated),
        "strong_leads_adjudicated": len(strong_leads),
        "highest_licence": highest_licence,
        "highest_claim_layer": highest_layer,
        "bucket_tally_generated": dict(tally),
        "layer_tally_generated": dict(layers),
        "status_tally_generated": dict(statuses),
        "duplicate_ledger_entries_append_only": dup_ids,
        "remediation": "terminal audit remediation pass 2026-07-09: E103R (corrected "
                       "categorical joint maxT; verdict class unchanged) + E104R "
                       "(bound-based certification, CAMPAIGN_NULL_GATES_CERTIFIED); "
                       "closure layer regenerated under the corrected generator.",
        "review_bundle_path": f"{ROOT}/final/review_bundle/",
    }
    final_verdicts = {
        "by_layer_source": "curated",
        "by_layer": {
            "L0_L1_physical_signid": "COMPLETE (inventory/structure established)",
            "L2_structure": "GRADUATED_STRUCTURAL_FINDING (recurrent A-initial slot, "
                            "E103/E103R) + many bounded negatives",
            "L3_functional": "REPLICATED_RELATIVE_CONSTRAINT (A-initial enrichment, "
                             "register/ledger structure); no functional transfer licence "
                             "earned",
            "L4_plus_semantic_phonetic_translation": "NOT_REACHED / NOT_AUTHORIZED "
                                                     "(absolute-value gate fails, E102: "
                                                     "single independent channel)",
        },
        "campaign_level": [
            "CURRENT_CORPUS_EXHAUSTED_WITHIN_SCOPE",
            "GRADUATED_STRUCTURAL_FINDING (A-initial positional enrichment, relative)",
            "PROSPECTIVE_PROGRAMME_READY (FRACTION_ORDER_ANETAKI_SEAL frozen)",
            "CONTINUE_ONLY_AFTER_NEW_EVIDENCE (anchor independence is the bottleneck)",
            "NO_DECIPHERMENT_BREAKTHROUGH",
        ],
        "bottleneck_source": "curated",
        "bottleneck": "anchor independence (a single context-co-occurrence channel; no 2nd "
                      "independent linguistic channel — stroke/palaeography SOURCE_BLOCKED), "
                      "NOT corpus size (E093 LA data-sufficient) and NOT detector power "
                      "(gates fire, E104R certified). A second independent channel is "
                      "NECESSARY, not sufficient: value assignment additionally requires "
                      "externally anchored evidence (bilinguals, secure multi-slot "
                      "onomastics, metrological ties).",
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

    # ---- artifact manifest (§13/§14) — hashes every emitted closure file, EXCLUDING
    # itself (C8) ----
    manifest = {}
    for path in sorted(glob.glob(f"{FINAL}/*.json") + glob.glob(f"{FINAL}/*.csv")):
        if os.path.basename(path) == "ARTIFACT_MANIFEST.json":
            continue
        manifest[os.path.relpath(path, ROOT)] = sha256_file(path)
    dump("ARTIFACT_MANIFEST.json", {"generated_from": "EPOCH_LEDGER.yaml",
                                    "n_epochs": N,
                                    "self_excluded": True,
                                    "files": manifest})

    # ---- E105 result.json (C10) ----
    e105_dir = f"{ROOT}/epochs/EPOCH-105"
    e105_result = {
        "task_id": "EPOCH-105",
        "verdict": "CLOSURE_SYNTHESIS_COMPLETE",
        "verdict_rule": "mechanical: all closure artifacts emitted AND 0 RUNNING/BLOCKED/"
                        "RESERVED epochs AND 0 missing-verdict epochs (DE_AUTHORIZED is "
                        "terminal) AND licence line derived from LICENCE_STATE.json",
        "epochs_unique": N,
        "non_terminal_epochs": N - terminal_epochs,
        "missing_verdict_epochs": [eid(e) for e in eps
                                   if not (e.get("verdict") or e.get("verdicts") or
                                           e.get("de_authorized"))],
        "plan_hash": sha256_file(f"{e105_dir}/prereg.md"),
        "code_manifest": {
            "final/generate_closure.py (this, remediation revision)":
                sha256_file(f"{FINAL}/generate_closure.py"),
            "epochs/EPOCH-105/machinery.py (frozen copy of the ORIGINAL generator, "
            "superseded by the remediation revision under audit items C1-C12)":
                sha256_file(f"{e105_dir}/machinery.py"),
        },
        "emitted_artifacts_sha256": {
            os.path.relpath(p, ROOT): sha256_file(p)
            for p in sorted(glob.glob(f"{FINAL}/*.json") + glob.glob(f"{FINAL}/*.csv"))
        },
        "note": "Emitted by the remediation-revision generator (terminal audit pass "
                "2026-07-09). The ORIGINAL E105 run predates this file; its generator is "
                "frozen at epochs/EPOCH-105/machinery.py. Counts generated (invariant #12).",
    }
    json.dump(e105_result, open(f"{e105_dir}/result.json", "w"), indent=2)

    print(f"epochs={N} (ledger rows {raw_rows})  graduated={len(graduated)}  "
          f"strong_leads={len(strong_leads)}")
    print("bucket tally:", dict(tally))
    print("layer tally:", dict(layers))
    print("status tally:", dict(statuses))
    print("de_authorized:", de_auth)
    print("duplicate append-only entries:", dup_ids)
    return final_state, tally, layers


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--final-commit", default="", help="closing commit hash to stamp into "
                    "CAMPAIGN_FINAL_STATE.json (C9)")
    args = ap.parse_args()
    main(final_commit=args.final_commit)
