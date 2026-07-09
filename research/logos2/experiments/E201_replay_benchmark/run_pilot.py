"""E201 pilot P1 (exploratory) — prereg 46d8da5. Cells: UGA evidence ladder, CSYL small ladder,
control battery (5 reps x 6 controls), process-replay ENCODING (no scoring). Checkpointed to
results/. No Linear A data is loaded."""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


def ck(name, obj):
    json.dump(obj, open(os.path.join(OUT, name + ".json"), "w"), indent=1, default=str)
    print(f"[cell done] {name}", flush=True)


def ladder(dataset, n, tag):
    cw, pw, pairs = harness.load_cog(dataset)
    cw, pw, pairs = harness.subsample(cw, pw, pairs, n, harness.seed_for(tag, "sub"))
    all_pairs = list(pairs.items())
    rungs = []

    def rung(name, **kw):
        r = harness.run_cell(cw, pw, pairs, seed=harness.seed_for(tag, name), **kw)
        r["rung"] = name
        rungs.append(r)
        print(f"  {tag}/{name}: cognate_acc={r.get('cognate_accuracy'):.3f} "
              f"(chance {r.get('chance_cognate_accuracy'):.4f}) "
              f"ambiguous={r['ambiguous_chars']}/{r['n_chars']}", flush=True)

    rung("R1_distribution_only")
    rungs.append({"rung": "R2_formula_boundaries", "status": "NOT_APPLICABLE",
                  "note": "cognate pair lists carry no document structure (prereg disclosure)"})
    rungs.append({"rung": "R3_semantic_classes", "status": "NOT_APPLICABLE",
                  "note": "no semantic labels in .cog data (prereg disclosure)"})
    rung("R4_one_name", anchors=all_pairs[:1])
    rung("R5_five_names", anchors=all_pairs[:5])
    rungs.append({"rung": "R6_related_corpus", "status": "INHERENT_BASELINE",
                  "note": "the plain column IS the related-language lexicon; identical to R1"})
    rung("R7_bilingual_10pct", bilingual_frac=0.10)
    return {"dataset": dataset, "n": n, "rungs": rungs,
            "leak_check": harness.leak_detector(cw, pw)}


def control_battery(n_reps=5):
    cw, pw, pairs = harness.load_cog("uga-heb.no_speNL.cog")
    cw, pw, pairs = harness.subsample(cw, pw, pairs, 300, harness.seed_for("CTRL", "sub"))
    all_pairs = list(pairs.items())
    _, gpw, _ = harness.load_cog("csyl-greek.cog")   # unrelated target lexicon
    rows, n_grad = [], 0
    for rep in range(n_reps):
        s = lambda name: harness.seed_for("CTRL", name, rep)
        cells = {}
        # 1 shuffled inventory (within-word char shuffle destroys structure)
        cwx = harness.control_shuffled_inventory(cw, s("shuf"))
        cells["shuffled_inventory"] = harness.run_cell(cwx, pw, pairs, seed=s("shuf2"))
        # 2 unrelated target
        cells["unrelated_target"] = harness.run_cell(cw, gpw[:300], pairs, seed=s("unrel"))
        # 3 synthetic isolate target (freq/length-matched nonsense lexicon)
        synth = harness.control_synthetic_isolate(pw, s("iso"))
        cells["synthetic_isolate"] = harness.run_cell(cw, synth, pairs, seed=s("iso2"))
        # 4/5 corrupted anchors at f=0.1/0.3 (real data; anchors partly wrong)
        for f in (0.1, 0.3):
            bad = harness.control_corrupt_anchors(all_pairs[:10], pw, f, s(f"corr{f}"))
            cells[f"corrupted_anchors_{f}"] = harness.run_cell(
                cw, pw, pairs, anchors=bad, seed=s(f"corr2{f}"))
        # 6 leaked names: inject plain words as cipher words; detector must fire
        leaked_cw = cw[:270] + pw[:30]
        det = harness.leak_detector(leaked_cw, pw)
        cells["leaked_names_detector"] = {"detector": det, "must_fire": True,
                                          "pass": det["fired"]}
        for name, r in cells.items():
            if name == "leaked_names_detector":
                continue
            g = harness.graduates(r)
            # corrupted-anchor cells run on REAL data: graduation there is legitimate;
            # the false-graduation count covers structure-destroyed/unrelated/synthetic cells
            counted = name in ("shuffled_inventory", "unrelated_target", "synthetic_isolate")
            if g and counted:
                n_grad += 1
            rows.append({"rep": rep, "control": name, "counted_for_false_grad": counted,
                         "graduated": g,
                         "cognate_accuracy": r.get("cognate_accuracy"),
                         "chance": r.get("chance_cognate_accuracy")})
        rows.append({"rep": rep, "control": "leaked_names_detector",
                     "fired": cells["leaked_names_detector"]["detector"]["fired"],
                     "pass": cells["leaked_names_detector"]["pass"]})
    return {"cell": "CONTROL_battery", "rows": rows,
            "false_graduations": n_grad,
            "n_counted_cells": sum(1 for r in rows if r.get("counted_for_false_grad")),
            "detector_fired_all": all(r.get("fired", True) for r in rows
                                      if r.get("control") == "leaked_names_detector")}


