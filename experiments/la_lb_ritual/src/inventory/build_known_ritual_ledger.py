#!/usr/bin/env python3
"""§VII known-pair quarantine ledger — source-critical, with drift characterization.

Characterizes the ALREADY-PUBLIC ritual/localized continuities (+ PA-I-TO admin comparison). The
edit-distance here operates ONLY on these quarantined, public known pairs to fill the required
`number_of_edit_operations` field — it is NOT a candidate↔target matcher and touches neither packet A
nor packet B (the §XI leakage audit confirms no similarity runs on the inventories). These pairs must
NOT select candidates/targets, set thresholds, fit drift rules, define edit operations, or establish
power. Default: KNOWN_PAIR_DEVELOPMENT / CONFIRMATORY_INELIGIBLE.
"""
import json, os, sys

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "la_lb_continuity", "src", "common"))
import syllabary as syl  # noqa: E402

CHANNEL = {"channel_origin": "POSTHOC_GENRE_REDIRECT", "channel_class": "EXPLORATORY_POSTHOC_CHANNEL"}

# (pair_id, LA phonetic, LB translit, la_context, lb_context, chronology, cite, first_pub, indep_semantic)
PAIRS = [
    ("KRP-TU-RU-SA", ["TU", "RU", "SA"], "tu-ri-so", "LA libation (stone vessel, Kophinas)",
     "LB admin toponym (KN)", "LM IB → LM II-IIIA", "Salgarella 2025 lecture", "pre-2025", "toponym (Tylissos)"),
    ("KRP-I-DA", ["I", "DA"], "i-da-i-jo", "LA libation (stone vessels, Zakros/PK/Nerokurou)",
     "LB adj. Idaian (KN)", "LM IB → LM II-IIIA", "Salgarella 2025 lecture", "pre-2025", "oronym (Mt Ida)"),
    ("KRP-SE-TO-I-JA", ["SE", "TO", "I", "JA"], "se-to-i-ja", "LA libation (stone vessel, Prassa, LM IA)",
     "LB district (KN)", "LM IA → LM II-IIIA", "Salgarella 2025 lecture", "pre-2025", "toponym (Seteia)"),
    ("KRP-DI-KI-TA", ["DI", "KI", "TA"], "di-ka-ta-de", "LA (bare form absent in silver)",
     "LB Diktaian sanctuary (KN Fp 1)", "— → LM II-IIIA", "Salgarella 2025 lecture", "pre-2025", "sanctuary (Dikte)"),
    ("KRP-PA-I-TO", ["PA", "I", "TO"], "pa-i-to", "LA admin (HT tablets) — ADMIN COMPARISON",
     "LB admin toponym (KN)", "LM IB → LM II-IIIA", "Younger; Salgarella 2025", "pre-2025", "toponym (Phaistos)"),
]


def _edit_ops(a, b):
    """Levenshtein on GORILA-number sequences — quarantined-known-pairs only (not a matcher)."""
    m, n = len(a), len(b)
    dp = list(range(n + 1))
    for i in range(1, m + 1):
        prev, dp[0] = dp[0], i
        for j in range(1, n + 1):
            cur = dp[j]
            dp[j] = min(dp[j] + 1, dp[j - 1] + 1, prev + (a[i - 1] != b[j - 1]))
            prev = cur
    return dp[n]


def build():
    rows = []
    for pid, la, lb_translit, lactx, lbctx, chron, cite, firstpub, indep in PAIRS:
        la_raw = syl.render(la)
        lb_raw = syl.lb_sequence(lb_translit)
        a = [int(x[2:]) if isinstance(x, str) and x.startswith("AB") and x[2:].isdigit() else x for x in la_raw]
        b = [int(x[1:]) if isinstance(x, str) and x.startswith("*") and x[1:].isdigit() else x for x in lb_raw]
        edits = _edit_ops(a, b)
        rows.append({
            **CHANNEL,
            "pair_id": pid, "la_form": "-".join(la), "lb_form": lb_translit,
            "la_raw_sign_sequence": la_raw, "lb_raw_sign_sequence": lb_raw,
            "la_context": lactx, "lb_context": lbctx, "chronology": chron,
            "source_citation": cite, "first_known_publication": firstpub,
            "selection_history": "observed before this channel (POSTHOC_GENRE_REDIRECT)",
            "exact_identity": edits == 0,
            "palaeographic_identity": edits == 0,          # tier-A map = exact here (no allographs clustered)
            "projected_phonetic_identity": edits == 0,
            "drift_required": edits > 0,
            "number_of_edit_operations": edits,
            "independent_semantic_support": indep,
            "posthoc_risk": "HIGH",
            "development_role": "KNOWN_PAIR_DEVELOPMENT",
            "confirmatory_eligibility": "CONFIRMATORY_INELIGIBLE",
        })
    return rows


def main():
    out = os.path.normpath(os.path.join(HERE, "..", "..", "data", "quarantine")); os.makedirs(out, exist_ok=True)
    rows = build()
    with open(os.path.join(out, "known_ritual_pair_ledger.jsonl"), "w", encoding="utf-8") as f:
        for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("known ritual pairs:", len(rows))
    for r in rows:
        print(f"  {r['pair_id']:16} {r['la_form']:11} ~ {r['lb_form']:11} edits={r['number_of_edit_operations']} "
              f"drift={r['drift_required']} [{r['confirmatory_eligibility']}]")
    exact = sum(1 for r in rows if r["exact_identity"])
    print(f"  exact-identity: {exact}/{len(rows)}; drift-required: {sum(1 for r in rows if r['drift_required'])}")


if __name__ == "__main__":
    main()
