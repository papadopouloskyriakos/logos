# EPOCH-014 — Register-stratified phonotactics (value-free strata test)

**Frontier F7 (gate A) · prereg frozen 2026-07-08T05:14:39Z ·
plan_hash `017c615f…be2ff9` · seed 20260708 · claim ceiling L2 (no language named, no values used)**

## Question

Do Linear A's physical registers — **LIB** (stone-vessel libation carriers), **LEDG** (tablets),
**SEAL** (nodules/roundels/sealings) — carry measurably distinct sign-sequence statistics, consistent
with distinct linguistic strata (F7's mixed-language hypothesis), or one global system? Registers are
defined by SUPPORT TYPE only (Art. XI/XII: never by the statistics under test). Primary metric:
bigram JSD (word-internal + boundary bigrams, ≥2-sign words, rare signs→OTH) against a
document-length-matched label-permutation null (2,000 perms), Holm over the 3 pairs.

## Controls (run first) — machinery VALIDATED

| Control | Result | Gate |
|---|---|---|
| PC1 LB KN-A (personnel) vs KN-D (livestock), same site/language | JSD .3076, p .0005, excess-ratio **1.92** | must fire → **PASS** |
| PC2 random 50/50 splits of KN-D (20 reps) | FP 2/20 at p<.05 | ≤3/20 → **PASS** |
| PC3 power at each LA pair size (10 reps each) | 10/10, 10/10, 10/10 | ≥7/10 → **PASS** (ABSENT would have been readable) |
| LB single-language benchmark (recurrent-word removal on A vs D) | post-removal p .0005, excess-ratio **B_LB = 0.2125** | interpretation ceiling |

The LB benchmark is the epoch's key calibration: **one language, two document types, still systemic
post-removal divergence (xr 0.21)** — so "systemic register phonotactics" alone never licenses a
distinct-language reading.

## LA result — everything diverges, including sites within registers

| Pair | docs | words | JSD | excess-ratio | p (Holm) |
|---|---|---|---|---|---|
| LIB–LEDG | 85/257 | 259/844 | .2135 | **1.20** | .0015 |
| LIB–SEAL | 85/92 | 259/106 | .2663 | 0.83 | .0015 |
| LEDG–SEAL | 257/92 | 844/106 | .1974 | 0.62 | .0015 |
| *site:* LEDG HT vs non-HT | 162/95 | 630/214 | .1851 | 0.77 | (.0005) |
| *site:* SEAL HT vs non-HT | 43/49 | 53/53 | .3394 | **1.51** | (.0005) |

All three register pairs are Holm-significant at the permutation floor — **but the within-register
site divergence (SEAL HT/non-HT xr 1.51) exceeds every between-register divergence (max 1.20).**
By the frozen site gate every pair is site-discounted.

## VERDICT (mechanical, frozen rule): `REGISTER_STRATA_NO_POWER`

Register-vs-site attribution is undecidable at corpus scale: Linear A's dominant stratification axis
is at least as much **place** as **document type**, and LIB (the libation register) never co-occurs
with LEDG/SEAL at any site, so the libation-vs-administrative contrast is *permanently* site-confounded
in the extant corpus (assumption A4 realized).

## Post-hoc (non-verdict, exploratory)

- **PH1 — register within one site (unconfounded):** LEDG vs SEAL at HT: JSD .1767, xr 0.44, p .0005;
  at Khania: xr 1.38, p .0005. A real register contrast exists with site held fixed.
- **PH2 — recurrent-word removal everywhere:** divergence is mostly recurrent vocabulary. Residual
  excess-ratios: LEDG–SEAL 0.19, LEDG@HT vs non-HT 0.31, LIB–LEDG 0.45, LIB–SEAL 0.33, and the
  unconfounded LEDG–SEAL@HT falls to **0.126 (p .017) — BELOW the LB single-language ceiling 0.2125.**
- **PH4 — length-only adversary:** word-length profiles alone explain almost nothing (JSD ≤ .006);
  divergences are not length artifacts. LIB's long formula words are visible but tiny in absolute terms.

**Bearing on F7 (mixed-language):** NO SUPPORT GAINED. Where the comparison is clean (within-site),
the vocabulary-stripped register residual sits *below* what a single language (LB Greek across
personnel/livestock docs) produces. The only residuals above the single-language ceiling involve LIB —
exactly the register that cannot be separated from site/region. Nothing here refutes a mixed-language
Crete either: the discriminating comparison (libation vs admin at one site) does not exist in the
extant corpus; that is a **data-acquisition target**, not an analysis gap.

**Caveats:** A2 (editorial segmentation conventions may differ for stone vessels — bears on LIB pairs),
A3 (excess-ratio cross-size comparability), SEAL post-removal site test unrunnable (31/26 words).

## Successors

1. **Scribal-hand stratification:** GORILA/SigLA hand attributions at HT would let hand-vs-register-vs-site be
   separated on tablets (is the site effect actually a hands effect?).
2. **Unconfounded register test with power:** preregister LEDG–SEAL@HT + LEDG–SEAL@KH joint (stouffer) as the
   primary contrast; E014-posthoc gives the effect size for the power analysis.
3. **Trigram/gappy statistics at HT-only scale** to raise sensitivity of the within-site residual (0.126) test.
4. **LIB-internal geography:** East-Crete peak-sanctuary vessels vs Zakros vessels — is LIB itself one stratum?
5. **The SEAL HT/non-HT xr 1.51 anomaly:** roundel-vs-nodule composition differs (HT 25N/18R, non-HT 6N/42R+1S) —
   support-subtype, site, and chancellery-convention attributions need a dedicated design.
6. **New-dig leverage:** any future stone-vessel find at HT/Khania is worth disproportionate attention — it is the
   single missing cell that would unlock the libation-vs-admin comparison.

## Compliance

Art. V (all claims L2; interpretation gate applied — wording capped below distinct-strata), VII (search
receipt: exactly the preregistered metric/threshold space; zero post-hoc selection entered the verdict),
VIII (document-level permutation inference; effective_n = docs), IX (token budgets on every table row),
XI/XII (registers = physical support; recurrent-word lists derived mechanically; no prior reading used),
XV (no licence earned or touched), XVII (post-hoc labeled non-verdict; append-only), XVIII (A1–A5
declared; A4 realized and reported), XXII (this line). Verdict computed by frozen rule in
`scripts/e014_register_strata.py`; artifacts in `data/register_strata/`.
