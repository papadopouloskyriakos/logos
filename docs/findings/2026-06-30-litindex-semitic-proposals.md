# Finding 2026-06-30 — litindex populated with 6 verified West-Semitic proposals (2 candidates rejected)

Populated the §C.1 decontamination index (`scripts/comparison/litindex.py`) with the published
West-Semitic Linear A proposals — the first of the two gates on the C.4 contamination number
(`2026-06-30-c4-ablation-qwen72b.md`). Because a **fabricated or mis-attributed claim poisons the
regurgitation detector** (worse than a gap), every candidate was independently verified before
inclusion; 2 of 8 were **rejected**.

## Method — adversarial per-claim verification

Recon (web) surfaced 8 candidate equations attributed to Gordon via the BAS Library "Is Linear A
Semitic?" sidebar. An 8-agent workflow then independently corroborated each against sources **other
than BAS** (default-to-REJECT). The decisive independent source was **G. A. Rendsburg, "'Someone Will
Succeed in Deciphering Minoan': Cyrus H. Gordon and Minoan Linear A", *Biblical Archaeologist* 59:1
(1996) 36–43** (JSTOR 3210534), which enumerates Gordon's vessel equations as exactly **three**.

## Written (6, claim_type=`semitic_proposal`)

| sign | value | reading | attribution |
|---|---|---|---|
| `SU-PU` | sp | Ugaritic *sp* / Heb. *sap* "bowl" | Gordon 1966 (orig. Antiquity 31, 1957) |
| `KA-RO-PA` | krpn | Ugaritic *krpn* "goblet" | Gordon 1966 |
| `SU-PA-RA` | spl | Ugaritic *spl* / Heb. *sēpel* "bowl" | Gordon 1966 |
| `KU-RO` | kull | Semitic *kull* "total" (etymology of the accounting term) | Gordon 1966 |
| `JA-NE` | yn | West-Semitic "wine" (Heb. *yayin*, Ugar. *yn*) | Gordon 1966, Plate X |
| `A-SA-SA-RA-ME` | asherah | vocative "oh Asherah!" | **Best 1981** (Talanta 13), *not* Gordon |

## Rejected (2) — the verification earning its keep

- **`qa-pa` = Akkadian *kappu*** — UNVERIFIED. Only the BAS page attributes it to Gordon; Rendsburg's
  authoritative list of *three* vessel equations omits it. Omitted.
- **Semitic `ki-ro`** — UNVERIFIED. No attributable peer-reviewed Semitic etymology exists; the *kull*
  etymology belongs to `ku-ro`, a different word. `KI-RO` keeps only its accounting `lexical_reading`.

## Corrections applied

`ka-ro-pa` → Ugaritic *krpn* (the "Akkadian karpu / carafe" gloss is a popularization, not in
Rendsburg); `ya-ne` keyed `JA-NE` per GORILA/corpus convention (the corpus has no `YA`), with Gordon's
`ya-ne` transcription preserved in the note. All Semitic readings are flagged **DISPUTED** — indexed to
*catch regurgitation*, never as accepted readings.

## State + what's still gated

Index now 63 claims (was 57). Component signs were already `L_known` via the LB-transfer seed, so the
partition is unchanged; the value is that the LLM's **cognate proposals** (root/gloss) now have real
Semitic targets to be quarantined against. `SEED_NONEXHAUSTIVE` stays True. Verified: 250 passed,
4 xfailed; litindex tests +1 regression locking the verified set and the two omissions.

**The C.4 contamination number is still not fully live:** this closes gate 1 (index content); gate 2
remains — wiring `ablation.contamination()` to match the LLM's **cognate glosses/roots** against these
lexical claims (the value-vocabulary reconciliation), since the metric currently keys only on
phonetic `(sign, value)` correspondences.
