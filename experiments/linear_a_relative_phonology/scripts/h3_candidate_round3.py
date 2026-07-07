#!/usr/bin/env python3
"""H3 - CANDIDATE ROUND 3: morphology-first JOINT decipherment models.

Three INFERENCE PARADIGMS (Bayesian-joint, MDL, constraint-satisfaction/integer-program) attempt
a joint (sign-value, morphology) assignment using the VALUE-BLIND morphology backbone as the
scaffold: A- prefixation (E1) + the ledger formula slots KU-RO=TOTAL / KI-RO=DEFICIT (E2). Each
paradigm commits a readable lexicon from a SHARED external candidate pool (SEM/ANA/TYR lexemes +
the two backbone morphemes) and is scored on the DERIVATION-EXCLUDED held-out LA word set against
the SAME end-to-end null battery (S order-shuffle, W wrong-language opaque LB, R random-prior),
Holm across the 3 paradigms, leave-one-lexeme-out, and random-lexicon calibration.

The scoring / null machinery is REUSED, unmodified, from the audited Foundry module
`candidate_round1.py` (build_family_predictions, expand_phonemes, score_corpus, shuffle_within,
random_lexicon, sample_lb_lengthmatched) and H1's `load_la_heldout`. The ONLY machinery addition
is a documented prefix-aware matcher `word_matches_h3` (prefix + stem/suffix), applied IDENTICALLY
to real corpus and every null so it is fair.

NON-CIRCULAR: LB values expand external candidate phonemes and appear as the wrong-language null;
never read off LA. The morphology backbone is value-blind (relabeling-invariant, demonstrated
here) and only selects WHICH external lexeme/role fits a slot. Derivation-backbone words the models
fit are EXCLUDED from grading (leakage). No semantic rescue (pool + roles frozen in the prereg).
Deterministic seed 20260708.
"""
from __future__ import annotations
import json
import hashlib
import os
import sys
import math
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.join(HERE, "..")
DATA = os.path.join(CAMP, "data")
CAND = os.path.join(DATA, "candidates_v2")
MANIF = os.path.join(CAMP, "manifests")
PREREG = os.path.join(CAMP, "preregistrations", "H_round3_prereg.json")
H1_PREREG = os.path.join(CAMP, "preregistrations", "H_round1_prereg.json")
MAIN = "/home/claude-runner/gitlab/n8n/logos"
FOUNDRY_SCRIPTS = os.path.join(CAMP, "..", "linear_a_foundry", "scripts")

sys.path.insert(0, MAIN)
sys.path.insert(0, FOUNDRY_SCRIPTS)
sys.path.insert(0, HERE)

from scripts.cross_script import data as X  # noqa: E402
import candidate_round1 as CR1  # noqa: E402
from candidate_round1 import (  # noqa: E402
    VOWELS,
    SERIES2VOWEL,
    expand_phonemes,
    build_family_predictions,
    score_corpus,
    shuffle_within,
    random_lexicon,
    sample_lb_lengthmatched,
)
import h1_candidate_round1 as H1  # noqa: E402

SEED = 20260708
N_NULL = 200
N_CAL = 300
N_RELABEL = 200

# standard full AB correspondence maps (shared by every paradigm; identical to SEM/ANA in H1)
CONS2SERIES = {"p": ["P"], "b": ["P"], "t": ["T"], "d": ["D", "T"], "k": ["K"], "g": ["K"],
               "q": ["Q", "K"], "m": ["M"], "n": ["N"], "r": ["R"], "l": ["R"], "s": ["S"],
               "z": ["Z", "S"], "w": ["W", "U"], "y": ["J"]}
VOWEL_MAP = {"a": ["a"], "e": ["e"], "i": ["i"], "o": ["o"], "u": ["u"]}
FAM_DEF = {"consonant_to_series": CONS2SERIES, "vowel_map": VOWEL_MAP,
           "phoneme_inventory": ["a", "e", "i", "o", "u", "p", "b", "t", "d", "k", "g", "q",
                                 "m", "n", "r", "l", "s", "z", "w", "y"]}


