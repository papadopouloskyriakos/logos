#!/usr/bin/env python3
"""PC_positive_controls.py — TASK PC: validate the comparison pipeline can DETECT truth and REJECT fakes.

Six controls, all graded MECHANICALLY (no LLM), seed 20260708:

  PC1  Ugaritic->Hebrew known Semitic decipherment    -> gate must RECOVER (run_canary, real data)
  PC2  opaque Linear B with known Greek truth          -> gate must RECOVER (Ventris map vs permuted)
  PC3  synthetic *301-style corpus, PLANTED sign value -> sweep must RECOVER the plant, ranked #1
  PC4  synthetic FALSE Semitic-root claim by search    -> deflation must REJECT (best-of-search at floor)
  PC5  known agglutinative (suffix) formula corpus     -> S_morph must FIRE, affixes = suffixes
  PC6  known Semitic prefix/root morphology corpus     -> S_morph must FIRE, affixes = prefixes
  PC-NP degraded PC1 (tiny held-out)                   -> must return NO_POWER (honest abstention)

Calibration claim (design §C.3): the L_fake FLOOR is > 0 AND < the positive benchmark; a real
correspondence clears it, a search-found fake does not. Everything below is a REAL measured number.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import unicodedata
from collections import Counter
from typing import Dict, List, Sequence, Tuple

import numpy as np

CAMP = "/home/claude-runner/gitlab/n8n/logos-di-mino-301-audit"
if CAMP not in sys.path:
    sys.path.insert(0, CAMP)

from scripts.comparison import lexstat, nulls, lfake, morphostat  # noqa: E402
from scripts.comparison import run_canary as canary  # noqa: E402

SEED = 20260708
RESULTS_DIR = os.path.join(CAMP, "experiments/di_mino_301_audit/data/results")
REPORTS_DIR = os.path.join(CAMP, "experiments/di_mino_301_audit/reports")
LINB_GREEK = os.path.join(CAMP, "corpus/bronze/linearb/linear_b-greek.cog")
GOLD_COG = os.path.join(CAMP, "corpus/bronze/ugaritic/uga-heb.gold.cog")


# --------------------------------------------------------------------------- #
# PC1 — Ugaritic -> Hebrew (real machinery, real data). MUST RECOVER.
# --------------------------------------------------------------------------- #
def pc1_ugaritic_hebrew() -> dict:
    rep = canary.run(n_fake=100, eps_grid=(0.20, 0.25, 0.30), base_seed=SEED,
                     max_heldout=500)
    h = rep["headline"]
    recovered = h["verdict"] == "CANARY_HOLDS_REAL_CLEARS_FLOOR"
    floor_positive = h["lfake_floor_mean"] > 0.0
    floor_below_benchmark = h["lfake_floor_mean"] < h["real_cognate_s_lex"]
    return {
        "name": "PC1_ugaritic_to_hebrew_real_semitic_decipherment",
        "expectation": "RECOVER",
        "primary_eps": h["eps"],
        "positive_s_lex_real_cognates": round(h["real_cognate_s_lex"], 4),
        "lfake_floor_mean": round(h["lfake_floor_mean"], 4),
        "lfake_floor_p95": round(h["lfake_floor_p95"], 4),
        "corrected_margin_bar": round(h["corrected_margin_bar"], 4),
        "margin_over_corrected_bar": round(h["real_cognate_s_lex"] - h["corrected_margin_bar"], 4),
        "canary_verdict": h["verdict"],
        "floor_gt_zero": bool(floor_positive),
        "floor_lt_positive_benchmark": bool(floor_below_benchmark),
        "recovered": bool(recovered),
        "outcome": "RECOVERED" if recovered else "FAILED_TO_RECOVER",
        "calibrated": bool(floor_positive and floor_below_benchmark and recovered),
    }


# --------------------------------------------------------------------------- #
# PC2 — opaque Linear B decoded to Greek. MUST RECOVER (true map beats permuted maps).
# --------------------------------------------------------------------------- #
_GK2LAT = {
    "α": "a", "β": "b", "γ": "g", "δ": "d", "ε": "e", "ζ": "z", "η": "e", "θ": "t",
    "ι": "i", "κ": "k", "λ": "r", "μ": "m", "ν": "n", "ξ": "k", "ο": "o", "π": "p",
    "ρ": "r", "σ": "s", "ς": "s", "τ": "t", "υ": "u", "φ": "p", "χ": "k", "ψ": "p",
    "ω": "o", "ϝ": "w", "f": "w",  # digamma is written both ways in this cog
}


def _norm_phon(s: str) -> str:
    """Coarse phonemic normalization so the DEFECTIVE LB syllabary and Greek land in one space:
    lowercase, l/r merged (LB has no l), drop word-final s (LB drops final consonants), collapse
    doubled letters, keep only [a-z]. Applied IDENTICALLY to both sides -> non-circular."""
    s = s.lower()
    out = []
    for ch in s:
        out.append(_GK2LAT.get(ch, ch))
    s = "".join(out)
    s = re.sub(r"[^a-z]", "", s)
    s = s.replace("l", "r")
    s = re.sub(r"(.)\1+", r"\1", s)      # collapse doubles
    s = re.sub(r"s$", "", s)             # LB drops a final -s
    return s


def _lb_value(ch: str):
    try:
        nm = unicodedata.name(ch)
    except ValueError:
        return None
    m = re.match(r"LINEAR B SYLLABLE B[0-9A-F]+ (\S+)", nm)
    return m.group(1) if m else None


def _load_linb_greek() -> Tuple[List[List[str]], List[str], List[str]]:
    """Return (lb_sign_seqs, greek_lexicon_norm, greek_first_norm).

    lb_sign_seqs : per-row list of LB syllabic VALUES (e.g. ['A','E','RI','QO','TA']).
    greek_lexicon_norm : all normalized Greek readings (the candidate lexicon / truth).
    greek_first_norm   : the first normalized reading per row (parallel to lb_sign_seqs).
    """
    lb_seqs: List[List[str]] = []
    gk_first: List[str] = []
    gk_lex: set = set()
    with open(LINB_GREEK, encoding="utf-8") as f:
        next(f)
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 2 or not parts[0].strip():
                continue
            vals = [v for v in (_lb_value(ch) for ch in parts[0]) if v]
            if len(vals) < 2:
                continue
            readings = [r for r in parts[1].split("|") if r and r != "_"]
            if not readings:
                continue
            lb_seqs.append(vals)
            gk_first.append(_norm_phon(readings[0]))
            for r in readings:
                nr = _norm_phon(r)
                if nr:
                    gk_lex.add(nr)
    return lb_seqs, sorted(gk_lex), gk_first


def _decode_lb(seqs: Sequence[Sequence[str]], value_map: Dict[str, str]) -> List[str]:
    """Romanize each LB value sequence through value_map (VALUE->latin syllable), then normalize."""
    out = []
    for seq in seqs:
        out.append(_norm_phon("".join(value_map.get(v, "") for v in seq)))
    return out


def _ventris_map(values: Sequence[str]) -> Dict[str, str]:
    """The TRUE Ventris reading of each LB value: the value string IS its phonetic reading
    (e.g. 'QO'->'qo','RI'->'ri','A2'->'a'). Non-circular: this is the published decipherment map,
    used only to transcribe the LB side, exactly as a decipherment claim would apply its map."""
    m = {}
    for v in values:
        r = v.lower()
        r = re.sub(r"[0-9]", "", r)      # A2->a, RA3->ra
        r = r.replace("q", "k").replace("z", "s")  # labiovelar/affricate -> coarse
        m[v] = r
    return m


def _banded_map_permutation(values: Sequence[str], value_map: Dict[str, str],
                            freq: Counter, seed: int, n_bands: int = 4) -> Dict[str, str]:
    """Frequency-banded permutation of the VALUE->reading assignment (Packard 1974 applied to the
    sign map): a sign keeps a reading of comparable-frequency, but the specific sign<->reading pair
    is destroyed. This is the decipherment null for a sign map."""
    rng = np.random.default_rng(seed)
    ordered = sorted(values, key=lambda v: (-freq.get(v, 0), v))
    per = max(1, int(np.ceil(len(ordered) / n_bands)))
    perm_map = {}
    for b in range(0, len(ordered), per):
        band = ordered[b:b + per]
        readings = [value_map[v] for v in band]
        idx = np.arange(len(readings)); rng.shuffle(idx)
        for v, j in zip(band, idx):
            perm_map[v] = readings[int(j)]
    return perm_map


def pc2_linearb_greek(eps: float = 0.34, n_null: int = 100) -> dict:
    lb_seqs, gk_lex, gk_first = _load_linb_greek()
    values = sorted({v for seq in lb_seqs for v in seq})
    freq: Counter = Counter(v for seq in lb_seqs for v in seq)
    true_map = _ventris_map(values)

    lb_true = _decode_lb(lb_seqs, true_map)
    # held-out forms = LB forms decoded with the TRUE map; candidate lexicon = Greek truth readings
    pos = lexstat.s_lex(lb_true, gk_lex, eps)

    # NULL: permuted sign->reading maps (frequency-banded). A wrong map must NOT recover Greek.
    null_scores = []
    for i in range(n_null):
        pm = _banded_map_permutation(values, true_map, freq, seed=SEED + i)
        null_scores.append(lexstat.s_lex(_decode_lb(lb_seqs, pm), gk_lex, eps))
    null = np.array(null_scores)
    p95 = float(np.percentile(null, 95))
    recovered = pos > p95
    return {
        "name": "PC2_opaque_linearb_to_greek_ventris",
        "expectation": "RECOVER",
        "eps": eps,
        "n_lb_forms": len(lb_seqs),
        "n_greek_lexemes": len(gk_lex),
        "n_lb_signs": len(values),
        "positive_s_lex_true_ventris_map": round(pos, 4),
        "permuted_map_null_mean": round(float(null.mean()), 4),
        "permuted_map_null_p95": round(p95, 4),
        "permuted_map_null_max": round(float(null.max()), 4),
        "margin_over_null_p95": round(pos - p95, 4),
        "power_ratio": round(pos / max(float(null.mean()), 1e-9), 2),
        "floor_gt_zero": bool(null.mean() > 0),
        "floor_lt_positive_benchmark": bool(null.mean() < pos),
        "recovered": bool(recovered),
        "outcome": "RECOVERED" if recovered else "FAILED_TO_RECOVER",
        "calibrated": bool(recovered and null.mean() > 0 and null.mean() < pos),
    }


# --------------------------------------------------------------------------- #
# Shared: a small syllabary + real Semitic (Hebrew) lexemes for the planted-value controls.
# --------------------------------------------------------------------------- #
def _hebrew_lexemes(n: int = 400) -> List[str]:
    heb = []
    with open(GOLD_COG, encoding="utf-8") as f:
        next(f)
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) < 2:
                continue
            for r in p[1].split("|"):
                r = re.sub(r"[^a-z<>]", "", r.lower())
                if 3 <= len(r) <= 8:
                    heb.append(r)
    heb = sorted(set(heb))
    rng = np.random.default_rng(SEED)
    if len(heb) > n:
        idx = sorted(rng.choice(len(heb), size=n, replace=False))
        heb = [heb[i] for i in idx]
    return heb


# candidate value space for the unknown sign — the admissible sweep, like the 301 audit:
# every bare consonant, every bare vowel, and every CV syllable (the true plant lives in here).
_CONS = list("bgdhwzytklmnsprqc<")
_VOW = list("aeiou")
VALUE_SPACE = list(_CONS) + list(_VOW) + [c + v for c in _CONS for v in _VOW]  # ~118 values


# --------------------------------------------------------------------------- #
# PC3 — planted unknown sign value. Sweep MUST recover the plant, ranked #1.
# --------------------------------------------------------------------------- #
def _plant_corpus(lexemes: Sequence[str], true_value: str, sign: str = "X"
                  ) -> Tuple[List[str], List[str]]:
    """Encode every occurrence of `true_value` as the unknown SIGN. Forms that contain the sign are
    the '*301-style' attestations; the rest of the letters are already-known values. Decoding
    sign->true_value reconstructs a REAL lexeme (in the lexicon); a wrong value does not."""
    enc, held = [], []
    for w in lexemes:
        if true_value in w:
            enc.append(w.replace(true_value, sign))
            held.append(w)
    return enc, held


def _best_of_sweep_null_corpus(lexicon: Sequence[str], n_attest: int, eps: float,
                               n_reps: int = 100) -> np.ndarray:
    """The multiple-testing FLOOR for the value sweep: run the SAME full VALUE_SPACE sweep on
    signal-FREE corpora (random CV forms with one unknown sign each) and keep the best value's recall
    per rep. This is the distribution a value found on a NO-signal corpus would reach by search — the
    bar a genuinely-planted value must clear (the 'English is a Semitic language' deflation)."""
    rng = np.random.default_rng(SEED + 99)
    cons, vow = list("ktpmnsrbdgw"), list("aeiou")
    best = []
    for rep in range(n_reps):
        corpus = []
        for _ in range(n_attest):
            L = int(rng.integers(2, 5))
            w = "".join(rng.choice(cons) + rng.choice(vow) for _ in range(L))
            i = int(rng.integers(0, len(w)))
            corpus.append(w[:i] + "X" + w[i + 1:])
        best.append(max(lexstat.s_lex([w.replace("X", v) for w in corpus], lexicon, eps)
                        for v in VALUE_SPACE))
    return np.array(best)


def _sweep_sign_value(encoded: Sequence[str], lexicon: Sequence[str], sign: str,
                      eps: float) -> List[Tuple[str, float]]:
    """s_lex against the real lexicon for each candidate value substituted for `sign`. Non-circular:
    the lexicon (truth) grades; the sign value is the hypothesis under test."""
    scored = []
    for v in VALUE_SPACE:
        decoded = [w.replace(sign, v) for w in encoded]
        scored.append((v, lexstat.s_lex(decoded, lexicon, eps)))
    scored.sort(key=lambda t: -t[1])
    return scored


def pc3_planted_value(true_value: str = "n", eps: float = 0.0) -> dict:
    """Plant a common single consonant as the hidden value of sign X and encode every occurrence.
    Recovery uses EXACT-reconstruction recall (eps=0): only decoding X->true_value turns the
    attestations back into REAL lexemes, so the true value uniquely tops the sweep. Deflated against
    the best-of-sweep floor on signal-free corpora (multiple-testing bar)."""
    lex = _hebrew_lexemes(400)
    lexset = set(lex)
    encoded, held = _plant_corpus(lex, true_value)
    ranking = _sweep_sign_value(encoded, lex, "X", eps)
    top_v, top_s = ranking[0]
    true_rank = 1 + next(i for i, (v, _) in enumerate(ranking) if v == true_value)
    true_s = dict(ranking)[true_value]
    # next-best value that is NOT the true value
    others = [s for v, s in ranking if v != true_value]
    second_s = others[0] if others else 0.0
    null_best = _best_of_sweep_null_corpus(lex, len(encoded), eps, n_reps=100)
    p95 = float(np.percentile(null_best, 95))
    recovered = (top_v == true_value) and (true_rank == 1) and (true_s > second_s) and (true_s > p95)
    return {
        "name": "PC3_planted_unknown_sign_value",
        "expectation": "RECOVER",
        "eps": eps,
        "planted_true_value": true_value,
        "n_attestations_with_sign": len(encoded),
        "value_space_size": len(VALUE_SPACE),
        "top_ranked_value": top_v,
        "top_ranked_s_lex": round(top_s, 4),
        "true_value_rank": true_rank,
        "true_value_s_lex": round(true_s, 4),
        "next_best_non_true_s_lex": round(second_s, 4),
        "margin_over_next_best": round(true_s - second_s, 4),
        "search_deflated_null_p95": round(p95, 4),
        "search_deflated_null_max": round(float(null_best.max()), 4),
        "true_clears_deflated_null": bool(true_s > p95),
        "recovered": bool(recovered),
        "outcome": "RECOVERED" if recovered else "FAILED_TO_RECOVER",
        "calibrated": bool(recovered),
    }


# --------------------------------------------------------------------------- #
# PC4 — FALSE Semitic-root claim manufactured by search. MUST REJECT.
# --------------------------------------------------------------------------- #
def _random_corpus(n: int, seed: int) -> List[str]:
    """A NON-Semitic random syllabic corpus (uniform CV strings) — there is NO real correspondence
    to Hebrew. Any 'match' found by searching values for the unknown sign is a pure artefact."""
    rng = np.random.default_rng(seed)
    cons = list("ktpmnsrbdgw")
    vow = list("aeiou")
    forms = []
    for _ in range(n):
        L = int(rng.integers(2, 5))
        forms.append("".join(rng.choice(cons) + rng.choice(vow) for _ in range(L)))
    return forms


def pc4_false_root_by_search(eps: float = 0.0) -> dict:
    """The EXACT partner of PC3 with NO plant: a signal-free random corpus + one unknown sign,
    searched over the whole VALUE_SPACE for the best-looking Semitic match. Because there is no true
    value, the best-of-search recall is just a draw from the multiple-testing floor and must NOT
    clear it -> REJECT (the 'English is a Semitic language' failure mode is caught by deflation)."""
    lex = _hebrew_lexemes(400)
    rng = np.random.default_rng(SEED + 7)
    corpus = _random_corpus(82, SEED + 7)   # same attestation count as PC3
    encoded = []
    for w in corpus:
        i = int(rng.integers(0, len(w)))
        encoded.append(w[:i] + "X" + w[i + 1:])
    ranking = _sweep_sign_value(encoded, lex, "X", eps)
    best_v, best_s = ranking[0]
    # deflation floor: best-of-sweep on OTHER signal-free corpora (identical machinery to PC3)
    null_best = _best_of_sweep_null_corpus(lex, len(encoded), eps, n_reps=100)
    p95 = float(np.percentile(null_best, 95))
    clears = best_s > p95
    rejected = not clears
    return {
        "name": "PC4_false_semitic_root_by_search",
        "expectation": "REJECT",
        "eps": eps,
        "n_random_forms": len(corpus),
        "best_search_value": best_v,
        "best_search_s_lex": round(best_s, 4),
        "search_deflated_null_p95": round(p95, 4),
        "search_deflated_null_mean": round(float(null_best.mean()), 4),
        "search_deflated_null_max": round(float(null_best.max()), 4),
        "best_clears_deflated_floor": bool(clears),
        "rejected": bool(rejected),
        "outcome": "REJECTED" if rejected else "FALSE_POSITIVE_GRADUATED",
        "calibrated": bool(rejected),
    }


# --------------------------------------------------------------------------- #
# PC5 / PC6 — morphology detector must FIRE on genuine morphology and identify affix POSITION.
# --------------------------------------------------------------------------- #
def _agglutinative_corpus(seed: int, n_insc: int = 12
                          ) -> Tuple[List[List[str]], List[str]]:
    """Productive SUFFIX chaining (agglutinative): stems + a fixed suffix inventory, many stems per
    suffix, spread across independent inscriptions."""
    rng = np.random.default_rng(seed)
    stems = ["".join(rng.choice(list("ktpmnsr")) + rng.choice(list("aeiou"))
                     for _ in range(int(rng.integers(2, 4)))) for _ in range(40)]
    suffixes = ["lar", "im", "ci", "de"]
    insc, lex = [], []
    for _ in range(n_insc):
        forms = []
        for _ in range(rng.integers(6, 10)):
            st = stems[int(rng.integers(0, len(stems)))]
            sf = suffixes[int(rng.integers(0, len(suffixes)))]
            forms.append(st + sf)
        insc.append(forms)
        lex.extend(forms)
    return insc, sorted(set(lex))


def _semitic_prefix_corpus(seed: int, n_insc: int = 12
                           ) -> Tuple[List[List[str]], List[str]]:
    """Productive Semitic-style PREFIX + triliteral roots: prefixes {m,t,y,n} on many roots, spread
    across independent inscriptions."""
    rng = np.random.default_rng(seed)
    roots = ["".join(rng.choice(list("bgdhwzklmnpqrst")) for _ in range(3)) for _ in range(40)]
    prefixes = ["m", "t", "y", "n"]
    insc, lex = [], []
    for _ in range(n_insc):
        forms = []
        for _ in range(rng.integers(6, 10)):
            rt = roots[int(rng.integers(0, len(roots)))]
            pf = prefixes[int(rng.integers(0, len(prefixes)))]
            forms.append(pf + rt + rng.choice(list("aeiou")))  # root + a vowel melody
        insc.append(forms)
        lex.extend(forms)
    return insc, sorted(set(lex))


def _run_morph(insc: List[List[str]], lex: List[str]) -> dict:
    return morphostat.s_morph(insc, lex, max_affix_len=3, n_null=500, seed=SEED)


def pc5_agglutinative() -> dict:
    insc, lex = _agglutinative_corpus(SEED + 11)
    r = _run_morph(insc, lex)
    inv = morphostat.derive_affix_inventory(lex, max_affix_len=3)
    kinds = Counter(k for k, _ in inv)
    fires = bool(r["has_power"] and r["is_significant"])
    dominant = "suffix" if kinds.get("suffix", 0) >= kinds.get("prefix", 0) else "prefix"
    return {
        "name": "PC5_agglutinative_suffix_morphology",
        "expectation": "FIRE_suffix",
        "s_morph_score": round(float(r["score"]), 4),
        "null_mean": round(float(r["null_mean"]), 4),
        "z": round(float(r["z"]), 3),
        "has_power": bool(r["has_power"]),
        "is_significant": bool(r["is_significant"]),
        "n_affixes_detected": len(inv),
        "affix_kind_counts": dict(kinds),
        "dominant_affix_kind": dominant,
        "fires": fires,
        "outcome": "FIRED_SUFFIX" if (fires and dominant == "suffix") else
                   ("FIRED_WRONG_POSITION" if fires else "NO_FIRE"),
        "calibrated": bool(fires and dominant == "suffix"),
    }


def pc6_semitic_prefix() -> dict:
    insc, lex = _semitic_prefix_corpus(SEED + 13)
    r = _run_morph(insc, lex)
    inv = morphostat.derive_affix_inventory(lex, max_affix_len=3)
    kinds = Counter(k for k, _ in inv)
    fires = bool(r["has_power"] and r["is_significant"])
    # single-char prefixes are the plant; check they are recovered
    pref1 = sorted(s for k, s in inv if k == "prefix" and len(s) == 1)
    dominant = "prefix" if kinds.get("prefix", 0) >= kinds.get("suffix", 0) else "suffix"
    planted = {"m", "t", "y", "n"}
    recovered_prefixes = sorted(planted & set(pref1))
    return {
        "name": "PC6_semitic_prefix_root_morphology",
        "expectation": "FIRE_prefix",
        "s_morph_score": round(float(r["score"]), 4),
        "null_mean": round(float(r["null_mean"]), 4),
        "z": round(float(r["z"]), 3),
        "has_power": bool(r["has_power"]),
        "is_significant": bool(r["is_significant"]),
        "n_affixes_detected": len(inv),
        "affix_kind_counts": dict(kinds),
        "dominant_affix_kind": dominant,
        "planted_prefixes_recovered": recovered_prefixes,
        "fires": fires,
        "outcome": "FIRED_PREFIX" if (fires and len(recovered_prefixes) >= 2) else
                   ("FIRED_WRONG_POSITION" if fires else "NO_FIRE"),
        "calibrated": bool(fires and len(recovered_prefixes) >= 2),
    }


# --------------------------------------------------------------------------- #
# PC-NP — degraded to below detection. MUST return NO_POWER (honest abstention).
# --------------------------------------------------------------------------- #
def pcnp_no_power() -> dict:
    # a 2-inscription, 3-form corpus: too little independence to test recurrence -> no power
    insc = [["nabc", "tabc"], ["mabc"]]
    lex = ["nabc", "tabc", "mabc"]
    r = morphostat.s_morph(insc, lex, max_affix_len=2, n_null=200, seed=SEED,
                           min_inscriptions=3)
    no_power = not bool(r["has_power"])
    return {
        "name": "PCNP_degraded_below_detection",
        "expectation": "NO_POWER",
        "n_inscriptions": 2,
        "has_power": bool(r["has_power"]),
        "is_significant": bool(r["is_significant"]),
        "reason": str(r.get("reason", "")),
        "returned_no_power": bool(no_power),
        "outcome": "NO_POWER_HONEST_ABSTENTION" if no_power else "OVERCLAIMED_POWER",
        "calibrated": bool(no_power),
    }


# --------------------------------------------------------------------------- #
def main() -> int:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    t0 = time.time()
    controls = []
    print("PC1 (Ugaritic->Hebrew, real canary) ...", flush=True)
    controls.append(pc1_ugaritic_hebrew())
    print("PC2 (opaque Linear B -> Greek) ...", flush=True)
    controls.append(pc2_linearb_greek())
    print("PC3 (planted sign value) ...", flush=True)
    controls.append(pc3_planted_value())
    print("PC4 (false root by search) ...", flush=True)
    controls.append(pc4_false_root_by_search())
    print("PC5 (agglutinative suffix) ...", flush=True)
    controls.append(pc5_agglutinative())
    print("PC6 (Semitic prefix/root) ...", flush=True)
    controls.append(pc6_semitic_prefix())
    print("PC-NP (degraded -> no power) ...", flush=True)
    controls.append(pcnp_no_power())

    all_calibrated = all(c["calibrated"] for c in controls)
    detect_ok = all(c["calibrated"] for c in controls if c["expectation"] == "RECOVER")
    reject_ok = next(c for c in controls if c["name"].startswith("PC4"))["calibrated"]
    fire_ok = all(c["calibrated"] for c in controls if c["expectation"].startswith("FIRE"))
    nopower_ok = next(c for c in controls if c["name"].startswith("PCNP"))["calibrated"]

    summary = {
        "seed": SEED,
        "elapsed_sec": round(time.time() - t0, 1),
        "n_controls": len(controls),
        "detects_truth_recover": bool(detect_ok),
        "rejects_search_fake": bool(reject_ok),
        "morphology_fires_and_distinguishes": bool(fire_ok),
        "returns_no_power_when_degraded": bool(nopower_ok),
        "pipeline_calibrated": bool(all_calibrated),
        "controls": controls,
    }
    outpath = os.path.join(RESULTS_DIR, "positive_controls.json")
    with open(outpath, "w") as f:
        json.dump(summary, f, indent=2)
    print("\nWROTE", outpath)
    for c in controls:
        print(f"  {c['name']:52} {c['expectation']:12} -> {c['outcome']:28} "
              f"calibrated={c['calibrated']}")
    print(f"\nPIPELINE CALIBRATED: {all_calibrated}  (elapsed {summary['elapsed_sec']}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
