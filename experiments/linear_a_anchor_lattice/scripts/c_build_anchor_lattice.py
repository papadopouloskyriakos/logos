#!/usr/bin/env python3
"""
TASK C - Dependency-aware all-anchor lattice.

Builds ONE auditable hypergraph over the WP-B sign universe (conservative grain,
163 variables / 69 A-only). Ingests:
  - 115 wp5 provenance records (62 signs) from the foundry anchor inventory
  - the 5 firm toponym equations (Phaistos, Setoija, Sybrita, Tylissos, Dikte)
  - WP-B substitution (F4 rel-classes) + morphology relations (from the universe)
  - WP-D SOURCE_EXPANSION_NULL (Kom el-Hetan / Egyptian; SEED_A=0, 0 new anchors)

CRITICAL (Art. XI/XII): collapse dependency clones. No edge counts as INDEPENDENT
merely because it carries a different citation; homomorphy (shape) is circular w.r.t.
value; toponym/PN/gloss all descend from the ONE LA=LB continuity meta-lineage.

Seed 20260708. Emits data/anchor_lattice/lattice.json and prints an audit.
"""
import json, os, hashlib
from collections import Counter, defaultdict

SEED = 20260708
ROOT = "/home/claude-runner/gitlab/n8n/logos-linear-a-anchor-lattice/experiments/linear_a_anchor_lattice"
FOUNDRY = "/home/claude-runner/gitlab/n8n/logos-linear-a-decipherment-foundry/experiments/linear_a_foundry/data"

univ = json.load(open(f"{ROOT}/data/sign_universe/conservative.json"))
wp5  = json.load(open(f"{FOUNDRY}/wp5_anchor_inventory.json"))
wpd  = json.load(open(f"{ROOT}/data/source_expansion/new_anchors.json"))
f4   = json.load(open(f"{ROOT}/data/substitution_bridge/F4_la_relative_constraints.json"))

SIGNS = univ["signs"]                      # 163 variables keyed by canonical_id
INV   = wp5["sign_inventory"]              # 62 records

nodes, edges = {}, []

def nid(t, k):  # stable node id
    return f"{t}:{k}"

def add_node(ntype, key, **attrs):
    i = nid(ntype, key)
    if i not in nodes:
        nodes[i] = {"id": i, "type": ntype, "key": key, **attrs}
    else:
        nodes[i].update({k: v for k, v in attrs.items() if v is not None})
    return i

def eid(payload):
    return "E:" + hashlib.sha1(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]

def add_edge(etype, signs, cand_values, slots, source, page, chronology, geography,
             lineage, independence_class, channels, rule_complexity, transformations,
             prior_exposure, deriv_vs_heldout, circularity_risk, search_multiplicity,
             failure_condition, referents=None, la_forms=None, ext_forms=None,
             value_bearing=False, note=None):
    payload = {"etype": etype, "signs": sorted(signs), "referents": sorted(referents or []),
               "lineage": lineage, "channels": sorted(channels)}
    e = {
        "id": eid(payload), "etype": etype,
        "signs_constrained": sorted(signs),
        "candidate_values": cand_values,
        "slots": slots,
        "source": source, "page": page,
        "chronology": chronology, "geography": geography,
        "dependency_lineage": lineage,
        "independence_class": independence_class,
        "evidence_channels": sorted(channels),
        "rule_complexity": rule_complexity,
        "transformations": transformations,
        "prior_exposure": prior_exposure,
        "derivation_vs_heldout": deriv_vs_heldout,
        "circularity_risk": circularity_risk,
        "search_multiplicity": search_multiplicity,
        "failure_condition": failure_condition,
        "value_bearing": value_bearing,
        "external_referents": sorted(referents or []),
        "linear_a_forms": sorted(la_forms or []),
        "external_forms": sorted(ext_forms or []),
    }
    if note: e["note"] = note
    edges.append(e)
    return e

# ---------------------------------------------------------------- LANGUAGES
add_node("LANGUAGE", "Linear_A_unknown", status="undeciphered")
add_node("LANGUAGE", "Mycenaean_Greek_LB", status="read")
add_node("LANGUAGE", "Egyptian", status="read")
add_node("LANGUAGE", "Cypriot_Greek", status="read")

