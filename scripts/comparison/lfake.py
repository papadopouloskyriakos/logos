#!/usr/bin/env python3
"""lfake.py — the L_fake fabricated-language canary generator (logos comparison-layer §C.3 + F.2).

L_fake is a phonotactically-plausible, *invented* lexicon built from a parameterized grammar and
calibrated to a REAL candidate language's (a) phoneme-frequency distribution, (b) root-template
structure, and (c) lexicon size. It is never published and never present in any training corpus, so
running the full comparison pipeline against L_fake yields an *empirical false-positive floor*: any
"signal" it produces is definitionally spurious. A Gordon/Di Mino-style match on a real candidate
must clear the L_fake score DISTRIBUTION (many instances) by the corrected margin, or it is
spurious — memorisation cannot be invoked because there is nothing to memorise (refinement F.2).

Generator-calibration technique adopted from Nair 2026 (arXiv:2604.17828): a parameterized synthetic
generator is calibrated to the empirical range of the real comparator, parameters are swept, and the
DIVERGENCE of the generator output from the calibration targets is REPORTED HONESTLY. The synthetic
baseline is never treated as ground truth — it is a floor whose own mismatch with the target is
published alongside the numbers it produces.

Modes
-----
  semitic  — trilateral-root morphology (CCC root embedded in a surface skeleton of the candidate's
             length distribution). Used when calibrating to a Semitic candidate (Hebrew/Ugaritic).
  cv       — CV-syllable templates (e.g. CV, CVC, CVCV) with a consonant + vowel inventory; used
             for non-consonantal-skeleton candidates.
  markov   — order-1 phonotactic walk (the general fallback; captures bigram structure).

All randomness flows through a single ``numpy.random.Generator`` (seeded) so every lexicon is
deterministic. Generated forms that exactly reproduce a candidate form are rejected and resampled,
so L_fake never reproduces a CALIBRATION-SET form. The semitic-mode root sampler draws whole root
TRIPLES from the candidate's attested trilateral-root frequency distribution (not independent
marginals) and seats them at the deterministic template slots — this closes the F.2 root-template
gap that the old independent-consonant sampler left open (root_template_TV fell from ~0.84 to
~0.33 end-to-end with bhsa rejection (~0.23 standalone), on the Ugaritic<->Hebrew gold).

REGURGITATION BOUNDARY (honestly stated, not overclaimed): rejection is exact-form against the
calibration set PLUS, optionally, an externally-supplied full-lexicon reject set
(``external_reject``). When the operator supplies a full Hebrew lexicon (ETCBC/bhsa; see
run_canary.py), emitted forms whose canonical skeleton matches a real Hebrew lexeme or attested
trilateral root are also rejected, and the RESIDUAL real-collision rate of the emitted lexicon is
reported per instance. Without an external lexicon the rejection only covers the calibration set,
so real Biblical-Hebrew roots from OUTSIDE that set can still slip in — that residual is measured
and published (``residual_real_collision_rate``), never silently re-asserted as "zero real lexical
content". The honest statement is: L_fake contains no calibration-set form, and with a full lexicon
its residual collision with the wider Hebrew language is bounded and reported (target near 0).

Citations: Nair 2026 (arXiv:2604.17828) — synthetic-generator calibration + honest divergence
reporting; Packard 1974 — frequency-banded permutation null (see nulls.py); logos design §C.3, F.2.
"""
from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

# --------------------------------------------------------------------------- #
# Citations (kept as module constants so reports can echo them verbatim).
# --------------------------------------------------------------------------- #
CITATION_NAIR = (
    "Nair 2026, arXiv:2604.17828 — parameterized synthetic generators calibrated to the empirical "
    "range of a real comparator, swept across it, with honest reporting of generator-output "
    "divergence from calibration targets (the synthetic baseline is never treated as ground truth)."
)
CITATION_DESIGN = (
    "logos comparison-layer §C.3 (fabricated-language canary) + refinement F.2 "
    "(L_fake must be frequency / root-template / lexicon-size matched to each real candidate)."
)

# Default vowel classification for the `cv` / `auto` modes. For the consonantal-skeleton
# Semitic transliterations in corpus/bronze/ugaritic (b, g, d, w, y, <, ... with no written
# vowels) the `semitic` mode treats the whole inventory as consonantal.
DEFAULT_VOWELS = frozenset("aeiou")

# Invented gloss morphemes — English-shaped but SEMANTICALLY VOID. The gloss is only a label that
# makes L_fake read like a lexicon entry; it carries no real meaning and is never matched on. The
# forms (above) are the matchable content and are guaranteed invented.
_GLOSS_ROOTS = [
    "kor", "nal", "ves", "trel", "mish", "daro", "quen", "sula", "pirn", "hale",
    "zeph", "mor", "lir", "than", "wesh", "cal", "nor", "bal", "fen", "rul",
]
_GLOSS_SUFFIX = ["", "ing", "ment", "ness", "tion", "able", "ful", "ance", "ence", "ity"]
_GLOSS_PREFIX = ["", "un", "re", "be", "a"]


# --------------------------------------------------------------------------- #
# Calibration extraction (measure the candidate's empirical stats — Nair step 1)
# --------------------------------------------------------------------------- #
def char_frequencies(forms: Sequence[str]) -> Counter:
    """Marginal character counts over all forms (the phoneme-frequency target)."""
    c: Counter = Counter()
    for w in forms:
        c.update(w)
    return c


