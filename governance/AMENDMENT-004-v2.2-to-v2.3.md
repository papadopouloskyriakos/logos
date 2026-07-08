# AMENDMENT-004 — Constitution v2.2 → v2.3 (LLM-provider agnosticism via a proxy)

Recorded under **Article XXIII**. Non-silent, **non-retroactive**. Approved by the repository owner
by explicit directive ("wire logos to use the z.ai API key via `nllei01litellm01` for ALL of its LLM
requirements … the tests MUST be reproducible with ANY LLM used; they should be LLM agnostic",
2026-07-08).

| field | value |
|---|---|
| **date** | 2026-07-08 |
| **approver** | Repository owner (direct directive) |
| **old text** | `governance/CONSTITUTION.md` Article XXI @ v2.2 (git history before this commit) |
| **new text** | `governance/CONSTITUTION.md` Article XXI @ v2.3 |
| **retroactivity** | NON-RETROACTIVE — no completed result is re-graded; it changes an operational default, not an epistemic rule |
| **companion CLAUDE.md** | invariant #11 restated to match |

## Rationale (the owner's argument, adopted)

The prior wording ("LLM via the Claude Code subscription only; never set `ANTHROPIC_API_KEY`") was
justified in part by "reproducibility." That justification conflated two things:

- **Scientific reproducibility** — a verdict must not depend on *which* model proposed the hypothesis.
  This is already guaranteed by the machine, not by pinning a vendor: **Art. VI / invariants #2, #4,
  #5** — the LLM is a *proposer signal* (confidence ≤ 0.75) and is **never on the verdict path**;
  `scripts/verdict.py` computes outcomes mechanically from held-out data. A genuine reading survives
  being proposed by any competent model; one that survives only under a specific model is the fitted
  artifact the whole apparatus exists to reject. **LLM-agnosticism is therefore the correct, stronger
  reading of the constitution's own discipline** — not a relaxation of it.
- **Bitwise run-replay** — replaying one campaign's exact artifacts. LLMs are not bitwise
  deterministic regardless of vendor; run-provenance is handled by seeds + `plan_hash` + content-hash
  dedup + the append-only ledger (**Art. XVII**), never by trusting a fixed model.

Article XXI **already** states tooling constraints are *operational, not epistemic*, grant *no
epistemic privilege to a particular model or vendor*, and that *"a model change requires a recorded
compatibility and reproducibility note."* This amendment is exactly that recorded note plus the
matching update to the operational default.

## Change (Article XXI — Current defaults)

| id | article | old default | new default |
|---|---|---|---|
| **T1** | XXI | `LLM access: Claude Code subscription through claude -p`; `Prohibited: ANTHROPIC_API_KEY`; `Local models: Ollama on the approved GPU host` | LLM access is **provider-agnostic through the approved LiteLLM proxy** (`nllei01litellm01:4000`), selected at runtime by `$LOGOS_LLM_BACKEND` which **defaults to `litellm` (z.ai/GLM)** per the owner directive "z.ai is default for logos … everything must be using z.ai" — `ollama` is the explicit local fallback. The proxy holds all vendor keys; logos holds only a **scoped LiteLLM virtual key**, supplied via env / an untracked secret file (`runtime/secrets/litellm.env`, gitignored) — **never committed, never a raw vendor key in the repo, and `ANTHROPIC_API_KEY` still never set in-process.** Backends wired through the proxy: z.ai/GLM (**default model `glm-5.2`**; full series `glm-4.5`…`glm-4.7`,`glm-5`…`glm-5.2` via the Anthropic-compatible endpoint), local Ollama, Mistral/Codestral/Devstral. Note: because z.ai/GLM is now the default proposer, a re-run of the LLM-ablation (§C.4) proposes with GLM unless `LOGOS_LLM_BACKEND=ollama` is set — a deliberate owner choice, recorded here (the proposer remains a ≤0.75 signal, never on the verdict path, so no verdict moves). |

## Worker architecture (owner directive 2026-07-08)

Division of labour, recorded so it is not re-litigated: the **Claude Code session remains the
coordinator / scientific-overview / discipline-enforcement layer**; **token-intensive, repetitive
worker labour** (brute-force search, epoch execution, fan-out) is **handed to z.ai/GLM via
`scripts/zai_agent.py`** — a self-contained tool-use loop that calls GLM through the proxy with NO
claude-code / anthropic dependency. Workers PROPOSE and EXECUTE; the mechanical gates
(`scripts/verdict.py`, controls, nulls) remain the sole adjudicator (invariants #2/#4/#5), so moving
the worker LLM to GLM changes cost/vendor, never a verdict.

## Compatibility & reproducibility note (required by Article XXI)

- **Proposer only.** The proxy backend is reached solely by the LLM-ablation proposer
  (`scripts/comparison/llm_backend.py` → `litellm_client.py`). It imports nothing from
  `scripts/verdict.py`; no verdict, gate, or licence depends on it (invariants #2/#4).
- **Swappability verified.** `generate()` has an identical fail-closed contract and return shape to
  the local `ollama_client`; `tests/test_litellm_client.py` (network-mocked) and
  `tests/test_ollama_client.py` both pass. A live end-to-end call
  (`llm_backend.generate` → proxy → z.ai `glm-4.6`) returns a real completion with real token counts.
- **Secret hygiene.** The vendor key lives only in `/srv/litellm/.env` on the proxy host; logos's
  scoped virtual key lives only in the gitignored `runtime/secrets/litellm.env`. Neither is committed.
- **Reproducibility scope.** Because the proposer is a capped signal, changing the proposer model
  changes *which hypotheses are explored and the search-receipt / effective-n bookkeeping*, **not**
  any mechanically-computed verdict class. That is the intended, and now explicit, meaning of
  "reproducible with any LLM."

## Scientific consequence

None. No experiment is re-graded. The amendment records an operational default change and makes
explicit an LLM-agnosticism that Art. VI and invariants #2/#4/#5 already required. The v2.2 text
remains in git history as the immutable prior record (Art. XVII).
