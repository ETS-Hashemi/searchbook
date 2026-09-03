#!/usr/bin/env bash
# Build the textbook locally.
#   ./build.sh                 -> full book  (output: build-full/main.pdf)
#   ./build.sh ch04-astar      -> only that chapter, via \includeonly (output: build/only-ch04-astar.pdf)
#   ./build.sh appA-study-plan -> works for appendices too
# Requires: pdflatex, biber, makeindex, latexmk (TeX Live).
set -uo pipefail
cd "$(dirname "$0")"
if [ $# -ge 1 ]; then
  ONLY="$1"
  if [ -f "chapters/$ONLY.tex" ]; then DIR=chapters; elif [ -f "appendices/$ONLY.tex" ]; then DIR=appendices; else
    echo "No such chapter/appendix: $ONLY" >&2; exit 2; fi
  OUT=build; JOB="only-$ONLY"
  mkdir -p "$OUT/chapters" "$OUT/appendices" "$OUT/frontmatter"
  printf '\\includeonly{%s/%s}\n\\input{main.tex}\n' "$DIR" "$ONLY" > "$OUT/$JOB.tex"
  cp "$OUT/$JOB.tex" "./$JOB.tex"
  latexmk -g -pdf -outdir="$OUT" -jobname="$JOB" "./$JOB.tex" > "$OUT/$JOB.latexmk.log" 2>&1
  STATUS=$?
  rm -f "./$JOB.tex"
  LOG="$OUT/$JOB.log"
else
  OUT=build-full; JOB=main
  mkdir -p "$OUT/chapters" "$OUT/appendices" "$OUT/frontmatter"
  latexmk -g -pdf -outdir="$OUT" main.tex > "$OUT/$JOB.latexmk.log" 2>&1
  STATUS=$?
  LOG="$OUT/$JOB.log"
fi
echo "=== build status: $STATUS (0 = success) ; log: $LOG ==="
if [ -f "$LOG" ]; then
  echo "--- errors ---";            grep -n -E '^(.*):[0-9]+: |^! ' "$LOG" | head -40
  echo "--- undefined refs/cites ---"; grep -n -E "Reference .* undefined|Citation .* undefined|multiply defined|undefined on input line" "$LOG" | head -40
  echo "--- overfull boxes > 15pt ---"; grep -n -E "Overfull \\\\hbox \([0-9]{2,}\.?[0-9]*pt" "$LOG" | awk -F'[(p]' '{ if ($2+0 > 15) print }' | head -20
  echo "--- pages ---"; grep -o -E "Output written on .*" "$LOG" | tail -1
fi
exit $STATUS
