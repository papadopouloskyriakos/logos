#!/usr/bin/env python3
"""metrology.py — Direction D: constraint-optimization over the Linear A ACCOUNTING tablets.

This is NUMERICAL / METROLOGICAL structure, NOT language. There is NO phonetic-value claim
anywhere in this module: a fraction SIGN is treated as an opaque categorical label whose unknown
RATIONAL VALUE in (0,1) is recovered from balance arithmetic. We never read a sign's meaning; we
solve it.

THE PROBLEM (and why the integer parse alone fails). An HT accounting tablet line is typically
``[recipient-word] [commodity-LOGOGRAM] [integer] [FRACTION-signs]`` and the document carries a
KU-RO ("total") line (sometimes per-commodity sub-totals). Summing the *integers* alone balanced
only a handful of tablets against their KU-RO total — the missing mass is the FRACTIONS plus the
commodity grouping. So we parse line items, treat each distinct fraction sign as an unknown, and
SOLVE the values that make the most accounts balance — exactly the Corazza-et-al.-2021 program,
done here from the public lineara.xyz transliterations.

THE CARDINAL RISK IS OVERFITTING. Fraction values fitted to make the TRAINING tablets balance are
*not a result*; they are a tautology (≈ a dozen free rationals can absorb a lot of arithmetic). The
honest headline is therefore HELD-OUT balance — the fraction of tablets NOT used to solve the values
that nonetheless balance EXACTLY — measured against a PERMUTATION NULL that shuffles the
sign→value assignment. If real ≈ null, the "solved" system does not generalize and we report the
null. (Four prior logos metrics turned out to be structural confounds caught only by exactly this
kind of held-out + null test; this module assumes it is the fifth until proven otherwise.)

WHAT THE SOLVER USES — AND DOES NOT. The fraction-sign LABEL is the editorial token string (the
vulgar-fraction gloss ``¹⁄₂`` / ``³⁄₄`` or the raw Aegean fraction glyph 𐝆/𐝃/𐝕). The solver only
ever sees that string as an opaque identifier; it recovers the value from the balance constraints
alone. The editorial *implied* numeric (parsing ``¹⁄₂``→1/2) and the published Corazza value are
computed SEPARATELY and used ONLY for the comparison report — never fed to the solve. Agreement is
therefore corroboration, not circularity at the solve step.

HONESTY CAVEAT WE CANNOT REMOVE. The editorial transliterations themselves embed an interpretation:
an editor who chose ``¹⁄₂`` for a damaged sign may have chosen it partly to make the account balance.
The held-out split controls *solver* overfitting and the permutation null controls *value-assignment*
specificity, but neither fully removes editorial circularity. This caveat is reported in every run.

Reference (CITED, NOT treated as ground truth): Corazza, M., Ferrara, S., Montecchi, B.,
Tamburini, F., & Valério, M. (2021). "The mathematical values of fraction signs in the Linear A
script: A computational, statistical and typological approach." Journal of Archaeological Science
125:105214. doi:10.1016/j.jas.2020.105214. They restricted to the LM I horizon to control system
drift; so do we. We COMPARE our independently-solved values to theirs; we do not assume them.

Pure stdlib + numpy, deterministic (seeded). The LLM never grades; this is arithmetic (invariant 4).
Imports nothing from scripts.verdict (invariant: signals only, confidence-capped elsewhere).
"""
from __future__ import annotations

import json
import os
import re
import unicodedata
from collections import Counter, defaultdict
from fractions import Fraction
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SILVER = os.path.join(ROOT, "corpus", "silver", "inscriptions_structured.json")
ONTOLOGY = os.path.join(ROOT, "corpus", "silver", "signs_ontology.json")

CITATION_CORAZZA = (
    "Corazza, Ferrara, Montecchi, Tamburini & Valério (2021), J. Archaeol. Sci. 125:105214 — "
    "'The mathematical values of fraction signs in the Linear A script'. Constraint programming over "
    "LM I accounts; values CITED for comparison, NOT assumed as ground truth."
)

# Published Corazza et al. 2021 fraction-sign values (CITED reference, NOT ground truth). Keyed by the
# conventional klasmatogram letter. H and A are flagged uncertain by the authors themselves. Composite
# signs are additive (JE = J+E = 3/4; DD = D+D = 1/3) — we record those explicitly too.
CORAZZA_2021: Dict[str, Fraction] = {
    "J": Fraction(1, 2), "E": Fraction(1, 4), "B": Fraction(1, 5), "D": Fraction(1, 6),
    "F": Fraction(1, 8), "K": Fraction(1, 10), "L2": Fraction(1, 20), "L3": Fraction(1, 30),
    "L4": Fraction(1, 40), "L6": Fraction(1, 60), "W": Fraction(2, 5), "X": Fraction(1, 12),
    "JE": Fraction(3, 4), "DD": Fraction(1, 3),
}
CORAZZA_2021_UNCERTAIN = {"H": Fraction(1, 16), "A": Fraction(1, 24)}

