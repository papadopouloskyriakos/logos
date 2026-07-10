"""E204 Parser B — HTML tag-stripping character FSM (PARSER_B_SPEC.md). Independent of
Parser A: different source rendering (.html), no record-level regexes, own tokenizer, own
prose/decimal detectors. Shares ONLY SCHEMA.json + raw files. Emits parser_b_output.csv."""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
Y = "/home/claude-runner/gitlab/n8n/logos/corpus/bronze/younger_lineara/"
SCHEMA = json.load(open(os.path.join(HERE, "SCHEMA.json")))
FRAC = set(SCHEMA["fraction_alphabet"])
SITES = SCHEMA["site_prefix"]
SUPPORT_WORDS = {"tablet", "nodule", "roundel", "sealing", "vessel", "bar", "lame",
                 "gorila", "za", "wc", "wa", "wb", "zb", "zc", "zd", "ze", "zf", "zg"}
ENT = {"&amp;": "&", "&lt;": "<", "&gt;": ">", "&nbsp;": " ", "&#8226;": "•",
       "&bull;": "•", "&quot;": '"'}


def is_int_tok(t):
    return t.isdigit() and 1 <= len(t) <= 4


def is_frac_tok(t):
    return 0 < len(t) <= 2 and all(ch in FRAC for ch in t)


def is_locus_tok(t):
    """side.line shapes via character walk: optional letter, optional dot, digits,
    optional -digits; or side./edge./lat."""
    if t in ("side.", "edge.", "lat."):
        return True
    s = t
    if s and s[0] in "ab":
        s = s[1:]
    if s.startswith("."):
        s = s[1:]
    if not s:
        return False
    core = s.split("-")[0]
    return core.isdigit()


def lower_run(tokens):
    run, best = 0, 0
    for t in tokens:
        if t.isalpha() and t.islower():
            run += 1; best = max(best, run)
        else:
            run = 0
    return best


def has_decimal_gloss(tokens):
    for t in tokens:
        if "." in t:
            a, _, b = t.partition(".")
            if a.isdigit() and b.isdigit():
                return True
    return False


def iter_rows(raw):
    """Yield (is_row, payload): table rows as lists of cell texts, and inter-row text."""
    i, n = 0, len(raw)
    buf_text = []
    row = None
    cell = None
    while i < n:
        if raw[i] == "<":
            j = raw.find(">", i + 1)
            if j == -1:
                break
            tag = raw[i + 1:j].split()[0].lower() if raw[i + 1:j].split() else ""
            if tag == "tr":
                if buf_text:
                    yield (False, "".join(buf_text)); buf_text = []
                row = []
                cell = None
            elif tag == "/tr":
                if row is not None:
                    if cell is not None:
                        row.append("".join(cell))
                    yield (True, row)
                row, cell = None, None
            elif tag == "td":
                if row is not None:
                    if cell is not None:
                        row.append("".join(cell))
                    cell = []
            elif tag == "/td":
                if row is not None and cell is not None:
                    row.append("".join(cell)); cell = None
            i = j + 1
        elif raw[i] == "&":
            j = raw.find(";", i + 1)
            if 0 < j - i <= 8:
                ch = ENT.get(raw[i:j + 1], " ")
                (cell if cell is not None else buf_text).append(ch)
                i = j + 1
            else:
                (cell if cell is not None else buf_text).append(raw[i]); i += 1
        else:
            (cell if cell is not None else buf_text).append(raw[i]); i += 1
    if buf_text:
        yield (False, "".join(buf_text))


def parse_file(fname):
    src = os.path.basename(fname).split(".")[0]
    raw = open(fname, encoding="utf-8", errors="replace").read()
    out = []
    doc_id = site = support = None
    for is_row, payload in iter_rows(raw):
        if not is_row:
            toks = payload.split()
            for k in range(len(toks) - 1):
                p = toks[k].rstrip(",")
                num = toks[k + 1].rstrip(",")
                if p in SITES and num and num[0].isdigit():
                    window = [w.strip("(),:").lower() for w in toks[k + 2:k + 14]]
                    if any(w in SUPPORT_WORDS for w in window):
                        doc_id = f"{p} {num.rstrip(',')}"
                        site = SITES[p]
                        support = next((w for w in window if w in SUPPORT_WORDS), "?")
                        break
            continue
        if doc_id is None:
            continue
        cells = [" ".join(c.split()) for c in payload]
        cells = [c for c in cells]
        if not cells:
            continue
        first = cells[0].strip()
        if not first or not is_locus_tok(first.split()[0] if first.split() else ""):
            continue
        alltoks = [t for c in cells for t in c.split()]
        if has_decimal_gloss(alltoks) or lower_run(alltoks) >= 4:
            continue
        locus = first.split()[0]
        body_cells = cells[1:]
        uncertain = 1 if any("?" in c for c in body_cells) else 0
        restored = 1 if any(("[" in c or "]" in c) for c in body_cells) else 0
        damaged = 1 if any("…" in c for c in body_cells) else 0
        def cleaned(c):
            return "".join(ch for ch in c if ch not in "[]{}?<>")
        nz_int, nz_frac = "", ""
        content_cells = []
        for c in body_cells:
            cc = cleaned(c).strip()
            if not cc:
                continue
            toks = cc.replace("-", " - ").split()
            if all(is_int_tok(t) for t in toks if t != "-"):
                nz_int += "".join(t for t in toks if is_int_tok(t))
            elif all(is_frac_tok(t) for t in toks if t != "-"):
                nz_frac += "".join(t for t in toks if is_frac_tok(t))
            else:
                content_cells.append(cc)
        if not nz_int and not nz_frac:
            continue
        statement = content_cells[0] if content_cells else ""
        logogram = " ".join(c for c in content_cells[1:] if c) if len(content_cells) > 1 else ""
        context = statement.replace(" - ", "-").replace(" -", "-").replace("- ", "-")
        context = context.split()[-1] if context.split() else ""
        is_kuro = 1 if "KU-RO" in (statement.replace(" ", "")) or "KU-RO" in context else 0
        out.append(dict(source_file=src, doc_id=doc_id, site=site, support=support,
                        locus=locus, seq=len(out), context_word=context,
                        logogram=logogram, integer=nz_int, fraction_seq=nz_frac,
                        uncertain=uncertain, restored=restored, damaged=damaged,
                        is_kuro=is_kuro, parser="B"))
    return out


def main():
    rows = []
    for f in ("HTtexts.html", "misctexts.html", "religioustexts.html"):
        rows += parse_file(Y + f)
    with open(os.path.join(HERE, "parser_b_output.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SCHEMA["fields"])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    n_frac = sum(1 for r in rows if r["fraction_seq"])
    docs = {r["doc_id"] for r in rows}
    print(f"parser B: {len(rows)} records, {n_frac} with fractions, {len(docs)} docs")


if __name__ == "__main__":
    main()
