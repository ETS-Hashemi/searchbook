#!/usr/bin/env bash
# Build the textbook locally.
#   ./build.sh                 -> full book  (output: build-full/main.pdf)
#   ./build.sh ch04-astar      -> only that chapter, via \includeonly (output: build/only-ch04-astar.pdf)
#   ./build.sh appA-study-plan -> works for appendices too
# Requires: pdflatex, biber, makeindex, latexmk (TeX Live).
set -uo pipefail
cd "$(dirname "$0")"
if [ "${1:-}" = "--standalone" ]; then
  # ./build.sh --standalone path/to/fragment.tex  -> build/standalone-<name>.pdf
  FRAG="$2"; NAME="standalone-$(basename "$FRAG" .tex)"; OUT=build
  mkdir -p "$OUT"
  cat > "./$NAME.tex" <<TEX
\\documentclass[11pt,a4paper,oneside,openany]{book}
\\usepackage{searchbook}
\\addbibresource{references.bib}
\\addbibresource{bib/ch01-extra.bib}
\\addbibresource{bib/ch02-extra.bib}
\\addbibresource{bib/ch03-extra.bib}
\\addbibresource{bib/ch04-extra.bib}
\\addbibresource{bib/ch05-extra.bib}
\\addbibresource{bib/ch06-extra.bib}
\\addbibresource{bib/ch07-extra.bib}
\\addbibresource{bib/ch08-extra.bib}
\\addbibresource{bib/ch09-extra.bib}
\\addbibresource{bib/ch10-extra.bib}
\\addbibresource{bib/ch11-extra.bib}
\\addbibresource{bib/ch12-extra.bib}
\\addbibresource{bib/ch13-extra.bib}
\\addbibresource{bib/ch14-extra.bib}
\\addbibresource{bib/ch15-extra.bib}
\\addbibresource{bib/ch16-extra.bib}
\\addbibresource{bib/ch17-extra.bib}
\\addbibresource{bib/ch18-extra.bib}
\\addbibresource{bib/ch19-extra.bib}
\\addbibresource{bib/ch20-extra.bib}
\\addbibresource{bib/ch21-extra.bib}
\\addbibresource{bib/ch22-extra.bib}
\\addbibresource{bib/ch23-extra.bib}
\\addbibresource{bib/ch24-extra.bib}
\\addbibresource{bib/ch25-extra.bib}
\\makeindex[intoc,title=Index]
\\begin{document}
\\mainmatter
\\input{$FRAG}
\\printbibliography
\\printindex
\\end{document}
TEX
  latexmk -g -pdf -outdir="$OUT" -jobname="$NAME" "./$NAME.tex" > "$OUT/$NAME.latexmk.log" 2>&1
  STATUS=$?
  rm -f "./$NAME.tex"
  LOG="$OUT/$NAME.log"
elif [ $# -ge 1 ]; then
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
