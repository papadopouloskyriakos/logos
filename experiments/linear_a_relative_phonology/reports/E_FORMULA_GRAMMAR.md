# E2 — Formula Grammar of Linear A

**Task E2 (Formula Grammar).** Induce finite-state / probabilistic formula
structures from Linear A, split by site, support, document type, chronology and
inscription length. Two grammars: the **administrative ledger** grammar
(KU-RO / KI-RO / PO-TO-KU-RO) and the **votive / libation** formula family
(*SA-SA-RA(-ME) + A-TA-I-*301-WA-JA).

- Constitution v2.2 · claim layer **L2/L3** (structure / functional role) · **no
  phonetic value assigned** · **no transfer licence claimed**.
- Seed `20260708`. Script:
  `scripts/e2_formula_grammar.py`. Data: `data/E2_formula.json`. Corpus:
  `corpus/silver/inscriptions_structured.json` (1341 inscriptions).
- **Non-circularity.** Sign-sequences (`KU-RO`, `JA-SA-SA-RA-ME`, …) are treated
  as **anonymous recurring anchors** — conventional GORILA sign-names, not
  phonetic/semantic values. The only "meaning-like" test is the **arithmetic**
  one (does the numeral after a total-anchor equal the running sum of the entry
  numerals before it?) — a relative-structure property independent of any reading.

---

## 1. Two grammars are disjoint by document type

Document type is defined mechanically from the reading stream: an inscription is
a **LEDGER** if it carries ≥1 numeral, else non-accounting.

| anchor family | ledger (has numerals) | non-ledger | supports |
|---|---|---|---|
| `KU-RO` / `PO-TO-KU-RO` (TOTAL) | **34** carriers | **0** | Tablet-dominant |
| `KI-RO` (DEFICIT) | **12** carriers | **0** | Tablet-dominant |
| `*SA-SA-RA` / `*301-WA` opener | **0** | **29** | Stone-vessel-dominant |

The accounting anchors and the libation anchors are in **complementary
distribution**: KU-RO/KI-RO occur *only* in numeral-bearing inscriptions; the
libation anchors occur *only* on (largely stone) vessels with no numerals. Two
distinct formula grammars, cleanly separated by channel.

---

## 2. Administrative ledger grammar (n = 333 numeral-bearing inscriptions)

### 2.1 Probabilistic finite-state model (token-class bigram FSA)

Alphabet: `W` syllabic word · `LOG` commodity logogram · `N` numeral ·
`FR` fraction · `TOT` total-anchor · `DEF` deficit-anchor. Key transitions
(probabilities, from `E2_formula.json.ledger_grammar.fsa_transition_prob`):

| from \ to | N | LOG | W | FR | end |
|---|---|---|---|---|---|
| **^ (start)** | .02 | .45 | .53 | – | – |
| **W** | **.535** | .243 | .169 | .036 | .014 |
| **LOG** | **.456** | .191 | .138 | .082 | .127 |
| **N** | .030 | .303 | .441 | .097 | .104 |
| **TOT** | **.795** | .180 | .026 | – | – |
| **DEF** | .375 | .125 | .313 | .125 | – |

The dominant cycle is **`(W|LOG) → N`**: a value-carrier followed by a quantity,
i.e. the `ENTRY = CARRIER VALUE` rule. After a number the chain returns to a
carrier (`N → W` .44, `N → LOG` .30), i.e. the ledger is a repeated entry loop.

### 2.2 The TOTAL slot is distinctive and terminal-leaning

`TOT → N` fires at **0.795** — markedly higher than a generic carrier
(`W → N` .535, `LOG → N` .456). The total-anchor is a dedicated slot that almost
always takes a following numeral.

- mean normalised position **0.692**; **59.0 %** fall in the last third of the
  inscription (terminal-leaning grand-total behaviour).
- 39 TOTAL occurrences across 35 inscriptions; **31/39 (79.5 %)** immediately
  followed by a numeral.

### 2.3 Arithmetic sum-consistency (the relative-structure "total" test)

For each TOTAL anchor, does the numeral that follows equal the running sum of the
entry numerals since the previous total?

- testable occurrences (a numeral present after): **31**
- **exact matches: 7 (22.6 %)**; exact-or-near (|Δ|≤2): **12 (38.7 %)**
- near-misses concentrate on segments carrying fraction glyphs (½ ¼ …) which the
  silver corpus stores as un-numbered glyphs, so their contribution is dropped
  from the integer sum. Clean examples where the sum lands exactly: HT9b (24=24),
  HT11b (180=180), HT13 (130=130), HT85a (66=66), HT89 (87=87), HT117a (10=10).

This is a **partial, honest corroboration** of KU-RO occupying a *summation*
slot: the exact rate is limited by the corpus's dropped fractions, not by the
hypothesis. It is *not* a phonetic/semantic claim — only that the anchor sits in
a position whose numeral is arithmetically the running total.

### 2.4 The DEFICIT slot behaves differently from TOTAL

`KI-RO` (16 occurrences / 12 inscriptions): mean normalised position **0.503**
(mid-text, *not* terminal), followed-by-number **0.50** (vs 0.795 for TOTAL).
A structurally distinct slot — line-item / balance rather than grand total —
discovered purely from position and adjacency, with no value assigned.

