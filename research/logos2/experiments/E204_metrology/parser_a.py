"""E204 Parser A — line-regex strategy over the .txt renderings (PARSER_A_SPEC.md).
Shares ONLY SCHEMA.json and the raw files with Parser B. Emits parser_a_output.csv."""
import csv
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
Y = "/home/claude-runner/gitlab/n8n/logos/corpus/bronze/younger_lineara/"
SCHEMA = json.load(open(os.path.join(HERE, "SCHEMA.json")))
FRAC = set(SCHEMA["fraction_alphabet"])
SITES = SCHEMA["site_prefix"]

PREFIX = "|".join(sorted(SITES, key=len, reverse=True))
DOC_RE = re.compile(rf"^\s?({PREFIX})\s?([0-9]+[a-z]?)\s*(?:,|\()"
                    rf".{{0,120}}?(tablet|nodule|roundel|sealing|vessel|bar|lame|GORILA|"
                    rf"Za|Wc|Wa|Wb|Zb|Zc|Zd|Ze|Zf|Zg)", re.I)
LOCUS_RE = re.compile(r"^\s?((?:side|edge|lat)\.|[ab]?(?:\.|\s)?(?:[0-9]+(?:-[0-9]+)?))\s+")
PROSE_MARKERS = re.compile(r"\b(according|perhaps|sometimes|found|distribute|gave|record[s]?|"
                           r"note|cf\.|see|comments|update|bibliography)\b|=", re.I)
DECIMAL_GLOSS = re.compile(r"\d+\.\d+")
INT_RE = re.compile(r"^[0-9]{1,4}$")
WORDTOK_RE = re.compile(r"^[A-Z*][A-Z0-9*+₀-₉²³]*$")


def frac_token(t):
    return t and all(c in FRAC for c in t) and len(t) <= 2


def parse_file(fname):
    src = os.path.basename(fname).split(".")[0]
    out = []
    doc_id, site, support = None, None, None
    lines = open(fname, encoding="utf-8", errors="replace").read().split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].replace("•", " • ")
        m = DOC_RE.match(line)
        if m:
            doc_id = f"{m.group(1)} {m.group(2)}"
            site = SITES.get(m.group(1), "?")
            support = m.group(3).lower()
            i += 1
            continue
        if doc_id is None:
            i += 1
            continue
        if DECIMAL_GLOSS.search(line) or PROSE_MARKERS.search(line):
            i += 1
            continue
        lm = LOCUS_RE.match(line)
        if not lm:
            i += 1
            continue
        locus = lm.group(1).strip()
        rest = line[lm.end():]
        uncertain = 1 if "?" in rest else 0
        restored = 1 if ("[" in rest or "]" in rest) else 0
        damaged = 1 if ("⟦" in rest or "vest." in rest or "…" in rest) else 0
        # tokenize; join hyphen-split sign groups (Younger writes "PA - DE" and "PA-DE")
        toks = [t for t in re.split(r"[\s•]+", rest) if t and t not in ("•",)]
        joined = []
        for t in toks:
            if t == "-" and joined:
                joined[-1] += "-"
            elif joined and joined[-1].endswith("-"):
                joined[-1] += t
            else:
                joined.append(t)
        toks = [t.strip("-") for t in joined if t.strip("-")]
        # continuation lines: subsequent lines of ONLY fraction letters
        j = i + 1
        extra = []
        while j < len(lines):
            nxt = [t for t in re.split(r"\s+", lines[j].strip()) if t]
            if nxt and all(frac_token(t) for t in nxt):
                extra += nxt
                j += 1
            else:
                break
        # number zone: maximal suffix of ints/fraction tokens
        clean = [re.sub(r"[\[\]{}?<>]", "", t) for t in toks]
        clean = [t for t in clean if t]
        nz = []
        k = len(clean)
        while k > 0 and (INT_RE.match(clean[k - 1]) or frac_token(clean[k - 1])):
            nz.insert(0, clean[k - 1])
            k -= 1
        nz += extra
        if not nz:
            i = j
            continue
        integer = "".join(t for t in nz if INT_RE.match(t))
        frac_seq = "".join(t for t in nz if frac_token(t))
        pre = clean[:k]
        logogram = " ".join(t for t in pre if "+" in t or t.startswith("*") or
                            t.startswith("{"))
        words = [t for t in pre if t not in logogram.split() and WORDTOK_RE.match(t)]
        context = words[-1] if words else ""
        is_kuro = 1 if any("KU-RO" in t for t in pre) else 0
        out.append(dict(source_file=src, doc_id=doc_id, site=site, support=support,
                        locus=locus, seq=len(out), context_word=context,
                        logogram=logogram, integer=integer, fraction_seq=frac_seq,
                        uncertain=uncertain, restored=restored, damaged=damaged,
                        is_kuro=is_kuro, parser="A"))
        i = j
    return out


def main():
    rows = []
    for f in ("HTtexts.txt", "misctexts.txt", "religioustexts.txt"):
        rows += parse_file(Y + f)
    with open(os.path.join(HERE, "parser_a_output.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SCHEMA["fields"])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    n_frac = sum(1 for r in rows if r["fraction_seq"])
    docs = {r["doc_id"] for r in rows}
    print(f"parser A: {len(rows)} records, {n_frac} with fractions, {len(docs)} docs")


if __name__ == "__main__":
    main()
