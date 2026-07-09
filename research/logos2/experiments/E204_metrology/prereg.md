# E204 — Fraction/metrology replication, extension, adversarial audit

**Classification (PRECHECK §4):** EXTENSION. Governed by MILESTONE2_CONTROL_ADDENDUM @ 5deec1e.
**Seal discipline:** the FRACTION_ORDER_ANETAKI_SEAL is NOT opened (its opening event — the
Anetaki II face-delta publication — has not occurred) and its contents (incl. the E004
derivation/controls files listed in its manifest) are NOT read, because E204's own model/
scoring/null/threshold stack is not yet frozen (§0.6) and the seal must stay prospective.

## Design that WOULD run (frozen for the record)
CP/SAT re-implementation of the epigraphic arithmetic constraint system over fraction-sign
values (variables = fraction signs; constraints = within-document additive relations between
entry quantities and totals involving fraction signs); four evidence components separated
(arithmetic / occurrence statistics / palaeographic composition / typological+optimality
priors); exact or bounded enumeration; leave-one-constraint-out; leave-one-component-out;
alternative bases and sub-bases; alternative optimality objectives; prior sensitivity;
transcription perturbation; matched random notation systems; whole-pipeline selection-aware
null; posterior/model averaging. Graduation ceiling L3 (quantity/metrological class); never L4.

## Blocking determination (mechanical census, 2026-07-10)
`signs_ontology.json` classifies 10 fraction signs (*802 *805 *806 *810 *815 *903 *904 *906
FRAC:L FRAC:double-mina). Their total occurrence in the accessible structured corpus:
**12 tokens across 10 documents; exactly 1 document carries ≥2 fraction signs.** Additive
arithmetic constraints require co-occurring fraction sequences with quantities; at n=1
multi-fraction document the constraint system has no power (cf. Corazza-Ferrara-scale inputs:
hundreds of fraction sequences from the full GORILA apparatus, which silver did not ingest).

**Verdict: BLOCKED_DATA (fail closed).** No arithmetic cell is run; no seal is touched.

## Data request (feeds EVIDENCE_ACQUISITION_PRIORITIES)
Ingest the GORILA klasmatogram (fraction-sign) apparatus into silver as a provenance-tracked
MEASUREMENT task (L0/L1): per-document fraction-sign sequences with adjacent integer
quantities and commodity context. This is an in-house transcription-normalization task on
already-licensed material — the highest-feasibility unblock in the campaign (no new
excavation or licence needed).
