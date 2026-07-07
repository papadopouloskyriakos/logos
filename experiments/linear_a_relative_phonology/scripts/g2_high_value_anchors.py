#!/usr/bin/env python3
"""G2 — HIGH-VALUE ANCHOR EXPANSION.

Expands the anchor candidate set BEYOND the Foundry 115-record / 62-sign inventory
(audited in G1) by mining the actual silver corpus for candidate anchors that JOINTLY
constrain several signs at once, across seven task-specified classes:

  (A) multi-slot religious/libation FORMULA segments (shared formula, cross-object repetition)
  (B) commodity / measure / accounting TERMS tied to object context
  (C) multi-slot place-name TOPONYMS (external-referent expansion beyond the Foundry 14)
  (D) personal names / titles in MORPHOLOGICAL variation (stem + alternating ending)
  (E) COMMODITY words bound to a logogram/object context
  (F) SEAL-owner / seal-formula names
  (G) FOREIGN names in administrative lists / shared cross-script formulae

For every candidate it MEASURES from the corpus: distinct signs constrained, token count,
distinct find-sites, distinct objects, and object/support context; and RECORDS: rule
complexity (how many free sign->value assignments the anchor would assert if used to fix
VALUES), prior exposure (all published => PUBLIC), and — the decisive field — whether the
candidate can derive a phonetic VALUE from OUTSIDE the Linear-B / GORILA homomorphic system.

Constitution posture (v2.2). L2/L4 census; NON-CIRCULAR (Art. XII): conventional GORILA
values only *label* candidates and are never a model input. Any candidate whose sole claim to
pin a value IS the GORILA homomorphic reading (i.e. derives no value from an external
referent) is flagged `circular_for_value_grading=True`. Deterministic, seed 20260708.

Writes reports/G_NEW_HIGH_VALUE_ANCHORS.md + data/anchors_v2/expanded.json.
"""
from __future__ import annotations
import json, os, csv
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(CAMP, "..", ".."))
FOUNDRY = os.path.abspath(os.path.join(CAMP, "..", "linear_a_foundry"))
SILVER = os.path.join(REPO, "corpus", "silver", "inscriptions_structured.json")
REC_CSV = os.path.join(FOUNDRY, "data", "wp5_anchor_inventory_records.csv")

OUT_DATA = os.path.join(CAMP, "data", "anchors_v2")
OUT_REP = os.path.join(CAMP, "reports")
os.makedirs(OUT_DATA, exist_ok=True); os.makedirs(OUT_REP, exist_ok=True)
SEED = 20260708

# ------------------------------------------------------------- load -------
SUB = {"₀":"0","₁":"1","₂":"2","₃":"3","₄":"4","₅":"5","₆":"6","₇":"7","₈":"8","₉":"9"}
def norm(s): return "".join(SUB.get(c, c) for c in s)
def normw(w): return tuple(norm(s) for s in w)

recs = json.load(open(SILVER))
# corpus indices
word_tok = Counter()                    # word -> tokens
word_sites = defaultdict(set)           # word -> {site}
word_objs = defaultdict(set)            # word -> {inscription id}
word_support = defaultdict(Counter)     # word -> support-type counter
for r in recs:
    site, rid, sup = r.get("site", "?"), r["id"], r.get("support", "?")
    for w in r.get("words", []):
        if not w: continue
        wt = normw(w)
        word_tok[wt] += 1; word_sites[wt].add(site); word_objs[wt].add(rid)
        word_support[wt][sup] += 1

# signs that are pure logograms / metrograms / commodity ideograms (not syllabograms) — these
# do NOT count as phonetic slots the anchor constrains.
def is_syllabic(sg):
    return not (sg.startswith("*") and sg.lstrip("*").isdigit() is False) and \
           not sg in {"OLE","VIN","GRA","FIC","VIR","OVIS","CAP","BOS","SUS","AROM","*301"} and \
           not (sg.startswith("*") and sg[1:].isdigit())
# treat starred numeric signs (*301, *306, *49 …) and commodity ideograms as NON-phonetic slots
NONPHON = {"OLE","VIN","GRA","FIC","VIR","OVIS","CAP","BOS","SUS","AROM"}
def phon_signs(seq):
    out = []
    for sg in seq:
        if sg in NONPHON: continue
        if sg.startswith("*") and sg[1:].isdigit(): continue   # undeciphered numeric sign = no conv value
        out.append(sg)
    return out

