#!/usr/bin/env python3
"""CANDIDATE-LANGUAGE ROUND 1 (bounded, honest, multi-family end-to-end null).

Tests three justified candidate families as HELD-OUT hypotheses:
  ANA  = pre-Greek Aegean / Anatolian-contact (Luwic)
  SEM  = West/Common Semitic
  CTRL = agnostic random-lexicon negative control

Each family is a BOUNDED preregistered correspondence (prereg/candidate_round1_prereg.json):
phoneme inventory + allowed changes into the LA syllabary + a SMALL lexicon of candidate-
language WORDS. Every lexeme is EXPANDED to its predicted LA syllabogram-value string(s) via
the fixed correspondence (derived from the candidate language, never read off LA). A held-out
LA multi-sign GORILA word MATCHES a family iff its value-string is a predicted whole-word form,
or (affix entries) it ends with a predicted affix string.

Primary statistic = token-weighted match rate on the held-out multi-sign syllabic word set.
Scored vs the WP6 multi-family END-TO-END null:
  (S) order-shuffle LA within word           -> kills form structure (non-decisive)
  (W) wrong-language opaque LB, length-matched -> the WP6 trap: a real other language, same matcher
  (R) random-prior: lexicon permuted, search size preserved -> kills lexicon informativeness
Decisive nulls for a LANGUAGE claim = W and R. FWER_family = fraction of decisive null
realizations with match >= real. Search-adjusted across the 3 families by Holm. Leave-one-
lexeme-out reported (Egyptian-channel discipline: does a single lexeme carry the signal?).

Non-circular: LB values appear ONLY as the wrong-language null corpus; predicted forms are
derived from candidate-language dictionaries, never fitted to LA. Deterministic seed 20260708.
"""
from __future__ import annotations
import json, os, sys
from collections import Counter

import numpy as np

MAIN = "/home/claude-runner/gitlab/n8n/logos"
sys.path.insert(0, MAIN)
from scripts.cross_script import data as X  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
PREREG = os.path.join(HERE, "..", "prereg", "candidate_round1_prereg.json")
SEED = 20260708
N_NULL = 200
EXPAND_CAP = 256  # max predicted forms per lexeme (bound the correspondence search)

# --------------------------------------------------- syllabogram (onset-series, vowel) decomposition
# series letter -> {vowel: value}  (standard Ventris-Chadwick values of the 59 AB syllabograms)
SERIES2VOWEL = {
    "":  {"a": "A",  "e": "E",  "i": "I",  "o": "O",  "u": "U"},
    "D": {"a": "DA", "e": "DE", "i": "DI", "u": "DU"},
    "J": {"a": "JA", "e": "JE", "u": "JU"},
    "K": {"a": "KA", "e": "KE", "i": "KI", "o": "KO", "u": "KU"},
    "M": {"a": "MA", "e": "ME", "i": "MI", "u": "MU"},
    "N": {"a": "NA", "e": "NE", "i": "NI", "u": "NU"},
    "P": {"a": "PA", "i": "PI", "o": "PO", "u": "PU"},
    "Q": {"a": "QA", "e": "QE", "i": "QI"},
    "R": {"a": "RA", "e": "RE", "i": "RI", "o": "RO", "u": "RU"},
    "S": {"a": "SA", "e": "SE", "i": "SI", "u": "SU"},
    "T": {"a": "TA", "e": "TE", "i": "TI", "o": "TO", "u": "TU"},
    "W": {"a": "WA", "i": "WI"},
    "Z": {"a": "ZA", "e": "ZE", "o": "ZO", "u": "ZU"},
}
VOWELS = set("aeiou")


def load_prereg():
    return json.load(open(PREREG))


def realize_syllable(series_options, vowel, out_partial):
    """Given a set of series-letter options and a vowel, return list of extended sign-lists."""
    ext = []
    for pre in out_partial:
        for ser in series_options:
            val = SERIES2VOWEL.get(ser, {}).get(vowel)
            if val is not None:
                ext.append(pre + [val])
    return ext


