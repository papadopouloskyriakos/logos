# H3 — Candidate Round 3: morphology-first JOINT decipherment models

**Task H3** · Constitution v2.2 (Art. III guilty-until-proven, V claim layers, VII search receipt,
VIII effective-n/multiplicity, XII no grading by the creating rule, XV transfer licences) · seed
`20260708` · as_of `2026-07-07`.

- Prereg (frozen before run): `preregistrations/H_round3_prereg.json`
- Script: `scripts/h3_candidate_round3.py` — reuses the **audited** Foundry null machinery
  `candidate_round1.py` (imported, not re-run: `expand_phonemes`, `build_family_predictions`,
  `score_corpus`, `shuffle_within`, `random_lexicon`, `sample_lb_lengthmatched`) and H1's
  `load_la_heldout`. Single documented addition: a prefix-aware matcher `word_matches_h3`
  (prefix + stem/suffix) applied **identically** to real corpus and every null.
- Data: `data/H3_round3.json` (+ `data/candidates_v2/H3_round3.json`) · Manifest:
  `manifests/H3_round3_manifest.json`
- Highest claim layer reached: **L2/L3**. Transfer licences **NOT_EARNED**. No phonetic value
  assigned to any Linear A sign or class.

## VERDICT: `AT_JOINT_INFERENCE_NULL`

Three inference paradigms — **Bayesian-joint**, **MDL**, **constraint-satisfaction/integer-program**
— were run as a *morphology-first joint (sign-value, morphology) decipherment*, using the
value-blind backbone (A- prefixation + the ledger `KU-RO`=TOTAL / `KI-RO`=DEFICIT formula slots) as
the joint scaffold and committing a readable lexicon from a shared external candidate pool
(SEM/ANA/TYR + the two backbone morphemes). **No paradigm is GENUINE.** The mechanical reason is
computed for the record and is the campaign's core finding rendered three ways: the backbone is
**value-blind (relabeling-invariant)** — under 200 consistent relabelings of the AB value map the
held-out read-count is **exactly invariant (std 0)**, so the joint posterior over sign-values is
**flat (3.585 bits, 12 equally-probable assignments)**, the CSP feasible set is pinned only by the
**choice of external lexeme** (dictionary feasibility, not Linear A), and MDL's entire gain sits on
the *derivation words it is scored to exclude*. Held-out reading power: BAYES/CSP raw match 0.082
(pure A-`-prefix`/`-na` word-shape typicality, random-lexicon percentile p **0.076 / 0.093** —
inside the band; Holm **0.179**), MDL 0.000 (commits only `kull`, which reads nothing off the
excluded TOTAL slot), agnostic control at the null. Honest expectation confirmed.

---

## 1. The morphology-first backbone and the derivation/held-out split

The joint models are scaffolded on the campaign's durable L2/L3 positive — anonymous
morphology/formula structure — which is **value-blind** (D5/F4: relative classes real but value-blind;
position→C/V REFUTED; seed-propagation a frequency artifact):

| backbone element | measured |
|---|---|
| ledger TOTAL slot: `KU-RO` family tokens | **44** |
| ledger DEFICIT slot: `KI-RO` family tokens | **18** |
| A- prefix words (tail is an attested LA word) | **14** |
| **derivation words excluded from grading (leakage)** | **18 distinct forms** (76 tokens) |

The joint model *fits* the derivation backbone, so scoring on it would be Invariant-3 overfitting.
It is removed. **Held-out target = 998 multi-sign syllabic word tokens (745 types, 42 sites)**, down
from the full 1074. Wrong-language null corpus: 24,447 length-matched DĀMOS Linear B multi-sign words.

## 2. The backbone is value-blind — the null generator, computed three ways

Every AB-based reading assigns the **same** conventional value to a given sign, so the LA-internal
morphology/formula statistics are invariant under any consistent relabeling of the value map. The
joint inference therefore cannot recover a value from internal structure. Made mechanical:

- **Relabeling-invariance (headline).** 200 consistent relabelings of the 59-value AB map, applied to
  corpus *and* predicted forms alike: held-out read-count **82 → 82, std 0.0, invariant = True**. A
  consistent relabeling is an isomorphism of the whole reading, so the backbone carries **0 bits**
  about which phonetic value any sign holds.
- **Bayesian posterior (identifiability).** Over the space of which word-lexeme the `KU-RO` string
  *means*, the value-blind likelihood is flat: **posterior entropy 3.585 bits = 12 equally-probable
  assignments** (`effective_assignments_valueblind = 12`). The feasibility-restricted posterior
  collapses to `kull` (entropy 0), but that concentration is a **dictionary fact about the external
  spelling**, not phonetic information recovered from Linear A.
- **CSP feasible set.** Hard constraints C1 (a total-role lexeme whose expansion ∋ `KU-RO`) + C2 (a
  prefix morpheme whose expansion ∋ `A`) are satisfiable, but by a **single** pool assignment
  (`kull`, `a-_article`) → `feasible_assignment_count = 1`, uniquely pinning **2 signs** (`A`, `KU`).
  Those two signs are forced by the *chosen external lexeme's spelling*, not by LA.
- **Value-coverable vs read.** The 2 pinned signs cover **0** held-out words and read **0** lexically
  — one-lexeme-deep, mirroring `SEED_A = 0` (H2).

## 3. The three inference paradigms scored vs the end-to-end null battery

Decisive FWER = `max(p_W, p_R)`; Holm step-down across the 3 serious paradigms; leave-one-lexeme-out
worst-case; random-lexicon calibration (N_CAL=300). Prefix-aware matcher applied to every null.

