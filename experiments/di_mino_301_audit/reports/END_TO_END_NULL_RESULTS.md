# END-TO-END ADAPTIVE NULL — RESULTS

**Campaign:** Di Mino `*301=/na/` exact audit · **Constitution** v2.2 · **Seed** 20260708
**Generator:** `scripts/end_to_end_null.py` · **Data:** `data/results/end_to_end_null.json`
**Spec:** `reports/END_TO_END_NULL_SPEC.md` · **Binding:** `reports/VERDICT_FRAMING_CONSTRAINTS.md`
All numbers below are RUN, not asserted. Value space is enumerable (13 onset outcomes drive the root
skeleton) → **exact** rates reported alongside Monte-Carlo estimates with CIs.

## 1. Headline

> **The whole adaptive pipeline manufactures a match at least as strong as the observed
> `/na/ → N-W-Y → "dwell"` chain on essentially every null run.** End-to-end false-positive rate =
> **1.0** under best-of-value+collapse+language search (free semantic target, as actually chosen
> post-hoc); **0.769** per single random value even before the language search. The observed chain is
> **statistically indistinguishable** from the null on the lexical/gloss legs.

Because the **positive controls PASSED** (PC3 recovers a planted sign value at rank **1/113**; the pipeline
demonstrably *can* find a real signal), a null-indistinguishable observed result is a **genuine negative**,
not a dead detector.

## 2. End-to-end false-positive rate (the whole pipeline)

| Statistic | Value | 95% CI | Reading |
|-----------|-------|--------|---------|
| **PRIMARY** — free-target, best-of-search FP | **1.000** | — | the search ALWAYS lands a coherent real-root exact reading |
| PRIMARY — free-target, per single random value | **0.769** | [0.497, 0.918] Wilson | 10/13 onsets already manufacture one |
| MC random-uniform, M_gloss_free | 0.735 | [0.670, 0.791] | N=200 realizations |
| MC frequency-matched, M_gloss_free | 0.850 | [0.794, 0.893] | N=200 (Packard-band weights) |
| conservative — dwell target pre-committed, per random value | 0.077 | [0.034, 0.102] | only onset `n` reaches dwell on the narrow LA axis |
| conservative — dwell, best-of-6-languages (target skeleton) | 0.750 | — | 3/4 load-bearing langs gloss n-w-y habitation-tier |
| conservative — dwell hit over the **logged** root/gloss search | **1.000** | — | 7,800 logged cells → a dwell-tier hit is CERTAIN |
| strict — value-graduation FP (M_gate, PC-calibrated) | ~0.006 | Clopper–Pearson ≤1.54% | best-of random maps; **/na/ does not clear it** |

