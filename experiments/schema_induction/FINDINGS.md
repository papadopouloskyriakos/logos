# Administrative-schema induction — EXPLORATORY / DESCRIPTIVE (isolated scratch)

**Date:** 2026-07-05. **STATUS: exploratory / descriptive consistency evidence — NOT gate-validated**
(same status as the 4/4 clean cross-script pins). A claimable result needs a separate
**pre-registered post-correction run** (+ a fraction/glyph re-ingest for the excluded tablets).
Reads corpus read-only; writes ONLY to `experiments/schema_induction/`. §2 Exit-B hard stop, `paper/`
freeze, Phase B (168/168) all in force; sweep untouched; no worker/sweep imports; no network.

Core question: does the administrative structure reconcile from **structure alone (no phonetics)**,
above a permutation null? **Yes — 29–35% exact vs a 0.5% null.**

## 1. Phase 1 — verified structure (not assumed)

- **num / logogram / KU-RO confirmed:** 1276 `num.v` integers (1–3000); 629 logogram occurrences
  (OLE/GRA/CYP/VIN/VIR…); `KU-RO` 37×, `KI-RO` 16×.
- **ACTUAL KU-RO→total layout (from data, quantified over 37 KU-RO):** the total is the `num`
  **immediately following KU-RO on the same line** in **29**; after **one** intervening commodity
  sign in **6** (e.g. `HT39 KU-RO *414+A 100`); **no** same-line number in **2** (e.g. HT40, total
  lost); the total itself carries a fraction in **5** (e.g. `HT13 KU-RO 130 ¹⁄₂`). → **35/37 (95%)
  KU-RO carry a usable total.** Reconciliation is **section-based** (a KU-RO sums entries since the
  previous KU-RO/KI-RO boundary — verified: HT88's `KU-RO 6` sums its post-KI-RO group, not the
  whole tablet). **Gate: PASSED** — the KU-RO→number relationship is a usable signal.
- **LB positive control — DEFERRED (present but not comparable):** `corpus/bronze/linearb/damos/
  items.jsonl` (5840 items; 177 with `to-so`/`to-sa`) holds tablet transcriptions in a **raw-text
  `item.content` field, not tokenized** like the LA corpus, and LB quantities are **metrogram-graded
  (S/V/Z → non-integer)**, with many `to-so` lines broken (`to-so-[`). Parsing it is an
  out-of-scope re-ingest and it is not a clean integer analog → **cannot run cleanly this pass;
  proceeded with TEST + NULL only** (not fabricated).
- **Partition:** 34 KU-RO tablets → **24 integer-only** (reconcilable), **10 fraction-bearing
  EXCLUDED** (HT9a/13/27a/46a/89/94a/100/104/123+124a/b — fractions are unparsed raw strings).

## 2. Entry structure — (commodity, numeral) adjacency

**82.5%** of the 1276 numerals have a **word immediately before** (the atomic entry
`word → quantity`); **28.1%** a **logogram** specifically (the rest are syllabic-word entries —
personnel/toponym counts, e.g. `A-RU-RA 3`). Deviations: standalone numerals (headers, running
totals, sub-counts) and numerals after unparsed glyph/fraction tokens.

## 3. Reconciliation — three-way (the core test)

| stream | exact-match | rate |
|---|---|---|
| **LA (test), all integer-only sections** | 7 / 24 | **29.2%** |
| **LA (test), clean subset (≥1 parsed `num` entry)** | 7 / 20 | **35.0%** |
| **NULL (totals permuted across sections, N=2000)** | — | **0.54% mean, 4.17% max** |
| **LB positive control** | — | **DEFERRED (see §1)** |

**LA reconciliation is ~55–65× the permutation null** → the administrative structure reconciles from
structure alone, far above chance. The 7 clean exact matches are non-trivial sums:
`HT11b 180=180 (5 entries) · HT85a 66=66 (7) · HT9b 24=24 (7) · HT117a 10=10 (10) · HT88 6=6 (6) ·
HT94b 5=5 (5) · HT25b 52=52 (2)`.

**Why not higher (honest):** the misses are **not** small arithmetic errors (within±2 is only 33.3%,
barely above exact) — they are dominated by (a) **unparsed-quantity tablets** (HT67/74/116b/25b-2nd:
quantities live in untransliterated glyph `𐝫` or fraction tokens → `sum=0`, excluded from the clean
subset); (b) **multi-section tablets** my first-pass sectioniser handles crudely; and (c) genuine LA
non-reconciliation (damage / scribal — well attested epigraphically). The ceiling here is **ingest
completeness + parser sophistication, not absence of structure** — the null proves the structure is
real.

## 4. Induced template + commodity inventory (descriptive)

**Template (measured conformance):** `heading? → (commodity/word × quantity)+ [→ KI-RO deficit group]
→ KU-RO total`. Entry conformance 82.5% (word→num); section-total conformance 29–35% exact (≫ null).

**Commodity inventory + quantity distribution** (typed logograms, n = #entries, median/max quantity):

| commodity | n | Σ qty | median | max |
|---|---|---|---|---|
| OLE (oil) | 88 | 723 | 4 | 100 |
| GRA (grain) | 85 | 5051 | 20 | 976 |
| VIR (men) | 34 | 1521 | 20 | 235 |
| VIN (wine) | 28 | 507 | 6 | 104 |
| CYP (cyperus) | 27 | 128 | 3 | 23 |
| OLIV (olives) | 20 | 324 | 13 | 93 |
| HIDE | 11 | 2446 | 120 | 941 |

`KI-RO` (deficit/owed) appears **16×** — handled as a section boundary (its group is a separate
deficit block, not folded into the KU-RO grand total).

## 5. Isolation
Only `experiments/schema_induction/` written (`reconcile.py`, `reconcile_results.json`, this file).
`paper/`, prereg, Zenodo, corpus source, and the running sweep unmodified; corpus not normalized; no
re-ingest, no fraction parsing; no worker/sweep imports; no network.

## 6. Explicit status + what a claimable version needs
**EXPLORATORY / DESCRIPTIVE — consistency evidence, not a validated result.** A claimable version
needs: (1) a **pre-registered** run (prereg → external timestamp → one-shot), executed
**post-Exit-B-correction**; (2) a **fraction + glyph re-ingest** to bring the 10 fraction-bearing and
the unparsed-quantity tablets into exact reconciliation; (3) a proper **LB (DĀMOS) positive control**
via a `content`-parse handling metrograms; (4) a more careful **sectioniser** for multi-section
tablets. The 29–35%-vs-0.5% gap here is the reason such a pre-registered run is worth doing — it is
not itself the claim.
