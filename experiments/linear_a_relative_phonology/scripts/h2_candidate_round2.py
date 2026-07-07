#!/usr/bin/env python3
"""H2 - CANDIDATE ROUND 2: ANCHOR-CONSTRAINED family/isolate models.

Same 5 models as H1 (SEM/ANA/TYR serious, FIN unrelated negative-control, CTRL agnostic random),
the SAME end-to-end null battery + Holm + leave-one-lexeme-out + random-lexicon calibration. The
NEW element is the ANCHOR CONSTRAINT built from the WP-G audited anchors.

The 6 SEED_B toponym anchors (external place-name referents, `data/anchors_v2/seeds.json`) are the
only value-bearing anchors in the whole inventory (G3: SEED_A=0; the other 97 records + 6 relative
G2 classes are SEED_X shape-homomorphy / value-inheritance / value-blind and are NOT used). Each
anchor is a fixed LA sign-string (e.g. PA-I-TO=Phaistos) pinning 17 distinct signs.

Anchor use:
  (1) AUGMENT: add the 6 anchor forms to each family's predicted-form set (anchor-augmented read).
  (2) EXCLUDE: remove anchor-source tokens (equal / prefix / suffix an anchor form) from the
      held-out target as leakage.

Art. XII grading rule: every SEED_B anchor is READ through the GORILA/LB conventional sign-values,
so its pinned value == the GORILA homomorphic value (circular_for_grading=true). The anchor-augmented
forms therefore contribute ZERO to the honest STRICT verdict score (family-lexeme forms only, on the
anchor-excluded held-out set). A PERMISSIVE score (family UNION anchor forms) is reported as a
sensitivity bound; its difference isolates any anchor reading power beyond the anchor source words
(expected 0 per SEED_A=0 / one-toponym-deep).

The scoring/null machinery is REUSED unmodified from the audited Foundry module `candidate_round1.py`
(imported, not re-run). Family definitions + CTRL materialization + held-out loader are REUSED from
the audited `h1_candidate_round1.py`. NEW: prereg, anchor layer, strict/permissive split, anchor-only
reading-power test. Deterministic seed 20260708.

NON-CIRCULAR: LB values expand candidate phonemes and are the wrong-language null; never read off LA.
Anchors are external toponym strings, marked circular_for_grading and excluded from the verdict score.
No phonetic value is assigned to any LA sign or class by this script.
"""
from __future__ import annotations
import json
import hashlib
import os
import sys
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.join(HERE, "..")
DATA = os.path.join(CAMP, "data")
CAND = os.path.join(DATA, "candidates_v2")
MANIF = os.path.join(CAMP, "manifests")
PREREG = os.path.join(CAMP, "preregistrations", "H_round2_prereg.json")
H1_PREREG = os.path.join(CAMP, "preregistrations", "H_round1_prereg.json")
SEEDS = os.path.join(DATA, "anchors_v2", "seeds.json")
MAIN = "/home/claude-runner/gitlab/n8n/logos"
FOUNDRY_SCRIPTS = os.path.join(CAMP, "..", "linear_a_foundry", "scripts")

sys.path.insert(0, MAIN)
sys.path.insert(0, FOUNDRY_SCRIPTS)
sys.path.insert(0, HERE)

from scripts.cross_script import data as X  # noqa: E402
import candidate_round1 as CR1  # noqa: E402  (audited; __main__-guarded => import runs nothing)
from candidate_round1 import (  # noqa: E402
    VOWELS,
    build_family_predictions,
    word_matches,
    score_corpus,
    shuffle_within,
    random_lexicon,
    sample_lb_lengthmatched,
)
# audited H1 module (same guard) -> reuse loaders + CTRL materialization + fam offset, byte-identical
import h1_candidate_round1 as H1  # noqa: E402
from h1_candidate_round1 import load_la_heldout, materialize_ctrl, _norm, _fam_offset  # noqa: E402

SEED = 20260708
N_NULL = 200
N_CAL = 300