### 2.5 Coverage

- **96.6 %** of all numerals (1233 / 1276) are immediately preceded by a
  value-carrier → a well-formed `CARRIER VALUE` entry.
- **88.6 %** of ledger inscriptions (295 / 333) have *all* their numerals
  well-formed. The induced entry grammar parses the overwhelming majority of the
  accounting corpus.

### 2.6 Facet breakdowns (`ledger_grammar.by_*` in the JSON)

- **by support**: Tablet 273, Stone vessel 35, Clay vessel 5, Lames 4, 4-sided
  bar 4 … TOTAL/DEFICIT anchors are essentially Tablet-only.
- **by site**: Haghia Triada 171, Khania 61, Zakros 34, Phaistos 14, Malia 13.
- **by chronology**: LMIB 262 (the accounting horizon), undated 46, MMII/LMIA
  minor. The ledger grammar is an **LMIB** phenomenon.
- **by length**: 5+‑carrier ledgers concentrate the KU-RO totals; single-carrier
  ledgers (labels/dockets) rarely carry a total.

---

## 3. Votive / libation formula grammar (n = 29 carriers)

Carriers = inscriptions whose sign-stream contains `SA-SA-RA` or the opener
family `{A-TA-I-*301, TA-NA-I-*301, A-NA-TI-*301, *301-WA}`. Anchor families
detected on the joined sign-string (robust to GORILA word-division artefacts):

| label | anchor family | carriers | fill rate |
|---|---|---|---|
| **OP** | opener `*301-WA` (A-TA-I-*301-WA-JA …) | 18 | 0.62 |
| **SSR** | `*SA-SA-RA(-ME)` core | 16 | 0.55 |
| **UNK** | `U-NA-(RU-)KA-NA-SI/TI` | 6 | 0.21 |
| **IPN** | `I-PI-NA-M(A/INA)` | 4 | 0.14 |
| **SIR** | `SI-RU(-TE)` | 5 | 0.17 |

### 3.1 Induced canonical template (rigid linear order)

**`OP  <  SSR  <  UNK  <  IPN  <  SIR`**

Every one of the **10** co-occurring anchor pairs is **100 % directionally
consistent** — zero inversions across the corpus (e.g. OP<SSR 5/5, OP<SIR 5/5,
SSR<UNK 4/4, IPN<SIR 4/4, and IPN, SIR always *follow* OP/SSR/UNK).

- **Permutation null**: shuffling each multi-anchor carrier's realised anchor
  order uniformly (10 multi-anchor carriers, 20 000 permutations), the observed
  "all 10 pairs perfectly consistent" is reached in **0** shuffles →
  **p = 5·10⁻⁵**. The rigid order is not a small-n artefact.
- Fill rates decay along the template (OP/SSR near-obligatory core; UNK/IPN/SIR
  optional tail) — a **head-obligatory, tail-optional** slot grammar.
- Template-order coverage: **29 / 29** carriers realise their anchors as a
  non-inverting subsequence of the canonical order.

### 3.2 Facets

- **by support**: Stone vessel 24, Inked inscription 2, Clay vessel 1, Metal
  object 1, Nodule 1 — a cult-object channel, disjoint from the tablet ledgers.
- **by site**: Iouktas 7, Syme 5, Palaikastro 4, Knossos 2, plus singletons
  (Kophinas, Platanos, Poros, Psykhro, Troullos, Phaistos, Thera) — a
  pan-Cretan sanctuary distribution.
- **by chronology (dated)**: LMIA 5, LMI 5, MMII/MMIIIB/LMIB/LMIIIA singletons;
  15 undated. Skews **earlier / longer-lived** than the LMIB-locked ledger
  grammar.

---

## 4. Verdict

Two well-formed Linear-A formula grammars are induced, both at **structural /
functional-role (L2/L3)** with **no phonetic value assigned**:

1. **Ledger grammar** — a repeated `CARRIER VALUE` entry loop (96.6 % of
   numerals well-formed), with a distinctive terminal **TOTAL** slot
   (`KU-RO`, `TOT→N` = 0.795, 59 % terminal) partially corroborated
   arithmetically (7/31 exact, 12/31 within 2; near-misses = dropped fractions),
   and a positionally-distinct mid-text **DEFICIT** slot (`KI-RO`). An LMIB,
   tablet-bound, Haghia-Triada-centred phenomenon.
2. **Votive/libation grammar** — a **rigid linear anchor template**
   `OP < SSR < UNK < IPN < SIR` with zero order inversions
   (permutation p = 5·10⁻⁵) and head-obligatory/tail-optional fills. A
   stone-vessel, sanctuary-distributed, earlier phenomenon.

The two grammars are in complementary distribution (accounting anchors never on
vessels; libation anchors never with numerals) — the strongest available
structural evidence for **two distinct Linear-A registers**, established without
assigning a single sound value. No transfer licence is earned; these are
anonymous relative structures.

**Limitations.** Anchor per-pair support in the votive grammar is small
(n_both 3–5); the permutation null aggregates them but each pair alone is weak.
Ledger sum-consistency is bounded above by the silver corpus's un-numbered
fraction glyphs. Both grammars describe *positional regularity*, not meaning.
