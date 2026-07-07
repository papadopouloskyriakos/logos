# 04 — Segmentation comparison on `A-TA-I-*301-WA-JA` (T05)

**Prereg:** `DI_MINO_EXACT_CLAIM_V1` (sha `8b098a4c`). **Seed:** 20260708.
**Generator:** `scripts/segmentation_compare.py` → `data/results/segmentation_target.json`
(sha256 `d57a4383…`). Signs are atomic tokens. The two **data-driven** families
(NO_PHONETIC_STRUCTURAL, PROBABILISTIC) are computed from the silver LA corpus with **no phonetic
values** — the non-circular check on whether Di Mino's `*301-WA-JA` "root" boundary is a
distributional fact or a phonetically-motivated cut.

## A. The five internal boundaries of `A-TA-I-*301-WA-JA`

`[A] · [TA] · [I] · [*301] · [WA] · [JA]` → boundaries **b1** (A|…), **b2** (A-TA|…),
**b3** (A-TA-I|…), **b4** (…*301|WA…), **b5** (…WA|JA).

## B. Where each family cuts

| family | boundaries | parse | isolates `*301-WA-JA` as a unit? | phonetically motivated? |
|---|---|---|---|---|
| **DI_MINO** | {b1,b2,b3} | `a │ ta │ i │ **301-wa-ja** (root n-w-y)` | **YES** (the load-bearing claim) | **YES** |
| **DAVIS** (i-*301+affix) | {b2,b4} | `A-TA │ **I-*301** │ WA-JA` | no (`*301` grouped with `I`) | no |
| **THOMAS** | {b5} | `A-TA-I-*301-WA │ JA` | no (`*301` inside stem) | no |
| **DIPLOMATIC** | {} | `A-TA-I-*301-WA-JA` (one graphic word) | no (whole word) | no |
| **NO_PHONETIC_STRUCTURAL** | **{b3,b4,b5}** | `A-TA-I │ **301** │ WA │ JA` | **NO — cuts b4, splitting `*301` from `WA`** | no (data) |
| **PROBABILISTIC** (branch-entropy) | **{b1,b5}** | `A │ TA-I-*301-WA │ JA` | **NO** | no (data) |
| PROBABILISTIC (Viterbi/MDL) | {} | `A-TA-I-*301-WA-JA` (kept whole) | no | no (data) |

DAVIS/THOMAS shown as the structural families the mandate names; the exact Davis 2014 / "Thomas"
segmentation artifacts are **not in-repo** → `SOURCE_DEPENDENCY` flagged in the JSON. Their structural
commitments (Davis: `I-*301` recurring stem; Thomas: `-JA/-E` inflectional ending) are, however,
independently corroborated by the corpus (the `WA-JA`~`WA-E` alternation at IOZa2 vs PKZa11, and the
`A-`~`JA-` alternation at A-TA-I- vs JA-TA-I- in APZa1).

## C. Measured corpus signal (branching entropy, per boundary)

| boundary | fwd H (bits) / support | bwd H (bits) / support | score | reading |
|---|---|---|---|---|
| b1 `A│TA…` | 4.79 / 169 | 0.00 / 11 | **4.79** | `A-` freely separable (many words start `A-…`) |
| b2 `A-TA│I…` | 1.47 / 19 | 0.00 / 11 | 1.47 | weak |
| b3 `A-TA-I│*301…` | **0.00** / 13 | 0.41 / 12 | 0.41 | **`A-TA-I` is ALWAYS followed by `*301`** (deterministic, NOT a boundary) |
| b4 `…*301│WA…` | 0.39 / 13 | 0.39 / 13 | 0.78 | weak |
| b5 `…WA│JA` | 0.41 / 12 | **4.55** / 95 | **4.97** | `-JA` freely separable ending (many words end `…│JA`) |

Branching-entropy peaks (> mean 2.483) fall at **b1 and b5** — the word *edges* (`A-` prefix, `-JA`
ending), never at Di Mino's internal `b2`/`b3`. Critically, **b3 forward-entropy = 0.00**: after
`A-TA-I` the corpus *always* continues to `*301`, so `A-TA-I` is not a completed unit and `b3` is the
*least* boundary-like internal position — the opposite of Di Mino's morpheme cut there.

The **structural-recurrence** family independently credits **b4** (a boundary *after* `*301`), i.e. the
distribution treats `*301` as separable from the following `WA` — directly **contradicting** the
`*301-WA-JA` root grouping.

## D. Agreement / disagreement (Jaccard over boundary sets)

| pair | Jaccard | shared boundaries |
|---|---|---|
| DI_MINO vs DAVIS | 0.25 | {b2} |
| DI_MINO vs THOMAS | 0.00 | ∅ |
| DI_MINO vs DIPLOMATIC | 0.00 | ∅ |
| DI_MINO vs NO_PHONETIC_STRUCTURAL | 0.20 | {b3} |
| DI_MINO vs PROBABILISTIC(BE) | 0.25 | {b1} |
| DAVIS vs THOMAS | 0.00 | ∅ |
| NO_PHONETIC_STRUCTURAL vs PROBABILISTIC(BE) | 0.25 | {b5} |

**Universal agreement:** every family that cuts at all agrees `A-` is separable (b1) and/or `-JA` is a
separable ending (b5) — the *edges*, which are also the least informative (a prefix + an ending shared
across the whole formula corpus). **No two families agree on the internal morpheme structure**, and
DI_MINO shares **zero** boundaries with THOMAS, DIPLOMATIC, or Viterbi/MDL.

## E. Load-bearing result — the `*301-WA-JA` "root" is NOT distributionally supported

The claim's decipherment pivots on segmenting `*301-WA-JA` as one unit (the triconsonantal root
`n-w-y`), which requires a cut at **b3** and **no cut** at **b4/b5**.

| data-driven family | isolates `*301-WA-JA` as a root unit? | what it does around `*301` |
|---|---|---|
| NO_PHONETIC_STRUCTURAL | **NO** | cuts b4 (after `*301`) → `*301` split from `WA` |
| PROBABILISTIC (branch-entropy) | **NO** | cuts b1,b5 only → `*301` buried mid-stem |
| PROBABILISTIC (Viterbi/MDL) | **NO** | keeps the whole word (11× attested type) → no root |

**Not one** value-free, corpus-driven segmentation reproduces Di Mino's `*301-WA-JA` root grouping;
the structural method actively cuts `*301` *away* from `WA`. The `b3` boundary Di Mino needs is the
single most *anti*-boundary internal position in the data (fwd-entropy 0.00). Therefore the root
boundary is **phonetically motivated** — chosen so that `na-wa-ja` strips to `n-w-y` — not a fact the
distribution supports. This corroborates the `02_…` circularity finding (e2→e3→e4): the segmentation
that yields the root is a *consequence* of assuming `*301=/na/`, not independent evidence for it.

## F. What the segmentation comparison does and does not license
- **Supported (value-free):** `A-TA-I-*301-WA-JA` behaves as a formula-initial word with a separable
  `A-` onset (alternating `JA-`) and a separable `-JA/-E` ending — an inflected invocation word. This
  is the *stable structural* residue (candidate `PARTIAL_SUPPORT` at L3, no phonetic licence).
- **NOT supported:** the specific `a│ta│i│301-wa-ja` morpheme cut, the `*301-WA-JA`=root unit, and
  hence the `n-w-y` extraction. Segmentation evidence is **against**, not for, the root boundary.
- Per prereg, `S_morph` (recurring morphology) is primary; segmentation feeds H2/H5 but is never alone
  sufficient. Here it removes a load-bearing premise rather than supplying held-out morphology.
