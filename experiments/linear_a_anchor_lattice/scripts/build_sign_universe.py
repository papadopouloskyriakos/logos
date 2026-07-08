#!/usr/bin/env python3
"""TASK B - Canonical unresolved-sign universe for the anchor-lattice campaign.

Builds the complete variable universe for joint inference from the Linear A corpus,
enriched from every read-only input, at THREE allograph grains so no downstream
result can depend on a single spec (Constitution v2.2 sensitivity requirement):

  SIGN_UNIVERSE_ALLOGRAPH_SPLIT   - finest: every catalogued sign kept distinct
                                    (letter/subscript allographs *131B, RA2 separate)
  SIGN_UNIVERSE_CONSERVATIVE      - PRIMARY: repo-audited expert merges only
                                    (*131B/*131C -> *131; subscript AB kept distinct)
  SIGN_UNIVERSE_ALLOGRAPH_MERGED  - coarsest: also fold subscript AB into graphic base
                                    (RA2->RA, PA3->PA, TA2->TA, PU2->PU)

The three grains differ ONLY on the allograph axis; ligature/canonicalisation is held
fixed (the corpus diplomatic->canonical map). NON-CIRCULAR: LB/GORILA conventional
values are attached as GRADED benchmark labels only, never used to form a variable or
earn a value; they are flagged `benchmark_label_graded_only`.
"""
import json, os, re, sys
from collections import Counter, defaultdict

SEED = 20260708
HERE = os.path.dirname(os.path.abspath(__file__))
EXP  = os.path.dirname(HERE)
WT   = "/home/claude-runner/gitlab/n8n/logos-linear-a-anchor-lattice"
OUT_DATA = os.path.join(EXP, "data", "sign_universe")
OUT_REP  = os.path.join(EXP, "reports")
os.makedirs(OUT_DATA, exist_ok=True); os.makedirs(OUT_REP, exist_ok=True)

# ---- inputs ---------------------------------------------------------------
ONT   = json.load(open(os.path.join(WT, "corpus/silver/signs_ontology.json")))
CORP  = json.load(open(os.path.join(WT, "corpus/silver/inscriptions_structured.json")))
CGRAPH= json.load(open("/home/claude-runner/gitlab/n8n/logos-linear-a-relative-phonology-seals/"
                       "experiments/linear_a_relative_phonology/data/C_la_graph.json"))
WP5   = json.load(open("/home/claude-runner/gitlab/n8n/logos-linear-a-decipherment-foundry/"
                       "experiments/linear_a_foundry/data/wp5_anchor_inventory.json"))
SIG_SIGNS = json.load(open(os.path.join(WT, "corpus/bronze/sigla_browse_2026/sigla_signs.json")))
SIG_DOCS  = json.load(open(os.path.join(WT, "corpus/bronze/sigla_browse_2026/sigla_documents.json")))
LITIDX = json.load(open(os.path.join(WT, "corpus/silver/literature_index.json")))

SUBSCRIPT = {"₀":"0","₁":"1","₂":"2","₃":"3","₄":"4",
             "₅":"5","₆":"6","₇":"7","₈":"8","₉":"9"}
def ascii_tok(t):
    for k,v in SUBSCRIPT.items(): t=t.replace(k,v)
    return t

# ---- canonicalisation (mirrors scripts/inventory/build_ontology.py, audited) -----
def conservative_id(sid):
    """letter-suffix star allographs collapse: *131B/*131C -> *131 (GORILA-attested)."""
    m = re.match(r"\*(\d+)([A-Z]?)$", sid)
    if m and m.group(2):
        return "*" + m.group(1)
    return sid
def merged_id(sid):
    """+ fold subscript AB allographs into graphic base: RA2->RA, PA3->PA."""
    sid = conservative_id(sid)
    m = re.match(r"([A-Z]+?)(\d+)$", sid)
    if m:
        return m.group(1)
    return sid
def allograph_family(sid):
    c = ascii_tok(sid)
    m = re.match(r"\*(\d+)", c)
    if m: return "*"+m.group(1)
    m = re.match(r"([A-Z]+?)(\d+)$", c)
    if m: return m.group(1)
    return c

# ---- reverse diplomatic map: corpus raw token -> canonical ontology key ----
REV = {}
for k, v in ONT.items():
    for dt in v.get("diplomatic_tokens", []):
        REV.setdefault(dt, k)
    REV.setdefault(k, k)

def canon(raw):
    return REV.get(raw, raw)