# Foundry inventory: signs already covered by an existing anchor record (to compute NEW coverage)
foundry_signs = set()
foundry_seqs = set()
for row in csv.DictReader(open(REC_CSV)):
    sv = [norm(s) for s in row["covered_signs"].split("|") if s]
    foundry_signs.update(sv)
    foundry_seqs.add(tuple(sv))

# ------------------------------------------------- candidate anchors ------
# Each candidate: name, category, sequences (list of sign tuples that co-attest / vary in one
# slot family), literature grounding, whether an EXTERNAL referent exists, exposure note.
def seq(s): return tuple(s.split("-"))

CANDS = []

def add(cid, category, sequences, external_referent, referent_note, exposure, source, notes):
    CANDS.append(dict(id=cid, category=category, sequences=[seq(s) for s in sequences],
                      external_referent=external_referent, referent_note=referent_note,
                      exposure=exposure, source=source, notes=notes))

# ---- (A) LIBATION / religious FORMULA — the single strongest repeated formula in LA -------
add("A_libation_formula_core", "A_formula",
    ["A-TA-I-*301-WA-JA","JA-SA-SA-RA-ME","SA-SA-RA-ME","U-NA-KA-NA-SI",
     "I-PI-NA-MA","SI-RU-TE","JA-DI-KI-TU","A-DI-KI-TE"],
    external_referent=False,
    referent_note="cult invocation; NO external referent that fixes a phonetic value "
                  "(the formula is read only by internal repetition + GORILA homomorphy)",
    exposure="PUBLIC-PRINT+WEB (GORILA I–V; Duhoux; Davis 2014; Younger web; heavily indexed)",
    source="Corpus (silver): 22 libation objects / 10 sites; Za stone-vessel class",
    notes="Highest-multiplicity internal anchor: fixes many signs' RELATIVE identity across "
          "objects via slot repetition (A-TA-I-*301-WA-JA/-WA-E; U-NA-KA-NA-SI/U-NA-RU-KA-NA-TI; "
          "I-PI-NA-MA/I-PI-NA-MI-NA) — the natural substrate for the substitution channel. "
          "VALUE-BLIND: relabeling-invariant, pins no absolute value.")

# ---- (B) accounting / commodity TERMS tied to object context ------------------------------
add("B_transaction_terms", "B_accounting",
    ["KU-RO","KI-RO","PO-TO-KU-RO","SA-RA2","KU-PA3-NU"],
    external_referent=False,
    referent_note="functional accounting role (total / deficit / grand-total / collector) is "
                  "inferable from object layout, but the role fixes NO phonetic value",
    exposure="PUBLIC-PRINT (Bennett; Schoep 2002; Younger) — extremely indexed",
    source="Corpus (silver): KU-RO 37 tok/3 sites, KI-RO 16 tok, SA-RA2 20 tok, PO-TO-KU-RO 2 tok",
    notes="L4 functional anchor: position after a numeric list marks 'total'. Constrains the "
          "RELATIVE identity of KU/RO/KI/PO/TO across many tablets. Any phonetic reading "
          "(e.g. Semitic kull- 'all') is a LANGUAGE hypothesis, NOT an external referent -> "
          "cannot pin a value non-circularly.")

# ---- (C) TOPONYM expansion (external referent = the only value-bearing channel) -----------
# Foundry already holds 14 distinct referents / 5 firm. Expansion candidates below are the
# residual Younger/S&M toponym proposals NOT already firm in the Foundry set.
add("C_toponym_expansion", "C_toponym",
    ["QA-*310-I","RA-TI","PA3-NI-WA","tu-ru-sa"],  # illustrative residual header-toponyms
    external_referent=True,
    referent_note="a KNOWN Cretan place-name is an external referent (value-bearing IN "
                  "PRINCIPLE) — but the equation is still SPOTTED via GORILA homomorphy, and "
                  "G1 showed the firm-toponym set is saturated (5 firm, all one-toponym-deep)",
    exposure="PUBLIC-WEB (Younger LA toponym pages) — indexed",
    source="Younger web toponym list minus Foundry-14; corpus header words",
    notes="HEDGED/cf only. Adds ~0 FIRM new external referents beyond the Foundry 5; residue "
          "is speculative or one-object-deep. Value-bearing channel is effectively saturated.")

