# EPOCH-031 REPORT — LEDGER WORD→NUMERAL ORDER, CALIBRATED PAIR-FLIP NULL

**Task ID:** EPOCH-031
**Campaign:** Linear A frontier-72h
**Layer:** L2/L3 (token-ORDER structure only — no numeral-value arithmetic, no phonetics, no meaning)
**Successor of:** EPOCH-030 (raw word→numeral order p_wordfirst=0.982 found, but its frozen full-stream-shuffle null was MISCALIBRATED, fp=0.48 → MACHINERY_UNINFORMATIVE)
**Verdict (frozen mechanical):** `LEDGER_WORD_NUMERAL_CROSS_SITE_ROBUST`

---

## 1. Question (frozen)

Is word-before-numeral the dominant adjacency order, robustly across independent SITES, under a
properly-calibrated null?

A word/num adjacency = an adjacent (token_i, token_{i+1}) pair in a stream where the types are {word, num}
in either order (corpus type key = `'num'`).

```
p_wordfirst = (#word→num) / (#word→num + #num→word)
```

## 2. Data & inspection (step 0)

`corpus/silver/inscriptions_structured.json` — 1341 inscriptions, each with `site` and an ordered `stream`
of tokens `{"t": "word"|"num"|"nl"|"div"|"other", ...}`.

**Global counts (E030-confirmed, reproduced exactly):**

| metric | value |
|---|---|
| n_adj (word/num adjacencies) | **1059** |
| n_word_first (word→num) | **1040** |
| n_num_first (num→word) | **19** |
| p_wordfirst | **0.982059** |

**Per-site (≥15 adjacencies = testable):** 8 sites — Haghia Triada (692), Zakros (117), Khania (80),
Phaistos (30), Tylissos (28), Arkhalkhori (27), Malia (25), Palaikastro (18). All show p_wordfirst 0.95–1.00.

## 3. Null model (frozen, calibrated pair-flip)

H0: no order preference. For each observed adjacent word/num pair, independently keep or FLIP its order
with probability 0.5 (fair coin per pair), recompute p_wordfirst. **Exchangeable by construction**
(H0: word-first prob = 0.5 per pair) → guaranteed calibrated. 5000 draws. Two-sided p for
"p_wordfirst deviates from 0.5". Equivalently #word_first ~ Binomial(n_adj, 0.5); exact two-sided binomial
p computed alongside and required to AGREE.

## 4. Global result (step 2)

| statistic | value |
|---|---|
| p_wordfirst | 0.982059 |
| pair-flip two-sided p | **0.0** (floor: no draw reached the observed extremity in 5000 draws) |
| exact Binomial(1059, 0.5) two-sided p | **6.85 × 10⁻²⁷⁹** |
| null mean p_wordfirst | 0.5002 (≈0.5 ✓) |

**Agreement:** pair-flip p = 0.0 and binom p = 6.85e-279 — both ≪ 0.05, same direction. The pair-flip p
saturates at 0 because the observed p_wordfirst=0.982 is so extreme that no Monte-Carlo draw matched it;
the exact binomial p confirms the true tail probability is astronomically small. **They agree.**

## 5. Positive control (step 3) — gates the verdict

The pair-flip null is calibrated by construction; the PC CONFIRMS calibration:

| PC component | result | gate |
|---|---|---|
| (a) DETECT planted 90% word-first bias | p = 0.0, direction = word-first ✓ | reject p≤0.05, correct direction — **PASS** |
| (b) FALSE-POSITIVE on fair-coin H0 (30 sets) | rejection rate = **0.033** (1/30) | ≤ 0.10 — **PASS** |

**PC verdict: PASSED.** The null is properly calibrated (fp 0.033 ≪ 0.10), in stark contrast to E030's
miscalibrated stream-shuffle null (fp 0.48). This unblocks the significance claim.

## 6. LA MAIN — cross-site held-out (step 4)

Per site with ≥15 word/num adjacencies:

| site | n_adj | p_wordfirst | pair-flip p | binom p | sig (p≤0.05, word-first) |
|---|---|---|---|---|---|
| Haghia Triada | 692 | 0.9913 | 0.0 | 1.47e-194 | ✓ |
| Zakros | 117 | 0.9744 | 0.0 | 3.21e-30 | ✓ |
| Khania | 80 | 0.9500 | 0.0 | 2.76e-18 | ✓ |
| Phaistos | 30 | 0.9667 | 0.0 | 5.77e-08 | ✓ |
| Tylissos | 28 | 1.0000 | 0.0 | 7.45e-09 | ✓ |
| Arkhalkhori | 27 | 1.0000 | 0.0 | 1.49e-08 | ✓ |
| Malia | 25 | 1.0000 | 0.0 | 5.96e-08 | ✓ |
| Palaikastro | 18 | 1.0000 | 0.0 | 7.63e-06 | ✓ |

- **n_sites_testable = 8**
- **n_sites_sig = 8** (all individually significant)
- **direction_consistent = TRUE** (all 8 word-first; no flips)

**Leave-one-site-out (exclude Haghia Triada, the largest site, 692 adj):** on the pooled rest
(n_adj = 367, p_wordfirst = 0.9646), pair-flip p = 0.0, binom p = 1.96e-87 → **survives**. The result is
not driven by Haghia Triada.

## 7. Frozen mechanical verdict (step 5)

Gate evaluation:
- PC passed? **YES** (detect p=0.0 correct direction; fp=0.033 ≤ 0.10).
- Global pair-flip p ≤ 0.05, word-first direction? **YES** (p=0.0, p_wordfirst=0.982 > 0.5).
- ≥3 sites individually significant, same direction? **YES** (8/8, all word-first).
- Survives leave-one-site-out? **YES** (loo_p=0.0, word-first).

→ **`LEDGER_WORD_NUMERAL_CROSS_SITE_ROBUST`**

## 8. Bottom line (honest, scoped)

Under a properly-calibrated pair-flip null (PC-confirmed: detected planted bias, false-positive rate 0.033),
word-before-numeral is the dominant adjacency order in the Linear A token stream — 1040 word→num vs 19
num→word (p_wordfirst=0.982) — and this is **robust across all 8 independent testable sites** (8/8
significant, identical word-first direction) and **survives leave-one-site-out** of the largest site.

This CERTIFIES, at the **L2/L3 token-ORDER** level, the Linear A administrative **"entry-then-quantity"
ledger grammar**: a word (the entry) is followed by its numeral (the quantity). This is a structural
ordering claim only — it says nothing about what the words mean, what the numerals count, or the arithmetic
values of the numerals. It is the token-ORDER skeleton of a ledger, not its semantics.

The 19 num→word exceptions (~1.8%) are a real structural exception class worth characterizing (successor).

## 9. Non-circularity

Token TYPES (word/num) and stream ORDER are directly observed in the structured corpus. No phonetic value,
no arithmetic on numeral values, Linear B not used, anonymous (no sign identities enter the statistic). The
pair-flip null is exchangeable by construction and its calibration was confirmed by the false-positive
control (0.033 ≤ 0.10).

## 10. Deviations

- The binomial PMF was computed in log-space (lgamma) to avoid float overflow at n=1059 — a numerical-
  stability implementation detail, not a method change; the exact two-sided binomial p value is unchanged.
- pairflip_p = 0.0 is a Monte-Carlo floor effect (5000 draws, none reached the observed extremity); the
  exact Binomial(1059,0.5) p = 6.85e-279 is reported alongside and agrees (both ≪ 0.05).
- Corpus path resolved to repo-root `corpus/silver/inscriptions_structured.json` (the campaign dir has no
  `corpus/` subdir); token type key is `'num'` (not `'numeral'`), matching E030's corrected inspection.

## 11. Outputs (PATH CONTRACT)

- `experiments/linear_a_frontier_72h/epochs/EPOCH-031/prereg.md` ✓
- `experiments/linear_a_frontier_72h/epochs/EPOCH-031/plan_hash.txt` = `b69715289f69b21255ec6c210ec31c8224bccf40370b63d7350ce78a22393cc6  prereg.md` ✓
- `experiments/linear_a_frontier_72h/epochs/EPOCH-031/machinery.py` (with `__main__` self-check, all asserts pass) ✓
- `experiments/linear_a_frontier_72h/epochs/EPOCH-031/result.json` ✓
- `experiments/linear_a_frontier_72h/reports/EPOCH031_REPORT.md` (this file) ✓
- `experiments/linear_a_frontier_72h/data/epoch_031/` : `full_run.json`, `per_site_table.csv`, `global_counts.json` ✓