# ---- 1. corpus statistics per SPLIT canonical key -------------------------
stat = defaultdict(lambda: {
    "freq":0, "n_initial":0, "n_interior":0, "n_final":0, "n_sole":0,
    "sites":Counter(), "chron":Counter(), "support":Counter(), "docs":set(),
    "in_KURO":0, "in_KIRO":0, "in_formula_total":0, "as_A_prefix_head":0,
})
FORMULA_TOTAL = {("KU","RO"), ("KI","RO"), ("PO","TO","KU","RO")}
for ins in CORP:
    site = ins.get("site"); chron = ins.get("context"); sup = ins.get("support")
    did = ins.get("id")
    for st in ins.get("stream", []):
        if st.get("t") != "word":
            continue
        signs = st["signs"]
        wl = len(signs)
        wtup = tuple(ascii_tok(s) for s in signs)
        for i, s in enumerate(signs):
            c = canon(s)
            d = stat[c]
            d["freq"] += 1
            d["sites"][site]+=1; d["chron"][chron]+=1; d["support"][sup]+=1
            d["docs"].add(did)
            if wl == 1: d["n_sole"] += 1
            elif i == 0: d["n_initial"] += 1
            elif i == wl-1: d["n_final"] += 1
            else: d["n_interior"] += 1
            if wtup in FORMULA_TOTAL:
                d["in_formula_total"] += 1
                if wtup[:2]==("KU","RO"): d["in_KURO"]+=1
                if wtup[:2]==("KI","RO"): d["in_KIRO"]+=1
        # A- prefix head: word starts with A and len>=2 -> the A sign is a prefix head
        if wl >= 2 and ascii_tok(signs[0]) == "A":
            stat[canon(signs[0])]["as_A_prefix_head"] += 1

# ---- 2. substitution neighbours (C_la_graph) ------------------------------
sub_neigh = defaultdict(set)
for e in CGRAPH["sign_substitution_graph"]["top_edges"]:
    a, b = [ascii_tok(x) for x in e["signs"]]
    sub_neigh[canon(a)].add(canon(b)); sub_neigh[canon(b)].add(canon(a))
rel_class_of = {}
for rc in CGRAPH["rel_classes"]:
    for s in rc["signs"]:
        rel_class_of[canon(ascii_tok(s))] = rc["rel_class"]
# ---- 3. morphological neighbours (productive affixes) ----------------------
affix_role = {}
for af in CGRAPH.get("productive_affixes_secondary", []):
    affix_role.setdefault(canon(ascii_tok(af["affix"])), []).append(
        {"boundary":af["boundary"], "distinct_long_stems":af.get("distinct_long_stems"),
         "clean":af.get("clean")})

# ---- 4. anchor coverage (wp5) ---------------------------------------------
anchor = {}
for r in WP5["sign_inventory"]:
    sid = ascii_tok(r["sign_id"])
    anchor[canon(sid)] = {
        "conventional_value_LB_graded": r.get("conventional_value") or None,
        "dependency_tier": r.get("dependency_tier"),
        "n_independent_channels": r.get("n_independent_channels"),
        "robust_anchor": r.get("robust_anchor"),
        "channel_H_homomorphy_tier": r.get("channel_H_homomorphy_tier"),
        "channel_C_cypriot_stable": r.get("channel_C_cypriot_stable"),
        "strong_lexical_items": r.get("strong_lexical_items"),
    }
INDEP = set(canon(ascii_tok(s)) for s in WP5["summary"]["independent_signs"])

# ---- 5. SigLA stroke/image availability -----------------------------------
# 5a. glyph-bbox counts per SigLA sign name (the stroke/shape source)
glyph_count = Counter()
for d in SIG_DOCS:
    for g in d.get("glyphs", []):
        if g.get("sign") and not g.get("is_divider"):
            glyph_count[g["sign"]] += 1
sigla_names = set(s["name"] for s in SIG_SIGNS.values())
# 5b. induce phonetic<->AB cross-reference by positional voting on shared documents
#     (graded catalog cross-reference ONLY; earns no value, non-circular).
def norm_desig(x): return re.sub(r"[^A-Za-z0-9]", "", x).upper()
sig_by = {norm_desig(d["designation"]): d for d in SIG_DOCS}
vote = defaultdict(Counter)   # silver canonical key -> Counter(sigla_name)
aligned_docs = 0
for ins in CORP:
    key = norm_desig(ins["id"])
    sd = sig_by.get(key)
    if not sd: continue
    # silver ordered signs: words + logograms in stream order (skip div/nl/num)
    sv_seq = []
    for st in ins.get("stream", []):
        if st.get("t") == "word": sv_seq += [canon(s) for s in st["signs"]]
        elif st.get("t") in ("logo","ideo"):
            if st.get("v"): sv_seq.append(canon(st["v"]))
    sg_seq = [g["sign"] for g in sd.get("glyphs", []) if g.get("sign") and not g.get("is_divider")]
    if len(sv_seq) == len(sg_seq) and len(sv_seq) > 0:
        aligned_docs += 1
        for a, b in zip(sv_seq, sg_seq):
            vote[a][b] += 1
