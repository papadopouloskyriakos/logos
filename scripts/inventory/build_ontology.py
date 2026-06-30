#!/usr/bin/env python3
"""build_ontology.py -- Layered Linear A sign inventory ontology.

Expert-audit mandate (docs/findings/2026-06-30-expert-redteam-synthesis.md §5):
  "INHERIT from GORILA/SigLA, do NOT cluster. 259 -> ~90 is a parse + metadata join,
   not a learning problem. Build a layered sign ontology: raw observation ->
   diplomatic token -> canonical sign id -> allograph family -> functional class ->
   value hypothesis. Keep logograms + numerals as SEPARATE channels."

This script parses corpus/silver/inscriptions.json into that layered ontology and emits:
  - corpus/silver/signs_ontology.json            (canonical_sign_id -> metadata)
  - corpus/silver/inventory_syllabograms_raw.json
  - corpus/silver/inventory_syllabograms_conservative.json
  - corpus/silver/inventory_syllabograms_exploratory.json

=== GORILA / SigLA / lineara.xyz convention used for AB-vs-A-only ===

The lineara.xyz (Douros) transliteration -- like GORILA (Godart & Olivier, *Recueil des
inscriptions en linear A*, 1976-85) and the SigLA sign list -- encodes the distinction
DIRECTLY in the token string:

  * AB-series  = signs SHARED with Linear B that have known Mycenaean-Greek phonetic
    values. In the data these are bare CV / V syllabic strings drawn from the canonical
    Linear A syllabary (A, TA, QE, KU, ...), including subscripted allographs RA2, PA3,
    TA2, PU2 (Unicode ₂₃ or ASCII 23 suffix). The canonical syllable<->glyph table is
    /tmp/lineara/items_analysis/syllables.txt; the AB syllabary is exactly the entries
    BEFORE the *-series begins (the ~60 signs with deciphered values).

  * A-only (*-series) = signs that appear in Linear A but NOT in Linear B -- no
    deciphered value. In the data these carry a literal '*' prefix followed by a GORILA
    catalogue number (*301, *34, *306, ...). This is the GORILA/SigLA editorial
    convention for "undeciphered": the star marks "value unknown".

  * F/M-suffixed *-series (*21F, *22M, *28B ...) are SEXED ideogram variants (female /
    male / animal) -> classified LOGOGRAM, not syllabogram (they denote a commodity
    subtype, not a phoneme).

  * The *800-*929 range is the Aegean FRACTION / weight series (cross-ref
    numbers.txt) -> classified FRACTION, not syllabogram.

  * Multi-letter commodity abbreviations that are NOT CV syllables (OLE/OLIV olive-oil,
    GRA grain, VIN wine, VIR person, HIDE hide, TELA cloth, CYP safflower, CAP caprid,
    AROM aromatics, VAS vessel, GAL measure, VS vase) -> LOGOGRAM.

  * Ligatures (token contains '+') are decomposed: the HEAD determines the ligature's
    functional class; for the syllabogram stream, syllabogram-headed ligatures are
    decomposed into their syllabogram components (a ligature is a cluster, not a new
    sign). Logogram-headed ligatures go to the logogram channel and never enter the
    syllabogram stream.

  * Editorial damage markers ('[', ']', '[?]', '[ ]') are preserved in the
    diplomatic_token and STRIPPED to recover the base sign for canonical id + class
    (represent damage with masks, not deletion -- redteam §5).

Anything that cannot be confidently placed by these rules is classed 'uncertain' rather
than guessed. Pure stdlib; deterministic; order-stable output.
"""
import argparse
import json
import os
import re
from collections import Counter, OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))          # .../logos
SILVER = os.path.join(ROOT, "corpus", "silver", "inscriptions.json")
OUT_DIR = os.path.join(ROOT, "corpus", "silver")

