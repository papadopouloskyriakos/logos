#!/usr/bin/env python3
"""H1 — CANDIDATE ROUND 1: relative-class-constrained family models.

Five bounded models scored on held-out multi-sign LA GORILA syllabic words against the
multi-family END-TO-END null battery (S order-shuffle, W wrong-language opaque LB, R random-
prior), Holm-adjusted across families, leave-one-lexeme-out, and random-lexicon calibration.

Three SERIOUS candidates (SEM West Semitic, ANA pre-Greek Anatolian/Luwic, TYR Tyrsenian/
Etruscan-related), one UNRELATED NEGATIVE-CONTROL real language (FIN Finnish/Uralic —
chronogeographically impossible), one AGNOSTIC RANDOM control (CTRL).

Admission (relative-class-constrained): recorded per family in the prereg. The D5 anonymous
relative classes are value-blind, so every AB-based family inherits the SAME NULL K2-vs-vowel
agreement — the classes cannot discriminate families (verified here for the record). Admission
therefore rests on chronology/geography/A-prefix morphology (E1/E3)/formula grammar (E2)/anchors
(G)/CV structure, all in the prereg. No family's phonemes or correspondence ever saw Linear A.

The scoring / null machinery is REUSED, unmodified, from the audited Foundry module
`candidate_round1.py` (imported, not re-run: build_family_predictions, expand_phonemes,
word_matches, score_corpus, shuffle_within, random_lexicon, sample_lb_lengthmatched). This is a
NEW one-shot: new prereg, new families, new held-out loader. Deterministic seed 20260708.

NON-CIRCULAR: LB values expand candidate phonemes into predicted LA sign strings and appear as
the wrong-language null; they are never read off LA. D5 classes grade only. No phonetic value is
assigned to any LA sign or class by this script.
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
PREREG = os.path.join(CAMP, "preregistrations", "H_round1_prereg.json")
MAIN = "/home/claude-runner/gitlab/n8n/logos"
FOUNDRY_SCRIPTS = os.path.join(CAMP, "..", "linear_a_foundry", "scripts")

sys.path.insert(0, MAIN)
sys.path.insert(0, FOUNDRY_SCRIPTS)

from scripts.cross_script import data as X  # noqa: E402
# audited machinery (module __main__-guarded => import runs nothing)
import candidate_round1 as CR1  # noqa: E402
from candidate_round1 import (  # noqa: E402
    VOWELS,
    SERIES2VOWEL,
    build_family_predictions,
    word_matches,
    score_corpus,
    shuffle_within,
    random_lexicon,
    sample_lb_lengthmatched,
)

SEED = 20260708
N_NULL = 200
N_CAL = 300

SYLLABARY_AB = set(v for series in SERIES2VOWEL.values() for v in series.values())
# extended AB syllabogram values that occur in GORILA words but are not base-CV (kept as
# non-matching syllabic targets so the denominator is the honest full syllabic word set)
EXTRA_SYLL = {"AU", "JU", "NWA", "PA3", "PA₃", "PU2", "PU₂", "RA2", "RA₂", "TA2", "TA₂", "TWE", "PTE",
              "DWE", "DWO", "TWO", "RO2", "RO₂", "A2", "A₂", "A3", "A₃"}


def _norm(tok: str) -> str:
    """Normalize subscript digits to ASCII so RA₂ == RA2 (kept distinct from RA)."""
    return (tok.replace("₀", "0").replace("₁", "1").replace("₂", "2").replace("₃", "3")
               .replace("₄", "4").replace("₅", "5").replace("₆", "6").replace("₇", "7")
               .replace("₈", "8").replace("₉", "9"))


def load_la_heldout():
    """Held-out LA multi-sign syllabic word tokens from the GORILA word stream."""
    ins = json.load(open(os.path.join(MAIN, "corpus", "silver", "inscriptions_structured.json")))
    syll = {_norm(s) for s in (SYLLABARY_AB | EXTRA_SYLL)}
    toks, sites = [], []
    for rec in ins:
        site = rec.get("site", "?")
        for item in rec.get("stream", []):
            if item.get("t") != "word":
                continue
            signs = [_norm(s) for s in item["signs"]]
            if len(signs) < 2:
                continue
            if all(s in syll for s in signs):
                toks.append(tuple(signs))
                sites.append(site)
    return toks, sites


def relative_class_agreement(d5_path):
    """For the record: agreement of the D5 K=2 anonymous partition with the AB-value vowel/CV
    labelling that EVERY AB-based family shares (KU is /u/ for all families). adjMI + perm p.
    Confirms the relative classes are family-independent and NULL vs vowel/CV."""
    d5 = json.load(open(d5_path))
    classes = d5["reference_partition_K2"]["classes"]
    sign2class = {}
    for c in classes:
        for s in c["signs"]:
            sign2class[_norm(s)] = c["anon_class"]
    # AB-value vowel & CV for each graded sign (from SERIES2VOWEL: value -> vowel)
    val2vowel = {}
    for series, mp in SERIES2VOWEL.items():
        for v, val in mp.items():
            val2vowel[val] = v
    signs = sorted(set(sign2class) & set(val2vowel))
    part = [sign2class[s] for s in signs]
    vowel = [val2vowel[s] for s in signs]
    cv = ["V" if s in SERIES2VOWEL[""].values() else "C" for s in signs]

    def adj_mi(a, b, rng, nperm=2000):
        def mi(x, y):
            n = len(x)
            cx, cy, cxy = Counter(x), Counter(y), Counter(zip(x, y))
            import math
            m = 0.0
            for (xi, yi), nij in cxy.items():
                m += (nij / n) * math.log((nij * n) / (cx[xi] * cy[yi]))
            return m
        obs = mi(a, b)
        nulls = []
        bb = list(b)
        for _ in range(nperm):
            rng.shuffle(bb)
            nulls.append(mi(a, bb))
        nulls = np.array(nulls)
        adj = (obs - nulls.mean())
        p = (int((nulls >= obs).sum()) + 1) / (nperm + 1)
        return round(obs, 4), round(float(adj), 4), round(p, 4)
    rng = __import__("random").Random(SEED)
    mo_v, adj_v, p_v = adj_mi(part, vowel, rng)
    mo_c, adj_c, p_c = adj_mi(part, cv, rng)
    return {
        "n_graded_signs_overlap": len(signs),
        "K2_vs_vowel": {"mi_obs": mo_v, "adj_mi": adj_v, "perm_p": p_v},
        "K2_vs_CV": {"mi_obs": mo_c, "adj_mi": adj_c, "perm_p": p_c},
        "note": ("family-INDEPENDENT: every AB-based family shares this sign->vowel/CV labelling, "
                 "so the anonymous classes cannot discriminate families and are NULL vs vowel/CV."),
    }


def materialize_ctrl(fams, seed):
    """Agnostic random control lexicon: 4 word + 2 suffix; lengths drawn from the three serious
    families' entries; phonemes CV-alternating from CTRL's neutral inventory."""
    rng = np.random.default_rng(seed)
    word_lens, suf_lens = [], []
    for k in ("SEM_westSemitic", "ANA_preGreek_Anatolian", "TYR_tyrsenian"):
        for e in fams[k]["lexicon"]:
            (word_lens if e["kind"] == "word" else suf_lens).append(len(e["phonemes"].split()))
    inv = fams["CTRL_agnostic_random"]["phoneme_inventory"]
    cons = [p for p in inv if p not in VOWELS]
    vows = [p for p in inv if p in VOWELS]

    def rand_phon(length):
        toks = []
        for j in range(length):
            toks.append(vows[rng.integers(0, len(vows))] if j % 2 == 1
                        else cons[rng.integers(0, len(cons))])
        return " ".join(toks)
    lex = []
    for _ in range(4):
        lex.append({"form": "ctrl", "function": "CONTROL", "kind": "word",
                    "phonemes": rand_phon(int(rng.choice(word_lens)))})
    for _ in range(2):
        lex.append({"form": "ctrl", "function": "CONTROL", "kind": "suffix",
                    "phonemes": rand_phon(int(rng.choice(suf_lens)))})
    return lex


def _fam_offset(fname: str) -> int:
    return int(hashlib.md5(fname.encode()).hexdigest(), 16) % 50000


def run():
    os.makedirs(CAND, exist_ok=True)
    os.makedirs(MANIF, exist_ok=True)
    prereg = json.load(open(PREREG))
    fams = prereg["families"]

    la, la_sites = load_la_heldout()
    n_la = len(la)
    la_len_dist = Counter(len(w) for w in la)
    la_len_dist = {k: v / n_la for k, v in la_len_dist.items()}

    lb_seqs, _, _ = X.load_b_damos()
    lb = [tuple(s for s in w if s) for w in lb_seqs if len([s for s in w if s]) >= 2]

    # materialize CTRL
    ctrl_lex = materialize_ctrl(fams, SEED)
    fams["CTRL_agnostic_random"]["lexicon"] = ctrl_lex

    # relative-class agreement (for the record; family-independent)
    rel_agree = relative_class_agreement(os.path.join(DATA, "D_la_posterior.json"))

    # shared null banks (identical across families => comparable)
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
        real_rate, real_m = score_corpus(la, wf, sf)
        hits = sorted(set("-".join(w) for w in la if word_matches(w, wf, sf)))

        S = score_bank(S_BANK, wf, sf)
        W = score_bank(W_BANK, wf, sf)
        R = r_null_scores(lex, fam_def, seed0=SEED + 300 + _fam_offset(fname))

        def emp_p(arr):
            return (int((arr >= real_rate).sum()) + 1) / (len(arr) + 1)

        def summ(arr):
            return {"mean": round(float(arr.mean()), 5), "sd": round(float(arr.std()), 5),
                    "p95": round(float(np.percentile(arr, 95)), 5), "max": round(float(arr.max()), 5),
                    "emp_p": round(emp_p(arr), 4),
                    "z": round(float((real_rate - arr.mean()) / (arr.std() + 1e-12)), 3)}

        p_S, p_W, p_R = emp_p(S), emp_p(W), emp_p(R)
        decisive_p = max(p_W, p_R)

        # leave-one-lexeme-out
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
            "per_lexeme": per_entry,
            "real_token_match_rate": round(real_rate, 5), "real_matched_tokens": real_m,
            "n_heldout_tokens": n_la, "matched_LA_word_types": hits,
            "null_S_order_shuffle": summ(S), "null_W_wrong_language_LB": summ(W),
            "null_R_random_prior": summ(R),
            "p_S": round(p_S, 4), "p_W": round(p_W, 4), "p_R": round(p_R, 4),
            "decisive_FWER_maxWR": round(decisive_p, 4),
            "leave_one_lexeme_out": loo, "loo_worst_decisive_p": round(loo_worst, 4),
        }

    # Holm across the 5 families on the decisive FWER
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

    # random-lexicon calibration for the serious families + the negative control
    calibration = {}
    for fname in ("SEM_westSemitic", "ANA_preGreek_Anatolian", "TYR_tyrsenian", "FIN_uralic_negctrl"):
        fam_def = fams[fname]
        lex = fam_def["lexicon"]
        real_rate = results[fname]["real_token_match_rate"]
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
    verdict = "BEATS_END_TO_END_NULL" if (genuine and not ctrl_cleared_raw) else "AT_END_TO_END_NULL"

    out = {
        "experiment": "H1_candidate_round1_relative_class_constrained",
        "seed": SEED, "n_nulls_per_family": N_NULL,
        "held_out": {"unit": "GORILA multi-sign syllabic word tokens",
                     "n_tokens": n_la, "n_types": len(set(la)),
                     "n_sites": len(set(la_sites)),
                     "la_word_length_dist": {str(k): round(v, 4) for k, v in sorted(la_len_dist.items())}},
        "wrong_language_null": {"corpus": "DAMOS Linear B wordforms, multi-sign, length-matched",
                                "n_lb_multisign_words": len(lb)},
        "relative_class_D5_agreement_for_record": rel_agree,
        "families": results,
        "families_clearing_calibrated_and_serious": genuine,
        "ctrl_agnostic_cleared_raw_bar": ctrl_cleared_raw,
        "negctrl_FIN_cleared_raw_bar": negctrl_cleared_raw,
        "verdict": verdict,
    }
    os.makedirs(CAND, exist_ok=True)
    outp = os.path.join(DATA, "H1_round1.json")
    json.dump(out, open(outp, "w"), indent=1)
    json.dump(out, open(os.path.join(CAND, "H1_round1.json"), "w"), indent=1)

    # manifest
    def sha(p):
        h = hashlib.sha256()
        h.update(open(p, "rb").read())
        return h.hexdigest()
    manifest = {"prereg_sha256": sha(PREREG), "script_sha256": sha(os.path.abspath(__file__)),
                "output_sha256": sha(outp), "seed": SEED, "verdict": verdict}
    json.dump(manifest, open(os.path.join(MANIF, "H1_round1_manifest.json"), "w"), indent=1)

    print(json.dumps({"verdict": verdict, "n_la_heldout": n_la, "n_la_types": len(set(la)),
                      "genuine_serious": genuine, "ctrl_cleared_raw": ctrl_cleared_raw,
                      "negctrl_FIN_cleared_raw": negctrl_cleared_raw,
                      "rel_class_K2_vs_vowel_p": rel_agree["K2_vs_vowel"]["perm_p"],
                      **{f: {"desig": results[f]["designation"][:12],
                             "real": results[f]["real_token_match_rate"],
                             "eff_n": results[f]["effective_n_predicted_forms"],
                             "p_S": results[f]["p_S"], "p_W": results[f]["p_W"], "p_R": results[f]["p_R"],
                             "decisive": results[f]["decisive_FWER_maxWR"],
                             "holm": results[f]["holm_adjusted_decisive_p"],
                             "loo_worst": results[f]["loo_worst_decisive_p"],
                             "clears_raw": results[f]["clears_raw_bar"],
                             "clears_cal": results[f].get("clears_calibrated"),
                             "cal_pct": results[f].get("calibration", {}).get("real_percentile_p_vs_random_lexicons"),
                             "cal_falseclear": results[f].get("calibration", {}).get("raw_bar_false_clear_rate"),
                             "hits": results[f]["matched_LA_word_types"][:8]}
                         for f in results}}, indent=1))
    print("\nWROTE", outp)
    return out


if __name__ == "__main__":
    run()