# --------------------------------------------------------------------------- #
# Token / fraction-sign recognition
# --------------------------------------------------------------------------- #
_NUM = re.compile(r"^\d+$")
_FRAC_SLASH = "⁄"  # ⁄
_VULGAR = set("½⅓⅔¼¾⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞⅐⅑⅒")
_SUP = {"⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5",
        "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9"}
_SUB = {"₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4", "₅": "5",
        "₆": "6", "₇": "7", "₈": "8", "₉": "9"}
_SINGLE_VULGAR = {
    "½": Fraction(1, 2), "⅓": Fraction(1, 3), "⅔": Fraction(2, 3), "¼": Fraction(1, 4),
    "¾": Fraction(3, 4), "⅕": Fraction(1, 5), "⅖": Fraction(2, 5), "⅗": Fraction(3, 5),
    "⅘": Fraction(4, 5), "⅙": Fraction(1, 6), "⅚": Fraction(5, 6), "⅛": Fraction(1, 8),
    "⅜": Fraction(3, 8), "⅝": Fraction(5, 8), "⅞": Fraction(7, 8), "⅐": Fraction(1, 7),
    "⅑": Fraction(1, 9), "⅒": Fraction(1, 10),
}
# The Linear A fraction / measure glyph series (Unicode A701..A732, U+10740..U+1075F). U+1076B has no
# Unicode name and is used as an ILLEGIBLE NUMBER on the tablets (e.g. HT67: '𐝫 / 𐝫 / KU-RO 402'), so
# it is deliberately EXCLUDED from the fraction set.
_AEG_FRAC_LO, _AEG_FRAC_HI = 0x10740, 0x1075F


def _is_aegean_fraction(s: str) -> bool:
    return bool(s) and all(_AEG_FRAC_LO <= ord(c) <= _AEG_FRAC_HI and unicodedata.name(c, "") for c in s)


def is_fraction_sign(raw: str) -> bool:
    """A fraction SIGN is a vulgar-fraction gloss (¹⁄₂, ³⁄₄, ½...), an Aegean fraction glyph
    (𐝆/𐝃/𐝕...), or the named 'double mina'. Star-numbers (*308), commodity logograms, the em-dash
    and illegible-number glyphs are NOT fractions."""
    if not raw:
        return False
    s = raw.replace("≈", "").strip()
    if not s:
        return False
    if s == "double mina":
        return True
    if _FRAC_SLASH in s:
        return True
    if all(c in _VULGAR for c in s):
        return True
    if _is_aegean_fraction(s):
        return True
    return False


def editorial_value(raw: str) -> Optional[Fraction]:
    """Parse the editorial *implied* numeric of a vulgar-fraction gloss (¹⁄₂→1/2). Returns None for
    Aegean-glyph-only labels and named 'double mina' (no editorial numeric). Used ONLY for the
    comparison report — never fed to the solver."""
    if not raw:
        return None
    s = raw.replace("≈", "").strip()
    if len(s) == 1 and s in _SINGLE_VULGAR:
        return _SINGLE_VULGAR[s]
    if _FRAC_SLASH in s:
        a, b = s.split(_FRAC_SLASH, 1)
        num = "".join(_SUP.get(c, c) for c in a)
        den = "".join(_SUB.get(c, c) for c in b)
        if num.isdigit() and den.isdigit() and int(den) != 0:
            return Fraction(int(num), int(den))
    return None


def fraction_letter(raw: str) -> Optional[str]:
    """Conventional klasmatogram letter for an Aegean fraction glyph (via its Unicode name, e.g.
    'LINEAR A SIGN A707 J' → 'J'), or for a vulgar gloss whose editorial value matches a Corazza
    letter. Returns None when no letter is determinable."""
    s = raw.replace("≈", "").strip()
    if _is_aegean_fraction(s) and len(s) == 1:
        nm = unicodedata.name(s, "")
        parts = nm.split()
        if parts:
            return parts[-1]
    ev = editorial_value(raw)
    if ev is not None:
        for letter, val in CORAZZA_2021.items():
            if val == ev:
                return letter
    return None


def corazza_value(raw: str) -> Optional[Fraction]:
    """Published Corazza-2021 value for a fraction sign, via its letter; None if not asserted there."""
    letter = fraction_letter(raw)
    if letter and letter in CORAZZA_2021:
        return CORAZZA_2021[letter]
    return None