def load_anchor_forms():
    """SEED_B toponym anchors as LA sign-string tuples; order taken from the record_id.
    Every SEED_B anchor is marked circular_for_grading (its pinned value == the GORILA value)."""
    s = json.load(open(SEEDS))
    anchors = []
    for r in s["record_seeds"]:
        if r["seed_class"] != "SEED_B":
            continue
        form = tuple(_norm(x) for x in r["record_id"].replace("top_", "").upper().split("_"))
        # sanity: order-preserving parse must equal the covered-sign set
        assert set(form) == set(_norm(x) for x in r["covered_signs"]), (r["record_id"], form)
        anchors.append({"record_id": r["record_id"], "form": form,
                        "covered_signs": [_norm(x) for x in r["covered_signs"]],
                        "seed_class": r["seed_class"], "circular_for_grading": True,
                        "reason": "pinned value == GORILA/LB conventional value (Art. XII); one-toponym-deep (G3)"})
    pinned = sorted({sg for a in anchors for sg in a["form"]})
    return anchors, pinned, s.get("SEED_A_count", None)


def is_anchor_source(w, anchor_forms):
    """token is anchor-source (leakage) if it EQUALS / STARTS-WITH / ENDS-WITH any anchor form."""
    for f in anchor_forms:
        if w == f:
            return True
        if len(w) > len(f) and (w[:len(f)] == f or w[-len(f):] == f):
            return True
    return False