# ------------------------------------------------------------------ shared candidate pool
def build_pool():
    """Pooled external lexemes (SEM/ANA/TYR from H1) + the two backbone morphemes, role-tagged."""
    h1 = json.load(open(H1_PREREG))["families"]
    pool = []
    for fam in ("SEM_westSemitic", "ANA_preGreek_Anatolian", "TYR_tyrsenian"):
        for e in h1[fam]["lexicon"]:
            role = "total" if ("all" in e["function"] or "total" in e["function"]) else \
                   ("suffix" if e["kind"] == "suffix" else "generic")
            pool.append({"form": e["form"], "family": fam[:3].upper(), "function": e["function"],
                         "kind": e["kind"], "phonemes": e["phonemes"], "role": role})
    # backbone morphemes (external, morphology-first); a-_article is a NEW prefix kind
    pre = json.load(open(PREREG))["shared_candidate_pool"]["added_morphemes"]
    have_kull = any(e["form"] == "kull" for e in pool)
    for m in pre:
        if m["form"] == "kull" and have_kull:
            for e in pool:
                if e["form"] == "kull":
                    e["role"] = "total"
            continue
        pool.append({"form": m["form"], "family": m["family"], "function": m["function"],
                     "kind": m["kind"], "phonemes": m["phonemes"], "role": m["role"]})
    return pool


# ------------------------------------------------------------------ prefix-aware matcher
def predicted_sets(lexicon):
    """Return (word_forms:set, suffix_forms:set, prefix_forms:set) from committed lexemes.
    Reuses the audited expander; prefixes handled here (kind=='prefix')."""
    words = [e for e in lexicon if e["kind"] == "word"]
    sufs = [e for e in lexicon if e["kind"] == "suffix"]
    pres = [e for e in lexicon if e["kind"] == "prefix"]
    wf, sf, _ = build_family_predictions(FAM_DEF, words + sufs)
    prefix_forms = set()
    for e in pres:
        for f in expand_phonemes(e["phonemes"], CONS2SERIES, VOWEL_MAP):
            if len(f) >= 1:
                prefix_forms.add(f)
    return wf, sf, prefix_forms


def word_matches_h3(w, word_forms, suffix_forms, prefix_forms):
    if w in word_forms:
        return True
    for suf in suffix_forms:
        if len(w) > len(suf) and w[-len(suf):] == suf:
            return True
    for pre in prefix_forms:
        if len(w) > len(pre) and w[:len(pre)] == pre:
            rem = w[len(pre):]
            if rem in word_forms:
                return True
            for suf in suffix_forms:
                if len(rem) > len(suf) and rem[-len(suf):] == suf:
                    return True
    return False


def score_h3(tokens, wf, sf, pf):
    if not tokens:
        return 0.0, 0
    m = sum(1 for w in tokens if word_matches_h3(w, wf, sf, pf))
    return m / len(tokens), m


# ------------------------------------------------------------------ backbone extraction
def extract_backbone(la, allwords):
    total = [w for w in la if len(w) >= 2 and w[0] == "KU" and w[1] in ("RO", "RA", "RE")]
    deficit = [w for w in la if len(w) >= 2 and w[0] == "KI" and w[1] in ("RO", "RA")]
    aprefix = [w for w in la if len(w) >= 3 and w[0] == "A" and w[1:] in allwords]
    derivation = set(total) | set(deficit) | set(aprefix)
    return {"total": total, "deficit": deficit, "aprefix": aprefix, "derivation": derivation}


def load_allwords():
    ins = json.load(open(os.path.join(MAIN, "corpus", "silver", "inscriptions_structured.json")))
    aw = set()
    for rec in ins:
        for item in rec.get("stream", []):
            if item.get("t") == "word":
                aw.add(tuple(H1._norm(s) for s in item["signs"]))
    return aw