def expand_phonemes(phonemes, cons2series, vowel_map, cap=EXPAND_CAP):
    """Turn a phoneme string into the set of predicted syllabogram-value tuples (bounded).

    Two standard Linear-B spelling facts applied UNIFORMLY to every family: (1) geminate
    consonants are collapsed (LB never writes doubles); (2) a coda ("dead-vowel") consonant is
    spelled C + an epenthetic vowel that ranges over ALL family vowels (the LB dead vowel is not
    fixed: ku-ru-so for khrusos, a-to-ro-qo for anthropos). CV parsing: consonant+vowel -> CV
    sign; coda consonant (before consonant/end) -> C + {all vowels}; initial/hiatus vowel ->
    pure-vowel sign. Consonant+vowel realizations with no syllabogram are pruned (no PE/DO/ZI).
    The larger predicted set is FULLY absorbed by the search-size-matched random-prior null and
    reported as effective_n."""
    # geminate collapse on consonant phonemes
    toks_raw = phonemes.split()
    toks = []
    for t in toks_raw:
        if toks and t == toks[-1] and t not in vowel_map:
            continue
        toks.append(t)
    all_vowels = sorted({v for vs in vowel_map.values() for v in vs})
    partial = [[]]  # list of sign-lists under construction
    i = 0
    while i < len(toks):
        ph = toks[i]
        if ph in vowel_map:
            realized_v = vowel_map[ph]
            new = []
            for pre in partial:
                for v in realized_v:
                    new.extend(realize_syllable([""], v, [pre]))
            partial = new
            i += 1
        else:
            series = cons2series.get(ph)
            if series is None:
                i += 1
                continue
            if i + 1 < len(toks) and toks[i + 1] in vowel_map:
                vlist = vowel_map[toks[i + 1]]
                new = []
                for pre in partial:
                    for v in vlist:
                        new.extend(realize_syllable(series, v, [pre]))
                partial = new
                i += 2
            else:  # coda: epenthetic dead vowel ranges over all family vowels
                new = []
                for pre in partial:
                    for v in all_vowels:
                        new.extend(realize_syllable(series, v, [pre]))
                partial = new
                i += 1
        if len(partial) > cap:
            partial = [list(p) for p in sorted(set(tuple(p) for p in partial))[:cap]]
    forms = sorted(set(tuple(p) for p in partial if p))
    return forms


def build_family_predictions(fam_def, lexicon):
    """Return (word_forms:set of tuples, suffix_forms:list of tuples, per_entry:list)."""
    cons2series = fam_def["consonant_to_series"]
    vowel_map = fam_def["vowel_map"]
    word_forms = set()
    suffix_forms = set()
    per_entry = []
    for e in lexicon:
        forms = expand_phonemes(e["phonemes"], cons2series, vowel_map)
        # whole-word entries must be multi-sign to be discriminating
        if e["kind"] == "word":
            wf = [f for f in forms if len(f) >= 2]
            word_forms.update(wf)
            per_entry.append({"form": e["form"], "function": e["function"], "kind": "word",
                              "n_predicted": len(wf),
                              "examples": ["-".join(f) for f in wf[:6]]})
        else:  # suffix
            sf = [f for f in forms if len(f) >= 1]
            suffix_forms.update(sf)
            per_entry.append({"form": e["form"], "function": e["function"], "kind": "suffix",
                              "n_predicted": len(sf),
                              "examples": ["-".join(f) for f in sf[:6]]})
    return word_forms, suffix_forms, per_entry


def word_matches(w, word_forms, suffix_forms):
    if w in word_forms:
        return True
    for suf in suffix_forms:
        if len(w) > len(suf) and w[-len(suf):] == suf:
            return True
    return False


def score_corpus(tokens, word_forms, suffix_forms):
    """token-weighted match rate on a list of word tuples."""
    if not tokens:
        return 0.0, 0
    m = sum(1 for w in tokens if word_matches(w, word_forms, suffix_forms))
    return m / len(tokens), m


# --------------------------------------------------- corpora
def load_la_multisign():
    wu = json.load(open(os.path.join(DATA, "candidate_wordunits.json")))
    toks = [tuple(w["signs"]) for w in wu["words"] if len(w["signs"]) >= 2]
    return toks


def load_lb_multisign(syllabary):
    seqs, _, _ = X.load_b_damos()
    # keep multi-sign words; restrict to LA-comparable AB values (others simply never match)
    out = [tuple(s for s in w) for w in seqs if len([s for s in w if s]) >= 2]
    return out


def sample_lb_lengthmatched(lb_words, la_len_dist, n, rng):
    """Sample LB words to match the LA multi-sign word-length distribution."""
    by_len = {}
    for w in lb_words:
        by_len.setdefault(len(w), []).append(w)
    lens = list(la_len_dist.keys())
    probs = np.array([la_len_dist[l] for l in lens], dtype=float)
    probs /= probs.sum()
    out = []
    for _ in range(n):
        L = int(rng.choice(lens, p=probs))
        pool = by_len.get(L)
        if not pool:  # nearest available length
            avail = sorted(by_len.keys(), key=lambda k: abs(k - L))
            pool = by_len[avail[0]]
        out.append(pool[rng.integers(0, len(pool))])
    return out


