#!/usr/bin/env python3
"""G1 — EXISTING ANCHOR AUDIT.

Audits the Foundry 115-record / 62-sign LA anchor inventory
(experiments/linear_a_foundry/data/wp5_anchor_inventory_records.csv +
 wp5_anchor_inventory_signs.csv), enriched with per-record provenance detail from the
cross-script gate census/toponym CSVs. For every anchor record it records the twelve audit
fields (source, page/record, chronology, geography, dependency class, candidate LA locus,
matching slots, rule complexity, quality tier, prior exposure, held-out prediction, failure
status), then DE-DUPLICATES:

  (1) exact record duplicates,
  (2) dependency clones — records that descend from ONE root lineage (one GORILA/Younger/
      Salgarella source, or one external referent read the identical way),

and reports the de-duplicated independent-anchor count at several honest granularities.

Deterministic. Non-circular: no LA phonetic value is used as a model input; conventional
values only label records. Writes reports/G_EXISTING_ANCHOR_AUDIT.md + data/anchors_v2/audit.json.
"""
from __future__ import annotations
import csv, json, os, re
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.abspath(os.path.join(HERE, ".."))
FOUNDRY = os.path.abspath(os.path.join(CAMP, "..", "linear_a_foundry"))
GATE = "/home/claude-runner/gitlab/n8n/logos-la-lb-continuity/experiments/crossscript_gate"

REC_CSV   = os.path.join(FOUNDRY, "data", "wp5_anchor_inventory_records.csv")
SIGN_CSV  = os.path.join(FOUNDRY, "data", "wp5_anchor_inventory_signs.csv")
INV_JSON  = os.path.join(FOUNDRY, "data", "wp5_anchor_inventory.json")
CENSUS    = os.path.join(GATE, "phase2", "anchor_census.csv")

OUT_DATA  = os.path.join(CAMP, "data", "anchors_v2")
OUT_REP   = os.path.join(CAMP, "reports")
os.makedirs(OUT_DATA, exist_ok=True); os.makedirs(OUT_REP, exist_ok=True)

# ---------------------------------------------------------------- load ----
records = list(csv.DictReader(open(REC_CSV)))
signs   = list(csv.DictReader(open(SIGN_CSV)))
census  = {r["anchor_id"]: r for r in csv.DictReader(open(CENSUS))}
inv     = json.load(open(INV_JSON))
frozen  = inv["summary"]["frozen_empirical_held_out"]

# LA find-site abbreviation -> geography (Neopalatial Crete unless noted)
SITE_GEO = {
    "HT": "Haghia Triada (S-central Crete)", "ZA": "Zakros (E Crete)",
    "Za": "Zakros (E Crete)", "PH": "Phaistos (S-central Crete)",
    "KO": "Kophinas (S-central Crete)", "TH": "Thera/Akrotiri (Cyclades)",
    "PK": "Palaikastro (E Crete)", "KN": "Knossos (N-central Crete)",
}
# root dependency LINEAGE per record. A lineage = one source+method chain from which the
# record's value inherits. Records sharing a lineage are dependency clones of each other.
def lineage_of(rec, cen):
    ch, cls = rec["channel"], rec["class"]
    if ch == "H_homomorphy":
        return "LIN-H:Salgarella2020-homomorphy(=GORILA shape-transcription substrate)"
    if ch == "C_cypriot":
        return "LIN-C:S&M2017-Table6.2-Cypriot-stability"
    if cls == "personal_name":
        return "LIN-PN:Hooker1975/S&M-onomastic-resemblance-table"
    if cls == "gloss_acrophonic":
        return "LIN-GLOSS:acrophonic-single-sign"
    if cls == "variation_constraint":
        return "LIN-VAR:S&M2017-§5-internal-LA-variation"
    if cls == "toponym":
        # collapse toponyms by DISTINCT external referent (the place)
        return "LIN-TOP:" + referent_of(rec, cen)
    return "LIN-?"

