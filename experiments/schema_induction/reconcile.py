#!/usr/bin/env python3
"""schema_induction/reconcile.py — EXPLORATORY / DESCRIPTIVE administrative-schema induction.

Integer-only total reconciliation on Linear A KU-RO tablets, from STRUCTURE ALONE (no phonetics),
against a permutation NULL. READ-ONLY input; writes ONLY to experiments/schema_induction/.
NOT gate-validated — consistency evidence only; a claimable result needs a pre-registered
post-correction run (and a fraction re-ingest for fraction tablets). No worker/sweep imports.

Reconciliation rule (verified from data, NOT assumed):
  - A KU-RO total sums the entry quantities in ITS SECTION (from the previous KU-RO / KI-RO
    boundary up to this KU-RO), because tablets can have multiple sections (e.g. HT88: a KI-RO
    group then a KU-RO=6 group). Whole-tablet summation over-counts.
  - The total is the num after KU-RO (optionally after one commodity sign, e.g. HT39 KU-RO *414+A
    100), on the same line. Tablets whose KU-RO has no following number (HT40) yield no target.
  - Fraction-bearing tablets are EXCLUDED from exact integer reconciliation (fractions are unparsed
    raw strings this pass).
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(ROOT, "corpus/silver/inscriptions_structured.json"), encoding="utf-8"))
ONTO = json.load(open(os.path.join(ROOT, "corpus/silver/signs_ontology.json"), encoding="utf-8"))
IDX = {dt: (cid, v.get("class")) for cid, v in ONTO.items() for dt in v.get("diplomatic_tokens", [])}
FR = re.compile(r"[¼½¾⁄₀-₉⁰-⁹]")

KURO, KIRO = ["KU", "RO"], ["KI", "RO"]


def is_logogram(signs):
    return any(IDX.get(s, (s, None))[1] == "logogram" for s in signs)


def has_fraction(rec):
    return any(t["t"] == "other" and FR.search(t.get("raw", "")) for t in rec["stream"])


def reconcile_tablet(rec):
    """Walk the stream; emit (section_sum, total) pairs for each KU-RO with a section."""
    st = rec["stream"]
    pairs, sec_sum, sec_entries, i = [], 0, 0, 0
    while i < len(st):
        tok = st[i]
        if tok["t"] == "word" and tok["signs"] == KURO:
            # total = next num, allowing one intervening commodity sign, before nl
            j, total = i + 1, None
            while j < len(st) and st[j]["t"] != "nl":
                if st[j]["t"] == "num":
                    total = st[j]["v"]
                    break
                j += 1
            if total is not None:
                pairs.append({"section_sum": sec_sum, "n_entries": sec_entries, "total": total})
            sec_sum, sec_entries, i = 0, 0, (j + 1)
            continue
        if tok["t"] == "word" and tok["signs"] == KIRO:
            # deficit boundary: start a new section (KI-RO's own number, if any, is a deficit)
            sec_sum, sec_entries = 0, 0
            i += 1
            continue
        if tok["t"] == "num":
            sec_sum += tok["v"]
            sec_entries += 1
        i += 1
    return pairs


def main():
    kuro_tabs = [r for r in D if any(t["t"] == "word" and t["signs"] == KURO for t in r["stream"])]
    intonly = [r for r in kuro_tabs if not has_fraction(r)]
    fracbear = [r for r in kuro_tabs if has_fraction(r)]

    # ---- entry (logogram/word , numeral) adjacency ----
    adj_num, adj_word_before, adj_logo_before = 0, 0, 0
    for r in D:
        st = r["stream"]
        for i, tok in enumerate(st):
            if tok["t"] != "num":
                continue
            adj_num += 1
            k = i - 1
            while k >= 0 and st[k]["t"] == "div":
                k -= 1
            if k >= 0 and st[k]["t"] == "word":
                adj_word_before += 1
                if is_logogram(st[k]["signs"]):
                    adj_logo_before += 1

    # ---- reconciliation (test) ----
    sections = []
    per_tablet = []
    for r in intonly:
        pairs = reconcile_tablet(r)
        for p in pairs:
            p2 = dict(p, id=r["id"], delta=p["section_sum"] - p["total"],
                      match=(p["section_sum"] == p["total"]))
            sections.append(p2)
            per_tablet.append(p2)
    n_sec = len(sections)
    exact = sum(1 for s in sections if s["match"])
    within1 = sum(1 for s in sections if abs(s["delta"]) <= 1)
    within2 = sum(1 for s in sections if abs(s["delta"]) <= 2)

    # ---- NULL: permute totals across sections (specificity test) ----
    # within-tablet shuffle of entry values is sum-invariant (invalid null); we instead break the
    # entries<->total pairing by permuting the totals vector against the section-sums vector.
    sums = [s["section_sum"] for s in sections]
    totals = [s["total"] for s in sections]
    N = 2000
    # deterministic permutations (no RNG import needed): rotate + index-mixing, N distinct shifts
    null_matches = []
    m = len(totals)
    if m > 1:
        for d in range(1, N + 1):
            shift = 1 + (d * 7919) % (m - 1)          # coprime-ish stride, avoids identity
            mt = sum(1 for k in range(m) if sums[k] == totals[(k + shift) % m])
            null_matches.append(mt / m)
        null_rate = sum(null_matches) / len(null_matches)
        null_max = max(null_matches)
    else:
        null_rate = null_max = None

    # ---- descriptive: commodity inventory + quantity distribution ----
    import collections
    commodity_qty = collections.defaultdict(list)
    for r in D:
        st = r["stream"]
        for i, tok in enumerate(st):
            if tok["t"] == "num":
                k = i - 1
                while k >= 0 and st[k]["t"] == "div":
                    k -= 1
                if k >= 0 and st[k]["t"] == "word" and is_logogram(st[k]["signs"]):
                    cid = IDX.get(st[k]["signs"][0], (st[k]["signs"][0], None))[0]
                    commodity_qty[cid].append(tok["v"])
    comm_summary = {c: {"n": len(v), "sum": sum(v), "max": max(v), "median": sorted(v)[len(v)//2]}
                    for c, v in sorted(commodity_qty.items(), key=lambda kv: -len(kv[1]))}

    kiro_count = sum(1 for r in D for t in r["stream"] if t["t"] == "word" and t["signs"] == KIRO)

    out = {
        "STATUS": "EXPLORATORY / DESCRIPTIVE — consistency evidence, NOT gate-validated. "
                  "A claimable result needs a pre-registered post-correction run; fraction tablets "
                  "need a fraction re-ingest.",
        "phase1": {
            "kuro_tablets": len(kuro_tabs), "integer_only": len(intonly),
            "fraction_bearing_excluded": len(fracbear),
            "fraction_bearing_ids": [r["id"] for r in fracbear],
            "lb_positive_control": "DEFERRED — DĀMOS items.jsonl exists (177 to-so/to-sa tablets) but "
                                   "in RAW-TEXT content (not tokenized like LA) and metrogram-graded "
                                   "(S/V/Z, non-integer); parsing = out-of-scope re-ingest. TEST+NULL only.",
        },
        "entry_adjacency": {
            "num_tokens": adj_num, "num_with_word_immediately_before": adj_word_before,
            "num_with_logogram_immediately_before": adj_logo_before,
            "word_before_rate": round(adj_word_before / adj_num, 3) if adj_num else None,
            "logogram_before_rate": round(adj_logo_before / adj_num, 3) if adj_num else None,
        },
        "reconciliation_TEST": {
            "n_sections": n_sec, "exact_match": exact,
            "exact_rate": round(exact / n_sec, 3) if n_sec else None,
            "within_1_rate": round(within1 / n_sec, 3) if n_sec else None,
            "within_2_rate": round(within2 / n_sec, 3) if n_sec else None,
            "delta_distribution": collections.Counter(s["delta"] for s in sections).most_common(),
            "per_section": sorted(per_tablet, key=lambda s: (not s["match"], s["id"])),
        },
        "reconciliation_NULL": {
            "method": "permute totals across sections (break entries<->total pairing), N=%d" % N,
            "mean_match_rate": round(null_rate, 4) if null_rate is not None else None,
            "max_match_rate": round(null_max, 4) if null_max is not None else None,
            "note": "within-tablet entry shuffle is sum-invariant (invalid); totals-permutation used.",
        },
        "descriptive_commodities": comm_summary,
        "kiro_deficit_count": kiro_count,
    }
    with open(os.path.join(OUT, "reconcile_results.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)

    print("STATUS:", out["STATUS"])
    print(f"\nPhase 1: KU-RO tablets={len(kuro_tabs)}  integer-only={len(intonly)}  "
          f"fraction-bearing(excluded)={len(fracbear)}")
    print("  LB positive control:", out["phase1"]["lb_positive_control"][:80], "...")
    ea = out["entry_adjacency"]
    print(f"\nEntry adjacency: {ea['word_before_rate']:.1%} of {ea['num_tokens']} numerals have a "
          f"word immediately before; {ea['logogram_before_rate']:.1%} a logogram.")
    rt = out["reconciliation_TEST"]
    print(f"\nRECONCILIATION (test): {rt['exact_match']}/{rt['n_sections']} sections exact "
          f"= {rt['exact_rate']:.1%}  (within±1 {rt['within_1_rate']:.1%}, within±2 {rt['within_2_rate']:.1%})")
    rn = out["reconciliation_NULL"]
    print(f"NULL (totals permuted): mean match {rn['mean_match_rate']:.1%}, max {rn['max_match_rate']:.1%}")
    print(f"\nThree-way: LA exact {rt['exact_rate']:.1%}  vs  NULL {rn['mean_match_rate']:.1%}  vs  LB-positive DEFERRED")
    print("\nPer-section (mismatches first):")
    for s in rt["per_section"]:
        flag = "OK " if s["match"] else "XX "
        print(f"  {flag}{s['id']:10} entries={s['n_entries']:2} sum={s['section_sum']:4} "
              f"total={s['total']:4} Δ={s['delta']:+d}")
    print("\n[written] experiments/schema_induction/reconcile_results.json")


if __name__ == "__main__":
    main()
