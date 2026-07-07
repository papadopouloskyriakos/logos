# C3/C4 — Head-to-head models + known-script controls · SEMITIC_MORPHOLOGY → **NOT_SUPPORTED**

**Prereg** DI_MINO_EXACT_CLAIM_V1 (sha `8b098a4c`) · **Constitution** v2.2 · **Seed** 20260708
**Generator** `scripts/C_morphology_audit.py` → `data/results/morphology.json` (§C3, §C4). Non-circular:
Linear A signs are atomic tokens with NO phonetic value; LB/Ugaritic values grade the CONTROLS only.

---

## C3 — Head-to-head (Di Mino vs Davis vs Thomas vs neutral-agglutinative vs Semitic-weak-root vs Markov)

**Non-circular metric.** Each competing analysis commits to a single contiguous **invariant lexical unit**
(the root/stem it says recurs across the whole invocation paradigm). We measure, at the sign level under
**leave-target-out**, the fraction of the 6 non-target held-out invocation forms that contain that unit.
This uses only sign sequences — no phonetic values, no gloss.

| model | claimed invariant unit | held-out invariance | forms containing it |
|---|---|:--:|:--:|
| **DAVIS** (root inflected at both ends) | `I-*301` stem | **0.833** | 5/6 |
| NEUTRAL_AGGLUTINATIVE | `I-*301` medial stem, variable edges | 0.833 | 5/6 |
| THOMAS (`-JA/-E` ending) | `TA-I-*301` core | 0.500 | 3/6 |
| **DI_MINO** | **`*301-WA-JA` root (√n-w-y)** | **0.167** | **1/6** |
| SEMITIC_WEAK_ROOT | weak-medial triconsonantal root (= Di Mino at sign level) | 0.167 | 1/6 |

Diagnostic (Thomas): fraction of held-out forms ending in `-JA` or `-E` = **0.50** (the `-JA ~ -E`
inflectional alternation Thomas predicts, corroborated by `A-TA-I-*301-WA-JA` vs `A-TA-I-*301-WA-E`).

**Markov baselines** (1st/2nd-order sign Markov trained on all LA words EXCEPT invocation-slot forms;
next-sign top-1 on the held-out invocation forms, 36 predictions): markov1 = **0.111**, markov2 = **0.083**.
The invocation word is *lexically special* — general LA sign statistics barely predict it — which is the
signature of a **memorised formula lexeme**, not of productive, generalisable morphology.

**Result.** Di Mino's `*301-WA-JA` root is the **worst** of the six analyses at predicting the held-out
paradigm (0.167), tied only with the sign-level Semitic-weak-root model it reduces to; **Davis's `I-*301`
stem wins (0.833)**. The head-to-head is a decisive loss for the root parse.

---

## C4 — Known-script controls (the method must distinguish the structures it claims to test)

Identical adjudication — derive each corpus's own recurring affix inventory, then the productivity-gated
cross-inscription recurrence vs the within-form permutation null (`morphostat.s_morph`, n_null=300, random
pseudo-inscription groups of ~8) — run on six corpora:

| corpus | n_forms | n_affix | score | null | z | has_power | significant | what it detects |
|---|--:|--:|--:|--:|--:|:--:|:--:|---|
| **real Semitic — Ugaritic** | 2214 | 26 | 0.390 | 0.341 | **15.2** | ✓ | ✓ | proclitics `l- w- b- k- m-`, prefixes `y- t-` (POSITIVE control fires) |
| **synthetic Semitic-root** | 240 | 38 | 0.510 | 0.235 | **25.2** | ✓ | ✓ | `l- w-` proclitics + prefix-conj `ya- ta- ma-` (fires; radicals linearised) |
| **synthetic agglutinative** | 240 | 8 | 0.667 | 0.389 | **11.1** | ✓ | ✓ | prefixes `aP- iP- uP-`, suffixes `-Sa -Si -Su` (fires) |
| **opaque Linear B** (Greek) | 2500 | 35 | 0.274 | 0.179 | **36.5** | ✓ | ✓ | Greek inflectional prefixes/suffixes (fires — and it is NOT Semitic) |
| LA — all words | 3147 | 6 | 0.204 | 0.120 | 16.9 | ✓ | ✓ | LA general affixation `A- I- JA-`, `-JA -RO` |
| **LA — invocation set only** | 7 | 6 | 1.000 | 0.083 | 8.95 | **✗ (NO_POWER)** | ✗ | 7 distinct forms → one group; too thin for the cross-inscription test |

