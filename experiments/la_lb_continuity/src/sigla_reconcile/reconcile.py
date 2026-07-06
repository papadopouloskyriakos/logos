#!/usr/bin/env python3
"""Deterministic SigLA ↔ silver reconciliation (§IV).

Builds a designation crosswalk (SigLA ↔ silver ↔ GORILA), a metadata-agreement report, and a
corpus-delta. NO source is silently deemed correct: every disagreement is a delta category, not a
correction. The learned AB#→value table is a LABELLED reconciliation AID (evidence the sources agree
on shared AB signs); it is LEVEL_3-adjacent and MUST NOT be used by the continuity primary model.

Run:  python3 experiments/la_lb_continuity/src/sigla_reconcile/reconcile.py [--out DIR]
Emits RECONCILE_SUMMARY.json + crosswalk/delta JSON to --out (default data/, gitignored) and prints
all figures (the reports transcribe these — invariant 12: counts generated, not hand-written).
"""
import argparse, json, os, re, sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(__file__))
import config  # noqa: E402


def norm_desig(s):
    """SigLA 'HT 24a' and silver 'HT24a' -> canonical 'HT24A' (strict: spaces + case only)."""
    return re.sub(r"\s+", "", str(s)).upper()

# Greek face letters (roundel/nodule faces) -> Latin, for the LENIENT base crosswalk only.
_GREEK = {"Α": "A", "Β": "B", "Γ": "G", "Δ": "D", "Ε": "E", "Ζ": "Z", "Η": "H", "Θ": "TH",
          "α": "A", "β": "B", "γ": "G", "δ": "D", "ε": "E", "ζ": "Z"}

def base_key(s):
    """Collapse face/join/cruft granularity to a shared BASE: 'HTWA1019Α'->'HTWA1019',
    'HT24a'->'HT24', 'HT123+124A'->'HT123'. Used ONLY to diagnose convention-vs-genuine divergence —
    NEVER as an exact identity (it deliberately over-merges)."""
    k = norm_desig(s)
    k = "".join(_GREEK.get(ch, ch) for ch in k)
    k = re.sub(r"[<>\.\[\]]", "", k)
    k = k.split("+")[0]                       # a join fragment -> its first member
    k = re.sub(r"(?<=\d)[A-Z]{1,2}$", "", k)  # trailing 1-2 face letters after a digit
    return k

def norm_period(s):
    return re.sub(r"\s+", "", str(s or "")).upper()  # 'LM IB' / 'LMIB' -> 'LMIB'


def load():
    sigla = json.load(open(config.SIGLA_DOCUMENTS, encoding="utf-8"))
    signs = json.load(open(config.SIGLA_SIGNS, encoding="utf-8"))
    silver = json.load(open(config.SILVER, encoding="utf-8"))
    S = {}
    for d in sigla:
        S[norm_desig(d["designation"])] = d
    V = {}
    for r in silver:
        V[norm_desig(r["id"])] = r
    return S, V, signs


def learn_ab_value(S, V, matched):
    """Learn AB#->phonetic value by 1:1 alignment on matched docs whose AB-subsequence length equals
    the silver sign count (pure-syllabic, no composite gap). Returns (table, consistency, votes, n_docs)."""
    votes = defaultdict(Counter)
    n = 0
    for k in matched:
        ab = [g for g in S[k]["transcription"] if g.startswith("AB")]
        sig = V[k]["signs"]
        if ab and len(ab) == len(sig):
            n += 1
            for a, s in zip(ab, sig):
                votes[a][s] += 1
    table, consist = {}, {}
    for a, c in votes.items():
        top, m = c.most_common(1)[0]
        table[a] = top
        consist[a] = round(m / sum(c.values()), 4)
    return table, consist, {a: dict(c) for a, c in votes.items()}, n


