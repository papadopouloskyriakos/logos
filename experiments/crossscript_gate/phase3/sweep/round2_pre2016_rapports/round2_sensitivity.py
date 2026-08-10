#!/usr/bin/env python3
"""round2_sensitivity.py — annex-style sensitivity checks for the round-2 register
entries (corpus/divergences.json R2READ/R2DOUBT/R2SITE), mirroring the D1 discipline
(scripts/d1_sensitivity.py): NO wholesale re-runs, NO verdict may flip via annex, any
improvement is NOT a claim. Published baselines are read from runtime artifacts.

Blocks:
  (1) SITE-RELABEL — the published boundary-recovery gap (leave-one-site-out) under the
      R2SITE corrections: ARKH series -> Arkhanes, ARG Zg 1 -> Argos, LACH Za 1 ->
      Tel Lachish (13 docs; distinct sites 52 -> 55). Direction note: the published run
      MERGED Arkhanes into Arkalochori, i.e. used coarser clusters; un-merging changes
      the LOSO fold structure.
  (2) DOC-EXCLUSION — the same gap with the 14 R2READ/R2DOUBT documents excluded
      (19 word tokens = 0.60% of the corpus): bounds the exposure of the published
      segmentation positive to every reading-divergent or doubted-inclusion document
      at once.
  (3) INPUT-INTERSECTION — mechanical check that the metrology null and the KU-RO
      harness consume none of the affected documents (set intersection on their doc
      lists from runtime artifacts).

Constitution: Art. XVII (annex supplements, published figures untouched), Art. XXII
(stage R2-SENS-01; recorded in ROUND2_DELTA.md postscript), invariant 12 (all numbers
script-generated). Deterministic (seed 0).
"""
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(_HERE, *[os.pardir] * 5))
sys.path.insert(0, ROOT)

from scripts.comparison import morphology                       # noqa: E402

PUB_MORPHOLOGY = os.path.join(ROOT, "runtime", "morphology-real.json")
PUB_METROLOGY = os.path.join(ROOT, "runtime", "metrology-real.json")
OUT = os.path.join(_HERE, "round2_sensitivity.json")

SITE_FIX = {"ARKH1a": "Arkhanes", "ARKH1b": "Arkhanes", "ARKH2": "Arkhanes",
            "ARKH3a": "Arkhanes", "ARKH3b": "Arkhanes", "ARKH4a": "Arkhanes",
            "ARKH4b": "Arkhanes", "ARKH5": "Arkhanes", "ARKH6": "Arkhanes",
            "ARKHZc8": "Arkhanes", "ARKHZf9": "Arkhanes",
            "ARGZg1": "Argos", "LACHZa1": "Tel Lachish"}
AFFECTED = ["KNZb<27>", "KHWc2124", "THEZb15", "HTWc3024", "PKZb26", "SKOZc1",
            "KNZe56", "LACHZa1", "DRAZg1", "INZb1", "MIZb3", "PKZb23", "PEZb8",
            "HTZf(HM767)"]


def _br_stats(br):
    dp = br["segmenters"]["dp_unigram"]["micro_f1"]
    rnd = br["random_baseline"]["micro_f1"]
    return {"dp_unigram_micro_f1": dp, "random_micro_f1": rnd,
            "gap": round(dp - rnd, 4), "boundary_base_rate": br["boundary_base_rate"],
            "n_sites": br["n_sites"]}


def _published(reproduction):
    if os.path.exists(PUB_MORPHOLOGY):
        pub = json.load(open(PUB_MORPHOLOGY, encoding="utf-8"))["boundary_recovery"]
        dp = pub["segmenters"]["dp_unigram"]["micro_f1"]
        rnd = pub["random_baseline"]["micro_f1"]
        return ({"dp_unigram_micro_f1": dp, "random_micro_f1": rnd,
                 "gap": round(dp - rnd, 4)}, "runtime/morphology-real.json",
                reproduction["dp_unigram_micro_f1"] == dp
                and reproduction["random_micro_f1"] == rnd)
    return ({k: reproduction[k] for k in
             ("dp_unigram_micro_f1", "random_micro_f1", "gap")},
            "recomputed (runtime baseline file absent)", None)


def _leg(corpus, seed, dp_iters):
    return _br_stats(morphology.boundary_recovery(
        corpus, seed=seed, min_site_size=1, dp_iters=dp_iters, use_morfessor=False))


def build(seed=0, dp_iters=6):
    corpus = morphology.load_corpus()
    reproduction = _leg(corpus, seed, dp_iters)
    published, source, matches = _published(reproduction)

    relabeled = [morphology.Inscription(iid=i.iid,
                                        site=SITE_FIX.get(i.iid, i.site),
                                        words=i.words) for i in corpus]
    n_relabel = sum(1 for i in corpus if i.iid in SITE_FIX)
    leg1 = _leg(relabeled, seed, dp_iters)

    excluded = [i for i in corpus if i.iid not in AFFECTED]
    n_excl = len(corpus) - len(excluded)
    leg2 = _leg(excluded, seed, dp_iters)

    blocks = []
    for name, leg, extra in (
            ("site_relabel", leg1, {"n_docs_relabeled": n_relabel}),
            ("doc_exclusion", leg2, {"n_docs_excluded": n_excl}),
    ):
        delta = {k: round(leg[k] - published[k], 4)
                 for k in ("dp_unigram_micro_f1", "random_micro_f1", "gap")}
        flip = bool(leg["gap"] <= 0)
        improved = leg["gap"] > published["gap"]
        blocks.append({
            "name": name, **extra,
            "published_value": published, "published_source": source,
            "reproduction_matches_published": matches,
            "sensitivity_value": leg, "delta": delta, "verdict_flip": flip,
            "interpretation": (
                f"gap {published['gap']:+} as published -> {leg['gap']:+} "
                f"({name}); "
                + ("VERDICT FLIP SIGNAL — published verdict stands; any follow-up "
                   "is a new preregistered run" if flip else
                   "no verdict moves"
                   + ("; the larger gap is an IMPROVEMENT and is NOT a claim "
                      "(discipline rule)" if improved else ""))),
        })

    inter = {"affected_docs": AFFECTED}
    if os.path.exists(PUB_METROLOGY):
        raw = open(PUB_METROLOGY, encoding="utf-8").read()
        met = json.loads(raw[raw.index("{"):])          # artifact has a HEADLINE line

        def strings(o):
            if isinstance(o, str):
                yield o
            elif isinstance(o, dict):
                for k, v in o.items():
                    yield k
                    yield from strings(v)
            elif isinstance(o, list):
                for v in o:
                    yield from strings(v)
        aff_norm = {a.replace(" ", "") for a in AFFECTED}
        hits = sorted({s for s in strings(met) if s.replace(" ", "") in aff_norm})
        inter["metrology_n_tablets"] = met.get("corpus", {}).get("n_tablets")
        inter["metrology_intersection"] = hits
    else:
        inter["metrology_intersection"] = "runtime/metrology-real.json absent"
    result = {"stage": "R2-SENS-01", "seed": seed, "dp_iters": dp_iters,
              "blocks": blocks, "input_intersection": inter}
    json.dump(result, open(OUT, "w"), indent=2)
    return result


if __name__ == "__main__":
    r = build()
    for b in r["blocks"]:
        print(f"{b['name']}: {b['interpretation']}")
        print(f"   delta={b['delta']} flip={b['verdict_flip']} "
              f"n_sites {b['published_value'].get('n_sites', '?')}->"
              f"{b['sensitivity_value']['n_sites']}")
    print("input_intersection:", json.dumps(r["input_intersection"])[:300])
    print(f"-> {OUT}")
