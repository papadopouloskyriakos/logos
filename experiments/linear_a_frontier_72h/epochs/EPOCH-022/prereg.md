# EPOCH-022 — PREREGISTRATION (frozen BEFORE any analysis run)

**Campaign:** linear-a-frontier-72h · **§12 dedicated adaptive-null family 3 of 3, gate A.**
**Epoch question:** the campaign's one genuinely LA-side positive is **A- prefixation**
(word-initial productive-stem productivity on GORILA words: E015 confirmatory test, obs=47
distinct recurring stems, `A|PRE`). E015's own null (`e015_lib.null_pvals` / `synth_corpus`,
sign-unigram-weighted i.i.d. resample, n_null=2000) already gave p=0.0005, but (a) that null was
built and interpreted *inside* E015, which also ran a PC-LB gate that came back vacuous
(`MACHINERY_UNINFORMATIVE`) — A- was reported "not gate-licensed"; (b) it is a with-replacement
resample, not an exact-multiset-preserving null; (c) it was never priced against the alternative
"A- was the best of the U(LA) candidate universe" (71 other candidates were scanned in the SAME
epoch, exploratory-only, Holm 0.05, 0/71 survived — but A- itself was never run through that same
family-wise machinery, only judged alone since it was the pre-registered confirmatory target).
§12 requires a **third, independent, dedicated adaptive-null family** (≥200 realizations) for
this positive, built fresh and interpreted independent of E015's vacuous PC-LB gate. This epoch
supplies it.

**Branch:** research/linear-a-frontier-72h · **Seed:** 20260708 · **Date frozen:** 2026-07-08
**Claim layer:** L2/L3 (positional affix slot — no phonetic value, no language, sign identities
anonymous in interpretation though real GORILA sign labels are used mechanically as opaque IDs,
exactly as E015 did). No transfer licence touched (Art. XV). This epoch does **not** re-open
E015's PC-LB vacuity (A- stays reported-not-gate-licensed at the morphology-**recovery** level);
it prices A-'s **own** null directly, on real LA data, independent of that gate.
**Articles triggered:** V (L2/L3 cap), VII (search receipt below), VIII (effective_n = distinct
GORILA words / real candidate-universe size, not raw sign count), IX (adaptive p + null mean/p95
+ deflated p reported side-by-side), XI/XII (non-circular: no phonetic value anywhere; GORILA
sign labels are corpus-native opaque tokens, not IPA/values — identical convention to E015/E1;
positive-control uses an out-of-alphabet synthetic marker, never a real sign), XVII (append-only
— E015's `result.json` untouched; this is a declarative re-pricing, cross-referenced both ways),
XVIII (assumptions below), XXII (this header + compliance line).

## Search receipt (Art. VII)

Exactly **2** prior epochs computed a null-priced statistic for `A|PRE` productivity on GORILA
words: **E1** (relphono campaign, original discovery, adaptive p .008) and **E015** (this
campaign, replication + marginalization robustness, GORILA-anchor p 0.0005, obs 47, null_mean
24.9/24.947). **K=2** independent prior architectures. No hyperparameter sweep occurs *within*
this epoch's own null design (all thresholds below are frozen once, pre-run, not tuned to the
outcome). Where a family-wise (72-candidate) deflation is computed (Step 3), it is reported as
its own explicit number, not folded into K.

## STEP 0 — inputs (reused verbatim from E015/E1, not re-derived)

- Corpus: `corpus/silver/inscriptions_structured.json`, loaded via `e015_lib.load_la_docs()`
  (618 docs, ≥2 signs each).
