#!/usr/bin/env python3
"""EPOCH-009 acquisition: polite single-threaded fetch of all SigLA document renders.
Prereg epochs/EPOCH-009/prereg.md sha256 ec87a23b87d0c984ba47e79d6b9d8dfd0d83f397fa5a1f05cb188e3cc8d88cdc.
"""
import json, os, time, urllib.parse, urllib.request

W = "/home/claude-runner/gitlab/n8n/logos-linear-a-frontier-72h"
EXP = f"{W}/experiments/linear_a_frontier_72h"
RD = f"{EXP}/data/stroke_corpus/renders"
UA = "logos-epoch009-stroke-sweep/1.0"
SPACING = 1.2

def dest_of(desig):
    return f"{RD}/{desig.replace(' ', '_').replace('/', '~')}.png"

def fetch(desig):
    dest = dest_of(desig)
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return "cached"
    safe = urllib.parse.quote(desig)
    url = f"https://sigla.phis.me/document/{safe}/{safe}.png"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            blob = r.read()
        if not blob:
            time.sleep(SPACING); return "ERROR:empty"
        open(dest, "wb").write(blob)
        time.sleep(SPACING)
        return "fetched"
    except Exception as e:
        time.sleep(SPACING)
        return f"ERROR:{type(e).__name__}:{e}"

def main():
    docs = json.load(open(f"{W}/corpus/bronze/sigla_browse_2026/sigla_documents.json"))
    desigs = [d["designation"] for d in docs]
    log = {}
    for i, d in enumerate(desigs):                       # pass 1
        log[d] = fetch(d)
        if i % 50 == 0:
            print(f"[pass1 {i}/{len(desigs)}] {d}: {log[d]}", flush=True)
            json.dump(log, open(f"{RD}/../fetch_log.json", "w"), indent=0)
    fails = [d for d in desigs if log[d].startswith("ERROR")]
    print(f"pass1 done: {len(fails)} failures; retrying once", flush=True)
    for d in fails:                                      # pass 2 (single retry)
        time.sleep(2.0)
        log[d] = fetch(d)
    n_ok = sum(1 for v in log.values() if not v.startswith("ERROR"))
    json.dump(log, open(f"{RD}/../fetch_log.json", "w"), indent=0)
    print(f"DONE: {n_ok}/{len(desigs)} available "
          f"({sum(1 for v in log.values() if v=='fetched')} fetched this run)", flush=True)

if __name__ == "__main__":
    main()
