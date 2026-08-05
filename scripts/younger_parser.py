#!/usr/bin/env python3
"""younger_parser.py — SCOPED parser for Younger's Linear A text pages (bronze .txt).

Machine-parses corpus/bronze/younger_lineara/{HTtexts,misctexts,religioustexts}.txt —
the de-tagged tables that scripts/audit_ab21_ab22.py previously consulted only by eye —
just far enough to serve as a divergence-register witness (scripts/divergence_register.py).
This is NOT an edition: it extracts doc-header designations plus the
`side.line statement logogram number fraction` table rows, and from each row ONLY the
side.line, word labels, logograms and integer numbers. Fractions (Younger's single
capital letters J/E/F/K/L2/L3/...), klasmatograms, seal commentary, findspot prose and
restoration discussion are out of scope and dropped.

Hazards handled (all mechanical):
  - spaced subscripts: `KU-PA 3 -NU` -> KU-PA3-NU (digit 2/3 between a word chunk and a
    '-'-leading continuation chunk is a subscript, not a count);
  - hyphen-wrapped words: `RO -SI-RA`, `PA-TA- ] NE`, `A-RA-JU-U-DE- ZA` re-join;
  - spaced numerals: `9 7` -> 97 (adjacent digit chunks are one numeral split by layout);
  - spaced gender suffixes: `OVIS f` -> OVISf (lowercase m/f/x attaches to a logogram);
  - spaced ligatures: `OVIS +SI`, `CAPm + KU` -> OVIS+SI, CAPm+KU;
  - `[ ... ]` restoration spans (bare-bracket chunks) flag their labels `restored`
    and keep them out of `words`/`logograms`; edge damage brackets (`]RA-RI`, `VIR[`)
    are stripped from the label and do NOT open a span;
  - commentary rows (`a.2-3: ...`) and prose/citation lines never join a row.

Known, accepted limitations (documented, out of register scope): word-FINAL spaced
subscripts (`PA 3` at end of statement) are indistinguishable from a count and read as
word PA + number 3; single-sign words not followed by a hyphen chunk are dropped with
the fraction letters; roundel tables without a `side.line` header (e.g. KN Wc 29) yield
doc headers but no rows.

LICENSING: the .txt pages are Younger's copyrighted edition (bronze, gitignored); this
parser CODE is public, its bulk output is never committed — only defect-level excerpts
flow into corpus/divergences.json (fair-dealing basis of the 2026-08-05 audit docs).

    python3 scripts/younger_parser.py [--dir corpus/bronze/younger_lineara] [--doc "HT 122"]
"""
import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YOUNGER_DIR = os.path.join(ROOT, "corpus", "bronze", "younger_lineara")
FILES = ("HTtexts.txt", "misctexts.txt", "religioustexts.txt")

VERSION = "younger-parser-v1"

# Doc header: ` HT 122 , page tablet (HM 1366) ...` / ` SY Za 2 (HM 3429) ...`
_HEADER = re.compile(
    r"^\s{0,4}([A-Z]{2,4})\s*(\(\?\))?\s+((?:W[a-z]|Z[a-z])\s+)?(\d+[a-z]?(?:\+\d+)?)\s*[,(]")
# Table opener: a column-header line beginning `side.line ...`
_TABLE = re.compile(r"^\s*side\.line\b", re.IGNORECASE)
# side.line forms: a.1  a.2-3  a.  .1  .1-2  .6-7  b   (bare letter needs a token-ish rest)
_SIDELINE = re.compile(r"(?:[a-e]\.(?:\d+[a-z]?(?:-\d+[a-z]?)?)?|\.(?:\d+[a-z]?(?:-\d+[a-z]?)?)|[a-e])")

_NUM = re.compile(r"^\d+$")
_FRACTION = re.compile(r"^[A-Z]\d?$")     # J E F K L2 L3 ... (Younger fraction letters)
_PUNCT = {"•", "\U000100c1", "·", ",", ";"}
GENDER = ("m", "f", "x")
# Commodity/livestock logogram stems used by Younger's tables (scoped set).
LOGO_STEMS = {"GRA", "VIN", "VINa", "OLE", "OLIV", "FIC", "VIR", "OVIS", "CAP", "BOS",
              "SUS", "AES", "CYP", "TELA", "QIF", "ME"}
