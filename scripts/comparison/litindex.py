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

SCOPE + HONESTY (read before extending): this is the MECHANISM plus a still-growing SEED — it is NOT
yet the exhaustive literature index (a separate, deferred Phase-0 task; see design §D step 2). The
seed contains genuinely-public, citable published proposals: the standard GORILA Linear-B-value
transfers (homomorphic Linear A syllabograms transcribed with their Linear B values, after Ventris
1953); the two universally-published accounting readings (KU-RO "total", KI-RO "deficit"); and six
published WEST-SEMITIC lexical proposals (added 2026-06-30) — C. H. Gordon's su-pu / ka-ro-pa /
su-pa-ra / ku-ro / ya-ne (Evidence for the Minoan Language, 1966) and J. Best's a-sa-sa-ra-me =
"oh Asherah!" (Talanta, 1981). Every Semitic claim was independently verified (chiefly Rendsburg
1996) before inclusion; unverifiable candidates (qa-pa=kappu, a Semitic ki-ro) were OMITTED. The
Semitic readings are DISPUTED — indexed so a model regurgitating them is caught, NEVER as accepted
readings. Each carries a source + year. The seed is deliberately CONSERVATIVE: a sign wrongly left
out is wrongly granted ``L_virgin`` status, the *dangerous* direction (it could let a regurgitated
value masquerade as discovery), so expand toward completeness — never pad with uncertain
attributions. When in doubt a claim is OMITTED.

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
CITATION_GORDON = (
    "C. H. Gordon, 'Evidence for the Minoan Language' (Ventnor Publishers, 1966), synthesizing his "
    "1957- articles ('Notes on Minoan Linear A', Antiquity 31, 1957) — the West-Semitic reading of "
    "Linear A. Independently described by G. A. Rendsburg, \"'Someone Will Succeed in Deciphering "
    "Minoan': Cyrus H. Gordon and Minoan Linear A\", Biblical Archaeologist 59:1 (1996) 36-43 "
    "(JSTOR 3210534). A DISPUTED hypothesis, rejected by mainstream scholarship — indexed for "
    "DECONTAMINATION (recording what was PUBLISHED so a model regurgitating it is caught), NEVER as "
    "an accepted reading."
)
CITATION_BEST = (
    "J. G. P. Best, 'YASSARAM!', Talanta 13 (1981) 17-21 — reading (j)a-sa-sa-ra-me as the vocative "
    "'oh Asherah!'. Builds on Gordon's Semitic-Minoan thesis; an older Asasara-as-goddess reading "
    "(Sundwall; A. Evans) was refuted by M. Pope, 'The Minoan Goddess Asasara - An Obituary', BICS 8 "
    "(1961) 29-31. DISPUTED — indexed for decontamination, not as an accepted reading."
)
CITATION_DIMINO = (
    "T. Di Mino (2026), 'Ya Diktu: Grammar of the Minoan Peak Sanctuary Libation Formula' (draft; "
    "recorded in docs/linear-a-claims-2026.md). Reads the libation word A-TA-I-*301-WA-JA via a "
    "/na/-initial value for *301 as Semitic N-W-Y 'to dwell' (nawaya). DISPUTED + NOT independently "
    "verified: contradicted by B. Davis (i-*301 = the verb 'give/dedicate'; structural V-S-O analysis, "
    "Kadmos 52, 2013, and Minoan Stone Vessels with Linear A Inscriptions, Aegaeum 36, 2014), and the "
    "match is partial (~1/5 of one word to 2/3 of a root). ATTRIBUTION NOTE (audit 2026-06-30): the "
    "i-*301='give/dedicate' counter is BRENT DAVIS's — do NOT re-attribute it to Steele 2024; the "
    "Steele-2024 item in hand is O. Dickinson's book review (JGA), which contains NO *301 gloss (its "
    "p.474 'prayers or dedications' line is neutral on the dwell-vs-give crux). The current "
    "expert-review benchmark, Salgarella 2025 §8 'Which Language Does Linear A Encode?', is PAYWALLED "
    "(only the section title is in hand) — checking *301 against it is an OPEN item, not resolved. "
    "Indexed to QUARANTINE the single highest-profile Linear A reading so any model regurgitating it "
    "is caught — NEVER as an accepted reading."
)
CITATION_SPICES = (
    "E. Salgarella, F. Bellinato & S. Ferrara, 'On Aegean spices: decipherment prospects on Linear A "
    "and B spice-related signs', Kadmos 64(1/2):29-44 (2025), doi:10.1515/kadmos-2025-0002. The "
    "KA+PO monogram = karphos 'cinnamon' reading originates with A. Sacconi, Kadmos 11 (1972):22-26; "
    "the fenugreek alternative with B. Foster (1974, Duke diss.). DISPUTED/SPECULATIVE by the authors' "
    "own hedging — indexed for DECONTAMINATION (these are now PUBLIC 2025 readings a model could "
    "regurgitate as 'discovery' in the L_virgin test), NEVER as accepted readings."
)

