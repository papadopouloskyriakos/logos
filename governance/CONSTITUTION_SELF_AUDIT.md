# Constitution v2.0 — adversarial self-audit (adoption gate)

Append-only record (Art. XVII). Produced at adoption by a 4-agent adversarial workflow
(run `wf_4c40bcc4-428`, 2026-07-07): self-consistency, frozen-paper safety, retroactive mapping,
implementation backlog. The audit **cleared v2.0 for ratification** — all 12 owner findings are genuinely
addressed by the cited articles; the defects below are *operational precision*, not intent (the auditor's
own words), consistent with AMENDMENT-001's claim that v1.0's weakness was precision, not intent.

**Two classes, handled differently.** Defects in **my adoption artifacts** are fixed in the ratification
commit. Defects in the **constitution text** may NOT be silently edited (Art. XXIII); they are logged here
as **candidate AMENDMENT-002** items for owner decision. v2.0 is ratified *as delivered*; AMENDMENT-002 is
optional precision-tightening the owner may approve later.

## A. Artifact defects — FIXED in the ratification commit

| # | defect (article) | fix |
|---|---|---|
| A1 | AMENDMENT-001 + README cited `RETROACTIVE_COMPLIANCE.md` and `IMPLEMENTATION_BACKLOG.md` as the mechanisms carrying non-retroactivity + forward-obligation tracking, but neither existed — a **ratification-blocking dangling reference** (auditor: "should block ratification until the files land"). | Both files authored and committed in this same commit; references now resolve. |
| A2 | `assumption_register.json` modeled a single mutable `status`, violating Art. XVII append-only. | Rebuilt to schema v2: `original_status` + `current_status` + append-only `revisions[]`; top-level `append_only: true` + discipline note. |
| A3 | `assumption_register.json` A05 hand-wrote a count ("66 units, 2 of 4 classes"), violating Art. XIX ("counts are generated, never hand-written"). | Count removed from prose; replaced with a `count_source` pointer to the generated `power_gate.json`. `transfer_licences.json` given a `count_provenance` note (records qualitative state only). |

## B. Constitution-text defects — CANDIDATE AMENDMENT-002 (owner decision; NOT silently patched)

### B1 — Controlled-vocabulary gap (contradiction: Art. XVI vs "Required status vocabulary")
Art. XVI lists `DEPENDENCY_COLLAPSE`, `LEAKAGE_DETECTED`, `DOMAIN_SHIFT_FAILURE` as allowed failure states,
but the closed "Required status vocabulary" omits all three — a stage that fails on leakage is required to
record a status the vocabulary forbids. **Proposed fix:** add the three tokens to the status vocabulary.

### B2 — Token collision across two closed vocabularies (Art. VI confidence classes vs status vocabulary)
`EXPLORATORY` and `SUPPORTED` appear in both the Art. VI confidence ladder and the lifecycle status
vocabulary with different intended axes, no mapping. A bare "SUPPORTED" is under-defined. **Proposed fix:**
namespace them (e.g. `confidence:SUPPORTED` vs `status:SUPPORTED`) or rename one axis; state that every
claim carries exactly one token from each of the two axes.

### B3 — "Required … may include" is gameable (Art. XIII stress tests; Art. XV controls)
Both head a *mandatory* article with a *permissive* verb ("may include"), so a claimant can run an empty
subset and still assert compliance (contrast Art. XIV "include", no "may"). **Proposed fix:** make the
enumerated stress tests / controls that are *applicable to the claim's layer* mandatory-unless-justified,
with any omission recorded as a deviation (Art. XXII).

### B4 — Undefined "genuine independence" bar drives effective_n (Art. VIII / Art. XI)
Dependent sources collapse to one lineage "unless genuine independence is demonstrated," but no operational
criterion/adjudicator is given — and effective_n gates graduation, so the undefined bar is directly gameable
to inflate evidence. **Proposed fix:** define an independence test (distinct underlying edition AND distinct
decipherment lineage AND no shared upstream lexicon) in the Art. XI source-dependency graph; default to
DEPENDENT when unproven.

