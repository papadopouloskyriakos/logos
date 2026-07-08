#!/usr/bin/env python3
"""epoch_runner.py — deterministic epoch-contract enforcement around a GLM worker (zai_agent).

The problem this solves: a free-form GLM worker produces correct science but is not RELIABLE about
completeness/integrity (e.g. EPOCH-023 skipped writing its report). Trusting the model to follow a
multi-step protocol perfectly does not scale. So we apply the LOGOS principle one level up: the model
does the creative/statistical work; DETERMINISTIC CODE enforces the structural contract, and the worker
is auto-looped to repair mechanical failures before the orchestrator ever sees it.

Layers:
  1. MECHANICAL COMPLETION GATE (check_epoch) — post-loop, no LLM: required files exist+non-empty;
     plan_hash matches prereg sha256; result.json schema (keys, verdict in allowed vocab, >=N
     successors, layer present); overclaim scan; optional reproducibility (re-run a script, diff a
     numeric subset of result.json).
  2. AUTO-REPAIR LOOP (run_epoch) — feed the exact problem list back to GLM (<=max_repairs passes);
     the worker re-reads its own dir and patches ONLY the flagged items (frozen prereg/plan_hash are
     off-limits). Then re-gate. Escalate to the orchestrator only if it still fails.
  3. MANIFEST — the runner returns the exact list of files produced, so committing adds only paths that
     exist (no `git add` pathspec-fatal).

What this deliberately does NOT do: judge scientific soundness (is the null appropriate? is the PC
fair?). That stays with the human/Claude orchestrator — automating it away would defeat the discipline.

Usage:
    from scripts.epoch_runner import run_epoch, EpochSpec
    spec = EpochSpec(epoch_id="EPOCH-024", workdir=FRONTIER, task=TASK,
                     required_files=["epochs/EPOCH-024/prereg.md", ...],
                     allowed_verdicts={"...","..."}, repro_script="epochs/EPOCH-024/machinery.py")
    report = run_epoch(spec)   # -> {"passed":bool,"problems":[...],"manifest":[...],"repairs":int}
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Set

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from scripts.zai_agent import ZaiAgent  # noqa: E402

REQUIRED_RESULT_KEYS = {"task_id", "verdict", "numbers", "key_findings", "successor_hypotheses"}
# Over-layer (L4+) claim words. The phonetic-slash form is /na/-style (1-4 letters, slash-delimited,
# NOT a path segment) — the earlier `/[a-z]+/` matched file paths, a false positive fixed here.
OVERCLAIM = re.compile(
    r"\b(phonetic|pronounc|semitic|greek|translat|meaning)\b|\bmeans\b|(?<![\w./])/[a-z]{1,4}/(?![\w./])", re.I)
DISCLAIMER_HINT = re.compile(
    r"non.?circular|no phonetic|anonymous|not? (a )?(sound|value|reading)|assigned to any sign|"
    r"only a positional|positional slot|disclaim|control.?only|benchmark|"
    r"licen[cs]e|does not|structural (result|only)|\bl4\+?\b|never a (sound|value|reading|meaning)|"
    r"no meaning|no .{0,20}is assigned|assigned to|does not (generalize|constitute)|positional|no semantic|"
    r"\bno\b.{0,40}(phonetic|meaning|value|reading|semantic)|(phonetic|meaning|value|semantic).{0,20}\bor meaning\b|"
    r"analog|token.?type|held.?out|closest l\d", re.I)


def _demark(s: str) -> str:
    """Strip markdown emphasis so `does **not**` / `_meaning_` still match keyword regexes."""
    return s.replace("*", "").replace("`", "").replace("_", "")


def _looks_like_path_or_code(line: str) -> bool:
    """True for lines that are file paths / code refs (not prose) — excluded from the overclaim scan."""
    s = line.strip().strip("-* ").strip("`")
    return bool(re.match(r"^[\w./-]+\.(md|json|py|txt|yaml|yml|csv|npz)$", s) or s.startswith("experiments/")
                or s.startswith("epochs/") or s.startswith("reports/") or s.startswith("scripts/")
                or s.startswith("data/"))


def _scan_overclaim(rel: str, fp: str) -> List[str]:
    """Flag over-layer claims, skipping disclaimer context (this/prev-2 lines) and path/code lines."""
    out: List[str] = []
    lines = [_demark(l) for l in open(fp, encoding="utf-8", errors="replace").read().splitlines()]
    for i, line in enumerate(lines):
        if not OVERCLAIM.search(line):
            continue
        if line.lstrip().startswith(">") or _looks_like_path_or_code(line):
            continue  # blockquote (disclaimer/quote) or a path/code line
        window = " ".join(lines[max(0, i - 2):i + 1])
        if DISCLAIMER_HINT.search(window):
            continue  # negated/disclaimed within a 3-line window
        out.append(f"POSSIBLE_OVERCLAIM: {rel}:{i + 1}: {line.strip()[:100]}")
    return out


@dataclass
class EpochSpec:
    epoch_id: str
    workdir: str
    task: str
    required_files: List[str]                 # paths relative to workdir
    allowed_verdicts: Set[str]
    min_successors: int = 5
    result_path: Optional[str] = None         # default epochs/<id>/result.json
    prereg_path: Optional[str] = None
    plan_hash_path: Optional[str] = None
    repro_script: Optional[str] = None        # re-run this and confirm it exits 0 (determinism/soundness smoke)
    repro_check: Optional[Callable[[dict], List[str]]] = None  # orchestrator numeric verifier(result_json)->problems
    scan_files: List[str] = field(default_factory=list)       # extra files for the overclaim scan
    model: str = "glm-5.2"
    max_steps: int = 36
    max_repairs: int = 2


def _p(spec: EpochSpec, rel: str) -> str:
    return rel if os.path.isabs(rel) else os.path.join(spec.workdir, rel)


def spec_for(*, epoch_id: str, workdir: str, base: str, task_body: str, allowed_verdicts: Set[str],
             extra_required: Optional[List[str]] = None, repro_script: Optional[str] = None,
             repro_check=None, **kw) -> "EpochSpec":
    """Build an EpochSpec with CANONICAL, non-drifting artifact paths under `base` (the campaign subdir,
    e.g. 'experiments/linear_a_frontier_72h'). Also prepends an explicit path contract to the task so the
    worker cannot resolve 'reports/…' to the wrong root — the exact ambiguity that misplaced E023's report.
    """
    ed = f"{base}/epochs/{epoch_id}"
    rp = f"{ed}/result.json"
    report = f"{base}/reports/{epoch_id.replace('-', '')}_REPORT.md"
    required = [f"{ed}/prereg.md", f"{ed}/plan_hash.txt", rp] + (extra_required or [])
    contract = (
        f"PATH CONTRACT (absolute within the working dir — use these EXACT paths, do not abbreviate):\n"
        f"  prereg   -> {ed}/prereg.md\n  plan_hash -> {ed}/plan_hash.txt\n  result   -> {rp}\n"
        f"  report   -> {report}\n  data dir -> {base}/data/{epoch_id.lower().replace('-', '_')}/\n\n")
    return EpochSpec(
        epoch_id=epoch_id, workdir=workdir, task=contract + task_body,
        required_files=required + [report], allowed_verdicts=allowed_verdicts,
        result_path=rp, prereg_path=f"{ed}/prereg.md", plan_hash_path=f"{ed}/plan_hash.txt",
        repro_script=repro_script, repro_check=repro_check, scan_files=[report], **kw)


def check_epoch(spec: EpochSpec) -> List[str]:
    """Deterministic completion gate. Returns a list of problem strings ([] == PASS)."""
    problems: List[str] = []
    rp = spec.result_path or f"epochs/{spec.epoch_id}/result.json"
    pre = spec.prereg_path or f"epochs/{spec.epoch_id}/prereg.md"
    ph = spec.plan_hash_path or f"epochs/{spec.epoch_id}/plan_hash.txt"

    # 1. completeness
    for rel in spec.required_files:
        fp = _p(spec, rel)
        if not os.path.exists(fp):
            problems.append(f"MISSING_FILE: {rel}")
        elif os.path.getsize(fp) == 0:
            problems.append(f"EMPTY_FILE: {rel}")

    # 2. plan_hash integrity
    pre_fp, ph_fp = _p(spec, pre), _p(spec, ph)
    if os.path.exists(pre_fp) and os.path.exists(ph_fp):
        sha = hashlib.sha256(open(pre_fp, "rb").read()).hexdigest()
        if sha not in open(ph_fp, encoding="utf-8", errors="replace").read():
            problems.append(f"PLAN_HASH_MISMATCH: sha256(prereg)={sha[:12]}… not found in {ph}")

    # 3. result.json schema
    rp_fp = _p(spec, rp)
    result = None
    if os.path.exists(rp_fp):
        try:
            result = json.load(open(rp_fp, encoding="utf-8"))
            missing = REQUIRED_RESULT_KEYS - set(result)
            if missing:
                problems.append(f"RESULT_MISSING_KEYS: {sorted(missing)}")
            v = str(result.get("verdict", "")).split()[0] if result.get("verdict") else ""
            if spec.allowed_verdicts and v not in spec.allowed_verdicts:
                problems.append(f"VERDICT_NOT_IN_VOCAB: '{v}' not in {sorted(spec.allowed_verdicts)}")
            succ = result.get("successor_hypotheses", [])
            if not isinstance(succ, list) or len(succ) < spec.min_successors:
                problems.append(f"TOO_FEW_SUCCESSORS: {len(succ) if isinstance(succ,list) else 'n/a'} < {spec.min_successors}")
        except Exception as e:
            problems.append(f"RESULT_JSON_UNPARSEABLE: {e}")

    # 4. overclaim scan (windowed disclaimer handling; path/code lines excluded)
    for rel in [rp] + spec.scan_files:
        fp = _p(spec, rel)
        if os.path.exists(fp):
            problems.extend(_scan_overclaim(rel, fp))

    # 5. reproducibility smoke (re-run the worker's own machinery/script; must exit 0)
    if spec.repro_script:
        sp = _p(spec, spec.repro_script)
        if os.path.exists(sp):
            try:
                r = subprocess.run([sys.executable, sp], cwd=spec.workdir,
                                   capture_output=True, text=True, timeout=600)
                if r.returncode != 0:
                    problems.append(f"REPRO_SCRIPT_FAILED(rc={r.returncode}): {(r.stderr or '')[:200]}")
            except Exception as e:
                problems.append(f"REPRO_SCRIPT_ERROR: {e}")
        else:
            problems.append(f"REPRO_SCRIPT_MISSING: {spec.repro_script}")

    # 6. orchestrator numeric verifier (optional, pluggable)
    if spec.repro_check and result is not None:
        try:
            problems.extend(spec.repro_check(result))
        except Exception as e:
            problems.append(f"REPRO_CHECK_RAISED: {e}")

    return problems


def _manifest(spec: EpochSpec) -> List[str]:
    """Files under epochs/<id>/ + reports/<id>* + declared required_files that actually exist."""
    found: Set[str] = set()
    for rel in spec.required_files:
        if os.path.exists(_p(spec, rel)):
            found.add(rel)
    edir = _p(spec, f"epochs/{spec.epoch_id}")
    if os.path.isdir(edir):
        for f in os.listdir(edir):
            if f != "__pycache__" and os.path.isfile(os.path.join(edir, f)):
                found.add(f"epochs/{spec.epoch_id}/{f}")
    return sorted(found)


def run_epoch(spec: EpochSpec) -> Dict:
    """Run the GLM worker, then gate + auto-repair. Returns a machine-readable completion report."""
    agent = ZaiAgent(model=spec.model, workdir=spec.workdir, allow_write=True, max_steps=spec.max_steps)
    agent.run(spec.task)
    problems = check_epoch(spec)
    repairs = 0
    while problems and repairs < spec.max_repairs:
        repairs += 1
        repair_task = (
            f"REPAIR PASS for {spec.epoch_id}. Your epoch output FAILED these MECHANICAL checks — fix ONLY "
            f"these, re-reading your own files in epochs/{spec.epoch_id}/ first. DO NOT change the frozen "
            f"prereg.md or plan_hash.txt. Problems:\n- " + "\n- ".join(problems) +
            "\nWhen done, STOP. Use run_bash/read_file/write_file."
        )
        agent = ZaiAgent(model=spec.model, workdir=spec.workdir, allow_write=True, max_steps=16)
        agent.run(repair_task)
        problems = check_epoch(spec)
    return {"epoch_id": spec.epoch_id, "passed": not problems, "problems": problems,
            "repairs": repairs, "manifest": _manifest(spec)}


def git_add_existing(repo: str, paths: List[str]) -> List[str]:
    """Force-add only paths that exist (avoids `git add` pathspec-fatal aborting the whole stage)."""
    existing = [p for p in paths if os.path.exists(os.path.join(repo, p))]
    if existing:
        subprocess.run(["git", "-C", repo, "add", "-f", *existing], check=False)
    return existing