# --------------------------------------------------------------------------- #
# Commodity logograms (from the ontology) — used for per-commodity sub-totals
# --------------------------------------------------------------------------- #
def load_commodities(ontology_path: str = ONTOLOGY) -> set:
    """Base commodity logogram labels (class == 'logogram') from the signs ontology. Ligatures
    collapse to their base (VIR+KA → VIR, GRA+PA → GRA)."""
    out = set()
    try:
        ont = json.load(open(ontology_path, encoding="utf-8"))
    except (OSError, ValueError):
        return out
    for v in ont.values():
        if isinstance(v, dict) and v.get("class") == "logogram":
            for t in v.get("diplomatic_tokens", []):
                out.add(t.split("+")[0].split("[")[0])
            fam = v.get("allograph_family", "").replace("LOGO:", "")
            if fam:
                out.add(fam.split("+")[0])
    return {c for c in out if c}


def _base_commodity(label: str, commodities: set) -> Optional[str]:
    b = label.split("+")[0].split("[")[0]
    return b if b in commodities else None


# --------------------------------------------------------------------------- #
# Loading + reconstructing the token stream from the public structured silver
# --------------------------------------------------------------------------- #
def _stream_to_tokens(stream: Sequence[dict]) -> List[dict]:
    """Normalise a silver `stream` into typed tokens: {'k':'label','s':str} | {'k':'num','v':int} |
    {'k':'frac','s':str} | {'k':'nl'} | {'k':'div'}. Fraction glosses live in the silver `other.raw`."""
    out: List[dict] = []
    for tok in stream:
        t = tok.get("t")
        if t == "word":
            out.append({"k": "label", "s": "-".join(tok.get("signs", []))})
        elif t == "num":
            out.append({"k": "num", "v": int(tok["v"])})
        elif t == "nl":
            out.append({"k": "nl"})
        elif t == "div":
            out.append({"k": "div"})
        elif t == "other":
            raw = tok.get("raw", "")
            if is_fraction_sign(raw):
                out.append({"k": "frac", "s": raw})
            # else: illegible number / star-number / em-dash — dropped (recorded as a parse gap)
    return out


def _matches_horizon(context: str, horizon: str) -> bool:
    if not horizon:
        return True
    c = (context or "").upper().replace(" ", "")
    return c.startswith(horizon.upper())


def load_tablets(path: str = SILVER, site_prefix: str = "HT",
                 horizon: str = "LMI", require_total: bool = True) -> List[dict]:
    """Load accounting tablets from the structured silver. ``site_prefix`` matches the tablet id
    prefix (HT = Haghia Triada); ``horizon`` restricts by the chronology in `context` (LM I per
    Corazza 2021). Only tablets carrying a KU-RO total are kept when ``require_total``."""
    data = json.load(open(path, encoding="utf-8"))
    out = []
    for rec in data:
        iid = str(rec.get("id", ""))
        if site_prefix and not iid.startswith(site_prefix):
            continue
        if not _matches_horizon(rec.get("context", ""), horizon):
            continue
        toks = _stream_to_tokens(rec.get("stream", []))
        if require_total and not any(t["k"] == "label" and t["s"] == "KU-RO" for t in toks):
            continue
        out.append({"doc": iid, "context": rec.get("context", ""), "tokens": toks})
    return out


# --------------------------------------------------------------------------- #
# Accounting parse: tablet -> balance units
# --------------------------------------------------------------------------- #
def parse_tablet(tablet: dict, commodities: set) -> List[dict]:
    """Parse one tablet's token stream into balance units.

    A balance unit = a KU-RO total line plus the line items it totals. Items accumulate (keyed by
    commodity) until a KU-RO closes them: a commodity-tagged ``KU-RO OLIV …`` totals that commodity's
    column; an untagged ``KU-RO …`` totals everything accumulated (single-commodity tablet). A line
    with no commodity inherits the current column commodity. KI-RO ("deficit") lines are recorded but
    do not themselves form a balance constraint.

    Returns units: {doc, commodity, total_int, total_fracs[], items:[(int,[frac,...]),...]}.
    """
    toks = tablet["tokens"]
    # split into lines on nl
    lines: List[List[dict]] = []
    cur: List[dict] = []
    for t in toks:
        if t["k"] == "nl":
            if cur:
                lines.append(cur)
                cur = []
        else:
            cur.append(t)
    if cur:
        lines.append(cur)

    acc: Dict[Optional[str], List[Tuple[int, List[str]]]] = defaultdict(list)
    order: List[Optional[str]] = []
    column_commodity: Optional[str] = None
    units: List[dict] = []

    def push(commod, ival, fracs):
        acc[commod].append((ival, list(fracs)))
        if commod not in order:
            order.append(commod)

    for ln in lines:
        labels = [t["s"] for t in ln if t["k"] == "label"]
        is_total = "KU-RO" in labels
        is_deficit = ("KI-RO" in labels) and not is_total
        commod_labels = [t["s"] for t in ln if t["k"] == "label"
                         and _base_commodity(t["s"], commodities)]
        commod = _base_commodity(commod_labels[0], commodities) if commod_labels else None
        ints = [t["v"] for t in ln if t["k"] == "num"]
        fracs = [t["s"] for t in ln if t["k"] == "frac"]

        if is_total:
            total_int = ints[0] if ints else 0
            if commod is not None and commod in acc:
                items = acc.pop(commod)
                order[:] = [o for o in order if o != commod]
            else:
                items = [it for cm in order for it in acc.get(cm, [])]
                acc.clear()
                order.clear()
            units.append({"doc": tablet["doc"], "commodity": commod,
                          "total_int": total_int, "total_fracs": fracs, "items": items})
        elif is_deficit:
            continue
        else:
            if commod is not None:
                column_commodity = commod
            use_c = commod if commod is not None else column_commodity
            if ints:
                push(use_c, ints[0], fracs)
            elif fracs:
                push(use_c, 0, fracs)
            # else: header / illegible line with no quantity — ignored
    return units


