# EPOCH-020 — dedicated adaptive-null (family 2 of 3) for E017's leg1'-INV site-allograph positive

**Verdict (INV, the partition E017 upgraded to L1): `SITE_ALLOGRAPH_SURVIVES_ADAPTIVE_NULL`**
(concentrated in 1 of 60 signs — see caveat below; not overturned, but not broadly distributed either).
**SEN partition (contrast only, no verdict claimed): 0/60 signs Holm-survive.**
**E017's leg2 (doc-level site classification) stays `CONFOUNDED`, not re-opened.**
Claim layer: L1 palaeographic only. No transfer licence touched. Plan hash
`9025339523fc34770a95ddcd58673b5f280654d0eadbd0cb19241bb7ab599d79`
(`epochs/EPOCH-020/prereg.md`, frozen before any run). Seed 20260708.

## 1. Reproduction (Step 1)

E017's exact leg1'-INV code path, rerun byte-for-byte: `T_obs = 0.1767`, matching E017's
`result.json["leg1_prime"]["INV"]["T_obs"]` to 4 d.p. exactly. This is the number every downstream
result below re-prices.

## 2. Why a dedicated null

E017's original null was a **free permutation** of the doc→site label vector — a good first check, but
it does not match three nuisance structures the real corpus has: (a) wildly unequal site sizes (HT 355
docs down to 10 sites with n≤2), (b) per-sign site-support (each of the 60 `F_SIGN` signs is attested
at a different number of sites), (c) document-support imbalance (311 of 722 docs have exactly 1 stroke
instance; support ranges 1–56, heavily right-skewed).

**Model built:** a **support-stratified restricted (block) permutation**. Documents are binned into 5
strata by instance-count support (`{1}`, `{2}`, `{3,4}`, `{5..8}`, `{9+}`; 76–311 docs per stratum, all
≫ 5 sites), and the site-label vector is permuted **only within each stratum**. This exactly preserves
overall site sizes (any permutation does) and, by construction, the site-label ↔ document-support joint
distribution the real corpus actually has — something a free shuffle discards. Per-sign site-support
(the third nuisance axis) cannot be fixed exactly by a single global permutation; it was validated
empirically instead (below) rather than assumed.

**Realizations:** `M = 10,000` restricted draws (≥200 required; 10,000 chosen for p-resolution — a
60-sign Holm family's first-step threshold is `α/60 ≈ 1.7e-4`, unreachable at the `M=200` floor of
`1/201 ≈ 0.005`). A free-shuffle null was also run at the same `M=10,000` as the **weaker comparison**
required by the brief — a direct, apples-to-apples restricted-vs-free contrast, not just a citation of
E017's original (differently-sized) run.

**Per-sign site-support diagnostic** (500-draw subsample, both null styles): the restricted null tracks
each sign's real distinct-site-count more closely than the free shuffle for 31 of 60 signs vs 29 of 60
(mean |deviation| 1.63 vs 1.67). **This passes the prereg's majority bar, but only barely (31/60, not a
strong margin)** — reported honestly rather than oversold; the restricted null is a modest, not dramatic,
improvement on this specific axis, even though it is a large improvement on (a)/(c) by construction.

## 3. Positive control (Step 4, run and passed BEFORE the real-data verdict was trusted)

Synthetic scaffold: real document/site/support structure, `F_SIGN`-shaped sign↔doc incidence,
`N(0,I_10)` baseline, `d_eff = 1.2` (same convention as E017).

| Check | Result |
|---|---|
| **Power** (S1: site signal planted in `INV` only) | `T_obs = 1.3555`, adaptive `p = 0.000999` → **fires** (restricted null does not eat a true signal) |
| **Calibration** (S0: zero site signal, R=100 independent synthetic corpora) | per-sign Holm-family false-graduation rate = **0/100**, one-sided 95% Clopper–Pearson upper bound = **0.0005** ≤ 0.05 target → **passes** |

`PC_PASS = true`. The adaptive-null + per-sign-Holm pipeline has power to detect a real site signal
confined to topology features and does not spuriously graduate signs on pure noise.

## 4. Main result — INV partition (the one E017 upgraded to L1)

