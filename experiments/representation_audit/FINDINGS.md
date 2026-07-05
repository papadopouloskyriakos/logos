# Representation audit — transcription-uncertainty recon + sensitivity (READ-ONLY)

**Date:** 2026-07-05. **Isolated scratch pass.** Reads corpus + code read-only; writes ONLY to
`experiments/representation_audit/`. Nothing under `paper/`, no prereg, no deposited artifact, no
running sweep touched. Findings only — no manuscript edit is implied by anything below.

## Phase-1 gate: **Y (executable).** The corpus retains a real, documented transcription-variant
signal (allograph families, undeciphered `*NNN` markers, damage brackets, three pre-built inventory
treatments), so sensitivity runs are meaningful — they are in Phase 2.

---

## 1. Corpus source path + format + one verbatim record

- **Loaders (public code):** `scripts/corpus_io.py` (→ `corpus/silver/inscriptions.json`, flat),
  `scripts/corpus_io_structured.py` (→ `corpus/silver/inscriptions_structured.json`, with
  segmentation), `scripts/inventory/build_ontology.py` (→ `signs_ontology.json` +
  `inventory_syllabograms_{raw,conservative,exploratory}.json`).
- **Bronze source (gitignored):** the lineara.xyz `items_analysis/inscriptions.json`
  `transliteratedWords` field; a separate Younger bronze (`corpus/bronze/younger_lineara/`).
- **Format:** JSON list, 1341 inscriptions. Verbatim (`inscriptions_structured.json`, HT1):
```json
{ "id":"HT1","site":"Haghia Triada","context":"LMIB","support":"Tablet",
  "words":[["QE","RA₂","U"],["KI","RO"],["ZU","SU"],["DI","DI","ZA","KE"],["KU","PA₃","NU"],["A","RA","NA","RE"]],
  "stream":[{"t":"word","signs":["QE","RA₂","U"]},{"t":"div"},{"t":"nl"},
            {"t":"word","signs":["KI","RO"]},{"t":"num","v":197}, ...],
  "signs":["QE","RA₂","U","KI","RO","ZU","SU","DI","DI","ZA","KE","KU","PA₃","NU","A","RA","NA","RE"] }
```

## 2. Annotation present/absent (with real on-disk examples)

| dimension | status | evidence |
|---|---|---|
| **Uncertain / undeciphered signs** | **PRESENT** | GORILA `*NNN` series kept as distinct tokens (`*307`, `*118`…); ontology `class="syllabogram-Aonly"`, `value_hypothesis="undeciphered … no established value"`; 72 such canonical signs. |
| **Damage / lacuna / restoration** | **PARTIAL** | Bracket markers survive **inside compound tokens**: `KU+[ ]`, `HIDE+[?]`, `QA2+[?]+PU`, `]TU+RO`, `TE+RO[`, `WI+ZE[`. But the normalizer keeps only tokens with a latin letter (`is_sign_token`), so **standalone** lacuna/vestigia positions are dropped — damage is retained only where fused to a readable sign. |
| **Multiple / variant readings per position** | **ABSENT** | No position carries alternative readings (no `A/B` or option lists); one token per position after `-`-splitting. |
| **Allograph vs canonical** | **PRESENT (3-layer)** | Ontology encodes `diplomatic_token → canonical_sign_id → allograph_family`. Subscripted allographs (RA₂/PA₃/TA₂/PU₂) kept **distinct** in conservative, **merged** in exploratory. |
| **Provenance** | **PRESENT (per inscription)** | `site`, `context` (e.g. LMIB), `support` (Tablet) on every record; per-token `examples`+`frequency` in the ontology. No per-token confidence score. |

## 3. Cross-source disagreement + prior audit

- **Cross-source handling:** AB-vs-A-only is **read straight off the token** by the GORILA/SigLA
  editorial convention (bare CV/V matching the Linear-B syllabary → AB; literal `*`-prefix + GORILA
  number → A-only), verified against `syllables.txt`. It is an editorial convention, **not** a
  silent statistical resolution. The silver corpus derives from a single primary bronze
  (lineara.xyz); a second source (Younger) is retained separately, not merged position-by-position.
- **Prior audit — CITE, not redo:** `docs/findings/2026-06-30-inventory-cleaned.md` **already
  characterized transcription-treatment sensitivity of the information-floor statistics.** Confirmed
  from the on-disk inventories (V=92/88/131, N=5171/5171/5117 match its table exactly). Its table:

  | stream | N | V | H_rate | D | U(P=30) |
  |---|---|---|---|---|---|
  | conservative (PRIMARY, = paper V_syllabic) | 5171 | 92 | 4.467 | 2.057 | 219 |
  | exploratory (allographs merged) | 5171 | 88 | 4.467 | 1.992 | 217 |
  | raw syllabogram | 5117 | 131 | 4.432 | 2.602 | 247 |
  | raw silver (old, uncleaned) | 5792 | 259 | 4.330 | 3.687 | 345 |

  **Its load-bearing result — `U ≪ N` on EVERY stream** (U 217–345 vs N ≈ 5.1–5.8k) — is **robust to
  transcription treatment**; and that unicity/identifiability claim is already **withdrawn** in the
  paper (§9.4). So V/U/H/D sensitivity is settled; Phase 2 covers the stats it did *not*:
  `distinct_words` and `mean_signs_per_word` (the sufficiency-locator anchors).