def residual_terms(unit: dict) -> Tuple[int, Dict[str, int]]:
    """Linear form of the balance constraint: ``const + Σ coef[sign]·value(sign) == 0``.
    const = Σ item integers − total integer; coef counts a sign +1 per item occurrence, −1 per
    total occurrence."""
    const = sum(v for v, _ in unit["items"]) - unit["total_int"]
    coef: Dict[str, int] = defaultdict(int)
    for _, ff in unit["items"]:
        for f in ff:
            coef[f] += 1
    for f in unit["total_fracs"]:
        coef[f] -= 1
    return const, {k: v for k, v in coef.items() if v != 0}


def is_fraction_bearing(unit: dict) -> bool:
    return bool(residual_terms(unit)[1])


def unit_balances(unit: dict, values: Dict[str, Fraction], tol: float = 1e-9) -> Optional[bool]:
    """Does the unit balance exactly under ``values``? None if a sign value is unknown (uncomputable).
    Integer-only units balance iff const == 0 (independent of any fraction value)."""
    const, coef = residual_terms(unit)
    if not coef:
        return const == 0
    total = Fraction(const)
    for sign, c in coef.items():
        if sign not in values:
            return None
        total += c * values[sign]
    return abs(float(total)) < tol


# --------------------------------------------------------------------------- #
# The fraction solve — robust max-constraint-satisfaction (consensus)
# --------------------------------------------------------------------------- #
def candidate_grid(max_den: int = 60) -> List[Fraction]:
    """Rational candidate values k/n in (0,1) with n over the Corazza denominator set."""
    dens = [d for d in (2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 30, 40, 60) if d <= max_den]
    vals = set()
    for n in dens:
        for k in range(1, n):
            vals.add(Fraction(k, n))
    return sorted(vals)


def _single_sign_hints(units: Sequence[dict]) -> Dict[str, Counter]:
    """Arithmetic warm-start hints: a constraint with exactly one distinct sign pins its value
    directly (const + coef·v == 0 ⇒ v = −const/coef). Pure arithmetic — no editorial input."""
    hints: Dict[str, Counter] = defaultdict(Counter)
    for u in units:
        const, coef = residual_terms(u)
        if len(coef) == 1:
            (sign, c), = coef.items()
            if c != 0:
                v = Fraction(-const, c)
                if 0 < v < 1:
                    hints[sign][v] += 1
    return hints


def _solve_exact(rows: Sequence[Tuple[Dict[str, int], int]], labels: Sequence[str],
                 defaults: Dict[str, Fraction]) -> Optional[Dict[str, Fraction]]:
    """Exact rational Gaussian elimination of ``Σ coef·val == rhs``. Free (undetermined) variables
    are set to ``defaults``; returns a particular solution dict, or None if the rows are
    inconsistent."""
    idx = {l: i for i, l in enumerate(labels)}
    n = len(labels)
    M = []
    for coef, rhs in rows:
        r = [Fraction(0)] * (n + 1)
        for s, c in coef.items():
            r[idx[s]] = Fraction(c)
        r[n] = Fraction(rhs)
        M.append(r)
    pivots: Dict[int, int] = {}
    pr = 0
    for col in range(n):
        piv = next((r for r in range(pr, len(M)) if M[r][col] != 0), None)
        if piv is None:
            continue
        M[pr], M[piv] = M[piv], M[pr]
        pv = M[pr][col]
        M[pr] = [x / pv for x in M[pr]]
        for r in range(len(M)):
            if r != pr and M[r][col] != 0:
                f = M[r][col]
                M[r] = [a - f * b for a, b in zip(M[r], M[pr])]
        pivots[col] = pr
        pr += 1
    for r in range(len(M)):
        if all(M[r][c] == 0 for c in range(n)) and M[r][n] != 0:
            return None
    val = {l: defaults.get(l, Fraction(0)) for l in labels}
    for col, r in pivots.items():
        s = M[r][n]
        for c in range(n):
            if c != col and M[r][c] != 0:
                s -= M[r][c] * val[labels[c]]
        val[labels[col]] = s
    return val


