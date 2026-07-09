# EPOCH-060 REPORT — Metrological / Logographic Ledger Entry Template (L2)

**Campaign:** Linear A frontier-72h
**Epoch:** 060
**Layer:** L2 (token CLASS + POSITION only)
**Verdict:** `METRO_LOGO_ENTRY_TEMPLATE_CROSS_SITE`

---

## 1. Question

The corpus `other` tokens (dismissed until now) form a coherent class split into:
- **LOGOGRAMS** — GORILA commodity signs, raw values starting with `*` (e.g. `*304`, `*305`, `*308`).
- **FRACTIONS** — the Linear A fraction system, raw values containing the fraction slash `⁄` (e.g. `¹⁄₂`, `¹⁄₄`, `¹⁄₃`) or a Unicode vulgar-fraction char (U+2150–U+215F).

Do these tokens occupy consistent, cross-site positions in the ledger ENTRY?
- **H1 LOGO->NUM:** are logogram-class tokens followed by a numeral (commodity-sign then quantity)?
- **H2 FRAC-TERMINAL:** are fraction-class tokens entry-terminal (immediately followed by `nl` or END)?

Beyond a within-line position-shuffle null, and cross-site? Token CLASS + POSITION only — no logogram identity, no fraction value, no readings.

## 2. Method (frozen in prereg.md, hash `0a846cc4…`)

**Classification.** `t=='word'`→WORD, `t=='num'`→NUM, `t=='div'`→DIV, `t=='nl'`→NL; `t=='other'`→ LOGOGRAM if `raw` starts with `*`, FRACTION if `raw` contains `⁄` or a U+2150–U+215F char, else OTHERSIGN (ignored).

**Metrics.**
- H1 LOGO->NUM = (# logogram tokens whose next token is NUM) / (# logogram tokens).
- H2 FRAC-TERMINAL = (# fraction tokens whose next token is NL or END) / (# fraction tokens).

**Null (unified).** Within each line (segment of non-NL tokens between NL tokens), randomly permute the order of the non-NL tokens, preserving the line's token multiset and the NL/line structure. Recompute H1, H2. 1000 permutations. perm p = frac(null ≥ observed), one-sided enrichment. This asks whether logograms sit before numerals AND fractions sit line-final more than random ordering within the same lines.

**Positive control (synthetic, gates verdict).** (a) DETECT: planted corpus with logo always before num and frac always line-final → must flag both at p≤0.05. (b) FALSE-POSITIVE: logo/frac placed uniformly at random within variable-length lines → must not fire above 0.10 across 30 draws.

## 3. Inspection

| class | n | sites ≥10 |
|---|---|---|
| LOGOGRAM | 160 | Haghia Triada (98), Khania (30), Phaistos (10) |
| FRACTION | 311 | Haghia Triada (195), Khania (73), Zakros (12) |

LOGOGRAM after-token histogram: NUM 93, DIV 26, NL 18, FRACTION 11, END 6, WORD 3, OTHERSIGN 2, LOGOGRAM 1.
FRACTION after-token histogram: NL 265, END 43, NUM 1, OTHERSIGN 1, WORD 1 → 308/311 entry-terminal.

## 4. Positive Control — PASSED

| arm | result |
|---|---|
| DETECT p (H1) | 0.0 |
| DETECT p (H2) | 0.0 |
| false-positive rate (30 uniform draws) | 0.10 (at bound, ≤0.10) |

Detect arm unambiguous; false-positive at the 0.10 bound (driven by permutation-p coarseness for short lines). Machinery is informative. LB PC is synthetic only (LB stream lacks the `other`+raw class tagging).

## 5. Global Results

| stat | n | obs | null mean | perm p |
|---|---|---|---|---|
| H1 LOGO->NUM | 160 | **0.581** | 0.259 | **0.0** |
| H2 FRAC-TERMINAL | 311 | **0.990** | 0.461 | **0.0** |

Both globally enriched far beyond the within-line shuffle null.

## 6. Cross-Site

**H1 LOGO->NUM** (sites with ≥10 logograms): 3/3 enriched, same direction.

| site | n_logo | obs | null | perm p |
|---|---|---|---|---|
| Haghia Triada | 98 | 0.622 | 0.286 | 0.0 |
| Khania | 30 | 0.433 | 0.181 | 0.0 |
| Phaistos | 10 | 0.500 | 0.217 | 0.018 |

**H2 FRAC-TERMINAL** (sites with ≥10 fractions): 3/3 enriched, same direction.

| site | n_frac | obs | null | perm p |
|---|---|---|---|---|
| Haghia Triada | 195 | 0.990 | 0.434 | 0.0 |
| Khania | 73 | 1.000 | 0.576 | 0.0 |
| Zakros | 12 | 1.000 | 0.365 | 0.0 |

## 7. Frozen Mechanical Verdict

PC passed ✓; H1 globally enriched (p=0.0) ✓ and holds in ≥2 sites (3/3) ✓; H2 globally enriched (p=0.0) ✓ and holds in ≥2 sites (3/3) ✓.

→ **`METRO_LOGO_ENTRY_TEMPLATE_CROSS_SITE`**

## 8. Bottom Line

Yes — there is a metrological/logographic entry template, and it replicates cross-site. The positional skeleton is:

> **[commodity-logogram] → [numeral quantity] … [fraction remainder | line-end]**

Logogram-class tokens are followed by a numeral ~58% of the time (vs ~26% under within-line shuffle; 3/3 sites), and fraction-class tokens are entry-terminal ~99% of the time (vs ~46% under null; 3/3 sites, two of them at obs=1.000). This is pure L2 token-CLASS + POSITION structure: no logogram identity, no fraction value, no readings, no metrological arithmetic were used. The commodity-sign-then-quantity and fraction-closes-the-entry regularities are not artifacts of within-line token ordering — they hold beyond the shuffle null and across Haghia Triada, Khania, Phaistos (H1) and Haghia Triada, Khania, Zakros (H2).

## 9. Non-circularity

Token classes come only from corpus tagging (`t=='other'` + raw pattern); the null destroys any sign-identity association by permuting within-line order while preserving the token multiset. Only positional class structure is tested. L2 ONLY.

## 10. Deviations

- False-positive control rate landed exactly at the 0.10 bound (3/30 uniform draws flagged), driven by permutation-p coarseness for short lines; detect arm is unambiguous (p=0.0). Verdict proceeds since fp_ok is defined as ≤0.10.
- LB positive control is synthetic only (LB stream lacks the `other`+raw class tagging); stated per protocol.

## 11. Outputs

- `experiments/linear_a_frontier_72h/epochs/EPOCH-060/prereg.md` (frozen)
- `experiments/linear_a_frontier_72h/epochs/EPOCH-060/plan_hash.txt` (`0a846cc4…  prereg.md`)
- `experiments/linear_a_frontier_72h/epochs/EPOCH-060/machinery.py` (with `__main__` self-check)
- `experiments/linear_a_frontier_72h/epochs/EPOCH-060/result.json`
- `experiments/linear_a_frontier_72h/data/epoch_060/{global,cross_site,before_after}.json`
