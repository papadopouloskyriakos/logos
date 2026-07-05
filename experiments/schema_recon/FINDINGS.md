# Schema recon — does the corpus retain the administrative payload layer? (READ-ONLY)

**Date:** 2026-07-05. Reads corpus + code read-only; writes ONLY to `experiments/schema_recon/`.
Nothing under `paper/`, no prereg, no deposited file, no sweep touched. Findings only — no
normalization, no schema computed.

## 1. Corpus source-of-truth + a verbatim record with numerals + logogram

- **Payload lives in `corpus/silver/inscriptions_structured.json`** (the flat
  `inscriptions.json` is `signs` **only** — no numerals, no position; experiments that need the
  payload must use the *structured* file). Built by `corpus_io_structured.py` from the bronze
  `transliteratedWords` ordered stream.
- **Verbatim, HT2** (commodity × quantity, adjacency preserved):
```json
{ "id":"HT2","site":"Haghia Triada","context":"LMIB","support":"Tablet",
  "stream":[ {"t":"word","signs":["A","KA","RU"]}, {"t":"div"},
             {"t":"word","signs":["OLE+U"]}, {"t":"num","v":20}, {"t":"nl"},
             {"t":"word","signs":["OLE+A"]}, {"t":"num","v":17}, {"t":"nl"},
             {"t":"word","signs":["OLE+E"]}, {"t":"num","v":3},  {"t":"nl"},
             {"t":"word","signs":["KI","RE","TA","NA"]}, {"t":"word","signs":["OLE+U"]}, {"t":"num","v":54}, {"t":"nl"},
             {"t":"word","signs":["OLE+A"]}, {"t":"num","v":47}, {"t":"nl"}, {"t":"num","v":1} ] }
```
The ordered stream is literally *heading → (commodity, quantity)⁺*: `OLE+U 20 · OLE+A 17 · OLE+E 3 …`.

## 2. Present / ABSENT (with on-disk evidence)

Stream token census (1341 inscriptions): `word 3147 · nl 2114 · num 1276 · div 463 · other 1056`.

| element | status | evidence |
|---|---|---|
| **Numerals (quantities) as parsed values** | **PRESENT** | `{"t":"num","v":int}` — **1276** tokens, values **1–3000** (HT2: `num 20/17/3/54/47`). *Integers only* (`^\d+$`). |
| **Commodity / logogram signs as typed tokens** | **PRESENT** | **629** occurrences, **20** distinct (`OLE 133, GRA 115, CYP 95, VIN 75, VIR 58, VS 34, OLIV 26, HIDE 17 …`); ontology `class="logogram"` (`LOGO:` prefix). In-stream they are `word` tokens (`OLE+U`), typed via the ontology. |
| **Fraction signs** | **PRESENT but UNPARSED** | **310** tokens, **10** distinct Aegean fractions (`¹⁄₂,³⁄₄,³⁄₈,¹⁄₁₆,¹⁄₃,¹⁄₄,¹⁄₅,¹⁄₈,≈¹⁄₄,≈¹⁄₆`) captured as `{"t":"other","raw":"…"}` — retained as strings, **not** numeric values. |
| **Word-position / role (line, sequence)** | **PRESENT** | full ordered `stream`; `nl` **2114** (line breaks), `div` **463** (word dividers). Sequence + line fully retained. *Role* (heading vs entry) is implicit in position, **not** an explicit tag. |
| **Total / subtotal marker** | **PRESENT (as words, not a typed marker)** | `KU-RO` (grand total) **37**×, `KI-RO` (deficit/owed) **16**×, `PO-TO-KU-RO` variants 2×; ordinary `word` tokens, recoverable by sign-sequence match. |

Also in `other` (1056): 515 untransliterated raw Linear-A glyph groups (`𐝀𐝁𐝁 …`, 39 distinct) and
160 `*NNN` unidentified tokens (57 distinct).

## 3. Bottom line — is transaction-schema induction (commodity × quantity × total) executable?

**PARTIAL-executable on the corpus as-ingested.**

- **Executable NOW (integer core):** the ordered structured stream supplies **commodity (logogram)
  × integer-quantity** with **adjacency/pairing**, **line/sequence position**, and **totals**
  (`KU-RO`/`KI-RO`). HT2 shows the exact commodity-then-quantity structure. This is enough to induce
  the entry-level schema and attempt total-reconciliation on integer-only tablets.
- **Needs a re-ingest for a *quantitatively complete* schema:** **fractions are unparsed** (310
  present as raw strings → any exact total-vs-entries reconciliation would under/mis-count), and 515
  commodity/sign glyph groups are untransliterated. The bronze
  `transliteratedWords`/`parsedInscription` source is **on disk** (`/tmp/lineara/items_analysis/
  inscriptions.json`, 1.5 MB) — so a fraction-parsing re-ingest is feasible **without a re-fetch**.
  (The prior audit `docs/findings/2026-06-30-inventory-cleaned.md` already flagged that numeric/
  fraction content beyond the integer stream needs `parsedInscription`.)

**Verdict: PARTIAL** — the commodity × integer-quantity × total × position schema is executable now
on `inscriptions_structured.json`; a fraction-complete, exact-reconciliation schema needs a
fraction-parsing re-ingest from the already-present bronze (not a re-fetch, not a re-fetch-from-Younger).

## Isolation
Only `experiments/schema_recon/` written (this file). `paper/`, prereg, Zenodo, corpus source, and
the running sweep unmodified; corpus not normalized; no schema computed; no network.
