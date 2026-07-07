#!/usr/bin/env python3
"""Experiment 2: masked quantity-channel recovery (accounting channel) under UNSEEN lexical-family (A12)
+ cross-site conditions.

Two observable targets, neither of which lets the masked numeral into the predictor:
  (a) QUANTITY PRESENCE — does this entry carry a counted quantity? (balanced ~0.45)
  (b) MAGNITUDE BUCKET — among quantity-bearing entries, is the count small/medium/large (log10 of value)?

Question: does opaque WORD context predict whether/how-much a line is counted, beyond a layout-only baseline,
a document-series shortcut, and a label-shuffle null — under unseen lexical families and across sites?
No semantic labels; no Linear A; deterministic. The numeral value never enters any predictor for target (a);
for (b) it is the (masked) TARGET, predicted from word context only.
"""
import json
import math
import os
import random
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "admin_schema", "src", "corpus"))
import graph_common as gc

SEED = 20260707
LB = os.path.join(gc.MODEL_VISIBLE, "lb_graph.jsonl")
NHS = gc.EXP.replace("admin_schema", "observable_channels")


def build_dataset():
    """One example per ENTRY that has >=1 word-form. Numeral value captured only as the (maskable) target."""
    data = []
    for line in open(LB):
        g = json.loads(line)
        ids = {n["id"]: n for n in g["nodes"]}
        ent_words = defaultdict(list); ent_num_vals = defaultdict(list); ent_has_logo = defaultdict(bool)
        ent_order = {}
        for e in g["edges"]:
            if e["type"] != "CONTAINS":
                continue
            d = ids.get(e["dst"], {})
            if d.get("type") == "WORD_FORM":
                ent_words[e["src"]].append(d)
                ent_order.setdefault(e["src"], len(ent_order))
            elif d.get("type") == "NUMERAL":
                ent_num_vals[e["src"]].append(d.get("value"))
            elif d.get("type") == "LOGOGRAM":
                ent_has_logo[e["src"]] = True
        n_ent = max(len(ent_order), 1)
        for ent, words in ent_words.items():
            if not words:
                continue
            vals = [v for v in ent_num_vals.get(ent, []) if isinstance(v, (int, float)) and v > 0]
            has_num = len(ent_num_vals.get(ent, [])) > 0
            signs = [s for w in words for s in w["opaque_id"].split("+")]
            pos = ent_order[ent] / n_ent                       # normalized position within document
            data.append({"site": g["meta"]["site_code"], "series": g["meta"]["document_series"],
                         "has_num": has_num, "max_val": max(vals) if vals else None,
                         "has_logo": ent_has_logo.get(ent, False),
                         "n_words": len(words), "mean_len": round(sum(w["opaque_id"].count("+") + 1 for w in words) / len(words), 2),
                         "pos": round(pos, 3), "signs": signs,
                         "lex_fam": tuple(sorted({w["opaque_id"] for w in words}))})
    return data


def split_unseen_family(data, test_frac=0.25):
    fams = sorted({wf for d in data for wf in d["lex_fam"]})
    def h(x):
        return int(gc.content_hash(x + str(SEED)), 16)
    test_fams = {f for f in fams if (h(f) % 1000) < test_frac * 1000}
    train, test = [], []
    for d in data:
        if all(wf in test_fams for wf in d["lex_fam"]):
            test.append(d)
        elif not any(wf in test_fams for wf in d["lex_fam"]):
            train.append(d)
    return train, test


class NB:
    def __init__(self):
        self.prior = Counter(); self.cond = defaultdict(Counter); self.vocab = set()

    def fit(self, X, y):
        for feats, t in zip(X, y):
            self.prior[t] += 1
            for f in feats:
                self.cond[t][f] += 1; self.vocab.add(f)
        return self

    def predict(self, feats):
        best, bs = None, -1e18
        V = max(len(self.vocab), 1)
        for t in self.prior:
            lp = math.log(self.prior[t]); tot = sum(self.cond[t].values())
            for f in feats:
                lp += math.log((self.cond[t].get(f, 0) + 0.5) / (tot + 0.5 * V))
            if lp > bs:
                bs, best = lp, t
        return best


