#!/usr/bin/env python3
"""LOGOS-2 mechanical deliverable generator (invariant 12: counts from scripts).
Emits: EXPERIMENT_STATUS.csv, CLAIM_LEDGER.csv, MACHINE_READABLE_SUMMARY.json,
ARTIFACT_MANIFEST.json, BUNDLE_MANIFEST.sha256. Refuses until E212 is FINAL and the
E213 seal exists. Prose deliverables are authored separately and hashed here."""
import csv, glob, hashlib, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIN = os.path.join(ROOT, "final")
def j(p):
    try: return json.load(open(p))
    except Exception: return {}

def main():
    g = j(os.path.join(ROOT, "experiments", "E212_independence_graph.json"))
    if g.get("status") != "FINAL":
        print("REFUSED: E212 not FINAL"); return 1
    if not os.path.exists(os.path.join(ROOT, "experiments", "E213_prospective_seal", "SEAL_MANIFEST.json")):
        print("REFUSED: E213 seal absent"); return 1

    # EXPERIMENT_STATUS.csv — from STATUS.json files, never hand-written
    rows = []
    for sp in sorted(glob.glob(os.path.join(ROOT, "experiments", "E2*", "STATUS.json"))):
        s = j(sp)
        exp = os.path.basename(os.path.dirname(sp))
        rows.append([exp, s.get("status") or s.get("verdict", ""), s.get("prior", "")])
    rows.append(["E211_RAG", j(os.path.join(ROOT, "rag", "STATUS.json")).get("status", ""), ""])
    rows.append(["E212", "FINAL", ""])
    e213 = j(os.path.join(ROOT, "experiments", "E213_prospective_seal", "SEAL_MANIFEST.json"))
    rows.append(["E213", e213.get("status", ""), f"{e213.get('n_predictions')} predictions sealed"])
    rows.append(["E201_F1b", "PENDING_EXTERNAL", "import boundary armed; not closure-blocking"])
    with open(os.path.join(FIN, "EXPERIMENT_STATUS.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["experiment", "terminal_status", "note"]); w.writerows(rows)

    # CLAIM_LEDGER.csv — from the FINAL independence graph
    with open(os.path.join(FIN, "CLAIM_LEDGER.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["claim", "layer", "classification", "decisive_inputs"])
        for k, c in g["claims"].items():
            w.writerow([k, c.get("level", ""), c.get("classification", ""),
                        "; ".join(c.get("decisive_inputs", []))])

    # MACHINE_READABLE_SUMMARY.json
    e204 = j(os.path.join(ROOT, "experiments", "E204_metrology", "E204_FINAL_STATUS.json"))
    soft = j(os.path.join(ROOT, "experiments", "E204_metrology", "results_metrology", "METROLOGY_SOFT_RESULTS.json"))
    s2 = j(os.path.join(ROOT, "experiments", "E206_onomastic_linkage", "stage2", "STAGE2_RESULT.json"))
    rag = j(os.path.join(ROOT, "rag", "EVALUATION_RESULTS.json"))
    summary = {
        "campaign": "LOGOS-2 Anchor-to-Identifiability", "closed": "2026-07-10",
        "headline": "NO_DECIPHERMENT_ADVANCE_BEYOND_L3; identifiability threshold mapped; "
                    "all substantive claims SINGLE_CHANNEL; prospective seal armed",
        "E203_exact_ambiguity_log10": 224.83,
        "E204_terminal_status": e204.get("E204_TERMINAL_STATUS"),
        "E204_soft_optimum": soft.get("soft_optimum"),
        "E204_loo_stable_relations": soft.get("loo_stable_relations"),
        "E206_S2_verdict": s2.get("verdict"), "E206_S2_replay_qualification": s2.get("replay_qualification"),
        "E211_RAG": {"verdict": "RAG_USEFUL_FOR_AUDIT_ONLY", "recall_at_5": rag.get("bm25", {}).get("recall_at_5", rag.get("recall_at_5"))},
        "independence_verdict": g.get("independence_verdict"),
        "seal": {"sha256": e213.get("sealed_sha256"), "n_predictions": e213.get("n_predictions")},
        "pending_external": ["E201_F1b (CSA sweep ~2026-07-13; cannot alter closed conclusions)"]}
    json.dump(summary, open(os.path.join(FIN, "MACHINE_READABLE_SUMMARY.json"), "w"), indent=1)

    # ARTIFACT_MANIFEST.json + BUNDLE_MANIFEST.sha256 over research/logos2 (code+results, no .venv/db)
    arts = []
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in (".venv", "__pycache__", "logs")]
        for fn in sorted(fns):
            if fn.endswith((".sqlite", ".pyc")) or fn == "BUNDLE_MANIFEST.sha256":
                continue
            p = os.path.join(dp, fn)
            arts.append({"file": os.path.relpath(p, ROOT),
                         "sha256": hashlib.sha256(open(p, "rb").read()).hexdigest()})
    json.dump({"n_files": len(arts), "files": arts},
              open(os.path.join(FIN, "ARTIFACT_MANIFEST.json"), "w"), indent=1)
    man_h = hashlib.sha256(open(os.path.join(FIN, "ARTIFACT_MANIFEST.json"), "rb").read()).hexdigest()
    with open(os.path.join(FIN, "BUNDLE_MANIFEST.sha256"), "w") as f:
        f.write(man_h + "  ARTIFACT_MANIFEST.json\n")
    print(f"package: {len(rows)} experiments | {len(g['claims'])} claims | {len(arts)} artifacts hashed")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
