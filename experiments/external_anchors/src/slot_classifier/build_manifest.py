#!/usr/bin/env python3
"""Generate the internal-only slot feature table + gold candidate manifest. Writes to data/silver
and data/gold; records the manifest sha256. Refuses to run if any anchor-matching module exists that
could have leaked (defensive: the manifest must be built BEFORE matching)."""
import hashlib, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))            # experiments/external_anchors
sys.path.insert(0, HERE)
import slotlib

def sha(p):
    h = hashlib.sha256(); h.update(open(p, "rb").read()); return h.hexdigest()

def main():
    # leakage guard: no matching module may exist yet
    for bad in ("src/anchor_matching", "src/matcher"):
        if os.path.isdir(os.path.join(ROOT, bad)):
            raise SystemExit("REFUSE: %s exists — slot manifest must be frozen BEFORE matching." % bad)
    D, idx = slotlib.load_corpus(verify=True)
    silver, gold = slotlib.build_records(D, idx)
    sp = os.path.join(ROOT, "data/silver/linear_a_slot_features.jsonl")
    gp = os.path.join(ROOT, "data/gold/slot_candidate_manifest.jsonl")
    os.makedirs(os.path.dirname(sp), exist_ok=True); os.makedirs(os.path.dirname(gp), exist_ok=True)
    with open(sp, "w", encoding="utf-8") as f:
        for r in silver: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(gp, "w", encoding="utf-8") as f:
        for r in gold: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    mp = os.path.join(ROOT, "data/manifests/slot_candidate_manifest.sha256")
    open(mp, "w").write(f"{sha(gp)}  data/gold/slot_candidate_manifest.jsonl\n"
                        f"{sha(sp)}  data/silver/linear_a_slot_features.jsonl\n"
                        f"rule_version={slotlib.RULE_VERSION} split={slotlib.SPLIT_RULE} seed={slotlib.SPLIT_SEED}\n")
    # summary
    import collections
    by = collections.Counter((r["candidate_class"], r["class_probability_or_tier"]) for r in gold)
    print("candidates:", len(gold))
    for (c, t), n in sorted(by.items()):
        print(f"  {c:20} tier {t}: {n}")
    print("gold sha256:", sha(gp)[:24])

if __name__ == "__main__":
    main()
