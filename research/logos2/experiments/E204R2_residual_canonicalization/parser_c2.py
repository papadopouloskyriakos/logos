"""E204R Parser C — tree-based canonical table parser (html.parser.HTMLParser subclass builds
an explicit element tree; table walk extracts records). Implements the frozen semantic spec
independently. Shares nothing with Parser D except raw files + spec + SCHEMA."""
import csv
import json
import os
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
Y = "/home/claude-runner/gitlab/n8n/logos/corpus/bronze/younger_lineara/"
SCHEMA = json.load(open(os.path.join(HERE, "SCHEMA.json")))
FRAC = set(SCHEMA["fraction_alphabet"])
SITES = SCHEMA["site_prefix"]
SUPPORT = {"tablet", "nodule", "roundel", "sealing", "vessel", "bar", "lame", "gorila",
           "za", "wc", "wa", "wb", "zb", "zc", "zd", "ze", "zf", "zg"}
PROSE = {"according", "perhaps", "sometimes", "found", "distribute", "gave", "record",
         "records", "note", "cf.", "see", "comments", "update", "bibliography"}


class Node:
    __slots__ = ("tag", "children", "parent")

    def __init__(self, tag, parent=None):
        self.tag, self.children, self.parent = tag, [], parent


class TreeBuilder(HTMLParser):
    STRUCTURAL = {"table", "tr", "td", "th", "sub", "sup"}

    def __init__(self):
        super().__init__(convert_charrefs=True)  # stdlib decodes entities (spec map subsumed)
        self.root = Node("root")
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        if tag in self.STRUCTURAL:
            if tag in ("tr", "td", "th"):          # table recovery: auto-close (amendment R1)
                close = {"tr": ("tr", "td", "th"), "td": ("td", "th"), "th": ("td", "th")}[tag]
                p = self.cur
                while p is not self.root and p.tag in close:
                    p = p.parent
                    self.cur = p
                if tag == "tr":
                    while self.cur is not self.root and self.cur.tag == "tr":
                        self.cur = self.cur.parent
            n = Node(tag, self.cur)
            self.cur.children.append(n)
            self.cur = n

    def handle_endtag(self, tag):
        if tag in self.STRUCTURAL:
            p = self.cur
            while p is not self.root and p.tag != tag:
                p = p.parent
            if p is not self.root:
                self.cur = p.parent

    def handle_data(self, data):
        self.cur.children.append(data)


def text_of(node):
    """Recursive text with sub/sup digits appended directly to the preceding token."""
    parts = []
    for ch in (node.children if isinstance(node, Node) else []):
        if isinstance(ch, str):
            parts.append(ch)
        elif ch.tag in ("sub", "sup"):
            t = text_of(ch).strip()
            if parts:
                parts[-1] = parts[-1].rstrip() + t
            else:
                parts.append(t)
        elif ch.tag in ("table", "tr", "td", "th"):
            continue  # nested structure handled by the walker
        else:
            parts.append(text_of(ch))
    return " ".join("".join(parts).replace(" ", " ").split())


def walk(node, out):
    """Yield ('text', s) for inter-table text and ('row', [cells]) for table rows, in order."""
    for ch in (node.children if isinstance(node, Node) else []):
        if isinstance(ch, str):
            s = " ".join(ch.replace(" ", " ").split())
            if s:
                out.append(("text", s))
        elif ch.tag == "tr":
            cells = [text_of(c) for c in ch.children
                     if isinstance(c, Node) and c.tag in ("td", "th")]
            out.append(("row", cells))  # cell subtrees are NOT re-walked (amendment R1)
        elif ch.tag in ("sub", "sup"):
            s = text_of(ch)
            if s:
                out.append(("text", s))
        else:
            walk(ch, out)


def is_locus(tok):
    if tok in ("side.", "edge.", "lat."):
        return True
    s = tok
    if s[:1] and s[:1] in "ab":
        s = s[1:]
    while s[:1] and s[:1] in "iv":
        s = s[1:]
    if s[:1] == ".":
        s = s[1:]
    core = s.split("-")[0]
    return core.isdigit() and len(core) <= 2


def cell_class(cell):
    toks = [t for t in cell.replace("-", " ").split() if t]
    if toks and all(t.isdigit() and len(t) <= 4 for t in toks):
        return "int"
    if toks and all(len(t) <= 2 and all(c in FRAC for c in t) for t in toks):
        return "frac"
    return "content" if toks else "empty"


def coalesce(stream):
    """Merge consecutive text events (inline tags fragment designations across nodes)."""
    out, buf = [], []
    for kind, payload in stream:
        if kind == "text":
            buf.append(payload)
        else:
            if buf:
                out.append(("text", " ".join(buf))); buf = []
            out.append((kind, payload))
    if buf:
        out.append(("text", " ".join(buf)))
    return out


