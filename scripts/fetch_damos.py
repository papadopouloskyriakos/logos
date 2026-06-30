#!/usr/bin/env python3
"""fetch_damos.py — polite harvester for the DĀMOS Linear B corpus (the cross-script / JEPA unblocker).

DĀMOS (Database of Mycenaean at Oslo, https://damos.hf.uio.no/) is the comprehensive annotated digital
corpus of all published Mycenaean Greek **Linear B** inscriptions (~5,723 documents across Knossos,
Pylos, Thebes, Mycenae, Tiryns, Khania, …). Linear B is Linear A's DECIPHERED sister script (known
phonetic values after Ventris 1953; known language = Mycenaean Greek), so it is the "answer key" for
the cross-script transfer bets — the sequence/phonetic JEPA, the pseudo-decipherment learning curves,
and the known-answer harness.

LICENSE / REUSE. DĀMOS content is **CC BY-NC-SA 4.0** (software GPL-3.0): openly licensed for
NON-COMMERCIAL research reuse WITH ATTRIBUTION + SHARE-ALIKE. This harvester is for personal academic
research. REQUIRED CITATION (the maintainers ask for it explicitly):

    Aurora, Federico. 2015. "DAMOS (Database of Mycenaean at Oslo). Annotating a fragmentarily attested
    language." In: P. A. Fuertes-Olivera et al. (eds.), Current Work in Corpus Linguistics
    (Procedia - Social and Behavioral Sciences 198), 21-31.

The raw harvested data lands under ``corpus/bronze/linearb/damos/`` and is GITIGNORED (this CODE is
public per the logos open-by-default policy; the derived corpus is kept local, not redistributed).

POLITENESS. Single-threaded; a configurable delay (default 1.0 s) between requests + a descriptive
User-Agent; resumable (skips ids already saved) so an interrupted run never re-hammers the server.
The site has NO robots.txt (404) and exposes a public JSON API (the React app's own backend):

    POST /ajaxgetfilter         -> collection facets (the corpus size by site)
    GET  /ajaxitem/<id>/        -> one document: {item:{heading, content (TRANSLITERATION), series, …}}
    GET  /ajaxitemcontent/<id>  -> just the transliteration content

Item ids are dense ~1..~5800. We iterate ids and keep every one that returns an ``item``.

    python3 scripts/fetch_damos.py [--max-id 6000] [--delay 1.0] [--out <dir>]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

BASE = "https://damos.hf.uio.no"
UA = "logos-research/0.1 (personal academic use; DAMOS is CC BY-NC-SA 4.0; cites Aurora 2015)"
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUT = os.path.join(_ROOT, "corpus", "bronze", "linearb", "damos")

CITATION = ("Aurora, Federico. 2015. DAMOS (Database of Mycenaean at Oslo). Annotating a fragmentarily "
            "attested language. Procedia - Social and Behavioral Sciences 198, 21-31.")
LICENSE = "CC BY-NC-SA 4.0 (content); GPL-3.0 (software). Source: https://damos.hf.uio.no/"


def _get(url: str, timeout: int = 30) -> object:
    """GET a URL and parse JSON; returns None on 404/empty, raises on other transient errors."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise
    body = body.strip()
    if not body:
        return None
    return json.loads(body)


def collections(out_dir: str) -> dict:
    """Fetch + persist the collection facets (corpus size by site) — also a connectivity check."""
    req = urllib.request.Request(f"{BASE}/ajaxgetfilter", method="POST",
                                 headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode("utf-8"))
    with open(os.path.join(out_dir, "collections.json"), "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    return data


def _seen_ids(path: str) -> set:
    """Ids already harvested (for resume)."""
    seen = set()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    seen.add(int(json.loads(line)["_id"]))
                except Exception:
                    continue
    return seen


def harvest(out_dir: str, max_id: int, delay: float, timeout: int = 30) -> None:
    os.makedirs(out_dir, exist_ok=True)
    # provenance first, so the directory is always self-describing
    with open(os.path.join(out_dir, "PROVENANCE.md"), "w", encoding="utf-8") as fh:
        fh.write(f"# DĀMOS Linear B corpus (harvested)\n\n"
                 f"- Source: {BASE}/ (public JSON API: /ajaxitem/<id>/)\n"
                 f"- License: {LICENSE}\n"
                 f"- Citation: {CITATION}\n"
                 f"- Use: personal academic research (non-commercial). GITIGNORED; not redistributed.\n"
                 f"- Harvester: scripts/fetch_damos.py (delay {delay}s, max_id {max_id}).\n")
    col = collections(out_dir)
    total = sum(int(v) for v in (col.get("collections") or {}).values()) if isinstance(col, dict) else 0
    print(f"DĀMOS reports ~{total} documents across {len(col.get('collections', {}))} collections.")

    items_path = os.path.join(out_dir, "items.jsonl")
    seen = _seen_ids(items_path)
    print(f"resuming: {len(seen)} ids already harvested; iterating 1..{max_id}")

    kept, missing = len(seen), 0
    with open(items_path, "a", encoding="utf-8") as out:
        for iid in range(1, max_id + 1):
            if iid in seen:
                continue
            try:
                data = _get(f"{BASE}/ajaxitem/{iid}/", timeout=timeout)
            except Exception as exc:  # transient — back off and retry once
                time.sleep(min(10.0, delay * 5))
                try:
                    data = _get(f"{BASE}/ajaxitem/{iid}/", timeout=timeout)
                except Exception:
                    print(f"  id {iid}: ERROR {str(exc)[:60]} (skipped)")
                    time.sleep(delay)
                    continue
            item = data.get("item") if isinstance(data, dict) else None
            if item:
                rec = {"_id": iid, "heading": item.get("heading"), "item": item}
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                out.flush()
                kept += 1
                if kept % 200 == 0:
                    print(f"  harvested {kept} docs (at id {iid})")
            else:
                missing += 1
            time.sleep(delay)
    print(f"DONE: {kept} documents in {items_path}; {missing} empty ids in range.")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Polite harvester for the DĀMOS Linear B corpus (CC BY-NC-SA).")
    p.add_argument("--max-id", type=int, default=6000, help="highest item id to probe (dense ~1..5800)")
    p.add_argument("--delay", type=float, default=1.0, help="seconds between requests (be polite)")
    p.add_argument("--out", default=DEFAULT_OUT, help="output dir (default corpus/bronze/linearb/damos)")
    p.add_argument("--timeout", type=int, default=30)
    args = p.parse_args(argv)
    harvest(args.out, args.max_id, args.delay, args.timeout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
