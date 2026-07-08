# EPOCH-022 — dedicated adaptive-null family for A- prefixation (Constitution §12, family 3 of 3, gate A)

**Verdict (mechanical): `A_PREFIX_SURVIVES_ADAPTIVE_NULL`.** PC_PASS = True (power 25/25 seeds at
p≤0.01, calibration false-graduation 0/300, CP-upper-95% 0.0099 ≤ 0.05). Single-confirmatory
adaptive p (PERMUTE, exact-multiset null) = **0.0002** (0/5,000 draws ≥ observed). Best-of-72
deflated p: **maxT (primary) = 0.0002**, Bonferroni/Holm = 0.0144 — both clear the frozen
family-wise bar (`p_maxT ≤ 0.05`). A- is the third and final of the campaign's three required
dedicated adaptive-null families (E018 decomposition channel, E020 site-allograph topology, this
epoch A- prefixation).

**Stage header (Art. XXII).** Articles triggered: V (L2/L3 cap — positional affix slot only, no
phonetic value, no language), VII (search receipt: K=2 prior epochs computed this exact statistic
— E1 original discovery, E015 replication+marginalization; no hyperparameter sweep within this
epoch itself), VIII (effective_n = the 72-candidate frozen universe and the 2,424-word corpus, not
raw sign count), IX (adaptive p, null mean/p95/max, and the deflated best-of-family p reported
side by side on every number), XI/XII (non-circular: GORILA sign labels are the corpus's own
opaque tokens exactly as E015 used them — no phonetic value anywhere; the positive control's
planted "prefix" is an out-of-alphabet synthetic marker `__PLANT__`, never a real sign, matching
E018's "arbitrary integer sign IDs, never real values" convention), XVII (append-only — E015's
`result.json` untouched; one pre-result deviation logged in `DEVIATIONS.md`), XVIII (open
limitations noted below), XXII (this header + compliance line). Plan hash
`5b4547602f9e908a357c3851d44d464f41f8ee140545ee65d5ff26cba2556c3a` (`epochs/EPOCH-022/prereg.md`,
frozen before any run). Seed 20260708.

## 1. Reproduction (Step 1) — byte-for-byte

