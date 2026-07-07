#!/usr/bin/env python3
"""C1 — SUBSTITUTION / ALTERNATION CANDIDATES (Constitution v2.2, Art. III/V/XI/XII).

GOAL. Find pairs (and families) of Linear A word-forms that differ by ONE sign (equal length =
SUBSTITUTION) or by a single insert/delete (length differs by 1 = INDEL/affixal) in MATCHED
contexts, and separate them into the philological categories that an editor would use to explain
the difference: same-document, same-formula, same-site, cross-site, chronological, possible
scribal-correction, possible allographic-variation, damage-induced, edition-disagreement.

STRICTLY NON-PHONETIC. No Linear B value is ever assigned to any Linear A sign. Signs are compared
as OPAQUE identity tokens (the GORILA/SigLA Latin transliteration string). We are cataloguing
RELATIVE structure — which forms stand in a one-sign contrast in a shared context — not reading
anything. Every candidate carries an explicit NON-phonological alternative explanation and a
dependency-cluster note (the whole silver word-stream descends from the single GORILA/Ventris
homomorphic transliteration lineage; SigLA adds an independent palaeographic edition used ONLY to
flag edition-disagreements).

Sources
  * silver GORILA word units  : corpus/silver/inscriptions_structured.json (3,147 word units).
  * SigLA (independent edition): corpus/bronze/sigla_browse_2026/database.js, decoded to
    sigla_documents.json (Salgarella & Castellan, CC BY-NC-SA; licensed-derived, gitignored).
    Used ONLY to detect single-locus edition disagreements on 575 shared documents.

Deterministic, seed 20260708, pure stdlib.
"""
from __future__ import annotations

import difflib
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict

SEED = 20260708
MAIN = "/home/claude-runner/gitlab/n8n/logos"
HERE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.dirname(HERE)
DATA = os.path.join(CAMP, "data")
REPORTS = os.path.join(CAMP, "reports")
STRUCTURED = os.path.join(MAIN, "corpus", "silver", "inscriptions_structured.json")
SIGLA_JSON = "/tmp/claude-1000/-home-claude-runner-gitlab-n8n-logos/0f4d307e-2ce9-4892-991d-bdc274686cce/scratchpad/sigla_documents.json"
AB2VAL = "/tmp/claude-1000/-home-claude-runner-gitlab-n8n-logos/0f4d307e-2ce9-4892-991d-bdc274686cce/scratchpad/ab2val.json"

SUBSCRIPT = "₀₁₂₃₄₅₆₇₈₉"
# A "clean syllabogram" token: pure CV/V syllabogram (optionally with an allograph digit), i.e. the
# kind of sign that COULD carry a phonological contrast. Excludes *NNN unidentified signs,
# logograms/ligatures (VIN, OLE+U, VIR+KA, CYP, +, numeric fractions), which are representational.
_SYLL = re.compile(r"^[A-Z][A-Z]?[0-9]?$")
_LOGOGRAM_WORDS = {"VIN", "OLE", "GRA", "FIC", "CYP", "VIR", "OVIS", "SUS", "BOS", "AROM",
                   "VINa", "OLIV", "NI"}  # NI doubles as fig logogram; treated case-by-case below


# --------------------------------------------------------------------------- helpers
def desub(s: str) -> str:
    """Normalise subscript digits to ASCII (RA₂ -> RA2). Identity otherwise."""
    return "".join(str(SUBSCRIPT.index(c)) if c in SUBSCRIPT else c for c in s)


def is_syllabogram(tok: str) -> bool:
    """True iff tok is a clean identified syllabogram (a possible phonological slot)."""
    if tok.startswith("*") or "+" in tok or tok.startswith("A") and re.match(r"^A\d\d", tok):
        return False
    return bool(_SYLL.match(desub(tok)))


def is_unidentified(tok: str) -> bool:
    """*NNN GORILA unidentified sign, or a fraction/measure sign — a reading-gap slot."""
    return tok.startswith("*") or re.match(r"^A\d\d", tok) is not None


