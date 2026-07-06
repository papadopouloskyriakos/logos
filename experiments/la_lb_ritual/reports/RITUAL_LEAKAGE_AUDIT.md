# RITUAL_LEAKAGE_AUDIT — §XI (firewall proven before any matching interface)

`channel_class = EXPLORATORY_POSTHOC_CHANNEL`. Enforced by `tests/test_ritual_leakage.py` (7/7).

| guarantee | status |
|---|---|
| LA builder cannot read LB targets | ✅ (source-checked) |
| LB builder cannot read LA candidates | ✅ |
| Neither builder's blind generation reads the known-pair ledger | ✅ (LA quarantine uses a hardcoded known-forms set, one-directional, not the ledger file) |
| Drift feasibility does not import/fit the candidate/target packets | ✅ (observes operations only) |
| Packet A has no LB and no phonetic transliteration | ✅ (raw GORILA IDs only) |
| Packet B has no LA candidate / no LA sequence | ✅ |
| No report shows LA and LB inventories side by side | ✅ (except the quarantined public known-pair ledger, permitted) |
| No similarity function operates on the real inventories in this pass | ✅ (no module imports the admin real matcher; sim uses synthetic/within-script only) |

The firewall exists **before** any matching code. No real LA↔LB ritual matching, similarity, or score
is computed anywhere in this pass.
