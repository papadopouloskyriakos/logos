"""Tests for the local-Ollama client (scripts/comparison/ollama_client) — comparison-layer §C.4.

NO NETWORK: urllib.request.urlopen is patched to return a canned Ollama JSON, so the parse path is
exercised deterministically. The properties locked in:
  (a) generate parses response + token counts + eval_seconds from eval_duration;
  (b) generate returns ok=False on a raised exception and NEVER propagates (a dead host degrades);
  (c) extract_json handles fenced-json, fenced-plain, raw-with-prose, and returns None on garbage;
  (d) doctrine grep — the module source contains no anthropic/openai and no ANTHROPIC_API_KEY.

Run from anywhere:
    python3 -m pytest tests/test_ollama_client.py -q
"""
import io
import json
import os
import sys
from contextlib import contextmanager
from unittest import mock

import pytest

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from scripts.comparison import ollama_client  # noqa: E402


# --------------------------------------------------------------------------- #
# Helpers — a fake urlopen returning a canned Ollama /api/generate body
# --------------------------------------------------------------------------- #
class _FakeResp:
    def __init__(self, payload: dict):
        self._data = json.dumps(payload).encode()

    def read(self):
        return self._data

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


@contextmanager
def _patch_urlopen(payload=None, raises=None):
    def fake(req, timeout=None):
        if raises is not None:
            raise raises
        return _FakeResp(payload)

    with mock.patch("urllib.request.urlopen", side_effect=fake):
        yield


# --------------------------------------------------------------------------- #
# (a) generate parses response + token counts
# --------------------------------------------------------------------------- #
def test_generate_parses_response_and_token_counts():
    payload = {
        "response": "MA = /da/ ?",
        "prompt_eval_count": 42,
        "eval_count": 7,
        "eval_duration": 2_000_000_000,  # 2.0 s in nanoseconds
    }
    with _patch_urlopen(payload=payload):
        out = ollama_client.generate("gemma3", "give a value", host="http://x:11434")

    assert out["ok"] is True
    assert out["response"] == "MA = /da/ ?"
    assert out["prompt_tokens"] == 42
    assert out["eval_tokens"] == 7
    assert out["eval_seconds"] == pytest.approx(2.0)


def test_generate_default_options_temperature_zero():
    """Reproducibility: options default to {'temperature': 0}; the posted body must carry it."""
    captured = {}

    def fake(req, timeout=None):
        captured["body"] = json.loads(req.data.decode())
        return _FakeResp({"response": "ok", "prompt_eval_count": 1, "eval_count": 1})

    with mock.patch("urllib.request.urlopen", side_effect=fake):
        ollama_client.generate("gemma3", "p", host="http://x:11434")

    assert captured["body"]["options"] == {"temperature": 0}
    assert captured["body"]["stream"] is False


# --------------------------------------------------------------------------- #
# (b) generate returns ok=False on a raised exception, never propagating
# --------------------------------------------------------------------------- #
def test_generate_degrades_on_exception_never_raises():
    with _patch_urlopen(raises=OSError("dead host")):
        out = ollama_client.generate("gemma3", "p", host="http://nope:11434", timeout=1)
    assert out["ok"] is False
    assert out["response"] == ""
    assert out["prompt_tokens"] == 0
    assert out["eval_tokens"] == 0


# --------------------------------------------------------------------------- #
# (c) extract_json — fenced-json, fenced-plain, raw-with-prose, garbage -> None
# --------------------------------------------------------------------------- #
def test_extract_json_fenced_json_block():
    text = 'Here is my answer:\n```json\n{"sign": "DA", "value": "da", "conf": 0.7}\n```\nDone.'
    obj = ollama_client.extract_json(text)
    assert obj == {"sign": "DA", "value": "da", "conf": 0.7}


def test_extract_json_fenced_plain_block():
    text = "```\n{\"a\": 1, \"b\": [2, 3]}\n```"
    assert ollama_client.extract_json(text) == {"a": 1, "b": [2, 3]}


def test_extract_json_raw_with_prose():
    text = 'The model thinks {"value": "ka", "nested": {"x": 1}} is best, trust me.'
    assert ollama_client.extract_json(text) == {"value": "ka", "nested": {"x": 1}}


def test_extract_json_handles_brace_in_string():
    text = 'prose {"note": "a } brace in a string", "n": 1} tail'
    assert ollama_client.extract_json(text) == {"note": "a } brace in a string", "n": 1}


def test_extract_json_returns_none_on_garbage():
    assert ollama_client.extract_json("no json here at all") is None
    assert ollama_client.extract_json("{ broken : ") is None
    assert ollama_client.extract_json("") is None
    assert ollama_client.extract_json(None) is None


# --------------------------------------------------------------------------- #
# JSONL observability log — sha only, ts defaults to None (determinism)
# --------------------------------------------------------------------------- #
def test_log_call_writes_sha_not_prompt(tmp_path):
    log_path = str(tmp_path / "llm_calls.jsonl")
    result = {"prompt_tokens": 3, "eval_tokens": 5, "eval_seconds": 1.5, "ok": True}
    rec = ollama_client.log_call(
        result, model="gemma3", prompt="SECRET PROMPT", log_path=log_path
    )

    assert rec["ts"] is None  # no clock supplied -> None, not a time() call
    assert rec["prompt_sha"] == ollama_client.prompt_sha("SECRET PROMPT")
    assert rec["model"] == "gemma3"

    with open(log_path, encoding="utf-8") as f:
        line = f.readline()
    on_disk = json.loads(line)
    # Privacy: the raw prompt text must NEVER appear in the log line.
    assert "SECRET PROMPT" not in line
    assert on_disk["prompt_sha"] == rec["prompt_sha"]
    assert on_disk["ok"] is True


def test_log_call_accepts_caller_timestamp(tmp_path):
    log_path = str(tmp_path / "llm_calls.jsonl")
    result = {"prompt_tokens": 1, "eval_tokens": 1, "eval_seconds": 0.1, "ok": True}
    rec = ollama_client.log_call(
        result, model="gemma3", prompt="p", ts=1700000000.0, log_path=log_path
    )
    assert rec["ts"] == 1700000000.0


# --------------------------------------------------------------------------- #
# (d) doctrine grep — no anthropic / openai / ANTHROPIC_API_KEY in the source
# --------------------------------------------------------------------------- #
def test_module_source_has_no_proprietary_provider():
    src_path = os.path.join(_REPO_ROOT, "scripts", "comparison", "ollama_client.py")
    with open(src_path, encoding="utf-8") as f:
        src = f.read().lower()
    assert "anthropic" not in src
    assert "openai" not in src
    assert "anthropic_api_key" not in src
