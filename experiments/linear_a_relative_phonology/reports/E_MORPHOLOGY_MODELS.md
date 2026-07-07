# E1 — Anonymous morphology induction (three families) + C4 re-characterization

**Task E1.** Three independent morphology-induction families on Linear A sign-sequences
(GORILA_WORD primary; ENTRY, FORMULA secondary), with a Linear B positive control. Characterizes the
wave-2 C4 "productive word-initial affixation" finding across all three families, deflates it against a
frequency-matched null, and measures cross-family agreement.

Constitution v2.2. Articles III (guilty-until-proven), V (claim layers), VII (search receipt), VIII
(effective-n / multiplicity), XII (no grading by the creating rule). **Highest claim layer L2/L3.
Licences NOT_EARNED. No phonetic value assigned.** Script `scripts/e1_morphology_models.py`; data
`data/E1_morphology.json`; seed 20260708; pure stdlib + read-only corpus loader.

## The three families (all anonymous — every input is a distributional statistic over sign IDs)

| Family | Principle | Inference |
|---|---|---|
| (a) **MDL / Morfessor** | two-part description length: frequent multi-sign sequences stay whole (stems); non-recurrent material is peeled into cheap shared morphs | Viterbi-DP segmentation, EM re-count to convergence |
| (b) **Bayesian DP** | `word = [prefix?] stem [suffix?]`; affix presence ~ Beta-Bernoulli; affix signs & stems ~ Dirichlet-Process cache over a **sign-by-sign base measure** `G0(x)=∏ p_unigram(xᵢ)` — so a whole-word stem and a stem+affix split are equiprobable *under the base* and only the DP cache (rich-get-richer) breaks the tie | MAP hard-EM (iterated conditional modes), collapsed DP predictive |
| (c) **Finite-state paradigms** | Linguistica-style signatures with the **stem-recurrence criterion**: an affix is credited on stem *t* only if *t* is independently attested (free word, or residual of ≥2 words) | exact combinatorial enumeration |

Two earlier Bayesian formulations were **rejected in-session for failing the positive control** (an
append-only methods note, not a silent fix): a Dirichlet-multinomial with a `NONE` symbol, and a soft-EM
mixture — both collapse to the trivial "no morphology" fixed point *even on Linear B*, because a whole
word can always memorise itself as one atomic stem. Only the sign-by-sign base measure (family b above)
removes that degeneracy. **A model is not trusted as a null until it fires on the readable analogue.**

## Positive control — Linear B DĀMOS (13,562 wordforms, known productive inflection)

The SAME three families, on a readable script whose `-JO / -O / -A / -JA` endings are real Mycenaean
Greek inflection (read AFTERWARD to grade recovery — never a model input):

| Family | LB top suffixes recovered | Fires? |
|---|---|---|
| Bayesian DP | **JO 354**, JA 123, TA 115, RO 105, TO 88, WO 88, QE 80, O 78 | YES (π_suffix 0.211) |
| Paradigm | **JO 308**, RO 172, JA 165, TO 163, TA 156, WO 130, NO 124 | YES |
| MDL | POTINIJA, MENA, RIJO, IJO, TERIJA (whole derived words; weak peeling) | WEAK |

Bayesian and paradigm are **validated detectors** (they recover real morphology). MDL under-segments
even LB — expected for a description-length model on a large sign alphabet.

## Linear A results (GORILA_WORD: 3,147 units / 1,165 types / 259 signs; mean length 1.84)

**Top prefixes (distinct-stem productivity):**

| | family (a) MDL | family (b) Bayes | family (c) Paradigm |
|---|---|---|---|
| prefixes | SI 5, A 3, KU 3, KA 2, **I** 2 | **A 43**, **I 17**, U 16, DA 16, DU 15, SI 12 | **A 47**, **I 28**, JA 22, DA 22, KA 21, SI 20 |
| suffixes | NI 4, KA 4, KU 3, TE 3 | **JA 22**, TI 21, RA 19, TA 18, NA 18 | **JA 26**, RA 22, TI 20, RE 19, TE 18 |

- Bayesian π_prefix = 0.145, π_suffix = 0.164 (LA), vs LB 0.203 / 0.211 — **Linear A carries affixation,
  but less than Linear B** (consistent with the wave-2 short-word / underpowered typology).
