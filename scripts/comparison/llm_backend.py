#!/usr/bin/env python3
"""llm_backend.py — provider-agnostic LLM dispatch for the comparison-layer proposer.

One import surface for callers (ablation, l_not_indexed). The concrete backend is chosen at RUNTIME
by the ``LOGOS_LLM_BACKEND`` environment variable — the whole point of invariant #11 as amended
(v2.3, governance/AMENDMENT-004): the tests must be reproducible with ANY LLM, so the proposer is
swappable and nothing about which model proposes may move a mechanically-computed verdict.

  LOGOS_LLM_BACKEND = "litellm" (DEFAULT) -> scripts.comparison.litellm_client  (LiteLLM proxy;
                                             routes to z.ai/GLM, Mistral, local Ollama, ... uniformly)
  LOGOS_LLM_BACKEND = "ollama"            -> scripts.comparison.ollama_client   (local gpu host)

Aliases accepted for the proxy backend: "litellm", "proxy", "zai", "z.ai". The DEFAULT is the proxy
(z.ai per the owner directive 2026-07-08 / AMENDMENT-004): all of logos's programmatic LLM goes through
z.ai unless a run explicitly sets LOGOS_LLM_BACKEND=ollama to fall back to the local gpu host.

``generate`` dispatches; ``extract_json`` / ``log_call`` / ``prompt_sha`` are backend-agnostic and are
re-exported from ollama_client unchanged. NEVER on the verdict path (invariant #2).
"""
from __future__ import annotations

import os
from typing import Any, Dict, Optional

from scripts.comparison import litellm_client, ollama_client

# Backend-agnostic helpers — identical regardless of proposer provider.
extract_json = ollama_client.extract_json
log_call = ollama_client.log_call
prompt_sha = ollama_client.prompt_sha

_PROXY_ALIASES = {"litellm", "proxy", "zai", "z.ai"}


def active_backend() -> str:
    """Return the selected backend name ('litellm' | 'ollama'), from $LOGOS_LLM_BACKEND.

    Default is 'litellm' (the z.ai proxy) — all logos LLM goes through z.ai unless the env explicitly
    selects 'ollama'. Any unrecognised value also falls back to the local 'ollama' backend.
    """
    return "litellm" if os.environ.get("LOGOS_LLM_BACKEND", "litellm").strip().lower() in _PROXY_ALIASES else "ollama"


def generate(
    model: str,
    prompt: str,
    *,
    options: Optional[Dict[str, Any]] = None,
    timeout: int = 180,
    host: Optional[str] = None,
) -> Dict[str, Any]:
    """Dispatch to the configured proposer backend. Same fail-closed contract as either client.

    ``host`` keeps the Ollama meaning for the local backend. For the proxy backend it is ignored
    (the proxy base_url comes from $LITELLM_BASE_URL / the untracked secret file), so a stray
    --host Ollama URL never mis-targets the proxy.
    """
    if active_backend() == "litellm":
        return litellm_client.generate(model, prompt, options=options, timeout=timeout)
    return ollama_client.generate(model, prompt, options=options, timeout=timeout, host=host)