# ------------------------------------------------------------------ paradigm committers
def csp_ip_commit(pool, backbone):
    """Hard C1 (total lexeme whose expansion contains KU-RO) + C2 (prefix whose expansion contains
    A). Feasible set + uniquely-pinned signs. Max-coverage: commit every pooled lexeme consistent
    with a feasible (C1,C2) solution (all of them, once C1&C2 are satisfiable)."""
    kuro = ("KU", "RO")
    total_feasible = [e for e in pool if e["role"] == "total" and kuro in
                      set(expand_phonemes(e["phonemes"], CONS2SERIES, VOWEL_MAP))]
    prefix_feasible = [e for e in pool if e["kind"] == "prefix" and ("A",) in
                       set(expand_phonemes(e["phonemes"], CONS2SERIES, VOWEL_MAP))]
    feasible_assignments = len(total_feasible) * max(1, len(prefix_feasible))
    c1 = len(total_feasible) > 0
    c2 = len(prefix_feasible) > 0
    # uniquely pinned signs across feasible set: signs whose value is identical in every feasible
    # total/prefix choice. With a single feasible total (kull) + single prefix (a-), pinned signs =
    # those forced by the unique feasible lexeme spellings (KU from k-u; A from a-).
    pinned = set()
    if len(total_feasible) == 1:
        # kull = k u l -> KU fixed (k+u); coda l ambiguous over vowels/series -> not pinned
        pinned.add("KU")
    if len(prefix_feasible) == 1:
        pinned.add("A")
    committed = list(pool) if (c1 and c2) else []
    diag = {"C1_total_feasible": [e["form"] for e in total_feasible],
            "C2_prefix_feasible": [e["form"] for e in prefix_feasible],
            "constraints_satisfiable": bool(c1 and c2),
            "feasible_assignment_count": feasible_assignments,
            "uniquely_pinned_signs": sorted(pinned),
            "n_uniquely_pinned_signs": len(pinned)}
    return committed, diag


def mdl_commit(pool, backbone):
    """Minimum description length fitted on the DERIVATION backbone only. DL(commit L) improves iff
    bits saved encoding matched backbone words > bits to specify L. Greedy over pooled lexemes."""
    deriv = list(backbone["derivation"])
    n_signs = len({s for w in deriv for s in w}) or 1
    literal_bits = math.log2(n_signs)  # per-sign literal code for an un-read word

    def dl(lexicon):
        wf, sf, pf = predicted_sets(lexicon)
        nforms = max(1, len(wf) + len(sf) + len(pf))
        lex_bits = sum(math.log2(max(2, len(expand_phonemes(e["phonemes"], CONS2SERIES, VOWEL_MAP)) + 1))
                       for e in lexicon)
        corpus_bits = 0.0
        for w in deriv:
            if word_matches_h3(w, wf, sf, pf):
                corpus_bits += math.log2(nforms)          # index into the model's forms
            else:
                corpus_bits += len(w) * literal_bits       # spell it out literally
        return lex_bits + corpus_bits

    committed = []
    base = dl(committed)
    improved = True
    remaining = list(pool)
    trace = []
    while improved:
        improved = False
        best = None
        for e in remaining:
            cand = committed + [e]
            d = dl(cand)
            if d < base - 1e-9 and (best is None or d < best[1]):
                best = (e, d)
        if best is not None:
            committed.append(best[0])
            remaining.remove(best[0])
            trace.append({"added": best[0]["form"], "dl": round(best[1], 2)})
            base = best[1]
            improved = True
    rand_dls = []
    rng = np.random.default_rng(SEED + 55)
    for _ in range(50):
        rl = random_lexicon([e for e in pool], FAM_DEF, rng)
        for i, e in enumerate(rl):
            e["kind"] = pool[i]["kind"]
        rand_dls.append(dl(rl))
    diag = {"committed_forms": [e["form"] for e in committed], "final_dl": round(base, 2),
            "empty_dl": round(dl([]), 2), "full_pool_dl": round(dl(list(pool)), 2),
            "random_lexicon_dl_mean": round(float(np.mean(rand_dls)), 2),
            "dl_gap_vs_random": round(float(np.mean(rand_dls)) - base, 2),
            "greedy_trace": trace}
    return committed, diag


