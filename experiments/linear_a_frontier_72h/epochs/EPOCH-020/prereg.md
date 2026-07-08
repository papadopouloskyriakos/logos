# EPOCH-020 — PREREGISTRATION (frozen BEFORE any analysis run)

**Campaign:** linear-a-frontier-72h · **§12 dedicated adaptive-null family 2 of 3, gate A.**
**Epoch question:** E017 reported `SITE_ALLOGRAPH_REAL` carried by leg1' restricted to the
RENDERING-INVARIANT topology partition (`INV` = `n_endpoints, n_junctions, n_loops, n_components,
n_strokes`): `T_obs = 0.1767`, doc-level FREE permutation p_holm = 0.0004 over the {p1_INV, p1_SEN,
p2_INV, p2_SEN} family. A free permutation is a good first null but does not match the exact nuisance
structure that could manufacture within<cross-site spread without any real allograph signal: (a) the 5
major sites have wildly unequal document counts (HT 355, KH 189, PH 50, KN 36, ZA 35 — plus a long
tail of 16 minor sites down to n=1), (b) individual signs are attested at very different numbers of
sites (a sign seen at 2 sites cannot generate the same cross-site contrast structure as one seen at 5),
(c) documents vary hugely in "support" (instance count: median 2, range 1–56, right-skewed — 311 of 722
docs have exactly 1 instance). This epoch builds a **matched-marginal restricted permutation** and
re-prices leg1'-INV under it, adding a **per-sign Holm-family false-graduation calibration** the
original epoch did not run.

**Branch:** research/linear-a-frontier-72h · **Seed:** 20260708 · **Date frozen:** 2026-07-08
**Claim layer:** L1 ONLY (sign-form geometry, palaeographic). No phonetic value anywhere; no transfer
licence touched (Art. XV). This epoch does NOT re-open E017's leg2 (doc-level site classification),
which E017 left `CONFOUNDED` (leg2_INV_fire = false in E017; leg2 never fired) — leg2 stays untouched
and unclaimed here.
**Articles triggered:** V (L1 cap), VII (search receipt — every test/threshold enumerated here, nothing
chosen post hoc), VIII (effective_n = documents, never instances), XI/XII (non-circularity: topology
features only, `INV` partition reused unchanged from E009/E017; site labels are SigLA designations,
never a phonetic value; no target-side value ever enters this script), XVII (append-only; deviations in
DEVIATIONS.md + result.json `deviations[]`), XVIII (assumptions below), XXII (this header).

## STEP 0 — inputs (unchanged from E017, reused verbatim)

- Corpus: `data/stroke_corpus/features/instances.json` (identical file, identical `ok`-filter,
  identical `INV`/`SEN` partition — `INV_idx=[0,1,2,3,4]`, `SEN_idx=[5,6,7,8,9]`, same as
  `scripts/epoch009_stroke_corpus.py:26-27` and `epochs/EPOCH-017/prereg.md`).
- Sign/doc frame: identical `F_SIGN` construction (label count ≥3, attested at ≥2 sites with ≥3
  instances at each of those sites) as `scripts/e017_allograph_deconfound.py`.
- Site universe: **all** site labels derived from `site_of(doc)` (not pre-restricted to the top 5) —
  same as E017's leg1 (leg2 alone restricts to the 5 sites with ≥10 eligible docs). Preserving the
  full ~21-label site-size vector is a strict superset of "preserve the 5 major sites" and is more
  conservative, so no information about minor-site imbalance is thrown away.

## STEP 1 — byte-for-byte reproduction (run FIRST, reported before any null)

Rerun E017's exact `leg1_test(Z[:, INV], F_SIGN, inst_doc, by_sign, doc_site_code, N_PERM, rng)` code
path (same data load, same standardization, same seed 20260708) and report `T_obs`. **Must equal
0.1767** (E017 `result.json["leg1_prime"]["INV"]["T_obs"]`) to 4 d.p., else this is logged as a
prereg-blocking discrepancy in DEVIATIONS.md before anything else runs.