# ---------------------------------------------------------------- SOURCES
SRC = {
 "anchors_csv":   ("crossscript_gate/anchors.csv", "-"),
 "census_csv":    ("crossscript_gate/phase2/anchor_census.csv", "-"),
 "toponym_csv":   ("crossscript_gate/toponym_anchors.csv", "-"),
 "salgarella":    ("Salgarella 2020 Aegean Linear Script(s), homomorphy grades", "ch.4-5"),
 "sm2017":        ("Steele & Meissner 2017 (Cypriot high-certainty 11)", "-"),
 "edel1966":      ("Edel 1966 Kom el-Hetan Aegean List (re-collated Edel&Gorg 2005; Cline 2011)", "statue-base N"),
 "corpus_silver": ("corpus/silver/inscriptions_structured.json (1341 inscr / 1165 forms)", "-"),
 "sigla":         ("SigLA database (doc-alignment vote; GORILA numbers)", "-"),
}
for k, (s, p) in SRC.items():
    add_node("SOURCE", k, description=s, page=p)

# ---------------------------------------------------------------- DEPENDENCY LINEAGES
# value_bearing_channels=1 (do_not_repeat anchor_state). Only the lexical/onomastic
# channel is value-bearing; H is shape/circular, C is a cross-script chain that reuses
# the same continuity assumption, EG is null. ALL L-family edges descend from the ONE
# LA=LB transnumeration meta-lineage (Art. XI collapse target).
add_node("DEPENDENCY_LINEAGE", "META_CONTINUITY_LA_eq_LB",
         description="LA sign = LB homophone (standard transnumeration). Shared ancestor of L/H/C.",
         value_bearing=True, circular_for_values=True)
LIN = {
 "LIN_L_TOP":   ("lexical/onomastic - toponym equations", True,  "META_CONTINUITY_LA_eq_LB"),
 "LIN_L_PN":    ("lexical/onomastic - personal-name equations", True, "META_CONTINUITY_LA_eq_LB"),
 "LIN_L_GLOSS": ("lexical - commodity/gloss equations", True, "META_CONTINUITY_LA_eq_LB"),
 "LIN_H":       ("homomorphy / sign-shape (Salgarella 2020) - SHAPE-ONLY, circular", False, "META_CONTINUITY_LA_eq_LB"),
 "LIN_C":       ("Cypriot cross-script stability (S&M 2017) - chain reuses continuity", False, "META_CONTINUITY_LA_eq_LB"),
 "LIN_EG":      ("Egyptian epigraphic (Edel 1966 / Kom el-Hetan) - WP-D, SEED_A=0", True, "EGYPTIAN_INDEPENDENT"),
}
add_node("DEPENDENCY_LINEAGE", "EGYPTIAN_INDEPENDENT",
         description="Egyptian consonant-skeleton record; dependency-distinct from LA=LB continuity",
         value_bearing=True, circular_for_values=False)
for k, (d, vb, parent) in LIN.items():
    add_node("DEPENDENCY_LINEAGE", k, description=d, value_bearing=vb, parent_meta_lineage=parent)

# ---------------------------------------------------------------- SIGN nodes (163)
for k, v in SIGNS.items():
    add_node("SIGN", k, sign_class=v["class"],
             occurrence_count=v.get("occurrence_count"),
             stroke_image=bool(v.get("stroke_image_available")),
             has_anchor=bool(v.get("has_anchor_coverage")),
             has_subst=bool(v.get("has_substitution_coverage")),
             allograph_family=v.get("allograph_family"))
    # STROKE_FAMILY node + membership (circular channel; NOT value-bearing)
    fam = v.get("allograph_family")
    if fam:
        add_node("STROKE_FAMILY", fam)

AONLY = {k for k, v in SIGNS.items() if v["class"] == "A-only"}

