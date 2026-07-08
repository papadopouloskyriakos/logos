"""Tests for the provider-agnostic LiteLLM proxy client (scripts/comparison/litellm_client).

NO NETWORK: urllib.request.urlopen is patched to return a canned OpenAI-compatible chat body, so the
parse path is exercised deterministically. Properties locked in:
  (a) generate parses response + token counts from the OpenAI choices/usage shape;
  (b) generate returns ok=False on a raised exception AND on an {"error":...} body, and NEVER
      propagates (a dead/unauth proxy degrades — signals fail closed);
  (c) LOGOS_LLM_MODEL overrides the requested model in the outgoing request body;
  (d) Authorization: Bearer <key> is sent when a key resolves, and absent when none does;
  (e) llm_backend dispatches to ollama by default and to litellm when LOGOS_LLM_BACKEND selects it;
  (f) doctrine grep — the module source never sets ANTHROPIC_API_KEY and never hardcodes a key.

Run from anywhere:
    python3 -m pytest tests/test_litellm_client.py -q
"""
import io
import json
import os
import sys
from unittest import mock

import pytest

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from scripts.comparison import litellm_client, llm_backend  # noqa: E402


def _canned(body: dict):
    """A context-manager fake mimicking urlopen(...) returning `body` as JSON, capturing the request."""
    captured = {}

    class _Resp(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def _fake_urlopen(req, timeout=None):
        captured["url"] = req.full_url
        captured["headers"] = {k.lower(): v for k, v in req.headers.items()}
        captured["body"] = json.loads(req.data.decode())
        return _Resp(json.dumps(body).encode())

    return _fake_urlopen, captured


OPENAI_OK = {
    "choices": [{"message": {"role": "assistant", "content": "PROXY_OK"}, "finish_reason": "stop"}],
    "usage": {"prompt_tokens": 11, "completion_tokens": 3},
    "model": "glm-4.6",
}


def test_generate_parses_openai_shape(monkeypatch):
    monkeypatch.setenv("LITELLM_BASE_URL", "http://proxy:4000")
    monkeypatch.setenv("LITELLM_API_KEY", "sk-test123")
    monkeypatch.delenv("LOGOS_LLM_MODEL", raising=False)
    fake, cap = _canned(OPENAI_OK)
    with mock.patch("urllib.request.urlopen", fake):
        res = litellm_client.generate("glm-4.6", "hi", options={"temperature": 0, "num_predict": 12})
    assert res["ok"] is True
    assert res["response"] == "PROXY_OK"
    assert res["prompt_tokens"] == 11 and res["eval_tokens"] == 3
    assert cap["url"] == "http://proxy:4000/v1/chat/completions"
    assert cap["headers"].get("authorization") == "Bearer sk-test123"
    assert cap["body"]["max_tokens"] == 12  # num_predict -> max_tokens mapping


def test_model_override(monkeypatch):
    monkeypatch.setenv("LITELLM_BASE_URL", "http://proxy:4000")
    monkeypatch.setenv("LITELLM_API_KEY", "sk-x")
    monkeypatch.setenv("LOGOS_LLM_MODEL", "glm-4.6")
    fake, cap = _canned(OPENAI_OK)
    with mock.patch("urllib.request.urlopen", fake):
        litellm_client.generate("gemma3", "hi")  # caller asks for a local model...
    assert cap["body"]["model"] == "glm-4.6"  # ...but the override routes it to the proxy model


def test_error_body_degrades(monkeypatch):
    monkeypatch.setenv("LITELLM_BASE_URL", "http://proxy:4000")
    monkeypatch.setenv("LITELLM_API_KEY", "sk-x")
    fake, _ = _canned({"error": {"message": "insufficient balance", "code": "1113"}})
    with mock.patch("urllib.request.urlopen", fake):
        res = litellm_client.generate("glm-4.6", "hi")
    assert res["ok"] is False and res["response"] == ""


def test_dead_proxy_never_raises(monkeypatch):
    monkeypatch.setenv("LITELLM_BASE_URL", "http://proxy:4000")

    def _boom(req, timeout=None):
        raise OSError("connection refused")

    with mock.patch("urllib.request.urlopen", _boom):
        res = litellm_client.generate("glm-4.6", "hi")
    assert res["ok"] is False and res["response"] == ""


def test_no_key_no_auth_header(monkeypatch):
    monkeypatch.setenv("LITELLM_BASE_URL", "http://proxy:4000")
    monkeypatch.delenv("LITELLM_API_KEY", raising=False)
    # Point the secret-file loader at a nonexistent path so no key resolves.
    monkeypatch.setattr(litellm_client, "_SECRET_FILE", "/nonexistent/litellm.env")
    fake, cap = _canned(OPENAI_OK)
    with mock.patch("urllib.request.urlopen", fake):
        litellm_client.generate("glm-4.6", "hi")
    assert "authorization" not in cap["headers"]


def test_backend_dispatch(monkeypatch):
    monkeypatch.delenv("LOGOS_LLM_BACKEND", raising=False)
    assert llm_backend.active_backend() == "ollama"
    monkeypatch.setenv("LOGOS_LLM_BACKEND", "litellm")
    assert llm_backend.active_backend() == "litellm"
    monkeypatch.setenv("LOGOS_LLM_BACKEND", "zai")
    assert llm_backend.active_backend() == "litellm"
    seen = {}
    monkeypatch.setattr(llm_backend.litellm_client, "generate",
                        lambda *a, **k: seen.setdefault("hit", True) or {"ok": True})
    llm_backend.generate("m", "p")
    assert seen.get("hit") is True


def test_doctrine_no_hardcoded_key():
    src = open(os.path.join(_REPO_ROOT, "scripts", "comparison", "litellm_client.py")).read()
    assert "ANTHROPIC_API_KEY" not in src
    # no obvious hardcoded sk- / z.ai key literal in source (keys come from env / untracked secret)
    assert "sk-" not in src
    assert "f0e050eb" not in src
