# E — Full Formula Interpretation audit (Task E)

**Prereg:** `DI_MINO_EXACT_CLAIM_V1` (sha `8b098a4c`). **Constitution:** v2.2. **Seed:** 20260708.
**Generator:** `scripts/E_full_formula_audit.py` → `data/formula_claim_matrix.json`.
**Source:** `corpus/silver/inscriptions_structured.json` (GORILA-derived silver; edition = *GORILA*,
Godart & Olivier 1976–1985, digitized via SigLA). All counts script-generated (invariant 12).
**Non-circular:** conventional Linear B values grade benchmarks ONLY; the sole LA-side model input under
test is `*301`'s value. No LLM graded any claim; verdicts are mechanical per the frozen prereg.

Scope: every claimed word/morpheme in the public formula translation — IOZa2 line 1:
`A-TA-I-*301-WA-JA · JA-DI-KI-TU · JA-SA-SA-RA-ME · U-NA-KA-NA-SI · I-PI-NA-MA · SI-RU-TE · TA-NA-RA-TE-U-TI-NU · I`.

---

## A. Headline — the "full formula translation" is one novel parameter wearing a formula

| quantity | measured |
|---|---|
| formula words in IOZa2 line 1 | **8** |
| words with a **published** morpheme table | **1** (only `A-TA-I-*301-WA-JA`, Figure 1) |
| words **SOURCE_BLOCKED** for any lexical/morphological reading | **7** |
| total signs across the 8 words | **35** |
| **novel parameters** (signs without a conventional LB anchor) | **1** (`*301`) |
| conventional Linear-B-transfer signs (`literature_match`, score 0) | **34** |
| novel fraction of the whole translation | **2.86 %** |

**The entire published "decipherment of the formula" reduces to ONE free parameter (`*301=/na/`).** The
other 34 signs are standard GORILA/Ventris shared-syllabary readings — recording them is not discovery
(barred from scoring). Only word 1 carries a published morpheme table; **words 2–8 are transliterated but
carry no published lexical or morphological analysis** and return `SOURCE_BLOCKED` (per prereg §Extended
`SOURCE_BLOCKED` protocol — recorded, never collapsed into the H1–H6 core verdict).

---

## B. Per-component claim matrix

Full machine-readable detail (per-sign class, conventional value, novelty, prior literature, alternatives,
independent prediction, status) is in `data/formula_claim_matrix.json`. Summary:

| # | word (slot) | attest / sites | novel params | Di Mino published reading | prior literature (NOT Di Mino) | status |
|---|---|---|---|---|---|---|
| 1 | `A-TA-I-*301-WA-JA` (invocation-verb) | 11 / 5 | **1** (`*301`) | Fig.1: 1cs `A-` + tG `TA-` + stem-vowel `I` + root `n-w-y` "dwell" | canonical LF word 1 (Duhoux, Davis, Younger); `*301` value long open | UNDER_TEST (family A/C) |
| 2 | `JA-DI-KI-TU` | 1 / 1 | 0 | **title only** — "Ya Diktu" (no morpheme table) | "Diktu"~Mt Dikte floated generally | SOURCE_BLOCKED |
| 3 | `JA-SA-SA-RA-ME` | 7 / 5 | 0 | none | dominant prior: theonym "Asasara(-me)" mother-goddess (Hiller, Duhoux) | SOURCE_BLOCKED |
| 4 | `U-NA-KA-NA-SI` | 4 / 3 | 0 | none | standard LF frame word; no consensus gloss | SOURCE_BLOCKED |
| 5 | `I-PI-NA-MA` | 6 / 5 | 0 | none | standard LF frame word; no consensus gloss | SOURCE_BLOCKED |
| 6 | `SI-RU-TE` | 7 / 5 | 0 | none | standard LF closing word; no consensus gloss | SOURCE_BLOCKED |
| 7 | `TA-NA-RA-TE-U-TI-NU` | 1 / 1 | 0 | none | hapax tail | SOURCE_BLOCKED |
| 8 | `I` | 39 / 7 | 0 | none | ubiquitous single-sign word | SOURCE_BLOCKED |

Note the recurrence figures (cols 3) are **value-free** — attestations of the exact graphic word type across
the whole silver corpus, computed with no phonetic values. They are structural facts (L3) that hold whether
or not any reading is correct, so they cannot be evidence *for* the readings.

---

## C. The homophony red flag — `/na/` is already spelled `NA`

| sign | tokens in corpus |
|---|---|
| standard `NA` (AB06 = /na/) | **158** |
| `*301` | 31 |