def allograph_base(tok: str):
    """Collapse a numbered/lettered allograph to its base sign.
    * star / A-code sign: a trailing LETTER is a variant marker (*131B/*131C -> *131,
      *21F/*21M -> *21); the numeric core IS the sign identity and is kept.
    * plain CV syllabogram: a trailing DIGIT is a variant marker (RA2 -> RA, PA3 -> PA,
      A2 -> A); a trailing LETTER is part of the syllabogram (JE, JA, KU are NOT variants).
    Returns the token itself when there is no variant marker."""
    t = desub(tok)
    if t.startswith("*") or re.match(r"^A\d\d", t):
        if len(t) > 1 and t[-1].isalpha() and any(ch.isdigit() for ch in t):
            return t[:-1]
        return t
    return re.sub(r"\d+$", "", t)


def allograph_related(a: str, b: str) -> bool:
    """True iff a,b are numbered/lettered allographs of one base (RA/RA2, *21F/*21M, *131B/*131C)."""
    a, b = desub(a), desub(b)
    if a == b:
        return False
    return allograph_base(a) == allograph_base(b)


CHRONO_ORDER = {"MMIA": 1, "MMII": 2, "MMIIA": 2, "MMIIB": 2, "MMIII": 3, "MMIIIA": 3,
                "MMIIIB": 3, "LMI": 4, "LMIA": 4, "LMIB": 5, "LBI": 5, "LMII": 6,
                "LMIIIA": 7, "LMIII": 7, "Geometric": 9}


# --------------------------------------------------------------------------- load silver
def load_word_units():
    docs = json.load(open(STRUCTURED))
    # occurrences: for each word token, its context in the doc's meaningful stream
    occ = []                      # list of dicts
    type_occ = defaultdict(list)  # word_type(tuple) -> list of occ indices
    for d in docs:
        did, site = d["id"], d["site"]
        chrono = d.get("context") or ""
        support = d.get("support") or ""
        # build a meaningful event list (drop nl); track word units with neighbours
        ev = [t for t in d.get("stream", []) if t.get("t") != "nl"]
        # positions of word events
        word_idx_in_doc = 0
        n_words_doc = sum(1 for t in ev if t["t"] == "word")
        for i, t in enumerate(ev):
            if t["t"] != "word":
                continue
            signs = tuple(t["signs"])
            prev = ev[i - 1] if i > 0 else None
            nxt = ev[i + 1] if i + 1 < len(ev) else None

            def wt(x):
                return tuple(x["signs"]) if x and x["t"] == "word" else None

            def kind(x):
                if x is None:
                    return "EDGE"
                return x["t"]
            o = {
                "type": signs,
                "doc": did, "site": site, "chrono": chrono, "support": support,
                "word_pos": word_idx_in_doc, "n_words_doc": n_words_doc,
                "prev_kind": kind(prev), "next_kind": kind(nxt),
                "prev_word": wt(prev), "next_word": wt(nxt),
                "followed_by_num": (nxt is not None and nxt.get("t") == "num"),
                "preceded_by_break": (prev is None or prev.get("t") in ("div",)),
            }
            occ.append(o)
            type_occ[signs].append(len(occ) - 1)
            word_idx_in_doc += 1
    return docs, occ, type_occ


# --------------------------------------------------------------------------- pair generation
def substitution_pairs(types):
    """Equal-length, differ at exactly one position. Returns list of (t1,t2,pos)."""
    pairs = {}
    by_key = defaultdict(list)   # (len, blank_pos, context) -> list of (type, fill)
    for t in types:
        L = len(t)
        if L < 2:
            continue
        for p in range(L):
            ctx = t[:p] + ("\x00",) + t[p + 1:]
            by_key[(L, p, ctx)].append((t, t[p]))
    for (L, p, ctx), members in by_key.items():
        if len(members) < 2:
            continue
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                t1, f1 = members[i]
                t2, f2 = members[j]
                if f1 == f2:
                    continue
                key = frozenset((t1, t2))
                if key not in pairs:
                    pairs[key] = (t1, t2, p)
    return list(pairs.values())


def indel_pairs(types):
    """Length differs by exactly 1, edit distance 1 (one sign inserted/deleted).
    Returns list of (long_type, short_type, del_pos, inserted_sign)."""
    by_len = defaultdict(set)
    for t in types:
        by_len[len(t)].add(t)
    out = {}
    for L in sorted(by_len):
        longs = by_len[L]
        shorts = by_len.get(L - 1, set())
        if not shorts:
            continue
        for t in longs:
            for p in range(L):
                sub = t[:p] + t[p + 1:]
                if sub in shorts:
                    key = frozenset((t, sub))
                    if key not in out:
                        out[key] = (t, sub, p, t[p])
    return list(out.values())


