#!/usr/bin/env python3
"""EPOCH-005 — KNZg57a provenance trace (mechanical re-runnable checks).

Re-verifies every locally checkable fact behind the EPOCH-005 verdict and emits
epochs/EPOCH-005/audit_checks.json. Web facts (GitHub commit history) are recorded
in result.json with their API URLs; this script re-checks them only if --web.
"""
import hashlib, json, os, re, subprocess, sys

ROOT = "/home/claude-runner/gitlab/n8n/logos-linear-a-frontier-72h"
EP = os.path.join(ROOT, "experiments/linear_a_frontier_72h/epochs/EPOCH-005")
LINEARA = "/tmp/lineara"
SILVER_TOKENS = ["*401+RU", "*401+RU", "*418+L2", "NI", "VAS"]
RAW_EXPECTED = ["*401+RU", "*652", "*653", "*401+RU", "*418+L2", "NI", "VAS"]

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()

checks = []
def check(name, ok, detail):
    checks.append({"check": name, "pass": bool(ok), "detail": detail})
    print(("PASS " if ok else "FAIL ") + name + " :: " + detail)

# C1 silver record
silver = json.load(open(os.path.join(ROOT, "corpus/silver/inscriptions.json")))
rec = [r for r in silver if r["id"] == "KNZg57a"]
check("C1_silver_record", len(rec) == 1 and rec[0]["signs"] == SILVER_TOKENS,
      f"silver KNZg57a signs == {SILVER_TOKENS}")

# C2 raw lineara record + identified-token sequence
raw = json.load(open(os.path.join(LINEARA, "items_analysis/inscriptions.json")))
rraw = {e[0]: e[1] for e in raw if isinstance(e, list) and len(e) >= 2}
ra = rraw.get("KNZg57a", {})
LACUNA = "\U0001076B"  # 𐝫
ident = [w for w in ra.get("transliteratedWords", []) if w and w != LACUNA]
check("C2_raw_lineara_tokens", ident == RAW_EXPECTED,
      f"raw identified (non-lacuna) tokens {ident} == {RAW_EXPECTED} (17 slots incl. 10 lacunae)")

# C3 deterministic builder filter explains silver(5) from raw(7): letterless *652/*653 dropped
derived = [w for w in ra.get("transliteratedWords", []) if w and re.search(r"[A-Za-z]", w)]
check("C3_builder_filter", derived == SILVER_TOKENS,
      "corpus_io.is_sign_token (requires a latin letter) drops '*652','*653' + lacunae -> exactly the 5 silver tokens")

# C4 raw record cites the Kanta 2024 article (local paper byte-identical to bronze)
lp = os.path.join(LINEARA, "papers/KNZg57.pdf")
kanta_sha = "87dad27b79ee3ef4539b844d7ed30a0069ac14acdd2ff75eed160f9baadf57d2"
check("C4_cited_paper_is_kanta2024", os.path.exists(lp) and sha256(lp) == kanta_sha,
      f"lineara.xyz papers/KNZg57.pdf sha256 == {kanta_sha[:12]}… (== bronze kanta_etal_2024)")
check("C4b_imageRights", ra.get("imageRights") == "Ph Saperstein" and
      "KNZg57.pdf" in ra.get("imageRightsURL", ""),
      "record credits 'Ph Saperstein' [= Ph. Sapirstein, Fig. 7 photo credit] + links the article PDF")

# C5 Kanta 2024 prose: vas+RU named, but NO transliterated sequence (entailment rule)
txt = subprocess.run(["pdftotext", os.path.join(ROOT, "corpus/bronze/kanta_etal_2024_anetaki",
                     [f for f in os.listdir(os.path.join(ROOT, "corpus/bronze/kanta_etal_2024_anetaki"))
                      if f.endswith(".pdf")][0]), "-"],
                     capture_output=True, text=True).stdout
has_vasru = "vas+RU" in txt
seq_printed = bool(re.search(r"\*401\+RU\W+\*401\+RU|\*418", txt))
check("C5_kanta_vasRU_does_not_license", has_vasru and not seq_printed,
      "prose 'vas+PA, vas+RU, etc.' present; NO sign-sequence printed -> DOES_NOT_LICENSE (consistent only)")