# ---------------------------------------------------------------------------
# Canonical AB syllabary (shared w/ Linear B, known values).
# Sourced from /tmp/lineara/items_analysis/syllables.txt -- the signs that carry
# a deciphered value, i.e. every entry before the *-series begins. Subscripted
# allographs (RA2/PA3/TA2/PU2) are DISTINCT signs (distinct Linear-B values:
# rya / ai / two / rya) and are deliberately NOT merged in the conservative set.
# ---------------------------------------------------------------------------
AB_VALUES = sorted(set("""A AU DA DE DI DU E I JA JE JU KA KE KI KO KU
MA ME MI MO MU NA NE NI NU NWA O PA PA2 PA3 PI PO PU PU2 PU3 QA QE QI QO
RA RA2 RA3 RE RI RO RU SA SE SI SO SU TA TA2 TA3 TE TI TO TU TWE TWO
U WA WE WI WO ZA ZE ZI ZO ZU PTE DWE DWO NWA RAI MO2 NO2""".split()))

# commodity ideogram heads (logograms). Drawn from the corpus + syllables.txt.
LOGOGRAM_HEADS = {
    "OLE", "OLEA", "OLEE", "OLEU", "OLIV",          # olive oil
    "GRA",                                            # grain / wheat
    "VIN", "VINa", "VINb",                           # wine
    "VIR",                                            # person / man
    "HIDE",                                           # hide / leather
    "TELA",                                           # cloth
    "CYP",                                            # safflower / cyperus
    "CAP", "CAPm",                                    # caprid / goat
    "BOS", "BOSm",                                    # bovid
    "AROM",                                           # aromatics
    "VAS", "VS",                                      # vessel / vase
    "GAL",                                            # liquid measure
    "MEN", "MUL", "MULm",                            # fig / murex / etc ideograms
    "QIf",                                            # (phonetic complement on logograms, kept w/ logo)
}

# *-series ranges that are FRACTIONS / fractional weights (Aegean fraction series).
# Cross-ref /tmp/lineara/items_analysis/numbers.txt: *800-*829 and *900-*906 carry
# fractional values (1/3, 1/5, 1/8 ...). These are NOT syllabograms.
def _is_fraction_star(num):
    return (800 <= num <= 829) or (900 <= num <= 906) or num == 701

# Fraction / quantity tokens (the L-series weight marks, omega measure, etc.)
FRACTION_TOKENS = {
    "L", "L2", "L3", "L4", "L6", "W", "X", "Y",
    "B", "D", "F", "H", "J", "K",                    # single-letter fraction marks (see numbers.txt)
    "BB", "DD", "EE", "FF",
    "OMEGA", "Ω",                               # the omega-like fraction glyph
    "double mina", "double_mina",
}

# sexed-ideogram suffixes -> the *-sign is a LOGOGRAM (female/male/beast variant)
_SEXED_SUFFIX = re.compile(r"\*[0-9]+[FM]$|.*[FM](?=$)")  # used carefully below

# Unicode Aegean numeral block: U+10100..U+1013F (1..90000 + fractions) and the
# Ancient-Greek / Linear-A fraction extensions up to U+1018A.
def _is_numeral_glyph(ch):
    if len(ch) != 1:
        return False
    cp = ord(ch)
    return (0x10100 <= cp <= 0x1018A) or (0x10D00 <= cp <= 0x10D3F)

# ---------------------------------------------------------------------------
# token normalisation helpers
# ---------------------------------------------------------------------------
_SUBSCRIPT = {"₀": "0", "₁": "1", "₂": "2", "₃": "3",
              "₄": "4", "₅": "5", "₆": "6", "₇": "7",
              "₈": "8", "₉": "9"}
_SUB_RE = re.compile("[" + "".join(_SUBSCRIPT.keys()) + "]")


def _ascii(tok):
    """Unicode subscripts -> ASCII digits (PA₃ -> PA3)."""
    return _SUB_RE.sub(lambda m: _SUBSCRIPT[m.group(0)], tok)


def _star_num(tok):
    m = re.match(r"\*(\d+)", tok)
    return int(m.group(1)) if m else None


def _strip_damage(tok):
    """Remove editorial damage brackets. '[?]' / '[ ]' / '[' / ']' -> '' (unknown).

    Returns (clean_head, damaged_flag, has_unknown_component)."""
    damaged = ("[" in tok) or ("]" in tok)
    # an explicit '[?]' or '[ ]' marks an UNKNOWN sign component, not a partial of head
    has_unknown = ("[?]" in tok) or ("[ ]" in tok) or ("[]" in tok)
    cleaned = tok.replace("[?]", "").replace("[ ]", "").replace("[]", "")
    cleaned = cleaned.replace("[", "").replace("]", "")
    cleaned = cleaned.strip("+").strip()
    return cleaned, damaged, has_unknown


