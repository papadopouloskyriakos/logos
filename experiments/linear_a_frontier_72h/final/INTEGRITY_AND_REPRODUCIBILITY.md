# Integrity and Reproducibility (§12.10 / §15)

## Repository state
- **Branch:** `research/linear-a-frontier-72h` · **worktree:** `logos-linear-a-frontier-72h`.
- **Commit range:** `c1f089e` (72h scaffold) … **final commit recorded in `CAMPAIGN_FINAL_STATE.json` and the
  `CAMPAIGN_COMPLETE` marker** (stamped by the closing commit). 122+ commits on-branch.
- **Append-only history confirmed:** the ledger (`EPOCH_LEDGER.yaml`) is append-only; corrections are recorded as
  ERRATUM/SUPERSEDING/QUALIFICATION entries (E002–E014 carry duplicate terminal records = history), never silent
  edits. The E022 "sole survivor" narrowing is an append-only QUALIFICATION (E103), not a deletion.

## Protected assets — untouched (verified)
- **Paper:** `git status paper/` = clean. The submitted, byte-frozen TACL/Zenodo manuscript is **not modified**.
- **Governance / corpus / runtime:** `git status governance/ corpus/ runtime/` = clean. Constitution, transfer-
  licence state (`transfer_licences.json`, all NOT_EARNED), and licensed raw data are unchanged.
- **Secrets:** no vendor key committed. The only `ANTHROPIC_API_KEY` occurrence in tracked files is the disclosure
  phrase *"NO ANTHROPIC_API_KEY in-process"* in the ledger — a statement of absence, not a value. The z.ai key was
  **not** rotated and lives only in gitignored `runtime/secrets/litellm.env` + the proxy.

## Reproducibility
- **Deterministic epochs:** E103 (fixed seeds) re-runs **byte-identical on scientific content** (verdict + per-scheme
  numbers + PC), verified this session. E104 is seeded (nulls seeded 1000+i, plants 5000+i) → reproducible; wall-time
  ~3.5 min for 200 nulls + 40 plants.
- **Generated counts:** every campaign count comes from `final/generate_closure.py` parsing `EPOCH_LEDGER.yaml`
  (invariant #12). Re-running the generator reproduces all `final/*.json` + CSVs.
- **Machinery frozen per epoch:** each epoch dir carries `machinery.py` + `plan_hash.txt` (sha256 of the frozen
  prereg) + `result.json` (with `plan_hash` + `code_manifest`).

## Test status
- Epoch self-checks pass (E103 machinery `__main__` self-test; E104 imports and runs E103's frozen kernel).
- Closure generator runs clean and emits all 7 JSON + 2 CSV artifacts; `ARTIFACT_MANIFEST.json` hashes them.
- No project-wide pytest suite is part of this campaign; verification is per-epoch mechanical (controls + nulls +
  orchestrator re-verification recorded in each ledger entry) plus the coordinator re-verification in
  `VERIFICATION_AUDIT.md`.

## Known reproducibility limitations
- Bucket classification for the 65 pre-field-schema epochs (no `dichotomy_side`) is heuristic (labelled
  `bucket_source=heuristic` per row in the master CSV); the curated narrative tally in `EXHAUSTION_MAP_DRAFT.md`
  remains the human-audited classification. The per-epoch **verdicts** are verbatim from the ledger and are exact.
- Licensed source material (DĀMOS / GORILA / SigLA JSON) is gitignored and excluded from the review bundle — it
  cannot be redistributed. Silver-corpus derivatives used by the epochs are committed where licence permits.

## Compute / source blockers (recorded)
- `SOURCE_BLOCKED`: GORILA-plate stroke contours (F2), Ariadne-2025 Anetaki full edition (F1/F8).
- No compute blocker at close (H100 not required; all closure epochs ran on local CPU in minutes).