**Interpretation.** The reading's only novel free parameter is `*301=/na/`, but the pipeline that turns a
value into "dwell" rides many more adaptive freedoms: best-of-65 value, best-of-4 segmentation,
best-of-5 collapse (III-y/-h/-'/-w/hollow), best-of-6 language, and gloss polysemy (~3.6 senses/root),
then a **post-hoc semantic target**. Under the null these freedoms manufacture a coherent
value→real-root→exact-gloss chain with probability ≈ 1. The observed chain is one such manufactured chain.

## 3. Leg-by-leg (all adaptive choices reproduced)

- **Random / frequency-matched *301 value** (Packard band-preserving): the 65 CV grid collapses to 13
  distinct onset outcomes for the root skeleton → enumerated exactly + MC-sampled. `/na/` S_lex rank =
  **21/65** (49th pctile, **below** the Packard null mean 0.667 < 0.752). `/na/` is **not** even best-of-value.
- **Best-of-value search:** **10/13** onsets already yield a real Semitic weak/hollow root with a concrete
  citable gloss → best-of-search success = **certain**.
- **Random segmentation** + best-of-4 families: **80.8%** of random cut sets still isolate a scorable
  (≥2-consonant) *301-bearing root; the segmentation degree of freedom is nearly free.
- **Random roots / fake lexica (L_fake) / wrong-language lexica:** edit-distance "match-exists" channel is
  **NO_POWER** — frozen canary L_fake floor **1.00**, Packard-permuted **1.00**; independent reconstruction
  here **0.99**. A near-match to n-w-y is guaranteed in any dense Semitic-shaped lexicon. Root existence
  rests on the BDB-cited B1 table, not this statistic.
- **Random glosses / random language families:** best-of-6-languages manufactures "dwell" with p=0.75 on the
  target skeleton; the dwelling/settlement field is served by **13 distinct** Semitic roots → reaching a
  dwell-tier gloss is a high-prior outcome of any family-wide search.
- **Random morphological parses:** S_morph is **invariant** under relabelling `*301 → any value`
  (0.2738 ≡ 0.2738) → the primary held-out statistic has **NO discriminative power for the value**
  (framing constraint §1 — this is *not itself* a rejection).

## 4. Distinguishability (decides REJECT vs NULL_PUBLISHED)

| Test | Result |
|------|--------|
| Lexical/gloss chain distinguishable from the fake/root-search null? | **No** (null reaches ≥ observed strength every run) |
| Value channel has power? (PC3) | **Yes** — planted value recovered rank **1/113** |
| `/na/` fails the rank-1 clause? | **Yes** — rank 21/65 |
| H2 held-out root recurrence fails? | **Yes** — **0/3** divergent clean sites carry the WA-JA root |
| H3 "dwell" beats formula features? | **Yes, fails** — dwell **0.0/3**, below give/dedicate (3.0) & invocation (2.5) |

## 5. Search-adjusted significance of the whole chain

- Logged root/gloss search cells: **7,800** (value × collapse × language × segmentation); author's stated
  simulations ~**10⁵**. `N_eff` value×segmentation = **260**; `E[max]` null over logged cells = **0.833**.
- `P(≥1 dwell-tier hit over the logged search)` = **1.000**; `/na/` does **not** clear `E[max]`.
- **Search-adjusted p of a chain at least this strong ≈ 1.000** → search-adjusted significance is **nil**.
- The advertised `N-W-Y = "dwell"` is **inexact under the frozen rules**: `na-wa-ya` gives final YOD
  (n-w-y); Hebrew "dwell" is n-w-**H** (final HE). Reaching "dwell" needs an **unregistered III-y → III-h
  transform** — **charged** here to the receipt; not present in the frozen correspondence rules.

## 6. Verdict (frozen rule; honors all three framing constraints)

```
value channel · S_morph        : NO_DISCRIMINATIVE_POWER_FOR_VALUE   (invariant; NOT a rejection)
value channel · S_lex          : REJECT contribution — /na/ rank 21/65, below null mean, fails rank-1
                                  clause WITH power (PC3 recovers a planted value rank 1/113)
lexical / gloss chain (H2/H3)  : NULL_PUBLISHED — indistinguishable from the fake/root-search null
                                  (end-to-end FP = 1.0; dwell hit certain over the logged search)
III-y -> III-h transform       : CHARGED; advertised N-W-Y="dwell" is INEXACT under the frozen rules
core chain /na/->N-W-Y->dwell  : REJECT — adequate power (PC PASS) + fails >=3 load-bearing clauses
   ->Semitic                     (value rank-1, H2 held-out recurrence 0/3, H3 beats-features 0.0/3)
structural i-*301 core         : UNAFFECTED — literature-supported (Davis/Thomas), NOT Di Mino's novelty
impossibility                  : NOT CLAIMED — a historical Semitic relationship is not excluded; the
                                  SPECIFIC fixed-triconsonantal-root chain is simply not supported
```

**FINAL:** `REJECT_CORE_CHAIN__NULL_PUBLISHED_LEXICAL_LEG__NO_POWER_S_MORPH`

Release gate (VERDICT_FRAMING_CONSTRAINTS §Release gate): positive controls **PASS** · end-to-end null
**COMPLETE** · search multiplicity **fully charged** (7,800 logged cells, exact + MC) · core verdict
**mechanically computed** from held-out artifacts. Gate satisfied — the verdict may issue.