def consensus_solve(units: Sequence[dict], grid: Optional[List[Fraction]] = None,
                    restarts: int = 400, seed: int = 0,
                    ) -> Tuple[Dict[str, Fraction], int]:
    """Find fraction-sign values maximising the number of EXACTLY-balanced constraints (the task's
    'satisfy the most constraints'), via RANSAC over exact rational solves.

    The balance constraints are linear equations over the unknown sign values. A genuinely-balanced
    subset of tablets is mutually consistent and shares one rational solution; unbalanced tablets
    (scribal error / misparse) are outliers. So we repeatedly sample a small consistent subset of
    constraints, solve it EXACTLY over the rationals, and keep the solution that satisfies the most
    of ALL constraints — robust to outliers in a way least-squares is not (one bad tablet cannot drag
    the solution). A final coordinate-ascent polish over the rational grid fills any sign the sampled
    systems left free. The value 0 / out-of-(0,1) means 'no consistent value found' (reported as
    undetermined). Deterministic for a fixed seed."""
    if grid is None:
        grid = candidate_grid()
    labels = sorted({s for u in units for s in residual_terms(u)[1]})
    if not labels:
        return {}, 0
    constraints = [residual_terms(u) for u in units]
    constraints = [(const, coef) for const, coef in constraints if coef]
    hints = _single_sign_hints(units)
    defaults = {l: (hints[l].most_common(1)[0][0] if l in hints else Fraction(0)) for l in labels}
    rng = np.random.default_rng(seed)

    def satisfied(values):
        return sum(1 for u in units if unit_balances(u, values) is True)

    def consider(values, best):
        bv, bn = best
        n = satisfied(values)
        return (dict(values), n) if n > bn else best

    best = consider(defaults, ({}, -1))
    sample_size = min(len(constraints), max(1, len(labels)))
    for _ in range(restarts):
        k = min(len(constraints), int(rng.integers(1, sample_size + 1)))
        pick = rng.choice(len(constraints), size=k, replace=False)
        rows = [(constraints[i][1], -constraints[i][0]) for i in pick]
        sol = _solve_exact(rows, labels, defaults)
        if sol is None:
            continue
        # only accept determined values inside (0,1); out-of-range -> fall back to default
        clean = {l: (sol[l] if 0 < sol[l] < 1 else defaults[l]) for l in labels}
        best = consider(clean, best)
    # coordinate-ascent polish on the best solution
    values = dict(best[0]) if best[0] else dict(defaults)
    cand = [Fraction(0)] + list(grid)
    for _ in range(8):
        improved = False
        for l in labels:
            base = satisfied(values)
            best_c, best_cn = values[l], base
            for c in cand:
                if c == values[l]:
                    continue
                values[l] = c
                n = satisfied(values)
                if n > best_cn:
                    best_cn, best_c = n, c
            values[l] = best_c
            if best_cn > base:
                improved = True
        if not improved:
            break
    best = consider(values, best)
    return best[0], best[1]


# --------------------------------------------------------------------------- #
# Held-out validation (grouped K-fold by document) + permutation null
# --------------------------------------------------------------------------- #
def _grouped_folds(docs: Sequence[str], k: int, seed: int) -> List[List[str]]:
    uniq = sorted(set(docs))
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(uniq))
    folds: List[List[str]] = [[] for _ in range(min(k, len(uniq)))]
    for i, idx in enumerate(perm):
        folds[i % len(folds)].append(uniq[idx])
    return [f for f in folds if f]


def heldout_balance(units: Sequence[dict], k: int = 5, seed: int = 0,
                    solver_seed: int = 0) -> dict:
    """Leave-a-fold-of-documents-out: solve fractions on TRAIN docs only, measure the fraction of
    TEST units that balance EXACTLY. Reported overall and on the fraction-bearing subset (where the
    fraction values actually matter). Grouping is by document so no tablet straddles train/test."""
    docs = [u["doc"] for u in units]
    folds = _grouped_folds(docs, k, seed)
    train_fb_bal = train_fb_tot = 0
    test_fb_bal = test_fb_tot = 0
    test_all_bal = test_all_tot = 0
    test_fb_computable = 0
    fold_solutions: List[Dict[str, Fraction]] = []
    fold_test_units: List[List[dict]] = []
    for fold in folds:
        test_docs = set(fold)
        train = [u for u in units if u["doc"] not in test_docs]
        test = [u for u in units if u["doc"] in test_docs]
        train_fb = [u for u in train if is_fraction_bearing(u)]
        values, _ = consensus_solve(train_fb, seed=solver_seed)
        fold_solutions.append(values)
        fold_test_units.append(test)
        for u in train_fb:
            train_fb_tot += 1
            if unit_balances(u, values) is True:
                train_fb_bal += 1
        for u in test:
            res = unit_balances(u, values)
            test_all_tot += 1
            if res is True:
                test_all_bal += 1
            if is_fraction_bearing(u):
                test_fb_tot += 1
                if res is not None:
                    test_fb_computable += 1
                if res is True:
                    test_fb_bal += 1
    rate = lambda a, b: (a / b) if b else None
    return {
        "scheme": "grouped_kfold_by_document",
        "k": len(folds),
        "train_fraction_balance_rate": rate(train_fb_bal, train_fb_tot),
        "heldout_fraction_balance_rate": rate(test_fb_bal, test_fb_tot),
        "heldout_overall_balance_rate": rate(test_all_bal, test_all_tot),
        "n_test_fraction_bearing": test_fb_tot,
        "n_test_fraction_computable": test_fb_computable,
        "n_test_units": test_all_tot,
        "_fold_solutions": fold_solutions,
        "_fold_test_units": fold_test_units,
    }