# --------------------------------------------------------------------------- metadata per form
def form_meta(t, type_occ, occ):
    idxs = type_occ.get(t, [])
    docs = sorted({occ[i]["doc"] for i in idxs})
    sites = sorted({occ[i]["site"] for i in idxs})
    chronos = sorted({occ[i]["chrono"] for i in idxs if occ[i]["chrono"]})
    supports = sorted({occ[i]["support"] for i in idxs})
    prev_ctx = Counter()
    next_ctx = Counter()
    n_followed_num = 0
    n_list_entry = 0
    for i in idxs:
        o = occ[i]
        if o["prev_word"]:
            prev_ctx[("PREV", o["prev_word"])] += 1
        if o["next_word"]:
            next_ctx[("NEXT", o["next_word"])] += 1
        if o["followed_by_num"]:
            n_followed_num += 1
        if o["preceded_by_break"] and o["followed_by_num"]:
            n_list_entry += 1
    return {
        "form": list(t), "freq": len(idxs), "docs": docs, "sites": sites,
        "chronos": chronos, "supports": supports,
        "prev_ctx": prev_ctx, "next_ctx": next_ctx,
        "n_followed_num": n_followed_num, "n_list_entry": n_list_entry,
    }


def context_overlap(ma, mb):
    """Shared external neighbour contexts (paradigmatic slots) between the two forms."""
    pa = set(ma["prev_ctx"]) | set(ma["next_ctx"])
    pb = set(mb["prev_ctx"]) | set(mb["next_ctx"])
    shared = pa & pb
    union = pa | pb
    jac = len(shared) / len(union) if union else 0.0
    return shared, round(jac, 4)


def cand_id(kind, t1, t2):
    h = hashlib.sha1((kind + "|" + " ".join(t1) + "||" + " ".join(t2)).encode()).hexdigest()[:12]
    return kind[:3].upper() + "-" + h