- Word list: **GORILA words** (`e015_lib`'s `gorila_words(docs)` — the human-transliterated word
  boundaries, i.e. the corpus's own segmentation, not any epoch-induced one). n=2424 words.
- Candidate universe: `e015_lib.candidate_universe(words_gorila, min_att=10)` — (sign,PRE/SUF)
  pairs with ≥10 attestations on GORILA words. **Frozen deterministic function, reused
  unchanged.** Expected n=72 (71 scanned in E015 + `A|PRE` itself, matching E015's
  `universe_n_gorila_full=72` / `universe_n_scan=71`); logged as a blocking discrepancy in
  DEVIATIONS.md if it differs.
- Productivity statistic: `e015_lib.productivities(words, targets)` — for prefix candidate
  `(s,PRE)`: number of DISTINCT stems `t` such that a word `s+t` exists, where `t` is either
  itself an attested word or recurs ≥2× as a residual elsewhere in the corpus (E1's exact
  "recurrent stem" criterion). **Frozen deterministic function, reused unchanged.**

## STEP 1 — byte-for-byte reproduction (run FIRST, reported before any null)

Rerun `e015_lib.null_pvals(gorila_words(docs), [("A","PRE")], n_null=2000, seed=20260708+100)`
exactly as E015's `e015_la.py` calls it. **Must equal** `obs=47`, `null_mean≈24.947`,
`p≈0.0004998` (E015 `data/marginalized_morph/la_application.json
→ a_prefix_confirmatory.gorila_anchor`) to reported precision, else logged as a prereg-blocking
discrepancy in DEVIATIONS.md before anything else runs.

## STEP 2 — dedicated adaptive null (≥200 realizations; PERMUTE primary, BOOTSTRAP weaker comparison)

**Nuisance structure to preserve** (exactly the brief's three axes): LA sign-unigram frequency,
word-length distribution, document/word-count structure. Since `productivities()` operates on the
GLOBAL pooled GORILA word multiset (no per-document computation), "document/word-count structure"
reduces to: same total word count, same per-word length, same word→document assignment (order),
with only sign IDENTITY randomized.

**PERMUTE null (primary, exact-multiset-preserving)**: pool every sign token across all 2424
GORILA words (5069 tokens total); draw a uniform random permutation of the pooled token list
(`rng.shuffle`); re-chop into words using the ORIGINAL, unchanged per-word length sequence in
original word order. This is a bijection of the same multiset onto the same slot sizes: LA
sign-unigram frequency is preserved **exactly** (not approximately — every real token used
exactly once, globally, as in the real corpus), word-length distribution is preserved **exactly**
(slot sizes literally unchanged), word count and word→document assignment are untouched. This is
strictly stronger than E015's own null (which drew tokens **with replacement**, weighted by
unigram frequency — an approximation of the same target distribution, with added sampling noise).

- **Realizations**: `M = 5,000` (≥200 required; 1,000+ requested if cheap — benchmarked at
  ~2.4 ms/realization for the full 72-candidate `productivities()` pass, so 5,000 is ≈12 s,
  cheap; frozen here, not raised post hoc for resolution reasons the way E018 logged).
- For every realization, compute `productivities(synthetic_words, U_full)` for **all 72**
  candidates in `U_full` in one pass (needed for Step 3's family deflation), and record the
  `A|PRE` value for the single-confirmatory null distribution.

**BOOTSTRAP null (weaker comparison, NOT confirmatory, reproduces E015's own null design
independently)**: `e015_lib.synth_corpus` (i.i.d.-with-replacement draw from the sign-unigram,
same word-length profile), `N = 2,000` realizations, same 72-candidate pass. Reported side by
side with PERMUTE; if the two disagree materially, that is itself reported honestly (a
sensitivity gap, not resolved in either null's favor by fiat).

## STEP 3 — adaptive / search-adjusted pricing of A- (single-confirmatory AND best-of-family)

- **Single-confirmatory adaptive p** (frozen definition): under PERMUTE, `p_single = (1 +
  #{realizations with A|PRE productivity ≥ 47}) / (1 + M)`. This is the number that answers "is
  A- significant, given it was pre-registered as the ONE confirmatory affix" (no multiplicity
  correction — matches how E1/E015 originally reported it).
- **Best-of-family deflated p** (frozen definition, THREE convergent estimators, all computed
  from the SAME `M=5,000` PERMUTE pool, no re-running):
  1. **Bonferroni**: `min(1, 72 × p_single)`.
  2. **Holm step-down**: raw per-candidate `p_c = (1 + #{null_c ≥ obs_c}) / (1+M)` for all 72
     candidates on real data; `e015_lib.holm()` (reused unchanged) gives the Holm-adjusted p for
     `A|PRE`.
  3. **maxT permutation (primary/most-correct estimator)**: for every candidate `c`, standardize
     each realization's value `z_{j,c} = (V_{j,c} − mean_c) / max(sd_c, 1e-9)` using the pool's
     own per-candidate mean/sd (`sd_c=0` degenerate cases flagged in `result.json`, `z` treated as
     0 for those draws' contribution unless `V≠mean`, in which case a fallback direct-count p is
     reported alongside instead of a z-based one — logged explicitly, not silently patched); the
     family test statistic per realization is `M_j = max_c z_{j,c}` over the 72-candidate family
     (this IS the maxT null, no separate simulation needed — reuses Step 2's pool). Price A-'s own
     standardized value `z_A = (47 − mean_A)/sd_A` against `{M_j}`:
     `p_maxT = (1 + #{M_j ≥ z_A}) / (1+M)`.
  This directly answers "what would A-'s p have been if it had been selected post-hoc as the
  single best-looking candidate out of the 72 tried" — the family-false-graduation-rate framing
  the brief asks for, expressed as a p-value rather than a binary rate (equivalent formulation:
  `p_maxT` IS the probability, under the null, that the family's best candidate reaches at least
  `z_A`).

## STEP 4 — positive control (run and interpreted BEFORE the real-data pricing above is trusted)

**PC-power** — plant a KNOWN productive prefix into a synthetic LA-matched corpus:
- Construct a synthetic corpus of `n=2424` words matching the real GORILA per-word-length
  distribution exactly. `K_STEMS=45` distinct 1–2-sign stems (drawn i.i.d. from the REAL
  sign-unigram, matching realistic LA residual lengths) are each used in exactly 2 words prefixed
  by an **out-of-alphabet synthetic marker** `"__PLANT__"` (never a real sign ID — Art. XI/XII
  non-circularity, matches E018's "synthetic PC uses arbitrary integer sign IDs, never real
  values" convention). This guarantees `productivities` counts exactly `K_STEMS=45` distinct
  recurring stems for `__PLANT__|PRE` by construction (deterministic ground truth). Remaining
  `2424 − 90 = 2334` words are filled i.i.d. from the real sign-unigram at real GORILA lengths
  (no `__PLANT__` token anywhere outside the 90 planted words).
- For each of **25 independent seeds** (fresh stem draws + fresh filler draws), build this
  planted corpus, then run the SAME PERMUTE null (M=300 realizations — ≥200 required, per-seed) on
  it, and compute `p_plant` for `__PLANT__|PRE`.
- **Power pass condition**: ≥80% of the 25 seeds (≥20/25) achieve `p_plant ≤ 0.01`.

**PC-calibration** — no-prefix synthetic corpus, family false-graduation rate ≤ alpha:
- `R = 300` (≥200 required) INDEPENDENT fresh PERMUTE draws of the REAL GORILA corpus (same
  mechanism as Step 2, fresh RNG stream, disjoint from the `M=5,000` reference pool — no
  self-inclusion) are each treated as a pseudo-observed corpus with **no true prefix structure**
  (by construction of the permutation, there is no real word-initial dependency in these draws).
  Each of the 300 is scored against the Step-2 `M=5,000` PERMUTE pool as null reference: compute
  its own 72 raw candidate p-values (using the SAME reference-pool counting formula as Step 3),
  Holm-adjust at `alpha=0.01`, and record whether **any** of the 72 candidates spuriously
  survives Holm.
- **Calibration pass condition**: false-graduation rate over the 300 draws has a one-sided 95%
  Clopper–Pearson upper bound `≤ 0.05` (5× nominal alpha — same generous-but-frozen tolerance
  E020 used for an `R=100` calibration; `R=300` here gives finer resolution on the same target).

`PC_PASS := power_pass AND calibration_pass`. **PC fail overrides everything below — verdict
becomes `HARNESS_NOT_VALIDATED`, no A- claim from this epoch's null (fail-closed).**

## Mechanical verdict (frozen; PC fail overrides all)

Given `PC_PASS = true`:

- **`A_PREFIX_SURVIVES_ADAPTIVE_NULL`** := `p_single ≤ 0.01` AND `p_maxT ≤ 0.05` (best-of-family
  deflated significance also clears a family-wise bar).
- **`A_PREFIX_SURVIVES_CONFIRMATORY_BUT_NOT_BEST_OF_FAMILY`** := `p_single ≤ 0.01` AND
  `p_maxT > 0.05` (the pre-registered confirmatory reading holds, but A- would NOT have survived
  had it been chosen post-hoc as the best of the 72-candidate universe — the classic
  "pre-registration is load-bearing" outcome).
- **`A_PREFIX_COLLAPSES`** := `p_single > 0.01` (the E1/E015 result does not survive contact with
  the exact-multiset PERMUTE null — an under-matched-null artifact, not a real LA-side signal).

Given `PC_PASS = false`: **`HARNESS_NOT_VALIDATED`** (no verdict on A- from this epoch).

## Honest-accounting commitments (verbatim in report regardless of verdict)

- This is a **re-pricing** of E1/E015's A- finding under a stricter, independently-built null, not
  a new discovery channel and not a claim-layer promotion. A `SURVIVES` verdict does not newly
  license anything beyond E015's own L2/L3 ceiling; it does not reopen or resolve E015's vacuous
  PC-LB gate (morphology-**recovery** licensing stays untouched — A- remains
  reported-not-gate-licensed at that level regardless of this epoch's outcome).
- Both `p_single` (PERMUTE) and the BOOTSTRAP-null comparison are reported in full even though
  BOOTSTRAP is explicitly the weaker, non-confirmatory arm — no cherry-picking between them.
- The three best-of-family estimators (Bonferroni / Holm / maxT) are reported together; if they
  disagree, the disagreement is reported, not resolved by silently preferring the most favorable
  one. `p_maxT` is designated primary in the prereg (most statistically correct — accounts for
  cross-candidate correlation that Bonferroni/Holm ignore) BEFORE any number is computed.
- Sign identities remain the corpus's own opaque GORILA labels throughout (as in E1/E015); no
  phonetic value, no language identification, no reading. Claim ceiling L2/L3 (Art. V); no
  transfer licence touched (Art. XV).

## Deviations protocol (Art. XVII)

Any departure from the above (parameter change, formula change, additional post hoc test) is
logged in `epochs/EPOCH-022/DEVIATIONS.md` and in `result.json["deviations"]`, and is
`POSTHOC_CHARACTERIZATION`, never the primary verdict.
