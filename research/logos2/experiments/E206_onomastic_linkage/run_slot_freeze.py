"""E206 Stage-1 slot freeze — internal structure ONLY (prereg in this dir; no external name
data of any kind is loaded). Emits SLOT_FREEZE.json + SLOT_FREEZE.sha256."""
import hashlib
import json
import os
from collections import Counter, defaultdict

SILVER = "corpus/silver/inscriptions_structured.json"
HERE = os.path.dirname(os.path.abspath(__file__))

# contamination references (published/prior-exposed sequences; frozen in prereg)
CONTAM = {
    ("PA", "I", "TO"), ("SE", "TO", "I", "JA"), ("SU", "KI", "RI", "TA"),
    ("DI", "KI", "TE"), ("I", "DA"), ("KU", "RO"), ("PO", "TO", "KU", "RO"),
}
CONTAM_PREFIX = [("A", "TA", "I")]  # libation formula head family (A-TA-I-*301-WA-JA...)


def main():
    d = json.load(open(SILVER))
    sha = hashlib.sha256(open(SILVER, "rb").read()).hexdigest()

    tok_count = Counter()
    sites_of = defaultdict(set)
    docs_of = defaultdict(set)
    s1, s2, s3 = set(), set(), set()

    # S3 derivation: most frequent document-initial word on non-Tablet, multi-site documents
    init_counter = Counter()
    for ins in d:
        if ins.get("support") == "Tablet":
            continue
        ws = ins.get("words") or []
        if ws:
            init_counter[tuple(ws[0])] += 1
    formula_head = None
    for w, c in init_counter.most_common():
        hit_sites = {i["site"] for i in d if (i.get("words") or [None])[0] == list(w)}
        if c >= 3 and len(hit_sites) >= 2:
            formula_head = w
            break

    for ins in d:
        st = ins.get("stream", [])
        words_seq = []
        for i, tok in enumerate(st):
            if tok.get("t") != "word":
                continue
            w = tuple(tok.get("signs", []))
            if len(w) < 2:
                continue
            words_seq.append(w)
            tok_count[w] += 1
            sites_of[w].add(ins["site"])
            docs_of[w].add(ins["id"])
            nxt = st[i + 1]["t"] if i + 1 < len(st) else None
            if nxt == "num":
                s1.add(w)                                 # S1 ledger-entry head
            window = [t.get("signs") for t in st[max(0, i - 2):i + 3]
                      if t.get("t") == "word"]
            if ["KU", "RO"] in window and w != ("KU", "RO"):
                s2.add(w)                                 # S2 totals-adjacent
        if formula_head and formula_head in words_seq:
            j = words_seq.index(formula_head)
            if j + 1 < len(words_seq):
                s3.add(words_seq[j + 1])                  # S3 formula slot-2

    s4 = {w for w, ss in sites_of.items() if len(w) >= 3 and len(ss) >= 2} - s3
    s5 = {w for w, ss in sites_of.items()
          if len(w) >= 3 and len(ss) == 1 and tok_count[w] >= 3}
    s1 = {w for w in s1 if tok_count[w] >= 2}

    def contaminated(w):
        if w in CONTAM:
            return True
        return any(w[:len(p)] == p for p in CONTAM_PREFIX)

    classes = {"S1_entry_head": s1, "S2_totals_adjacent": s2,
               "S3_formula_slot2": s3, "S4_cross_site_recurrent": s4,
               "S5_site_local_recurrent": s5}
    cands = {}
    for cls, ws in classes.items():
        for w in ws:
            c = cands.setdefault("-".join(w), {
                "signs": list(w), "classes": [], "tokens": tok_count[w],
                "sites": sorted(sites_of[w]), "n_docs": len(docs_of[w]),
                "docs": sorted(docs_of[w])[:20],
                "contaminated_prior_exposure": contaminated(w)})
            c["classes"].append(cls)

    out = {
        "experiment": "E206_stage1_slot_freeze", "frozen": "2026-07-10",
        "silver_sha256": sha,
        "derived_formula_head_internal": list(formula_head) if formula_head else None,
        "criteria": {"S1": "word len>=2 immediately preceding a numeral, >=2 tokens",
                     "S2": "word within +-2 word-positions of KU-RO",
                     "S3": "word immediately after the internally-derived formula head on its documents",
                     "S4": "word len>=3 attested at >=2 sites, excl. S3",
                     "S5": "word len>=3, single-site, >=3 tokens"},
        "class_sizes": {k: len(v) for k, v in classes.items()},
        "n_candidates_union": len(cands),
        "n_contaminated": sum(1 for c in cands.values()
                              if c["contaminated_prior_exposure"]),
        "candidates": cands,
        "external_data_loaded": False,
        "note": "SLOT candidates are L2 structural objects; no name/place/person wording "
                "until Stage-2 evidence under its own prereg.",
    }
    p = os.path.join(HERE, "SLOT_FREEZE.json")
    json.dump(out, open(p, "w"), indent=1, ensure_ascii=False)
    with open(os.path.join(HERE, "SLOT_FREEZE.sha256"), "w") as f:
        f.write(hashlib.sha256(open(p, "rb").read()).hexdigest() + "  SLOT_FREEZE.json\n")
    print("formula head (internal):", formula_head)
    print("class sizes:", out["class_sizes"], "| union:", out["n_candidates_union"],
          "| contaminated:", out["n_contaminated"])


if __name__ == "__main__":
    main()
