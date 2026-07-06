#!/usr/bin/env python3
"""Derive a non-Cretan Egyptian→foreign correspondence corpus from the LOCALLY-OWNED Hoch 1994 scan.

Hoch is a scanned book (300dpi CCITT + OCR layer). The OCR normalizes the specialized transliteration
CONSISTENTLY (aleph ꜣ→'3'/'—', ayin ꜥ→'c', š→'s'); the romanized headwords + romanized source-language
comparanda (Akk./Ug./Heb./…) are recoverable. This extractor parses entries and assigns CONFIDENCE
TIERS by OCR cleanliness — the model is fit on tier A/B only; tier C is sensitivity — so OCR noise is
NOT baked into the primary false-positive calibration. Cretan/Keftiu/LA entries are excluded by rule.

Licensing: Hoch is copyrighted (Princeton UP); the scan + derived records are GITIGNORED (data/*). This
CODE + the manifest checksums + coverage counts are committed. Source sha 4df9bc09….
"""
import json, os, re, subprocess, sys

HOCH = "/home/claude-runner/gitlab/n8n/logos-external-anchors/experiments/external_anchors/data/bronze/pdf_local/hoch1994_semitic-words-in-egyptian-texts.pdf"
LANG_FAMILY = {"Akk": "East Semitic", "Ug": "NW Semitic", "Heb": "NW Semitic", "BH": "NW Semitic",
               "Syr": "NW Semitic", "Aram": "NW Semitic", "Phoen": "NW Semitic", "Amor": "NW Semitic",
               "Eth": "South Semitic", "Sem": "Semitic (unspec)"}
CRETAN = re.compile(r"keftiu|kftw|caphtor|kaptar|crete|cret|aegean|linear a", re.I)
_HEAD = re.compile(r'^\*?\s*([A-Za-z3c][A-Za-z3c\-; ]{1,38})\.\s+(N|V|adj|Vb|n|Adj)\.[^"]{0,30}"([A-Z][^"]{1,45})"')
_SRC = re.compile(r'\b(Akk|Ug|Heb|BH|Syr|Aram|Phoen|Amor|Eth|Sem)\.\s+([a-z3c][a-z3cāūīēō\-]{2,20})\b')
# drop obvious OCR/prose false positives on the source side
_STOP = {"word", "words", "transcription", "tran", "root", "form", "text", "meaning", "loan", "verb", "noun"}


def _clean_translit(s):
    return re.sub(r"[^A-Za-z3c;\- ]", "", s).strip()


def _tier(head, srcs):
    """A = clean headword + ≥1 clean NW/East-Semitic source; B = one bounded uncertainty; C = else."""
    head_clean = bool(re.fullmatch(r"[A-Za-z3c;\- ]{2,40}", head)) and "  " not in head
    good_src = [s for s in srcs if s[1] not in _STOP and len(s[1]) >= 3]
    if head_clean and len(good_src) >= 1 and any(LANG_FAMILY[s[0]] in ("NW Semitic", "East Semitic") for s in good_src):
        return "A", good_src
    if head_clean and good_src:
        return "B", good_src
    return "C", good_src


def extract():
    text = subprocess.run(["pdftotext", "-f", "28", "-l", "470", HOCH, "-"],
                          capture_output=True, text=True, timeout=300).stdout
    # split into entry blocks at each headword line; keep following prose until the next headword
    lines = text.splitlines()
    heads = [(i, m) for i, l in enumerate(lines) if (m := _HEAD.match(l.strip()))]
    records = []
    for k, (i, m) in enumerate(heads):
        j = heads[k + 1][0] if k + 1 < len(heads) else min(i + 40, len(lines))
        block = "\n".join(lines[i:j])
        if CRETAN.search(block):
            continue                                   # exclude Cretan/Keftiu target material by rule
        head = _clean_translit(m.group(1).split(";")[0])
        srcs = [(l, w) for (l, w) in _SRC.findall(block)]
        tier, good = _tier(head, srcs)
        records.append({
            "calibration_id": f"HOCH-{k:04d}",
            "source_id": "hoch1994", "egyptian_transliteration": head,
            "egyptian_reading_confidence": {"A": 0.75, "B": 0.55, "C": 0.35}[tier],  # capped: OCR-derived
            "gloss": m.group(3).strip().rstrip("."),
            "foreign_source_forms": [{"language": l, "form": w, "family": LANG_FAMILY[l]} for l, w in good],
            "source_language_families": sorted({LANG_FAMILY[l] for l, _ in good}),
            "item_class": "LOANWORD", "calibration_eligibility": tier,
            "source_form_confidence": 0.6 if good else 0.2,
            "record_version": "hoch-ocr-v1-2026-07-06", "provenance": "Hoch1994 OCR (aleph=3, ayin=c normalized)",
        })
    return records


def main():
    recs = extract()
    from collections import Counter
    tiers = Counter(r["calibration_eligibility"] for r in recs)
    fittable = [r for r in recs if r["calibration_eligibility"] in ("A", "B") and r["foreign_source_forms"]]
    out = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "bronze"))
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "egyptian_foreign_forms.jsonl"), "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"entries extracted: {len(recs)}   tiers: {dict(tiers)}")
    print(f"fittable (A/B with a source form): {len(fittable)}")
    print(f"tier-A: {tiers['A']}  (primary calibration set)")
    print("sample A:", [(r['egyptian_transliteration'], r['foreign_source_forms'][0]['language'],
                         r['foreign_source_forms'][0]['form']) for r in recs
                        if r['calibration_eligibility'] == 'A'][:8])


if __name__ == "__main__":
    main()