# Citation tokens that must never join a row as a continuation line.
_BAN = {"CMS", "GORILA", "HM", "AM", "JGY", "II", "III", "IV"}


def _chunk_tokenish(c):
    """True if a whitespace chunk could belong to a transcription row (not prose).

    Lowercase is prose EXCEPT: bare gender letters (m/f/x), a small epigraphic set
    (vacat, vest., mutila, ...), and single trailing lowercase letters inside
    otherwise-uppercase labels (OVISf, CAPm+KU, VINa)."""
    if c.startswith("{") or c.endswith("}"):
        return True                     # `{*535: 54+81}` standardized-number spans
    c = c.replace("(?)", "")
    if ":" in c or "(" in c or ")" in c or c in _BAN:
        return False
    if c in GENDER or c in ("vacat", "vest.", "vest", "supra", "infra", "mutila", "deest"):
        return True
    core = c.strip("[]")
    return not core or bool(re.fullmatch(r"(?:[^a-z]+[mfxab]?)+", core))


def _tokenish(line):
    chunks = line.split()
    return bool(chunks) and all(_chunk_tokenish(c) for c in chunks)


def _stem(core):
    return core[:-1] if len(core) > 2 and core[-1] in GENDER else core


def _classify(core):
    """'word' or 'logo' for one cleaned label chunk (scoped convention)."""
    if "-" in core:
        return "word"
    if core.startswith("*") or "+" in core or _stem(core) in LOGO_STEMS:
        return "logo"
    return "word"


def extract_row(chunks):
    """Fold one row's whitespace chunks into (labels, numbers).

    labels: list of [kind, text, restored]; numbers: list of int."""
    labels, numbers = [], []
    in_restoration = False
    in_braces = False
    pending_plus = False
    last_was_digit = False
    for i, c in enumerate(chunks):
        if in_braces or c.startswith("{"):
            in_braces = not c.endswith("}")
            last_was_digit = False
            continue
        if c in _PUNCT:
            last_was_digit = False
            continue
        if set(c) <= {"[", "]"}:                       # bare bracket chunk(s)
            if c == "[":
                in_restoration = True
            elif c == "]":
                in_restoration = False
            last_was_digit = False
            continue
        if _NUM.match(c):
            nxt = chunks[i + 1] if i + 1 < len(chunks) else ""
            if (c in ("2", "3") and labels and labels[-1][0] == "word"
                    and nxt.startswith("-") and re.search(r"[A-Za-z]", nxt)):
                labels[-1][1] += c                     # spaced subscript: KU-PA 3 -NU
            elif last_was_digit:
                numbers[-1] = int(str(numbers[-1]) + c)  # spaced numeral: 9 7 -> 97
                last_was_digit = True
            else:
                numbers.append(int(c))
                last_was_digit = True
            continue
        last_was_digit = False
        if c == "+":
            pending_plus = True
            continue
        core = c.strip("[]{}()")
        if not core:
            continue
        if _NUM.match(core):
            numbers.append(int(core))                  # bracket-attached digit: `2[`
            continue
        if pending_plus:
            pending_plus = False
            if labels:
                labels[-1][1] += "+" + core            # CAPm + KU -> CAPm+KU
                continue
        if core.startswith("+") and labels:
            labels[-1][1] += core                      # OVIS +SI -> OVIS+SI
            continue
        if core.startswith("-"):
            if labels and labels[-1][0] == "word":
                labels[-1][1] += core                  # -NU / -SI-RA continuation
            else:
                labels.append(["word", core.lstrip("-"), in_restoration])
            continue
        if core in GENDER:
            if labels and labels[-1][0] == "logo":
                labels[-1][1] += core                  # OVIS f -> OVISf
            continue
        if re.search(r"[a-z]", core) and not re.fullmatch(r"(?:[^a-z]+[mfxab]?)+", core):
            continue    # prose leak (vacat, vest., ...); keeps OVISf / CAPm+KU / VINa
        if labels and labels[-1][0] == "word" and labels[-1][1].endswith("-"):
            labels[-1][1] += core                      # PA-TA- ] NE -> PA-TA-NE
            continue
        if _FRACTION.match(core):
            if i + 1 < len(chunks) and chunks[i + 1].startswith("-"):
                labels.append(["word", core, in_restoration])  # I -KU-PA... word start
            continue                                   # else a fraction letter: dropped
        labels.append([_classify(core), core, in_restoration])
    labels = [l for l in labels if l[1].strip("-")]
    for l in labels:
        l[1] = l[1].rstrip("-")
    return labels, numbers