def _allograph_family(canonical):
    """Graphic root: PA for PA/PA3, RA for RA/RA2, *131 for *131B/*131C, OLE for OLE+U."""
    c = _ascii(canonical)
    # star-series: family = *<number> (drop trailing variant letter)
    m = re.match(r"\*(\d+)", c)
    if m:
        return "*" + m.group(1)
    # syllable with subscript digit -> base CV/V
    m = re.match(r"([A-Z]+?)(\d+)$", c)
    if m:
        return m.group(1)
    return c


# ---------------------------------------------------------------------------
# classification core
# ---------------------------------------------------------------------------
def classify_token(raw):
    """Return a dict describing one raw token's place in the ontology.

    Keys: raw_observation, diplomatic_token, canonical_sign_id, allograph_family,
          functional_class, value_hypothesis, components (for ligatures),
          is_damaged, has_unknown_component."""
    rec = {
        "raw_observation": raw,
        "diplomatic_token": raw,
        "canonical_sign_id": None,
        "allograph_family": None,
        "functional_class": "uncertain",
        "value_hypothesis": None,
        "components": [],
        "is_damaged": False,
        "has_unknown_component": False,
    }
    if raw is None or (isinstance(raw, str) and raw in ("None", "")):
        rec["functional_class"] = "uncertain"
        rec["canonical_sign_id"] = "__DATA_ERROR__"
        rec["allograph_family"] = "__DATA_ERROR__"
        return rec

    ascii_tok = _ascii(raw)
    cleaned, damaged, has_unknown = _strip_damage(ascii_tok)
    rec["is_damaged"] = damaged
    rec["has_unknown_component"] = has_unknown
    # diplomatic token preserves the original notation (incl. damage) verbatim
    rec["diplomatic_token"] = raw

    comps = [c for c in cleaned.split("+") if c] if cleaned else []
    rec["components"] = comps
    head = comps[0] if comps else cleaned

    # ---- whole-token numeric / fraction glyphs first (single codepoint tokens) ----
    if _is_numeral_glyph(raw.strip()):
        rec["functional_class"] = "numeral"
        rec["canonical_sign_id"] = "NUM:" + hex(ord(raw.strip()))
        rec["allograph_family"] = "aegean-numeral"
        rec["value_hypothesis"] = "Aegean numeral glyph (numbers.txt)"
        return rec

    # ---- PUA / unencoded glyph ----
    if len(raw.strip()) == 1 and 0xF0000 <= ord(raw.strip()) <= 0xFFFFF:
        rec["functional_class"] = "uncertain"
        rec["canonical_sign_id"] = "PUA:" + hex(ord(raw.strip()))
        rec["allograph_family"] = "private-use-area"
        rec["value_hypothesis"] = "unencoded PUA glyph (needs epigrapher)"
        return rec

    # ---- determine the head's functional class ----
    head_class = _classify_head(head)

    # ---- ligatures: head determines channel ----
    if len(comps) >= 2:
        rec["functional_class"] = head_class if head_class != "uncertain" else "uncertain"
        rec["canonical_sign_id"] = _canonical_for(head, head_class) or cleaned
        rec["allograph_family"] = _allograph_family(rec["canonical_sign_id"])
        rec["value_hypothesis"] = _value_hint(head_class)
        return rec

    # ---- simple (non-ligature) token ----
    rec["functional_class"] = head_class
    rec["canonical_sign_id"] = _canonical_for(head, head_class) or cleaned
    rec["allograph_family"] = _allograph_family(rec["canonical_sign_id"])
    rec["value_hypothesis"] = _value_hint(head_class)
    return rec


