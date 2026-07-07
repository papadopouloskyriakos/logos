# G2 — New High-Value Anchor Expansion

**Task.** Expand the anchor candidate set beyond the Foundry 115-record / 62-sign inventory (G1) by mining the silver corpus for candidates that JOINTLY constrain several signs, across the seven task classes (multi-slot toponyms; personal names in variant forms; titles with morphology; commodity/measure terms; seal-owner names; foreign names; shared cross-script formulae). For each: signs constrained, rule complexity, prior exposure, and — decisively — whether it can pin a VALUE from OUTSIDE the Linear-B/GORILA system.

**Constitution.** L2/L4 census; NON-CIRCULAR (Art. XII) — GORILA values label only, never a model input. Deterministic, seed 20260708. Attestation is corpus-measured (invariant 12): 1341 inscriptions, 984 distinct multi-sign words.

Artifacts: `scripts/g2_high_value_anchors.py` -> `data/anchors_v2/expanded.json`.

---

## 1. Candidate classes, ranked by relative-anchor strength (signs x sites)

`new_signs` = phonetic signs NOT already covered by any Foundry anchor record (Foundry covered 61 signs). `rule_cx` = simultaneous sign->value assignments if used to fix VALUES. `circular` = value claim would ride on GORILA homomorphy (Art. XII).

| candidate | class | signs | new | sites | objs | tok | rule_cx | kind | circular |
|---|---|---|---|---|---|---|---|---|---|
| A_libation_formula_core | A_formula | 19 | 0 | 10 | 22 | 39 | 19 | relative-only | YES |
| D_morphological_variants | D_morphology | 17 | 0 | 10 | 29 | 29 | 17 | relative-only | YES |
| B_transaction_terms | B_accounting | 9 | 1 | 3 | 58 | 83 | 9 | relative-only | YES |
| E_commodity_logogram | E_commodity | 9 | 1 | 3 | 28 | 29 | 9 | relative-only | YES |
| G_foreign_names | G_foreign | 9 | 0 | 3 | 4 | 4 | 9 | relative-only | YES |
| C_toponym_expansion | C_toponym | 10 | 1 | 2 | 5 | 5 | 10 | VALUE-BEARING | no |
| F_seal_formula | F_seal | 6 | 0 | 1 | 1 | 1 | 6 | relative-only | YES |

## 2. The decisive split — value-bearing vs relative-only

- **New VALUE-BEARING anchor classes:** 1 (C_toponym_expansion).
- **New FIRM held-out value anchors produced:** **0**. Every VALUE-BEARING candidate is the toponym channel, which G1 already showed saturated: 5 firm referents, each one-toponym-deep, 0 held-out-survivable. Expansion adds hedged/cf residue only.
- **New RELATIVE/structural anchor classes:** 6 (A_libation_formula_core, D_morphological_variants, B_transaction_terms, E_commodity_logogram, G_foreign_names, F_seal_formula).
- Relative anchors touch **35** distinct phonetic signs, of which **1** are NEW vs the Foundry inventory: PA3.

## 3. Per-class detail (measured)

### A_libation_formula_core  (A_formula)

- **Signs constrained:** 19 phonetic (A, DI, I, JA, KA, KI, MA, ME, NA, PI, RA, RU, SA, SI, TA, TE, TU, U, WA) + non-phonetic slots ['*301'].
- **New signs vs Foundry:** 0 (none).
- **Attestation:** 39 tokens / 22 objects / 10 sites ['Apodoulou', 'Iouktas', 'Knossos', 'Kophinas', 'Palaikastro', 'Platanos', 'Psykhro', 'Syme', 'Troullos', 'Vrysinas']; support {'Stone vessel': 37, 'Metal object': 1, 'Inked inscription': 1}.
- **Sequences attested / declared:** 8/8.
- **Rule complexity:** 19 simultaneous value assignments.
- **Prior exposure:** PUBLIC-PRINT+WEB (GORILA I–V; Duhoux; Davis 2014; Younger web; heavily indexed).
- **External referent:** False — cult invocation; NO external referent that fixes a phonetic value (the formula is read only by internal repetition + GORILA homomorphy)
- **Art. XII:** CIRCULAR: value claim would ride on GORILA homomorphic values (no external referent) — usable ONLY as a RELATIVE/structural anchor
- **Notes:** Highest-multiplicity internal anchor: fixes many signs' RELATIVE identity across objects via slot repetition (A-TA-I-*301-WA-JA/-WA-E; U-NA-KA-NA-SI/U-NA-RU-KA-NA-TI; I-PI-NA-MA/I-PI-NA-MI-NA) — the natural substrate for the substitution channel. VALUE-BLIND: relabeling-invariant, pins no absolute value.