# ---------------------------------------------------------------- 5 FIRM TOPONYM EQUATIONS
# (LA-attested >=4 distinctive slots AND an accepted place identity)
FIRM = [
 ("Phaistos", "pa-i-to",     ["PA-I-TO"],                 ["Haghia Triada"],        ["HT120","HT97a"], 3, ["PA","I","TO"]),
 ("Setoija",  "se-to-i-ja",  ["SE-TO-I-JA"],              ["Prassa"],               ["PRZa1"],         4, ["SE","TO","I","JA"]),
 ("Sybrita",  "su-ki-ri-ta", ["SU-KI-RI-TA"],             ["Phaistos"],             ["PHWa32"],        4, ["SU","KI","RI","TA"]),
 ("Tylissos", "tu-ri-so",    ["A-TU-RI-SI-TI","TU-RU-SA"],["Knossos","Kophinas"],   [],                5, ["TU","RI","SI","TI","RU","SA","A"]),
 ("Dikte",    "di-ka-ta",    ["A-DI-KI-TE"],              ["Palaikastro"],          [],                4, ["DI","KI","TE","A"]),
]
firm_signs = set()
for topo, lbref, laforms, sites, docs, slots, signlist in FIRM:
    add_node("EXTERNAL_REFERENT", f"TOPO:{topo}", kind="toponym")
    add_node("EXTERNAL_FORM", f"LB:{lbref}", language="Mycenaean_Greek_LB")
    for lf in laforms: add_node("LINEAR_A_FORM", lf)
    for s in sites:    add_node("SITE", s)
    for dc in docs:    add_node("INSCRIPTION", dc)
    signs_present = [s for s in signlist if s in SIGNS]
    firm_signs |= set(signs_present)
    add_edge("toponym_equation", signs_present,
             cand_values={s: s for s in signs_present},   # graded LB label only
             slots=slots, source=[SRC["toponym_csv"][0], SRC["census_csv"][0]],
             page="-", chronology="LMIB (younger LA where marked)", geography=sites,
             lineage="LIN_L_TOP", independence_class="L_toponym",
             channels=["L"], rule_complexity="place-identity match on syllable skeleton",
             transformations=["LA->LB transnumeration","toponym identification"],
             prior_exposure="HIGH (canonical toponyms, published)",
             deriv_vs_heldout="DERIVATION (used to build the anchor set)",
             circularity_risk="HIGH under Art.XII (value assigned by the same continuity rule graded)",
             search_multiplicity="1 of ~15 candidate toponyms x forms",
             failure_condition="LA form is not that place / not read as LB value under LOTO",
             referents=[f"TOPO:{topo}"], la_forms=laforms, ext_forms=[f"LB:{lbref}"],
             value_bearing=True,
             note="FIRM_TOPONYM_EQUATION (1 of 5)")

# ---------------------------------------------------------------- 115 wp5 PROVENANCE RECORDS
# Build referent-equation hyperedges: one edge per (referent) linking all signs citing it.
ref_to_signs = defaultdict(set)   # referent-item -> signs
ref_kind = {}
tier_of = {}
homomorphy_signs = set()
cypriot_signs = set()
n_prov = 0
for r in INV:
    sg = r["sign_id"]
    tier_of[sg] = r["dependency_tier"]
    L = r["channel_L_lexical"]
    for it in L.get("toponym_items", []): ref_to_signs[it].add(sg); ref_kind[it] = "toponym"; n_prov += 1
    for it in L.get("name_items", []):    ref_to_signs[it].add(sg); ref_kind[it] = "personal_name"; n_prov += 1
    for it in L.get("gloss_items", []):   ref_to_signs[it].add(sg); ref_kind[it] = "commodity_gloss"; n_prov += 1
    if r["channel_H_homomorphy_tier"] and r["channel_H_homomorphy_tier"] > 0:
        homomorphy_signs.add(sg)
    if r["channel_C_cypriot_stable"]:
        cypriot_signs.add(sg)

EQ_ETYPE = {"toponym": "toponym_equation", "personal_name": "personal_name_equation",
            "commodity_gloss": "commodity_measure_equation"}
