# Branch-status reconciliation

Independent comparison of each campaign's `STATUS.md` header vs its authoritative final verdict
(CAMPAIGN.md/DECISION_LOG.md/TASK_LEDGER.yaml). **The authoritative status always lives in the ledger/decision
log; STATUS.md headers are cosmetic and were NOT rewritten (read-only audit).**

| branch | STATUS.md header | authoritative final verdict | reconciliation |
|---|---|---|---|
| di-mino | "CLOSED 2026-07-08: DI_MINO_CORE_VERDICT=REJECT" | REJECT | ✅ CURRENT |
| relative-phonology | "CAMPAIGN CLOSED (final verdict issued)" | NEW_CONSTRAINTS_BUT_NO_DECIPHERMENT | ✅ CURRENT |
| constraint-expansion | ends mid-campaign ("Next: H+J, K, L", Stages E+F) | NEW_CONSTRAINTS_BUT_NO_DECIPHERMENT (CAMPAIGN.md) | ⚠ STALE header; verdict in CAMPAIGN.md |
| foundry | "do not issue final verdict until quotas complete" (mandate text) | NEW_CONSTRAINTS_AND_A_SHARPER_OBSTACLE (FINAL_CAMPAIGN_REPORT.md) | ⚠ STALE header; verdict in FINAL_CAMPAIGN_REPORT |
| admin-schema | "SCAFFOLD created … status=INCOMPLETE" | automated pilot NO_POWER; human gate CLOSED_BY_OWNER | ⚠ STALE; also lists Stage 5 twice |
| no-human | "Programme opened … UNTESTED" | source-label route NO_POWER_BEFORE_MODELING | ⚠ STALE header |
| observable | "Programme opened … pivot" | L3 channel REFUTED / L2 SUPPORTED-no-licence | ⚠ STALE header; verdict in DECISION_LOG |
| external-anchors | "NO_POWER … Next: fit the frozen Hoch" | **EA-13 frozen pass: POWERED_DESIGN at La≥4, scarcity-limited** | ⚠ MATERIAL: the "Next" ran; NO_POWER is superseded by the frozen pass (P1 missed it) |
| la-lb-continuity | both "CLOSED+ARCHIVED split verdict" AND a mid-pass header | H_exact=NULL_PUBLISHED / H_drift=NO_POWER | ⚠ self-contradictory header; verdict in FINAL_CHANNEL_VERDICT.md |
| la-lb-ritual | "Verdicts (not yet issued)" then status=COMPLETE/NO_POWER next line | NO_POWER | ⚠ STALE/self-contradictory header |
| egyptian | "READY_FOR_PREREG / first channel to pass its gate" | mechanical CONFIRM but honest TRIVIAL (effective-n≈1); CLOSED | ⚠ STALE; verdict in FINAL_EGYPTIAN_CHANNEL_VERDICT + reconciliation |

**Proposed corrections (NOT applied — old history preserved):** update the ~8 stale STATUS.md headers to point to
their final-verdict artifact; the one *material* correction is external-anchors (EA-02 NO_POWER → design-powered-
at-La≥4-but-scarcity-limited per EA-13). None changes a scientific conclusion; all are cosmetic except EA-02.