def length_distribution(forms: Sequence[str]) -> Counter:
    """Empirical word-length distribution (the length/template target)."""
    return Counter(len(w) for w in forms)


def _normalize_weights(counts: Dict[str, int]) -> Tuple[Tuple[str, ...], Tuple[float, ...]]:
    """Sort the inventory and return (chars, prob-weights) summing to 1."""
    items = sorted(counts.items())
    chars = tuple(ch for ch, _ in items)
    total = sum(v for _, v in items)
    weights = tuple(v / total for _, v in items)
    return chars, weights


def _positional_counts(forms: Sequence[str]) -> Dict[int, Counter]:
    """Per-position character counts (used to bias root-slot placement toward consonant-dense
    positions, capturing Semitic root-template structure)."""
    pos: Dict[int, Counter] = {}
    for w in forms:
        for i, ch in enumerate(w):
            pos.setdefault(i, Counter())[ch] += 1
    return pos


def _positional_density(pos_counts: Dict[int, Counter], length: int) -> np.ndarray:
    """For a word of ``length`` slots, return a length-L vector of non-negative positional
    densities (how character-heavy each slot is across the candidate). Used to pick root slots."""
    total = sum(sum(c.values()) for c in pos_counts.values()) or 1
    dens = np.zeros(length, dtype=float)
    for i in range(length):
        dens[i] = sum(pos_counts.get(i, Counter()).values()) / total
    s = dens.sum()
    if s <= 0:
        dens = np.full(length, 1.0 / length)
    else:
        dens /= s
    return dens


def _bigram_counts(forms: Sequence[str]) -> Counter:
    bg: Counter = Counter()
    for w in forms:
        for a, b in zip(w, w[1:]):
            bg[a + b] += 1
    return bg


def _trilateral_roots(forms: Sequence[str], pos_counts: Dict[int, Counter],
                      root_len: int = 3) -> Counter:
    """Extract a heuristic trilateral (root_len-consonant) 'root' per candidate form, using the
    SAME positional-density rule the generator uses to place its root slots. Reading the consonants
    at those slots gives a root-template distribution that is directly comparable between candidate
    and generator output (apples-to-apples divergence in the report)."""
    roots: Counter = Counter()
    for w in forms:
        L = len(w)
        if L < root_len:
            continue
        dens = _positional_density(pos_counts, L)
        # pick the root_len highest-density positions (deterministic per form)
        slots = sorted(np.argsort(-dens)[:root_len].tolist())
        root = "".join(w[j] for j in slots if j < L)
        if len(root) == root_len:
            roots[root] += 1
    return roots


def _classify_cv_pattern(form: str, vowels: frozenset) -> str:
    return "".join("V" if ch in vowels else "C" for ch in form)


# --------------------------------------------------------------------------- #
# Canonical-skeleton normalization for cross-transliteration rejection (F.2)
# --------------------------------------------------------------------------- #
# Different Hebrew transliterations write the guttural aleph differently (the Ugaritic
# alpha-convention writes aleph+V as a/i/u or a bare '<'; pointed schemes use separate marks).
# For an EXACT-FORM rejection we only need a stable skeleton: lowercase, unify the aleph
# representations, keep every other consonant distinct. This is deliberately NOT a phonemic
# collapse — tsade/shin/samekh and ḥet/he stay distinct so the reject set stays sharp.
_ALEPH_CLASS = frozenset("aA<>")          # aleph variants across the schemes we handle


def canonical_skeleton(form: str) -> str:
    """Normalize a Hebrew/Ugaritic transliterated form to a stable consonantal skeleton.

    Lowercase; unify aleph representations (``a``, ``>`` and bare aleph) to ``<``; leave all
    other consonants distinct. Two forms share a skeleton iff they are the same Hebrew
    consonantal word written in either of the two transliterations this layer handles.
    """
    if not form:
        return ""
    out = []
    for ch in form:
        if ch in _ALEPH_CLASS:
            out.append("<")
        elif ch == " " or ch == "-":
            continue
        else:
            out.append(ch.lower())
    return "".join(out)


def _deterministic_root_slots(pos_counts: Dict[int, Counter], length: int,
                              root_len: int) -> List[int]:
    """The root_len highest-positional-density slots for a word of ``length`` (deterministic).

    This mirrors :func:`_trilateral_roots`'s extraction rule EXACTLY, so when the generator seats
    an empirically-sampled root at these slots the divergence metric RECOVERS that same root
    (the root-template match is then limited only by finite-sample noise on the attested set,
    not by an extractor/placer mismatch). Used by the semitic empirical-root sampler.
    """
    n = min(root_len, length)
    if n <= 0:
        return []
    dens = _positional_density(pos_counts, length)
    # identical selection rule to _trilateral_roots: highest-density slots, sorted ascending
    return sorted(np.argsort(-dens)[:n].tolist())


