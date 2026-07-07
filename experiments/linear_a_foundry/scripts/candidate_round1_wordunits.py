#!/usr/bin/env python3
"""CANDIDATE-LANGUAGE ROUND 1 — build GORILA WORD units (task mandate).

We DO NOT use load_a()'s 539 packed inscriptions (WP2: packing costs AUC 0.685 vs 0.760
word-segmented). Instead we read corpus/silver/inscriptions_structured.json and keep the
stream tokens with t=='word' — the GORILA word boundaries (3147 words, ~1.84 signs/word).

For a PHONETIC candidate-language test only signs with a conventional (Linear-B-derived)
transliteration value are usable, so we keep words whose every sign is an AB-value
syllabogram (the 59 non-* signs in the conservative inventory). *-series signs carry no
agreed value and logograms (GRA/VIN/OLE/…) are not phonetic; both are dropped.

The conventional transliteration (QE, RA2, KU-RO, …) is a FIXED published convention,
applied identically to real LA, shuffled LA, wrong-language LB, and random lexicons. It is
never fitted on the LA side — it is the shared common ground of every candidate-language
test. Non-circularity (LB values grade only, never model inputs) is preserved: the ONLY
thing graded is whether a candidate language's own lexicon predicts LA forms better than
the multi-family null.

Deterministic. Read-only corpus from the main worktree.
"""
from __future__ import annotations
import json, os
from collections import Counter, defaultdict

MAIN = "/home/claude-runner/gitlab/n8n/logos"
STRUCT = os.path.join(MAIN, "corpus/silver/inscriptions_structured.json")
INV = os.path.join(MAIN, "corpus/silver/inventory_syllabograms_conservative.json")
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")


def build():
    syl = set(s for s in json.load(open(INV))["inventory"] if not s.startswith("*"))
    ins = json.load(open(STRUCT))
    words = []          # list of (tuple_signs, site, inscription_id)
    for rec in ins:
        site = rec.get("site"); iid = rec.get("id")
        for st in rec.get("stream", []):
            if st.get("t") == "word":
                sg = [s for s in st.get("signs", []) if s]
                if sg and all(s in syl for s in sg):
                    words.append([sg, site, iid])
    wc = Counter(tuple(w[0]) for w in words)
    w2sites = defaultdict(set)
    for w, site, _ in words:
        w2sites[tuple(w)].add(site)
    # formula / name-like recurring forms: freq>=5 OR attested at >=2 sites
    formula = sorted((w for w in wc if wc[w] >= 5 or len(w2sites[w]) >= 2),
                     key=lambda w: -wc[w])
    multi = [w for w in words if len(w[0]) >= 2]  # discriminating set for lexical hypotheses
    out = {
        "provenance": "GORILA word units (stream t=='word') from inscriptions_structured.json; "
                      "syllabic-only (all signs in the 59 AB-value non-* syllabograms)",
        "n_word_tokens_all_syllabic": len(words),
        "n_word_types_all_syllabic": len(wc),
        "n_word_tokens_multi_sign": len(multi),
        "n_word_types_multi_sign": len(set(tuple(w[0]) for w in multi)),
        "mean_signs_per_word": round(sum(len(w[0]) for w in words) / len(words), 4),
        "syllabary_AB_values": sorted(syl),
        "words": [{"signs": w, "site": s, "id": i} for w, s, i in words],
        "formula_namelike_types": ["-".join(w) for w in formula],
        "n_formula_namelike_types": len(formula),
    }
    os.makedirs(DATA, exist_ok=True)
    p = os.path.join(DATA, "candidate_wordunits.json")
    json.dump(out, open(p, "w"), indent=1)
    print("word tokens (syllabic):", len(words), " multi-sign:", len(multi),
          " types:", len(wc), " formula types:", len(formula))
    print("WROTE", os.path.abspath(p))


if __name__ == "__main__":
    build()