EQ_LIN   = {"toponym": "LIN_L_TOP", "personal_name": "LIN_L_PN", "commodity_gloss": "LIN_L_GLOSS"}
EQ_CHAN  = {"toponym": "L", "personal_name": "L", "commodity_gloss": "L"}

for ref, sgset in sorted(ref_to_signs.items()):
    kind = ref_kind[ref]
    add_node("EXTERNAL_REFERENT", f"{kind}:{ref}", kind=kind)
    signs_present = [s for s in sgset if s in SIGNS]
    # skip the 5 firm toponyms already added as firm edges? Keep them - they are the
    # provenance-record view; firm edges are the audited-slot view. Both cite same lineage.
    add_edge(EQ_ETYPE[kind], signs_present,
             cand_values={s: s for s in signs_present},
             slots=len(str(ref).split("_")), source=[SRC["census_csv"][0], SRC["anchors_csv"][0]],
             page="-", chronology="mixed", geography="mixed Cretan admin sites",
             lineage=EQ_LIN[kind], independence_class=f"L_{kind}",
             channels=[EQ_CHAN[kind]],
             rule_complexity="onomastic/lexical skeleton match",
             transformations=["LA->LB transnumeration"],
             prior_exposure="HIGH (published onomastic corpus)",
             deriv_vs_heldout="DERIVATION",
             circularity_risk="HIGH under Art.XII" if kind != "commodity_gloss" else "HIGH (gloss guess)",
             search_multiplicity=f"1 referent among {len(ref_to_signs)} lexical items",
             failure_condition="referent placement fails held-out (LOTO) verification",
             referents=[f"{kind}:{ref}"], value_bearing=True)

# cross-script descent (homomorphy) - CIRCULAR shape channel, NOT value-bearing
for sg in sorted(homomorphy_signs):
    add_node("CROSS_SCRIPT_SIGN", f"LB_shape:{sg}", script="Linear_B_or_AB")
    add_edge("cross_script_descent", [sg],
             cand_values={sg: sg}, slots=1, source=[SRC["salgarella"][0]],
             page=SRC["salgarella"][1], chronology="LMIB->LB", geography="Crete",
             lineage="LIN_H", independence_class="H_homomorphy",
             channels=["H"], rule_complexity="glyph shape similarity grade",
             transformations=["shape homomorphy"],
             prior_exposure="HIGH",
             deriv_vs_heldout="DERIVATION",
             circularity_risk="MAXIMAL (shape-only value transfer; capped <=0.75, do_not_repeat CIRCULAR)",
             search_multiplicity="57 graded signs",
             failure_condition="shape match does not imply value (already known circular)",
             referents=[f"CROSS_SCRIPT_SIGN:LB_shape:{sg}"], value_bearing=False)

# Cypriot stability - chain, NOT independently value-bearing
for sg in sorted(cypriot_signs):
    add_node("CROSS_SCRIPT_SIGN", f"Cypriot:{sg}", script="Cypriot_syllabary")
    add_edge("cross_script_descent", [sg],
             cand_values={sg: sg}, slots=1, source=[SRC["sm2017"][0]],
             page="-", chronology="LB->Cypriot", geography="Cyprus",
             lineage="LIN_C", independence_class="C_cypriot",
             channels=["C"], rule_complexity="cross-script value stability",
             transformations=["LA->LB->Cypriot chain"],
             prior_exposure="HIGH",
             deriv_vs_heldout="DERIVATION",
             circularity_risk="HIGH (chain reuses the LA=LB continuity it is meant to corroborate)",
             search_multiplicity="11 high-certainty signs",
             failure_condition="chain breaks if LA!=LB",
             referents=[f"CROSS_SCRIPT_SIGN:Cypriot:{sg}"], value_bearing=False)

