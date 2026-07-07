#!/usr/bin/env python3
"""Per-stage constitutional headers (Constitution v2.0/2.1 Art. XXII).

Art. XXII: every research stage OPENS by recording articles_consulted / articles_triggered / required
gates / assumptions checked / authorized + forbidden outputs, and CLOSES with a compliance / deviations /
violations / waivers / amendments block. This module builds + validates that header (composing the Art.
XVIII assumption gate) and renders the markdown form used in experiment reports. A stage without a valid
header is blocked (a linter can call `validate`). Deterministic; no DB.
"""
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

# valid article references I..XXIII
_ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV",
          "XVI", "XVII", "XVIII", "XIX", "XX", "XXI", "XXII", "XXIII"]
VALID_ARTICLES = set(_ROMAN)

_OPEN_FIELDS = ("stage", "articles_consulted", "articles_triggered", "required_gates",
                "assumptions_checked", "authorized_outputs", "forbidden_outputs")


def open_header(stage, articles_consulted, articles_triggered, required_gates,
                assumptions_checked, authorized_outputs, forbidden_outputs, claim_layer=None):
    return {"stage": stage, "articles_consulted": list(articles_consulted),
            "articles_triggered": list(articles_triggered), "required_gates": list(required_gates),
            "assumptions_checked": list(assumptions_checked), "authorized_outputs": list(authorized_outputs),
            "forbidden_outputs": list(forbidden_outputs), "claim_layer": claim_layer}


def close_block(constitutional_compliance, deviations=None, violations=None, waivers=None,
                amendments_required=None):
    return {"constitutional_compliance": constitutional_compliance, "deviations": deviations or [],
            "violations": violations or [], "waivers": waivers or [],
            "amendments_required": amendments_required or []}


def validate(header, enforce_assumptions=True):
    """Return a list of problems (empty = OK). Checks required fields, valid article refs, and — via the
    Art. XVIII gate — that no declared assumption is FALSE/STALE (that would block the stage)."""
    problems = []
    for f in _OPEN_FIELDS:
        if f not in header:
            problems.append(f"missing required header field '{f}' (Art. XXII)")
    for a in header.get("articles_consulted", []) + header.get("articles_triggered", []):
        if a not in VALID_ARTICLES:
            problems.append(f"invalid article reference '{a}' (must be I..XXIII)")
    if enforce_assumptions and header.get("assumptions_checked"):
        try:
            from scripts import assumption_gate
            r = assumption_gate.check(header["assumptions_checked"])
            for b in r["blocked"]:
                problems.append(f"stage depends on FALSE/STALE assumption {b['id']} ({b['status']}) — Art. XVIII blocks")
        except KeyError as e:
            problems.append(str(e))
    return problems


def render_md(header, close=None):
    """Markdown header block (matches the experiment-report convention)."""
    lines = ["## Constitutional stage header (Art. XXII)", ""]
    lines.append(f"- **stage:** {header['stage']}"
                 + (f" · **claim_layer:** {header['claim_layer']}" if header.get("claim_layer") else ""))
    lines.append(f"- **articles_consulted:** {', '.join(header['articles_consulted'])}")
    lines.append(f"- **articles_triggered:** {', '.join(header['articles_triggered'])}")
    lines.append(f"- **required_gates:** {'; '.join(header['required_gates'])}")
    lines.append(f"- **assumptions_checked:** {', '.join(header['assumptions_checked'])}")
    lines.append(f"- **authorized_outputs:** {'; '.join(header['authorized_outputs'])}")
    lines.append(f"- **forbidden_outputs:** {'; '.join(header['forbidden_outputs'])}")
    if close:
        lines += ["", f"- **constitutional_compliance:** {close['constitutional_compliance']}"]
        for k in ("deviations", "violations", "waivers", "amendments_required"):
            if close.get(k):
                lines.append(f"- **{k}:** {'; '.join(close[k])}")
    return "\n".join(lines)


def _demo():
    h = open_header("Experiment 2 — masked quantity",
                    articles_consulted=["V", "VIII", "XII", "XIII", "XV", "XVI"],
                    articles_triggered=["XIII", "XII"], claim_layer="L3",
                    required_gates=["beat baseline + null under A12", "cross-site"],
                    assumptions_checked=["A06", "A07"],
                    authorized_outputs=["anonymous LB structural observations"],
                    forbidden_outputs=["any Linear A semantic/phonetic claim"])
    print(render_md(h, close_block("COMPLIANT")))
    print("\nvalidate:", validate(h))


if __name__ == "__main__":
    _demo()
