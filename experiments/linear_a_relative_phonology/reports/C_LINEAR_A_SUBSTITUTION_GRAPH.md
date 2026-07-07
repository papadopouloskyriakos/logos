# C4 — Linear A Substitution Graph

**Task C4.** Build the Linear A substitution graph over GORILA word units (edge types: single-sign
substitution, prefix / suffix alternation, optional sign, transposition, allographic candidate),
**weight edges by DISTINCT long-frame / formulaic support** (C3: long ≥3-sign frames are the best
scorer, raw pair count is not), assign **only anonymous relative classes** (`REL_CLASS_01`, …, no
phonetic value), and surface the classes that behave like the **one axis C3 calibrated as
trustworthy** — the **consonant-held / vocalic-alternation** axis, best recovered when **word-final**
(morphophonological, LB AUC 0.744, degree-preserving lift up to 2.5×).

- Engine: `experiments/linear_a_relative_phonology/scripts/c4_la_substitution_graph.py`
- Data: `experiments/linear_a_relative_phonology/data/C_la_graph.json`
- Seed 20260708, deterministic, pure stdlib + repo loader; reuses audited C1/C3 primitives. All
  counts script-generated (Inv. 12).

## Non-circularity (Art. XII)

Graph construction and REL_CLASS formation consume **sign identity, word-frame membership,
long-frame support, and word-final position ONLY**. No phonetic value is ever a model input. The
GORILA / Linear-B-homomorphic `(consonant, vowel)` transliteration is read **afterward, to grade a
flagged benchmark**, and the 5 known LA pure-vowel signs {A,E,I,O,U} likewise grade, never gate.
Every value-graded number below carries the caveat that the homomorphy is the exact channel this
campaign disputes; it **earns no licence** (L2/L3 relative structure only).

## Corpus

3,147 GORILA word tokens / **1,165 types** (984 of length ≥2) over 1,341 documents; 259 distinct
signs, **60 clean syllabograms** (possible phonological slots).

## The graph (word units)

| edge type | count |
|---|---:|
| single_sign_substitution | 2,787 |
| allographic_candidate (subset of subst.) | 7 |
| prefix_alternation | 420 |
| suffix_alternation | 446 |
| optional_sign (medial indel) | 89 |
| transposition (adjacent swap) | 25 |
| **total typed edges** | **3,774** |

**Strong-component structure** (connected components over single-sign substitution): **73
components** over the connected nodes, plus **398** length-≥2 nodes with no substitution edge at all.

| component size | 2 | 3 | 4 | 5 | 6 | 8 | 18 | 20 | 361 |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| # components | 50 | 8 | 5 | 3 | 2 | 2 | 1 | 1 | **1** |

The graph is **one giant component + dust**: a single 361-form component (2,601 substitution edges,
580 tokens) dominates — the administrative `{KU,SA,KI,A,…}-RO / -RA₂` deficit/total family (C1's
`FAM-5aa496eb66`) — and everything else is components of ≤20 forms. This is the expected shape of a
small administrative corpus: one large paradigm of ledger headwords, and a long tail of near-hapax
minimal pairs.

## The sign-substitution graph → REL_CLASSes

Restricting to **clean, non-allographic** sign substitutions licensed by ≥1 **long** (≥3-sign)
frame gives **130 sign edges**. Requiring the C3 promotion rule — **≥2 distinct long/formulaic
frames** — leaves only **12 strong edges**. **The single most-supported LA sign substitution is
licensed by just 3 distinct long frames** (DA/RU, A/DA, A/JA), versus **98** for LB's top
consonant-held swap (JA/JO). The signal the detector fed on in Linear B is almost absent here.

Anonymous classes = connected components of the strong (≥2 long-frame) sign graph, ranked by
aggregate long-frame support then word-final concentration:

| class | signs | edges | Σ long-frame w | word-final frac | within-graph final null (lift, p) | verdict |
|---|---|--:|--:|--:|---|---|
| **REL_CLASS_01** | A DA JA KA MI RU SI TA | 7 | 17 | **0.294** | 0.65×, p=0.79 | **NOT_WORD_FINAL_DOMINANT** |
| REL_CLASS_02 | KU MA SA | 2 | 4 | 0.500 | 1.06×, p=0.67 | WORD_FINAL_BUT_NULL_NOT_BEATEN |
| REL_CLASS_03 | RA RE | 1 | 2 | 0.500 | 1.04×, p=0.51 | UNDERPOWERED |
| REL_CLASS_04 | PA TE | 1 | 2 | 0.500 | 1.04×, p=0.51 | UNDERPOWERED |
| REL_CLASS_05 | KI WA | 1 | 2 | 0.000 | 0.00×, p=1.0 | UNDERPOWERED |