## STEP 2 — restricted (matched-marginal) adaptive null (≥200 realizations; primary null)

**Model: support-stratified block permutation of the doc→site label map.**

1. Compute per-document **support** = count of `ok` stroke instances belonging to that document
   (identical quantity already used elsewhere in this pipeline as `n_inst`, e.g. E017's nuisance
   vector `NU`). This is the "document support/length imbalance" axis named in the epoch brief; no
   independent tablet-length field exists in the corpus, so instance-count is the corpus's own
   built-in support proxy — used nowhere else as a target, so this is not circular.
2. Bin all 722 documents into **5 support strata** by fixed count thresholds chosen from the
   corpus's own natural break points (frozen here, not tuned to any test result): `{1}` (n=311),
   `{2}` (n=112), `{3,4}` (n=76), `{5..8}` (n=88), `{9+}` (n=135). Every stratum has ≥76 documents,
   ≫ 5 sites, leaving ample permutation entropy within each stratum.
3. **Restricted permutation**: within each stratum independently, permute the site-label vector among
   only the documents in that stratum (`rng.permutation` per stratum, concatenated back to the full
   722-doc array). This is a permutation of the FULL label vector (so a) overall site sizes are
   preserved exactly, as in any permutation) but additionally (c) it can never place a rich, well-
   attested document into the "slot" of a singleton document or vice versa — the site-label ↔
   document-support joint distribution the real corpus has is preserved by construction, not just
   the free-shuffle's marginal site counts.
