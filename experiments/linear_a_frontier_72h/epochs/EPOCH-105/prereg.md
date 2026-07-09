# EPOCH-105 preregistration — cross-epoch dependency-aware synthesis + closure (§7)

**Reason:** SYNTHESIZE_EVIDENCE / CLOSE_FRONTIER. **Layer:** N/A (synthesis). **Licence:** none.

## Objective
Build the unified, dependency-aware evidence synthesis over all 104 epochs and emit every machine-readable closure
artifact + the master epoch table + reconciliation table, with all counts GENERATED from the append-only ledger
(invariant #12). Report, for the durable claim (A-), raw vs dependency-adjusted vs independent-channel support.

## Design (frozen)
`final/generate_closure.py` parses EPOCH_LEDGER.yaml, dedups to the terminal record per epoch (append-only history
preserved), classifies each epoch (dichotomy_side where present; heuristic verdict-keyword bucket otherwise, LABELLED
as such), and emits: EPOCHS_001_TO_FINAL_MASTER_TABLE.csv, RECONCILIATION_TABLE.csv, CAMPAIGN_FINAL_STATE.json,
FINAL_VERDICTS.json, GRADUATED_FINDINGS.json, STRONG_LEADS.json, METHOD_EXHAUSTION_MAP.json, PROSPECTIVE_SEALS.json,
ARTIFACT_MANIFEST.json.

## Dependency-adjusted independence (the load-bearing synthesis fact)
Per E102's independence audit, the campaign's above-null structure rests on ONE independent channel (context
co-occurrence); the positional channel (which carries A-) is independent but the vowel signal does not live there.
A- prefixation is itself a positional-channel constraint validated in its own right (E103). Report the durable
claim's independent-channel count = 1 and do NOT combine dependent p-values as independent evidence.

## Verdict rule
CLOSURE_SYNTHESIS_COMPLETE iff all closure artifacts emit, the reconciliation shows 0 running / 0 reserved-unexecuted
/ 0 missing-verdict (excluding terminal DE_AUTHORIZED), and the graduated-findings + strong-leads sets are frozen.

## Forbidden
No new claim is created here; synthesis only aggregates terminal epoch verdicts. No p-value combination across
dependent lineages. No licence change.
