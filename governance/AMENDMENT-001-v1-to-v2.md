# AMENDMENT-001 — Constitution v1.0 → v2.0

Recorded under **Article XXIII** (Amendments are explicit and versioned). This amendment is **non-silent
and non-retroactive**: it does not, and may not, convert any prior failed or null result into a success
(Article XXIII final clause; Article XVII).

| field | value |
|---|---|
| **date** | 2026-07-07 |
| **approver** | Repository owner (delivered Constitution v2.0 for adoption) |
| **old text** | `CLAUDE.md` — "Mission" + "Invariants — do not break these" (the 12 numbered invariants), as committed at `f6a5682` |
| **new text** | [`governance/CONSTITUTION-v2.0.md`](./CONSTITUTION-v2.0.md) (Preamble + Articles I–XXIII + claim/licence matrix + status vocabulary + conventions + one-line rule) |
| **retroactivity** | **NON-RETROACTIVE.** All prior verdicts stand unchanged. The existing record is *re-expressed* in the v2.0 status vocabulary and claim-layer scheme in [`RETROACTIVE_COMPLIANCE.md`](./RETROACTIVE_COMPLIANCE.md); it is not re-graded. The honest forward clock (Art. XVII) begins at this commit. |
| **commit** | the commit that adds this file (append-only) |

## Reason — the owner's audit of v1.0

v1.0 was strong (prediction-before-verdict, held-out eval, mechanical verdicts, multiple-testing
correction, corpus versioning, deterministic dedup, information limits, proposal/decision separation,
open tooling, generated counts). Its weaknesses were **operational precision**, not intent. The owner's
audit raised 12 findings; v2.0 addresses each:

| # | v1.0 gap | v2.0 remedy |
|---|---|---|
| 1 | "Acceptance" underspecified — collapses distinct levels into one "cracked" state | **Article V** claim layers L0–L9 + **Article XV** transfer-licence hierarchy; no wording above the earned layer |
| 2 | "Never write defeatist framing" too broad — could suppress warranted negatives | **Preamble**: bounded negatives (underpowered / falsified / not-identifiable) are authorized; only *unsupported global* "uncrackable" claims are forbidden |
| 3 | Model/verifier separation incomplete — a mechanical verifier can still share proposer assumptions/leakage | **Article III** independence audit (proposer_id/verifier_id/shared_*); mechanical ≠ independent |
| 4 | Fixed `≤0.75` cap is arbitrary / false precision | **Article VI** retains it as a governance ceiling, explicitly *not* a calibrated probability; ties confidence to layers + evidence classes |
| 5 | Unicity distance may be misapplied | **Article IX** full information-budget panel; unicity distance is a component/analogy only |
| 6 | Multiplicity correction too simplistic (`n_h × n_signs × n_roots`) | **Article VII** complete search receipt; reproduce the whole adaptive process under the null |
| 7 | Effective sample size missing | **Article VIII** `raw_n` **and** `effective_n`; graduation on independent evidence |
| 8 | Source dependency not governed | **Article XI** source dependency graph; dependent sources = one lineage |
| 9 | No immutable correction protocol | **Article XVII** append-only record; ERRATUM / SUPERSEDING / INVALIDATION, never silent deletion |
| 10 | No assumption register | **Article XVIII** every load-bearing premise stated, verified, pinned, with expiry |
| 11 | Structural/functional/semantic/lexical/phonetic claims need separate gates | **Article XV** transfer licences; a lower licence never implies a higher one |
| 12 | Constitution did not govern itself | **Article XXII** every stage cites articles; **Article XXIII** versioned amendments |

## Scientific consequence

- **No result is upgraded.** The three completed negatives — Egyptian/Cretan one-shot (TRIVIAL_RECOVERY),
  admin-schema automated pilot (NO_POWER), no-human source-label route (NO_POWER_BEFORE_MODELING → in
  v2.0 vocabulary, `NO_POWER`) — remain negatives. Observable-channels Experiment 1 (masked logogram)
  remains a bounded negative for the commodity channel.
- **New obligations attach going forward** (Article XVIII/VII/VIII/IX): stages must now emit a search
  receipt, an information-budget panel, `raw_n`+`effective_n`, and cite triggered articles. Tracked in
  [`IMPLEMENTATION_BACKLOG.md`](./IMPLEMENTATION_BACKLOG.md).
- **The submitted paper is byte-frozen** and was reviewed for v2.0 compliance at adoption; any residual
  gap is handled by ERRATUM (Article XVII), never by a silent rebuild. See `RETROACTIVE_COMPLIANCE.md`.

## Affected experiments

All active/closed programmes now operate under v2.0: `egyptian_calibration`, `admin_schema`,
`no_human_structure`, `observable_channels`, plus the frozen paper. Re-expression (not re-grading) is in
`RETROACTIVE_COMPLIANCE.md`.

## Adoption gate — adversarial self-audit

Before ratification a 4-agent adversarial audit (`wf_4c40bcc4-428`) checked v2.0 for self-consistency,
frozen-paper safety, retroactive-record fit, and implementation obligations. Result: **cleared** — all 12
findings genuinely addressed; the **frozen paper is COMPLIANT** at its earned layer **L2** and needs no
change (Art. XVII). Artifact defects it caught (dangling file refs; a mutable assumption register vs Art. XVII;
a hand-written count vs Art. XIX) are **fixed in this commit**. Residual precision defects in the v2.0 *text*
are logged as candidate **AMENDMENT-002** (owner decision) in [`CONSTITUTION_SELF_AUDIT.md`](./CONSTITUTION_SELF_AUDIT.md);
none blocks adoption.
