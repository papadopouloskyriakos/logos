# vast.ai instance 44534071 — full result backup (2026-07-16)

Complete, checksum-verified backup of ALL results on rental instance `44534071` (`ssh1.vast.ai:14070`)
taken 2026-07-16 ~15:08 CEST, immediately before wrap-up + `vastai destroy`.

## Contents
- `csa_backup_20260716.tgz` — tarball of the instance's entire `/root/logos/runtime/csa_sweep/` tree
  (173 files). **Remote-computed sha256 = `b71fa4e990a6d931e86bc34e6e905355cc9929151238b04383f9cf9ac90a4444`**;
  the pulled tarball matched byte-for-byte (Check 0).
- `csa_sweep/` — extracted tree:
  - `cells/` — 168 sweep cells (the full 5-bench grid: ugaritic 44 / linearb 44 / cypriot 44 /
    phoenician 24 / luvian 12).
  - `T0_convergence/` — T0 verdict run: `linearb_full_seed0_steps6000.json` (verdict
    **CONVERGENCE_ARTIFACT**, acc 0.3732, 6000 steps), `traj_seed0.jsonl` (6-pt trajectory),
    `HEARTBEAT_T0.json`, `t0.log`.
  - `logs/vast_run.log` — full rental scheduler log.
- `REMOTE_MANIFEST.sha256` — sha256 of every one of the 173 files, computed ON the instance.
- `logos_sweep.tgz`, `ports.log` — instance provenance (the Jul-11 code bundle + port note).

## Verification (triple-checked)
- **Check 0** — pulled tarball sha256 == remote sha256 (`b71fa4e9…`). PASS.
- **Check 1** — `sha256sum -c REMOTE_MANIFEST.sha256` → **173/173 OK, 0 failures.** Every file
  byte-identical to the instance. PASS.
- **Check 2** — backup cells vs the already-merged local corpus (`runtime/csa_sweep/cells/`):
  167/168 byte-identical; **1 cell differs** (see note). 0 missing.
- **Check 3** — T0 verdict parses (CONVERGENCE_ARTIFACT); all 168 cells parse as valid JSON.

## Known note — one dual-computed cell (NOT data loss)
`cypriot-greek__sz600__seed0.json` was computed independently twice during the multi-config period:
- **rental** (`host vast44534071`): acc **0.0817** (49 found), energy 226.73 — this backup.
- **local hardened2** (`host nllei01claude01-hardened2`): acc **0.3183** (191 found), energy 216.98 —
  the copy currently in the merged corpus / used by the published chart.
Both are legitimate CSA restarts (stochastic; the local one reached lower energy → better solution).
Both are preserved. **Curve-rebuild decision (deferred):** for all-rental consistency use the rental
value 0.0817; or keep the lower-energy local 0.3183 as best-of-2. Affects one point on the cypriot
curve only; does NOT affect the T0 verdict or any headline conclusion.