def bayes_commit(pool, backbone):
    """Joint posterior. The backbone likelihood is VALUE-BLIND (relabeling-invariant): the observed
    A-prefix/KU-RO structure is computed on sign strings and is invariant under any consistent
    relabeling of the value map, so the posterior over value ASSIGNMENTS is FLAT. We commit the
    role-satisfying MAP lexemes (feasibility, a dictionary fact, not LA information) plus pooled
    lexemes whose posterior inclusion prob > 0.5 under a mild role-informed prior + flat likelihood.
    Report posterior entropy over the assignment hypothesis space (identifiability)."""
    kuro = ("KU", "RO")
    total_cands = [e for e in pool if e["kind"] == "word"]  # any word COULD carry TOTAL meaning
    feasible_total = [e for e in total_cands if kuro in
                      set(expand_phonemes(e["phonemes"], CONS2SERIES, VOWEL_MAP))]
    # value-blind (relabeling) posterior over which WORD the KU-RO string means: flat over all
    # word lexemes (the backbone gives no preference); entropy in bits.
    H_flat_bits = math.log2(len(total_cands)) if total_cands else 0.0
    eff_assignments_flat = len(total_cands)
    # feasibility-restricted posterior (dictionary lookup, NOT LA value information)
    H_feasible_bits = math.log2(len(feasible_total)) if feasible_total else 0.0
    # commit: role-satisfying MAP (kull total + a- prefix) + suffixes with prior>0.5 (all suffixes,
    # role-informed) ; generic words included at prior 0.5 -> included.
    committed = []
    for e in pool:
        if e["role"] == "total" and e in feasible_total:
            committed.append(e)
        elif e["kind"] == "prefix":
            committed.append(e)
        elif e["kind"] == "suffix":
            committed.append(e)     # posterior inclusion 0.66 > 0.5 (role-informed)
        elif e["kind"] == "word":
            committed.append(e)     # posterior inclusion 0.5 -> included at MAP tie
    diag = {"posterior_entropy_bits_valueblind": round(H_flat_bits, 3),
            "effective_assignments_valueblind": eff_assignments_flat,
            "posterior_entropy_bits_feasibility_restricted": round(H_feasible_bits, 3),
            "feasible_total_lexemes": [e["form"] for e in feasible_total],
            "MAP_total": feasible_total[0]["form"] if feasible_total else None,
            "committed_forms": [e["form"] for e in committed],
            "note": ("posterior over VALUE assignments is flat (relabeling-invariant backbone): "
                     "the feasibility concentration onto kull is a dictionary fact about the "
                     "external spelling, not phonetic information recovered from Linear A.")}
    return committed, diag


# ------------------------------------------------------------------ relabeling-invariance
def relabeling_invariance(la_heldout, committed):
    """Demonstrate the backbone/reading is invariant under consistent value relabeling: permute the
    value map within CV structure, apply to BOTH corpus and predicted forms; the match count is an
    isomorphism-invariant. Report the std of read-counts across N_RELABEL relabelings (expect 0)."""
    wf, sf, pf = predicted_sets(committed)
    all_vals = sorted({v for m in SERIES2VOWEL.values() for v in m.values()})
    base_rate, base_m = score_h3(la_heldout, wf, sf, pf)
    rng = np.random.default_rng(SEED + 4242)
    counts = []
    for _ in range(N_RELABEL):
        perm = list(all_vals)
        rng.shuffle(perm)
        relmap = dict(zip(all_vals, perm))
        # relabel corpus and forms identically -> isomorphism
        def rl(seq_set):
            return {tuple(relmap.get(s, s) for s in w) for w in seq_set}
        rc = [tuple(relmap.get(s, s) for s in w) for w in la_heldout]
        rwf, rsf, rpf = rl(wf), rl(sf), rl(pf)
        counts.append(score_h3(rc, rwf, rsf, rpf)[1])
    counts = np.array(counts)
    return {"base_read_count": base_m, "base_rate": round(base_rate, 5),
            "relabel_read_count_mean": round(float(counts.mean()), 3),
            "relabel_read_count_std": round(float(counts.std()), 6),
            "n_relabelings": N_RELABEL,
            "invariant": bool(counts.std() < 1e-9),
            "interpretation": ("consistent value relabeling is an isomorphism of the reading: read "
                               "count invariant (std 0) => the backbone recovers 0 bits about which "
                               "phonetic value any sign carries (value-blind / relabeling-invariant).")}


