# EPOCH-044 REPORT — NUMERAL-GROUP CARDINALITY / COMPOUND-QUANTITY STRUCTURE (L2/L3)

**Verdict: `SINGLE_NUMERAL_DOMINANT`**

In Linear A ledger entries, a quantity is a **SINGLE numeral token**, not a run of
consecutive numeral tokens. There is **no compound-quantity structure** at the
token-count level: every numeral-run in the corpus is length 1.

---

## 1. Question

Is a quantity in an LA ledger entry a SINGLE `num` token, or a RUN of consecutive
`num` tokens (a COMPOUND quantity, e.g. integer + fraction)? What is the
distribution of numeral-run lengths, and is a multi-token (compound) structure
PRESENT and CONSISTENT across sites? Pure token-count structure (L2/L3): count
consecutive `num` tokens; no numeral-value interpretation, no arithmetic, tokens
anonymous.

## 2. Data & definitions

- LA corpus: `corpus/silver/inscriptions_structured.json` (1341 inscriptions,
  1276 `num` tokens).
- A **numeral-run** = a maximal run of consecutive `num` tokens in an
  inscription's ordered `stream`; broken by any non-`num` token.
- **p_compound** = fraction of numeral-runs with length ≥ 2.
- **NULL**: token-order shuffle WITHIN each inscription (preserves the type
  multiset per inscription), 1000 draws, two-sided p.
- A site qualifies for cross-site analysis iff it has ≥ 20 numeral-runs.

## 3. Global result

| quantity | value |
|---|---|
| total numeral-runs | **1276** |
| run-length histogram | `{1: 1276}` — **100% length-1** |
| p_compound (observed) | **0.0** |
| shuffle-null mean p_compound | **0.181** |
| two-sided p | **0.0** |
| direction | **DEFICIT** |

There are **zero adjacent `num`-`num` pairs** anywhere in the corpus. Under the
shuffle null, ~18% of runs would be compound by chance; the observed 0.0 is a
massive, significant **deficit**. Numerals are spread out far more than chance —
they are **one-per-entry**, not clustered.

## 4. Positive control (gates the verdict) — PASSED

Built on the LA pooled type multiset (LB lacks a comparable stream-level
numeral-run structure in the available data; stated as a deviation).

| PC test | result |
|---|---|
| detect planted clustering (excess) | obs p_compound 0.333, **p = 0.0, direction = excess** ✓ |
| detect planted spreading (deficit) | obs p_compound 0.0, **p = 0.0, direction = deficit** ✓ |
| false-positive rate (20 shuffled true-H0 sets) | **0.05** (≤ 0.10 required) ✓ |
| **PC verdict** | **PASSED** |

The machinery detects both planted clustering and planted spreading, and does
not fire on shuffled true-H0 streams.

## 5. Cross-site (≥ 20 numeral-runs) — 8 sites, all DEFICIT

| site | n_runs | p_compound | null_mean | p | direction |
|---|---|---|---|---|---|
| Haghia Triada | 834 | 0.0 | 0.197 | 0.0 | deficit |
| Zakros | 126 | 0.0 | 0.182 | 0.0 | deficit |
| Khania | 121 | 0.0 | 0.086 | 0.0 | deficit |
| Phaistos | 37 | 0.0 | 0.145 | 0.0 | deficit |
| Arkhalkhori | 33 | 0.0 | 0.192 | 0.0 | deficit |
| Tylissos | 31 | 0.0 | 0.230 | 0.0 | deficit |
| Malia | 30 | 0.0 | 0.218 | 0.0 | deficit |
| Palaikastro | 20 | 0.0 | 0.277 | 0.002 | deficit |

- Sites testable: **8**. Sites significant **excess**: **0**. Sites significant
  **deficit**: **8**. Direction **consistent** (all deficit).
- **Leave-one-site-out** (exclude Haghia Triada): p_compound 0.0, null mean
  0.152, **p = 0.0, deficit**. The effect is not HT-driven.

## 6. Frozen mechanical verdict

- PC PASSED ✓
- Global EXCESS significant? **NO** — global is significant **deficit** (p=0.0).
- ≥ 3 sites significant excess? **NO** (0 sites).
- Runs overwhelmingly length-1 (100%) AND no significant excess →
  **`SINGLE_NUMERAL_DOMINANT`**.

The compound-quantity hypotheses (`COMPOUND_QUANTITY_STRUCTURE_CROSS_SITE`,
`COMPOUND_QUANTITY_SITE_LOCAL`) require significant **excess** compound runs;
the data show the opposite — a significant, cross-site **deficit**. Quantities in
LA ledger entries are **one numeral-token each**.

## 7. Discipline / non-circularity

Pure token-count structure (L2/L3). No phonetics, no sound, no meaning, no
reading. Numeral VALUES are NOT interpreted and NO arithmetic is performed — only
the COUNT of consecutive `num` tokens (run length) is measured. Tokens are
ANONYMOUS. The positive control is built on the LA type multiset itself with a
token-order-shuffle null (LB stream-level numeral runs unavailable); this is
stated as a deviation and does not use the LA result to validate itself.

## 8. Bottom line

LA quantities are **single numeral tokens**. There is no compound-quantity
(integer+fraction) run structure at the token-count level: 1276/1276 numeral-runs
are length 1, p_compound = 0.0, and this is a significant **deficit** relative to
a within-inscription order-shuffle null (which would produce ~18% compound runs
by chance), consistent across all 8 testable sites and robust to leaving out
Haghia Triada. If LA encodes fractional quantities, it does so **within a single
numeral token** (or via non-numeral separators), not as a run of consecutive
numeral tokens.

## 9. Successor hypotheses

1. **E045** — Test whether the token that separates consecutive numerals is
   structurally constrained (word before, `nl` after = rigid word+quantity+newline
   ledger cell) vs shuffle null.
2. **E046** — Test whether single-numeral quantities attach to specific commodity
   word tokens (lexical-attachment, L2/L3, no phonetics).
3. **E047** — Cross-script: derive a comparable LB token stream and test whether
   LB (known to use integer+fraction compounds) shows compound runs where LA does
   not.
4. **E048** — Test positional regularity of `num` tokens within the line
   (line-final?) via a within-line shuffle null.
5. **E049** — Examine within-line ordering of multiple `num` tokens
   (word-num-word-num) for a fixed quantity-slot structure.
6. **E050** — Analytic (exact) null for p_compound under random placement of k
   num tokens among n stream slots, to confirm the deficit without Monte Carlo.
