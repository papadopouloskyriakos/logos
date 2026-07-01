#!/usr/bin/env python3
"""Linear B morphology POSITIVE CONTROL (preprint item 1.5).

Runs the IDENTICAL bigram-floor affix test used on Linear A (scripts/comparison/morphology.py:
run_affix_panel / null_falsification) against Mycenaean Greek (Linear B), whose longer words carry
uncontested inflectional morphology. Purpose: show the test HAS measurable power in a relevant
syllabic setting, so Linear A's NO POWER means "finds morphology where it demonstrably exists and
correctly finds none in Linear A," not "the floor is too strong to detect anything."

Corpus: DĀMOS (corpus/bronze/linearb/damos/items.jsonl), the ingested Mycenaean corpus. Words are
parsed from each tablet's `content` transcription: hyphen-joined lowercase syllabograms are words;
UPPERCASE logograms, numerals, word dividers and editorial marks are dropped.

Affix panel: PRE-REGISTERED (a-priori, from Ventris & Chadwick 1953 and standard Mycenaean grammar),
NOT tuned to fire. Suffixal, because Greek inflection is suffixal. The productivity gate (an affix
must attach to >=2 distinct residual stems) and the conservative max(shuffle, L_fake) floor are the
real test — a suffix that merely echoes the sign-bigram statistics scores as NO POWER, exactly as in
Linear A.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.comparison import morphology as M
from scripts.comparison.morphology import Affix, Inscription, SignCodec
from scripts.cross_script.data import _damos_wordforms   # canonical DĀMOS parser (the §7.3 / 13,562-wordform one)

DAMOS = "corpus/bronze/linearb/damos/items.jsonl"

# --- PRE-REGISTERED Mycenaean affix panel (a-priori; Ventris & Chadwick 1953; Bartoněk 2003) ------
# Final-syllabogram inflectional/derivational endings that are securely grammatical in Mycenaean.
MYC_AFFIXES = (
    Affix("-jo",   "suffix", (("JO",),),        "JO",   "V&C adj/gen -yo-"),
    Affix("-o-jo", "suffix", (("O", "JO"),),    "O-JO", "V&C gen sg -oio"),
    Affix("-de",   "suffix", (("DE",),),        "DE",   "V&C allative -de"),
    Affix("-qe",   "suffix", (("QE",),),        "QE",   "V&C enclitic -kʷe 'and'"),
    Affix("-si",   "suffix", (("SI",),),        "SI",   "V&C dat-loc pl -si"),
    Affix("-pi",   "suffix", (("PI",),),        "PI",   "V&C instr pl -phi"),
    Affix("-o-i",  "suffix", (("O", "I"),),     "O-I",  "V&C dat pl -ois"),
    Affix("-a",    "suffix", (("A",),),         "A",    "V&C a-stem / neut pl"),
    Affix("-o",    "suffix", (("O",),),         "O",    "V&C o-stem nom/gen/dat"),
    Affix("-e",    "suffix", (("E",),),         "E",    "V&C dat sg -ei"),
    Affix("-i",    "suffix", (("I",),),         "I",    "V&C dat-loc sg -i"),
    Affix("-we",   "suffix", (("WE",),),        "WE",   "V&C u-stem / -wes"),
    Affix("-ne",   "suffix", (("NE",),),        "NE",   "V&C n-stem endings"),
    Affix("-ro",   "suffix", (("RO",),),        "RO",   "V&C -lo-/-ro- adj (broadened)", broadened=True),
    Affix("-wo",   "suffix", (("WO",),),        "WO",   "V&C -wo- (broadened)", broadened=True),
    Affix("-ta",   "suffix", (("TA",),),        "TA",   "V&C agent -tas (broadened)", broadened=True),
)

def load_linb():
    """One Inscription per DĀMOS tablet; words via the canonical _damos_wordforms (uppercase VALUES)."""
    corpus = []
    for line in open(DAMOS, encoding="utf-8"):
        rec = json.loads(line)
        it = rec.get("item", {})
        content = it.get("content") or ""
        words = _damos_wordforms(content)          # [['DE','U','KI','JO','JO'], ...]
        if words:
            corpus.append(Inscription(iid=str(it.get("id", rec.get("_id", ""))),
                                      site=str(it.get("ishort", "")), words=words))
    return corpus

def main():
    corpus = load_linb()
    n_docs = len(corpus)
    all_words = [w for ins in corpus for w in ins.words]
    n_tok = len(all_words)
    n_types = len({tuple(w) for w in all_words})
    import statistics
    lens = [len(w) for w in all_words]
    print(f"[corpus] docs={n_docs}  word-tokens={n_tok}  distinct-wordforms={n_types}")
    print(f"[corpus] signs/word: mean={statistics.mean(lens):.2f} median={statistics.median(lens)} "
          f"<=2 signs={sum(1 for x in lens if x<=2)/n_tok:.1%}")
    codec = SignCodec.from_corpus(corpus)
    print(f"[corpus] distinct syllabograms={len(codec.to_char)}")
    print(f"[panel] {len(MYC_AFFIXES)} pre-registered Mycenaean affixes")
    res = M.null_falsification(corpus, codec, affixes=MYC_AFFIXES, n_null=200, seed=0)
    print("\n===== RESULT (identical bigram-floor test) =====")
    print(f"  REAL   confirm rate = {res['real_confirm_rate']:.3f}  "
          f"({res['real']['n_confirm']}/{res['real']['n_affixes_tested']})  "
          f"confirmed: {res['real_confirmed_affixes']}")
    print(f"  SHUFFLE floor       = {res['shuffle_confirm_rate']:.3f}")
    print(f"  L_fake bigram floor = {res['lfake_confirm_rate']:.3f}")
    print(f"  floor (max)         = {res['floor']:.3f}")
    print(f"  has_morphology_power = {res['has_morphology_power']}   "
          f"(beats_shuffle={res['beats_shuffle_floor']}, beats_lfake={res['beats_lfake_floor']})")
    out = {
        "corpus": {"docs": n_docs, "word_tokens": n_tok, "wordforms": n_types,
                   "mean_signs_per_word": round(statistics.mean(lens), 3),
                   "distinct_syllabograms": len(codec.to_char)},
        "panel_size": len(MYC_AFFIXES),
        "real_confirm_rate": res["real_confirm_rate"],
        "real_confirmed_affixes": res["real_confirmed_affixes"],
        "shuffle_confirm_rate": res["shuffle_confirm_rate"],
        "lfake_confirm_rate": res["lfake_confirm_rate"],
        "floor": res["floor"],
        "has_morphology_power": res["has_morphology_power"],
        "beats_shuffle": res["beats_shuffle_floor"],
        "beats_lfake": res["beats_lfake_floor"],
    }
    Path("results").mkdir(exist_ok=True)
    json.dump(out, open("results/linb_morphology_control.json", "w"), indent=2)
    print("\n  -> results/linb_morphology_control.json")

if __name__ == "__main__":
    main()
