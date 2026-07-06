#!/usr/bin/env python3
"""sigla_decode.py — decode SigLA's client-side database.js into structured JSON.

SigLA (https://sigla.phis.me/, © Salgarella & Castellan, CC BY-NC-SA 4.0) is a js_of_ocaml app
that ships its whole corpus as two OCaml `Marshal` blobs embedded in `database.js`, encoded as
OCaml-escaped (`\\ddd` decimal) byte strings inside JS single-quoted literals (`var signs = ...`,
`var data = ...`). This decodes them without a browser or the OCaml runtime:

  stage 1  JS string literal  -> OCaml string value (undo `\\\\` etc.)
  stage 1  OCaml `%S` escapes -> raw bytes           (undo `\\ddd`, strip surrounding `"`)
  stage 2  OCaml Marshal      -> Python values        (blocks/strings/ints/doubles + sharing)
  stage 3  domain shapes      -> documents + signs    (OCaml Map/list/option walkers)

LICENSING: SigLA is CC BY-NC-SA 4.0. The raw snapshot AND this decoder's JSON output are treated
as licensed vendor-derived data -> GITIGNORED under corpus/bronze/ (house policy #10). This SCRIPT
(the method) is public. Reproduce locally from the snapshot; do not redistribute the JSON.

Validated 2026-07-06: ARKH 7 -> A308 (matches SigLA's own doc HTML), KH Wc 2026 -> A322, HT 24a
AB-signs match corpus/silver 9/9 (AB81=KU AB56=PA3 AB53=RI AB57=JA AB03=PA AB31=SA AB26=RU AB28=I
AB70=KO). See corpus/bronze/sigla_browse_2026/DECODE.md.

Usage:
  python scripts/sigla_decode.py [--src DB_JS] [--out OUTDIR]
  # defaults: src=corpus/bronze/sigla_browse_2026/database.js  out=<same dir>
"""
import argparse, json, os, re, struct, sys

# ---------------------------------------------------------------- stage 1: bytes out of database.js
def extract_literal(varname, text):
    m = re.search(r"var\s+%s\s*=\s*'" % re.escape(varname), text)
    if not m:
        raise KeyError(f"var {varname} not found")
    i = m.end(); buf = []
    while i < len(text):
        c = text[i]
        if c == "\\": buf.append(text[i:i+2]); i += 2; continue
        if c == "'": break
        buf.append(c); i += 1
    return "".join(buf)

def js_unescape(s):
    out = []; i = 0; n = len(s)
    while i < n:
        c = s[i]
        if c == "\\":
            nx = s[i+1]
            if nx == "x": out.append(chr(int(s[i+2:i+4], 16))); i += 4; continue
            if nx == "u": out.append(chr(int(s[i+2:i+6], 16))); i += 6; continue
            out.append({"\\": "\\", '"': '"', "'": "'", "n": "\n", "t": "\t",
                        "r": "\r", "b": "\b", "f": "\f", "0": "\0", "/": "/"}.get(nx, nx))
            i += 2; continue
        out.append(c); i += 1
    return "".join(out)

def ocaml_unescape(s):
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"': s = s[1:-1]   # strip %S quotes
    out = bytearray(); i = 0; n = len(s)
    while i < n:
        c = s[i]
        if c == "\\":
            nx = s[i+1]
            if nx.isdigit(): out.append(int(s[i+1:i+4]) & 0xFF); i += 4; continue
            if nx == "x": out.append(int(s[i+2:i+4], 16)); i += 4; continue
            out.append({"\\": 0x5c, '"': 0x22, "'": 0x27, "n": 0x0a,
                        "t": 0x09, "r": 0x0d, "b": 0x08}.get(nx, ord(nx)))
            i += 2; continue
        out.append(ord(c) & 0xFF); i += 1
    return bytes(out)

def blob_bytes(varname, text):
    b = ocaml_unescape(js_unescape(extract_literal(varname, text)))
    if b[:4].hex() != "8495a6be":
        raise ValueError(f"{varname}: not an OCaml Marshal small blob (magic {b[:4].hex()})")
    return b

# ---------------------------------------------------------------- stage 2: OCaml Marshal reader
class Marshal:
    def __init__(self, b):
        self.b = b; self.pos = 20; self.objs = []      # 20-byte small header
    def _u(self, n, signed=False):
        v = int.from_bytes(self.b[self.pos:self.pos+n], "big", signed=signed); self.pos += n; return v
    def read(self):
        c = self.b[self.pos]; self.pos += 1
        if c >= 0x80: return self._block(c & 0x0F, (c >> 4) & 0x07)
        if c >= 0x40: return c & 0x3F
        if c >= 0x20: return self._string(c & 0x1F)
        if c == 0x00: return self._u(1, True)
        if c == 0x01: return self._u(2, True)
        if c == 0x02: return self._u(4, True)
        if c == 0x03: return self._u(8, True)
        if c == 0x04: return self.objs[len(self.objs) - self._u(1)]
        if c == 0x05: return self.objs[len(self.objs) - self._u(2)]
        if c == 0x06: return self.objs[len(self.objs) - self._u(4)]
        if c == 0x08: h = self._u(4); return self._block(h & 0xFF, h >> 10)
        if c == 0x09: return self._string(self._u(1))
        if c == 0x0A: return self._string(self._u(4))
        if c in (0x0B, 0x0C):
            v = struct.unpack_from(">d" if c == 0x0B else "<d", self.b, self.pos)[0]
            self.pos += 8; self.objs.append(v); return v
        if c in (0x0D, 0x0E, 0x0F, 0x07):
            n = self._u(1) if c in (0x0D, 0x0E) else self._u(4)
            fmt = ">" if c in (0x0D, 0x0F) else "<"
            a = list(struct.unpack_from(fmt + "d"*n, self.b, self.pos)); self.pos += 8*n
            self.objs.append(a); return a
        raise ValueError(f"unhandled Marshal code 0x{c:02x} at {self.pos-1}")
    def _string(self, n):
        s = bytes(self.b[self.pos:self.pos+n]); self.pos += n; self.objs.append(s); return s
    def _block(self, tag, size):
        if size == 0: return {"tag": tag, "items": []}
        obj = {"tag": tag, "items": []}; self.objs.append(obj)
        for _ in range(size): obj["items"].append(self.read())
        return obj