# resolve: top-voted SigLA name with >=2 votes and >=60% agreement
sigla_xref = {}
for c, ctr in vote.items():
    tot = sum(ctr.values()); name, n = ctr.most_common(1)[0]
    if n >= 2 and n/tot >= 0.6:
        sigla_xref[c] = {"sigla_name": name, "votes": n, "agreement": round(n/tot,3),
                         "glyph_bbox_count": glyph_count.get(name,0)}

def sigla_for(key, cls, fam):
    """Return (sigla_name, glyph_bbox_count, method) for stroke availability."""
    # A-only: *NNN -> A<NNN> via gorila number
    m = re.match(r"\*(\d+)", key)
    if m:
        nm = "A"+m.group(1)
        if nm in sigla_names or glyph_count.get(nm,0)>0:
            return nm, glyph_count.get(nm,0), "gorila_number"
    # induced cross-reference (AB-shared and others)
    if key in sigla_xref:
        x = sigla_xref[key]; return x["sigla_name"], x["glyph_bbox_count"], "doc_alignment_vote"
    fam_m = re.match(r"\*(\d+)", fam or "")
    if fam_m:
        nm = "A"+fam_m.group(1)
        if glyph_count.get(nm,0)>0: return nm, glyph_count.get(nm,0), "gorila_number_family"
    return None, 0, None

# ---- 6. literature-index status -------------------------------------------
lit_signs = Counter()
for c in LITIDX.get("claims", []):
    s = c.get("sign","")
    for part in re.split(r"[-\s]", s):
        p = ascii_tok(part.strip())
        if p: lit_signs[canon(p)] += 1

# ---- 7. candidate-value domain + uncertainty ------------------------------
def value_domain(cls):
    if cls == "syllabogram-AB":   return "syllabic_CV_or_V"
    if cls == "syllabogram-Aonly":return "syllabic_CV_or_V"
    if cls == "logogram":         return "commodity_ideogram_semantic"
    if cls == "numeral":          return "numeric_quantity"
    if cls == "fraction":         return "fractional_quantity"
    return "unknown"
def uncertainty(cls, freq, has_anchor, robust, has_sub):
    if cls in ("numeral","fraction"): return "value_type_known_quantity"
    if cls == "logogram": return "semantic_referent_debated"
    # syllabogram / uncertain
    if robust: return "low_relative_class_multichannel"
    if has_anchor and has_sub: return "medium_partial_relational_support"
    if freq >= 20: return "high_frequent_but_unanchored"
    return "very_high_rare_unanchored"

