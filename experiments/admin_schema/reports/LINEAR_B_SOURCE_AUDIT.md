# LINEAR B SOURCE AUDIT (§IV)

## Primary source: DĀMOS (Database of Mycenaean at Oslo)

`corpus/bronze/linearb/damos/items.jsonl` (main worktree; ~5,840 tablets / ~13,562 wordforms). Each record
(`item.*`) carries:

| DĀMOS field | content | layer |
|---|---|---|
| `heading`, `series`, `subseries`, `set`, `tablenumber` | document identity + series/type | **MODEL_VISIBLE** |
| `object`, `material` | support (tablet / nodule / label…), clay | **MODEL_VISIBLE** |
| `find_area`, `area_code`, `find_place`, `find_area_name` | site / findspot | **MODEL_VISIBLE** |
| `chronology1`, `chronogroup` | chronological phase | **MODEL_VISIBLE** |
| `vasewriter` / scribe fields | scribal hand (where recorded) | **MODEL_VISIBLE** (sensitivity — coverage varies) |
| `content` / `richcontent` | line-numbered transliteration with quoted words, numerals, ideograms | **MIXED — see below** |
| `permalink1/2` | stable identifiers (damos.hf.uio.no/N) | metadata |
| `notes`, `comment` | editorial prose (may contain readings) | **EVALUATION_ONLY** |

## The blinding crux (load-bearing)

`content` is **transliterated** — the syllabic *phonetic values* (`de-u-ki-jo-jo`, `ko-no-so`) that ARE the
deciphered reading. Feeding these to the model would defeat the entire premise. The firewall (§VII) therefore
requires a **de-phoneticising transform** at ingest:

- Each syllabogram → its **opaque Linear B graphic sign-ID** — the Ventris–Chadwick/GORILA sign number or the
  Unicode B-number (`ko` → `B070`, `no` → `B052`, `so` → `B012`), **stripped of the phonetic value**. The
  B-number is a *graphic* identity, not a sound. (`scripts/cross_script/data.py` already parses the Unicode
  name `"LINEAR B SYLLABLE B078 QE"` → the B-number is the opaque ID, `QE` is the value to withhold.)
- Numerals, fractions, and **logograms/ideograms** → kept as opaque symbol IDs (structure, not reading).
- Line numbers (`.1`, `.2`), word boundaries, quotation ('…'), entry/row structure → kept (layout).
- The **transliteration string, lemma, Greek word, gloss, translation** → routed to `data/evaluation_only/`,
  never to `data/model_visible/`.

Model-visible LB representation = **[opaque sign-ID sequence · numerals · logograms · layout · document
series/type · support · site/findspot · chronology · scribe · damage/uncertainty]**. This is exactly the
representation Linear A already ships in (see `LINEAR_A_FEATURE_COMPATIBILITY.md`).

## Secondary LB sources (to reconcile where available)

- **LiBER** (Linear B Electronic Resources) — layout-preserving digital edition; would supply spatial/layout
  coordinates beyond DĀMOS line numbers. Status: `TO_AUDIT` (web). Layout is a *sensitivity* feature (LA has
  SigLA bounding boxes; LB fine layout coverage partial) — not in the transfer-critical primary set unless
  confirmed representable in both.
- **PA-I-TO** (RTI/3D Linear B epigraphy) — palaeography/imaging; supports damage/allography features and
  scribal-hand evidence. Status: `TO_AUDIT`. Imaging is LB-only enrichment → LB-only sensitivity, never a
  transfer-critical feature.
- Standard corpus editions / lexica (for the **gold role labels** only) → **EVALUATION_ONLY** (§VI).

## Gold-label backbone

The **role/schema gold labels** (§VI) derive from the deciphered Linear B lexicon (which lemma is a toponym,
personal name, commodity, etc.). These are ground truth for *evaluation only* and live behind the firewall;
they never enter the model-visible layer.

## Verdict

DĀMOS is sufficient as the LB backbone (corpus coverage, series, site, chronology, scribe, structure,
numerals, logograms). The one non-trivial engineering requirement is the **de-phoneticising ingest**
(transliteration → opaque sign-IDs) — feasible via the existing Unicode B-number parse. LiBER/PA-I-TO are
enrichments, not blockers, and their LB-only features stay out of the transfer-critical set.
