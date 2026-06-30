#!/usr/bin/env python3
"""ollama_client.py — minimal local-Ollama client for the LLM-ablation proposer (comparison-layer §C.4).

PORTED (project rule: port, don't rewrite) from ../finops-agora/scripts/agora_lib.py::llm_call — the
proven urllib POST to {OLLAMA_URL}/api/generate (stream=False, returns 'response' + token counts). The
agora DB observability is replaced by a JSONL append (no DB dependency in logos's comparison layer).

DOCTRINE (CLAUDE.md):
  - This client feeds the LLM-ABLATION PROPOSER ONLY. The proposer is a SIGNAL source
    (confidence ≤ 0.75, invariant #5) and is NEVER on the verdict path (invariant #2). Nothing here
    imports or calls scripts/verdict.py; the ablation MEASURES proposer behaviour, it never decides.
  - LOCAL/SUBSCRIPTION ONLY (invariant #11): Ollama on the gpu host. This module NEVER touches a
    proprietary-cloud API key and NEVER imports a proprietary-cloud SDK — local urllib only.
  - Token counts and timings are READ FROM the Ollama response (invariant #12: generated, not guessed)
    so callers can report real throughput.

API:
  - generate(model, prompt, *, options=None, timeout=180, host=None) -> dict
        {response, prompt_tokens, eval_tokens, eval_seconds, ok}. A dead host degrades (ok=False,
        response='') — it never raises, so one bad call cannot crash a batch.
  - extract_json(text) -> object | None
        Robust first-JSON-object extraction (fenced ```json, fenced ```, raw-with-prose). None on
        garbage; never raises. (gemma3 emits fenced JSON — verified.)
  - log_call(...) appends a privacy-preserving JSONL line (prompt_sha, never the prompt text) to
    runtime/ablation/llm_calls.jsonl.

Pure stdlib. Deterministic except the live network call + its runtime clock (eval_seconds fallback).

    python3 -m pytest tests/test_ollama_client.py -q
"""
from __future__ import annotations

import hashlib
import json
import os
import urllib.request
from typing import Any, Dict, Optional

CITATION_DESIGN = (
    "logos comparison-layer §C.4 (LLM-ablation delta — the LLM is a proposer signal, confidence "
    "≤ 0.75, NEVER on the verdict path) ported from finops-agora agora_lib.llm_call."
)

DEFAULT_HOST = "http://nllei01gpu01:11434"

# JSONL observability log — relative to the repo root (this file is scripts/comparison/ollama_client.py).
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
LOG_PATH = os.path.join(_REPO_ROOT, "runtime", "ablation", "llm_calls.jsonl")


