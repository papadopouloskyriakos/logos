#!/usr/bin/env python3
"""morphology.py — Direction A: unsupervised Linear A MORPHOLOGY / SEGMENTATION induction.

THE RESULT THIS MODULE CAN PRODUCE IS STRUCTURAL, NEVER PHONETIC. It asks one question an Aegean
epigrapher would accept: do the scribe's own word-divisions exhibit RECURRING, PRODUCTIVE morphology
(affixes at word edges that attach to many distinct stems across independent inscriptions, above a
within-word permutation null and surviving multiplicity correction)? It makes **NO phonetic-value
claim** anywhere — a confirmed affix is a paradigmatic (positional/productive) object, not a sound.

WHY THIS MODULE IS CONFOUND-PROOF BY CONSTRUCTION (the contamination arc lesson: three metrics turned
out to be structural confounds — forced-1.0, baseline-ceiling, coverage — each caught only by
adversarial verification + null tests). Here the guards are baked in, not bolted on:

  1. The pre-registered affixes (docs/prereg-morphology-2026-06-30.md) are FROZEN. This module tests
     EXACTLY those, mapped faithfully to GORILA sign sequences; it never adds/tunes a prediction.
  2. Every affix is scored against the within-WORD sign-order permutation null (Nair 2026, reused from
     nulls.within_form_permutation): the null preserves each word's sign multiset and length while
     destroying position, so an affix only scores if its sign sits at the edge MORE than its own
     frequency/content would give by chance. This neutralises the "common sign" confound directly.
  3. The morphostat PRODUCTIVITY GATE (>= min_stems DISTINCT stems) is reused: a single libation
     formula word copied across many tablets bears its "affix" on ONE stem and earns no credit — only
     genuine, productive affixation (varied residual) scores. This neutralises the formulaic-repetition
     confound (the dominant false positive on a short, formulaic corpus).
  4. Multiplicity: the panel of N affixes is deflated with the logos §B.3 order-statistic bar
     (logos_stats.expected_max_order_stat) + a Sidak corrected p across N. Target p < 0.01 corrected.
  5. NULL FALSIFICATION (the headline honesty gate): the SAME panel is run on (a) a sign-order-shuffled
     corpus and (b) an L_fake fabricated corpus (lfake.py, markov-calibrated to the sign-sequence
     statistics). The pre-registered affixes MUST NOT survive there. If the real confirmation rate is
     not clearly above both floors, the method has NO POWER and we DO NOT claim morphology — we say so.
  6. NO_POWER is a first-class verdict (S_morph-style, refinement F.1): when the corpus cannot
     discriminate an affix (too few distinct stems / inscriptions, or a degenerate null), the verdict
     is NO_POWER, never a fake REFUTE.

Two independent segmenters form an ENSEMBLE (never one cherry-picked model): Morfessor Baseline and a
Goldwater-style Dirichlet-process unigram segmenter (Viterbi-MAP variant, pure numpy). They are
externally validated by WORD-BOUNDARY RECOVERY against the scribe's divisions with LEAVE-ONE-SITE-OUT
splits (formulaic dependence makes ordinary k-fold optimistic). A segmenter that cannot beat the
random-boundary baseline is reported and NOT used.

Citations: Goldwater, Griffiths & Johnson 2009 (Bayesian word segmentation, DP unigram); Creutz &
Lagus 2007 / Virpioja et al. 2013 (Morfessor Baseline); Nair 2026 arXiv:2604.17828 (within-form
permutation null; synthetic-generator floor); Bailey & Lopez de Prado 2014 (deflated / order-statistic
multiplicity bar, via logos_stats); B. Davis 2013/2014 (libation-formula word order, the i-*301 stem);
R. Thomas 2020 (libation-formula affixes); Duhoux / Valerio (nominal affixes). Pure numpy/stdlib +
morfessor; deterministic (seeded). Does NOT import scripts.verdict (invariant 2/4).
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from statistics import NormalDist
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

_NORMAL = NormalDist()

# make `scripts.comparison` importable when run as a plain script (cron-style)
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from scripts.comparison.nulls import within_form_permutation  # noqa: E402  (Nair within-form null)
from scripts.comparison import lfake  # noqa: E402
from scripts import logos_stats  # noqa: E402  (deflated / order-statistic multiplicity bar)

DEFAULT_SILVER = os.path.join(_ROOT, "corpus", "silver", "inscriptions_structured.json")

CITATION_GOLDWATER = (
    "Goldwater, Griffiths & Johnson 2009 — Bayesian framework for word segmentation (Dirichlet-process "
    "unigram lexicon); here the deterministic Viterbi-MAP variant (DP base measure + concentration)."
)
CITATION_MORFESSOR = (
    "Creutz & Lagus 2007 / Virpioja et al. 2013 — Morfessor Baseline minimum-description-length "
    "morph segmentation (unsupervised)."
)
CITATION_NULLS = (
    "Nair 2026 arXiv:2604.17828 — within-form fixed-seed permutation null (reused from nulls.py): "
    "preserves each word's sign multiset and length, destroys position; the confound guard for the "
    "affix-edge test. Same generator supplies the sign-order-shuffled falsification corpus."
)
CITATION_DSR = (
    "Bailey & Lopez de Prado 2014 (via logos_stats.expected_max_order_stat) — §B.3 deflated bar / "
    "order-statistic multiplicity correction for the number of affixes tested."
)
CITATION_PREREG = (
    "docs/prereg-morphology-2026-06-30.md (FROZEN) — Davis 2013/2014 (i-*301 stem, V-S-O), Thomas 2020 "
    "(libation affixes a-/ja-/ta-/na-/t-; -wa/-u/-ja/-ti/-nu/-e/-de/-ka), Duhoux/Valerio (i-; -te/-ti)."
)

# NO PHONETIC CLAIM — stated once, echoed in every report.
NO_PHONETIC_CLAIM = (
    "STRUCTURAL RESULT ONLY. A CONFIRM means a sign-subsequence recurs productively at a word edge "
    "above the within-word permutation null and the multiplicity bar; it is a paradigmatic / "
    "positional object. This module makes NO phonetic-value (sound) claim for any sign or affix."
)


# --------------------------------------------------------------------------- #
# The corpus record + loader
# --------------------------------------------------------------------------- #
@dataclass
class Inscription:
    """One inscription: a list of words, each a list of GORILA sign labels (the scribe's divisions)."""
    iid: str
    site: str
    words: List[List[str]]

    @property
    def signs(self) -> List[str]:
        return [s for w in self.words for s in w]


def load_corpus(path: str = DEFAULT_SILVER) -> List[Inscription]:
    """Load the structured silver (scripts/corpus_io_structured.py output). Each record's `words`
    field is the scribe's word division = the segmentation ground truth."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    out: List[Inscription] = []
    for d in data:
        words = [[str(s) for s in w] for w in d.get("words", []) if w]
        if not words:
            continue
        out.append(Inscription(iid=str(d.get("id", "")), site=str(d.get("site", "")), words=words))
    return out


def word_length_distribution(corpus: Sequence[Inscription]) -> Dict[str, object]:
    """Signs-per-word distribution + the Fuls (2015) reconciliation (generated, not hand-written;
    invariant 12). Reconciles the Direction-A finding's 'short, mostly 1-2-sign words' premise against
    Fuls 2015's reported 3.3-sign average — BOTH hold; they count different denominators. On the
    word-tokens the morphology test consumes, words are short (median/mode 1, ~76% are <=2 signs), which
    is exactly why morphology is not separable from bigram order. Fuls's 3.3 is recovered (~3.07) only on
    DISTINCT MULTI-sign words, i.e. after excluding the ~56% single-sign administrative/abbreviation
    tokens (cf. the abbreviation channel, prereg-morphology-salgarella-addendum) and de-duplicating."""
    import statistics
    from collections import Counter
    tok = [len(w) for ins in corpus for w in ins.words]
    distinct = {"-".join(w) for ins in corpus for w in ins.words}
    dl = [len(w.split("-")) for w in distinct]
    n = len(tok)

    def _mean(xs: List[int]) -> float:
        return (sum(xs) / len(xs)) if xs else 0.0

    return {
        "n_tokens": n,
        "n_distinct": len(distinct),
        "token_mean": _mean(tok),
        "token_median": int(statistics.median(tok)),
        "token_mode": Counter(tok).most_common(1)[0][0],
        "pct_len1": (sum(1 for x in tok if x == 1) / n) if n else 0.0,
        "pct_len_le2": (sum(1 for x in tok if x <= 2) / n) if n else 0.0,
        "pct_len_le3": (sum(1 for x in tok if x <= 3) / n) if n else 0.0,
        "token_mean_ge2": _mean([x for x in tok if x >= 2]),
        "distinct_mean": _mean(dl),
        "distinct_mean_ge2": _mean([x for x in dl if x >= 2]),
        "fuls_2015_reported": 3.3,
        "histogram": dict(sorted(Counter(tok).items())),
    }


# --------------------------------------------------------------------------- #
# Sign <-> private-use-char codec.  Each distinct GORILA sign becomes ONE character so that
# (a) Morfessor and the DP segmenter treat a sign as an atom, and (b) the Nair within_form_permutation
# (which shuffles CHARACTERS) shuffles SIGNS — a genuine reuse of the null, not a re-implementation.
# --------------------------------------------------------------------------- #
_PUA_BASE = 0xE000


class SignCodec:
    def __init__(self, signs: Sequence[str]):
        uniq = sorted(set(signs))
        if len(uniq) > 6000:                      # PUA block safety (we never approach this)
            raise ValueError("too many distinct signs for the PUA codec")
        self.to_char: Dict[str, str] = {s: chr(_PUA_BASE + i) for i, s in enumerate(uniq)}
        self.to_sign: Dict[str, str] = {c: s for s, c in self.to_char.items()}

    def enc_word(self, word: Sequence[str]) -> str:
        return "".join(self.to_char[s] for s in word if s in self.to_char)

    def dec_word(self, s: str) -> List[str]:
        return [self.to_sign[c] for c in s if c in self.to_sign]

    @classmethod
    def from_corpus(cls, corpus: Sequence[Inscription]) -> "SignCodec":
        return cls([s for ins in corpus for s in ins.signs])


# --------------------------------------------------------------------------- #
# THE PRE-REGISTERED AFFIX PANEL — FROZEN.  Test EXACTLY these (docs/prereg-morphology-2026-06-30.md);
# never add/tune. Each `sign_seqs` is a list of acceptable sign-tuples (a SET for fuzzy/broadened
# predictions). `edge` in {prefix, suffix, stem}. Mapping is faithful to the GORILA labels:
#   a- = sign A word-initial; ja- = JA; ta- = TA; na- = NA; i- = I; -wa = WA word-final; etc.
#   t- (Thomas, a fuzzy CONSONANT prefix): BROADENED to the t-series syllabograms {TA,TE,TI,TO,TU,TA2}
#      word-initial — stated as broadened (we cannot test a bare consonant on a syllabary).
#   -te/-ti (Duhoux/Valerio): the SET {TE,TI} word-final (broadened across the two written vowels).
#   i-*301 (Davis): the two-sign stem [I,*301] appearing INTERIOR with surrounding (variable) affixes.
# --------------------------------------------------------------------------- #
T_SERIES = [("TA",), ("TE",), ("TI",), ("TO",), ("TU",), ("TA₂",)]  # TA2 = TA-subscript-2 variant


@dataclass(frozen=True)
class Affix:
    affix: str                                   # transliteration label
    edge: str                                    # 'prefix' | 'suffix' | 'stem'
    sign_seqs: Tuple[Tuple[str, ...], ...]       # acceptable sign-tuples (a set for fuzzy predictions)
    sign_seq: str                                # human-readable
    source: str
    broadened: bool = False


PREREG_AFFIXES: Tuple[Affix, ...] = (
    # H1a (Davis): the stable verb stem i-*301 carrying changing affixes.
    Affix("i-*301", "stem", (("I", "*301"),), "I-*301", "Davis 2013/2014"),
    # H2 prefixes (Thomas)
    Affix("a-", "prefix", (("A",),), "A", "Thomas 2020"),
    Affix("ja-", "prefix", (("JA",),), "JA", "Thomas 2020"),
    Affix("ta-", "prefix", (("TA",),), "TA", "Thomas 2020"),
    Affix("na-", "prefix", (("NA",),), "NA", "Thomas 2020"),
    Affix("t-", "prefix", tuple(T_SERIES), "{TA,TE,TI,TO,TU,TA₂}", "Thomas 2020", broadened=True),
    # H2 suffixes (Thomas)
    Affix("-wa", "suffix", (("WA",),), "WA", "Thomas 2020"),
    Affix("-u", "suffix", (("U",),), "U", "Thomas 2020"),
    Affix("-ja", "suffix", (("JA",),), "JA", "Thomas 2020"),
    Affix("-ti", "suffix", (("TI",),), "TI", "Thomas 2020"),
    Affix("-nu", "suffix", (("NU",),), "NU", "Thomas 2020"),
    Affix("-e", "suffix", (("E",),), "E", "Thomas 2020"),
    Affix("-de", "suffix", (("DE",),), "DE", "Thomas 2020"),
    Affix("-ka", "suffix", (("KA",),), "KA", "Thomas 2020"),
    # H3 nominal (Duhoux / Valerio)
    Affix("i-", "prefix", (("I",),), "I", "Duhoux/Valerio"),
    Affix("-te/-ti", "suffix", (("TE",), ("TI",)), "{TE,TI}", "Duhoux/Valerio", broadened=True),
)


def prereg_affix_labels() -> List[str]:
    """The frozen affix labels (for reporting / pre-registration echo)."""
    return [a.affix for a in PREREG_AFFIXES]


def prereg_sign_sequences() -> List[str]:
    """The frozen affixes rendered as edge-tagged sign sequences (the exact predictions scored)."""
    out = []
    for a in PREREG_AFFIXES:
        tag = {"prefix": "#-", "suffix": "-#", "stem": "..#.."}[a.edge]
        if a.edge == "prefix":
            out.append(f"{a.sign_seq}- ({a.affix})")
        elif a.edge == "suffix":
            out.append(f"-{a.sign_seq} ({a.affix})")
        else:
            out.append(f"...{a.sign_seq}... ({a.affix})")
    return out


# --------------------------------------------------------------------------- #
# Affix attestation on the scribe's words.  `affix_residual` returns a hashable STEM/residual that
# must VARY for the affix to count as productive morphology (the morphostat productivity logic):
#   prefix A on [A,KA,RU] -> residual ('P', KA, RU)       (the stem after stripping the prefix)
#   suffix WA on [..,WA]  -> residual ('S', ...)          (the stem before stripping the suffix)
#   stem [I,*301] interior -> residual ('M', before_tuple, after_tuple)  (the VARIABLE affixes)
# None means the word does not bear the affix (as a PROPER edge — never the whole word).
# --------------------------------------------------------------------------- #
def affix_residual(word: Sequence[str], affix: Affix) -> Optional[tuple]:
    w = tuple(word)
    n = len(w)
    if affix.edge == "prefix":
        for seq in affix.sign_seqs:
            k = len(seq)
            if n > k and w[:k] == seq:            # proper prefix (word longer than the affix)
                return ("P",) + w[k:]
        return None
    if affix.edge == "suffix":
        for seq in affix.sign_seqs:
            k = len(seq)
            if n > k and w[-k:] == seq:           # proper suffix
                return ("S",) + w[:-k]
        return None
    # stem (interior): the sign-subsequence appears with material on at least one side (an affix
    # environment). Productivity is measured over the VARIABLE surrounding affixes.
    for seq in affix.sign_seqs:
        k = len(seq)
        for i in range(0, n - k + 1):
            if w[i:i + k] == seq:
                before, after = w[:i], w[i + k:]
                if before or after:               # must carry at least one affix (not a bare stem word)
                    return ("M", before, after)
    return None


def _bearing(corpus: Sequence[Inscription], affix: Affix) -> Tuple[int, set, int]:
    """(n_distinct_inscriptions_bearing, set_of_distinct_residuals, n_words_bearing)."""
    n_insc = 0
    residuals: set = set()
    n_words = 0
    for ins in corpus:
        bears = False
        for w in ins.words:
            r = affix_residual(w, affix)
            if r is not None:
                residuals.add(r)
                n_words += 1
                bears = True
        if bears:
            n_insc += 1
    return n_insc, residuals, n_words


def affix_rate(corpus: Sequence[Inscription], affix: Affix, min_stems: int = 2) -> float:
    """Productivity-gated cross-inscription recurrence rate (morphostat §A.2 logic, at sign level):
    fraction of INDEPENDENT inscriptions bearing the affix productively, 0 unless it attaches to
    >= min_stems DISTINCT stems (else: lexical repetition, no credit)."""
    m = len(corpus)
    if m == 0:
        return 0.0
    n_insc, residuals, _ = _bearing(corpus, affix)
    if len(residuals) < min_stems:
        return 0.0
    return n_insc / m


# --------------------------------------------------------------------------- #
# The within-WORD sign-order permutation null (Nair, reused). Each draw permutes the SIGNS inside
# every word (per inscription, deterministic per-inscription seed) via the codec + within_form_permutation,
# preserving each word's sign multiset and length while destroying position.
# --------------------------------------------------------------------------- #
def shuffle_corpus(corpus: Sequence[Inscription], codec: SignCodec, seed: int) -> List[Inscription]:
    out: List[Inscription] = []
    for k, ins in enumerate(corpus):
        enc = [codec.enc_word(w) for w in ins.words]
        perm = within_form_permutation(enc, seed=(seed * 100003 + k) % (2 ** 32))
        out.append(Inscription(ins.iid, ins.site, [codec.dec_word(s) for s in perm]))
    return out


def _null_rates(corpus: Sequence[Inscription], affix: Affix, codec: SignCodec,
                n_null: int, seed: int, min_stems: int = 2) -> List[float]:
    return [affix_rate(shuffle_corpus(corpus, codec, seed + d), affix, min_stems=min_stems)
            for d in range(n_null)]


# --------------------------------------------------------------------------- #
# THE PRE-REGISTERED AFFIX TEST (per affix) — verdict in CONFIRM / REFUTE / NO_POWER.
# --------------------------------------------------------------------------- #
def _affix_verdict_row(affix: Affix, observed: float, null: np.ndarray, n_insc: int,
                       n_distinct_stems: int, n_words: int, *, n_trials: int, min_stems: int,
                       min_inscriptions: int, alpha: float) -> Dict[str, object]:
    """Build one affix's verdict row from its observed rate + its (shared) within-word null draws.
    Separated so test_affix (single affix) and run_affix_panel (shared draws) share EXACTLY one
    verdict rule — no divergence between the unit-tested path and the headline path."""
    null_mean = float(null.mean()) if len(null) else 0.0
    null_std = float(null.std(ddof=1)) if len(null) > 1 else 0.0
    z = (observed - null_mean) / null_std if null_std > 1e-9 else 0.0
    nt = logos_stats.dsr_trial_count(1, n_trials)         # >= n_trials, never below 1
    deflated_bar = logos_stats.expected_max_order_stat(null_mean, null_std, nt)  # §B.3 order-stat bar

    # Two p-values, reported together (honesty: neither alone decides):
    #   empirical_raw_p — distribution-FREE permutation p; robust but resolution-limited to 1/(n_null+1).
    #   per_test_p      — normal tail of the EMPIRICALLY-standardized rate (only the tail shape is
    #                     approximated; the rate is an average over ~all inscriptions so it is ~normal
    #                     by CLT). This is the one that can represent the small p a strong affix earns.
    empirical_raw_p = ((1.0 + float(np.sum(null >= observed - 1e-12))) / (len(null) + 1.0)
                       if len(null) else 1.0)
    per_test_p = _NORMAL.cdf(-z) if null_std > 1e-9 else 1.0
    # Sidak FWER correction across the WHOLE panel (the multiplicity to deflate for)
    dsr_corrected_p = float(min(1.0, max(0.0, 1.0 - (1.0 - per_test_p) ** nt)))

    # --- power: can the corpus discriminate THIS affix at all? (S_morph F.1 escape) ----------------
    has_power = (null_std > 1e-9) and (n_distinct_stems >= min_stems) and (n_insc >= min_inscriptions)

    if not has_power:
        reason_bits = []
        if n_words == 0:
            reason_bits.append("affix unattested in the corpus")
        if n_distinct_stems < min_stems:
            reason_bits.append(f"only {n_distinct_stems} distinct stem(s) (< {min_stems}): cannot "
                               f"assess productivity")
        if n_insc < min_inscriptions:
            reason_bits.append(f"borne by {n_insc} inscription(s) (< {min_inscriptions}): cannot "
                               f"test cross-inscription recurrence")
        if null_std <= 1e-9:
            reason_bits.append("within-word null degenerate (no spread): no discrimination")
        verdict = "NO_POWER"
        reason = ("corpus cannot discriminate this affix (" + "; ".join(reason_bits) + ") — "
                  "reported as no-power, NOT a refutation.")
    elif (observed > deflated_bar and dsr_corrected_p < alpha and empirical_raw_p < 0.05):
        # three guards: above the §B.3 order-stat bar (statistic space), Sidak corrected p < alpha,
        # AND the distribution-free permutation null also rejects (observed beats ~all null draws).
        verdict = "CONFIRM"
        reason = (f"productive recurrence {observed:.3f} clears the deflated bar {deflated_bar:.3f} "
                  f"(z={z:.2f}), corrected p={dsr_corrected_p:.3g} < {alpha}, and permutation "
                  f"p={empirical_raw_p:.3g}: recurs at the predicted edge on {n_distinct_stems} "
                  f"distinct stems across {n_insc} inscriptions.")
    else:
        verdict = "REFUTE"
        reason = (f"powered but NOT above the bar: observed {observed:.3f} vs deflated bar "
                  f"{deflated_bar:.3f} (z={z:.2f}), corrected p={dsr_corrected_p:.3g}, permutation "
                  f"p={empirical_raw_p:.3g} — the affix does not recur at the predicted edge above "
                  f"the within-word null (a real negative).")

    return {
        "affix": affix.affix,
        "sign_seq": affix.sign_seq,
        "edge": affix.edge,
        "source": affix.source,
        "broadened": affix.broadened,
        "n_distinct_stems": n_distinct_stems,
        "n_inscriptions_bearing": n_insc,
        "n_words_bearing": n_words,
        "observed_rate": float(observed),
        "null_mean": null_mean,
        "null_std": null_std,
        "z": float(z),
        "per_test_p": float(per_test_p),
        "empirical_raw_p": float(empirical_raw_p),
        "deflated_bar": float(deflated_bar),
        "dsr_corrected_p": float(dsr_corrected_p),
        "n_trials": int(nt),
        "has_power": bool(has_power),
        "verdict": verdict,
        "reason": reason,
    }


def test_affix(corpus: Sequence[Inscription], affix: Affix, codec: SignCodec, *,
               n_trials: int, n_null: int = 200, seed: int = 0, min_stems: int = 2,
               min_inscriptions: int = 2, alpha: float = 0.01) -> Dict[str, object]:
    """Score ONE pre-registered affix against the within-word permutation null + the §B.3 deflated
    multiplicity bar. `n_trials` = TOTAL affixes in the panel (the multiplicity to deflate for)."""
    n_insc, residuals, n_words = _bearing(corpus, affix)
    observed = affix_rate(corpus, affix, min_stems=min_stems)
    null = np.asarray(_null_rates(corpus, affix, codec, n_null, seed, min_stems), dtype=float)
    return _affix_verdict_row(affix, observed, null, n_insc, len(residuals), n_words,
                              n_trials=n_trials, min_stems=min_stems,
                              min_inscriptions=min_inscriptions, alpha=alpha)


def run_affix_panel(corpus: Sequence[Inscription], codec: Optional[SignCodec] = None, *,
                    affixes: Sequence[Affix] = PREREG_AFFIXES, n_null: int = 200, seed: int = 0,
                    min_stems: int = 2, min_inscriptions: int = 2,
                    alpha: float = 0.01) -> Dict[str, object]:
    """Run the full FROZEN pre-registered panel; multiplicity-deflate for the number of affixes.

    Null draws are SHARED across affixes: the corpus is sign-order-shuffled once per draw and ALL
    affixes are scored on that same shuffled realization. This is both ~N_affix faster and cleaner —
    every affix is standardized against the identical null realizations (one common multiplicity
    family), exactly as the §B.3 order-statistic bar assumes."""
    codec = codec or SignCodec.from_corpus(corpus)
    n_trials = len(affixes)
    # observed + bearing per affix
    bearing = {a.affix: _bearing(corpus, a) for a in affixes}
    observed = {a.affix: affix_rate(corpus, a, min_stems=min_stems) for a in affixes}
    # shared within-word null draws (shuffle the whole corpus once per draw; score every affix on it)
    null_lists: Dict[str, List[float]] = {a.affix: [] for a in affixes}
    for d in range(n_null):
        draw = shuffle_corpus(corpus, codec, seed + d)
        for a in affixes:
            null_lists[a.affix].append(affix_rate(draw, a, min_stems=min_stems))
    rows = []
    for a in affixes:
        n_insc, residuals, n_words = bearing[a.affix]
        rows.append(_affix_verdict_row(
            a, observed[a.affix], np.asarray(null_lists[a.affix], dtype=float),
            n_insc, len(residuals), n_words, n_trials=n_trials, min_stems=min_stems,
            min_inscriptions=min_inscriptions, alpha=alpha))
    counts = Counter(r["verdict"] for r in rows)
    n_confirm = counts.get("CONFIRM", 0)
    return {
        "n_inscriptions": len(corpus),
        "n_affixes_tested": n_trials,
        "affixes": rows,
        "verdict_counts": dict(counts),
        "n_confirm": n_confirm,
        "confirm_rate": n_confirm / n_trials if n_trials else 0.0,
        "confirmed_affixes": [r["affix"] for r in rows if r["verdict"] == "CONFIRM"],
        "alpha": alpha,
    }


# --------------------------------------------------------------------------- #
# NULL FALSIFICATION (the headline honesty gate): run the SAME panel on (a) a sign-order-shuffled
# corpus and (b) an L_fake fabricated corpus. The pre-registered affixes MUST NOT survive there.
# --------------------------------------------------------------------------- #
def build_lfake_corpus(corpus: Sequence[Inscription], codec: SignCodec,
                       seed: int = 0) -> List[Inscription]:
    """A fabricated corpus calibrated (markov, on the sign-bigram + start/end statistics) to the real
    sign sequences, then assembled into inscriptions matching the real word-count distribution. It
    has NO genuine morphology; if the pre-registered affixes 'confirm' here, the apparent morphology
    is a sign-statistics echo (no power) — this is L_fake as a conservative false-positive FLOOR."""
    enc_words = [codec.enc_word(w) for ins in corpus for w in ins.words if w]
    enc_words = [w for w in enc_words if w]
    cfg = lfake.calibrate_to(enc_words, mode="markov")
    gen = lfake.LFakeGenerator(cfg, seed=seed)
    # generate a pool of fabricated forms (>= the number of real words) to draw inscriptions from
    n_words_total = sum(len(ins.words) for ins in corpus)
    pool = [e["form"] for e in gen.generate_lexicon(n=max(64, n_words_total), with_glosses=False)]
    if not pool:
        return []
    rng = np.random.default_rng(seed + 777)
    out: List[Inscription] = []
    pi = 0
    for ins in corpus:                            # match the real per-inscription word counts
        k = len(ins.words)
        words = []
        for _ in range(k):
            form = pool[pi % len(pool)]
            pi += 1
            words.append(codec.dec_word(form))
        words = [w for w in words if w] or [codec.dec_word(pool[int(rng.integers(0, len(pool)))])]
        out.append(Inscription(f"LF_{ins.iid}", "L_fake", words))
    return out


def null_falsification(corpus: Sequence[Inscription], codec: Optional[SignCodec] = None, *,
                       affixes: Sequence[Affix] = PREREG_AFFIXES, n_null: int = 120, seed: int = 0,
                       n_shuffle: int = 1, n_lfake: int = 1, alpha: float = 0.01,
                       real: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    """Compare the affix-confirmation rate on REAL vs sign-order-SHUFFLE vs L_FAKE corpora.

    The shuffle/L_fake corpora carry no genuine morphology, so the pre-registered affixes must NOT
    confirm there. If REAL ~= the floors, the method has no power and we DO NOT claim morphology.

    Pass a precomputed ``real`` panel (run_affix_panel output) to keep the headline IDENTICAL to the
    detailed affix table; otherwise it is computed here at ``n_null``.
    """
    codec = codec or SignCodec.from_corpus(corpus)

    if real is None:
        real = run_affix_panel(corpus, codec, affixes=affixes, n_null=n_null, seed=seed, alpha=alpha)

    shuffle_rates: List[float] = []
    shuffle_confirms: List[int] = []
    for i in range(max(1, n_shuffle)):
        sh = shuffle_corpus(corpus, codec, seed=seed + 13 + i)
        r = run_affix_panel(sh, codec, affixes=affixes, n_null=n_null, seed=seed + 13 + i, alpha=alpha)
        shuffle_rates.append(r["confirm_rate"])
        shuffle_confirms.append(r["n_confirm"])

    real_word_set = {"-".join(w) for ins in corpus for w in ins.words}
    lfake_rates: List[float] = []
    lfake_confirms: List[int] = []
    lfake_overlap: List[float] = []           # transparency: fabricated words must not be real words
    for i in range(max(1, n_lfake)):
        lf = build_lfake_corpus(corpus, codec, seed=seed + 29 + i)
        r = run_affix_panel(lf, codec, affixes=affixes, n_null=n_null, seed=seed + 29 + i, alpha=alpha)
        lfake_rates.append(r["confirm_rate"])
        lfake_confirms.append(r["n_confirm"])
        lf_words = ["-".join(w) for ins in lf for w in ins.words]
        lfake_overlap.append(sum(1 for w in lf_words if w in real_word_set) / max(len(lf_words), 1))

    real_rate = real["confirm_rate"]
    shuffle_rate = float(np.mean(shuffle_rates)) if shuffle_rates else 0.0
    lfake_rate = float(np.mean(lfake_rates)) if lfake_rates else 0.0
    floor = max(shuffle_rate, lfake_rate)

    # honesty gate: the method has power for morphology only if REAL is CLEARLY above BOTH floors.
    #   SHUFFLE  destroys ALL within-word position (symmetric) -> the floor for "is there ANY edge
    #            structure". L_FAKE (markov) preserves the 1st-order sign-transition + word-initial
    #            statistics -> the stronger floor for "is the structure BEYOND a bigram model".
    # Taking the conservative MAX(shuffle, lfake) means a CONFIRM survives only structure a bigram
    # model cannot manufacture (the contamination-arc lesson: an apparent signal a fabricated corpus
    # reproduces is not a real one).
    has_morphology_power = (real["n_confirm"] >= 1) and (real_rate > floor + 1e-9)
    beats_shuffle = real_rate > shuffle_rate + 1e-9
    beats_lfake = real_rate > lfake_rate + 1e-9
    if has_morphology_power:
        statement = (f"REAL confirms {real['n_confirm']}/{real['n_affixes_tested']} pre-registered "
                     f"affixes (rate {real_rate:.3f}) ABOVE the shuffle floor ({shuffle_rate:.3f}) and "
                     f"the L_fake floor ({lfake_rate:.3f}). The pre-registered morphology is a "
                     f"structural signal beyond what a bigram model reproduces. " + NO_PHONETIC_CLAIM)
    elif beats_shuffle and not beats_lfake:
        statement = (f"REAL ({real_rate:.3f}) beats the shuffle floor ({shuffle_rate:.3f}) — there IS "
                     f"edge structure — but NOT the L_fake bigram floor ({lfake_rate:.3f}): the "
                     f"apparent affixation is fully reproducible by a 1st-order sign-transition model "
                     f"(the short, mostly 1-2-sign words make 'morphology' and 'bigram order' "
                     f"indistinguishable). NO POWER to claim morphology beyond sign-statistics; "
                     f"report the null. DO NOT claim morphology.")
    else:
        statement = (f"REAL confirmation rate ({real_rate:.3f}) is NOT clearly above the shuffle "
                     f"({shuffle_rate:.3f}) / L_fake ({lfake_rate:.3f}) floors -> the affix test has "
                     f"NO POWER to distinguish real morphology from sign-statistics here. "
                     f"DO NOT claim morphology; report the null.")
    return {
        "real": real,
        "real_confirm_rate": real_rate,
        "real_confirmed_affixes": real["confirmed_affixes"],
        "shuffle_confirm_rate": shuffle_rate,
        "shuffle_confirms": shuffle_confirms,
        "lfake_confirm_rate": lfake_rate,
        "lfake_confirms": lfake_confirms,
        "lfake_audit": {
            "calibration": "markov (sign-bigram + word-initial start distribution)",
            "lexical_overlap_rate_with_real": float(np.mean(lfake_overlap)) if lfake_overlap else 0.0,
            "note": "L_fake is a CONSERVATIVE floor: it preserves the real sign-transition statistics "
                    "so any affix it reproduces is a 1st-order sign-statistic, not morphology. "
                    "Overlap with real words must be ~0 (fabricated, not memorised).",
        },
        "floor": floor,
        "beats_shuffle_floor": bool(beats_shuffle),
        "beats_lfake_floor": bool(beats_lfake),
        "has_morphology_power": bool(has_morphology_power),
        "honesty_statement": statement,
    }


# --------------------------------------------------------------------------- #
# SEGMENTERS — the ensemble (never one cherry-picked model).
#   (1) Morfessor Baseline (MDL).
#   (2) A Goldwater-style DP unigram segmenter (Viterbi-MAP variant, pure numpy).
# Each predicts word boundaries in an UNSEGMENTED encoded sign-stream.
# --------------------------------------------------------------------------- #
class DPUnigramSegmenter:
    """Dirichlet-process unigram word segmenter (Goldwater et al. 2009), deterministic Viterbi-MAP
    variant. A word w has DP-smoothed probability  P(w) = (count[w] + alpha * P0(w)) / (N + alpha),
    with a base measure P0(w) = p_boundary * prod_char (1 - p_boundary)^(len-1) * (1/V)^len that
    penalises long / many morphs (the prior that prevents the trivial all-one-word or all-singletons
    solutions). Inference: iterate Viterbi segmentation of every utterance under the current lexicon,
    re-estimating counts (a hard-EM / MAP approximation to the Gibbs sampler — deterministic, fast)."""

    def __init__(self, alpha: float = 2.0, p_boundary: float = 0.5, max_len: int = 8,
                 iters: int = 8, seed: int = 0):
        self.alpha = float(alpha)
        self.p_boundary = float(p_boundary)
        self.max_len = int(max_len)
        self.iters = int(iters)
        self.seed = int(seed)
        self.counts: Counter = Counter()
        self.total = 0
        self.vocab = 1

    def _p0(self, w: str) -> float:
        L = len(w)
        if L <= 0:
            return 1e-12
        return self.p_boundary * ((1.0 - self.p_boundary) ** (L - 1)) * ((1.0 / self.vocab) ** L)

    def _logp_word(self, w: str) -> float:
        p = (self.counts.get(w, 0) + self.alpha * self._p0(w)) / (self.total + self.alpha)
        return float(np.log(p + 1e-300))

    def _viterbi(self, u: str) -> List[str]:
        n = len(u)
        if n == 0:
            return []
        best = [-1e300] * (n + 1)
        back = [0] * (n + 1)
        best[0] = 0.0
        for i in range(1, n + 1):
            lo = max(0, i - self.max_len)
            for j in range(lo, i):
                cand = best[j] + self._logp_word(u[j:i])
                if cand > best[i]:
                    best[i] = cand
                    back[i] = j
        # backtrace
        segs: List[str] = []
        i = n
        while i > 0:
            j = back[i]
            segs.append(u[j:i])
            i = j
        segs.reverse()
        return segs

    def fit(self, utterances: Sequence[str]) -> "DPUnigramSegmenter":
        utts = [u for u in utterances if u]
        self.vocab = max(1, len({c for u in utts for c in u}))
        # init: every utterance is one whole word (conservative under-segmentation)
        self.counts = Counter(utts)
        self.total = sum(self.counts.values())
        for _ in range(self.iters):
            new: Counter = Counter()
            for u in utts:
                for w in self._viterbi(u):
                    new[w] += 1
            if new == self.counts:
                break
            self.counts = new
            self.total = sum(self.counts.values())
        return self

    def segment(self, utterance: str) -> List[str]:
        return self._viterbi(utterance)

    def boundaries(self, utterance: str) -> List[int]:
        """Internal boundary positions (cut after index p-1, i.e. between morph[k-1] and morph[k])."""
        segs = self.segment(utterance)
        out, pos = [], 0
        for s in segs[:-1]:
            pos += len(s)
            out.append(pos)
        return out


class MorfessorSegmenter:
    """Thin wrapper over Morfessor Baseline for boundary recovery (graceful if morfessor absent)."""

    def __init__(self, seed: int = 0):
        self.seed = int(seed)
        self.model = None
        self.available = False

    def fit(self, utterances: Sequence[str]) -> "MorfessorSegmenter":
        try:
            import morfessor
            import morfessor.utils
        except Exception:
            self.available = False
            return self
        utts = [u for u in utterances if u]
        if not utts:
            self.available = False
            return self
        data = [(c, w) for w, c in Counter(utts).items()]
        model = morfessor.BaselineModel()
        model.load_data(data)
        # deterministic batch training; silence the progress bar (dots) + logging.
        # Morfessor's train_batch shuffles compounds via the stdlib `random` module, so its
        # segmentation is NOT reproducible unless we seed that module here (the wrapper's `seed`
        # was previously stored but never applied — the source of ±0.01-0.02 drift in the
        # descriptive boundary-recovery / morpheme-inventory numbers across identical re-runs).
        import logging
        import random as _random
        _random.seed(self.seed)
        logging.getLogger("morfessor").setLevel(logging.ERROR)
        morfessor.utils.show_progress_bar = False
        try:
            model.train_batch()
        except Exception:
            self.available = False
            return self
        self.model = model
        self.available = True
        return self

    def segment(self, utterance: str) -> List[str]:
        if not self.available or self.model is None or not utterance:
            return [utterance] if utterance else []
        morphs, _ = self.model.viterbi_segment(utterance)
        return list(morphs)

    def boundaries(self, utterance: str) -> List[int]:
        segs = self.segment(utterance)
        out, pos = [], 0
        for s in segs[:-1]:
            pos += len(s)
            out.append(pos)
        return out


def random_boundaries(utterance: str, rate: float, rng: np.random.Generator) -> List[int]:
    """Random-boundary baseline: each of the (len-1) internal positions is a boundary w.p. `rate`."""
    n = len(utterance)
    return [p for p in range(1, n) if rng.random() < rate]


# --------------------------------------------------------------------------- #
# WORD-BOUNDARY RECOVERY (validates the METHOD): predict boundaries in the unsegmented stream, score
# precision/recall/F1 against the scribe's true word divisions, LEAVE-ONE-SITE-OUT externalization.
# --------------------------------------------------------------------------- #
def true_boundaries(words: Sequence[Sequence[str]]) -> Tuple[str, List[int]]:
    """Return (encoded-stream-length-as-stream, true internal boundary positions). Positions are cut
    points after the cumulative sign count of each word except the last."""
    bnds, pos = [], 0
    for w in words[:-1]:
        pos += len(w)
        bnds.append(pos)
    return bnds, sum(len(w) for w in words)


def _prf(pred: set, true: set) -> Tuple[float, float, float, int, int, int]:
    tp = len(pred & true)
    fp = len(pred - true)
    fn = len(true - pred)
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return prec, rec, f1, tp, fp, fn


def _boundary_rate(corpus: Sequence[Inscription]) -> float:
    """Empirical fraction of internal stream positions that are scribe word-boundaries (for the
    random baseline + as the natural under/over-segmentation reference)."""
    bnd = pos = 0
    for ins in corpus:
        n = len(ins.signs)
        if n <= 1:
            continue
        bnd += len(ins.words) - 1
        pos += n - 1
    return bnd / pos if pos else 0.0


def _score_segmenter_on(test: Sequence[Inscription], codec: SignCodec, segmenter) -> Dict[str, float]:
    tp = fp = fn = 0
    for ins in test:
        stream = codec.enc_word(ins.signs)
        if len(stream) <= 1:
            continue
        true_b, _ = true_boundaries(ins.words)
        pred_b = segmenter.boundaries(stream)
        _, _, _, a, b, c = _prf(set(pred_b), set(true_b))
        tp += a; fp += b; fn += c
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return {"precision": prec, "recall": rec, "f1": f1, "tp": tp, "fp": fp, "fn": fn}


def _score_random_on(test: Sequence[Inscription], codec: SignCodec, rate: float,
                     rng: np.random.Generator) -> Dict[str, float]:
    tp = fp = fn = 0
    for ins in test:
        stream = codec.enc_word(ins.signs)
        if len(stream) <= 1:
            continue
        true_b, _ = true_boundaries(ins.words)
        pred_b = random_boundaries(stream, rate, rng)
        _, _, _, a, b, c = _prf(set(pred_b), set(true_b))
        tp += a; fp += b; fn += c
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return {"precision": prec, "recall": rec, "f1": f1, "tp": tp, "fp": fp, "fn": fn}


def boundary_recovery(corpus: Sequence[Inscription], codec: Optional[SignCodec] = None, *,
                      seed: int = 0, min_site_size: int = 1, dp_iters: int = 6,
                      use_morfessor: bool = True) -> Dict[str, object]:
    """LEAVE-ONE-SITE-OUT word-boundary recovery for each segmenter + the random baseline.

    For each site: train the segmenters on ALL OTHER sites' inscriptions, predict boundaries on the
    held-out site, accumulate micro tp/fp/fn. Macro = mean of per-fold F1; micro = pooled F1. A
    segmenter that cannot beat the random-boundary baseline (micro F1) is flagged `beats_random=False`
    and SHOULD NOT be used downstream.
    """
    codec = codec or SignCodec.from_corpus(corpus)
    by_site: Dict[str, List[Inscription]] = defaultdict(list)
    for ins in corpus:
        by_site[ins.site or "(unknown)"].append(ins)
    sites = [s for s, ins in by_site.items() if len(ins) >= min_site_size]

    base_rate = _boundary_rate(corpus)
    rng = np.random.default_rng(seed)

    seg_names = ["dp_unigram"] + (["morfessor"] if use_morfessor else [])
    micro = {nm: {"tp": 0, "fp": 0, "fn": 0} for nm in seg_names}
    micro_rand = {"tp": 0, "fp": 0, "fn": 0}
    per_site: Dict[str, dict] = {}
    macro_f1: Dict[str, List[float]] = {nm: [] for nm in seg_names + ["random"]}

    for site in sorted(sites):
        train = [ins for ins in corpus if ins.site != site]
        test = by_site[site]
        train_utts = [codec.enc_word(ins.signs) for ins in train if len(ins.signs) >= 1]

        segmenters = {"dp_unigram": DPUnigramSegmenter(iters=dp_iters, seed=seed).fit(train_utts)}
        if use_morfessor:
            segmenters["morfessor"] = MorfessorSegmenter(seed=seed).fit(train_utts)

        site_row = {}
        for nm, seg in segmenters.items():
            sc = _score_segmenter_on(test, codec, seg)
            micro[nm]["tp"] += sc["tp"]; micro[nm]["fp"] += sc["fp"]; micro[nm]["fn"] += sc["fn"]
            macro_f1[nm].append(sc["f1"])
            site_row[nm] = {"f1": round(sc["f1"], 4), "precision": round(sc["precision"], 4),
                            "recall": round(sc["recall"], 4)}
        # random baseline (same held-out site, predicting at the TRAIN boundary rate) — scored ONCE,
        # the same per-fold draw feeds both the macro (per-site F1) and the micro (pooled) totals.
        train_rate = _boundary_rate(train)
        scr = _score_random_on(test, codec, train_rate, rng)
        micro_rand["tp"] += scr["tp"]; micro_rand["fp"] += scr["fp"]; micro_rand["fn"] += scr["fn"]
        macro_f1["random"].append(scr["f1"])
        site_row["random"] = {"f1": round(scr["f1"], 4)}
        site_row["n_test"] = len(test)
        per_site[site] = site_row

    def _f1(d):
        prec = d["tp"] / (d["tp"] + d["fp"]) if (d["tp"] + d["fp"]) else 0.0
        rec = d["tp"] / (d["tp"] + d["fn"]) if (d["tp"] + d["fn"]) else 0.0
        return 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0, prec, rec

    segmenter_summary = {}
    rand_f1, rand_p, rand_r = _f1(micro_rand)
    for nm in seg_names:
        f1, p, r = _f1(micro[nm])
        segmenter_summary[nm] = {
            "micro_f1": round(f1, 4), "micro_precision": round(p, 4), "micro_recall": round(r, 4),
            "macro_f1": round(float(np.mean(macro_f1[nm])) if macro_f1[nm] else 0.0, 4),
            "beats_random": bool(f1 > rand_f1),
        }
    return {
        "n_sites": len(sites),
        "boundary_base_rate": round(base_rate, 4),
        "random_baseline": {"micro_f1": round(rand_f1, 4), "micro_precision": round(rand_p, 4),
                            "micro_recall": round(rand_r, 4),
                            "macro_f1": round(float(np.mean(macro_f1["random"]))
                                              if macro_f1["random"] else 0.0, 4)},
        "segmenters": segmenter_summary,
        "usable_segmenters": [nm for nm in seg_names if segmenter_summary[nm]["beats_random"]],
        "per_site": per_site,
        "note": "Leave-one-site-out (NOT k-fold: formulaic dependence). A segmenter that cannot beat "
                "the random-boundary baseline is flagged beats_random=False and is not used.",
    }


# --------------------------------------------------------------------------- #
# MORPHEME INDUCTION — run both segmenters on the WORD list -> a morpheme inventory + segmentations.
# --------------------------------------------------------------------------- #
def induce_morphemes(corpus: Sequence[Inscription], codec: Optional[SignCodec] = None, *,
                     seed: int = 0, dp_iters: int = 8, top_k: int = 30,
                     use_morfessor: bool = True) -> Dict[str, object]:
    """Train each segmenter on the WORD list (words = sign sequences) and report the induced morpheme
    inventory (recurring word-internal sign-subsequences) + ensemble agreement on per-word splits."""
    codec = codec or SignCodec.from_corpus(corpus)
    words = [w for ins in corpus for w in ins.words if w]
    enc_words = [codec.enc_word(w) for w in words]
    enc_unique = sorted(set(enc_words))

    dp = DPUnigramSegmenter(iters=dp_iters, seed=seed).fit(enc_words)
    segmenters = {"dp_unigram": dp}
    if use_morfessor:
        mf = MorfessorSegmenter(seed=seed).fit(enc_words)
        if mf.available:
            segmenters["morfessor"] = mf

    inventories: Dict[str, List[Tuple[str, int]]] = {}
    splitsets: Dict[str, Dict[str, Tuple[int, ...]]] = {}
    for nm, seg in segmenters.items():
        inv: Counter = Counter()
        splits: Dict[str, Tuple[int, ...]] = {}
        for ew in enc_unique:
            morphs = seg.segment(ew)
            # boundary positions for this word (interior cut points)
            pos, cuts = 0, []
            for mm in morphs[:-1]:
                pos += len(mm)
                cuts.append(pos)
            splits[ew] = tuple(cuts)
            for mm in morphs:
                if len(mm) >= 1:
                    inv["-".join(codec.dec_word(mm))] += 1
        # keep only morphemes that recur (>=2) — a hapax morph is not an inventory item
        inventories[nm] = [(m, c) for m, c in inv.most_common() if c >= 2][:top_k]
        splitsets[nm] = splits

    # ensemble agreement on interior split points (over the words both segmenters split)
    agreement = None
    if len(segmenters) >= 2:
        names = list(segmenters.keys())
        a, b = splitsets[names[0]], splitsets[names[1]]
        agree = total = 0
        for ew in enc_unique:
            n = len(ew)
            if n <= 1:
                continue
            sa, sb = set(a.get(ew, ())), set(b.get(ew, ()))
            for p in range(1, n):
                total += 1
                if (p in sa) == (p in sb):
                    agree += 1
        agreement = round(agree / total, 4) if total else None

    return {
        "n_word_tokens": len(words),
        "n_word_types": len(enc_unique),
        "segmenters": list(segmenters.keys()),
        "inventories": {nm: [{"morpheme": m, "count": c} for m, c in inv]
                        for nm, inv in inventories.items()},
        "ensemble_split_agreement": agreement,
        "note": "Morphemes = recurring (>=2) word-internal sign-subsequences induced unsupervised. "
                "STRUCTURAL only; no phonetic value is assigned.",
    }


# --------------------------------------------------------------------------- #
# Full report + CLI
# --------------------------------------------------------------------------- #
def build_report(corpus: Sequence[Inscription], *, seed: int = 0, n_null: int = 200,
                 boundary: bool = True, dp_iters: int = 6, min_site_size: int = 1,
                 n_shuffle: int = 1, n_lfake: int = 1, use_morfessor: bool = True,
                 alpha: float = 0.01) -> Dict[str, object]:
    codec = SignCodec.from_corpus(corpus)
    report: Dict[str, object] = {
        "module": "scripts/comparison/morphology.py",
        "direction": "A — unsupervised Linear A morphology / segmentation induction",
        "no_phonetic_claim": NO_PHONETIC_CLAIM,
        "citations": [CITATION_PREREG, CITATION_GOLDWATER, CITATION_MORFESSOR, CITATION_NULLS,
                      CITATION_DSR],
        "n_inscriptions": len(corpus),
        "n_sites": len({ins.site for ins in corpus}),
        "prereg_affixes": prereg_sign_sequences(),
    }
    if boundary:
        report["boundary_recovery"] = boundary_recovery(
            corpus, codec, seed=seed, min_site_size=min_site_size, dp_iters=dp_iters,
            use_morfessor=use_morfessor)
    report["morpheme_induction"] = induce_morphemes(
        corpus, codec, seed=seed, dp_iters=max(dp_iters, 6), use_morfessor=use_morfessor)
    affix_test = run_affix_panel(corpus, codec, n_null=n_null, seed=seed, alpha=alpha)
    report["affix_test"] = affix_test
    # the floors are run at the SAME n_null; the real panel is reused so headline == table.
    report["null_falsification"] = null_falsification(
        corpus, codec, n_null=n_null, seed=seed, n_shuffle=n_shuffle,
        n_lfake=n_lfake, alpha=alpha, real=affix_test)
    # headline
    nf = report["null_falsification"]
    report["headline"] = {
        "n_confirmed_affixes": report["affix_test"]["n_confirm"],
        "confirmed_affixes": report["affix_test"]["confirmed_affixes"],
        "real_confirm_rate": nf["real_confirm_rate"],
        "shuffle_confirm_rate": nf["shuffle_confirm_rate"],
        "lfake_confirm_rate": nf["lfake_confirm_rate"],
        "has_morphology_power": nf["has_morphology_power"],
        "statement": nf["honesty_statement"],
    }
    return report


def _fmt(report: Dict[str, object]) -> str:
    L: List[str] = []
    L.append("=" * 80)
    L.append("DIRECTION A — Linear A MORPHOLOGY / SEGMENTATION INDUCTION (structural; NO phonetic claim)")
    L.append("=" * 80)
    L.append(f"inscriptions={report['n_inscriptions']}  sites={report['n_sites']}")
    L.append(f"pre-registered affixes (FROZEN): {len(report['prereg_affixes'])}")
    if "boundary_recovery" in report:
        br = report["boundary_recovery"]
        L.append("")
        L.append("WORD-BOUNDARY RECOVERY (leave-one-site-out; validates the METHOD):")
        L.append(f"  random-boundary baseline micro-F1 = {br['random_baseline']['micro_f1']:.3f} "
                 f"(boundary base rate {br['boundary_base_rate']:.3f})")
        for nm, s in br["segmenters"].items():
            flag = "USABLE" if s["beats_random"] else "NOT USED (<= random)"
            L.append(f"  {nm:<12} micro-F1={s['micro_f1']:.3f} macro-F1={s['macro_f1']:.3f}  -> {flag}")
    mi = report["morpheme_induction"]
    L.append("")
    L.append(f"MORPHEME INDUCTION ({', '.join(mi['segmenters'])}; "
             f"ensemble split agreement={mi['ensemble_split_agreement']}):")
    for nm, inv in mi["inventories"].items():
        top = ", ".join(f"{e['morpheme']}({e['count']})" for e in inv[:10])
        L.append(f"  {nm}: {top}")
    L.append("")
    L.append("PRE-REGISTERED AFFIX TEST (CONFIRM/REFUTE/NO_POWER; deflated for the panel size):")
    for r in report["affix_test"]["affixes"]:
        L.append(f"  {r['affix']:<9} [{r['edge']:<6} {r['sign_seq']:<22}] "
                 f"stems={r['n_distinct_stems']:<3} insc={r['n_inscriptions_bearing']:<3} "
                 f"obs={r['observed_rate']:.3f} null={r['null_mean']:.3f} z={r['z']:+.2f} "
                 f"bar={r['deflated_bar']:.3f} p={r['dsr_corrected_p']:.3g}  -> {r['verdict']}")
    nf = report["null_falsification"]
    L.append("")
    L.append("NULL FALSIFICATION (headline honesty gate):")
    L.append(f"  REAL confirm rate    = {nf['real_confirm_rate']:.3f}  "
             f"({report['affix_test']['n_confirm']}/{report['affix_test']['n_affixes_tested']}: "
             f"{', '.join(nf['real_confirmed_affixes']) or 'none'})")
    L.append(f"  SHUFFLE confirm rate = {nf['shuffle_confirm_rate']:.3f}")
    L.append(f"  L_FAKE  confirm rate = {nf['lfake_confirm_rate']:.3f}")
    L.append(f"  has_morphology_power = {nf['has_morphology_power']}")
    L.append("  " + nf["honesty_statement"])
    L.append("")
    L.append("NOTE: " + report["no_phonetic_claim"])
    return "\n".join(L)


def main(argv: Optional[Sequence[str]] = None) -> int:
    import argparse
    p = argparse.ArgumentParser(description="Direction A — Linear A morphology / segmentation induction "
                                            "(structural; NO phonetic-value claim).")
    p.add_argument("--corpus", default=DEFAULT_SILVER, help="structured silver inscriptions JSON")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--n-null", type=int, default=200, help="within-word permutation null draws")
    p.add_argument("--no-boundary", action="store_true", help="skip leave-one-site-out boundary recovery")
    p.add_argument("--no-morfessor", action="store_true", help="skip Morfessor (DP segmenter only)")
    p.add_argument("--dp-iters", type=int, default=6)
    p.add_argument("--min-site-size", type=int, default=1)
    p.add_argument("--n-shuffle", type=int, default=1)
    p.add_argument("--n-lfake", type=int, default=1)
    p.add_argument("--alpha", type=float, default=0.01)
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    if not os.path.exists(args.corpus):
        sys.stderr.write(f"corpus not found at {args.corpus}; run scripts/corpus_io_structured.py first\n")
        return 2
    corpus = load_corpus(args.corpus)
    report = build_report(corpus, seed=args.seed, n_null=args.n_null, boundary=not args.no_boundary,
                          dp_iters=args.dp_iters, min_site_size=args.min_site_size,
                          n_shuffle=args.n_shuffle, n_lfake=args.n_lfake,
                          use_morfessor=not args.no_morfessor, alpha=args.alpha)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False, default=str))
    else:
        print(_fmt(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
