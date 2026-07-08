# EPOCH-051 REPORT — A-HEADING x ACCOUNTING-INTENSITY INTERACTION (L2/L3)

**Campaign:** Linear A frontier-72h · **Epoch:** 051
**Connects:** E034 (A-initial words mark inscription-INITIAL/heading position) + E045 (document classes differ in accounting intensity = numeral-density)
**Question:** Do inscriptions whose FIRST word token's first sign is `A` ("A-headed") have a different numeral-density than non-A-headed inscriptions — i.e. does the A-heading mark a document FUNCTION — and is that difference robust across sites, controlling for the support/site confound?

**Discipline (non-circular):** `A-` = literal first sign token `"A"` of the first word token (anonymous positional token; NO phonetic value, NO meaning). `numeral_density` = (#num)/(#word+#num) over content tokens. Eligibility: ≥2 content tokens AND ≥1 word. L2/L3 only. LB control-only (LB lacks this structure — stated as deviation).

---

## VERDICT (frozen, mechanical): `A_HEADING_FUNCTION_SITE_LOCAL`

The global A-heading × numeral-density difference **is** significant and directionally consistent, but it **vanishes under confound control** (within the largest document class and within the largest site) and **cross-site robustness cannot be established** (only 1 testable site). The global signal is therefore a between-stratum confound artifact, not a within-stratum document-function marker.

---

## 0. Inspection

- Eligible inscriptions (≥2 content, ≥1 word): **465** of 1341.
- **A-headed: 61** · **non-A-headed: 404**.
- A-heading rate varies markedly by **support** (Tablet 0.117, Stone vessel 0.173, Nodule 0.000, Lames 0.000) and by **site** (HT 0.091, Khania 0.150, Zakros 0.026, Palaikastro 0.231) — i.e. the confound structure is real and strong.

## 1. Freeze
- `prereg.md` frozen → `plan_hash.txt = a88cd36d1a4d86cbee5602c8282580c1c1cf2b34205c1a515d51e087e1744687`.
- `machinery.py` with `__main__` self-check (passes).

## 2. GLOBAL effect

| group | n | mean density |
|---|---|---|
| A-headed | 61 | **0.199** |
| non-A-headed | 404 | **0.307** |

Mann-Whitney U (two-sided) **p = 1.3e-4**. Direction: **A-headed inscriptions have LOWER numeral-density** (sparser). Consistent in every stratum examined.

## 3. POSITIVE CONTROL (gates verdict) — **PASSED**

- **DETECT:** planted +0.20 density shift on a random half → detected, p ≈ 0.0, correct direction. ✔
- **FALSE-POSITIVE:** two groups from the SAME density distribution → rejection rate **0.08** over 25 splits (≤ 0.10). ✔

Machinery is calibrated → verdict is informative.

## 4. LA MAIN — confound-controlled + cross-site

### (a) Confound control — **FAILS**

| stratum | n A-headed | n non-A-headed | MW p | direction |
|---|---|---|---|---|
| within **Tablet** (largest class) | 36 | 273 | **0.076** (n.s.) | A-headed lower |
| within **Haghia Triada** (largest site) | 18 | 179 | **0.299** (n.s.) | A-headed lower |

Direction is consistent (A-headed always sparser), but neither within-stratum test reaches p≤0.05. The Tablet stratum (36 vs 273) is well-powered, so this is a **confound-control failure**, not merely a power issue: the global effect is largely absorbed by support/site.

### (b) Cross-site — **underpowered / not robust**

- Sites with ≥15 in each group: **1** (Haghia Triada only).
- Significant sites: **0**.
- Direction consistent across testable sites: yes (but only 1 site).
- **Leave-one-site-out on HT:** pooled-minus-HT still significant, **p = 0.001** — so HT is not the sole driver, yet the within-stratum tests still fail.

## 5. Bottom line

There is a real, strong, directionally consistent **global** association: A-headed inscriptions are numeral-sparser (0.199 vs 0.307, p=1.3e-4). But once you hold document class or site constant, the effect disappears (within-Tablet p=0.076, within-HT p=0.299), and only one site is even testable for cross-site robustness. **The A-heading mark does not, on this evidence, distinguish a document FUNCTION in a confound-robust, cross-site way** — the apparent signal is driven by A-heading rate and accounting intensity both co-varying with support and site. Verdict: `A_HEADING_FUNCTION_SITE_LOCAL`.

`A-` is treated as an anonymous positional token throughout; only token composition was used; no phonetics, no meaning, no sign values.

---

## Outputs (PATH CONTRACT)
- `experiments/linear_a_frontier_72h/epochs/EPOCH-051/prereg.md`
- `experiments/linear_a_frontier_72h/epochs/EPOCH-051/plan_hash.txt`
- `experiments/linear_a_frontier_72h/epochs/EPOCH-051/machinery.py`
- `experiments/linear_a_frontier_72h/epochs/EPOCH-051/result.json`
- `experiments/linear_a_frontier_72h/reports/EPOCH051_REPORT.md`
- `experiments/linear_a_frontier_72h/data/epoch_051/per_inscription_features.json`
- `experiments/linear_a_frontier_72h/data/epoch_051/full_analysis.json`