## 4. Phase-1 gate verdict: **Y — executable.**

---

## 5. Phase 2 — sensitivity of existing statistics (`sensitivity.py` → `sensitivity_results.json`)

**Treatments (each real & documented, per Phase 1):** `raw` (diplomatic token) · `conservative`
(ontology `canonical_sign_id`, allographs distinct — the **paper primary**) · `exploratory`
(`allograph_family`, allographs merged) · `excl_unident` (conservative minus the undeciphered
`*NNN` class). **Statistics (all pre-existing `LINEAR_A`/`benchmark_stats` definitions):** N sign
tokens, V distinct signs, word tokens, **distinct word-forms** (=paper `distinct_words`),
**mean signs/word** (=paper `mean_signs_per_word`). Syllabogram stream; baseline = conservative.

| statistic | raw | conservative | exploratory | excl_unident |
|---|---|---|---|---|
| N sign tokens | 5117 | **5117** | 5117 | 4836 |
| V distinct signs | 175 | **131** | 123 | 59 |
| word tokens | 2595 | **2595** | 2595 | 2497 |
| **distinct word-forms** | 1062 | **1021** | 1007 | 923 |
| **mean signs/word** | 1.972 | **1.972** | 1.972 | 1.937 |

**Δ vs conservative:** N `+0/+0/−5.5%` · V `+33.6/−6.1/−55.0%` · word-tokens `+0/+0/−3.8%` ·
distinct-words `+4.0/−1.4/−9.6%` · mean-signs `+0/+0/−1.8%`.

**Stable vs moved:**
- **STABLE under the genuinely-plausible ambiguity (allograph merge, conservative↔exploratory):**
  mean-signs (0%), N (0%), word-tokens (0%), distinct-words (−1.4%), V (−6.1%). Under the plausible
  transcription ambiguity, everything is essentially invariant.
- **MOVES only under aggressive treatments:** V under `raw` (+33.6%, ligatures unmerged) and
  `excl_unident` (−55%, dropping all undeciphered signs); distinct-words under `excl_unident`
  (−9.6%). These are deliberately extreme bounds, not the plausible centre.

*(My uncurated `conservative` V=131 = the prior audit's **raw** V, because I map to canonical without
its frequency-threshold curation; the curated V=92/88/131 in §3 is authoritative for V. My
computation confirms the same direction and the same robustness.)*

### Sensitivity verdict: **LOW / LOCALIZED.**
Under the plausible transcription ambiguity (allograph merging — the only genuinely contested axis),
no statistic moves materially (≤ ~6%, most 0%). Large swings appear only under deliberately extreme
treatments (unmerged ligatures; deleting all undeciphered signs), and even there the prior audit's
downstream conclusion (`U ≪ N`) survives on every stream. **Administrative-schema / structure
induction can proceed on the current representation once the freeze lifts; full
palaeographic/uncertainty modelling is NOT a precondition — it is a refinement.**

## 6. Flagged observations on frozen-paper statistics (information only — NO edit implied)

None move **materially** under a plausible transcription. Two lower-severity provenance notes,
flagged for Redrick, changing nothing:

- **`distinct_words = 650` (band 600–700) is a curated/literature anchor, not a corpus count.** A
  direct recompute of distinct syllabogram word-forms from the deposited corpus gives **1021**
  (all-class 1078), ~57% above 650; Younger's curated `lexicon.txt` is the plausible external source
  of the 600–700 figure. This is a **definitional** difference (curated lexicon vs raw segmented
  word-forms), **not** a transcription-sensitivity effect — the corpus recompute moves only
  −9.6%…+4% across treatments, and the 650 anchor is treatment-independent. It does **not** change
  the sufficiency conclusion (the 600–700 band already brackets it; recovery is at-floor across the
  regime). Separately relevant only because this same locator is already under the Exit-B correction.
- **`mean_signs_per_word = 2.3` vs a direct recompute of 1.97** (syllabogram-only; 1.84 all-class) —
  a word/ligature-counting definitional gap, **treatment-stable** (0% across raw/conservative/
  exploratory). `n_sign_tokens = 5792` reproduces **exactly** (all-class N).

## 7. Isolation confirmation

Only `experiments/representation_audit/` was written (`sensitivity.py`, `sensitivity_results.json`,
this file). `paper/`, the prereg, deposited/Zenodo files, and the corpus source are **unmodified**;
the corpus was **not** normalized or "fixed"; the running sweep, scheduler, and watchers were **not**
touched; no network used. `sensitivity.py` imports no worker/sweep module (stdlib only).