- MDL segments almost nothing (mean 1.08 morphs/word, 17 stem families) — with 259 signs and mean length
  1.84, the description length rarely pays for a boundary. This is a genuine power statement, not a bug
  (the same MDL fires on LB's longer words).

**Cross-family agreement (top-10 sets):**

| slot | Jaccard MDL–Bayes | MDL–Para | Bayes–Para | 3-way intersection |
|---|---|---|---|---|
| prefixes | 0.176 | 0.333 | **0.538** | **A, I, SI** |
| suffixes | 0.176 | 0.111 | **0.667** | TA, TE |

Bayesian and paradigm — the two validated detectors — agree strongly and both rank **A-** first among
prefixes and **-JA** first among suffixes. MDL is the outlier (under-segmentation).

## Re-characterizing the wave-2 C4 finding, with deflation (Art. VIII)

C4 flagged productive word-INITIAL affixation: **A- (11 stems), I- (9), -JA (8)**. Re-measured here:

**Cross-family productivity of the three C4 affixes** (higher = agrees more strongly):

| affix | MDL | Bayes | Paradigm |
|---|---|---|---|
| A- prefix | 3 | 43 | 47 |
| I- prefix | 2 | 17 | 28 |
| -JA suffix | 0 | 22 | 26 |

(Absolute counts exceed C4's because the paradigm criterion here credits any independently-attested
residual stem, where C4 required ≥3-sign long-frame support; this is a looser, purely paradigmatic
productivity — a definitional difference, not a contradiction.)

**Frequency-matched null (200 draws, word-length distribution + sign unigram preserved; Holm across the
10 tests):**

| affix | observed | null mean [95% CI] | p (raw) | p (Holm) |
|---|---|---|---|---|
| **A- prefix** | 47 | 23.9 [16, 32] | **0.005** | **0.050** |
| I- prefix | 28 | 22.1 [15, 31] | 0.080 | 0.716 |
| -JA suffix | 26 | 19.9 [12, 29] | 0.114 | 0.915 |
| U-/E-/O- prefix | 10/5/4 | 8.7/4.3/3.7 | n.s. | 1.0 |
| -RE/-NE/-TU suffix | 19/11/12 | 15.0/7.3/9.1 | n.s. | ~0.9 |
| -SI suffix | 14 | 27.2 [19,37] | 1.0 (below chance) | 1.0 |

**Verdict — PARTIAL_ROBUST.** Of the three C4-flagged affixes, **only A- prefixation exceeds the
frequency-matched null after multiplicity correction** (A- p_raw 0.005, p_Holm 0.050 — borderline at
α=0.05). **I- and -JA are indistinguishable from a frequency artifact** once the null accounts for the
fact that A/I/JA are among the corpus's most frequent signs and the multiplicity of tests is deflated.
The C4 "productive A-/I-/-JA affixation" headline **over-claimed I- and -JA**; the residue is a single
robust anonymous prefix class, A-.

## Other anonymous structure surfaced (paradigm family, GORILA_WORD)

- **305 stem families** (≥2 words sharing a recurrent stem).
- **39 reduplication candidates** — including the real Linear A libation-formula words
  `A-SA-SA-RA-ME`, `JA-SA-SA-RA`, `QA-QA-RU`, `TI-TI-MA`, `KU-KU-DA-RA`, `KI-KI-RA-JA` (adjacent-sign
  reduplication is a genuine, value-free morphological pattern here).
- **Optional-sign (medial slot) classes**: DA (7), TA (6), RA/RU/RI/MA (5) — signs whose medial removal
  yields another attested word.
- **Paradigm cells**: 100 word-initial alternation stems, 107 word-final — anonymous slots where several
  signs alternate on a shared stem (e.g. stem `-ZA` takes {I, MA, ME, PA, RE} initially).

Robustness across segmentations: A- is the top prefix on ENTRY (10) and FORMULA (23) as well; -JA is the
top suffix on FORMULA (9). The signal is not an artifact of the GORILA word tokenization.

## Grading benchmark (READ-ONLY, never a model input — Art. XII)

Top-6 paradigm prefixes are `A, I, JA, DA, KA, SI`: **33% are pure-vowel signs** — i.e. the strongest
anonymous prefix class (A-) coincides with a pure-vowel sign, but the prefix inventory is not
predominantly vocalic. Reported for grading only; pure-vowel identity entered no model. **No phonetic
value is assigned; no transfer licence is earned.**

## Net

Three independent families, one validated on Linear B. On Linear A they agree on a real but modest
morphology: a single robust word-initial prefix class **A-** (survives a frequency-matched, multiplicity-
corrected null), plus rich but frequency-consistent paradigmatic substrate (stem families, reduplication
incl. the libation words, optional-sign and alternation cells). **The wave-2 C4 claim is corrected from
three productive affixes (A-, I-, -JA) to one (A-);** I- and -JA do not survive deflation. This stays at
L2/L3 anonymous relative structure — no values, no licences.