# --------------------------------------------------------------------------- #
# The calibrated configuration
# --------------------------------------------------------------------------- #
@dataclass
class LFakeConfig:
    """All parameters needed to instantiate a generator calibrated to one candidate."""

    mode: str  # 'semitic' | 'cv' | 'markov'
    inventory: Tuple[str, ...]
    weights: Tuple[float, ...]                       # marginal phoneme weights (aligned w/ inventory)
    vowels: frozenset
    consonants: Tuple[str, ...]
    consonant_weights: Tuple[float, ...]
    vowel_weights: Tuple[float, ...]
    length_probs: Dict[int, float]                   # length -> probability
    root_len: int                                    # trilateral = 3 (semitic)
    lexicon_size: int                                # target number of unique invented forms
    positional_counts: Dict[int, Counter] = field(default_factory=dict)
    cv_template_probs: Dict[str, float] = field(default_factory=dict)
    bigram_counts: Counter = field(default_factory=Counter)
    start_counts: Counter = field(default_factory=Counter)
    trans_counts: Dict[str, Counter] = field(default_factory=dict)
    candidate_forms: Tuple[str, ...] = ()            # for the rejection test (no real content)
    temperature: float = 1.0                         # frequency sharpness (Nair sweep param)
    # F.2 root-template axis: attested trilateral-root FREQUENCY distribution sampled whole (not
    # independent marginals) + deterministic template-slot seating. Closes the root_template_TV gap.
    root_triples: Tuple[Tuple[str, ...], ...] = ()           # each tuple = root_len consonant chars
    root_triple_weights: Tuple[float, ...] = ()              # frequency weights, aligned w/ root_triples
    empirical_roots: bool = True                             # semitic default; False => independent
    # F.2 regurgitation boundary: canonical skeletons of REAL Hebrew to reject on top of the
    # calibration set (lexemes + attested trilateral roots). Empty => calibration-set-only rejection.
    external_reject: frozenset = field(default_factory=frozenset)
    external_reject_source: str = ""                         # provenance label for the report
    provenance: Dict[str, object] = field(default_factory=dict)


def _sharpen(weights: Sequence[float], temperature: float) -> np.ndarray:
    """Apply a temperature to the weight vector. temperature<1 sharpens (peaks the common
    phonemes), >1 flattens; 1.0 leaves it. Used by the Nair parameter sweep."""
    w = np.asarray(weights, dtype=float) + 1e-9
    w = w ** (1.0 / max(temperature, 1e-6))
    return w / w.sum()


def calibrate_to(candidate_forms: Sequence[str],
                 mode: str = "auto",
                 vowels: Optional[frozenset] = None,
                 root_len: int = 3,
                 temperature: float = 1.0,
                 external_reject: Optional[frozenset] = None,
                 external_reject_source: str = "",
                 empirical_roots: Optional[bool] = None) -> LFakeConfig:
    """Calibrate an LFakeConfig to a real candidate's empirical stats (Nair step 1).

    ``mode='auto'`` picks ``semitic`` when the vowel ratio is low (consonantal skeleton, the
    Northwest-Semitic transliteration case) and ``cv`` otherwise; ``markov`` is always available.

    F.2 root-template axis (semitic): the attested trilateral-root frequency distribution is
    extracted from the candidate and stored, so the generator samples whole root TRIPLES from it
    rather than three independent marginals. ``empirical_roots`` defaults to True for semitic and
    False otherwise; it self-disables when the candidate yields too few distinct trilaterals.

    F.2 regurgitation boundary: ``external_reject`` is a frozenset of canonical skeletons (see
    :func:`canonical_skeleton`) of REAL Hebrew to reject on top of the calibration candidate set.
    Pass the ETCBC/bhsa-derived set here (see run_canary.load_hebrew_reject_set) to bound L_fake's
    collision with the wider Hebrew language; leave empty for calibration-set-only rejection.
    """
    forms = [w for w in candidate_forms if w]
    if not forms:
        raise ValueError("calibrate_to: empty candidate form list")
    vset = vowels if vowels is not None else DEFAULT_VOWELS

    chars, weights = _normalize_weights(char_frequencies(forms))
    cons_counts = {ch: n for ch, n in char_frequencies(forms).items() if ch not in vset}
    vow_counts = {ch: n for ch, n in char_frequencies(forms).items() if ch in vset}
    if not cons_counts:                       # degenerate: everything is a "vowel"
        cons_counts = dict(char_frequencies(forms))
    cons_c, cons_w = _normalize_weights(cons_counts)
    if vow_counts:
        vow_c, vow_w = _normalize_weights(vow_counts)
    else:
        vow_c, vow_w = cons_c, cons_w          # cv mode degenerate on a vowel-less skeleton

    ldist = length_distribution(forms)
    n_total = sum(ldist.values())
    length_probs = {L: c / n_total for L, c in ldist.items()}

    if mode == "auto":
        vowel_ratio = sum(vow_counts.values()) / max(sum(char_frequencies(forms).values()), 1)
        mode = "semitic" if vowel_ratio < 0.15 else "cv"

    # F.2 root-template axis: extract the attested trilateral-root FREQUENCY distribution.
    pos_counts = _positional_counts(forms)
    roots_c = _trilateral_roots(forms, pos_counts, root_len)
    # tuple-of-tuples + aligned weights, sorted for determinism (identical across runs)
    root_items = sorted(roots_c.items())
    root_triples = tuple(tuple(r) for r, _ in root_items)
    root_triple_weights = tuple(float(c) for _, c in root_items)
    # self-disable on degenerate inputs (tiny / 1-char inventory) so those paths keep their old
    # independent-sampler behaviour and the tiny-inventory rejection test is unaffected.
    emp = (False if empirical_roots is None and mode != "semitic"
           else (bool(empirical_roots) if empirical_roots is not None else True))
    if emp and len(set(root_triples)) < max(2 * root_len, 5):
        emp = False
    # normalize external_reject to a frozenset of canonical skeletons
    ext = frozenset(external_reject) if external_reject else frozenset()

    cfg = LFakeConfig(
        mode=mode,
        inventory=chars,
        weights=weights,
        vowels=vset,
        consonants=cons_c,
        consonant_weights=cons_w,
        vowel_weights=vow_w,
        length_probs=length_probs,
        root_len=root_len,
        lexicon_size=len(set(forms)),
        positional_counts=pos_counts,
        cv_template_probs={},
        bigram_counts=_bigram_counts(forms),
        start_counts=Counter(w[0] for w in forms if w),
        trans_counts={},
        candidate_forms=tuple(set(forms)),
        temperature=temperature,
        root_triples=root_triples,
        root_triple_weights=root_triple_weights,
        empirical_roots=emp,
        external_reject=ext,
        external_reject_source=external_reject_source,
        provenance={"mode": mode, "root_len": root_len, "n_candidate_forms": len(forms),
                    "n_unique": len(set(forms)), "vowel_set": sorted(vset),
                    "n_attested_roots": len(root_triples), "empirical_roots": emp,
                    "external_reject_size": len(ext),
                    "external_reject_source": external_reject_source},
    )

    if mode == "cv":
        pat = Counter(_classify_cv_pattern(w, vset) for w in forms)
        ptot = sum(pat.values())
        cfg.cv_template_probs = {p: c / ptot for p, c in pat.items()}
    elif mode == "markov":
        tc: Dict[str, Counter] = {}
        for w in forms:
            for a, b in zip(w, w[1:]):
                tc.setdefault(a, Counter())[b] += 1
        cfg.trans_counts = tc

    return cfg