### B5 — No mechanical thresholds between confidence classes (Art. VI)
`SUPPORTED → HELD_OUT_SUPPORTED → REPLICATED → PROVISIONALLY_ACCEPTED → ACCEPTED` has no defined boundary;
Art. XIX hands "deflation" to code but never the class cut-offs. **Proposed fix:** attach each class to a
mechanical predicate (evidence tier from Art. IV's ordered list × effective_n × deflated significance),
computed by deterministic code.

### B6 — No composition rule across the three ladders (Art. V layer × Art. VI confidence × Art. XV licence)
Nothing forbids labeling an L6 claim `HELD_OUT_SUPPORTED` while no `PHONETIC_TRANSFER_LICENSE` is held.
**Proposed fix:** state the invariant *a claim's confidence class is capped by the licence earned for its
claim layer* — the licence gate dominates.

### B7 — "Every claim" panel scope is ill-posed for observational claims (Art. IX)
L0/L1 OBSERVED data have no effect to power, so "minimum detectable effect / estimated power" is undefined;
"every claim" is either unimplementable or loosely evadable. **Proposed fix:** scope the information-budget
panel to *inferential/graduating* claims (L2+ or any claim seeking a confidence class ≥ SUPPORTED).

### B8 — finding #4 remedy only half-cures the 0.75 cap (Art. VI) — the one inadequate remedy
Art. VI removed the "false precision" half (declared 0.75 non-probabilistic) but left the "arbitrary" half:
0.75 is still an underived magic number. **Proposed fix:** either derive the ceiling from the gate's
measured false-graduation calibration (`gate_null_calibration.py`), or restate it as an explicitly
conventional governance constant with no epistemic content (acknowledge, don't dress up).

## C. Structural note (not a defect) — Art. III/VI independence ceiling under Art. XXI
Under a single-vendor tooling constraint (Art. XXI) with no independent human expert, true proposer/verifier
independence is unreachable *in-repo*, so the top confidence classes (`REPLICATED`, `PROVISIONALLY_ACCEPTED`,
`ACCEPTED`) that require `INDEPENDENT_EXPERT_AGREEMENT` **cannot be self-assigned by the repo** — which is
*correct by design*: the Preamble already requires qualified external review for acceptance. Recorded so it
is not mistaken for a bug: these classes are reserved for out-of-repo human adjudication, exactly as intended.

---

**Status:** `RESOLVED` — B1–B8 were enacted in **AMENDMENT-002 (v2.0 → v2.1)**, 2026-07-07, owner-approved.
See [`AMENDMENT-002-v2.0-to-v2.1.md`](./AMENDMENT-002-v2.0-to-v2.1.md). A1/A2/A3 were resolved in the v2.0
ratification commit. This audit record is retained (append-only, Art. XVII) as the provenance of v2.1.

---

## Second round — v2.1 + tooling adversarial review (2026-07-07)

After building the enforcement tooling, a 4-agent adversarial review (workflow `wf_c5c47c7f-d52`, find →
independently verify) raised 19 findings; **16 confirmed** by a second verifier. All fixed in the same
session:

- **Code (fail-open → fail-closed):** `licence_gate.py` accepted mistyped/out-of-range layers and unknown
  confidence strings (a **critical** Art. XV/B6 bypass) → normalize + fail closed, block boundary tracks the
  licence matrix; `info_budget.requires_panel` exempted unknown confidence/layer → fail closed + added
  `source_dependency_structure`/`search_space_size` to load-bearing + a power floor; `search_receipt`
  empty-config collapsed multiplicity → reject empty config, count full trial identity; `assumption_gate`
  only blocked FALSE/STALE → **VERIFIED is now the sole non-blocking state** (UNKNOWN/PARTIAL block);
  `stage_header` never validated the close block → added `validate_close`.
- **`effective_n` correctness:** the headline was `min` of per-dimension marginals, which **overstates**
  independence vs the joint dependency → headline is now the **joint union-find components** (conservative,
  guilty-until-proven); marginals reported as upper bounds.
- **`source_dependency` faithfulness (B4):** collapsed on the hand-authored `lineage` label, ignoring the
  atomic fields → now computes independence **mechanically** from `derives_from` / shared edition / lexicon /
  tradition, honoring `independence_demonstrated` (GORILA+Salgarella now correctly = 1 vote).
- **Constitution (B5/B6):** the B5 tier comparator was inverted (let in-sample tier-6 qualify as held-out)
  and B6's layer→licence map was partial (froze L0/L1/L7 at SUPPORTED) → **AMENDMENT-003 (v2.2)**.

3 findings were not confirmed by the verifier and dropped. All new behaviour is locked by regression tests.
