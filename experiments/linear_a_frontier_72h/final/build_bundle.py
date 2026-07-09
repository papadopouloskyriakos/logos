"""Rebuild the external review bundle (audit package) + LOGOS_72H_REVIEW_BUNDLE.zip.

Terminal-audit remediation packaging (items D1-D6, C8):
- copies the closure narrative docs + generated JSON/CSV from final/ into review_bundle/;
- copies EPOCH-103/104 dirs INCLUDING the append-only remediation files (prereg_addendum_R,
  plan_hash_R, machinery_R, result_R) alongside the frozen originals, and EPOCH-105 with its
  emitted result.json (D3);
- ships the FRACTION_ORDER seal manifest AND the five licence-clean files it references, laid
  out at the manifest's relative paths so `sha256sum -c` succeeds from the bundle root (D1);
- writes BUNDLE_MANIFEST.sha256 (sha256sum format, bundle-relative paths, excluding itself)
  so the whole bundle verifies with one command (C8-adjacent: no self-entry);
- zips the bundle to final/LOGOS_72H_REVIEW_BUNDLE.zip (deterministic file order).

README.md is authored in place inside review_bundle/ and is preserved, not generated.
"""
import hashlib
import os
import shutil
import zipfile

ROOT = "experiments/linear_a_frontier_72h"
FINAL = f"{ROOT}/final"
BUNDLE = f"{FINAL}/review_bundle"

NARRATIVE = [
    "CAMPAIGN_FINAL_REPORT.md", "CROSS_EPOCH_EVIDENCE_SYNTHESIS.md", "GRADUATED_FINDINGS.md",
    "STRONG_LEADS_AND_FAILED_REPLICATIONS.md", "METHOD_EXHAUSTION_MAP.md",
    "INFORMATION_GAIN_AND_BOTTLENECKS.md", "PROSPECTIVE_SEALS_AND_FUTURE_TESTS.md",
    "NEXT_STEPS_AFTER_CAMPAIGN.md", "INTEGRITY_AND_REPRODUCIBILITY.md",
]
GENERATED = [
    "CAMPAIGN_FINAL_STATE.json", "FINAL_VERDICTS.json", "GRADUATED_FINDINGS.json",
    "STRONG_LEADS.json", "METHOD_EXHAUSTION_MAP.json", "PROSPECTIVE_SEALS.json",
    "ARTIFACT_MANIFEST.json", "EPOCHS_001_TO_FINAL_MASTER_TABLE.csv",
    "RECONCILIATION_TABLE.csv",
]
EPOCH_FILES = {
    "EPOCH-103": ["prereg.md", "plan_hash.txt", "machinery.py", "result.json",
                  "prereg_addendum_R.md", "plan_hash_R.txt", "machinery_R.py",
                  "result_R.json"],
    "EPOCH-104": ["prereg.md", "plan_hash.txt", "machinery.py", "result.json",
                  "prereg_addendum_R.md", "plan_hash_R.txt", "machinery_R.py",
                  "result_R.json"],
    "EPOCH-105": ["prereg.md", "plan_hash.txt", "machinery.py", "result.json"],
}
# D1: the seal manifest's five referenced files (licence-clean, campaign-derived), at the
# manifest's own relative paths so `sha256sum -c` works from the bundle root.
SEAL_MANIFEST_SRC = f"{ROOT}/data/seals/FRACTION_ORDER_ANETAKI_SEAL.manifest.sha256"
SEAL_REFERENCED = [
    f"{ROOT}/data/seals/FRACTION_ORDER_ANETAKI_SEAL.json",
    f"{ROOT}/epochs/EPOCH-004/prereg.md",
    f"{ROOT}/epochs/EPOCH-004/derivation.json",
    f"{ROOT}/epochs/EPOCH-004/controls_pc.json",
    f"{ROOT}/scripts/fraction_order_seal.py",
]


def main():
    # fresh bundle, preserving the authored README
    readme = open(f"{BUNDLE}/README.md").read()
    shutil.rmtree(BUNDLE)
    os.makedirs(BUNDLE)
    open(f"{BUNDLE}/README.md", "w").write(readme)

    for f in NARRATIVE + GENERATED:
        shutil.copy2(f"{FINAL}/{f}", f"{BUNDLE}/{f}")
    for ep, files in EPOCH_FILES.items():
        os.makedirs(f"{BUNDLE}/epochs/{ep}", exist_ok=True)
        for f in files:
            shutil.copy2(f"{ROOT}/epochs/{ep}/{f}", f"{BUNDLE}/epochs/{ep}/{f}")
    # seal manifest at its convenience location + referenced files at manifest paths (D1)
    os.makedirs(f"{BUNDLE}/seals", exist_ok=True)
    shutil.copy2(SEAL_MANIFEST_SRC, f"{BUNDLE}/seals/FRACTION_ORDER_ANETAKI_SEAL.manifest.sha256")
    for src in SEAL_REFERENCED:
        dst = f"{BUNDLE}/{src}"  # src already starts with experiments/...
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)

    # BUNDLE_MANIFEST.sha256 — every file, bundle-relative, excluding itself
    entries = []
    for dirpath, _, files in os.walk(BUNDLE):
        for f in sorted(files):
            p = os.path.join(dirpath, f)
            rel = os.path.relpath(p, BUNDLE)
            if rel == "BUNDLE_MANIFEST.sha256":
                continue
            h = hashlib.sha256(open(p, "rb").read()).hexdigest()
            entries.append((rel, h))
    entries.sort()
    with open(f"{BUNDLE}/BUNDLE_MANIFEST.sha256", "w") as f:
        for rel, h in entries:
            f.write(f"{h}  {rel}\n")

    # zip (deterministic order)
    zip_path = f"{FINAL}/LOGOS_72H_REVIEW_BUNDLE.zip"
    if os.path.exists(zip_path):
        os.remove(zip_path)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        all_files = sorted(
            os.path.relpath(os.path.join(dp, f), BUNDLE)
            for dp, _, fs in os.walk(BUNDLE) for f in fs)
        for rel in all_files:
            z.write(os.path.join(BUNDLE, rel), arcname=f"review_bundle/{rel}")
    print(f"bundle files: {len(entries) + 1}  zip: {zip_path}")
    print("zip sha256:", hashlib.sha256(open(zip_path, "rb").read()).hexdigest())


if __name__ == "__main__":
    main()
