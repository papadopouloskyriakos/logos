#!/usr/bin/env python3
"""litindex.py — literature index + L_known/L_virgin partition (logos comparison-layer §C.1, §C.2).

This module is the *decontamination* mechanism the design calls the necessary-but-not-sufficient
first line against regurgitation (§C.1): a frontier model has read Gordon, Best, Di Mino, so a
proposed correspondence that merely reproduces a *published* sign-value is shared-source
contamination, NOT independent evidence. We index published Linear A sign-value / correspondence
claims; any proposed correspondence matching the index is tagged ``literature_match`` and
quarantined (it may be tested, but can never count as discovery).

§C.2 is the decisive generalization test: partition signs into

  - ``L_known``  — at least one published proposal references the sign, and
  - ``L_virgin`` — no published proposal references it.

"Discovery claims may rest only on ``L_virgin`` held-out success" — regurgitation can only return
what is in the literature, so a system that is right about literature-known signs but useless on the
untouched ``L_virgin`` signs memorized rather than discovered. :func:`virgin_support` isolates the
share of held-out support attributable to ``L_virgin`` signs — the §E gate clause "support
generalizes to L_virgin signs".

SCOPE + HONESTY (read before extending): this is the MECHANISM plus a small, genuinely-public SEED
— it is NOT the exhaustive literature index (a separate, deferred Phase-0 task; see design §D step 2).
The seed contains only well-known, citable published proposals: the standard GORILA Linear-B-value
transfers (the homomorphic Linear A syllabograms transcribed with their Linear B values, after
Ventris 1953) and the two universally-published Linear A accounting readings (KU-RO "total", KI-RO
"deficit"). Each carries a source + year. The seed is deliberately CONSERVATIVE: a sign wrongly
left out of the index is wrongly granted ``L_virgin`` status, which is the *dangerous* direction
(it could let a regurgitated value masquerade as a discovery), so a seed must be expanded toward
completeness — never padded with uncertain attributions. When in doubt a claim is OMITTED.

Pure stdlib + (optional) json for the on-disk artifact. Deterministic: :func:`load_index` with the
default (embedded) seed is a pure function of the module source.
"""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Set

CITATION_DESIGN = (
    "logos comparison-layer §C.1 (literature index + quarantine: a proposed correspondence matching "
    "a published claim is tagged literature_match and can never count as discovery) and §C.2 "
    "(L_known / L_virgin partition: discovery claims may rest only on L_virgin held-out success)."
)
CITATION_GORILA = (
    "GORILA = L. Godart & J.-P. Olivier, 'Recueil des inscriptions en Linéaire A' (Études "
    "crétoises 21, 1976-1985) — the standard critical edition whose transliteration assigns "
    "homomorphic Linear A signs the phonetic value of their Linear B look-alikes."
)
CITATION_VENTRIS = (
    "M. Ventris & J. Chadwick 1953 — the Linear B decipherment that fixes the syllabic values "
    "transferred to the homomorphic Linear A (AB-series) signs."
)
CITATION_ACCOUNTING = (
    "KU-RO 'total/sum' and KI-RO 'deficit/owed' are the two near-universally accepted Linear A "
    "lexical readings, recurring at the foot of Linear A accounting lists; published throughout the "
    "corpus literature (GORILA; J. G. Younger, 'Linear A Texts in phonetic transcription', the "
    "public online edition)."
)

# A loud, machine-readable flag so no downstream consumer mistakes the seed for the full index.
SEED_NONEXHAUSTIVE = True
SEED_NOTE = (
    "NON-EXHAUSTIVE SEED — placeholder for the full §C.1 literature index (deferred). Contains only "
    "genuinely-public, well-known, citable proposals. A sign absent here is treated as L_virgin, "
    "which is the dangerous direction; EXPAND toward completeness, never pad with uncertain claims."
)