# C6 positive control: KNZg55 traces to a published source through the same pipeline
z55 = [r for r in silver if r["id"] == "KNZg55"]
yng = open(os.path.join(ROOT, "corpus/bronze/younger_lineara/misctexts.txt"), encoding="utf-8", errors="ignore").read()
check("C6_positive_control_KNZg55",
      len(z55) == 1 and z55[0]["signs"] == ["JA", "SA", "JA"] and
      "KN Zg 55" in yng and re.search(r"JA-\s*SA\s*-JA", yng),
      "silver KNZg55=JA-SA-JA recovered in Younger misctexts (HM 621; CMS II 2 213) -> method has power")

# C7 negative control: no source anywhere yields a 'KN Zg 56' reading
neg = 0
for p in ["corpus/bronze/younger_lineara/misctexts.txt",
          "corpus/bronze/delfreo_rapport_koronowesa/rapport.txt",
          "corpus/silver/inscriptions.json"]:
    neg += len(re.findall(r"Zg ?56", open(os.path.join(ROOT, p), encoding="utf-8", errors="ignore").read()))
neg += len(re.findall(r"Zg ?56", json.dumps(raw)))
check("C7_negative_control_Zg56", neg == 0, f"'KN Zg 56' hits across candidate sources = {neg} (expected 0)")

# C8 Del Freo: both carriers 'inédit' (no reading)
df = open(os.path.join(ROOT, "corpus/bronze/delfreo_rapport_koronowesa/rapport.txt"),
          encoding="utf-8", errors="ignore").read()
check("C8_delfreo_inedit", "KN Zg 57" in df and "KN Zg 58" in df and df.count("inédit") >= 2,
      "Rapport 2016-2021 lists KN Zg 57/58 as inédit — no transliteration")

# C9 J1 exposure audit does NOT register the lineara.xyz public transliteration
j1 = subprocess.run(["git", "-C", ROOT, "show",
                     "research/linear-a-relative-phonology-seals:experiments/linear_a_relative_phonology/data/J1_exposure.json"],
                    capture_output=True, text=True).stdout
check("C9_J1_gap", "lineara" not in j1.lower() and "401+RU" not in j1 and
      "No public source" in j1,
      "J1_exposure.json asserts 'No public source carries a transliterated sign-group sequence' and omits lineara.xyz -> factually false since 2025-03-23")

# C10 both seals state in_current_corpus:false while silver holds the 5-token fragment
m = json.load(open(os.path.join(ROOT, "experiments/linear_a_anchor_lattice/data/seals/M_ANETAKI_LATTICE_DELTA_SEAL.json")))
a = subprocess.run(["git", "-C", ROOT, "show",
                    "research/linear-a-relative-phonology-seals:experiments/linear_a_relative_phonology/seals/ANETAKI_FINAL_EDITION_DELTA_SEAL.json"],
                   capture_output=True, text=True).stdout
check("C10_seal_misstatement", m.get("in_current_corpus") is False and '"in_current_corpus": false' in a,
      "both seals record in_current_corpus:false; silver contains KNZg57a (partial) -> ERRATUM wording needed")

# C11 token classes: NI is AB; ligatures unclassed in syllabogram ontology (MP1 impact bounded)
onto = json.load(open(os.path.join(ROOT, "corpus/silver/signs_ontology.json")))
check("C11_token_classes", onto.get("NI", {}).get("class") == "syllabogram-AB" and
      all(t not in onto for t in ["*401+RU", "*418+L2", "VAS", "*652", "*653"]),
      "NI=syllabogram-AB; the vessel ligatures are not A-only syllabogram types -> MP1 A-only count contamination ~0, denominator overlap 5-7 tokens")

if "--web" in sys.argv:
    import urllib.request
    u = "https://api.github.com/repos/mwenge/lineara.xyz/commits/5facf29c"
    d = json.load(urllib.request.urlopen(u))
    check("W1_reading_commit", d["commit"]["author"]["date"].startswith("2025-03-23"),
          "GitHub 5facf29c 2025-03-23T17:22:23Z adds the 17-slot reading (Robert Hogan)")

out = {"epoch": "EPOCH-005", "checks": checks,
       "n_pass": sum(c["pass"] for c in checks), "n_total": len(checks)}
os.makedirs(EP, exist_ok=True)
json.dump(out, open(os.path.join(EP, "audit_checks.json"), "w"), indent=1)
print(f"\n{out['n_pass']}/{out['n_total']} checks pass -> {EP}/audit_checks.json")