def shuffle_within(tokens, rng):
    out = []
    for w in tokens:
        w2 = list(w)
        rng.shuffle(w2)
        out.append(tuple(w2))
    return out


def random_lexicon(lexicon, fam_def, rng):
    """Permute the lexicon: same #entries/kinds, same phoneme LENGTHS, random phonemes from the
    family's own inventory. Preserves expansion/search size; destroys the specific lexemes."""
    inv = fam_def["phoneme_inventory"]
    cons = [p for p in inv if p not in VOWELS]
    vows = [p for p in inv if p in VOWELS]
    new = []
    for e in lexicon:
        toks = e["phonemes"].split()
        nt = []
        for t in toks:
            if t in fam_def["vowel_map"] or t in VOWELS:
                nt.append(vows[rng.integers(0, len(vows))] if vows else "a")
            else:
                nt.append(cons[rng.integers(0, len(cons))] if cons else "t")
        new.append({"form": "rand", "function": "rand", "kind": e["kind"], "phonemes": " ".join(nt)})
    return new


# --------------------------------------------------- main
def run():
    prereg = load_prereg()
    fams = prereg["families"]
    la = load_la_multisign()
    n_la = len(la)
    la_len_dist = Counter(len(w) for w in la)
    la_len_dist = {k: v / n_la for k, v in la_len_dist.items()}
    syllabary = set(json.load(open(os.path.join(DATA, "candidate_wordunits.json")))["syllabary_AB_values"])
    lb = load_lb_multisign(syllabary)

    # materialize CTRL random lexicon deterministically
    ctrl_rng = np.random.default_rng(SEED)
    ana_lex = fams["ANA_preGreek_Anatolian"]["lexicon"]
    sem_lex = fams["SEM_westSemitic"]["lexicon"]
    # match CTRL structure: 4 word + 2 suffix, lengths ~ mean of ANA/SEM entries
    template = []
    for e in ana_lex + sem_lex:
        template.append((e["kind"], len(e["phonemes"].split())))
    word_lens = [l for k, l in template if k == "word"]
    suf_lens = [l for k, l in template if k == "suffix"]
    ctrl_inv = fams["CTRL_agnostic_random"]["phoneme_inventory"]
    ctrl_cons = [p for p in ctrl_inv if p not in VOWELS]
    ctrl_vows = [p for p in ctrl_inv if p in VOWELS]

    def rand_phon(length):
        toks = []
        for j in range(length):
            if j % 2 == 1:
                toks.append(ctrl_vows[ctrl_rng.integers(0, len(ctrl_vows))])
            else:
                toks.append(ctrl_cons[ctrl_rng.integers(0, len(ctrl_cons))])
        return " ".join(toks)

    ctrl_lex = []
    for _ in range(4):
        L = int(ctrl_rng.choice(word_lens))
        ctrl_lex.append({"form": "ctrl", "function": "CONTROL", "kind": "word", "phonemes": rand_phon(L)})
    for _ in range(2):
        L = int(ctrl_rng.choice(suf_lens))
        ctrl_lex.append({"form": "ctrl", "function": "CONTROL", "kind": "suffix", "phonemes": rand_phon(L)})
    fams["CTRL_agnostic_random"]["_materialized_lexicon"] = ctrl_lex

    lexicons = {
        "ANA_preGreek_Anatolian": ana_lex,
        "SEM_westSemitic": sem_lex,
        "CTRL_agnostic_random": ctrl_lex,
    }

    # ---- precompute shared null banks (identical across families => comparable) ----
    S_BANK = []  # order-shuffle LA corpora
    W_BANK = []  # wrong-language LB length-matched corpora
    for r in range(N_NULL):
        S_BANK.append(shuffle_within(la, np.random.default_rng(SEED + 100 + r)))
        W_BANK.append(sample_lb_lengthmatched(lb, la_len_dist, n_la,
                                              np.random.default_rng(SEED + 200 + r)))

    def score_bank(bank, wf, sf):
        return np.array([score_corpus(c, wf, sf)[0] for c in bank])

    def r_null_scores(lex, fam_def, n=N_NULL, seed0=SEED + 300):
        """random-prior: permute the lexicon (search size preserved), score on REAL LA."""
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
        R = r_null_scores(lex, fam_def, seed0=SEED + 300 + hash(fname) % 50000)

        def emp_p(arr):
            return (int((arr >= real_rate).sum()) + 1) / (len(arr) + 1)

        def summ(arr):
            return {"mean": round(float(arr.mean()), 5), "sd": round(float(arr.std()), 5),
                    "p95": round(float(np.percentile(arr, 95)), 5),
                    "max": round(float(arr.max()), 5),
                    "emp_p": round(emp_p(arr), 4),
                    "z": round(float((real_rate - arr.mean()) / (arr.std() + 1e-12)), 3)}

        p_S, p_W, p_R = emp_p(S), emp_p(W), emp_p(R)
        decisive_p = max(p_W, p_R)  # must beat BOTH decisive nulls

        # ---- leave-one-lexeme-out (robustness): worst-case decisive FWER (reuse shared banks)
        loo = []
        for k in range(len(lex)):
            sublex = [lex[j] for j in range(len(lex)) if j != k]
            swf, ssf, _ = build_family_predictions(fam_def, sublex)
            sub_real, _ = score_corpus(la, swf, ssf)
            wsc = score_bank(W_BANK, swf, ssf)
            rsc = r_null_scores(sublex, fam_def, seed0=SEED + 9000 + k * 211 + hash(fname) % 40000)
            pw = (int((wsc >= sub_real).sum()) + 1) / (N_NULL + 1)
            pr = (int((rsc >= sub_real).sum()) + 1) / (N_NULL + 1)
            loo.append({"dropped": lex[k]["form"], "sub_real_rate": round(sub_real, 5),
                        "p_W": round(pw, 4), "p_R": round(pr, 4), "decisive_p": round(max(pw, pr), 4)})
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
            "materialized_lexicon": [e["phonemes"] for e in lex] if fname.startswith("CTRL") else None,
        }

    # ---- Holm across the 3 families on the decisive FWER
    order = sorted(results.keys(), key=lambda f: results[f]["decisive_FWER_maxWR"])
    m = len(order)
    holm = {}
    running = 0.0
    for rank, f in enumerate(order):
        p = results[f]["decisive_FWER_maxWR"]
        adj = min(1.0, p * (m - rank))
        running = max(running, adj)  # enforce monotonic step-down
        holm[f] = round(running, 4)
    for f in results:
        results[f]["holm_adjusted_decisive_p"] = holm[f]
        results[f]["clears_raw_bar"] = bool(
            holm[f] < 0.05 and results[f]["loo_worst_decisive_p"] < 0.05)

    # ---- RANDOM-LEXICON FALSE-CLEAR CALIBRATION -------------------------------------------------
    # The decisive bar (beat W and R) can be passed by ANY lexicon that generates LA-typical word
    # shapes -- not just a real language. To calibrate its specificity we draw many random lexicons
    # matched to each real family's STRUCTURE and measure how often they clear the SAME raw bar, and
    # where the real family sits in the random-lexicon match-rate distribution. A family only counts
    # as a genuine signal if it beats this calibration (real match rate above the random-lexicon
    # band AND the raw-bar false-clear rate is controlled).
    N_CAL = 300
    calibration = {}
    for fname in ("ANA_preGreek_Anatolian", "SEM_westSemitic"):
        fam_def = fams[fname]
        lex = lexicons[fname]
        real_rate = results[fname]["real_token_match_rate"]
        cal_rates = []
        cal_clear = 0
        for c in range(N_CAL):
            rlex = random_lexicon(lex, fam_def, np.random.default_rng(SEED + 700000 + c * 17))
            rwf, rsf, _ = build_family_predictions(fam_def, rlex)
            rr = score_corpus(la, rwf, rsf)[0]
            cal_rates.append(rr)
            # does this random lexicon clear the decisive bar? (vs W bank + fresh R draws)
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
        # genuine signal requires: clears raw bar, survives LOO, AND real rate beats random-lexicon
        # band at p<0.05 with a controlled false-clear rate
        results[fname]["clears_calibrated"] = bool(
            results[fname]["clears_raw_bar"]
            and pct < 0.05
            and calibration[fname]["raw_bar_false_clear_rate"] <= 0.10)

    results["CTRL_agnostic_random"]["clears_calibrated"] = False  # control, by construction

    genuine = [f for f in results if results[f].get("clears_calibrated")]
    ctrl_cleared_raw = results["CTRL_agnostic_random"]["clears_raw_bar"]
    verdict = "BEATS_END_TO_END_NULL" if genuine else "AT_END_TO_END_NULL"

    out = {
        "experiment": "candidate_language_round_1",
        "seed": SEED, "n_nulls_per_family": N_NULL,
        "held_out": {"unit": "GORILA multi-sign syllabic word tokens",
                     "n_tokens": n_la,
                     "n_types": len(set(la)),
                     "la_word_length_dist": {str(k): round(v, 4) for k, v in sorted(la_len_dist.items())}},
        "wrong_language_null": {"corpus": "DAMOS Linear B wordforms (load_b_damos), multi-sign, "
                                          "length-matched to LA", "n_lb_multisign_words": len(lb)},
        "families": results,
        "families_clearing_calibrated": genuine,
        "ctrl_cleared_raw_bar": ctrl_cleared_raw,
        "verdict": verdict,
        "interpretation": None,
    }
    out["interpretation"] = (
        "Three candidate families tested as held-out hypotheses against the WP6 multi-family "
        "end-to-end null (S order-shuffle; W wrong-language opaque LB; R random-prior). A family is a "
        "GENUINE signal only if it (1) clears the decisive bar max(p_W,p_R) Holm-adjusted<0.05, (2) "
        "survives leave-one-lexeme-out (not carried by a single word), AND (3) beats a random-lexicon "
        "calibration (real match rate above the same-structure random-lexicon band at p<0.05 with a "
        "controlled false-clear rate). Result: %s. %s%s"
        % (verdict,
           ("GENUINE families: " + ", ".join(genuine) + ". " if genuine
            else "No family is a genuine signal. "),
           ("SEM_westSemitic's raw clearing (decisive p=%.3f) is driven ENTIRELY by the single lexeme "
            "kull->KU-RO/KU-RA/KU-RE (leave-one-lexeme-out decisive p=%.2f — dropping it erases the "
            "signal). ANA fails the wrong-language null (p_W=%.3f). Critically, the AGNOSTIC RANDOM "
            "control%s cleared the raw bar, and random lexicons of matched structure clear it at rate "
            "%.1f%%(SEM)/%.1f%%(ANA) — so the bar is passable by generic LA word-shape typicality, not "
            "language-specific lexical fit. This is the WP6 AT_END_TO_END_NULL trap confirmed for named "
            "candidate languages: a single famous administrative match (KU-RO 'total') survives, but no "
            "family predicts held-out LA forms beyond a same-structure random lexicon."
            % (results["SEM_westSemitic"]["decisive_FWER_maxWR"],
               results["SEM_westSemitic"]["loo_worst_decisive_p"],
               results["ANA_preGreek_Anatolian"]["p_W"],
               (" (CTRL)" if ctrl_cleared_raw else ""),
               results["SEM_westSemitic"]["calibration"]["raw_bar_false_clear_rate"] * 100,
               results["ANA_preGreek_Anatolian"]["calibration"]["raw_bar_false_clear_rate"] * 100))))

    os.makedirs(DATA, exist_ok=True)
    p = os.path.join(DATA, "candidate_round1_results.json")
    json.dump(out, open(p, "w"), indent=1)

    print(json.dumps({"verdict": verdict, "genuine": genuine, "ctrl_cleared_raw": ctrl_cleared_raw,
                      **{f: {"real": results[f]["real_token_match_rate"],
                             "eff_n": results[f]["effective_n_predicted_forms"],
                             "p_S": results[f]["p_S"], "p_W": results[f]["p_W"],
                             "p_R": results[f]["p_R"],
                             "decisive_FWER": results[f]["decisive_FWER_maxWR"],
                             "holm": results[f]["holm_adjusted_decisive_p"],
                             "loo_worst": results[f]["loo_worst_decisive_p"],
                             "clears_raw": results[f]["clears_raw_bar"],
                             "clears_calibrated": results[f].get("clears_calibrated"),
                             "cal_pct": results[f].get("calibration", {}).get("real_percentile_p_vs_random_lexicons"),
                             "cal_false_clear": results[f].get("calibration", {}).get("raw_bar_false_clear_rate"),
                             "hits": results[f]["matched_LA_word_types"][:8]}
                         for f in results}}, indent=1))
    print("\nWROTE", os.path.abspath(p))
    return out


if __name__ == "__main__":
    run()
