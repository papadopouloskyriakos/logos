# LOGOS-2 autopilot policy

- One worker at a time: the registered campaign session (state/session.json) is resumed by the
  watchdog ONLY when `claude agents --json` shows no active worker for this repo family. The
  flock in state/watchdog.lock serializes watchdog instances themselves.
- Permission mode: acceptEdits, never bypassPermissions; project policy governs Bash; blocked
  operations fail closed and are recorded.
- No secrets in repo, cron, logs, or state. No sudo, no root cron, no /etc/crontab.
- Protected assets are spot-checked every wake; a mismatch is a hard stop (no launch).
- STOP file (automation/STOP) halts new launches; WATCHDOG_HALTED.json (8 consecutive failures)
  halts launches while leaving scientific jobs untouched; final closure
  (final/MACHINE_READABLE_SUMMARY.json campaign_closed=true) ends the loop.
- Watchdog never kills processes; reruns of failed experiments happen only under campaign
  governance (amendment discipline), decided by the resumed agent, never by the watchdog.
- Frozen conclusions in section 1 of the super-prompt are binding and non-reinterpretable.
