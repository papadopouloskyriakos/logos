# Retroactive compliance — the existing record re-expressed in v2.0

Append-only (Art. XVII). Per AMENDMENT-001 this is **re-expression, not re-grading** (Art. XXIII
non-retroactive): every prior verdict stands unchanged; here it is restated in v2.0 claim layers
(Art. V), status vocabulary, transfer licences (Art. XV), with Art. XII circularity and Art. VIII
effective_n notes. Grounded in the programme reports + `CLAUDE.md`; produced by audit run `wf_4c40bcc4-428`.

## Submitted paper (TACL #11385 / Zenodo 10.5281/zenodo.21119213) — **COMPLIANT, no change**

- **Highest claim layer asserted:** **L2** (segmentation / document structure) — DP-unigram segmenter
  recovers scribal word division at micro-F1 0.436 vs 0.389 random, site-clustered LOSO gap CI excludes 0.
  Genuinely held-out-earned.
- Every layer above L2 is returned as **null / no-power / capped / declined**, never asserted: morphology
  NO-POWER; L3/L4 not claimed; L5 *301 gloss only critiqued; L6 phonetic explicit NULL ("no sound value is
  imputed for any sign"); L8 Salgarella isolate treated as an *identifiability constraint*, not a logos
  claim; L9 absent. Cross-script image leg touches L1 but is "circular by construction," ≤0.75-capped, "not
  a positive decipherment claim."
- **Art. XVII:** no overclaim ⇒ no ERRATUM, no INVALIDATION; adopting v2.0 **forces no change** to the
  byte-frozen PDF (sha256 in SUBMISSION_NOTES §(f)). The L0–L9 tabulation is a going-forward documentation
  convention that postdates the frozen submission and is not retrofitted into it.

## Completed / running programmes

| programme | layer attempted | highest **earned** | v2.0 status | licence | key note |
|---|---|---|---|---|---|
| **egyptian_calibration** | L6 phonetic (implicit L8) | **L0 / none on LA** | **`TRIVIAL_RECOVERY`** | PHONETIC not earned | Cretan one-shot: mechanical CONFIRM_GENERALIZES left unretuned (Art. IV/XVII); adversarial 4/4 lenses → RECOVERED_TRIVIAL = honest NULL. |
| **admin_schema** | L3 role / L4 semantic | **L2** structure | **`NO_POWER`** | none | Stage 5.1 pilot α 0.614 < 0.667 gate; human-gold path `INCOMPLETE` (annotators required). |
| **no_human_structure** | L3 role / L4 semantic | **L2** structure | **`NO_POWER`** (`NO_POWER_BEFORE_MODELING`; route CLOSED) | none | Edition-independent structural signal ≈ 0.026; pivoted to observable_channels. |
| **observable_channels** | L3 functional (commodity) | **L2** structure | **`RUNNING`** (Exp 1 = per-channel negative) | FUNCTIONAL not earned | Commodity carried by the document-series shortcut (0.63); word context fails A12 + cross-site. |

### Art. XII (never grade a target by the rule that created it)
- **egyptian_calibration:** LOW/mitigated — targets from an independent Egyptological edition; Edel read the
  terminal sign as š ≠ answer s, mitigating reading-circularity. Defect is *triviality/fragility*, not
  circularity.
- **admin_schema:** firewall ENFORCED — structural-control labels (numeral/logogram/total) excluded from the
  load-bearing semantic eval (forbids "assign QUANTITY from a numeral, then claim recovery").
- **no_human_structure:** CAUGHT & QUARANTINED — index-LF "precision on gold = 1.0" is circular (LF and gold
  share one cited index); honest load-bearing metric is the edition-independent 0.026.
- **observable_channels:** controlled by design — the logogram is MASKED and predicted from opaque word
  context, not read off itself. The exposed issue is Art. XIII (the series *convenience* must be removed;
  when it is, the signal collapses) — not self-grading.

### Art. VIII (effective_n, not raw_n)
- **egyptian_calibration:** raw_n = 3 anchors, **effective_n ≈ 1** — Lyktos is a pure-identity freebie;
  Knossos + Amnisos both hinge on the *same* terminal-š→s rule resting on *one* training record (HV-0234);
  leave-one-out flips 3→1 (REFUTE). Below the information floor (Art. IX).
- **admin_schema:** raw pilot 160 form-types, but agreed non-trivial GOLD_A = **4** (KN 0 / non-KN 4);
  α gates before power.
- **no_human_structure:** raw 4,759 forms, effective non-trivial REFERENCE_GOLD_A = **66** (PLACE 43 /
  HUMAN 23), only 2 of 4 load-bearing classes, grouped sealed ≈ 19; all descend from **one** lineage.
  Min-detectable 0.92 vs est 0.29 ⇒ power 0.0.
- **observable_channels:** **adequately powered** — 457 unseen-family (A12) test units, 115 logograms; the
  negative is a *signal* result, not underpower (the pivot fixed the label route's power problem).

### Obligations created by adoption (Art. XVIII / XVII)
All four verdicts are immutable honest negatives; none is repaired or re-run under its old `plan_hash`. Any
successor needs a fresh `plan_hash` + the predeclared thresholds (egyptian: fold-tolerant generic-Egyptian
baseline + support > n=1 + independent correspondences; no_human/admin: a genuinely independent
machine-readable source crossing the ≥3-load-bearing-class threshold). observable_channels must complete
experiments 2–6 + A0–A12 + the null battery before any gate verdict; LA output stays forbidden above the
STRUCTURAL/FUNCTIONAL licence, and SEMANTIC+ remain `NOT_AUTHORIZED`.
