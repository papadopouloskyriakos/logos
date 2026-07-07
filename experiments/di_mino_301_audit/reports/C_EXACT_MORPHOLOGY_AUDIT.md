# C — Exact morphology audit (Di Mino H5) · MORPH_A / MORPH_TA / MORPH_I / MORPH_ROOT

**Prereg** DI_MINO_EXACT_CLAIM_V1 (sha `8b098a4c`) · **Constitution** v2.2 · **Seed** 20260708
**Generator** `scripts/C_morphology_audit.py` → `data/results/morphology.json` · all counts script-generated (invariant 12).
**Non-circular:** signs are ATOMIC tokens; NO phonetic value is assigned on the Linear A side anywhere in this
audit; known LB/Semitic values grade the CONTROLS only (report C_ALTERNATIVE_ANALYSES §C4). Machinery reused:
`scripts/comparison/{morphostat,nulls}` (productivity gate + within-form permutation null).

## The parse under test (Di Mino Figure 1, §3.1 "Position 1: The Invocation Verb")

`A-TA-I-*301-WA-JA` →  `A` = 1cs person prefix · `TA` = tG reflexive-causative stem morpheme ·
`I` = invariant stem vowel (claimed "invariant across 14 attestations") · `*301-WA-JA` = triconsonantal
root C₁C₂C₃ (√n-w-y "dwell"). Each slot is adjudicated SEPARATELY (prereg H5: "one supported slot does NOT
validate the parse").

## The held-out invocation-verb-slot inventory (position 1, distinct forms)

7 distinct forms carry `*301` in the position-1 slot. The target `A-TA-I-*301-WA-JA` has **11 identical
attestations**; the other 6 forms are single-attestation variants:

| form | att. | site(s) | prefix | sign before `*301` | sign after `*301` |
|---|---|---|---|---|---|
| **A-TA-I-*301-WA-JA** (target) | 11 | Iouktas, Kophinas, Palaikastro, Syme, Troullos | A- | I | WA |
| A-TA-I-*301-WA-E | 1 | Palaikastro | A- | I | WA |
| A-NA-TI-*301-WA-JA | 1 | Iouktas | A- | **TI** | WA |
| A-TA-I-*301-DE-KA | 1 | Zakros | A- | I | **DE** |
| TA-NA-I-*301-U-TI-NU | 1 | Iouktas | **(none)** | I | **U** |
| TA-NA-I-*301-TI | 1 | Psykhro | **(none)** | I | **TI** |
| JA-TA-I-*301-U-JA | 1 | Apodoulou | **JA-** | I | **U** |

This table is the whole adjudication in miniature: the "invariant" prefix alternates `A- ~ JA- ~ (TA-NA)`,
the "invariant stem vowel" is `TI` in `A-NA-TI-*301`, and the sign after `*301` (the claimed root's C₂) is
`WA / U / TI / DE`, not a stable radical.

---

## MORPH_A — `A` = 1cs person prefix → **STRUCTURAL_ONLY** (function unlicensed)

C1 productivity (whole LA lexicon, `A-` as a proper word-initial element):

| metric | value |
|---|---|
| distinct forms bearing `A-` | **115** |
| inscriptions | 118 · sites | **21** |
| distinct residual stems after stripping `A-` | **115** |
| non-target forms / stems | 114 / 114 |

`A-` is one of the most **productive** word-initial elements in Linear A (115 distinct stems across 21
sites) — so it passes the *structural* productivity gate as a separable onset (L3). But the productivity
test cannot see PERSON: "1cs prefix (I)" is an L7 grammatical/semantic reading with no held-out handle.
Decisive against the specific label: in the very same position-1 slot the onset **alternates
`A- ~ JA-`** (`JA-TA-I-*301-U-JA`, Apodoulou) and drops entirely in `TA-NA-I-*301-…`. A fixed 1cs marker
does not alternate with another prefix and vanish across the paradigm. **Verdict: the separable onset is
real (L3); "1cs person" is NOT supported.**

## MORPH_TA — `TA` = tG reflexive-causative stem morpheme → **NOT_SUPPORTED**

Slot-2 sign (immediately after `A-`) across the distinct invocation forms:

| slot-2 sign | distinct forms |
|---|---|
| TA | 3 |
| NA | 1 (`A-NA-TI-*301-WA-JA`) |

Position-2 is **not invariantly `TA`** — `A-NA-TI-*301-WA-JA` puts `NA` there and shifts the whole prefix
complex. `A-TA` as a two-sign prefix attaches to 9 distinct stems across 9 sites, so `A-TA-` is a real
recurring onset cluster — but "**tG reflexive-causative stem morpheme**" is a specific L7 derivational-binyan
claim with (a) no invariance even at the sign level and (b) no structural or held-out test that could
confirm a *reflexive-causative* function. `TA` is among the commonest Linear A signs and occurs in every
word position. **Verdict: NOT_SUPPORTED (position not invariant; function untestable and unlicensed).**

## MORPH_I — `I` = invariant stem vowel (claimed invariant across 14 attestations) → **PARTIAL_STRUCTURAL**

Sign immediately before `*301`, across the 7 distinct invocation forms:

| sign before `*301` | distinct forms |
|---|---|
| I | 6 |
| TI | 1 (`A-NA-TI-*301`) |

The sequence `I-*301` recurs in **6 distinct forms across 8 sites** (`A-TA-I-*301-DE-KA`,
`A-TA-I-*301-WA-E`, `JA-TA-I-*301-U-JA`, `TA-NA-I-*301-TI`, `TA-NA-I-*301-U-TI-NU`, + target) — a genuine
recurring stem juncture (this is exactly **Davis's `I-*301` stem**, C_ALTERNATIVE §C3). Two honesty flags:
(1) the claim "**invariant across 14 attestations**" is **repetition-inflated** — 11 of the 14 are byte-identical
copies of the target word, so the invariance is lexical copying, not paradigmatic productivity (the
`A-TA-I` 3-sign prefix attaches to only **3 distinct stems**: `*301-WA-JA`, `*301-WA-E`, `*301-DE-KA`);
(2) `A-NA-TI-*301` breaks strict invariance. "Stem **vowel**" is an L7 phonological label, unlicensed.
**Verdict: `I-*301` recurs structurally (L3, and it favours Davis over Di Mino); "invariant stem vowel"
as stated is repetition-inflated and phonologically unlicensed.**

## MORPH_ROOT — `*301-WA-JA` = triconsonantal root C₁C₂C₃ (√n-w-y) → **REFUTED**

The load-bearing slot. C1 held-out recurrence of the contiguous unit `*301-WA-JA`:

| metric | value |
|---|---|
| distinct forms containing `*301-WA-JA` | **2** (target + `A-NA-TI-*301-WA-JA`) |
| **non-target** forms containing it | **1** |
| sign AFTER `*301` (claimed C₂), distinct invocation forms | WA ×3, U ×2, TI ×1, DE ×1 |
| sign after `*301`, **all** `*301` forms (admin incl.) | WA, U, TI, DE, NA, SI, RI, KI, NE, PI, U-RA … (highly variable) |

`*301-WA-JA` has **no held-out recurrence** beyond copies of the target and the single `A-NA-TI-*301-WA-JA`
(itself a target-adjacent variant). The sign after `*301` — which the claim needs to be the stable second
radical C₂ = /w/ — is instead **WA / U / TI / DE / NA / SI / …** across the corpus, so `*301` heads **no
stable triconsonantal root**. This corroborates report **04** (segmentation): every value-free segmenter
cuts boundary **b4** (*after* `*301`), splitting `*301` **away** from `WA`; the `b3` cut Di Mino needs has
forward-entropy **0.00** (after `A-TA-I` the corpus *always* continues to `*301`). The "root" is an artifact
of first assuming `*301=/na/` (report 02 circularity e2→e3→e4). **Verdict: REFUTED.**

---

## S_morph on held-out invocation inscriptions (what morphology IS recoverable)

Running the productivity-gated cross-inscription recurrence (`morphostat.s_morph`, within-form null,
n_null=500) over the 6 held-out non-target invocation inscriptions, using the invocation lexicon's own
derived affix inventory:

- score = **0.278**, null_mean = 0.013, **z = 13.10**, exact rank p = 0.0020, **has_power=True,
  is_significant=True** (9 affixes, 6 independent inscriptions).

Held-out Linear A morphology in this slot **is** real and significant — but it is **edge-affixal**: the
derived inventory that recurs is `prefix A- / A-TA- / A-TA-I- / TA-NA-` and `suffix -JA / -WA-JA / -E`,
i.e. the separable onset and the `-JA/-E` ending. This is precisely the **Davis (I-*301 stem, both-end
inflection) / Thomas (-JA/-E ending)** structure — and it is **orthogonal to, indeed against,** Di Mino's
*internal* `*301-WA-JA` root cut. The recoverable morphology vindicates the rival parses, not this one.

## Per-slot summary (prereg C5 — reported separately, never collapsed)

| slot | claim | mechanical verdict | why |
|---|---|---|---|
| MORPH_A | 1cs person prefix | **STRUCTURAL_ONLY** | separable onset real (L3); `A-~JA-` alternation kills fixed 1cs; person = unlicensed L7 |
| MORPH_TA | tG reflexive-causative stem | **NOT_SUPPORTED** | slot-2 not invariant (`A-NA-TI`); binyan function untestable/unlicensed |
| MORPH_I | invariant stem vowel ×14 | **PARTIAL_STRUCTURAL** | `I-*301` recurs (favours Davis); "×14" repetition-inflated; `A-NA-TI` breaks it; vowel = unlicensed |
| MORPH_ROOT | `*301-WA-JA` triconsonantal root | **REFUTED** | no held-out recurrence; post-`*301` sign variable; segmentation cuts b4 against it |

**No single supported slot validates the parse (prereg H5).** The only slots that survive survive at **L3
(separable positional elements)** and, where they do, they support **Davis/Thomas edge morphology, not the
`*301-WA-JA` root** — the one slot the `/na/`→n-w-y→"dwell" chain actually requires.
