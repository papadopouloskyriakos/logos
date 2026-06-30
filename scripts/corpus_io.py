#!/usr/bin/env python3
"""corpus_io.py — normalize the lineara.xyz corpus into logos silver format.

Reads the raw lineara items_analysis/inscriptions.json (bronze, gitignored) and emits
corpus/silver/inscriptions.json: one record per inscription:

    {id, site, context, support, signs:[...]}

where `signs` is the syllable sequence parsed from `transliteratedWords` (hyphen-split;
numerals, line-breaks, and ditto/separator glyphs dropped; subscripts kept on their sign,
e.g. QE-RA₂-U -> ['QE','RA₂','U']).

LICENSING: lineara.xyz carries NO open license and its data derives from the copyrighted
GORILA corpus (Godart & Olivier) + Douros. So both bronze and silver are GITIGNORED here
(invariant 10/12) — only this normalizer CODE is public, never the derived corpus data.

    python3 scripts/corpus_io.py [path/to/inscriptions.json]
"""
import json
import os
import re
import sys

BRONZE = os.environ.get("LOGOS_BRONZE", "/tmp/lineara/items_analysis/inscriptions.json")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SILVER = os.path.join(ROOT, "corpus", "silver", "inscriptions.json")


def is_sign_token(tok):
    """A real transliterated sign-group contains at least one latin letter.
    This drops numerals ('197'), line-breaks, and ditto/separator glyphs (𐄁)."""
    return bool(tok and tok.strip() and re.search(r"[A-Za-z]", tok))


def split_signs(word):
    """QE-RA₂-U -> ['QE','RA₂','U']."""
    return [p for p in word.split("-") if p]


def normalize(raw_path, out_path):
    data = json.load(open(raw_path))
    out = []
    for entry in data:
        if not (isinstance(entry, list) and len(entry) >= 2 and isinstance(entry[1], dict)):
            continue
        iid, d = entry[0], entry[1]
        signs = []
        for w in d.get("transliteratedWords") or []:
            if isinstance(w, str) and is_sign_token(w):
                signs.extend(split_signs(w))
        if not signs:
            continue
        out.append({
            "id": iid,
            "site": d.get("site", ""),
            "context": d.get("context", ""),
            "support": d.get("support", ""),
            "signs": signs,
        })
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    json.dump(out, open(out_path, "w"), ensure_ascii=False, indent=1)
    return out


if __name__ == "__main__":
    raw = sys.argv[1] if len(sys.argv) > 1 else BRONZE
    if not os.path.exists(raw):
        sys.exit(f"bronze corpus not found at {raw} (clone mwenge/lineara.xyz first)")
    docs = normalize(raw, SILVER)
    n = sum(len(d["signs"]) for d in docs)
    uniq = len({s for d in docs for s in d["signs"]})
    print(f"normalized {len(docs)} inscriptions, {n} signs, {uniq} unique -> {SILVER}")