def permutation_null(heldout: dict, n_perms: int = 500, seed: int = 0) -> dict:
    """Confound guard: re-evaluate held-out fraction balance after SHUFFLING the sign→value
    assignment within each fold's solved solution. A real fraction system must balance held-out
    tablets FAR above this null. p = (1 + #{null ≥ real}) / (1 + n_perms)."""
    real_bal = real_tot = 0
    for values, test in zip(heldout["_fold_solutions"], heldout["_fold_test_units"]):
        for u in test:
            if is_fraction_bearing(u):
                real_tot += 1
                if unit_balances(u, values) is True:
                    real_bal += 1
    real_rate = (real_bal / real_tot) if real_tot else 0.0

    rng = np.random.default_rng(seed)
    null_rates = []
    for _ in range(n_perms):
        nb = 0
        for values, test in zip(heldout["_fold_solutions"], heldout["_fold_test_units"]):
            labels = list(values.keys())
            if labels:
                shuffled = list(values.values())
                rng.shuffle(shuffled)
                perm_vals = dict(zip(labels, shuffled))
            else:
                perm_vals = {}
            for u in test:
                if is_fraction_bearing(u) and unit_balances(u, perm_vals) is True:
                    nb += 1
        null_rates.append(nb / real_tot if real_tot else 0.0)
    null_arr = np.array(null_rates) if null_rates else np.array([0.0])
    p = (1 + int(np.sum(null_arr >= real_rate))) / (1 + len(null_arr))
    return {
        "method": "fraction_value_shuffle",
        "n_perms": n_perms,
        "real_heldout_fraction_balance": real_rate,
        "n_test_fraction_bearing": real_tot,
        "null_mean": float(null_arr.mean()),
        "null_max": float(null_arr.max()),
        "p_value": p,
        "separated": bool(real_rate > null_arr.max() and real_tot > 0),
    }


# --------------------------------------------------------------------------- #
# Corazza comparison
# --------------------------------------------------------------------------- #
def compare_to_corazza(solved: Dict[str, Fraction]) -> List[dict]:
    rows = []
    for sign in sorted(solved):
        sv = solved[sign]
        ev = editorial_value(sign)
        cv = corazza_value(sign)
        rows.append({
            "sign": sign,
            "unicode": [unicodedata.name(c, hex(ord(c))) for c in sign.replace("≈", "").strip()],
            "letter": fraction_letter(sign),
            "solved_value": str(sv) if sv != 0 else "undetermined",
            "solved_float": round(float(sv), 6) if sv != 0 else None,
            "editorial_value": str(ev) if ev is not None else None,
            "corazza_2021_value": str(cv) if cv is not None else None,
            "agrees_with_corazza": (cv is not None and sv == cv),
            "agrees_with_editorial": (ev is not None and sv == ev),
        })
    return rows