# --------------------------------------------------------------------------- classification
def classify(kind, forms, diff, type_occ, occ):
    (ta, tb) = forms
    ma = form_meta(ta, type_occ, occ)
    mb = form_meta(tb, type_occ, occ)
    shared_ctx, ctx_jac = context_overlap(ma, mb)

    # co-occurrence in a single document
    shared_docs = sorted(set(ma["docs"]) & set(mb["docs"]))
    shared_sites = sorted(set(ma["sites"]) & set(mb["sites"]))
    all_sites = sorted(set(ma["sites"]) | set(mb["sites"]))
    all_chronos = sorted(set(ma["chronos"]) | set(mb["chronos"]))

    # differing signs
    if kind == "SUB":
        pos = diff
        sa, sb = ta[pos], tb[pos]
        diff_signs = [sa, sb]
    else:  # INDEL
        sa, sb = diff, None  # inserted sign
        diff_signs = [diff]

    tags = []

    # damage-induced: a differing sign is an unidentified *NNN / fraction
    damage = any(is_unidentified(s) for s in diff_signs if s)
    if damage:
        tags.append("damage_induced")

    # allographic variation (SUB only, numbered/lettered variant of same base)
    allographic = (kind == "SUB" and allograph_related(sa, sb))
    if allographic:
        tags.append("allographic_variation")

    # possible scribal correction: same doc, the two forms are adjacent word units (|Δpos|<=1)
    scribal = False
    if shared_docs:
        tags.append("same_document")
        # adjacency within a shared document
        for did in shared_docs:
            pa = [occ[i]["word_pos"] for i in type_occ[ta] if occ[i]["doc"] == did]
            pb = [occ[i]["word_pos"] for i in type_occ[tb] if occ[i]["doc"] == did]
            if any(abs(x - y) <= 1 for x in pa for y in pb):
                scribal = True
        if scribal:
            tags.append("possible_scribal_correction")

    # same-formula: share a specific neighbouring WORD context (paradigmatic slot)
    if shared_ctx:
        tags.append("same_formula")

    # spatial
    if shared_sites:
        tags.append("same_site")
    if not shared_sites and ma["sites"] and mb["sites"]:
        tags.append("cross_site")

    # chronological: the two forms sit in disjoint, dated chronological phases
    chrono_a = set(ma["chronos"])
    chrono_b = set(mb["chronos"])
    if chrono_a and chrono_b and not (chrono_a & chrono_b):
        # only meaningful if the phases are actually distinct in time-order
        oa = {CHRONO_ORDER.get(c) for c in chrono_a if c in CHRONO_ORDER}
        ob = {CHRONO_ORDER.get(c) for c in chrono_b if c in CHRONO_ORDER}
        if oa and ob and oa != ob:
            tags.append("chronological")

    # ---- primary category (mutually exclusive), priority order ----
    priority = ["damage_induced", "allographic_variation", "possible_scribal_correction",
                "same_document", "same_formula", "same_site", "cross_site"]
    primary = next((c for c in priority if c in tags), "unmatched_context")

    # ---- quality tier ----
    clean = all(is_syllabogram(s) for s in diff_signs if s)
    both_multi = ma["freq"] >= 2 and mb["freq"] >= 2
    one_multi = ma["freq"] >= 2 or mb["freq"] >= 2
    controlled = ("same_document" in tags) or ("same_formula" in tags)
    confound = damage or allographic
    if kind == "SUB" and clean and both_multi and controlled and not confound:
        tier = "A"
    elif kind == "SUB" and clean and one_multi and (controlled or "same_site" in tags) and not confound:
        tier = "B"
    elif damage or (kind == "INDEL" and not controlled):
        tier = "D"
    elif ("cross_site" in tags and not controlled) or allographic or (not one_multi) \
            or (not clean):
        tier = "C"
    else:
        tier = "C"
    if damage:
        tier = "D"

    # ---- non-phonological alternative explanation ----
    alts = []
    if damage:
        alts.append("A differing sign is a GORILA-unidentified/damaged sign (*NNN or measure); the "
                    "contrast may be a reading gap, not a real alternation.")
    if allographic:
        alts.append("The two signs are numbered/lettered allographs of one base sign (orthographic "
                    "homophone/variant), not a phonological substitution.")
    if "cross_site" in tags and not controlled:
        alts.append("Two forms attested only at different sites in no shared context: likely two "
                    "distinct lexemes that are coincidental near-homographs, not one alternating word.")
    if "possible_scribal_correction" in tags:
        alts.append("Adjacent occurrences in one document may be dittography or an in-situ correction, "
                    "or simply two distinct list entries, not a paradigmatic alternation.")
    if primary in ("same_document", "same_site") and not shared_ctx:
        alts.append("Co-listing (two distinct personal names / toponyms / commodities enumerated in "
                    "the same ledger) explains the pair without any phonological relationship.")
    if kind == "INDEL":
        alts.append("A one-sign length difference can be affixation/logographic determinative or a "
                    "segmentation artefact rather than a substitution.")
    if not alts:
        alts.append("A one-sign minimal pair does not entail phonological relatedness on a corpus this "
                    "small; the contrast can be two unrelated lexemes (base-rate near-homography).")

    # segmentation note
    seg = ("Both forms are whole GORILA word units (segmentation-dependent). "
           f"len(A)={len(ta)}, len(B)={len(tb)}.")

    return {
        "id": cand_id(kind, ta, tb),
        "kind": kind,
        "forms": {"A": list(ta), "B": list(tb)},
        "diff": ({"position": diff, "sign_A": sa, "sign_B": sb} if kind == "SUB"
                 else {"inserted_sign": diff, "long": list(ta), "short": list(tb)}),
        "freq": {"A": ma["freq"], "B": mb["freq"]},
        "documents": {"A": ma["docs"], "B": mb["docs"], "shared": shared_docs},
        "sites": {"A": ma["sites"], "B": mb["sites"], "shared": shared_sites, "all": all_sites},
        "chronology": {"A": ma["chronos"], "B": mb["chronos"], "all": all_chronos},
        "supports": {"A": ma["supports"], "B": mb["supports"]},
        "source_editions": ["GORILA/silver (L_GORILA_VENTRIS transliteration lineage)"],
        "damage_status": ("differing sign(s) include an unidentified/measure sign" if damage
                          else "all differing signs are identified in GORILA"),
        "segmentation": seg,
        "context_similarity": {
            "shared_neighbour_contexts": [list(x[1]) if isinstance(x[1], tuple) else x[1]
                                          for x in sorted(shared_ctx)][:12],
            "n_shared_neighbour_contexts": len(shared_ctx),
            "neighbour_context_jaccard": ctx_jac,
            "internal_shared_signs": (len(ta) - 1 if kind == "SUB" else min(len(ta), len(tb))),
        },
        "category_tags": tags,
        "primary_category": primary,
        "chronological_flag": ("chronological" in tags),
        "alternative_explanation": " ".join(alts),
        "dependency_cluster": ("L_GORILA_VENTRIS — both sign identities and the word segmentation "
                               "descend from the single GORILA homomorphic transliteration lineage; "
                               "no independent channel corroborates the contrast (SigLA palaeography "
                               "checked separately for edition disagreement)."),
        "quality_tier": tier,
    }