def _classify_head(head):
    h = _ascii(head)
    if not h:
        return "uncertain"
    # numeral glyph
    if _is_numeral_glyph(h):
        return "numeral"
    # explicit fraction / weight token
    if h in FRACTION_TOKENS or h.lower().replace(" ", "_") in {t.lower() for t in FRACTION_TOKENS}:
        return "fraction"
    # *-series
    if h.startswith("*"):
        num = _star_num(h)
        if num is not None and _is_fraction_star(num):
            return "fraction"
        # sexed ideogram variant (*21F / *22M / *28B ...): F or M suffix on a *-number
        if re.match(r"\*\d+[FM]$", h):
            return "logogram"
        return "syllabogram-Aonly"
    # AB syllabogram (known Linear-B value)?
    if h in AB_VALUES:
        return "syllabogram-AB"
    # bare CV/V syllable pattern that we simply did not enumerate? -> AB if it matches
    if re.fullmatch(r"[AEIOU]|[BCDGHJKLMNPQRSTWZ][AEIOU]", h):
        return "syllabogram-AB"
    # commodity ideogram head
    if h in LOGOGRAM_HEADS:
        return "logogram"
    # single uppercase letter not otherwise recognised -> likely a fraction mark
    if re.fullmatch(r"[A-Z]", h):
        return "fraction"
    return "uncertain"


def _canonical_for(head, cls):
    h = _ascii(head)
    if cls == "numeral":
        return "NUM:" + hex(ord(h)) if len(h) == 1 else ("NUM:" + h)
    if cls == "fraction":
        if h.startswith("*"):
            return h
        return "FRAC:" + h
    if cls in ("syllabogram-AB", "syllabogram-Aonly"):
        return h
    if cls == "logogram":
        return "LOGO:" + h
    return h or None


def _value_hint(cls):
    return {
        "syllabogram-AB": "inherited Linear-B phonetic value (known)",
        "syllabogram-Aonly": "undeciphered (GORILA *-series); no established value",
        "logogram": "commodity ideogram (semantic, not phonetic)",
        "numeral": "Aegean numeral / quantity",
        "fraction": "Aegean fractional weight / measure",
        "separator": "word / phrase separator",
        "uncertain": "unclassified -- needs epigrapher review",
    }.get(cls)


# ---------------------------------------------------------------------------
# stream builders for the three inventories
# ---------------------------------------------------------------------------
SYLL_CLASSES = {"syllabogram-AB", "syllabogram-Aonly"}


def _syll_components(rec):
    """For a syllabogram-class token, return the list of canonical syllabogram ids
    it contributes to the stream. Ligatures are decomposed; non-syllabogram
    components ([?], a stray logogram) are skipped. Simple tokens -> [canonical]."""
    if rec["functional_class"] not in SYLL_CLASSES:
        return []
    out = []
    for comp in rec["components"] or [rec["canonical_sign_id"]]:
        ccls = _classify_head(comp)
        if ccls in SYLL_CLASSES:
            out.append(_ascii(comp))
    return out


def _aonly_confidence(docs):
    """For every A-only canonical id, decide if it is a CLEARLY-attested syllabogram.

    A *-series sign is 'confident' (clearly a recurring phonetic sign, not a stray
    logogram / transcription artifact) iff it appears as a BARE token at least once
    AND has total frequency >= 2. Signs that appear ONLY inside ligatures, or only
    once (hapax), are 'tentative' -> excluded from the conservative stream, kept in
    the exploratory one. AB signs are always confident (their Linear-B values are
    known). This is the 'clearly-A-only syllabograms' qualifier from the redteam."""
    bare = Counter()
    total = Counter()
    for d in docs:
        for tok in d.get("signs", []):
            rec = classify_token(tok)
            if rec["functional_class"] != "syllabogram-Aonly":
                continue
            cid = rec["canonical_sign_id"]
            total[cid] += 1
            # bare = a simple non-ligature token (appears on its own, not as a cluster)
            if not rec["components"] or len(rec["components"]) <= 1:
                bare[cid] += 1
    confident, tentative = set(), set()
    for cid, tot in total.items():
        if bare[cid] >= 1 and tot >= 2:
            confident.add(cid)
        else:
            tentative.add(cid)
    return confident, tentative


