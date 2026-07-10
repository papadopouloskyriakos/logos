# AMENDMENT W1 — watchdog failure-classification defect repair (2026-07-10)

## Failure class established
`SESSION_LIMIT_TRANSIENT`: at 2026-07-10 ~04:35 CEST all six subagents of workflow
wf_f945aa2d-05e failed with "You've hit your session limit · resets 6:20am
(Europe/Amsterdam)". A session/usage limit is a *transient quota condition with a
published reset time*, not a fault of the watchdog, the session, or the campaign.

## Defect
`fail_exit` counted EVERY nonzero `claude -r` return toward the 8-consecutive-failure
breaker (8 × 15 min = 2 h to permanent halt). A limit window can exceed 2 h, so an idle
session during such a window would permanently halt the autopilot (`WATCHDOG_HALTED.json`)
on a self-resolving condition. No failures had accrued when this was found (counter = 0;
the live session kept the watchdog in heartbeat no-op the whole outage).

## Repair (surgical; no semantics changed for genuine failures)
In the continuation branch only: if the `claude -r` log matches a session/usage-limit
signature, emit event `session_limit_transient` and exit 0 **without bumping and without
resetting** the consecutive-failure counter. All other nonzero returns still go through
`fail_exit` unchanged. Scientific machinery, thresholds, prompts, and the breaker itself
are untouched.

## Audit trail
As-run failure evidence: workflow wf_f945aa2d-05e journal (all six agents errored) —
preserved in the session transcript dir. Test suite rerun after the patch (see commit).
