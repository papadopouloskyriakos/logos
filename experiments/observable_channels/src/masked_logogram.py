#!/usr/bin/env python3
"""Experiment 1: masked logogram recovery under UNSEEN lexical-family (A12) + cross-site conditions.

Hide the logogram in an entry; predict it from the entry's opaque word forms + structure. Held-out by
lexical + morphological family (strict A12 — test word-forms unseen in training). Baselines: frequency +
document-series shortcut (which the transferable model must beat WITHOUT using series). Models: M_struct
(structure only, no sign identity) and M_sign (sub-lexical sign-bag Naive Bayes). Null: shuffle logogram
labels. No semantic labels; no Linear A; deterministic.
"""
import json
import math
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "admin_schema", "src", "corpus"))
import graph_common as gc

SEED = 20260707
LB = os.path.join(gc.MODEL_VISIBLE, "lb_graph.jsonl")
NHS = gc.EXP.replace("admin_schema", "observable_channels")


def build_dataset():
    """One example per entry that contains >=1 word-form and exactly-identifiable logogram(s)."""
    data = []
    for line in open(LB):
        g = json.loads(line)
        ids = {n["id"]: n for n in g["nodes"]}
        ent_words = defaultdict(list); ent_logos = defaultdict(list); ent_has_num = defaultdict(bool)
        for e in g["edges"]:
            if e["type"] != "CONTAINS":
                continue
            d = ids.get(e["dst"], {})
            if d.get("type") == "WORD_FORM" and d["opaque_id"].count("+") >= 0:
                ent_words[e["src"]].append(d)
            elif d.get("type") == "LOGOGRAM":
                ent_logos[e["src"]].append(d["opaque_id"])
            elif d.get("type") == "NUMERAL":
                ent_has_num[e["src"]] = True
        for ent, logos in ent_logos.items():
            words = ent_words.get(ent, [])
            if not words or not logos:
                continue
            target = Counter(logos).most_common(1)[0][0]      # the entry's logogram
            signs = [s for w in words for s in w["opaque_id"].split("+")]
            data.append({"target": target, "site": g["meta"]["site_code"], "series": g["meta"]["document_series"],
                         "n_words": len(words), "mean_len": round(sum(w["opaque_id"].count("+") + 1 for w in words) / len(words), 2),
                         "has_num": ent_has_num.get(ent, False),
                         "word_forms": [w["opaque_id"] for w in words], "signs": signs,
                         "lex_fam": tuple(sorted({w["opaque_id"] for w in words})),
                         "morph_fam": tuple(sorted({"+".join(w["opaque_id"].split("+")[:-1]) or w["opaque_id"] for w in words}))})
    return data


def split_unseen_family(data, test_frac=0.25):
    """Assign whole lexical families to train/test so TEST word-forms are UNSEEN in TRAIN (A12)."""
    fams = sorted({wf for d in data for wf in d["lex_fam"]})
    def h(x):
        return int(gc.content_hash(x + str(SEED)), 16)
    test_fams = {f for f in fams if (h(f) % 1000) < test_frac * 1000}
    train, test = [], []
    for d in data:
        # an example is TEST only if ALL its word-forms are in test families (fully unseen); else TRAIN
        if all(wf in test_fams for wf in d["lex_fam"]):
            test.append(d)
        elif not any(wf in test_fams for wf in d["lex_fam"]):
            train.append(d)
        # mixed -> dropped (leakage guard)
    return train, test


class NB:
    """multinomial NB over a feature bag -> target logogram."""
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
            lp = math.log(self.prior[t])
            tot = sum(self.cond[t].values())
            for f in feats:
                lp += math.log((self.cond[t].get(f, 0) + 0.5) / (tot + 0.5 * V))
            if lp > bs:
                bs, best = lp, t
        return best


def acc(model_pred, test, feat):
    return round(sum(1 for d in test if model_pred(feat(d)) == d["target"]) / len(test), 3)


def min_detectable(p0, n, alpha=0.05, power=0.8):
    from math import comb
    for pa in [x / 100 for x in range(int(p0 * 100) + 1, 101)]:
        cum = 0.0; crit = n + 1
        for c in range(n, -1, -1):
            cum += comb(n, c) * p0 ** c * (1 - p0) ** (n - c)
            if cum > alpha:
                crit = c + 1; break
        pw = sum(comb(n, c) * pa ** c * (1 - pa) ** (n - c) for c in range(crit, n + 1))
        if pw >= power:
            return round(pa, 2)
    return None


def run():
    data = build_dataset()
    train, test = split_unseen_family(data)
    ntest = len(test)
    # baselines
    maj = Counter(d["target"] for d in train).most_common(1)[0][0]
    b_freq = round(sum(1 for d in test if d["target"] == maj) / ntest, 3)
    series_maj = {s: Counter(d["target"] for d in train if d["series"] == s).most_common(1)[0][0]
                  for s in {d["series"] for d in train} if any(d["series"] == s for d in train)}
    b_series = round(sum(1 for d in test if series_maj.get(d["series"]) == d["target"]) / ntest, 3)
    # M_struct (structure only — strict A12, no sign identity)
    def sfeat(d):
        return [f"nw={min(d['n_words'],4)}", f"ml={round(d['mean_len'])}", f"num={d['has_num']}"]
    m_struct = NB().fit([sfeat(d) for d in train], [d["target"] for d in train])
    a_struct = acc(m_struct.predict, test, sfeat)
    # M_sign (sub-lexical sign-bag NB; word-forms unseen but signs recur)
    m_sign = NB().fit([d["signs"] for d in train], [d["target"] for d in train])
    a_sign = acc(m_sign.predict, test, lambda d: d["signs"])
    # NULL: shuffle training targets, refit M_sign
    import random
    rng = random.Random(SEED); ys = [d["target"] for d in train]; rng.shuffle(ys)
    m_null = NB().fit([d["signs"] for d in train], ys)
    a_null = acc(m_null.predict, test, lambda d: d["signs"])
    # cross-site: train KN -> test non-KN
    tr_kn = [d for d in train if d["site"] == "KN"]; te_nonkn = [d for d in test if d["site"] != "KN"]
    xsite = None
    if tr_kn and te_nonkn:
        m_x = NB().fit([d["signs"] for d in tr_kn], [d["target"] for d in tr_kn])
        xb = Counter(d["target"] for d in tr_kn).most_common(1)[0][0]
        xsite = {"n_test_nonKN": len(te_nonkn),
                 "M_sign": acc(m_x.predict, te_nonkn, lambda d: d["signs"]),
                 "baseline": round(sum(1 for d in te_nonkn if d["target"] == xb) / len(te_nonkn), 3)}
    mdi = min_detectable(b_series, ntest)
    out = {"n_examples": len(data), "n_train": len(train), "n_test_unseen_family": ntest,
           "distinct_logograms": len({d["target"] for d in data}),
           "baseline_frequency": b_freq, "baseline_series_shortcut": b_series,
           "M_struct_A12": a_struct, "M_sign_A12": a_sign, "null_label_shuffle": a_null,
           "min_detectable_over_series(n)": mdi, "cross_site_KN_to_nonKN": xsite,
           "sign_model_beats_series": a_sign > b_series, "sign_model_beats_null": a_sign > a_null + 0.03,
           "interpretation": "under UNSEEN-lexical-family (A12): does word context predict the commodity beyond the frequency+series shortcut and beyond a label-shuffle null?"}
    os.makedirs(os.path.join(NHS, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(NHS, "results", "masked_logogram.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    run()
