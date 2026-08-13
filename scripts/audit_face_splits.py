#!/usr/bin/env python3
"""audit_face_splits.py — two further lineara.xyz lineage defects, mechanically checked.

Found 2026-08-13 while auditing an external Linear A decipherment preprint against our
own corpus. Both are defects in OUR bronze/silver, independent of that preprint.

D5 — FACE-SPLIT WORD TOKENS.  Where a sign-group runs across two faces (or two ruled
lines) of a stone vessel, the lineage emits it as TWO word tokens in
`transliteratedWords`. Younger's edition marks the continuation with trailing/leading
hyphens and, at IO Za 12, says so in as many words ("the two sides break up the word").
Effect: spurious word types, undercounted tokens for the split lexeme. Every confirmed
case is a libation-formula document, i.e. exactly the subcorpus every structural study
of Linear A leans on.

D6 — A319 LABELLED *904.  The transliteration layer prints `*904` for a sign whose
glyph in `parsedInscription` is U+1066B LINEAR A SIGN A319. `corpus/silver/
signs_ontology.json` inherits the wrong label and classes it `fraction` /
"Aegean fractional weight / measure". A319 is a GORILA *-series sign; the genuine
fraction signs (A701 A, A704 E, A705 F, A707 J, A708 K) occur alongside it in the very
same document (HT Zd 157+156).

Read-only. Prints a report; writes nothing.

    python3 scripts/audit_face_splits.py
"""
import json
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BRONZE_REPO = os.path.join(ROOT, "corpus", "bronze", "lineara", "inscriptions.json")
BRONZE = os.environ.get("LOGOS_BRONZE") or _BRONZE_REPO
YOUNGER = os.path.join(ROOT, "corpus", "bronze", "younger_lineara", "misctexts.txt")
ONTOLOGY = os.path.join(ROOT, "corpus", "silver", "signs_ontology.json")

A319 = "\U0001066B"
DAMAGE = "\U0001076B"

# Confirmed face-split cases: doc id -> (Younger's word, the two lineage tokens).
# Witnesses are the trailing/leading hyphens in corpus/bronze/younger_lineara/misctexts.txt.
FACE_SPLITS = {
    "IOZa12": ("JA-SA-SA-RA-ME", ("JA-SA", "SA-RA-ME")),
    "IOZa16": ("JA-SA-SA-RA-ME", ("JA-SA-SA-RA", "ME")),
    "KNZa10": ("JA-SA-SA-RA-MA-NA", ("JA-SA-SA-RA-MA", "NA")),
    "PKZa16": ("PU₂-RE", ("PU₂", "RE-JA")),
}


def load_bronze():
    with open(BRONZE, encoding="utf-8") as fh:
        return {k: v for k, v in json.load(fh)}


def words(entry):
    return [w for w in (entry.get("transliteratedWords") or [])
            if w and re.search(r"[A-Za-z0-9*]", w)]


def scan_younger():
    """Continuation markers: a line ending in '-' whose next non-empty line starts '-'."""
    if not os.path.exists(YOUNGER):
        return None
    lines = [l.rstrip() for l in open(YOUNGER, encoding="utf-8", errors="replace")]
    hits = []
    for i, line in enumerate(lines):
        s = line.strip()
        if not s or not s.endswith("-") or set(s) <= {"-", " "}:
            continue
        for j in range(i + 1, min(i + 4, len(lines))):
            t = lines[j].strip()
            if not t:
                continue
            if re.match(r"^(\.[a-z]:\s*)?-", t) and not set(t) <= {"-", " "}:
                hits.append((i + 1, s[-42:], t[:42]))
            break
    return hits


def main():
    D = load_bronze()
    print(f"bronze: {len(D)} documents  ({BRONZE})")

    print("\n=== D5 — face-split word tokens ===")
    confirmed = 0
    spurious_types = set()
    for doc, (true_word, parts) in sorted(FACE_SPLITS.items()):
        entry = D.get(doc)
        if entry is None:
            print(f"  {doc:8s} NOT IN CORPUS")
            continue
        ws = words(entry)
        present = all(p in ws for p in parts)
        joined = true_word in ws
        status = "SPLIT (confirmed)" if present and not joined else \
                 "joined — defect absent" if joined else "unverified"
        if present and not joined:
            confirmed += 1
            spurious_types.update(parts)
        print(f"  {doc:8s} Younger: {true_word:20s} lineage: {' + '.join(parts):28s} {status}")
    print(f"  confirmed split documents: {confirmed}/{len(FACE_SPLITS)}"
          f"   spurious word types introduced: {len(spurious_types)}")

    hits = scan_younger()
    if hits is None:
        print("  (Younger misctexts.txt absent — continuation scan skipped)")
    else:
        print(f"  Younger continuation markers found by scan: {len(hits)}")
        for ln, a, b in hits:
            print(f"    L{ln:<6d} ...{a}  ->  {b}")

    print("\n=== D6 — A319 mislabelled *904 ===")
    label_docs, glyph_docs, both = set(), set(), set()
    for k, v in D.items():
        if any("*904" in (w or "") for w in (v.get("transliteratedWords") or [])):
            label_docs.add(k)
        if A319 in (v.get("parsedInscription") or ""):
            glyph_docs.add(k)
    both = label_docs & glyph_docs
    print(f"  docs whose transliteration prints '*904': {len(label_docs)} {sorted(label_docs)}")
    print(f"  docs whose sign layer contains U+1066B A319: {len(glyph_docs)} {sorted(glyph_docs)}")
    print(f"  overlap: {len(both)}  -> label '*904' and glyph A319 co-occur in "
          f"{len(both)}/{len(label_docs) or 1} label-bearing docs")
    if os.path.exists(ONTOLOGY):
        onto = json.load(open(ONTOLOGY, encoding="utf-8"))
        e904, e319 = onto.get("*904"), onto.get("*319")
        print(f"  signs_ontology['*904'] = {e904}")
        print(f"  signs_ontology['*319'] = {e319}")
    # context: A319 sits in counted quantity slots
    print("  context (A319 immediately followed by a numeral):")
    for k in sorted(glyph_docs):
        ws = words(D[k])
        for i, w in enumerate(ws):
            if "*904" in w:
                nxt = ws[i + 1] if i + 1 < len(ws) else "-"
                print(f"    {k:14s} ...{w} -> next token {nxt!r}")
    # the genuine fraction signs in the same document
    for k in sorted(glyph_docs):
        s = D[k].get("parsedInscription") or ""
        fr = sorted({unicodedata.name(c) for c in s
                     if 0x10740 <= ord(c) <= 0x1075F and unicodedata.name(c, None)})
        if fr:
            print(f"    {k:14s} genuine fraction signs present: {', '.join(fr)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