def records(stream):
    stream = coalesce(stream)
    doc_id = site = support = None
    out, dup_log = [], []
    seen = set()
    for kind, payload in stream:
        if kind == "text":
            toks = payload.split()
            for k in range(len(toks) - 1):
                p = toks[k].strip(",")
                num = toks[k + 1].strip(",.")
                num2 = toks[k + 2].strip(",.") if k + 2 < len(toks) else ""
                if p in SITES and not num[:1].isdigit() and num.lower() in \
                        ("za", "zb", "zc", "zd", "ze", "zf", "zg", "wa", "wb", "wc",
                         "wd", "we", "wg", "wy") and num2[:1].isdigit():
                    win = [w.strip("(),:").lower() for w in toks[k + 1:k + 14]]
                    doc_id, site = f"{p} {num} {num2}", SITES[p]
                    support = num.lower()
                    break
                if p in SITES and num[:1].isdigit():
                    win = [w.strip("(),:").lower() for w in toks[k + 2:k + 14]]
                    if any(w in SUPPORT for w in win):
                        doc_id, site = f"{p} {num}", SITES[p]
                        support = next(w for w in win if w in SUPPORT)
                        break
            continue
        if doc_id is None or not payload:
            continue
        cells = payload
        first = cells[0].split()
        if not first or not is_locus(first[0]):
            # continuation row: only fraction cells
            nonempty = [c for c in cells if c.strip()]
            if out and nonempty and all(cell_class(c) == "frac" for c in nonempty):
                out[-1]["fraction_seq"] += "".join("".join(c.split()) for c in nonempty)
            continue
        low = payload_lower = " ".join(cells).lower()
        if any(m in payload_lower.split() or f"{m}" in payload_lower for m in PROSE):
            continue
        if any(a.isdigit() and b.isdigit()
               for c in cells for a, _, b in [t.partition(".") for t in c.split()] if _):
            continue  # decimal gloss
        row_all = " ".join(cells)
        uncertain = 1 if "?" in row_all else 0
        restored = 1 if ("[" in row_all or "]" in row_all) else 0
        damaged = 1 if ("…" in row_all or "vest." in row_all) else 0
        integer = frac = ""
        content = []
        rc1_damaged = 0
        anomaly = 0
        for c in cells[1:]:
            cc = "".join(ch for ch in c if ch not in "[]{}?<>").strip()
            if not cc:
                continue
            k = cell_class(cc)
            if k == "int":
                integer += "".join(cc.split())
            elif k == "frac":
                frac += "".join(cc.split())
            else:
                leading_hyphen = cc.lstrip().startswith("-")     # RC1
                txt = " ".join(cc.replace(" - ", "-").replace("- ", "-")
                               .replace(" -", "-").split())
                toks2 = [t for t in txt.split() if t.strip("•")]
                txt = " ".join(t.strip("•") for t in toks2 if t.strip("•"))
                if leading_hyphen and txt and not txt.startswith("-"):
                    txt = "-" + txt
                if leading_hyphen:
                    rc1_damaged = 1
                if "&" in txt or "#" in txt:                     # RC3
                    anomaly = 1
                if txt:
                    content.append(txt)
        if not integer and not frac:
            continue
        statement = content[0] if content else ""
        logogram = " ".join(content[1:])
        key = (doc_id, first[0], statement, integer, frac)
        if key in seen:
            dup_log.append(key)
            continue
        seen.add(key)
        out.append(dict(source_file="", doc_id=doc_id, site=site, support=support,
                        locus=first[0], seq=len(out), context_word=statement,
                        logogram=logogram, integer=integer, fraction_seq=frac,
                        uncertain=uncertain, restored=restored,
                        damaged=1 if (damaged or rc1_damaged) else 0,
                        anomaly=anomaly,
                        is_kuro=1 if "KU-RO" in statement else 0, parser="C2"))
    return out, dup_log


def main():
    rows, dups = [], []
    for f in ("HTtexts.html", "misctexts.html", "religioustexts.html"):
        tb = TreeBuilder()
        tb.feed(open(Y + f, encoding="utf-8", errors="replace").read())
        stream = []
        walk(tb.root, stream)
        rr, dd = records(stream)
        for r in rr:
            r["source_file"] = f.split(".")[0]
        rows += rr
        dups += dd
    with open(os.path.join(HERE, "parser_c2_output.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SCHEMA["fields"])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    json.dump({"duplicates_logged": len(dups)},
              open(os.path.join(HERE, "parser_c2_duplicates.json"), "w"))
    print(f"parser C2: {len(rows)} records, "
          f"{sum(1 for r in rows if r['fraction_seq'])} with fractions, "
          f"{len({r['doc_id'] for r in rows})} docs, dups {len(dups)}")


if __name__ == "__main__":
    main()
