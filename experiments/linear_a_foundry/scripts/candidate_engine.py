#!/usr/bin/env python3
"""Shared engine for CANDIDATE-LANGUAGE ROUNDS 2 & 3 (bounded, honest, multi-family null).

This is the SAME rigorous protocol as candidate_round1.py, refactored into a reusable
`run_round(prereg, out, manifest)` so rounds 2 and 3 inherit the identical machinery byte-for-
byte. The only intentional change from round 1 is DETERMINISM: round 1 seeded the random-prior
null with Python's salted ``hash(fname)`` (non-reproducible across processes); here per-family
offsets come from a stable md5 so the whole pipeline is reproducible under seed 20260708 as the
task mandates.

Protocol (identical to round 1):
  - Each family = a BOUNDED preregistered correspondence (phoneme inventory + allowed changes
    into the LA syllabary) + a SMALL cited lexicon of candidate-language WORDS.
  - Every lexeme is EXPANDED to its predicted LA syllabogram-value string(s) via the FIXED
    correspondence (derived from the candidate language, never read off LA).
  - A held-out LA multi-sign GORILA word (t=='word' units, syllabic-only, >=2 signs) MATCHES a
    family iff its value-string is a predicted whole-word form, or (affix entries) it ends with a
    predicted affix string.
  - Primary statistic = token-weighted match rate on the held-out multi-sign word set.
  - Scored vs the WP6 multi-family END-TO-END null:
      (S) order-shuffle LA within word           -> kills form structure (non-decisive)
      (W) wrong-language opaque LB, length-matched -> the WP6 trap (real other language, same matcher)
      (R) random-prior: lexicon permuted, search size preserved -> kills lexicon informativeness
    Decisive nulls for a LANGUAGE claim = W and R. FWER_family = fraction of decisive null
    realizations with match >= real (per-null empirical p, take the max over W and R).
  - Search-adjusted across the families in the round by Holm.
  - Leave-one-lexeme-out reported (Egyptian-channel discipline: is the signal one lexeme?).
  - 300-draw random-lexicon false-clear calibration: how often a same-structure random lexicon
    clears the SAME decisive bar, and where the real family sits in the random-lexicon band.

A family COUNTS as a genuine signal only if it (1) clears Holm-adjusted decisive FWER<0.05,
(2) survives leave-one-lexeme-out (<0.05), (3) beats the random-lexicon calibration (real rate
above the band at p<0.05 with controlled false-clear rate), AND the agnostic random CONTROL of
the same round does NOT clear the raw bar. Non-circular: LB values appear ONLY as the wrong-
language null; predicted forms come from candidate-language dictionaries, never fitted to LA.
"""
from __future__ import annotations
import hashlib
import json
import os
from collections import Counter

import numpy as np

# Reuse the round-1 primitives verbatim (pure, __main__-guarded so importing runs nothing).
import candidate_round1 as R1
from candidate_round1 import (
    VOWELS,
    build_family_predictions,
    load_la_multisign,
    load_lb_multisign,
    random_lexicon,
    sample_lb_lengthmatched,
    score_corpus,
    shuffle_within,
    word_matches,
)

SEED = 20260708
N_NULL = 200
N_CAL = 300

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
MANIFESTS = os.path.join(HERE, "..", "manifests")

MAIN = "/home/claude-runner/gitlab/n8n/logos"
CORPUS_INPUTS = [
    os.path.join(MAIN, "corpus", "silver", "inscriptions_structured.json"),
    os.path.join(MAIN, "corpus", "silver", "inventory_syllabograms_conservative.json"),
]