# --------------------------------------------------------------------------- #
# Synthetic accounting corpus (for tests + demo): planted fraction values
# --------------------------------------------------------------------------- #
def synthetic_corpus(planted: Dict[str, Fraction], n_tablets: int = 30, seed: int = 0,
                     noise_frac: float = 0.0) -> List[dict]:
    """Build tablets (in the loader's token format) whose line items balance their KU-RO total EXACTLY
    under the PLANTED fraction values, so a correct solver recovers ``planted`` and held-out tablets
    balance. Construction mirrors real clean accounts (e.g. HT104's ``2·¹⁄₂ == 1``): each tablet
    targets one or two signs, placing a whole-number-summing group of that sign across its items so
    the fractional mass closes to an integer carried by the KU-RO total. ``noise_frac`` corrupts that
    fraction of tablets (off-by-one total) to mimic scribal error / our misreadings. Deterministic."""
    rng = np.random.default_rng(seed)
    signs = list(planted)
    tablets = []
    for t in range(n_tablets):
        # target sign(s): cycle so every sign is exercised; occasionally a 2-sign constraint
        s1 = signs[t % len(signs)]
        m1 = planted[s1].denominator           # m1 * planted[s1] is a whole number
        whole = m1 * planted[s1]
        placements = [s1] * m1
        if rng.random() < 0.35 and len(signs) > 1:      # add a 2nd sign -> multi-sign constraint
            s2 = signs[int(rng.integers(len(signs)))]
            m2 = planted[s2].denominator
            whole += m2 * planted[s2]
            placements += [s2] * m2
        rng.shuffle(placements)
        n_items = max(2, min(len(placements), int(rng.integers(2, 6))))
        # distribute placements across items round-robin
        buckets: List[List[str]] = [[] for _ in range(n_items)]
        for i, s in enumerate(placements):
            buckets[i % n_items].append(s)
        toks: List[dict] = []
        sum_int = 0
        for b in buckets:
            base = int(rng.integers(0, 40))
            sum_int += base
            toks.append({"k": "label", "s": f"RE-CI-{int(rng.integers(0,999)):03d}"})
            toks.append({"k": "num", "v": base})
            for s in b:
                toks.append({"k": "frac", "s": s})
            toks.append({"k": "nl"})
        total_int = sum_int + int(whole)
        if noise_frac and rng.random() < noise_frac:
            total_int += 1                      # corrupt: no longer balances
        toks.append({"k": "label", "s": "KU-RO"})
        toks.append({"k": "num", "v": total_int})
        tablets.append({"doc": f"SYN{t:03d}", "context": "LMIB", "tokens": toks})
    return tablets


# --------------------------------------------------------------------------- #
# Top-level analysis
# --------------------------------------------------------------------------- #
def analyze(tablets: Sequence[dict], commodities: Optional[set] = None,
            k: int = 5, n_perms: int = 500, seed: int = 0) -> dict:
    """Full Direction-D pipeline: parse → solve → held-out → null → Corazza comparison."""
    if commodities is None:
        commodities = load_commodities()
    units: List[dict] = []
    for tab in tablets:
        units.extend(parse_tablet(tab, commodities))

    fb_units = [u for u in units if is_fraction_bearing(u)]
    int_units = [u for u in units if not is_fraction_bearing(u)]
    int_bal = sum(1 for u in int_units if unit_balances(u, {}) is True)

    # fraction inventory
    inv: Dict[str, int] = Counter()
    for u in units:
        for f in u["total_fracs"]:
            inv[f] += 1
        for _, ff in u["items"]:
            for f in ff:
                inv[f] += 1
    inventory = {sign: {
        "count": cnt,
        "editorial_value": str(editorial_value(sign)) if editorial_value(sign) is not None else None,
        "corazza_letter": fraction_letter(sign),
        "corazza_2021_value": str(corazza_value(sign)) if corazza_value(sign) is not None else None,
    } for sign, cnt in sorted(inv.items(), key=lambda kv: -kv[1])}

    # solve on the full corpus (the reported "solved values"); held-out is the honest headline
    solved, n_sat = consensus_solve(fb_units, seed=seed)

    # parse coverage: a unit "fraction-resolvable" if its integer residual is within reach of its
    # fraction signs (|const| <= #fraction signs); these are the constraints fractions can balance.
    n_resolvable = 0
    for u in fb_units:
        const, coef = residual_terms(u)
        nfr = sum(abs(c) for c in coef.values())
        if abs(const) <= nfr:
            n_resolvable += 1

    heldout = heldout_balance(units, k=k, seed=seed, solver_seed=seed)
    null = permutation_null(heldout, n_perms=n_perms, seed=seed)

    # power check (mirrors the morphostat no-power escape): the held-out fraction test is only
    # meaningful with enough fraction-bearing TEST units.
    is_powered = heldout["n_test_fraction_bearing"] >= 5
    power_reason = (None if is_powered else
                    f"only {heldout['n_test_fraction_bearing']} fraction-bearing held-out units — "
                    f"too few to power the generalization test (corpus underdetermined)")

    solved_report = {sign: {
        "value": str(val) if val != 0 else "undetermined",
        "float": round(float(val), 6) if val != 0 else None,
    } for sign, val in sorted(solved.items())}

    report = {
        "direction": "D — metrology / accounting constraint-optimization",
        "no_phonetic_claim": True,
        "corpus": {
            "n_tablets": len(tablets),
            "n_balance_units": len(units),
            "n_documents": len({u["doc"] for u in units}),
        },
        "parse_coverage": {
            "n_units": len(units),
            "n_integer_only": len(int_units),
            "n_integer_only_balanced": int_bal,
            "integer_balance_rate": (int_bal / len(int_units)) if int_units else None,
            "n_fraction_bearing": len(fb_units),
            "n_fraction_resolvable": n_resolvable,
        },
        "fraction_inventory": inventory,
        "solve": {
            "method": "consensus_max_constraint_satisfaction",
            "n_fraction_constraints": len(fb_units),
            "n_constraints_satisfied": n_sat,
            "solved_values": solved_report,
        },
        "heldout": {k2: v2 for k2, v2 in heldout.items() if not k2.startswith("_")},
        "heldout_is_powered": is_powered,
        "heldout_power_reason": power_reason,
        "null": null,
        "corazza_comparison": compare_to_corazza(solved),
        "caveats": [
            "OVERFITTING is the cardinal risk: the headline is HELD-OUT balance vs the permutation "
            "null, NOT train balance.",
            "EDITORIAL CIRCULARITY cannot be fully removed: the transliterated fraction glosses may "
            "themselves have been chosen partly to balance accounts; held-out + null control solver "
            "overfitting and value-assignment specificity but not this.",
            "NO phonetic / linguistic claim is made — this is numerical/metrological structure only.",
            "Solved values are recovered from balance arithmetic alone; the fraction SIGN is an opaque "
            "label. Editorial and Corazza values are used ONLY for comparison, never for the solve.",
        ],
        "citations": [CITATION_CORAZZA],
    }
    return report


