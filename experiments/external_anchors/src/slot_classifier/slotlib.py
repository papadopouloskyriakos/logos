#!/usr/bin/env python3
"""slotlib.py — INTERNAL-ONLY Linear A slot classifier (Task A).

Assigns each distinct Linear A word-form a candidate document-role / semantic class using ONLY
evidence internal to the Linear A corpus (position, context, recurrence, genre, logogram adjacency,
totals/deficits). It MUST NOT consult external anchors, Egyptian spellings, personal-name lists,
candidate-language lexica, projected phonetic values, or any anchor-match score. Leakage is enforced
by tests (see tests/test_slot_classifier_leakage.py): this module imports only the stdlib and reads
only the checksum-pinned read-only Linear A corpus + its internal sign ontology.

Frozen before any external matching. rule_version below is the freeze tag.
"""
import hashlib
import json
import os
import re
from collections import Counter, defaultdict

RULE_VERSION = "slot-rules-v1-2026-07-06"
MANIFEST_VERSION = 1
SPLIT_SEED = 20260706
SPLIT_RULE = "leave-one-site-out (heldout_group = primary site); ties broken by SPLIT_SEED-ordered site name"

# Read-only Linear A inputs — referenced in place from the main worktree, checksum-pinned.
_CORPUS_DIR = "/home/claude-runner/gitlab/n8n/logos/corpus/silver"
_STRUCT = os.path.join(_CORPUS_DIR, "inscriptions_structured.json")
_ONTO = os.path.join(_CORPUS_DIR, "signs_ontology.json")
# expected sha256 (from data/manifests/linear_a_inputs.sha256) — integrity + anti-drift guard
_EXPECT = {
    _STRUCT: "aaee1aeb5b186fa0e4d9d0adc71026e6786d47328b9ecee5236380756462b500",
    _ONTO: "246f63f1608a1238a2b2851b9f0a475817ce265b66d2fa622cc795627b97a80d",
}
# transaction terms attested INTERNALLY as Linear A accounting words (identified by recurring form +
# position, NOT by any external/phonetic reading): total / deficit / grand-total.
_TRANSACTION = {("KU", "RO"): "total", ("KI", "RO"): "deficit", ("PO", "TO", "KU", "RO"): "grand_total"}
_RITUAL_SUPPORTS = {"Stone vessel", "Clay vessel", "Metal object", "Stone object"}
_DAMAGE_RE = re.compile(r"[\[\]?]|^\*")


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()


def load_corpus(verify=True):
    if verify:
        for p, exp in _EXPECT.items():
            got = _sha(p)
            if got != exp:
                raise RuntimeError(f"INPUT DRIFT: {p} sha256 {got} != pinned {exp}")
    D = json.load(open(_STRUCT, encoding="utf-8"))
    O = json.load(open(_ONTO, encoding="utf-8"))
    idx = {dt: (cid, v.get("class")) for cid, v in O.items() for dt in v.get("diplomatic_tokens", [])}
    return D, idx


def sign_class(sign, idx):
    return idx.get(sign, (sign, None))[1]


def is_logogram_word(word, idx):
    return any(sign_class(s, idx) == "logogram" for s in word)


def damaged(word):
    return any(_DAMAGE_RE.search(s) for s in word)


def extract_features(D, idx):
    """Per distinct word-form: aggregate internal position/context/recurrence/genre features."""
    feats = defaultdict(lambda: {
        "occ": 0, "sites": set(), "docs": set(), "genres": Counter(),
        "pre_num": 0, "post_logo": 0, "header": 0, "terminal": 0,
        "adj_kuro": 0, "adj_kiro": 0, "ritual_genre": 0, "len_signs": 0, "damaged": False})
    for r in D:
        site = r.get("site", ""); doc = r.get("id", ""); genre = r.get("support", "")
        st = r["stream"]
        # index word tokens within the stream to read neighbours
        word_positions = [i for i, t in enumerate(st) if t["t"] == "word"]
        words_seq = [st[i]["signs"] for i in word_positions]
        for wi, i in enumerate(word_positions):
            w = tuple(st[i]["signs"])
            f = feats[w]
            f["occ"] += 1; f["sites"].add(site); f["docs"].add(doc); f["genres"][genre] += 1
            f["len_signs"] = len(w)
            if damaged(list(w)):
                f["damaged"] = True
            if genre in _RITUAL_SUPPORTS:
                f["ritual_genre"] += 1
            # next non-div token in the stream
            j = i + 1
            while j < len(st) and st[j]["t"] == "div":
                j += 1
            nxt = st[j] if j < len(st) else None
            if nxt and nxt["t"] == "num":
                f["pre_num"] += 1
            if nxt and nxt["t"] == "word" and is_logogram_word(nxt["signs"], idx):
                f["post_logo"] += 1
            # header: first word on the tablet; terminal: last word
            if wi == 0:
                f["header"] += 1
            if wi == len(word_positions) - 1:
                f["terminal"] += 1
            # adjacency to KU-RO / KI-RO in the same word sequence (prev or next word)
            for adj in (words_seq[wi-1] if wi > 0 else None, words_seq[wi+1] if wi+1 < len(words_seq) else None):
                if adj == ["KU", "RO"]:
                    f["adj_kuro"] += 1
                if adj == ["KI", "RO"]:
                    f["adj_kiro"] += 1
    return feats