# --------------------------------------------------------------------------- #
# The generator
# --------------------------------------------------------------------------- #
class LFakeGenerator:
    """Generate an invented, matchable-in-structure lexicon from a calibrated config.

    Parameters
    ----------
    config : LFakeConfig
        Output of :func:`calibrate_to`.
    seed : int
        Seed for the internal ``numpy.random.GGenerator`` (deterministic).

    Notes
    -----
    Every emitted form is checked against the candidate lexicon (and, when supplied, the external
    full-lexicon reject set) and rejected on a canonical-skeleton match, so L_fake never reproduces
    a calibration-set form and — with a full Hebrew lexicon supplied — its residual collision with
    the wider Hebrew language is bounded and reported. The rejection counts are recorded in
    :attr:`rejections` (calibration-set) and :attr:`lexicon_rejections` (external) and surfaced in
    the divergence report as a safety audit.
    """

    def __init__(self, config: LFakeConfig, seed: int):
        self.cfg = config
        self.seed = int(seed)
        self.rng = np.random.default_rng(self.seed)
        self._candidate = set(config.candidate_forms)
        self.rejections = 0                  # collisions with the calibration candidate set
        self.lexicon_rejections = 0          # collisions with the external full-Hebrew reject set
        self.generated: List[str] = []

        # sharpened marginal weights (temperature is the Nair sweep parameter)
        self._w_inv = _sharpen(config.weights, config.temperature)
        self._w_cons = _sharpen(config.consonant_weights, config.temperature)
        self._w_vow = _sharpen(config.vowel_weights, config.temperature)
        self._lengths = np.array(sorted(config.length_probs), dtype=int)
        self._length_p = np.array([config.length_probs[L] for L in self._lengths], dtype=float)
        self._length_p /= self._length_p.sum()

        # F.2 root-template: empirical root-triple sampler (whole triples from the attested
        # distribution) + deterministic template-slot seating. Falls back gracefully to the
        # independent-consonant sampler when empirical_roots is off / no attested triples.
        self._emp_roots = bool(config.empirical_roots) and len(config.root_triples) > 0
        if self._emp_roots:
            wt = np.asarray(config.root_triple_weights, dtype=float)
            self._root_p = wt / wt.sum()
            self._root_triples = config.root_triples
        else:
            self._root_p = None
            self._root_triples = None

        # F.2 regurgitation: canonical skeletons of the external reject set (real Hebrew lexemes
        # + attested trilateral roots), used in the rejection test alongside the candidate set.
        self._reject_canon = frozenset(config.external_reject) if config.external_reject else frozenset()

    # -- low-level samplers -------------------------------------------------
    def _sample_char(self, chars: Tuple[str, ...], w: np.ndarray) -> str:
        return str(self.rng.choice(chars, p=w))

    def _sample_length(self) -> int:
        return int(self.rng.choice(self._lengths, p=self._length_p))

    def _sample_root(self, use_empirical: bool = True) -> List[str]:
        n = self.cfg.root_len
        if use_empirical and self._emp_roots and self._root_triples is not None:
            # F.2: draw a WHOLE attested root triple from the empirical frequency distribution,
            # capturing the consonant co-occurrence structure (not independent marginals).
            if self._root_p is not None and len(self._root_p) == len(self._root_triples):
                i = int(self.rng.choice(len(self._root_p), p=self._root_p))
            else:
                i = int(self.rng.integers(0, len(self._root_triples)))
            r = self._root_triples[i]
            return list(r) if len(r) == n else list(r) + [
                self._sample_char(self.cfg.consonants, self._w_cons) for _ in range(n - len(r))]
        # fallback: independent marginal consonants (the pre-F.2 behaviour)
        return [self._sample_char(self.cfg.consonants, self._w_cons) for _ in range(n)]

    def _sample_root_slots(self, length: int) -> List[int]:
        if self._emp_roots:
            # F.2: seat the root at the DETERMINISTIC top-density slots — the same rule
            # _trilateral_roots uses to EXTRACT roots, so the divergence metric recovers the
            # injected attested root and the root_template match is limited only by finite-sample
            # noise on the attested set (not an extractor/placer mismatch).
            return _deterministic_root_slots(self.cfg.positional_counts, length, self.cfg.root_len)
        dens = _positional_density(self.cfg.positional_counts, length)
        n = min(self.cfg.root_len, length)
        # sample n distinct positions without replacement, biased by positional density
        idx = self.rng.choice(length, size=n, replace=False, p=dens)
        return sorted(int(i) for i in idx)

    # -- mode-specific form generation -------------------------------------
    def _gen_semitic(self, length_boost: int = 0, fixed_length: Optional[int] = None) -> str:
        cfg = self.cfg
        if fixed_length is not None:
            L = max(int(fixed_length) + length_boost, cfg.root_len)
        else:
            L = self._sample_length() + length_boost
            L = max(L, cfg.root_len)
        # When the form is exactly a BARE root (L == root_len) and a full-lexicon reject set is
        # active, an empirical (attested, real-Hebrew) root would be rejected as a real word, so
        # the length would be un-producible and the length distribution would bias long. For
        # bare-root lengths only, draw an INVENTED root so the form can survive rejection; longer
        # forms embed the empirical root in a template (root + filler = non-lexeme) and keep the
        # F.2 root-co-occurrence match. (Bare-root lengths are a small minority of the lexicon.)
        bare_root = (L == cfg.root_len) and bool(self._reject_canon)
        root = self._sample_root(use_empirical=not bare_root)
        slots = self._sample_root_slots(L)
        chars: List[Optional[str]] = [None] * L
        for pos, cons in zip(slots, root):
            chars[pos] = cons
        for i in range(L):
            if chars[i] is None:
                chars[i] = self._sample_char(cfg.inventory, self._w_inv)  # affix / filler
        return "".join(c for c in chars if c is not None)

    def _gen_cv(self, length_boost: int = 0, fixed_length: Optional[int] = None) -> str:
        cfg = self.cfg
        if not cfg.cv_template_probs:
            return self._gen_semitic(length_boost, fixed_length=fixed_length)
        pats = list(cfg.cv_template_probs.keys())
        probs = np.array([cfg.cv_template_probs[p] for p in pats], dtype=float)
        probs /= probs.sum()
        # chain 1-3 templates to reach variety; length_boost adds syllables when the space is thin
        n_syll = int(self.rng.choice([1, 2, 3], p=[0.25, 0.5, 0.25])) + length_boost
        out: List[str] = []
        for _ in range(max(1, n_syll)):
            pat = str(self.rng.choice(pats, p=probs))
            for slot in pat:
                if slot == "V":
                    out.append(self._sample_char(_vowel_chars(cfg), self._w_vow))
                else:
                    out.append(self._sample_char(cfg.consonants, self._w_cons))
        return "".join(out)

    def _gen_markov(self, length_boost: int = 0, fixed_length: Optional[int] = None) -> str:
        cfg = self.cfg
        if fixed_length is not None:
            L = max(int(fixed_length) + length_boost, 1)
        else:
            L = self._sample_length() + length_boost
        if not cfg.start_counts:
            return self._gen_semitic(length_boost, fixed_length=fixed_length)
        starts = sorted(cfg.start_counts)
        sw = np.array([cfg.start_counts[s] for s in starts], dtype=float)
        sw /= sw.sum()
        ch = str(self.rng.choice(starts, p=sw))
        out = [ch]
        for _ in range(max(0, L - 1)):
            nxt = cfg.trans_counts.get(ch)
            if not nxt:
                out.append(self._sample_char(cfg.inventory, self._w_inv))
            else:
                targets = sorted(nxt)
                tw = np.array([nxt[t] for t in targets], dtype=float)
                tw /= tw.sum()
                ch = str(self.rng.choice(targets, p=tw))
                out.append(ch)
        return "".join(out)

    def _generate_one(self) -> str:
        mode = self.cfg.mode
        if mode == "semitic":
            base = self._gen_semitic
        elif mode == "cv":
            base = self._gen_cv
        elif mode == "markov":
            base = self._gen_markov
        else:
            raise ValueError(f"unknown L_fake mode: {mode!r}")
        # Sample the length ONCE and rejection-sample the FORM at that fixed length. This keeps the
        # calibrated length distribution intact even though empirical-root (semitic) forms collide
        # with the candidate/lexicon sets at a LENGTH-DEPENDENT rate (short real-root forms collide
        # far more often); re-sampling the length on every collision would under-produce short
        # forms and bias the length distribution. Only the last few attempts grow the length, as a
        # last resort when a particular length has nearly no novel forms left (degenerate/tiny
        # inventories). Rejection tests: (a) never a calibration-set form (the canary guarantee);
        # (b) with an external full-lexicon reject set, never a canonical-skeleton match for a real
        # Hebrew lexeme / attested trilateral root (the F.2 regurgitation boundary).
        L = self._sample_length()
        for attempt in range(64):
            boost = 0 if attempt < 48 else (attempt - 48) // 4   # last 16 attempts grow the length
            w = base(boost, fixed_length=L)
            if not w:
                continue
            if w in self._candidate:
                self.rejections += 1
                continue
            if self._reject_canon and canonical_skeleton(w) in self._reject_canon:
                self.lexicon_rejections += 1
                continue
            return w
        # rare exhaustion of the fixed length: try a few FRESH length draws (preserves the length
        # distribution) before the invented last-resort fallback (degenerate/tiny inventories).
        for _ in range(8):
            w = base(0)
            if not w:
                continue
            if w in self._candidate:
                self.rejections += 1
                continue
            if self._reject_canon and canonical_skeleton(w) in self._reject_canon:
                self.lexicon_rejections += 1
                continue
            return w
        return base(4) + "_lf" if base(4) else "lf"   # last-resort invented fallback

    # -- public API ---------------------------------------------------------
    def generate_lexicon(self, n: Optional[int] = None,
                         with_glosses: bool = True) -> List[dict]:
        """Generate ``n`` unique invented forms (default = calibrated lexicon size)."""
        target = n if n is not None else self.cfg.lexicon_size
        seen: set = set()
        out: List[dict] = []
        guard = 0
        while len(out) < target and guard < target * 200:
            guard += 1
            w = self._generate_one()
            if w in seen:
                continue
            seen.add(w)
            entry = {"form": w}
            if with_glosses:
                entry["gloss"] = self._invented_gloss()
                entry["invented"] = True          # explicit flag: never a real meaning
            out.append(entry)
        self.generated = [e["form"] for e in out]
        return out

    def _invented_gloss(self) -> str:
        rng = self.rng
        root = str(rng.choice(_GLOSS_ROOTS))
        suf = str(rng.choice(_GLOSS_SUFFIX))
        pre = str(rng.choice(_GLOSS_PREFIX))
        return f"{pre}{root}{suf}".lower()