# map toponym record -> canonical external referent (place). Tylissos appears twice.
REFERENT = {
    "top_pa_i_to": "Phaistos", "top_se_to_i_ja": "se-to-i-ja(unlocated)",
    "top_tu_ru_sa": "Tylissos", "top_a_tu_ri_si_ti": "Tylissos",   # <- clone of tu_ru_sa
    "top_di_ki_te": "Mt-Dikte", "top_su_ki_ri_ta": "Sybrita",
    "top_i_da_a_cf": "Mt-Ida", "top_ku_79_ni_younger": "Kydonia",
    "top_da_u_49_younger": "da-wo(minor-locality)", "top_i_ti_ni_sa_younger": "Itanos",
    "top_ku_ni_su_younger": "ku-ni-su(unlocated)", "top_ku_ta_younger": "ku-ta-to(bare-cf)",
    "top_sa_ra2_younger": "Ayia-Triada(inferential)", "top_di_na_u_younger": "di-na-u(unlocated)",
    "top_i_na_ta_i_zu_di_si_ka_younger": "Inatos(hedged)",
}
def referent_of(rec, cen):
    return REFERENT.get(rec["record_id"], rec["record_id"])

# firmness of a toponym equation (from census sm_trust + citation status)
FIRM_PRIMARY_TOPO = {"top_pa_i_to","top_se_to_i_ja","top_tu_ru_sa","top_di_ki_te","top_su_ki_ri_ta"}
HEDGED_OR_CF = {"top_i_da_a_cf","top_ku_79_ni_younger","top_ku_ta_younger","top_sa_ra2_younger",
                "top_i_na_ta_i_zu_di_si_ka_younger"}

def chronology(rec):
    # LA anchors are Neopalatial (MM III–LM IB, ~1600–1450 BCE); LB comparanda are
    # Mycenaean (Knossos LM II–IIIA / mainland LM IIIB, ~1400–1200 BCE). The value inheritance
    # therefore runs BACKWARD in time (younger LB used to read older LA) — recorded, not scored.
    if rec["channel"] == "C_cypriot":
        return "LA Neopalatial (~1600-1450 BCE) <- via LB <- Cypriot syll. (1st mill. BCE)"
    return "LA Neopalatial (MM III-LM IB, ~1600-1450 BCE); comparandum LB Mycenaean (~1400-1200 BCE)"

def rule_complexity(rec, cen, n_slots):
    # how many free sign->value assignments the equation asserts at once
    if rec["class"] == "variation_constraint":
        return {"n_value_assignments": 0, "note": "series-membership only; asserts no value (ic4)"}
    return {"n_value_assignments": n_slots,
            "note": "one LB value asserted per covered sign simultaneously"}

# prior exposure: every anchor here is drawn from published print/web scholarship pre-dating
# the campaign, so all are PUBLIC/EXPOSED. Younger web pages are the most exposed.
def prior_exposure(rec):
    if "younger" in rec["record_id"]:
        return "PUBLIC-WEB (Younger LA pages, archived Wayback; heavily indexed)"
    return "PUBLIC-PRINT (Steele&Meissner 2017 CUP / Salgarella 2020 CUP; indexed)"

# held-out prediction + failure status come from the FROZEN cross-script gate (cited, not re-run)
LOTO_RECOVERED = set(frozen["recovered_signs_LOTO"])  # {'I','RI'}
def heldout(rec):
    covered = [s for s in rec["covered_signs"].split("|") if s]
    hit = sorted(set(covered) & LOTO_RECOVERED)
    if rec["channel"] in ("H_homomorphy", "C_cypriot"):
        pred = "none (sign-IDENTITY channel; inherits LB value, derives none)"
        fail = "N/A_NO_VALUE_DERIVED (structural corroboration only)"
    elif rec["class"] == "variation_constraint":
        pred = "none (series-membership; never pins a value)"
        fail = "N/A_NEVER_PINS"
    else:
        pred = "if value correct, held-out LA distribution should re-derive it (LOTO)"
        if hit:
            fail = f"RECOVERED_BUT_ONE-TOPONYM-DEEP ({','.join(hit)}); non-survivable if that toponym also held out"
        else:
            fail = "REFUTE_LOTO_FRAGILE (not recovered; distributional channel=0.0000)"
    return pred, fail, hit