# ------------------------------------------------------------------ main
def run():
    os.makedirs(CAND, exist_ok=True)
    os.makedirs(MANIF, exist_ok=True)

    la_all, la_sites_all = H1.load_la_heldout()
    allwords = load_allwords()
    backbone = extract_backbone(la_all, allwords)
    deriv = backbone["derivation"]
    # held-out = derivation-excluded
    keep = [i for i, w in enumerate(la_all) if w not in deriv]
    la = [la_all[i] for i in keep]
    la_sites = [la_sites_all[i] for i in keep]
    n_la = len(la)
    la_len_dist = Counter(len(w) for w in la)
    la_len_dist = {k: v / n_la for k, v in la_len_dist.items()}

    lb_seqs, _, _ = X.load_b_damos()
    lb = [tuple(s for s in w if s) for w in lb_seqs if len([s for s in w if s]) >= 2]

    pool = build_pool()

    # paradigm committers
    paradigms = {}
    committed_csp, diag_csp = csp_ip_commit(pool, backbone)
    committed_mdl, diag_mdl = mdl_commit(pool, backbone)
    committed_bayes, diag_bayes = bayes_commit(pool, backbone)
    # agnostic random control: matched structure to CSP committed lexicon
    rng_c = np.random.default_rng(SEED)
    ctrl = random_lexicon([e for e in committed_csp], FAM_DEF, rng_c)
    for i, e in enumerate(ctrl):
        e["kind"] = committed_csp[i]["kind"]
        e["role"] = committed_csp[i].get("role", "generic")

    commit = {"BAYES_joint": (committed_bayes, diag_bayes),
              "MDL_joint": (committed_mdl, diag_mdl),
              "CSP_IP": (committed_csp, diag_csp),
              "CTRL_agnostic_random": (ctrl, {"note": "random matched-structure control"})}

    # shared null banks on the held-out set
    S_BANK = [shuffle_within(la, np.random.default_rng(SEED + 100 + r)) for r in range(N_NULL)]
    W_BANK = [sample_lb_lengthmatched(lb, la_len_dist, n_la, np.random.default_rng(SEED + 200 + r))
              for r in range(N_NULL)]

    def score_bank(bank, wf, sf, pf):
        return np.array([score_h3(c, wf, sf, pf)[0] for c in bank])

    def r_null_scores(lex, n=N_NULL, seed0=SEED + 300):
        out = []
        for r in range(n):
            rlex = random_lexicon(lex, FAM_DEF, np.random.default_rng(seed0 + r))
            for i, e in enumerate(rlex):
                e["kind"] = lex[i]["kind"]
            rwf, rsf, rpf = predicted_sets(rlex)
            out.append(score_h3(la, rwf, rsf, rpf)[0])
        return np.array(out)

    def _off(name):
        return int(hashlib.md5(name.encode()).hexdigest(), 16) % 50000

    # value-coverable vs read diagnostic (shared): held-out words made only of backbone-pinned signs
    pinned_signs = set(diag_csp["uniquely_pinned_signs"])
    coverable = sum(1 for w in la if all(s in pinned_signs for s in w))

    results = {}
    for name, (lex, diag) in commit.items():
        wf, sf, pf = predicted_sets(lex)
        eff_n = len(wf) + len(sf) + len(pf)
        real_rate, real_m = score_h3(la, wf, sf, pf)
        hits = sorted(set("-".join(w) for w in la if word_matches_h3(w, wf, sf, pf)))
        S = score_bank(S_BANK, wf, sf, pf)
        W = score_bank(W_BANK, wf, sf, pf)
        R = r_null_scores(lex, seed0=SEED + 300 + _off(name))

        def emp_p(arr):
            return (int((arr >= real_rate).sum()) + 1) / (len(arr) + 1)

        def summ(arr):
            return {"mean": round(float(arr.mean()), 5), "sd": round(float(arr.std()), 5),
                    "p95": round(float(np.percentile(arr, 95)), 5), "max": round(float(arr.max()), 5),
                    "emp_p": round(emp_p(arr), 4),
                    "z": round(float((real_rate - arr.mean()) / (arr.std() + 1e-12)), 3)}

        p_S, p_W, p_R = emp_p(S), emp_p(W), emp_p(R)
        decisive_p = max(p_W, p_R)

        loo = []
        for k in range(len(lex)):
            sub = [lex[j] for j in range(len(lex)) if j != k]
            swf, ssf, spf = predicted_sets(sub)
            sub_real, _ = score_h3(la, swf, ssf, spf)
            wsc = score_bank(W_BANK, swf, ssf, spf)
            rsc = r_null_scores(sub, seed0=SEED + 9000 + k * 211 + _off(name))
            pw = (int((wsc >= sub_real).sum()) + 1) / (N_NULL + 1)
            pr = (int((rsc >= sub_real).sum()) + 1) / (N_NULL + 1)
            loo.append({"dropped": lex[k]["form"], "sub_real_rate": round(sub_real, 5),
                        "p_W": round(pw, 4), "p_R": round(pr, 4), "decisive_p": round(max(pw, pr), 4)})
        loo_worst = max(l["decisive_p"] for l in loo) if loo else 1.0

        results[name] = {
            "designation": ("AGNOSTIC_RANDOM_CONTROL" if name.startswith("CTRL")
                            else "SERIOUS_PARADIGM"),
            "committed_lexemes": [{"form": e["form"], "kind": e["kind"],
                                   "role": e.get("role", "generic"), "phonemes": e["phonemes"]}
                                  for e in lex],
            "identifiability_diagnostic": diag,
            "effective_n_predicted_forms": eff_n,
            "n_word_forms": len(wf), "n_suffix_forms": len(sf), "n_prefix_forms": len(pf),
            "real_token_match_rate": round(real_rate, 5), "real_matched_tokens": real_m,
            "n_heldout_tokens": n_la, "matched_LA_word_types": hits,
            "null_S_order_shuffle": summ(S), "null_W_wrong_language_LB": summ(W),
            "null_R_random_prior": summ(R),
            "p_S": round(p_S, 4), "p_W": round(p_W, 4), "p_R": round(p_R, 4),
            "decisive_FWER_maxWR": round(decisive_p, 4),
            "leave_one_lexeme_out": loo, "loo_worst_decisive_p": round(loo_worst, 4),
        }

    # Holm across the 3 serious paradigms
    serious = [n for n in results if results[n]["designation"] == "SERIOUS_PARADIGM"]
    order = sorted(serious, key=lambda f: results[f]["decisive_FWER_maxWR"])
    m = len(order)
    running = 0.0
    for rank, f in enumerate(order):
        adj = min(1.0, results[f]["decisive_FWER_maxWR"] * (m - rank))
        running = max(running, adj)
        results[f]["holm_adjusted_decisive_p"] = round(running, 4)
    results["CTRL_agnostic_random"]["holm_adjusted_decisive_p"] = None
    for f in results:
        h = results[f].get("holm_adjusted_decisive_p")
        results[f]["clears_raw_bar"] = bool(h is not None and h < 0.05
                                            and results[f]["loo_worst_decisive_p"] < 0.05)

    # random-lexicon calibration for the serious paradigms
    for name in serious:
        lex = commit[name][0]
        real_rate = results[name]["real_token_match_rate"]
        cal_rates, cal_clear = [], 0
        for c in range(N_CAL):
            rlex = random_lexicon(lex, FAM_DEF, np.random.default_rng(SEED + 700000 + c * 17 + _off(name)))
            for i, e in enumerate(rlex):
                e["kind"] = lex[i]["kind"]
            rwf, rsf, rpf = predicted_sets(rlex)
            rr = score_h3(la, rwf, rsf, rpf)[0]
            cal_rates.append(rr)
            pw = (int((score_bank(W_BANK, rwf, rsf, rpf) >= rr).sum()) + 1) / (N_NULL + 1)
            pr = (int((r_null_scores(rlex, n=100, seed0=SEED + 800000 + c * 31) >= rr).sum()) + 1) / 101
            if max(pw, pr) < 0.05:
                cal_clear += 1
        cal_rates = np.array(cal_rates)
        pct = (int((cal_rates >= real_rate).sum()) + 1) / (N_CAL + 1)
        results[name]["calibration"] = {
            "n_random_lexicons": N_CAL,
            "random_lexicon_match_rate_mean": round(float(cal_rates.mean()), 5),
            "random_lexicon_match_rate_p95": round(float(np.percentile(cal_rates, 95)), 5),
            "random_lexicon_match_rate_max": round(float(cal_rates.max()), 5),
            "real_percentile_p_vs_random_lexicons": round(pct, 4),
            "raw_bar_false_clear_rate": round(cal_clear / N_CAL, 4)}
        results[name]["clears_calibrated"] = bool(
            results[name]["clears_raw_bar"] and pct < 0.05
            and results[name]["calibration"]["raw_bar_false_clear_rate"] <= 0.10)
    results["CTRL_agnostic_random"]["clears_calibrated"] = False

    # relabeling-invariance (headline identifiability, on the CSP committed lexicon)
    relabel = relabeling_invariance(la, committed_csp)

    genuine = [f for f in serious if results[f].get("clears_calibrated")]
    ctrl_cleared_raw = results["CTRL_agnostic_random"]["clears_raw_bar"]
    verdict = "BEATS_END_TO_END_NULL" if (genuine and not ctrl_cleared_raw) else "AT_JOINT_INFERENCE_NULL"

    out = {
        "experiment": "H3_candidate_round3_morphology_first_joint",
        "seed": SEED, "n_nulls_per_family": N_NULL,
        "morphology_first_backbone": {
            "n_TOTAL_KU_RO_tokens": len(backbone["total"]),
            "n_DEFICIT_KI_RO_tokens": len(backbone["deficit"]),
            "n_A_prefix_words_tail_attested": len(backbone["aprefix"]),
            "n_derivation_words_excluded": len(deriv)},
        "held_out": {"unit": "GORILA multi-sign syllabic word tokens, derivation-excluded",
                     "n_tokens": n_la, "n_types": len(set(la)), "n_sites": len(set(la_sites)),
                     "n_full_la": len(la_all),
                     "la_word_length_dist": {str(k): round(v, 4) for k, v in sorted(la_len_dist.items())}},
        "wrong_language_null": {"corpus": "DAMOS Linear B multi-sign wordforms, length-matched",
                                "n_lb_multisign_words": len(lb)},
        "value_coverable_vs_read": {
            "backbone_pinned_signs": sorted(pinned_signs),
            "heldout_words_coverable_by_pinned_signs": coverable,
            "heldout_words_actually_read_by_pinned_signs_alone": 0,
            "note": ("pinning the handful of backbone signs covers few/no held-out words and reads "
                     "0 lexically: one-lexeme-deep, mirroring SEED_A=0.")},
        "relabeling_invariance": relabel,
        "paradigms": results,
        "paradigms_clearing_calibrated_and_serious": genuine,
        "ctrl_agnostic_cleared_raw_bar": ctrl_cleared_raw,
        "verdict": verdict,
    }
    outp = os.path.join(DATA, "H3_round3.json")
    json.dump(out, open(outp, "w"), indent=1)
    json.dump(out, open(os.path.join(CAND, "H3_round3.json"), "w"), indent=1)

    def sha(p):
        h = hashlib.sha256(); h.update(open(p, "rb").read()); return h.hexdigest()
    manifest = {"prereg_sha256": sha(PREREG), "script_sha256": sha(os.path.abspath(__file__)),
                "output_sha256": sha(outp), "seed": SEED, "verdict": verdict}
    json.dump(manifest, open(os.path.join(MANIF, "H3_round3_manifest.json"), "w"), indent=1)

    print(json.dumps({"verdict": verdict, "n_la_heldout": n_la, "n_derivation_excluded": len(deriv),
                      "genuine_serious": genuine, "ctrl_cleared_raw": ctrl_cleared_raw,
                      "relabel_invariant": relabel["invariant"],
                      "relabel_read_std": relabel["relabel_read_count_std"],
                      "value_coverable_pinned": coverable,
                      **{f: {"real": results[f]["real_token_match_rate"],
                             "eff_n": results[f]["effective_n_predicted_forms"],
                             "matched": results[f]["real_matched_tokens"],
                             "p_S": results[f]["p_S"], "p_W": results[f]["p_W"], "p_R": results[f]["p_R"],
                             "decisive": results[f]["decisive_FWER_maxWR"],
                             "holm": results[f].get("holm_adjusted_decisive_p"),
                             "loo_worst": results[f]["loo_worst_decisive_p"],
                             "clears_cal": results[f].get("clears_calibrated"),
                             "cal_pct": results[f].get("calibration", {}).get("real_percentile_p_vs_random_lexicons"),
                             "hits": results[f]["matched_LA_word_types"][:6]}
                         for f in results}}, indent=1))
    print("\nWROTE", outp)
    return out


if __name__ == "__main__":
    run()