def acc(pred, test, feat, key):
    return round(sum(1 for d in test if pred(feat(d)) == d[key]) / len(test), 3)


def layout_feat(d):
    return [f"nw={min(d['n_words'],4)}", f"ml={round(d['mean_len'])}", f"pos={round(d['pos']*3)}"]


def bucket(v):
    return "S" if v < 10 else ("M" if v < 100 else "L")


def target_block(train, test, key, feat_layout, feat_sign):
    """baselines + M_struct(layout) + M_sign(word context) + null, for one classification target."""
    maj = Counter(d[key] for d in train).most_common(1)[0][0]
    b_maj = round(sum(1 for d in test if d[key] == maj) / len(test), 3)
    series_maj = {s: Counter(d[key] for d in train if d["series"] == s).most_common(1)[0][0]
                  for s in {d["series"] for d in train}}
    b_series = round(sum(1 for d in test if series_maj.get(d["series"], maj) == d[key]) / len(test), 3)
    m_struct = NB().fit([feat_layout(d) for d in train], [d[key] for d in train])
    a_struct = acc(m_struct.predict, test, feat_layout, key)
    m_sign = NB().fit([feat_sign(d) for d in train], [d[key] for d in train])
    a_sign = acc(m_sign.predict, test, feat_sign, key)
    rng = random.Random(SEED); ys = [d[key] for d in train]; rng.shuffle(ys)
    a_null = acc(NB().fit([feat_sign(d) for d in train], ys).predict, test, feat_sign, key)
    # cross-site KN -> non-KN
    tr_kn = [d for d in train if d["site"] == "KN"]; te_x = [d for d in test if d["site"] != "KN"]
    xsite = None
    if tr_kn and te_x:
        mx = NB().fit([feat_sign(d) for d in tr_kn], [d[key] for d in tr_kn])
        xmaj = Counter(d[key] for d in tr_kn).most_common(1)[0][0]
        xsite = {"n_test_nonKN": len(te_x), "M_sign": acc(mx.predict, te_x, feat_sign, key),
                 "baseline": round(sum(1 for d in te_x if d[key] == xmaj) / len(te_x), 3)}
    return {"n_test": len(test), "baseline_majority": b_maj, "baseline_series_shortcut": b_series,
            "M_struct_layout_A12": a_struct, "M_sign_wordctx_A12": a_sign, "null_label_shuffle": a_null,
            "sign_beats_best_baseline": a_sign > max(b_maj, b_series) + 0.02,
            "sign_beats_null": a_sign > a_null + 0.03, "cross_site_KN_to_nonKN": xsite}


def run():
    data = build_dataset()
    train, test = split_unseen_family(data)
    # target (a): quantity presence (balanced binary)
    pres = target_block(train, test, "has_num", layout_feat, lambda d: d["signs"])
    # target (b): magnitude bucket among quantity-bearing entries (value is the MASKED target)
    tr_v = [dict(d, mag=bucket(d["max_val"])) for d in train if d["max_val"]]
    te_v = [dict(d, mag=bucket(d["max_val"])) for d in test if d["max_val"]]
    mag = target_block(tr_v, te_v, "mag", layout_feat, lambda d: d["signs"]) if te_v else None
    out = {"n_examples": len(data), "n_train": len(train), "n_test_unseen_family": len(test),
           "quantity_presence": pres, "magnitude_bucket_SML": mag,
           "note": "numeral value never enters the presence predictor; for magnitude it is the masked target predicted from word context only.",
           "interpretation": "under A12 unseen-family: does opaque WORD context predict the accounting quantity channel beyond layout, the series shortcut, and a label-shuffle null, and does it transfer cross-site?"}
    os.makedirs(os.path.join(NHS, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(NHS, "results", "masked_quantity.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    run()
