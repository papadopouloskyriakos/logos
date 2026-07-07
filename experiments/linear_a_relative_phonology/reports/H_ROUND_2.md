# H2 — Candidate Round 2: anchor-constrained family/isolate models

**Task H2** · Constitution v2.2 (Art. III guilty-until-proven, V claim layers, VII search receipt,
VIII effective-n/multiplicity, XII no grading by the creating rule, XV transfer licences) · seed
`20260708` · as_of `2026-07-07`.

- Prereg (frozen before run): `preregistrations/H_round2_prereg.json`
- Script: `scripts/h2_candidate_round2.py` — reuses the **audited** Foundry null machinery
  `candidate_round1.py` (imported, not re-run) **and** the audited `h1_candidate_round1.py`
  (byte-identical family defs, CTRL materialization, held-out loader `load_la_heldout`)
- Anchors: `data/anchors_v2/seeds.json` (WP-G audited) — the **6 SEED_B toponym anchors** only
- Data: `data/H2_round2.json` (+ `data/candidates_v2/H2_round2.json`) · Manifest:
  `manifests/H2_round2_manifest.json` (output sha256 `d9953ce5…`)
- Highest claim layer reached: **L2/L3**. Transfer licences **NOT_EARNED**. No phonetic value
  assigned to any Linear A sign or class.

## VERDICT: `AT_ANCHOR_CONSTRAINED_NULL`

Adding the WP-G audited anchors as a constraint recovers **nothing**. The 6 SEED_B toponym anchors
(the only value-bearing anchors in the whole inventory; **G3: SEED_A = 0**) are all read through the
GORILA/LB conventional values, so each is `circular_for_grading` (Art. XII) and excluded from the
honest score. **Anchor augmentation adds ZERO held-out matches for every family**
(`anchor_augmentation_delta_matches = 0`, all 5 families; `anchor_adds_reading_beyond_sources =
false`). Pinning the anchors' 17 sign-values makes **135 / 1067** anchor-excluded held-out words
value-*coverable* but yields **0** new lexical readings and **0** anchor-form matches beyond the 7
excluded source tokens — a direct demonstration that SEED_A = 0 (one-toponym-deep). With anchors
excluded, the strict scores collapse to the H1 picture: no serious family beats the multi-family
end-to-end null; the only raw-clearing signal (**SEM**, decisive 0.0149) is the single `KU-RO` "total"
lexeme that fails Holm (**0.0745**) and dies at LOO (**1.000**); the highest raw match (**TYR**, 0.073)
sits inside the random-lexicon band (percentile p **0.219**); the negative control (**FIN**) and the
agnostic control (**CTRL**) sit at the null.

---

## 1. The anchor constraint

The WP-G audit (`data/anchors_v2/seeds.json`) yields **SEED_A = 0**: no independently secure value
seed exists. The only value-bearing anchors are **6 SEED_B firm-primary toponym equations**, pinning
**17 distinct signs**:

| anchor form | referent | pinned signs |
|---|---|---|
| `PA-I-TO` | Phaistos | PA, I, TO |
| `SE-TO-I-JA` | se-to-i-ja (unlocated) | SE, TO, I, JA |
| `TU-RU-SA` | Tylissos | TU, RU, SA |
| `DI-KI-TE` | Mt-Dikte | DI, KI, TE |
| `SU-KI-RI-TA` | Sybrita | SU, KI, RI, TA |
| `A-TU-RI-SI-TI` | Tylissos (clone) | A, TU, RI, SI, TI |

**Pinned set (17):** A, DI, I, JA, KI, PA, RI, RU, SA, SE, SI, SU, TA, TE, TI, TO, TU.

**Art. XII marking.** Every SEED_B anchor is *read* through the GORILA/LB conventional sign-values —
`PA-I-TO` is recognizable as Phaistos only because PA=/pa/, I=/i/, TO=/to/ are the same values the
families use. The pinned value therefore **equals** the GORILA homomorphic value, so an anchor-credited
held-out match is not independent evidence for any family. All 6 are marked `circular_for_grading =
true` and **excluded from the strict verdict score**. (G3 independently demotes them from SEED_A: the
cited frozen LOTO gate recovers only {I, RI}, each one-toponym-deep.) The other **97** anchor records
(57 shape-homomorphy + 11 Cypriot value-inheritance + 25 onomastic personal names + 4 internal
variation) and the 6 relative/structural G2 classes are SEED_X (value-blind / circular) and are **not
used as value anchors at all**.

**Leakage exclusion.** 7 held-out tokens are anchor-source (equal / prefix / suffix an anchor form:
`PA-I-TO`, `SE-TO-I-JA`, `TU-RU-SA`, `SU-KI-RI-TA`, `A-TU-RI-SI-TI`, `A-DI-KI-TE`, …) and are removed
from the graded set. Held-out target: **1067** multi-sign syllabic word tokens (757 types, 42 sites),
down from H1's 1074.

**Family-independence (recorded).** Toponyms are language-independent proper nouns read through the
shared AB syllabary, so *every* AB-based family augments with the *same* 6 forms and inherits the *same*
17 pinned signs. The anchor constraint — exactly like the D5 relative classes (F4) — **cannot break the
symmetry between families**. It is computed for the record and does not gate scoring.

## 2. Anchor reading power (the SEED_A = 0 demonstration)

