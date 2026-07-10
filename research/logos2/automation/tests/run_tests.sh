#!/bin/bash
set -euo pipefail
WD=/home/claude-runner/gitlab/n8n/logos-logos2/research/logos2/automation
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
PASS=0; FAIL=0
ok(){ echo "PASS: $1"; PASS=$((PASS+1)); }
bad(){ echo "FAIL: $1"; FAIL=$((FAIL+1)); }

# T1 cron fixture install/remove preserves unrelated entries, single block, trailing newline
printf '#CRONICLE# 0 2 * * * /some/other.sh\n' > "$T/cron"
CRON_FIXTURE="$T/cron" bash "$WD/install_cron.sh" >/dev/null
CRON_FIXTURE="$T/cron" bash "$WD/install_cron.sh" >/dev/null   # idempotent second install
n_begin=$(grep -c "BEGIN LOGOS2_AUTOPILOT" "$T/cron"); n_other=$(grep -c CRONICLE "$T/cron")
tail -c1 "$T/cron" | od -An -c | grep -q '\\n' && nl_ok=1 || nl_ok=0
[[ $n_begin -eq 1 && $n_other -eq 1 && $nl_ok -eq 1 ]] && ok "cron install idempotent+preserving+newline" || bad "cron install"
CRON_FIXTURE="$T/cron" bash "$WD/remove_cron.sh" >/dev/null
grep -q CRONICLE "$T/cron" && ! grep -q LOGOS2 "$T/cron" && ok "cron remove selective" || bad "cron remove"

# sandbox repo for watchdog behaviour tests
R="$T/repo"; git init -q -b research/logos2-anchor-identifiability "$R"
mkdir -p "$R/research/logos2/automation/logs" "$R/research/logos2/automation/state" "$R/research/logos2/final"
cp "$WD/WATCHDOG_PROMPT.md" "$R/research/logos2/automation/"
echo '{"session_id":"test-sid","session_name":"logos2-autopilot"}' > "$R/research/logos2/automation/state/session.json"
echo '{"consecutive_failures":0}' > "$R/research/logos2/automation/AUTOPILOT_STATE.json"
printf 'x' > "$R/f"; git -C "$R" add -A; git -C "$R" -c user.email=t@t -c user.name=t commit -qm init
# make protected-asset spot-check pass trivially in sandbox: create matching baseline
echo "$(echo hi | sha256sum | cut -d' ' -f1)  /dev/null" > "$R/research/logos2/PROTECTED_ASSET_HASHES.sha256" || true
WDENV=(WD_REPO="$R" WD_SKIP_CLAUDE=1 WD_SKIP_PA=1 WD_LOCK="$T/l1" )

# T2 STOP behaviour
touch "$R/research/logos2/automation/STOP"
env "${WDENV[@]}" bash "$WD/logos2_watchdog.sh" && ok "STOP exits 0 (no launch)" || bad "STOP"
rm "$R/research/logos2/automation/STOP"

# T3 final-state exit
echo '{"campaign_closed": true}' > "$R/research/logos2/final/MACHINE_READABLE_SUMMARY.json"
env "${WDENV[@]}" bash "$WD/logos2_watchdog.sh" && ok "final-state exits 0" || bad "final-state"
rm "$R/research/logos2/final/MACHINE_READABLE_SUMMARY.json"

# T4 branch mismatch fails
git -C "$R" checkout -q -b wrongbranch
env "${WDENV[@]}" bash "$WD/logos2_watchdog.sh" 2>/dev/null && bad "branch mismatch should fail" || ok "branch mismatch fails closed"
git -C "$R" checkout -q research/logos2-anchor-identifiability

# T5 lock exclusion: hold the lock, second invocation exits 0 immediately
exec 8>"$T/l2"; flock -n 8
env WD_REPO="$R" WD_SKIP_CLAUDE=1 WD_SKIP_PA=1 WD_LOCK="$T/l2" bash "$WD/logos2_watchdog.sh" && ok "lock exclusion exits 0" || bad "lock exclusion"
exec 8>&-

# T6 consecutive-failure halt (mocked failures via WD_FORCE_FAIL); grep-based PA bypass:
# sandbox PA check fails -> counts as failures too; drive to >=8 and expect HALT marker
echo '{"consecutive_failures":0}' > "$R/research/logos2/automation/AUTOPILOT_STATE.json"
for i in $(seq 1 9); do
  env WD_REPO="$R" WD_SKIP_CLAUDE=1 WD_SKIP_PA=1 WD_FORCE_FAIL=1 WD_LOCK="$T/l3" bash "$WD/logos2_watchdog.sh" 2>/dev/null || true
done
[[ -f "$R/research/logos2/automation/WATCHDOG_HALTED.json" ]] && ok "8-failure halt marker written" || bad "halt marker"
# after halt, watchdog exits 0 without launching
env WD_REPO="$R" WD_SKIP_CLAUDE=1 WD_SKIP_PA=1 WD_LOCK="$T/l3" bash "$WD/logos2_watchdog.sh" && ok "halted -> no-op exit 0" || bad "halted behaviour"

echo "== $PASS passed, $FAIL failed =="
exit $([[ $FAIL -eq 0 ]] && echo 0 || echo 1)