# ---------------------------------------------------------------- WP-B RELATIVE SUBSTITUTION (F4)
for c in f4["within_la_equivalence_classes"]:
    rc = c["rel_class"]
    add_node("RELATIVE_CLASS", rc, n_signs=c["n_signs"], interpretation=c["interpretation"])
    signs_present = [s for s in c["signs"] if s in SIGNS]
    add_edge("relative_substitution_relation", signs_present,
             cand_values=None, slots=None, source=["F4_la_relative_constraints.json (WP-F)"],
             page="-", chronology="LA internal", geography="LA corpus",
             lineage="LIN_REL", independence_class="RELATIVE_value_free",
             channels=["substitution"],
             rule_complexity="within-LA vowel-alternation / shared-consonant neighborhood",
             transformations=["relative-class reduction"],
             prior_exposure="LOW (derived here)",
             deriv_vs_heldout="DERIVATION (relative only)",
             circularity_risk="N/A (value-free; earns NO absolute value, Art.XV)",
             search_multiplicity="5 classes over 17 rel-assigned signs",
             failure_condition="class is not a real phonological neighborhood",
             value_bearing=False,
             note="RELATIVE ONLY - NO absolute value; F4 channel = NO_POWER")
add_node("DEPENDENCY_LINEAGE", "LIN_REL",
         description="within-LA relative substitution (value-free)", value_bearing=False)

# pairwise substitution edges from the universe (33 signs) - relative
subpairs = 0
for k, v in SIGNS.items():
    for nb in v.get("substitution_neighbors", []) or []:
        if nb in SIGNS:
            subpairs += 1
            add_edge("relative_substitution_relation", sorted([k, nb]),
                     cand_values=None, slots=None, source=["sign_universe conservative (WP-B)"],
                     page="-", chronology="LA internal", geography="LA corpus",
                     lineage="LIN_REL", independence_class="RELATIVE_value_free",
                     channels=["substitution"], rule_complexity="substitution neighbor pair",
                     transformations=["relative pairing"], prior_exposure="LOW",
                     deriv_vs_heldout="DERIVATION (relative)",
                     circularity_risk="N/A (value-free)",
                     search_multiplicity="pairwise over corpus", value_bearing=False,
                     failure_condition="pair is not a genuine substitution neighborhood")

# ---------------------------------------------------------------- WP-B MORPHOLOGY RELATIONS
morph_signs = []
for k, v in SIGNS.items():
    mr = v.get("morphological_role")
    if mr:
        morph_signs.append(k)
        add_node("MORPHOLOGICAL_RELATION", f"morph:{k}", detail=mr)
        add_edge("morphological_relation", [k],
                 cand_values=None, slots=None, source=["sign_universe conservative (WP-B)"],
                 page="-", chronology="LA internal", geography="LA corpus",
                 lineage="LIN_MORPH", independence_class="STRUCTURAL_value_free",
                 channels=["morphology"], rule_complexity="prefix/suffix boundary role",
                 transformations=["morpheme boundary detection"],
                 prior_exposure="LOW", deriv_vs_heldout="DERIVATION (structural)",
                 circularity_risk="N/A (value-free structural role)",
                 search_multiplicity=f"{len([1 for x in SIGNS.values() if x.get('morphological_role')])} morph-role signs",
                 failure_condition="boundary is a frequency artifact", value_bearing=False)
add_node("DEPENDENCY_LINEAGE", "LIN_MORPH",
         description="LA-internal morphological role (value-free structural)", value_bearing=False)

# ---------------------------------------------------------------- FORMULA SLOTS
FS = ["KU-RO_total", "KI-RO_deficit", "total_formula", "A_prefix_head", "libation_formula"]
for f in FS: add_node("FORMULA_SLOT", f)
add_node("DEPENDENCY_LINEAGE", "LIN_FORMULA", description="admin/libation formula slot (structural)", value_bearing=False)
for k, v in SIGNS.items():
    fs = v.get("formula_slots") or {}
    hits = [slot for slot, n in fs.items() if n]
    if hits:
        add_edge("formula_slot_constraint", [k],
                 cand_values=None, slots=hits, source=["sign_universe conservative (WP-B)"],
                 page="-", chronology="LA admin", geography="LA corpus",
                 lineage="LIN_FORMULA", independence_class="STRUCTURAL_value_free",
                 channels=["formula"], rule_complexity="ledger/libation slot membership",
                 transformations=["formula-slot mapping"], prior_exposure="MED (KU-RO known total)",
                 deriv_vs_heldout="DERIVATION (structural)", circularity_risk="N/A (value-free)",
                 search_multiplicity="6 signs in formula slots",
                 failure_condition="slot role misassigned", value_bearing=False)