### D_morphological_variants  (D_morphology)

- **Signs constrained:** 17 phonetic (A, DA, DU, I, JA, KU, MA, MI, NA, NI, PA, RE, RI, TA, TE, ZA, ZU).
- **New signs vs Foundry:** 0 (none).
- **Attestation:** 29 tokens / 29 objects / 10 sites ['Arkhalkhori', 'Haghia Triada', 'Khania', 'Kophinas', 'Nerokurou', 'Palaikastro', 'Petras', 'Syme', 'Tylissos', 'Zakros']; support {'Tablet': 18, 'Stone vessel': 9, 'Metal object': 2}.
- **Sequences attested / declared:** 12/12.
- **Rule complexity:** 17 simultaneous value assignments.
- **Prior exposure:** PUBLIC-PRINT (GORILA; Davis 2014 morphology) — indexed.
- **External referent:** False — a shared stem across inflected forms constrains that the stem signs carry the SAME value in every form — a RELATIVE constraint; asserts NO value
- **Art. XII:** CIRCULAR: value claim would ride on GORILA homomorphic values (no external referent) — usable ONLY as a RELATIVE/structural anchor
- **Notes:** Rich RELATIVE/morphological anchor set (paradigm cells). VALUE-BLIND: relabeling-invariant by construction; feeds segmentation/morphology WPs, not values.

### B_transaction_terms  (B_accounting)

- **Signs constrained:** 9 phonetic (KI, KU, NU, PA3, PO, RA2, RO, SA, TO).
- **New signs vs Foundry:** 1 (PA3).
- **Attestation:** 83 tokens / 58 objects / 3 sites ['Haghia Triada', 'Phaistos', 'Zakros']; support {'Tablet': 82, 'Stone vessel': 1}.
- **Sequences attested / declared:** 5/5.
- **Rule complexity:** 9 simultaneous value assignments.
- **Prior exposure:** PUBLIC-PRINT (Bennett; Schoep 2002; Younger) — extremely indexed.
- **External referent:** False — functional accounting role (total / deficit / grand-total / collector) is inferable from object layout, but the role fixes NO phonetic value
- **Art. XII:** CIRCULAR: value claim would ride on GORILA homomorphic values (no external referent) — usable ONLY as a RELATIVE/structural anchor
- **Notes:** L4 functional anchor: position after a numeric list marks 'total'. Constrains the RELATIVE identity of KU/RO/KI/PO/TO across many tablets. Any phonetic reading (e.g. Semitic kull- 'all') is a LANGUAGE hypothesis, NOT an external referent -> cannot pin a value non-circularly.

### E_commodity_logogram  (E_commodity)

- **Signs constrained:** 9 phonetic (KA, KU, NA, NU, PA3, RA2, SA, SI, U) + non-phonetic slots ['OLE'].
- **New signs vs Foundry:** 1 (PA3).
- **Attestation:** 29 tokens / 28 objects / 3 sites ['Haghia Triada', 'Phaistos', 'Syme']; support {'Stone vessel': 1, 'Tablet': 28}.
- **Sequences attested / declared:** 3/3.
- **Rule complexity:** 9 simultaneous value assignments.
- **Prior exposure:** PUBLIC-PRINT (GORILA) — indexed.
- **External referent:** False — adjacency to a commodity ideogram (OLE oil, GRA grain…) fixes a SEMANTIC field, not a phonetic value; the ideogram itself carries no syllabic value
- **Art. XII:** CIRCULAR: value claim would ride on GORILA homomorphic values (no external referent) — usable ONLY as a RELATIVE/structural anchor
- **Notes:** L5 semantic-field anchor at best. Does NOT license a phonetic value (Art. XV SEMANTIC != PHONETIC). Circular for value grading.

### G_foreign_names  (G_foreign)