# --------------------------------------------------------------------------- #
# Schema
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class LitClaim:
    """One published Linear A sign-value / correspondence claim.

    Fields:
      sign           — the sign or '-'-joined sign-sequence the claim is about (GORILA naming,
                       e.g. "DA", "*301", or the sequence "KU-RO"). Matched against candidate
                       correspondences for quarantine and used to mark component signs L_known.
      proposed_value — the published reading (a phonetic value like "da", or a lexical gloss for a
                       sequence reading like "total").
      source         — citable source string (edition / author). MUST be non-empty.
      year           — publication year. MUST be a positive int.
      claim_type     — "lb_value_transfer" | "lexical_reading" | "semitic_proposal" | ... (free
                       string; the discipline machinery only needs it for provenance reporting).
      note           — optional human note.
    """

    sign: str
    proposed_value: str
    source: str
    year: int
    claim_type: str
    note: str = ""


# --------------------------------------------------------------------------- #
# The seed (genuinely-public, cited)
# --------------------------------------------------------------------------- #
# The homomorphic Linear A syllabograms carried over from Linear B with their Linear B value. The
# romanized GORILA sign-name IS the transferred value (DA -> /da/), so the proposed_value is derived
# from the name rather than re-typed by hand. This is the single most-published, least-controversial
# class of Linear A sign-value proposal (§C.1's "Linear-B-value transfers that are common knowledge").
LB_TRANSFER_SIGNS = (
    "A", "DA", "DE", "DI", "DU", "E", "I", "JA", "JE", "JO", "JU",
    "KA", "KE", "KI", "KO", "KU", "MA", "ME", "MI", "MU",
    "NA", "NE", "NI", "NU", "NWA", "O", "PA", "PE", "PI", "PO", "PU",
    "QA", "QE", "QI", "RA", "RE", "RI", "RO", "RU",
    "SA", "SE", "SI", "SU", "TA", "TE", "TI", "TO", "TU",
    "U", "WA", "WE", "WI", "ZA", "ZE", "ZO",
)

# The two near-universally accepted Linear A lexical (sequence) readings.
_LEXICAL_READINGS = (
    ("KU-RO", "total", "GORILA; Younger, Linear A Texts (public)", 1985,
     "Sum recurring at the foot of Linear A accounting lists — the most secure LA reading."),
    ("KI-RO", "deficit", "GORILA; Younger, Linear A Texts (public)", 1985,
     "The complementary 'owed/deficit' accounting term."),
)


def _build_seed() -> List[LitClaim]:
    """Assemble the embedded seed deterministically from the cited constants."""
    claims: List[LitClaim] = []
    for sign in LB_TRANSFER_SIGNS:
        claims.append(
            LitClaim(
                sign=sign,
                proposed_value=sign.lower(),     # GORILA romanization == transferred LB value
                source="GORILA (Godart & Olivier 1976-1985); LB values after Ventris 1953",
                year=1976,
                claim_type="lb_value_transfer",
                note="homomorphic Linear A sign read with its Linear B value",
            )
        )
    for sign, value, source, year, note in _LEXICAL_READINGS:
        claims.append(
            LitClaim(sign=sign, proposed_value=value, source=source, year=year,
                     claim_type="lexical_reading", note=note)
        )
    # deterministic order: sort by (claim_type, sign) so the seed is byte-stable regardless of
    # construction order — a control must be reproducible.
    claims.sort(key=lambda c: (c.claim_type, c.sign))
    return claims


SEED_CLAIMS: List[LitClaim] = _build_seed()

# Default on-disk artifact (public-literature metadata — small, cited, not vendor corpus).
_DEFAULT_JSON = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "corpus", "silver", "literature_index.json",
)