# ---------------------------------------------------------------- WP-D LOANWORD (Egyptian) - NULL
for t in wpd["kom_el_hetan_toponym_table"]:
    add_node("EXTERNAL_REFERENT", f"toponym:{t['toponym']}", kind="toponym")
    add_node("EXTERNAL_FORM", f"EG:{t['egyptian_rendering']}", language="Egyptian")
    add_node("EXTERNAL_FORM", f"LB:{t['lb_reflex']}", language="Mycenaean_Greek_LB")
add_edge("loanword_equation", [],
         cand_values=None, slots=4, source=[SRC["edel1966"][0]],
         page=SRC["edel1966"][1], chronology="Amenhotep III (14th c. BCE)", geography="Egypt/Crete",
         lineage="LIN_EG", independence_class="EGYPTIAN_INDEPENDENT",
         channels=["Egyptian_epigraphic"], rule_complexity="EA-13 La>=4 loanword design",
         transformations=["Egyptian consonant-skeleton -> LA slot match"],
         prior_exposure="HIGH (Kom el-Hetan Aegean List published)",
         deriv_vs_heldout="HELD-OUT-CAPABLE but VACUOUS",
         circularity_risk="LOW (dependency-distinct) but 0 eligible anchors",
         search_multiplicity="5 externally-rendered toponyms x LA corpus",
         failure_condition="no LA toponym is BOTH >=4-slot AND externally rendered",
         value_bearing=True,
         note="WP-D SOURCE_EXPANSION_NULL: n_new_independent_anchors=0; only Phaistos overlaps and at 3 slots < 4")

# ---------------------------------------------------------------- CANDIDATE_VALUE (graded-only)
# LB/GORILA conventional labels attached to L-anchored signs as GRADED benchmark labels only
# (benchmark_label_graded_only; never a variable input, earn no value/licence - non_circular_note).
cand_signs = set()
for e in edges:
    if e["value_bearing"] and e["dependency_lineage"] in ("LIN_L_TOP", "LIN_L_PN", "LIN_L_GLOSS"):
        cand_signs |= set(e["signs_constrained"])
for sg in sorted(cand_signs):
    add_node("CANDIDATE_VALUE", f"gradedLB:{sg}", for_sign=sg,
             status="benchmark_label_graded_only",
             note="LB/GORILA conventional value used ONLY to grade benchmarks; earns no licence")

# ================================================================ DEPENDENCY COLLAPSE (Art. XI/XII)
# A value-bearing INDEPENDENT anchor needs >=2 dependency-lineage-DISTINCT value-bearing
# supports where the lineages do NOT share a meta-lineage ancestor.
def meta_of(lin):
    n = nodes.get(nid("DEPENDENCY_LINEAGE", lin), {})
    return n.get("parent_meta_lineage", lin)

value_bearing_lineages = {"LIN_L_TOP", "LIN_L_PN", "LIN_L_GLOSS", "LIN_EG"}  # H,C,REL,MORPH,FORMULA excluded
# per-sign: set of distinct META-lineages carrying a value-bearing edge
sign_meta = defaultdict(set)
sign_vb_lineages = defaultdict(set)
for e in edges:
    if e["value_bearing"] and e["dependency_lineage"] in value_bearing_lineages:
        for s in e["signs_constrained"]:
            sign_vb_lineages[s].add(e["dependency_lineage"])
            sign_meta[s].add(meta_of(e["dependency_lineage"]))

# INVENTORY-side (pre-collapse) figures reported by source (NOT independence)
inv_multi = [r["sign_id"] for r in INV if r["dependency_tier"] == "multi_channel_independent"]
inv_pins  = [r["sign_id"] for r in INV if r["dependency_tier"] == "one_toponym_deep_pin"]

# Dependency-collapsed independent anchors: >=2 DISTINCT META-lineages
collapsed_independent = sorted(s for s, m in sign_meta.items() if len(m) >= 2)
# held-out survivable (frozen gate): 0 (SEED_A=0)
held_out_survivable = 0

