#!/usr/bin/env python3
"""corpus_io_structured.py — re-ingest the Linear A corpus PRESERVING word boundaries + accounting structure.

The flat `corpus_io.py` silver flattens `transliteratedWords` into one `signs` array, LOSING the scribe's
word divisions — which are the held-out SEGMENTATION GROUND TRUTH that Direction A (morphology induction)
needs, and losing the word→count accounting structure Direction D (metrology) needs. This re-ingest keeps both.

Per inscription it emits, from the bronze `transliteratedWords` ordered stream:
  - words   : [[sign,...], ...]              — the scribe's word divisions (segmentation ground truth)
  - stream  : [{t, ...}, ...]                — the full ordered structure, tokens typed as
              word {signs:[...]} | div (word-divider 𐄁) | nl (line break) | num {v:int} | other {raw}
  - signs   : flattened (kept for backward compatibility with existing code)

Direction A consumes `words` (boundary recovery vs the model's predicted boundaries). Direction D consumes
`stream` (a `word` immediately followed by a `num` is a line item; a KU-RO/KI-RO word + its num is a
total/deficit — validate that line items balance the total). The scribe's word divisions are a genuine
held-out signal, NOT a logos hypothesis.

LICENSING: bronze derives from copyrighted GORILA + lineara.xyz — bronze + silver are GITIGNORED; only this
normalizer CODE is public (invariant 10/12).

    python3 scripts/corpus_io_structured.py [path/to/inscriptions.json]
"""
import json
import os
import re
import sys

BRONZE = os.environ.get("LOGOS_BRONZE", "/tmp/lineara/items_analysis/inscriptions.json")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SILVER = os.path.join(ROOT, "corpus", "silver", "inscriptions_structured.json")

DIVIDERS = {"\U000100c1", "\U00010101"}     # 𐄁 and the Aegean check/separator glyph variants
_NUM = re.compile(r"^\d+$")


def is_word(tok):
    return bool(tok and re.search(r"[A-Za-z]", tok))


def split_signs(word):
    return [p for p in word.split("-") if p]


def classify(tok):
    """Type one bronze transliteratedWords token."""
    if tok == "\n":
        return {"t": "nl"}
    if tok in DIVIDERS:
        return {"t": "div"}
    if _NUM.match(tok.strip()):
        return {"t": "num", "v": int(tok.strip())}
    if is_word(tok):
        return {"t": "word", "signs": split_signs(tok)}
    return {"t": "other", "raw": tok}


def normalize(raw_path, out_path):
    data = json.load(open(raw_path))
    out = []
    for entry in data:
        if not (isinstance(entry, list) and len(entry) >= 2 and isinstance(entry[1], dict)):
            continue
        iid, d = entry[0], entry[1]
        stream = [classify(t) for t in (d.get("transliteratedWords") or []) if isinstance(t, str)]
        words = [s["signs"] for s in stream if s["t"] == "word"]
        if not words:
            continue
        signs = [sg for w in words for sg in w]
        out.append({
            "id": iid, "site": d.get("site", ""), "context": d.get("context", ""),
            "support": d.get("support", ""),
            "words": words, "stream": stream, "signs": signs,
        })
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    json.dump(out, open(out_path, "w"), ensure_ascii=False, indent=1)
    return out


def line_items(rec):
    """Direction-D helper: (word_signs, count) pairs where a word is immediately followed by a numeral,
    plus the KU-RO 'total' and KI-RO 'deficit' line items separated out for balance-checking."""
    items, total, deficit = [], None, None
    st = rec["stream"]
    for i, tok in enumerate(st):
        if tok["t"] == "word":
            # find the next non-nl token; if it's a num, this is a counted line item
            j = i + 1
            while j < len(st) and st[j]["t"] == "nl":
                j += 1
            if j < len(st) and st[j]["t"] == "num":
                w = "-".join(tok["signs"])
                if w == "KU-RO":
                    total = st[j]["v"]
                elif w == "KI-RO":
                    deficit = st[j]["v"]
                else:
                    items.append((w, st[j]["v"]))
    return items, total, deficit


if __name__ == "__main__":
    raw = sys.argv[1] if len(sys.argv) > 1 else BRONZE
    if not os.path.exists(raw):
        sys.exit(f"bronze not found at {raw}")
    docs = normalize(raw, SILVER)
    nwords = sum(len(d["words"]) for d in docs)
    print(f"re-ingested {len(docs)} inscriptions, {nwords} words "
          f"(mean {nwords/len(docs):.1f} words/inscription) -> {SILVER}")
    # Direction-D sanity check: on HT tablets with a KU-RO total, do the line items balance it?
    bal = imbal = no_total = 0
    examples = []
    for d in docs:
        if not str(d["id"]).startswith("HT"):
            continue
        items, total, deficit = line_items(d)
        if total is None:
            no_total += 1
            continue
        s = sum(v for _, v in items)
        if s == total:
            bal += 1
        else:
            imbal += 1
            if len(examples) < 5:
                examples.append((d["id"], s, total, len(items)))
    print(f"Direction-D balance check on HT tablets with a KU-RO total: "
          f"{bal} balance exactly, {imbal} do not, {no_total} HT tablets have no KU-RO total.")
    for iid, s, t, n in examples:
        print(f"   {iid}: sum(line items)={s} vs KU-RO total={t} ({n} items)")