def build_streams(docs):
    """Return (raw, conservative, exploratory) as dicts with keys
    inventory (sorted list), V, stream (list of ids in corpus order), N.

      raw          : every syllabogram-class token (AB + ALL A-only), ligatures as
                     single symbols -- reproduces the un-curated syllabogram mass.
      conservative : PRIMARY. AB (all) + CLEARLY-A-only syllabograms only (bare AND
                     recurrent); ligatures decomposed to components; letter-suffix
                     *-allographs merged to base. Targets ~90.
      exploratory  : conservative + PROBABILISTIC allograph merges (subscripted AB
                     signs collapsed into their graphic base family: RA2->RA, PA3->PA,
                     TA2->TA, PU2->PU). An aggressive-merge lower bound. The opposite
                     sensitivity direction (loose: include hapax A-only signs, no merges)
                     is the raw inventory below.
    """
    confident, tentative = _aonly_confidence(docs)

    raw_stream, cons_stream, expl_stream = [], [], []
    raw_seq, cons_seq, expl_seq = [], [], []   # per-inscription sequences (bigram boundaries)
    for d in docs:
        r_row, c_row, e_row = [], [], []
        for tok in d.get("signs", []):
            rec = classify_token(tok)
            if rec["functional_class"] not in SYLL_CLASSES:
                continue
            # raw = literal canonical id, ligature stays one symbol
            r_row.append(rec["canonical_sign_id"])
            # conservative / exploratory = decomposed ligatures into components
            comps = _syll_components(rec)
            for sid in comps:
                base = _ascii(sid)
                cons_id = _conservative_id(base)
                expl_id = _exploratory_id(base)
                # AB signs always in conservative; A-only only if confident.
                keep = (_classify_head(base) == "syllabogram-AB"
                        or base in confident or cons_id in confident)
                if keep:
                    c_row.append(cons_id)
                    # exploratory = conservative confident set + aggressive merges
                    e_row.append(expl_id)
        raw_stream.extend(r_row); cons_stream.extend(c_row); expl_stream.extend(e_row)
        if r_row:
            raw_seq.append(r_row)
        if c_row:
            cons_seq.append(c_row)
        if e_row:
            expl_seq.append(e_row)

    def bundle(stream, sequences, label):
        inv = sorted(set(stream))
        return {
            "label": label,
            "V": len(inv),
            "N": len(stream),
            "inventory": inv,
            "stream": stream,
            "sequences": sequences,
        }

    return (bundle(raw_stream, raw_seq, "raw"),
            bundle(cons_stream, cons_seq, "conservative"),
            bundle(expl_stream, expl_seq, "exploratory"))


def _conservative_id(sid):
    """Expert-style merges ONLY (GORILA-attested):
       letter-suffix allographs of a *-number collapse to the base sign
       (*131B/*131C -> *131, *309B/*309C -> *309). Subscripted AB signs (RA2, PA3,
       TA2, PU2) are kept DISTINCT (they carry distinct Linear-B values)."""
    m = re.match(r"\*(\d+)([A-Z]?)$", sid)
    if m and m.group(2):
        return "*" + m.group(1)
    return sid


def _exploratory_id(sid):
    """+ probabilistic / aggressive allograph merges (a sensitivity bound, NOT used
       as the primary inventory): also collapse subscripted AB signs into their
       graphic base family (RA2->RA, PA3->PA, TA2->TA, PU2->PU)."""
    sid = _conservative_id(sid)
    m = re.match(r"([A-Z]+?)(\d+)$", sid)
    if m:
        return m.group(1)
    return sid


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def _read_corpus(path):
    with open(path) as f:
        data = json.load(f)
    docs = data if isinstance(data, list) else data.get("inscriptions", [])
    return [d for d in docs if d.get("signs")]


