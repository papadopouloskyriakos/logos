#!/usr/bin/env python3
"""searchlog.py — N_eff instrumentation: COUNT the trials, don't estimate them (design §B.2).

Design §B.2 ("Effective-n: COUNT it, don't estimate it") makes the multiple-testing trial count
EXACT for the machine search: instrument the retrieval to log every distinct
``(sign-value-assignment × lexeme × segmentation)`` candidate it actually scored, and that logged
count IS ``N_eff`` — the number fed to the deflated bar (§B.3, ``verdict.grade``). No hand-waving,
no estimate.

This module is the producer of that number. Today ``verdict.grade`` takes ``n_eff`` as a
hand-passed int; a future scanner instead drives a :class:`SearchLog`, scores its candidates through
it, and reads ``.n_eff`` off the log. That makes invariant 12 (counts are GENERATED, not
hand-written) real for the single most abuse-prone figure in the whole pipeline — the trial count a
human/LLM search hides and the machine search is forced to publish.

Two honesty properties are mechanical here:

  - **Dedup is deterministic** (invariant 6): a candidate's identity is the canonical
    ``(assignment, lexeme, segmentation)`` triple. Re-scoring the same triple — a retry, a replayed
    crash, the same root reached by two query paths — is a NO-OP and does not inflate ``N_eff``.
    The assignment key is order-independent (a sorted tuple of ``(sign, value)`` pairs) so the same
    partial map written in any order collapses to one identity.
  - **The sanity bound only DETECTS under-logging** (§B.2): ``N_eff ≲ S_unknown · V̄_branch · R_L ·
    F · G_seg`` is an upper bound on how many distinct candidates the search space CAN hold. It is
    never used as the count — only to flag a logged ``n_eff`` that EXCEEDS it, which means the bound
    is under-specified or the logger is double-counting a triple it failed to canonicalize (a bug).
    An under-logging (n_eff far below the bound) is the silent failure that would deflate the bar
    dishonestly; the bound + the flag are how a future scanner self-checks.

Pure stdlib. Deterministic: the log is an insertion-ordered set of frozen triples; no randomness,
no clock, no I/O. (Invariant 4: the statistic is arithmetic — a count of distinct keys — never a
model.)
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple, Union

CITATION_DESIGN = (
    "logos comparison-layer §B.2 (Effective-n: COUNT it, don't estimate it — instrument the "
    "retrieval to log every distinct (sign-value-assignment × lexeme × segmentation) candidate it "
    "actually scored; that count IS N_eff). Sanity upper bound N_eff ≲ S_unknown · V̄_branch · "
    "R_L · F · G_seg is used ONLY to detect under-logging, never as the count."
)

# A sign-value assignment may be given as a mapping {sign: value} or as an iterable of
# (sign, value) pairs; both canonicalize to the same key.
AssignmentLike = Union[Mapping[str, str], Iterable[Tuple[str, str]]]
AssignmentKey = Tuple[Tuple[str, str], ...]
SegmentationLike = Union[str, Sequence[str]]
CandidateKey = Tuple[AssignmentKey, str, str]


# --------------------------------------------------------------------------- #
# Canonicalization — a candidate's identity is order-independent and hashable
# --------------------------------------------------------------------------- #
def canonical_assignment(assignment: AssignmentLike) -> AssignmentKey:
    """Canonical, hashable key for a sign→value assignment: a sorted tuple of ``(sign, value)``.

    Order-independence is the point: the same partial map ``{*301: na, *311: ki}`` reached by two
    different query paths (or serialized in two orders) must collapse to ONE identity, or it inflates
    ``N_eff``. Sorting on ``(sign, value)`` makes the key independent of insertion order and of the
    mapping-vs-pairs input shape. Each ``(sign, value)`` pair is stringified so heterogeneous sign
    ids (e.g. ``"*301"`` vs an int) compare consistently.
    """
    if isinstance(assignment, Mapping):
        pairs = assignment.items()
    else:
        pairs = assignment
    norm: List[Tuple[str, str]] = [(str(s), str(v)) for s, v in pairs]
    return tuple(sorted(norm))


def canonical_segmentation(segmentation: SegmentationLike) -> str:
    """Canonical, hashable key for a segmentation.

    A segmentation may arrive as a string (already-joined, e.g. ``"na-wa-ya"``) or as a sequence of
    segments (``["na", "wa", "ya"]``); both collapse to the same delimited string so the two input
    shapes are ONE identity. The delimiter ``\\x1f`` (unit separator) cannot occur in a transcription
    form, so the join is unambiguous.
    """
    if isinstance(segmentation, str):
        return segmentation
    return "\x1f".join(str(seg) for seg in segmentation)


def candidate_key(assignment: AssignmentLike, lexeme: str,
                  segmentation: SegmentationLike) -> CandidateKey:
    """The full canonical identity of a scored candidate: ``(assignment, lexeme, segmentation)``."""
    return (canonical_assignment(assignment), str(lexeme), canonical_segmentation(segmentation))


# --------------------------------------------------------------------------- #
# SearchLog — the instrumented retrieval's N_eff producer
# --------------------------------------------------------------------------- #
class SearchLog:
    """Deduplicating log of every distinct candidate a retrieval actually scored.

    Drive it from the scanner: for each candidate the retrieval scores, call
    :meth:`log_candidate`. ``.n_eff`` is the number of DISTINCT canonical triples logged — the exact
    multiple-testing trial count for the deflated bar (§B.3). Re-scoring the same triple is a no-op
    (invariant 6); ``.n_logged`` exposes the gross call count so a caller can see the dedup ratio.
    """

    __slots__ = ("_seen", "_order", "_n_logged")

    def __init__(self) -> None:
        self._seen: Dict[CandidateKey, None] = {}   # dict preserves insertion order, dedups on key
        self._order: List[CandidateKey] = []
        self._n_logged = 0

    def log_candidate(self, sign_value_assignment: AssignmentLike, lexeme: str,
                      segmentation: SegmentationLike) -> bool:
        """Record one scored candidate; return True iff it was NEW (not a re-score of a logged triple).

        The candidate's identity is the canonical ``(assignment, lexeme, segmentation)`` triple
        (order-independent assignment, input-shape-independent segmentation). A duplicate increments
        the gross :attr:`n_logged` counter but does NOT add to ``n_eff`` — replays and crashed
        retries are idempotent (invariant 6).
        """
        self._n_logged += 1
        key = candidate_key(sign_value_assignment, lexeme, segmentation)
        if key in self._seen:
            return False
        self._seen[key] = None
        self._order.append(key)
        return True

    @property
    def n_eff(self) -> int:
        """The COUNTED effective-n: number of DISTINCT candidates scored (design §B.2)."""
        return len(self._seen)

    @property
    def n_logged(self) -> int:
        """Gross number of :meth:`log_candidate` calls, including duplicates (dedup-ratio numerator)."""
        return self._n_logged

    def candidates(self) -> List[CandidateKey]:
        """The distinct candidate keys, in first-seen (insertion) order. Deterministic."""
        return list(self._order)

    # --- per-dimension distinct counts (for the tight sanity tripwire, not the count itself) ------- #
    @property
    def distinct_pairs(self) -> int:
        """Distinct (sign, value) ASSIGNMENT pairs used across all logged maps. ≤ S_unknown·V_branch."""
        return len({pair for (akey, _, _) in self._seen for pair in akey})

    @property
    def distinct_signs(self) -> int:
        """Distinct free SIGNS assigned across all logged maps. ≤ S_unknown."""
        return len({pair[0] for (akey, _, _) in self._seen for pair in akey})

    @property
    def distinct_lexemes(self) -> int:
        """Distinct LEXEMES scored. ≤ R_L."""
        return len({lex for (_, lex, _) in self._seen})

    @property
    def distinct_segmentations(self) -> int:
        """Distinct SEGMENTATIONS scored. ≤ G_seg."""
        return len({seg for (_, _, seg) in self._seen})

    def bound_report(self, s_unknown: int, v_branch: int, r_l: int, g_seg: int) -> Dict[str, object]:
        """Per-dimension sanity tripwire (§B.2) — the CORRECT over-bound check for map-valued candidates.

        Bounds each OBSERVABLE dimension against its declared cap; an honest, properly-canonicalized log
        can exceed none of them, so any ``over=True`` is a defect (under-specified cap or a dedup bug).
        Unlike comparing ``n_eff`` to the atomic product, joint maps do not trip a false positive here
        (8 distinct maps over 3 signs × 2 values use only 6 distinct pairs ≤ 6). Families ``F`` are not
        carried in the candidate key, so they are not checked here.
        """
        dims = {
            "pairs": (self.distinct_pairs, int(s_unknown) * int(v_branch)),
            "signs": (self.distinct_signs, int(s_unknown)),
            "lexemes": (self.distinct_lexemes, int(r_l)),
            "segmentations": (self.distinct_segmentations, int(g_seg)),
        }
        per_dim = {
            name: {"observed": obs, "cap": cap, "over": over_bound_flag(obs, cap),
                   "fill_ratio": (obs / cap) if cap > 0 else None}
            for name, (obs, cap) in dims.items()
        }
        return {
            "n_eff": self.n_eff,
            "per_dimension": per_dim,
            "over_bound": any(d["over"] for d in per_dim.values()),
        }

    def __len__(self) -> int:
        return self.n_eff

    def __contains__(self, item: CandidateKey) -> bool:
        return item in self._seen


# --------------------------------------------------------------------------- #
# Sanity upper bound — detect under-logging, NEVER the count (§B.2)
# --------------------------------------------------------------------------- #
def sanity_upper_bound(s_unknown: int, v_branch: int, r_l: int, f: int, g_seg: int) -> int:
    """Atomic search-space size (design §B.2): ``S_unknown · V̄_branch · R_L · F · G_seg``.

    The product of (signs free) × (values/sign) × (roots in L) × (families) × (segmentations) — a
    reference SCALE for the search, used ONLY for context, NEVER as the count. The honest ``N_eff`` is
    always the logged :attr:`SearchLog.n_eff`.

    IMPORTANT — do NOT compare ``n_eff`` directly to this product. A logged candidate's assignment is a
    full partial MAP, so the number of distinct (map × lexeme × segmentation) triples (``n_eff``) can
    legitimately exceed this per-ATOM product (which counts single sign→value pairs); doing so trips a
    FALSE over-bound (the original defect). The correct tripwire is the PER-DIMENSION check in
    :meth:`SearchLog.bound_report` / :func:`check_bound`, which bounds each observable dimension
    (distinct pairs ≤ S·V, distinct signs ≤ S, distinct lexemes ≤ R_L, distinct segmentations ≤ G_seg)
    — none of which an honest joint-map log can exceed.

    Any factor ``<= 0`` collapses the product to 0 (an empty / degenerate search space).
    """
    factors = (int(s_unknown), int(v_branch), int(r_l), int(f), int(g_seg))
    if any(x <= 0 for x in factors):
        return 0
    bound = 1
    for x in factors:
        bound *= x
    return bound


def over_bound_flag(observed: int, cap: int) -> bool:
    """True iff an OBSERVED distinct count exceeds its per-dimension ``cap`` — under-specified cap or a
    dedup bug. A correct cap for the right dimension (see :func:`check_bound`) can never be exceeded by
    an honest, properly-canonicalized log, so a True flag is a defect to surface, not a verdict input.
    """
    return observed > cap


def check_bound(log: "SearchLog", s_unknown: int, v_branch: int, r_l: int, f: int,
                g_seg: int) -> Dict[str, object]:
    """Per-dimension sanity report for a logged search (§B.2). Takes the LOG (not a bare n_eff) so the
    tripwire can bound each OBSERVABLE dimension rather than the joint ``n_eff`` (the original false-
    positive). Returns the :meth:`SearchLog.bound_report` dict, plus the atomic-product ``bound`` as a
    reference scale and ``fill_ratio = n_eff / bound`` — a low fill ratio is the SILENT failure
    (under-logging), a True ``over_bound`` (any dimension) is the LOUD one (under-specified cap / dedup
    bug). ``f`` (families) is carried only into the reference product, not the per-dimension caps.
    """
    report = log.bound_report(s_unknown, v_branch, r_l, g_seg)
    bound = sanity_upper_bound(s_unknown, v_branch, r_l, f, g_seg)
    report["bound"] = bound
    report["fill_ratio"] = (log.n_eff / bound) if bound > 0 else None
    return report


# --------------------------------------------------------------------------- #
# CLI demo — log a handful of candidates (incl. duplicates), prove dedup
# --------------------------------------------------------------------------- #
def main(argv: Optional[Sequence[str]] = None) -> int:
    import argparse
    import json

    p = argparse.ArgumentParser(description="N_eff instrumentation (design §B.2) — dedup demo")
    p.add_argument("--json", action="store_true", help="emit JSON")
    args = p.parse_args(argv)

    log = SearchLog()
    # A handful of candidates the retrieval 'scored'. Note the deliberate duplicates:
    #  - the same assignment written in a DIFFERENT order        -> must collapse to one identity
    #  - the same segmentation as a string vs a list of segments -> must collapse to one identity
    #    (the string MUST be the canonical \x1f-joined form for this to hold; a string is taken
    #     verbatim, a sequence is joined with \x1f)
    #  - the SAME triple re-scored (a replayed retry)            -> must NOT inflate n_eff
    candidates = [
        ({"*301": "na", "*311": "ki"}, "nakim", ["na", "kim"]),       # base
        ({"*311": "ki", "*301": "na"}, "nakim", "na\x1fkim"),         # reordered map + str seg == dup
        ({"*301": "na", "*311": "ki"}, "nakim", ["na", "kim"]),       # exact replay == dup
        ({"*301": "na"}, "nawaya", ["na", "wa", "ya"]),              # distinct
        ({"*301": "na"}, "nawaya", ["naw", "aya"]),                  # distinct (other segmentation)
        ({"*301": "da"}, "nawaya", ["na", "wa", "ya"]),             # distinct (other value)
    ]
    for assignment, lexeme, seg in candidates:
        log.log_candidate(assignment, lexeme, seg)

    # Sanity report for this toy space: 2 free signs, 2 values/sign, 2 roots, 1 family, 3 segs
    # (the log holds 3 distinct segmentations: na|kim, na|wa|ya, naw|aya — declare them honestly so
    # the per-dimension tripwire passes; declaring g_seg=2 would correctly fire over_bound).
    info = check_bound(log, s_unknown=2, v_branch=2, r_l=2, f=1, g_seg=3)
    out = {
        "n_logged": log.n_logged,
        "n_eff": log.n_eff,
        "bound": info["bound"],
        "over_bound": info["over_bound"],
        "fill_ratio": info["fill_ratio"],
        "distinct_candidates": [
            {"assignment": list(a), "lexeme": lx, "segmentation": sg.split("\x1f")}
            for (a, lx, sg) in log.candidates()
        ],
        "citation": CITATION_DESIGN,
    }
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(f"logged {log.n_logged} candidates -> n_eff = {log.n_eff} distinct "
              f"(dedup removed {log.n_logged - log.n_eff})")
        print(f"sanity bound = {info['bound']}  over_bound = {info['over_bound']}  "
              f"fill_ratio = {info['fill_ratio']}")
        for a, lx, sg in log.candidates():
            print(f"  {dict(a)} | {lx} | {sg.split(chr(0x1f))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