# --------------------------------------------------------------------------- #
# Ollama generate (ported from agora_lib.llm_call, DB logging stripped)
# --------------------------------------------------------------------------- #
def generate(
    model: str,
    prompt: str,
    *,
    options: Optional[Dict[str, Any]] = None,
    timeout: int = 180,
    host: Optional[str] = None,
) -> Dict[str, Any]:
    """POST to {host}/api/generate (stream=False). Returns a dict; NEVER raises.

    options defaults to {'temperature': 0} for reproducibility — the caller overrides for sampling.
    host defaults to $OLLAMA_URL or the gpu host. eval_seconds is read from the response's
    eval_duration (nanoseconds) when present, else falls back to wall-clock latency.
    """
    import time

    url = (host or os.environ.get("OLLAMA_URL") or DEFAULT_HOST).rstrip("/")
    body = json.dumps(
        {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": options if options is not None else {"temperature": 0},
        }
    ).encode()

    t0 = time.time()
    out: Dict[str, Any] = {
        "response": "",
        "prompt_tokens": 0,
        "eval_tokens": 0,
        "eval_seconds": 0.0,
        "ok": False,
    }
    try:
        req = urllib.request.Request(
            f"{url}/api/generate", data=body, headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            d = json.loads(r.read().decode())
        out["response"] = d.get("response", "") or ""
        out["prompt_tokens"] = int(d.get("prompt_eval_count", 0) or 0)
        out["eval_tokens"] = int(d.get("eval_count", 0) or 0)
        # eval_duration is nanoseconds in the Ollama API; fall back to wall-clock latency.
        eval_ns = d.get("eval_duration")
        if eval_ns:
            out["eval_seconds"] = float(eval_ns) / 1e9
        else:
            out["eval_seconds"] = time.time() - t0
        out["ok"] = True
    except Exception:
        # A dead host must DEGRADE, not crash the batch (invariant: signals fail closed).
        out["eval_seconds"] = time.time() - t0
        out["ok"] = False
    return out


# --------------------------------------------------------------------------- #
# Robust JSON extraction from an LLM reply
# --------------------------------------------------------------------------- #
def extract_json(text: Any) -> Optional[Any]:
    """Extract the FIRST JSON object from an LLM reply. Returns the parsed object, or None.

    Handles, in order:
      1. a fenced ```json ... ``` block,
      2. a fenced ``` ... ``` block,
      3. raw JSON with leading/trailing prose (brace-balanced scan).
    Never raises — unparseable input yields None.
    """
    if not isinstance(text, str):
        return None

    # 1 & 2: fenced code blocks. Try a ```json fence first, then a bare ``` fence.
    for fence in ("```json", "```JSON", "```"):
        start = text.find(fence)
        if start == -1:
            continue
        inner_start = start + len(fence)
        end = text.find("```", inner_start)
        if end == -1:
            continue
        candidate = text[inner_start:end].strip()
        obj = _try_parse_first_object(candidate)
        if obj is not None:
            return obj

    # 3: raw JSON embedded in prose — scan the whole string.
    return _try_parse_first_object(text)


def _try_parse_first_object(s: str) -> Optional[Any]:
    """Parse the first brace-balanced {...} (or whole-string JSON) in s. None on failure."""
    s = s.strip()
    if not s:
        return None
    # Fast path: the whole thing is valid JSON.
    try:
        return json.loads(s)
    except Exception:
        pass
    # Brace-balanced scan for the first complete {...}, respecting strings/escapes.
    start = s.find("{")
    while start != -1:
        depth = 0
        in_str = False
        esc = False
        for i in range(start, len(s)):
            c = s[i]
            if in_str:
                if esc:
                    esc = False
                elif c == "\\":
                    esc = True
                elif c == '"':
                    in_str = False
                continue
            if c == '"':
                in_str = True
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    chunk = s[start : i + 1]
                    try:
                        return json.loads(chunk)
                    except Exception:
                        break  # malformed; advance to the next '{'
        start = s.find("{", start + 1)
    return None


# --------------------------------------------------------------------------- #
# JSONL observability log (privacy-preserving: sha of prompt, never the text)
# --------------------------------------------------------------------------- #
def prompt_sha(prompt: str) -> str:
    """Deterministic content hash of a prompt (sha256 hex). Logged in place of the prompt text."""
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def log_call(
    result: Dict[str, Any],
    *,
    model: str,
    prompt: str,
    ts: Optional[float] = None,
    log_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Append one privacy-preserving JSONL line per call. Returns the logged record.

    The full prompt text is NEVER logged (privacy/size) — only its sha. There is no clock in the
    deterministic test path: ts defaults to None (caller may supply one) rather than calling time.
    """
    path = log_path or LOG_PATH
    record = {
        "ts": ts,  # caller-supplied; None when no clock is available (determinism in tests)
        "model": model,
        "prompt_sha": prompt_sha(prompt),
        "prompt_tokens": int(result.get("prompt_tokens", 0) or 0),
        "eval_tokens": int(result.get("eval_tokens", 0) or 0),
        "eval_seconds": float(result.get("eval_seconds", 0.0) or 0.0),
        "ok": bool(result.get("ok", False)),
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")
    return record