# --------------------------------------------------------------------------- #
# Loader
# --------------------------------------------------------------------------- #
def load_index(path: Optional[str] = None) -> List[LitClaim]:
    """Load the literature index.

    ``path is None`` (default) returns a COPY of the embedded :data:`SEED_CLAIMS` — a pure function
    of the module source, requiring no file I/O, so callers and tests are deterministic. If ``path``
    is given it is parsed as the JSON artifact written by :func:`dump_index` / the CLI (a list of
    claim objects). Loaded claims are returned in the same deterministic (claim_type, sign) order.
    """
    if path is None:
        return list(SEED_CLAIMS)
    with open(path, "r", encoding="utf-8") as fh:
        payload = json.load(fh)
    rows = payload["claims"] if isinstance(payload, dict) else payload
    claims = [
        LitClaim(
            sign=r["sign"],
            proposed_value=r["proposed_value"],
            source=r["source"],
            year=int(r["year"]),
            claim_type=r["claim_type"],
            note=r.get("note", ""),
        )
        for r in rows
    ]
    claims.sort(key=lambda c: (c.claim_type, c.sign))
    return claims


def dump_index(claims: Sequence[LitClaim], path: str) -> None:
    """Serialize an index to the JSON artifact (records the non-exhaustive seed flag + note)."""
    payload = {
        "_seed_nonexhaustive": SEED_NONEXHAUSTIVE,
        "_seed_note": SEED_NOTE,
        "_citations": [CITATION_DESIGN, CITATION_GORILA, CITATION_VENTRIS, CITATION_ACCOUNTING],
        "n_claims": len(claims),
        "claims": [asdict(c) for c in claims],
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False, sort_keys=False)
        fh.write("\n")


# --------------------------------------------------------------------------- #
# §C.2 partition
# --------------------------------------------------------------------------- #
def _atomic_signs(sign_field: str) -> List[str]:
    """Expand a claim's ``sign`` into the atomic signs it references.

    A sequence reading like "KU-RO" is a *published proposal touching* both KU and RO, so each
    component sign is no longer literature-virgin. Single signs ("*301", "DA") expand to themselves.
    """
    return [tok for tok in (t.strip() for t in sign_field.split("-")) if tok]


def known_signs(index: Iterable[LitClaim]) -> Set[str]:
    """The set of atomic signs referenced by any claim in ``index`` (the literature-known signs)."""
    out: Set[str] = set()
    for claim in index:
        out.update(_atomic_signs(claim.sign))
    return out


def partition_signs(all_signs: Iterable[str],
                    index: Iterable[LitClaim]) -> Dict[str, Set[str]]:
    """Partition ``all_signs`` into ``L_known`` / ``L_virgin`` against the literature ``index`` (§C.2).

    A sign is ``L_known`` iff at least one indexed claim references it (directly or as a component of
    a sequence reading); otherwise ``L_virgin``. Returns ``{'L_known': set, 'L_virgin': set}``; the
    two sets partition ``set(all_signs)`` exactly (disjoint, union == input). Signs referenced by the
    index but absent from ``all_signs`` are ignored (the partition is of the corpus inventory, not of
    the index).
    """
    signs = set(all_signs)
    lit = known_signs(index)
    l_known = {s for s in signs if s in lit}
    l_virgin = signs - l_known
    return {"L_known": l_known, "L_virgin": l_virgin}


# --------------------------------------------------------------------------- #
# §C.1 quarantine helper
# --------------------------------------------------------------------------- #
def matching_claims(sign: str, index: Iterable[LitClaim],
                    proposed_value: Optional[str] = None) -> List[LitClaim]:
    """Indexed claims that a proposed correspondence collides with (the §C.1 quarantine test).

    Matches on the atomic sign overlap between ``sign`` (which may itself be a '-'-joined sequence)
    and each claim. When ``proposed_value`` is given, only claims whose value also matches
    (case-insensitive) are returned — an exact-correspondence hit; otherwise any sign-level hit is
    returned. The caller tags any non-empty result ``literature_match`` and quarantines it.
    """
    atoms = set(_atomic_signs(sign))
    pv = None if proposed_value is None else proposed_value.strip().lower()
    hits: List[LitClaim] = []
    for claim in index:
        if atoms & set(_atomic_signs(claim.sign)):
            if pv is None or claim.proposed_value.strip().lower() == pv:
                hits.append(claim)
    return hits


