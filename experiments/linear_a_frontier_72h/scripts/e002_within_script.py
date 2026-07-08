#!/usr/bin/env python3
"""EPOCH-002 leg 1 — WITHIN-SCRIPT (opaque LB): do higher-order substitution motifs beat the
flat cofill-Jaccard baseline at recovering same-consonant / same-vowel classes under
frequency-disjoint + formula-disjoint holdouts?

Preregistered: epochs/EPOCH-002/prereg.md (plan_hash 09c55c9e...). Seed 20260708.
Positive control FIRST (flat same-C AUC in [0.68, 0.72] else DETECTOR_BROKEN).
"""
from __future__ import annotations
import os, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e002_motif_common as M
C = M.C

SEED = M.SEED
N_PERM_LABEL = 1000
N_PERM_DEGREE = 200
N_BOOT = 1000


def build_family_lookups(seqs, doc_words, doc_meta):
    """Return {family: (lookup, meta)} for flat + MF_A/B/C on a given (sub)corpus."""
    out = {}
    f_flat = M.inc_flat(seqs)
    out["FLAT"] = (M.jaccard_lookup(f_flat), {"fset": f_flat, "coverage": len(f_flat)})
    f_a = M.inc_trigram(seqs)
    out["MF_A_trigram"] = (M.jaccard_lookup(f_a), {"fset": f_a, "coverage": len(f_a)})
    f_b = M.inc_formula(seqs, doc_words, doc_meta)
    out["MF_B_formula"] = (M.jaccard_lookup(f_b), {"fset": f_b, "coverage": len(f_b)})
    per_site = M.site_slotmaps(doc_words, doc_meta)
    out["MF_C_site"] = (M.site_mean_lookup(per_site),
                        {"per_site": per_site,
                         "coverage": len(set().union(*[set(f) for f in per_site.values()]))})
    return out


def degree_null_site(per_site, signs, rel, restrict, n=N_PERM_DEGREE, seed=SEED):
    """MF_C degree-preserving null: permute incidence sign labels WITHIN each site."""
    import random
    rng = random.Random(seed)
    look = M.site_mean_lookup(per_site)
    rows = M.pair_table(look, signs, rel)
    obs, _, _ = M.auc_from_rows(rows, "same_consonant", restrict)
    null = []
    for _ in range(n):
        shuf = {}
        for site, fset in per_site.items():
            incid = [(s, f) for s, fs in fset.items() for f in fs]
            scol = [s for s, _ in incid]
            rng.shuffle(scol)
            f2 = defaultdict(set)
            for s, (_, f) in zip(scol, incid):
                f2[s].add(f)
            shuf[site] = dict(f2)
        rows2 = M.pair_table(M.site_mean_lookup(shuf), signs, rel)
        a_, _, _ = M.auc_from_rows(rows2, "same_consonant", restrict)
        if a_ is not None:
            null.append(a_)
    null.sort()
    ge = sum(1 for x in null if x >= obs)
    return {"obs": obs, "n_null": len(null), "null_mean": float(np.mean(null)),
            "null_p95": float(np.quantile(null, 0.95)),
            "p_one_sided": (ge + 1) / (len(null) + 1)}