def _vowel_chars(cfg: LFakeConfig) -> Tuple[str, ...]:
    vs = tuple(ch for ch in cfg.inventory if ch in cfg.vowels)
    return vs if vs else cfg.inventory


# --------------------------------------------------------------------------- #
# Divergence reporting (Nair step 3 — honest, never ground-truth)
# --------------------------------------------------------------------------- #
def _freq_dist(forms: Sequence[str]) -> Dict[str, float]:
    c = char_frequencies(forms)
    tot = sum(c.values()) or 1
    return {ch: n / tot for ch, n in c.items()}


def _length_dist(forms: Sequence[str]) -> Dict[int, float]:
    c = length_distribution(forms)
    tot = sum(c.values()) or 1
    return {L: n / tot for L, n in c.items()}


def _tv(p: Dict, q: Dict) -> float:
    keys = set(p) | set(q)
    return 0.5 * sum(abs(p.get(k, 0.0) - q.get(k, 0.0)) for k in keys)


def _kl(p: Dict, q: Dict, eps: float = 1e-9) -> float:
    keys = set(p) | set(q)
    tot = 0.0
    for k in keys:
        pk = p.get(k, 0.0)
        qk = q.get(k, eps)
        if pk > 0:
            tot += pk * math.log(pk / qk)
    return tot


