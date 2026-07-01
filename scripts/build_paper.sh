#!/usr/bin/env bash
# build_paper.sh — render the logos preprint to LaTeX (.tex) + PDF from the Markdown source.
#
# Deterministic, reproducible paper build. Requires pandoc + xelatex (texlive-xetex) and a
# Unicode-rich serif (DejaVu Serif covers the Greek + math the paper uses; verified 0 missing
# characters). Outputs land next to the source in docs/preprint/.
#
# Usage:  bash scripts/build_paper.sh [SOURCE.md]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="${1:-$ROOT/docs/preprint/logos-preprint-2026-07-01.md}"
OUTDIR="$(dirname "$SRC")"
STEM="$(basename "$SRC" .md)"

command -v pandoc  >/dev/null || { echo "ERROR: pandoc not found (apt-get install pandoc)"; exit 1; }
command -v xelatex >/dev/null || { echo "ERROR: xelatex not found (apt-get install texlive-xetex)"; exit 1; }

COMMON=(--pdf-engine=xelatex
        -V mainfont="DejaVu Serif"
        -V monofont="DejaVu Sans Mono"
        -V geometry:margin=1in
        -V fontsize=10pt
        -V colorlinks=true
        -V linkcolor=blue -V urlcolor=blue)

echo "[build] $SRC"
echo "[build] -> $OUTDIR/$STEM.tex (standalone LaTeX)"
pandoc "$SRC" -s "${COMMON[@]}" -o "$OUTDIR/$STEM.tex"

echo "[build] -> $OUTDIR/$STEM.pdf"
warn=$(pandoc "$SRC" "${COMMON[@]}" --toc -o "$OUTDIR/$STEM.pdf" 2>&1 | grep -ic "missing character" || true)
echo "[build] missing characters: $warn (expect 0)"
echo "[build] done: $(ls -la "$OUTDIR/$STEM.pdf" | awk '{print $5" bytes"}')"
