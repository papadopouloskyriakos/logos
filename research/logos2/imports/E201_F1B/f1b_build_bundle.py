#!/usr/bin/env python3
"""E201-F1b — STAGE the completed Exit-B CSA sufficiency sweep into a results/csa/ import bundle.
Generates sweep OUTPUT artifacts only (JSON + a bundled tarball of the raw cells); NO scoring here
(scoring happens AFTER import_f1b.py writes the receipt, per BOUNDARY.md). Counts are generated,
never hand-typed (invariant 12)."""
from __future__ import annotations
import json, glob, os, collections, hashlib, tarfile

MAIN = "/home/claude-runner/gitlab/n8n/logos"
CELLS = f"{MAIN}/runtime/csa_sweep/cells"
T0DIR = f"{MAIN}/runtime/csa_sweep/T0_convergence"
BACKUP_TGZ = f"{MAIN}/runtime/csa_sweep_vast_backup_20260716/csa_backup_20260716.tgz"
OUT = f"{MAIN}/results/csa/exitB_sweep_20260716"
os.makedirs(OUT, exist_ok=True)


def sha256(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


# ---- per-benchmark recovery summary, generated from the 168 cells ----
cells = collections.defaultdict(list)
for f in sorted(glob.glob(f"{CELLS}/*.json")):
    c = json.load(open(f))
    b = c.get("benchmark") or os.path.basename(f).split("__")[0]
    cells[b].append({"size": c.get("size"), "seed": c.get("seed"), "acc": c.get("acc"),
                     "found": c.get("found"), "total": c.get("total")})

summary = {"kind": "exitB_csa_sufficiency_sweep_recovery_summary",
           "generated_from": "runtime/csa_sweep/cells (168 cells)", "steps_budget": 2000,
           "recovery_method": "CSA (Tamburini 2025 CSA_OptMatcher)",
           "note": "recovery = found/total held-out cognate recovery; steps=2000 => LOWER BOUND "
                   "(T0 convergence control verdict CONVERGENCE_ARTIFACT, LinearB still climbing at 6000 steps).",
           "benchmarks": {}}
for b, rows in cells.items():
    rows = [r for r in rows if r["size"] is not None and r["acc"] is not None]
    full_size = max(r["size"] for r in rows)
    full = [r["acc"] for r in rows if r["size"] == full_size]
    allacc = [r["acc"] for r in rows]
    summary["benchmarks"][b] = {
        "n_cells": len(rows), "full_size": full_size,
        "full_recovery_mean": round(sum(full) / len(full), 6),
        "full_recovery_max": round(max(full), 6),
        "max_recovery_any_size": round(max(allacc), 6),
        "n_seeds_full": len(full),
    }
json.dump(summary, open(f"{OUT}/recovery_by_benchmark.json", "w"), indent=1)

# ---- T0 convergence control (copy the verdict + trajectory) ----
t0 = json.load(open(f"{T0DIR}/linearb_full_seed0_steps6000.json"))
json.dump({"T0_VERDICT": t0.get("T0_VERDICT"), "acc_at_cap": t0.get("acc"),
           "steps_run": t0.get("steps"), "early_stopped": t0.get("early_stopped"),
           "trajectory": t0.get("trajectory")},
          open(f"{OUT}/T0_convergence.json", "w"), indent=1)

# ---- raw cells, bundled (scheduler output; hashed by the importer) ----
with tarfile.open(f"{OUT}/cells.tgz", "w:gz") as tar:
    for f in sorted(glob.glob(f"{CELLS}/*.json")):
        tar.add(f, arcname=f"cells/{os.path.basename(f)}")

# ---- provenance (points back to the checksum-verified backup) ----
json.dump({"sweep": "Exit-B CSA sufficiency sweep (robustness extension)",
           "completed_utc": "2026-07-15T07:07Z", "n_cells": sum(len(v) for v in cells.values()),
           "raw_output_path_on_main": "runtime/csa_sweep/cells",
           "verified_backup_tarball": "runtime/csa_sweep_vast_backup_20260716/csa_backup_20260716.tgz",
           "verified_backup_sha256": sha256(BACKUP_TGZ) if os.path.exists(BACKUP_TGZ) else None,
           "compute": "vast.ai instance 44534071 (destroyed post-backup)"},
          open(f"{OUT}/PROVENANCE.json", "w"), indent=1)

print(f"staged bundle -> {OUT}")
for fn in sorted(os.listdir(OUT)):
    print(f"  {fn}  ({os.path.getsize(os.path.join(OUT, fn))} bytes)")
print("\nper-benchmark full-size recovery (generated):")
for b, s in summary["benchmarks"].items():
    print(f"  {b:22s} full={s['full_size']:<5} mean={s['full_recovery_mean']:.4f} "
          f"max_any_size={s['max_recovery_any_size']:.4f}")