def _row(sideline, chunks):
    labels, numbers = extract_row(chunks)
    return {
        "line": sideline,
        "words": [t for k, t, r in labels if k == "word" and not r],
        "logograms": [t for k, t, r in labels if k == "logo" and not r],
        "restored": [t for k, t, r in labels if r],
        "numbers": numbers,
    }


def parse_file(path):
    """-> list of {'designation', 'line_no', 'rows': [row, ...]} in file order."""
    docs = []
    doc = None
    in_table = False
    open_row = None            # (sideline, chunks)

    def close_row():
        nonlocal open_row
        if open_row is not None and doc is not None:
            doc["rows"].append(_row(*open_row))
        open_row = None

    for line_no, line in enumerate(open(path, encoding="utf-8"), 1):
        line = line.rstrip("\n")
        m = _HEADER.match(line)
        if m:
            close_row()
            site, q, cls, num = m.group(1), m.group(2) or "", m.group(3), m.group(4)
            des = site + q + " " + ((cls.strip() + " ") if cls else "") + num
            doc = {"designation": des, "line_no": line_no, "rows": []}
            docs.append(doc)
            in_table = False
            continue
        if _TABLE.match(line):
            close_row()
            in_table = True
            continue
        if doc is None or not in_table:
            continue
        chunks = line.split()
        if not chunks:
            close_row()
            continue
        first = chunks[0]
        if first.endswith(":"):               # commentary row (`a.2-3: ...`)
            close_row()
            continue
        if _SIDELINE.fullmatch(first) and all(_chunk_tokenish(c) for c in chunks[1:]):
            close_row()
            open_row = (first, list(chunks[1:]))
            continue
        if open_row is not None and _tokenish(line):
            open_row[1].extend(chunks)        # wrapped row continuation
            continue
        close_row()
    close_row()
    return docs


def parse_dir(dirpath=YOUNGER_DIR, files=FILES):
    """-> dict designation -> {'sources': ['HTtexts.txt:2783', ...], 'rows': [...]}.

    Deterministic: fixed file order, file order within; duplicate designations merge
    by appending rows (Younger repeats tabulations for alternative restorations)."""
    merged = {}
    for fn in files:
        path = os.path.join(dirpath, fn)
        if not os.path.exists(path):
            continue
        for doc in parse_file(path):
            slot = merged.setdefault(doc["designation"], {"sources": [], "rows": []})
            slot["sources"].append(f"{fn}:{doc['line_no']}")
            slot["rows"].extend(doc["rows"])
    return merged


def dedup_rows(rows):
    """Drop exact repeats (same side.line + identical extracted content), keep order."""
    seen, out = set(), []
    for r in rows:
        key = (r["line"], tuple(r["words"]), tuple(r["logograms"]),
               tuple(r["restored"]), tuple(r["numbers"]))
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dir", default=YOUNGER_DIR)
    ap.add_argument("--doc", help="print the parsed rows of one designation")
    args = ap.parse_args(argv)

    docs = parse_dir(args.dir)
    n_rows = sum(len(d["rows"]) for d in docs.values())
    print(f"younger parse ({VERSION}): {len(docs)} doc headers, {n_rows} rows "
          f"from {', '.join(FILES)}")
    if args.doc:
        d = docs.get(args.doc)
        if not d:
            sys.exit(f"designation {args.doc!r} not found")
        print(f"{args.doc}  (sources: {', '.join(d['sources'])})")
        for r in d["rows"]:
            print(f"  {r['line']:<8} words={r['words']} logos={r['logograms']} "
                  f"restored={r['restored']} nums={r['numbers']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
