"""Provisional Egyptian-style distortion layer for the matched-scarcity control. FIXED params;
NOT tuned to maximize recovery. Replaced by the frozen Hoch correspondence model once REQ-02 is fit."""
DEFAULT = {"vowel_drop": 0.4, "cons_merge": 0.1, "epenthesis": 0.05, "omission": 0.1, "subst": 0.1, "noise": 0.05}
VOWELS = set("aeiou")
def degrade(skeleton, rng, params=None):
    p = dict(DEFAULT, **(params or {})); out = []
    for tok in skeleton:
        if isinstance(tok, str) and tok and tok[0].lower() in VOWELS and rng.random() < p["vowel_drop"]:
            continue
        if rng.random() < p["omission"]:
            continue
        if rng.random() < p["subst"]:
            out.append(("SUB", tok)); continue
        out.append(tok)
        if rng.random() < p["epenthesis"]:
            out.append(("EP",))
    return out