| paradigm | committed | eff_n | real rate | matched | p_S | p_W | p_R | decisive | **Holm** | **LOO worst** | cal p | clears? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **BAYES_joint** | 19 lexemes (posterior>0.5) | 40 | **0.0822** | 82 | 0.055 | 0.005 | 0.060 | 0.0597 | **0.179** | 0.199 | **0.076** | **NO** |
| **MDL_joint** | 1 lexeme (`kull`) | 5 | **0.0000** | 0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | **NO** |
| **CSP_IP** | 19 lexemes (max-coverage) | 40 | **0.0822** | 82 | 0.055 | 0.005 | 0.070 | 0.0697 | **0.179** | 0.229 | **0.093** | **NO** |
| CTRL (agnostic) | 19 random | 45 | 0.0271 | 27 | 0.075 | 1.0 | 0.746 | 1.0 | — | 1.0 | — | NO |

`paradigms_clearing_calibrated_and_serious`: **none**. `ctrl_agnostic_cleared_raw_bar`: **False**.

### 3.1 BAYES / CSP: the raw match is A-prefix word-shape typicality, absorbed by calibration

BAYES and CSP commit the whole feasible pool and reach raw 0.0822 (`A-NA`, `A-DU-KU-MI-NA`,
`A-KU-MI-NA`, `A-RE-PI-RE-NA`, `A-MA-WA-SI`, …) — the prefix matcher credits `A-`+readable-stem. But
the same-structure random-lexicon band **reproduces it**: real percentile p **0.076 (BAYES) / 0.093
(CSP)**, both inside the band (`raw_bar_false_clear_rate` 0.047 / 0.063). It is generic LA
word-shape (`A-` initial + `-na`/`-si` tails), not lexical fit — the identical confound the
random-prior/random-lexicon controls exist to absorb (cf. H1/H2 TYR at percentile 0.213 / 0.219).
Holm 0.179 ≫ 0.05.

### 3.2 MDL: the only "signal" is the `KU-RO` word it is scored to exclude

The MDL optimum commits a **single** lexeme, `kull` — DL 248.8 (empty) → **231.2**, a 40.4-bit gain
vs a random lexicon. But every bit of that gain is earned on the **derivation** `KU-RO` tokens, which
are *excluded from the held-out grade as leakage*. On the held-out set `kull` reads **0** words
(match rate 0.000, decisive 1.0). This is the Egyptian-channel / single-lexeme trap in its purest
form: the parsimonious optimum is one famous administrative equation and nothing else.

### 3.3 The agnostic control behaves

CTRL (random matched-structure committed lexicon) reads 27 held-out words on shape alone but sits at
the null (decisive **1.0**, p_R 0.746): the prefix-aware bar is **not** trivially passable by
matched-structure noise, and neither serious paradigm clears it.

## 4. What is and is not determined

- **Not determined (all NULL):** no inference paradigm — Bayesian-joint, MDL, or CSP/IP — recovers a
  sign-value assignment that reads held-out Linear A beyond a same-structure random lexicon. No
  phonetic value, vowel, consonant, or language affiliation is assigned to any LA sign or class.
- **Determined (for the record):** (a) the morphology-first backbone is **value-blind /
  relabeling-invariant** (read-count std 0 over 200 relabelings; Bayesian posterior flat at 3.585
  bits / 12 assignments) — no inference paradigm operating on internal structure *can* recover a
  value; (b) the CSP feasible set pins 2 signs, both by external-lexeme choice, covering 0 held-out
  words (one-lexeme-deep, `SEED_A = 0`); (c) MDL's 40-bit gain is entirely on the excluded derivation
  `KU-RO`; (d) BAYES/CSP raw match is A-prefix word-shape typicality inside the random-lexicon band
  (p 0.076 / 0.093); (e) the agnostic control sits at the null.

## 5. Verdict and next step

```
H3_ROUND_3: AT_JOINT_INFERENCE_NULL
  - 0/3 serious inference paradigms GENUINE (Holm-adjusted decisive FWER >= 0.05 for every paradigm;
    BAYES/CSP inside random-lexicon band; MDL reads 0 held-out).
  - backbone value-blind: relabeling read-count std 0 (200 relabelings); Bayesian posterior flat
    (3.585 bits, 12 assignments); CSP feasible set = 1, pins 2 signs by external-lexeme choice.
  - MDL commits kull only -> 40-bit gain entirely on the EXCLUDED derivation KU-RO; 0 held-out reads.
  - BAYES/CSP raw 0.082 -> random-lexicon percentile p 0.076 / 0.093 (A-prefix shape typicality).
  - agnostic CTRL at the null (decisive 1.0).
```

Consistent with H1, H2, and the whole campaign: internal morphology + formula structure is real (L2)
but **value-blind**, and no value-bearing joint inference survives the multi-family end-to-end null.
Transfer licences **unchanged: NONE** (Art. XV). No semantic rescue was applied; any revised system
(new lexemes, relaxed constraints) would require a new plan hash + receipt + sealed target, not an
edit. **Next task: I1 (constraint-reduced agnostic value search)** — see `H_MODEL_COMPARISON.md` for
the three-round synthesis.

**Compliance (Art. XXII):** prereg frozen before run; predictions external to LA (Art. XII honoured);
derivation-backbone words excluded as leakage; multiplicity Holm-corrected across 3 paradigms
(Art. VIII); effective_n reported per paradigm (Art. VIII); decisive nulls + LOO + random-lexicon
calibration run; agnostic control included; relabeling-invariance computed for the record;
append-only; no licence bypass (Art. XV).
