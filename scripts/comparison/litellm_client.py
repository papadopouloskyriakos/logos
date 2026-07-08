#!/usr/bin/env python3
"""litellm_client.py — provider-agnostic LLM client via the LiteLLM proxy (nllei01litellm01).

Sibling of ``ollama_client`` (comparison-layer §C.4). Same fail-closed ``generate(...) -> dict``
contract and the same {response, prompt_tokens, eval_tokens, eval_seconds, ok} return shape, so the
two are drop-in interchangeable behind ``llm_backend``. This one speaks the OpenAI-compatible
``/v1/chat/completions`` surface the LiteLLM proxy exposes; the proxy translates to whatever backend a
model is bound to (z.ai/GLM via the Anthropic endpoint, local Ollama, Mistral, ...), so logos stays
LLM-agnostic — ANY model the proxy serves is reachable through one uniform call.

DOCTRINE (CLAUDE.md, as amended):
  - PROPOSER SIGNAL ONLY. Like ``ollama_client``, this feeds the LLM-ablation proposer (confidence
    <= 0.75, invariant #5) and is NEVER on the verdict path (invariant #2). Nothing here imports or
    calls scripts/verdict.py.
  - PROVIDER-AGNOSTIC BACKEND (invariant #11, amended v2.2 -> v2.3, governance/AMENDMENT-004): logos
    obtains inference through a configured proxy, not a hard-wired vendor. The proxy holds the vendor
    keys; logos holds only a scoped LiteLLM *virtual* key, supplied via the environment
    (LITELLM_API_KEY) or an untracked secret file (runtime/secrets/litellm.env, gitignored). This
    module NEVER hardcodes a key and NEVER sets the Anthropic API-key environment variable.
  - The tests being reproducible with ANY LLM is the point: the mechanical gate (verdict.py) decides,
    the proposer is swappable. Swapping the proposer model must not move a verdict.
  - Token counts/timings are read FROM the proxy response (invariant #12: generated, not guessed).

API (mirrors ollama_client):
  - generate(model, prompt, *, options=None, timeout=180, base_url=None, api_key=None) -> dict
        {response, prompt_tokens, eval_tokens, eval_seconds, ok}. A dead/unauth proxy DEGRADES
        (ok=False, response='') — it never raises, so one bad call cannot crash a batch.
  - extract_json / prompt_sha / log_call are re-exported from ollama_client (backend-agnostic).

Pure stdlib. Deterministic except the live network call + its runtime clock.

    python3 -m pytest tests/test_litellm_client.py -q
"""
from __future__ import annotations

import json
import os
import time
import urllib.request
from typing import Any, Dict, Optional

# Backend-agnostic helpers live in ollama_client; re-export so callers have one surface.
from scripts.comparison.ollama_client import extract_json, log_call, prompt_sha  # noqa: F401

CITATION_DESIGN = (
    "logos comparison-layer §C.4 provider-agnostic proposer backend via the LiteLLM proxy "
    "(nllei01litellm01); invariant #11 amended v2.3 (governance/AMENDMENT-004). Proposer signal, "
    "confidence <= 0.75, NEVER on the verdict path."
)

# Defaults are the internal proxy; both are overridable by env / the untracked secret file.
DEFAULT_BASE_URL = "http://nllei01litellm01:4000"
_SECRET_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir, "runtime", "secrets", "litellm.env"
)


def _load_secret_file(path: Optional[str] = None) -> Dict[str, str]:
    """Parse a KEY=VALUE untracked secret file (runtime/secrets/litellm.env). Missing file -> {}.

    ``path`` defaults to the module-level ``_SECRET_FILE`` read AT CALL TIME (not bound as a default
    argument), so tests/callers can redirect it by patching the module attribute.
    """
    out: Dict[str, str] = {}
    try:
        with open(path or _SECRET_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                out[k.strip()] = v.strip().strip('"').strip("'")
    except OSError:
        pass
    return out


def _cfg(base_url: Optional[str], api_key: Optional[str]) -> Dict[str, str]:
    """Resolve base_url / api_key / model, precedence: explicit arg > env > secret file > default."""
    sf = _load_secret_file()
    base = base_url or os.environ.get("LITELLM_BASE_URL") or sf.get("LITELLM_BASE_URL") or DEFAULT_BASE_URL
    key = api_key or os.environ.get("LITELLM_API_KEY") or sf.get("LITELLM_API_KEY") or ""
    model_override = os.environ.get("LOGOS_LLM_MODEL") or sf.get("LOGOS_LLM_MODEL") or ""
    return {"base": base.rstrip("/"), "key": key, "model_override": model_override}


def _map_options(options: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Translate the Ollama-style options dict to OpenAI chat params (best-effort, drop unknowns)."""
    o = options or {"temperature": 0}
    params: Dict[str, Any] = {}
    if "temperature" in o:
        params["temperature"] = o["temperature"]
    if "seed" in o:
        params["seed"] = int(o["seed"])
    # Ollama num_predict == OpenAI max_tokens (either name accepted from callers).
    if "num_predict" in o and o["num_predict"] not in (None, -1):
        params["max_tokens"] = int(o["num_predict"])
    elif "max_tokens" in o:
        params["max_tokens"] = int(o["max_tokens"])
    if "top_p" in o:
        params["top_p"] = o["top_p"]
    return params


def generate(
    model: str,
    prompt: str,
    *,
    options: Optional[Dict[str, Any]] = None,
    timeout: int = 180,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """POST to {base}/v1/chat/completions (OpenAI format). Returns a dict; NEVER raises.

    ``LOGOS_LLM_MODEL`` (env or secret file) overrides ``model`` when set, so a caller that asks for a
    local model name still routes to the configured proxy model (e.g. glm-4.6) — that is how "all of
    logos's LLM requirements via the proxy" is expressed without touching caller code.
    """
    cfg = _cfg(base_url, api_key)
    eff_model = cfg["model_override"] or model
    t0 = time.time()
    out: Dict[str, Any] = {
        "response": "",
        "prompt_tokens": 0,
        "eval_tokens": 0,
        "eval_seconds": 0.0,
        "ok": False,
    }
    body = json.dumps(
        {
            "model": eff_model,
            "messages": [{"role": "user", "content": prompt}],
            **_map_options(options),
        }
    ).encode()
    headers = {"Content-Type": "application/json"}
    if cfg["key"]:
        headers["Authorization"] = f"Bearer {cfg['key']}"
    try:
        req = urllib.request.Request(f"{cfg['base']}/v1/chat/completions", data=body, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            d = json.loads(r.read().decode())
        choices = d.get("choices") or []
        if choices:
            out["response"] = (choices[0].get("message") or {}).get("content", "") or ""
        usage = d.get("usage") or {}
        out["prompt_tokens"] = int(usage.get("prompt_tokens", 0) or 0)
        out["eval_tokens"] = int(usage.get("completion_tokens", 0) or 0)
        out["eval_seconds"] = time.time() - t0  # OpenAI surface has no eval_duration; use latency.
        # ok iff the proxy returned a real completion (an {"error":...} body degrades to ok=False).
        out["ok"] = bool(choices) and "error" not in d
    except Exception:
        # A dead/unauth proxy must DEGRADE, not crash the batch (signals fail closed).
        out["eval_seconds"] = time.time() - t0
        out["ok"] = False
    return out
