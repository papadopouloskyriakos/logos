# 03 — Exact `*301` + Libation-Formula corpus (T04)

**Prereg:** `DI_MINO_EXACT_CLAIM_V1` (sha `8b098a4c`). **Constitution:** v2.2. **Seed:** 20260708.
**Generator:** `scripts/build_libation_formula_corpus.py` → `data/libation_formula_exact/corpus.json`
(sha256 `0526ed73…`). **Source:** `corpus/silver/inscriptions_structured.json` (GORILA-derived silver;
edition = *GORILA*, Godart & Olivier 1976–1985; digitized via SigLA). All counts are script-generated
(invariant 12). **Non-circular:** no phonetic value is assigned to `*301` here.

## A. Headline counts (measured)

| quantity | value |
|---|---|
| `*301`-bearing attestations | **36** |
| distinct `*301` forms | **23** |
| `*301` inscriptions | 36 (one form each; 36 word-tokens) |
| Libation-Formula carriers (structural markers) | **31** |
| LF carriers WITHOUT `*301` (formula frame only) | 15 |
| `*301` graphic token variants | `*301`, `I+*301`, `DA+*301`, `MI+*301` (3 are ligatures) |

`*301` occurs both as a free syllabogram in the religious formula (invocation-verb slot) **and** as a
ligature (`I+*301`, `DA+*301`, `MI+*301`) in administrative contexts (nodules, roundels, tablets) — a
distributional fact the `/na/` reading must accommodate, since a CV syllabogram `/na/` inside an
administrative ligature `MI+*301` (Khania roundels) has no obvious religious-verb interpretation.

## B. Partition (per frozen prereg §Global partitions)

**Derivation set** (frozen religious language Di Mino derives on): `IOZa2` (Iouktas — his Figure 1
inscription), `TLZa1` (Troullos — fullest formula), and the `i-*301` core (the `I+*301` ligature
anchors `HTWa1022`, `KN2`). Derivation **sites** = {Iouktas, Troullos}.

**Held-out set:** all other `*301` forms — LF carriers at non-derivation sites + **all** administrative
`*301` tablet/nodule/roundel forms + the prereg-named leave-form-out variants `TA-NA-I-*301-U-TI-NU`
(`IOZa6`) and `A-TA-I-*301-DE-KA` (`ZAZb3`).

| partition | attestations |
|---|---|
| DERIVATION | 4 (`IOZa2`, `TLZa1`, `HTWa1022`, `KN2`) |
| HELD_OUT | 32 |
| HELD_OUT & **leave-site-out eligible** (site ∉ derivation sites) | **26** |
| HELD_OUT invocation-verb-slot & leave-site-out eligible | **11** |

**Power:** `held_out_leave_site_out ≥ 3` → **ADEQUATE** for H1 (prereg NO_POWER threshold = ~3
independent held-out `*301` forms). Held-out leave-site-out sites (13): Apodoulou, Arkhalkhori,
Haghia Triada, Khania, Knossos, Kophinas, Palaikastro, Psykhro, Skoteino Cave, Syme, Tiryns, Tylissos,
Zakros.

## C. ⚠ Partition-integrity flag (honesty, not silently resolved)

The prereg's "no site/form in both partitions" rule collides with its own naming of `IOZa6`
(`TA-NA-I-*301-U-TI-NU`) as a held-out variant: **Iouktas is a derivation site** (`IOZa2`). Five
held-out Iouktas forms therefore sit on a derivation site and are **leave-form-out eligible but NOT
leave-site-out clean**:

| id | form | site | status |
|---|---|---|---|
| `IOZa3` | A-TA-I-*301-WA-JA | Iouktas | site-contaminated (also = target form) |
| `IOZa4` | *301-WA | Iouktas | site-contaminated |
| `IOZa6` | TA-NA-I-*301-U-TI-NU | Iouktas | site-contaminated (prereg-named held-out) |
| `IOZa7` | A-TA-I-*301-WA-JA | Iouktas | site-contaminated (also = target form) |
| `IOZa8` | A-NA-TI-*301-WA-JA | Iouktas | site-contaminated |

**Consequence for the gate:** H1's success requires *both* leave-target-out *and* **eligible
leave-site-out**. `IOZa6` satisfies leave-form-out only; it must **not** be counted toward the
leave-site-out clause. After removing the target form (`A-TA-I-*301-WA-JA`, 11 attestations, incl.
Iouktas/Troullos derivation copies) the leave-site-out held-out `*301` pool is the 26 non-derivation-
site attestations, of which the invocation-verb-slot variants at clean sites are:
`A-TA-I-*301-WA-E` (PKZa11, Palaikastro), `A-TA-I-*301-DE-KA` (ZAZb3, Zakros),
`TA-NA-I-*301-TI` (PSZa2, Psykhro), `JA-TA-I-*301-U-JA` (APZa1, Apodoulou), plus 7 A-TA-I-*301-WA-JA
copies at Kophinas/Syme/Palaikastro (these vanish under leave-target-out). Net **clean, non-target
invocation-slot held-out variants = 4 sites** — barely above the NO_POWER floor and each one-form-deep.