def main():
    ap = argparse.ArgumentParser(description="Layered Linear A sign ontology")
    ap.add_argument("--corpus", default=SILVER)
    ap.add_argument("--out", default=OUT_DIR)
    args = ap.parse_args()

    docs = _read_corpus(args.corpus)
    # corpus-order record list (with repeats -> Counter below for freq)
    flat = [t for d in docs for t in d.get("signs", [])]
    freq = Counter(flat)

    # classify every distinct token
    ontology = OrderedDict()
    per_token = {}
    for tok in sorted(freq):
        rec = classify_token(tok)
        per_token[tok] = rec

    # build canonical -> metadata (aggregate freq + examples across allographs)
    canon_meta = OrderedDict()
    # iterate in stable canonical order
    for tok in sorted(freq):
        rec = per_token[tok]
        cid = rec["canonical_sign_id"]
        if cid is None:
            continue
        m = canon_meta.get(cid)
        if m is None:
            m = {
                "class": rec["functional_class"],
                "allograph_family": rec["allograph_family"],
                "frequency": 0,
                "diplomatic_tokens": [],
                "examples": [],
                "value_hypothesis": rec["value_hypothesis"],
            }
            canon_meta[cid] = m
        m["frequency"] += freq[tok]
        m["diplomatic_tokens"].append(rec["diplomatic_token"])
        # collect a couple of example inscription ids
        if len(m["examples"]) < 3:
            for d in docs:
                if tok in d.get("signs", []):
                    if d.get("id") not in m["examples"]:
                        m["examples"].append(d.get("id"))
                    break

    # write the full ontology
    ont_path = os.path.join(args.out, "signs_ontology.json")
    with open(ont_path, "w") as f:
        json.dump(canon_meta, f, ensure_ascii=False, indent=2)

    # three syllabogram inventories
    raw, cons, expl = build_streams(docs)
    for bundle, name in [(raw, "inventory_syllabograms_raw.json"),
                         (cons, "inventory_syllabograms_conservative.json"),
                         (expl, "inventory_syllabograms_exploratory.json")]:
        # strip the long `stream`/`sequences` lists from the human inventory file
        inv_obj = {k: v for k, v in bundle.items()
                   if k not in ("stream", "sequences")}
        with open(os.path.join(args.out, name), "w") as f:
            json.dump(inv_obj, f, ensure_ascii=False, indent=2)
        # sidecar: flat stream + per-inscription sequences (bigram boundaries) for floor_cleaned
        sc = os.path.join(args.out, name.replace(".json", ".stream.json"))
        with open(sc, "w") as f:
            json.dump({"label": bundle["label"],
                       "stream": bundle["stream"],
                       "sequences": bundle["sequences"]}, f)

    # ---- report ----
    class_counts = Counter(m["class"] for m in canon_meta.values())
    print("=" * 70)
    print("LINEAR A SIGN ONTOLOGY  (build_ontology.py)")
    print("=" * 70)
    print(f"inscriptions             : {len(docs)}")
    print(f"raw tokens (N_raw)       : {len(flat)}")
    print(f"distinct raw tokens      : {len(freq)}")
    print(f"canonical sign ids       : {len(canon_meta)}")
    print()
    print("functional_class         : distinct canonical ids")
    for cls in ["syllabogram-AB", "syllabogram-Aonly", "logogram",
                "numeral", "fraction", "separator", "uncertain"]:
        print(f"  {cls:22s} : {class_counts.get(cls, 0)}")
    print()
    print("syllabogram inventories (V = distinct; N = stream length):")
    print(f"  raw          : V={raw['V']:4d}  N={raw['N']:5d}   (ligatures as single tokens)")
    print(f"  conservative : V={cons['V']:4d}  N={cons['N']:5d}   (PRIMARY; expert merges, ligatures decomposed)")
    print(f"  exploratory  : V={expl['V']:4d}  N={expl['N']:5d}   (+ subscript allograph collapse)")
    print()
    print("AB-vs-A-only convention (GORILA/SigLA/lineara.xyz):")
    print("  AB-series      = bare CV/V syllabic tokens with known Linear-B values")
    print("                   (incl. subscripted allographs RA2/PA3/TA2/PU2 = distinct signs).")
    print("  A-only         = '*' + GORILA catalogue number (*301, *34 ...); value unknown.")
    print("  *-F/*-M suffix = sexed ideogram -> LOGOGRAM;  *-800..929 = fraction series.")
    print("=" * 70)
    print(f"wrote: {ont_path}")
    print(f"wrote: {args.out}/inventory_syllabograms_{{raw,conservative,exploratory}}.json (+.stream.json)")
    return raw, cons, expl


if __name__ == "__main__":
    main()