| quantity | value |
|---|---|
| held-out words fully value-coverable by the 17 pinned signs | **135 / 1067** |
| of those, matched by an actual anchor FORM (beyond excluded sources) | **0** |
| anchor augmentation Δ matches (per family, all 5) | **0** |
| `anchor_adds_reading_beyond_sources` | **false** |

Pinning 17 signs' values renders 135 held-out words *value-coverable* — but a covered word is only a
phonetic string with **no external referent**, i.e. **no lexical reading**. The anchors match no
held-out word beyond their own (excluded) source toponyms. This is the campaign's anchor finding made
mechanical: firm toponym equations are one-toponym-deep and buy **zero** held-out reading power.

## 3. Results — strict score (anchor-excluded, family-lexeme only) vs the end-to-end null battery

Decisive FWER = `max(p_W, p_R)`; Holm step-down across the 5 families; LOO worst-case; random-lexicon
calibration. `perm` = permissive score granting the 6 anchor forms (sensitivity).

| model | eff_n | strict rate | perm rate | Δ(anchor) | p_W | p_R | decisive | **Holm** | **LOO worst** | cal p | clears? |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SEM | 19 | **0.0384** (KU-RO fam) | 0.0384 | **0** | 0.005 | 0.0149 | 0.0149 | **0.0745** | **1.000** | 0.0066 | **NO** |
| ANA | 6 | 0.0038 | 0.0038 | 0 | 0.254 | 0.0697 | 0.2537 | 0.761 | 0.647 | 0.0266 | NO |
| TYR | 14 | **0.0731** | 0.0731 | 0 | 0.005 | **0.1542** | 0.1542 | 0.617 | 0.443 | **0.219** | NO |
| FIN (neg-ctrl) | 11 | 0.0009 | 0.0009 | 0 | 0.915 | 0.692 | 0.9154 | 1.000 | 1.000 | 0.445 | NO |
| CTRL (agnostic) | 12 | 0.0028 | 0.0028 | 0 | 0.532 | 0.393 | 0.5323 | 1.000 | 0.876 | — | NO |

`families_clearing_calibrated_and_serious`: **none**. `ctrl_agnostic_cleared_raw_bar`: **False**.
`negctrl_FIN_cleared_raw_bar`: **False**. `permissive == strict` for every family.

### 3.1 SEM is still one famous lexeme (`KU-RO`)

SEM strict rate 0.0384 (KU-RO/KU-RA/KU-RE) raw-clears the decisive nulls (0.0149) but fails Holm
(0.0745) and collapses under LOO (drop `kull` → decisive p 1.000). One shared accounting shortcut, no
other held-out form — the Egyptian-channel discipline verdict, unchanged by anchoring.

### 3.2 TYR highest raw match = shape typicality

TYR reaches 0.0731 (`A-DU-KU-MI-NA`, `A-RE-SA-NA`, `A-NA`, …) but the random-lexicon band reproduces it
(real percentile p **0.219**) — LA word-shape typicality (`A-` initial + `-na`), not lexical fit.

### 3.3 Controls behave

FIN (impossible language) decisive 0.915 / LOO 1.000; CTRL (agnostic random) decisive 0.532. The bar
credits neither an impossible language nor matched-structure noise.

## 4. What is and is not determined

- **Not determined (all NULL):** anchoring on the WP-G anchors gives **no** serious family any
  held-out reading power; no phonetic value, vowel, consonant, or language affiliation is assigned to
  any LA sign or class.
- **Determined (for the record):** (a) SEED_A = 0 — the 6 value-bearing anchors are one-toponym-deep,
  `circular_for_grading`, and add **0** matches (Δ = 0, all families); (b) pinning 17 sign-values covers
  135/1067 held-out words but reads **0** of them lexically; (c) the anchor constraint is
  family-independent (cannot arbitrate families), mirroring D5/F4; (d) strict scores reproduce H1 — SEM
  single-lexeme (KU-RO), TYR shape-typicality, controls at null.

## 5. Verdict and next step

```
H2_ROUND_2: AT_ANCHOR_CONSTRAINED_NULL
  - 0/3 serious families GENUINE on the strict (anchor-excluded, Art. XII) score.
  - anchor augmentation Δ = 0 for ALL families; anchor_adds_reading_beyond_sources = false.
  - anchors pin 17 signs, cover 135/1067 held-out words, read 0 (SEED_A = 0, one-toponym-deep).
  - SEM raw-clears on KU-RO alone -> Holm 0.0745, LOO 1.000 (single-lexeme).
  - TYR highest raw 0.073 -> random-lexicon percentile p 0.219 (shape typicality).
  - neg-control FIN and agnostic CTRL at the null (decisive 0.915 / 0.532).
```

Consistent with H1 and the whole campaign: internal structure and firm toponym anchors are real (L2)
but value-blind / one-deep, and no value-bearing family survives the multi-family end-to-end null even
when the audited anchors are supplied. Transfer licences **unchanged: NONE** (Art. XV). A GENUINE result
would still require held-out reading success + cross-site survival, which the established nulls make
near-impossible; run honestly, the round remains at the null.

**Compliance (Art. XXII):** prereg frozen before run; predictions external to LA and anchors marked
`circular_for_grading` + excluded (Art. XII honoured); multiplicity Holm-corrected across 5 families
(Art. VIII); effective_n reported per family (Art. VIII); decisive nulls + LOO + random-lexicon
calibration run; controls included; append-only; no licence bypass (Art. XV).
