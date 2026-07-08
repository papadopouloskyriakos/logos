#!/usr/bin/env python3
"""llm_backend.py — provider-agnostic LLM dispatch for the comparison-layer proposer.

One import surface for callers (ablation, l_not_indexed). The concrete backend is chosen at RUNTIME
by the ``LOGOS_LLM_BACKEND`` environment variable — the whole point of invariant #11 as amended
(v2.3, governance/AMENDMENT-004): the tests must be reproducible with ANY LLM, so the proposer is
swappable and nothing about which model proposes may move a mechanically-computed verdict.

  LOGOS_LLM_BACKEND = "ollama"  (default) -> scripts.comparison.ollama_client   (local gpu host)
  LOGOS_LLM_BACKEND = "litellm"           -> scripts.comparison.litellm_client  (LiteLLM proxy;
                                             routes to z.ai/GLM, Mistral, local Ollama, ... uniformly)

Aliases accepted for the proxy backend: "litellm", "proxy", "zai", "z.ai". Default preserves the prior
local-only behaviour, so existing runs are unchanged until the env explicitly opts in.

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
    """Return the selected backend name ('ollama' | 'litellm'), from $LOGOS_LLM_BACKEND."""
    return "litellm" if os.environ.get("LOGOS_LLM_BACKEND", "ollama").strip().lower() in _PROXY_ALIASES else "ollama"


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