# ---------------------------------------------------------- per-record ----
audit_rows = []
for rec in records:
    rid = rec["record_id"]
    cen = census.get(rid, {})
    covered = [s for s in rec["covered_signs"].split("|") if s]
    n_slots = len(covered)
    # geography from LA find-site in census identification
    sites = re.findall(r'LA\s+([A-Z][A-Za-z]?)', cen.get("identification","")) if cen else []
    geo = SITE_GEO.get(sites[0], "Crete (find-site not pinned in source)") if sites else \
          ("cross-Aegean sign continuity" if rec["channel"] in ("H_homomorphy","C_cypriot")
           else "Crete (find-site not pinned in source)")
    pred, fail, hit = heldout(rec)
    audit_rows.append({
        "record_id": rid,
        "source": rec["provenance"],
        "page_record": cen.get("citation", rec["provenance"]),
        "chronology": chronology(rec),
        "geography": geo,
        "channel": rec["channel"],
        "class": rec["class"],
        "dependency_class": lineage_of(rec, cen),
        "candidate_la_locus": cen.get("la_signs", rec["covered_signs"]),
        "covered_signs": covered,
        "matching_slots": n_slots,
        "rule_complexity": rule_complexity(rec, cen, n_slots),
        "quality_tier": rec["tier"],
        "sm_trust": rec["sm_trust"],
        "source_status": rec["source_status"],
        "prior_exposure": prior_exposure(rec),
        "heldout_prediction": pred,
        "failure_status": fail,
        "loto_recovered_signs": hit,
    })

# ------------------------------------------------------------- dedup ------
# (1) exact duplicates: identical (channel, covered_signs) OR identical record_id
seen, exact_dups = {}, []
for r in audit_rows:
    key = (r["channel"], tuple(r["covered_signs"]))
    if key in seen:
        exact_dups.append({"record_id": r["record_id"], "duplicate_of": seen[key]})
    else:
        seen[key] = r["record_id"]

# (2) dependency-lineage collapse
by_lineage = defaultdict(list)
for r in audit_rows:
    by_lineage[r["dependency_class"]].append(r["record_id"])
n_root_lineages = len(by_lineage)

# toponym referent collapse (clones within LIN-TOP)
topo_rows = [r for r in audit_rows if r["class"] == "toponym"]
topo_by_ref = defaultdict(list)
for r in topo_rows:
    topo_by_ref[REFERENT[r["record_id"]]].append(r["record_id"])
topo_clone_collapses = {ref: ids for ref, ids in topo_by_ref.items() if len(ids) > 1}
n_distinct_topo_referents = len(topo_by_ref)

# ------------------------------------------------- independence tiers -----
# TIER A  value-BEARING & independent-referent & FIRM-PRIMARY & de-cloned toponym equations
tierA = sorted({REFERENT[r] for r in FIRM_PRIMARY_TOPO})               # de-cloned firm places
# TIER B  all distinct external referents (incl. hedged/cf/secondary), de-cloned
tierB = sorted(topo_by_ref.keys())
# value-INHERITING lineages (H,C) contribute 0 independent VALUE anchors
value_inheriting = [l for l in by_lineage if l.startswith(("LIN-H","LIN-C"))]
# value-BLIND resemblance / never-pin lineages (PN, GLOSS, VAR) contribute ~0 held-out value
value_blind = [l for l in by_lineage if l.startswith(("LIN-PN","LIN-GLOSS","LIN-VAR"))]

# EMPIRICAL held-out-survivable independent anchors (the only count that decides a reading)
# frozen gate: LOTO recovered only {I,RI}, each ONE-toponym-deep, distributional channel 0.0000
n_heldout_survivable = 0     # one-toponym-deep pins are NOT survivable once the toponym is held out
loto_recovered_one_deep = sorted(LOTO_RECOVERED)

