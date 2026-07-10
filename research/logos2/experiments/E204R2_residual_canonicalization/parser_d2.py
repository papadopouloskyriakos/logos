"""E204R Parser D — single-pass streaming character scanner (explicit states; rows emitted as
they close; no tree, no record regexes). Independent implementation of the frozen semantic
spec. Shares nothing with Parser C except raw files + spec + SCHEMA."""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
Y = "/home/claude-runner/gitlab/n8n/logos/corpus/bronze/younger_lineara/"
SCHEMA = json.load(open(os.path.join(HERE, "SCHEMA.json")))
FRACL = frozenset(SCHEMA["fraction_alphabet"])
SITEMAP = SCHEMA["site_prefix"]
SUPP = frozenset(["tablet", "nodule", "roundel", "sealing", "vessel", "bar", "lame",
                  "gorila", "za", "wc", "wa", "wb", "zb", "zc", "zd", "ze", "zf", "zg"])
PROSEW = frozenset(["according", "perhaps", "sometimes", "found", "distribute", "gave",
                    "record", "records", "note", "cf.", "see", "comments", "update",
                    "bibliography"])
ENTMAP = {"amp": "&", "lt": "<", "gt": ">", "nbsp": " ", "bull": "•", "#8226": "•",
          "#149": "•", "#183": "•", "quot": '"'}


def squash(s):
    out, prev_sp = [], True
    for ch in s.replace(" ", " "):
        sp = ch in " \t\r\n"
        if sp and prev_sp:
            continue
        out.append(" " if sp else ch)
        prev_sp = sp
    return "".join(out).strip()


class Stream:
    """Emits ('text', str) and ('row', [cells]) events from raw HTML in one pass."""

    def __init__(self):
        self.events = []
        self._text = []          # inter-row text buffer
        self._row = None         # list of finished cells
        self._cell = None        # chars of the open cell
        self._sub_depth = 0

    def _flush_text(self):
        s = squash("".join(self._text))
        if s:
            self.events.append(("text", s))
        self._text = []

    def _sink(self):
        return self._cell if self._cell is not None else self._text

    def feed(self, raw):
        i, n = 0, len(raw)
        while i < n:
            ch = raw[i]
            if ch == "<":
                j = raw.find(">", i + 1)
                if j < 0:
                    break
                body = raw[i + 1:j].strip().lower()
                name = body.split()[0] if body.split() else ""
                closing = name.startswith("/")
                tag = name.lstrip("/")
                if tag == "tr":
                    if closing:
                        if self._row is not None:
                            if self._cell is not None:
                                self._row.append(squash("".join(self._cell)))
                                self._cell = None
                            self.events.append(("row", self._row))
                            self._row = None
                    else:
                        self._flush_text()
                        self._row = []
                        self._cell = None
                elif tag in ("td", "th"):
                    if self._row is not None:
                        if closing:
                            if self._cell is not None:
                                self._row.append(squash("".join(self._cell)))
                                self._cell = None
                        else:
                            if self._cell is not None:
                                self._row.append(squash("".join(self._cell)))
                            self._cell = []
                elif tag in ("sub", "sup"):
                    self._sub_depth += (-1 if closing else 1)
                    self._sub_depth = max(self._sub_depth, 0)
                elif tag in ("p", "br", "div", "li") and not closing:
                    self._sink().append("\n" if self._cell is None else " ")
                i = j + 1
            elif ch == "&":
                j = raw.find(";", i + 1)
                if 0 < j - i <= 8:
                    self._sink().append(ENTMAP.get(raw[i + 1:j].lower(), " "))
                    i = j + 1
                elif raw[i + 1:i + 2] == "#":                   # RC2 unterminated numeric ref
                    k2 = i + 2
                    while k2 < n and raw[k2].isdigit() and k2 - i <= 6:
                        k2 += 1
                    ref = raw[i + 1:k2].lower()
                    if ref[1:].isdigit():
                        self._sink().append(ENTMAP.get(ref, "•" if ref in
                                            ("#149", "#183", "#8226") else " "))
                        i = k2
                    else:
                        self._sink().append(ch); i += 1
                else:
                    self._sink().append(ch)
                    i += 1
            else:
                if self._sub_depth > 0 and not ch.isspace():
                    sink = self._sink()
                    while sink and sink[-1].isspace():
                        sink.pop()
                    sink.append(ch)
                else:
                    self._sink().append(ch)
                i += 1
        self._flush_text()
        return self.events


def locus_like(tok):
    if tok in ("side.", "edge.", "lat."):
        return True
    t = tok
    if t and t[0] in "ab":
        t = t[1:]
    while t and t[0] in "iv":
        t = t[1:]
    if t and t[0] == ".":
        t = t[1:]
    if not t:
        return False
    head = t
    dash = t.find("-")
    if dash > 0:
        head = t[:dash]
    return head.isdigit() and 0 < len(head) <= 2