**No REL_CLASS earns `CANDIDATE_CONSONANT_HELD_ANALOGUE`.** The threshold (Σw ≥ 4 **and** word-final
fraction ≥ 0.5 **and** within-graph final null beaten at p ≤ 0.10) is met by none.

The largest, best-supported class **REL_CLASS_01** is the opposite of the calibrated signature: its
strongest edges are the **word-INITIAL A- alternation** (A/DA, A/JA, A/SI, A/KA, A/MI — the frequent
`A-` prefix swapping into other CV signs at position 0), so its word-final fraction (0.294) is
**below** a within-graph null (0.454) — it is word-initial-dominant. Greek inflection lives
word-**final**; LA's most repeated long-frame substitution axis lives word-**initial**.

## The brutal audit (same standard that just refuted WP-A)

**Audit 1 — degree-preserving (Maslov–Sneppen) null, `same_consonant` benchmark enrichment among
top-k weight-ranked sign edges** (×300; benchmark **FLAGGED**, uses disputed homomorphic values):

| top-k | same_consonant obs / null | lift | z | p |
|--:|---|--:|--:|--:|
| 20 | 0.050 / 0.026 | 1.94 | 0.34 | **0.140** |
| 40 | 0.075 / 0.057 | 1.31 | 0.24 | 0.419 |
| 80 | 0.088 / 0.083 | 1.05 | 0.07 | 0.432 |

The `same_consonant` lift decays 1.9× → 1.0× and is **non-significant at every cutoff**. Contrast
Linear B (C3, k=20): lift **2.52×, z=3.82, p=0.007**. The consonant-held enrichment that made the
substitution channel trustworthy on LB **does not reproduce on LA**. `any_phon` and `same_vowel`
are at or below the null throughout (lift ≤ 0.96).

**Audit 2 — value-free permutation: does the weight ranking select WORD-FINAL edges?** (statistic =
mean word-final fraction of the top-k weight-ranked edges; null = shuffle final-fraction labels
across all 130 clean edges, ×2000). This is the **decisive, value-independent** test of the C3
promotion rule.

| top-k | obs mean final frac | null mean | p |
|--:|--:|--:|--:|
| 20 | 0.358 | 0.478 | **0.889** |
| 40 | 0.304 | 0.478 | **0.999** |
| 80 | 0.377 | 0.478 | **0.999** |

**The high-long-frame-support edges are LESS word-final than chance** (p ≥ 0.89). The morpho­
phonological signature that carried LB's 0.744 AUC is **absent — indeed reversed** — on Linear A.

## Secondary structure — productive affixes (indel edges, C3-flagged as affixation-confounded)

Not a REL_CLASS (C3 flagged INDEL as confounded; excluded from the phonological classes), but the
graph does surface **productive one-sign affixes**: prefix **A-** (11 distinct long stems), prefix
**I-** (9), suffix **-JA** (8), medial-optional **DA/TA** (7/6), suffixes **-ME / -RE / -NA** (6).
These are candidate morphological formatives (L3 structure), consistent with the strong word-INITIAL
A- axis above; they carry **no phonetic reading**.

## Verdict

`SUBSTITUTION_GRAPH_BUILT; CONSONANT_HELD_ANALOGUE = NOT_RECOVERED (underpowered + wrong-signature).`

1. **The graph is real and dominated by one administrative alternation family** (361 forms), matching
   C1. That structure is genuine relative organisation of the corpus.
2. **When the ONE C3-trusted component (consonant-held / word-final) is isolated and put through the
   same audit that refuted WP-A, it does not survive on Linear A.** No REL_CLASS earns the analogue
   label; `same_consonant` enrichment is non-significant (lift 1.9→1.0, p ≥ 0.14); and the value-free
   word-final test **refutes** the promotion rule (strong edges are *less* word-final than chance,
   p ≥ 0.89).
3. **Two reasons, both honest:** (a) **No power** — the strongest LA sign substitution is licensed by
   3 long frames vs LB's 98; the repeated formulaic contexts that carry the signal in Linear B barely
   exist at LA scale. (b) **Wrong signature** — the axis that IS strong on LA is **word-initial** (the
   `A-` alternation), structurally opposite to the word-final Greek inflectional slot the calibration
   trusts.
4. **Consequence for the campaign.** The substitution channel's *load-bearing* positive (C3's
   consonant-held axis, AUC 0.744) **does not transfer its diagnostic signature to Linear A** under a
   like-for-like audit. Per guilty-until-proven-innocent, the "not value-blind" claim **cannot yet
   rest on the LA substitution graph**: the surviving object is L2/L3 relative structure (a headword
   paradigm + productive word-initial affixation), not evidence of a recoverable vocalic-alternation
   system. Only a bilingual or ≥3 independent held-out anchors could promote it further; more of the
   same corpus cannot.
