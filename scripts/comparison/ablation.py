#!/usr/bin/env python3
"""ablation.py — the §C.4 LLM-ablation delta (logos comparison-layer §C.4).

Design §C.4 (verbatim intent): "Run the pipeline (a) WITH the LLM proposer and (b) with it REMOVED
(cognate-aware metric + mechanical verdict only). Correspondences surviving in (a) but not (b),
intersected with the literature index, estimate the contamination the LLM is laundering. Large delta
on literature hits => the LLM is a regurgitation engine; demote it to recall-only, never verdict-path."

This module MEASURES proposer behaviour. It is NOT on the verdict path and it never grades:

  * It imports NO scripts.verdict and calls nothing in it (CLAUDE.md invariant #2 — the LLM never
    grades its own outcome; the ablation only compares two PROPOSERS' correspondence sets).
  * The LLM arm is a SIGNAL source (invariant #5, confidence <= 0.75). Here it produces a set of
    candidate (sign, value) correspondences; the mechanical arm produces another; we report their
    delta and its (partial) intersection with the published-literature index. No decision is taken.
  * Everything except the live Ollama call is deterministic + seeded (invariants #4, #6). The
    mechanical arm is a pure function of (forms, hebrew_lexicon, eps); the LLM arm is intentionally
    seed-varied (that variance is the thing being measured).
  * LLM access is local Ollama only, via scripts.comparison.ollama_client (invariant #11). No
    proprietary-cloud SDK, no ANTHROPIC_API_KEY.

Two proposer arms over the SAME held-out Linear A forms:

  ARM (a) llm_propose      — gemma3 via ollama_client.generate (temperature 0.8, seed-varied):
                             ask for a STRICT-JSON partial_map sign->value toward the family.
  ARM (b) mechanical_propose — NO model: nearest-Hebrew-lexeme positional alignment over consonant
                             skeletons, recurrence-gated. See MECHANICAL_INDUCTION for the exact rule.

The headline is :func:`contamination`: of the LLM's literature-matching correspondences, what share
did the mechanical arm FAIL to reproduce (contamination_rate). HONESTY: the seed literature index
(litindex) holds only GORILA syllabic values, so the LLM's NW-Semitic values usually match nothing in
it -> a_lit_hits == 0 -> contamination_rate is UNDEFINED (reported None + a litindex_partial flag),
NOT a misleading 0. The raw delta_only / jaccard / shared are the meaningful v1 signal and are always
reported. See CONTAM_CAVEAT.

    python3 scripts/comparison/ablation.py --no-llm            # mechanical-only (no GPU; CI path)
    python3 scripts/comparison/ablation.py --model gemma3:12b --seeds 30 --n-forms 40
    python3 -m pytest tests/test_ablation.py -q
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from dataclasses import dataclass
from typing import Dict, FrozenSet, List, Optional, Sequence, Set, Tuple

import numpy as np

# make `scripts.comparison` importable when run as a plain script (cron-style), mirroring run_canary.
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from scripts.comparison import lexstat, litindex, ollama_client  # noqa: E402
from scripts.comparison import run_canary  # noqa: E402  (re-uses load_hebrew_reject_set)

# NOTE (invariant #2): scripts.verdict is deliberately NOT imported. The ablation measures the
# proposer; it does not grade. tests/test_ablation.py asserts this absence by grep.

CITATION_DESIGN = (
    "logos comparison-layer §C.4 (LLM-ablation delta: correspondences surviving WITH the LLM but not "
    "WITHOUT it, intersected with the literature index, estimate the contamination the LLM launders; "
    "large delta on literature hits => regurgitation engine, demote to recall-only, never verdict-path)."
)

DEFAULT_MODEL = "gemma3:12b"
DEFAULT_FAMILY = "NW-Semitic"

# Corpus + data artifacts (generated, not hand-written — invariant #12).
INSCRIPTIONS_JSON = os.path.abspath(os.path.join(_ROOT, "corpus", "silver", "inscriptions.json"))

# Linear A / Linear B syllabary ONSETS (the consonant inventory). A sign contributes a consonant to
# its skeleton iff its romanized GORILA value begins with one of these — which cleanly excludes
# pure-vowel signs (A,E,I,O,U,AU) AND the commodity logograms / numerals (VIN->'v', GRA->'g',
# CYP->'c', OLE+...->'o', *NNN->digit) whose onsets are NOT in the syllabary, so no file lookup is
# needed to gate them out.
LINEAR_A_CONSONANTS = frozenset("djkmnpqrstwz")
VOWELS = frozenset("aeiou")

# Minimum number of DISTINCT forms a mechanical correspondence must recur across to count (the
# frequency floor: a single chance alignment is not a "correspondence"). Design §C.4 / §B.1 logic.
MIN_RECURRENCE = 2

MECHANICAL_INDUCTION = (
    "ARM (b), no model, deterministic. (1) Each Linear A form is reduced to a CONSONANT SKELETON: "
    "one character per sign = the leading consonant of that sign's romanized GORILA value, keeping "
    "only signs whose onset is in the Linear A/B syllabary inventory (LINEAR_A_CONSONANTS); pure-"
    "vowel signs, logograms and numerals contribute no character (their onset is not a syllabary "
    "consonant), so the skeleton is consonantal and comparable to the romanized Hebrew consonant "
    "skeletons. A parallel list records which sign produced each skeleton character. (2) For each "
    "form skeleton of length >= 2, its NEAREST Hebrew lexeme is found by normalized edit distance "
    "(lexstat.ned_capped / normalized_edit_distance) within eps (default 0.34); ties broken "
    "lexicographically; no match -> the form contributes nothing. (3) The form's skeleton signs are "
    "aligned POSITIONALLY to the matched Hebrew lexeme's characters (sign_i -> heb_char_i for i in "
    "range(min(len(skel), len(heb)))), emitting (sign_label -> aligned_hebrew_char) correspondences. "
    "(4) RECURRENCE GATE: only correspondences emitted by >= MIN_RECURRENCE (2) DISTINCT forms "
    "survive, so a lone chance alignment never becomes a correspondence. Fully deterministic; the "
    "`seed` argument is accepted for interface symmetry with llm_propose and is not consumed (the "
    "induction has no stochastic step). Empty Hebrew lexicon -> empty set (the arm reports no power)."
)

CONTAM_CAVEAT = (
    "litindex is a NON-EXHAUSTIVE seed (litindex.SEED_NONEXHAUSTIVE) holding only GORILA syllabic "
    "values + the KU-RO/KI-RO accounting readings. The LLM proposes NW-Semitic phonetic values, "
    "which usually match nothing in that seed, so a_lit_hits is frequently 0. When a_lit_hits == 0 "
    "the contamination_rate (= delta_lit_hits / a_lit_hits) is UNDEFINED and is reported as None with "
    "litindex_partial=True — NEVER as a misleading 0. The literature-intersection number is therefore "
    "a PARTIAL (seed-only) lower bound on regurgitation; it strengthens only as the index is expanded "
    "toward completeness (litindex.SEED_NOTE). The raw delta_only / jaccard / n_shared over the two "
    "proposers' correspondence sets are the meaningful v1 structural signal and are reported "
    "regardless of literature coverage."
)


# --------------------------------------------------------------------------- #
# Normalization helpers (sign labels <-> canonical keys; phonetic value cleanup)
# --------------------------------------------------------------------------- #
def _nfkd(s: str) -> str:
    import unicodedata
    return unicodedata.normalize("NFKD", s)


def sign_key(label: str) -> str:
    """Canonical ASCII sign key for a GORILA sign label.

    NFKD-folds subscript variant digits to ASCII (``RA₂`` -> ``RA2``, ``PA₃`` -> ``PA3``), uppercases,
    and keeps only ``[A-Z0-9+*]`` (so ligatures like ``OLE+U`` and undeciphered ``*301`` survive while
    stray combining marks drop). The key is the identity a correspondence is keyed by, in BOTH arms,
    so the two arms and the literature index compare on the same token.
    """
    out = [c for c in _nfkd(label).upper() if c.isalnum() or c in "+*"]
    return "".join(out)


def gorila_value(label: str) -> str:
    """Lowercased romanized GORILA value of a sign label (``RA₂`` -> ``ra2``, ``OLE+U`` -> ``ole+u``).

    This is the 'value' the proposer sees; a form is the '-'-join of these (e.g. ``qe-ra2-u``).
    """
    out = [c for c in _nfkd(label).lower() if c.isalnum() or c in "+*"]
    return "".join(out)


def _norm_value(value: object) -> str:
    """Normalize a proposed phonetic value into a comparable token.

    Lowercases and strips the cosmetic wrappers proposers add (slashes, square/curly/round brackets,
    quotes, asterisks, spaces, dots, hyphens) while PRESERVING the romanized-consonant symbols the
    mechanical arm emits ($ = shin, & = ayin, < = aleph, H/S/T emphatics, ...). Angle brackets are
    NOT stripped precisely because '<' is the aleph symbol. Non-strings -> ''. Applied to BOTH arms so
    a genuine agreement (both say a sign sounds like 'k') registers as a shared correspondence.
    """
    if not isinstance(value, str):
        return ""
    drop = set("/[]{}()⟨⟩\"'*. -")
    s = value.strip().lower()
    return "".join(ch for ch in s if ch not in drop)


# --------------------------------------------------------------------------- #
# Form representation
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Form:
    """One held-out Linear A form (a whole inscription's signs, or a windowed sub-sequence).

    fid    — stable id (inscription id, plus a ``[start:end]`` window marker when windowed).
    signs  — the original GORILA sign LABELS (subscripts preserved), in order.
    """

    fid: str
    signs: Tuple[str, ...]

    @property
    def keys(self) -> Tuple[str, ...]:
        """Canonical ASCII sign keys, in order (the identity a correspondence is keyed by)."""
        return tuple(sign_key(s) for s in self.signs)

    @property
    def surface(self) -> str:
        """The form as the proposer sees it: lowercased GORILA values joined by '-' (``qe-ra2-u``)."""
        return "-".join(gorila_value(s) for s in self.signs)

    def consonant_skeleton(self) -> Tuple[str, Tuple[str, ...]]:
        """(skeleton_string, parallel sign-keys) — one consonant per syllabary sign; see MECHANICAL_INDUCTION."""
        chars: List[str] = []
        owners: List[str] = []
        for label in self.signs:
            g = gorila_value(label)
            onset = g[0] if g and g[0] in LINEAR_A_CONSONANTS else None
            if onset is not None:
                chars.append(onset)
                owners.append(sign_key(label))
        return "".join(chars), tuple(owners)


def build_form(fid: str, signs: Sequence[str]) -> Form:
    """Public constructor (used by tests + loaders) — a Form from an id and a sign-label sequence."""
    return Form(fid=str(fid), signs=tuple(signs))


# --------------------------------------------------------------------------- #
# Data loaders (deterministic, seeded sampling)
# --------------------------------------------------------------------------- #
def _load_inscriptions(path: str = INSCRIPTIONS_JSON) -> List[dict]:
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data if isinstance(data, list) else data.get("inscriptions", [])


def heldout_forms(n: int, seed: int, *, window: int = 6, min_signs: int = 2,
                  path: str = INSCRIPTIONS_JSON) -> List[Form]:
    """Sample ``n`` distinct Linear A forms from the silver corpus (deterministic given ``seed``).

    The pool is every inscription with >= ``min_signs`` signs (single-sign records are not "forms"),
    sorted by id for a stable index space; ``numpy.default_rng(seed)`` draws ``n`` distinct indices
    without replacement. An inscription longer than ``window`` is reduced to a ``window``-sign
    sub-sequence at a seeded offset (so long admin lists become bounded forms comparable in length to
    Hebrew lexemes); shorter inscriptions are kept whole. Returns at most ``n`` forms (the whole
    eligible pool if it is smaller than ``n``).
    """
    insc = _load_inscriptions(path)
    pool = sorted((r for r in insc if len(r.get("signs", [])) >= min_signs),
                  key=lambda r: str(r.get("id", "")))
    if not pool:
        return []
    rng = np.random.default_rng(seed)
    k = min(n, len(pool))
    idx = sorted(int(i) for i in rng.choice(len(pool), size=k, replace=False))
    forms: List[Form] = []
    for i in idx:
        rec = pool[i]
        signs = list(rec.get("signs", []))
        fid = str(rec.get("id", f"_{i}"))
        if len(signs) > window:
            offset = int(rng.integers(0, len(signs) - window + 1))
            signs = signs[offset:offset + window]
            fid = f"{fid}[{offset}:{offset + window}]"
        forms.append(build_form(fid, signs))
    return forms


def hebrew_lexicon() -> Tuple[FrozenSet[str], str]:
    """The candidate Semitic lexicon: ETCBC/bhsa romanized consonant skeletons (run_canary loader).

    Returns ``(frozenset_of_skeletons, provenance)``. Degrades gracefully to ``(frozenset(), "")``
    when the bhsa clone is absent — the mechanical arm then reports no power.
    """
    return run_canary.load_hebrew_reject_set()


# --------------------------------------------------------------------------- #
# ARM (a) — the LLM proposer (gemma3 via ollama_client)  [SIGNAL, conf <= 0.75]
# --------------------------------------------------------------------------- #
_PROMPT_TEMPLATE = """You are assisting a Linear A decipherment research harness. Below are {n} \
held-out Linear A inscriptions, each given as a sequence of GORILA sign names joined by '-'. \
Working ONLY from these forms, propose a partial decipherment toward {family} (cognate vocabulary \
and sign sound-values).

Held-out forms:
{forms_block}

Return STRICT JSON ONLY (a single JSON object, optionally inside one ```json fence; no other prose) \
with exactly these keys:
{{
  "partial_map": {{ "<SIGN_NAME>": "<proposed phonetic value, e.g. a consonant or CV syllable>" }},
  "cognates": [ {{ "form": "<one form above>", "lexeme": "<{family} lexeme>", "gloss": "<meaning>" }} ],
  "prediction": "<one falsifiable claim about a held-out inscription NOT listed above>"
}}
Use the EXACT sign names shown (e.g. "QE", "RA2"). Only include signs that appear above. Keep \
partial_map to your most confident correspondences."""


def build_prompt(forms: Sequence[Form], family: str = DEFAULT_FAMILY) -> str:
    """Render the proposer prompt: the held-out forms by their (canonical) sign names + the JSON ask."""
    lines = [f"  FORM_{i + 1}: {'-'.join(f.keys)}" for i, f in enumerate(forms)]
    return _PROMPT_TEMPLATE.format(n=len(forms), family=family, forms_block="\n".join(lines))


def parse_proposal(text: object, valid_signs: Set[str]) -> Set[Tuple[str, str]]:
    """Parse an LLM reply into a set of (canonical_sign_key, normalized_value) correspondences.

    Robust: garbage / missing partial_map / non-string values yield an empty set, never an error.
    Only keys that normalize to a sign actually shown to the model (``valid_signs``) are kept, so the
    proposer cannot invent signs.
    """
    obj = ollama_client.extract_json(text)
    if not isinstance(obj, dict):
        return set()
    pm = obj.get("partial_map")
    if not isinstance(pm, dict):
        return set()
    out: Set[Tuple[str, str]] = set()
    for raw_sign, raw_val in pm.items():
        sk = sign_key(str(raw_sign))
        if sk not in valid_signs:
            continue
        val = _norm_value(raw_val)
        if val:
            out.add((sk, val))
    return out


def llm_propose(forms: Sequence[Form], model: str, seed: int, *, family: str = DEFAULT_FAMILY,
                host: Optional[str] = None, timeout: int = 180,
                log_path: Optional[str] = None) -> Set[Tuple[str, str]]:
    """ARM (a): ask the local LLM (gemma3 via Ollama) for a partial_map and parse it to a corr. set.

    Sampling is enabled (temperature 0.8, options seed=``seed``) so distinct seeds explore distinct
    proposals — the seed-variance is exactly what the ablation measures. The call is logged
    (privacy-preserving sha, never the prompt text) and a dead/garbled call contributes an EMPTY
    proposal without crashing the batch (invariant: signals fail closed).
    """
    if not forms:
        return set()
    prompt = build_prompt(forms, family)
    res = ollama_client.generate(model, prompt, options={"temperature": 0.8, "seed": int(seed)},
                                 timeout=timeout, host=host)
    try:
        ollama_client.log_call(res, model=model, prompt=prompt, log_path=log_path)
    except Exception:
        pass  # observability is best-effort; never let logging crash a proposal
    valid = {sk for f in forms for sk in f.keys}
    return parse_proposal(res.get("response", ""), valid)


# --------------------------------------------------------------------------- #
# ARM (b) — the mechanical proposer (no LLM, deterministic)
# --------------------------------------------------------------------------- #
def _nearest_lexeme(skel: str, heb_by_len: Dict[int, List[str]], eps: float) -> Optional[str]:
    """Nearest Hebrew lexeme to ``skel`` by normalized edit distance, within ``eps``; None if none.

    Only length-plausible buckets are scanned (NED <= eps implies the length gap is within the edit
    cap). Ties on distance are broken lexicographically for determinism.
    """
    best: Optional[str] = None
    best_d = eps + 1.0
    Lf = len(skel)
    for L, bucket in heb_by_len.items():
        m = max(Lf, L)
        if abs(Lf - L) > int(np.floor(eps * m)):
            continue
        for cand in bucket:
            if not lexstat.ned_capped(skel, cand, eps):
                continue
            d = lexstat.normalized_edit_distance(skel, cand)
            if d < best_d or (d == best_d and (best is None or cand < best)):
                best_d = d
                best = cand
    return best


def mechanical_propose(forms: Sequence[Form], hebrew_lexicon: FrozenSet[str], seed: int, *,
                       eps: float = 0.34,
                       min_recurrence: int = MIN_RECURRENCE) -> Set[Tuple[str, str]]:
    """ARM (b): cognate-aware correspondence induction WITHOUT a model. See MECHANICAL_INDUCTION.

    Deterministic given ``forms`` (and ``eps``); ``seed`` is accepted for interface symmetry with
    llm_propose and is not consumed. Empty ``hebrew_lexicon`` -> empty set (no power).
    """
    if not hebrew_lexicon:
        return set()
    heb_by_len: Dict[int, List[str]] = {}
    for w in hebrew_lexicon:
        heb_by_len.setdefault(len(w), []).append(w)

    # correspondence -> set of DISTINCT form ids that emitted it (the recurrence ledger)
    ledger: Dict[Tuple[str, str], Set[str]] = {}
    for f in forms:
        skel, owners = f.consonant_skeleton()
        if len(skel) < 2:
            continue
        best = _nearest_lexeme(skel, heb_by_len, eps)
        if best is None:
            continue
        for i in range(min(len(skel), len(best))):
            corr = (owners[i], _norm_value(best[i]))
            if not corr[1]:
                continue
            ledger.setdefault(corr, set()).add(f.fid)

    return {corr for corr, fids in ledger.items() if len(fids) >= min_recurrence}


# --------------------------------------------------------------------------- #
# DELTA + CONTAMINATION (design §C.4 headline)
# --------------------------------------------------------------------------- #
def _lit_hit(corr: Tuple[str, str], index: Sequence["litindex.LitClaim"]) -> bool:
    """True iff a (sign, value) correspondence reproduces a PUBLISHED sign-value (litindex §C.1).

    Matches on sign-atomic overlap AND value equality (litindex.literature_match), so it fires only
    when the proposer's value coincides with a published value for that sign — the precise §C.4
    "intersected with the literature index" semantics.
    """
    sign, value = corr
    return litindex.literature_match(sign, index, proposed_value=value)


def contamination(a_set: Set[Tuple[str, str]], b_set: Set[Tuple[str, str]],
                  index: Sequence["litindex.LitClaim"]) -> Dict[str, object]:
    """The §C.4 delta + contamination report between ARM (a) [LLM] and ARM (b) [mechanical].

    Reports n_a, n_b, n_shared = |a∩b|, jaccard, delta_only = |a\\b| (the LLM-only correspondences),
    a_lit_hits = |a ∩ literature|, delta_lit_hits = |(a\\b) ∩ literature|, and

        contamination_rate = delta_lit_hits / a_lit_hits

    the share of the LLM's literature-matching correspondences that the mechanical arm did NOT find
    (i.e. the literature signal the LLM is laundering on its own). HONESTY (CONTAM_CAVEAT): when
    a_lit_hits == 0 the rate is UNDEFINED and reported as None with litindex_partial=True, never a
    misleading 0. A supplementary SIGN-LEVEL overlap is also reported because the two arms use
    different value vocabularies (LLM phonetic values vs mechanical romanized-Hebrew chars), so the
    correspondence-level jaccard can understate agreement.
    """
    a = set(a_set)
    b = set(b_set)
    shared = a & b
    union = a | b
    delta = a - b  # LLM-only correspondences

    a_lit = sorted(c for c in a if _lit_hit(c, index))
    delta_lit = sorted(c for c in delta if _lit_hit(c, index))
    a_lit_hits = len(a_lit)
    delta_lit_hits = len(delta_lit)

    if a_lit_hits == 0:
        contamination_rate: Optional[float] = None
    else:
        contamination_rate = delta_lit_hits / a_lit_hits
    # The literature index is a NON-EXHAUSTIVE seed, so ANY contamination figure here — None OR a
    # finite rate — is a partial, seed-only LOWER BOUND. Flag it whenever the index is non-exhaustive
    # (the prior code set this False for a finite rate, which falsely implied a complete index for
    # that measurement, contradicting CONTAM_CAVEAT).
    litindex_partial = bool(litindex.SEED_NONEXHAUSTIVE) or a_lit_hits == 0

    # supplementary sign-level overlap (value-vocabulary-agnostic)
    a_signs = {s for s, _ in a}
    b_signs = {s for s, _ in b}
    sign_union = a_signs | b_signs

    return {
        "n_a": len(a),
        "n_b": len(b),
        "n_shared": len(shared),
        "jaccard": (len(shared) / len(union)) if union else 0.0,
        "delta_only": len(delta),
        "a_lit_hits": a_lit_hits,
        "delta_lit_hits": delta_lit_hits,
        "contamination_rate": contamination_rate,
        "litindex_partial": litindex_partial,
        "seed_nonexhaustive": bool(litindex.SEED_NONEXHAUSTIVE),
        "litindex_caveat": CONTAM_CAVEAT,
        "a_lit_correspondences": [list(c) for c in a_lit],
        "delta_lit_correspondences": [list(c) for c in delta_lit],
        "sign_level": {
            "n_a_signs": len(a_signs),
            "n_b_signs": len(b_signs),
            "n_shared_signs": len(a_signs & b_signs),
            "jaccard_signs": (len(a_signs & b_signs) / len(sign_union)) if sign_union else 0.0,
        },
    }


# --------------------------------------------------------------------------- #
# run_ablation — aggregate over seeds
# --------------------------------------------------------------------------- #
def _dist(vals: Sequence[float]) -> Dict[str, object]:
    arr = np.asarray(list(vals), dtype=float)
    if arr.size == 0:
        return {"n": 0, "mean": None, "std": None, "min": None, "p50": None, "max": None}
    return {
        "n": int(arr.size),
        "mean": float(arr.mean()),
        "std": float(arr.std()),
        "min": float(arr.min()),
        "p50": float(np.percentile(arr, 50)),
        "max": float(arr.max()),
    }


def _survival(counter: Counter) -> List[dict]:
    """Per-correspondence survival, most-persistent first (count desc, then sign, then value)."""
    rows = [{"sign": s, "value": v, "seeds": c} for (s, v), c in counter.items()]
    rows.sort(key=lambda r: (-r["seeds"], r["sign"], r["value"]))
    return rows


def run_ablation(model: str, n_seeds: int, n_forms: int, seed0: int, *, with_llm: bool = True,
                 family: str = DEFAULT_FAMILY, eps: float = 0.34, window: int = 6,
                 host: Optional[str] = None, timeout: int = 180,
                 log_path: Optional[str] = None) -> Dict[str, object]:
    """Run the §C.4 ablation over ``n_seeds`` seeds (``seed0 .. seed0+n_seeds-1``) and aggregate.

    For each seed: sample the SAME held-out forms for both arms; run ARM (b) [mechanical,
    deterministic] and, when ``with_llm``, ARM (a) [LLM, seed-varied]; score :func:`contamination`.
    Aggregates the jaccard / delta_only / contamination_rate distributions across seeds, and the
    per-correspondence SURVIVAL (how many seeds each (sign,value) appears in) for each arm separately.
    """
    heb, heb_src = hebrew_lexicon()
    index = litindex.load_index()

    per_seed: List[dict] = []
    a_surv: Counter = Counter()
    b_surv: Counter = Counter()

    for s in range(seed0, seed0 + n_seeds):
        forms = heldout_forms(n_forms, s, window=window)
        b_set = mechanical_propose(forms, heb, s, eps=eps)
        # ARM (a) per-seed exception isolation: a single bad call (even one that violates generate()'s
        # documented no-raise contract) must NOT abort the whole batch or lose accumulated survival.
        a_set: Set[Tuple[str, str]] = set()
        llm_error: Optional[str] = None
        if with_llm:
            try:
                a_set = llm_propose(forms, model, s, family=family, host=host,
                                    timeout=timeout, log_path=log_path)
            except Exception as exc:                       # noqa: BLE001 — isolate the seed, keep going
                llm_error = str(exc)[:200]
        con = contamination(a_set, b_set, index)
        per_seed.append({
            "seed": s,
            "n_forms": len(forms),
            "n_a": con["n_a"], "n_b": con["n_b"], "n_shared": con["n_shared"],
            "jaccard": con["jaccard"], "delta_only": con["delta_only"],
            "a_lit_hits": con["a_lit_hits"], "delta_lit_hits": con["delta_lit_hits"],
            "contamination_rate": con["contamination_rate"],
            "litindex_partial": con["litindex_partial"],
            "seed_nonexhaustive": con["seed_nonexhaustive"],
            "llm_error": llm_error,
            "sign_level": con["sign_level"],
        })
        for c in a_set:
            a_surv[c] += 1
        for c in b_set:
            b_surv[c] += 1

    crates = [p["contamination_rate"] for p in per_seed if p["contamination_rate"] is not None]
    aggregate = {
        "jaccard": _dist([p["jaccard"] for p in per_seed]),
        "delta_only": _dist([p["delta_only"] for p in per_seed]),
        "n_a": _dist([p["n_a"] for p in per_seed]),
        "n_b": _dist([p["n_b"] for p in per_seed]),
        "a_lit_hits": _dist([p["a_lit_hits"] for p in per_seed]),
        "delta_lit_hits": _dist([p["delta_lit_hits"] for p in per_seed]),
        "contamination_rate": _dist(crates),
        "n_seeds_with_defined_contamination_rate": len(crates),
        "jaccard_signs": _dist([p["sign_level"]["jaccard_signs"] for p in per_seed]),
    }

    return {
        "citation": CITATION_DESIGN,
        "model": model,
        "family": family,
        "with_llm": bool(with_llm),
        "params": {"n_seeds": n_seeds, "n_forms": n_forms, "seed0": seed0, "eps": eps,
                   "window": window, "min_recurrence": MIN_RECURRENCE},
        "hebrew_lexicon_source": heb_src,
        "n_hebrew_skeletons": len(heb),
        "mechanical_power": bool(heb),
        "mechanical_induction": MECHANICAL_INDUCTION,
        "litindex_caveat": CONTAM_CAVEAT,
        "seed_nonexhaustive": bool(litindex.SEED_NONEXHAUSTIVE),
        "n_literature_claims": len(index),
        "aggregate": aggregate,
        "survival_arm_a_llm": _survival(a_surv),
        "survival_arm_b_mechanical": _survival(b_surv),
        "per_seed": per_seed,
    }


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _default_out(model: str, family: str) -> str:
    safe = "".join(c if c.isalnum() or c in "-._" else "_" for c in f"{model}-{family}")
    return os.path.join(_ROOT, "runtime", "ablation", f"{safe}.json")


def _summary(report: Dict[str, object]) -> str:
    agg = report["aggregate"]
    j = agg["jaccard"]
    d = agg["delta_only"]
    cr = agg["contamination_rate"]

    def _m(stat):
        return "n/a" if stat["mean"] is None else f"{stat['mean']:.3f}"

    lines = [
        "=" * 78,
        "LLM-ABLATION DELTA  (logos comparison-layer §C.4)",
        "=" * 78,
        f"model={report['model']}  family={report['family']}  with_llm={report['with_llm']}  "
        f"seeds={report['params']['n_seeds']}  n_forms={report['params']['n_forms']}  "
        f"eps={report['params']['eps']}",
        f"Hebrew lexicon: {report['n_hebrew_skeletons']} skeletons  "
        f"(power={report['mechanical_power']})  src={report['hebrew_lexicon_source'] or 'ABSENT'}",
        f"jaccard(a,b)      mean={_m(j)}  (correspondence-level; arms use different value vocab)",
        f"jaccard_signs     mean={_m(agg['jaccard_signs'])}  (sign-level overlap)",
        f"delta_only (a\\b)  mean={_m(d)}  (LLM-only correspondences)",
        f"contamination_rate mean={_m(cr)}  over "
        f"{agg['n_seeds_with_defined_contamination_rate']}/{report['params']['n_seeds']} seeds "
        f"with a_lit_hits>0",
        "LITINDEX CAVEAT: " + report["litindex_caveat"],
        f"survival: arm_a (LLM) {len(report['survival_arm_a_llm'])} distinct corr; "
        f"arm_b (mech) {len(report['survival_arm_b_mechanical'])} distinct corr",
    ]
    return "\n".join(lines)


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="C.4 LLM-ablation delta (logos comparison-layer §C.4)")
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--family", default=DEFAULT_FAMILY)
    p.add_argument("--seeds", type=int, default=30, help="number of seeds (seed0 .. seed0+seeds-1)")
    p.add_argument("--n-forms", type=int, default=40, help="held-out forms sampled per seed")
    p.add_argument("--seed0", type=int, default=0)
    p.add_argument("--eps", type=float, default=0.34, help="normalized-edit-distance match radius")
    p.add_argument("--window", type=int, default=6, help="max signs per windowed form")
    p.add_argument("--no-llm", action="store_true",
                   help="mechanical-only (no GPU; tests/CI) — ARM (a) is empty")
    p.add_argument("--host", default=None, help="Ollama host (default $OLLAMA_URL or the gpu host)")
    p.add_argument("--timeout", type=int, default=180)
    p.add_argument("--out", default=None, help="output JSON (default runtime/ablation/<model>-<family>.json)")
    p.add_argument("--print-json", action="store_true", help="print the full JSON report to stdout")
    args = p.parse_args(argv)

    report = run_ablation(
        args.model, args.seeds, args.n_forms, args.seed0,
        with_llm=not args.no_llm, family=args.family, eps=args.eps, window=args.window,
        host=args.host, timeout=args.timeout,
    )

    out = args.out or _default_out(args.model, args.family)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False, default=str)
        fh.write("\n")

    if args.print_json:
        print(json.dumps(report, indent=2, ensure_ascii=False, default=str))
    else:
        print(_summary(report))
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
