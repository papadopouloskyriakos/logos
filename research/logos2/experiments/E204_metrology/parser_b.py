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


def strip_html(raw):
    """Char-scanner tag stripper; <br>/<p>/<tr>/<td>/<div> become newlines."""
    out, i, n = [], 0, len(raw)
    while i < n:
        c = raw[i]
        if c == "<":
            j = raw.find(">", i + 1)
            if j == -1:
                break
            tag = raw[i + 1:j].split()[0].lower().strip("/") if raw[i + 1:j].split() else ""
            if tag in ("br", "p", "tr", "td", "div", "li", "table"):
                out.append("\n")
            i = j + 1
        elif c == "&":
            j = raw.find(";", i + 1)
            if 0 < j - i <= 8:
                out.append(ENT.get(raw[i:j + 1], " "))
                i = j + 1
            else:
                out.append(c); i += 1
        else:
            out.append(c); i += 1
    return "".join(out)


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


def parse_file(fname):
    src = os.path.basename(fname).split(".")[0]
    text = strip_html(open(fname, encoding="utf-8", errors="replace").read())
    lines = [ln for ln in text.split("\n")]
    out = []
    doc_id = site = support = None
    i = 0
    while i < len(lines):
        toks = [t for t in lines[i].replace("•", " • ").split() if t]
        # document detection: (SITE-PREFIX, integer) then a support word within 12 tokens
        for k in range(len(toks) - 1):
            p = toks[k].rstrip(",")
            num = toks[k + 1].rstrip(",")
            if p in SITES and num and num[0].isdigit():
                window = [w.strip("(),:").lower() for w in toks[k + 2:k + 14]]
                if any(w in SUPPORT_WORDS for w in window):
                    doc_id = f"{p} {num}"
                    site = SITES[p]
                    support = next((w for w in window if w in SUPPORT_WORDS), "?")
                    break
        if doc_id is None:
            i += 1
            continue
        if has_decimal_gloss(toks) or lower_run(toks) >= 4:
            i += 1
            continue
        if not toks or not is_locus_tok(toks[0]):
            i += 1
            continue
        locus = toks[0]
        body = toks[1:]
        uncertain = 1 if any("?" in t for t in body) else 0
        restored = 1 if any(("[" in t or "]" in t) for t in body) else 0
        damaged = 1 if any("…" in t for t in body) else 0
        # merge hyphen-separated sign groups (token-level FSM)
        merged, pend = [], None
        for t in body:
            if t == "•":
                if pend: merged.append(pend); pend = None
                continue
            if t == "-":
                if pend: pend += "-"
                continue
            if pend and pend.endswith("-"):
                pend += t
            elif pend is None:
                pend = t
            else:
                merged.append(pend); pend = t
        if pend:
            merged.append(pend)
        merged = [t.strip("-") for t in merged if t.strip("-")]
        clean = ["".join(ch for ch in t if ch not in "[]{}?<>") for t in merged]
        clean = [t for t in clean if t]
        # continuation lines: only fraction tokens
        j = i + 1
        extra = []
        while j < len(lines):
            nt = [t for t in lines[j].split() if t]
            if nt and all(is_frac_tok(t) for t in nt):
                extra += nt; j += 1
            else:
                break
        nz = []
        k = len(clean)
        while k > 0 and (is_int_tok(clean[k - 1]) or is_frac_tok(clean[k - 1])):
            nz.insert(0, clean[k - 1]); k -= 1
        nz += extra
        if not nz:
            i = j
            continue
        integer = "".join(t for t in nz if is_int_tok(t))
        frac_seq = "".join(t for t in nz if is_frac_tok(t))
        pre = clean[:k]
        logogram = " ".join(t for t in pre if "+" in t or t.startswith("*") or
                            t.startswith("{"))
        words = [t for t in pre if t not in set(logogram.split()) and t and
                 (t[0].isupper() or t[0] == "*")]
        context = words[-1] if words else ""
        is_kuro = 1 if any("KU-RO" in t for t in pre) else 0
        out.append(dict(source_file=src, doc_id=doc_id, site=site, support=support,
                        locus=locus, seq=len(out), context_word=context,
                        logogram=logogram, integer=integer, fraction_seq=frac_seq,
                        uncertain=uncertain, restored=restored, damaged=damaged,
                        is_kuro=is_kuro, parser="B"))
        i = j
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
