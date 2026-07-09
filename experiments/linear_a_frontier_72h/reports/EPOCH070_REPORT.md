# EPOCH-070 REPORT — What do fractions attach to? (num->frac vs word->frac; cross-site vs site-local)

**Campaign:** Linear A frontier-72h · **Epoch:** 070 · **Layer:** L2 (token-class adjacency only)
**Task:** Is num->frac a CROSS-SITE metrological template, or does fractional attachment vary by site?
**Verdict (mechanical, frozen rule):** `FRAC_ATTACHMENT_SITE_LOCAL`

---

## 1. Question & scope

E060 established that FRACTION-class tokens are entry-TERMINAL (frac->nl, cross-site 3/3) and that logograms precede numerals (logo->num). It did **not** test what *precedes* a fraction. The naive metrological expectation is num->frac ("N and a fraction" — a whole quantity plus a fractional remainder).

**Scope is L2 only:** the token CLASS immediately before a fraction-class token. No fraction value, no sign values, no readings, no metrological arithmetic.

**Non-circular:** fraction-class = `t=='other'` AND raw contains U+2044 (`⁄`) or a vulgar-fraction char (`½¼¾⅓⅕⅙⅛⅔⅗`) — the E060 definition. Attachment = the `t` field of the immediately preceding token. The null is a **within-line shuffle** that preserves each line's exact token multiset and `nl` structure, so any enrichment is beyond chance token ordering given the line contents.

## 2. Data (verified)

- Corpus: `corpus/silver/inscriptions_structured.json`, ordered `stream`.
- **n = 310 fraction tokens.**
- Before-class histogram (global): `word 148 (0.48), num 120 (0.39), nl 28, other 12, div 1, START 1`.
- Sites with ≥20 fractions: **Haghia Triada (194), Khania (73)**. (Next: Zakros 12 — below threshold.)

## 3. Metric & null (frozen)

- `R_num`  = fraction of fractions immediately preceded by a `num` token.
- `R_word` = fraction of fractions immediately preceded by a `word` token.
- **NULL:** within each line (segment between `nl`), permute the order of the non-`nl` tokens (preserving the line's token multiset + `nl` structure); recompute rates; 2000 permutations; perm p = frac(null ≥ observed), one-sided enrichment (add-1).
- **SITE-CONTRAST:** site-label permutation over pooled HT+Khania fractions; stat = |R_num(HT) − R_num(Khania)|; 5000 perms.

## 4. Positive control (SYNTHETIC) — gates the verdict

The PC corpora are **synthetic**.

| PC | Setup | Result |
|----|-------|--------|
| DETECT | fractions ALWAYS follow a numeral | R_num=1.000, null=0.335, **p=0.0005 → DETECTED** |
| FALSE-POSITIVE | fractions placed uniformly at random within lines (40 draws) | FPR = **0.050** (≤ 0.10 required) → **CALIBRATED** |

Machinery self-check (within-line null on a known synthetic) PASSED: nl structure and token multiset preserved under permutation; enrichment detected where planted.

**PC VERDICT: PASSED.** Machinery is informative.

## 5. Global results

| rate | observed | null mean | perm p |
|------|---------:|----------:|-------:|
| R_num  | **0.387** | 0.130 | **0.0005** ✓ enriched |
| R_word | **0.477** | 0.354 | **0.0005** ✓ enriched |

Both num->frac and word->frac are enriched globally beyond the within-line shuffle null. word->frac is in fact the *more common* attachment (148 vs 120).

## 6. Per-site results (≥20 fractions)

| Site | n | R_num | null | perm p | enriched? |
|------|--:|------:|-----:|-------:|:---------:|
| Haghia Triada | 194 | **0.479** | 0.162 | **0.0005** | yes |
| Khania | 73 | **0.055** | 0.022 | **0.020** | yes |

Both sites show num->frac enrichment *individually*. But the magnitudes are wildly different.

## 7. Site contrast (KEY test)

| | value |
|---|---|
| R_num(HT) | 0.479 |
| R_num(Khania) | 0.055 |
| \|diff\| | **0.425** |
| contrast perm p (5000 perms) | **0.0002** |
| **differ?** | **YES** |

Khania attaches fractions overwhelmingly to **words** (R_word Khania ≈ 0.67), while Haghia Triada splits roughly evenly between words (0.41) and numerals (0.48).

## 8. Frozen mechanical verdict

Applying the frozen rule:

- `FRAC_NUM_ATTACHMENT_CROSS_SITE` requires PC passed **AND** R_num globally enriched **AND** R_num enriched same-direction in BOTH sites **AND** R_num(HT) NOT significantly different from R_num(Khania).
  → The last condition **FAILS** (contrast p=0.0002, |diff|=0.425). ❌
- `FRAC_ATTACHMENT_SITE_LOCAL` triggers iff R_num differs significantly between HT and Khania (contrast perm p ≤ 0.05) **OR** R_num enriched in only one site.
  → Contrast p=0.0002 ≤ 0.05. ✅

**VERDICT: `FRAC_ATTACHMENT_SITE_LOCAL`.**

## 9. Bottom line (honest)

num->frac is a *real* attachment signal — it is enriched globally and in both sites individually above the within-line shuffle null. But it is **NOT a uniform cross-site metrological template**. The fractional attachment is a **site convention**: at Haghia Triada nearly half of fractions follow a numeral (R_num=0.48), whereas at Khania only ~5% do (R_num=0.055) and fractions there attach overwhelmingly to words (R_word≈0.67). The two sites differ massively and significantly (contrast perm p=0.0002). So the answer to "what do fractions attach to?" is: **it depends on the site** — HT uses a num->frac metrological remainder pattern, Khania uses a word->frac pattern. This is site-local, not a shared Linear A metrological grammar.

(Token-class adjacency only; no fraction values, no sign values, no readings, no metrological arithmetic. PC synthetic, stated as such.)

## 10. Outputs

- prereg: `experiments/linear_a_frontier_72h/epochs/EPOCH-070/prereg.md` (FROZEN)
- plan_hash: `experiments/linear_a_frontier_72h/epochs/EPOCH-070/plan_hash.txt`
- machinery: `experiments/linear_a_frontier_72h/epochs/EPOCH-070/machinery.py` (with `__main__` self-check)
- result: `experiments/linear_a_frontier_72h/epochs/EPOCH-070/result.json`
- data: `experiments/linear_a_frontier_72h/data/epoch_070/`
- this report: `experiments/linear_a_frontier_72h/reports/EPOCH070_REPORT.md`
