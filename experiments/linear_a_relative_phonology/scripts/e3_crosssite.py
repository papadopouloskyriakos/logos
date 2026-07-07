#!/usr/bin/env python3
"""E3 — CROSS-SITE / CROSS-GENRE GENERALIZATION of the E1 affixation paradigm.

Question (from C5's severe Haghia-Triada dependency flag): is the wave-2 headline
paradigm — productive word-INITIAL A-/I- prefixation + word-final -JA suffixation,
characterized by recurrent-stem productivity (E1 `paradigm_induction`) — a property of
the Linear A administrative language, or is it Haghia-Triada-bound (60% of the corpus)?

Design (all held-out; NON-CIRCULAR Art. XII — the only thing transferred across a split is
the ANONYMOUS affix IDENTITY {A-, I-, -JA}; the productivity + frequency-matched null are
recomputed entirely on the held-out partition, on its OWN unigram + length distribution):

  T1  per-site power + descriptive productivity table.
  T2  train Haghia Triada -> test pooled non-HT  (inventory overlap + held-out affix null).
  T3  train pooled non-HT -> test Haghia Triada  (reverse).
  T4  leave-one-SITE-out over sites with enough support; held-out affix null per site.
  T5  leave-one-FORMULA-FAMILY-out, families = document genre (SUPPORT: Tablet / Nodule /
      Stone vessel = libation / Roundel / Clay vessel). Tests whether A-/I-/-JA is admin-
      general or a libation-formula (stone-vessel) artefact.

Known values (pure vowels A,I; -JA) are used to NAME the transferred affixes and to GRADE
recovery afterward — never a model input, never a gate. Highest claim layer L2/L3; no licence.
Deterministic seed 20260708; pure stdlib. Reuses audited E1 primitives.
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e1_morphology_models as e1  # noqa: E402  (audited primitives)

CAMP = os.path.dirname(HERE)
SEGDIR = os.path.join(CAMP, "data", "segmentations")
DATA = os.path.join(CAMP, "data")
REPORTS = os.path.join(CAMP, "reports")
SEED = 20260708
N_NULL = 300

HEADLINE_PRE = ["A", "I"]          # word-initial prefixes (pure-vowel; graded afterward)
HEADLINE_SUF = ["JA"]              # word-final suffix
CONTEXT_PRE = ["A", "I", "U", "E", "O"]
CONTEXT_SUF = ["JA", "RE", "NE", "TU", "SI"]


# --------------------------------------------------------------------------- data
def load_units():
    d = json.load(open(os.path.join(SEGDIR, "SEG_GORILA_WORD.json")))
    out = []
    for u in d["units"]:
        out.append({
            "signs": tuple(u["signs"]),
            "site": u["site"] or "(unknown)",
            "support": u["support"] or "(unknown)",
        })
    return out


def words_of(units):
    return [u["signs"] for u in units]


# --------------------------------------------------------------------------- primitives
def productivities(words):
    """Recurrent-stem productivity for the headline+context affixes on one word set."""
    wset = set(words)
    rc = e1._residual_index(wset)
    pre = {s: e1.productivity_prefix(words, s, wset, rc) for s in CONTEXT_PRE}
    suf = {s: e1.productivity_suffix(words, s, wset, rc) for s in CONTEXT_SUF}
    n_recur_stems = sum(1 for t, c in rc.items() if c >= 2 or t in wset)
    return pre, suf, n_recur_stems


def descriptive(words):
    n = len(words)
    if n == 0:
        return {"n_words": 0}
    init = Counter(w[0] for w in words if len(w) >= 1)
    fin = Counter(w[-1] for w in words if len(w) >= 1)
    return {
        "frac_init_A": round(init.get("A", 0) / n, 4),
        "frac_init_I": round(init.get("I", 0) / n, 4),
        "frac_fin_JA": round(fin.get("JA", 0) / n, 4),
    }


def held_out_null(words, pre_targets, suf_targets):
    """E1 frequency-matched i.i.d. null recomputed on THIS partition only. Holm across all tests."""
    return e1.freq_matched_null(words, pre_targets, suf_targets, n_null=N_NULL, seed=SEED)


def learn_inventory(words, k=15):
    """Independently induce the top-k prefix/suffix inventory (paradigm criterion) on a word set."""
    para = e1.paradigm_induction(words)
    pre = list(para["prefixes"].items())[:k]
    suf = list(para["suffixes"].items())[:k]
    return {p: c for p, c in pre}, {s: c for s, c in suf}


def spearman(shared, a, b):
    """Spearman rho over the productivity of a shared affix set between two inventories."""
    if len(shared) < 3:
        return None
    xs = sorted(shared, key=lambda s: a[s])
    ys = sorted(shared, key=lambda s: b[s])
    rx = {s: i for i, s in enumerate(xs)}
    ry = {s: i for i, s in enumerate(ys)}
    n = len(shared)
    d2 = sum((rx[s] - ry[s]) ** 2 for s in shared)
    return round(1 - 6 * d2 / (n * (n * n - 1)), 3)


def inventory_overlap(inv_a, inv_b, k=15):
    """Jaccard + Spearman between two independently-induced affix inventories."""
    out = {}
    for slot, (a, b) in [("prefixes", (inv_a[0], inv_b[0])), ("suffixes", (inv_a[1], inv_b[1]))]:
        A, B = set(a), set(b)
        shared = A & B
        out[slot] = {
            "train_top": sorted(A),
            "test_top": sorted(B),
            "shared": sorted(shared),
            "jaccard": round(len(shared) / len(A | B), 3) if (A | B) else 0.0,
            "spearman_on_shared": spearman(shared, a, b),
        }
    return out


def verdict_from_null(null, pre_targets, suf_targets):
    """Which headline affixes clear Holm p<0.05 on this partition + power summary."""
    rows = {}
    for s in pre_targets:
        d = null["prefix"][s]
        rows["pre_" + s] = {"obs": d["observed"], "null_mean": d["null_mean"],
                            "p_ge": d["p_ge"], "p_holm": d["p_holm"],
                            "sig": d["p_holm"] < 0.05}
    for s in suf_targets:
        d = null["suffix"][s]
        rows["suf_" + s] = {"obs": d["observed"], "null_mean": d["null_mean"],
                            "p_ge": d["p_ge"], "p_holm": d["p_holm"],
                            "sig": d["p_holm"] < 0.05}
    return rows


# --------------------------------------------------------------------------- tests
def t1_per_site(units):
    by = defaultdict(list)
    for u in units:
        by[u["site"]].append(u["signs"])
    rows = {}
    for site, words in sorted(by.items(), key=lambda kv: -len(kv[1])):
        pre, suf, nrs = productivities(words)
        rows[site] = {
            "n_words": len(words), "n_types": len(set(words)),
            "n_recurrent_stems": nrs,
            "prod_A_pre": pre["A"], "prod_I_pre": pre["I"], "prod_JA_suf": suf["JA"],
            **descriptive(words),
        }
    return rows


def split_eval(train_words, test_words, name):
    inv_tr = learn_inventory(train_words)
    inv_te = learn_inventory(test_words)
    ov = inventory_overlap(inv_tr, inv_te)
    null = held_out_null(test_words, HEADLINE_PRE, HEADLINE_SUF)
    verd = verdict_from_null(null, HEADLINE_PRE, HEADLINE_SUF)
    _, _, nrs = productivities(test_words)
    return {
        "name": name,
        "n_train_words": len(train_words), "n_test_words": len(test_words),
        "n_test_types": len(set(test_words)), "n_test_recurrent_stems": nrs,
        "inventory_overlap": ov,
        "held_out_headline_null": verd,
        "n_headline_significant": sum(1 for r in verd.values() if r["sig"]),
    }


def t4_loso(units, min_words=40):
    by = defaultdict(list)
    for u in units:
        by[u["site"]].append(u["signs"])
    big = [s for s, w in by.items() if len(w) >= min_words]
    rows = {}
    for site in sorted(big, key=lambda s: -len(by[s])):
        test = by[site]
        train = [w for s in by for w in by[s] if s != site]
        null = held_out_null(test, HEADLINE_PRE, HEADLINE_SUF)
        verd = verdict_from_null(null, HEADLINE_PRE, HEADLINE_SUF)
        _, _, nrs = productivities(test)
        rows[site] = {
            "n_test_words": len(test), "n_test_types": len(set(test)),
            "n_test_recurrent_stems": nrs,
            "n_train_words": len(train),
            "held_out_headline_null": verd,
            "n_headline_significant": sum(1 for r in verd.values() if r["sig"]),
        }
    return rows, big


def t5_lofo(units, min_words=60):
    """Leave-one-formula-family-out; family = document genre (support type)."""
    by = defaultdict(list)
    for u in units:
        by[u["support"]].append(u["signs"])
    big = [s for s, w in by.items() if len(w) >= min_words]
    rows = {}
    for supp in sorted(big, key=lambda s: -len(by[s])):
        test = by[supp]
        train = [w for s in by for w in by[s] if s != supp]
        null = held_out_null(test, HEADLINE_PRE, HEADLINE_SUF)
        verd = verdict_from_null(null, HEADLINE_PRE, HEADLINE_SUF)
        _, _, nrs = productivities(test)
        rows[supp] = {
            "n_test_words": len(test), "n_test_types": len(set(test)),
            "n_test_recurrent_stems": nrs, "n_train_words": len(train),
            "held_out_headline_null": verd,
            "n_headline_significant": sum(1 for r in verd.values() if r["sig"]),
            **descriptive(test),
        }
    return rows, big


# --------------------------------------------------------------------------- main
def main():
    units = load_units()
    words_all = words_of(units)
    ht = [u["signs"] for u in units if u["site"] == "Haghia Triada"]
    non_ht = [u["signs"] for u in units if u["site"] != "Haghia Triada"]

    results = {"seed": SEED, "n_null": N_NULL,
               "headline_prefixes": HEADLINE_PRE, "headline_suffixes": HEADLINE_SUF,
               "n_words_total": len(words_all), "n_ht": len(ht), "n_non_ht": len(non_ht)}

    # full-corpus baseline (well-powered reference)
    null_full = held_out_null(words_all, HEADLINE_PRE, HEADLINE_SUF)
    results["full_corpus_headline_null"] = verdict_from_null(null_full, HEADLINE_PRE, HEADLINE_SUF)

    results["T1_per_site"] = t1_per_site(units)
    results["T2_train_HT_test_nonHT"] = split_eval(ht, non_ht, "train_HT->test_nonHT")
    results["T3_train_nonHT_test_HT"] = split_eval(non_ht, ht, "train_nonHT->test_HT")
    loso, loso_sites = t4_loso(units)
    results["T4_leave_one_site_out"] = {"min_words": 40, "sites": loso_sites, "rows": loso}
    lofo, lofo_supp = t5_lofo(units)
    results["T5_leave_one_formula_family_out"] = {
        "family_axis": "document_genre_support", "min_words": 60,
        "families": lofo_supp, "rows": lofo}

    # ---- generalization verdict (mechanical) ----
    # Does the paradigm survive OFF Haghia Triada? The disjoint-from-HT partitions are:
    #   T2 non-HT pool, and T5 Stone-vessel (libation) vs Tablet/Nodule (admin).
    non_ht_sig = results["T2_train_HT_test_nonHT"]["n_headline_significant"]
    lofo_sig = {k: v["n_headline_significant"] for k, v in lofo.items()}
    loso_any = {k: v["n_headline_significant"] for k, v in loso.items()}
    results["generalization_verdict"] = {
        "full_corpus_n_sig": sum(1 for r in results["full_corpus_headline_null"].values() if r["sig"]),
        "non_HT_pool_n_sig": non_ht_sig,
        "per_genre_n_sig": lofo_sig,
        "per_heldout_site_n_sig": loso_any,
        "note": "sig = Holm p<0.05 vs frequency-matched i.i.d. null on the held-out partition's "
                "OWN unigram+length dist; 3 headline affixes tested {A-,I-,-JA}. Underpowered "
                "partitions (low n_test_recurrent_stems) cannot reject even a real effect.",
    }

    os.makedirs(DATA, exist_ok=True)
    outp = os.path.join(DATA, "E3_crosssite.json")
    with open(outp, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("WROTE", outp)

    # console summary
    print("\nFULL corpus headline:", {k: (v["obs"], v["p_holm"], v["sig"])
                                      for k, v in results["full_corpus_headline_null"].items()})
    print("\nT2 train HT -> test nonHT")
    t2 = results["T2_train_HT_test_nonHT"]
    print("  n_test_words", t2["n_test_words"], "recur_stems", t2["n_test_recurrent_stems"])
    print("  inv jaccard pre/suf:", t2["inventory_overlap"]["prefixes"]["jaccard"],
          t2["inventory_overlap"]["suffixes"]["jaccard"],
          "spearman pre/suf:", t2["inventory_overlap"]["prefixes"]["spearman_on_shared"],
          t2["inventory_overlap"]["suffixes"]["spearman_on_shared"])
    print("  headline null:", {k: (v["obs"], v["null_mean"], v["p_holm"], v["sig"])
                               for k, v in t2["held_out_headline_null"].items()})
    print("\nT3 train nonHT -> test HT")
    t3 = results["T3_train_nonHT_test_HT"]
    print("  headline null:", {k: (v["obs"], v["null_mean"], v["p_holm"], v["sig"])
                               for k, v in t3["held_out_headline_null"].items()})
    print("\nT5 leave-one-genre-out")
    for supp, r in lofo.items():
        print(f"  {supp:16s} nW={r['n_test_words']:4d} recur={r['n_test_recurrent_stems']:4d} "
              f"sig={r['n_headline_significant']} "
              f"{ {k:(v['obs'],v['p_holm'],v['sig']) for k,v in r['held_out_headline_null'].items()} }")
    print("\nT4 leave-one-site-out")
    for site, r in loso.items():
        print(f"  {site:16s} nW={r['n_test_words']:4d} recur={r['n_test_recurrent_stems']:4d} "
              f"sig={r['n_headline_significant']}")
    return results


if __name__ == "__main__":
    main()