`/na/` is already densely and unambiguously written by the standard `NA` sign — **158 tokens, including three
times inside the very same IOZa2 line** (`U-NA-KA-NA-SI` ×2, `I-PI-NA-MA`, `TA-NA-RA-TE-U-TI-NU`). Assigning
`*301` a **second** `/na/` value posits a true CV homophone in a syllabary whose whole design pressure runs
the other way (Aegean linear scripts strongly avoid homophonous syllabograms). A scribe intending `/na/` had
`NA` ready to hand and used it 158 times; there is no distributional reason to also spell `/na/` with `*301`.
This is an **independent structural argument against `*301=/na/`** that does not even require the held-out
gate — it falls straight out of the formula the claim is built on.

---

## D. Does the COMPLETE system predict formula-level structure? (vs neutral models)

The mandate asks whether the complete reading system predicts word order / recurrence / regional variants /
object type / formula position / recipient structure / grammatical dependencies better than neutral
structural models. Two obstacles, both fatal to awarding credit:

**(1) There is no "complete system" to test.** Only word 1 (and within it only `*301`) is specified. Words
2–8 have no published reading, so the system makes **no** cross-word prediction to grade.

**(2) Every structural regularity that IS observable is value-free — recovered without any reading.**

| system-level feature | who actually predicts it | credit to the readings? |
|---|---|---|
| **word order** | FIXED_TEMPLATE (frozen-formula) model — measured order-consistency **12/12 = 1.00** across LF carriers with ≥2 slots, using value-free marker matching | **NO** — reproduced, not improved |
| **recurrence** | value-free type counting (reports 03/04) | NO |
| **regional variants** (`WA-JA`~`WA-E`, `A-`~`JA-`) | structural alternation (report 04 §B/§F) | NO — no reading needed or predicted |
| object type | all carriers are stone libation vessels; nothing to predict | SOURCE_BLOCKED |
| formula position | value-free structural slot (report 03 §E); an L3 role, earns no phonetic/lexical licence | NO |
| recipient structure | requires parsing `JA-SA-SA-RA-ME` etc. | SOURCE_BLOCKED |
| grammatical dependencies | requires cross-word syntax beyond word 1 | SOURCE_BLOCKED |

The word-order test is the sharpest: the libation formula is a **frozen template**, so a neutral model with
**zero phonetic input** predicts the slot order perfectly (12/12). Di Mino's Semitic morphology can at best
reproduce this; reproducing a template that a value-free baseline already nails is not evidence for the
phonetic values. Consistent with reports 02 (circularity e2→e3→e4) and 04 (the `*301-WA-JA` root cut is the
single most *anti*-boundary internal position, fwd-entropy 0.00, and the value-free segmenter cuts *after*
`*301`, splitting it from `WA`).

---

## E. Discovery-firewall accounting (which claims could ever count)

- **34/35 signs** = `KNOWN_AB_TRANSFER` → `literature_match`, score 0. Reproducing conventional GORILA
  transliteration is explicitly **not** discovery and is barred from the gate.
- **1/35 signs** = `*301` = `LINEAR_A_ONLY_NEW` → the sole thing that could score, and only if it clears the
  H1 held-out `S_morph`/`S_lex` gate after `E[max_Neff]` deflation (logged value × lexeme × segmentation
  trials, and against the author's own stated ~10⁵ simulations). Its root consequence (`n-w-y`) is a
  deterministic artifact of the value (H2 scores 0 if it is just `na-wa-ya` vowel-stripping — it is).
- **Words 2–8**: `SOURCE_BLOCKED`. The 40-sign table, 408-term lexicon, and "Ya Diktu" manuscript are not
  public (report F / report 01), so no morpheme table exists to audit for any word past the first.

---

## F. Verdict for Task E

`FULL_FORMULA_VERDICT = ONE_NOVEL_PARAMETER + SOURCE_BLOCKED_REMAINDER`.

The publicly-adjudicable "full formula translation" is **98 % conventional Linear B transliteration and 2 %
(one sign) novel hypothesis**. No component beyond word 1 has a published reading to test; every one returns
`SOURCE_BLOCKED`. No system-level regularity (word order, recurrence, regional variation) requires or is
improved by the phonetic readings over neutral structural models — word order is a frozen-template fact
recovered value-free at 12/12. And the one novel parameter faces an independent structural objection from the
formula itself: `/na/` is already written 158× by the standard `NA` sign, three times in the same line, so
`*301=/na/` posits a costly homophone. Task E therefore supplies **no** held-out morphological support for the
claim beyond what family A/C adjudicate for `*301` alone, and adds one fresh disconfirming datum (homophony).
This does not by itself decide the core verdict (that is family A/C + the frozen `DI_MINO_CORE_VERDICT` rule);
it removes the "whole coherent formula" impression by showing the formula's coherence is entirely the
value-free template, not the decipherment.
