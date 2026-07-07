#!/usr/bin/env python3
"""B5 -- LINEAR A SEGMENTATION ENSEMBLE (Constitution v2.2 Art. III/VII/VIII/XII).

Apply ONLY the B3-validated unsupervised segmentation families to Linear A and produce a
PROBABILISTIC boundary set (never a single deterministic ground-truth segmentation -- B4 proved
any LA segmentation is an OVER-CUT SUPERSET with ~0 skill over cut-everywhere at LA's hapax
regime). For every inter-sign gap we report six attributes:

  1. boundary probability     -- ensemble vote fraction across the 5 base validated models
  2. cross-model agreement     -- which/how many models fire (+ the B3 MULTISCALE >=2/4 decision)
  3. source representation      -- independent structural marks at that gap (row-break / numeral
                                   closure / divider) reconstructed from the raw stream
  4. site stability             -- fraction of the base vote preserved under leave-one-SITE-out retrain
  5. encoding sensitivity       -- fraction preserved under subscript-variant folding (re-encode+retrain)
  6. damage sensitivity         -- fraction preserved under random sign-deletion (full-pipeline retrain)

NON-CIRCULAR (Art. XII): GORILA word dividers and any phonetic value are used ONLY to GRADE the
ensemble (P/R/F1, over-cut ratio). They are NEVER an input to any model. All six families are the
frozen B3 implementations (imported), which are unsupervised (EM / cue rules on sign streams).
"""
from __future__ import annotations
import json, os, re, sys, random
from collections import Counter

ROOT = "/home/claude-runner/gitlab/n8n/logos-linear-a-relative-phonology-seals"
sys.path.insert(0, ROOT)
HERE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.dirname(HERE)
DATA = os.path.join(CAMP, "data")
SEGDIR = os.path.join(DATA, "segmentations")
REPORTS = os.path.join(CAMP, "reports")
SEED = 20260708

# frozen B3 validated primitives (unsupervised). b3 lives in the campaign scripts dir and
# itself imports `scripts.cross_script` from ROOT, so both paths must be on sys.path.
sys.path.insert(0, HERE)
from b3_known_script_segmentation import (  # noqa: E402
    build_stats, build_be_trie, seg_tp, seg_be, run_bayes, run_mdl, run_fst,
    score_boundaries,
)

BASE_MODELS = ["CUE_TP_min", "CUE_BranchEntropy", "BAYESIAN_unigram", "MDL", "FINITE_STATE_bigram"]
SUBSCRIPT = re.compile(r"[₀-₉]")   # unicode subscript digits
K_DAMAGE = 15
DAMAGE_P = 0.15
rng = random.Random(SEED)


# --------------------------------------------------------------------------- LA data
def load_la():
    """Return list of inscription records with sign stream, gold word-boundary gaps, and
    per-gap structural marks (num/nl/div between the two flanking words)."""
    recs = json.load(open(os.path.join(ROOT, "corpus/silver/inscriptions_structured.json"),
                          encoding="utf-8"))
    out = []
    for r in recs:
        signs = list(r["signs"])
        # gold word-boundary gaps (grading only): gap index = left sign index
        gold = set()
        c = 0
        for w in r["words"][:-1]:
            c += len(w)
            gold.add(c - 1)
        # structural marks: walk raw stream, map to word-word gaps
        st = r["stream"]
        wpos = [i for i, t in enumerate(st) if t["t"] == "word"]
        marks = {}   # left-sign-index of gap -> set of {NUM,NL,DIV}
        # cumulative sign count at end of each word:
        cum = []
        cc = 0
        for i in wpos:
            cc += len(st[i]["signs"])
            cum.append(cc)
        for k in range(len(wpos) - 1):
            gidx = cum[k] - 1               # gap after last sign of word k
            between = {st[j]["t"] for j in range(wpos[k] + 1, wpos[k + 1])}
            m = set()
            if "num" in between:
                m.add("NUM")
            if "nl" in between:
                m.add("NL")
            if "div" in between:
                m.add("DIV")
            marks[gidx] = m
        out.append({"id": r["id"], "site": r["site"], "support": r.get("support"),
                    "period": r.get("context"), "signs": signs, "gold": gold, "marks": marks})
    return out


def reencode(signs):
    return [SUBSCRIPT.sub("", s) for s in signs]