def parse(b): return Marshal(b).read()

# ---------------------------------------------------------------- stage 3: domain walkers
def S(v): return v.decode("utf-8", "replace") if isinstance(v, (bytes, bytearray)) else v
def isB(v, t=None, n=None):
    return isinstance(v, dict) and (t is None or v["tag"] == t) and (n is None or len(v["items"]) == n)
def olist(v):
    out = []
    while isB(v, 0, 2): out.append(v["items"][0]); v = v["items"][1]
    return out
def opt(v): return None if v == 0 else (v["items"][0] if isB(v, 0, 1) else v)
def omap(v, acc=None):                                   # OCaml Map.Make: Empty=0 | Node(l,k,d,r,h)
    if acc is None: acc = []
    if isB(v, 0, 5):
        l, k, d, r, h = v["items"]; omap(l, acc); acc.append((S(k), d)); omap(r, acc)
    return acc

def signname(rec):                                       # sign record B(n>=2): [class, gorila_no, ...]
    f = rec["items"]; cls = S(f[0]); num = f[1]
    if cls == "AB" and isinstance(num, int): return f"AB{num:02d}"
    return f"{cls}{num}"

def first_sign(v):                                       # first embedded sign record under v (or None)
    if isB(v) and len(v["items"]) >= 2 and isinstance(v["items"][0], (bytes, bytearray)) \
       and isinstance(v["items"][1], int):
        return v
    if isB(v):
        for x in v["items"]:
            r = first_sign(x)
            if r: return r
    return None

def decode_signs(text):
    root = parse(blob_bytes("signs", text))
    out = {}
    for key, d in omap(root["items"][0]):
        f = d["items"]
        out[str(key)] = {"sigla_id": key, "class": S(f[0]), "gorila_number": f[1],
                         "name": signname(d),
                         "ref": S(opt(f[3])) if len(f) > 3 and opt(f[3]) is not None else None}
    return out

def decode_documents(text):
    root = parse(blob_bytes("data", text))
    docs = []
    for designation, doc in omap(root["items"][0]):
        rec = doc["items"][0]["items"]
        meta = rec[0]["items"]
        glyphs = []
        for g in rec[4]["items"]:
            gf = g["items"]
            sr = first_sign(gf[1])
            bbox = gf[7]["items"] if isB(gf[7]) else None
            glyphs.append({
                "sign": signname(sr) if sr else None,
                "is_divider": (sr is None and len(gf) > 4 and gf[4] == 1),
                "bbox": bbox,                             # [x, y, w, h] px in the drawing
            })
        docs.append({
            "designation": designation,
            "support": S(meta[0]) if meta[0] else None,
            "site": S(meta[2]) if meta[2] else None,
            "dimensions_cm": (opt(meta[6])["items"] if opt(meta[6]) is not None else None),
            "period": S(opt(meta[7])) if opt(meta[7]) is not None else None,
            "source_url": S(opt(meta[8])) if opt(meta[8]) is not None else None,
            "sigla_path": S(rec[1]),
            "transcription": [g["sign"] for g in glyphs if g["sign"]],
            "n_glyphs": len(glyphs),
            "glyphs": glyphs,
        })
    return docs

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    default_src = os.path.join(here, "..", "corpus", "bronze", "sigla_browse_2026", "database.js")
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=os.path.normpath(default_src))
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = a.out or os.path.dirname(a.src)
    text = open(a.src, encoding="latin-1").read()
    signs = decode_signs(text); docs = decode_documents(text)
    os.makedirs(out, exist_ok=True)
    json.dump(signs, open(os.path.join(out, "sigla_signs.json"), "w"), ensure_ascii=False, indent=1)
    json.dump(docs, open(os.path.join(out, "sigla_documents.json"), "w"), ensure_ascii=False, indent=1)
    n_syll = sum(1 for s in signs.values() if s["class"] == "AB")
    print(f"signs:     {len(signs)}  ({n_syll} AB-class, {len(signs)-n_syll} A-only)")
    print(f"documents: {len(docs)}   sites={len(set(d['site'] for d in docs))}")
    print(f"wrote {out}/sigla_signs.json and sigla_documents.json (GITIGNORED — licensed-derived)")

if __name__ == "__main__":
    main()
