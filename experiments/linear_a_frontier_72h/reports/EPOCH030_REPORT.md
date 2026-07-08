# EPOCH030 REPORT — Numeral / logogram attachment order in the ledger grammar (L2/L3)

**Task:** EPOCH-030 · Linear A frontier-72h
**Question:** In Linear A administrative token streams, do NUMERAL tokens (`t=='num'`) attach to WORD tokens (`t=='word'`) in a FIXED ORDER — specifically WORD→NUMERAL (entry word followed by its quantity) rather than NUMERAL→WORD — and is that ordering ROBUST across independent SITES?
**Layer:** L2/L3 (pure token-stream positional grammar). **No phonetics, no meaning, no numeral values, no reading.** Numerals are treated only as tokens of type `num`; only token TYPE and POSITION are used.
**Verdict (mechanical, frozen rule):** `MACHINERY_UNINFORMATIVE`

---

## 1. Verdict gate trace (frozen rule, prereg.md §7)

The frozen verdict is GATED by the positive control (PC). PC must pass before any LA verdict is admissible. PC FAILED → `MACHINERY_UNINFORMATIVE` regardless of the LA numbers below.

| Gate | Condition | Value | Pass? |
|---|---|---|---|
| PC (a) detect planted order | planted p_wordfirst≈0.90 detected, p ≤ 0.05, dir word_first | p = 0.0, p_wordfirst = 0.895, dir ok | ✅ |
| PC (b) false-positive control | fair-coin (p_wordfirst=0.5) rejection rate ≤ 0.10 | **0.48** | ❌ |
| Global LA direction | null_p ≤ 0.05 | 0.0 | (would pass) |
| ≥2 sites individually sig | count of sites p ≤ 0.05 | 8 / 8 | (would pass) |
| Direction consistent | all sig sites same direction | all `word_first` | (would pass) |
| Leave-one-site-out | loo_p ≤ 0.05, same dir | loo_p = 0.0, word_first | (would pass) |

PC gate (b) fails (synthetic fair-coin false-positive rate **0.48** ≫ 0.10 threshold) → **MACHINERY_UNINFORMATIVE**. The LA findings below are therefore reported as **exploratory / not adjudicated** — the stream-shuffle null, as configured, cannot be trusted to separate a real attachment-order direction from a direction-randomized stream.

## 2. Positive control (gates the verdict) — FAILED

The PC is synthetic, built from the LA stream itself (disclosed in prereg.md §5: the LB damos corpus carries wordform sequences only and has no ordered word/numeral stream, so a real-stream PC is unavailable).

- **(a) Planted order DETECTED:** a synthetic corpus was built by forcing every real word-num adjacency to word→num with probability 0.90 (realized p_wordfirst = 0.895). The shuffle test rejected at p = 0.0 with the correct (word_first) direction. The machinery *does* see a planted direction. ✅
- **(b) False-positive control FAILED:** 25 synthetic corpora were built by assigning each real word-num adjacency to word→num vs num→word by a fair coin (planted p_wordfirst = 0.5, NO real direction by construction). Each was tested at p ≤ 0.05. **Rejection rate = 0.48** (12/25 rejected), against a frozen threshold of ≤ 0.10.
  - Synthetic p-values ranged from 0.0 to 1.0; twelve fell at or below 0.05.
  - Interpretation: the stream-shuffle null does **not** reproduce the observed marginal p_wordfirst under direction-randomization. Because the shuffle permutes *all* token positions (not just pair directions), a fair-coin direction assignment still leaves the word/num tokens placed in positions where, post-shuffle, the expected p_wordfirst is ≈0.5 — yet the realized fair-coin corpora land far from 0.5 often enough to reject ~half the time. The null is **not calibrated** for this statistic. Per the frozen rule, this is `MACHINERY_UNINFORMATIVE`.
- The direction-isolating **pair-flip** deviation null (prereg §4 companion) fails PC (b) identically: false-positive rate **0.44** (11/25), detect-planted p = 0.0. Same conclusion under either null.

## 3. Global LA signal (exploratory — NOT adjudicated, PC failed)

Inspection of the LA stream (1341 inscriptions):

- Token-type vocabulary and global counts: `word` 3147, `nl` 2114, `num` 1276, `other` 1056, `div` 463. (No separate `logogram`/`fraction` type; commodity logograms live under `other`/`word`. Disclosed in prereg §2.)
- Word-numeral adjacencies: **1059** total — **1040** word→num, **19** num→word.
- Global **p_wordfirst = 0.9821** (observed); stream-shuffle null mean p_wordfirst = 0.4993; **null_p = 0.0**.