# --------------------------------------------------------------------------- ensemble
def ensemble_predict(train_streams, predict_streams):
    """Train the 5 base validated families (unsupervised) on train_streams, predict boundary
    gap-sets on predict_streams. Returns {model_name: [set_of_gaps per predict stream]} plus the
    B3 MULTISCALE (>=2 of 4) decision."""
    uni, fwd, bwd = build_stats(train_streams)
    succ, pred = build_be_trie(train_streams)
    tp = [seg_tp(s, fwd, uni) for s in predict_streams]
    be = [seg_be(s, succ, pred) for s in predict_streams]
    bp, _ = run_bayes(train_streams, predict_streams)
    mp, _ = run_mdl(train_streams, predict_streams)
    fp_, _ = run_fst(train_streams, predict_streams)
    multi = []
    for i in range(len(predict_streams)):
        votes = Counter()
        for src in (be[i], bp[i], mp[i], fp_[i]):
            for g in src:
                votes[g] += 1
        multi.append({g for g, v in votes.items() if v >= 2})
    return {"CUE_TP_min": tp, "CUE_BranchEntropy": be, "BAYESIAN_unigram": bp,
            "MDL": mp, "FINITE_STATE_bigram": fp_, "MULTISCALE_ENSEMBLE": multi}


def votes_per_gap(preds, n):
    """preds: {model: [gapset,...]} -> per stream, dict gap-> set(models that cut)."""
    out = []
    for i in range(n):
        d = {}
        for m in BASE_MODELS:
            for g in preds[m][i]:
                d.setdefault(g, set()).add(m)
        out.append(d)
    return out


# --------------------------------------------------------------------------- grading (GORILA, grading only)
def grade(pred_sets, golds, streams):
    """ensemble grading at vote thresholds 1..5 and MULTISCALE, incl. margin over all-cut."""
    def allcut_f1(golds, streams):
        tp = fp = fn = 0
        for g, s in zip(golds, streams):
            allg = set(range(len(s) - 1))
            tp += len(allg & g)
            fp += len(allg - g)
            fn += len(g - allg)
        P = tp / (tp + fp) if tp + fp else 0
        R = tp / (tp + fn) if tp + fn else 0
        return 2 * P * R / (P + R) if P + R else 0.0
    f1_all = allcut_f1(golds, streams)
    return f1_all


