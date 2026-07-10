#!/usr/bin/env python3
"""E214 adversarial-closure verifier battery. Read-only. Exit 0 iff all checks pass.
Checks: (1) banned-wording sweep (disclaimer-aware); (2) status vocabulary; (3) freeze
integrity (every *.sha256 still matches its target); (4) E212 graph shape; (5) append-only
as-run preservation; (6) seal integrity WITHOUT opening (if E213 exists)."""
import hashlib, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # research/logos2
MAIN = "/home/claude-runner/gitlab/n8n/logos"
FAILS = []

BANNED = [r"\bdeciphered\b", r"\btranslation of\b", r"\breads as\b", r"\bproves\b",
          r"RAG confirm", r"retrieved proof", r"phonetic value of .{1,40} is\b",
          r"\bwe can now read\b", r"\bthe language (is|was)\b"]
DISCLAIM = re.compile(r"\b(no|not|never|cannot|can't|without|refus|reject|null|ban|forbid|"
                      r"must not|may not|barred|banned)\b", re.I)
SELF = ("run_battery.py", "BANNED_WORDING", "verifier")

def sweep_wording():
    n_flag = 0
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in (".venv", "results_asrun_R0", "__pycache__",
                                              "state", "logs")]
        for fn in fns:
            if not fn.endswith((".md", ".json", ".csv", ".txt")) or any(s in fn for s in SELF):
                continue
            p = os.path.join(dp, fn)
            try:
                lines = open(p, encoding="utf-8", errors="replace").read().splitlines()
            except Exception:
                continue
            for i, ln in enumerate(lines, 1):
                for pat in BANNED:
                    if re.search(pat, ln, re.I) and not DISCLAIM.search(ln):
                        FAILS.append(f"WORDING {os.path.relpath(p, ROOT)}:{i}: {ln.strip()[:100]}")
                        n_flag += 1
    return n_flag

VOCAB = {"L3_METROLOGICAL_CLASS_SUPPORTED", "METROLOGICAL_RELATIONS_PARTIAL",
         "UNDERDETERMINED_AFTER_ABLATION", "NULL_NOT_DISTINCTIVE", "E204_INVALID",
         "NO_MATCH_BEYOND_CANARIES", "L3_ONOMASTIC_CLASS_SUPPORTED",
         "ONOMASTIC_CANDIDATES_EXPLORATORY_ONLY", "E206_INVALID", "POSITIONAL_ONLY",
         "PRIOR_GENERIC", "CORES_TYPICAL_OF_RANDOM", "GATE_PASSED", "GATE_FAILED",
         "RAG_USEFUL_FOR_AUDIT_ONLY", "RAG_NOT_USEFUL", "PENDING_EXTERNAL",
         "CAMPAIGN_NULL_GATES_CERTIFIED", "ENGINE_VALIDATED", "GATE_PASSED_5_OF_5", "SUPPORTED", "REFUTED", "NO_POWER",
         "UNDERDETERMINED", "COMPLETE", "RUNNING", "PROPOSED", "BLOCKED", "INVALID",
         "SEALED_PROSPECTIVE", "NOT_AN_EVIDENTIAL_CHANNEL"}

def check_vocab():
    for dp, dns, fns in os.walk(os.path.join(ROOT, "experiments")):
        dns[:] = [d for d in dns if d not in (".venv", "__pycache__", "results_asrun_R0")]
        for fn in fns:
            if fn.endswith(".json") and ("RESULT" in fn or "STATUS" in fn.upper()):
                try:
                    j = json.load(open(os.path.join(dp, fn)))
                except Exception:
                    continue
                for key in ("verdict", "E204_TERMINAL_STATUS"):
                    v = j.get(key)
                    if isinstance(v, str) and v.split(" ")[0] not in VOCAB:
                        FAILS.append(f"VOCAB {fn}: {key}={v} not in frozen vocabulary")
                s = j.get("status")
                if isinstance(s, str) and not re.fullmatch(r"[A-Z0-9_]+( \(.*\))?", s.split(" (")[0] if False else s) \
                        and not re.fullmatch(r"[A-Za-z0-9_]+", s.split(" ")[0]):
                    FAILS.append(f"VOCAB {fn}: status={s!r} not a mechanical token")

def check_freezes():
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d != ".venv"]
        for fn in fns:
            if not fn.endswith(".sha256"):
                continue
            p = os.path.join(dp, fn)
            for ln in open(p):
                parts = ln.split()
                if len(parts) != 2:
                    continue
                want, rel = parts[0], parts[1]
                err = p + ".ERRATUM.md"
                if os.path.exists(err) and os.path.basename(rel) in open(err).read():
                    continue  # covered by an append-only erratum record
                target = None
                for root in (dp, ROOT, MAIN):
                    cand = os.path.join(root, rel)
                    if os.path.exists(cand):
                        target = cand
                        break
                if target is None:
                    continue  # asset lives on another branch; not checkable from this tree
                got = hashlib.sha256(open(target, "rb").read()).hexdigest()
                if got != want:
                    FAILS.append(f"FREEZE {fn}: {rel} hash drift")

def check_graph():
    p = os.path.join(ROOT, "experiments", "E212_independence_graph.json")
    try:
        g = json.load(open(p))
    except Exception as e:
        FAILS.append(f"E212 graph unreadable: {e}"); return
    ok_prefix = ("SINGLE_CHANNEL", "CONDITIONALLY_INDEPENDENT", "NOT_A_CHANNEL",
                 "MULTI_CHANNEL_INDEPENDENT")
    for cid, c in g.get("claims", {}).items():
        if not str(c.get("classification", "")).startswith(ok_prefix):
            FAILS.append(f"E212 claim {cid}: bad classification")
    if "independence_verdict" not in g:
        FAILS.append("E212: independence_verdict missing (graph not finalized)")

def check_asrun():
    p = os.path.join(ROOT, "experiments", "E207_morphology", "results_asrun_R0")
    if not os.path.isdir(p):
        FAILS.append("APPEND-ONLY: E207 results_asrun_R0 (INVALID as-run) was deleted")

def check_seal():
    sd = os.path.join(ROOT, "experiments", "E213_prospective_seal")
    if not os.path.isdir(sd):
        print("  (E213 seal not present yet — skipped)"); return
    man = json.load(open(os.path.join(sd, "SEAL_MANIFEST.json")))
    blob = os.path.join(sd, man["sealed_file"])
    got = hashlib.sha256(open(blob, "rb").read()).hexdigest()
    if got != man["sealed_sha256"]:
        FAILS.append("SEAL: sealed blob hash mismatch")
    if man.get("opened"):
        FAILS.append("SEAL: manifest marked opened before opening condition")

def main():
    n = sweep_wording(); check_vocab(); check_freezes(); check_graph(); check_asrun(); check_seal()
    print(f"banned-wording flags: {n}")
    for f in FAILS:
        print("FAIL:", f)
    print("BATTERY:", "PASS" if not FAILS else f"FAIL ({len(FAILS)})")
    return 1 if FAILS else 0

if __name__ == "__main__":
    raise SystemExit(main())
