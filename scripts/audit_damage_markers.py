#!/usr/bin/env python3
"""audit_damage_markers.py — Tsirkas D1 on the logos lineage: word-attached damage
(break/lacuna marker U+1076B) is present in the bronze Unicode `words` layer but stripped
from the `transliteratedWords` layer that corpus_io*.py ingest — so silver carries no
damage information and "phantom types" (word types attested ONLY damaged, never complete)
are indistinguishable from real complete types.

This script mirrors scripts/audit_ab21_ab22.py's role for D4: a mechanical, re-runnable
audit that (a) verifies the stripping mechanism on the bronze in-repo copy, (b) emits a
per-word-token damage sidecar annex for silver (corpus/silver/damage_annex.json,
gitignored like all silver: derived from licensed GORILA/lineara.xyz data), and (c) prints
a script-generated summary (invariant #12: counts are generated, never hand-written).

SILVER IS NOT REBUILT (standing rule: no silver rebuild without an explicit decision).
The annex is a sidecar keyed by doc id; token order = silver stream word order.

Alignment: the bronze `words` (Unicode) and `transliteratedWords` layers correspond 1:1
positionally (1,719/1,720 entries; the one misaligned entry is skipped and reported).
A word token's damage = U+1076B occurrences in its aligned Unicode token: leading
(break before, ]WORD), trailing (break after, WORD[), internal.

Constitution: Art. XI (defect on the source lineage), Art. XVII (append-only: annex
supplements, published silver untouched), Art. XXII (this header). Record:
docs/2026-08-05-tsirkas-full-repo-audit.md §2 + docs/2026-08-05-d1-damage-annex.md.
Credit: Tsirkas D1 (github.com/ChristosTsirkas/corpus-validation-for-undeciphered-scripts-linear-a).

    python3 scripts/audit_damage_markers.py [--bronze PATH] [--out PATH] [--summary-only]
"""
import argparse
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.corpus_io_structured import BRONZE, classify  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SILVER_STRUCTURED = os.path.join(ROOT, "corpus", "silver", "inscriptions_structured.json")
ANNEX = os.path.join(ROOT, "corpus", "silver", "damage_annex.json")
MARKER = "\U0001076b"  # unassigned codepoint in the Linear A block, used by the
                       # Douros/lineara.xyz encoding as the break/lacuna marker (Tsirkas D1)

VERSION = "damage-annex-v1"


def damage_flags(unicode_token):
    """(leading, trailing, internal) marker presence for one Unicode word token."""
    core = unicode_token.strip(MARKER)
    return (
        unicode_token.startswith(MARKER),
        unicode_token.endswith(MARKER),
        MARKER in core,
    )


def code(flags):
    """Compact damage code: subset of 'LTI' ('' = clean)."""
    lead, trail, internal = flags
    return ("L" if lead else "") + ("T" if trail else "") + ("I" if internal else "")


def build_annex(bronze_path):
    data = json.load(open(bronze_path))
    per_doc = {}
    misaligned = []
    for entry in data:
        if not (isinstance(entry, list) and len(entry) >= 2 and isinstance(entry[1], dict)):
            continue
        iid, d = entry[0], entry[1]
        translit = [t for t in (d.get("transliteratedWords") or []) if isinstance(t, str)]
        unicode_words = [t for t in (d.get("words") or []) if isinstance(t, str)]
        stream = [classify(t) for t in translit]
        word_idx = [i for i, s in enumerate(stream) if s["t"] == "word"]
        if not word_idx:
            continue  # not a silver doc (corpus_io_structured inclusion rule)
        if len(translit) != len(unicode_words):
            misaligned.append(iid)
            continue
        codes = [code(damage_flags(unicode_words[i])) for i in word_idx]
        types = ["-".join(stream[i]["signs"]) for i in word_idx]
        per_doc[iid] = {"w": codes, "types": types}
    return per_doc, misaligned


def summarize(per_doc):
    n_tokens = sum(len(d["w"]) for d in per_doc.values())
    by_flag = {"L": 0, "T": 0, "I": 0}
    combo = {}
    damaged = 0
    type_clean = set()
    type_damaged = set()
    for d in per_doc.values():
        for c, ty in zip(d["w"], d["types"]):
            if c:
                damaged += 1
                combo[c] = combo.get(c, 0) + 1
                for f in c:
                    by_flag[f] += 1
                type_damaged.add(ty)
            else:
                type_clean.add(ty)
    all_types = type_clean | type_damaged
    phantom = type_damaged - type_clean
    return {
        "docs": len(per_doc),
        "word_tokens": n_tokens,
        "damage_touching_tokens": damaged,
        "damage_touching_pct": round(100.0 * damaged / n_tokens, 1) if n_tokens else 0.0,
        "by_flag": by_flag,
        "by_combo": dict(sorted(combo.items())),
        "distinct_types": len(all_types),
        "ever_damaged_types": len(type_damaged),
        "phantom_types": len(phantom),
        "phantom_pct": round(100.0 * len(phantom) / len(all_types), 1) if all_types else 0.0,
        "types_excluding_phantoms": len(all_types) - len(phantom),
    }


def cross_check_silver(per_doc):
    """The annex doc-id set must equal the silver structured doc-id set (if silver present)."""
    if not os.path.exists(SILVER_STRUCTURED):
        return {"checked": False, "note": "silver structured not present"}
    silver_ids = {r["id"] for r in json.load(open(SILVER_STRUCTURED))}
    annex_ids = set(per_doc)
    return {
        "checked": True,
        "silver_docs": len(silver_ids),
        "annex_docs": len(annex_ids),
        "only_in_silver": sorted(silver_ids - annex_ids),
        "only_in_annex": sorted(annex_ids - silver_ids),
        "match": silver_ids == annex_ids,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--bronze", default=BRONZE)
    ap.add_argument("--out", default=ANNEX)
    ap.add_argument("--summary-only", action="store_true",
                    help="print the summary without writing the annex")
    args = ap.parse_args(argv)

    if not os.path.exists(args.bronze):
        sys.exit(f"bronze corpus not found at {args.bronze}")
    bronze_sha = hashlib.sha256(open(args.bronze, "rb").read()).hexdigest()

    per_doc, misaligned = build_annex(args.bronze)
    summary = summarize(per_doc)
    check = cross_check_silver(per_doc)

    annex = {
        "version": VERSION,
        "marker": "U+1076B",
        "bronze_sha256": bronze_sha,
        "misaligned_skipped": misaligned,
        "summary": summary,
        "silver_cross_check": {k: v for k, v in check.items() if k != "only_in_silver" or v},
        "docs": per_doc,
    }
    if not args.summary_only:
        json.dump(annex, open(args.out, "w"), ensure_ascii=False, indent=1, sort_keys=True)

    s = summary
    print(f"D1 damage annex ({VERSION}) — bronze sha256 {bronze_sha[:16]}")
    print(f"docs: {s['docs']} (misaligned skipped: {len(misaligned)}: {misaligned})")
    print(f"word tokens: {s['word_tokens']}; damage-touching: {s['damage_touching_tokens']}"
          f" ({s['damage_touching_pct']}%)  flags L/T/I: {s['by_flag']}  combos: {s['by_combo']}")
    print(f"types: {s['distinct_types']}; ever-damaged: {s['ever_damaged_types']}; "
          f"PHANTOM (only-damaged): {s['phantom_types']} ({s['phantom_pct']}%)"
          f" -> {s['types_excluding_phantoms']} excluding phantoms")
    print(f"silver cross-check: {'MATCH' if check.get('match') else check}")
    if not args.summary_only:
        print(f"annex -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
