#!/usr/bin/env python3
"""lvirgin.py — the §C.2 L_VIRGIN GENERALIZATION TEST (logos comparison-layer §C.2).

Design §C.2 (verbatim intent): "Partition signs into L_known (any published proposal exists) and
L_virgin (none). A real correspondence *system* forces values on L_virgin signs too. **Discovery
claims may rest only on L_virgin held-out success.** Regurgitation can only return what's in the
training corpus; it cannot predict the untouched signs."

THE COMPLEMENT TO THE CONTAMINATION TABLE. The §C.4 per-word contamination table already showed that
qwen MEMORIZES the famous published Linear A readings (KU-RO/kull, A-SA-SA-RA-ME/asherah, ...).
L_virgin asks the *opposite* question: does qwen impute a CONSISTENT (non-random) phonetic value for
the GORILA *-series syllabograms — signs that have NO established published value, so qwen could not
have memorized one? Cross-seed CONSISTENCY on a virgin sign is evidence of SOMETHING beyond pure
table-lookup (reasoning OR a stable hallucination); cross-seed RANDOMNESS is the signature of pure
memorization (nothing to recall ⇒ a fresh guess each seed).

*** CRITICAL HONESTY (this is the whole point of the file — read it before touching anything) ***
CONSISTENCY IS NON-RANDOM IMPUTATION, **NOT VERIFIED CORRECTNESS.** There is NO ground truth for an
L_virgin sign value — by definition no published reading exists — so this test can NEVER show that
qwen is RIGHT about a virgin sign, only that it is SELF-CONSISTENT across independent seeds beyond
what a random draw from its own output distribution would give. A near-zero known-minus-virgin
consistency gap means qwen imputes virgin signs as non-randomly as it recites known ones (structure /
reasoning present — correctness UNKNOWN); a large positive gap means qwen is consistent ONLY where the
value is published (regurgitation-dominated). Either way the number carries NO verdict weight: the LLM
is a SIGNAL (CLAUDE.md invariants #2/#5, confidence ≤ 0.75), never on the verdict path. This module
imports NO scripts.verdict and grades nothing.

WHY A PURPOSE-BUILT RUN (not a re-read of the ablation output). The genuine *-series virgin
syllabograms are RARE (median corpus frequency ~4), so in a normal §C.4 ablation each virgin sign
lands in ~1 sampled seed (n=1) and no cross-seed consistency is estimable. The fix here: PROBE every
target sign in EVERY seed, each in a FIXED real-inscription context window, so each sign accrues
~n_seeds independent value-proposals and a modal-share consistency becomes measurable. The fixed
per-sign window isolates qwen's value-consistency for that sign from context variation.

PARTITION (from corpus/silver/signs_ontology.json, by sign CLASS — independent of the litindex):
  * L_known  = class 'syllabogram-AB'     (homomorphic AB signs that carry a conventional GORILA /
               Linear-B value qwen can have memorized) — the memorization-positive control.
  * L_virgin = class 'syllabogram-Aonly'  (the GORILA *-series, "undeciphered … no established
               value") — the untouched signs.
  * EXCLUDED ENTIRELY: logogram / fraction / numeral / uncertain — non-phonetic signs qwen must not
    be scored on. Counts of what was excluded are reported.

CONSISTENCY METRIC (the sample-size control is the load-bearing part). Per target sign:
  n            = number of seeds in which qwen returned a value for that sign,
  modal_share  = (count of the single most-frequent value) / n,
  expected     = Monte-Carlo E[modal_share] of n i.i.d. draws from qwen's POOLED GLOBAL value
                 distribution (its empirical output marginal over all signs/seeds),
  excess       = modal_share − expected.
The `expected` term is essential: a sign seen in only n=1 seed has modal_share == 1.0 mechanically,
so raw modal_share rewards low coverage. `excess` measures concentration BEYOND a random draw of the
same size, so an n=1 sign gets excess ≈ 0, not a spurious 1.0. Aggregated as mean excess per class;
the HEADLINE is the known−virgin excess gap plus a label-shuffle PERMUTATION p-value, with a matched-n
robustness check (signs with n ≥ n_min only) so the comparison is not driven by coverage differences.

    python3 scripts/comparison/lvirgin.py --model qwen2.5:72b --seeds 40
    python3 -m pytest tests/test_lvirgin.py -q
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import Counter
from typing import Dict, List, Mapping, Optional, Sequence, Set, Tuple

import numpy as np

# make `scripts.comparison` importable when run as a plain script (cron-style), mirroring ablation.
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from scripts.comparison import ablation  # noqa: E402  (build_form, llm_propose, sign_key, Form, ...)

# NOTE (invariant #2): scripts.verdict is deliberately NOT imported. L_virgin MEASURES a proposer
# signal; it never grades. tests/test_lvirgin.py asserts this absence by grep.

CITATION_DESIGN = (
    "logos comparison-layer §C.2 (L_known/L_virgin partition: 'Discovery claims may rest only on "
    "L_virgin held-out success — regurgitation can only return what is in the literature, it cannot "
    "predict the untouched signs'). This test measures cross-seed CONSISTENCY of the LLM proposer's "
    "imputed values on virgin signs as NON-RANDOM IMPUTATION, never as verified correctness."
)

DEFAULT_MODEL = "qwen2.5:72b"

ONTOLOGY_JSON = os.path.abspath(os.path.join(_ROOT, "corpus", "silver", "signs_ontology.json"))
INSCRIPTIONS_JSON = os.path.abspath(os.path.join(_ROOT, "corpus", "silver", "inscriptions.json"))

# §C.2 partition by ontology CLASS.
KNOWN_CLASS = "syllabogram-AB"        # conventional GORILA / Linear-B value (memorizable) -> L_known
VIRGIN_CLASS = "syllabogram-Aonly"    # the *-series, "no established value"               -> L_virgin
# Everything else is non-phonetic and must NOT be scored (qwen has no syllabic value to impute).
EXCLUDED_CLASSES = ("logogram", "fraction", "numeral", "uncertain")

HONESTY = (
    "CONSISTENCY IS NON-RANDOM IMPUTATION, NOT VERIFIED CORRECTNESS. There is NO ground truth for an "
    "L_virgin (GORILA *-series) sign value, so this test can NEVER show qwen is RIGHT about a virgin "
    "sign — only whether qwen imputes the SAME value across independent seeds MORE than a random draw "
    "from its own global value distribution would. Cross-seed consistency on virgin signs is evidence "
    "of something BEYOND pure lookup (reasoning OR a stable hallucination); it is NOT evidence of a "
    "correct reading and carries NO verdict weight (CLAUDE.md #2/#5: the LLM is a signal ≤0.75, never "
    "on the verdict path). gap≈0 / p>0.05 ⇒ virgin imputed as non-randomly as known (structure / "
    "reasoning present, correctness UNKNOWN); gap≫0 ⇒ qwen is consistent ONLY where the value is "
    "memorizable (regurgitation-dominated). NEVER report this as a decipherment of any sign."
)

CONSISTENCY_METRIC = (
    "Per sign: modal_share = max value-count / n (n = seeds that returned a value), with the "
    "sample-size control excess = modal_share − E[modal_share], where E is the Monte-Carlo expected "
    "modal share of n i.i.d. draws from qwen's pooled GLOBAL value distribution (so an n=1 sign gets "
    "excess ≈ 0, not a spurious 1.0). Aggregated as mean excess per class; headline = known−virgin "
    "excess gap + a label-shuffle permutation p-value (≥2000 perms) + a matched-n (n ≥ n_min) "
    "robustness check + mean-n coverage per class."
)


# --------------------------------------------------------------------------- #
# Loaders
# --------------------------------------------------------------------------- #
def load_ontology(path: str = ONTOLOGY_JSON) -> Dict[str, dict]:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_inscriptions(path: str = INSCRIPTIONS_JSON) -> List[dict]:
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data if isinstance(data, list) else data.get("inscriptions", [])


# --------------------------------------------------------------------------- #
# §C.2 partition (by ontology CLASS)
# --------------------------------------------------------------------------- #
def partition_by_class(ontology: Mapping[str, dict], index=None) -> Dict[str, object]:
    """Partition the ontology into L_known / L_virgin by sign CLASS; report exclusions (§C.2).

    L_known  = signs of class ``syllabogram-AB`` (conventional GORILA value — memorizable).
    L_virgin = signs of class ``syllabogram-Aonly`` (the *-series; "no established value") **MINUS any
    sign that carries a published litindex proposal** (e.g. Di Mino's quarantined ``*301``=/na/): such a
    sign COULD have been memorized, so by §C.2's definition ("L_virgin = no published proposal exists")
    it is NOT literature-virgin and is quarantined out of the clean comparison (reported under
    ``lit_quarantined``). EXCLUDED = logogram / fraction / numeral / uncertain (non-phonetic — never
    scored). Sign labels are canonicalized with :func:`ablation.sign_key` so they compare on the same
    token the proposer keys its partial_map by. Returns sets + ``excluded``/``lit_quarantined`` for audit.
    """
    from scripts.comparison import litindex
    if index is None:
        index = litindex.load_index()
    lit_known = {ablation.sign_key(s) for s in litindex.known_signs(index)}

    known: Set[str] = set()
    virgin: Set[str] = set()
    excluded: Counter = Counter()
    excluded_signs: Dict[str, List[str]] = {}
    for label, meta in ontology.items():
        cls = (meta or {}).get("class")
        key = ablation.sign_key(label)
        if cls == KNOWN_CLASS:
            known.add(key)
        elif cls == VIRGIN_CLASS:
            virgin.add(key)
        else:
            excluded[str(cls)] += 1
            excluded_signs.setdefault(str(cls), []).append(label)
    # §C.2 integrity: an A-only sign that the litindex already records a published proposal for is NOT
    # virgin (it could be memorized) — quarantine it out of L_virgin so it can never count as 'reasoning'.
    lit_quarantined = sorted(s for s in virgin if s in lit_known)
    virgin -= set(lit_quarantined)
    return {
        "L_known": known,
        "L_virgin": virgin,
        "excluded": dict(excluded),
        "excluded_signs": {k: sorted(v) for k, v in excluded_signs.items()},
        "lit_quarantined": lit_quarantined,
        "known_class": KNOWN_CLASS,
        "virgin_class": VIRGIN_CLASS,
    }


# --------------------------------------------------------------------------- #
# Probe forms — a FIXED real-inscription context window per target sign
# --------------------------------------------------------------------------- #
def _sign_seed(seed: int, key: str) -> int:
    """A stable (cross-process) integer seed for a (run-seed, sign) pair.

    Python's built-in ``hash`` is salted, so a reproducible per-sign window needs a content hash.
    """
    h = hashlib.sha256(f"{int(seed)}|{key}".encode("utf-8")).hexdigest()
    return int(h[:16], 16)


def _build_occurrence_index(inscriptions: Sequence[dict]) -> Dict[str, List[Tuple[int, int]]]:
    """Map each canonical sign key -> list of (inscription_index, position) where it occurs BARE.

    Only inscriptions with >= 2 signs are indexed (a single-sign record has no context window).
    Positions are recorded in corpus order (deterministic). A target sign that appears ONLY inside a
    ligature token (e.g. ``*316+KI``) gets no bare entry here, so it is reported as no-coverage rather
    than silently probed under a different token.
    """
    idx: Dict[str, List[Tuple[int, int]]] = {}
    for ri, rec in enumerate(inscriptions):
        signs = rec.get("signs", [])
        if len(signs) < 2:
            continue
        for pos, tok in enumerate(signs):
            idx.setdefault(ablation.sign_key(tok), []).append((ri, pos))
    return idx


def _window_for_sign(target_key: str, inscriptions: Sequence[dict],
                     occ_index: Mapping[str, List[Tuple[int, int]]],
                     n_context: int, seed: int) -> Optional[ablation.Form]:
    """A FIXED real-context :class:`ablation.Form` containing ``target_key`` (deterministic), or None.

    One occurrence is chosen deterministically (rng seeded by the (seed, sign) content hash) from the
    sign's bare occurrences, and an ``n_context``-sign window CONTAINING that occurrence is sliced out
    of the real inscription. The same window is produced every call (so it is identical across every
    proposer seed — value-consistency is isolated from context variation). None when the sign never
    occurs bare in a >=2-sign inscription (no real context ⇒ honest skip, see coverage reporting).
    """
    occ = occ_index.get(target_key)
    if not occ:
        return None
    rng = np.random.default_rng(_sign_seed(seed, target_key))
    ri, pos = occ[int(rng.integers(len(occ)))]
    signs = list(inscriptions[ri].get("signs", []))
    half = n_context // 2
    start = max(0, pos - half)
    end = min(len(signs), start + n_context)
    start = max(0, end - n_context)            # shift left if the window ran off the right edge
    window = signs[start:end]
    fid = f"{inscriptions[ri].get('id', f'_{ri}')}:{target_key}[{start}:{end}]"
    return ablation.build_form(fid, window)


def target_probe_forms(ontology: Mapping[str, dict], inscriptions: Sequence[dict], *,
                       n_known: int, n_virgin: int, n_context: int = 6,
                       seed: int = 0) -> List[Tuple[str, ablation.Form]]:
    """Build ``(target_sign_key, Form)`` probes: a fixed real-context window per target sign (§C.2).

    Targets are the L_virgin *-series syllabograms PLUS a comparison set of L_known AB syllabograms
    (the memorization control). Candidates are taken in deterministic (sorted) order; a candidate with
    no real bare context (:func:`_window_for_sign` is None) is SKIPPED (reported by
    :func:`coverage_report`); selection stops at ``n_known`` known and ``n_virgin`` virgin covered
    signs to keep the single prompt reasonable. Returns the known probes first, then the virgin ones.
    """
    part = partition_by_class(ontology)
    occ_index = _build_occurrence_index(inscriptions)

    def _select(keys: Set[str], cap: int) -> List[Tuple[str, ablation.Form]]:
        out: List[Tuple[str, ablation.Form]] = []
        for sk in sorted(keys):
            if len(out) >= cap:
                break
            form = _window_for_sign(sk, inscriptions, occ_index, n_context, seed)
            if form is not None:
                out.append((sk, form))
        return out

    known_pairs = _select(part["L_known"], n_known)
    virgin_pairs = _select(part["L_virgin"], n_virgin)
    return known_pairs + virgin_pairs


def coverage_report(ontology: Mapping[str, dict], inscriptions: Sequence[dict], *,
                    n_context: int = 6, seed: int = 0) -> Dict[str, object]:
    """Per-class context coverage of the partition (which signs have / lack a real window) — honesty.

    Reports, for each class, the candidate count, how many have a real bare context window, and the
    signs SKIPPED for having none (e.g. *-series signs that occur only inside ligatures). Reproduces
    the same windows :func:`target_probe_forms` selects from, so the two never drift.
    """
    part = partition_by_class(ontology)
    occ_index = _build_occurrence_index(inscriptions)

    def _cov(keys: Set[str]) -> Dict[str, object]:
        covered: List[str] = []
        skipped: List[str] = []
        for sk in sorted(keys):
            if _window_for_sign(sk, inscriptions, occ_index, n_context, seed) is not None:
                covered.append(sk)
            else:
                skipped.append(sk)
        return {"n_candidates": len(keys), "n_covered": len(covered),
                "n_skipped_no_context": len(skipped), "covered": covered, "skipped": skipped}

    return {"L_known": _cov(part["L_known"]), "L_virgin": _cov(part["L_virgin"])}


# --------------------------------------------------------------------------- #
# Proposer loop — probe EVERY target EVERY seed (signal; fail-closed)
# --------------------------------------------------------------------------- #
def run_lvirgin(model: str, n_seeds: int, host: Optional[str] = None, *,
                probe_pairs: Optional[List[Tuple[str, ablation.Form]]] = None,
                ontology_path: str = ONTOLOGY_JSON, inscriptions_path: str = INSCRIPTIONS_JSON,
                n_known: int = 20, n_virgin: int = 25, n_context: int = 6, probe_seed: int = 0,
                family: str = ablation.DEFAULT_FAMILY, timeout: int = 180,
                log_path: Optional[str] = None) -> Dict[str, object]:
    """Run the proposer over ALL probe forms for each seed; accumulate per-sign value Counters.

    For each seed ``0 .. n_seeds-1`` the LLM proposer is called ONCE over the WHOLE probe set
    (:func:`ablation.llm_propose`, temperature 0.8, options seed=seed — so the proposal is seed-varied
    and the call is logged via ollama_client). For each TARGET sign we record the value qwen assigned
    in its partial_map that seed (or nothing if it declined). A dead / garbled / raising call
    contributes NO values that seed (fail-closed; the seed is isolated, the batch never crashes).

    Returns the raw accumulation + partition + coverage + per-seed log. The statistical analysis is
    :func:`analyze` (kept separate so the proposer loop and the arithmetic are independently testable).
    ``probe_pairs`` / loaders are injectable for hermetic tests.
    """
    if probe_pairs is None:
        ontology = load_ontology(ontology_path)
        inscriptions = load_inscriptions(inscriptions_path)
        probe_pairs = target_probe_forms(ontology, inscriptions, n_known=n_known, n_virgin=n_virgin,
                                          n_context=n_context, seed=probe_seed)
        partition = partition_by_class(ontology)
        coverage = coverage_report(ontology, inscriptions, n_context=n_context, seed=probe_seed)
    else:
        partition = {"L_known": set(), "L_virgin": set()}  # caller-supplied; filled below if absent
        coverage = {}

    forms = [form for (_sk, form) in probe_pairs]
    target_keys = [sk for (sk, _form) in probe_pairs]

    # If the caller injected probe_pairs without a partition, classify the injected targets via the
    # ontology if available, else leave to the caller-provided partition (tests pass one explicitly).
    per_sign: Dict[str, Counter] = {sk: Counter() for sk in target_keys}

    per_seed: List[dict] = []
    n_dead = 0
    for s in range(n_seeds):
        corr: Set[Tuple[str, str]] = set()
        err: Optional[str] = None
        try:
            corr = ablation.llm_propose(forms, model, s, family=family, host=host,
                                        timeout=timeout, log_path=log_path)
        except Exception as exc:                       # noqa: BLE001 — isolate the seed, keep going
            err = str(exc)[:200]
        # one value per sign (JSON dict keys are unique); break ties deterministically (min).
        val_by_sign: Dict[str, str] = {}
        for (sk, v) in corr:
            if sk not in val_by_sign or v < val_by_sign[sk]:
                val_by_sign[sk] = v
        seed_n = 0
        for sk in target_keys:
            v = val_by_sign.get(sk)
            if v:
                per_sign[sk][v] += 1
                seed_n += 1
        if seed_n == 0:
            n_dead += 1
        per_seed.append({"seed": s, "n_values": seed_n, "error": err})

    return {
        "citation": CITATION_DESIGN,
        "model": model,
        "n_seeds": n_seeds,
        "family": family,
        "params": {"n_known": n_known, "n_virgin": n_virgin, "n_context": n_context,
                   "probe_seed": probe_seed, "timeout": timeout},
        "partition": {
            "L_known": sorted(partition.get("L_known", set())),
            "L_virgin": sorted(partition.get("L_virgin", set())),
            "excluded": partition.get("excluded", {}),
            "excluded_signs": partition.get("excluded_signs", {}),
            "n_known": len(partition.get("L_known", set())),
            "n_virgin": len(partition.get("L_virgin", set())),
        },
        "coverage": coverage,
        "probe_signs": {
            "known": [sk for (sk, _f) in probe_pairs if sk in partition.get("L_known", set())],
            "virgin": [sk for (sk, _f) in probe_pairs if sk in partition.get("L_virgin", set())],
            "all": target_keys,
        },
        "per_sign_values": {sk: dict(c) for sk, c in per_sign.items()},
        "per_seed": per_seed,
        "n_seeds_no_values": n_dead,
        "honesty": HONESTY,
        "_partition_sets": partition,   # internal handoff to analyze (sets; stripped before JSON)
    }


# --------------------------------------------------------------------------- #
# Analysis — excess-over-random modal share + permutation null + matched-n
# --------------------------------------------------------------------------- #
def _global_distribution(per_sign_values: Mapping[str, Mapping[str, int]]) -> Counter:
    """qwen's POOLED global value distribution (the null sampling distribution)."""
    glob: Counter = Counter()
    for c in per_sign_values.values():
        glob.update(c)
    return glob


def _expected_modal_shares(ns: Set[int], probs: np.ndarray, *, n_trials: int,
                           rng: np.random.Generator) -> Dict[int, float]:
    """E[modal_share] of ``n`` i.i.d. draws from ``probs``, by Monte-Carlo, per distinct n (>=1).

    For n==1 the modal share is always 1.0 (one draw is its own mode) — returned analytically so an
    n=1 sign always nets excess 0. Degenerate distributions (1 category) also give 1.0 for every n.
    """
    out: Dict[int, float] = {}
    K = int(probs.size)
    for n in sorted(ns):
        if n <= 0:
            continue
        if n == 1 or K <= 1:
            out[n] = 1.0
            continue
        counts = rng.multinomial(n, probs, size=n_trials)     # (n_trials, K)
        out[n] = float((counts.max(axis=1) / n).mean())
    return out


def _permutation_gap_p(excesses: np.ndarray, is_known: np.ndarray, obs_gap: float, *,
                       n_perm: int, rng: np.random.Generator) -> Optional[float]:
    """Two-sided label-shuffle p for the known−virgin excess gap. None when a class is empty.

    Shuffles the class labels across signs ``n_perm`` times; p = (1 + #{|perm gap| >= |obs gap|}) /
    (n_perm + 1) (add-one smoothing). The null is 'class is unrelated to consistency-excess', so a
    small p says the known/virgin difference is unlikely to be a coincidence of which signs landed in
    which class.
    """
    if is_known.sum() == 0 or (~is_known).sum() == 0:
        return None
    labels = is_known.copy()
    hits = 0
    tol = 1e-12
    for _ in range(n_perm):
        perm = rng.permutation(labels)
        gk = excesses[perm].mean()
        gv = excesses[~perm].mean()
        if abs(gk - gv) >= abs(obs_gap) - tol:
            hits += 1
    return (hits + 1) / (n_perm + 1)


def analyze(per_sign_values: Mapping[str, Mapping[str, int]],
            partition: Mapping[str, object], *, seed: int,
            n_min: int = 10, n_trials: int = 2000, n_perm: int = 2000) -> Dict[str, object]:
    """Per-sign consistency-excess, aggregated by class, with a permutation null + matched-n check.

    See :data:`CONSISTENCY_METRIC`. Each sign that got >= 1 value gets ``modal_share`` and the
    sample-size-corrected ``excess = modal_share - E[modal_share | n]``, where E is Monte-Carlo over
    qwen's pooled global value distribution. Aggregated to a mean excess per class; the headline is
    the known−virgin excess gap + a label-shuffle permutation p-value. A matched-n re-run (signs with
    n >= ``n_min`` only) guards against the gap being an artifact of coverage differences, and mean-n
    coverage is reported per class.

    HONESTY: a positive excess means a sign is imputed MORE consistently than a random draw of the
    same size — it is NON-RANDOM IMPUTATION, never a verified-correct value (there is no ground truth
    on virgin signs). Interpretation strings never claim correctness.
    """
    l_known = set(partition.get("L_known", set()))
    l_virgin = set(partition.get("L_virgin", set()))

    rng = np.random.default_rng(seed)

    # Global value distribution (the null) over ALL recorded values (every sign, every seed).
    glob = _global_distribution(per_sign_values)
    values = sorted(glob)
    total = sum(glob.values())
    if total > 0 and values:
        probs = np.array([glob[v] for v in values], dtype=float)
        probs = probs / probs.sum()
    else:
        probs = np.array([], dtype=float)

    # Distinct n across classified signs (so we MC each n once).
    ns: Set[int] = set()
    classified: List[Tuple[str, Counter, str]] = []  # (sign, counter, class)
    for sign, raw in per_sign_values.items():
        c = Counter(raw)
        n = int(sum(c.values()))
        if n <= 0:
            continue
        if sign in l_known:
            cls = "L_known"
        elif sign in l_virgin:
            cls = "L_virgin"
        else:
            continue                     # unclassified target (should not happen) -> not scored
        classified.append((sign, c, cls))
        ns.add(n)

    expected = _expected_modal_shares(ns, probs, n_trials=n_trials, rng=rng) if probs.size else {}

    per_sign_rows: List[dict] = []
    for sign, c, cls in classified:
        n = int(sum(c.values()))
        top_value, top_count = c.most_common(1)[0]
        modal_share = top_count / n
        exp = expected.get(n, 1.0 if (n == 1 or probs.size <= 1) else float("nan"))
        excess = modal_share - exp
        per_sign_rows.append({
            "sign": sign,
            "class": cls,
            "n": n,
            "distinct_values": len(c),
            "modal_value": top_value,            # qwen's MODAL imputation — NOT a verified value
            "modal_count": int(top_count),
            "modal_share": modal_share,
            "expected_modal_share": exp,
            "excess": excess,
        })
    per_sign_rows.sort(key=lambda r: (r["class"], -r["excess"], r["sign"]))

    def _class_stats(rows: Sequence[dict], cls: str) -> Dict[str, object]:
        ex = [r["excess"] for r in rows if r["class"] == cls]
        ns_ = [r["n"] for r in rows if r["class"] == cls]
        return {
            "n_signs": len(ex),
            "mean_excess": float(np.mean(ex)) if ex else None,
            "mean_modal_share": (float(np.mean([r["modal_share"] for r in rows if r["class"] == cls]))
                                 if ex else None),
            "mean_n": float(np.mean(ns_)) if ns_ else None,
        }

    def _headline(rows: Sequence[dict], rng_local: np.random.Generator) -> Dict[str, object]:
        kex = np.array([r["excess"] for r in rows if r["class"] == "L_known"], dtype=float)
        vex = np.array([r["excess"] for r in rows if r["class"] == "L_virgin"], dtype=float)
        if kex.size == 0 or vex.size == 0:
            return {"excess_gap": None, "permutation_p": None, "n_perm": n_perm,
                    "mean_excess_known": (float(kex.mean()) if kex.size else None),
                    "mean_excess_virgin": (float(vex.mean()) if vex.size else None),
                    "n_known": int(kex.size), "n_virgin": int(vex.size),
                    "no_power": True}
        gap = float(kex.mean() - vex.mean())
        excesses = np.concatenate([kex, vex])
        is_known = np.concatenate([np.ones(kex.size, bool), np.zeros(vex.size, bool)])
        p = _permutation_gap_p(excesses, is_known, gap, n_perm=n_perm, rng=rng_local)
        return {"excess_gap": gap, "permutation_p": p, "n_perm": n_perm,
                "mean_excess_known": float(kex.mean()), "mean_excess_virgin": float(vex.mean()),
                "n_known": int(kex.size), "n_virgin": int(vex.size), "no_power": False}

    headline = _headline(per_sign_rows, rng)

    # matched-n robustness: only signs with n >= n_min (coverage-balanced comparison).
    matched_rows = [r for r in per_sign_rows if r["n"] >= n_min]
    matched = _headline(matched_rows, rng)
    matched["n_min"] = n_min

    interpretation = _interpret(headline)

    return {
        "consistency_metric": CONSISTENCY_METRIC,
        "honesty": HONESTY,
        "n_classified_signs": len(classified),
        "global_distribution": {"n_distinct_values": len(values), "n_value_tokens": total,
                                "top": glob.most_common(10)},
        "class_stats": {"L_known": _class_stats(per_sign_rows, "L_known"),
                        "L_virgin": _class_stats(per_sign_rows, "L_virgin")},
        "headline": headline,
        "matched_n": matched,
        "interpretation": interpretation,
        "per_sign": per_sign_rows,
    }


def _interpret(headline: Mapping[str, object]) -> str:
    """A non-numeric reading of the headline — ALWAYS anti-correctness (no ground truth on virgin)."""
    if headline.get("no_power") or headline.get("excess_gap") is None:
        return ("NO POWER: a class has no signs with values — the consistency gap is not estimable. "
                "Nothing claimed.")
    gap = float(headline["excess_gap"])
    p = headline.get("permutation_p")
    p_big = (p is None) or (p > 0.05)
    if p_big or abs(gap) < 0.05:
        return ("Virgin signs are imputed about as NON-RANDOMLY as known signs (known−virgin excess "
                "gap ≈ 0, permutation p not significant): qwen shows cross-seed structure on the "
                "untouched *-series, consistent with reasoning OR a stable hallucination. This is "
                "NOT proven correctness — there is no ground truth on virgin signs; carries no "
                "verdict weight.")
    if gap > 0:
        return ("Known signs are imputed MORE consistently than virgin signs (positive known−virgin "
                "excess gap, permutation-significant): qwen is self-consistent chiefly where the "
                "value is memorizable — regurgitation-dominated, weak generalization to untouched "
                "signs. (Still says nothing about correctness on virgin signs.)")
    return ("Virgin signs are imputed MORE consistently than known signs (negative gap) — unusual; "
            "inspect the per-sign table and global distribution before reading anything into it. "
            "Consistency is not correctness.")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _default_out(model: str) -> str:
    safe = "".join(c if c.isalnum() or c in "-._" else "_" for c in model)
    return os.path.join(_ROOT, "runtime", "lvirgin", f"{safe}.json")


def _summary(report: Dict[str, object]) -> str:
    a = report["analysis"]
    part = report["run"]["partition"]
    cov = report["run"].get("coverage", {})
    hl = a["headline"]
    mn = a["matched_n"]
    ks = a["class_stats"]["L_known"]
    vs = a["class_stats"]["L_virgin"]

    def _f(x):
        return "n/a" if x is None else f"{x:+.3f}"

    def _p(x):
        return "n/a" if x is None else f"{x:.4f}"

    lines = [
        "=" * 80,
        "§C.2 L_VIRGIN GENERALIZATION TEST  (logos comparison-layer §C.2)",
        "=" * 80,
        f"model={report['run']['model']}  seeds={report['run']['n_seeds']}  "
        f"family={report['run']['family']}",
        f"partition (by ontology class): L_known={part['n_known']} (syllabogram-AB)  "
        f"L_virgin={part['n_virgin']} (syllabogram-Aonly)",
        f"EXCLUDED (non-phonetic, never scored): {part['excluded']}",
    ]
    if cov:
        ck, cv = cov.get("L_known", {}), cov.get("L_virgin", {})
        lines.append(f"context coverage: known {ck.get('n_covered','?')}/{ck.get('n_candidates','?')}"
                     f"  virgin {cv.get('n_covered','?')}/{cv.get('n_candidates','?')}"
                     f"  (skipped-no-context virgin: {cv.get('n_skipped_no_context','?')})")
    lines += [
        f"probed: known={len(report['run']['probe_signs']['known'])}  "
        f"virgin={len(report['run']['probe_signs']['virgin'])}  "
        f"(seeds with no values: {report['run']['n_seeds_no_values']})",
        "-" * 80,
        f"mean excess-over-random consistency:  L_known={_f(ks['mean_excess'])} (mean n={ks['mean_n']})"
        f"   L_virgin={_f(vs['mean_excess'])} (mean n={vs['mean_n']})",
        f"HEADLINE known−virgin excess gap = {_f(hl['excess_gap'])}   permutation p = {_p(hl['permutation_p'])}"
        f"  ({hl['n_known']} vs {hl['n_virgin']} signs, {hl['n_perm']} perms)",
        f"matched-n (n>={mn['n_min']}) gap = {_f(mn['excess_gap'])}   permutation p = {_p(mn['permutation_p'])}"
        f"  ({mn['n_known']} vs {mn['n_virgin']} signs)",
        "-" * 80,
        "INTERPRETATION: " + a["interpretation"],
        "HONESTY: " + HONESTY,
    ]
    return "\n".join(lines)


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="§C.2 L_virgin generalization test (logos comparison-layer)")
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--seeds", type=int, default=40, help="proposer seeds 0..seeds-1 (each probes ALL signs)")
    p.add_argument("--n-known", type=int, default=20, help="L_known (AB) comparison signs to probe")
    p.add_argument("--n-virgin", type=int, default=25, help="L_virgin (*-series) signs to probe")
    p.add_argument("--n-context", type=int, default=6, help="signs per fixed context window")
    p.add_argument("--probe-seed", type=int, default=0, help="seed for fixed per-sign window selection")
    p.add_argument("--n-min", type=int, default=10, help="min n for the matched-n robustness check")
    p.add_argument("--mc-trials", type=int, default=2000, help="Monte-Carlo trials for E[modal_share]")
    p.add_argument("--perm", type=int, default=2000, help="label-shuffle permutations (>=2000)")
    p.add_argument("--analysis-seed", type=int, default=0, help="seed for MC + permutation null")
    p.add_argument("--family", default=ablation.DEFAULT_FAMILY)
    p.add_argument("--host", default=None, help="Ollama host (default $OLLAMA_URL or the gpu host)")
    p.add_argument("--timeout", type=int, default=180)
    p.add_argument("--out", default=None, help="output JSON (default runtime/lvirgin/<model>.json)")
    p.add_argument("--print-json", action="store_true", help="print the full JSON report to stdout")
    args = p.parse_args(argv)

    run = run_lvirgin(args.model, args.seeds, host=args.host, n_known=args.n_known,
                      n_virgin=args.n_virgin, n_context=args.n_context, probe_seed=args.probe_seed,
                      family=args.family, timeout=args.timeout)
    analysis = analyze(run["per_sign_values"], run["_partition_sets"], seed=args.analysis_seed,
                       n_min=args.n_min, n_trials=args.mc_trials, n_perm=args.perm)
    run.pop("_partition_sets", None)              # sets are not JSON-serializable; drop the handoff
    report = {"citation": CITATION_DESIGN, "run": run, "analysis": analysis}

    out = args.out or _default_out(args.model)
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