# A loud, machine-readable flag so no downstream consumer mistakes the seed for the full index.
SEED_NONEXHAUSTIVE = True
SEED_NOTE = (
    "NON-EXHAUSTIVE SEED — still a placeholder for the full §C.1 literature index (deferred). Contains "
    "genuinely-public, citable proposals: the GORILA Linear-B-value transfers, the KU-RO/KI-RO "
    "accounting readings, and (added 2026-06-30, each independently verified) six published "
    "WEST-SEMITIC proposals — Gordon's su-pu/ka-ro-pa/su-pa-ra/ku-ro/ya-ne (Evidence for the Minoan "
    "Language, 1966) and Best's a-sa-sa-ra-me='oh Asherah!' (Talanta 1981). Added 2026-06-30 (audit): "
    "four PUBLIC 2025 logographic/composite readings from Salgarella/Bellinato/Ferrara, Kadmos 64 "
    "('On Aegean spices') — A646/A341='root', *127(KA+PO)='spice', LB *157='root' — SPECULATIVE by the "
    "authors' own hedging, indexed so they cannot leak into the L_virgin test as 'discovery'. "
    "Unverifiable candidates (qa-pa=kappu, a Semitic ki-ro) were OMITTED. All disputed readings are "
    "indexed to CATCH regurgitation of them, never as accepted readings. A sign absent here is treated "
    "as L_virgin (the dangerous direction); EXPAND toward completeness, never pad with uncertain "
    "attributions."
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

# Published West-Semitic LEXICAL proposals for specific Linear A words (the 'Semitic hypothesis').
# VERIFIED 2026-06-30 against sources INDEPENDENT of the BAS Library sidebar — chiefly G. A.
# Rendsburg, Biblical Archaeologist 59:1 (1996), which enumerates Gordon's THREE vessel equations
# (su-pu, ka-ro-pa, su-pa-ra). Two candidates FAILED independent corroboration and were OMITTED, not
# padded in: (a) qa-pa = Akkadian kappu — only the BAS page attributes it to Gordon; Rendsburg's
# list of three omits it; (b) a Semitic etymology for KI-RO — none attributable (the published
# Semitic kull etymology belongs to KU-RO, a different word). proposed_value is the consonantal
# Semitic cognate/name (so a later cognate-matcher can hit it); the gloss + caveat live in the note.
# (sign, value, source, year, note)
_SEMITIC_PROPOSALS = (
    ("SU-PU", "sp", CITATION_GORDON, 1966,
     "Gordon: su-pu/su-po = Ugaritic sp / Hebrew sap 'basin, bowl' (the LA word is followed by a "
     "pot pictogram). First proposed Antiquity 31 (1957). DISPUTED, not an accepted reading."),
    ("KA-RO-PA", "krpn", CITATION_GORDON, 1966,
     "Gordon: ka-ro-pa = Ugaritic krpn 'goblet/large drinking-cup'. (The 'Akkadian karpu / carafe' "
     "gloss is a popularization, NOT in Rendsburg's primary account.) First proposed Antiquity 31 (1957)."),
    ("SU-PA-RA", "spl", CITATION_GORDON, 1966,
     "Gordon: su-pa-ra = Ugaritic spl / Hebrew sepel 'bowl' (l/r undistinguished in the script). DISPUTED."),
    ("KU-RO", "kull", CITATION_GORDON, 1966,
     "Gordon's SEMITIC ETYMOLOGY of the accounting term ku-ro 'total' = Semitic kull / Hebrew kol "
     "'all, whole'. (The accounting reading 'total' is near-universal — see the lexical_reading entry.)"),
    ("JA-NE", "yn", CITATION_GORDON, 1966,
     "Gordon (transcribing it 'ya-ne'): = West Semitic 'wine', Hebrew yayin / Ugaritic yn; on a wine "
     "pithos from Knossos (Evidence for the Minoan Language 1966, Plate X). Sign keyed JA per GORILA/"
     "corpus convention (the corpus has no 'YA'). DISPUTED."),
    ("A-SA-SA-RA-ME", "asherah", CITATION_BEST, 1981,
     "Best (1981): (j)a-sa-sa-ra-me = vocative 'oh Asherah!' (NW Semitic divine name; Ugaritic "
     "Athirat/atrt). The Linear A libation-formula word; ATTRIBUTION is to Best, NOT Gordon. DISPUTED."),
    # Di Mino's highest-profile anchor — DISPUTED + UNVERIFIED, indexed ONLY to quarantine it (so a model
    # reproducing *301=/na/ is caught) and to mark *301 L_known (excluding it from any L_virgin discovery set).
    ("*301", "na", CITATION_DIMINO, 2026,
     "Di Mino (2026) reads *301 with a /na/-initial value in A-TA-I-*301-WA-JA -> Semitic N-W-Y 'to "
     "dwell' (nawaya). DISPUTED + NOT independently verified (Davis: i-*301 = verb 'give/dedicate'); "
     "indexed to QUARANTINE the single highest-profile Linear A reading, NEVER as accepted."),
)

# Published 2025 LOGOGRAPHIC / composite-sign readings (Salgarella, Bellinato & Ferrara, Kadmos 64,
# 2025, 'On Aegean spices'). Indexed because they are now PUBLIC and a model could regurgitate them as
# "discovery" in the L_virgin generalization test — exactly the §C.2 leak this partition exists to
# close (audit 2026-06-30 flagged the gap). They are SPECULATIVE by the authors' OWN hedging: the
# KA+PO spice reading has THREE competing values (cinnamon / fenugreek / Greek karpos 'fruit'), and the
# A646 'root' reading rests on a SINGLE hapax on the damaged HT 33 — which FAILS logos's own unicity
# standard. They also use LB-value backward-projection (AB39=/pi/ acrophony) — the same move logos
# quarantines Di Mino for; indexed to QUARANTINE, never as accepted. (sign, value, source, year, note)
_LOGOGRAPHIC_READINGS = (
    ("A646", "root", CITATION_SPICES, 2025,
     "Salgarella/Bellinato/Ferrara 2025: A646 lower element = RAD(ix) 'root', with AB39=/pi/ "
     "acrophonic for a Minoan 'root' word. SPECULATIVE (authors' hedge); a SINGLE hapax on the damaged "
     "HT 33 — fails logos's unicity standard; uses LB-value backward-projection. Quarantine, not accepted."),
    ("A341", "root", CITATION_SPICES, 2025,
     "Salgarella et al. 2025: A341 shares the lower 'root' (RADix) element with A646 (graphic "
     "decomposition only). SPECULATIVE; indexed so it cannot masquerade as an L_virgin discovery."),
    ("*127", "spice", CITATION_SPICES, 2025,
     "The KA+PO monogram (*127) read as a spice logogram: Sacconi 1972 'cinnamon' vs Foster 1974 "
     "'fenugreek' — THREE competing options (cf. Linear B ka-po = Greek karpos 'fruit'). DISPUTED + "
     "multiple-option; indexed to quarantine."),
    ("*157", "root", CITATION_SPICES, 2025,
     "Linear B *157 read as RAD(ix)+/wi/ 'root' (Salgarella et al. 2025) — the LB comparandum for the "
     "A646/A341 'root' reading. SPECULATIVE; indexed to quarantine."),
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
    for sign, value, source, year, note in _SEMITIC_PROPOSALS:
        claims.append(
            LitClaim(sign=sign, proposed_value=value, source=source, year=year,
                     claim_type="semitic_proposal", note=note)
        )
    for sign, value, source, year, note in _LOGOGRAPHIC_READINGS:
        claims.append(
            LitClaim(sign=sign, proposed_value=value, source=source, year=year,
                     claim_type="logographic_reading", note=note)
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
        "_citations": [CITATION_DESIGN, CITATION_GORILA, CITATION_VENTRIS, CITATION_ACCOUNTING,
                       CITATION_GORDON, CITATION_BEST, CITATION_DIMINO],
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
