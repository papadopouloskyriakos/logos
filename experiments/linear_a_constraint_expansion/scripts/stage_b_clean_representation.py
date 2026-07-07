#!/usr/bin/env python3
"""Stage B — cleaned, notation-typed corpus representation (Constitution v2.2 Art. VIII/IX/XVII).

Implements the load-bearing repairs the Stage B forensics surfaced, WITHOUT mutating the read-only silver
corpus (writes a derived view to data/):
  1. normalize the ASCII/Unicode-subscript sign-key mismatch (PA3<->PA_3 etc.);
  2. separate the 222 commodity-LOGOGRAM tokens misrouted into the phonetic WORD channel -> a clean phonetic
     wordform inventory (feeds Stage D morphology/segmentation on real syllabic material only);
  3. type each word token: PHONETIC / LOGOGRAM / MIXED (via signs_ontology class);
  4. recompute the corrected effective denominators (physical objects; usable >=2-sign lexical units).
Every reduction is answer-neutral (ontology class / catalog-ID grouping), reversible, and file-cited.
Reads corpus read-only from the main worktree. Deterministic.
"""
import json
import os
import re
import unicodedata
from collections import Counter, defaultdict

MAIN = "/home/claude-runner/gitlab/n8n/logos"
ONTO = json.load(open(os.path.join(MAIN, "corpus/silver/signs_ontology.json")))
INSC = json.load(open(os.path.join(MAIN, "corpus/silver/inscriptions_structured.json")))
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

SUB = {"₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4", "₅": "5", "₆": "6", "₇": "7", "₈": "8", "₉": "9"}


def norm(sign):
    """normalize a corpus sign token to the ontology key convention (Unicode subscript -> ASCII digit)."""
    return "".join(SUB.get(c, c) for c in unicodedata.normalize("NFC", sign))


# commodity logograms carried (mis-routed) in the word channel, grounded in the Stage-B5 audit + standard
# GORILA LA metric/commodity signs. Transliteration conventions (not syllabic values).
COMMODITY_LOGOGRAMS = {"GRA", "OLE", "OLIV", "VIN", "CYP", "VS", "VAS", "AROM", "CAP", "GAL", "FIC", "NI",
                       "OVIS", "SUS", "BOS", "OLE+U", "GRA+PA", "FIC+SA"}


def sign_class(sign):
    o = ONTO.get(norm(sign)) or ONTO.get(sign)
    return o.get("class") if o else "unknown"


def is_logo(sign):
    s = norm(sign)
    if s in COMMODITY_LOGOGRAMS or sign in COMMODITY_LOGOGRAMS:
        return True
    c = sign_class(sign)
    return c == "logogram" or str(c).startswith("LOGO")


def word_type(signs):
    if any("+" in s for s in signs):          # ligature (composite; not a free phonetic wordform)
        return "LIGATURE"
    flags = [is_logo(s) for s in signs]
    if all(flags):
        return "LOGOGRAM"
    if any(flags):
        return "MIXED"
    return "PHONETIC"


def catalog_group(iid):
    """GORILA object grouping: strip a trailing a/b/g side letter + fragment index -> physical object key."""
    m = re.match(r"^([A-Z]+\d+)[a-z]?", iid)
    return m.group(1) if m else iid


def run():
    words = []                       # (iid, site, signs_normalized, wtype)
    for r in INSC:
        for t in (r.get("stream") or []):
            if t.get("t") == "word":
                sg = [norm(s) for s in t.get("signs", [])]
                words.append((r["id"], r.get("site", "?"), tuple(sg), word_type(t.get("signs", []))))
    by_type = Counter(w[3] for w in words)
    phonetic = [w for w in words if w[3] == "PHONETIC"]
    phon_forms = Counter(w[2] for w in phonetic)
    multi = [w for w in phonetic if len(w[2]) >= 2]
    # corrected effective denominators
    objects = {catalog_group(r["id"]) for r in INSC}
    multi_sign_recs = [r for r in INSC if sum(len(t.get("signs", [])) for t in (r.get("stream") or []) if t.get("t") == "word") >= 2]
    content_sig = {tuple(norm(s) for t in (r.get("stream") or []) if t.get("t") == "word" for s in t.get("signs", []))
                   for r in multi_sign_recs}
    out = {
        "word_token_types": dict(by_type),
        "phonetic_wordform_types": len(phon_forms),
        "phonetic_multisign_types": len({w[2] for w in multi}),
        "logogram_tokens_separated": by_type.get("LOGOGRAM", 0) + by_type.get("MIXED", 0),
        "effective_denominators": {
            "raw_records": len(INSC),
            "physical_objects": len(objects),
            "records_ge2_signs": len(multi_sign_recs),
            "distinct_content_signatures_ge2": len(content_sig),
        },
        "syllabary_parameters_conservative": 92,
        "value_informative_gain": False,
        "note": ("Answer-neutral representation cleanup only. Separates non-phonetic logograms from the word "
                 "channel and corrects effective_n. Does NOT inform sign values (Stage A diagnosis holds). "
                 "Feeds Stage D on clean phonetic material. Subscript normalization applied (fixes the "
                 "ASCII/Unicode key mismatch that dropped ~133 tokens on naive joins)."),
    }
    os.makedirs(DATA, exist_ok=True)
    # clean phonetic wordform inventory for Stage D
    json.dump({"phonetic_wordforms": {"+".join(k): v for k, v in phon_forms.most_common()},
               "note": "logograms + mixed tokens excluded; subscript-normalized"},
              open(os.path.join(DATA, "clean_phonetic_wordforms.json"), "w"), indent=1)
    json.dump(out, open(os.path.join(DATA, "stage_b_representation.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    run()