def classify(cell):
    toks = []
    for piece in cell.split():
        for sub in piece.split("-"):
            if sub:
                toks.append(sub)
    if not toks:
        return "empty"
    if all(t.isdigit() and len(t) <= 4 for t in toks):
        return "int"
    ok_frac = True
    for t in toks:
        if len(t) > 2:
            ok_frac = False
            break
        for c in t:
            if c not in FRACL:
                ok_frac = False
                break
    return "frac" if ok_frac else "content"


def hyphen_norm(s):
    parts = s.split()
    glued, cur = [], ""
    for p in parts:
        if p == "-":
            cur += "-"
        elif cur.endswith("-") or (cur and p.startswith("-")):
            cur += p.lstrip("-") if p.startswith("-") and not cur.endswith("-") else p
        elif cur:
            glued.append(cur)
            cur = p
        else:
            cur = p
    if cur:
        glued.append(cur)
    return " ".join(g.strip("-") for g in glued if g.strip("-"))


def main():
    all_rows, dup_n = [], 0
    for fname in ("HTtexts.html", "misctexts.html", "religioustexts.html"):
        raw = open(Y + fname, encoding="utf-8", errors="replace").read()
        events = Stream().feed(raw)
        doc = site = supp = None
        seen = set()
        for kind, payload in events:
            if kind == "text":
                words = payload.split()
                for k, w in enumerate(words[:-1]):
                    pref = w.strip(",")
                    nxt = words[k + 1].strip(",.")
                    third = words[k + 2].strip(",.") if k + 2 < len(words) else ""
                    supp_codes = ("za", "zb", "zc", "zd", "ze", "zf", "zg",
                                  "wa", "wb", "wc", "wd", "we", "wg", "wy")
                    if pref in SITEMAP and nxt.lower() in supp_codes and third[:1].isdigit():
                        doc, site, supp = f"{pref} {nxt} {third}", SITEMAP[pref], nxt.lower()
                        break
                    if pref in SITEMAP and nxt[:1].isdigit():
                        window = [x.strip("(),:").lower() for x in words[k + 2:k + 14]]
                        hit = [x for x in window if x in SUPP]
                        if hit:
                            doc, site, supp = f"{pref} {nxt}", SITEMAP[pref], hit[0]
                            break
                continue
            if doc is None or not payload:
                continue
            cells = payload
            head_toks = cells[0].split()
            if not head_toks or not locus_like(head_toks[0]):
                filled = [c for c in cells if c.strip()]
                if all_rows and filled and all(classify(c) == "frac" for c in filled):
                    all_rows[-1]["fraction_seq"] += "".join(
                        "".join(c.split()) for c in filled)
                continue
            joined = " ".join(cells)
            low = joined.lower()
            if any(w in PROSEW for w in low.split()):
                continue
            dec = False
            for t in joined.split():
                d = t.find(".")
                if 0 < d < len(t) - 1 and t[:d].isdigit() and t[d + 1:].isdigit():
                    dec = True
                    break
            if dec:
                continue
            unc = 1 if "?" in joined else 0
            res = 1 if ("[" in joined or "]" in joined) else 0
            dam = 1 if ("…" in joined or "vest." in joined) else 0
            integer = frac = ""
            content = []
            rc1_dam = 0
            anomaly = 0
            for c in cells[1:]:
                stripped = "".join(ch for ch in c if ch not in "[]{}?<>")
                stripped = squash(stripped)
                if not stripped:
                    continue
                kind2 = classify(stripped)
                if kind2 == "int":
                    integer += "".join(stripped.split())
                elif kind2 == "frac":
                    frac += "".join(stripped.split())
                elif kind2 == "content":
                    starts_dash = stripped.startswith("-")       # RC1
                    hn = hyphen_norm(stripped)
                    kept = [t.strip("•") for t in hn.split() if t.strip("•")]
                    if kept:
                        joined2 = " ".join(kept)
                        if starts_dash and not joined2.startswith("-"):
                            joined2 = "-" + joined2
                        if starts_dash:
                            rc1_dam = 1
                        if "&" in joined2 or "#" in joined2:      # RC3
                            anomaly = 1
                        content.append(joined2)
            if not integer and not frac:
                continue
            statement = content[0] if content else ""
            logogram = " ".join(content[1:])
            key = (doc, head_toks[0], statement, integer, frac)
            if key in seen:
                dup_n += 1
                continue
            seen.add(key)
            all_rows.append(dict(source_file=fname.split(".")[0], doc_id=doc, site=site,
                                 support=supp, locus=head_toks[0], seq=len(all_rows),
                                 context_word=statement, logogram=logogram,
                                 integer=integer, fraction_seq=frac, uncertain=unc,
                                 restored=res, damaged=1 if (dam or rc1_dam) else 0,
                                 anomaly=anomaly,
                                 is_kuro=1 if "KU-RO" in statement else 0, parser="D2"))
    with open(os.path.join(HERE, "parser_d2_output.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SCHEMA["fields"])
        w.writeheader()
        for r in all_rows:
            w.writerow(r)
    print(f"parser D2: {len(all_rows)} records, "
          f"{sum(1 for r in all_rows if r['fraction_seq'])} with fractions, "
          f"{len({r['doc_id'] for r in all_rows})} docs, dups {dup_n}")


if __name__ == "__main__":
    main()