def run():
    seqs, doc_words, doc_meta = C.load_lb_damos()
    signs = M.scorable_signs(seqs)
    rel = M.pair_relations(signs)
    band = M.freq_bands(seqs, signs, nb=4)
    wb = M.within_band_pairs(rel, band)
    from collections import Counter
    out = {"experiment": "EPOCH-002_within_script_motifs", "seed": SEED,
           "plan_hash": M.PLAN_HASH,
           "corpus": {"lb_word_tokens": len(seqs), "docs": len(doc_words),
                      "scorable_signs": len(signs),
                      "relation_counts": dict(Counter(rel.values())),
                      "n_within_band_pairs": len(wb)}}
    print("signs", len(signs), "pairs", len(rel), "within-band", len(wb))

    fams = build_family_lookups(seqs, doc_words, doc_meta)

    # ---------- POSITIVE CONTROL FIRST ----------
    flat_rows = M.pair_table(fams["FLAT"][0], signs, rel)
    flat_full_C, _, _ = M.auc_from_rows(flat_rows, "same_consonant")
    out["positive_control"] = {"flat_full_same_C_auc": flat_full_C,
                               "window": [0.68, 0.72],
                               "pass": 0.68 <= flat_full_C <= 0.72}
    print(f"POSITIVE CONTROL flat same-C AUC = {flat_full_C:.4f} pass={out['positive_control']['pass']}")
    if not out["positive_control"]["pass"]:
        out["verdict"] = "DETECTOR_BROKEN"
        M.dump("E002_within_script.json", out)
        return out

    # ---------- observed AUCs, all families, full + freq-disjoint ----------
    obs = {}
    rows_by_fam = {}
    for fam, (look, meta) in fams.items():
        rows = M.pair_table(look, signs, rel)
        rows_by_fam[fam] = rows
        rec = {"coverage_signs": meta["coverage"]}
        for cls, tag in (("same_consonant", "same_C"), ("same_vowel", "same_V")):
            a_full, npos, nneg = M.auc_from_rows(rows, cls)
            a_fd, npos_fd, nneg_fd = M.auc_from_rows(rows, cls, wb)
            rec[f"{tag}_full"] = a_full
            rec[f"{tag}_freq_disjoint"] = a_fd
            rec[f"{tag}_n_pos_fd"] = npos_fd
        rec["n_neg_fd"] = nneg_fd
        obs[fam] = rec
        print(f"{fam:14s} sameC full={rec['same_C_full']:.3f} fd={rec['same_C_freq_disjoint']:.3f} "
              f"sameV full={rec['same_V_full']:.3f} fd={rec['same_V_freq_disjoint']:.3f} cov={rec['coverage_signs']}")
    out["observed"] = obs

    # ---------- frequency-matched label nulls (primary significance) + Holm 3x2 ----------
    label_nulls, holm_input = {}, []
    for fam in ("MF_A_trigram", "MF_B_formula", "MF_C_site"):
        sim_by_pair = {frozenset((a, b)): s for a, b, _, s in rows_by_fam[fam]}
        label_nulls[fam] = {}
        for cls, tag in (("same_consonant", "same_C"), ("same_vowel", "same_V")):
            o = obs[fam][f"{tag}_freq_disjoint"]
            r = M.label_null_freq_matched(sim_by_pair, signs, band, None, cls, o,
                                          restrict=wb, n=N_PERM_LABEL)
            label_nulls[fam][tag] = r
            holm_input.append((f"{fam}:{tag}", r["p_one_sided"]))
            print(f"label-null {fam} {tag}: obs={o:.3f} null_mean={r['null_mean']:.3f} p={r['p_one_sided']:.4f}")
    adj = M.holm(holm_input)
    out["label_nulls_freq_matched"] = label_nulls
    out["holm_families_x_axes"] = adj

    # flat's own label-null p on the primary endpoint (context, outside the Holm family)
    sim_flat = {frozenset((a, b)): s for a, b, _, s in flat_rows}
    out["flat_label_null_same_C_fd"] = M.label_null_freq_matched(
        sim_flat, signs, band, None, "same_consonant",
        obs["FLAT"]["same_C_freq_disjoint"], restrict=wb, n=N_PERM_LABEL)

    # ---------- degree-preserving nulls ----------
    deg = {}
    for fam in ("FLAT", "MF_A_trigram", "MF_B_formula"):
        deg[fam] = M.degree_preserving_null(fams[fam][1]["fset"], signs, rel,
                                            "same_consonant", restrict=wb, n=N_PERM_DEGREE)
        print(f"degree-null {fam}: obs={deg[fam]['obs']:.3f} p95={deg[fam]['null_p95']:.3f} p={deg[fam]['p_one_sided']:.4f}")
    deg["MF_C_site"] = degree_null_site(fams["MF_C_site"][1]["per_site"], signs, rel, wb)
    print(f"degree-null MF_C_site: obs={deg['MF_C_site']['obs']:.3f} p95={deg['MF_C_site']['null_p95']:.3f} p={deg['MF_C_site']['p_one_sided']:.4f}")
    out["degree_preserving_nulls"] = deg

    # ---------- wrong-language (within-word shuffled) corpus ----------
    sh_seqs = M.shuffle_within_words(seqs)
    sh_docw = M.shuffle_doc_words(doc_words)
    sh_fams = build_family_lookups(sh_seqs, sh_docw, doc_meta)
    wrong = {}
    for fam, (look, meta) in sh_fams.items():
        rows = M.pair_table(look, signs, rel)
        a_full, _, _ = M.auc_from_rows(rows, "same_consonant")
        a_fd, _, _ = M.auc_from_rows(rows, "same_consonant", wb)
        wrong[fam] = {"same_C_full": a_full, "same_C_freq_disjoint": a_fd,
                      "pass_lt_055": (a_full or 0) < 0.55}
        print(f"wrong-lang {fam}: sameC full={a_full:.3f} fd={a_fd:.3f} pass={wrong[fam]['pass_lt_055']}")
    out["wrong_language_shuffled"] = wrong

    # ---------- paired sign bootstrap vs flat ----------
    boots = {}
    for fam in ("MF_A_trigram", "MF_B_formula", "MF_C_site"):
        boots[fam] = {
            "full": M.sign_bootstrap_delta(fams[fam][0], fams["FLAT"][0], signs, n=N_BOOT),
            "freq_disjoint": M.sign_bootstrap_delta(fams[fam][0], fams["FLAT"][0], signs,
                                                    n=N_BOOT, restrict_band=band)}
        b = boots[fam]["freq_disjoint"]
        print(f"bootstrap {fam} fd: dmean={b['delta_mean']:.4f} ci95={b['ci95']}")
    out["sign_bootstrap_delta_vs_flat"] = boots

    # ---------- LOSO (formula-disjoint) 6 largest series ----------
    series_docs = defaultdict(list)
    for did, m_ in doc_meta.items():
        if did in doc_words:
            series_docs[m_.get("series") or "NA"].append(did)
    big = sorted(series_docs, key=lambda s: -sum(len(doc_words[d]) for d in series_docs[s]))[:6]
    loso = {"held_series": big, "folds": []}
    for held in big:
        sub_docw = {d: ws for d, ws in doc_words.items()
                    if (doc_meta.get(d) or {}).get("series") != held}
        sub_seqs = [w for ws in sub_docw.values() for w in ws]
        sub_fams = build_family_lookups(sub_seqs, sub_docw, doc_meta)
        fold = {"held": held, "n_train_words": len(sub_seqs)}
        for fam, (look, meta) in sub_fams.items():
            rows = M.pair_table(look, signs, rel)
            a_, _, _ = M.auc_from_rows(rows, "same_consonant")
            fold[fam] = a_
        loso["folds"].append(fold)
        print(f"LOSO held={held}: " + " ".join(f"{f}={fold[f]:.3f}" for f in sub_fams))
    for fam in ("MF_A_trigram", "MF_B_formula", "MF_C_site"):
        loso[f"{fam}_wins_vs_flat"] = sum(1 for f in loso["folds"] if (f[fam] or 0) > (f["FLAT"] or 0))
    out["loso"] = loso

    # ---------- mechanical per-family verdicts (prereg order) ----------
    verdicts = {}
    for fam in ("MF_A_trigram", "MF_B_formula", "MF_C_site"):
        p_holm = adj[f"{fam}:same_C"]
        ci = boots[fam]["freq_disjoint"]["ci95"]
        wins = loso[f"{fam}_wins_vs_flat"]
        if p_holm >= 0.05:
            v = "NO_POWER"
        elif ci[0] > 0 and wins >= 5:
            v = "SUPERIOR"
        elif ci[1] < 0:
            v = "INFERIOR"
        else:
            v = "EQUIVALENT"
        verdicts[fam] = {"holm_p_same_C_fd": p_holm, "boot_ci95_fd": ci,
                         "loso_wins": wins, "verdict": v}
    fam_v = [verdicts[f]["verdict"] for f in verdicts]
    if "SUPERIOR" in fam_v:
        leg = "SUPERIOR"
    elif all(v == "NO_POWER" for v in fam_v):
        leg = "NO_POWER"
    elif "EQUIVALENT" in fam_v:
        leg = "EQUIVALENT"
    else:
        leg = "INFERIOR"
    out["family_verdicts"] = verdicts
    out["leg_verdict"] = f"MOTIF_WITHIN_{leg}"
    p = M.dump("E002_within_script.json", out)
    print("\nWITHIN LEG VERDICT:", out["leg_verdict"], "| wrote", p)
    for f, v in verdicts.items():
        print(" ", f, v["verdict"], "holm_p", round(v["holm_p_same_C_fd"], 4),
              "ci", [round(x, 4) for x in v["boot_ci95_fd"]], "loso_wins", v["loso_wins"])
    return out


if __name__ == "__main__":
    run()