def process_replay_encoding():
    """ENCODING ONLY (prereg): evidence-level configs; scoring deferred to F1."""
    enc = {
      "cell": "PROCESS_REPLAY_encoding",
      "cases": {
        "ventris_1952_analogue": {
          "dataset": "linear_b-greek.cog + linear_b-greek.names.cog",
          "evidence": {"anchors": "5 toponym name pairs (SOFT)", "distribution": True,
                        "related_corpus": True, "bilingual": False},
          "gate_question": "does the L4-L6 graduation rule graduate this configuration?",
          "approximation": "cognate lists approximate the tablet corpus; grid/triplet structure not represented - DISCLOSED"},
        "ugaritic_analogue": {
          "dataset": "uga-heb.no_speNL.cog",
          "evidence": {"anchors": "axe-head-style few names", "related_corpus": True},
          "gate_question": "same"},
        "failure_case_random_map": {
          "dataset": "uga-heb.no_speNL.cog vs synthetic isolate target",
          "evidence": {"anchors": "10 fabricated name pairs"},
          "gate_question": "gate must REFUSE"},
        "failure_case_wrong_language": {
          "dataset": "uga source vs greek target",
          "evidence": {"anchors": "5 coincidental resemblances (best-of search)"},
          "gate_question": "gate must REFUSE; multiplicity charged for the search"}
      },
      "scoring": "DEFERRED to F1 (after CSA-sweep at-scale cells land)"}
    return enc


def main():
    t0 = time.time()
    uga = ladder("uga-heb.no_speNL.cog", 300, "UGA"); ck("UGA_ladder", uga)
    csy = ladder("csyl-greek.cog", 200, "CSYL"); ck("CSYL_ladder", csy)
    ctl = control_battery(); ck("CONTROL_battery", ctl)
    enc = process_replay_encoding(); ck("PROCESS_REPLAY_encoding", enc)
    ok_controls = (ctl["false_graduations"] == 0) and ctl["detector_fired_all"]
    summary = {
      "pilot": "P1", "exploratory": True,
      "harness_verdict": "HARNESS_OPERATIONAL" if ok_controls else "CONTROL_FAILURE",
      "false_graduations": f"{ctl['false_graduations']}/{ctl['n_counted_cells']}",
      "runtime_s": round(time.time() - t0, 1),
      "promotion_decisions": "NONE at pilot (promotion gate is a confirmatory F1 decision)",
    }
    ck("P1_summary", summary)
    print("VERDICT:", summary["harness_verdict"], "| false grads:", summary["false_graduations"])
    return 0 if ok_controls else 1


if __name__ == "__main__":
    raise SystemExit(main())