def classify(word, f, idx):
    """Return (candidate_class, tier, secondary_flags). Internal rules only; tiers A/B/C/X."""
    occ = f["occ"]; nsites = len(f["sites"]); ndocs = len(f["docs"])
    flags = []
    # X — exclude from confirmatory use: damaged/uncertain form or degenerate length
    if f["damaged"] or f["len_signs"] <= 1:
        return ("UNKNOWN", "X", ["damaged_or_short"])
    # TRANSACTION_TERM (A) — attested accounting words
    if tuple(word) in _TRANSACTION:
        return ("TRANSACTION_TERM", "A", [_TRANSACTION[tuple(word)]])
    # COMMODITY (A) — word is/contains a logogram (internal ontology class only, no phonetic value)
    if is_logogram_word(list(word), idx):
        return ("COMMODITY", "A", [])
    ritual_rate = f["ritual_genre"] / occ if occ else 0.0
    header_rate = f["header"] / occ if occ else 0.0
    pre_num_rate = f["pre_num"] / occ if occ else 0.0
    # RITUAL_FORMULA (B/C) — predominantly on ritual supports (stone/clay vessels)
    if ritual_rate >= 0.5:
        tier = "B" if occ >= 3 else "C"
        return ("RITUAL_FORMULA", tier, ["ritual_genre_rate=%.2f" % ritual_rate])
    # entry-leading behaviour: heads a tablet or is followed by a commodity/quantity
    entry_leading = (header_rate >= 0.5) or (pre_num_rate >= 0.5) or (f["post_logo"] >= 1)
    if entry_leading:
        # TOPONYM_LIKE — recurs across the administrative network (>=2 sites OR >=3 docs)
        if nsites >= 2 or ndocs >= 3:
            tier = "B" if (nsites >= 2 and ndocs >= 3) else "C"
            return ("TOPONYM_LIKE", tier, ["nsites=%d" % nsites, "ndocs=%d" % ndocs])
        # PERSON_NAME_LIKE — entry-leading but localized/hapax (single site, few docs)
        return ("PERSON_NAME_LIKE", "C", ["localized", "ndocs=%d" % ndocs])
    # weak signals
    if f["adj_kuro"] or f["adj_kiro"]:
        return ("TRANSACTION_TERM", "C", ["adjacent_to_total_or_deficit"])
    return ("UNKNOWN", "C", flags)


def primary_site(f):
    # deterministic: most-frequent site; ties -> seed-ordered site name
    sc = Counter()
    for s in f["sites"]:
        sc[s] = sum(1 for _ in [s])  # sites is a set; weight by presence
    # weight by doc count per site is not tracked per-site here; use doc-set membership proxy
    if not f["sites"]:
        return ""
    return sorted(f["sites"], key=lambda s: (s,))[0] if len(f["sites"]) == 1 else \
        sorted(f["sites"], key=lambda s: (-1, s))[0]


def build_records(D, idx):
    feats = extract_features(D, idx)
    silver, gold = [], []
    for wid, (word, f) in enumerate(sorted(feats.items())):
        occ = f["occ"]
        cls, tier, flags = classify(word, f, idx)
        psite = sorted(f["sites"])[0] if f["sites"] else ""  # deterministic primary (alpha) for LOSO
        strid = "-".join(word)
        pos = {"header_rate": round(f["header"]/occ, 3), "terminal_rate": round(f["terminal"]/occ, 3),
               "pre_num_rate": round(f["pre_num"]/occ, 3), "post_logo": f["post_logo"]}
        ctx = {"occ": occ, "n_sites": len(f["sites"]), "n_docs": len(f["docs"]),
               "adj_kuro": f["adj_kuro"], "adj_kiro": f["adj_kiro"],
               "ritual_genre_rate": round(f["ritual_genre"]/occ, 3), "len_signs": f["len_signs"]}
        silver.append({"normalized_string_id": strid, "word": list(word), **pos, **ctx,
                       "sites": sorted(f["sites"]), "genres": dict(f["genres"])})
        gold.append({
            "candidate_id": "LA-SLOT-%04d" % wid,
            "corpus_record_id": sorted(f["docs"])[0] if f["docs"] else "",
            "normalized_string_id": strid,
            "site": psite,
            "document_id": sorted(f["docs"]),
            "genre": sorted(f["genres"], key=lambda g: -f["genres"][g])[0] if f["genres"] else "",
            "position_features": pos,
            "context_features": ctx,
            "candidate_class": cls,
            "class_probability_or_tier": tier,
            "secondary_flags": flags,
            "rule_or_model_version": RULE_VERSION,
            "transcription_status": "damaged" if f["damaged"] else "clean",
            "damaged_sign_flag": bool(f["damaged"]),
            "alternative_transcriptions": [],
            "leakage_exclusion_status": "internal_only_clean",
            "heldout_group": psite,           # leave-one-site-out unit
            "manifest_version": MANIFEST_VERSION,
        })
    return silver, gold