# --------------------------------------------------------------------------- edition disagreement
def edition_disagreements():
    """Single-locus disagreements between GORILA/silver and the independent SigLA edition on the 575
    shared documents. Restricted to positions where BOTH editions give a clean syllabogram."""
    if not (os.path.exists(SIGLA_JSON) and os.path.exists(AB2VAL)):
        return [], {"available": False, "reason": "SigLA decode / ab2val not present"}
    ab = json.load(open(AB2VAL))
    sv = {d["id"]: d for d in json.load(open(STRUCTURED))}
    sg = {x["designation"].replace(" ", "").upper(): x for x in json.load(open(SIGLA_JSON))}

    def abmap(code):
        m = re.match(r"AB0*(\d+)([A-Z]?)$", code)
        if not m:
            return code
        n, suf = m.group(1), m.group(2)
        key = "AB%02d" % int(n)
        return (ab[key] + suf) if key in ab else ("*" + n + suf)

    out = []
    n_common = 0
    for did, s in sv.items():
        g = sg.get(did.upper())
        if not g:
            continue
        n_common += 1
        sv_signs = [desub(x) for x in s["signs"]]
        sg_signs = [abmap(t) for t in g["transcription"]]
        sm = difflib.SequenceMatcher(a=sv_signs, b=sg_signs, autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "replace" and (i2 - i1) == 1 and (j2 - j1) == 1:
                a, b = sv_signs[i1], sg_signs[j1]
                if a == b:
                    continue
                both_syll = is_syllabogram(a) and is_syllabogram(b)
                allo = allograph_related(a, b)
                clazz = ("syllabogram_disagreement" if both_syll
                         else ("allograph_or_star_disagreement" if allo
                               else "representational (logogram/unidentified) — excluded from phon."))
                out.append({
                    "id": "EDI-" + hashlib.sha1((did + a + b + str(i1)).encode()).hexdigest()[:10],
                    "kind": "EDITION",
                    "document": did, "site": s["site"], "chrono": s.get("context") or "",
                    "locus_index_silver": i1,
                    "GORILA_silver": a, "SigLA": b,
                    "class": clazz,
                    "both_clean_syllabograms": both_syll,
                    "allograph_related": allo,
                    "primary_category": "edition_disagreement",
                    "quality_tier": ("C" if both_syll else "D"),
                    "source_editions": ["GORILA/silver (L_GORILA_VENTRIS)",
                                        "SigLA (L_LA_PALAEOGRAPHY, independent edition)"],
                    "alternative_explanation": (
                        "The two editions read the physical sign differently; the 'substitution' is an "
                        "editorial reading disagreement, not an in-language alternation."),
                    "dependency_cluster": "cross-edition (GORILA vs SigLA) — palaeographic, not phonological.",
                })
    meta = {"available": True, "shared_documents_compared": n_common,
            "total_single_locus_disagreements": len(out),
            "syllabogram_level": sum(1 for x in out if x["both_clean_syllabograms"])}
    return out, meta


# --------------------------------------------------------------------------- run
def run():
    os.makedirs(DATA, exist_ok=True)
    os.makedirs(REPORTS, exist_ok=True)
    docs, occ, type_occ = load_word_units()
    types = list(type_occ)
    n_tokens = sum(len(v) for v in type_occ.values())

    sub = substitution_pairs(types)
    ind = indel_pairs(types)

    cands = []
    for (t1, t2, p) in sub:
        cands.append(classify("SUB", (t1, t2), p, type_occ, occ))
    for (tl, ts, p, ins) in ind:
        cands.append(classify("INDEL", (tl, ts), ins, type_occ, occ))

    # ---- ALTERNATION FAMILIES: connected components over SUBSTITUTION edges ----
    # A family = a set of word-forms mutually linked by single-sign substitutions (a paradigm-like
    # cluster, e.g. the {KU,KI,SA,RE,NU,*86}-RO deficit/total family). This is the substitution
    # dependency cluster (which interlinked candidates a form participates in).
    adj = defaultdict(set)
    for (t1, t2, p) in sub:
        adj[t1].add(t2)
        adj[t2].add(t1)
    fam_of = {}
    families = []
    seen = set()
    for node in adj:
        if node in seen:
            continue
        stack = [node]
        comp = []
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            comp.append(x)
            stack.extend(adj[x] - seen)
        fid = "FAM-" + hashlib.sha1((" ".join(sorted(" ".join(c) for c in comp))).encode()).hexdigest()[:10]
        for c in comp:
            fam_of[c] = fid
        families.append({
            "family_id": fid, "size_forms": len(comp),
            "n_substitution_edges": sum(1 for (a, b, _) in sub if a in set(comp) and b in set(comp)),
            "forms": ["-".join(c) for c in sorted(comp, key=lambda z: (-sum(len(type_occ[z2]) for z2 in [z]), z))][:40],
            "total_tokens": sum(len(type_occ[c]) for c in comp),
        })
    families.sort(key=lambda f: (-f["size_forms"], -f["total_tokens"]))
    # annotate SUB candidates with their family
    fam_size = {f["family_id"]: f["size_forms"] for f in families}
    for c in cands:
        if c["kind"] == "SUB":
            a = tuple(c["forms"]["A"])
            fid = fam_of.get(a)
            c["substitution_family"] = {"family_id": fid, "family_size_forms": fam_size.get(fid)}
        else:
            c["substitution_family"] = {"family_id": None, "family_size_forms": None}

    edis, edmeta = edition_disagreements()

    # ---- tallies ----
    cat_tags = Counter()
    for c in cands:
        for t in c["category_tags"]:
            cat_tags[t] += 1
        if not c["category_tags"]:
            cat_tags["unmatched_context"] += 1
    primary = Counter(c["primary_category"] for c in cands)
    tiers = Counter(c["quality_tier"] for c in cands)
    kinds = Counter(c["kind"] for c in cands)
    chrono_n = sum(1 for c in cands if c["chronological_flag"])

    # add edition disagreements into the primary/tier tallies as their own category
    primary["edition_disagreement"] = len(edis)
    for e in edis:
        tiers[e["quality_tier"]] += 1

    out = {
        "experiment": "C1_substitution_alternation_candidates",
        "seed": SEED,
        "non_phonetic": "signs compared as opaque identity tokens; NO Linear B value assigned",
        "corpus": {
            "word_units": n_tokens, "word_types": len(types),
            "documents": len(docs),
            "types_len_ge2": sum(1 for t in types if len(t) >= 2),
        },
        "counts": {
            "substitution_pairs": len(sub),
            "indel_pairs": len(ind),
            "total_wordpair_candidates": len(cands),
            "edition_disagreement_loci": len(edis),
        },
        "primary_category_distribution": dict(primary.most_common()),
        "category_tag_distribution_nonexclusive": dict(cat_tags.most_common()),
        "chronological_flagged": chrono_n,
        "quality_tier_distribution": dict(sorted(tiers.items())),
        "kind_distribution": dict(kinds),
        "edition_disagreement_meta": edmeta,
        "alternation_families": {
            "n_families": len(families),
            "n_multiform_families": sum(1 for f in families if f["size_forms"] >= 3),
            "largest": families[:40],
        },
        "candidates": cands,
        "edition_disagreement_candidates": edis,
    }
    outpath = os.path.join(DATA, "C1_candidates.json")
    json.dump(out, open(outpath, "w"), indent=1, ensure_ascii=False)
    # console summary
    print(json.dumps({k: v for k, v in out.items()
                      if k not in ("candidates", "edition_disagreement_candidates")}, indent=1))
    print("\nWROTE", outpath, "  (", os.path.getsize(outpath), "bytes )")
    return out


if __name__ == "__main__":
    run()
