#!/usr/bin/env python3
"""representation_audit/sensitivity.py — READ-ONLY transcription-treatment sensitivity.

Recomputes EXISTING descriptive statistics (defined in learning_curves.LINEAR_A /
benchmark_stats) under alternative, DOCUMENTED transcription treatments, to see whether
they move materially. Reads the corpus + ontology READ-ONLY; writes ONLY into this dir.
Does NOT import worker/sweep modules and does NOT touch paper/, prereg, or the sweep.

Treatments (each a REAL, documented variant from Phase-1 recon — not arbitrary):
  raw          : diplomatic token as-is (inventory_syllabograms_raw; V=131)
  conservative : ontology canonical_sign_id, allographs kept DISTINCT  <-- the PAPER PRIMARY
                 (inventory_syllabograms_conservative; V=92; LINEAR_A.V_syllabic)
  exploratory  : ontology allograph_family, subscripted allographs MERGED
                 (inventory_syllabograms_exploratory; V=88)
  excl_unident : conservative MINUS class 'syllabogram-Aonly' (the undeciphered *NNN signs
                 treated as unreadable / dropped — a real transcriber choice)

Statistics (all pre-existing, reused definitions):
  N_sign_tokens        LINEAR_A.n_sign_tokens (=5792 all-class)  -> here per syllabogram stream
  V                    LINEAR_A.V_syllabic (=92)                 -> distinct sign types
  num_word_tokens      benchmark_stats word count
  distinct_word_forms  LINEAR_A.distinct_words (=650, the sufficiency locator anchor)
  mean_signs_per_word  LINEAR_A.mean_signs_per_word (=2.3); benchmark_stats np.mean(word_lengths)
"""
import json
import os
import statistics

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.dirname(os.path.abspath(__file__))
ONTO = json.load(open(os.path.join(ROOT, "corpus/silver/signs_ontology.json"), encoding="utf-8"))
STRUCT = json.load(open(os.path.join(ROOT, "corpus/silver/inscriptions_structured.json"), encoding="utf-8"))

# diplomatic token -> (canonical_sign_id, allograph_family, class)
IDX = {}
for cid, v in ONTO.items():
    for dt in v.get("diplomatic_tokens", []):
        IDX[dt] = (cid, v.get("allograph_family"), v.get("class"))

SYLL = {"syllabogram-AB", "syllabogram-Aonly"}


def map_sign(sign, treatment):
    """Return the mapped sign under a treatment, or None to DROP the position."""
    cid, fam, cls = IDX.get(sign, (sign, sign, None))
    if treatment == "raw":
        return sign
    if treatment == "conservative":
        return cid
    if treatment == "exploratory":
        return fam if fam not in (None, "__DATA_ERROR__") else cid
    if treatment == "excl_unident":
        return None if cls == "syllabogram-Aonly" else cid
    raise ValueError(treatment)


def syllabogram_only(sign):
    _, _, cls = IDX.get(sign, (sign, sign, None))
    return cls in SYLL


def compute(treatment, syll_filter=True):
    words = []          # list of mapped word tuples (non-empty)
    sign_tokens = []
    for rec in STRUCT:
        for w in rec.get("words", []):
            mw = []
            for s in w:
                if syll_filter and not syllabogram_only(s):
                    continue
                m = map_sign(s, treatment)
                if m is None:
                    continue
                mw.append(m)
            if mw:
                words.append(tuple(mw))
                sign_tokens.extend(mw)
    lens = [len(w) for w in words]
    return {
        "treatment": treatment,
        "syllabogram_filter": syll_filter,
        "N_sign_tokens": len(sign_tokens),
        "V_distinct_signs": len(set(sign_tokens)),
        "num_word_tokens": len(words),
        "distinct_word_forms": len(set(words)),
        "mean_signs_per_word": round(statistics.mean(lens), 4) if lens else 0.0,
    }


def main():
    treatments = ["raw", "conservative", "exploratory", "excl_unident"]
    results = {t: compute(t, syll_filter=True) for t in treatments}
    # also an all-class (unfiltered) view for context
    results_allclass = {t: compute(t, syll_filter=False) for t in ("conservative", "exploratory")}

    base = results["conservative"]
    metrics = ["N_sign_tokens", "V_distinct_signs", "num_word_tokens",
               "distinct_word_forms", "mean_signs_per_word"]
    diff = {}
    for t in treatments:
        diff[t] = {}
        for m in metrics:
            b, x = base[m], results[t][m]
            pct = (100.0 * (x - b) / b) if b else 0.0
            diff[t][m] = {"value": x, "delta_vs_conservative": round(x - b, 4), "pct": round(pct, 2)}

    paper_anchors = {"n_sign_tokens": 5792, "V_syllabic": 92, "distinct_words": 650,
                     "distinct_words_lo": 600, "distinct_words_hi": 700, "mean_signs_per_word": 2.3}

    out = {
        "note": "READ-ONLY transcription-treatment sensitivity of EXISTING LINEAR_A statistics.",
        "input_manifest": {
            "ontology": "corpus/silver/signs_ontology.json (166 canonical ids, 259 diplomatic tokens)",
            "corpus": "corpus/silver/inscriptions_structured.json (1341 inscriptions, scribe word divisions)",
            "treatments": {
                "raw": "diplomatic token as-is",
                "conservative": "ontology canonical_sign_id (PAPER PRIMARY; allographs distinct)",
                "exploratory": "ontology allograph_family (allographs merged)",
                "excl_unident": "conservative minus class syllabogram-Aonly (*NNN dropped)"},
        },
        "paper_anchors_LINEAR_A": paper_anchors,
        "results_syllabogram_stream": results,
        "results_allclass_context": results_allclass,
        "diff_vs_conservative_baseline": diff,
    }
    with open(os.path.join(OUT, "sensitivity_results.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)

    # human table
    print("PAPER anchors (LINEAR_A):", paper_anchors)
    print("\nSYLLABOGRAM STREAM — statistic under each treatment (baseline = conservative = paper):")
    hdr = ["metric"] + treatments
    print("  " + "  ".join(f"{h:>18}" for h in hdr))
    for m in metrics:
        row = [m] + [f"{results[t][m]}" for t in treatments]
        print("  " + "  ".join(f"{c:>18}" for c in row))
    print("\nDELTA vs conservative (paper primary):")
    for m in metrics:
        cells = []
        for t in treatments:
            d = diff[t][m]
            cells.append(f"{d['pct']:+.1f}%" if t != "conservative" else "baseline")
        print("  %-22s %s" % (m, "  ".join(f"{c:>12}" for c in cells)))
    print("\n[written] experiments/representation_audit/sensitivity_results.json")


if __name__ == "__main__":
    main()
