#!/usr/bin/env bash
# Build both TACL/arXiv targets from the shared body.
# Usage: bash build.sh
set -u
cd "$(dirname "$0")"
HERE="$(pwd)"
OUT="$HERE/../build"
mkdir -p "$OUT"

export TEXINPUTS="$HERE:"
export BIBINPUTS="$HERE:"
export BSTINPUTS="$HERE:"

build_one () {
  local main="$1" outname="$2"
  echo "=================== building $main ==================="
  pdflatex -interaction=nonstopmode -halt-on-error -output-directory="$OUT" "$main.tex" >/dev/null 2>&1
  ( cd "$OUT" && bibtex "$main" >/dev/null 2>&1 )
  pdflatex -interaction=nonstopmode -halt-on-error -output-directory="$OUT" "$main.tex" >/dev/null 2>&1
  pdflatex -interaction=nonstopmode -halt-on-error -output-directory="$OUT" "$main.tex" >/dev/null 2>&1
  pdflatex -interaction=nonstopmode -output-directory="$OUT" "$main.tex" > "$OUT/$main.lastrun.log" 2>&1
  mv -f "$OUT/$main.pdf" "$OUT/$outname.pdf" 2>/dev/null
  echo "  -> $OUT/$outname.pdf"
}

build_one main-arxiv logos-arxiv
build_one main-tacl  logos-tacl-anon
echo "done."