| Quantity | Restricted (matched) null | Free-shuffle null (weaker comparison) |
|---|---|---|
| T_obs | 0.1767 | 0.1767 |
| null T mean | 0.0014 | 0.0004 |
| null T p95 | 0.0663 | 0.0568 |
| null T max (10,000 draws) | 0.1452 | 0.1304 |
| adaptive p | 0.0001 (floor of 1/10,001) | 0.0001 (floor) |

The observed `T_obs = 0.1767` exceeds the **maximum** of 10,000 matched-marginal null draws
(0.1452) — a substantially wider margin than the null's own p95 (0.0663). The aggregate signal
survives the stricter, matched null cleanly; it is not an artifact of the free shuffle's cruder
matching.

**Per-sign Holm family (Step 3):** of 60 `F_SIGN` signs, sorted p-values start
`0.0001, 0.0002, 0.006, 0.007, 0.0101, …` — only the single smallest (`p=0.0001`, itself at the
`M=10,000` resolution floor) clears the Holm bar at `α=0.01`; the second-smallest (`p=0.0002`) just
misses the rank-2 Holm threshold (`α/59 ≈ 1.695e-4`). **1 of 60 signs Holm-survives.**
**False-graduation rate of the whole per-sign Holm family under the matched null** (leave-one-out
calibration over 2,000 restricted-null draws, real `INV` feature values): **0.0000** — the family does
not spuriously graduate signs under the null, so the 1 real survivor is not multiple-testing noise.

**Honest reading:** the *aggregate* leg1'-INV statistic is robust to the stricter null (not an
artifact of under-matching) — `SITE_ALLOGRAPH_SURVIVES_ADAPTIVE_NULL`. But the effect is **not
broadly distributed across the sign inventory**: only one sign individually clears a well-calibrated
Holm bar, with a second sign close behind. This is a materially more precise (and more modest)
characterization than E017's aggregate-only report could give — E017 could not distinguish "many
signs each weakly site-coherent" from "one or two signs carrying the whole aggregate," and this
epoch resolves that in favor of the latter.

## 5. SEN partition — contrast only, no verdict

| Quantity | Restricted null |
|---|---|
| T_obs | 0.1445 |
| null T mean / p95 / max | 0.0327 / 0.0910 / 0.1687 |
| adaptive p | 0.0011 |
| signs Holm-surviving | **0 / 60** |
| false-graduation rate (matched null) | 0.0000 |

SEN's aggregate p also beats 0.01 under the matched null, but **zero** signs individually survive
Holm — a weaker, more diffuse signal than INV's, consistent with SEN being the rendering-sensitive
partition E017 never claimed L1 on. Reported for contrast only; this epoch issues no verdict on SEN.

## 6. What this epoch does NOT do

- Does not re-open E017's leg2 (document-level site classification via nearest-neighbor embedding),
  which E017 left `CONFOUNDED` (`leg2_INV_fire = false`, balanced accuracy below the nuisance
  comparator). That confound is untouched here.
- Does not raise the claim layer past L1 or touch any transfer licence (Art. XV) — this is
  palaeographic sign-form geometry, not a reading.
- Does not certify photograph-level or scribe-level truth — E017's Step-0 source audit
  (photographs and a second rendering both `SOURCE_BLOCKED`) still applies; this epoch inherits that
  ceiling unchanged.
- Is a **re-pricing** of an existing L1 finding under a stricter null, not a new discovery channel.

## 7. Deviations (Art. XVII)

One deviation, logged in `epochs/EPOCH-020/DEVIATIONS.md`: a bug in the first-draft
`holm_survives_any` helper (required *all* 60 signs in a family to individually pass their Holm
threshold, instead of counting survivors via the correct step-down rule) was caught and fixed
**before** `result.json` was ever written by the buggy version — no published result was affected,
this is a pre-result bugfix, not an erratum. All numbers in this report are from the corrected code.

## Artifacts

- `epochs/EPOCH-020/{prereg.md,plan_hash.txt,result.json,DEVIATIONS.md}`
- `scripts/e020_allograph_adaptive_null.py`
- `data/allograph_adaptive_null/persign_detail.json` (full per-sign p-value vectors, INV and SEN)