`e015_lib.null_pvals(gorila_words, [("A","PRE")], n_null=2000, seed=20260708+100)` rerun exactly:
`obs=47`, `null_mean=24.947`, `p=0.0004998` — matches E015's `la_application.json →
a_prefix_confirmatory.gorila_anchor` to full reported precision (`match: true` in `result.json`).
This is the number this epoch re-prices under a stricter, independently-built null.

## 2. Why a dedicated null, independent of E015's own

E015's original null (`e015_lib.synth_corpus`) draws each corpus word i.i.d.-**with-replacement**
from the sign-unigram distribution, matching word lengths. This is a good first null but (a) it is
a *resample*, not an exact bijection of the real corpus's own token multiset — it adds sampling
variance the real corpus does not have — and (b) A- was never priced against the same 71-candidate
universe E015's own exploratory scan tried, only judged alone as the confirmatory target. §12
requires a null built fresh for this specific positive and interpreted independent of E015's own
(vacuous) PC-LB gate.

**PERMUTE null (primary, exact-multiset-preserving).** Pool every sign token across all 2,424
GORILA words (5,069 tokens total); draw a uniform random permutation of the pooled token list;
re-chop into words using the ORIGINAL, unchanged per-word length sequence in original word order.
This is a bijection of the same multiset onto the same slot sizes: LA sign-unigram frequency is
preserved **exactly** (every real token used exactly once, globally — not approximated by a
frequency-weighted resample), word-length distribution is preserved **exactly** (slot sizes
literally unchanged), and word count / word→document assignment are untouched (the
"document/word-count structure" nuisance axis the brief names). Only sign IDENTITY at each
position is randomized — strictly stronger than E015's own null.

**Realizations:** `M = 5,000` (≥200 required; the brief's "≥1,000 if cheap" — benchmarked at
≈2.4 ms/realization for the full 72-candidate pass, so 5,000 costs ≈12 s; frozen in the prereg,
not raised post hoc). A **BOOTSTRAP** weaker comparison (`e015_lib.synth_corpus`, `N=2,000`,
independently reimplemented and reseeded, not reused from E015's stored numbers) is reported
alongside, never confirmatory.

| | PERMUTE (primary, M=5,000) | BOOTSTRAP (weaker comparison, N=2,000) |
|---|---|---|
| null mean | 24.532 | 24.833 |
| null sd | 3.990 | 4.227 |
| null p50 / p95 / max | 24 / 31 / **39** | 25 / 32 / **39** |
| **observed (real) A\|PRE productivity** | **47** | **47** |
| raw adaptive p | **0.0002** (0/5,000 ≥ 47) | **0.0005** (0/2,000 ≥ 47) |
| lift over null mean | 1.92× | 1.89× |

The observed value (47) exceeds the **maximum** of both 5,000 PERMUTE draws and 2,000 BOOTSTRAP
draws (both cap at 39) by 8 stems — a clean, non-marginal separation. The two null designs agree
closely (means 24.5 vs 24.8, both p at their respective Monte-Carlo floors): the
exact-multiset-vs-resample distinction makes little practical difference at this effect size,
exactly as E018 found for its own PERMUTE/BOOTSTRAP comparison. **Single-confirmatory adaptive
p = 0.0002** (PERMUTE, primary).

## 3. Best-of-family deflation — "what if A- had been the best of 72 candidates tried?"

The brief requires pricing A- as if it had been selected post hoc as the best-looking candidate
out of the full frozen GORILA universe (`U_full`, 72 candidates: A|PRE + the 71 E015 scanned
exploratorily). Three convergent estimators, all computed from the SAME `M=5,000` PERMUTE pool
(no re-running):

| Method | Deflated p for A\|PRE |
|---|---|
| **Bonferroni** (`72 × p_single`) | 0.0144 |
| **Holm step-down** (`e015_lib.holm`, reused unchanged) | 0.0144 |
| **maxT permutation** (primary — accounts for cross-candidate correlation) | **0.0002** |

A|PRE is the smallest raw p by a wide margin among all 72 candidates (next-closest: `ME|SUF`
p=0.0122, `RA|SUF` p=0.0364 — see table below), so Holm's step-down collapses to the
single-step Bonferroni bound here. **Bonferroni/Holm alone would place A- at p=0.0144** — still
clears the secondary family bar (0.05) but NOT the primary confirmatory bar (0.01) taken in
isolation; a researcher relying only on that conservative, independence-assuming bound might read
A- as "surviving the family test only weakly." The **maxT** estimator — which uses the empirical
joint null distribution of *all 72 candidates together* (72-dimensional per-realization max of
standardized scores) rather than assuming independence — tells a sharper story: A-'s own
standardized deviation (`z_obs = 5.63`) exceeds the **maximum** of 5,000 draws of "the single most
extreme candidate across all 72" (empirical max-z null: mean 2.54, sd 0.51, **max 5.19**). In
5,000 joint draws, no candidate — real or synthetic-position — ever reaches z=5.63 by chance, so
`p_maxT` sits at the same Monte-Carlo floor as the single-confirmatory p (0.0002). **Both numbers
are reported honestly, not resolved in the more favorable direction by fiat**: Bonferroni is a
valid, conservative upper bound (0.0144, still < 0.05); maxT is the statistically correct
estimator for this specific, correlated candidate family and gives a much sharper answer (0.0002).
Per the frozen classification rule (`p_maxT ≤ 0.05`), A- clears the family-wise bar cleanly.

**Top of the 72-candidate family, ranked by raw PERMUTE p** (A- is not close to its nearest
competitor):

| candidate | obs | null mean | raw p | Holm p |
|---|---|---|---|---|
| **A\|PRE** | **47** | 24.53 | **0.0002** | **0.0144** |
| ME\|SUF | 12 | 6.10 | 0.0122 | 0.866 |
| RA\|SUF | 22 | 15.53 | 0.0364 | 1.0 |
| I\|PRE | 28 | 21.34 | 0.0526 | 1.0 |
| JU\|SUF | 9 | 5.15 | 0.0580 | 1.0 |

## 4. Positive control (Step 4, run and interpreted BEFORE the real-data pricing above was trusted)

**PC-power.** 25 independent synthetic "LA-matched" corpora (2,424 words each, real GORILA
per-word-length distribution, real sign-unigram for filler), each with a KNOWN productive prefix
planted on an out-of-alphabet marker `__PLANT__` attached to `K_STEMS=45` distinct genuinely
recurring stems (guaranteed deterministically — see Deviations D1 below for a pre-result fix to
this construction). Each planted corpus scored against its own `N=300` PERMUTE null.

| Check | Result |
|---|---|
| obs_plant (all 25 seeds) | **45/45** (deterministic, matches K_STEMS exactly) |
| p_plant (all 25 seeds) | **0.0033** (0/300 null draws ≥ 45) |
| Seeds at p ≤ 0.01 | **25/25 = 100%** (pass bar: ≥80%) |

**PC-calibration.** 300 fresh, independent PERMUTE draws of the REAL corpus (disjoint RNG stream
from the M=5,000 reference pool — no self-inclusion) — by construction of the permutation
mechanism, none of these 300 have any true word-initial dependency (pure H0). Each is scored
against the M=5,000 reference pool across all 72 candidates, Holm-adjusted at α=0.01, and checked
for ≥1 spurious survivor.

| Check | Result |
|---|---|
| R (fresh no-prefix draws) | 300 |
| False graduations (≥1 of 72 candidates Holm-survives) | **0/300** |
| False-graduation rate | 0.0000 |
| One-sided 95% Clopper–Pearson upper bound | **0.0099** |
| Pass bar | ≤ 0.05 |

`PC_PASS = power_pass (True) AND calibration_pass (True) = True`. The dedicated null has power to
detect a real planted prefix at LA's own scale and does not spuriously graduate any of the 72
real candidates under its own no-signal draws — the machinery is trusted before the real result
above is interpreted.

## 5. Mechanical verdict

Per the prereg's frozen rule: `PC_PASS=True`, `p_single=0.0002 ≤ 0.01`, `p_maxT=0.0002 ≤ 0.05` →

**`A_PREFIX_SURVIVES_ADAPTIVE_NULL`**

A- prefixation survives (a) an independently-built, exact-multiset-preserving null strictly
stronger than E015's own resample null, (b) the weaker BOOTSTRAP comparison at essentially
identical strength, and (c) pricing as the best of the full 72-candidate GORILA universe under the
statistically correct (correlation-aware) maxT estimator — though the cruder Bonferroni/Holm bound
alone (0.0144) is a useful honest caveat: A- is not so extreme that it would survive *any*
conceivable multiplicity correction at the strictest 0.01 bar without the more precise maxT
treatment.

## 6. What this epoch does NOT do

- Does **not** reopen or resolve E015's PC-LB gate. That gate stayed `MACHINERY_UNINFORMATIVE`
  (vacuous 30%-TEST target); A- remains **reported, not gate-licensed** at the
  morphology-**recovery** level (i.e., "can a marginalized/frozen segmentation pipeline recover a
  known affix from scratch on held-out LB" is still unanswered). This epoch answers a narrower,
  independent question: "does A-'s own significance survive a stricter, dedicated null, priced
  against the real candidate universe it was drawn from." Both statements are true simultaneously
  and are not in tension.
- Does **not** raise the claim layer past L2/L3 (Art. V) or touch any transfer licence (Art. XV):
  this is a positional affix slot on the corpus's own opaque sign labels — no phonetic value, no
  language identification, no reading.
- Does **not** assign new significance to any of the other 71 candidates — none survive Holm at
  this or any prior epoch's bar; A- remains the SOLE validated LA affix.
- Is a **re-pricing** of an existing positive under a stricter null (§12's third and final
  required family for this campaign), not a new discovery channel.

## 7. Open limitation (Art. XVIII)

The PERMUTE null randomizes sign identity across ALL word slots globally (not within-document or
within-site), so it cannot detect a confound that operates at the document or site level (e.g., a
scribal/administrative convention that concentrates A-initial words in a handful of documents for
reasons unrelated to morphology — see the campaign's own site-allograph findings, E017/E020, for
evidence that LA sign distribution IS site-structured in other respects). This null answers "is
the aggregate corpus-wide productivity pattern explicable by unigram frequency and word-length
alone" — a clean, necessary, but not sufficient bar; a stratified (site- or document-matched)
null is a natural successor test, exactly analogous to E020's stratified null for the
site-allograph channel.

## 8. Deviations (Art. XVII)

**D1 (pre-result fix, not an erratum)** — the prereg's PC-power construction ("each used in
exactly 2 words prefixed by `__PLANT__`... guarantees... by construction") was implemented
literally at first (two byte-identical planted words), but `productivities()` dedupes the word
list into a `set` before computing recurrence, so identical duplicates collapse to one and do NOT
mechanically guarantee `rc[stem]≥2`. Caught and fixed — inserting the bare stem as its own
standalone word instead, satisfying the `t in wset` branch of the recurrence test directly — before
`result.json` was ever finalized (same status as E020's own pre-result bugfix: the first-pass
flawed run already showed `power_pass=True`, `obs_plant` 30–37, `p_plant≈0.0033`; the corrected run
gives the intended deterministic `obs_plant=45` on all 25 seeds, same `p_plant`, same
`power_pass=True`). No threshold, null design, or verdict rule was altered. Full detail in
`epochs/EPOCH-022/DEVIATIONS.md`.

## Artifacts

- `epochs/EPOCH-022/{prereg.md,plan_hash.txt,result.json,DEVIATIONS.md}`
- `scripts/e022_aprefix_adaptive_null.py`
- `data/aprefix_adaptive_null/{calibration_detail.json,power_detail.json,permute_null_pool_A.json,family_top10.json}`
