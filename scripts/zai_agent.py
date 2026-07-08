#!/usr/bin/env python3
"""zai_agent.py — a logos-native agentic harness that runs on z.ai/GLM, with NO claude-code dependency.

Owner directive (2026-07-08): "if required do NOT use claude-code; make the code use directly the API
of z.ai — everything must be using z.ai." This is that harness: a self-contained tool-use loop that
drives GLM (glm-4.6 by default) through the approved LiteLLM proxy (nllei01litellm01) to do real work —
read/write files, run shell commands — the same shape of agent loop claude-code provides, but the model
doing the reasoning is z.ai/GLM.

DOCTRINE (CLAUDE.md / Constitution v2.3):
  - This is an OPERATOR/PROPOSER, not an adjudicator. Anything it produces is a signal (invariant #5,
    confidence <= 0.75) and is NEVER a verdict: the mechanical gates (scripts/verdict.py, the comparison
    layer) remain the only thing that decides. An epoch driven by this harness still freezes a prereg,
    runs its positive control, and computes a mechanical verdict — the model only proposes/executes.
  - PROVIDER: z.ai/GLM via the LiteLLM proxy (invariant #11 as amended, v2.3). The vendor key lives on
    the proxy; this process reads only the scoped virtual key from env / runtime/secrets/litellm.env.
    ANTHROPIC_API_KEY is never set; no claude-code / anthropic SDK is imported.
  - OBSERVABILITY (invariant #12): every step + real token counts are logged to runtime/zai_agent/.

Usage:
    python3 scripts/zai_agent.py --task "Summarise the frontier epoch ledger status" [--model glm-4.6]
        [--max-steps 20] [--workdir .] [--allow-write]
    # or programmatically:
    from scripts.zai_agent import ZaiAgent
    out = ZaiAgent(workdir=".").run("… task …")

Pure stdlib + the in-repo litellm_client (which is pure urllib). No third-party deps.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
from typing import Any, Dict, List, Optional

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

# Reuse the proxy config resolution (env / untracked secret file) — no key ever hardcoded here.
from scripts.comparison.litellm_client import _cfg  # noqa: E402

LOG_DIR = os.path.join(_REPO_ROOT, "runtime", "zai_agent")

SYSTEM = (
    "You are the logos z.ai research operator, running on GLM through the approved proxy. You do real "
    "work by calling the provided tools (run_bash, read_file, write_file). You are a PROPOSER/OPERATOR, "
    "never an adjudicator: you never declare a scientific verdict yourself — mechanical gates decide. "
    "Work in small, verifiable steps; prefer reading real files and running real commands over guessing. "
    "When the task is complete, reply with a final plain-text summary and DO NOT call another tool."
)

TOOLS = [
    {"type": "function", "function": {
        "name": "run_bash",
        "description": "Run a bash command in the working directory and return its stdout+stderr (truncated).",
        "parameters": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}}},
    {"type": "function", "function": {
        "name": "read_file",
        "description": "Read a UTF-8 text file (optionally a line range) and return its contents.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"},
            "max_bytes": {"type": "integer", "description": "cap on returned bytes (default 8000)"}},
            "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "write_file",
        "description": "Write text to a file (creates parent dirs). Requires the agent to be run with writes enabled.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}}},
]


class ZaiAgent:
    """A minimal, honest tool-use loop over GLM via the LiteLLM proxy."""

    def __init__(self, *, model: str = "glm-5.2", workdir: str = ".", allow_write: bool = False,
                 max_steps: int = 20, timeout: int = 180):
        self.model = model
        self.workdir = os.path.abspath(workdir)
        self.allow_write = allow_write
        self.max_steps = max_steps
        self.timeout = timeout
        self.cfg = _cfg(None, None)  # {base, key, model_override}
        # LOGOS_LLM_MODEL (env / secret file) wins unless the caller explicitly passed a non-default model.
        if self.cfg["model_override"] and model == "glm-5.2":
            self.model = self.cfg["model_override"]
        self.tokens_in = 0
        self.tokens_out = 0

    # ---- tools -------------------------------------------------------------
    def _run_bash(self, command: str) -> str:
        try:
            p = subprocess.run(command, shell=True, cwd=self.workdir, capture_output=True,
                               text=True, timeout=self.timeout)
            out = (p.stdout or "") + (("\n[stderr]\n" + p.stderr) if p.stderr else "")
            return (out or "(no output)")[:8000]
        except subprocess.TimeoutExpired:
            return f"(timeout after {self.timeout}s)"
        except Exception as e:  # never crash the loop
            return f"(error: {e})"

    def _read_file(self, path: str, max_bytes: int = 8000) -> str:
        try:
            fp = path if os.path.isabs(path) else os.path.join(self.workdir, path)
            with open(fp, "r", encoding="utf-8", errors="replace") as f:
                return f.read(int(max_bytes or 8000))
        except Exception as e:
            return f"(error: {e})"

    def _write_file(self, path: str, content: str) -> str:
        if not self.allow_write:
            return "(writes disabled: re-run with allow_write=True / --allow-write)"
        try:
            fp = path if os.path.isabs(path) else os.path.join(self.workdir, path)
            os.makedirs(os.path.dirname(fp) or ".", exist_ok=True)
            with open(fp, "w", encoding="utf-8") as f:
                f.write(content)
            return f"(wrote {len(content)} bytes to {path})"
        except Exception as e:
            return f"(error: {e})"

    def _dispatch(self, name: str, args: Dict[str, Any]) -> str:
        if name == "run_bash":
            return self._run_bash(args.get("command", ""))
        if name == "read_file":
            return self._read_file(args.get("path", ""), args.get("max_bytes", 8000))
        if name == "write_file":
            return self._write_file(args.get("path", ""), args.get("content", ""))
        return f"(unknown tool: {name})"

    # ---- proxy call --------------------------------------------------------
    def _chat(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        body = json.dumps({
            "model": self.model, "messages": messages, "tools": TOOLS,
            "tool_choice": "auto", "temperature": 0,
        }).encode()
        headers = {"Content-Type": "application/json"}
        if self.cfg["key"]:
            headers["Authorization"] = f"Bearer {self.cfg['key']}"
        req = urllib.request.Request(f"{self.cfg['base']}/v1/chat/completions", data=body, headers=headers)
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            d = json.loads(r.read().decode())
        u = d.get("usage") or {}
        self.tokens_in += int(u.get("prompt_tokens", 0) or 0)
        self.tokens_out += int(u.get("completion_tokens", 0) or 0)
        return d

    # ---- loop --------------------------------------------------------------
    def run(self, task: str) -> Dict[str, Any]:
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": task},
        ]
        transcript: List[Dict[str, Any]] = []
        final = ""
        for step in range(self.max_steps):
            d = self._chat(messages)
            if "choices" not in d:
                final = f"(proxy error: {json.dumps(d)[:300]})"
                break
            msg = d["choices"][0]["message"]
            tool_calls = msg.get("tool_calls") or []
            # The assistant turn must be recorded verbatim (with tool_calls) before tool results.
            messages.append({"role": "assistant", "content": msg.get("content") or "",
                             **({"tool_calls": tool_calls} if tool_calls else {})})
            if not tool_calls:
                final = msg.get("content") or ""
                break
            for tc in tool_calls:
                fn = tc.get("function", {})
                name = fn.get("name", "")
                try:
                    args = json.loads(fn.get("arguments") or "{}")
                except Exception:
                    args = {}
                result = self._dispatch(name, args)
                transcript.append({"step": step, "tool": name, "args": args, "result_head": result[:400]})
                messages.append({"role": "tool", "tool_call_id": tc.get("id", ""),
                                 "name": name, "content": result})
        out = {"task": task, "model": self.model, "final": final, "steps": len(transcript),
               "tools_used": transcript, "tokens_in": self.tokens_in, "tokens_out": self.tokens_out,
               "provider": "z.ai/GLM via LiteLLM proxy"}
        self._log(out)
        return out

    def _log(self, out: Dict[str, Any]) -> None:
        try:
            os.makedirs(LOG_DIR, exist_ok=True)
            rec = {k: out[k] for k in ("task", "model", "steps", "tokens_in", "tokens_out", "provider")}
            rec["final_head"] = (out.get("final") or "")[:400]
            with open(os.path.join(LOG_DIR, "runs.jsonl"), "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        except Exception:
            pass


def main() -> None:
    ap = argparse.ArgumentParser(description="logos z.ai/GLM agent harness (no claude-code).")
    ap.add_argument("--task", required=True)
    ap.add_argument("--model", default="glm-5.2")
    ap.add_argument("--workdir", default=".")
    ap.add_argument("--max-steps", type=int, default=20)
    ap.add_argument("--allow-write", action="store_true")
    a = ap.parse_args()
    agent = ZaiAgent(model=a.model, workdir=a.workdir, allow_write=a.allow_write, max_steps=a.max_steps)
    out = agent.run(a.task)
    print(f"\n=== FINAL ({out['model']}, {out['steps']} tool-steps, "
          f"{out['tokens_in']}+{out['tokens_out']} tok, via z.ai) ===\n{out['final']}")


if __name__ == "__main__":
    main()