def literature_match(sign: str, index: Iterable[LitClaim],
                     proposed_value: Optional[str] = None) -> bool:
    """True iff a proposed correspondence collides with the index (⇒ quarantine; never discovery)."""
    return bool(matching_claims(sign, index, proposed_value))


# --------------------------------------------------------------------------- #
# §E gate clause: support generalizes to L_virgin signs
# --------------------------------------------------------------------------- #
def virgin_support(per_sign_support: Mapping[str, float],
                   partition: Mapping[str, Set[str]]) -> float:
    """Share of held-out support attributable to ``L_virgin`` signs (the §E generalization clause).

    DEFINITION. ``per_sign_support`` maps a sign to a non-negative support score (e.g. that sign's
    contribution to held-out S_lex). We return the FRACTION of total support mass that falls on
    ``L_virgin`` signs::

        virgin_support = sum(support[s] for s in L_virgin) / sum(support[s] for s in known∪virgin)

    Only signs that the partition classifies (``L_known`` ∪ ``L_virgin``) enter either sum;
    unclassified signs in the mapping are ignored. The result is in [0, 1]: 1.0 means *all* the
    held-out support is on literature-virgin signs (the strongest anti-regurgitation evidence —
    nothing in the literature could have supplied it); a low value means the support is concentrated
    on signs whose values are already published (consistent with memorization).

    DEGENERATE / NO-POWER PATH (reported honestly, never a misleading real-looking 0):
    if there is no support mass at all — an empty mapping, all-zero (or non-positive) scores, or no
    classified signs — the function returns **0.0**, which here means "no virgin-attributable support
    exists / the test has no power", and MUST NOT be read as evidence that support fails to generalize.
    A caller gating on this value must first confirm total support is positive (the statistic has
    power) before interpreting a low fraction as a generalization failure.
    """
    l_known = set(partition.get("L_known", set()))
    l_virgin = set(partition.get("L_virgin", set()))
    classified = l_known | l_virgin

    total = 0.0
    virgin = 0.0
    for sign, score in per_sign_support.items():
        if sign not in classified:
            continue
        s = float(score)
        if s <= 0.0:                       # support scores are non-negative; ignore non-positive noise
            continue
        total += s
        if sign in l_virgin:
            virgin += s
    if total <= 0.0:                       # degenerate / no-power: honest 0.0, not a real null
        return 0.0
    return virgin / total


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main(argv: Optional[Sequence[str]] = None) -> int:
    import argparse

    p = argparse.ArgumentParser(description="Literature index + L_known/L_virgin partition (§C.1/§C.2)")
    p.add_argument("--index", default=None,
                   help="path to a JSON index; default = embedded seed")
    p.add_argument("--emit", default=None,
                   help="write the (loaded) index to this JSON path and exit")
    p.add_argument("--emit-default", action="store_true",
                   help="write the embedded seed to corpus/silver/literature_index.json")
    p.add_argument("--signs", nargs="*", default=None,
                   help="signs to partition into L_known / L_virgin")
    args = p.parse_args(argv)

    index = load_index(args.index)

    if args.emit_default:
        dump_index(index, _DEFAULT_JSON)
        print(json.dumps({"emitted": _DEFAULT_JSON, "n_claims": len(index),
                          "seed_nonexhaustive": SEED_NONEXHAUSTIVE}, indent=2))
        return 0
    if args.emit:
        dump_index(index, args.emit)
        print(json.dumps({"emitted": args.emit, "n_claims": len(index)}, indent=2))
        return 0

    out: Dict[str, object] = {
        "n_claims": len(index),
        "seed_nonexhaustive": SEED_NONEXHAUSTIVE,
        "n_known_signs": len(known_signs(index)),
    }
    if args.signs:
        part = partition_signs(args.signs, index)
        out["L_known"] = sorted(part["L_known"])
        out["L_virgin"] = sorted(part["L_virgin"])
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
