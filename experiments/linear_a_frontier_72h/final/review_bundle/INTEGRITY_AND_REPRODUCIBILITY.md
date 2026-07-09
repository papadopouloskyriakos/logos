# Integrity and Reproducibility (§12.10 / §15)

Reflects the terminal audit remediation pass (2026-07-09): E103R + E104R reruns under frozen append-only prereg
addenda, corrected closure generator, regenerated closure layer, rebuilt review bundle.

## Repository state
- **Branch:** `research/linear-a-frontier-72h` · **worktree:** `logos-linear-a-frontier-72h`.
- **Commit range:** `c1f089e` (72h scaffold) … the closing commit recorded in the `final_commit` field of
  `CAMPAIGN_FINAL_STATE.json` (stamped by the closure regeneration; the `CAMPAIGN_COMPLETE` marker carries the
  pre-remediation closure commit).
- **Append-only history confirmed:** the ledger (`EPOCH_LEDGER.yaml`) is append-only; corrections are recorded as
  ERRATUM/SUPERSEDING/QUALIFICATION entries (E002–E014 carry duplicate terminal records = history; the terminal
  audit added SUPERSEDING records for E103 (E103R) and E104 (E104R)), never silent edits. The E022 "sole survivor"
  narrowing is an append-only QUALIFICATION (E103, re-stated exactly under E103R), not a deletion. Frozen preregs
  and original result.json files are untouched; reruns live in `prereg_addendum_R.md` / `result_R.json` alongside.

## Protected assets — untouched (verified)
- **Paper:** `git status paper/` = clean (re-verified at the remediation pass). The submitted, byte-frozen
  TACL/Zenodo manuscript is **not modified**.
- **Governance / corpus / runtime:** `git status governance/ corpus/ runtime/` = clean. Constitution, transfer-
  licence state (`transfer_licences.json`, all NOT_EARNED), and licensed raw data are unchanged.
- **Secrets:** no vendor key committed. The only `ANTHROPIC_API_KEY` occurrence in tracked files is the disclosure
  phrase *"NO ANTHROPIC_API_KEY in-process"* in the ledger — a statement of absence, not a value. The z.ai key was
  **not** rotated and lives only in gitignored `runtime/secrets/litellm.env` + the proxy.

## Reproducibility
- **Deterministic epochs:** E103R (fixed seeds) re-runs byte-identical on scientific content (verdict + per-variant
  numbers + PC). Its corrected joint null was additionally verified by an independent reconstruction (distinct
  algorithm — `Generator.choice` — different seed, M=20,000): identical survivor sets in all three variants,
  marginal means matching theory. E104R is seeded (nulls 1000+i for i<400, plants 5000+i) → reproducible;
  wall-time ~9 min for 400 nulls + 40 plants.
- **Generated counts:** every campaign count comes from `final/generate_closure.py` (remediation revision; the
  generator that ran at original closure is frozen at `epochs/EPOCH-105/machinery.py`) parsing `EPOCH_LEDGER.yaml`
  (invariant #12). Re-running the generator reproduces all `final/*.json` + CSVs; `epochs/EPOCH-105/result.json`
  records the generator's code manifest and the sha256 of every emitted closure artifact.
- **Machinery frozen per epoch:** each epoch dir carries `machinery.py` + `plan_hash.txt` (sha256 of the frozen
  prereg) + `result.json` (with `plan_hash` + `code_manifest`); remediated epochs additionally carry
  `machinery_R.py` + `plan_hash_R.txt` (sha256 of the frozen addendum) + `result_R.json`.

## Test status
- Epoch self-checks pass (E103R machinery `__main__` self-test; E104R imports and runs the E103R kernel).
- Closure generator runs clean and emits all JSON + CSV artifacts + `epochs/EPOCH-105/result.json`;
  `ARTIFACT_MANIFEST.json` hashes every emitted closure file and **excludes itself** from its own file list.
  The bundle ships a `BUNDLE_MANIFEST.sha256` (sha256sum format, bundle-relative paths, self-excluded) so
  `sha256sum -c BUNDLE_MANIFEST.sha256` verifies the whole bundle mechanically.
- No project-wide pytest suite is part of this campaign; verification is per-epoch mechanical (controls + nulls +
  orchestrator re-verification recorded in each ledger entry) plus the coordinator re-verification in
  `VERIFICATION_AUDIT.md`.

## Known reproducibility limitations
- Bucket classification for the pre-field-schema epochs (no `dichotomy_side`) is a documented headline-keyword
  heuristic (labelled `bucket_source=headline` per row in the master CSV; the rule is stated in
  `generate_closure.py`). Headlines with no status keyword bucket as OTHER. The per-epoch **verdicts** are
  verbatim and untruncated from the append-only ledger and are exact.
- **plan_hash coverage:** E019, E020, and E022 have no `plan_hash` field in their ledger rows; their hashes are
  read from `epochs/<id>/plan_hash.txt` on disk (recorded per row as `plan_hash_source=file(plan_hash.txt)`). All
  other epochs carry the hash in the ledger itself.
- Licensed source material (DĀMOS / GORILA / SigLA JSON) is gitignored and excluded from the review bundle — it
  cannot be redistributed. Silver-corpus derivatives used by the epochs are committed where licence permits.

## Compute / source blockers (recorded)
- `SOURCE_BLOCKED`: GORILA-plate stroke contours (F2), Ariadne-2025 Anetaki full edition (F1/F8).
- No compute blocker at close (H100 not required; all closure epochs ran on local CPU in minutes).