- **Signs constrained:** 9 phonetic (A, I, KA, MA, NA, RA, RE, SA, TA).
- **New signs vs Foundry:** 0 (none).
- **Attestation:** 4 tokens / 4 objects / 3 sites ['Haghia Triada', 'Palaikastro', 'Zakros']; support {'Tablet': 2, 'Stone vessel': 2}.
- **Sequences attested / declared:** 3/3.
- **Rule complexity:** 9 simultaneous value assignments.
- **Prior exposure:** PUBLIC-PRINT (S&M 2017 onomastics; Egyptian toponym lists) — indexed.
- **External referent:** conditional — a name shared with a READABLE script (LB/Cypriot/Egyptian list) COULD pin values via the readable side — but each proposed match is value-blind resemblance on a huge name space (the multiplicity trap); no firm bilingual
- **Art. XII:** CIRCULAR: value claim would ride on GORILA homomorphic values (no external referent) — usable ONLY as a RELATIVE/structural anchor
- **Notes:** In PRINCIPLE value-bearing IF a genuine bilingual name-match existed; in practice the same relabeling/multiplicity problem as the PN channel (G1). No firm anchor.

### C_toponym_expansion  (C_toponym)

- **Signs constrained:** 10 phonetic (I, NI, PA3, QA, RA, RU, SA, TI, TU, WA) + non-phonetic slots ['*310'].
- **New signs vs Foundry:** 1 (PA3).
- **Attestation:** 5 tokens / 5 objects / 2 sites ['Haghia Triada', 'Kophinas']; support {'Tablet': 4, 'Stone vessel': 1}.
- **Sequences attested / declared:** 2/4.
- **Rule complexity:** 10 simultaneous value assignments.
- **Prior exposure:** PUBLIC-WEB (Younger LA toponym pages) — indexed.
- **External referent:** True — a KNOWN Cretan place-name is an external referent (value-bearing IN PRINCIPLE) — but the equation is still SPOTTED via GORILA homomorphy, and G1 showed the firm-toponym set is saturated (5 firm, all one-toponym-deep)
- **Art. XII:** VALUE-BEARING channel (external referent) — but see G1: firm set saturated, all one-toponym-deep, 0 held-out-survivable
- **Notes:** HEDGED/cf only. Adds ~0 FIRM new external referents beyond the Foundry 5; residue is speculative or one-object-deep. Value-bearing channel is effectively saturated.

### F_seal_formula  (F_seal)

- **Signs constrained:** 6 phonetic (A, KA, ME, NU, RA, SA).
- **New signs vs Foundry:** 0 (none).
- **Attestation:** 1 tokens / 1 objects / 1 sites ['Iouktas']; support {'Clay vessel': 1}.
- **Sequences attested / declared:** 1/2.
- **Rule complexity:** 6 simultaneous value assignments.
- **Prior exposure:** PUBLIC-PRINT (CMS; Karnava; Decorte) — indexed.
- **External referent:** False — the 'Archanes formula' on seal-stones (A-KA-NU-… / A-SA-SA-RA-ME) repeats across seals but names an unknown owner/deity — NO external value referent
- **Art. XII:** CIRCULAR: value claim would ride on GORILA homomorphic values (no external referent) — usable ONLY as a RELATIVE/structural anchor
- **Notes:** DATA-ABSENT here: cannot be measured against the silver corpus. High multiplicity in the literature but VALUE-BLIND (internal repetition). Flagged NOT_MEASURED.

## 4. Verdict

ALL high-multiplicity NEW anchors (libation formula, accounting terms, morphological paradigms, commodity, seal formulae) are VALUE-BLIND / relabeling-invariant: they enrich the RELATIVE-structure substrate (substitution/segmentation/morphology WPs) but cannot, per Art. XII, grade an absolute-value hypothesis without riding on GORILA homomorphy. NO new value-bearing held-out anchor was produced. G1's conclusion stands: a bilingual or >=3 genuinely independent held-out anchors remain required.

**Bearing on the campaign.** Expansion is a large WIN for the RELATIVE programme and a clean NULL for the value programme. The libation formula (22 objects / 10 sites, slot-varying: `A-TA-I-*301-WA-JA`/`-WA-E`, `U-NA-KA-NA-SI`/`U-NA-RU-KA-NA-TI`, `I-PI-NA-MA`/`I-PI-NA-MI-NA`) plus the accounting family and ~80 morphological paradigm pairs give the load-bearing SUBSTITUTION channel a rich, cross-site, relabeling-invariant substrate — exactly what it must be audited on. But not one of them derives a value from outside Linear B: every new high-multiplicity anchor is VALUE-BLIND, and the only value-bearing channel (toponyms) was already shown saturated in G1 (5 firm, one-toponym-deep, 0 held-out-survivable). **G2 adds 0 new held-out value anchors.**

*Generated by `scripts/g2_high_value_anchors.py`; all counts echoed from `data/anchors_v2/expanded.json` (invariant 12).*