def _fam_offset(fname: str) -> int:
    """Deterministic per-family seed offset (replaces round-1's salted hash())."""
    return int(hashlib.md5(fname.encode()).hexdigest(), 16) % 50000


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _materialize_ctrl(fams, ctrl_key, real_keys, seed):
    """Build the agnostic random control lexicon: 4 word + 2 suffix, lengths drawn from the
    real families' entries, phonemes drawn C/V-alternating from the control inventory. Same
    construction as round 1, generalized over whichever real families the round declares."""
    rng = np.random.default_rng(seed)
    word_lens, suf_lens = [], []
    for k in real_keys:
        for e in fams[k]["lexicon"]:
            (word_lens if e["kind"] == "word" else suf_lens).append(len(e["phonemes"].split()))
    if not suf_lens:
        suf_lens = [max(1, min(word_lens))]
    inv = fams[ctrl_key]["phoneme_inventory"]
    cons = [p for p in inv if p not in VOWELS]
    vows = [p for p in inv if p in VOWELS]

    def rand_phon(length):
        toks = []
        for j in range(length):
            if j % 2 == 1:
                toks.append(vows[rng.integers(0, len(vows))])
            else:
                toks.append(cons[rng.integers(0, len(cons))])
        return " ".join(toks)

    lex = []
    for _ in range(4):
        lex.append({"form": "ctrl", "function": "CONTROL", "kind": "word",
                    "phonemes": rand_phon(int(rng.choice(word_lens)))})
    for _ in range(2):
        lex.append({"form": "ctrl", "function": "CONTROL", "kind": "suffix",
                    "phonemes": rand_phon(int(rng.choice(suf_lens)))})
    return lex