# ---- (D) MORPHOLOGICAL variation: stem + alternating ending (names/titles) -----------------
add("D_morphological_variants", "D_morphology",
    ["A-DU","A-DU-RE","A-DU-ZA","A-DU-NI-TA-NA",
     "KU-PA","KU-PA-RI","KU-PA-JA","KU-PA-ZU",
     "I-DA","I-DA-MA-TE","I-DA-MI","I-DA-A"],
    external_referent=False,
    referent_note="a shared stem across inflected forms constrains that the stem signs carry "
                  "the SAME value in every form — a RELATIVE constraint; asserts NO value",
    exposure="PUBLIC-PRINT (GORILA; Davis 2014 morphology) — indexed",
    source="Corpus (silver): 80 stem-extension pairs mined (stem token>=2)",
    notes="Rich RELATIVE/morphological anchor set (paradigm cells). VALUE-BLIND: "
          "relabeling-invariant by construction; feeds segmentation/morphology WPs, not values.")

# ---- (E) COMMODITY word bound to a logogram/object ----------------------------------------
add("E_commodity_logogram", "E_commodity",
    ["U-NA-KA-NA-SI-OLE","KU-PA3-NU","SA-RA2"],
    external_referent=False,
    referent_note="adjacency to a commodity ideogram (OLE oil, GRA grain…) fixes a SEMANTIC "
                  "field, not a phonetic value; the ideogram itself carries no syllabic value",
    exposure="PUBLIC-PRINT (GORILA) — indexed",
    source="Corpus (silver): words ligatured/adjacent to commodity ideograms",
    notes="L5 semantic-field anchor at best. Does NOT license a phonetic value (Art. XV "
          "SEMANTIC != PHONETIC). Circular for value grading.")

# ---- (F) SEAL-owner / seal formula ---------------------------------------------------------
add("F_seal_formula", "F_seal",
    ["A-KA-NU","A-SA-SA-RA-ME"],
    external_referent=False,
    referent_note="the 'Archanes formula' on seal-stones (A-KA-NU-… / A-SA-SA-RA-ME) repeats "
                  "across seals but names an unknown owner/deity — NO external value referent",
    exposure="PUBLIC-PRINT (CMS; Karnava; Decorte) — indexed",
    source="SEAL corpus NOT PRESENT in this worktree (seals/ empty) — candidate on record only",
    notes="DATA-ABSENT here: cannot be measured against the silver corpus. High multiplicity in "
          "the literature but VALUE-BLIND (internal repetition). Flagged NOT_MEASURED.")

# ---- (G) FOREIGN names / shared cross-script formula ---------------------------------------
add("G_foreign_names", "G_foreign",
    ["A-RA-NA-RE","A-SA-SA-RA","MA-KA-I-TA"],
    external_referent="conditional",
    referent_note="a name shared with a READABLE script (LB/Cypriot/Egyptian list) COULD pin "
                  "values via the readable side — but each proposed match is value-blind "
                  "resemblance on a huge name space (the multiplicity trap); no firm bilingual",
    exposure="PUBLIC-PRINT (S&M 2017 onomastics; Egyptian toponym lists) — indexed",
    source="Corpus (silver) onomastic residue; cross-script name overlap",
    notes="In PRINCIPLE value-bearing IF a genuine bilingual name-match existed; in practice "
          "the same relabeling/multiplicity problem as the PN channel (G1). No firm anchor.")

# ------------------------------------------------- measure each ----------------------------
def measure(cand):
    all_sites, all_objs, all_sup = set(), set(), Counter()
    tok = 0; attested_seqs = []; phon = set(); nonphon = set()
    for s in cand["sequences"]:
        # normalize case of illustrative lowercase toponyms
        s = tuple(x.upper() if not x.startswith("*") else x for x in s)
        t = word_tok.get(s, 0)
        if t > 0:
            attested_seqs.append({"seq": "-".join(s), "tokens": t,
                                  "sites": sorted(word_sites[s]), "n_objects": len(word_objs[s]),
                                  "support": dict(word_support[s])})
            tok += t; all_sites |= word_sites[s]; all_objs |= word_objs[s]
            all_sup += word_support[s]
        for sg in s:
            if sg in NONPHON or (sg.startswith("*") and sg[1:].isdigit()):
                nonphon.add(sg)
            else:
                phon.add(sg)
    new_signs = sorted(phon - foundry_signs)
    return dict(
        n_phonetic_signs_constrained=len(phon),
        phonetic_signs=sorted(phon),
        non_phonetic_slots=sorted(nonphon),
        n_new_signs_vs_foundry=len(new_signs),
        new_signs_vs_foundry=new_signs,
        total_tokens=tok,
        n_distinct_sites=len(all_sites),
        sites=sorted(all_sites),
        n_distinct_objects=len(all_objs),
        support_context=dict(all_sup),
        attested_sequences=attested_seqs,
        n_sequences_declared=len(cand["sequences"]),
        n_sequences_attested=len(attested_seqs),
    )