def run(path: str = SILVER, site_prefix: str = "HT", horizon: str = "LMI",
        k: int = 5, n_perms: int = 500, seed: int = 0) -> dict:
    tablets = load_tablets(path, site_prefix=site_prefix, horizon=horizon)
    rep = analyze(tablets, k=k, n_perms=n_perms, seed=seed)
    rep["corpus"]["site_prefix"] = site_prefix
    rep["corpus"]["horizon"] = horizon
    return rep


# --------------------------------------------------------------------------- #
# Headline
# --------------------------------------------------------------------------- #
def headline(report: dict) -> str:
    pc = report["parse_coverage"]
    ho = report["heldout"]
    nl = report["null"]
    bits = [
        f"{report['corpus']['n_documents']} docs / {pc['n_units']} balance units; "
        f"integer balance {pc['n_integer_only_balanced']}/{pc['n_integer_only']}.",
        f"{pc['n_fraction_bearing']} fraction-bearing constraints, "
        f"{report['solve']['n_constraints_satisfied']} satisfied by the solved system.",
    ]
    if not report["heldout_is_powered"]:
        bits.append(f"HELD-OUT fraction test UNDERPOWERED ({report['heldout_power_reason']}).")
    rfb = ho.get("heldout_fraction_balance_rate")
    bits.append(
        f"held-out fraction balance="
        f"{(round(rfb, 3) if rfb is not None else None)} vs null mean="
        f"{round(nl['null_mean'], 3)} (max {round(nl['null_max'], 3)}), p={round(nl['p_value'], 3)}, "
        f"separated={nl['separated']}.")
    agree = [r['sign'] for r in report['corazza_comparison'] if r['agrees_with_corazza']]
    bits.append("Corazza agreement on: " + (", ".join(agree) if agree else "none of the solved signs."))
    return " ".join(bits)


def main(argv: Optional[Sequence[str]] = None) -> int:
    import argparse
    p = argparse.ArgumentParser(description="Direction D — Linear A metrology constraint-optimization")
    p.add_argument("--path", default=SILVER, help="structured silver corpus json")
    p.add_argument("--site", default="HT", help="tablet id prefix (HT = Haghia Triada)")
    p.add_argument("--horizon", default="LMI", help="chronology prefix restriction (LM I per Corazza)")
    p.add_argument("--k", type=int, default=5, help="held-out folds (grouped by document)")
    p.add_argument("--n-perms", type=int, default=500, help="permutation-null draws")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--demo", action="store_true", help="run on a synthetic planted corpus instead")
    p.add_argument("--json", action="store_true", help="emit the full JSON report")
    args = p.parse_args(argv)

    if args.demo:
        planted = {"¹⁄₂": Fraction(1, 2), "¹⁄₄": Fraction(1, 4), "³⁄₄": Fraction(3, 4),
                   "¹⁄₃": Fraction(1, 3)}
        tablets = synthetic_corpus(planted, n_tablets=40, seed=args.seed, noise_frac=0.15)
        rep = analyze(tablets, k=args.k, n_perms=args.n_perms, seed=args.seed)
        rep["corpus"]["site_prefix"] = "SYNTHETIC"
    else:
        if not os.path.exists(args.path):
            print(f"corpus not found at {args.path}; run scripts/corpus_io_structured.py first, "
                  f"or pass --demo")
            return 2
        rep = run(args.path, site_prefix=args.site, horizon=args.horizon,
                  k=args.k, n_perms=args.n_perms, seed=args.seed)

    print("HEADLINE:", headline(rep))
    if args.json:
        print(json.dumps(rep, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