# ------------------------------------------------------------- write ------
summary = {
    "raw_provenance_records": len(records),
    "raw_signs_touched": len(signs),
    "exact_duplicate_records": len(exact_dups),
    "exact_duplicate_detail": exact_dups,
    "n_root_dependency_lineages": n_root_lineages,
    "records_per_lineage": {l: len(v) for l, v in sorted(by_lineage.items())},
    "channel_is_value_bearing": {
        "LIN-TOP (toponym external referent)": "YES - only channel that derives a value from outside LB",
        "LIN-PN (onomastic resemblance)": "NO - value-blind; no external referent constrains the string",
        "LIN-GLOSS (acrophonic)": "WEAK - single-sign guess, not held-out testable",
        "LIN-VAR (internal variation)": "NO - never pins a value by construction (ic4)",
        "LIN-H (homomorphy)": "NO - sign-IDENTITY; inherits LB value (this IS the GORILA transcription substrate)",
        "LIN-C (Cypriot stability)": "NO - sign continuity; inherits LB/Greek value",
    },
    "n_value_inheriting_lineages": len(value_inheriting),
    "n_value_blind_or_neverpin_lineages": len(value_blind),
    "toponym_channel": {
        "raw_toponym_records": len(topo_rows),
        "distinct_external_referents_after_declone": n_distinct_topo_referents,
        "clone_collapses": topo_clone_collapses,
        "firm_primary_unqueried_referents": tierA,
        "n_firm_primary_unqueried_referents": len(tierA),
        "hedged_or_cf_only_referents": sorted(REFERENT[r] for r in HEDGED_OR_CF),
    },
    "DEDUP_HEADLINE": {
        "independent_anchor_count__tierA_firm_primary_declone": len(tierA),
        "independent_anchor_count__tierB_all_distinct_referents": len(tierB),
        "independent_VALUE_bearing_lineages": 1,
        "empirical_heldout_survivable_independent_anchors": n_heldout_survivable,
        "loto_recovered_one_toponym_deep": loto_recovered_one_deep,
        "gate_verdict": frozen["verdict"],
        "distributional_channel_top1": frozen["distributional_channel_top1"],
    },
    "frozen_gate_citation": {k: frozen[k] for k in
        ("verdict","distributional_channel_top1","recovered_signs_LOTO","recovered_depth","prereg_dois")},
    "non_circular_note": "Conventional LA values label records only; no value is a model input. "
                         "Held-out numbers are cited from the frozen preregistered cross-script gate, not re-run.",
}
out = {"task": "G1_existing_anchor_audit", "seed": 20260708, "summary": summary,
       "audit_rows": audit_rows}
json.dump(out, open(os.path.join(OUT_DATA, "audit.json"), "w"), indent=1)

# ---- console echo (real numbers) ----
print("raw records:", len(records), "| signs touched:", len(signs))
print("exact duplicate records:", len(exact_dups), exact_dups)
print("root dependency lineages:", n_root_lineages)
for l, v in sorted(by_lineage.items()): print("   ", l, "->", len(v), "records")
print("toponym raw:", len(topo_rows), "| distinct referents:", n_distinct_topo_referents)
print("toponym clone collapses:", topo_clone_collapses)
print("TIER-A firm-primary de-cloned referents:", len(tierA), tierA)
print("TIER-B all distinct referents:", len(tierB))
print("value-bearing lineages:", 1, "| value-inheriting:", len(value_inheriting),
      "| value-blind/never-pin:", len(value_blind))
print("EMPIRICAL held-out-survivable independent anchors:", n_heldout_survivable)
print("LOTO recovered (one-toponym-deep):", loto_recovered_one_deep,
      "| gate verdict:", frozen["verdict"], "| distributional top1:", frozen["distributional_channel_top1"])
print("wrote", os.path.join(OUT_DATA, "audit.json"))