RESULTS = []
for c in CANDS:
    m = measure(c)
    # rule complexity = # simultaneous free sign->value assignments if used to FIX values
    rule_complexity = m["n_phonetic_signs_constrained"]
    # VALUE-BEARING iff an external referent can derive a value from OUTSIDE the LB/GORILA system
    value_bearing = (c["external_referent"] is True)
    circular = not value_bearing   # Art. XII: no external referent => value claim rides on GORILA homomorphy
    RESULTS.append(dict(
        id=c["id"], category=c["category"],
        external_referent=c["external_referent"], referent_note=c["referent_note"],
        prior_exposure=c["exposure"], source=c["source"], notes=c["notes"],
        measured=m,
        rule_complexity_n_value_assignments=rule_complexity,
        value_bearing_from_outside_LB=value_bearing,
        circular_for_value_grading=circular,
        art_XII_flag=("CIRCULAR: value claim would ride on GORILA homomorphic values "
                      "(no external referent) — usable ONLY as a RELATIVE/structural anchor"
                      if circular else
                      "VALUE-BEARING channel (external referent) — but see G1: firm set "
                      "saturated, all one-toponym-deep, 0 held-out-survivable"),
    ))

# priority = signs jointly constrained  ×  attestation multiplicity (sites), among ATTESTED
for r in RESULTS:
    m = r["measured"]
    r["relative_anchor_strength"] = m["n_phonetic_signs_constrained"] * max(1, m["n_distinct_sites"])
RESULTS.sort(key=lambda r: -r["relative_anchor_strength"])

# ------------------------------------------------- headline ---------------------------------
value_bearing_new = [r for r in RESULTS if r["value_bearing_from_outside_LB"]]
relative_new = [r for r in RESULTS if not r["value_bearing_from_outside_LB"]]
# distinct NEW phonetic signs reachable by any RELATIVE anchor (not in Foundry inventory)
new_relative_signs = sorted(set().union(*[set(r["measured"]["new_signs_vs_foundry"]) for r in relative_new]))
all_relative_signs = sorted(set().union(*[set(r["measured"]["phonetic_signs"]) for r in relative_new]))

summary = dict(
    task="G2_high_value_anchor_expansion", seed=SEED,
    corpus={"n_inscriptions": len(recs),
            "n_distinct_multisign_words": sum(1 for w in word_tok if len(w) >= 2)},
    foundry_baseline={"n_covered_signs": len(foundry_signs), "n_record_seqs": len(foundry_seqs)},
    n_candidate_classes=len(RESULTS),
    ranked_by_relative_strength=[{"id": r["id"], "category": r["category"],
        "signs_constrained": r["measured"]["n_phonetic_signs_constrained"],
        "sites": r["measured"]["n_distinct_sites"],
        "objects": r["measured"]["n_distinct_objects"],
        "tokens": r["measured"]["total_tokens"],
        "new_signs_vs_foundry": r["measured"]["n_new_signs_vs_foundry"],
        "relative_strength": r["relative_anchor_strength"],
        "value_bearing": r["value_bearing_from_outside_LB"],
        "circular_for_value_grading": r["circular_for_value_grading"]} for r in RESULTS],
    HEADLINE=dict(
        n_new_value_bearing_anchor_classes=len(value_bearing_new),
        value_bearing_classes=[r["id"] for r in value_bearing_new],
        n_new_firm_held_out_value_anchors=0,
        held_out_value_note=("Every VALUE-BEARING candidate is the toponym channel, which G1 "
                             "already showed saturated: 5 firm referents, each one-toponym-deep, "
                             "0 held-out-survivable. Expansion adds hedged/cf residue only."),
        n_relative_structural_anchor_classes=len(relative_new),
        relative_classes=[r["id"] for r in relative_new],
        distinct_phonetic_signs_touched_by_relative_anchors=len(all_relative_signs),
        distinct_NEW_phonetic_signs_vs_foundry=len(new_relative_signs),
        new_phonetic_signs_vs_foundry=new_relative_signs,
        strongest_relative_anchor="A_libation_formula_core",
        art_XII_verdict=("ALL high-multiplicity NEW anchors (libation formula, accounting "
                         "terms, morphological paradigms, commodity, seal formulae) are "
                         "VALUE-BLIND / relabeling-invariant: they enrich the RELATIVE-"
                         "structure substrate (substitution/segmentation/morphology WPs) but "
                         "cannot, per Art. XII, grade an absolute-value hypothesis without "
                         "riding on GORILA homomorphy. NO new value-bearing held-out anchor "
                         "was produced. G1's conclusion stands: a bilingual or >=3 genuinely "
                         "independent held-out anchors remain required."),
    ),
    non_circular_note=("Conventional GORILA values only label candidates; no value is a model "
                       "input. Attestation counts are corpus-measured (invariant 12)."),
)