*If the machinery were calibrated*, this would be an overwhelming word→numeral attachment signal. Because PC (b) failed, this is reported as a candidate signal requiring a re-calibrated null, not an established fact.

## 4. Cross-site (exploratory — NOT adjudicated, PC failed)

Sites with ≥ 15 word-num adjacencies: **8** (of which all 8 are individually significant).

| Site | n_adj | p_wordfirst | p | dir |
|---|---:|---:|---:|---|
| Haghia Triada | 692 | 0.9913 | 0.0 | word_first |
| Zakros | 117 | 0.9744 | 0.0 | word_first |
| Khania | 80 | 0.9500 | 0.0 | word_first |
| Phaistos | 30 | 0.9667 | 0.0 | word_first |
| Tylissos | 28 | 1.0000 | 0.0 | word_first |
| Arkhalkhori | 27 | 1.0000 | 0.0 | word_first |
| Malia | 25 | 1.0000 | 0.0 | word_first |
| Palaikastro | 18 | 1.0000 | 0.004 | word_first |

8 / 8 sites individually significant at p ≤ 0.05, **all** `word_first` (direction consistent). Leave-one-site-out (drop Haghia Triada, the largest site): loo_p = 0.0, loo_p_wordfirst = 0.9646 (same direction). *(Again: not adjudicated — PC failed.)* Under the frozen rule these would collectively meet the `NUMERAL_ORDER_CROSS_SITE_ROBUST` bar; that bar is **not** reached because the PC gate fails first.

## 5. Bottom line (honest, bounded)

- **The machinery is not calibrated.** The stream-shuffle null rejects direction-randomized (fair-coin) synthetic corpora 48% of the time (threshold 10%). It cannot distinguish a real attachment-order direction from a direction-randomized stream. Per the frozen rule this is `MACHINERY_UNINFORMATIVE`, and no LA claim is adjudicated.
- **What the (un-adjudicated) numbers would suggest, if re-calibrated:** a near-universal word→numeral attachment order (global p_wordfirst = 0.982, only 19 of 1059 adjacencies num→word), present and significant at all 8 testable sites, in a consistent direction, surviving leave-one-site-out. On its own terms the cross-site-robust bar would be met — but the PC failure voids that.
- **Honest reading:** the raw asymmetry is extreme (98% word-first) and is very likely a real property of the LA administrative stream (entry word followed by its quantity is exactly what a ledger grammar would predict). But THIS epoch's null model cannot establish it mechanically, because the stream-shuffle conflates adjacency-density structure with pair-direction structure and is not type-I-calibrated here. The result is a **methodological null, not a substantive null**.
- **No meaning claimed.** Tokens carry no phonetic / sound / meaning / language / reading. No numeral values are read or compared. Only token TYPE and POSITION.

## 6. Successor hypotheses (for a re-calibrated re-test)

- Re-define the null so it is **direction-isolating and calibrated**: condition on the observed multiset of adjacency *positions* and randomize only pair *direction* (a proper exchangeable pair-direction null), then verify the fair-coin false-positive rate ≤ 0.10 before any LA verdict. The pair-flip null here is a step in that direction but still failed calibration (0.44) — likely because the two-sided p on a heavily discrete statistic is anti-conservative at small per-site n; an exact binomial / sign test on n_word_first ~ Binomial(n_adj, 0.5) is the natural calibrated replacement.
- L2: once calibrated, test whether the rare num→word exceptions (19/1059) cluster at specific sites, positions, or commodity classes — exceptions may mark a distinct grammatical construction rather than noise.
- L3: extend to TRIPLES (word→num→div, word→num→nl) to test whether the attachment order is part of a longer positional template.
- L2: relate attachment order to document class (tablet vs nodule vs roundel) — a robust ledger grammar should be class-invariant.
- L2: compare LA p_wordfirst to a matched LB control once an ordered word/numeral stream can be reconstructed for LB.

## 7. Outputs

- `epochs/EPOCH-030/prereg.md`, `plan_hash.txt` (frozen before verdict; PC run first).
- `epochs/EPOCH-030/machinery.py` — adjacent word/numeral pair-direction metric; stream-shuffle (frozen) + pair-flip (deviation) nulls; synthetic planted-order detect + fair-coin false-positive positive control; per-site + leave-one-site-out; frozen mechanical verdict.
- `epochs/EPOCH-030/result.json` — full numbers incl. inspections, both nulls, per-site, leave-one-site-out, PC detail.
- `data/epoch_030/` — data dir (path contract).