def _bigram_dist(forms: Sequence[str]) -> Dict[str, float]:
    bg = _bigram_counts(forms)
    tot = sum(bg.values()) or 1
    return {k: v / tot for k, v in bg.items()}


def divergence_report(generated_forms: Sequence[str],
                      candidate_forms: Sequence[str],
                      cfg: Optional[LFakeConfig] = None) -> dict:
    """Report how far the generator output sits from the calibration targets (Nair).

    Returns a dict of named divergence metrics. These are *reported*, never minimized silently —
    a synthetic baseline is not ground truth, and a non-zero divergence is itself information about
    how aggressive the floor is.
    """
    gen = list(generated_forms)
    cand = list(candidate_forms)

    p_char_g = _freq_dist(gen)
    p_char_c = _freq_dist(cand)
    p_len_g = _length_dist(gen)
    p_len_c = _length_dist(cand)
    p_bg_g = _bigram_dist(gen)
    p_bg_c = _bigram_dist(cand)

    pos_counts = _positional_counts(cand) if cfg is None else cfg.positional_counts
    root_len = cfg.root_len if cfg is not None else 3
    roots_g = _trilateral_roots(gen, pos_counts, root_len)
    roots_c = _trilateral_roots(cand, pos_counts, root_len)
    rt = sum(roots_g.values()) or 1
    rc = sum(roots_c.values()) or 1
    p_root_g = {k: v / rt for k, v in roots_g.items()}
    p_root_c = {k: v / rc for k, v in roots_c.items()}

    # lexical-overlap safety audit (must be 0.0 — the canary guarantee)
    cand_set = set(cand)
    overlap = sum(1 for w in gen if w in cand_set)
    overlap_rate = overlap / max(len(gen), 1)

    # F.2 regurgitation audit: residual collision of the EMITTED forms with the external full
    # Hebrew lexicon (lexemes + attested trilateral roots), measured on the canonical skeleton.
    # With external_reject supplied this is ~0 by construction (rejection sampling); without it
    # the candidate-set-only rejection leaves a measurable residual that is PUBLISHED here.
    ext = cfg.external_reject if cfg is not None else frozenset()
    if ext:
        coll = sum(1 for w in gen if canonical_skeleton(w) in ext)
        residual_rate = coll / max(len(gen), 1)
        collision_word = ("residual real-Hebrew collision rate of the emitted lexicon "
                          "(rejection sampled against the external lexicon; expect ~0).")
    else:
        # measure honestly against the external set even though we did not reject against it, so
        # the calibration-set-only limitation is visible (used by the canary before bhsa is wired)
        residual_rate = float("nan")
        collision_word = ("NOT measured here: no external reject set was supplied, so rejection "
                           "only covers the calibration candidate set; real Hebrew roots from "
                           "outside it can still be present (see residual_real_collision_rate in "
                           "run_canary when bhsa is supplied).")
    ext_src = (cfg.external_reject_source if cfg is not None else "") or ""
    ext_size = len(ext) if ext else 0

    # length KS statistic (scipy) — honest continuous distance on the length CDF
    from scipy.stats import ks_2samp
    len_g = [len(w) for w in gen]
    len_c = [len(w) for w in cand]
    try:
        ks_stat = float(ks_2samp(len_g, len_c).statistic)
    except Exception:
        ks_stat = float("nan")

    return {
        "n_generated": len(gen),
        "n_candidate": len(cand),
        "lexicon_size_ratio": len(gen) / max(len(cand), 1),
        "phoneme_freq_TV": _tv(p_char_g, p_char_c),
        "phoneme_freq_KL": _kl(p_char_g, p_char_c),
        "length_TV": _tv(p_len_g, p_len_c),
        "length_KS": ks_stat,
        "bigram_KL": _kl(p_bg_g, p_bg_c),
        "root_template_TV": _tv(p_root_g, p_root_c),
        "lexical_overlap_rate": overlap_rate,      # == 0.0 required (canary property: no calibration-set form)
        "residual_real_collision_rate": residual_rate,  # F.2: vs the wider Hebrew language
        "external_reject_size": ext_size,
        "external_reject_source": ext_src,
        "unique_rate": len(set(gen)) / max(len(gen), 1),
        "note": "Divergence from calibration targets (reported, not minimized). "
                "A synthetic baseline is NOT ground truth.",
        "regurgitation_note": collision_word,
    }


