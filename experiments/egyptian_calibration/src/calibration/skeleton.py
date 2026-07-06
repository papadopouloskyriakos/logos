#!/usr/bin/env python3
"""f() — the ONE deterministic, answer-blind skeletonizer for the Cretan-anchor test (prereg §3).

Applied IDENTICALLY to (i) Egyptian En-list oval transliterations, (ii) target Linear B forms, and
(iii) every candidate-pool member. The reduction rule is fixed here so no answer-aware preprocessing
can leak into scoring (red-team blocker B2):

  - lowercase + NFC-normalise; strip editorial brackets/marks and combining diacritics;
  - split nothing special — scan characters left to right;
  - DROP vowels (a e i o u + accented variants);
  - DROP vowel-carriers / glides: aleph (ꜣ ʾ ' and OCR '3'), ayin (ʿ ʕ), and the glides j w y;
  - KEEP every other letter as a consonant, in order;
  - š and s are kept DISTINCT (any š≡s equivalence must be earned by the model, not preprocessed).

This makes f(a-mi-ni-so)=('m','n','s') and f([j]ʿ-m-n-i-šꜣ)=('m','n','š') — the leading aleph/ayin is a
vowel-carrier dropped on BOTH sides, resolving the v1 Amnisos discrepancy. Deterministic; no parameters.
"""
import unicodedata

VOWELS = set("aeiouāēīōūáéíóúàèìòùâêîôûäëïöüăĕĭŏŭãẽĩõũ")
# aleph (ꜣ/ʾ and OCR '3'), ayin (ꜥ/ʿ/ʕ), and glides j/w/y — all vowel-carriers in group writing
CARRIERS = set("ꜣꜥʾʼ'`ʿʕ3jwy")


def _strip(text):
    # brackets / parentheses / question-marks / dots-of-uncertainty / asterisks / digits-in-signs removed;
    # hyphens and letters retained for the scan.
    out = []
    for ch in text:
        if ch in "[]()<>{}?.·*0123456789 \t":
            continue
        out.append(ch)
    return "".join(out)


def f(text):
    """Raw transliteration (hyphenated or not; a str) -> tuple of consonant symbols."""
    if text is None:
        return tuple()
    s = unicodedata.normalize("NFC", str(text)).lower()
    s = _strip(s)
    cons = []
    for ch in s:
        if ch == "-":
            continue
        if unicodedata.combining(ch):
            continue
        if not ch.isalpha():
            continue
        if ch in VOWELS or ch in CARRIERS:
            continue
        cons.append(ch)
    return tuple(cons)


def f_str(text):
    return "-".join(f(text))


def levenshtein(a, b):
    """Edit distance between two consonant tuples/sequences (unit costs)."""
    a, b = tuple(a), tuple(b)
    n, m = len(a), len(b)
    if n == 0:
        return m
    if m == 0:
        return n
    prev = list(range(m + 1))
    for i in range(1, n + 1):
        cur = [i] + [0] * m
        for j in range(1, m + 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] != b[j - 1]))
        prev = cur
    return prev[m]


if __name__ == "__main__":
    # self-check against the frozen target skeletons (prereg §3)
    checks = [
        ("kꜣ-jn-jw-šꜣ", "k-n-š"),      # Knossos oval
        ("ko-no-so", "k-n-s"),          # Knossos LB
        ("[j]ʿ-m-n-i-šꜣ", "m-n-š"),    # Amnisos oval
        ("a-mi-ni-so", "m-n-s"),        # Amnisos LB
        ("rj-kꜣ-tj", "r-k-t"),          # Lyktos oval
        ("ru-ki-to", "r-k-t"),          # Lyktos LB
        ("bꜣ-y-šꜣ-tj", "b-š-t"),       # Phaistos oval
        ("pa-i-to", "p-t"),             # Phaistos LB
        ("Kꜣ-tw-nꜣ-y", "k-t-n"),       # Kydonia oval
        ("ku-do-ni-ja", "k-d-n"),       # Kydonia LB
        ("kꜣ-tj-i-rꜥ", "k-t-r"),       # Kythera oval
        ("ku-te-ra", "k-t-r"),          # Kythera LB
    ]
    ok = True
    for raw, want in checks:
        got = f_str(raw)
        flag = "OK " if got == want else "FAIL"
        if got != want:
            ok = False
        print(f"  {flag} f({raw!r}) = {got!r}   (want {want!r})")
    print("ALL PASS" if ok else "MISMATCH")
