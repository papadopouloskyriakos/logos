#!/usr/bin/env python3
"""fetch_ugaritic.py — fetch the Luo / B-K&K decipherment datasets into corpus/bronze (gitignored).

Sources pinned by the acquire+port workflow (2026-06-30):
  Ugaritic<->Hebrew GOLD (2,214 cognate pairs) + Noisy balanced test  -- ftamburin/CSA_OptMatcher
  Ugaritic<->Hebrew FULL noisy candidate pool (43,951)                -- j-luo93/NeuroDecipher
  Linear B<->Greek cognate pairs (919)                                -- ftamburin/CSA_OptMatcher
These are the EXACT files Luo 2019 / Snyder 2010 / Berg-Kirkpatrick & Klein / Tamburini 2025 used.

Licensing: raw academic data -> corpus/bronze (gitignored, invariant 10). Silver normalization
into corpus/silver is a later step.

    python3 scripts/fetch_ugaritic.py
"""
import hashlib
import os
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRONZE = os.path.join(ROOT, "corpus", "bronze")
UA = {"User-Agent": "logos-research/0.1 (decipherment research; see repo)"}

# (relative path under corpus/bronze, source URL, expected line count)
FILES = [
    ("ugaritic/uga-heb.gold.cog",
     "https://raw.githubusercontent.com/ftamburin/CSA_OptMatcher/main/data/uga-heb.no_speNL.cog",
     2215),
    ("ugaritic/uga-heb.full.cog",
     "https://raw.githubusercontent.com/j-luo93/NeuroDecipher/master/data/uga-heb.no_spe.cog",
     43952),
    ("ugaritic/uga-heb.noisy.cog",
     "https://raw.githubusercontent.com/ftamburin/CSA_OptMatcher/main/data/uga-heb.no_speNoisy.cog",
     4442),
    ("linearb/linear_b-greek.cog",
     "https://raw.githubusercontent.com/ftamburin/CSA_OptMatcher/main/data/linear_b-greek.cog",
     920),
]


def fetch(url, dest, expect_lines, retries=3):
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "wb") as f:
                f.write(data)
            n = data.count(b"\n") + (0 if data.endswith(b"\n") else 1)
            sha = hashlib.sha256(data).hexdigest()[:16]
            ok = abs(n - expect_lines) <= 1
            flag = "OK  " if ok else "WARN"
            print(f"  [{flag}] {os.path.relpath(dest, ROOT)}: {n} lines (expect {expect_lines}), "
                  f"sha256={sha}, {len(data)} bytes")
            return sha, n, ok
        except Exception as e:
            print(f"  [retry {attempt}/{retries}] {url}: {e}")
            time.sleep(2 * attempt)
    return None, 0, False


def main():
    manifest, allok = [], True
    for rel, url, expect in FILES:
        dest = os.path.join(BRONZE, rel)
        print(f"fetch {url}")
        sha, n, ok = fetch(url, dest, expect)
        manifest.append((rel, url, n, sha))
        allok = allok and ok
    mpath = os.path.join(BRONZE, "MANIFEST.txt")
    with open(mpath, "w") as f:
        f.write("# logos bronze provenance (fetch_ugaritic.py)\n")
        for rel, url, n, sha in manifest:
            f.write(f"{sha or 'FAILED'}\t{n}\t{rel}\t{url}\n")
    print(f"\nmanifest -> {os.path.relpath(mpath, ROOT)}")
    print("ALL OK" if allok else "WARN: some line counts off — inspect before use")
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