def aggregate_divergence(candidate_forms: Sequence[str],
                         cfg: LFakeConfig,
                         n_instances: int = 8,
                         base_seed: int = 0) -> dict:
    """Run many L_fake instances, return per-metric mean/std of the divergence (Nair sweep base).

    Also aggregates the rejection-pressure counters (calibration-set collisions and external
    full-lexicon collisions) so the report shows how hard the regurgitation boundary is working.
    """
    rows: List[dict] = []
    rejections: List[int] = []
    lex_rejections: List[int] = []
    for i in range(n_instances):
        gen = LFakeGenerator(cfg, seed=base_seed + i)
        gen.generate_lexicon()
        rows.append(divergence_report(gen.generated, candidate_forms, cfg))
        rejections.append(int(gen.rejections))
        lex_rejections.append(int(gen.lexicon_rejections))
    keys = [k for k, v in rows[0].items() if isinstance(v, (int, float))]
    agg: Dict[str, dict] = {}
    for k in keys:
        vals = np.array([r[k] for r in rows], dtype=float)
        # skip NaN-only aggregates (e.g. un-measured residual) — reported per-instance instead
        if np.isnan(vals).all():
            continue
        vals = np.nan_to_num(vals, nan=0.0)
        agg[k] = {"mean": float(np.mean(vals)), "std": float(np.std(vals)),
                  "min": float(np.min(vals)), "max": float(np.max(vals))}
    rej = np.array(rejections, dtype=float)
    lex = np.array(lex_rejections, dtype=float)
    agg["calibration_rejections"] = {"mean": float(rej.mean()), "std": float(rej.std()),
                                     "min": float(rej.min()), "max": float(rej.max())}
    agg["external_lexicon_rejections"] = {"mean": float(lex.mean()), "std": float(lex.std()),
                                          "min": float(lex.min()), "max": float(lex.max())}
    return {"per_instance": rows, "aggregate": agg,
            "n_instances": n_instances, "base_seed": base_seed,
            "calibration_rejections": rejections,
            "external_lexicon_rejections": lex_rejections}