# ---- 8. assemble per-SPLIT-key records ------------------------------------
CLASS_MAP = {  # ontology class -> universe class label
    "syllabogram-AB":"AB-shared", "syllabogram-Aonly":"A-only",
    "logogram":"logogram", "numeral":"numeral", "fraction":"numeral",
    "uncertain":"uncertain",
}
def build_record(key):
    ov = ONT.get(key, {})
    cls_raw = ov.get("class","uncertain")
    cls = CLASS_MAP.get(cls_raw, "uncertain")
    fam = ov.get("allograph_family") or allograph_family(key)
    d = stat.get(key)
    an = anchor.get(key)
    sname, gcnt, smeth = sigla_for(key, cls_raw, fam)
    has_sub = key in sub_neigh or key in rel_class_of
    has_anchor = an is not None and (an.get("robust_anchor") or an.get("n_independent_channels",0)>=1 or an.get("conventional_value_LB_graded"))
    rec = {
        "canonical_id": key,
        "aliases": sorted(set(ov.get("diplomatic_tokens", [])) | {key}),
        "class": cls,
        "class_ontology": cls_raw,
        "allograph_family": fam,
        "conservative_id": conservative_id(key),
        "merged_id": merged_id(key),
        "occurrence_count": (d["freq"] if d else ov.get("frequency",0)),
        "attested_in_corpus": d is not None,
        "position_counts": ({"initial":d["n_initial"],"interior":d["n_interior"],
                             "final":d["n_final"],"sole":d["n_sole"]} if d else None),
        "n_documents": (len(d["docs"]) if d else 0),
        "site_distribution": (dict(d["sites"].most_common()) if d else {}),
        "chronology_distribution": (dict(d["chron"].most_common()) if d else {}),
        "support_distribution": (dict(d["support"].most_common()) if d else {}),
        "formula_slots": ({"in_total_formula":d["in_formula_total"],"in_KURO":d["in_KURO"],
                           "in_KIRO":d["in_KIRO"],"as_A_prefix_head":d["as_A_prefix_head"]} if d else None),
        "substitution_neighbors": sorted(sub_neigh.get(key, [])),
        "rel_class": rel_class_of.get(key),
        "morphological_role": affix_role.get(key),
        "cross_script": {
            "shared_with_linearB": cls == "AB-shared",
            "sigla_name": sname,
            "sigla_glyph_bbox_count": gcnt,
            "sigla_link_method": smeth,
        },
        "stroke_image_available": bool(sname and gcnt > 0),
        "anchor_coverage": an,
        "in_independent_multichannel_set": key in INDEP,
        "literature_index_mentions": lit_signs.get(key, 0),
        "candidate_value_domain": value_domain(cls_raw),
        "benchmark_label_graded_only": (an.get("conventional_value_LB_graded") if an else None),
        "has_substitution_coverage": has_sub,
        "has_anchor_coverage": bool(has_anchor),
        "uncertainty": uncertainty(cls_raw, (d["freq"] if d else 0), bool(has_anchor),
                                    bool(an and an.get("robust_anchor")), has_sub),
    }
    return rec

# universe = all ontology keys that are attested in corpus OR catalogued as signs
#   (exclude pure data-error / PUA placeholder from the syllabic variable count, keep tagged)
split_keys = sorted(set(stat.keys()) | set(ONT.keys()))
# drop tokens that never resolve to a real sign
split_keys = [k for k in split_keys if k in ONT or stat.get(k)]

records_split = {k: build_record(k) for k in split_keys}

# ---- aggregate SPLIT records up to CONSERVATIVE / MERGED grains ------------
def aggregate(records, idfunc):
    groups = defaultdict(list)
    for k, r in records.items():
        groups[idfunc(k)].append(r)
    out = {}
    for gid, rs in groups.items():
        base = dict(rs[0])
        base["canonical_id"] = gid
        base["members_split"] = sorted(r["canonical_id"] for r in rs)
        base["aliases"] = sorted(set().union(*[set(r["aliases"]) for r in rs]))
        base["occurrence_count"] = sum(r["occurrence_count"] for r in rs)
        base["attested_in_corpus"] = any(r["attested_in_corpus"] for r in rs)
        # merge position/formula
        def sumf(field, sub):
            vals = [r[field][sub] for r in rs if r.get(field)]
            return sum(vals) if vals else 0
        if any(r.get("position_counts") for r in rs):
            base["position_counts"] = {s: sumf("position_counts",s) for s in ("initial","interior","final","sole")}
        if any(r.get("formula_slots") for r in rs):
            base["formula_slots"] = {s: sumf("formula_slots",s) for s in ("in_total_formula","in_KURO","in_KIRO","as_A_prefix_head")}
        base["n_documents"] = None  # doc sets not unioned at agg grain
        for field in ("site_distribution","chronology_distribution","support_distribution"):
            c = Counter()
            for r in rs: c.update(r[field])
            base[field] = dict(c.most_common())
        base["substitution_neighbors"] = sorted(set().union(*[set(r["substitution_neighbors"]) for r in rs]))
        base["stroke_image_available"] = any(r["stroke_image_available"] for r in rs)
        base["has_substitution_coverage"] = any(r["has_substitution_coverage"] for r in rs)
        base["has_anchor_coverage"] = any(r["has_anchor_coverage"] for r in rs)
        base["in_independent_multichannel_set"] = any(r["in_independent_multichannel_set"] for r in rs)
        base["literature_index_mentions"] = sum(r["literature_index_mentions"] for r in rs)
        anchors = [r["anchor_coverage"] for r in rs if r["anchor_coverage"]]
        base["anchor_coverage"] = anchors[0] if anchors else None
        base["benchmark_label_graded_only"] = sorted(set(
            r["benchmark_label_graded_only"] for r in rs if r["benchmark_label_graded_only"])) or None
        out[gid] = base
    return out