## D. The 23 distinct `*301` forms (form → inscriptions)

Invocation-verb slot (position 1 of the Libation Formula), word-initial:

| form | attest. | inscriptions (site) | partition |
|---|---|---|---|
| **A-TA-I-*301-WA-JA** (target) | 11 | IOZa2/3/7 (Iouktas), KOZa1 (Kophinas), PKZa12 (Palaikastro), SYZa1/2/3/4/8 (Syme), TLZa1 (Troullos) | DERIV (IOZa2,TLZa1) + HELD_OUT |
| A-TA-I-*301-WA-E | 1 | PKZa11 (Palaikastro) | HELD_OUT |
| A-NA-TI-*301-WA-JA | 1 | IOZa8 (Iouktas) | HELD_OUT (site-contam) |
| A-TA-I-*301-DE-KA | 1 | ZAZb3 (Zakros) | HELD_OUT (named) |
| TA-NA-I-*301-U-TI-NU | 1 | IOZa6 (Iouktas) | HELD_OUT (named, site-contam) |
| TA-NA-I-*301-TI | 1 | PSZa2 (Psykhro) | HELD_OUT |
| JA-TA-I-*301-U-JA | 1 | APZa1 (Apodoulou) | HELD_OUT |
| *301-WA | 1 | IOZa4 (Iouktas) | HELD_OUT (site-contam) |

Administrative / other context (NOT part of the public claim — this audit's generalization test):

| form | attest. | inscriptions (site) |
|---|---|---|
| TE-*301 | 2 | HT8a, HT98a (Haghia Triada — tablets) |
| I+*301 | 2 | HTWa1022 (nodule, DERIV), KN2 (Knossos tablet, DERIV) |
| MI+*301 | 2 | KHWc2064, KHWc2099 (Khania roundels) |
| *301-NA | 1 | KH5 (Khania tablet) |
| *301-SI | 1 | TIZb1 (Tiryns) |
| *301-U-RA | 1 | HT115a (Haghia Triada) |
| A-*301 | 1 | KH58 (Khania) |
| A-*301-KI-TA-A | 1 | TYZb4 (Tylissos) |
| DA+*301 | 1 | KH18 (Khania) |
| DA-DU-*301 | 1 | DRAZg1 (unprovenanced) |
| E-*301 | 1 | HTWa1026 (Haghia Triada nodule) |
| NA-TU-*301-NE | 1 | SKOZc1 (Skoteino Cave) |
| SA-*301-RI | 1 | ZA11b (Zakros) |
| ZU-*301-SE-DE-*21F-*118 | 1 | ARKH2 (Arkhalkhori) |
| A-RE-NE-SI-DI-*301-PI-KE-PA-JA-TA-RI-SE-TE-RI-MU-A-JA-KU | 1 | KNZf13 (Knossos metal) |

## E. Libation-Formula frame (the recurring slots the target sits inside)

Full-formula exemplars (all slots present) are **IOZa2** and **TLZa1** — exactly the two derivation
inscriptions, i.e. the fullest formulae are the ones the claim was built on. Recurring slots
(value-free markers): invocation-verb `A-TA-I-*301-WA-JA`(~) → `JA-DI-KI-TU`/`A-DI-KI-TE` →
`(JA-/A-)SA-SA-RA-ME` → `U-NA-KA-NA-SI`(~) → `I-PI-NA-MA`(~) → `SI-RU-TE`. 15 LF carriers lack `*301`
entirely (e.g. `JA-SA-SA-RA-ME · U-NA-KA-NA-SI` at IOZa9/PKZa27; `A-SA-SA-RA-ME` at IOZa10/PKZa4) —
these hold the formula frame fixed while the position-1 word varies, and are held-out context for H4
(invocation-verb slot behaviour).

## F. Source-dependency (Art. XI)

**Single-source** for every form: GORILA (with SigLA as a digitiser of the same autopsies). There is
**no independent second epigraphic witness** inside the corpus for any single `*301` attestation; the
34 singleton forms carry no internal cross-check. This caps how much any one-attestation held-out form
(e.g. the four clean invocation variants in §C) can bear: each is one toponym / one object deep, the
same fragility flagged in the cross-script gate (memory: crossscript-gate-phase0).

## G. Verdict inputs handed to the gate
- H1 power = **ADEQUATE** on raw held-out count (26), but the *clean, non-target, leave-site-out
  invocation-slot* pool is **4 forms across 4 sites**, each single-attestation → the discriminating
  evidence is thin and **each form is one-source (GORILA)**.
- The prereg-named held-out anchor `IOZa6` is **leave-site-out-contaminated** and may score only under
  leave-form-out — recorded here, enforced downstream (never counted for the leave-site-out clause).
- `*301` is distributed across religious AND administrative registers (ligatures) — any single value
  for `*301` must be consistent with both; the public claim addresses only the religious register.
