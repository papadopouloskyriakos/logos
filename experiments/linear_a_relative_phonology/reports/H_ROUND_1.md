# H1 — Candidate Round 1: relative-class-constrained family models

**Task H1** · Constitution v2.2 (Art. III guilty-until-proven, V claim layers, VII search receipt,
VIII effective-n/multiplicity, XII no grading by the creating rule, XV transfer licences) · seed
`20260708` · as_of `2026-07-07`.

- Prereg (frozen before run): `preregistrations/H_round1_prereg.json`
- Script: `scripts/h1_candidate_round1.py` (reuses the **audited** Foundry null machinery
  `candidate_round1.py` — imported, not re-run: `build_family_predictions`, `expand_phonemes`,
  `word_matches`, `score_corpus`, `shuffle_within`, `random_lexicon`, `sample_lb_lengthmatched`)
- Data: `data/H1_round1.json` (+ `data/candidates_v2/H1_round1.json`) · Manifest:
  `manifests/H1_round1_manifest.json`
- Highest claim layer reached: **L2/L3**. Transfer licences **NOT_EARNED**. No phonetic value
  assigned to any Linear A sign or class.

## VERDICT: `AT_END_TO_END_NULL`

No serious candidate family beats the multi-family end-to-end null. The one raw match that clears the
decisive nulls before correction (**SEM** West Semitic, decisive FWER 0.0149) is a **single-lexeme
artifact** — the famous `KU-RO` "total" — that fails Holm (adj p **0.0745**) and collapses completely
under leave-one-lexeme-out (drop `kull` → match rate **0.0**, decisive p **1.0**). The family with the
highest raw match rate (**TYR** Tyrsenian, 0.073) sits **inside** the same-structure random-lexicon
band (real percentile p **0.213**; random-prior z 0.97) — pure Linear-A word-shape typicality, not
lexical fit. The unrelated negative-control real language (**FIN** Finnish) and the agnostic random
control (**CTRL**) both sit at the null and do **not** clear the bar. Honest expectation confirmed.

---

## 1. Held-out target and non-circularity