def run_round(prereg_path, out_path, manifest_path, experiment_name):
    prereg = json.load(open(prereg_path))
    fams = prereg["families"]
    ctrl_key = next(k for k in fams if k.startswith("CTRL"))
    real_keys = [k for k in fams if k != ctrl_key]

    la = load_la_multisign()
    n_la = len(la)
    la_len_dist = Counter(len(w) for w in la)
    la_len_dist = {k: v / n_la for k, v in la_len_dist.items()}
    lb = load_lb_multisign(set())

    ctrl_lex = _materialize_ctrl(fams, ctrl_key, real_keys, SEED)
    fams[ctrl_key]["_materialized_lexicon"] = ctrl_lex
    lexicons = {k: fams[k]["lexicon"] for k in real_keys}
    lexicons[ctrl_key] = ctrl_lex

    # shared null banks (identical across families => comparable)
    S_BANK, W_BANK = [], []
    for r in range(N_NULL):
        S_BANK.append(shuffle_within(la, np.random.default_rng(SEED + 100 + r)))
        W_BANK.append(sample_lb_lengthmatched(lb, la_len_dist, n_la,
                                              np.random.default_rng(SEED + 200 + r)))

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
        lex = lexicons[fname]
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
                    "p95": round(float(np.percentile(arr, 95)), 5),
                    "max": round(float(arr.max()), 5),
                    "emp_p": round(emp_p(arr), 4),
                    "z": round(float((real_rate - arr.mean()) / (arr.std() + 1e-12)), 3)}

        p_S, p_W, p_R = emp_p(S), emp_p(W), emp_p(R)
        decisive_p = max(p_W, p_R)

        # leave-one-lexeme-out worst-case decisive FWER
        loo = []
        for k in range(len(lex)):
            sublex = [lex[j] for j in range(len(lex)) if j != k]
            swf, ssf, _ = build_family_predictions(fam_def, sublex)
            sub_real, _ = score_corpus(la, swf, ssf)
            wsc = score_bank(W_BANK, swf, ssf)
            rsc = r_null_scores(sublex, fam_def,
                                seed0=SEED + 9000 + k * 211 + _fam_offset(fname))
            pw = (int((wsc >= sub_real).sum()) + 1) / (N_NULL + 1)
            pr = (int((rsc >= sub_real).sum()) + 1) / (N_NULL + 1)
            loo.append({"dropped": lex[k]["form"], "sub_real_rate": round(sub_real, 5),
                        "p_W": round(pw, 4), "p_R": round(pr, 4),
                        "decisive_p": round(max(pw, pr), 4)})
        loo_worst = max(l["decisive_p"] for l in loo) if loo else 1.0

        results[fname] = {
            "gloss": fam_def["gloss"],
            "effective_n_predicted_forms": eff_n,
            "n_word_forms": len(wf), "n_suffix_forms": len(sf),
            "per_lexeme": per_entry,
            "real_token_match_rate": round(real_rate, 5),
            "real_matched_tokens": real_m, "n_heldout_tokens": n_la,
            "matched_LA_word_types": hits,
            "null_S_order_shuffle": summ(S),
            "null_W_wrong_language_LB": summ(W),
            "null_R_random_prior": summ(R),
            "p_S": round(p_S, 4), "p_W": round(p_W, 4), "p_R": round(p_R, 4),
            "decisive_FWER_maxWR": round(decisive_p, 4),
            "leave_one_lexeme_out": loo,
            "loo_worst_decisive_p": round(loo_worst, 4),
            "materialized_lexicon": [e["phonemes"] for e in lex] if fname == ctrl_key else None,
        }

    # Holm across the families in this round on the decisive FWER
    order = sorted(results.keys(), key=lambda f: results[f]["decisive_FWER_maxWR"])
    m = len(order)
    running = 0.0
    holm = {}
    for rank, f in enumerate(order):
        adj = min(1.0, results[f]["decisive_FWER_maxWR"] * (m - rank))
        running = max(running, adj)
        holm[f] = round(running, 4)
    for f in results:
        results[f]["holm_adjusted_decisive_p"] = holm[f]
        results[f]["clears_raw_bar"] = bool(
            holm[f] < 0.05 and results[f]["loo_worst_decisive_p"] < 0.05)

    # random-lexicon false-clear calibration (real families only)
    calibration = {}
    for fname in real_keys:
        fam_def = fams[fname]
        lex = lexicons[fname]
        real_rate = results[fname]["real_token_match_rate"]
        cal_rates, cal_clear = [], 0
        for c in range(N_CAL):
            rlex = random_lexicon(lex, fam_def, np.random.default_rng(SEED + 700000 + c * 17))
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
            results[fname]["clears_raw_bar"]
            and pct < 0.05
            and calibration[fname]["raw_bar_false_clear_rate"] <= 0.10)

    results[ctrl_key]["clears_calibrated"] = False

    genuine = [f for f in real_keys if results[f].get("clears_calibrated")]
    ctrl_cleared_raw = results[ctrl_key]["clears_raw_bar"]
    # A family only COUNTS if it clears AND the agnostic control does NOT (task rule).
    counts = [f for f in genuine if not ctrl_cleared_raw]
    verdict = "BEATS_END_TO_END_NULL" if counts else "AT_END_TO_END_NULL"

    out = {
        "experiment": experiment_name,
        "seed": SEED, "n_nulls_per_family": N_NULL, "n_calibration_lexicons": N_CAL,
        "deterministic_note": "per-family random-prior offsets from md5(family) (not salted hash); "
                              "fully reproducible under seed 20260708",
        "held_out": {"unit": "GORILA multi-sign syllabic word tokens", "n_tokens": n_la,
                     "n_types": len(set(la)),
                     "la_word_length_dist": {str(k): round(v, 4) for k, v in sorted(la_len_dist.items())}},
        "wrong_language_null": {"corpus": "DAMOS Linear B wordforms (load_b_damos), multi-sign, "
                                          "length-matched to LA", "n_lb_multisign_words": len(lb)},
        "families": results,
        "families_clearing_calibrated": genuine,
        "families_that_count": counts,
        "ctrl_cleared_raw_bar": ctrl_cleared_raw,
        "per_family_FWER": {f: {"decisive_FWER_maxWR": results[f]["decisive_FWER_maxWR"],
                                "holm_adjusted": results[f]["holm_adjusted_decisive_p"],
                                "loo_worst": results[f]["loo_worst_decisive_p"]}
                            for f in results},
        "verdict": verdict,
    }
    out["interpretation"] = (
        "%s: real families %s tested as held-out hypotheses vs the WP6 multi-family end-to-end null "
        "(S order-shuffle; W wrong-language opaque LB; R random-prior). A family COUNTS only if it "
        "(1) clears the decisive bar max(p_W,p_R) Holm-adjusted<0.05, (2) survives leave-one-lexeme-out, "
        "(3) beats the 300-draw random-lexicon calibration, AND the agnostic control does NOT clear the "
        "raw bar. Result: %s. %sAgnostic control cleared raw bar: %s. Per-family Holm-adjusted decisive "
        "FWER: %s. As pre-registered, the honest expectation was AT_END_TO_END_NULL; each family's "
        "raw-bar false-clear rate under same-structure random lexicons is reported so a bare match rate "
        "is never read as language-specific fit."
        % (experiment_name, ", ".join(real_keys), verdict,
           ("COUNTING families: " + ", ".join(counts) + ". " if counts
            else "No family counts as a genuine signal. "),
           ctrl_cleared_raw,
           {f: results[f]["holm_adjusted_decisive_p"] for f in real_keys}))

    os.makedirs(DATA, exist_ok=True)
    json.dump(out, open(out_path, "w"), indent=1)

    # manifest: inputs + hashes + outputs (counts generated, not hand-written)
    os.makedirs(MANIFESTS, exist_ok=True)
    manifest = {
        "experiment": experiment_name,
        "generated_by": os.path.basename(__file__) + " via run_round",
        "seed": SEED,
        "prereg": {"path": os.path.abspath(prereg_path), "sha256": _sha256(prereg_path)},
        "corpus_inputs_readonly": [{"path": p, "sha256": _sha256(p)} for p in CORPUS_INPUTS],
        "derived_inputs": [{"path": os.path.abspath(os.path.join(DATA, "candidate_wordunits.json")),
                            "sha256": _sha256(os.path.join(DATA, "candidate_wordunits.json"))}],
        "wrong_language_null_corpus": "scripts.cross_script.data.load_b_damos (DAMOS Linear B)",
        "output": {"path": os.path.abspath(out_path), "sha256": _sha256(out_path)},
        "counts": {"n_heldout_LA_multisign_tokens": n_la,
                   "n_heldout_LA_multisign_types": len(set(la)),
                   "n_LB_multisign_null_words": len(lb),
                   "families": list(fams.keys())},
        "verdict": verdict,
    }
    json.dump(manifest, open(manifest_path, "w"), indent=1)

    print(json.dumps({"experiment": experiment_name, "verdict": verdict,
                      "genuine": genuine, "counts": counts,
                      "ctrl_cleared_raw": ctrl_cleared_raw,
                      "per_family": {f: {"real": results[f]["real_token_match_rate"],
                                         "eff_n": results[f]["effective_n_predicted_forms"],
                                         "p_S": results[f]["p_S"], "p_W": results[f]["p_W"],
                                         "p_R": results[f]["p_R"],
                                         "decisive_FWER": results[f]["decisive_FWER_maxWR"],
                                         "holm": results[f]["holm_adjusted_decisive_p"],
                                         "loo_worst": results[f]["loo_worst_decisive_p"],
                                         "clears_raw": results[f]["clears_raw_bar"],
                                         "clears_cal": results[f].get("clears_calibrated"),
                                         "cal_pct": results[f].get("calibration", {}).get("real_percentile_p_vs_random_lexicons"),
                                         "cal_false_clear": results[f].get("calibration", {}).get("raw_bar_false_clear_rate"),
                                         "hits": results[f]["matched_LA_word_types"][:8]}
                                     for f in results}}, indent=1))
    print("WROTE", os.path.abspath(out_path))
    print("WROTE", os.path.abspath(manifest_path))
    return out
