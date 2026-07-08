# FRONTIER-72h — MISSION REMINDER (self, coordinator)

*Loaded by the 10-minute cron reminder. Keeps the objectives + architecture in front of me across
long gaps and context resets. This is a reminder, not a re-run trigger.*

## Mission
Continue the honest attempt to decipher Linear A on the frontiers left open by the closed anchor-lattice
campaign (`ANCHOR_LATTICE_UNDERDETERMINED`). Build **independent symmetry-breaking channels**, integrate
them, and **retain only sign-value systems that make cross-source / cross-site / held-out predictions no
random-anchor or dependency-clone lattice can match**. Earn a *real* reading; refuse a *fitted* one.
Ceiling today: **L2/L3** (structural/administrative). All 7 transfer licences **NOT_EARNED**.

## Architecture — the part to never forget
- **This Claude session = coordinator / scientific overview / independent verifier / banker.** I design the
  prereg + frozen verdict rule, judge scientific soundness (is the null the right null? is the PC fair?),
  independently recompute every load-bearing number, and bank.
- **GLM-5.2 = the worker**, driven by **scripts** over the z.ai LiteLLM proxy — **not** Claude subagents:
  - `scripts/zai_agent.py` — claude-code-free GLM tool-use loop (run_bash / read_file / write_file).
  - `scripts/epoch_runner.py` — the **gated runner**: `run_epoch()` = worker + mechanical completion gate
    (`check_epoch`: required files, plan_hash==sha256(prereg), result schema + verdict-vocab + ≥5
    successors, disclaimer-aware overclaim scan, reproducibility re-run, pluggable numeric `repro_check`)
    + **auto-repair** (≤2 passes) ; `spec_for()` = canonical paths + path contract ; `git_add_existing()`.
- **DO NOT use the Workflow tool / Claude subagents for the token-intensive repetitive labour** — that
  spends Anthropic tokens; the whole point of the split is that GLM (z.ai) does that work via the scripts.
  Reserve Claude tokens for orchestration, scientific judgement, and verification.

## The clock (mechanical — do NOT finalize early)
Window **2026-07-08T03:20Z → 2026-07-11T03:20Z**; minimum 18 substantive epochs. Finalization is gated by
`scripts/clock_check.py`: authorized only when `now ≥ campaign_end AND completed_epochs ≥ 18`. A null is
**not** an early-stop. No idle-waiting, no padding/filler commits. Finalizing before the gate is FORBIDDEN.

## Per-epoch discipline (every epoch)
Prereg + `plan_hash` frozen BEFORE running → **positive control first** (gates the verdict, fail-closed) →
adaptive / frequency-matched null → multiplicity correction → **mechanical verdict from the frozen rule** →
≥5 successors. **Non-circular:** anonymous sign IDs, no phonetic/semantic values, Linear B control-only.
Append-only ledger (`EPOCH_LEDGER.yaml`), `git add -f`, commit + push each epoch. Verify-then-bank:
GLM proposes/operates, the gate enforces the contract, Claude judges soundness + recomputes, THEN bank.

## Current state
24/24 epochs banked. Strongest LA positive = **A- prefixation** (anonymous positional slot, L2/L3):
E022 global adaptive null (p .0002) → E023 site held-out (9/10, cross-site robust) → E024 multi-axis
(support 5/6 incl. Nodule=0, chronological phase 4/4). **Capstone still ahead: §12 frontier-exhaustion map.**

## What each cron firing should do
1. Run `python3 experiments/linear_a_frontier_72h/scripts/frontier_status.py` and print it (datetime + ETA
   + progress). 2. Re-read this mission. 3. If a worker is idle, the clock has NOT expired, and unblocked
   work remains → I MAY advance ONE gated epoch via `epoch_runner` (GLM), verify, bank. Else report + hold.
**Never** finalize before `clock_check.py` authorizes it.