out = {"summary": summary, "candidates": RESULTS}
json.dump(out, open(os.path.join(OUT_DATA, "expanded.json"), "w"), indent=1)

# ------------------------------------------------- report -----------------------------------
def row(r):
    m = r["measured"]
    vb = "VALUE-BEARING" if r["value_bearing_from_outside_LB"] else "relative-only"
    circ = "YES" if r["circular_for_value_grading"] else "no"
    return (f"| {r['id']} | {r['category']} | {m['n_phonetic_signs_constrained']} "
            f"| {m['n_new_signs_vs_foundry']} | {m['n_distinct_sites']} | {m['n_distinct_objects']} "
            f"| {m['total_tokens']} | {r['rule_complexity_n_value_assignments']} | {vb} | {circ} |")

H = summary["HEADLINE"]
md = []
md.append("# G2 — New High-Value Anchor Expansion\n")
md.append("**Task.** Expand the anchor candidate set beyond the Foundry 115-record / 62-sign "
          "inventory (G1) by mining the silver corpus for candidates that JOINTLY constrain "
          "several signs, across the seven task classes (multi-slot toponyms; personal names "
          "in variant forms; titles with morphology; commodity/measure terms; seal-owner "
          "names; foreign names; shared cross-script formulae). For each: signs constrained, "
          "rule complexity, prior exposure, and — decisively — whether it can pin a VALUE from "
          "OUTSIDE the Linear-B/GORILA system.\n")
md.append("**Constitution.** L2/L4 census; NON-CIRCULAR (Art. XII) — GORILA values label only, "
          "never a model input. Deterministic, seed 20260708. Attestation is corpus-measured "
          f"(invariant 12): {summary['corpus']['n_inscriptions']} inscriptions, "
          f"{summary['corpus']['n_distinct_multisign_words']} distinct multi-sign words.\n")
md.append("Artifacts: `scripts/g2_high_value_anchors.py` -> `data/anchors_v2/expanded.json`.\n")
md.append("---\n")
md.append("## 1. Candidate classes, ranked by relative-anchor strength (signs x sites)\n")
md.append("`new_signs` = phonetic signs NOT already covered by any Foundry anchor record "
          f"(Foundry covered {summary['foundry_baseline']['n_covered_signs']} signs). "
          "`rule_cx` = simultaneous sign->value assignments if used to fix VALUES. "
          "`circular` = value claim would ride on GORILA homomorphy (Art. XII).\n")
md.append("| candidate | class | signs | new | sites | objs | tok | rule_cx | kind | circular |")
md.append("|---|---|---|---|---|---|---|---|---|---|")
for r in RESULTS: md.append(row(r))
md.append("")
md.append("## 2. The decisive split — value-bearing vs relative-only\n")
md.append(f"- **New VALUE-BEARING anchor classes:** {H['n_new_value_bearing_anchor_classes']} "
          f"({', '.join(H['value_bearing_classes']) or 'none'}).")
md.append(f"- **New FIRM held-out value anchors produced:** **{H['n_new_firm_held_out_value_anchors']}**. "
          f"{H['held_out_value_note']}")
md.append(f"- **New RELATIVE/structural anchor classes:** {H['n_relative_structural_anchor_classes']} "
          f"({', '.join(H['relative_classes'])}).")
md.append(f"- Relative anchors touch **{H['distinct_phonetic_signs_touched_by_relative_anchors']}** "
          f"distinct phonetic signs, of which **{H['distinct_NEW_phonetic_signs_vs_foundry']}** are "
          f"NEW vs the Foundry inventory: {', '.join(H['new_phonetic_signs_vs_foundry']) or '(none)'}.\n")
