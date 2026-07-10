#!/usr/bin/env python3
"""E201-F1b import gate: hashes sweep outputs into IMPORT_RECEIPT.json BEFORE use.
Refuses code files and anything outside results/csa. Append-only receipt."""
import hashlib, json, os, sys

def main():
    if len(sys.argv) != 2:
        print("usage: import_f1b.py <results/csa dir on main>"); return 2
    src = os.path.abspath(sys.argv[1])
    if "results/csa" not in src.replace(os.sep, "/"):
        print("REFUSED: source must be a results/csa directory"); return 1
    here = os.path.dirname(os.path.abspath(__file__))
    rec_path = os.path.join(here, "IMPORT_RECEIPT.json")
    if os.path.exists(rec_path):
        print("REFUSED: receipt exists (append-only; write an ERRATUM instead)"); return 1
    rows = []
    for dp, _, fns in os.walk(src):
        for fn in sorted(fns):
            if fn.endswith((".py", ".sh", ".ipynb")):
                print(f"REFUSED: code file in import set: {fn}"); return 1
            p = os.path.join(dp, fn)
            rows.append({"file": os.path.relpath(p, src),
                         "sha256": hashlib.sha256(open(p, "rb").read()).hexdigest()})
    json.dump({"source": src, "n_files": len(rows), "files": rows,
               "boundary": "imports/E201_F1B", "scored_yet": False},
              open(rec_path, "w"), indent=1)
    print(f"receipt written: {len(rows)} files hashed; now score under the F1a-frozen harness")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