def parameter_sweep(candidate_forms: Sequence[str],
                    cfg: LFakeConfig,
                    seeds: Sequence[int] = (0, 1, 2, 3),
                    temperatures: Sequence[float] = (0.75, 1.0, 1.25),
                    root_lens: Sequence[int] = (2, 3, 4)) -> dict:
    """Sweep the generator parameters across the candidate's empirical range (Nair step 2).

    Reports how the divergence and the downstream-matchable structure of L_fake move with the
    temperature (frequency sharpness) and root length. Output is for honest reporting only.
    """
    import itertools
    grid = []
    for temp, rlen in itertools.product(temperatures, root_lens):
        swept = LFakeConfig(
            mode=cfg.mode, inventory=cfg.inventory, weights=cfg.weights, vowels=cfg.vowels,
            consonants=cfg.consonants, consonant_weights=cfg.consonant_weights,
            vowel_weights=cfg.vowel_weights, length_probs=cfg.length_probs, root_len=rlen,
            lexicon_size=cfg.lexicon_size, positional_counts=cfg.positional_counts,
            cv_template_probs=cfg.cv_template_probs, bigram_counts=cfg.bigram_counts,
            start_counts=cfg.start_counts, trans_counts=cfg.trans_counts,
            candidate_forms=cfg.candidate_forms, temperature=temp, provenance=cfg.provenance,
            # carry the F.2 axes through the sweep; the empirical root triples are only valid at
            # the calibrated root_len (re-extract by re-calibrating for other root_lens).
            root_triples=cfg.root_triples if rlen == cfg.root_len else (),
            root_triple_weights=cfg.root_triple_weights if rlen == cfg.root_len else (),
            empirical_roots=cfg.empirical_roots and rlen == cfg.root_len,
            external_reject=cfg.external_reject,
            external_reject_source=cfg.external_reject_source,
        )
        rows = []
        for s in seeds:
            g = LFakeGenerator(swept, seed=s)
            g.generate_lexicon()
            rows.append(divergence_report(g.generated, candidate_forms, swept))
        phon = np.array([r["phoneme_freq_TV"] for r in rows])
        root = np.array([r["root_template_TV"] for r in rows])
        bigr = np.array([r["bigram_KL"] for r in rows])
        grid.append({
            "temperature": temp, "root_len": rlen,
            "phoneme_freq_TV_mean": float(phon.mean()),
            "root_template_TV_mean": float(root.mean()),
            "bigram_KL_mean": float(bigr.mean()),
            "lexicon_size_ratio_mean": float(np.mean([r["lexicon_size_ratio"] for r in rows])),
            "overlap_max": float(np.max([r["lexical_overlap_rate"] for r in rows])),
        })
    return {"grid": grid, "n_seeds_per_point": len(list(seeds))}


# --------------------------------------------------------------------------- #
# CLI: calibrate to the Hebrew side of the gold file + print the divergence report
# --------------------------------------------------------------------------- #
def _load_hebrew_side(path: str) -> List[str]:
    forms: List[str] = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.rstrip("\n")
            if i == 0 or not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            for h in parts[1].split("|"):
                h = h.strip()
                if h:
                    forms.append(h)
    return forms


def main(argv: Optional[Sequence[str]] = None) -> int:
    import argparse, json, os
    p = argparse.ArgumentParser(description="L_fake fabricated-language canary generator")
    p.add_argument("--cognates", default=None,
                   help="gold cognate file (default: corpus/bronze/ugaritic/uga-heb.gold.cog)")
    p.add_argument("--mode", default="semitic", choices=["semitic", "cv", "markov", "auto"])
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--n-instances", type=int, default=8,
                   help="number of L_fake instances for the divergence aggregate")
    p.add_argument("--sweep", action="store_true", help="also run the parameter sweep")
    p.add_argument("--json", action="store_true", help="emit JSON instead of human text")
    args = p.parse_args(argv)

    here = os.path.dirname(os.path.abspath(__file__))
    cog = args.cognates or os.path.join(here, "..", "..", "corpus", "bronze", "ugaritic",
                                        "uga-heb.gold.cog")
    cog = os.path.abspath(cog)
    heb = _load_hebrew_side(cog)

    cfg = calibrate_to(heb, mode=args.mode)
    report = {
        "citation": [CITATION_NAIR, CITATION_DESIGN],
        "candidate": os.path.basename(cog),
        "calibration": {
            "mode": cfg.mode, "inventory_size": len(cfg.inventory),
            "lexicon_size_target": cfg.lexicon_size, "root_len": cfg.root_len,
            "vowel_set": sorted(cfg.vowels),
        },
    }
    agg = aggregate_divergence(heb, cfg, n_instances=args.n_instances, base_seed=args.seed)
    report["divergence_aggregate"] = agg["aggregate"]
    # one concrete sample lexicon
    sample = LFakeGenerator(cfg, seed=args.seed).generate_lexicon(n=15)
    report["sample_lfake"] = sample
    if args.sweep:
        report["parameter_sweep"] = parameter_sweep(heb, cfg)

    if args.json:
        print(json.dumps(report, indent=2, default=str))
    else:
        print("# L_fake calibration + divergence report")
        print(f"# candidate: {report['candidate']}  mode={cfg.mode}  "
              f"inventory={len(cfg.inventory)}  lexicon_size_target={cfg.lexicon_size}")
        print(f"# {CITATION_NAIR}")
        print("# divergence (generator output vs calibration targets) — reported, not minimized:")
        for k, v in agg["aggregate"].items():
            print(f"#   {k:<22} mean={v['mean']:.4f}  std={v['std']:.4f}  "
                  f"[min {v['min']:.4f}, max {v['max']:.4f}]")
        print("# sample L_fake forms (invented; no calibration-set form; residual real-Hebrew "
              "collision reported above):")
        print("#   " + " ".join(e["form"] for e in sample))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
