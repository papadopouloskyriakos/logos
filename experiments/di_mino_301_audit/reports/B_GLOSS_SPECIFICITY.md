# B — Gloss Specificity (Di Mino H3: gloss "dwell")

**Prereg** DI_MINO_EXACT_CLAIM_V1 (sha 8b098a4c) · **Seed** 20260708. Machine-readable tiers, pre-declared; nothing counts identical to 'dwell' silently.

## B4 — Semantic-specificity tiers (relative to the claim gloss 'dwell')

- **exact**: abide, dwell, inhabit, live, reside
- **near**: encamp, keep-at-home, lodge, remain, rest, settle, sojourn, spend-night, stay, tabernacle
- **broad**: abode, camp, dwelling, encampment, fold, habitation, home, meadow, oasis, pasture, resting-place, steppe, tent
- **unrelated**: any gloss outside the three sets above (e.g. intend, journey, drive-away, die, return, be-high).

## Tier assignment of the TARGET root's ACTUAL glosses, per language

| language | attested gloss(es) | tier | ends in yod? |
|---|---|---|---|
| Hebrew | dwell; abide; abode; habitation; pasture; rest; keep-at-home | **exact** | no |
| Aramaic | abode; dwelling; resting-place; rest | **near** | no |
| Akkadian | steppe; pasture; encampment; camp | **broad** | no |
| Ugaritic | drive-away; expel; chase | **unrelated** | YES |
| Arabic | intend; purpose; resolve; journey; depart; be-distant; date-stone | **unrelated** | YES |

## Best-of-language search over the fixed skeleton (weak collapse)

- load-bearing languages (excl. Ugaritic-uncertain): **4**
- dwell-tier: ['Hebrew', 'Aramaic', 'Akkadian']
- unrelated: ['Arabic']
- **literal-yod languages** (attested root actually ends in yod): ['Ugaritic', 'Arabic'] -> glosses {'Ugaritic': ['drive-away', 'expel', 'chase'], 'Arabic': ['intend', 'purpose', 'resolve', 'journey', 'depart', 'be-distant', 'date-stone']}; dwell-tier among them: NONE

The 'dwell' gloss is a **best-of-language selection**: it is discarded by the two languages that actually match the final yod, and survives only by switching to n-w-h (Hebrew/Aramaic) or the pastoral n-w-' (Akkadian).

## How high is the prior of reaching *some* 'dwell' gloss?

- **13 distinct** Semitic roots carry a dwell-tier gloss: 'hl, dwr, gwr, lwn, nw', nwh, nzl, qtn, skn, sry, wsb, ysb, ytb. The dwelling/settling semantic field is densely populated, so a family-wide root search reaches a dwell-tier gloss readily.

## B5 — Does "dwell" predict observable formula features better than rivals?

Pre-declared feature-compatibility table (NO LLM). Formula features (report 03 §E):

- **F1_precedes_theonym_recipient**: slot-1 word precedes JA-SA-SA-RA-ME (widely read as a divine name) -> favours a verb that TAKES the deity as an argument (recipient/vocative)
- **F2_dedicatory_libation_context**: carried on libation vessels/tables at cult sites -> favours an offering/dedication/invocation illocution
- **F3_transitive_object_slot**: the formula frame supplies following nominal slots -> favours a transitive verb over an intransitive stative

| gloss | F1 recipient | F2 dedicatory | F3 transitive | score /3 |
|---|---|---|---|---|
| dwell | 0.0 | 0.0 | 0.0 | **0.0** |
| give | 1.0 | 1.0 | 1.0 | **3.0** |
| dedicate | 1.0 | 1.0 | 1.0 | **3.0** |
| invoke | 1.0 | 1.0 | 0.5 | **2.5** |
| intend | 0.0 | 0.0 | 0.5 | **0.5** |
| NEUTRAL_PLACEHOLDER | 0.0 | 0.0 | 0.0 | **0.0** |

Random-gloss expected score ≈ 1.80. 'dwell' scores 0.0/3 — at or below the neutral placeholder and BELOW give/dedicate/invoke (3.0/2.5); it does NOT predict observable formula features better than rivals. Diagnostic only (no bilingual = no ground truth).

> Diagnostic, not decisive: absent a bilingual there is no semantic ground truth. The point is that observable formula structure does **not** favour 'dwell' over the dedicatory give/dedicate reading — if anything the deity-recipient slot disfavours an intransitive stative.