# A-only edges
aonly_vb = sorted(s for s in AONLY if sign_vb_lineages.get(s))          # any value-bearing lineage edge
aonly_any_edge = sorted(s for s in AONLY
                        if any(s in e["signs_constrained"] for e in edges
                               if e["etype"] not in ("cross_script_descent",)) )
aonly_collapsed_independent = [s for s in collapsed_independent if s in AONLY]

# ================================================================ COUNTS
node_counts = Counter(n["type"] for n in nodes.values())
edge_counts = Counter(e["etype"] for e in edges)

summary = {
    "seed": SEED,
    "grain": "conservative (163 variables; 69 A-only)",
    "node_counts_by_type": dict(node_counts),
    "n_nodes_total": len(nodes),
    "edge_counts_by_type": dict(edge_counts),
    "n_edges_total": len(edges),
    "provenance_records_ingested": {
        "wp5_provenance_records": 115, "wp5_L_items_counted": n_prov,
        "firm_toponym_equations": 5, "rel_substitution_classes": len(f4["within_la_equivalence_classes"]),
        "pairwise_substitution_edges": subpairs, "morphology_relation_signs": len(morph_signs),
        "wp_d_new_independent_anchors": wpd["n_new_independent_anchors"],
    },
    "dependency_lineages": {
        "total_declared": 6,
        "value_bearing_channels": 1,
        "value_bearing_lineages": sorted(value_bearing_lineages),
        "meta_lineage_collapse": "LIN_L_TOP/PN/GLOSS + LIN_H + LIN_C all descend from META_CONTINUITY_LA_eq_LB",
    },
    "INVENTORY_side_pre_collapse_NOT_independence": {
        "multi_channel_independent_signs": len(inv_multi),
        "one_toponym_deep_pins": len(inv_pins),
        "note": "these 'multi-channel' signs stack L+H+C citations that share ONE meta-lineage",
    },
    "DEPENDENCY_COLLAPSED_independent_anchor_count": len(collapsed_independent),
    "dependency_collapsed_independent_signs": collapsed_independent,
    "held_out_survivable_absolute_anchors": held_out_survivable,
    "collapse_rationale": (
        "value_bearing_channels=1 (only lexical/onomastic L is value-bearing). Within L, "
        "toponym/PN/gloss equations all descend from META_CONTINUITY_LA_eq_LB and are graded "
        "by the same rule that created them (Art.XII), so they are dependency clones, not "
        "independent supports. H (shape) is circular; C (Cypriot) reuses the continuity chain. "
        "Egyptian (LIN_EG) is the only genuinely dependency-distinct value-bearing lineage but "
        "SEED_A=0 (no eligible anchor). Hence >=2 distinct meta-lineages is reachable by NO sign."),
    "A_only_69_signs": {
        "total": len(AONLY),
        "with_any_value_bearing_lineage_edge": len(aonly_vb),
        "with_any_value_bearing_lineage_edge_signs": aonly_vb,
        "with_independent_collapsed_value": len(aonly_collapsed_independent),
        "relationally_dark_no_value_edge": len(AONLY) - len(aonly_vb),
        "note": ("*49 alone carries a value-bearing L (toponym) edge, and it is a single "
                 "one-toponym-deep pin (robust_anchor=false, not held-out survivable). "
                 "*324 has only a value-free relative substitution edge; 57/69 have only the "
                 "circular stroke channel. Independent-collapsed value to any A-only sign = 0."),
    },
}

os.makedirs(f"{ROOT}/data/anchor_lattice", exist_ok=True)
out = {"schema_version": "C1", "seed": SEED,
       "node_types": sorted(set(n["type"] for n in nodes.values())),
       "edge_types": sorted(set(e["etype"] for e in edges)),
       "summary": summary,
       "nodes": list(nodes.values()), "edges": edges}
json.dump(out, open(f"{ROOT}/data/anchor_lattice/lattice.json", "w"), indent=1)

print(json.dumps(summary, indent=1))