def run():
    os.makedirs(CAND, exist_ok=True)
    os.makedirs(MANIF, exist_ok=True)
    json.load(open(PREREG))  # ensure prereg present/frozen
    fams = json.load(open(H1_PREREG))["families"]  # byte-identical model defs

    anchors, pinned_signs, seed_A_count = load_anchor_forms()
    anchor_forms = [a["form"] for a in anchors]
    anchor_forms_set = set(anchor_forms)

    # held-out LA (reuse audited H1 loader) then anchor-exclude
    la_all, sites_all = load_la_heldout()
    la, la_sites, excluded = [], [], []
    for w, st in zip(la_all, sites_all):
        if is_anchor_source(w, anchor_forms):
            excluded.append("-".join(w))
        else:
            la.append(w)
            la_sites.append(st)
    n_la = len(la)
    la_len_dist = Counter(len(w) for w in la)
    la_len_dist = {k: v / n_la for k, v in la_len_dist.items()}

    lb_seqs, _, _ = X.load_b_damos()
    lb = [tuple(s for s in w if s) for w in lb_seqs if len([s for s in w if s]) >= 2]

    fams["CTRL_agnostic_random"]["lexicon"] = materialize_ctrl(fams, SEED)

    # --- anchor-constraint family-independence check (for the record) ---------------------------
    # Every AB-based family augments with the SAME anchor forms and inherits the SAME pinned signs;
    # the constraint cannot break family symmetry. (mirrors D5/F4 relative-class value-blindness.)
    anchor_family_independent = True  # by construction; all families share the identical anchor set

    # --- anchor-only reading power (does pinning 17 signs read new held-out words?) --------------
    pinned = set(pinned_signs)
    fully_coverable = [w for w in la if all(sg in pinned for sg in w)]
    matched_by_anchor_form = [w for w in fully_coverable if w in anchor_forms_set]  # ~0 (sources excluded)
    anchor_only = {
        "n_pinned_signs": len(pinned_signs), "pinned_signs": pinned_signs,
        "n_heldout_fully_coverable_by_pinned_signs": len(fully_coverable),
        "n_heldout_matched_by_an_anchor_FORM": len(matched_by_anchor_form),
        "note": ("Pinning 17 sign-values from the toponym anchors makes %d of %d anchor-excluded held-out "
                 "words fully value-coverable, but yields ZERO new lexical READINGS: a coverable word gives a "
                 "phonetic string with no external referent. %d held-out words are matched by an actual anchor "
                 "FORM beyond the excluded sources. SEED_A=%s -> no independently secure value seed."
                 % (len(fully_coverable), n_la, len(matched_by_anchor_form), seed_A_count)),
    }

    # shared null banks (identical across families => comparable), on the ANCHOR-EXCLUDED set
    S_BANK = [shuffle_within(la, np.random.default_rng(SEED + 100 + r)) for r in range(N_NULL)]
    W_BANK = [sample_lb_lengthmatched(lb, la_len_dist, n_la, np.random.default_rng(SEED + 200 + r))
              for r in range(N_NULL)]

    def score_bank(bank, wf, sf):
        return np.array([score_corpus(c, wf, sf)[0] for c in bank])

    def r_null_scores(lex, fam_def, n=N_NULL, seed0=SEED + 300):
        out = []
        for r in range(n):
            rlex = random_lexicon(lex, fam_def, np.random.default_rng(seed0 + r))
            rwf, rsf, _ = build_family_predictions(fam_def, rlex)
            out.append(score_corpus(la, rwf, rsf)[0])
        return np.array(out)

    results = {}
    for fname, fam_def in fams.items():
        lex = fam_def["lexicon"]
        wf, sf, per_entry = build_family_predictions(fam_def, lex)
        eff_n = len(wf) + len(sf)

        # STRICT (verdict): family-lexeme forms only, anchor-excluded held-out
        strict_rate, strict_m = score_corpus(la, wf, sf)
        strict_hits = sorted(set("-".join(w) for w in la if word_matches(w, wf, sf)))

        # PERMISSIVE (sensitivity): grant the 6 anchor forms as extra word-forms
        wf_perm = set(wf) | anchor_forms_set
        perm_rate, perm_m = score_corpus(la, wf_perm, sf)
        # matches attributable to an anchor form on NON-source held-out words:
        anchor_only_matches = sorted(set(
            "-".join(w) for w in la
            if (w in anchor_forms_set) and not word_matches(w, wf, sf)))

        S = score_bank(S_BANK, wf, sf)
        W = score_bank(W_BANK, wf, sf)
        R = r_null_scores(lex, fam_def, seed0=SEED + 300 + _fam_offset(fname))

        def emp_p(arr):
            return (int((arr >= strict_rate).sum()) + 1) / (len(arr) + 1)

        def summ(arr):
            return {"mean": round(float(arr.mean()), 5), "sd": round(float(arr.std()), 5),
                    "p95": round(float(np.percentile(arr, 95)), 5), "max": round(float(arr.max()), 5),
                    "emp_p": round(emp_p(arr), 4),
                    "z": round(float((strict_rate - arr.mean()) / (arr.std() + 1e-12)), 3)}

        p_S, p_W, p_R = emp_p(S), emp_p(W), emp_p(R)
        decisive_p = max(p_W, p_R)

        # leave-one-lexeme-out (strict score)
        loo = []
        for k in range(len(lex)):
            sublex = [lex[j] for j in range(len(lex)) if j != k]
            swf, ssf, _ = build_family_predictions(fam_def, sublex)
            sub_real, _ = score_corpus(la, swf, ssf)
            wsc = score_bank(W_BANK, swf, ssf)
            rsc = r_null_scores(sublex, fam_def, seed0=SEED + 9000 + k * 211 + _fam_offset(fname))
            pw = (int((wsc >= sub_real).sum()) + 1) / (N_NULL + 1)
            pr = (int((rsc >= sub_real).sum()) + 1) / (N_NULL + 1)
            loo.append({"dropped": lex[k]["form"], "sub_real_rate": round(sub_real, 5),
                        "p_W": round(pw, 4), "p_R": round(pr, 4), "decisive_p": round(max(pw, pr), 4)})
        loo_worst = max(l["decisive_p"] for l in loo) if loo else 1.0

        results[fname] = {
            "designation": fam_def["designation"], "gloss": fam_def["gloss"],
            "admission": fam_def.get("admission"),
            "effective_n_predicted_forms": eff_n, "n_word_forms": len(wf), "n_suffix_forms": len(sf),
            "strict_real_token_match_rate": round(strict_rate, 5), "strict_real_matched_tokens": strict_m,
            "permissive_real_token_match_rate": round(perm_rate, 5), "permissive_real_matched_tokens": perm_m,
            "anchor_augmentation_delta_matches": perm_m - strict_m,
            "anchor_form_only_matched_nonsource_heldout": anchor_only_matches,
            "n_heldout_tokens_anchor_excluded": n_la, "matched_LA_word_types_strict": strict_hits,
            "null_S_order_shuffle": summ(S), "null_W_wrong_language_LB": summ(W),
            "null_R_random_prior": summ(R),
            "p_S": round(p_S, 4), "p_W": round(p_W, 4), "p_R": round(p_R, 4),
            "decisive_FWER_maxWR": round(decisive_p, 4),
            "leave_one_lexeme_out": loo, "loo_worst_decisive_p": round(loo_worst, 4),
        }

    # Holm across the 5 families on the decisive FWER (strict)
    order = sorted(results.keys(), key=lambda f: results[f]["decisive_FWER_maxWR"])
    m = len(order)
    running = 0.0
    for rank, f in enumerate(order):
        adj = min(1.0, results[f]["decisive_FWER_maxWR"] * (m - rank))
        running = max(running, adj)
        results[f]["holm_adjusted_decisive_p"] = round(running, 4)
    for f in results:
        results[f]["clears_raw_bar"] = bool(
            results[f]["holm_adjusted_decisive_p"] < 0.05 and results[f]["loo_worst_decisive_p"] < 0.05)

    # random-lexicon calibration (strict) for serious families + negative control
    calibration = {}
    for fname in ("SEM_westSemitic", "ANA_preGreek_Anatolian", "TYR_tyrsenian", "FIN_uralic_negctrl"):
        fam_def = fams[fname]
        lex = fam_def["lexicon"]
        real_rate = results[fname]["strict_real_token_match_rate"]
        cal_rates, cal_clear = [], 0
        for c in range(N_CAL):
            rlex = random_lexicon(lex, fam_def, np.random.default_rng(SEED + 700000 + c * 17 + _fam_offset(fname)))
            rwf, rsf, _ = build_family_predictions(fam_def, rlex)
            rr = score_corpus(la, rwf, rsf)[0]
            cal_rates.append(rr)
            pw = (int((score_bank(W_BANK, rwf, rsf) >= rr).sum()) + 1) / (N_NULL + 1)
            pr = (int((r_null_scores(rlex, fam_def, n=100, seed0=SEED + 800000 + c * 31) >= rr).sum()) + 1) / 101
            if max(pw, pr) < 0.05:
                cal_clear += 1
        cal_rates = np.array(cal_rates)
        pct = (int((cal_rates >= real_rate).sum()) + 1) / (N_CAL + 1)
        calibration[fname] = {
            "n_random_lexicons": N_CAL,
            "random_lexicon_match_rate_mean": round(float(cal_rates.mean()), 5),
            "random_lexicon_match_rate_p95": round(float(np.percentile(cal_rates, 95)), 5),
            "random_lexicon_match_rate_max": round(float(cal_rates.max()), 5),
            "real_percentile_p_vs_random_lexicons": round(pct, 4),
            "raw_bar_false_clear_rate": round(cal_clear / N_CAL, 4),
        }
        results[fname]["calibration"] = calibration[fname]
        results[fname]["clears_calibrated"] = bool(
            results[fname]["clears_raw_bar"] and pct < 0.05
            and calibration[fname]["raw_bar_false_clear_rate"] <= 0.10)

    results["CTRL_agnostic_random"]["clears_calibrated"] = False

    genuine = [f for f in results if results[f].get("clears_calibrated")
               and fams[f]["designation"] == "SERIOUS_CANDIDATE"]
    ctrl_cleared_raw = results["CTRL_agnostic_random"]["clears_raw_bar"]
    negctrl_cleared_raw = results["FIN_uralic_negctrl"]["clears_raw_bar"]
    anchor_adds_reading = any(results[f]["anchor_augmentation_delta_matches"] > 0 for f in results)
    verdict = ("BEATS_ANCHOR_CONSTRAINED_NULL" if (genuine and not ctrl_cleared_raw)
               else "AT_ANCHOR_CONSTRAINED_NULL")

    out = {
        "experiment": "H2_candidate_round2_anchor_constrained",
        "seed": SEED, "n_nulls_per_family": N_NULL,
        "anchor_constraint": {
            "seed_B_anchors": anchors, "n_pinned_signs": len(pinned_signs),
            "SEED_A_count_cited": seed_A_count,
            "all_anchors_circular_for_grading": True,
            "anchor_constraint_family_independent": anchor_family_independent,
            "n_heldout_tokens_excluded_as_anchor_source": len(excluded),
            "excluded_anchor_source_tokens_sample": sorted(set(excluded))[:20],
            "anchor_only_reading_power": anchor_only,
        },
        "held_out": {"unit": "GORILA multi-sign syllabic word tokens, anchor-source EXCLUDED",
                     "n_tokens_anchor_excluded": n_la, "n_types": len(set(la)),
                     "n_sites": len(set(la_sites)),
                     "la_word_length_dist": {str(k): round(v, 4) for k, v in sorted(la_len_dist.items())}},
        "wrong_language_null": {"corpus": "DAMOS Linear B wordforms, multi-sign, length-matched",
                                "n_lb_multisign_words": len(lb)},
        "families": results,
        "families_clearing_calibrated_and_serious": genuine,
        "ctrl_agnostic_cleared_raw_bar": ctrl_cleared_raw,
        "negctrl_FIN_cleared_raw_bar": negctrl_cleared_raw,
        "anchor_augmentation_adds_heldout_reading_beyond_sources": anchor_adds_reading,
        "verdict": verdict,
    }
    outp = os.path.join(DATA, "H2_round2.json")
    json.dump(out, open(outp, "w"), indent=1)
    json.dump(out, open(os.path.join(CAND, "H2_round2.json"), "w"), indent=1)

    def sha(p):
        h = hashlib.sha256(); h.update(open(p, "rb").read()); return h.hexdigest()
    manifest = {"prereg_sha256": sha(PREREG), "script_sha256": sha(os.path.abspath(__file__)),
                "h1_prereg_sha256": sha(H1_PREREG), "seeds_sha256": sha(SEEDS),
                "output_sha256": sha(outp), "seed": SEED, "verdict": verdict}
    json.dump(manifest, open(os.path.join(MANIF, "H2_round2_manifest.json"), "w"), indent=1)

    print(json.dumps({
        "verdict": verdict, "n_la_anchor_excluded": n_la, "n_excluded_anchor_source": len(excluded),
        "n_pinned_signs": len(pinned_signs), "SEED_A_count": seed_A_count,
        "anchor_adds_reading_beyond_sources": anchor_adds_reading,
        "genuine_serious": genuine, "ctrl_cleared_raw": ctrl_cleared_raw,
        "negctrl_FIN_cleared_raw": negctrl_cleared_raw,
        "anchor_only_fully_coverable": anchor_only["n_heldout_fully_coverable_by_pinned_signs"],
        **{f: {"desig": results[f]["designation"][:12],
               "strict": results[f]["strict_real_token_match_rate"],
               "perm": results[f]["permissive_real_token_match_rate"],
               "anchor_delta": results[f]["anchor_augmentation_delta_matches"],
               "eff_n": results[f]["effective_n_predicted_forms"],
               "p_W": results[f]["p_W"], "p_R": results[f]["p_R"],
               "decisive": results[f]["decisive_FWER_maxWR"],
               "holm": results[f]["holm_adjusted_decisive_p"],
               "loo_worst": results[f]["loo_worst_decisive_p"],
               "clears_raw": results[f]["clears_raw_bar"],
               "clears_cal": results[f].get("clears_calibrated"),
               "cal_pct": results[f].get("calibration", {}).get("real_percentile_p_vs_random_lexicons"),
               "hits": results[f]["matched_LA_word_types_strict"][:8]}
           for f in results}}, indent=1))
    print("\nWROTE", outp)
    return out


if __name__ == "__main__":
    run()