| | value |
|---|---|
| Held-out unit | GORILA multi-sign **syllabic** word tokens (`t=='word'`, ≥2 signs, all signs in the 59-value AB syllabary) |
| n tokens / types / sites | **1074 / 763 /** multi-site |
| Wrong-language null corpus | DĀMOS Linear B multi-sign wordforms, length-matched (n = 24,447) |

Family predictions are derived from **external** candidate-language lexicons expanded through a **fixed**
A↔B script-borrowing correspondence; **no** Linear A statistic informs any family's phonemes or
correspondence. Known LB values expand phonemes and serve as the wrong-language null only — never read
off Linear A. The D5 anonymous classes grade for the record only (Art. XII).

## 2. The relative-class constraint is value-blind and family-independent (D5)

Every AB-based family reads a given LA sign with the **same** conventional syllabic value (`KU` is /u/
for all of them). So the D5 K=2 anonymous partition's agreement with the family-implied vowel/CV
labelling is **identical across all families** and equals the frozen D5 benchmark:

| D5 K=2 partition vs | adjMI | perm-p | reads as |
|---|---|---|---|
| vowel identity | 0.038 | **0.120** | NULL (recomputed here, 50 overlapping signs) |
| C/V split | 0.022 | **0.155** | NULL |

**Consequence (recorded in the prereg):** the anonymous relative classes cannot break the symmetry
between candidate families and neither admit nor exclude any AB-based family. Admission therefore rests
on chronology, geography, the A-prefix morphology (E1/E3), the formula grammars (E2), the anchor
evidence (G), and CV-syllabary structural fit — all itemised per family in the prereg's `admission`
blocks. This is exactly the F4 finding (relative classes are real L2 structure but value-blind) carried
into the candidate round.

## 3. The five models

| model | designation | admission highlights |
|---|---|---|
| **SEM** West/Common Semitic (Gordon/Rendsburg) | SERIOUS | E2-strong (`kull`→`KU-RO` total); but codas/clusters spell poorly in an open CV syllabary; no productive `a-` prefix |
| **ANA** pre-Greek Anatolian/Luwic (Palmer/Finkelberg) | SERIOUS | chrono/geo PASS (Aegean-Anatolian contact, `-ssa` substrate); E2-weak on KU-RO/KI-RO |
| **TYR** Tyrsenian/Etruscan-related (Facchetti–Negri) | SERIOUS | Aegean pre-IE isolate; CV-tolerant; E2-weak; direct attestation absent |
| **FIN** Finnish/Uralic | UNRELATED NEG-CONTROL | chrono/geo FAIL (impossible for MBA Crete); highly CV/open — a fair worst-case shape-typicality control |
| **CTRL** agnostic random lexicon | AGNOSTIC CONTROL | not a language; the null floor |

## 4. Results — scored vs the end-to-end null battery

Decisive FWER = `max(p_W, p_R)` (must beat BOTH the wrong-language-LB null **and** the random-prior
null); Holm step-down across the 5 families; LOO worst-case; random-lexicon calibration.

| model | eff_n | real match rate | matched | p_S | p_W | p_R | decisive | **Holm** | **LOO worst** | clears? |
|---|---|---|---|---|---|---|---|---|---|---|
| SEM | 19 | **0.0382** (41/1074) | KU-RO family | 0.005 | 0.005 | 0.0149 | 0.0149 | **0.0745** | **1.000** | **NO** |
| ANA | 6 | 0.0047 | 5 types | 0.309 | 0.0995 | 0.0348 | 0.0995 | 0.398 | 0.378 | NO |
| TYR | 14 | **0.0726** (78/1074) | 78 A-/‑na forms | 0.085 | 0.005 | **0.1592** | 0.1592 | 0.478 | 0.443 | NO |
| FIN (neg-ctrl) | 11 | 0.0009 | 1 type | 0.821 | 0.915 | 0.702 | 0.915 | 1.000 | 1.000 | NO |
| CTRL (agnostic) | 12 | 0.0028 | 3 types | 0.891 | 0.527 | 0.393 | 0.527 | 1.000 | 0.871 | NO |

`clears_calibrated` (serious): **none**. `ctrl_agnostic_cleared_raw_bar`: **False**.
`negctrl_FIN_cleared_raw_bar`: **False**.

### 4.1 SEM is one famous lexeme (`KU-RO`), then nothing — the single-anchor trap

Leave-one-lexeme-out isolates the entire SEM signal to `kull`:

| dropped lexeme | sub-rate | decisive p |
|---|---|---|
| **kull** (all/total) | **0.000** | **1.000** |
| semen / yayin / adon / ‑atu / ‑anu | 0.0382 (unchanged) | ≤0.015 |

All 41 SEM matches are `KU-RO` / `KU-RA` / `KU-RE`; the other five lexemes contribute **zero** unique
held-out matches. This is the Egyptian-channel discipline verdict again: a single celebrated
administrative equation ("total") survives the raw decisive nulls, but the family predicts **no other**
held-out Linear A form, so it fails Holm (0.0745) and dies at LOO (1.000). The `KU-RO` reading is not
evidence for Semitic; it is one shortcut term shared by any accounting tradition.

### 4.2 TYR has the highest raw match — and it is pure shape typicality

TYR reaches the top raw match rate (0.073, 78 tokens: `A-NA`, `A-SI`, `A-DU-KU-MI-NA`, `A-RE-SA-NA`, …)
but the **random-prior null reproduces it** (R mean 0.049, p95 0.091; real z = 0.97, p_R = 0.159) and
the real rate sits at **percentile p 0.213** inside the 300-draw random-lexicon band (mean 0.054, p95
0.099). Short CV words plus a `-na` suffix and the frequent `A-` word-initial shape match Linear A
regardless of the specific Tyrsenian lexemes — exactly the LA word-shape-typicality confound the
random-prior and random-lexicon controls exist to absorb. No language-specific fit survives.

### 4.3 The controls behave correctly

- **FIN** (real language, impossible for MBA Crete): decisive p **0.915**, LOO 1.000 — the machinery
  does **not** credit a chronogeographically impossible language. Only 1 accidental match (`SE-SI-TA`).
- **CTRL** (agnostic random): decisive p **0.527** — the decisive bar is **not** trivially passable by
  matched-structure noise. (Both SEM's and TYR's calibration false-clear rates are ≤3.3%, so the bar
  itself is specific; SEM fails on Holm+LOO, not on a leaky bar.)

## 5. What is and is not determined

- **Not determined (all NULL):** no candidate family — Semitic, Anatolian/Luwic, or Tyrsenian — predicts
  held-out multi-sign Linear A words beyond a same-structure random lexicon. No phonetic value, vowel,
  consonant, or language affiliation is assigned to any LA sign or class.
- **Determined (for the record):** (a) the D5 relative classes are value-blind and family-independent
  (K2-vs-vowel p 0.12), so they cannot arbitrate between families; (b) the only raw-clearing signal is
  the single `KU-RO` "total" equation, which fails Holm + LOO; (c) the highest raw match (TYR) is
  Linear-A word-shape typicality fully absorbed by the random-prior/random-lexicon controls; (d) the two
  controls sit at the null, confirming the bar is neither leaky nor credits impossible languages.

## 6. Verdict and next step

```
H1_ROUND_1: AT_END_TO_END_NULL
  - 0/3 serious candidate families GENUINE (Holm-adjusted decisive FWER >= 0.05 for every family,
    or LOO-fragile single-lexeme, or inside the random-lexicon band).
  - SEM raw-clears (decisive 0.0149) on KU-RO alone -> Holm 0.0745, LOO-worst 1.000 (single-lexeme).
  - TYR highest raw match 0.073 -> random-lexicon percentile p 0.213 (shape typicality).
  - Negative-control FIN and agnostic CTRL do NOT clear (decisive 0.915 / 0.527).
  - Relative classes (D5) value-blind and family-independent: no admission discrimination.
```

Consistent with the whole campaign: internal relative structure is real (L2) but value-blind, and no
value-bearing family survives the multi-family end-to-end null. Transfer licences **unchanged: NONE**
(Art. XV); no absolute value assigned. **Next task: H2 (anchor-constrained family/isolate models)** —
per the ledger, the round continues (no ending on one null); a GENUINE result there would still require
held-out reading success + cross-site survival before any L5+ wording.

**Compliance (Art. XXII):** prereg frozen before run; predictions external to LA (Art. XII honoured);
multiplicity Holm-corrected across 5 families (Art. VIII); effective_n reported per family (Art. VIII);
decisive nulls + LOO + random-lexicon calibration run; controls included; append-only; no licence bypass
(Art. XV).