Two things the control panel establishes:

1. **The method has POWER and is calibrated.** It fires on real Ugaritic and on both synthetic
   positive controls, i.e. it genuinely detects productive affixation where it exists. (The LA
   per-inscription held-out test in C_EXACT_MORPHOLOGY_AUDIT also fired at z=13.1 on LA's *edge* affixes.)
   The `LA-invocation` row is NO_POWER because 7 distinct forms collapse to a single pseudo-group — an
   honest thinness verdict, not a detector failure.

2. **"Fires" does NOT mean "Semitic."** The **opaque Greek Linear B** corpus fires the *hardest*
   (z=36.5) and the **synthetic agglutinative** corpus fires strongly (z=11.1) — neither is Semitic. The
   concatenative-affix productivity gate cannot, from edge affixes alone, distinguish Semitic
   root-and-pattern from agglutinative concatenation from Greek fusional inflection. Even the synthetic
   Semitic-root control is detected only via its *linearised* proclitics/prefix-conjugation prefixes, not
   as a nonconcatenative C₁C₂C₃ template — so a "morphology fires" result on Linear A would license
   **no** claim of Semitic templatic morphology specifically.

---

## SEMITIC_MORPHOLOGY — verdict → **NOT_SUPPORTED**

- The method **can** detect Semitic affixation (Ugaritic z=15.2; synthetic Semitic-root z=25.2) → it is
  not a dead detector.
- But it **cannot identify structure as Semitic** rather than agglutinative or Greek-fusional (opaque LB
  z=36.5; synthetic agglutinative z=11.1 both fire) → a "Semitic morphology" label is not earnable from
  affix recurrence.
- On Linear A the position-1 invocation set is a **near-frozen formula lexeme**: 11 identical copies + 6
  singleton variants, `A-TA-I` attaching to only 3 distinct stems, and the claimed `*301-WA-JA` root with
  **no** held-out recurrence (C_EXACT §MORPH_ROOT). What productive morphology IS recoverable on held-out
  LA is **edge-affixal** (Davis/Thomas), the opposite of Di Mino's internal root cut.

**Therefore the claim that `A-TA-I-*301-WA-JA` exhibits *Semitic* verbal morphology (1cs prefix + tG stem +
stem vowel + triconsonantal root) is NOT_SUPPORTED.** The evidence that survives licenses only an L3
structural residue — a formula-initial word with a separable `A-`/`JA-` onset and a `-JA/-E` ending around
an `I-*301` stem — which is family-agnostic and, in the head-to-head, favours **Davis over Di Mino**.

## Roll-up (prereg C5 — separate slots, never collapsed)

| slot | verdict |
|---|---|
| MORPH_A | STRUCTURAL_ONLY (1cs unlicensed; `A-~JA-` alternation) |
| MORPH_TA | NOT_SUPPORTED (slot-2 non-invariant; binyan untestable) |
| MORPH_I | PARTIAL_STRUCTURAL (`I-*301` recurs → favours Davis; "×14" repetition-inflated) |
| MORPH_ROOT | **REFUTED** (no held-out recurrence; post-`*301` sign variable; segmentation b4 against) |
| PARADIGM | **REJECT** (root present in 1/6 held-out; Davis stem 5/6) |
| SEMITIC_MORPHOLOGY | **NOT_SUPPORTED** (method cannot identify Semitic; LA morphology is formulaic + edge-affixal) |

No supported slot rescues the parse: the two slots that survive do so at L3 and point to **Davis's `I-*301`
stem**, not to the `*301-WA-JA` root on which the `/na/` → √n-w-y → "dwell" decipherment depends.