def reconcile():
    S, V, signs = load()
    ks, kv = set(S), set(V)
    matched = sorted(ks & kv)
    only_sigla = sorted(ks - kv)
    only_silver = sorted(kv - ks)

    # LENIENT base-level crosswalk: how much of the residual is face/join/cruft granularity vs genuine absence
    sigla_bases = {base_key(k) for k in ks}
    silver_bases = {base_key(k) for k in kv}
    only_silver_base_in_sigla = sum(1 for k in only_silver if base_key(k) in sigla_bases)
    only_sigla_base_in_silver = sum(1 for k in only_sigla if base_key(k) in silver_bases)
    base_matched = len(sigla_bases & silver_bases)

    # metadata agreement on matched
    site_agree = site_diff = 0
    period_agree = period_diff = period_na = 0
    support_agree = support_diff = 0
    site_conflicts, period_conflicts = [], []
    for k in matched:
        s, v = S[k], V[k]
        if (s.get("site") or "") == (v.get("site") or ""):
            site_agree += 1
        else:
            site_diff += 1
            if len(site_conflicts) < 20: site_conflicts.append((k, s.get("site"), v.get("site")))
        sp, vp = norm_period(s.get("period")), norm_period(v.get("context"))
        if not sp or not vp: period_na += 1
        elif sp == vp: period_agree += 1
        else:
            period_diff += 1
            if len(period_conflicts) < 20: period_conflicts.append((k, s.get("period"), v.get("context")))
        if (s.get("support") or "").lower() == (v.get("support") or "").lower():
            support_agree += 1
        else:
            support_diff += 1

    # segmentation / length delta: SigLA identified-sign count vs silver sign count
    len_equal = len_sigla_more = len_silver_more = 0
    len_delta_hist = Counter()
    seg_examples = []
    for k in matched:
        ns = len(S[k]["transcription"])      # SigLA identified signs (excludes dividers/unread)
        nv = len(V[k]["signs"])              # silver phonetic signs
        d = ns - nv
        len_delta_hist[max(-3, min(3, d))] += 1
        if d == 0: len_equal += 1
        elif d > 0: len_sigla_more += 1
        else:
            len_silver_more += 1
            if len(seg_examples) < 15:
                seg_examples.append((k, ns, nv,
                                     sum(1 for g in S[k]["transcription"] if not g.startswith("AB"))))

    # sign-class composition (why lengths differ): SigLA A-series (composites/ligatures) vs AB
    ab_glyphs = a_glyphs = 0
    for k in matched:
        for g in S[k]["transcription"]:
            if g.startswith("AB"): ab_glyphs += 1
            else: a_glyphs += 1

    # learned AB#->value aid (labelled; not for the continuity model)
    ab_table, ab_consist, ab_votes, ab_ndocs = learn_ab_value(S, V, matched)
    ab_clean = sum(1 for a in ab_consist if ab_consist[a] >= 0.98)

    # sign-inventory crosswalk: SigLA A### <-> silver *### token; count overlap
    silver_star = set()
    for r in V.values():
        for tok in r["signs"]:
            if tok.startswith("*"): silver_star.add(tok[1:])   # '*301' -> '301'
    sigla_a_nums = {str(s["gorila_number"]) for s in signs.values() if s["class"] == "A"}
    a_star_overlap = sorted(sigla_a_nums & silver_star, key=lambda x: int(x) if x.isdigit() else 0)

    summary = {
        "inputs": config.input_manifest(),
        "counts": {"sigla_docs": len(S), "silver_records": len(V), "sigla_signs": len(signs),
                   "matched": len(matched), "only_sigla": len(only_sigla), "only_silver": len(only_silver)},
        "base_level_crosswalk": {
            "base_matched": base_matched,
            "only_silver_resolved_by_base": only_silver_base_in_sigla,
            "only_sigla_resolved_by_base": only_sigla_base_in_silver,
            "only_silver_genuinely_absent": len(only_silver) - only_silver_base_in_sigla,
            "only_sigla_genuinely_absent": len(only_sigla) - only_sigla_base_in_silver,
            "note": "base_key over-merges faces/joins/cruft ON PURPOSE — diagnostic only, not identity"},
        "metadata_agreement_on_matched": {
            "site_agree": site_agree, "site_diff": site_diff,
            "period_agree": period_agree, "period_diff": period_diff, "period_na": period_na,
            "support_agree": support_agree, "support_diff": support_diff},
        "segmentation_delta": {
            "len_equal": len_equal, "sigla_more": len_sigla_more, "silver_more": len_silver_more,
            "delta_hist_clamped_-3..3": dict(sorted(len_delta_hist.items()))},
        "sign_class_on_matched": {"ab_glyphs": ab_glyphs, "a_series_glyphs": a_glyphs},
        "learned_ab_value_aid": {"docs_used": ab_ndocs, "distinct_ab": len(ab_table),
                                 "ge98pct_consistent": ab_clean, "table": ab_table, "consistency": ab_consist},
        "sign_inventory_crosswalk": {"sigla_A_numbers": len(sigla_a_nums), "silver_star_numbers": len(silver_star),
                                     "A_starnum_overlap": len(a_star_overlap)},
        "examples": {"site_conflicts": site_conflicts, "period_conflicts": period_conflicts,
                     "segmentation_silver_more": seg_examples,
                     "only_sigla_head": only_sigla[:30], "only_silver_head": only_silver[:30]},
    }
    return summary, {"matched": matched, "only_sigla": only_sigla, "only_silver": only_silver,
                     "ab_value_votes": ab_votes}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "..", "data"))
    a = ap.parse_args()
    out = os.path.normpath(a.out); os.makedirs(out, exist_ok=True)
    summary, detail = reconcile()
    json.dump(summary, open(os.path.join(out, "RECONCILE_SUMMARY.json"), "w"), ensure_ascii=False, indent=1)
    json.dump(detail, open(os.path.join(out, "reconcile_detail.json"), "w"), ensure_ascii=False, indent=1)
    c = summary["counts"]; m = summary["metadata_agreement_on_matched"]; s = summary["segmentation_delta"]
    ab = summary["learned_ab_value_aid"]
    print(f"SigLA {c['sigla_docs']} docs / {c['sigla_signs']} signs   silver {c['silver_records']} records")
    print(f"matched {c['matched']}  only-SigLA {c['only_sigla']}  only-silver {c['only_silver']}")
    b = summary["base_level_crosswalk"]
    print(f"base-level: {b['base_matched']} shared bases; residual resolved by face/join/cruft — "
          f"silver {b['only_silver_resolved_by_base']}/{c['only_silver']}, SigLA {b['only_sigla_resolved_by_base']}/{c['only_sigla']}; "
          f"genuinely absent — silver {b['only_silver_genuinely_absent']}, SigLA {b['only_sigla_genuinely_absent']}")
    print(f"site: agree {m['site_agree']} / diff {m['site_diff']}  | period: agree {m['period_agree']} "
          f"diff {m['period_diff']} na {m['period_na']}  | support: agree {m['support_agree']} diff {m['support_diff']}")
    print(f"segmentation: equal {s['len_equal']}  SigLA-more {s['sigla_more']}  silver-more {s['silver_more']}")
    print(f"sign-class on matched: AB {summary['sign_class_on_matched']['ab_glyphs']}  "
          f"A-series {summary['sign_class_on_matched']['a_series_glyphs']}")
    print(f"learned AB#→value aid: {ab['distinct_ab']} signs from {ab['docs_used']} docs, "
          f"{ab['ge98pct_consistent']} at ≥98% consistency")
    print(f"sign-inventory crosswalk: A↔*### overlap {summary['sign_inventory_crosswalk']['A_starnum_overlap']} "
          f"of {summary['sign_inventory_crosswalk']['sigla_A_numbers']} SigLA A-signs")
    print(f"wrote {out}/RECONCILE_SUMMARY.json + reconcile_detail.json (gitignored)")


if __name__ == "__main__":
    main()