# --------------------------------------------------------------------------- main
def main():
    la = load_la()
    all_streams = [r["signs"] for r in la]                       # train co-occurrence on everything
    pred_idx = [i for i, r in enumerate(la) if len(r["signs"]) >= 2]
    pred_streams = [la[i]["signs"] for i in pred_idx]
    golds = [la[i]["gold"] for i in pred_idx]
    sites = [la[i]["site"] for i in pred_idx]
    print(f"LA: {len(la)} inscriptions, {len(pred_idx)} with >=2 signs, "
          f"{sum(len(s)-1 for s in pred_streams)} gaps, "
          f"{len(set(s for r in la for s in r['signs']))} distinct signs, {len(set(sites))} sites")

    # ------- BASE ensemble (train on full corpus, predict >=2-sign inscriptions)
    base = ensemble_predict(all_streams, pred_streams)
    base_votes = votes_per_gap(base, len(pred_streams))

    # ------- ENCODING: subscript-variant folding, retrain + repredict (indices aligned 1:1)
    enc_all = [reencode(s) for s in all_streams]
    enc_pred = [reencode(s) for s in pred_streams]
    enc = ensemble_predict(enc_all, enc_pred)
    enc_votes = votes_per_gap(enc, len(pred_streams))

    # ------- LOSO: for each site, retrain excluding that site, predict that site's streams
    site_of_idx = {i: la[i]["site"] for i in pred_idx}
    all_sites = sorted(set(la[i]["site"] for i in range(len(la))))
    loso_votes = [None] * len(pred_streams)   # aligned to pred_streams positions
    pos_of_predidx = {gi: p for p, gi in enumerate(pred_idx)}
    for site in all_sites:
        train_s = [r["signs"] for r in la if r["site"] != site]
        heldp = [p for p in range(len(pred_streams)) if sites[p] == site]
        if not heldp:
            continue
        held_streams = [pred_streams[p] for p in heldp]
        lp = ensemble_predict(train_s, held_streams)
        lv = votes_per_gap(lp, len(held_streams))
        for k, p in enumerate(heldp):
            loso_votes[p] = lv[k]
    print("LOSO done")

    # ------- DAMAGE: K replicates of random sign deletion, full retrain, map cuts back
    #  damage_hit[p][g] = [n_replicates gap testable, n where base-cutting models still cut sum-frac]
    dmg_testable = [Counter() for _ in pred_streams]   # p -> {g: count testable}
    dmg_preserved = [Counter() for _ in pred_streams]  # p -> {g: sum(frac base-models preserved)}
    for rep in range(K_DAMAGE):
        rr = random.Random(SEED + 100 + rep)
        # damage each inscription ONCE (train corpus = all inscriptions; pred = the >=2-sign subset)
        dmg_all, keep_all = [], []
        for s in all_streams:
            mask = [rr.random() >= DAMAGE_P for _ in s]
            dmg_all.append([x for x, k in zip(s, mask) if k])
            keep_all.append(mask)
        dmg_pred = [dmg_all[i] for i in pred_idx]
        keepmaps = [keep_all[i] for i in pred_idx]
        dp = ensemble_predict(dmg_all, dmg_pred)
        dv = votes_per_gap(dp, len(dmg_pred))
        for p in range(len(pred_streams)):
            mask = keepmaps[p]
            # map original gap g (left sign index) -> damaged gap position, if g and g+1 both survive
            # damaged position of original sign i = number of survivors before i
            rank = []
            c = 0
            for k in mask:
                rank.append(c)
                if k:
                    c += 1
            for g, models in base_votes[p].items():
                if not models:
                    continue
                if g + 1 < len(mask) and mask[g] and mask[g + 1]:
                    dg = rank[g]                 # damaged gap left-index
                    dmg_testable[p][g] += 1
                    cut_models = dv[p].get(dg, set())
                    dmg_preserved[p][g] += len(cut_models & models) / len(models)
    print("DAMAGE done")

    # ------- assemble per-gap records
    inscr_out = []
    agg = {"n_gaps": 0, "n_cut_ge1": 0, "prob_hist": Counter(),
           "site_stab_sum": 0.0, "enc_stab_sum": 0.0, "dmg_stab_sum": 0.0, "stab_n": 0,
           "gold_prob_sum": 0.0, "nongold_prob_sum": 0.0, "n_gold": 0, "n_nongold": 0}
    for p, gi in enumerate(pred_idx):
        r = la[gi]
        s = r["signs"]
        gaps_rec = []
        for g in range(len(s) - 1):
            models = base_votes[p].get(g, set())
            prob = len(models) / len(BASE_MODELS)
            is_gold = g in r["gold"]
            marks = sorted(r["marks"].get(g, set()))
            rec = {"g": g, "L": s[g], "R": s[g + 1],
                   "prob": round(prob, 3),
                   "models": sorted(models),
                   "multiscale": bool(g in base["MULTISCALE_ENSEMBLE"][p]),
                   "is_gold": bool(is_gold),
                   "struct": marks}
            # stabilities only defined where base fired
            if models:
                lv = loso_votes[p] or {}
                site_stab = len((lv.get(g, set())) & models) / len(models)
                enc_stab = len((enc_votes[p].get(g, set())) & models) / len(models)
                nt = dmg_testable[p].get(g, 0)
                dmg_stab = (dmg_preserved[p].get(g, 0) / nt) if nt else None
                rec["site_stab"] = round(site_stab, 3)
                rec["enc_stab"] = round(enc_stab, 3)
                rec["dmg_stab"] = round(dmg_stab, 3) if dmg_stab is not None else None
                rec["dmg_testable_frac"] = round(nt / K_DAMAGE, 3)
                agg["site_stab_sum"] += site_stab
                agg["enc_stab_sum"] += enc_stab
                if dmg_stab is not None:
                    agg["dmg_stab_sum"] += dmg_stab
                agg["stab_n"] += 1
            gaps_rec.append(rec)
            agg["n_gaps"] += 1
            if models:
                agg["n_cut_ge1"] += 1
            agg["prob_hist"][len(models)] += 1
            if is_gold:
                agg["gold_prob_sum"] += prob
                agg["n_gold"] += 1
            else:
                agg["nongold_prob_sum"] += prob
                agg["n_nongold"] += 1
        inscr_out.append({"id": r["id"], "site": r["site"], "support": r["support"],
                          "period": r["period"], "signs": s, "gaps": gaps_rec})

    # ------- grading vs GORILA (grading only): threshold sweep + margin over all-cut
    f1_all = grade(None, golds, pred_streams)
    grading = {"note": "GORILA word dividers used ONLY to grade; never a model input.",
               "all_cut_baseline_f1": round(f1_all, 4), "thresholds": {}}
    for thr in range(1, 6):
        preds = []
        for p in range(len(pred_streams)):
            preds.append({g for g, ms in base_votes[p].items() if len(ms) >= thr})
        sc = score_boundaries(preds, golds)
        npred = sum(len(x) for x in preds)
        ngold = sum(len(g) for g in golds)
        grading["thresholds"][f">={thr}/5"] = {
            **sc, "n_pred": npred, "over_cut_ratio": round(npred / ngold, 3) if ngold else None,
            "margin_over_all_cut": round(sc["f1"] - f1_all, 4)}
    # multiscale grading
    ms_preds = [base["MULTISCALE_ENSEMBLE"][p] for p in range(len(pred_streams))]
    sc = score_boundaries(ms_preds, golds)
    npred = sum(len(x) for x in ms_preds)
    ngold = sum(len(g) for g in golds)
    grading["MULTISCALE_ge2of4"] = {**sc, "n_pred": npred,
                                    "over_cut_ratio": round(npred / ngold, 3),
                                    "margin_over_all_cut": round(sc["f1"] - f1_all, 4)}

    # ------- per-model over-cut ratios (grading)
    per_model = {}
    for m in BASE_MODELS + ["MULTISCALE_ENSEMBLE"]:
        preds = base[m]
        sc = score_boundaries(preds, golds)
        npred = sum(len(x) for x in preds)
        per_model[m] = {**sc, "n_pred": npred, "over_cut_ratio": round(npred / ngold, 3)}

    stabn = max(1, agg["stab_n"])
    summary = {
        "n_inscriptions_predicted": len(pred_idx),
        "n_gaps": agg["n_gaps"],
        "n_gaps_cut_by_ge1_model": agg["n_cut_ge1"],
        "frac_gaps_cut_ge1": round(agg["n_cut_ge1"] / agg["n_gaps"], 4),
        "gaps_by_n_models_agree": {str(k): agg["prob_hist"][k] for k in range(0, 6)},
        "mean_boundary_prob_all_gaps": round(
            sum(k * agg["prob_hist"][k] for k in range(6)) / agg["n_gaps"] / 5, 4),
        "mean_prob_at_gold_gaps": round(agg["gold_prob_sum"] / max(1, agg["n_gold"]), 4),
        "mean_prob_at_nongold_gaps": round(agg["nongold_prob_sum"] / max(1, agg["n_nongold"]), 4),
        "mean_site_stability_cutgaps": round(agg["site_stab_sum"] / stabn, 4),
        "mean_encoding_stability_cutgaps": round(agg["enc_stab_sum"] / stabn, 4),
        "mean_damage_stability_cutgaps": round(agg["dmg_stab_sum"] / stabn, 4),
    }

    out = {"task": "B5_la_segmentation_ensemble", "seed": SEED, "constitution": "v2.2",
           "base_models": BASE_MODELS, "damage": {"k": K_DAMAGE, "p": DAMAGE_P},
           "encoding_perturbation": "unicode-subscript folding (RA2->RA etc.)",
           "grading": grading, "per_model_vs_gorila": per_model, "summary": summary,
           "over_segmentation_caveat": (
               "B4 established any LA segmentation is an OVER-CUT SUPERSET with ~0 skill over "
               "cut-everywhere at LA's hapax regime; this ensemble is a PROBABILISTIC boundary "
               "set, NOT a deterministic ground-truth segmentation. Read prob as vote-share, not "
               "P(true boundary)."),
           "non_circularity": ("GORILA dividers + phonetic values used ONLY to grade; the 5 "
                               "families are frozen unsupervised B3 implementations."),
           "inscriptions": inscr_out}
    os.makedirs(SEGDIR, exist_ok=True)
    json.dump(out, open(os.path.join(SEGDIR, "la_ensemble.json"), "w"), indent=1, default=str)
    print(json.dumps({"grading": grading, "per_model": per_model, "summary": summary}, indent=1))
    return out


if __name__ == "__main__":
    main()