records_cons   = aggregate(records_split, conservative_id)
records_merged = aggregate(records_split, merged_id)

# ---- coverage summaries ----------------------------------------------------
SYLLABIC = {"AB-shared","A-only","uncertain"}
def summarize(records, label):
    vals = list(records.values())
    by_class = Counter(r["class"] for r in vals)
    syll = [r for r in vals if r["class"] in SYLLABIC]
    # "unresolved sign" universe: everything that lacks a proven LA value.
    # AB-shared carry only a GRADED LB benchmark label, not a proven LA value -> still unresolved.
    unresolved = [r for r in vals if r["class"] in ("AB-shared","A-only","uncertain","logogram")]
    def cov(subset, field):
        return sum(1 for r in subset if r[field])
    return {
        "grain": label,
        "n_variables_total": len(vals),
        "by_class": dict(by_class),
        "n_syllabic_variables": len(syll),
        "n_unresolved_value_variables": len(unresolved),
        "n_attested_in_corpus": sum(1 for r in vals if r["attested_in_corpus"]),
        "coverage": {
            "stroke_image": cov(vals,"stroke_image_available"),
            "anchor": cov(vals,"has_anchor_coverage"),
            "substitution": cov(vals,"has_substitution_coverage"),
        },
        "coverage_syllabic_only": {
            "n": len(syll),
            "stroke_image": cov(syll,"stroke_image_available"),
            "anchor": cov(syll,"has_anchor_coverage"),
            "substitution": cov(syll,"has_substitution_coverage"),
            "any_of_three": sum(1 for r in syll if r["stroke_image_available"] or r["has_anchor_coverage"] or r["has_substitution_coverage"]),
            "all_three": sum(1 for r in syll if r["stroke_image_available"] and r["has_anchor_coverage"] and r["has_substitution_coverage"]),
            "none_of_three": sum(1 for r in syll if not (r["stroke_image_available"] or r["has_anchor_coverage"] or r["has_substitution_coverage"])),
            "robust_anchor": sum(1 for r in syll if r.get("anchor_coverage") and r["anchor_coverage"].get("robust_anchor")),
            "independent_multichannel": sum(1 for r in syll if r["in_independent_multichannel_set"]),
        },
    }

grains = {
    "SIGN_UNIVERSE_ALLOGRAPH_SPLIT": (records_split, "split", "conservative.json".replace("conservative","split")),
    "SIGN_UNIVERSE_CONSERVATIVE":    (records_cons, "conservative", "conservative.json"),
    "SIGN_UNIVERSE_ALLOGRAPH_MERGED":(records_merged, "merged", "merged.json"),
}
fname = {"SIGN_UNIVERSE_ALLOGRAPH_SPLIT":"split.json",
         "SIGN_UNIVERSE_CONSERVATIVE":"conservative.json",
         "SIGN_UNIVERSE_ALLOGRAPH_MERGED":"merged.json"}

summaries = {}
for name,(recs,lab,_) in grains.items():
    summ = summarize(recs, lab)
    summaries[name] = summ
    out = {
        "inventory": name, "grain": lab, "seed": SEED,
        "non_circular_note": ("LB/GORILA conventional values attached as GRADED benchmark labels "
            "only (benchmark_label_graded_only); never a variable input, earn no value/licence. "
            "SigLA cross-reference is a graded catalog link (doc-alignment vote / GORILA number)."),
        "definition": {
            "split":"every catalogued sign distinct (letter/subscript allographs separate)",
            "conservative":"repo-audited expert merges only (*131B/*131C->*131; subscript AB kept distinct)",
            "merged":"also fold subscript AB into graphic base (RA2->RA, PA3->PA, TA2->TA, PU2->PU)",
        }[lab],
        "summary": summ,
        "signs": recs,
    }
    with open(os.path.join(OUT_DATA, fname[name]), "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)

meta = {
    "seed": SEED,
    "corpus": {"inscriptions": len(CORP), "distinct_corpus_word_tokens": len(stat)},
    "sigla_alignment": {"shared_docs_aligned_equal_length": aligned_docs,
                        "induced_xref_signs": len(sigla_xref)},
    "grain_counts": {n: summaries[n]["n_variables_total"] for n in grains},
    "summaries": summaries,
}
with open(os.path.join(OUT_DATA, "_meta.json"), "w") as f:
    json.dump(meta, f, indent=1, ensure_ascii=False)

print(json.dumps(meta, indent=1, ensure_ascii=False))
