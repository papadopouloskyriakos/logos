# Decoding the SigLA database (`database.js`) — method + validation

*2026-07-06. Tooling: `scripts/sigla_decode.py`. All counts below are script-generated.*

## What this is

We already hold a full snapshot of **SigLA** — *The signs of Linear A: a palaeographical database*
(Salgarella & Castellan, <https://sigla.phis.me/>, CC BY-NC-SA 4.0) — under
`corpus/bronze/sigla_browse_2026/`. The whole corpus ships to every visitor inside **`database.js`**
as two OCaml `Marshal` blobs (`var signs`, `var data`), encoded as OCaml-escaped byte strings in JS
string literals. The snapshot's `PROVENANCE.md` flagged it *"encoded/binary, not parsed."* It is now
parsed — no browser and no OCaml runtime required.

**So SigLA did not need acquiring; it needed decoding.** `scripts/sigla_decode.py` does that.

## Decode pipeline

| stage | transform |
|---|---|
| 1 | JS string literal → OCaml string value (undo `\\`, `\'`, `\"`) |
| 1 | OCaml `%S` escapes → raw bytes (undo decimal `\ddd`; strip the surrounding `"`) — magic `0x8495A6BE` = OCaml `Marshal` "small" |
| 2 | OCaml `Marshal` → Python values: blocks `{tag,items}`, strings, ints (INT8/16/32/64), doubles, **object sharing** (SHARED8/16/32 back-references) |
| 3 | domain walkers: OCaml `Map.Make` (`Empty=0 \| Node(l,k,d,r,h)`), lists (`[]=0 \| h::t`), options (`None=0 \| Some x`) |

`signs` and `data` are each a `Map`: `signs` keyed by SigLA sign-id, `data` keyed by document
designation. Both blobs parse to 100% of their bytes.

## What the corpus contains (generated)

- **802 documents** across **22 sites** — Haghia Triada 372, Khania 220, Phaistos 64, Zakros 44,
  Knossos 37, Mallia 20, Arkhanes 10, Kea 7, … (built from GORILA + post-GORILA additions, per the
  site's changelog).
- **Supports**: Tablet 452, Nodule 166, Roundel 146, plus sealings, pithoi, libation tables, sherds,
  a lamp, jewellery, a stone weight, …
- **Periods**: LM IB 640, MM IIB 34, MM IIIB 28, MM II 19, LM IA 18, LM I 17, …
- **376 signs** in the catalogue: **77 AB-class** (shared Linear A/B, e.g. `AB81`) + **299 A-only**
  (Linear-A-specific, e.g. `A308`, `A546`) — this is exactly the AB-vs-A distinction
  `scripts/inventory/build_ontology.py` cites SigLA for.
- **5,144 glyphs total, 4,756 sign-identified**, each with its SigLA sign-id **and a bounding box**
  `[x,y,w,h]` in the drawing. **783/802** carry a `source_url` (CEFAEL/GORILA etc.); **634/802**
  carry physical dimensions.

Per-document record (in `sigla_documents.json`): `designation, support, site, dimensions_cm, period,
source_url, sigla_path, transcription (ordered sign-ids), n_glyphs, glyphs[{sign, is_divider, bbox}]`.
Per-sign record (`sigla_signs.json`): `sigla_id, class, gorila_number, name, ref`.

## Validation

1. **Single-document ground truth.** `ARKH 7` → `A308` (+ a logogram) — matches SigLA's own rendered
   `doc_ARKH7.html` exactly. `KH Wc 2026` → `A322`.
2. **Against our independent silver corpus.** `HT 24a` — all **9/9** AB-signs match
   `corpus/silver` (AB81=KU AB56=PA₃ AB53=RI AB57=JA AB03=PA AB31=SA AB26=RU AB28=I AB70=KO).
3. **At scale (the decisive test).** For the **309** documents present in both SigLA and silver with
   a 1:1-alignable syllabic sequence, we *learned* the AB-number→sound map by alignment (nothing
   hardcoded). It reproduces the **canonical Linear B syllabary** with no top-value errors across
   **74** AB-signs: AB81=KU, AB08=A, AB57=JA, AB77=KA, AB59=TA, AB67=KI, AB80=MA, AB03=PA, AB01=DA,
   AB26=RU, AB53=RI, AB37=TI, AB60=RA, AB30=NI, AB58=SU, AB10=U … Residual 1-vote conflicts are
   ordinary SigLA-vs-Younger disagreements on damaged signs and occasional off-by-one alignment.

## Why SigLA differs from the ingested corpus (and why that is the point)

logos silver is built from **lineara.xyz** (a normalized transliteration). SigLA is **palaeographic**:
it keeps composite/ligature signs as **A-series sign-ids** (`A546`, `A707`, …) where lineara.xyz
*decomposes* them into syllabic components. That difference **is** the transcription-uncertainty layer
the Salgarella-lecture audit flagged as missing (Task G): SigLA gives, per glyph, the actual sign
drawn + its position + the AB-vs-A palaeographic classification.

## Downstream uses unlocked

- A second, authoritative corpus to **cross-check** silver (reconciles the 802-doc SigLA set against
  the 1,341-record silver set; exposes composite-vs-decomposed segmentation choices).
- The **palaeographic-variant / bounding-box** layer for representation-sensitivity work.
- SigLA's own **toponym forms** (`pa-i-to`, `tu-ru-sa`, `di-ki-ta`, …) for the LA→LB anchor channel.

## Reproduce

```
python scripts/sigla_decode.py         # reads corpus/bronze/sigla_browse_2026/database.js
```

Outputs `sigla_signs.json` + `sigla_documents.json` beside the source. **Licensing:** SigLA is
CC BY-NC-SA 4.0; the raw snapshot and this decoded JSON are treated as licensed vendor-derived data
and are **gitignored** (`corpus/bronze/*`, house policy #10). This script and this note (the *method*)
are public; the JSON is regenerated locally, not redistributed.