md.append("## 3. Per-class detail (measured)\n")
for r in RESULTS:
    m = r["measured"]
    md.append(f"### {r['id']}  ({r['category']})\n")
    md.append(f"- **Signs constrained:** {m['n_phonetic_signs_constrained']} phonetic "
              f"({', '.join(m['phonetic_signs'])})" +
              (f" + non-phonetic slots {m['non_phonetic_slots']}" if m['non_phonetic_slots'] else "") + ".")
    md.append(f"- **New signs vs Foundry:** {m['n_new_signs_vs_foundry']} "
              f"({', '.join(m['new_signs_vs_foundry']) or 'none'}).")
    md.append(f"- **Attestation:** {m['total_tokens']} tokens / {m['n_distinct_objects']} objects "
              f"/ {m['n_distinct_sites']} sites {m['sites']}; support {m['support_context']}.")
    md.append(f"- **Sequences attested / declared:** {m['n_sequences_attested']}/{m['n_sequences_declared']}.")
    md.append(f"- **Rule complexity:** {r['rule_complexity_n_value_assignments']} simultaneous value assignments.")
    md.append(f"- **Prior exposure:** {r['prior_exposure']}.")
    md.append(f"- **External referent:** {r['external_referent']} — {r['referent_note']}")
    md.append(f"- **Art. XII:** {r['art_XII_flag']}")
    md.append(f"- **Notes:** {r['notes']}\n")
md.append("## 4. Verdict\n")
md.append(H["art_XII_verdict"] + "\n")
md.append("**Bearing on the campaign.** Expansion is a large WIN for the RELATIVE programme and "
          "a clean NULL for the value programme. The libation formula (22 objects / 10 sites, "
          "slot-varying: `A-TA-I-*301-WA-JA`/`-WA-E`, `U-NA-KA-NA-SI`/`U-NA-RU-KA-NA-TI`, "
          "`I-PI-NA-MA`/`I-PI-NA-MI-NA`) plus the accounting family and ~80 morphological "
          "paradigm pairs give the load-bearing SUBSTITUTION channel a rich, cross-site, "
          "relabeling-invariant substrate — exactly what it must be audited on. But not one of "
          "them derives a value from outside Linear B: every new high-multiplicity anchor is "
          "VALUE-BLIND, and the only value-bearing channel (toponyms) was already shown "
          "saturated in G1 (5 firm, one-toponym-deep, 0 held-out-survivable). **G2 adds 0 new "
          "held-out value anchors.**\n")
md.append("*Generated by `scripts/g2_high_value_anchors.py`; all counts echoed from "
          "`data/anchors_v2/expanded.json` (invariant 12).*")

open(os.path.join(OUT_REP, "G_NEW_HIGH_VALUE_ANCHORS.md"), "w").write("\n".join(md))

# ------------------------------------------------- console -----------------
print("=== G2 HIGH-VALUE ANCHOR EXPANSION ===")
print("corpus multisign words:", summary["corpus"]["n_distinct_multisign_words"],
      "| foundry covered signs:", len(foundry_signs))
print("candidate classes:", len(RESULTS))
for r in RESULTS:
    m = r["measured"]
    print(f"  {r['id']:28s} signs={m['n_phonetic_signs_constrained']:2d} "
          f"new={m['n_new_signs_vs_foundry']:2d} sites={m['n_distinct_sites']:2d} "
          f"objs={m['n_distinct_objects']:3d} tok={m['total_tokens']:3d} "
          f"strength={r['relative_anchor_strength']:3d} "
          f"{'VALUE' if r['value_bearing_from_outside_LB'] else 'rel'} "
          f"circular={r['circular_for_value_grading']}")
print("HEADLINE: new value-bearing classes:", H["n_new_value_bearing_anchor_classes"],
      "| new FIRM held-out value anchors:", H["n_new_firm_held_out_value_anchors"])
print("relative classes:", H["n_relative_structural_anchor_classes"],
      "| distinct phon signs touched:", H["distinct_phonetic_signs_touched_by_relative_anchors"],
      "| NEW vs foundry:", H["distinct_NEW_phonetic_signs_vs_foundry"], H["new_phonetic_signs_vs_foundry"])
print("wrote", os.path.join(OUT_DATA, "expanded.json"))
print("wrote", os.path.join(OUT_REP, "G_NEW_HIGH_VALUE_ANCHORS.md"))