4. (b) per-sign site-support is not exactly preserved by construction (a single global doc→site
   permutation cannot exactly fix each of 60 signs' distinct-site-count simultaneously) — instead it
   is **empirically validated**: for every sign in `F_SIGN`, compare the realized distinct-site-count
   across restricted-null draws to (i) the real value and (ii) the free-shuffle null's realized
   distinct-site-count. **Pass condition**: mean |realized − real| under the restricted null must be
   strictly smaller than under the free shuffle, for a majority of `F_SIGN` signs. This is reported as
   a diagnostic, not gated — if it fails, the restricted null is downgraded to "no better matched than
   free shuffle" in the write-up (an honest outcome, not silently dropped).
5. **Realizations**: `M = 10,000` restricted-permutation draws (≥200 required; 10,000 chosen — same
   order as E017's `N_PERM` — for adequate p-value resolution to support a 60-sign Holm family, whose
   first-step threshold is `alpha/60 ≈ 1.7e-4`, unreachable at `M=200`'s floor of `1/201≈0.005`).
   Free-shuffle null (`rng.permutation` over all 722 docs, ignoring strata) is also run at the same
   `M=10,000` as the **weaker comparison** required by the brief (this reproduces E017's original null
   design, one-for-one, for a direct restricted-vs-free contrast).

## STEP 3 — per-sign statistic + Holm-family false-graduation calibration

`leg1_T` is already computed per-sign before being averaged into the aggregate `T`
(`scripts/e017_allograph_deconfound.py:138-152`); this epoch captures the **per-sign vector**
(`T_sign`, one value per `F_SIGN` member, `NaN`/excluded when a sign has no valid within/cross split
under a given label map — same `ok` gate as E017) for the observed map and for all `M` restricted-null
draws.

- Per-sign empirical p: `p_sign = (1 + #{m : T_null_sign[m] ≥ T_obs_sign}) / (M+1)`.
- Holm-adjust the 60-sign family at each draw (see below) and at the real observation.
- **False-graduation rate of the whole per-sign Holm family under the matched null**: for each of the
  `M` restricted-null draws taken in turn as a pseudo-observation, rank its per-sign T against the
  OTHER `M−1` draws (leave-one-out rank; for `M=10,000` the self-inclusion bias from using all `M`
  instead of `M−1` is ≤ 1e-4 and is accepted rather than paying a 10,000× cost blow-up — logged as an
  approximation, not a deviation, since it only makes the calibration *more* conservative), Holm-adjust
  at `alpha=0.01`, and record whether **any** of the 60 signs survives. The fraction of the `M` draws
  that spuriously graduate ≥1 sign is the **false-graduation rate**, which must be reported against
  `alpha=0.01` for calibration (Step 5 below runs the independent synthetic version of this same
  check as the prereg's formal calibration gate).

## STEP 4 — positive control (run before the real-data verdict is trusted; synthetic, known ground truth)

Reuse E017's synthetic-PC scaffold exactly (real document/site/support structure, `F_SIGN`-shaped
sign↔doc incidence, `d_eff=1.2`, `N(0,I_10)` baseline) and add one scenario:
- **S1 (site signal, INV only)** — as E017, offset confined to `INV` indices per site, `d_eff=1.2`.
- **S0 (no site signal at all)** — pure `N(0,I_10)` noise, no per-site offset anywhere (new this
  epoch; E017 had no true fully-null synthetic scenario).
- **POWER**: on S1, the restricted-null (Step 2 model, `M=1,000` for tractability — ≥200 required)
  aggregate adaptive p for `T_obs_INV` must be `<0.01` (null correctly rejected — the matched-marginal
  null does not eat the true signal).
- **CALIBRATION**: on S0, regenerate `R=100` independent synthetic no-signal corpora (fresh random `Z`
  each time, same fixed doc/site/support scaffold and same precomputed `M=1,000` restricted-permutation
  label draws reused across replicates — the permutation set is data-independent). For each replicate,
  compute the per-sign Holm-family graduation indicator (Step 3's procedure, using the replicate's own
  `M=1,000` null distribution) and average across `R=100`. **PC_PASS requires**: power holds AND the
  calibrated false-graduation rate's one-sided 95% Clopper–Pearson upper bound is `≤ 0.05` (5× nominal
  alpha, a deliberately generous tolerance given `R=100` gives coarse resolution on a 0.01 target — NOT
  tightened post hoc; frozen here). PC fail ⇒ verdict `ADAPTIVE_NULL_PC_FAIL`, stop, report as-is.

## Mechanical verdict (frozen; PC fail overrides all)

On the **INV partition** (the one E017 upgraded to L1):
- **SITE_ALLOGRAPH_SURVIVES_ADAPTIVE_NULL** := PC passes AND aggregate adaptive p (restricted null,
  `M=10,000`) for leg1'-INV `< 0.01` AND the per-sign Holm family (Step 3, on the real data) has ≥1
  sign surviving Holm at `alpha=0.01`.
- **ATTENUATED** := PC passes AND aggregate adaptive p `< 0.01` BUT the per-sign Holm family has 0
  surviving signs (the aggregate signal is real under the matched null but too diffuse across signs to
  localize to any individual one at this `effective_n` — an honest intermediate reading, not a pass/fail
  binary).
- **COLLAPSES** := PC passes AND aggregate adaptive p `≥ 0.01` under the restricted null (the E017 free-
  shuffle result does not survive contact with the matched-marginal null — E017's `SITE_ALLOGRAPH_REAL`
  was an artifact of an under-matched null, not of real signal).
- `ADAPTIVE_NULL_PC_FAIL` overrides all of the above (Step 4 fail).
Report the **SEN partition** run through the identical Steps 1–3 **for contrast only** — it carries no
verdict of its own here (E017 already found SEN's leg1 fires too, but SEN was never the upgraded-to-L1
leg; this epoch's job is INV).

## Honest-accounting commitments (verbatim in report regardless of verdict)

- This is a **re-pricing of E017's leg1'-INV finding under a stricter null**, not a new discovery
  channel. A `SURVIVES` verdict does not newly certify anything E017 didn't already claim at L1; a
  `COLLAPSES`/`ATTENUATED` verdict downgrades E017's confidence but does not resurrect the `CONFOUNDED`
  leg2 or touch any transfer licence.
- effective_n = documents (Art. VIII) throughout, matching E017.
- Nothing dropped silently: every stratum's realized document count, every sign's realized-vs-real
  distinct-site diagnostic, and the SEN-partition contrast numbers are reported in `result.json` in
  full, not summarized away.
