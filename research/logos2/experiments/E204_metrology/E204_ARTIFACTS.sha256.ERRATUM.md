# ERRATUM — E204_ARTIFACTS.sha256 (append-only record; the frozen file is NOT edited)

Dated 2026-07-10. The artifact freeze taken at the BLOCKED stage included `STATUS.json`,
which is a LIVE status pointer, not a frozen artifact. Its hash legitimately changed when
the experiment progressed:

- frozen line: `42cb4feca07e2fd148f5936c52b4f2dd513b1f2c9d533b2e8e8e75ade8cda5e1  STATUS.json`
  (status `BLOCKED_DATA`, commit 5c0f926 era)
- current:     `50703280b2a8fcc1c13e0de3e9aad39280450f466af7b44473952333ace57cd1  STATUS.json`
  (status `METROLOGY_STACK_FROZEN`, set at prereg commit bc5599f; prior status preserved inside the file)

Scope: this erratum covers ONLY the `STATUS.json` line. Every other line in
`E204_ARTIFACTS.sha256` remains binding and is verified by `verifiers/run_battery.py`.
No result, verdict, or data artifact is affected.
