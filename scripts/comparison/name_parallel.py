#!/usr/bin/env python3
"""name_parallel.py — Packard-style name-parallel anchor probe: BUILD + CALIBRATION layer (Phase 5a).

Packard (1974) asked whether Linear A word types run PARALLEL to Linear B personal/place names:
an LA word whose first two signs are value-identical to a KN name's first two signs and whose
third sign agrees in CONSONANT is a "name parallel". The AB->LB value mapping needs NO new table:
silver LA word tokens ARE the conventional values (the scripts/cross_script/data.py bridge), so
the probe statistic is pure counting over sign-value tuples.

This module is the STATISTICS + DATA layer only:

  * ``Criterion`` (frozen) + ``matches``/``match_count`` — the match semantics, fail-CLOSED on
    undecodable signs (A-only ``*NN``, subscript-variant values with no cv parse) and missing slots;
  * ``load_la_packard_pool`` — the LA type pool from structured silver (>=3 signs, logogram/
    fraction/numeral-filtered via the ontology, ``*NN``-in-criterion-slots exclusion COUNTED);
  * ``load_names_cog`` + ``kn_attested_names`` — the glossed, fully-decodable LB name list joined
    to the DĀMOS Knossos vocabulary (collectionid==1, dual-computed against the heading prefix;
    mismatch diagnostic reported; sanity band 100–250 logged);
  * N1 ``n1_banded_null`` — the primary null: the promoted ``nulls.banded_map_permutation``
    (Packard 1974 at the map level) applied to the pool's sign->value identity map;
  * N2 ``n2_document_permutation_null`` — pseudo-Knossos robustness null (random DĀMOS document
    subsets of the same size; survives-N1-not-N2 means "LB names generally, nothing
    Knossos-specific");
  * Art. XII strata (reported, non-verdict): S1 Salgarella dark-blue-only criterion slots;
    S2 toponym-motivated signs excluded (the sharp circularity test);
  * ``run_calibration`` — the two fail-CLOSED calibration gates that must be green BEFORE any
    prereg freeze: (a) an LB positive control that must FIRE, and (b) a cherry-pick false-fire
    rate over the criterion grid on fabricated LA-like corpora (lfake + banded flavours) with a
    Clopper–Pearson 95% upper bound target of <= 0.05.

MULTIPLICITY (the anti-slide clause): the <=12-variant ``criterion_grid`` is exploratory; the ONLY
confirmatory criterion is ``PRIMARY`` (``packard1974_kn_primary``). Every variant ever evaluated —
including while debugging — is registered on a ``CriterionLog`` and inflates the instrumented
``n_eff`` that raises the deflated bars (expected-max order statistic + corrected margin).

WHAT THIS MODULE NEVER DOES (invariants 1/2/4; Phase 5b gate): it never imports scripts/verdict.py,
never computes the true-value LA-pool-vs-KN-names statistic (that is the separately preregistered,
plan_hash-committed probe run), and a calibration result is a machinery property, never an LA claim.
Truth-layer cap: even a Phase-5b positive validates NO sign value and creates NO anchor (L3 max).

Citations: Packard 1974 (name parallels; frequency-banded permutation null); the promoted map-level
null credits the di-Mino-301 audit PC2 control (see nulls.banded_map_permutation).

Reproduce the calibration:  python3 scripts/comparison/name_parallel.py --seed 0
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from typing import Dict, FrozenSet, List, Optional, Sequence, Set, Tuple

import numpy as np

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from scripts import logos_stats  # noqa: E402  (expected-max order-statistic bar)
from scripts.comparison import lfake  # noqa: E402  (fabricated LA-like calibration corpora)
from scripts.comparison.nulls import banded_map_permutation  # noqa: E402  (promoted N1 null)
from scripts.comparison.phono_distributional import cv_label  # noqa: E402  (consonant classes)
from scripts.comparison.run_canary import corrected_margin_bar  # noqa: E402  (CF+Bonferroni bar)
from scripts.cross_script.data import (  # noqa: E402  (the A<->B value bridge, DĀMOS parser)
    _b_value_from_codepoint, _damos_wordforms, _norm_a_token)

STRUCTURED_SILVER = os.path.join(_ROOT, "corpus", "silver", "inscriptions_structured.json")
ONTOLOGY = os.path.join(_ROOT, "corpus", "silver", "signs_ontology.json")
NAMES_COG = os.path.join(_ROOT, "corpus", "bronze", "code", "CSA_OptMatcher", "data",
                         "linear_b-greek.names.cog")
DAMOS_ITEMS = os.path.join(_ROOT, "corpus", "bronze", "linearb", "damos", "items.jsonl")
SALGARELLA_GRADES = os.path.join(_ROOT, "experiments", "crossscript_gate",
                                 "salgarella_2020_grades.json")
ANCHOR_CENSUS = os.path.join(_ROOT, "experiments", "crossscript_gate", "phase2",
                             "anchor_census.csv")
CALIBRATION_JSON = os.path.join(_ROOT, "results", "name_parallel_calibration.json")

# ontology classes whose diplomatic tokens are NOT lexical syllabograms (the GRA/VIN gotcha:
# logograms sit in word position in the transliteration stream)
NONSYLLABIC_CLASSES = ("logogram", "fraction", "numeral", "uncertain")

WordType = Tuple[str, ...]


# --------------------------------------------------------------------------- #
# Criterion — frozen match semantics (Packard 1974, KN primary)
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Criterion:
    """One name-parallel match rule over sign-value tuples.

    ``n_exact`` leading slots must be value-IDENTICAL; the next slot (if ``slot3_mode`` is not
    'ignore') must be consonant-identical ('consonant', via phono_distributional.cv_label) or
    value-identical ('exact'). Sequences shorter than ``min_signs`` — or than the slots the rule
    needs — NEVER match, and a sign with no cv parse (``*NN``, RA2-style subscript values) never
    satisfies a consonant slot: fail closed, always.
    """
    name: str
    min_signs: int = 3
    n_exact: int = 2
    slot3_mode: str = "consonant"      # 'consonant' | 'exact' | 'ignore'

    def n_slots_used(self) -> int:
        return self.n_exact + (0 if self.slot3_mode == "ignore" else 1)


PRIMARY = Criterion(name="packard1974_kn_primary", min_signs=3, n_exact=2, slot3_mode="consonant")


def criterion_grid() -> List[Criterion]:
    """The exploratory <=12-variant grid (min_signs x n_exact x slot3_mode), PRIMARY first.

    Exactly 12 variants; every one evaluated in a calibration or probe session registers on the
    CriterionLog and inflates n_eff. PRIMARY is the only confirmatory criterion (Phase 5b P1).
    """
    grid = [PRIMARY]
    for min_signs in (3, 4):
        for n_exact in (1, 2, 3):
            for mode in ("consonant", "exact"):
                if (min_signs, n_exact, mode) == (PRIMARY.min_signs, PRIMARY.n_exact,
                                                  PRIMARY.slot3_mode):
                    continue
                grid.append(Criterion(name=f"grid_s{min_signs}_e{n_exact}_{mode}",
                                      min_signs=min_signs, n_exact=n_exact, slot3_mode=mode))
    return grid


class CriterionLog:
    """Instrumented criterion-variant multiplicity (the anti-Tsirkas-slide clause).

    Duck-types the gate_null_calibration._Log shape (``n_eff``, ``eps_grid``): every distinct
    criterion variant evaluated through :func:`match_count` with a log attached counts toward the
    ``n_eff`` that raises the deflated bars. Debugging variants evaluated outside a log must be
    hand-registered at prereg freeze (Phase 5b contract).
    """

    def __init__(self) -> None:
        self.variants: List[str] = []
        self.eps_grid = None

    def register(self, crit: Criterion) -> None:
        if crit.name not in self.variants:
            self.variants.append(crit.name)

    @property
    def n_eff(self) -> int:
        return max(1, len(self.variants))


def matches(la_word: Sequence[str], name: Sequence[str], crit: Criterion) -> bool:
    """Does one LA word type match one LB name under ``crit``? (reference pairwise semantics)."""
    need = crit.n_slots_used()
    if len(la_word) < crit.min_signs or len(name) < crit.min_signs:
        return False
    if len(la_word) < need or len(name) < need:
        return False
    for i in range(crit.n_exact):
        if la_word[i] != name[i]:
            return False
    if crit.slot3_mode == "ignore":
        return True
    a, b = la_word[crit.n_exact], name[crit.n_exact]
    if crit.slot3_mode == "exact":
        return a == b
    la_cv, nm_cv = cv_label(a), cv_label(b)
    if la_cv is None or nm_cv is None:      # undecodable in the consonant slot: fail closed
        return False
    return la_cv[0] == nm_cv[0]


def _match_key(seq: Sequence[str], crit: Criterion):
    """The criterion key of one sequence, or None when it cannot participate (fail closed).

    Two sequences match under ``crit`` iff their keys are equal and non-None — the hashed
    equivalent of :func:`matches` (property-tested against it).
    """
    need = crit.n_slots_used()
    if len(seq) < crit.min_signs or len(seq) < need:
        return None
    head = tuple(seq[:crit.n_exact])
    if crit.slot3_mode == "ignore":
        return head
    s3 = seq[crit.n_exact]
    if crit.slot3_mode == "exact":
        return head + (s3,)
    lab = cv_label(s3)
    if lab is None:
        return None
    return head + ("C:" + lab[0],)


def matched_types(pool: Sequence[WordType], names: Sequence[WordType],
                  crit: Criterion, log: Optional[CriterionLog] = None) -> List[WordType]:
    """The distinct pool TYPES matched by >= 1 name under ``crit`` (Packard's unit is the TYPE)."""
    if log is not None:
        log.register(crit)
    keys = {k for k in (_match_key(n, crit) for n in names) if k is not None}
    out, seen = [], set()
    for w in pool:
        if w in seen:
            continue
        seen.add(w)
        if _match_key(w, crit) in keys:
            out.append(w)
    return out


def match_count(pool: Sequence[WordType], names: Sequence[WordType],
                crit: Criterion, log: Optional[CriterionLog] = None) -> int:
    """The probe statistic: number of distinct pool types matched (see :func:`matched_types`)."""
    return len(matched_types(pool, names, crit, log=log))


# --------------------------------------------------------------------------- #
# Data layer — LA pool (silver structured), LB names (names.cog), DĀMOS KN join
# --------------------------------------------------------------------------- #
def nonsyllabic_tokens(ontology_path: str = ONTOLOGY) -> Set[str]:
    """Normalized diplomatic tokens of every non-syllabogram ontology class (logogram/fraction/
    numeral/uncertain) — the exclusion set of the pool's logogram filter."""
    onto = json.load(open(ontology_path, encoding="utf-8"))
    out: Set[str] = set()
    for entry in onto.values():
        if entry.get("class") in NONSYLLABIC_CLASSES:
            for t in entry.get("diplomatic_tokens", []):
                nt = _norm_a_token(t)
                if nt:
                    out.add(nt)
    return out


def build_pool(word_types: Sequence[WordType], nonsyllabic: Set[str],
               min_signs: int = 3) -> Tuple[List[WordType], Dict[str, int]]:
    """Pure pool construction (unit-testable without licensed data).

    Keeps types with >= ``min_signs`` signs; drops any type containing a non-syllabic sign in ANY
    slot (ontology classes above, plus every '+'-ligature — ligatures are logographic); then splits
    off types with an undecodable ``*NN`` sign in criterion slots 1–3 (counted, never silently
    dropped). Returns (decodable_pool_sorted, counts).
    """
    typed = sorted({t for t in word_types if len(t) >= min_signs})
    lexical = [t for t in typed
               if not any(s in nonsyllabic or "+" in s for s in t)]
    starred = [t for t in lexical if any(s.startswith("*") for s in t[:3])]
    pool = [t for t in lexical if not any(s.startswith("*") for s in t[:3])]
    counts = {
        "types_ge_min_signs": len(typed),
        "types_after_logogram_filter": len(lexical),
        "excluded_logogram_types": len(typed) - len(lexical),
        "excluded_undecodable_star_slots_1_3": len(starred),
        "pool_decodable_types": len(pool),
        "min_signs": min_signs,
    }
    return pool, counts


def load_la_packard_pool(silver_path: str = STRUCTURED_SILVER, ontology_path: str = ONTOLOGY,
                         min_signs: int = 3) -> Dict[str, object]:
    """The LA word-type pool from structured silver (word boundaries are the scribe's own).

    Signs are normalized exactly as the cross-script bridge does (`_norm_a_token`: subscripts ->
    ASCII, damage masks stripped), so pool tokens live in the SAME value space as the LB side.
    """
    docs = json.load(open(silver_path, encoding="utf-8"))
    nonsyll = nonsyllabic_tokens(ontology_path)
    types: Set[WordType] = set()
    for d in docs:
        for w in d["words"]:
            signs = tuple(t for t in (_norm_a_token(s) for s in w) if t)
            if len(signs) >= min_signs:
                types.add(signs)
    pool, counts = build_pool(sorted(types), nonsyll, min_signs=min_signs)
    counts["docs"] = len(docs)
    return {"pool": pool, "diagnostics": counts}


def load_names_cog(path: str = NAMES_COG, min_signs: int = 3) -> Dict[str, object]:
    """The LB name list: glossed rows of linear_b-greek.names.cog whose glyphs FULLY decode via
    the Unicode name bridge (`_b_value_from_codepoint`) to >= ``min_signs`` values.

    A row is glossed when its greek field is non-empty and not '_'. Partially-decodable rows are
    excluded (fail closed) and counted. Returns the sorted DISTINCT name types + diagnostics.
    """
    rows = glossed = decodable_rows = 0
    names: List[WordType] = []
    with open(path, encoding="utf-8") as f:
        next(f)                                     # 'linb\tgreek' header
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if not parts or not parts[0].strip():
                continue
            rows += 1
            gloss = parts[1].strip() if len(parts) > 1 else ""
            if not gloss or gloss == "_":
                continue
            glossed += 1
            vals: List[str] = []
            ok = True
            for ch in parts[0]:
                if ord(ch) < 0x10000:
                    continue                        # not a Linear B codepoint
                v = _b_value_from_codepoint(ch)
                if v is None:                       # logogram / unnamed: row not fully decodable
                    ok = False
                    break
                vals.append(v)
            if ok and len(vals) >= min_signs:
                decodable_rows += 1
                names.append(tuple(vals))
    distinct = sorted(set(names))
    return {"names": distinct,
            "diagnostics": {"rows": rows, "glossed_rows": glossed,
                            "glossed_fully_decodable_ge3_rows": decodable_rows,
                            "distinct_name_types": len(distinct), "min_signs": min_signs}}


def load_damos_docs(path: str = DAMOS_ITEMS) -> List[Dict[str, object]]:
    """DĀMOS documents as (id, collectionid, heading, syllabic wordform-type set)."""
    docs: List[Dict[str, object]] = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            item = rec.get("item", {}) or {}
            docs.append({
                "id": rec.get("_id"),
                "collectionid": item.get("collectionid"),
                "heading": rec.get("heading") or "",
                "wordforms": frozenset(
                    tuple(w) for w in _damos_wordforms(item.get("content", "") or "")),
            })
    return docs


def kn_attested_names(names: Sequence[WordType], docs: Sequence[Dict[str, object]],
                      sanity_band: Tuple[int, int] = (100, 250)) -> Dict[str, object]:
    """Join the name list to the DĀMOS Knossos vocabulary.

    KN membership is DUAL-COMPUTED — item.collectionid == 1 (authoritative) vs heading prefix
    'KN' — and the disagreement is a reported diagnostic (flagged above 2%). The joined name count
    must land in the pre-stated sanity band (logged, not enforced): outside it, inspect before use.
    """
    kn_coll = [d for d in docs if d["collectionid"] == 1]
    kn_head = [d for d in docs if str(d["heading"]).startswith("KN")]
    vocab_coll: Set[WordType] = set().union(*(d["wordforms"] for d in kn_coll)) if kn_coll else set()
    vocab_head: Set[WordType] = set().union(*(d["wordforms"] for d in kn_head)) if kn_head else set()
    mismatch = sum(1 for d in docs
                   if (d["collectionid"] == 1) != str(d["heading"]).startswith("KN"))
    kn_names = sorted(set(names) & vocab_coll)
    frac = (mismatch / len(docs)) if docs else 0.0
    diag = {
        "damos_docs": len(docs),
        "kn_docs_by_collectionid": len(kn_coll),
        "kn_docs_by_heading_prefix": len(kn_head),
        "doc_attribution_mismatches": mismatch,
        "doc_attribution_mismatch_fraction": round(frac, 6),
        "attribution_mismatch_over_2pct": bool(frac > 0.02),
        "kn_vocab_types": len(vocab_coll),
        "kn_vocab_symmetric_difference_vs_heading": len(vocab_coll ^ vocab_head),
        "kn_names": len(kn_names),
        "kn_names_by_heading": len(set(names) & vocab_head),
        "sanity_band": list(sanity_band),
        "in_sanity_band": bool(sanity_band[0] <= len(kn_names) <= sanity_band[1]),
    }
    return {"kn_names": kn_names, "kn_vocab": sorted(vocab_coll), "diagnostics": diag}


# --------------------------------------------------------------------------- #
# Nulls — N1 banded sign-map permutation (primary), N2 document permutation
# --------------------------------------------------------------------------- #
def banded_pool_null(pool: Sequence[WordType], seed: int, n_bands: int = 4,
                     signs: Optional[List[str]] = None,
                     freq: Optional[Counter] = None) -> List[WordType]:
    """One N1 draw: rewrite every pool word through a banded permutation of the identity
    sign->value map (the promoted nulls.banded_map_permutation). The permuted map is a within-band
    bijection, so distinct types stay distinct — only the sign<->value correspondence dies."""
    if signs is None:
        signs = sorted({s for w in pool for s in w})
    if freq is None:
        freq = Counter(s for w in pool for s in w)
    pm = banded_map_permutation(signs, {s: s for s in signs}, freq, seed=seed, n_bands=n_bands)
    return [tuple(pm.get(s, s) for s in w) for w in pool]


def n1_banded_null(pool: Sequence[WordType], names: Sequence[WordType], crit: Criterion,
                   B: int = 1000, seed: int = 0, n_bands: int = 4,
                   log: Optional[CriterionLog] = None) -> np.ndarray:
    """N1 primary null distribution: ``B`` banded-map draws -> match counts (mu0/sigma0 feed the
    deflated bars). Seeded and deterministic; the pool inventory is computed once."""
    signs = sorted({s for w in pool for s in w})
    freq = Counter(s for w in pool for s in w)
    if log is not None:
        log.register(crit)
    counts = np.empty(B, dtype=float)
    for i in range(B):
        perm = banded_pool_null(pool, seed=seed + i, n_bands=n_bands, signs=signs, freq=freq)
        counts[i] = match_count(perm, names, crit)
    return counts


def n2_document_permutation_null(pool: Sequence[WordType], all_names: Sequence[WordType],
                                 docs: Sequence[Dict[str, object]], n_docs: int,
                                 crit: Criterion, B: int = 1000, seed: int = 0,
                                 log: Optional[CriterionLog] = None) -> np.ndarray:
    """N2 robustness null: pseudo-Knossos = a random ``n_docs``-document DĀMOS subset; rebuild the
    name list against ITS vocabulary; recompute. An excess that survives N1 but not N2 says
    'LB names generally', not 'Knossos-specifically'."""
    rng = np.random.default_rng(seed)
    if log is not None:
        log.register(crit)
    nameset = set(all_names)
    counts = np.empty(B, dtype=float)
    for b in range(B):
        idx = rng.choice(len(docs), size=n_docs, replace=False)
        vocab: Set[WordType] = set()
        for i in idx:
            vocab |= docs[int(i)]["wordforms"]
        pseudo_names = sorted(nameset & vocab)
        counts[b] = match_count(pool, pseudo_names, crit)
    return counts


# --------------------------------------------------------------------------- #
# Deflated bars (Art. VIII/IX: n_eff-raised, never a raw p95)
# --------------------------------------------------------------------------- #
def bars_from_nulls(null_counts: Sequence[float], n_eff: int, alpha: float = 0.05) -> Dict[str, object]:
    """Both operative bars from one null distribution at instrumented multiplicity ``n_eff``:
    the expected-max order statistic E[max of n_eff draws] (logos_stats) and the Cornish-Fisher +
    Bonferroni corrected margin (run_canary). The operative bar is their max; monotone in n_eff."""
    arr = np.asarray(null_counts, dtype=float)
    mu0 = float(arr.mean()) if arr.size else 0.0
    sigma0 = float(arr.std(ddof=1)) if arr.size > 1 else 0.0
    emax = float(logos_stats.expected_max_order_stat(mu0, sigma0, int(n_eff)))
    cmb, cmb_diag = corrected_margin_bar(arr, n_comparisons=int(n_eff), alpha=alpha)
    return {"mu0": mu0, "sigma0": sigma0, "n_eff": int(n_eff), "alpha": alpha,
            "expected_max_order_stat": emax, "corrected_margin_bar": float(cmb),
            "operative_bar": float(max(emax, float(cmb))),
            "corrected_margin_diagnostics": _py(cmb_diag)}


# --------------------------------------------------------------------------- #
# Art. XII strata (same run, REPORTED, non-verdict)
# --------------------------------------------------------------------------- #
def load_salgarella_darkblue(path: str = SALGARELLA_GRADES) -> Set[str]:
    """The Salgarella 2020 dark-blue signs ('homomorphic and also likely homophone', Tables 2-3)."""
    grades = json.load(open(path, encoding="utf-8"))
    return {sign for sign, g in grades["signs"].items()
            if g.get("grade") == "homomorphic and also likely homophone"}


def load_toponym_covered_signs(path: str = ANCHOR_CENSUS) -> Set[str]:
    """Union of ``covered_signs`` over the anchor-census TOPONYM rows — the signs whose values are
    MOTIVATED by the toponym equations (the S2 circularity-exposure set, Art. XII)."""
    out: Set[str] = set()
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("class") == "toponym":
                out |= {s.strip() for s in (row.get("covered_signs") or "").split(",")
                        if s.strip()}
    return out


def stratum_s1_darkblue(pool: Sequence[WordType], crit: Criterion,
                        darkblue: Set[str]) -> List[WordType]:
    """S1: the sub-pool whose criterion slots are ALL Salgarella dark-blue signs — the slice where
    the AB->LB value convention has independent homomorphy+homophony support."""
    need = crit.n_slots_used()
    return [w for w in pool if len(w) >= need and all(s in darkblue for s in w[:need])]


def stratum_s2_toponym_excluded(pool: Sequence[WordType], crit: Criterion,
                                covered: Set[str]) -> List[WordType]:
    """S2: the sub-pool whose criterion slots use NO toponym-motivated sign (Art. XII: never grade
    a target by the rule that created it). An excess that vanishes under S2 is the known anchors
    restated, supporting REFUTE_LOTO_FRAGILE."""
    need = crit.n_slots_used()
    return [w for w in pool if len(w) >= need and not any(s in covered for s in w[:need])]


# --------------------------------------------------------------------------- #
# Fabricated LA-like corpora (false-fire flavours)
# --------------------------------------------------------------------------- #
_PUA_BASE = 0xE000


def lfake_la_like_corpus(pool: Sequence[WordType], seed: int) -> List[WordType]:
    """An L_fake LA-like corpus over the pool's sign inventory: signs are mapped to private-use
    characters, lfake's markov mode is calibrated to the encoded pool (bigram transitions, length
    distribution, marginals), a same-size fake lexicon is generated (never reproducing a
    calibration-set form — lfake's rejection), then mapped back to sign tuples."""
    signs = sorted({s for w in pool for s in w})
    to_char = {s: chr(_PUA_BASE + i) for i, s in enumerate(signs)}
    to_sign = {c: s for s, c in to_char.items()}
    forms = ["".join(to_char[s] for s in w) for w in pool]
    cfg = lfake.calibrate_to(forms, mode="markov", vowels=frozenset())
    gen = lfake.LFakeGenerator(cfg, seed=seed)
    lex = gen.generate_lexicon(n=len(forms), with_glosses=False)
    return sorted({tuple(to_sign[c] for c in e["form"]) for e in lex})


# --------------------------------------------------------------------------- #
# Calibration gates (fail CLOSED; both must be green before any prereg freeze)
# --------------------------------------------------------------------------- #
def _cp95_upper(k: int, B: int) -> float:
    """One-sided exact Clopper–Pearson 95% upper bound (Beta-quantile inversion)."""
    from scipy.stats import beta
    return float(beta.ppf(0.95, k + 1, B - k)) if k < B else 1.0


def _py(obj):
    """numpy -> plain-python sanitizer for json.dump."""
    if isinstance(obj, dict):
        return {k: _py(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_py(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return [_py(v) for v in obj.tolist()]
    return obj


def _false_fire_trial(fake_pool: Sequence[WordType], names: Sequence[WordType],
                      grid: Sequence[Criterion], n_eff: int, B_null: int, seed: int,
                      log: Optional[CriterionLog] = None) -> Dict[str, object]:
    """One cherry-pick trial (gate_null_calibration pattern): evaluate EVERY grid variant on the
    fabricated corpus, keep the best, grade it against its own N1 null at instrumented n_eff."""
    best_crit, best_m = None, -1
    for crit in grid:
        m = match_count(fake_pool, names, crit, log=log)
        if m > best_m:
            best_crit, best_m = crit, m
    nulls_best = n1_banded_null(fake_pool, names, best_crit, B=B_null, seed=seed)
    bars = bars_from_nulls(nulls_best, n_eff=n_eff)
    return {"best_variant": best_crit.name, "best_count": int(best_m),
            "mu0": bars["mu0"], "sigma0": bars["sigma0"],
            "operative_bar": bars["operative_bar"],
            "expected_max_order_stat": bars["expected_max_order_stat"],
            "corrected_margin_bar": bars["corrected_margin_bar"],
            "fired": bool(best_m > bars["operative_bar"])}


def run_calibration(seed: int = 0, B_pc_null: int = 500, B_trials: int = 500,
                    B_null_trial: int = 100, fast: bool = False,
                    out_path: str = CALIBRATION_JSON) -> Dict[str, object]:
    """The Phase-5a calibration run -> results/name_parallel_calibration.json.

    (a) LB POSITIVE CONTROL: a seeded held-out half of the KN-attested names (pool role) probed by
        the KN NON-name vocabulary under TRUE values must FIRE above the banded-map-permutation
        expected-max bar (B_pc_null draws); the reverse direction is reported as a secondary
        diagnostic. No fire => machinery INVALID and the LA run stays blocked.
    (b) FALSE-FIRE: ``B_trials`` fabricated LA-like corpora (alternating banded / lfake flavours),
        each cherry-picking the best of the 12-variant grid, graded against its own null at the
        instrumented n_eff; requires Clopper–Pearson 95% upper <= 0.05.

    The TRUE-VALUE LA-pool-vs-KN-names statistic is NEVER computed here (Phase 5b, prereg-gated).
    ``fast=True`` shrinks every B for smoke tests and is RECORDED in the JSON so a quick run can
    never impersonate the published calibration.
    """
    if fast:
        B_pc_null, B_trials, B_null_trial = 100, 40, 50
    log = CriterionLog()
    grid = criterion_grid()
    for crit in grid:                    # the whole grid is evaluated in this session
        log.register(crit)

    la = load_la_packard_pool()
    names_info = load_names_cog()
    docs = load_damos_docs()
    join = kn_attested_names(names_info["names"], docs)
    kn_names: List[WordType] = join["kn_names"]
    all_name_set = set(names_info["names"])

    # ---- (a) LB positive control -------------------------------------------------- #
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(kn_names))
    half = len(kn_names) // 2
    heldout = sorted(kn_names[int(i)] for i in order[:half])
    nonname_vocab = sorted(w for w in join["kn_vocab"]
                           if len(w) >= 3 and w not in all_name_set)

    m_obs = match_count(heldout, nonname_vocab, PRIMARY, log=log)
    nulls_pc = n1_banded_null(heldout, nonname_vocab, PRIMARY, B=B_pc_null, seed=seed + 10_000)
    bars_pc = bars_from_nulls(nulls_pc, n_eff=log.n_eff)
    pc_fires_emax = bool(m_obs > bars_pc["expected_max_order_stat"])
    pc_fires_both = bool(m_obs > bars_pc["operative_bar"])

    m_rev = match_count(nonname_vocab, heldout, PRIMARY, log=log)
    nulls_rev = n1_banded_null(nonname_vocab, heldout, PRIMARY, B=B_pc_null, seed=seed + 30_000)
    bars_rev = bars_from_nulls(nulls_rev, n_eff=log.n_eff)

    positive_control = {
        "design": ("held-out half of KN-attested names (pool role, true values) probed by the KN "
                   "non-name vocabulary; null = banded permutation of the pool's sign map"),
        "criterion": PRIMARY.name,
        "n_heldout_names_pool": len(heldout),
        "n_unused_name_half": len(kn_names) - len(heldout),
        "n_nonname_vocab_probes": len(nonname_vocab),
        "B_null": B_pc_null,
        "m_obs": int(m_obs),
        "bars": bars_pc,
        "fires_above_expected_max": pc_fires_emax,
        "fires_above_both_bars": pc_fires_both,
        "secondary_reverse_direction": {
            "design": "KN non-name vocabulary as pool probed by the held-out name half",
            "m_obs": int(m_rev),
            "bars": bars_rev,
            "fires_above_expected_max": bool(m_rev > bars_rev["expected_max_order_stat"]),
            "fires_above_both_bars": bool(m_rev > bars_rev["operative_bar"]),
        },
    }

    # ---- (b) false-fire over fabricated LA-like corpora --------------------------- #
    flavour_stats = {"banded": {"fires": 0, "trials": 0},
                     "lfake": {"fires": 0, "trials": 0}}
    best_variant_hist: Counter = Counter()
    best_counts: List[int] = []
    cols: Dict[str, list] = {k: [] for k in
                             ("flavour", "best_variant", "best_count", "mu0", "sigma0",
                              "expected_max_order_stat", "corrected_margin_bar",
                              "operative_bar", "fired")}
    fires = 0
    for t in range(B_trials):
        flavour = "banded" if t % 2 == 0 else "lfake"
        tseed = seed + 20_000 + t
        if flavour == "banded":
            fake = banded_pool_null(la["pool"], seed=tseed)
        else:
            fake = lfake_la_like_corpus(la["pool"], seed=tseed)
        trial = _false_fire_trial(fake, kn_names, grid, n_eff=log.n_eff,
                                  B_null=B_null_trial, seed=tseed + 500_000, log=log)
        flavour_stats[flavour]["trials"] += 1
        flavour_stats[flavour]["fires"] += int(trial["fired"])
        best_variant_hist[trial["best_variant"]] += 1
        best_counts.append(trial["best_count"])
        cols["flavour"].append(flavour)
        cols["best_variant"].append(trial["best_variant"])
        cols["best_count"].append(trial["best_count"])
        cols["mu0"].append(round(trial["mu0"], 3))
        cols["sigma0"].append(round(trial["sigma0"], 3))
        cols["expected_max_order_stat"].append(round(trial["expected_max_order_stat"], 3))
        cols["corrected_margin_bar"].append(round(trial["corrected_margin_bar"], 3))
        cols["operative_bar"].append(round(trial["operative_bar"], 3))
        cols["fired"].append(bool(trial["fired"]))
        fires += int(trial["fired"])

    def _flavour_floor(fl: str) -> Dict[str, float]:
        """Distribution of best counts + own-null mu0 for one fabricated-corpus flavour — the
        empirical spurious-match floor of that flavour (run_canary L_fake-floor analogue)."""
        bc = [c for c, f in zip(cols["best_count"], cols["flavour"]) if f == fl]
        mu = [m for m, f in zip(cols["mu0"], cols["flavour"]) if f == fl]
        if not bc:
            return {}
        return {"best_count_mean": round(float(np.mean(bc)), 3),
                "best_count_std": round(float(np.std(bc, ddof=1)), 3) if len(bc) > 1 else 0.0,
                "best_count_p95": round(float(np.percentile(bc, 95)), 3),
                "own_null_mu0_mean": round(float(np.mean(mu)), 3)}

    rate = fires / B_trials if B_trials else 0.0
    cp_upper = _cp95_upper(fires, B_trials) if B_trials else 1.0
    false_fire = {
        "design": ("cherry-pick best of the 12-variant grid on fabricated LA-like corpora "
                   "(alternating banded-permuted-pool / lfake-markov flavours) vs the real KN "
                   "name list; each best graded against its own banded-map null at instrumented "
                   "n_eff (gate_null_calibration pattern)"),
        "B_trials": B_trials,
        "B_null_per_trial": B_null_trial,
        "n_eff_instrumented": log.n_eff,
        "fires": fires,
        "false_fire_rate": round(rate, 5),
        "clopper_pearson_onesided_95_upper": round(cp_upper, 5),
        "target": 0.05,
        "passes": bool(cp_upper <= 0.05),
        "per_flavour": {k: {"trials": v["trials"], "fires": v["fires"],
                            "rate": round(v["fires"] / v["trials"], 5) if v["trials"] else 0.0,
                            "clopper_pearson_onesided_95_upper":
                                round(_cp95_upper(v["fires"], v["trials"]), 5)
                                if v["trials"] else 1.0}
                        for k, v in flavour_stats.items()},
        "best_variant_histogram": dict(sorted(best_variant_hist.items())),
        "best_count_min_median_max": [int(np.min(best_counts)),
                                      float(np.median(best_counts)),
                                      int(np.max(best_counts))] if best_counts else None,
        "flavour_floors": {fl: _flavour_floor(fl) for fl in ("banded", "lfake")},
        "trials": cols,
    }

    calibration_green = bool(pc_fires_emax and false_fire["passes"])
    out = {
        "harness": "name_parallel_calibration",
        "phase": "5a — build + calibration only; the LA probe is a separately gated Phase 5b step",
        "articles_triggered": ["V (claim layers, L3 cap)", "VII (search receipt via CriterionLog)",
                               "VIII (effective_n = instrumented variant multiplicity)",
                               "IX (deflated bars)", "XI (single LB-decipherment lineage: "
                               "SRC-NAMESCOG collapses with SRC-DAMOS)",
                               "XII (S1/S2 strata built for the probe)"],
        "seed": seed,
        "fast": bool(fast),
        "params": {"B_pc_null": B_pc_null, "B_trials": B_trials,
                   "B_null_trial": B_null_trial, "alpha": 0.05, "n_bands": 4},
        "criterion_grid": [asdict(c) for c in grid],
        "primary_criterion": PRIMARY.name,
        "n_eff_variants": log.n_eff,
        "variants_evaluated": list(log.variants),
        "la_pool": la["diagnostics"],
        "la_pool_true_value_statistic": ("NOT_COMPUTED — the confirmatory LA run is gated behind "
                                         "the Phase 5b prereg (committed plan_hash) and a green "
                                         "calibration file (invariant 1, fail CLOSED)"),
        "names_cog": names_info["diagnostics"],
        "kn_join": join["diagnostics"],
        "strata_preview": {
            "s1_salgarella_darkblue_signs": len(load_salgarella_darkblue()),
            "s2_toponym_covered_signs": len(load_toponym_covered_signs()),
        },
        "positive_control": positive_control,
        "false_fire": false_fire,
        "calibration_green": calibration_green,
        "green_rule": ("positive control fires above the expected-max order-stat bar AND "
                       "false-fire Clopper–Pearson 95% upper <= 0.05"),
    }
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(_py(out), f, indent=2, ensure_ascii=False)
    return out


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Name-parallel probe: build + calibration (Phase 5a)")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--fast", action="store_true",
                   help="smoke-test sizes; recorded in the JSON (cannot impersonate the real run)")
    p.add_argument("--out", default=CALIBRATION_JSON)
    args = p.parse_args(list(argv) if argv is not None else None)
    r = run_calibration(seed=args.seed, fast=args.fast, out_path=args.out)
    print("== name-parallel calibration (Phase 5a) ==")
    lp, nc, kj = r["la_pool"], r["names_cog"], r["kn_join"]
    print(f"LA pool: {lp['types_ge_min_signs']} types >= {lp['min_signs']} signs -> "
          f"{lp['types_after_logogram_filter']} after logogram filter "
          f"(-{lp['excluded_logogram_types']}) -> {lp['pool_decodable_types']} decodable "
          f"(-{lp['excluded_undecodable_star_slots_1_3']} with *NN in slots 1-3)")
    print(f"names.cog: {nc['rows']} rows, {nc['glossed_rows']} glossed, "
          f"{nc['glossed_fully_decodable_ge3_rows']} fully-decodable >=3 "
          f"({nc['distinct_name_types']} distinct)")
    print(f"KN join: {kj['kn_names']} KN-attested names "
          f"(band {kj['sanity_band']}, in_band={kj['in_sanity_band']}); "
          f"attribution mismatch {kj['doc_attribution_mismatches']}/{kj['damos_docs']} docs")
    pc = r["positive_control"]
    print(f"positive control: m_obs={pc['m_obs']} vs E[max]={pc['bars']['expected_max_order_stat']:.2f} "
          f"/ corrected={pc['bars']['corrected_margin_bar']:.2f} "
          f"(mu0={pc['bars']['mu0']:.2f}, sigma0={pc['bars']['sigma0']:.2f}) -> "
          f"fires={pc['fires_above_expected_max']} (both bars: {pc['fires_above_both_bars']})")
    ff = r["false_fire"]
    print(f"false-fire: {ff['fires']}/{ff['B_trials']} = {ff['false_fire_rate']:.4f} "
          f"(CP95 upper {ff['clopper_pearson_onesided_95_upper']:.4f}, target <= 0.05, "
          f"passes={ff['passes']})")
    print(f"CALIBRATION_GREEN: {r['calibration_green']}  (fast={r['fast']})")
    print(f" -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
